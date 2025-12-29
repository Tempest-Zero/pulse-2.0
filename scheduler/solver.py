"""OR-Tools constraint satisfaction scheduler with human-centered optimization.

Key design principles:
1. NO arbitrary duration inflation - trust user estimates
2. Soft constraints for lunch/buffers - flexible, not rigid
3. Task splitting for large tasks - better bin packing
4. Hard constraints only for: deadlines, no-overlap, user-specified fixed slots
"""

from ortools.sat.python import cp_model
from datetime import date

from .models import (
    ScheduleRequest,
    ScheduleResponse,
    ScheduledBlock,
    FixedSlot,
)
from .constraint import add_task_constraints
from .objective import build_objective
from .soft_constraints import build_soft_penalties, apply_mood_adjustment, add_learned_constraints
from .utils import time_to_minutes, minutes_to_time

# =============================================================================
# CONFIGURATION - Tunable Parameters (Fixes the core issue)
# =============================================================================

# Duration adjustments - NO arbitrary inflation
REALISM_FACTOR = 1.0          # Trust user estimates (was 1.2)
TRANSITION_BUFFER = 10        # 10-min gap between tasks for breathing room

# Soft constraint preferences (NOT hard blockers)
PREFERRED_MORNING_BUFFER = 15    # Preferred minutes after wake before first task
PREFERRED_SHUTDOWN_BUFFER = 30   # Preferred minutes before day end after last task

# Soft constraint penalties (per minute of violation)
LUNCH_OVERLAP_PENALTY = 50        # Penalty per minute of task overlapping lunch
MORNING_BUFFER_PENALTY = 30       # Penalty per minute before preferred start
SHUTDOWN_BUFFER_PENALTY = 30      # Penalty per minute after preferred end

# Task splitting configuration
MAX_CONTINUOUS_BLOCK = 120    # Split tasks longer than 2 hours
MIN_BLOCK_SIZE = 30           # Don't create blocks smaller than 30 min

# Deep work constraints
MAX_DEEP_WORK_BLOCKS = 3      # Slightly relaxed from 2
DEEP_WORK_DURATION = 90       # Each deep work block is 90 minutes

# Legacy constants (for backward compatibility, but not used as hard constraints)
MORNING_BUFFER_MINUTES = 0    # Tasks CAN start at day start (soft penalty instead)
SHUTDOWN_BUFFER = 0           # Tasks CAN end at day end (soft penalty instead)
BUFFER_MINUTES = TRANSITION_BUFFER  # Alias for backward compatibility


def generate_schedule(request: ScheduleRequest, learned_constraints: dict = None) -> ScheduleResponse:
    """
    Generate an optimized schedule from the request.

    Key changes from original:
    - NO auto-inserted lunch (handled as soft constraint)
    - NO hard morning/shutdown buffers (soft penalties instead)
    - Task splitting for better bin packing

    Args:
        request: ScheduleRequest with tasks, fixed slots, and preferences
        learned_constraints: Optional dict with avoid_time_slots and prefer_time_slots

    Returns:
        ScheduleResponse with status and scheduled blocks
    """
    # Parse day boundaries
    day_start = time_to_minutes(request.day_start_time)
    day_end = time_to_minutes(request.day_end_time)
    DAY_END = day_end - day_start

    # Calculate available capacity (only subtract user-specified fixed slots)
    fixed_slot_duration = sum(
        time_to_minutes(s.end_time) - time_to_minutes(s.start_time)
        for s in request.fixed_slots
        if s.name.lower() != "lunch"  # Don't count auto-lunch, we handle it softly
    )
    available_capacity = DAY_END - fixed_slot_duration

    # Calculate total task time (NO inflation - trust user estimates)
    total_task_minutes = sum(
        int(t.estimated_time_hours * 60) + TRANSITION_BUFFER
        for t in request.tasks
    )

    # Quick feasibility check
    if total_task_minutes > available_capacity:
        # Even with soft constraints, we can't fit more time than we have
        return _handle_overflow_simple(
            request, day_start, DAY_END, available_capacity,
            total_task_minutes, learned_constraints
        )

    # Try solving with soft constraints
    result = _solve_schedule_flexible(request, day_start, DAY_END, learned_constraints)

    if result.status in ("optimal", "feasible"):
        return result

    # Solver failed - shouldn't happen with soft constraints, but handle gracefully
    return _handle_overflow_simple(
        request, day_start, DAY_END, available_capacity,
        total_task_minutes, learned_constraints,
        reason="constraint conflicts"
    )


