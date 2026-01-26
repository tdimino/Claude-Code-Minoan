#!/bin/bash
# validate_year.sh - PreToolUse hook to block additions of post-2016 films
# Exit code 2 blocks the operation and returns error message to Claude

INPUT=$(cat)

# Extract year from Edit tool's new_string parameter
# Look for "year": followed by a number in the content being added
YEAR=$(echo "$INPUT" | jq -r '.tool_input.new_string // empty' | grep -oE '"year":\s*[0-9]+' | grep -oE '[0-9]+' | head -1)

if [ -n "$YEAR" ] && [ "$YEAR" -gt 2016 ]; then
  echo "BLOCKED: Cannot add post-2016 film to Crypt Librarian archive (year: $YEAR)" >&2
  echo "The pre-2016 rule is STRICT. Request explicit user approval for exceptions." >&2
  exit 2
fi

exit 0
