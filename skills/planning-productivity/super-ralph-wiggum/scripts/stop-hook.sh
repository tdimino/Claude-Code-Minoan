#!/bin/bash

# Ralph Wiggum Enhanced - Stop Hook
# Prevents session exit when a ralph-loop is active
# Feeds the same prompt back to continue the loop
#
# Enhanced features:
# - PRD completion detection (all features passes: true)
# - Auto-append iteration summary to progress.txt
# - Browser testing reminder

set -euo pipefail

# Read hook input from stdin
HOOK_INPUT=$(cat)

# Check if ralph-loop is active
RALPH_STATE_FILE=".claude/ralph-loop.local.md"

if [[ ! -f "$RALPH_STATE_FILE" ]]; then
  # No active loop - allow exit
  exit 0
fi

# Parse YAML frontmatter
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$RALPH_STATE_FILE")
ITERATION=$(echo "$FRONTMATTER" | grep '^iteration:' | sed 's/iteration: *//')
MAX_ITERATIONS=$(echo "$FRONTMATTER" | grep '^max_iterations:' | sed 's/max_iterations: *//')
COMPLETION_PROMISE=$(echo "$FRONTMATTER" | grep '^completion_promise:' | sed 's/completion_promise: *//' | sed 's/^"\(.*\)"$/\1/')
PRD_FILE=$(echo "$FRONTMATTER" | grep '^prd_file:' | sed 's/prd_file: *//')
PROGRESS_FILE=$(echo "$FRONTMATTER" | grep '^progress_file:' | sed 's/progress_file: *//')
TEMPLATE=$(echo "$FRONTMATTER" | grep '^template:' | sed 's/template: *//')

# Default progress file if not set
PROGRESS_FILE="${PROGRESS_FILE:-./progress.txt}"

# Validate numeric fields
if [[ ! "$ITERATION" =~ ^[0-9]+$ ]]; then
  echo "Ralph loop: State file corrupted (invalid iteration: '$ITERATION')" >&2
  rm "$RALPH_STATE_FILE"
  exit 0
fi

if [[ ! "$MAX_ITERATIONS" =~ ^[0-9]+$ ]]; then
  echo "Ralph loop: State file corrupted (invalid max_iterations: '$MAX_ITERATIONS')" >&2
  rm "$RALPH_STATE_FILE"
  exit 0
fi

# Check max iterations
if [[ $MAX_ITERATIONS -gt 0 ]] && [[ $ITERATION -ge $MAX_ITERATIONS ]]; then
  echo "Ralph loop: Max iterations ($MAX_ITERATIONS) reached."

  # Log completion to progress file
  if [[ -f "$PROGRESS_FILE" ]]; then
    echo "" >> "$PROGRESS_FILE"
    echo "## Loop Completed - $(date +%Y-%m-%d\ %H:%M)" >> "$PROGRESS_FILE"
    echo "- Reason: Max iterations reached ($MAX_ITERATIONS)" >> "$PROGRESS_FILE"
    echo "- Template: $TEMPLATE" >> "$PROGRESS_FILE"
    echo "---" >> "$PROGRESS_FILE"
  fi

  rm "$RALPH_STATE_FILE"
  exit 0
fi

# Get transcript path
TRANSCRIPT_PATH=$(echo "$HOOK_INPUT" | jq -r '.transcript_path')

if [[ ! -f "$TRANSCRIPT_PATH" ]]; then
  echo "Ralph loop: Transcript file not found" >&2
  rm "$RALPH_STATE_FILE"
  exit 0
fi

# Get last assistant message
if ! grep -q '"role":"assistant"' "$TRANSCRIPT_PATH"; then
  echo "Ralph loop: No assistant messages in transcript" >&2
  rm "$RALPH_STATE_FILE"
  exit 0
fi

