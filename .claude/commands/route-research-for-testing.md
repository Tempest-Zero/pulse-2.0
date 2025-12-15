# Route Research for Testing Command

Scan backend routers and generate a test coverage map.

## Usage

```
/route-research
```

## What This Does

1. Scans all routers in `backend/routers/`
2. Lists all endpoints with methods
3. Identifies auth requirements
4. Suggests test scenarios

## Output Format

```markdown
# API Route Coverage Report

## Summary
- Total Routers: X
- Total Endpoints: X
- Auth Required: X
- Public: X

## Router: [router_name]

### Endpoints

| Method | Path | Auth | Test Status |
|--------|------|------|-------------|
| GET | /endpoint | ✓ | ⬜ Not tested |
| POST | /endpoint | ✓ | ✅ Tested |

### Test Suggestions
1. [Test scenario for endpoint 1]
2. [Test scenario for endpoint 2]

---
```

## Routers to Scan

Based on Pulse 2.0 structure:
- `backend/routers/tasks_router.py`
- `backend/routers/schedule_router.py`
- `backend/routers/mood_router.py`
- `backend/routers/reflections_router.py`
- `backend/routers/ai_router.py`
- `backend/routers/auth_router.py`
- `backend/routers/extension_router.py`

## How to Identify Auth

Look for:
```python
Depends(get_current_user)  # Auth required
# No auth dependency        # Public endpoint
```

## Test File Mapping

| Router | Test File |
|--------|-----------|
| tasks_router.py | tests/test_tasks_*.py |
| schedule_router.py | tests/test_schedule_*.py |
| mood_router.py | tests/test_mood_*.py |
| reflections_router.py | tests/test_reflections_*.py |
| ai_router.py | tests/test_ai_*.py |

## Running Tests

```bash
# All tests
pytest backend/tests/

# Specific router
pytest backend/tests/test_tasks_routes.py -v
```
