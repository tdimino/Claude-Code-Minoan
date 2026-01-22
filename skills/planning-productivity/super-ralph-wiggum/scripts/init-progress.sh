#!/bin/bash

# Ralph Wiggum Enhanced - Progress File Initializer
# Creates a structured progress.txt file for Ralph loops
#
# Usage: init-progress.sh [output-file]

set -euo pipefail

OUTPUT_FILE="${1:-./progress.txt}"

# Don't overwrite existing file
if [[ -f "$OUTPUT_FILE" ]]; then
  echo "Progress file already exists: $OUTPUT_FILE"
  exit 0
fi

# Create progress file with structure
cat > "$OUTPUT_FILE" <<'EOF'
# Ralph Progress Log

Started: $(date +%Y-%m-%d)

## Codebase Patterns

Add reusable patterns discovered during iterations here.
These patterns help future iterations and humans understand the codebase.

Examples:
- Migrations: Use IF NOT EXISTS for idempotency
- Types: Export from actions.ts
- Tests: Mock external services in beforeEach

---

## Iteration Log

Progress from each iteration is appended below.

EOF

# Replace date placeholder
sed -i.bak "s/\$(date +%Y-%m-%d)/$(date +%Y-%m-%d)/" "$OUTPUT_FILE" && rm -f "$OUTPUT_FILE.bak"

echo "Created progress file: $OUTPUT_FILE"
