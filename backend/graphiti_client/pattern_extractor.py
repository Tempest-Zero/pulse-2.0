"""
Pattern extraction from Graphiti facts.

Graphiti stores data as natural language facts, not raw JSON.
We need to parse sentences like:
- "The Gym task is scheduled from 09:00 to 19:00"
- "test_user edited the task Gym"
- "The action for the Gym task is to move"
"""

import re
import json
from datetime import datetime
from typing import Optional
from .client import get_initialized_client


async def fetch_preferences(user_id: str, query: str):
    """Fetch preferences for a user from Graphiti."""
    try:
        client = await get_initialized_client()
        results = await client.search(
            query=query,
            group_ids=[user_id],
            num_results=20
        )
        return results
    except Exception as e:
        print(f"[fetch_preferences] Error: {e}")
        return []


# Regex patterns for extracting information from Graphiti facts
PATTERNS = {
    # "The Gym task is scheduled from 09:00 to 19:00"
    "time_range": re.compile(
        r"(?:the\s+)?(\w+(?:\s+\w+)*)\s+task\s+(?:is\s+)?scheduled\s+from\s+(\d{1,2}:\d{2})\s+to\s+(\d{1,2}:\d{2})",
        re.IGNORECASE
    ),
    # "The Gym task starts at 09:00"
    "task_starts": re.compile(
        r"(?:the\s+)?(\w+(?:\s+\w+)*)\s+task\s+starts\s+at\s+(\d{1,2}:\d{2})",
        re.IGNORECASE
    ),
    # "The Gym task ends at 19:00"
    "task_ends": re.compile(
        r"(?:the\s+)?(\w+(?:\s+\w+)*)\s+task\s+ends\s+at\s+(\d{1,2}:\d{2})",
        re.IGNORECASE
    ),
    # "test_user edited the Gym task to move from 09:00 to 19:00"
    "edited_with_times": re.compile(
        r"edited\s+(?:the\s+)?(\w+(?:\s+\w+)*)\s+task\s+to\s+move\s+from\s+(\d{1,2}:\d{2})\s+to\s+(\d{1,2}:\d{2})",
        re.IGNORECASE
    ),
    # "user moved Gym from 09:00 to 19:00"
    "moved": re.compile(
        r"moved\s+(?:the\s+)?(\w+(?:\s+\w+)*)\s+(?:task\s+)?from\s+(\d{1,2}:\d{2})\s+to\s+(\d{1,2}:\d{2})",
        re.IGNORECASE
    ),
    # "user edited the task Gym"
    "edited": re.compile(
        r"edited\s+(?:the\s+)?(?:task\s+)?(\w+(?:\s+\w+)*)",
        re.IGNORECASE
    ),
    # "prefers Gym at 19:00" or "prefers Gym in the evening"
    "prefers_time": re.compile(
        r"prefers?\s+(?:the\s+)?(\w+(?:\s+\w+)*)\s+(?:at|around)\s+(\d{1,2}:\d{2})",
        re.IGNORECASE
    ),
    # "avoids Gym at 09:00" or "doesn't want Gym in the morning"
    "avoids_time": re.compile(
        r"(?:avoids?|doesn'?t\s+want|not\s+want)\s+(?:the\s+)?(\w+(?:\s+\w+)*)\s+(?:at|around)\s+(\d{1,2}:\d{2})",
        re.IGNORECASE
    ),
    # "wake time is 07:00" or "wakes up at 7"
    "wake_time": re.compile(
        r"wakes?\s+(?:up\s+)?(?:at\s+)?(\d{1,2}:\d{2}|\d{1,2}(?:am|pm)?)",
        re.IGNORECASE
    ),
    # "sleep time is 22:00" or "goes to bed at 10pm"
    "sleep_time": re.compile(
        r"(?:sleep|bed|wind\s*down)\s+(?:time\s+)?(?:is\s+)?(?:at\s+)?(\d{1,2}:\d{2}|\d{1,2}(?:am|pm)?)",
        re.IGNORECASE
    ),
    # NEW PATTERNS for formats Graphiti produces:
    # "TaskName starts at 09:00" (no "task" keyword)
    "simple_starts": re.compile(
        r"^(\w+(?:\s+\w+)*)\s+starts\s+at\s+(\d{1,2}:\d{2})",
        re.IGNORECASE
    ),
    # "TaskName ends at 20:00" (no "task" keyword)
    "simple_ends": re.compile(
        r"^(\w+(?:\s+\w+)*)\s+ends\s+at\s+(\d{1,2}:\d{2})",
        re.IGNORECASE
    ),
    # "TaskName was edited by user" (passive voice)
    "was_edited": re.compile(
        r"^(\w+(?:\s+\w+)*)\s+was\s+edited\s+by\s+\w+",
        re.IGNORECASE
    ),
    # "TaskName involves the action move" - extract task name
    "involves_action": re.compile(
        r"^(\w+(?:\s+\w+)*)\s+involves\s+the\s+action\s+(move|edit)",
        re.IGNORECASE
    ),
}


