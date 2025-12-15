# Skill Developer (Meta Skill)

> Guidelines for creating and maintaining Claude skills in this repository.

## Purpose

Provides guidance for creating, updating, and organizing skills under `.claude/skills/`.

## When to Use

- [ ] Creating a new skill for a domain area
- [ ] Updating skill triggers in `skill-rules.json`
- [ ] Refactoring skill content into resources
- [ ] Adding new agents or commands

## Skill Structure

```
.claude/skills/
├── skill-rules.json           # Trigger definitions
├── README.md                   # Skills overview
└── <skill-name>/
    ├── SKILL.md                # Main guidance (<500 lines)
    └── resources/              # Detailed reference files
        ├── patterns.md
        ├── examples.md
        └── api-reference.md
```

## Creating a New Skill

### Step 1: Add to skill-rules.json

```json
{
    "id": "my-new-skill",
    "name": "My New Skill",
    "path": ".claude/skills/my-new-skill/SKILL.md",
    "enforcement": "suggest",
    "triggers": {
        "paths": ["path/to/files/**/*.ext"],
        "keywords": ["keyword1", "keyword2"],
        "intentPatterns": ["pattern.*match"]
    },
    "priority": 1
}
```

### Step 2: Create SKILL.md

Required sections:
1. **Title** - Name with brief description
2. **Purpose** - 1 paragraph explaining the skill
3. **When to Use** - Checklist of scenarios
4. **Quick Rules** - Essential guidance
5. **Common Gotchas** - Known issues table
6. **Resources** - Links to detail files

### Step 3: Add Resources (if needed)

Create `resources/` directory when:
- SKILL.md exceeds ~300 lines
- Complex patterns need examples
- API references are extensive

## Skill Content Rules

- Keep SKILL.md under 500 lines
- Use tables for structured data
- Include code examples inline when short
- Move long examples to resources
- Never invent paths/commands—verify from repo

## skill-rules.json Schema

```json
{
    "id": "unique-skill-id",
    "name": "Human Readable Name",
    "path": ".claude/skills/skill-id/SKILL.md",
    "enforcement": "suggest|require|block",
    "triggers": {
        "paths": ["glob/patterns/**/*"],
        "keywords": ["trigger", "words"],
        "intentPatterns": ["regex.*patterns"]
    },
    "priority": 1
}
```

## Enforcement Levels

| Level | Behavior |
|-------|----------|
| `suggest` | Display as recommendation (default) |
| `require` | Must acknowledge before proceeding |
| `block` | Hard stop until skill is followed |

**Always use `suggest` for new skills** until validated.
