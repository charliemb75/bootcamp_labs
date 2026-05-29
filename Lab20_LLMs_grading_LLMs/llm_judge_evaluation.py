from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

SYSTEM_PROMPT = """You are evaluating a model that has been asked to answer a healthcare summarization task using a patient's medical record.

Your job is to determine whether the model response is clinically reliable with respect to the source record and the user's original question.

Focus on the following requirements:
1. Completeness of Clinical Events: The response includes all major clinical events present in the source record that are relevant for answering the original question.
2. Temporal Correctness: If the question requires chronology or sequence, events are ordered correctly in time, with no incorrect sequencing or contradictions.
3. Factual Faithfulness (No Hallucination): The response does not introduce any events, diagnoses, treatments, or medical facts that are not explicitly supported by the patient record.
4. Medical Terminology: Medical terms, abbreviations, and clinical concepts are used correctly and without meaning changes.

Reasoning steps:
Step 1: Read the source patient record and identify the clinically relevant facts needed to answer the original question.
Step 2: Compare the model output against the source record to identify:
- Missing facts or events
- Added facts or events that are not supported
- Terminology mistakes or meaning changes
Step 3: If the task requires ordering, verify chronological consistency:
- Are events in the correct sequence?
- Are there any temporal contradictions?
Step 4: Aggregate the findings into criterion-level judgments and assign an overall score from 1 to 5.

Scoring guide:
- 5: Fully correct, complete, faithful, and properly ordered when ordering matters.
- 4: Mostly correct with only minor omissions or minor wording issues that do not affect clinical meaning.
- 3: Mixed quality with noticeable omissions, mild hallucination risk, or some ordering issues.
- 2: Serious completeness or faithfulness problems that would make the summary unreliable.
- 1: Unsafe or largely incorrect summary with major hallucinations or critical omissions.

Return only valid JSON matching this schema:
{
  "score": 1-5,
  "reasoning": "Explanation of how the score was determined, including missing or hallucinated events and ordering issues.",
  "criteria_met": {
    "completeness_of_clinical_events": true/false,
    "temporal_correctness": true/false,
    "factual_faithfulness": true/false
  }
}
"""

USER_PROMPT_TEMPLATE = """Original question for the model:
{question}

Patient's medical record:
{record}

Model output:
{output}
"""

# These defaults are approximate and can be updated if you want to track
# pricing for additional models or a newer rate card.
MODEL_PRICING_USD_PER_1M_TOKENS: dict[str, dict[str, float]] = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o": {"input": 5.00, "output": 15.00},
}

JSON_OUTPUT_DIR = Path(__file__).resolve().parent / "jsons"


def load_environment() -> None:
    """Load environment variables from a .env file if available."""
    load_dotenv()


def read_text_file(path: str | Path) -> str:
    """Read a text file with a clear error if the file does not exist."""
    file_path = Path(path).expanduser()
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    return file_path.read_text(encoding="utf-8", errors="replace").strip()


def build_user_prompt(question: str, record: str, output: str) -> str:
    """Fill the judge prompt template."""
    return USER_PROMPT_TEMPLATE.format(question=question, record=record, output=output)


def _extract_json_block(text: str) -> str:
    """Extract a JSON object from a response that may include code fences or extra text."""
    fenced_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if fenced_match:
        return fenced_match.group(1)

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]

    raise ValueError("The judge response did not contain a JSON object.")


def parse_judge_response(text: str) -> dict[str, Any]:
    """Parse and validate the judge response."""
    payload = json.loads(_extract_json_block(text))

    if not isinstance(payload, dict):
        raise ValueError("Judge output must be a JSON object.")

    score = payload.get("score")
    reasoning = payload.get("reasoning")
    criteria_met = payload.get("criteria_met")

    if not isinstance(score, int) or score < 1 or score > 5:
        raise ValueError("Field 'score' must be an integer between 1 and 5.")
    if not isinstance(reasoning, str) or not reasoning.strip():
        raise ValueError("Field 'reasoning' must be a non-empty string.")
    if not isinstance(criteria_met, dict):
        raise ValueError("Field 'criteria_met' must be an object.")

    expected_keys = (
        "completeness_of_clinical_events",
        "temporal_correctness",
        "factual_faithfulness",
    )
    missing = set(expected_keys).difference(criteria_met.keys())
    if missing:
        raise ValueError(f"criteria_met is missing keys: {sorted(missing)}")

    normalized_criteria: dict[str, bool] = {}
    for key in expected_keys:
        value = criteria_met[key]
        if not isinstance(value, bool):
            raise ValueError(f"criteria_met['{key}'] must be a boolean.")
        normalized_criteria[key] = value

    return {
        "score": score,
        "reasoning": reasoning.strip(),
        "criteria_met": normalized_criteria,
    }


