# Super Ralph Wiggum

Autonomous iteration loops for Claude Code based on the [Ralph Wiggum technique](https://ghuntley.com/ralph/) and [AI Hero's 11 Tips](https://www.aihero.dev/tips-for-ai-coding-with-ralph-wiggum).

> **The agent chooses the task, not you.** You define the end state. Ralph figures out how to get there.

## Quick Start

```
Run super-ralph-wiggum with test-coverage template, max 20 iterations
```

## Available Templates

| Template | Use Case |
|----------|----------|
| `test-coverage` | Improve test coverage to target % |
| `feature-prd` | Implement features from PRD file |
| `lint-fix` | Fix lint errors incrementally |
| `entropy-loop` | Remove dead code, smells, TODOs |
| `duplication-loop` | Extract duplicate code into utilities |
| `docs-generation` | Generate documentation |
| `dataset-generation` | Generate training data |
| `migration` | Framework/version migration |

## The 11 Tips

| # | Tip | Key Insight |
|---|-----|-------------|
| 1 | Ralph Is A Loop | Same prompt, multiple iterations |
| 2 | Start HITL, Then AFK | Learn → Trust → Let go |
| 3 | Define The Scope | Explicit stop conditions |
| 4 | Track Progress | progress.txt bridges context |
| 5 | Use Feedback Loops | Types, tests, linting |
| 6 | Take Small Steps | One change per commit |
| 7 | Prioritize Risky Tasks | Architecture first |
| 8 | Define Software Quality | Tell Ralph the repo type |
| 9 | Use Docker Sandboxes | AFK safety |
| 10 | Pay To Play | HITL still valuable |
| 11 | Make It Your Own | Customize loop types |

## Files

```
super-ralph-wiggum/
├── SKILL.md                 # Full documentation (read this)
├── README.md                # Quick reference (this file)
├── templates/               # Loop templates
│   ├── test-coverage.md
│   ├── feature-prd.md
│   ├── lint-fix.md
│   ├── entropy-loop.md
│   ├── duplication-loop.md
│   ├── docs-generation.md
│   ├── dataset-generation.md
│   └── migration.md
├── references/              # In-depth guides
│   ├── tips-and-tricks.md   # The 11 Tips expanded
│   ├── prompt-patterns.md   # 10 convergent prompt patterns
│   ├── prd-schema.md        # PRD file structure
│   ├── cost-estimation.md   # API cost guidelines
│   └── browser-testing.md   # Dev-browser integration
└── scripts/                 # Setup utilities
    └── setup-ralph-loop.sh
```

## Iteration Sizing

| Task Size | Iterations |
|-----------|------------|
| Small (lint, docs) | 5-10 |
| Medium (feature) | 15-30 |
| Large (migration) | 30-50 |

## Task Priority Order

1. Architectural decisions
2. Integration points
3. Unknown unknowns
4. Standard features
5. Polish and quick wins

## Key Commands

```bash
# Template mode
Use super-ralph-wiggum with test-coverage template, max 20 iterations

# PRD mode
Use super-ralph-wiggum with feature-prd template using ./prd.json

# HITL mode (single iteration)
Use super-ralph-wiggum with --once flag to fix authentication bug

# Cancel active loop
rm .claude/ralph-loop.local.md
```

## Attribution

- [Geoffrey Huntley](https://ghuntley.com/ralph/) - Original Ralph technique
- [Ryan Carson](https://x.com/ryancarson) - PRD-based workflows
- [Matt Pocock / AI Hero](https://www.aihero.dev/tips-for-ai-coding-with-ralph-wiggum) - The 11 Tips

---

**Full documentation**: See [SKILL.md](./SKILL.md)
