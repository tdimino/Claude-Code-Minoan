# Prompt Patterns for Ralph Wiggum Loops

Effective prompts are critical for Ralph loops to converge. This reference covers patterns that lead to successful autonomous iteration.

## The Anatomy of a Convergent Prompt

A well-structured Ralph prompt has five components:

```
1. CONTEXT INJECTION (@files)
2. TASK DESCRIPTION (what to accomplish)
3. COMPLETION CRITERIA (when to stop)
4. PROCESS (step-by-step procedure)
5. RULES (constraints and guardrails)
```

## Pattern 1: Scoped Single-Item Work

**Problem**: Agent tries to do too much, exhausts context window.

**Solution**: Explicitly scope to ONE item per iteration.

```
WRONG:
"Fix all the lint errors in the codebase"

RIGHT:
"Fix lint errors in ONE file at a time.
Pick the file with the most errors.
Fix all errors in that file before moving on.
If no errors remain, output <promise>COMPLETE</promise>."
```

## Pattern 2: Verification-First Workflow

**Problem**: Agent makes changes that break things.

**Solution**: Always verify before committing.

```
PROCESS:
1. Make the change
2. Run verification: pnpm test && pnpm typecheck && pnpm lint
3. IF ANY VERIFICATION FAILS:
   - Debug and fix the issue
   - Re-run verification
   - Do NOT proceed until green
4. Only commit when all checks pass
```

## Pattern 3: Progress File Protocol

**Problem**: Context doesn't persist between iterations.

**Solution**: Use @file injection and explicit append instructions.

```
@progress.txt

[Your task description]

After completing work, APPEND (do not overwrite) to progress.txt:
- Iteration number
- What was accomplished
- Any blockers or issues
- Current status
```

## Pattern 4: Explicit Completion Signals

**Problem**: Loop runs forever because completion isn't detected.

**Solution**: Use unambiguous, exact-match completion markers.

```
WRONG:
"When done, say you're finished"

RIGHT:
"When ALL of the following are true:
- Test coverage >= 90%
- All tests pass
- No lint errors
Output EXACTLY: <promise>COMPLETE</promise>

Do NOT output this phrase until ALL criteria are met."
```

## Pattern 5: Priority-Based Selection (Severity)

**Problem**: Agent works on low-value items first.

**Solution**: Specify priority criteria by severity.

```
Select the next item to work on using this priority:
1. Highest severity (errors before warnings)
2. Most impactful (user-facing before internal)
3. Easiest to fix (quick wins first)

Document your selection reasoning in progress.txt.
```

## Pattern 5b: Risk-Based Prioritization

**Problem**: Agent picks easy tasks first, leaving risky architectural work for later.

**Solution**: Prioritize by risk, not by ease.

```
When choosing the next task, prioritize in this order:

1. Architectural decisions and core abstractions
2. Integration points between modules
3. Unknown unknowns and spike work
4. Standard features and implementation
5. Polish, cleanup, and quick wins

Fail fast on risky work. Save easy wins for later.

Rationale: Code from architectural decisions stays forever.
Shortcuts here cascade through the entire project.
```

Use this pattern for feature development (PRD-based loops). Use Pattern 5 for cleanup loops (lint, coverage).

## Pattern 6: Atomic Commits

**Problem**: Large commits make it hard to debug failures.

**Solution**: One logical change per commit.

```
Commit after EACH successful change:
- One test file = one commit
- One bug fix = one commit
- One refactor = one commit

Commit message format: type(scope): description
Examples:
- test(auth): add login error handling tests
- fix(api): handle null response from endpoint
- refactor(utils): extract date formatting
```

## Pattern 7: Defensive Coding

**Problem**: Changes break existing functionality.

**Solution**: Add guards and rollback instructions.

```
BEFORE making any change:
1. Run the test suite to establish baseline
2. Note which tests currently pass

AFTER making changes:
1. Run the test suite again
2. If any PREVIOUSLY PASSING test now fails:
   - Your change broke something
   - Revert and try a different approach
3. Only commit if all baseline tests still pass
```

## Pattern 8: Blockers and Skip Logic

**Problem**: Agent gets stuck on an impossible task.

**Solution**: Provide escape hatches.

```
If you encounter a blocker you cannot resolve:
1. Document the blocker in progress.txt
2. Add a TODO comment in the code
3. Skip this item and move to the next
4. Do NOT output <promise>COMPLETE</promise>

Blockers include:
- Missing dependencies
- External service unavailable
- Requires manual intervention
- Unclear requirements
```

## Pattern 9: Incremental Targets

**Problem**: Binary success/failure doesn't show progress.

**Solution**: Use progressive milestones.

```
Coverage Milestones:
- 50% → Continue to 60%
- 60% → Continue to 70%
- 70% → Continue to 80%
- 80% → Continue to 90%
- 90% → Output <promise>COMPLETE</promise>

Log each milestone reached in progress.txt.
```

## Pattern 10: Context Preservation

**Problem**: Important context is lost between iterations.

**Solution**: Structured progress logging.

```
Append to progress.txt using this format:

## Iteration [N]
**File**: [filename]
**Action**: [what was done]
**Result**: [success/partial/blocked]
**Coverage**: [X%] → [Y%]
**Next**: [what should be done next]
---
```

## Anti-Patterns to Avoid

### 1. Vague Completion Criteria
❌ "When everything looks good"
✅ "When all tests pass AND coverage >= 80%"

### 2. Unbounded Scope
❌ "Improve the codebase"
✅ "Add JSDoc comments to exported functions in src/utils/"

### 3. Missing Verification
❌ "Make the change and commit"
✅ "Make the change, run tests, commit only if passing"

### 4. Implicit Progress
❌ (Assuming Claude remembers what happened)
✅ "@progress.txt to see previous iterations"

### 5. Ambiguous Priorities
❌ "Fix the important issues"
✅ "Fix P0 errors first, then P1, then P2"

## Template: Complete Prompt Structure

```
@progress.txt @prd.json

TASK: [Clear one-sentence description]

COMPLETION CRITERIA:
When ALL of these are true, output <promise>COMPLETE</promise>:
- [Criterion 1]
- [Criterion 2]
- [Criterion 3]

PROCESS:
1. [Step with verification]
2. [Step with verification]
3. [Commit step]
4. [Logging step]

RULES:
- Work on ONE [item] per iteration
- Run [verification] before committing
- Append progress to progress.txt
- If blocked, document and skip
```
