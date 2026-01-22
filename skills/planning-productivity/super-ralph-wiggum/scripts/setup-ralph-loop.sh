#!/bin/bash

# Ralph Wiggum Enhanced - Loop Setup Script
# Creates state file and initializes progress tracking for Ralph loops
#
# Usage:
#   setup-ralph-loop.sh [OPTIONS] [PROMPT]
#
# Options:
#   --template <name>        Use pre-built template (test-coverage, feature-prd, etc.)
#   --prd <file>            PRD file for task tracking
#   --max-iterations <n>    Maximum iterations (default: varies by template)
#   --completion-promise <text>  Phrase that signals completion
#   --progress <file>       Progress file location (default: ./progress.txt)
#   --browser               Enable browser testing prompts
#   --once                  Single iteration mode (HITL)
#   -h, --help              Show this help

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Defaults
PROMPT_PARTS=()
TEMPLATE=""
PRD_FILE=""
MAX_ITERATIONS=0
COMPLETION_PROMISE="COMPLETE"
PROGRESS_FILE="./progress.txt"
BROWSER_TESTING=false
ONCE_MODE=false

# Template defaults
declare -A TEMPLATE_ITERATIONS=(
  ["test-coverage"]=30
  ["feature-prd"]=20
  ["lint-fix"]=30
  ["docs-generation"]=25
  ["dataset-generation"]=50
  ["migration"]=40
)

show_help() {
  cat << 'HELP_EOF'
Ralph Wiggum Enhanced - Autonomous Iteration Loops

USAGE:
  setup-ralph-loop.sh [OPTIONS] [PROMPT...]

OPTIONS:
  --template <name>           Use pre-built template
                              Available: test-coverage, feature-prd, lint-fix,
                                        docs-generation, dataset-generation, migration
  --prd <file>               PRD JSON file for task tracking
  --max-iterations <n>       Maximum iterations before auto-stop
  --completion-promise <text> Phrase that signals completion (default: COMPLETE)
  --progress <file>          Progress file location (default: ./progress.txt)
  --browser                  Enable browser testing prompts
  --once                     Single iteration mode (no loop)
  -h, --help                 Show this help message

EXAMPLES:
  # Test coverage with default iterations
  setup-ralph-loop.sh --template test-coverage

  # Feature development with PRD
  setup-ralph-loop.sh --template feature-prd --prd ./prd.json

  # Custom prompt with limits
  setup-ralph-loop.sh --max-iterations 15 "Fix all TypeScript errors"

  # Single iteration (HITL mode)
  setup-ralph-loop.sh --once "Add error handling to the login function"

TEMPLATES:
  test-coverage      Improve test coverage (30 iterations)
  feature-prd        Implement features from PRD (20 iterations)
  lint-fix           Fix all lint errors (30 iterations)
  docs-generation    Generate documentation (25 iterations)
  dataset-generation Generate training data (50 iterations)
  migration          Framework migration (40 iterations)

STOPPING:
  Loop stops when:
  - Max iterations reached
  - Completion promise detected: <promise>COMPLETE</promise>
  - PRD mode: All features have passes: true

MONITORING:
  # View current iteration
  grep '^iteration:' .claude/ralph-loop.local.md

  # View progress
  cat progress.txt
HELP_EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -h|--help)
      show_help
      exit 0
      ;;
    --template)
      if [[ -z "${2:-}" ]]; then
        echo "Error: --template requires a name" >&2
        echo "Available templates: test-coverage, feature-prd, lint-fix, docs-generation, dataset-generation, migration" >&2
        exit 1
      fi
      TEMPLATE="$2"
      shift 2
      ;;
    --prd)
      if [[ -z "${2:-}" ]]; then
        echo "Error: --prd requires a file path" >&2
        exit 1
      fi
      PRD_FILE="$2"
      shift 2
      ;;
    --max-iterations)
      if [[ -z "${2:-}" ]] || ! [[ "$2" =~ ^[0-9]+$ ]]; then
        echo "Error: --max-iterations requires a positive integer" >&2
        exit 1
      fi
      MAX_ITERATIONS="$2"
      shift 2
      ;;
    --completion-promise)
      if [[ -z "${2:-}" ]]; then
        echo "Error: --completion-promise requires text" >&2
        exit 1
      fi
      COMPLETION_PROMISE="$2"
      shift 2
      ;;
    --progress)
      if [[ -z "${2:-}" ]]; then
        echo "Error: --progress requires a file path" >&2
        exit 1
      fi
      PROGRESS_FILE="$2"
      shift 2
      ;;
    --browser)
      BROWSER_TESTING=true
      shift
      ;;
    --once)
      ONCE_MODE=true
      shift
      ;;
    *)
      PROMPT_PARTS+=("$1")
      shift
      ;;
  esac