def _extract_hour(time_str) -> Optional[int]:
    """Extract hour from time string like '09:00', '9am', '19:00', or int."""
    if time_str is None:
        return None
    
    if isinstance(time_str, int):
        return time_str
    
    if isinstance(time_str, float):
        return int(time_str)
    
    if not isinstance(time_str, str):
        return None
    
    time_str = time_str.strip().lower()
    
    # Handle "HH:MM" format
    if ":" in time_str:
        try:
            return int(time_str.split(":")[0])
        except ValueError:
            return None
    
    # Handle "9am", "9pm" format
    match = re.match(r"(\d{1,2})(am|pm)?", time_str)
    if match:
        hour = int(match.group(1))
        period = match.group(2)
        if period == "pm" and hour < 12:
            hour += 12
        elif period == "am" and hour == 12:
            hour = 0
        return hour
    
    return None


def _parse_fact(fact_text: str, context: dict) -> bool:
    """
    Parse a single Graphiti fact and update context.
    
    Returns True if the fact was successfully parsed.
    """
    if not fact_text or not isinstance(fact_text, str):
        return False
    
    parsed = False
    
    # Try to parse as time range (scheduled from X to Y)
    match = PATTERNS["time_range"].search(fact_text)
    if match:
        task_name = match.group(1).strip().lower()
        from_time = match.group(2)
        to_time = match.group(3)
        
        from_hour = _extract_hour(from_time)
        to_hour = _extract_hour(to_time)
        
        if task_name and from_hour is not None:
            if task_name not in context["patterns"]["avoided_times"]:
                context["patterns"]["avoided_times"][task_name] = []
            if from_hour not in context["patterns"]["avoided_times"][task_name]:
                context["patterns"]["avoided_times"][task_name].append(from_hour)
        
        if task_name and to_hour is not None:
            if task_name not in context["patterns"]["time_preferences"]:
                context["patterns"]["time_preferences"][task_name] = []
            if to_hour not in context["patterns"]["time_preferences"][task_name]:
                context["patterns"]["time_preferences"][task_name].append(to_hour)
        
        parsed = True
    
    # Try to parse as "task starts at X" (avoided time)
    match = PATTERNS["task_starts"].search(fact_text)
    if match:
        task_name = match.group(1).strip().lower()
        start_time = match.group(2)
        start_hour = _extract_hour(start_time)
        
        if task_name and start_hour is not None:
            if task_name not in context["patterns"]["avoided_times"]:
                context["patterns"]["avoided_times"][task_name] = []
            if start_hour not in context["patterns"]["avoided_times"][task_name]:
                context["patterns"]["avoided_times"][task_name].append(start_hour)
        
        parsed = True
    
    # Try to parse as "task ends at X" (preferred end time)
    match = PATTERNS["task_ends"].search(fact_text)
    if match:
        task_name = match.group(1).strip().lower()
        end_time = match.group(2)
        end_hour = _extract_hour(end_time)
        
        if task_name and end_hour is not None:
            if task_name not in context["patterns"]["time_preferences"]:
                context["patterns"]["time_preferences"][task_name] = []
            if end_hour not in context["patterns"]["time_preferences"][task_name]:
                context["patterns"]["time_preferences"][task_name].append(end_hour)
        
        parsed = True
    
    # Try to parse as "edited X task to move from Y to Z"
    match = PATTERNS["edited_with_times"].search(fact_text)
    if match:
        task_name = match.group(1).strip().lower()
        from_time = match.group(2)
        to_time = match.group(3)
        
        from_hour = _extract_hour(from_time)
        to_hour = _extract_hour(to_time)
        
        if task_name and from_hour is not None:
            if task_name not in context["patterns"]["avoided_times"]:
                context["patterns"]["avoided_times"][task_name] = []
            if from_hour not in context["patterns"]["avoided_times"][task_name]:
                context["patterns"]["avoided_times"][task_name].append(from_hour)
        
        if task_name and to_hour is not None:
            if task_name not in context["patterns"]["time_preferences"]:
                context["patterns"]["time_preferences"][task_name] = []
            if to_hour not in context["patterns"]["time_preferences"][task_name]:
                context["patterns"]["time_preferences"][task_name].append(to_hour)
        
        parsed = True
    
    # Try to parse as "moved X from Y to Z"
    match = PATTERNS["moved"].search(fact_text)
    if match:
        task_name = match.group(1).strip().lower()
        from_time = match.group(2)
        to_time = match.group(3)
        
        from_hour = _extract_hour(from_time)
        to_hour = _extract_hour(to_time)
        
        if task_name and from_hour is not None:
            if task_name not in context["patterns"]["avoided_times"]:
                context["patterns"]["avoided_times"][task_name] = []
            if from_hour not in context["patterns"]["avoided_times"][task_name]:
                context["patterns"]["avoided_times"][task_name].append(from_hour)
        
        if task_name and to_hour is not None:
            if task_name not in context["patterns"]["time_preferences"]:
                context["patterns"]["time_preferences"][task_name] = []
            if to_hour not in context["patterns"]["time_preferences"][task_name]:
                context["patterns"]["time_preferences"][task_name].append(to_hour)
        
        parsed = True
    
    # Try to parse preferences
    match = PATTERNS["prefers_time"].search(fact_text)
    if match:
        task_name = match.group(1).strip().lower()
        pref_time = match.group(2)
        pref_hour = _extract_hour(pref_time)
        
        if task_name and pref_hour is not None:
            if task_name not in context["patterns"]["time_preferences"]:
                context["patterns"]["time_preferences"][task_name] = []
            if pref_hour not in context["patterns"]["time_preferences"][task_name]:
                context["patterns"]["time_preferences"][task_name].append(pref_hour)
        
        parsed = True
    
    # Try to parse avoidances
    match = PATTERNS["avoids_time"].search(fact_text)
    if match:
        task_name = match.group(1).strip().lower()
        avoid_time = match.group(2)
        avoid_hour = _extract_hour(avoid_time)
        
        if task_name and avoid_hour is not None:
            if task_name not in context["patterns"]["avoided_times"]:
                context["patterns"]["avoided_times"][task_name] = []
            if avoid_hour not in context["patterns"]["avoided_times"][task_name]:
                context["patterns"]["avoided_times"][task_name].append(avoid_hour)
        
        parsed = True
    
    # Try to parse wake time
    match = PATTERNS["wake_time"].search(fact_text)
    if match:
        wake_time = match.group(1)
        wake_hour = _extract_hour(wake_time)
        if wake_hour is not None:
            context["defaults"]["wake_time"] = f"{wake_hour:02d}:00"
        parsed = True
    
    # Try to parse sleep time
    match = PATTERNS["sleep_time"].search(fact_text)
    if match:
        sleep_time = match.group(1)
        sleep_hour = _extract_hour(sleep_time)
        if sleep_hour is not None:
            context["defaults"]["sleep_time"] = f"{sleep_hour:02d}:00"
        parsed = True
    
    return parsed