def _solve_schedule_flexible(
    request: ScheduleRequest,
    day_start: int,
    DAY_END: int,
    learned_constraints: dict = None
) -> ScheduleResponse:
    """
    Core solver with flexible (soft) constraints.

    Key design:
    - Tasks can overlap lunch (with penalty)
    - Tasks can start early/end late (with penalty)
    - Large tasks are split for better bin packing
    """
    # Build task list (no inflation)
    tasks = _build_task_list(request, day_start, DAY_END)

    # Split large tasks for better bin packing
    original_task_count = len(tasks)
    tasks = _maybe_split_tasks(tasks)
    tasks_were_split = len(tasks) > original_task_count

    # Apply mood adjustment (this is reasonable - low mood = slightly slower)
    apply_mood_adjustment(tasks, request.preferences.mood)

    # Convert user-specified fixed slots (NOT including auto-lunch)
    fixed_slots = []
    for slot in request.fixed_slots:
        if slot.name.lower() == "lunch":
            continue  # Skip - we handle lunch as soft constraint
        fixed_slots.append({
            "name": slot.name,
            "start": time_to_minutes(slot.start_time) - day_start,
            "end": time_to_minutes(slot.end_time) - day_start,
        })

    # Validate fixed slots don't overlap
    is_valid, error_msg = _validate_fixed_slots(request.fixed_slots)
    if not is_valid:
        return ScheduleResponse(status="infeasible", error=error_msg)

    # Build model
    model = cp_model.CpModel()

    # Fixed slot intervals (hard constraints - user specified)
    fixed_intervals = []
    for slot in fixed_slots:
        slot_start = model.NewIntVar(slot["start"], slot["start"], f"slot_start_{slot['name']}")
        slot_end = model.NewIntVar(slot["end"], slot["end"], f"slot_end_{slot['name']}")
        slot_interval = model.NewIntervalVar(
            slot_start, slot["end"] - slot["start"], slot_end, f"slot_{slot['name']}"
        )
        fixed_intervals.append(slot_interval)

    # Task constraints - NO morning buffer, NO shutdown buffer (those are soft)
    starts, ends, task_intervals = add_task_constraints(
        model, tasks, DAY_END,  # Full day range
        morning_buffer=0,       # No hard buffer
        add_no_overlap=False
    )

    # No overlap across tasks and fixed slots (HARD constraint)
    model.AddNoOverlap(fixed_intervals + task_intervals)

    # Add block ordering constraints if tasks were split
    if tasks_were_split:
        _add_block_ordering_constraints(model, tasks, starts, ends)

    # Collect all soft penalties
    all_penalties = []

    # 1. Energy peak matching (existing)
    energy_penalties = build_soft_penalties(
        model, tasks, starts, request.preferences, day_start
    )
    all_penalties.extend(energy_penalties)

    # 2. Soft lunch constraint (NEW - replaces hard FixedSlot)
    lunch_penalties = _add_soft_lunch_constraint(
        model, tasks, starts, ends, day_start, DAY_END
    )
    all_penalties.extend(lunch_penalties)

    # 3. Soft boundary preferences (NEW - replaces hard buffers)
    boundary_penalties = _add_soft_boundary_constraints(
        model, tasks, starts, ends, DAY_END
    )
    all_penalties.extend(boundary_penalties)

    # 4. Learned constraints from user history
    if learned_constraints:
        learned_penalties = add_learned_constraints(
            model, tasks, starts, ends, learned_constraints, day_start
        )
        all_penalties.extend(learned_penalties)

    # Build objective: minimize penalties + prioritize high priority tasks early
    build_objective(
        model, tasks, starts, ends, all_penalties,
        day_end=DAY_END,
        morning_buffer=0,  # No hard buffer in objective
        work_style=request.preferences.work_style
    )

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10.0
    solver.parameters.num_search_workers = 4
    status = solver.Solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        blocks = _build_schedule_blocks(solver, tasks, starts, ends, fixed_slots, day_start)
        return ScheduleResponse(
            status="optimal" if status == cp_model.OPTIMAL else "feasible",
            schedule=blocks
        )
    elif status == cp_model.INFEASIBLE:
        return ScheduleResponse(
            status="infeasible",
            error="Cannot find valid schedule - try removing some tasks"
        )
    else:
        return ScheduleResponse(
            status="infeasible",
            error=f"Solver timeout or error"
        )


