from __future__ import annotations
from datetime import datetime
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
# from normalobjects_langgraph import ComplaintState
import ast
import random

# Initialize OpenAI LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

@tool
def check_hawkins_records(query: str) -> str:
    """Search Hawkins historical records for information.
    
    Walvins, Germany has a long history of strange occurrences. These records
    might contain clues about patterns or explanations.
    
    Args:
        query: What to search for in the records
        
    Returns:
        Information from Hawkins historical records
    """
    # Simulate database lookup
    records = {
        "portal": "Records show portals have opened on various dates with no clear pattern. Weather, electromagnetic activity, and unknown factors seem involved.",
        "monsters": "Historical records indicate creatures from the Upside Down behave differently based on environmental factors, time of day, and proximity to certain individuals.",
        "psychics": "Records show that psychic abilities vary greatly. Some individuals can move objects but not see the future, others can see visions but not move things.",
        "electricity": "Walkins has a history of electrical anomalies. Records suggest a connection between the Downside Up and electromagnetic fields."
    }
    for key, value in records.items():
        if key in query.lower():
            return value
    return f"Records don't contain specific information about '{query}', but they note that many unexplained events have occurred in Hawkins over the years."
 
@tool
def gather_party_wisdom(question: str) -> str:
    """Ask the D&D party (Mike, Dustin, Lucas, Will) for their collective wisdom.
    
    The party has solved many mysteries together. Their combined knowledge
    and different perspectives can provide insights.
    
    Args:
        question: The question or problem to ask the party about
        
    Returns:
        The party's collective wisdom and suggestions
    """
    party_responses = {
        "portal": "Mike: 'Portals are unpredictable, but they usually open near strong emotional events or electromagnetic disturbances.' Dustin: 'Also, they seem to follow some kind of pattern related to the Mind Flayer's activity.'",
        "monsters": "Lucas: 'Demogorgons are territorial but also opportunistic.' Will: 'They can sense fear and strong emotions. Maybe that's why they act differently sometimes.'",
        "psychics": "Mike: 'El's powers seem connected to her emotional state.' Dustin: 'And they're limited by her physical and mental energy. That's probably why she can't do everything.'",
        "electricity": "Lucas: 'The Upside Down seems to interfere with electrical systems.' Dustin: 'But it also creates strange connections. It's like a feedback loop.'"
    }
    for key, response in party_responses.items():
        if key in question.lower():
            return response
    return "The party huddles together. Mike: 'This is a tough one.' Dustin: 'We need more information.' Lucas: 'Let's think about what we know.' Will: 'Maybe we should consult other sources?'"
 
# Create list of tools
tools = [check_hawkins_records, gather_party_wisdom]

def intake_node(state: ComplaintState) -> ComplaintState:
    """Step 1: Intake - Parse and categorize the complaint"""
    complaint = state["complaint"]

    if (not state.get("validation_result", True)) or (not state.get("check_result", True)):
        complaint = input("\n[INTAKE] Please rewrite your complaint with more details: ").strip()
        state["complaint"] = complaint

    # Verify complaint details using LLM
    verification_prompt = f"""Check whether this complaint contains information about at least one of the following aspects: who, what, when, and where.
It does not have to be perfectly detailed.
If the complaint is too vague or lacks essential details, it should be rejected with a brief explanation of what's missing.

Complaint: {complaint}

The answer is to be contained in two variables:
- validated: True if the complaint has enough detail, False if it needs clarification.
- reason: if rejected, provide a brief explanation of what is missing; if valid, return an empty string.
Respond exclusively in the following format: (validated, reason).
"""
    
    # Categorize complaint using LLM
    categorization_prompt = f"""Categorize this Downside Up complaint into one of these categories:
- portal: Issues with portal timing, location, or behavior
- monster: Issues with creature behavior (demogorgons, etc.)
- psychic: Issues with psychic abilities or limitations
- environmental: Issues with electricity, weather, or physical environment
- other: Anything else

Complaint: {complaint}

Respond with ONLY the category name (portal, monster, psychic, environmental, or other)."""

    response_ver = llm.invoke([HumanMessage(content=verification_prompt)])
    response_content = response_ver.content.strip()
    validated, reason = ast.literal_eval(response_content)

    if validated:
        print(f"\n[INTAKE] Complaint has enough detail to proceed.")
        response_cat = llm.invoke([HumanMessage(content=categorization_prompt)])
        category = response_cat.content.strip().lower()
        print(f"[INTAKE] Categorized as: {category}")

        # Update state
        new_state = {
            **state,
            "complaint": complaint,
            "check_result": validated,
            "check_reason": "",
            "category": category,
            "workflow_path": state.get("workflow_path", []) + ["intake"],
            "status": "intake",
        }

    else:
        print(f"\n[INTAKE] Complaint rejected: {reason}")
        new_state = {
            **state,
            "complaint": complaint,
            "check_result": validated,
            "check_reason": reason,
            "workflow_path": state.get("workflow_path", []) + ["intake"],
            "status": "intake",
        }
    
    return new_state

