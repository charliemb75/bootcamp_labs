# Lab 13 - Complaint Processor LangGraph

This graph processes a complaint through five stages:

1. `intake`
2. `validate`
3. `investigate`
4. `resolve`
5. `close`

## Possible scenarios

- **Complaint is too vague at first**
  - The graph rejects it during `intake`.
  - It asks the user to rewrite the complaint with more detail.
  - Then it loops back to `intake` and tries again.

- **Complaint has enough detail and fits a valid category**
  - The graph accepts it in `intake` and moves it to `validate`.
  - It categorizes the complaint as `portal`, `monster`, `psychic`, or `environmental` or `other`.

- **Complaint is categorized as `other`**
  - `validate` rejects it.
  - The workflow skips investigation and ends with manual review / escalation.

- **Complaint is valid and fully processed**
  - After `validate`, the graph goes to `investigate`.
  - Then it goes to `resolve`.
  - Finally it reaches `close`.

- **Environmental or monster complaints**
  - These may be marked for specialized review at `resolve`.
  - The final close message can show that review is required even if the workflow completed.

## When the graph asks for user input

The graph only asks for user input in two moments:

- **At the start of the program**
  - `Enter a complaint:`

- **If the first complaint is rejected by `intake`**
  - `Please rewrite your complaint with more details:`

After that, the rest of the workflow runs automatically without more user prompts.
