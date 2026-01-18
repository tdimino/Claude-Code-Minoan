#!/bin/bash
# cc-sessions-fzf.sh - Interactive Claude Code session picker with tmux integration
# Combines Claude history with tmux session awareness
#
# Usage: cc-sessions-fzf.sh [limit]
# Keys:
#   Enter   - Resume session in tmux (creates/attaches session, runs claude --resume)
#   Ctrl-O  - Open project in VSCode/Cursor
#   Ctrl-T  - Attach to existing tmux session only (no Claude resume)
#   Ctrl-Y  - Copy session ID to clipboard
#   Ctrl-D  - Show full session details
#   Esc     - Cancel

set -e

LIMIT=${1:-20}
HISTORY_FILE="$HOME/.claude/history.jsonl"
CACHE_FILE="/tmp/cc-sessions-cache.json"

# Colors for fzf
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m'

# Check dependencies
if ! command -v fzf &>/dev/null; then
    echo "fzf required. Install with: brew install fzf"
    exit 1
fi

if ! command -v jq &>/dev/null; then
    echo "jq required. Install with: brew install jq"
    exit 1
fi

# Get list of tmux sessions with their paths
get_tmux_sessions() {
    tmux list-sessions -F "#{session_name}:#{pane_current_path}" 2>/dev/null || echo ""
}

# Check if a project has an active tmux session
check_tmux_for_project() {
    local project_path="$1"
    local project_name=$(basename "$project_path")
    local tmux_sessions=$(get_tmux_sessions)

    # Check by session name matching project name
    if echo "$tmux_sessions" | grep -qi "^${project_name}:"; then
        echo "running"
        return
    fi

    # Check by path
    if echo "$tmux_sessions" | grep -q ":${project_path}$"; then
        echo "running"
        return
    fi

    echo "none"
}

# Check if Claude is running in a tmux session
check_claude_in_tmux() {
    local session_name="$1"
    if tmux list-panes -t "$session_name" -F "#{pane_current_command}" 2>/dev/null | grep -qi claude; then
        echo "claude"
    else
        echo "idle"
    fi
}

