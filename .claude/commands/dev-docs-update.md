# Dev-Docs Update Command

Update existing dev-docs for a task in progress.

## Usage

```
/dev-docs-update <task-name>
```

## What This Does

1. Reads existing files in `dev/active/<task-name>/`
2. Updates based on current status
3. Marks completed items
4. Adds new blockers or context

## Update Patterns

### Completing Tasks (tasks.md)
```diff
- [ ] Implement authentication
+ [x] Implement authentication
```

### Adding In-Progress Items
```diff
- [ ] Fix frontend build
+ [/] Fix frontend build
```

### Adding Blockers (context.md)
```markdown
## Blockers
- [x] ~~Previous blocker~~ (resolved)
- [ ] New blocker: [description]
```

### Adding Decisions (context.md)
```markdown
| Database | PostgreSQL session pooler | Supabase requires port 6543 |
```

### Updating Progress Summary (tasks.md)
```markdown
## Progress
- [x] Phase 1 complete (5/5 tasks)
- [/] Phase 2 in progress (2/4 tasks)
- [ ] Phase 3 not started
```

## Workflow

1. Check what has been done since last update
2. Mark completed tasks in tasks.md
3. Add any new findings to context.md
4. Update blockers if any
5. Optionally revise plan.md if scope changed

## When to Use

- Pausing work for the day
- Before a context reset
- After completing a major phase
- When encountering a blocker

## Archive Completed Tasks

When fully done:
```bash
# Move to completed
mv dev/active/<task-name> dev/completed/<task-name>
```

Or delete if not needed for reference:
```bash
rm -rf dev/active/<task-name>
```
