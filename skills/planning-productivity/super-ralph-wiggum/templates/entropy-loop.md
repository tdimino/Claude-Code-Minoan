# Entropy Loop Template

Reverse software entropy by systematically cleaning code smells.

## Philosophy

Software entropy is the tendency of codebases to deteriorate over time. Dead code accumulates, patterns drift, TODOs pile up. Ralph can accelerate entropy—or reverse it.

This template scans for code smells and fixes them one at a time, leaving the codebase better than it was found.

## Task

Identify and fix code smells incrementally until the codebase is clean.

## Process

1. **Scan for code smells** using appropriate tools:
   ```bash
   # Unused exports (TypeScript/JavaScript)
   npx knip
   # or
   npx ts-prune

   # Dead code detection
   npx ts-unused-exports tsconfig.json

   # Find TODOs and FIXMEs
   grep -rn "TODO\|FIXME" src/

   # Inconsistent patterns (via linter)
   npm run lint
   ```

2. **Prioritize smells** by impact:
   - Unused exports (may indicate dead modules)
   - Dead code paths (unreachable branches)
   - Inconsistent patterns (naming, structure)
   - Stale TODOs/FIXMEs (over 30 days old)
   - Type `any` usage (TypeScript)

3. **Fix ONE issue** per iteration:
   - Remove unused export/code
   - Resolve or remove TODO
   - Fix inconsistent pattern
   - Add proper types

4. **Run verification**:
   ```bash
   npm run typecheck && npm test && npm run lint
   ```

5. **Commit the fix**:
   ```
   chore(cleanup): remove unused export in utils.ts
   chore(cleanup): resolve TODO in auth.ts
   refactor: standardize naming in api/
   ```

6. **Log progress** - append to @progress.txt:
   ```
   ## Iteration N - [timestamp]
   - Smell: [type of smell]
   - File: [filename]
   - Action: [what was done]
   - Remaining: [count of similar smells]
   ---
   ```

## Rules

- Work on ONE smell per iteration
- Run verification before committing
- If removal breaks tests, investigate before proceeding
- Don't remove code that's used via dynamic imports or reflection
- If a TODO is actionable, either fix it or create an issue—don't leave it

## Smell Priority Order

1. **Unused exports** - May indicate entire modules are dead
2. **Type `any`** - Type safety holes
3. **Dead code** - Unreachable branches, commented code
4. **Stale TODOs** - Technical debt markers
5. **Inconsistent patterns** - Naming, structure

## Completion

When the scan shows no actionable smells (all tools report clean), output:

<promise>COMPLETE</promise>

Do NOT output this until the codebase passes all smell checks.

## Example Progress Log

```markdown
# Ralph Progress Log - Entropy Loop

## Codebase Patterns
- Using `npm run lint` for style checks
- Using `npx knip` for unused exports
- Test command: `npm test`

---

## Iteration 1 - 2026-01-22 10:00
- Smell: Unused export
- File: src/utils/deprecated.ts
- Action: Removed entire file (no imports found)
- Remaining: 12 unused exports
---

## Iteration 2 - 2026-01-22 10:05
- Smell: Type any
- File: src/api/client.ts:45
- Action: Added proper Response type
- Remaining: 8 any types
---
```