# Build session data with tmux status
build_session_data() {
    jq -rs --arg limit "$LIMIT" '
        # Categorize function
        def categorize:
            . as $msgs |
            ($msgs | map(.display // "") | join(" ") | ascii_downcase) as $all |
            [
                (if ($all | test("bug|error|broken|issue|debug|crash")) then "🐛" else null end),
                (if ($all | test("add|create|implement|build|new feature")) then "✨" else null end),
                (if ($all | test("investigate|explore|search|research|understand")) then "🔍" else null end),
                (if ($all | test("refactor|rename|clean|reorganize|simplify")) then "♻️" else null end),
                (if ($all | test("style|css|design|ui|layout|tailwind")) then "🎨" else null end),
                (if ($all | test("test|spec|jest|pytest|coverage")) then "🧪" else null end),
                (if ($all | test("deploy|docker|ci|cd|pipeline|release")) then "🚀" else null end),
                (if ($all | test("^/|/commit|/review|/plugin")) then "🔧" else null end)
            ] | map(select(. != null)) | .[0:3] | join("");

        group_by(.sessionId) |
        map(select(.[0].sessionId)) |
        map({
            sessionId: .[0].sessionId,
            project: .[0].project,
            projectName: (.[0].project | split("/") | last),
            messages: length,
            timestamp: (sort_by(.timestamp) | last | .timestamp),
            tags: (. | categorize),
            topic: (sort_by(.timestamp) | .[1:] | map(select(.display | length > 15)) | first | .display // "")[0:60],
            latest: (sort_by(.timestamp) | last | .display)[0:50]
        }) |
        sort_by(.timestamp) | reverse | .[0:($limit | tonumber)]
    ' "$HISTORY_FILE"
}

# Generate display line for fzf
format_session_line() {
    local json="$1"
    local idx="$2"

    local session_id=$(echo "$json" | jq -r '.sessionId')
    local project=$(echo "$json" | jq -r '.project')
    local project_name=$(echo "$json" | jq -r '.projectName')
    local messages=$(echo "$json" | jq -r '.messages')
    local timestamp=$(echo "$json" | jq -r '.timestamp')
    local tags=$(echo "$json" | jq -r '.tags')
    local topic=$(echo "$json" | jq -r '.topic' | tr '\n' ' ')

    # Check tmux status
    local tmux_status=$(check_tmux_for_project "$project")
    local tmux_icon="⚪"
    local tmux_label="no tmux"

    if [[ "$tmux_status" == "running" ]]; then
        local claude_status=$(check_claude_in_tmux "$(basename "$project")")
        if [[ "$claude_status" == "claude" ]]; then
            tmux_icon="🟢"
            tmux_label="claude running"
        else
            tmux_icon="🟡"
            tmux_label="tmux idle"
        fi
    fi

    # Format timestamp
    local time_fmt=$(date -r $((timestamp / 1000)) "+%b %d %H:%M" 2>/dev/null || echo "unknown")

    # Build display line (tab-separated for column alignment)
    # Format: IDX|SESSION_ID|PROJECT|PROJECT_NAME|TMUX_ICON|TMUX_LABEL|TAGS|MSGS|TIME|TOPIC
    printf "%d\t%s\t%s\t%s\t%s\t%s\t%s\t%d\t%s\t%s\n" \
        "$idx" "$session_id" "$project" "$project_name" \
        "$tmux_icon" "$tmux_label" "$tags" "$messages" "$time_fmt" "$topic"
}

# Preview function (called by fzf)
preview_session() {
    local line="$1"
    IFS=$'\t' read -r idx session_id project project_name tmux_icon tmux_label tags msgs time topic <<< "$line"

    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}${project_name}${NC} ${tmux_icon} ${tmux_label}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${GRAY}Project:${NC}  $project"
    echo -e "${GRAY}Session:${NC}  ${session_id:0:8}..."
    echo -e "${GRAY}Tags:${NC}     $tags"
    echo -e "${GRAY}Messages:${NC} $msgs"
    echo -e "${GRAY}Time:${NC}     $time"
    echo ""
    echo -e "${BLUE}Topic:${NC}"
    echo "  $topic"
    echo ""

    # Show recent activity from history
    echo -e "${YELLOW}Recent activity:${NC}"
    jq -r --arg sid "$session_id" '
        select(.sessionId == $sid) |
        .display // empty
    ' "$HISTORY_FILE" 2>/dev/null | tail -5 | while read -r line; do
        echo "  ${line:0:70}"
    done

    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GRAY}Enter${NC}=Resume in tmux  ${GRAY}Ctrl-O${NC}=VSCode  ${GRAY}Ctrl-T${NC}=Attach tmux  ${GRAY}Ctrl-Y${NC}=Copy ID"
}

# Resume session in tmux
resume_in_tmux() {
    local line="$1"
    IFS=$'\t' read -r idx session_id project project_name tmux_icon tmux_label tags msgs time topic <<< "$line"

    local session_name="$project_name"

    # Check if tmux session exists
    if tmux has-session -t "$session_name" 2>/dev/null; then
        # Session exists, attach and run claude --resume
        tmux send-keys -t "$session_name" "claude --resume $session_id" Enter
        tmux attach -t "$session_name"
    else
        # Create new session with claude --resume
        tmux new-session -s "$session_name" -c "$project" "claude --resume $session_id"
    fi
}

# Open in VSCode/Cursor
open_in_vscode() {
    local line="$1"
    IFS=$'\t' read -r idx session_id project project_name rest <<< "$line"

    code "$project"
    echo "claude --resume $session_id" | pbcopy
    echo "Opened $project_name in VSCode. Resume command copied to clipboard."
}

# Attach to tmux only
attach_tmux_only() {
    local line="$1"
    IFS=$'\t' read -r idx session_id project project_name rest <<< "$line"

    local session_name="$project_name"

    if tmux has-session -t "$session_name" 2>/dev/null; then
        tmux attach -t "$session_name"
    else
        echo "No tmux session found for $project_name"
        echo "Creating new session..."
        tmux new-session -s "$session_name" -c "$project"
    fi
}

# Copy session ID
copy_session_id() {
    local line="$1"
    IFS=$'\t' read -r idx session_id rest <<< "$line"
    echo "$session_id" | pbcopy
    echo "Session ID copied: ${session_id:0:8}..."
}

# Export functions for fzf
export -f preview_session
export -f check_tmux_for_project
export -f check_claude_in_tmux
export -f get_tmux_sessions
export HISTORY_FILE
export GREEN YELLOW BLUE PURPLE CYAN GRAY NC

# Main execution
main() {
    if [[ ! -f "$HISTORY_FILE" ]]; then
        echo "No Claude history found at $HISTORY_FILE"
        exit 1
    fi

    # Build session data
    local sessions=$(build_session_data)

    if [[ -z "$sessions" || "$sessions" == "[]" ]]; then
        echo "No Claude sessions found"
        exit 1
    fi

    # Format sessions for fzf
    local formatted=""
    local idx=1
    while IFS= read -r session_json; do
        local line=$(format_session_line "$session_json" "$idx")
        formatted+="$line"$'\n'
        ((idx++))
    done < <(echo "$sessions" | jq -c '.[]')

    # Run fzf
    local selected=$(echo -e "$formatted" | fzf \
        --ansi \
        --header="Claude Code Sessions ($(echo "$sessions" | jq length) found)" \
        --header-first \
        --preview='
            line={}
            IFS=$'"'"'\t'"'"' read -r idx session_id project project_name tmux_icon tmux_label tags msgs time topic <<< "$line"
            echo -e "\033[0;36m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
            echo -e "\033[0;32m${project_name}\033[0m ${tmux_icon} ${tmux_label}"
            echo -e "\033[0;36m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
            echo ""
            echo -e "\033[0;90mProject:\033[0m  $project"
            echo -e "\033[0;90mSession:\033[0m  ${session_id:0:8}..."
            echo -e "\033[0;90mTags:\033[0m     $tags"
            echo -e "\033[0;90mMessages:\033[0m $msgs"
            echo -e "\033[0;90mTime:\033[0m     $time"
            echo ""
            echo -e "\033[0;34mTopic:\033[0m $topic"
            echo ""
            echo -e "\033[0;36m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
            echo -e "\033[0;90mEnter\033[0m=Resume  \033[0;90mCtrl-O\033[0m=VSCode  \033[0;90mCtrl-T\033[0m=Tmux only  \033[0;90mCtrl-Y\033[0m=Copy ID"
        ' \
        --preview-window=right:50%:wrap \
        --bind='ctrl-o:execute-silent(
            line={}
            IFS=$'"'"'\t'"'"' read -r idx session_id project project_name rest <<< "$line"
            code "$project"
            echo "claude --resume $session_id" | pbcopy
        )+abort' \
        --bind='ctrl-t:execute(
            line={}
            IFS=$'"'"'\t'"'"' read -r idx session_id project project_name rest <<< "$line"
            session_name="$project_name"
            if tmux has-session -t "$session_name" 2>/dev/null; then
                tmux attach -t "$session_name"
            else
                tmux new-session -s "$session_name" -c "$project"
            fi
        )' \
        --bind='ctrl-y:execute-silent(
            line={}
            IFS=$'"'"'\t'"'"' read -r idx session_id rest <<< "$line"
            echo "$session_id" | pbcopy
        )+abort' \
        --with-nth=4,5,6,7,8,9 \
        --delimiter='\t' \
        --no-multi \
        --height=80% \
        --border=rounded \
        --prompt="Session > " \
        --pointer="▶" \
        --marker="●" \
        --color='bg+:#363a4f,bg:#24273a,spinner:#f4dbd6,hl:#ed8796,fg:#cad3f5,header:#ed8796,info:#c6a0f6,pointer:#f4dbd6,marker:#f4dbd6,fg+:#cad3f5,prompt:#c6a0f6,hl+:#ed8796'
    )

    # Handle selection (Enter key)
    if [[ -n "$selected" ]]; then
        resume_in_tmux "$selected"
    fi
}

main "$@"
