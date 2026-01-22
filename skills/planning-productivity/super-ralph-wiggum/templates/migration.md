# Framework Migration Template

## Task

Migrate codebase to a new framework, library version, or dependency, one module at a time.

## Process

1. **Read the migration plan**:
   - Source version/framework
   - Target version/framework
   - Breaking changes to address
   - Migration guide/documentation

2. **Identify modules to migrate**:
   - List all files/modules using old API
   - Prioritize by dependency order (migrate dependencies first)
   - Track migrated vs remaining

3. **Select ONE module** to migrate this iteration:
   - Choose module with fewest dependencies on unmigrated code
   - Or choose highest-impact module

4. **Migrate the module**:
   - Update imports/requires
   - Replace deprecated APIs with new equivalents
   - Update type definitions if needed
   - Handle breaking changes per migration guide

5. **Run verification**:
   ```bash
   pnpm typecheck && pnpm test
   ```

   If verification fails:
   - Check migration guide for missed changes
   - Fix issues before proceeding
   - Re-run verification until green

6. **Commit** the migration:
   ```
   refactor: migrate [module] from [old] to [new]
   ```

7. **Log progress** - append to @progress.txt:
   ```
   ## Iteration N - [timestamp]
   - Module: [module name]
   - Changes: [summary of changes]
   - Migrated: [X] / [total] modules
   - Issues: [any problems encountered]
   ---
   ```

8. **Update Codebase Patterns** with migration learnings:
   - API mappings that worked
   - Gotchas encountered
   - Patterns to follow for remaining modules

## Rules

- Migrate ONE module per iteration
- Ensure tests pass after each migration
- Follow the migration guide
- Document patterns for future iterations
- Don't skip modules (unless genuinely not needed)

## Common Migration Patterns

### Import Updates
```typescript
// Old
import { oldApi } from 'old-package';

// New
import { newApi } from 'new-package';
```

### API Replacements
```typescript
// Old
oldApi.deprecatedMethod(arg);

// New
newApi.newMethod(transformedArg);
```

### Type Updates
```typescript
// Old
type OldType = { ... };

// New
type NewType = { ... };
```

### Configuration Changes
- Update config files (tsconfig, eslint, etc.)
- Update package.json scripts
- Update environment variables

## Completion

When ALL modules are migrated and tests pass, output:

<promise>COMPLETE</promise>

Do NOT output this while any unmigrated modules remain.
