# Pulse Backend Guidelines

> FastAPI + SQLAlchemy + Supabase patterns for the Pulse 2.0 backend.

## Purpose

Provides guidance for working with the Python backend: API endpoints, database models, authentication, and AI recommendation system.

## When to Use

- [ ] Adding/modifying API endpoints in `routers/`
- [ ] Creating/updating SQLAlchemy models in `models/`
- [ ] Writing CRUD operations in `crud/`
- [ ] Working with Pydantic schemas in `schema/`
- [ ] Debugging database connections or CORS issues
- [ ] Modifying the AI recommendation engine in `ai/`

## Quick Rules

### Project Structure
```
backend/
├── main.py              # FastAPI app, CORS config, router includes
├── core/auth.py         # JWT tokens, password hashing (bcrypt)
├── routers/             # API endpoints (one file per domain)
├── models/              # SQLAlchemy ORM models
├── crud/                # Database operations
├── schema/              # Pydantic request/response schemas
├── ai/                  # RL-based recommendation engine
├── migrations/          # SQL migration scripts
└── tests/               # Pytest test suite
```

### Commands (Verified)
```bash
# Local development
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Production (from railway.json)
/app/venv/bin/uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
```

### Environment Variables
| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection (use Supabase session pooler, port 6543) |
| `CORS_ORIGINS` | Comma-separated allowed origins |
| `JWT_SECRET_KEY` | JWT signing key |

### Database Patterns
- **ORM**: SQLAlchemy 2.0 with `Session` from `models/base.py`
- **Connection**: Use `get_db()` dependency for request-scoped sessions
- **Pooling**: Supabase session pooler on port 6543 (NOT 5432)

### Authentication
- JWT tokens via `python-jose`
- Password hashing via `passlib[bcrypt]`
- `email-validator` required for Pydantic `EmailStr`

## Common Gotchas

| Issue | Cause | Fix |
|-------|-------|-----|
| CORS 403 | Origin not in CORS_ORIGINS | Add frontend URL to env var |
| DB disconnected | Wrong port (5432 vs 6543) | Use session pooler port 6543 |
| ImportError on startup | Missing dependency | Check requirements.txt |
| 422 Validation Error | Schema mismatch | Compare request body to Pydantic schema |

## Resources

- [patterns.md](resources/patterns.md) - Code patterns and examples
- [api-reference.md](resources/api-reference.md) - Endpoint documentation
