# Beads Workflow Patterns

Best practices and common patterns for AI agents using Beads effectively.

## Core Principles

1. **Initialize once per project** - `bd init` creates the `.beads/` directory
2. **Always use `--json`** - Makes output machine-parsable
3. **Query ready work at session start** - Orients agent after context loss
4. **Create issues for discovered work** - Never lose track of findings
5. **Close with descriptive reasons** - Builds useful audit trail

## Pattern 1: Session Startup

**Problem:** Agent needs to orient itself after context loss or compaction.

**Solution:** Query ready work and project state.

```bash
#!/bin/bash
# Session startup script

# Check for ready work
READY_JSON=$(bd ready --json)
READY_COUNT=$(echo "$READY_JSON" | jq 'length')

if [ "$READY_COUNT" -gt 0 ]; then
  echo "Found $READY_COUNT ready issues:"
  echo "$READY_JSON" | jq '.[] | {id, title, priority}'

  # Get highest priority ready issue
  NEXT_ISSUE=$(echo "$READY_JSON" | jq -r 'sort_by(.priority) | .[0]')
  NEXT_ID=$(echo "$NEXT_ISSUE" | jq -r '.id')

  echo "Recommended next: $NEXT_ID"
else
  echo "No ready work. Checking blocked issues:"
  bd blocked --json | jq '.[] | {id, title, blockers}'
fi
```

## Pattern 2: Feature Implementation with Discovery

**Problem:** While implementing a feature, agent discovers bugs, edge cases, or related work.

**Solution:** Create linked issues for discoveries.

```bash
#!/bin/bash
# Working on bd-42: "Add user authentication"

# Start the main work
bd update bd-42 --status in_progress --json

# During implementation, discover a bug
BUG_ID=$(bd create "Fix: Email validation allows invalid formats" \
  -t bug -p 1 -l "auth,validation" --json | jq -r '.id')

# Link discovery back to parent
bd dep add $BUG_ID bd-42 --type discovered-from --json

# Decide priority:
# If blocking: switch to bug immediately
# If not blocking: finish bd-42, bug will show in bd ready

# After completing main work
bd close bd-42 --reason "Auth flow implemented. Discovered validation bug ($BUG_ID) to fix separately." --json

# Bug is now ready to work on
bd ready --json | jq '.[] | select(.id == "'$BUG_ID'")'
```

## Pattern 3: Epic Breakdown

**Problem:** Large feature needs to be broken into manageable tasks.

**Solution:** Create epic with child tasks linked via parent-child dependencies.

```bash
#!/bin/bash
# Create the epic
EPIC_ID=$(bd create "Implement payment system" \
  -t epic -p 1 -l "payments,backend" \
  -d "Full payment processing including Stripe integration, invoice generation, and webhook handling" \
  --json | jq -r '.id')

echo "Created epic: $EPIC_ID"

# Create child tasks
TASK1=$(bd create "Integrate Stripe SDK" -t task -p 1 -l "payments,stripe" --json | jq -r '.id')
bd dep add $TASK1 $EPIC_ID --type parent-child --json

TASK2=$(bd create "Build invoice generation service" -t task -p 2 -l "payments,invoices" --json | jq -r '.id')
bd dep add $TASK2 $EPIC_ID --type parent-child --json

TASK3=$(bd create "Implement webhook handlers" -t task -p 2 -l "payments,webhooks" --json | jq -r '.id')
bd dep add $TASK3 $EPIC_ID --type parent-child --json

# Add dependencies between tasks
bd dep add $TASK3 $TASK1 --type blocks --json  # Webhooks need Stripe SDK first

# Visualize the epic
bd dep tree $EPIC_ID --json
```

## Pattern 4: Handling Blockers

**Problem:** Work is blocked, need to identify and resolve blockers.

**Solution:** Query blocked issues, assess blockers, decide action.

```bash
#!/bin/bash
# Find blocked work
BLOCKED_JSON=$(bd blocked --json)

# Examine a blocked issue
ISSUE_ID="bd-42"
ISSUE_DATA=$(bd show $ISSUE_ID --json)

# Get blockers
BLOCKERS=$(echo "$ISSUE_DATA" | jq -r '.dependencies[] | select(.type == "blocks") | .to_id')

echo "Issue $ISSUE_ID is blocked by: $BLOCKERS"

# Options:
# 1. Work on blockers first
for BLOCKER in $BLOCKERS; do
  BLOCKER_STATUS=$(bd show $BLOCKER --json | jq -r '.status')
  if [ "$BLOCKER_STATUS" == "open" ]; then
    echo "Blocker $BLOCKER is ready to work on"
    bd update $BLOCKER --status in_progress --json
    # Start working on blocker
    break
  fi
done

# 2. Or reassess if dependency is still valid
# bd dep remove $ISSUE_ID $BLOCKER
```

