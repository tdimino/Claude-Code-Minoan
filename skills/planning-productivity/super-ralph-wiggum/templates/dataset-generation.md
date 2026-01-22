# Dataset Generation Template

## Task

Generate training data samples that meet quality criteria, tracking progress until target count reached.

## Process

1. **Read the dataset specification**:
   - Target count (how many samples needed)
   - Quality criteria (what makes a good sample)
   - Output format (JSON, JSONL, CSV, etc.)
   - Output directory/file

2. **Check current progress**:
   - Read @progress.txt for current count
   - Check output file/directory for existing samples

3. **Generate ONE batch of samples** (5-10 samples):
   - Follow the format specification exactly
   - Ensure variety (no duplicates)
   - Meet all quality criteria

4. **Validate each sample**:
   - Check format is correct
   - Verify quality criteria met
   - Ensure uniqueness

5. **Save valid samples** to output file/directory

6. **Log progress** - append to @progress.txt:
   ```
   ## Iteration N - [timestamp]
   - Generated: [count] samples
   - Valid: [count] samples
   - Total: [cumulative count] / [target]
   - Quality notes: [any patterns or issues]
   ---
   ```

7. **Update Codebase Patterns** (top of progress.txt) with:
   - Common quality issues to avoid
   - Good patterns that worked well
   - Edge cases to include

## Rules

- Generate 5-10 samples per iteration
- Validate EVERY sample before saving
- Track cumulative count accurately
- Maintain variety (check for duplicates)
- Document quality patterns discovered

## Quality Guidelines

### Good Samples
- Realistic and diverse
- Cover edge cases
- Follow exact format spec
- No duplicates or near-duplicates

### Bad Samples
- Repetitive or templated
- Missing required fields
- Invalid format
- Too similar to existing samples

## Sample Formats

### JSONL (one JSON object per line)
```json
{"input": "...", "output": "...", "metadata": {...}}
```

### CSV
```csv
input,output,label
"text1","response1","category1"
```

### JSON Array
```json
[
  {"input": "...", "output": "..."},
  {"input": "...", "output": "..."}
]
```

## Completion

When cumulative sample count reaches the target, output:

<promise>COMPLETE</promise>

Do NOT output this until target count is genuinely reached.