def _try_parse_json(content: str, context: dict) -> bool:
    """
    Try to parse content as JSON (for backwards compatibility).
    
    Returns True if successfully parsed as JSON.
    """
    try:
        data = json.loads(content)
        
        # Handle user defaults format
        if data.get("type") == "user_defaults":
            if data.get("wake_time"):
                context["defaults"]["wake_time"] = data["wake_time"]
            if data.get("sleep_time"):
                context["defaults"]["sleep_time"] = data["sleep_time"]
            return True
        
        # Handle edit format
        if data.get("type") == "edit" or data.get("feedback_type") == "edited":
            edit_data = data.get("data", data)
            task_name = edit_data.get("task_name", "").lower()
            
            if not task_name:
                return False
            
            from_hour = _extract_hour(
                edit_data.get("from_time") or 
                edit_data.get("original_start_hour") or 
                edit_data.get("from_hour")
            )
            to_hour = _extract_hour(
                edit_data.get("to_time") or 
                edit_data.get("new_start_hour") or 
                edit_data.get("to_hour")
            )
            
            if from_hour is not None:
                if task_name not in context["patterns"]["avoided_times"]:
                    context["patterns"]["avoided_times"][task_name] = []
                context["patterns"]["avoided_times"][task_name].append(from_hour)
            
            if to_hour is not None:
                if task_name not in context["patterns"]["time_preferences"]:
                    context["patterns"]["time_preferences"][task_name] = []
                context["patterns"]["time_preferences"][task_name].append(to_hour)
            
            return True
        
        return False
        
    except (json.JSONDecodeError, TypeError, AttributeError):
        return False


