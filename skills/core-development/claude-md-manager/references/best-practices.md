# CLAUDE.md Best Practices Deep Dive

Comprehensive patterns for creating effective CLAUDE.md files based on research from Anthropic, HumanLayer, and production implementations.

## Table of Contents
- [Context Window Economics](#context-window-economics)
- [The WHAT/WHY/HOW Framework](#the-whatwhyhow-framework)
- [Progressive Disclosure Mastery](#progressive-disclosure-mastery)
- [File Import Patterns](#file-import-patterns)
- [Measuring Effectiveness](#measuring-effectiveness)
- [Maintenance Strategies](#maintenance-strategies)
- [Advanced Patterns](#advanced-patterns)

## Context Window Economics

### Why Every Line Matters

Claude Code's system prompt contains ~50 baseline instructions. Frontier LLMs can reliably follow 150-200 instructions. This leaves ~100-150 instruction slots for your CLAUDE.md and conversation.

**Token cost calculation:**
- Average CLAUDE.md line: ~15 tokens
- 100-line file: ~1,500 tokens
- 300-line file: ~4,500 tokens
- Conversation history: 2,000-10,000+ tokens
- System prompt: ~2,000 tokens

**Impact of bloat:**
- Instructions compete for attention
- Irrelevant context degrades all instruction-following
- Claude explicitly ignores instructions marked "may or may not be relevant"

### Right-Sizing by Project Complexity

| Project Type | Target Lines | Pattern |
|-------------|--------------|---------|
| Simple script/CLI | 20-40 | Single CLAUDE.md |
| Standard app | 60-100 | CLAUDE.md + 1-2 imports |
| Complex monorepo | 60-80 + agent_docs/ | Progressive disclosure |
| Enterprise codebase | 40-60 + heavy imports | Hierarchical files |

## The WHAT/WHY/HOW Framework

### WHAT: Technical Reality

Document only what Claude cannot infer from the code itself:

**Include:**
- Non-obvious tech stack choices (e.g., "Next.js App Router, NOT Pages")
- Architecture boundaries (service ownership, data flow)
- Non-standard file locations
- Build tool specifics (bun vs npm vs pnpm)

**Exclude:**
- Obvious framework usage (if there's a React component, Claude knows it's React)
- Standard directory structures
- Common patterns visible in code

### WHY: Context and Purpose

Explain the reasoning behind non-obvious decisions:

```markdown
## Why We Use X

# Authentication uses sessions (not JWT) because:
# - SSR requires server-readable auth state
# - No mobile clients planned
# - Simpler revocation
```

### HOW: Practical Workflows

Focus on commands and procedures Claude must execute correctly:

```markdown
## Commands
- Dev: `pnpm dev` (NOT npm - pnpm workspaces required)
- Test: `pnpm test --coverage` (required >80%)
- Deploy: `pnpm deploy:staging` then `pnpm deploy:prod`

## Workflow
- Always pull before pushing
- Squash before merge to main
- Run tests locally before PR
```

## Progressive Disclosure Mastery

### When to Split

**Split when:**
- CLAUDE.md exceeds 100 lines
- You have 3+ distinct workflow areas
- Team members work on isolated areas
- Instructions are highly task-specific

**Keep unified when:**
- File is under 60 lines
- All developers need all context
- Instructions are universally applicable

### Directory Structure Patterns

**By workflow stage:**
```
agent_docs/
├── setup.md          # Initial project setup
├── development.md    # Day-to-day development
├── testing.md        # Test writing and running
├── deployment.md     # Release process
└── troubleshooting.md # Common issues
```

**By domain:**
```
agent_docs/
├── frontend.md       # React/UI concerns
├── backend.md        # API/server concerns
├── database.md       # Schema and queries
├── infra.md          # DevOps/cloud
└── security.md       # Auth and access
```

**By team:**
```
agent_docs/
├── onboarding.md     # New team members
├── code-review.md    # PR standards
├── on-call.md        # Incident response
└── architecture.md   # Design decisions
```

### Reference Syntax in CLAUDE.md

```markdown
# Task-Specific Guides
- Setting up dev environment: @agent_docs/setup.md
- Writing tests: @agent_docs/testing.md
- Deploying changes: @agent_docs/deployment.md

Claude reads these when the task requires it.
```

## File Import Patterns

### Basic Imports

```markdown
# Import sibling files
@README.md
@CONTRIBUTING.md

# Import from subdirectories
@docs/api.md
@.github/PULL_REQUEST_TEMPLATE.md

# Import personal preferences (not committed)
@~/.claude/work-preferences.md
```

### Advanced Import Patterns

**Conditional documentation:**
```markdown
# When working on auth, see @docs/auth-architecture.md
# When working on payments, see @docs/payment-flow.md
# When debugging, see @docs/troubleshooting.md
```

**Team vs personal split:**
```markdown
# Team conventions (in repo)
@docs/conventions.md

# Personal preferences (in ~/.claude/)
# Add your own: @~/.claude/my-project-prefs.md
```

## Measuring Effectiveness

### Success Indicators

Your CLAUDE.md is effective when:
- Claude rarely asks for clarification on conventions
- Code reviews show consistent style adherence
- You stop repeating the same instructions
- Claude catches violations proactively
- New workflows are executed correctly first time

### Red Flags

Your CLAUDE.md needs work when:
- Claude ignores documented conventions
- You frequently add # instructions mid-conversation
- Claude asks questions answered in the file
- Generated code doesn't match project style
- Build/test commands fail consistently

### Iteration Using #

During conversations, press `#` to add instructions you're repeating:
1. Note instructions you give more than twice
2. Add them via `#` (appends to CLAUDE.md)
3. Review and organize quarterly
4. Move task-specific items to agent_docs/

## Maintenance Strategies

### Quarterly Review Checklist

- [ ] Remove outdated tech stack references
- [ ] Update changed commands
- [ ] Verify file references still exist
- [ ] Consolidate repeated patterns
- [ ] Move grown sections to agent_docs/
- [ ] Test all documented commands
- [ ] Remove instructions Claude now follows automatically

### Trigger-Based Updates

Update CLAUDE.md when:
- Major dependency upgrade
- Architecture refactor
- Team convention change
- New developer joins (test their experience)
- Claude repeatedly makes same mistake

### Version Control Best Practices

```bash
# Track as code
git add CLAUDE.md agent_docs/
git commit -m "docs: update CLAUDE.md for React 19 upgrade"

# Review in PRs like code
# Include CLAUDE.md in PR templates
```

## Advanced Patterns

### Context-Aware Instructions

```markdown
# When modifying database schema
1. Create migration: `pnpm db:migrate:create`
2. Apply locally: `pnpm db:migrate:dev`
3. Update types: `pnpm db:generate`
4. Test with: `pnpm test:db`

# When adding API endpoints
1. Add route in src/routes/
2. Add types in src/types/api.ts
3. Add tests in tests/api/
4. Update OpenAPI spec if public
```

### Negative Instructions (Use Sparingly)

```markdown
# Do NOT
- Create new utility files without checking /lib first
- Add dependencies without checking existing ones
- Modify migration files after merge to main
```

### Integration with Hooks

```markdown
# Pre-commit (automated, not in CLAUDE.md)
# See .claude/hooks/pre-commit for lint/format

# Post-implementation (Claude should do)
- Run type check: `pnpm typecheck`
- Update affected tests
- Check bundle size: `pnpm analyze`
```

### Team Synchronization

For teams, establish CLAUDE.md governance:
- Single owner for root CLAUDE.md
- PRs required for changes
- Document rationale for each instruction
- Regular team review of effectiveness

## Anti-Pattern Examples

### Too Verbose

```markdown
# BAD - 40 lines that could be 5
When you need to create a new React component, you should first
navigate to the src/components directory. Then create a new file
with the .tsx extension. The file name should be PascalCase...
[continues for 35 more lines]

# GOOD
## Components
- Location: src/components/{ComponentName}.tsx
- Style: Functional with hooks, no class components
- Tests: Required in __tests__/{ComponentName}.test.tsx
```

### Duplicating Code

```markdown
# BAD - copied code that will go stale
Here's our auth middleware:
\`\`\`typescript
export const authMiddleware = async (req, res, next) => {
  // 50 lines of code
}
\`\`\`

# GOOD - reference that stays current
Auth middleware: src/middleware/auth.ts:15-45
```

### Linting via LLM

```markdown
# BAD - waste of context and unreliable
Always ensure:
- 2 space indentation
- Trailing commas
- Single quotes
- Semicolons

# GOOD - use tools
# (No mention in CLAUDE.md - handled by .eslintrc and hooks)
```
