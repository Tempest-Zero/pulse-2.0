# CLAUDE.md - Backend (FastAPI)

> **Purpose**: Backend-specific commands, structure, and gotchas.

## Folder Structure

```
backend/
├── main.py              # FastAPI app entry point, CORS config
├── core/
│   └── auth.py          # JWT tokens, password hashing (bcrypt)
├── routers/             # API endpoints
│   ├── auth_router.py   # /auth/* (signup, login, me)
│   ├── tasks_router.py  # /tasks/*
│   ├── schedule_router.py
│   ├── mood_router.py
│   ├── reflections_router.py
│   ├── smart_schedule_router.py  # 3-Layer AI: /api/extract, /api/schedule, /api/feedback
│   └── extension_router.py
├── models/              # SQLAlchemy ORM models
│   ├── base.py          # DB engine, init_db(), get_db()
│   ├── user.py
│   ├── task.py
│   └── ...
├── crud/                # Database CRUD operations
├── schema/              # Pydantic request/response schemas
├── langgraph_flow/      # Layer 1: Brain (LangGraph + LLM)
│   ├── extraction_graph.py  # Multi-turn extraction workflow
│   ├── llm_extractor.py     # OpenAI structured extraction
│   ├── schemas.py           # Pydantic schemas for extraction
│   └── prompts.py           # System prompts
├── scheduler/           # Layer 2: Solver (OR-Tools CP-SAT)
│   ├── solver.py            # Main constraint solver
│   ├── models.py            # Pydantic request/response models
│   ├── constraint.py        # Task constraints
│   ├── objective.py         # Optimization objectives
│   └── soft_constraints.py  # Learned constraints
├── graphiti_client/     # Layer 3: Memory (Graphiti + Neo4j)
│   ├── client.py            # Neo4j connection
│   ├── resilient_client.py  # Fallback wrapper
│   ├── store.py             # Episode storage
│   └── pattern_extractor.py # Pattern extraction from facts
├── migrations/          # SQL migration scripts
│   └── 001_add_auth_columns.sql
└── tests/               # Pytest test suite
```

## Commands

### Local Development

```bash
# Create virtual environment (first time)
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Unix

# Install dependencies
pip install -r requirements.txt

# Run dev server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Testing

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

### Production (Railway)

Configured in `railway.json` and `nixpacks.toml`:
```bash
# Start command (from railway.json)
/app/venv/bin/uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
```

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `DATABASE_URL` | PostgreSQL connection | `postgresql://...@pooler.supabase.com:6543/postgres` |
| `CORS_ORIGINS` | Allowed frontend origins | `https://pulse-20-production-314b.up.railway.app` |
| `JWT_SECRET_KEY` | JWT signing key | (generate secure random string) |
| `SQL_ECHO` | Log SQL queries | `false` |

**Note**: Use Supabase session pooler (port 6543), NOT direct connection (port 5432).

## Database

- **ORM**: SQLAlchemy 2.0
- **Connection**: Configured in `models/base.py`
- **Migrations**: SQL scripts in `migrations/` folder (run manually in Supabase SQL Editor)

### Running a Migration

1. Open Supabase Dashboard → SQL Editor
2. Paste contents of `migrations/001_add_auth_columns.sql`
3. Execute

## Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check (Railway uses this) |
| `/auth/signup` | POST | Create account |
| `/auth/login` | POST | Get JWT token |
| `/auth/me` | GET | Get current user (requires token) |
| `/api/extract` | POST | Layer 1: NLP extraction (LangGraph + LLM) |
| `/api/schedule` | POST | Layer 2: Schedule generation (OR-Tools) |
| `/api/feedback` | POST | Layer 3: Store feedback (Graphiti) |
| `/api/generate` | POST | Full pipeline: Extract + Schedule |
| `/api/status` | GET | Check status of all 3 layers |
| `/tasks` | GET/POST | Task management |

## Common Gotchas

### CORS Issues
- CORS middleware is in `main.py` lines 58-74
- Add frontend URLs to `CORS_ORIGINS` env var (comma-separated)
- No trailing slash on URLs

### Auth Dependencies
- `passlib[bcrypt]` requires Rust compiler on some platforms (handled by nixpacks)
- `email-validator` is required for Pydantic's `EmailStr` type

### Database Connection Issues
- Use session pooler URL (port 6543) for Supabase
- Connection pool exhaustion: check for unclosed sessions
- If `database: disconnected` in health check, verify `DATABASE_URL`

### Import Errors on Startup
- Check Railway deploy logs for missing dependencies
- Common: `email-validator`, `python-jose`, `passlib`