async def get_user_context(user_id: str) -> dict:
    """
    Fetch complete user context from Graphiti.
    
    Handles both:
    1. Natural language facts (Graphiti's default output)
    2. JSON data (for backwards compatibility)
    
    Returns:
        {
            "defaults": {"wake_time": str|None, "sleep_time": str|None},
            "patterns": {"avoided_times": {task: [hours]}, "time_preferences": {task: [hours]}}
        }
    """
    context = {
        "defaults": {"wake_time": None, "sleep_time": None},
        "patterns": {"avoided_times": {}, "time_preferences": {}},
        "fetched_at": datetime.now().isoformat()
    }
    
    try:
        # Search for user preferences and edits
        results = await fetch_preferences(
            user_id,
            "task schedule time move edit preference wake sleep"
        )
        
        print(f"[pattern_extractor] Found {len(results)} results for user {user_id}")
        
        for result in results:
            # Get the fact content
            if hasattr(result, 'fact'):
                content = str(result.fact)
            elif isinstance(result, dict) and 'fact' in result:
                content = str(result['fact'])
            else:
                content = str(result)
            
            # Try JSON first (backwards compatibility)
            if _try_parse_json(content, context):
                print(f"[pattern_extractor] Parsed as JSON: {content[:50]}...")
                continue
            
            # Parse as natural language fact
            if _parse_fact(content, context):
                print(f"[pattern_extractor] Parsed as fact: {content[:50]}...")
            else:
                print(f"[pattern_extractor] Could not parse: {content[:50]}...")
        
        print(f"[pattern_extractor] Final context: {context}")
        
    except Exception as e:
        print(f"[pattern_extractor] Error fetching context: {e}")
    
    return context


# Alias for backward compatibility
async def get_user_defaults(user_id: str) -> dict:
    """Get user defaults only. Use get_user_context for full context."""
    context = await get_user_context(user_id)
    return context["defaults"]


async def extract_patterns(user_id: str) -> dict:
    """Get patterns only. Use get_user_context for full context."""
    context = await get_user_context(user_id)
    return context["patterns"]
