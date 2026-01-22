# Feature Development from PRD Template

## Task

Implement features from the PRD (Product Requirements Document) file, one feature per iteration.

## Process

1. **Read the PRD file** (@prd.json or specified PRD file)

2. **Find the next feature** to implement:
   - Filter to features where `passes: false`
   - Check dependencies: all features in `dependencies` array must have `passes: true`
   - Select the highest priority (lowest `priority` number)

3. **If no features available**:
   - All features have `passes: true` → output completion
   - Features blocked by dependencies → document blocker, skip iteration

4. **Read the feature details**:
   - `story`: What the user can do
   - `acceptance_criteria`: Specific requirements to satisfy
   - `notes`: Implementation hints (if any)

5. **Implement the feature**:
   - Focus on ONE feature only
   - Satisfy ALL acceptance criteria
   - Keep changes minimal and focused

6. **Run verification**:
   ```bash
   pnpm typecheck && pnpm test  # or npm run typecheck && npm test
   ```

   If verification fails:
   - Debug and fix the issue
   - Re-run verification
   - Do NOT proceed until green

7. **Update AGENTS.md** (if patterns discovered):
   - Add to AGENTS.md in directories with edited files
   - Include gotchas, conventions, dependencies
   - Don't add story-specific details

8. **Commit** with message:
   ```
   feat: [Feature ID] - [Feature Title]
   ```

9. **Update PRD**: Set `passes: true` for the completed feature

10. **Log progress** - append to @progress.txt:
    ```
    ## Iteration N - [timestamp]
    - Feature: [ID] - [title]
    - Status: COMPLETE
    - Files changed: [list]
    - Patterns learned: [any new patterns]
    ---
    ```

## Rules

- Work on ONE feature per iteration
- Verify ALL acceptance criteria are met
- Run typecheck + tests before committing
- Update AGENTS.md with reusable patterns
- Don't skip features (unless blocked by deps)

## Completion

When ALL features in the PRD have `passes: true`, output:

<promise>COMPLETE</promise>

The stop hook also auto-detects PRD completion.