## Pattern 5: Parallel Work (Multiple Agents/Machines)

**Problem:** Multiple agents working on same project need to avoid conflicts.

**Solution:** Use ID prefixes and ready work queries.

```bash
#!/bin/bash
# Agent 1 (on laptop)
AGENT_ID="laptop"

# Create issues with prefixed IDs
bd create "Implement feature A" --id "${AGENT_ID}-1" -p 1 --json
bd create "Write tests for A" --id "${AGENT_ID}-2" -p 2 --json

# Agent 2 (on desktop)
AGENT_ID="desktop"
bd create "Implement feature B" --id "${AGENT_ID}-1" -p 1 --json
bd create "Write tests for B" --id "${AGENT_ID}-2" -p 2 --json

# Both agents query ready work
bd ready --json | jq '.[] | {id, title}'

# Commit and push .beads/issues.jsonl
git add .beads/issues.jsonl
git commit -m "Add tasks"
git push

# On other machine
git pull  # Auto-import syncs JSONL → SQLite
bd ready --json  # See all ready work from both agents
```

## Pattern 6: Priority Triage

**Problem:** Too many issues, need to focus on what matters.

**Solution:** Use priority filtering and labels.

```bash
#!/bin/bash
# Critical issues first
CRITICAL=$(bd ready --priority 0 --json)
CRITICAL_COUNT=$(echo "$CRITICAL" | jq 'length')

if [ "$CRITICAL_COUNT" -gt 0 ]; then
  echo "🚨 $CRITICAL_COUNT critical issues:"
  echo "$CRITICAL" | jq '.[] | {id, title}'
  exit 0
fi

# High priority issues
HIGH=$(bd ready --priority 1 --json)
HIGH_COUNT=$(echo "$HIGH" | jq 'length')

if [ "$HIGH_COUNT" -gt 0 ]; then
  echo "⚡ $HIGH_COUNT high priority issues:"
  echo "$HIGH" | jq '.[] | {id, title}'
  exit 0
fi

# Backend work
BACKEND=$(bd ready --label backend --json)
echo "🔧 Backend issues:"
echo "$BACKEND" | jq '.[] | {id, title, priority}'
```

## Pattern 7: Work Discovery Template

**Problem:** Need consistent workflow for handling discovered work.

**Solution:** Template script for discovery scenarios.

```bash
#!/bin/bash
# Template: Discovering new work during implementation
# Usage: ./discover.sh "Issue title" bug 1 "backend,urgent"

CURRENT_ISSUE=${CURRENT_ISSUE:-"bd-unknown"}  # Set to current work
TITLE=$1
TYPE=${2:-task}
PRIORITY=${3:-2}
LABELS=${4:-""}

# Create the discovered issue
if [ -n "$LABELS" ]; then
  NEW_ID=$(bd create "$TITLE" -t $TYPE -p $PRIORITY -l "$LABELS" --json | jq -r '.id')
else
  NEW_ID=$(bd create "$TITLE" -t $TYPE -p $PRIORITY --json | jq -r '.id')
fi

echo "Created: $NEW_ID"

# Link back to current work
if [ "$CURRENT_ISSUE" != "bd-unknown" ]; then
  bd dep add $NEW_ID $CURRENT_ISSUE --type discovered-from --json
  echo "Linked $NEW_ID → $CURRENT_ISSUE (discovered-from)"
fi

# Assess urgency
if [ "$PRIORITY" -eq 0 ] || [ "$PRIORITY" -eq 1 ]; then
  echo "⚠️  High priority discovery - consider switching to $NEW_ID immediately"
else
  echo "📝 Added to backlog - will show in bd ready when current work completes"
fi
```

## Pattern 8: Cycle Detection and Resolution

**Problem:** Accidentally created circular dependencies.

**Solution:** Detect and resolve cycles.

```bash
#!/bin/bash
# Check for cycles
CYCLES=$(bd dep cycles --json)

if [ "$CYCLES" != "[]" ]; then
  echo "⚠️  Dependency cycles detected!"
  echo "$CYCLES" | jq '.'

  # Example resolution: remove one edge from cycle
  # Identify which dependency is least critical
  CYCLE_EDGE=$(echo "$CYCLES" | jq -r '.[0] | "\(.from_id) → \(.to_id)"')

  echo "Manual resolution required. Review cycle: $CYCLE_EDGE"
  echo "Consider: bd dep remove <from> <to>"
else
  echo "✅ No cycles detected"
fi
```

## Pattern 9: Batch Issue Creation from Plan

**Problem:** Have a detailed plan in markdown, need to convert to tracked issues.

**Solution:** Use markdown import feature.

