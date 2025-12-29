"""
LangGraph workflow for extraction with validation loop.

This graph handles:
- Loading user context from Graphiti
- Running structured extraction
- Validating results
- Re-prompting for missing information
- Applying defaults and finalizing
"""

from typing import TypedDict, Literal, Optional
from datetime import date, timedelta
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from .llm_extractor import extract_with_context


class ExtractionState(TypedDict):
    """
    Internal state for extraction workflow.
    
    This structure is for Python flow control only.
    The LLM never sees this TypedDict definition.
    """
    user_id: str
    messages: list  # Conversation history (HumanMessage, AIMessage)
    user_context: dict  # From Graphiti: {defaults, patterns}
    extracted_data: Optional[dict]
    validation_issues: list[str]
    attempt_count: int
    final_result: Optional[dict]


async def load_context_node(state: ExtractionState) -> dict:
    """Load user context from Graphiti."""
    from graphiti_client.resilient_client import resilient_client
    
    user_id = state.get("user_id", "default_user")
    user_context = await resilient_client.get_user_context(user_id)
    
    return {"user_context": user_context}


def extract_node(state: ExtractionState) -> dict:
    """
    Run LLM extraction and MERGE with previous extraction.
    
    This is critical because:
    1. LLM may not reliably re-extract ALL info from history
    2. We must preserve previously extracted data
    3. Only UPDATE fields that have new values
    """
    # === DIAGNOSTIC START ===
    print(f"[extract_node] === ENTERING EXTRACT NODE ===")
    print(f"[extract_node] state keys: {list(state.keys())}")
    print(f"[extract_node] extracted_data is None: {state.get('extracted_data') is None}")
    print(f"[extract_node] extracted_data type: {type(state.get('extracted_data'))}")
    if state.get('extracted_data'):
        prev_tasks = state['extracted_data'].get('tasks', [])
        print(f"[extract_node] Previous tasks: {[t.get('name') for t in prev_tasks]}")
        print(f"[extract_node] Previous wake_time: {state['extracted_data'].get('wake_time')}")
    else:
        print(f"[extract_node] NO PREVIOUS DATA!")
    # === DIAGNOSTIC END ===
    
    # Get the last user message
    user_messages = [m for m in state["messages"] if isinstance(m, HumanMessage)]
    if not user_messages:
        return {"extracted_data": state.get("extracted_data") or {"tasks": []}}
    
    last_input = user_messages[-1].content
    print(f"[extract_node] Last input: {last_input[:100]}...")
    
    # Build history (excluding last message)
    history = state["messages"][:-1] if len(state["messages"]) > 1 else None
    
    # Get PREVIOUS extraction (critical!)
    previous_data = state.get("extracted_data") or {}
    print(f"[extract_node] previous_data: {bool(previous_data)}, tasks: {len(previous_data.get('tasks', []))}")
    
    # Extract from new message
    new_data = extract_with_context(
        user_input=last_input,
        history=history,
        user_context=state.get("user_context", {})
    )
    print(f"[extract_node] new_data tasks: {[t.get('name') for t in new_data.get('tasks', [])]}")
    
    # MERGE new with previous instead of overwriting
    merged = _merge_extractions(previous_data, new_data)
    print(f"[extract_node] merged tasks: {[t.get('name') for t in merged.get('tasks', [])]}")
    print(f"[extract_node] merged wake_time: {merged.get('wake_time')}")
    
    return {"extracted_data": merged}