def validate_node(state: ComplaintState) -> ComplaintState:
    """Step 2: Validate - Check complaint detail against the selected category."""
    print("\n[VALIDATE] Checking complaint details...")

    complaint = state["complaint"]
    category = state.get("category", "other").strip().lower()

    # Validate complaint using LLM
    validation_prompt = f"""Approve or reject this Downside Up complaint according to these rules and the given category:
- Portal complaints are valid only if they reference specific location or timing anomalies
- Monster complaints require description of creature behavior or interactions
- Psychic complaints must reference specific ability limitations or malfunctions
- Environmental complaints need connection to electricity, weather, or observable physical phenomena
- Other category complaints must be rejected. Reason: escalation to manual evaluation needed.
- Complaints lacking sufficient detail to route properly must be rejected.

Complaint: {complaint}
Category: {category}

The answer is to be contained in two variables:
- validated: True if the complaint is valid, False if rejected.
- reason: if rejected, provide a brief explanation; if valid, return an empty string.
Respond exclusively in the following format: (validated, reason).
"""

    response = llm.invoke([HumanMessage(content=validation_prompt)])
    response_content = response.content.strip()
    validated, reason = ast.literal_eval(response_content)

    new_state = {
        **state,
        "workflow_path": state.get("workflow_path", []) + ["validate"],
        "validation_result": validated,
        "validation_reason": reason,
        "status": "validate",
    }

    if validated:
        print(f"[VALIDATE] Validation result: Approved request")
    if not validated:
        print(f"[VALIDATE] Validation result: Rejected request")
        if category == "other":
            print(f"[VALIDATE] Reason: The complaint could not be categorized and requires escalation to manual review.")
        else:
            print(f"[VALIDATE] Reason: {reason}")
    return new_state

