# Beads Command Quick Reference

Comprehensive command cheat sheet for the `bd` tool, organized by category.

## Project Setup

```bash
# Initialize Beads in current project
bd init

# Check version
bd --version

# Run interactive quickstart guide
bd quickstart
```

## Creating Issues

```bash
# Basic creation
bd create "Task title"
bd create "Task title" -d "Description"
bd create "Task title" -p 1 -t bug --json

# With labels
bd create "Task" -l "backend,urgent,p1"

# With assignee
bd create "Task" -a alice

# From markdown file
bd create -f plan.md --json

# Explicit ID (for parallel workers)
bd create "Worker task" --id worker1-100
```

**Options:**
- `-d, --description` - Issue description
- `-p, --priority` - Priority (0-4, 0=highest, 2=default)
- `-t, --type` - Type: `task`, `feature`, `bug`, `epic`, `chore`
- `-l, --labels` - Comma-separated labels
- `-a, --assignee` - Assign to user
- `--id` - Explicit issue ID
- `-f, --file` - Create from markdown file
- `--json` - JSON output

## Viewing Issues

```bash
# Show specific issue
bd show bd-42
bd show bd-42 --json

# List all issues
bd list
bd list --json

# Filter by status
bd list --status open
bd list --status in_progress
bd list --status closed

# Filter by priority
bd list --priority 0
bd list --priority 1

# Filter by assignee
bd list --assignee alice

# Filter by labels (AND - must have ALL)
bd list --label backend,urgent

# Filter by labels (OR - must have AT LEAST ONE)
bd list --label-any frontend,backend

# Combine filters
bd list --status open --priority 1 --label backend
```

## Updating Issues

```bash
# Update status
bd update bd-42 --status in_progress
bd update bd-42 --status open

# Update priority
bd update bd-42 --priority 0

# Update assignee
bd update bd-42 --assignee bob

# Close issue
bd close bd-42
bd close bd-42 --reason "Implementation complete"

# Close multiple issues
bd close bd-1 bd-2 bd-3

# JSON output
bd update bd-42 --status in_progress --json
bd close bd-42 --json
```

**Valid statuses:**
- `open` - Not started
- `in_progress` - Currently being worked on
- `closed` - Completed

## Dependencies

```bash
# Add dependency (bd-2 depends on bd-1)
bd dep add bd-2 bd-1

# Add with specific type
bd dep add bd-2 bd-1 --type blocks
bd dep add bd-child bd-parent --type parent-child
bd dep add bd-new bd-current --type discovered-from
bd dep add bd-3 bd-1 --type related

# Remove dependency
bd dep remove bd-2 bd-1

# Show dependency tree
bd dep tree bd-42
bd dep tree bd-42 --json

# Detect cycles
bd dep cycles
bd dep cycles --json
```

**Dependency types:**
- `blocks` - Hard blocker (default)
- `parent-child` - Hierarchical relationship
- `discovered-from` - Issue discovered during work on another
- `related` - Soft connection

## Finding Work

```bash
# Show ready work (no blockers)
bd ready
bd ready --json

# Filter ready work
bd ready --priority 1
bd ready --label backend
bd ready --assignee alice
bd ready --limit 10

# Show blocked issues
bd blocked
bd blocked --json

# Project statistics
bd stats
bd stats --json
```

## Labels

```bash
# Add label to issue
bd label add bd-42 security

# Remove label from issue
bd label remove bd-42 urgent

# List labels on specific issue
bd label list bd-42

# List all labels with counts
bd label list-all
bd label list-all --json
```

## Deleting Issues

```bash
# Delete single issue (preview mode)
bd delete bd-42

# Force delete
bd delete bd-42 --force

# Delete multiple
bd delete bd-1 bd-2 bd-3 --force

# Delete from file
bd delete --from-file deletions.txt --force

# Dry-run mode (preview only)
bd delete --from-file deletions.txt --dry-run

# Cascade delete (recursively delete dependents)
bd delete bd-42 --cascade --force

# JSON output
bd delete bd-42 --json
```

## Advanced Operations

```bash
# Rename issue prefix
bd rename-prefix kw- --dry-run
bd rename-prefix kw- --json

# Compact old closed issues (memory decay)
bd compact --dry-run --all
bd compact --threshold 180 --target-size 5000000

# Export/import
bd export issues.jsonl
bd import issues.jsonl
```

## Output Formats

Add `--json` to any command for machine-readable output:

```bash
bd create "Task" --json
bd list --json
bd show bd-42 --json
bd ready --json
bd dep tree bd-42 --json
bd stats --json
```

## Common Patterns

### Session Startup

```bash
# Find ready work
bd ready --json

# If nothing ready, check what's blocked
bd blocked --json
```

### Start Working

```bash
# Claim an issue
bd update bd-42 --status in_progress --json
```

### Discover New Work

```bash
# Create and link
NEW_ID=$(bd create "Fix discovered bug" -t bug -p 1 --json | jq -r '.id')
bd dep add $NEW_ID bd-current --type discovered-from --json
```

### Complete Work

```bash
# Close with reason
bd close bd-42 --reason "Implementation complete, tests passing" --json
```

### Create Epic with Tasks

```bash
# Create epic
EPIC_ID=$(bd create "User authentication" -t epic -p 1 --json | jq -r '.id')

# Create tasks linked to epic
bd create "Add login form" -p 1 --json
bd dep add bd-new $EPIC_ID --type parent-child

bd create "Add session management" -p 1 --json
bd dep add bd-new $EPIC_ID --type parent-child
```

## JSON Parsing Examples

```bash
# Get first ready issue
ISSUE=$(bd ready --json | jq -r '.[0]')
ISSUE_ID=$(echo "$ISSUE" | jq -r '.id')
ISSUE_TITLE=$(echo "$ISSUE" | jq -r '.title')

# Count ready issues
READY_COUNT=$(bd ready --json | jq 'length')

# Get all high-priority issues
bd list --priority 1 --json | jq '.[] | {id, title, status}'

# Check if specific issue is ready
bd ready --json | jq '.[] | select(.id == "bd-42")'
```

## Help

```bash
# General help
bd --help

# Command-specific help
bd create --help
bd dep --help
bd list --help
```