LAST_LINE=$(grep '"role":"assistant"' "$TRANSCRIPT_PATH" | tail -1)
LAST_OUTPUT=$(echo "$LAST_LINE" | jq -r '
  .message.content |
  map(select(.type == "text")) |
  map(.text) |
  join("\n")
' 2>/dev/null || echo "")

if [[ -z "$LAST_OUTPUT" ]]; then
  echo "Ralph loop: Empty assistant message" >&2
  rm "$RALPH_STATE_FILE"
  exit 0
fi

# Check for completion promise
if [[ "$COMPLETION_PROMISE" != "null" ]] && [[ -n "$COMPLETION_PROMISE" ]]; then
  PROMISE_TEXT=$(echo "$LAST_OUTPUT" | perl -0777 -pe 's/.*?<promise>(.*?)<\/promise>.*/$1/s; s/^\s+|\s+$//g; s/\s+/ /g' 2>/dev/null || echo "")

  if [[ -n "$PROMISE_TEXT" ]] && [[ "$PROMISE_TEXT" = "$COMPLETION_PROMISE" ]]; then
    echo "Ralph loop: Completion promise detected"

    # Log completion to progress file
    if [[ -f "$PROGRESS_FILE" ]]; then
      echo "" >> "$PROGRESS_FILE"
      echo "## Loop Completed - $(date +%Y-%m-%d\ %H:%M)" >> "$PROGRESS_FILE"
      echo "- Reason: Completion promise fulfilled" >> "$PROGRESS_FILE"
      echo "- Iterations: $ITERATION" >> "$PROGRESS_FILE"
      echo "- Template: $TEMPLATE" >> "$PROGRESS_FILE"
      echo "---" >> "$PROGRESS_FILE"
    fi

    rm "$RALPH_STATE_FILE"
    exit 0
  fi
fi

# Check PRD completion (all features passes: true)
if [[ "$PRD_FILE" != "null" ]] && [[ -n "$PRD_FILE" ]] && [[ -f "$PRD_FILE" ]]; then
  # Check if any feature has passes: false
  INCOMPLETE_COUNT=$(jq '[.features[] | select(.passes == false)] | length' "$PRD_FILE" 2>/dev/null || echo "-1")

  if [[ "$INCOMPLETE_COUNT" == "0" ]]; then
    echo "Ralph loop: All PRD features complete"

    # Log completion to progress file
    if [[ -f "$PROGRESS_FILE" ]]; then
      TOTAL_FEATURES=$(jq '.features | length' "$PRD_FILE" 2>/dev/null || echo "?")
      echo "" >> "$PROGRESS_FILE"
      echo "## Loop Completed - $(date +%Y-%m-%d\ %H:%M)" >> "$PROGRESS_FILE"
      echo "- Reason: All PRD features complete ($TOTAL_FEATURES features)" >> "$PROGRESS_FILE"
      echo "- Iterations: $ITERATION" >> "$PROGRESS_FILE"
      echo "- Template: $TEMPLATE" >> "$PROGRESS_FILE"
      echo "---" >> "$PROGRESS_FILE"
    fi

    rm "$RALPH_STATE_FILE"
    exit 0
  fi
fi

# Not complete - continue loop
NEXT_ITERATION=$((ITERATION + 1))

# Extract prompt (everything after the closing ---)
PROMPT_TEXT=$(awk '/^---$/{i++; next} i>=2' "$RALPH_STATE_FILE")

if [[ -z "$PROMPT_TEXT" ]]; then
  echo "Ralph loop: No prompt found in state file" >&2
  rm "$RALPH_STATE_FILE"
  exit 0
fi

# Update iteration counter
TEMP_FILE="${RALPH_STATE_FILE}.tmp.$$"
sed "s/^iteration: .*/iteration: $NEXT_ITERATION/" "$RALPH_STATE_FILE" > "$TEMP_FILE"
mv "$TEMP_FILE" "$RALPH_STATE_FILE"

# Build system message
if [[ "$COMPLETION_PROMISE" != "null" ]] && [[ -n "$COMPLETION_PROMISE" ]]; then
  SYSTEM_MSG="Ralph iteration $NEXT_ITERATION/$MAX_ITERATIONS | Complete: <promise>$COMPLETION_PROMISE</promise> (ONLY when TRUE!)"
else
  SYSTEM_MSG="Ralph iteration $NEXT_ITERATION/$MAX_ITERATIONS | No completion promise set"
fi

# Add PRD status if applicable
if [[ "$PRD_FILE" != "null" ]] && [[ -n "$PRD_FILE" ]] && [[ -f "$PRD_FILE" ]]; then
  COMPLETE_COUNT=$(jq '[.features[] | select(.passes == true)] | length' "$PRD_FILE" 2>/dev/null || echo "?")
  TOTAL_COUNT=$(jq '.features | length' "$PRD_FILE" 2>/dev/null || echo "?")
  SYSTEM_MSG="$SYSTEM_MSG | PRD: $COMPLETE_COUNT/$TOTAL_COUNT features"
fi

# Output JSON to block stop and feed prompt back
jq -n \
  --arg prompt "$PROMPT_TEXT" \
  --arg msg "$SYSTEM_MSG" \
  '{
    "decision": "block",
    "reason": $prompt,
    "systemMessage": $msg
  }'

exit 0
