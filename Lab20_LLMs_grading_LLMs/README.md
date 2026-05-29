# Lab 20: LLMs Grading LLMs

This folder contains two small utilities for evaluating clinical summaries with an LLM judge and then aggregating the results.

## `llm_judge_evaluation.py`

Uses an OpenAI model as a judge to compare:

1. The original question
2. The patient's medical record
3. The model output to be evaluated

It returns a JSON result with:

- `score`: integer from 1 to 5
- `reasoning`: short explanation of the score
- `criteria_met`: booleans for completeness, temporal correctness, and factual faithfulness
- `evaluation_metrics`: runtime, token usage, and estimated API cost when available

### Inputs

- `--question`: the original prompt given to the model
- `--record`: path to the patient's clinical record text file
- `--output`: path to the model response text file
- `--model`: OpenAI judge model to use, default `gpt-4o-mini`

If any of `--question`, `--record`, or `--output` is omitted, the script will ask for it interactively.

### Output

- Prints the evaluation JSON to the terminal
- Saves the same JSON under `Lab20_LLMs_grading_LLMs/jsons/`
- The saved filename matches the input output file name, but with a `.json` extension

### Example

```bash
python llm_judge_evaluation.py --question "Summarize the hospital course" --record medical_reports/p12031.txt --output model_outputs/p12031.txt
```

### Requirements

- `OPENAI_API_KEY` must be set
- The `openai` Python package must be installed
- A `.env` file is supported through `python-dotenv`

## `evaluation_statistics.py`

Reads every `.json` file in `Lab20_LLMs_grading_LLMs/jsons/` and computes aggregate statistics across all evaluations.

### Inputs

- All JSON evaluation files in `jsons/`

Each evaluation file is expected to contain at least:

- `score`
- `evaluation_metrics.time_taken`
- `evaluation_metrics.estimated_cost`
- `evaluation_metrics.token_usage` or token totals

### Output

- Writes `Lab20_LLMs_grading_LLMs/evaluation_statistics.json`
- The output includes:
  - `average_score`
  - total evaluation time
  - total token count
  - total estimated cost

### Example

```bash
python evaluation_statistics.py
```

## Typical workflow

1. Run `llm_judge_evaluation.py` for each model output you want to grade.
2. Collect the generated evaluation JSON files in `jsons/`.
3. Run `evaluation_statistics.py` to summarize all evaluations in one file.
