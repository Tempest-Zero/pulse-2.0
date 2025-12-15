# Dev-Docs Workflow

> For complex multi-step tasks that span multiple sessions.

## When to Use

- Tasks requiring 10+ tool calls
- Multi-session work (context may be lost between sessions)
- Complex features touching multiple components

## Structure

```
dev/
└── active/
    └── <task-name>/
        ├── plan.md      # What we're building and why
        ├── context.md   # Research, decisions, blockers
        └── tasks.md     # Checklist of subtasks
```

## Lifecycle

1. **Start**: Create `dev/active/<task-name>/` with plan.md
2. **During**: Update context.md with decisions, tasks.md with progress
3. **Complete**: Move to `dev/completed/<task-name>/` or delete

## Example

```
dev/
└── active/
    └── add-auth-system/
        ├── plan.md       # JWT auth with bcrypt passwords
        ├── context.md    # Decision: use python-jose, passlib[bcrypt]
        └── tasks.md      # [x] Backend auth, [x] Frontend auth, [ ] Tests
```

## Best Practices

- Keep plan.md focused—one paragraph on "what" and "why"
- Update tasks.md as you complete each step
- Note blockers/decisions in context.md so future sessions remember
- Don't over-engineer—simple markdown is enough
