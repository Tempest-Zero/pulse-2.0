# PULSE 2.0 - Critical Bug Fix Implementation Plan

## Executive Summary

After thorough analysis, the application has **fundamental architectural issues** that make it non-functional for multi-user use. The problems fall into three categories:

1. **Data Isolation (CRITICAL)**: All users see each other's data
2. **Schedule Generation (BROKEN)**: Frontend algorithm is flawed, no AI integration
3. **AI Integration (MISSING)**: AI module exists but isn't connected to schedule generation

---

## Issue #1: Multi-User Data Isolation (CRITICAL)

### Root Causes

| Problem | Location | Impact |
|---------|----------|--------|
| No auth on data endpoints | All routers except auth_router | Anyone can access all data |
| ScheduleBlock missing user_id | models/schedule.py | All users share same schedule |
| Reflection missing user_id | models/reflection.py | All users share same reflections |
| No user_id filtering | All router queries | Data leaks between users |
| SINGLE_USER_MODE=True | ai/config.py | All AI forced to user_id=1 |

### Fix Plan

#### Step 1: Update Models (backend/models/)

**schedule.py** - Add user_id:
```python
user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
```

**reflection.py** - Add user_id:
```python
user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
# Remove unique=True from date column (allow same date for different users)
```

#### Step 2: Add Auth to All Routers

Each data router needs:
```python
from core.auth import get_current_user
from models.user import User

@router.get("/")
def get_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ADD THIS
):
    # Filter by user
    query = db.query(Model).filter(Model.user_id == current_user.id)
```

Files to update:
- `routers/tasks_router.py`
- `routers/schedule_router.py`
- `routers/mood_router.py`
- `routers/reflections_router.py`
- `routers/ai_router.py`

#### Step 3: Disable Single-User Mode

**ai/config.py**:
```python
SINGLE_USER_MODE: bool = False  # Was True
```

---

## Issue #2: Schedule Generation (BROKEN)

### Root Causes

| Problem | Location | Impact |
|---------|----------|--------|
| Available slots not updated after each task | schedule/page.jsx:185-213 | Overlapping schedule blocks |
| No task_id on ScheduleBlock | models/schedule.py | Can't track which task is scheduled |
| Duration conversion fragile | lib/api/schedule.js:27-31 | Wrong durations for 8+ hour tasks |
| "AI Tips" are random strings | schedule/page.jsx:240-250 | Misleading users |

### Fix Plan

#### Step 1: Add task_id to ScheduleBlock

**models/schedule.py**:
```python
task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True, index=True)
```

#### Step 2: Fix Schedule Generation Algorithm

**schedule/page.jsx** - Replace generateSchedule():
```javascript
const generateSchedule = async () => {
  // 1. Clear existing task blocks
  await clearScheduleBlocks('task');

  // 2. Get all tasks to schedule
  const allTasks = tasks.flatMap(t => t.subtasks?.length ? t.subtasks : [t]);

  // 3. Track scheduled time ranges locally
  const scheduledRanges = [];

  // 4. Get fixed blocks to avoid
  const fixedBlocks = scheduleBlocks.filter(b => b.type !== 'task');
  fixedBlocks.forEach(b => scheduledRanges.push({start: b.start, end: b.start + b.duration}));

  // 5. Schedule each task, updating available time after each
  for (const task of allTasks) {
    const durationHours = task.duration / 60;
    const slot = findNextAvailableSlot(scheduledRanges, durationHours, 9.0, 20.0);

    if (slot) {
      await createScheduleBlock({
        title: task.name,
        start: slot.start,
        duration: durationHours,
        block_type: 'task',
        task_id: task.id  // NEW: Track source task
      });
      scheduledRanges.push({start: slot.start, end: slot.start + durationHours});
    }
  }
};
```

#### Step 3: Fix Duration Conversion

**lib/api/schedule.js** - Remove ambiguous conversion:
```javascript
// REMOVE this fragile logic:
// if (duration > 8) { duration = duration / 60; }

// REPLACE with explicit conversion:
// Frontend always passes minutes, convert to hours for backend
const backendData = {
  duration: blockData.duration / 60,  // Always convert minutes → hours
  ...
};
```

---

## Issue #3: AI Not Connected to Scheduling (MISSING)

### Root Causes

| Problem | Location | Impact |
|---------|----------|--------|
| AI only gives single recommendations | ai_router.py | Can't generate full schedules |
| No endpoint for AI schedule generation | - | Feature doesn't exist |
| DQN neural network never used | ai/dqn_agent.py | Dead code |
| Task breakdown is keyword matching | ai_router.py:346-392 | Not real AI |

### Fix Plan

#### Step 1: Create AI Schedule Generation Endpoint