done

# Join prompt parts
PROMPT="${PROMPT_PARTS[*]:-}"

# Load template if specified
if [[ -n "$TEMPLATE" ]]; then
  TEMPLATE_FILE="$SKILL_DIR/templates/${TEMPLATE}.md"
  if [[ ! -f "$TEMPLATE_FILE" ]]; then
    echo "Error: Template '$TEMPLATE' not found" >&2
    echo "Available templates: test-coverage, feature-prd, lint-fix, docs-generation, dataset-generation, migration" >&2
    exit 1
  fi

  TEMPLATE_CONTENT=$(cat "$TEMPLATE_FILE")

  # Set default iterations from template if not specified
  if [[ $MAX_ITERATIONS -eq 0 ]] && [[ -n "${TEMPLATE_ITERATIONS[$TEMPLATE]:-}" ]]; then
    MAX_ITERATIONS="${TEMPLATE_ITERATIONS[$TEMPLATE]}"
  fi

  # Merge template with user prompt
  if [[ -n "$PROMPT" ]]; then
    PROMPT="$TEMPLATE_CONTENT

ADDITIONAL INSTRUCTIONS:
$PROMPT"
  else
    PROMPT="$TEMPLATE_CONTENT"
  fi
fi

# Validate we have a prompt
if [[ -z "$PROMPT" ]]; then
  echo "Error: No prompt provided" >&2
  echo "Use --template <name> or provide a custom prompt" >&2
  echo "Run with --help for usage information" >&2
  exit 1
fi

# Handle PRD file injection
if [[ -n "$PRD_FILE" ]]; then
  if [[ ! -f "$PRD_FILE" ]]; then
    echo "Error: PRD file not found: $PRD_FILE" >&2
    exit 1
  fi
  # Inject PRD reference into prompt
  PROMPT="@$PRD_FILE

$PROMPT"
fi

# Initialize progress file
if [[ ! -f "$PROGRESS_FILE" ]]; then
  "$SCRIPT_DIR/init-progress.sh" "$PROGRESS_FILE"
fi

# Inject progress file reference
PROMPT="@$PROGRESS_FILE

$PROMPT"

# Add browser testing instructions if enabled
if [[ "$BROWSER_TESTING" == true ]]; then
  PROMPT="$PROMPT

BROWSER TESTING:
For UI changes, verify with screenshots using the dev-browser skill.
Load the skill with: Load the dev-browser skill
Take screenshots to verify visual changes are correct.
Do NOT mark UI features complete without visual verification."
fi

# HITL mode: just output the prompt, no state file
if [[ "$ONCE_MODE" == true ]]; then
  echo "Single iteration mode (HITL)"
  echo "=========================="
  echo ""
  echo "$PROMPT"
  exit 0
fi

# Create state file directory
mkdir -p .claude

# Quote completion promise for YAML
if [[ -n "$COMPLETION_PROMISE" ]]; then
  COMPLETION_PROMISE_YAML="\"$COMPLETION_PROMISE\""
else
  COMPLETION_PROMISE_YAML="null"
fi

# Create state file
cat > .claude/ralph-loop.local.md <<EOF
---
active: true
iteration: 1
max_iterations: $MAX_ITERATIONS
completion_promise: $COMPLETION_PROMISE_YAML
template: ${TEMPLATE:-custom}
prd_file: ${PRD_FILE:-null}
progress_file: $PROGRESS_FILE
browser_testing: $BROWSER_TESTING
started_at: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
---

$PROMPT
EOF

# Output setup message
cat <<EOF
Ralph Wiggum Enhanced - Loop Activated

Template: ${TEMPLATE:-custom}
Iteration: 1 of $(if [[ $MAX_ITERATIONS -gt 0 ]]; then echo $MAX_ITERATIONS; else echo "unlimited"; fi)
Completion: <promise>$COMPLETION_PROMISE</promise>
Progress: $PROGRESS_FILE
PRD: ${PRD_FILE:-none}
Browser: $BROWSER_TESTING

The stop hook is now active. When Claude tries to exit, the SAME PROMPT
will be fed back. Context persists through files and git history.

To monitor: head -10 .claude/ralph-loop.local.md
To cancel: rm .claude/ralph-loop.local.md

CRITICAL: Output <promise>$COMPLETION_PROMISE</promise> ONLY when the
statement is completely and unequivocally TRUE. Do not lie to exit!

EOF

# Output the prompt
echo "$PROMPT"
