#!/bin/bash
# Skill Activation Prompt Hook
# Triggered on UserPromptSubmit to suggest relevant skills based on prompt content

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RULES_FILE="$SCRIPT_DIR/../skills/skill-rules.json"

# Check if rules file exists
if [ ! -f "$RULES_FILE" ]; then
    exit 0
fi

# Read user prompt from stdin or environment
USER_PROMPT="${CLAUDE_PROMPT:-}"
if [ -z "$USER_PROMPT" ]; then
    read -r USER_PROMPT
fi

# Convert to lowercase for matching
PROMPT_LOWER=$(echo "$USER_PROMPT" | tr '[:upper:]' '[:lower:]')

# Initialize suggestions array
declare -a suggestions=()

# Function to check if keyword matches
check_keywords() {
    local skill_name="$1"
    local keywords="$2"
    
    for keyword in $keywords; do
        keyword_lower=$(echo "$keyword" | tr '[:upper:]' '[:lower:]')
        if [[ "$PROMPT_LOWER" == *"$keyword_lower"* ]]; then
            suggestions+=("$skill_name")
            return 0
        fi
    done
    return 1
}

# Check for backend-related content
BACKEND_KEYWORDS="fastapi uvicorn sqlalchemy pydantic supabase postgresql cors jwt auth router endpoint api database model crud schema migration bcrypt passlib backend python"
check_keywords "pulse-backend-guidelines" "$BACKEND_KEYWORDS"

# Check for frontend-related content
FRONTEND_KEYWORDS="next.js react app router shadcn tailwind next_public fetch useauth authprovider component page layout ssr client build npm pnpm frontend"
check_keywords "pulse-frontend-guidelines" "$FRONTEND_KEYWORDS"

# Check for extension-related content
EXTENSION_KEYWORDS="extension manifest service worker mv3 content script popup background chrome firefox sync storage permissions"
check_keywords "pulse-extension-guidelines" "$EXTENSION_KEYWORDS"

# Check for skill/infrastructure work
SKILL_KEYWORDS="skill agent hook command claude settings infrastructure"
check_keywords "skill-developer" "$SKILL_KEYWORDS"

# Output suggestions if any
if [ ${#suggestions[@]} -gt 0 ]; then
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  📚 SUGGESTED SKILLS                                         ║"
    echo "╠══════════════════════════════════════════════════════════════╣"
    
    # Remove duplicates and print
    printf '%s\n' "${suggestions[@]}" | sort -u | while read -r skill; do
        case "$skill" in
            "pulse-backend-guidelines")
                echo "║  ▸ pulse-backend-guidelines  (FastAPI/SQLAlchemy patterns)   ║"
                ;;
            "pulse-frontend-guidelines")
                echo "║  ▸ pulse-frontend-guidelines (Next.js/React patterns)        ║"
                ;;
            "pulse-extension-guidelines")
                echo "║  ▸ pulse-extension-guidelines (MV3 extension patterns)       ║"
                ;;
            "skill-developer")
                echo "║  ▸ skill-developer           (Meta: skill maintenance)       ║"
                ;;
        esac
    done
    
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
fi
