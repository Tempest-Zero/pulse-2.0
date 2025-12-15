# Agents Directory

Agents are autonomous prompt templates for multi-step work in Pulse 2.0.

## Available Agents

| Agent | Purpose |
|-------|---------|
| `code-architecture-reviewer.md` | Review code structure and integration points |
| `backend-error-fixer.md` | Diagnose and fix FastAPI/Python errors |
| `frontend-error-fixer.md` | Diagnose and fix Next.js build/runtime issues |
| `deployment-debugger.md` | Railway + Supabase deployment issues |
| `documentation-architect.md` | Write/update documentation |
| `plan-reviewer.md` | Critique plans for feasibility |
| `web-research-specialist.md` | Research obscure errors |

## Using Agents

Agents are invoked by referencing them in your prompt:

```
@agent:backend-error-fixer

I'm seeing this error: [paste error]
```

Or by asking Claude to "use the X agent for this".

## Agent Structure

Each agent `.md` file contains:
1. **Purpose** - What the agent does
2. **Inputs Expected** - What you should provide
3. **Method** - Step-by-step approach
4. **Output Format** - What to expect back
5. **Do Not Guess Rules** - Accuracy constraints

## Creating New Agents

1. Create `agent-name.md` in this directory
2. Follow the structure above
3. Include Pulse-specific context (file paths, commands)
4. Add "do not guess" rules for safety