```markdown
<!-- feature-plan.md -->
## Implement user dashboard

### Priority
1

### Type
epic

### Description
Create comprehensive user dashboard with analytics and settings.

### Labels
frontend,dashboard

## Add metrics widget

### Priority
1

### Type
feature

### Dependencies
bd-epic-id

### Description
Display key metrics in dashboard widget.

## Add settings panel

### Priority
2

### Type
feature

### Dependencies
bd-epic-id

### Description
User configuration and preferences panel.
```

```bash
# Import the plan
bd create -f feature-plan.md --json

# Review created issues
bd list --label dashboard --json
```

## Pattern 10: Memory Decay (Compaction)

**Problem:** Database grows too large with old closed issues.

**Solution:** Use compaction to summarize old work.

```bash
#!/bin/bash
# Periodic maintenance - run monthly or when db grows large

# Preview what would be compacted
bd compact --dry-run --all --threshold 90  # Issues closed >90 days ago

# Run compaction
# Note: Requires LLM access for semantic summarization
bd compact --threshold 90 --target-size 5000000  # Target 5MB

# Check results
bd stats --json | jq '{total_issues, open_issues, closed_issues}'
```

## Anti-Patterns to Avoid

### ❌ Don't: Create issues without linking discoveries

```bash
# Bad - orphaned discovery
bd create "Found a bug" --json
# Lost context: where was this found? What was I working on?
```

```bash
# Good - linked discovery
bd create "Found a bug" --json
bd dep add bd-new bd-current --type discovered-from --json
# Clear context preserved
```

### ❌ Don't: Forget to update status

```bash
# Bad - status never updated
bd create "Task" --json
# Work on it...
bd close bd-1 --json  # Status was still 'open'!
```

```bash
# Good - proper status tracking
bd create "Task" --json
bd update bd-1 --status in_progress --json
# Work on it...
bd close bd-1 --json
```

### ❌ Don't: Create circular dependencies

```bash
# Bad - creates cycle
bd dep add bd-1 bd-2
bd dep add bd-2 bd-3
bd dep add bd-3 bd-1  # Cycle! Nothing can be ready.
```

```bash
# Good - linear or tree dependencies
bd dep add bd-2 bd-1  # bd-2 depends on bd-1
bd dep add bd-3 bd-1  # bd-3 also depends on bd-1
# bd-1 is ready, then bd-2 and bd-3 become ready
```

### ❌ Don't: Use markdown files instead of Beads

```bash
# Bad - agent creates plan.md
echo "## Tasks\n- [ ] Task 1\n- [ ] Task 2" > plan.md
# Markdown files get lost, stale, not queryable
```

```bash
# Good - use Beads
bd create "Task 1" --json
bd create "Task 2" --json
bd ready --json  # Queryable, persistent, git-versioned
```

## Integration Examples

### AGENTS.md / CLAUDE.md Integration

```markdown
## Task Tracking with Beads

We use Beads (`bd`) for task tracking. At session start:

1. Run `bd ready --json` to find available work
2. If nothing ready, check `bd blocked --json` to see what's blocked
3. Claim work with `bd update <id> --status in_progress --json`
4. Create issues for discovered work: `bd create` + `bd dep add --type discovered-from`
5. Close completed work: `bd close <id> --reason "..." --json`

Run `bd quickstart` for full guide.
```

### Git Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit
# Ensure .beads/issues.jsonl is committed if it exists

if [ -f .beads/issues.jsonl ]; then
  git add .beads/issues.jsonl
fi
```

### CI/CD Integration

```yaml
# .github/workflows/beads-check.yml
name: Beads Checks

on: [pull_request]

jobs:
  check-cycles:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Install bd
        run: |
          curl -fsSL https://raw.githubusercontent.com/steveyegge/beads/main/scripts/install.sh | bash

      - name: Check for dependency cycles
        run: |
          bd dep cycles --json
          if [ $? -ne 0 ]; then
            echo "❌ Dependency cycles detected"
            exit 1
          fi

      - name: Check for critical issues
        run: |
          CRITICAL=$(bd ready --priority 0 --json | jq 'length')
          if [ "$CRITICAL" -gt 0 ]; then
            echo "⚠️  $CRITICAL critical issues remain"
          fi
```

## Summary

Effective Beads usage follows these principles:

1. **Session Start** → Query ready work (`bd ready --json`)
2. **During Work** → Create discoveries (`bd create` + link with `discovered-from`)
3. **Task Completion** → Close with reason (`bd close --reason`)
4. **Avoid Pitfall** → Never create cycles, always link discoveries, update status
5. **Multi-Agent** → Use ID prefixes, rely on git sync
6. **Maintenance** → Periodic compaction for large databases

By following these patterns, agents maintain perfect context across sessions and projects scale gracefully.
