# Documentation Generation Template

## Task

Generate documentation for undocumented public functions, classes, and modules.

## Process

1. **Identify undocumented code**:
   - Find public exports without JSDoc/docstrings
   - Prioritize by usage (more used = more important)
   - Check for missing README sections

2. **Select ONE item** to document this iteration:
   - A function without JSDoc
   - A class without documentation
   - A module without README
   - An API endpoint without docs

3. **Write comprehensive documentation**:

   For functions/methods:
   ```typescript
   /**
    * Brief description of what it does.
    *
    * @param paramName - Description of parameter
    * @returns Description of return value
    * @throws {ErrorType} When this error occurs
    * @example
    * ```typescript
    * const result = myFunction('input');
    * // result: expected output
    * ```
    */
   ```

   For classes:
   ```typescript
   /**
    * Brief description of the class purpose.
    *
    * @example
    * ```typescript
    * const instance = new MyClass();
    * instance.doSomething();
    * ```
    */
   ```

   For modules (README.md):
   - Purpose and overview
   - Installation/setup
   - Basic usage examples
   - API reference
   - Common patterns

4. **Verify examples work**:
   - Run code examples to ensure they compile
   - Check that output matches documentation
   - Test edge cases mentioned

5. **Commit** the documentation:
   ```
   docs(<scope>): add documentation for [item]
   ```

6. **Log progress** - append to @progress.txt:
   ```
   ## Iteration N - [timestamp]
   - Documented: [function/class/module name]
   - Type: [JSDoc/README/API docs]
   - File: [filename]
   ---
   ```

## Rules

- Document ONE item per iteration
- Include at least one working example
- Verify examples actually run
- Don't document obvious getters/setters
- Focus on public API, not internals

## Quality Checklist

- [ ] Description is clear and concise
- [ ] All parameters documented
- [ ] Return value documented
- [ ] Errors/exceptions documented
- [ ] At least one example provided
- [ ] Example actually works

## Completion

When all public exports have documentation, output:

<promise>COMPLETE</promise>

Do NOT output this while undocumented public APIs remain.
