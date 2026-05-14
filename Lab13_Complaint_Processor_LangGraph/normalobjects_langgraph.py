import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import HumanMessage
from typing import TypedDict, List, Optional
from typing_extensions import Annotated

load_dotenv()

# Make sure OPENAI_API_KEY is set in your .env file
print("OpenAI API Key loaded:", "OPENAI_API_KEY" in os.environ)


# ---------------------------------------------------
# Step 1: Setup and State Definition
# ---------------------------------------------------

class ComplaintState(TypedDict):
    """
    Shared state across the complaint workflow.
    Every node in the LangGraph receives this state
    and returns updates to it.
    """
    complaint: str
    category: str
    workflow_path: list[str]
    status: str
    check_result: str
    check_reason: str
    validation_result: str
    validation_reason: str
    investigation_content: str
    effectiveness_rating: str
    escalation: bool
    resolved: bool
    timestamp: str

    # Example:
    # customer_id: str


# ---------------------------------------------------
# Step 2: see node_functions.py for node implementations
# ---------------------------------------------------
from node_functions import (
    intake_node,
    validate_node,
    investigate_node,
    resolve_node,
    close_node
)


# ---------------------------------------------------
# Step 3: Build the Graph
# ---------------------------------------------------

# Create the graph, INCOMPLETE EXAMPLE - YOU MUST CONNECT AS YOU WISH
workflow = StateGraph(ComplaintState)
 
# Add nodes
workflow.add_node("intake", intake_node)
workflow.add_node("validate", validate_node)
workflow.add_node("investigate", investigate_node)
workflow.add_node("resolve", resolve_node)
workflow.add_node("close", close_node)
 
# Define edges
workflow.set_entry_point("intake")  # Start here
 
# Intake can go to either validation or back to intake based on the result
def route_after_intake(state: ComplaintState) -> str:
    return "retry" if state.get("check_result") == False else "approved"
workflow.add_conditional_edges("intake", route_after_intake, {"retry": "intake", "approved": "validate"})

# Validation can go to either investigate or back to intake based on the result
def route_after_validate(state: ComplaintState) -> str:
    if not state.get("validation_result", True):
        if state.get("category") == "other":
            return "escalate"
        else:
            return "retry"
    else:
        return "approved"
workflow.add_conditional_edges("validate", route_after_validate, {"retry": "intake", "approved": "investigate", "escalate": "close"})

workflow.add_edge("investigate", "resolve")
workflow.add_edge("resolve", "close")
 
# Close goes to end
workflow.add_edge("close", END)
 
# Compile the graph
app = workflow.compile()


# ---------------------------------------------------
# Step 4: Test the Workflow
# ---------------------------------------------------

# test_complaints = [
#     "The Downside Up portal opens at different times each day. How do I predict when?",
#     "Demogorgons sometimes work together and sometimes fight. What's their deal?",
#     "El can move things with her mind but can't lift heavy rocks. Why?",
#     "Why do creatures and power lines react so strangely together?",
#     "This is not a valid complaint about something random"  # Should be rejected
# ]

print("\nLangGraph complaint processor initialized.")
complaint = input("Enter a complaint: ")
print("\nProcessing the complaint...")

result = app.invoke({"complaint": complaint})