def _build_task_list(request: ScheduleRequest, day_start: int, DAY_END: int) -> list:
    """
    Convert TaskInput to internal task dict format.

    Duration = raw estimate + transition buffer only.
    NO arbitrary realism factor.
    """
    tasks = []

    for task in request.tasks:
        # Calculate deadline in solver coordinates
        days_until = (task.deadline - request.date).days
        # For same-day deadline, use full day; for future, allow full day
        deadline_minutes = min((days_until + 1) * DAY_END, DAY_END)

        # Duration: raw time + small transition buffer
        raw_duration = int(task.estimated_time_hours * 60)
        duration = raw_duration + TRANSITION_BUFFER

        # Handle optional tasks
        priority = task.priority
        if task.is_optional:
            priority = "low"

        tasks.append({
            "name": task.name,
            "duration": duration,
            "original_duration": raw_duration,
            "deadline": deadline_minutes,
            "priority": priority,
            "difficulty": task.difficulty,
            "is_optional": task.is_optional,
        })

    return tasks


def _maybe_split_tasks(tasks: list, max_block: int = MAX_CONTINUOUS_BLOCK) -> list:
    """
    Split large tasks into smaller blocks for better bin packing.

    A 4-hour task becomes 2 x 2-hour blocks that must be scheduled in order.
    This allows the solver to fit work around lunch and other fixed slots.
    """
    result = []

    for task in tasks:
        if task["duration"] <= max_block:
            result.append(task)
        else:
            # Split into blocks
            total_duration = task["duration"]
            num_blocks = (total_duration + max_block - 1) // max_block

            # Distribute duration evenly
            base_block_size = total_duration // num_blocks
            remainder = total_duration % num_blocks

            for i in range(num_blocks):
                block_duration = base_block_size + (1 if i < remainder else 0)

                # Don't create tiny blocks
                if block_duration < MIN_BLOCK_SIZE and i > 0:
                    result[-1]["duration"] += block_duration
                    continue

                block = {
                    "name": f"{task['name']} (part {i+1}/{num_blocks})",
                    "duration": block_duration,
                    "original_duration": block_duration - TRANSITION_BUFFER,
                    "deadline": task["deadline"],
                    "priority": task["priority"],
                    "difficulty": task["difficulty"],
                    "is_optional": task.get("is_optional", False),
                    "_parent_task": task["name"],
                    "_block_index": i,
                    "_total_blocks": num_blocks,
                }
                result.append(block)

    return result


def _add_block_ordering_constraints(model, tasks: list, starts: list, ends: list):
    """Ensure split task blocks are scheduled in order."""
    parent_blocks = {}
    for i, task in enumerate(tasks):
        parent = task.get("_parent_task")
        if parent:
            if parent not in parent_blocks:
                parent_blocks[parent] = []
            parent_blocks[parent].append((task["_block_index"], i))

    for parent, blocks in parent_blocks.items():
        blocks.sort(key=lambda x: x[0])
        for j in range(len(blocks) - 1):
            _, current_idx = blocks[j]
            _, next_idx = blocks[j + 1]
            model.Add(ends[current_idx] <= starts[next_idx])


