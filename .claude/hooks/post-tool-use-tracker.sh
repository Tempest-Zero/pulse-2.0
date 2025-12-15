#!/bin/bash
# Post Tool Use Tracker Hook
# Tracks edited files and categorizes them by component

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE_DIR="$SCRIPT_DIR/state"

# Create state directory if it doesn't exist
mkdir -p "$STATE_DIR"

# Get the file path from environment or arguments
FILE_PATH="${CLAUDE_FILE_PATH:-$1}"

if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# Determine component based on path
COMPONENT=""
if [[ "$FILE_PATH" == *"backend/"* ]]; then
    COMPONENT="backend"
elif [[ "$FILE_PATH" == *"frontend/"* ]]; then
    COMPONENT="frontend"
elif [[ "$FILE_PATH" == *"pulse-extension/"* ]]; then
    COMPONENT="extension"
elif [[ "$FILE_PATH" == *".claude/"* ]]; then
    COMPONENT="infrastructure"
else
    COMPONENT="other"
fi

# Timestamp
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Log the edit
LOG_FILE="$STATE_DIR/edit-log.txt"
echo "[$TIMESTAMP] [$COMPONENT] $FILE_PATH" >> "$LOG_FILE"

# Update component-specific tracking
COMPONENT_FILE="$STATE_DIR/${COMPONENT}-edits.txt"
echo "$FILE_PATH" >> "$COMPONENT_FILE"

# Keep logs manageable (last 100 entries)
if [ -f "$LOG_FILE" ]; then
    tail -n 100 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
fi

# Output summary (optional, can be suppressed)
if [ "${CLAUDE_VERBOSE:-false}" = "true" ]; then
    echo "📝 Tracked: $FILE_PATH ($COMPONENT)"
fi
