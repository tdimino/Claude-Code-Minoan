# Lint Error Fixing Template

## Task

Fix all linting errors incrementally, one file at a time.

## Process

1. **Run the linter** to get current errors:
   ```bash
   pnpm lint  # or npm run lint, eslint ., etc.
   ```

2. **Identify the file** with the most errors (or highest severity errors).

3. **Fix ALL errors in that file**:
   - Address each error systematically
   - Prefer fixes that improve code quality
   - Don't just disable rules without good reason

4. **Run linter again** to verify fixes:
   ```bash
   pnpm lint
   ```

5. **Run tests** to ensure fixes didn't break anything:
   ```bash
   pnpm test  # or npm test
   ```

6. **Commit** the fixes:
   ```
   fix(lint): resolve [N] errors in [filename]
   ```

7. **Log progress** - append to @progress.txt:
   ```
   ## Iteration N - [timestamp]
   - File: [filename]
   - Errors fixed: [count]
   - Remaining files: [count]
   ---
   ```

8. **Move to next file** with most errors.

## Rules

- Fix ONE file per iteration
- Fix ALL errors in that file before moving on
- Run tests after each file to catch regressions
- Don't disable rules without documenting why
- If a rule is consistently problematic, note it in progress.txt

## Common Fixes

### ESLint/TypeScript
- `@ts-ignore` → Fix the type issue or add proper typing
- `any` → Add specific type
- Unused variables → Remove or prefix with `_`
- Missing return types → Add explicit return type

### Prettier
- Run `pnpm format` or `npm run format` to auto-fix

### Style Issues
- Prefer auto-fix: `pnpm lint --fix`
- Then manually fix remaining issues

## Completion

When linter reports zero errors, output:

<promise>COMPLETE</promise>

Do NOT output this while any lint errors remain.
