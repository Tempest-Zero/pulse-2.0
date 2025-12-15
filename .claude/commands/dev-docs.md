# Dev-Docs Command

Create structured documentation for a new task using the 3-file system.

## Usage

```
/dev-docs <task-name>
```

## What This Creates

```
dev/
└── active/
    └── <task-name>/
        ├── plan.md      # What and why
        ├── context.md   # Research and decisions
        └── tasks.md     # Checklist of subtasks
```

## File Templates

### plan.md
```markdown
# [Task Name]

## Goal
[What we're building in 1-2 sentences]

## Why
[Reason for this work]

## Scope
- [ ] In scope: [item]
- [ ] Out of scope: [item]

## Success Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]

## Estimated Effort
[Small/Medium/Large] - [reason]
```

### context.md
```markdown
# Context: [Task Name]

## Research

### Findings
- [Finding 1]
- [Finding 2]

### Open Questions
- [ ] [Question 1]

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| [Topic] | [Choice] | [Why] |

## Blockers
- [ ] [Blocker if any]
```

### tasks.md
```markdown
# Tasks: [Task Name]

## Progress
- [x] Completed items
- [/] In progress
- [ ] Not started

## Phase 1: [Phase Name]
- [ ] Task 1
- [ ] Task 2

## Phase 2: [Phase Name]
- [ ] Task 3
- [ ] Task 4

## Verification
- [ ] Tests pass
- [ ] Build succeeds
- [ ] Deployed and verified
```

## When to Use

- Tasks requiring 10+ tool calls
- Multi-session work
- Complex features touching multiple components
- When you need to pause and resume later

## Output

After running this command, create the three files in `dev/active/<task-name>/`.
