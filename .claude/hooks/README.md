# Hooks Directory

Claude hooks for Pulse 2.0 - scripts triggered at specific points in the agent workflow.

## Active Hooks

| Hook | Trigger | Purpose |
|------|---------|---------|
| `skill-activation-prompt.sh` | UserPromptSubmit | Suggests relevant skills based on prompt |
| `post-tool-use-tracker.sh` | PostToolUse (Edit/Write) | Tracks edited files by component |

## Hook Types

### UserPromptSubmit
Runs BEFORE the agent processes a prompt. Use for:
- Skill suggestions
- Context injection
- Pre-validation

### PostToolUse
Runs AFTER a tool completes. Use for:
- File tracking
- Build checking (when enabled)
- State updates

### Stop (Not Enabled)
Runs to potentially halt execution. Use for:
- Build failure detection
- Test failure detection
- Critical error handling

**Note**: Stop hooks are disabled by default until verified working.

## State Directory

Hooks write state to `.claude/hooks/state/` which is gitignored:
- `edit-log.txt` - Recent edits with timestamps
- `backend-edits.txt` - Backend files edited
- `frontend-edits.txt` - Frontend files edited
- `extension-edits.txt` - Extension files edited

## Adding New Hooks

1. Create script in `.claude/hooks/`
2. Make executable: `chmod +x hook-name.sh`
3. Add to `.claude/settings.json` under appropriate trigger
4. Test before enabling

## Environment Variables

Hooks receive context via environment:
- `CLAUDE_PROMPT` - User's prompt text
- `CLAUDE_FILE_PATH` - File being edited (PostToolUse)
- `CLAUDE_TOOL` - Tool name being used
- `CLAUDE_VERBOSE` - Enable verbose output