def _add_soft_lunch_constraint(
    model: cp_model.CpModel,
    tasks: list,
    starts: list,
    ends: list,
    day_start: int,
    DAY_END: int,
    lunch_start_hour: int = 12,
    lunch_end_hour: int = 13,
) -> list:
    """
    Add SOFT lunch constraint - penalize overlap but don't forbid it.

    Tasks CAN overlap lunch if necessary, but pay a penalty.
    """
    penalties = []

    # Convert lunch times to solver coordinates
    lunch_start = (lunch_start_hour * 60) - day_start
    lunch_end = (lunch_end_hour * 60) - day_start

    # Skip if lunch is outside the day window
    if lunch_end <= 0 or lunch_start >= DAY_END:
        return penalties

    # Clamp to valid range
    lunch_start = max(0, lunch_start)
    lunch_end = min(lunch_end, DAY_END)
    lunch_duration = lunch_end - lunch_start

    for i, task in enumerate(tasks):
        # Calculate overlap with lunch
        # overlap = max(0, min(end, lunch_end) - max(start, lunch_start))

        overlap_start = model.NewIntVar(0, DAY_END, f"lunch_ovl_start_{i}")
        model.AddMaxEquality(overlap_start, [starts[i], lunch_start])

        overlap_end = model.NewIntVar(0, DAY_END, f"lunch_ovl_end_{i}")
        model.AddMinEquality(overlap_end, [ends[i], lunch_end])

        raw_overlap = model.NewIntVar(-DAY_END, DAY_END, f"lunch_raw_ovl_{i}")
        model.Add(raw_overlap == overlap_end - overlap_start)

        actual_overlap = model.NewIntVar(0, lunch_duration, f"lunch_overlap_{i}")
        model.AddMaxEquality(actual_overlap, [raw_overlap, 0])

        penalty = model.NewIntVar(0, lunch_duration * LUNCH_OVERLAP_PENALTY, f"lunch_penalty_{i}")
        model.Add(penalty == actual_overlap * LUNCH_OVERLAP_PENALTY)

        penalties.append(penalty)

    return penalties


def _add_soft_boundary_constraints(
    model: cp_model.CpModel,
    tasks: list,
    starts: list,
    ends: list,
    DAY_END: int,
) -> list:
    """
    Add SOFT morning and shutdown buffer preferences.

    Penalize tasks that start too early or end too late, but don't forbid them.
    """
    penalties = []

    preferred_start = PREFERRED_MORNING_BUFFER
    preferred_end = DAY_END - PREFERRED_SHUTDOWN_BUFFER

    for i, task in enumerate(tasks):
        # Morning penalty: if start < preferred_start
        if preferred_start > 0:
            morning_violation = model.NewIntVar(0, preferred_start, f"morning_viol_{i}")
            morning_diff = model.NewIntVar(-DAY_END, preferred_start, f"morning_diff_{i}")
            model.Add(morning_diff == preferred_start - starts[i])
            model.AddMaxEquality(morning_violation, [morning_diff, 0])

            morning_penalty = model.NewIntVar(0, preferred_start * MORNING_BUFFER_PENALTY, f"morning_pen_{i}")
            model.Add(morning_penalty == morning_violation * MORNING_BUFFER_PENALTY)
            penalties.append(morning_penalty)

        # Shutdown penalty: if end > preferred_end
        if PREFERRED_SHUTDOWN_BUFFER > 0:
            shutdown_violation = model.NewIntVar(0, PREFERRED_SHUTDOWN_BUFFER, f"shutdown_viol_{i}")
            shutdown_diff = model.NewIntVar(-DAY_END, PREFERRED_SHUTDOWN_BUFFER, f"shutdown_diff_{i}")
            model.Add(shutdown_diff == ends[i] - preferred_end)
            model.AddMaxEquality(shutdown_violation, [shutdown_diff, 0])

            shutdown_penalty = model.NewIntVar(0, PREFERRED_SHUTDOWN_BUFFER * SHUTDOWN_BUFFER_PENALTY, f"shutdown_pen_{i}")
            model.Add(shutdown_penalty == shutdown_violation * SHUTDOWN_BUFFER_PENALTY)
            penalties.append(shutdown_penalty)

    return penalties


def _handle_overflow_simple(
    request: ScheduleRequest,
    day_start: int,
    DAY_END: int,
    available_capacity: int,
    total_task_minutes: int,
    learned_constraints: dict,
    reason: str = "time constraints"
) -> ScheduleResponse:
    """Handle overflow by removing lowest-priority tasks."""
    # Sort by priority (keep high priority, overflow low/optional first)
    sorted_tasks = sorted(
        request.tasks,
        key=lambda t: (
            t.deadline,
            {"high": 0, "medium": 1, "low": 2}[t.priority],
            t.is_optional,
        )
    )

    fittable = []
    overflow = []
    used_minutes = 0

    for task in sorted_tasks:
        task_minutes = int(task.estimated_time_hours * 60) + TRANSITION_BUFFER
        if used_minutes + task_minutes <= available_capacity:
            fittable.append(task)
            used_minutes += task_minutes
        else:
            overflow.append(task)

    if not fittable:
        return ScheduleResponse(
            status="infeasible",
            error=f"No tasks can fit. Total time ({total_task_minutes} min) exceeds capacity ({available_capacity} min)."
        )

    # Try scheduling fittable tasks
    partial_request = ScheduleRequest(
        tasks=fittable,
        fixed_slots=request.fixed_slots,
        preferences=request.preferences,
        day_start_time=request.day_start_time,
        day_end_time=request.day_end_time,
        date=request.date
    )

    result = _solve_schedule_flexible(partial_request, day_start, DAY_END, learned_constraints)

    if result.status in ("optimal", "feasible"):
        result.status = "partial"
        result.overflow_tasks = [t.name for t in overflow]
        result.error = f"Moved {len(overflow)} task(s) to tomorrow due to {reason}"

    return result