def investigate_node(state: ComplaintState) -> ComplaintState:
    """Step 3: Investigate - Gather additional information about the complaint."""
    print("\n[INVESTIGATE] Gathering additional information...")

    complaint = state["complaint"]
    category = state.get("category", "other").strip().lower()

    # Only this node may use the research tools.
    from langchain_core.messages import HumanMessage, ToolMessage

    research_prompt = f"""Produce evidence for this Downside Up complaint based on the category:
- Portal issues: Investigate temporal patterns, location consistency, and environmental factors
- Monster issues: Gather behavioral data, interaction patterns, and environmental triggers
- Psychic issues: Document ability specifications, tested limitations, and contextual factors
- Environmental issues: Analyze power line activity, atmospheric conditions, and anomaly correlation

Complaint: {complaint}
Category: {category}

You may use these tools to gather information:
- check_hawkins_records(query)
- gather_party_wisdom(question)

Use the tools only inside this investigation step, then write a concise investigation report with relevant evidence, observations, or hypotheses related to the complaint.
"""

    research_llm = llm.bind_tools([check_hawkins_records, gather_party_wisdom])
    messages = [HumanMessage(content=research_prompt)]
    final_response = None

    for _ in range(5):
        response = research_llm.invoke(messages)
        final_response = response
        tool_calls = getattr(response, "tool_calls", None) or []

        if not tool_calls:
            break

        messages.append(response)

        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args", {}) or {}
            tool_id = tool_call.get("id")

            if tool_name == "check_hawkins_records":
                selected_tool = check_hawkins_records
                payload = tool_args if isinstance(tool_args, dict) else {"query": str(tool_args)}
            elif tool_name == "gather_party_wisdom":
                selected_tool = gather_party_wisdom
                payload = tool_args if isinstance(tool_args, dict) else {"question": str(tool_args)}
            else:
                selected_tool = None
                payload = None

            if selected_tool is None:
                tool_result = f"Tool '{tool_name}' is not available in investigate_node."
            else:
                tool_result = selected_tool.invoke(payload)

            messages.append(ToolMessage(content=str(tool_result), tool_call_id=tool_id))

    investigation_content = (final_response.content if final_response else "").strip()

    new_state = {
        **state,
        "workflow_path": state.get("workflow_path", []) + ["investigate"],
        "investigation_content": investigation_content,
        "status": "investigate",
    }

    print("\n" + "="*20 + " INFORMATION GATHERED " + "="*20)
    print(investigation_content)
    print("="*62)
    return new_state

def resolve_node(state: ComplaintState) -> ComplaintState:
    """Step 4: Resolve - Determine the appropriate resolution for the complaint."""
    print("\n[RESOLVE] Determining resolution...")

    complaint = state["complaint"]
    investigation_content = state.get("investigation_content", "")
    category = state.get("category", "other").strip().lower()

    # Validate complaint using LLM
    validation_prompt = f"""Assess if the investigation content provides sufficient evidence to resolve the complaint.
A relevant investigation should include some of these words: Records, Historical, Upside Down, Downside Up, Hawkins, Walvins, the D&D party (Mike, Dustin, Lucas, Will).

Complaint: {complaint}
Investigation Content: {investigation_content}

Respond ONLY with a predicted effectiveness rating: "high", "medium", or "low"
"""

    response = llm.invoke([HumanMessage(content=validation_prompt)])
    effectiveness_rating = response.content

    if category == "environmental" or category == "monster":
        escalation = random.choice([True, False])
    else:
        escalation = False

    new_state = {
        **state,
        "workflow_path": state.get("workflow_path", []) + ["resolve"],
        "effectiveness_rating": effectiveness_rating,
        "escalation": escalation,
        "resolved": True,
        "status": "resolve"
    }

    print(f"[RESOLVE] Rating of the gathered information: {effectiveness_rating}")
    if escalation:
        print("[RESOLVE] Review by specialized teams required!")
    return new_state

def close_node(state: ComplaintState) -> ComplaintState:
    print("\n[CLOSE] Finalizing complaint...")
    workflow_path = state.get("workflow_path", [])
    required_steps = ["intake", "validate", "investigate", "resolve"]
    wf_validated = all(step in workflow_path for step in required_steps)
    timestamp = datetime.now().isoformat(timespec="seconds")

    new_state = {
            **state,
            "workflow_path": state.get("workflow_path", []) + ["close"],
            "timestamp": timestamp,
            "status": "close",
            "resolved": wf_validated
        }

    print(f"[CLOSE] Workflow path: {" --> ".join(new_state['workflow_path'])}")
    print(f"[CLOSE] Veredict: {"Case closed." if (wf_validated or state.get("escalation")) else "Review by specialized teams required!"}")
    print(f"[CLOSE] Closing time: {timestamp}")
    return new_state
