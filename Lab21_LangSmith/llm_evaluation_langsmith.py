"""LangSmith bootstrap for the swimming analysis lab.

This module mirrors the setup shown in `02_langsmith.ipynb`:
- load environment variables from `.env`
- enable LangSmith tracing
- point LangSmith to the EU endpoint
- initialize the LangSmith and OpenAI clients
- verify the connection to LangSmith
"""

from __future__ import annotations
import argparse
import csv
import os
from pathlib import Path
from typing import Any
from dotenv import load_dotenv
from langsmith import Client, traceable
from langsmith.wrappers import wrap_openai
from openai import OpenAI
from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT

LANGSMITH_ENDPOINT = "https://eu.api.smith.langchain.com"
LANGSMITH_PROJECT = "swimming_analysis"
DATASET_NAME = "swimming_benchmark"

def configure_langsmith() -> None:
    """Load environment variables and configure LangSmith tracing."""
    load_dotenv()

    # Match the notebook setup exactly so traces are routed to the EU endpoint.
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_ENDPOINT"] = LANGSMITH_ENDPOINT
    os.environ["LANGSMITH_PROJECT"] = LANGSMITH_PROJECT
configure_langsmith()

client = Client()
openai_client = wrap_openai(OpenAI())

def verify_langsmith_connection() -> None:
    """Verify that we can talk to LangSmith with the configured credentials."""
    try:
        projects = client.list_projects(limit=1)
        first_project: Any = next(iter(projects), None)
        if first_project is not None:
            print(
                "LangSmith connection verified. "
                f"Project access looks good for '{LANGSMITH_PROJECT}'."
            )
        else:
            print(
                "LangSmith connection verified, but no projects were returned. "
                f"Project target is '{LANGSMITH_PROJECT}'."
            )
    except Exception as exc:  # pragma: no cover - runtime verification only
        raise RuntimeError(
            "Unable to verify the LangSmith connection. "
            "Check LANGSMITH_API_KEY, LANGSMITH_ENDPOINT, and network access."
        ) from exc


def load_records_as_string(csv_path: str | None = None) -> str:
    """Load a CSV file and return its full contents as a single string.

    If no path is provided, the user is prompted for one.
    """
    if not csv_path:
        csv_path = input("Please provide the path to the CSV file with the swimming records: ").strip()

    if not csv_path:
        raise ValueError("A CSV path is required.")

    path = Path(csv_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")

    records = path.read_text(encoding="utf-8")
    return records


def load_benchmark_examples(csv_path: str | None = None) -> list[dict[str, str]]:
    """Load question/answer pairs from a CSV file."""
    if not csv_path:
        csv_path = input(
            "Please provide the path to the QA benchmark CSV file: "
        ).strip()

    if not csv_path:
        raise ValueError("A benchmark CSV path is required.")

    path = Path(csv_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Benchmark CSV file not found: {path}")

    examples: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter=";")
        for row in reader:
            if not row:
                continue
            if len(row) < 2:
                raise ValueError(
                    f"Invalid benchmark row in {path}: expected question and answer."
                )
            question = row[0].strip()
            answer = row[1].strip()
            if question and answer:
                examples.append({"question": question, "answer": answer})

    if not examples:
        raise ValueError(f"No benchmark examples were found in {path}")

    return examples


def create_benchmark_dataset(
    benchmark_examples: list[dict[str, str]],
    records: str,
    dataset_name: str = DATASET_NAME,
    description: str = "Swimming record QA benchmark dataset",
) -> None:
    """Create a LangSmith dataset from benchmark examples."""
    existing = list(client.list_datasets(dataset_name=dataset_name, limit=1))
    if existing:
        dataset = existing[0]
        example_with_records = False
        first_example = next(client.list_examples(dataset_id=dataset.id, limit=1), None)
        if first_example is not None:
            inputs = getattr(first_example, "inputs", None)
            example_with_records = isinstance(inputs, dict) and "records" in inputs

        if example_with_records:
            print(
                f"Dataset '{dataset_name}' already exists and contains 'records' in inputs — skipping upload"
            )
            return

        print(
            f"Dataset '{dataset_name}' exists but examples do not contain 'records'. "
            "Deleting and recreating it with the correct schema."
        )
        client.delete_dataset(dataset_id=dataset.id)

    dataset = client.create_dataset(dataset_name, description=description)
    inputs = [
        {"question": example["question"], "records": records}
        for example in benchmark_examples
    ]
    outputs = [{"answer": example["answer"]} for example in benchmark_examples]

    client.create_examples(
        inputs=inputs,
        outputs=outputs,
        dataset_id=dataset.id,
    )
    print(f"Created dataset '{dataset_name}' with {len(benchmark_examples)} examples")


@traceable(name="swimming-training-target")
def target_swimming_question(inputs: dict[str, str]) -> dict[str, str]:
    """Run the LangSmith target function for swimming QA."""
    records = inputs.get("records")
    if records:
        system_prompt = (
            "You are an assistant that answers questions about my swimming training in the past months. "
            "The format of the training records is as follows: each line contains the date, distance swum, and time taken, separated by commas. "
            "If the date and the swimming pool coincide across consecutive lines, they belong to the same training session. "
            "Medley runs are separated into individual lines for each stroke."
            "Here are the records:\n"
            f"{records}"
        )
    else:
        system_prompt = (
            "You are an assistant that answers questions about my swimming training in the past months. "
            "No training records are available for this example. Answer the question as best as you can."
        )

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": inputs["question"]},
        ],
        max_tokens=1000,
        temperature=0.0,
    )
    return {"answer": response.choices[0].message.content.strip()}


_judge = create_llm_as_judge(
    prompt=CORRECTNESS_PROMPT,
    model="cohere:command-nightly",
    feedback_key="correctness",
)


def correctness_evaluator(
    inputs: dict[str, str],
    outputs: dict[str, str],
    reference_outputs: dict[str, str],
) -> dict[str, str]:
    """Evaluate whether the model answer matches the reference answer."""
    return _judge(
        inputs=inputs,
        outputs=outputs,
        reference_outputs=reference_outputs,
    )


def evaluate_dataset(
    dataset_name: str = DATASET_NAME,
    experiment_prefix: str = "swimming-gpt-4o-mini",
    max_concurrency: int = 2,
):
    """Run a LangSmith evaluation using the target and correctness judge."""
    results = client.evaluate(
        target_swimming_question,
        data=dataset_name,
        evaluators=[correctness_evaluator],
        experiment_prefix=experiment_prefix,
        max_concurrency=max_concurrency,
    )
    print(f"Completed evaluation for dataset '{dataset_name}'")
    print(results)
    return results


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="LangSmith setup and CSV loader for the swimming analysis lab."
    )
    parser.add_argument(
        "csv_path",
        nargs="?",
        default=None,
        help="Path to the CSV file containing the swimming records.",
    )
    parser.add_argument(
        "--benchmark-csv",
        dest="benchmark_csv",
        default=None,
        help="Path to the CSV file containing reference questions and answers.",
    )
    return parser.parse_args()



if __name__ == "__main__":
    verify_langsmith_connection()
    args = parse_args()
    records = load_records_as_string(args.csv_path)
    benchmark_examples = load_benchmark_examples(args.benchmark_csv)
    create_benchmark_dataset(benchmark_examples, records)
    evaluate_dataset()