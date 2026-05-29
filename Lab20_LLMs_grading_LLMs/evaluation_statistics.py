from __future__ import annotations

import json
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
JSON_DIR = BASE_DIR / "jsons"
OUTPUT_FILE = BASE_DIR / "evaluation_statistics.json"


def _read_json(path: Path) -> dict[str, Any]:
    """Read a JSON file and ensure it contains an object."""
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object in {path.name}")

    return payload


def _numeric(value: Any) -> float:
    """Convert a value to float, treating missing or invalid values as 0."""
    if isinstance(value, bool) or value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0


def _extract_total_tokens(payload: dict[str, Any]) -> float:
    """Extract token usage from a single evaluation payload."""
    metrics = payload.get("evaluation_metrics", {})
    if not isinstance(metrics, dict):
        return 0.0

    token_usage = metrics.get("token_usage", {})
    if not isinstance(token_usage, dict):
        return _numeric(metrics.get("total_tokens"))

    total_tokens = token_usage.get("total_tokens")
    if isinstance(total_tokens, (int, float)) and not isinstance(total_tokens, bool):
        return float(total_tokens)

    prompt_tokens = token_usage.get("prompt_tokens")
    completion_tokens = token_usage.get("completion_tokens")
    return _numeric(prompt_tokens) + _numeric(completion_tokens)


def build_statistics() -> dict[str, Any]:
    """Aggregate all evaluation JSON files into a single statistics object."""
    json_files = sorted(JSON_DIR.glob("*.json"))
    if not json_files:
        raise FileNotFoundError(f"No JSON files found in {JSON_DIR}")

    scores: list[float] = []
    total_time = 0.0
    total_tokens = 0.0
    total_cost = 0.0

    for json_file in json_files:
        payload = _read_json(json_file)
        scores.append(_numeric(payload.get("score")))

        metrics = payload.get("evaluation_metrics", {})
        if isinstance(metrics, dict):
            total_time += _numeric(metrics.get("time_taken"))
            total_cost += _numeric(metrics.get("estimated_cost"))
        total_tokens += _extract_total_tokens(payload)

    average_score = sum(scores) / len(scores)

    return {
        "average_score": round(average_score, 6),
        "evaluation_metrics": {
            "total_time": round(total_time, 6),
            "total_tokens": int(round(total_tokens)),
            "total_cost": round(total_cost, 6),
        },
    }


def main() -> None:
    """Generate the aggregated statistics JSON file."""
    statistics = build_statistics()
    OUTPUT_FILE.write_text(json.dumps(statistics, indent=2, ensure_ascii=True), encoding="utf-8")
    print(f"Wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
