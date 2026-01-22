# Duplication Loop Template

Find and eliminate duplicate code using copy-paste detection tools.

## Philosophy

Duplicate code is a maintenance burden. When logic is repeated, bugs must be fixed in multiple places. This template uses jscpd (or similar tools) to find clones and systematically extract them into shared utilities.

## Task

Reduce code duplication by extracting repeated patterns into reusable functions.

## Process

1. **Run duplication scan**:
   ```bash
   # JavaScript/TypeScript
   npx jscpd src/ --reporters console --min-lines 5 --min-tokens 50

   # With HTML report (useful for reviewing)
   npx jscpd src/ --reporters html --output ./jscpd-report

   # Python
   cpd --minimum-tokens 50 --language python --files src/
   ```

2. **Identify ONE duplication group** to address:
   - Prioritize by number of clones (more clones = higher value)
   - Consider file proximity (same module = easier extraction)
   - Assess semantic meaning (is this truly the same logic?)

3. **Extract shared code**:
   - Create utility function in appropriate location
   - Give it a clear, descriptive name
   - Add JSDoc/docstring explaining purpose
   - Consider edge cases the duplicated code might handle differently

4. **Update all call sites**:
   - Replace duplicated code with calls to new utility
   - Verify behavior is identical
   - Handle any site-specific variations via parameters

5. **Run verification**:
   ```bash
   npm run typecheck && npm test && npm run lint
   ```

6. **Commit the refactor**:
   ```
   refactor: extract formatDate utility from 4 locations
   refactor: consolidate API error handling into handleApiError
   ```

7. **Log progress** - append to @progress.txt:
   ```
   ## Iteration N - [timestamp]
   - Duplication: [brief description]
   - Locations: [count] files
   - Lines saved: [estimate]
   - New utility: [file:function]
   - jscpd duplicates remaining: [count]
   ---
   ```

## Rules

- Work on ONE duplication group per iteration
- Don't over-abstract—if variations are significant, they may not be true duplicates
- Run verification before committing
- If extraction breaks tests, the duplicated code wasn't truly identical
- Keep utilities focused—one responsibility per function

## Prioritization

1. **High clone count** - 4+ identical blocks = high value extraction
2. **Same module** - Easier to extract, clearer abstraction
3. **Large blocks** - 20+ lines of duplication = more maintenance burden
4. **Business logic** - More valuable than boilerplate

## Common Extraction Patterns

### Validation Logic
```typescript
// Before (duplicated)
if (!email || !email.includes('@')) { throw new Error('Invalid email'); }

// After (extracted)
import { validateEmail } from './utils/validation';
validateEmail(email);
```

### API Call Patterns
```typescript
// Before (duplicated)
try {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
} catch (e) { ... }

// After (extracted)
import { fetchJson } from './utils/api';
const data = await fetchJson(url);
```

### Formatting
```typescript
// Before (duplicated)
`${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`

// After (extracted)
import { formatDate } from './utils/format';
formatDate(date); // "2026-01-22"
```

## Completion

When jscpd reports duplications below the threshold (e.g., <5% or 0 significant clones), output:

<promise>COMPLETE</promise>

Do NOT output this until duplication is acceptably low.

## Example Progress Log

```markdown
# Ralph Progress Log - Duplication Loop

## Codebase Patterns
- jscpd threshold: 5 lines minimum, 50 tokens
- Utilities go in src/utils/
- Test command: npm test

---

## Iteration 1 - 2026-01-22 10:00
- Duplication: Date formatting pattern
- Locations: 6 files (api/, components/, services/)
- Lines saved: ~24 lines
- New utility: src/utils/format.ts:formatDate
- jscpd duplicates remaining: 12
---

## Iteration 2 - 2026-01-22 10:10
- Duplication: API error handling
- Locations: 4 files (services/)
- Lines saved: ~40 lines
- New utility: src/utils/api.ts:handleApiError
- jscpd duplicates remaining: 8
---
```
