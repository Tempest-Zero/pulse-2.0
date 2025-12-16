"""
LLM Service for AI-Powered Schedule Generation
Integrates with Google Gemini for intelligent scheduling and task analysis.
"""

import os
import json
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from dataclasses import dataclass

# Try to import Gemini client
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


@dataclass
class ScheduleBlock:
    """A scheduled block of time."""
    task_id: Optional[int]
    title: str
    start_hour: float  # 9.5 = 9:30 AM
    duration_hours: float
    block_type: str  # 'task', 'break', 'focus', 'exercise'
    reasoning: str  # Why this was scheduled here
    energy_required: str  # 'high', 'medium', 'low'
    cognitive_load: str  # 'high', 'medium', 'low'


@dataclass
class TaskBreakdown:
    """A breakdown of a complex task into subtasks."""
    subtasks: List[Dict[str, Any]]
    reasoning: str
    estimated_total_time: float


class LLMService:
    """
    Service for LLM-powered AI features.

    Supports:
    - Google Gemini (gemini-1.5-flash)
    - Intelligent fallback when no API key available
    """

    def __init__(self):
        self.gemini_model = None
        self._init_clients()

    def _init_clients(self):
        """Initialize Gemini client."""
        gemini_key = os.getenv("GEMINI_API_KEY")

        if GEMINI_AVAILABLE and gemini_key:
            genai.configure(api_key=gemini_key)
            self.gemini_model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 2000,
                    "response_mime_type": "application/json"
                }
            )
            print("[LLM] Gemini client initialized")
        else:
            print("[LLM] No Gemini API key found - using intelligent fallback")

    def _call_llm(self, system_prompt: str, user_prompt: str, json_mode: bool = True) -> str:
        """
        Call Gemini with the given prompts.
        Falls back gracefully if no LLM is available.
        """
        if self.gemini_model:
            try:
                # Combine system and user prompts for Gemini
                full_prompt = f"{system_prompt}\n\n{user_prompt}"
                if json_mode:
                    full_prompt += "\n\nRespond with valid JSON only."
                
                response = self.gemini_model.generate_content(full_prompt)
                return response.text
            except Exception as e:
                print(f"[LLM] Gemini error: {e}")

        # No LLM available
        return None

    def generate_intelligent_schedule(
        self,
        tasks: List[Dict[str, Any]],
        fixed_blocks: List[Dict[str, Any]],
        user_context: Dict[str, Any],
        working_hours: tuple = (9.0, 20.0)
    ) -> List[ScheduleBlock]:
        """
        Generate an AI-optimized schedule using LLM.

        Args:
            tasks: List of pending tasks with priority, deadline, duration, etc.
            fixed_blocks: Existing fixed commitments (meetings, classes)
            user_context: User's current state (mood, energy, time of day)
            working_hours: Start and end hours for scheduling

        Returns:
            List of ScheduleBlock objects with intelligent placement
        """
        if not tasks:
            return []

        system_prompt = """You are an expert productivity coach and schedule optimizer.
Your job is to create an optimal daily schedule that maximizes productivity while respecting human cognitive limits.

Key principles:
1. **Energy Management**: Schedule high-cognitive tasks when energy is highest (usually morning)
2. **Ultradian Rhythms**: Humans work best in 90-minute focused blocks followed by breaks
3. **Task Batching**: Group similar tasks together to minimize context switching
4. **Deadline Awareness**: Prioritize urgent tasks but don't create panic
5. **Recovery Time**: Include breaks - productivity drops without rest
6. **Cognitive Load**: Don't schedule multiple high-complexity tasks back-to-back

Always respond with valid JSON in this format:
{
    "schedule": [
        {
            "task_id": 1 or null for breaks,
            "title": "Task or block name",
            "start_hour": 9.0,
            "duration_hours": 1.5,
            "block_type": "task|break|focus|exercise",
            "reasoning": "Why scheduled here",
            "energy_required": "high|medium|low",
            "cognitive_load": "high|medium|low"
        }
    ],
    "optimization_notes": "Overall strategy explanation",
    "warnings": ["Any scheduling concerns"]
}"""

        # Format tasks for the prompt
        tasks_info = []
        for t in tasks:
            task_info = {
                "id": t.get("id"),
                "title": t.get("title"),
                "priority": t.get("priority", 3),
                "duration_hours": t.get("duration", 1.0),
                "difficulty": t.get("difficulty", "medium"),
                "deadline": t.get("deadline"),
                "description": t.get("description", "")[:200]  # Truncate long descriptions
            }
            tasks_info.append(task_info)

        # Format fixed blocks
        fixed_info = []
        for b in fixed_blocks:
            fixed_info.append({
                "title": b.get("title"),
                "start_hour": b.get("start"),
                "duration_hours": b.get("duration"),
                "type": b.get("block_type", "fixed")
            })

        user_prompt = f"""Create an optimal schedule for today.

**Current Context:**
- Current time: {user_context.get('current_hour', 9)}:00
- User's energy level: {user_context.get('energy_level', 'medium')}
- User's mood: {user_context.get('mood', 'neutral')}
- Day of week: {user_context.get('day_of_week', 'monday')}
- Tasks completed today: {user_context.get('tasks_completed', 0)}

**Working Hours:** {working_hours[0]}:00 to {working_hours[1]}:00

**Fixed Commitments (cannot be moved):**
{json.dumps(fixed_info, indent=2)}

**Tasks to Schedule (in priority order):**
{json.dumps(tasks_info, indent=2)}

Create an optimized schedule that:
1. Respects all fixed commitments
2. Places high-priority and difficult tasks during peak energy times
3. Includes strategic breaks (15-20 min every 90 min of work)
4. Considers the user's current energy and mood
5. Groups similar tasks when possible
6. Leaves buffer time for unexpected tasks

Return the schedule as JSON."""

        response = self._call_llm(system_prompt, user_prompt, json_mode=True)

        if response:
            try:
                data = json.loads(response)
                blocks = []
                for item in data.get("schedule", []):
                    blocks.append(ScheduleBlock(
                        task_id=item.get("task_id"),
                        title=item.get("title", "Untitled"),
                        start_hour=float(item.get("start_hour", 9.0)),
                        duration_hours=float(item.get("duration_hours", 1.0)),
                        block_type=item.get("block_type", "task"),
                        reasoning=item.get("reasoning", ""),
                        energy_required=item.get("energy_required", "medium"),
                        cognitive_load=item.get("cognitive_load", "medium")
                    ))
                return blocks
            except (json.JSONDecodeError, KeyError) as e:
                print(f"[LLM] Failed to parse schedule response: {e}")

        # Fallback to intelligent rule-based scheduling
        return self._fallback_schedule(tasks, fixed_blocks, user_context, working_hours)

    def _fallback_schedule(
        self,
        tasks: List[Dict[str, Any]],
        fixed_blocks: List[Dict[str, Any]],
        user_context: Dict[str, Any],
        working_hours: tuple
    ) -> List[ScheduleBlock]:
        """
        Intelligent fallback scheduling when LLM is unavailable.
        Uses evidence-based productivity principles.
        """
        blocks = []
        start_hour, end_hour = working_hours

        # Build occupied time ranges from fixed blocks
        occupied = [(b.get("start", 0), b.get("start", 0) + b.get("duration", 1))
                   for b in fixed_blocks]

        # Sort tasks by priority (descending) and deadline (ascending)
        sorted_tasks = sorted(
            tasks,
            key=lambda t: (-t.get("priority", 3), t.get("deadline") or "9999-12-31")
        )

        # Determine peak hours based on time of day
        current_hour = user_context.get("current_hour", 9)
        energy = user_context.get("energy_level", "medium")

        # Morning (9-12) = peak for most people
        # Afternoon (13-15) = post-lunch dip
        # Late afternoon (15-18) = secondary peak

        def is_peak_hour(hour: float) -> bool:
            if 9 <= hour < 12:
                return True
            if 15 <= hour < 17:
                return True
            return False

        def get_cognitive_load(task: Dict) -> str:
            difficulty = task.get("difficulty", "medium")
            priority = task.get("priority", 3)
            if difficulty == "hard" or priority >= 4:
                return "high"
            elif difficulty == "easy" or priority <= 2:
                return "low"
            return "medium"

        # Separate high and low cognitive load tasks
        high_load_tasks = [t for t in sorted_tasks if get_cognitive_load(t) == "high"]
        other_tasks = [t for t in sorted_tasks if get_cognitive_load(t) != "high"]

        # Find available slots
        available_slots = []
        current_time = start_hour

        for occ_start, occ_end in sorted(occupied):
            if occ_start > current_time:
                available_slots.append((current_time, occ_start))
            current_time = max(current_time, occ_end)

        if current_time < end_hour:
            available_slots.append((current_time, end_hour))

        # Schedule high-load tasks during peak hours first
        slot_idx = 0
        slot_time = available_slots[0][0] if available_slots else start_hour
        work_since_break = 0.0

        def find_slot(task_duration: float) -> Optional[float]:
            nonlocal slot_idx, slot_time
            while slot_idx < len(available_slots):
                slot_start, slot_end = available_slots[slot_idx]
                available_time = slot_end - max(slot_time, slot_start)
                if available_time >= task_duration:
                    return max(slot_time, slot_start)
                slot_idx += 1
                if slot_idx < len(available_slots):
                    slot_time = available_slots[slot_idx][0]
            return None

        # Schedule all tasks with breaks
        all_tasks = []

        # Prioritize high-load tasks for peak hours
        for task in high_load_tasks:
            task["_cognitive_load"] = "high"
            all_tasks.append(task)
        for task in other_tasks:
            task["_cognitive_load"] = get_cognitive_load(task)
            all_tasks.append(task)

        for task in all_tasks:
            task_duration = task.get("duration", 1.0)
            cognitive_load = task.get("_cognitive_load", "medium")

            # Need a break?
            if work_since_break >= 1.5:  # 90-minute ultradian rhythm
                break_start = find_slot(0.25)  # 15-minute break
                if break_start is not None:
                    blocks.append(ScheduleBlock(
                        task_id=None,
                        title="Break - Recharge",
                        start_hour=break_start,
                        duration_hours=0.25,
                        block_type="break",
                        reasoning="Strategic break after 90 minutes of focused work",
                        energy_required="low",
                        cognitive_load="low"
                    ))
                    slot_time = break_start + 0.25
                    work_since_break = 0.0

            # Find slot for task
            task_start = find_slot(task_duration)
            if task_start is None:
                break  # No more available time

            # Determine reasoning based on context
            is_peak = is_peak_hour(task_start)
            if cognitive_load == "high" and is_peak:
                reasoning = "High-priority task scheduled during peak cognitive hours for optimal focus"
            elif cognitive_load == "high" and not is_peak:
                reasoning = "Important task - consider breaking into smaller chunks if energy is low"
            elif cognitive_load == "low":
                reasoning = "Light task scheduled to maintain productivity without draining energy"
            else:
                reasoning = "Balanced task placement based on priority and available time"

            blocks.append(ScheduleBlock(
                task_id=task.get("id"),
                title=task.get("title", "Untitled Task"),
                start_hour=task_start,
                duration_hours=task_duration,
                block_type="task",
                reasoning=reasoning,
                energy_required="high" if cognitive_load == "high" else "medium",
                cognitive_load=cognitive_load
            ))

            slot_time = task_start + task_duration
            work_since_break += task_duration

        return blocks

    def breakdown_task_intelligently(
        self,
        task: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> TaskBreakdown:
        """
        Use LLM to intelligently break down a complex task into subtasks.

        Args:
            task: The task to break down
            user_context: User's context for personalization

        Returns:
            TaskBreakdown with subtasks and reasoning
        """
        system_prompt = """You are an expert project manager and productivity coach.
Your job is to break down complex tasks into actionable, manageable subtasks.

Key principles:
1. **SMART Subtasks**: Each subtask should be Specific, Measurable, Achievable, Relevant, Time-bound
2. **Progressive Complexity**: Start with easier subtasks to build momentum
3. **Clear Dependencies**: Order subtasks logically
4. **Realistic Durations**: Most focused work sessions should be 25-90 minutes
5. **Action-Oriented**: Each subtask should start with a verb

Always respond with valid JSON in this format:
{
    "subtasks": [
        {
            "title": "Action-oriented subtask title",
            "description": "Brief description of what to do",
            "duration_hours": 0.5,
            "difficulty": "easy|medium|hard",
            "order": 1,
            "dependencies": []
        }
    ],
    "reasoning": "Explanation of the breakdown strategy",
    "estimated_total_time": 3.5,
    "tips": ["Helpful tips for completing this task"]
}"""

        user_prompt = f"""Break down this task into manageable subtasks:

**Task:**
- Title: {task.get('title')}
- Description: {task.get('description', 'No description provided')}
- Total estimated duration: {task.get('duration', 2)} hours
- Difficulty: {task.get('difficulty', 'medium')}
- Priority: {task.get('priority', 3)}/5
- Deadline: {task.get('deadline', 'No specific deadline')}

**User Context:**
- Current energy level: {user_context.get('energy_level', 'medium')}
- Tasks already completed today: {user_context.get('tasks_completed', 0)}
- Preferred work session length: {user_context.get('preferred_session_length', 45)} minutes

Create a breakdown that:
1. Has 3-6 subtasks (more for longer/complex tasks)
2. Each subtask is completable in one focused session
3. Builds momentum by starting with achievable steps
4. Accounts for the user's current energy level

Return the breakdown as JSON."""

        response = self._call_llm(system_prompt, user_prompt, json_mode=True)

        if response:
            try:
                data = json.loads(response)
                return TaskBreakdown(
                    subtasks=data.get("subtasks", []),
                    reasoning=data.get("reasoning", ""),
                    estimated_total_time=data.get("estimated_total_time", task.get("duration", 2))
                )
            except (json.JSONDecodeError, KeyError) as e:
                print(f"[LLM] Failed to parse breakdown response: {e}")

        # Fallback to intelligent rule-based breakdown
        return self._fallback_breakdown(task, user_context)

    def _fallback_breakdown(
        self,
        task: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> TaskBreakdown:
        """
        Intelligent fallback for task breakdown when LLM is unavailable.
        Uses templates based on task type detection.
        """
        title = task.get("title", "").lower()
        description = task.get("description", "").lower()
        total_duration = task.get("duration", 2)
        difficulty = task.get("difficulty", "medium")

        # Detect task type and apply appropriate template
        templates = {
            "research": [
                ("Define research questions", "Clarify what you need to find out", 0.25, "easy"),
                ("Gather sources", "Find relevant articles, papers, or resources", 0.5, "medium"),
                ("Review and take notes", "Read through sources and extract key information", 0.75, "medium"),
                ("Synthesize findings", "Combine information into coherent insights", 0.5, "hard"),
            ],
            "write": [
                ("Create outline", "Structure your main points and arguments", 0.25, "easy"),
                ("Write first draft", "Get your ideas down without editing", 0.5, "medium"),
                ("Revise and refine", "Improve structure and clarity", 0.5, "medium"),
                ("Edit and proofread", "Fix grammar, spelling, and polish", 0.25, "easy"),
            ],
            "develop": [
                ("Plan implementation", "Break down technical requirements", 0.25, "medium"),
                ("Set up environment", "Prepare tools and dependencies", 0.25, "easy"),
                ("Implement core functionality", "Build the main features", 1.0, "hard"),
                ("Test and debug", "Verify everything works correctly", 0.5, "medium"),
            ],
            "design": [
                ("Research inspiration", "Gather reference materials and examples", 0.25, "easy"),
                ("Create initial sketches", "Explore different concepts", 0.5, "medium"),
                ("Develop chosen concept", "Refine the best direction", 0.75, "hard"),
                ("Finalize and export", "Prepare final deliverables", 0.25, "easy"),
            ],
            "study": [
                ("Preview material", "Skim through to understand scope", 0.25, "easy"),
                ("Active reading/watching", "Engage deeply with the content", 0.75, "medium"),
                ("Take notes and summarize", "Document key concepts", 0.5, "medium"),
                ("Practice and review", "Test your understanding", 0.5, "medium"),
            ],
            "plan": [
                ("Define objectives", "Clarify goals and success criteria", 0.25, "easy"),
                ("Brainstorm options", "Generate possible approaches", 0.5, "medium"),
                ("Evaluate and decide", "Choose the best path forward", 0.25, "medium"),
                ("Create action items", "Define specific next steps", 0.25, "easy"),
            ],
        }

        # Find matching template
        detected_type = None
        combined_text = f"{title} {description}"

        for task_type in templates:
            if task_type in combined_text:
                detected_type = task_type
                break

        # Default template for unknown task types
        if not detected_type:
            templates["default"] = [
                ("Understand the task", "Review requirements and gather information", 0.25, "easy"),
                ("Plan approach", "Decide how to tackle the task", 0.25, "easy"),
                ("Execute main work", "Complete the core task activities", 1.0, "medium"),
                ("Review and finalize", "Check quality and wrap up", 0.25, "easy"),
            ]
            detected_type = "default"

        template = templates[detected_type]

        # Scale durations to match total task duration
        template_total = sum(t[2] for t in template)
        scale_factor = total_duration / template_total if template_total > 0 else 1

        subtasks = []
        for i, (sub_title, sub_desc, sub_dur, sub_diff) in enumerate(template, 1):
            subtasks.append({
                "title": f"{task.get('title', 'Task')} - {sub_title}",
                "description": sub_desc,
                "duration_hours": round(sub_dur * scale_factor, 2),
                "difficulty": sub_diff,
                "order": i,
                "dependencies": [i-1] if i > 1 else []
            })

        reasoning = f"Task identified as '{detected_type}' type. "
        reasoning += "Broken down using proven workflow template with progressive complexity. "
        reasoning += f"Adjusted durations to fit {total_duration} hour total estimate."

        return TaskBreakdown(
            subtasks=subtasks,
            reasoning=reasoning,
            estimated_total_time=total_duration
        )

    def get_smart_recommendation(
        self,
        user_state: Dict[str, Any],
        available_tasks: List[Dict[str, Any]],
        recent_activity: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get an AI-powered recommendation for what to do next.

        This goes beyond the Q-learning system by considering:
        - Natural language understanding of task descriptions
        - Complex context like recent activity patterns
        - Personalized advice based on user history
        """
        if not available_tasks:
            return {
                "action": "break",
                "reasoning": "No tasks available. Take this time to rest or plan ahead.",
                "confidence": 1.0
            }

        system_prompt = """You are a personal productivity AI assistant.
Analyze the user's current state and recommend the best action right now.

Consider:
1. User's energy and mood
2. Time of day and natural productivity rhythms
3. Task priorities and deadlines
4. Recent activity (avoid burnout from too much focus)
5. Task variety (mix up cognitive demands)

Respond with JSON:
{
    "recommended_task_id": 1 or null,
    "action_type": "deep_focus|light_task|break|exercise|reflect",
    "reasoning": "Personalized explanation for the user",
    "duration_minutes": 45,
    "tips": ["Helpful suggestions"],
    "confidence": 0.85
}"""

        # Format context
        tasks_summary = []
        for t in available_tasks[:10]:  # Limit to top 10
            tasks_summary.append({
                "id": t.get("id"),
                "title": t.get("title"),
                "priority": t.get("priority"),
                "duration": t.get("duration"),
                "deadline": str(t.get("deadline")) if t.get("deadline") else None
            })

        user_prompt = f"""What should the user do right now?

**Current State:**
- Time: {user_state.get('time_block', 'afternoon')} ({user_state.get('hour', 14)}:00)
- Energy: {user_state.get('energy_level', 'medium')}
- Mood: {user_state.get('mood', 'neutral')}
- Day: {user_state.get('day_of_week', 'weekday')}

**Recent Activity (last 2 hours):**
{json.dumps(recent_activity[-5:] if recent_activity else [], indent=2)}

**Available Tasks:**
{json.dumps(tasks_summary, indent=2)}

Recommend the best action considering their current state and workload."""

        response = self._call_llm(system_prompt, user_prompt, json_mode=True)

        if response:
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                pass

        # Fallback to simple recommendation
        return self._fallback_recommendation(user_state, available_tasks)

    def _fallback_recommendation(
        self,
        user_state: Dict[str, Any],
        available_tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fallback recommendation logic."""
        energy = user_state.get("energy_level", "medium")
        time_block = user_state.get("time_block", "afternoon")

        # Low energy or night = suggest break
        if energy == "low" or time_block == "night":
            return {
                "recommended_task_id": None,
                "action_type": "break",
                "reasoning": "Your energy is low. Taking a short break will help you recharge and be more productive.",
                "duration_minutes": 15,
                "tips": ["Step away from screens", "Take a short walk", "Have a healthy snack"],
                "confidence": 0.8
            }

        # Find highest priority task
        if available_tasks:
            sorted_tasks = sorted(available_tasks, key=lambda t: -t.get("priority", 3))
            top_task = sorted_tasks[0]

            if energy == "high" and time_block in ("morning", "afternoon"):
                return {
                    "recommended_task_id": top_task.get("id"),
                    "action_type": "deep_focus",
                    "reasoning": f"Your energy is high - perfect time to tackle '{top_task.get('title')}'",
                    "duration_minutes": 90,
                    "tips": ["Eliminate distractions", "Set a timer", "Take notes on progress"],
                    "confidence": 0.75
                }
            else:
                return {
                    "recommended_task_id": top_task.get("id"),
                    "action_type": "light_task",
                    "reasoning": f"Good time to make progress on '{top_task.get('title')}'",
                    "duration_minutes": 45,
                    "tips": ["Start with the easiest part", "Don't aim for perfection"],
                    "confidence": 0.65
                }

        return {
            "recommended_task_id": None,
            "action_type": "reflect",
            "reasoning": "No urgent tasks. Use this time to plan and organize.",
            "duration_minutes": 15,
            "tips": ["Review your goals", "Plan tomorrow", "Celebrate progress"],
            "confidence": 0.7
        }


# Singleton instance
_llm_service = None

def get_llm_service() -> LLMService:
    """Get or create the LLM service singleton."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