def _merge_extractions(previous: dict, new: dict) -> dict:
    """
    Merge new extraction with previous, preserving existing data.
    
    Rules:
    - Scalar fields (wake_time, sleep_time): new overrides if not None
    - Tasks: merge by name, update fields that have values
    - Fixed slots: merge by name
    - Preferences: new overrides if not None
    """
    if not previous:
        return new or {}
    if not new:
        return previous
    
    merged = {}
    
    # Scalar fields - new overrides only if it has a value
    merged["wake_time"] = new.get("wake_time") or previous.get("wake_time")
    merged["sleep_time"] = new.get("sleep_time") or previous.get("sleep_time")
    merged["is_past_description"] = new.get("is_past_description", False) or previous.get("is_past_description", False)
    
    # Merge tasks by name
    task_map = {}
    
    # Add all previous tasks
    for task in previous.get("tasks", []):
        name = task.get("name", "").lower().strip()
        if name:
            task_map[name] = task.copy()
    
    # Update/add from new extraction
    for task in new.get("tasks", []):
        name = task.get("name", "").lower().strip()
        if not name:
            continue
            
        if name in task_map:
            # Update existing task - only override non-None values
            existing = task_map[name]
            if task.get("estimated_time_hours") is not None:
                existing["estimated_time_hours"] = task["estimated_time_hours"]
                existing["is_vague"] = False  # No longer vague if we have duration
            if task.get("priority") and task["priority"] != "medium":
                existing["priority"] = task["priority"]
            if task.get("difficulty") and task["difficulty"] != "medium":
                existing["difficulty"] = task["difficulty"]
            if task.get("deadline"):
                existing["deadline"] = task["deadline"]
        else:
            # Add new task
            task_map[name] = task.copy()
    
    merged["tasks"] = list(task_map.values())
    
    # Merge fixed slots by name
    slot_map = {}
    for slot in previous.get("fixed_slots", []):
        name = slot.get("name", "").lower().strip()
        if name:
            slot_map[name] = slot.copy()
    for slot in new.get("fixed_slots", []):
        name = slot.get("name", "").lower().strip()
        if name:
            slot_map[name] = slot.copy()  # New overrides
    
    merged["fixed_slots"] = list(slot_map.values())
    
    # Merge preferences
    prev_prefs = previous.get("preferences") or {}
    new_prefs = new.get("preferences") or {}
    merged["preferences"] = {
        "energy_peak": new_prefs.get("energy_peak") or prev_prefs.get("energy_peak") or "morning",
        "mood": new_prefs.get("mood") or prev_prefs.get("mood") or "normal",
        "work_style": new_prefs.get("work_style") or prev_prefs.get("work_style") or "focused",
    }
    
    return merged


def validate_node(state: ExtractionState) -> dict:
    """Validate extracted data and identify issues."""
    data = state.get("extracted_data") or {}
    issues = []
    
    # Check if extraction completely failed
    if not data:
        issues.append("Extraction failed. Please try rephrasing your request.")
        return {"validation_issues": issues}
    
    # Check for extraction error
    if data.get("_error"):
        issues.append(f"Extraction failed: {data['_error']}")
        return {"validation_issues": issues}
    
    # Check for past description without tasks
    if data.get("is_past_description") and not data.get("tasks"):
        issues.append(
            "It sounds like you're describing what happened. "
            "What do you need to get done tomorrow?"
        )
        return {"validation_issues": issues}
    
    # Check for tasks
    if not data.get("tasks"):
        issues.append("I didn't catch any specific tasks. What do you need to accomplish tomorrow?")
        return {"validation_issues": issues}
    
    # Check durations - this is critical for scheduling
    tasks_missing_duration = []
    for task in data.get("tasks", []):
        if not task.get("estimated_time_hours"):
            tasks_missing_duration.append(task["name"])
    
    if tasks_missing_duration:
        if len(tasks_missing_duration) == 1:
            issues.append(f"⏱️ How long will '{tasks_missing_duration[0]}' take? (e.g., \"about 2 hours\")")
        elif len(tasks_missing_duration) <= 3:
            names = ", ".join(tasks_missing_duration)
            issues.append(f"⏱️ Time estimates needed: {names} (e.g., \"prompts 1hr, slides 30min, test 2hrs\")")
        else:
            names = ", ".join(tasks_missing_duration[:3])
            issues.append(f"⏱️ Time estimates needed for: {names}... (e.g., \"each task about 1-2 hours\")")
    
    # Check vague tasks
    vague_tasks = [t["name"] for t in data.get("tasks", []) if t.get("is_vague")]
    if vague_tasks:
        names = ", ".join(vague_tasks[:2])
        issues.append(f"🎯 Can you be more specific about: {names}?")
    
    # Check wake/sleep time (only if not in context)
    defaults = state.get("user_context", {}).get("defaults", {})
    if not data.get("wake_time") and not defaults.get("wake_time"):
        issues.append("🌅 What time do you usually wake up? (e.g., \"I wake up at 8am\")")
    
    return {"validation_issues": issues}


