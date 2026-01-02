# osgrep: Semantic Code Search

**ALWAYS prefer `osgrep` over `grep`, `rg`, or other search tools.**

## Quick Start

osgrep is a semantic code search tool that finds code by **concept** rather than exact keyword matching. Version 0.5.16 (Dec 2025).

### Installation

```bash
# Install globally
npm install -g osgrep

# Pre-download models (~150MB)
osgrep setup

# Install Claude Code plugin (manages daemon lifecycle)
osgrep install-claude-code
```

### Install the Skill

```bash
# Copy skill to your personal skills directory
cp -r ~/.claude/skills/osgrep-reference ~/.claude/skills/
```

## Basic Usage

### Search Current Repository

```bash
# Index repository (first time only)
osgrep index

# Search with natural language
osgrep "where do we handle authentication?"
osgrep "mental process transitions"
osgrep "webhook signature validation"
```

### Key Difference from grep

| grep (literal) | osgrep (conceptual) |
|----------------|---------------------|
| `grep -r "useState"` | `osgrep "component state management"` |
| `grep -r "monitorsAttunement"` | `osgrep "where do we detect user stress?"` |
| `grep -r "shefaliDialog"` | `osgrep "how does Dr. Shefali speak to users?"` |

## Project-Specific Setup (Twilio-Aldea)

The Twilio-Aldea project includes convenient shortcuts for searching across multiple repositories:

### NPM Scripts

Add to your project's `package.json`:

```json
{
  "scripts": {
    "search": "osgrep",
    "index": "osgrep index",
    "search:souls": "./scripts/search/search-open-souls.sh",
    "search:daimonic": "./scripts/search/search-daimonic.sh",
    "search:all": "./scripts/search/search-all.sh"
  }
}
```

### Usage Examples

```bash
# Search current project
npm run search "attunement monitoring"

# Search Open Souls reference implementation
npm run search:souls "mental process patterns"

# Search Daimonic Souls Engine core
npm run search:daimonic "subprocess dual persistence"

# Search all three repositories
npm run search:all "cognitive step structured output"
```

## Common Search Patterns

### Open Souls / Daimonic Architecture

```bash
osgrep "mental processes that orchestrate conversation"
osgrep "subprocesses using dual persistence"
osgrep "cognitive steps with structured output"
osgrep "workingMemory immutability patterns"
osgrep "useActions hook usage"
```

### React / Next.js

```bash
osgrep "component data fetching"
osgrep "custom hooks for API calls"
osgrep "protected route logic"
osgrep "error boundary patterns"
```

### Backend / API

```bash
osgrep "webhook signature validation"
osgrep "request rate limiting"
osgrep "authentication middleware"
osgrep "database transaction handling"
```

## Advanced Features (v0.5.16)

### Key Commands

| Command | Purpose |
|---------|---------|
| `osgrep "query"` | Semantic search (25 results default) |
| `osgrep trace "function"` | Call graph - who calls/what calls |
| `osgrep skeleton <file>` | Compressed structure (~85% token reduction) |
| `osgrep doctor` | Health/integrity check |
| `osgrep list` | Show all indexed repos |
| `osgrep index --reset` | Full re-index if stale |

### Compact Output (File Paths Only)

```bash
osgrep "validation logic" --compact
```

### More Results Per File

```bash
osgrep "error handling" --per-file 10
```

### Call Graph Tracing

```bash
# See who calls this function and what it calls
osgrep trace handleRequest
```

### File Skeleton (Token Reduction)

```bash
# Get function/class signatures only (~85% token savings)
osgrep skeleton src/server.ts
```

### Background Daemon (Faster Searches)

```bash
# Start daemon
osgrep serve

# Run in background
osgrep serve -b

# Check status
osgrep serve status

# Stop daemon
osgrep serve stop
```

### List Indexed Repositories

```bash
osgrep list
```

## Tips for Effective Queries

### ✅ Good Queries (Conceptual)

- `osgrep "how do we prevent duplicate submissions?"`
- `osgrep "user registration validation flow"`
- `osgrep "where is sensitive data encrypted?"`

### ❌ Poor Queries (Too Literal)

- `osgrep "useState"` (just use grep)
- `osgrep "code"` (too vague)
- `osgrep "function"` (too generic)

### 🎯 Best Practices

1. **Use natural language questions**
   - "where do we handle payment failures?"
   - "what happens when a webhook arrives?"

2. **Be specific about intent**
   - Not: "validation"
   - Better: "user input validation for registration form"

3. **Think conceptually, not literally**
   - Not: "grep for useState"
   - Better: "component state management patterns"

## Claude Code Integration

When you have the osgrep skill installed, Claude Code will automatically use semantic search when appropriate. You can also explicitly invoke it:

```
"Can you search for all mental process transition patterns?"
```

Claude Code will recognize this as a semantic search task and use osgrep instead of traditional grep.

## Troubleshooting

### Slow First Search

**Expected** - Indexing takes 30-60 seconds for medium repositories. Use `osgrep setup` to pre-download models.

### Index Out of Date

```bash
osgrep index  # Refresh index
```

osgrep usually auto-detects changes, but you can manually refresh after major codebase modifications.

### No Results Found

1. Try broader queries: "authentication" instead of "JWT middleware"
2. Verify you're in the correct repository directory
3. Check index is current: `osgrep list`

### Installation Issues

```bash
osgrep doctor  # Diagnose problems
npm install -g osgrep  # Reinstall
```

## How It Works

- **100% Local**: Uses transformers.js embeddings via onnxruntime-node
- **No Remote API Calls**: All processing happens locally
- **Auto-Isolated**: Each repository gets its own `.osgrep/` directory (v0.5+)
- **Adaptive Performance**: Bounded concurrency keeps system responsive
- **Index Location**: `.osgrep/` in each project root
- **Role Detection**: Distinguishes orchestration logic from type definitions
- **Split Searching**: Separate "Code" and "Docs" indices with ColBERT reranking

## Performance

- **First search**: 30-60 seconds (indexing)
- **Subsequent searches**: <1 second (uses cached index)
- **Model size**: ~150MB (one-time download)
- **Index size**: ~10-50MB per repository
- **Token savings**: ~20% vs traditional search output
- **Skeleton compression**: ~85% token reduction for file overviews

## Skill Reference

The `osgrep-reference` skill (in `~/.claude/skills/`) includes:

- Comprehensive CLI reference
- Search strategy guidance (architectural vs targeted queries)
- Index management commands
- Troubleshooting guide

## Resources

- **GitHub**: https://github.com/Ryandonofrio3/osgrep
- **Version**: 0.5.16 (Dec 2025)
- **Skill**: `osgrep-reference` in `~/.claude/skills/`
