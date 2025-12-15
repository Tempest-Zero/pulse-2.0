# Skills Directory

Skills are modular knowledge packages that provide context-specific guidance to AI agents working in this repo.

## How Skills Work

1. **Trigger**: When you submit a prompt, `.claude/hooks/skill-activation-prompt.sh` reads `skill-rules.json`
2. **Match**: Your prompt is matched against file paths, keywords, and intent patterns
3. **Suggest**: Matching skills are displayed before processing begins
4. **Apply**: The agent can reference the SKILL.md for domain-specific guidance

## Available Skills

| Skill | Triggers On | Purpose |
|-------|-------------|---------|
| `pulse-backend-guidelines` | `backend/**`, FastAPI keywords | Python/FastAPI patterns, DB, auth |
| `pulse-frontend-guidelines` | `frontend/**`, Next.js keywords | React/Next.js patterns, API client |
| `pulse-extension-guidelines` | `pulse-extension/**`, MV3 keywords | Chrome extension patterns |
| `skill-developer` | `.claude/**`, skill keywords | Creating/updating skills |

## Skill Structure

```
skills/
├── skill-rules.json          # Trigger definitions
├── README.md                  # This file
└── <skill-name>/
    ├── SKILL.md               # Main guidance (<500 lines)
    └── resources/             # Detailed reference files
        ├── patterns.md
        └── examples.md
```

## Creating New Skills

1. Add entry to `skill-rules.json` with triggers
2. Create `<skill-name>/SKILL.md` with:
   - Purpose (1 paragraph)
   - When to Use (checklist)
   - Quick Rules (bullet list)
   - Resources list (if detail needed)
3. Add `resources/` only if main file exceeds ~300 lines

## Enforcement Levels

- `suggest`: Display as recommendation (default for all Pulse skills)
- `require`: Must acknowledge before proceeding
- `block`: Prevents action without following skill

All Pulse skills use `suggest` to avoid blocking workflows.