def _extract_token_usage(response: Any) -> dict[str, int] | None:
    """Extract token usage from an OpenAI API response when available."""
    usage = getattr(response, "usage", None)
    if usage is None:
        return None

    if isinstance(usage, dict):
        prompt_tokens = usage.get("prompt_tokens")
        completion_tokens = usage.get("completion_tokens")
        total_tokens = usage.get("total_tokens")
    else:
        prompt_tokens = getattr(usage, "prompt_tokens", None)
        completion_tokens = getattr(usage, "completion_tokens", None)
        total_tokens = getattr(usage, "total_tokens", None)

    token_usage: dict[str, int] = {}
    if isinstance(prompt_tokens, int):
        token_usage["prompt_tokens"] = prompt_tokens
    if isinstance(completion_tokens, int):
        token_usage["completion_tokens"] = completion_tokens
    if isinstance(total_tokens, int):
        token_usage["total_tokens"] = total_tokens

    return token_usage or None


def _estimate_cost_usd(model: str, token_usage: dict[str, int] | None) -> float | None:
    """Estimate API cost in USD from token usage and a local pricing table."""
    if not token_usage:
        return None

    pricing = MODEL_PRICING_USD_PER_1M_TOKENS.get(model)
    if pricing is None:
        return None

    prompt_tokens = token_usage.get("prompt_tokens", 0)
    completion_tokens = token_usage.get("completion_tokens", 0)
    estimated_cost = (
        (prompt_tokens / 1_000_000) * pricing["input"]
        + (completion_tokens / 1_000_000) * pricing["output"]
    )
    return round(estimated_cost, 6)


def _build_json_output_path(output_path: str | Path) -> Path:
    """Build the destination JSON path inside the jsons folder."""
    output_name = Path(output_path).expanduser().name
    return JSON_OUTPUT_DIR / Path(output_name).with_suffix(".json").name


def save_evaluation_result(result: dict[str, Any], output_path: str | Path) -> Path:
    """Save the evaluation result to the jsons folder and return the file path."""
    destination = _build_json_output_path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, ensure_ascii=True), encoding="utf-8")
    return destination


def evaluate_response(
    question: str,
    record_path: str | Path,
    output_path: str | Path,
    model: str = "gpt-4o-mini",
) -> dict[str, Any]:
    """
    Evaluate a model output against a clinical record using an LLM judge.

    Returns a dictionary with score, reasoning, criterion-level booleans,
    and evaluation metrics for the judge call.
    """
    load_environment()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY is not set.")

    try:
        from openai import OpenAI
    except ImportError as exc:  # pragma: no cover - runtime dependency
        raise ImportError(
            "The openai package is required. Install it with `pip install openai`."
        ) from exc

    record = read_text_file(record_path)
    output = read_text_file(output_path)
    user_prompt = build_user_prompt(question=question, record=record, output=output)

    client = OpenAI(api_key=api_key)
    start_time = time.perf_counter()
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    time_taken = round(time.perf_counter() - start_time, 6)

    content = response.choices[0].message.content or ""
    parsed = parse_judge_response(content)
    token_usage = _extract_token_usage(response)
    parsed["evaluation_metrics"] = {
        "time_taken": time_taken,
        "token_usage": token_usage,
        "estimated_cost": _estimate_cost_usd(model, token_usage),
    }
    return parsed


def _prompt_for_value(label: str) -> str:
    """Prompt the user until they provide a non-empty value."""
    value = ""
    while not value.strip():
        value = input(f"{label}: ").strip()
    return value


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run an LLM-as-judge evaluation for a clinical summarization task."
    )
    parser.add_argument(
        "--question",
        help="Original prompt/question given to the model.",
    )
    parser.add_argument(
        "--record",
        help="Path to the patient's clinical record .txt file.",
    )
    parser.add_argument(
        "--output",
        help="Path to the model response .txt file.",
    )
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="OpenAI model to use as the judge. Default: gpt-4o-mini",
    )

    args = parser.parse_args()

    question = args.question or _prompt_for_value("Original prompt")
    record_path = args.record or _prompt_for_value("Path to patient record txt")
    output_path = args.output or _prompt_for_value("Path to model response txt")

    result = evaluate_response(
        question=question,
        record_path=record_path,
        output_path=output_path,
        model=args.model,
    )

    saved_path = save_evaluation_result(result, output_path)
    print(json.dumps(result, indent=2, ensure_ascii=True))
    print(f"\nSaved evaluation JSON to: {saved_path}")


if __name__ == "__main__":
    main()
