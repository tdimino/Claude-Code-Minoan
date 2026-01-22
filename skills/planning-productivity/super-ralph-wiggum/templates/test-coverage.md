# Test Coverage Improvement Template

## Task

Improve test coverage by writing meaningful tests for user-facing behavior.

## Philosophy

A great test covers behavior users depend on. It validates real workflows, not implementation details. It catches regressions before users do.

Do NOT write tests just to increase coverage numbers. Use coverage as a guide to find UNTESTED USER-FACING BEHAVIOR.

If uncovered code is not worth testing (boilerplate, unreachable error branches, internal plumbing), add coverage ignore comments instead:
- `/* v8 ignore next */` for single lines
- `/* v8 ignore start */` ... `/* v8 ignore stop */` for blocks
- `/* istanbul ignore next */` for Istanbul/NYC

## Process

1. **Run coverage** to identify gaps:
   ```bash
   pnpm coverage  # or npm run coverage
   ```

2. **Analyze uncovered lines** and identify the most important USER-FACING FEATURE lacking tests.

   Prioritize:
   - Error handling users will encounter
   - CLI commands and options
   - Git operations and file parsing
   - API endpoints and validation
   - UI component behavior

   Deprioritize:
   - Internal utilities
   - Edge cases users won't hit
   - Boilerplate and glue code

3. **Write ONE meaningful test** that validates the feature works correctly for users.

4. **Run coverage again** - it should increase as a side effect of testing real behavior.

5. **Verify tests pass**:
   ```bash
   pnpm test  # or npm test
   ```

6. **Commit** with descriptive message:
   ```
   test(<file>): <describe the user behavior being tested>
   ```

7. **Log progress** - append to @progress.txt:
   ```
   ## Iteration N - [timestamp]
   - Tested: [feature/behavior]
   - Coverage: X% -> Y%
   - File: [test file created/modified]
   ---
   ```

## Rules

- Work on ONE test per iteration
- Prioritize user-facing behavior over coverage percentage
- Run verification before committing
- If a test is too complex, break into smaller tests
- Add ignore comments for genuinely untestable code

## Completion

When statement coverage reaches the target percentage, output:

<promise>COMPLETE</promise>

Do NOT output this until coverage target is genuinely reached.
