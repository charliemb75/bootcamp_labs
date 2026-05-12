import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from typing import TypedDict, List, Optional
from typing_extensions import Annotated

load_dotenv()

# Make sure OPENAI_API_KEY is set in your .env file
print("OpenAI API Key loaded:", "OPENAI_API_KEY" in os.environ)

# Initialize OpenAI LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

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

    # Example:
    # customer_id: str

# ---------------------------------------------------
# Step 2: Import Workflow Nodes
# ---------------------------------------------------

from node_functions import intake_node, validate_node, investigate_node, resolve_node, close_node

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
 
# Intake always goes to validate
workflow.add_edge("intake", "validate")
 
# Linear flow: investigate → resolve → close
workflow.add_edge("investigate", "resolve")
workflow.add_edge("resolve", "close")
 
# Close goes to end
workflow.add_edge("close", END)
 
# Compile the graph
app = workflow.compile()


if __name__ == "__main__":

    # ---------------------------------------------------
    # INITIAL STATE DEFINITION
    # ---------------------------------------------------

    initial_state: ComplaintState = {
        "complaint": "I am poor"
    }

    print("LangGraph complaint processor initialized.")
    print("\nInitial State:\n")
    for key, value in initial_state.items():
        print(f"{key}: {value}")

        "status": "received",
        "resolution_notes": [],
        "requires_human_review": False,
    }

    print("LangGraph complaint processor initialized.")
    print("\nInitial State:\n")
    for key, value in initial_state.items():
        print(f"{key}: {value}")