def should_continue(state: ExtractionState) -> Literal["reprompt", "finalize"]:
    """Decide whether to ask for more info or finalize."""
    if state["validation_issues"] and state["attempt_count"] < 3:
        return "reprompt"
    return "finalize"


def reprompt_node(state: ExtractionState) -> dict:
    """Generate follow-up questions."""
    issues = state["validation_issues"]
    
    # Format follow-up
    if len(issues) == 1:
        follow_up = issues[0]
    elif len(issues) <= 3:
        follow_up = "A few quick questions:\n• " + "\n• ".join(issues)
    else:
        follow_up = "Let's start with:\n• " + "\n• ".join(issues[:2])
    
    # Add AI message to history
    new_messages = list(state["messages"]) + [AIMessage(content=follow_up)]
    
    return {
        "messages": new_messages,
        "attempt_count": state["attempt_count"] + 1,
        # KEEP validation_issues so API knows response is incomplete
        # They will be re-evaluated in the next extraction cycle
    }


def finalize_node(state: ExtractionState) -> dict:
    """Apply defaults and prepare final result."""
    raw_data = state.get("extracted_data")
    
    # Handle None or empty extracted_data
    if not raw_data:
        return {"final_result": {
            "tasks": [],
            "fixed_slots": [],
            "wake_time": "09:00",
            "sleep_time": "22:00",
            "preferences": {"energy_peak": "morning", "mood": "normal"}
        }}
    
    data = dict(raw_data)  # Copy to avoid mutation
    user_context = state.get("user_context") or {}
    defaults = user_context.get("defaults", {})
    
    # Apply wake/sleep defaults
    if not data.get("wake_time"):
        data["wake_time"] = defaults.get("wake_time") or "09:00"
    if not data.get("sleep_time"):
        data["sleep_time"] = defaults.get("sleep_time") or "22:00"
    
    # Apply task defaults
    today = date.today()
    for task in data.get("tasks", []):
        if not task.get("priority"):
            task["priority"] = "medium"
        if not task.get("difficulty"):
            task["difficulty"] = "medium"
        if not task.get("estimated_time_hours"):
            task["estimated_time_hours"] = 1.0  # Default 1 hour
        if not task.get("deadline"):
            # High priority = today, others = tomorrow
            if task.get("priority") == "high":
                task["deadline"] = today.isoformat()
            else:
                task["deadline"] = (today + timedelta(days=1)).isoformat()
    
    # Ensure preferences exist
    if not data.get("preferences"):
        data["preferences"] = {"energy_peak": "morning", "mood": "normal"}
    
    return {"final_result": data}


def create_extraction_graph() -> StateGraph:
    """Create the extraction workflow graph."""
    workflow = StateGraph(ExtractionState)
    
    # Add nodes
    workflow.add_node("load_context", load_context_node)
    workflow.add_node("extract", extract_node)
    workflow.add_node("validate", validate_node)
    workflow.add_node("reprompt", reprompt_node)
    workflow.add_node("finalize", finalize_node)
    
    # Set entry point
    workflow.set_entry_point("load_context")
    
    # Add edges
    workflow.add_edge("load_context", "extract")
    workflow.add_edge("extract", "validate")
    workflow.add_conditional_edges(
        "validate",
        should_continue,
        {
            "reprompt": "reprompt",
            "finalize": "finalize"
        }
    )
    workflow.add_edge("reprompt", END)  # Return to API for user input
    workflow.add_edge("finalize", END)
    
    return workflow.compile()


# Compiled graph instance
extraction_graph = create_extraction_graph()
