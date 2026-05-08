# Lab 10: Complaint Handler

This project is a small LangChain demo that builds a playful AI agent to handle fictional complaints about the Upside Down. Instead of giving plain answers, the agent uses a set of custom tools to investigate the issue from different angles and then responds with a creative explanation.

## What the code does

The main script is [`normalobjects_langchain.py`](./normalobjects_langchain.py).

It does the following:

1. Loads environment variables from a `.env` file.
2. Creates a chat model with OpenAI via LangChain.
3. Defines four custom tools:
   - `consult_demogorgon`: returns a fictional Demogorgon perspective.
   - `check_hawkins_records`: searches mock Hawkins records.
   - `cast_interdimensional_spell`: suggests a creative magical fix.
   - `gather_party_wisdom`: asks the D&D-style party for advice.
4. Wraps those tools in a LangChain agent with a custom system prompt.
5. Sends several sample complaints to the agent.
6. Tracks which tools were used and prints a small usage report at the end.

The output is intentionally theatrical and fictional. The point of the exercise is to demonstrate:

- how to define custom tools with LangChain
- how an agent can choose between tools dynamically
- how to inspect tool usage after running the agent

## Requirements

You need:

- Python 3.10+ recommended
- An OpenAI API key
- The Python packages used by the script:
  - `langchain`
  - `langchain-openai`
  - `langchain-core`
  - `python-dotenv`

If your environment does not already have them, install them with:

```bash
pip install langchain langchain-openai langchain-core python-dotenv
```

## Setup

1. Create a `.env` file in the project root if you do not already have one.
2. Add your OpenAI API key:

```env
OPENAI_API_KEY=your_api_key_here
```

3. Make sure you are working from the repository root, `4_Labs`, or from the `Lab10_Complaint_Handler` folder.

## How to run

From the project folder:

```bash
cd Lab10_Complaint_Handler
python normalobjects_langchain.py
```

Or, from the repo root:

```bash
python Lab10_Complaint_Handler/normalobjects_langchain.py
```

## What you should see

When the script runs, it will:

- print the list of available tools
- initialize the model and agent
- process the sample complaints
- show the agent's responses
- print a tool usage summary at the end

## Notes

- The complaint examples are fictional and tied to Stranger Things-style worldbuilding.
- Some tool outputs are randomized, so results can vary from run to run.
- The tool usage tracker is meant for analysis and debugging, not for production telemetry.