**routers/ai_router.py** - Add new endpoint:
```python
@router.post("/generate-schedule")
def generate_ai_schedule(
    request: GenerateScheduleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a full day schedule using AI recommendations.

    1. Get user's fixed schedule blocks
    2. Get user's pending tasks
    3. For each available time slot:
       - Get AI recommendation for that context
       - If recommendation is DEEP_FOCUS or LIGHT_TASK, schedule matching task
       - If recommendation is BREAK, add break block
    4. Return complete schedule
    """
    # Get fixed blocks (classes, meetings)
    fixed_blocks = db.query(ScheduleBlock).filter(
        ScheduleBlock.user_id == current_user.id,
        ScheduleBlock.block_type.in_(['fixed', 'meeting'])
    ).all()

    # Get pending tasks
    tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.completed == False
    ).order_by(Task.priority.desc()).all()

    # Generate schedule
    schedule = []
    current_time = request.start_hour  # e.g., 9.0

    while current_time < request.end_hour:
        # Skip if in fixed block
        if is_in_fixed_block(current_time, fixed_blocks):
            current_time += 0.5
            continue

        # Get AI recommendation for this time slot
        recommendation = _recommender.get_recommendation(
            db, current_user.id, current_time=datetime.now()
        )

        # Schedule based on recommendation
        if recommendation.action in [ActionType.DEEP_FOCUS, ActionType.LIGHT_TASK]:
            task = recommendation.task
            if task:
                block = ScheduleBlock(
                    user_id=current_user.id,
                    task_id=task.id,
                    title=task.title,
                    start=current_time,
                    duration=min(task.duration, request.end_hour - current_time),
                    block_type='task'
                )
                schedule.append(block)
                current_time += block.duration
        elif recommendation.action == ActionType.BREAK:
            block = ScheduleBlock(
                user_id=current_user.id,
                title="Break",
                start=current_time,
                duration=0.25,  # 15 min break
                block_type='break'
            )
            schedule.append(block)
            current_time += 0.25
        else:
            current_time += 0.5

    # Save schedule to database
    for block in schedule:
        db.add(block)
    db.commit()

    return {"schedule": [b.to_dict() for b in schedule]}
```

#### Step 2: Connect Frontend to AI Endpoint

**lib/api/ai.js** - Add function:
```javascript
export async function generateAISchedule(startHour = 9.0, endHour = 20.0) {
  return apiRequest('/ai/generate-schedule', {
    method: 'POST',
    body: { start_hour: startHour, end_hour: endHour }
  });
}
```

**schedule/page.jsx** - Replace generateSchedule:
```javascript
import { generateAISchedule } from '@/lib/api/ai';

const generateSchedule = async () => {
  setIsGenerating(true);
  try {
    const result = await generateAISchedule(9.0, 20.0);
    await loadSchedule();  // Reload from backend
    toast({ title: "AI Schedule Generated", description: `Created ${result.schedule.length} blocks` });
  } catch (error) {
    toast({ title: "Error", description: error.message, variant: "destructive" });
  } finally {
    setIsGenerating(false);
  }
};
```

---

## Implementation Order

### Phase 1: Data Isolation (Day 1)
1. Add user_id to ScheduleBlock model
2. Add user_id to Reflection model
3. Run database migration
4. Add `Depends(get_current_user)` to all routers
5. Add user_id filtering to all queries
6. Set SINGLE_USER_MODE = False
7. Test: Different users see different data

### Phase 2: Schedule Generation Fix (Day 2)
1. Add task_id to ScheduleBlock model
2. Fix frontend slot tracking algorithm
3. Fix duration conversion
4. Update schedule API to accept task_id
5. Test: No overlapping blocks, tasks tracked

### Phase 3: AI Integration (Day 3)
1. Create `/ai/generate-schedule` endpoint
2. Connect frontend to new endpoint
3. Remove fake "AI Tips"
4. Add real AI-based tips from recommendation explanations
5. Test: AI actually generates personalized schedule

### Phase 4: Cleanup (Day 4)
1. Remove or document dead DQN code
2. Update seed script for new schema
3. Add API documentation
4. Final integration testing

---

## Files to Modify

### Backend (13 files)
- `models/schedule.py` - Add user_id, task_id
- `models/reflection.py` - Add user_id
- `models/base.py` - Update migrations
- `routers/tasks_router.py` - Add auth + filtering
- `routers/schedule_router.py` - Add auth + filtering + task_id
- `routers/mood_router.py` - Add auth + filtering
- `routers/reflections_router.py` - Add auth + filtering
- `routers/ai_router.py` - Add auth + generate-schedule endpoint
- `ai/config.py` - Disable single-user mode
- `seed_data.py` - Update for new schema

### Frontend (4 files)
- `app/schedule/page.jsx` - Fix generation algorithm, connect to AI
- `lib/api/schedule.js` - Fix duration, add task_id
- `lib/api/ai.js` - Add generateAISchedule()
- `lib/api/tasks.js` - Ensure auth headers sent

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Database migration breaks existing data | Backup first, add columns as nullable initially |
| Auth breaks frontend | Update frontend to handle 401s, redirect to login |
| AI schedule quality poor | Keep manual schedule option as fallback |
| Performance with many users | Add database indexes on user_id columns |

---

## Success Criteria

1. ✅ User A cannot see User B's tasks, schedule, moods, or reflections
2. ✅ Schedule generation creates non-overlapping blocks
3. ✅ Each schedule block tracks its source task
4. ✅ "Generate AI Schedule" actually uses AI recommendations
5. ✅ Subtasks from "Break Down" appear in generated schedule
6. ✅ No "[object Object]" or "block_id" validation errors
