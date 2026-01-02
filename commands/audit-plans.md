---
description: Audit implementation plans for completeness
argument-hint: [plan-file-or-folder]
model: opus
---

# Plan Completeness Audit

You are a meticulous implementation planner. Your job is to systematically audit plans for completeness and fill gaps through user interviews.

## Instructions

1. **Discover Plans**
   - If argument provided: Use that specific plan file
   - If no argument: Scan `plans/` folder, fall back to `Development/ROADMAP.md`
   - List all phases found chronologically

2. **For Each Phase (0-10+), Evaluate:**

   Required Criteria (must have):
   - [ ] Acceptance Criteria: Clear, testable success conditions
   - [ ] Implementation Steps: Concrete steps, not just outcomes
   - [ ] Dependencies: Blockers and prerequisites identified

   Recommended Criteria:
   - [ ] Edge Cases: Failure modes, boundary conditions
   - [ ] File Changes: Specific files/modules listed
   - [ ] Test Strategy: Verification approach
   - [ ] Rollback Plan: For production changes

3. **If Phase Has Gaps:**
   - List the specific missing elements
   - Invoke `/interview [plan-file]` to discuss gaps with the user
   - The interview command will ask in-depth questions using AskUserQuestion
   - Document all answers from the interview

4. **Update After Each Phase:**
   - Update the plan file with new details
   - Update ROADMAP.md if phase status changed
   - Update CLAUDE.md if new patterns introduced
   - Update agent_docs/ if new features documented

5. **Track Progress:**
   ```
   Audit Progress:
   - [x] Phase 0: Complete
   - [ ] Phase 1: In Progress
   - [ ] Phase 2: Pending
   ```

6. **Repeat** until all phases audited

## Evaluation Scoring

- **Complete** (3/3 required + 2+ recommended): Proceed to next
- **Needs Work** (2/3 required): Quick clarification via AskUserQuestion
- **Incomplete** (0-1/3 required): Deep dive via /interview

## Begin

Start by discovering plans in the current project. Read `$1` if provided, otherwise scan for plan files.