def _build_schedule_blocks(solver, tasks, starts, ends, fixed_slots, day_start):
    """Build schedule blocks from solver solution."""
    blocks = []
    for i, task in enumerate(tasks):
        start_mins = solver.Value(starts[i])
        end_mins = solver.Value(ends[i])

        reason = _build_reason(task, start_mins, fixed_slots)

        blocks.append(ScheduledBlock(
            task_name=task["name"],
            start_time=minutes_to_time(start_mins, day_start),
            end_time=minutes_to_time(end_mins, day_start),
            reason=reason,
        ))

    blocks.sort(key=lambda b: b.start_time)

    # Inject visible breaks and morning routine
    blocks = _inject_morning_routine(blocks, day_start)
    blocks = _inject_breaks(blocks, day_start)

    return blocks


def _inject_morning_routine(blocks: list, day_start: int) -> list:
    """Add morning routine block at start of day if there's a gap."""
    if not blocks:
        return blocks

    first_task_start = time_to_minutes(blocks[0].start_time)
    gap = first_task_start - day_start

    if gap >= 15:  # Only show if at least 15 min gap
        morning_block = ScheduledBlock(
            task_name="🌅 Morning Routine",
            start_time=minutes_to_time(0, day_start),
            end_time=minutes_to_time(gap, day_start),
            reason="Time for coffee, breakfast, and getting ready"
        )
        return [morning_block] + blocks

    return blocks


def _inject_breaks(blocks: list, day_start: int, min_break_minutes: int = 10) -> list:
    """Add visible break blocks between tasks when there's a gap."""
    if len(blocks) < 2:
        return blocks

    result = []
    for i, block in enumerate(blocks):
        result.append(block)

        if i < len(blocks) - 1:
            next_block = blocks[i + 1]
            current_end = time_to_minutes(block.end_time)
            next_start = time_to_minutes(next_block.start_time)
            gap = next_start - current_end

            if gap >= min_break_minutes:
                # Check if this is lunch time (around 12:00-13:00)
                if 720 <= current_end <= 780 or 720 <= next_start <= 780:
                    break_name = "🍽️ Lunch Break"
                    break_reason = "Time to eat and recharge"
                elif gap >= 60:
                    break_name = "🎯 Focus Break"
                    break_reason = "Longer break - good for a walk or personal task"
                else:
                    break_name = "☕ Break"
                    break_reason = "Rest and reset before next task"

                result.append(ScheduledBlock(
                    task_name=break_name,
                    start_time=block.end_time,
                    end_time=next_block.start_time,
                    reason=break_reason
                ))

    return result


def _build_reason(task: dict, start_mins: int, fixed_slots: list) -> str:
    """Build explanation for why task was scheduled at this time."""
    priority_reason = f"Scheduled as {task['priority']} priority task"

    if start_mins <= 15:
        return f"{priority_reason}, scheduled at start of day"

    for slot in fixed_slots:
        if abs(start_mins - slot["end"]) <= 5:
            return f"{priority_reason}, scheduled after {slot['name']}"

    return priority_reason


def _validate_fixed_slots(fixed_slots: list) -> tuple:
    """Check for overlapping fixed slots before solving."""
    for i, s1 in enumerate(fixed_slots):
        for s2 in fixed_slots[i + 1:]:
            s1_start = time_to_minutes(s1.start_time)
            s1_end = time_to_minutes(s1.end_time)
            s2_start = time_to_minutes(s2.start_time)
            s2_end = time_to_minutes(s2.end_time)

            if s1_end > s2_start and s2_end > s1_start:
                return False, f"Fixed slots overlap: '{s1.name}' conflicts with '{s2.name}'"

    return True, None
