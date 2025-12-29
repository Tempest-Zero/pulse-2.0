# Critical Debug Report - Pulse 2.0

**Generated:** 2025-12-29
**Branch:** `claude/restore-graphiti-folder-gJbNv`

---

## Executive Summary

The application has **major integration issues** - several modules exist but are **completely disconnected** from the main application. The frontend makes API calls to endpoints that either don't exist or have been removed.

---

## CRITICAL ISSUES

### 1. AI Router REMOVED but Frontend Depends On It

**Severity:** CRITICAL
**File:** `backend/main.py:144`

```python
# AI router removed  ← This comment indicates intentional removal
```

**But** `frontend/lib/api/ai.js` calls these endpoints:
- `GET /ai/recommendation`
- `POST /ai/feedback`
- `GET /ai/stats`
- `GET /ai/phase`
- `POST /ai/infer-feedback`
- `POST /ai/persist`
- `POST /ai/breakdown-task/{taskId}`
- `POST /ai/generate-schedule`

**Impact:** All AI features are broken. Frontend will get 404 errors.

**Fix Required:**
```python
# In backend/main.py, add:
from routers import ai_router  # Add to imports
app.include_router(ai_router)  # Add after line 148
```

---

### 2. Scheduler Module NOT Integrated

**Severity:** HIGH
**Location:** `/scheduler/` (root level)

The `scheduler/` module contains a complete OR-Tools constraint solver:
- `solver.py` - 604 lines of CP-SAT scheduling logic
- `models.py` - Pydantic schemas
- `soft_constraints.py` - Mood/preference handling
- `api.py` - Clean public API

**But `backend/routers/smart_schedule_router.py` uses PLACEHOLDER functions instead:**

```python
# Line 72-118: Placeholder parse_tasks_from_description()
# Line 121-183: Placeholder generate_schedule_with_solver()
# These ignore the actual OR-Tools solver!
```

**Impact:** Smart schedule feature uses basic sequential scheduling instead of optimized constraint solving.

**Fix Required:** Replace placeholder functions with imports from `scheduler/`:
```python
from scheduler import generate_schedule, ScheduleRequest
```

---

### 3. graphiti_client NOT Connected

**Severity:** HIGH
**Location:** `/graphiti_client/`

The Graphiti temporal knowledge graph client exists with:
- `client.py` - Neo4j + OpenAI initialization
- `resilient_client.py` - Fallback caching
- `pattern_extractor.py` - User preference learning
- `store.py` - Episode storage

**Zero imports anywhere in backend:**
```bash
$ grep -r "from graphiti_client" backend/
(no results)
```

**Impact:** User preference learning is disabled. No temporal memory.

---

### 4. langgraph_flow NOT Connected

**Severity:** HIGH
**Location:** `/langgraph_flow/`

The LangGraph extraction workflow exists with:
- `extraction_graph.py` - Multi-turn validation workflow
- `llm_extractor.py` - Structured LLM output
- `schemas.py` - Pydantic extraction schemas
- `prompts.py` - NLP extraction prompts

**Zero imports anywhere in backend:**
```bash
$ grep -r "from langgraph_flow" backend/
(no results)
```

**Impact:** NLP task extraction uses basic string splitting instead of LLM.

---

### 5. Root main.py References Missing Module

**Severity:** MEDIUM
**File:** `/main.py:8`

```python
from data.sample_input import sample_input  # ImportError!
```

**The `/data/` folder does not exist.** This is a standalone test script that can't run.

---

### 6. AI Module Import Path Issues

**Severity:** MEDIUM
**Files:** `backend/routers/ai_router.py`, `backend/ai/*.py`

Imports use relative paths assuming `backend/` is the working directory:
```python
from ai.config import AIConfig  # Works only if running from backend/
```

If running from project root, these will fail.

---

## Module Connectivity Matrix

