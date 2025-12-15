# CLAUDE.md - Pulse 2.0 Project Memory

> **Purpose**: Project-specific context for AI coding agents. Keep this focused on commands, structure, and quirks—not generic best practices.

## Repo Map

```
Pulse 2.0/
├── backend/          # FastAPI Python backend (AI recommendation engine)
├── frontend/         # Next.js 16 React app (dashboard UI)
├── pulse-extension/  # Chrome/Firefox extension (activity tracking)
├── docs/             # Documentation and reports
└── DEPLOYMENT.md     # Railway deployment guide
```

Each component has its own `CLAUDE.md` with specific commands and patterns:
- **Backend**: [backend/CLAUDE.md](backend/CLAUDE.md)
- **Frontend**: [frontend/CLAUDE.md](frontend/CLAUDE.md)
- **Extension**: [pulse-extension/CLAUDE.md](pulse-extension/CLAUDE.md)

## Integration Points

| From | To | How |
|------|-----|-----|
| Frontend | Backend | `NEXT_PUBLIC_API_URL` env var → `frontend/lib/api/config.js` |
| Extension | Backend | `SYNC_CONFIG.API_ENDPOINT` in `pulse-extension/lib/sync-scheduler.js` |
| Backend | Database | `DATABASE_URL` env var (Supabase PostgreSQL, port 6543) |
| Backend | Auth | JWT tokens via `core/auth.py`, password hashing with bcrypt |

## Deployment

- **Platform**: Railway
- **Backend URL**: `https://back-end-304.up.railway.app`
- **Frontend URL**: `https://pulse-20-production-314b.up.railway.app`
- **Database**: Supabase PostgreSQL (session pooler on port 6543)
- **Branch**: `claude/ai-integration-frontend-aZVkP`

## Dev-Docs Workflow

For complex multi-step tasks, use the dev-docs pattern:

```
dev/
└── active/
    └── <task-name>/
        ├── plan.md      # What we're building and why
        ├── context.md   # Research, decisions, blockers
        └── tasks.md     # Checklist of subtasks
```

**When to use**: Any task requiring 10+ tool calls or spanning multiple sessions.

## Working Style Rules

1. **Small steps**: Make incremental changes, verify each works
2. **Don't leave builds broken**: Always verify `npm run build` / tests pass before finishing
3. **Commit often**: Use descriptive commit messages, push to trigger Railway deploys
4. **Check actual files**: Don't assume—grep/view files for actual values

## Common Cross-Component Issues

| Issue | Cause | Fix |
|-------|------|-----|
| CORS errors | Frontend origin not in `CORS_ORIGINS` | Add to Railway env vars, redeploy backend |
| 404 on API | Wrong `NEXT_PUBLIC_API_URL` | Check `frontend/.env.production` |
| Extension sync fails | Hardcoded localhost in extension | Check `sync-scheduler.js` line 12 |
| Auth 401 | Missing/expired JWT token | Check token in localStorage |
| DB disconnected | Wrong `DATABASE_URL` or port | Use Supabase session pooler (port 6543) |
