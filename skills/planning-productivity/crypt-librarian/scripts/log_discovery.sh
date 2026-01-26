#!/bin/bash
# log_discovery.sh - SubagentStop hook to log film-researcher results for provenance
# Logs discovery sessions and optionally saves provenance to SQLite via crypt_db.py

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
LOG_DIR="$HOME/Desktop/Programming/crypt-librarian/logs"
LOG_FILE="$LOG_DIR/discovery-provenance.log"
CRYPT_DB="$HOME/Desktop/Programming/crypt-librarian/scripts/crypt_db.py"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Read subagent output from stdin
INPUT=$(cat)

# Extract agent info from SubagentStop event
AGENT_ID=$(echo "$INPUT" | jq -r '.agent_id // "unknown"')
AGENT_TYPE=$(echo "$INPUT" | jq -r '.agent_type // "unknown"')
SUBAGENT_NAME=$(echo "$INPUT" | jq -r '.subagent_name // "film-researcher"')
TASK_PROMPT=$(echo "$INPUT" | jq -r '.task_prompt // ""' | head -c 200)

# Log the discovery session to file
cat >> "$LOG_FILE" << EOF
---
timestamp: $TIMESTAMP
agent_id: $AGENT_ID
agent_type: $AGENT_TYPE
subagent: $SUBAGENT_NAME
task_prompt: $TASK_PROMPT
---

EOF

# If crypt_db.py exists and this was a film-researcher, save provenance to SQLite
if [ -f "$CRYPT_DB" ] && [ "$SUBAGENT_NAME" = "film-researcher" ]; then
    # Extract query from task prompt (best effort)
    QUERY=$(echo "$TASK_PROMPT" | grep -oE '"[^"]+"|gothic|occult|noir|literary|horror' | head -1 | tr -d '"')
    if [ -n "$QUERY" ]; then
        python3 "$CRYPT_DB" provenance \
            --source "claude-subagent" \
            --query "$QUERY" \
            --films "" 2>/dev/null || true
    fi
fi

echo "Discovery session logged: $SUBAGENT_NAME ($AGENT_ID)"
exit 0
