# Ralph Wiggum Cost Estimation Guide

Autonomous loops consume significant API credits. This guide helps estimate and manage costs.

## Cost Factors

### 1. Model Selection

| Model | Input (1M tokens) | Output (1M tokens) | Use Case |
|-------|-------------------|--------------------| ---------|
| Claude Opus 4.5 | $15.00 | $75.00 | Complex reasoning, architecture |
| Claude Sonnet 4 | $3.00 | $15.00 | General development (recommended) |
| Claude Haiku 3.5 | $0.80 | $4.00 | Simple iterations, high volume |

### 2. Context Size

Each iteration loads:
- System prompt (~2K tokens)
- Progress file (@progress.txt) - grows over time
- PRD/config files (@prd.json)
- Code context from file reads
- Previous tool outputs

**Typical iteration context**: 10K-50K input tokens

### 3. Output Volume

Each iteration generates:
- Reasoning and planning
- Code changes
- Commit messages
- Progress logging

**Typical iteration output**: 2K-10K tokens

## Cost Estimation Formula

```
Cost = Iterations × (Input_Tokens × Input_Rate + Output_Tokens × Output_Rate)
```

### Example: Test Coverage Loop

- Iterations: 20
- Model: Claude Sonnet
- Avg input: 30K tokens/iteration
- Avg output: 5K tokens/iteration

```
Cost = 20 × (30K × $3/1M + 5K × $15/1M)
     = 20 × ($0.09 + $0.075)
     = 20 × $0.165
     = $3.30
```

### Example: Feature Development (Large PRD)

- Iterations: 50
- Model: Claude Sonnet
- Avg input: 80K tokens/iteration (larger context)
- Avg output: 15K tokens/iteration

```
Cost = 50 × (80K × $3/1M + 15K × $15/1M)
     = 50 × ($0.24 + $0.225)
     = 50 × $0.465
     = $23.25
```

## Cost by Template Type

| Template | Typical Iterations | Typical Cost (Sonnet) |
|----------|-------------------|----------------------|
| test-coverage | 20-30 | $3-10 |
| lint-fix | 20-40 | $2-8 |
| docs | 15-30 | $3-7 |
| feature (small PRD) | 10-20 | $3-10 |
| feature (large PRD) | 40-60 | $20-50 |
| migration | 30-50 | $15-40 |
| dataset (100 items) | 50-100 | $10-30 |

## Cost Optimization Strategies

### 1. Use Haiku for Simple Tasks

For repetitive, mechanical tasks:

```bash
# Modify template to use Haiku
docker sandbox run claude --model haiku "@progress.txt ..."
```

Cost reduction: 70-80%

### 2. Limit Context Injection

Only inject what's necessary:

```bash
# Bad: Loading entire file
@large-config.json

# Good: Loading specific section
cat config.json | jq '.features' > features.json
@features.json
```

### 3. Rotate Progress Files

Progress files grow over time. Periodically summarize and rotate:

```bash
# Every 10 iterations, summarize progress
if (( i % 10 == 0 )); then
  # Summarize and rotate progress file
  head -20 progress.txt > progress-summary.txt
  echo "--- Previous iterations summarized above ---" >> progress-summary.txt
  mv progress-summary.txt progress.txt
fi
```

### 4. Early Exit on Errors

Don't waste iterations on broken states:

```bash
# Add pre-check
if ! pnpm test --passWithNoTests; then
  echo "Tests failing before iteration. Fix manually first."
  exit 1
fi
```

### 5. Set Conservative Limits

Start small, increase if needed:

```bash
# Start with 10 iterations
./ralph-loop.sh 10

# If incomplete, run 10 more (context is cleaner)
./ralph-loop.sh 10
```

## Monitoring Costs

### Using Claude API Dashboard

1. Go to console.anthropic.com
2. Navigate to Usage
3. Filter by date range
4. Monitor daily spend

### Using Docker Sandbox Metrics

```bash
# Track per-session costs
docker sandbox run claude --show-costs "@progress.txt ..."
```

### Budget Alerts

Set up spending limits in Anthropic console:
- Daily limit
- Monthly limit
- Per-session limit (if available)

## Real-World Cost Examples

### Geoffrey Huntley's 3-Month Loop

- Task: Build programming language "Cursed"
- Model: Mix of models
- Total iterations: Thousands
- Estimated cost: $500-2000

### Y Combinator Hackathon

- Task: 6 repositories overnight
- Duration: ~12 hours
- Cost: ~$297

### $50K Contract Completion

- Task: Full product implementation
- Method: PRD-based Ralph loops
- Cost: ~$297 (vs $50K contractor)

## Cost vs Value Analysis

Consider the value equation:

```
Value = (Time_Saved × Hourly_Rate) - API_Cost
```

Example:
- Developer hourly rate: $150
- Task would take: 8 hours
- Ralph completes in: 2 hours (monitoring) + $30 API
- Savings: (8 × $150) - (2 × $150 + $30) = $1200 - $330 = $870

## Appendix: Token Estimation

### Code Files
- 1 line of code ≈ 10-20 tokens
- 100-line file ≈ 1,500 tokens
- Large file (500 lines) ≈ 8,000 tokens

### Markdown/Docs
- 1 paragraph ≈ 100 tokens
- 1 page ≈ 500 tokens

### JSON
- Simple object ≈ 50 tokens
- PRD file ≈ 500-2,000 tokens