| Module | Location | Imported By | Status |
|--------|----------|-------------|--------|
| `backend/ai/` | backend | `ai_router.py` | Router removed from main.py |
| `scheduler/` | root | `main.py` (test only) | NOT integrated with backend |
| `graphiti_client/` | root | `langgraph_flow/` | NOT integrated with backend |
| `langgraph_flow/` | root | Nothing | NOT integrated with backend |

---

## File-Level Issues

### Backend

| File | Issue | Line |
|------|-------|------|
| `main.py` | AI router removed but ai/ exists | 144 |
| `main.py` | Missing `from routers import ai_router` | 20 |
| `routers/smart_schedule_router.py` | Uses placeholder instead of scheduler/ | 72-183 |
| `tasks/background.py` | Empty periodic task loop | 58-62 |

### Frontend

| File | Issue |
|------|-------|
| `lib/api/ai.js` | Calls /ai/* endpoints that don't exist |
| `components/ai-recommendation.jsx` | May exist but router is disabled |

### Root Level

| File | Issue |
|------|-------|
| `main.py` | References non-existent `data.sample_input` |
| `scheduler/` | Isolated from backend |
| `graphiti_client/` | Isolated from backend |
| `langgraph_flow/` | Isolated from backend |

---

## Recommended Fix Order

### Phase 1: Critical (Backend Won't Serve Frontend)

1. **Re-enable AI router in `backend/main.py`:**
   ```python
   # Line 20: Add ai_router to imports
   from routers import tasks_router, schedule_router, ..., ai_router

   # After line 148: Include the router
   app.include_router(ai_router)
   ```

### Phase 2: High (Features Don't Work Properly)

2. **Integrate scheduler/ into smart_schedule_router.py:**
   - Move `scheduler/` into `backend/scheduler/` OR
   - Add root to Python path OR
   - Import from `sys.path` manipulation

3. **Integrate graphiti_client into backend:**
   - Create a router for preference endpoints
   - Wire into smart_schedule_router for learned constraints

4. **Integrate langgraph_flow for NLP extraction:**
   - Replace placeholder `parse_tasks_from_description()`
   - Use `extraction_graph` for multi-turn validation

### Phase 3: Cleanup

5. **Fix or remove root `main.py`:**
   - Either create `data/sample_input.py` OR
   - Delete the standalone test script

6. **Add missing environment variables to `.env.example`:**
   - `NEO4J_URI`
   - `NEO4J_USER`
   - `NEO4J_PASSWORD`
   - `OPENAI_API_KEY`

---

## Architectural Recommendation

The current structure has modules scattered at root level that should be inside `backend/`:

```
Current (Broken):
pulse-2.0/
├── backend/
│   ├── ai/          ✓ Correct location, but router disabled
│   ├── routers/
│   └── ...
├── graphiti_client/  ✗ Should be in backend/
├── langgraph_flow/   ✗ Should be in backend/
├── scheduler/        ✗ Should be in backend/
└── main.py           ✗ Orphaned test script

Recommended:
pulse-2.0/
├── backend/
│   ├── ai/
│   ├── graphiti_client/   ← Move here
│   ├── langgraph_flow/    ← Move here
│   ├── scheduler/         ← Move here
│   └── routers/
└── (no root main.py)
```

---

## Quick Verification Commands

```bash
# Check if AI router is enabled
grep -n "ai_router" backend/main.py

# Check if scheduler is imported
grep -r "from scheduler" backend/

# Check if graphiti is imported
grep -r "graphiti_client" backend/

# Check if langgraph is imported
grep -r "langgraph_flow" backend/

# Test backend startup
cd backend && python -c "from main import app; print('OK')"
```

---

## Summary

| Category | Count |
|----------|-------|
| Critical Issues | 2 |
| High Severity | 3 |
| Medium Severity | 2 |
| Total Integration Gaps | 4 modules |

**The app is structurally incomplete.** The modules exist but are not wired together.
