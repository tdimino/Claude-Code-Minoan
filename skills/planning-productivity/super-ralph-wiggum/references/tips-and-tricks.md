# The 11 Tips for Ralph Wiggum

Based on [Matt Pocock's AI Hero guide](https://www.aihero.dev/tips-for-ai-coding-with-ralph-wiggum), combined with learnings from Geoffrey Huntley, Ryan Carson, and real-world usage.

## Tip 1: Ralph Is A Loop

Ralph simplifies multi-phase planning. Instead of writing a new prompt for each phase, you run the same prompt in a loop:

```bash
for ((i=1; i<=$MAX_ITERATIONS; i++)); do
  claude -p "@prd.json @progress.txt [Your prompt]"
  # Check for completion
done
```

Each iteration:
1. Looks at a plan file to see what needs done
2. Looks at a progress file to see what's already done
3. Decides what to do next
4. Explores the codebase
5. Implements the feature
6. Runs feedback loops (types, linting, tests)
7. Commits the code

**The key insight: the agent chooses the task, not you.**

## Tip 2: Start HITL, Then AFK

### HITL (Human-In-The-Loop)

Interactive pair programming with Ralph:

- Use `--once` flag for single iterations
- Watch what Ralph does, step in when needed
- Great for learning how Ralph works
- Best for debugging and complex decisions

```
Use super-ralph-wiggum with --once flag to fix this specific bug
```

### AFK (Away From Keyboard)

Autonomous overnight coding:

- Always set `--max-iterations` (NEVER run infinitely)
- Small tasks: 5-10 iterations
- Medium tasks: 15-30 iterations
- Large features: 30-50 iterations

```
Use super-ralph-wiggum with test-coverage template, max 30 iterations
```

**The progression:**
1. Start with HITL to learn and refine
2. Go AFK once you trust your prompt
3. Review the commits when you return

### Notifications for Long Loops

Build a CLI to ping you on WhatsApp/Slack when Ralph finishes. This reduces context switching—you can fully engage with another task. Loops usually take 30-45 minutes, though they can run for hours.

## Tip 3: Define The Scope

Before you let Ralph run, define what "done" looks like. This is a shift from planning to requirements gathering.

### Formats For Defining Scope

- A markdown list of user stories
- GitHub issues or Linear tasks
- Using [beads](https://github.com/steveyegge/beads)
- PRD items with `passes` field (recommended)

```json
{
  "category": "functional",
  "description": "New chat button creates a fresh conversation",
  "steps": [
    "Click the 'New Chat' button",
    "Verify a new conversation is created",
    "Check that chat area shows welcome state"
  ],
  "passes": false
}
```

### Why Scope Matters

Vague tasks = risky loops. Ralph might:
- Loop forever, finding endless improvements
- Take shortcuts, declaring victory prematurely

**Be explicit:**
- Files to include (so Ralph won't ignore "edge case" files)
- Stop condition (so Ralph knows when "complete" means complete)
- Edge cases (so Ralph won't decide certain things don't count)

### Adjusting PRDs Mid-Flight

You can adjust while Ralph is running:
- Already implemented but wrong? Set `passes` back to `false`, add notes, rerun.
- Missing a feature? Add a new PRD item even mid-loop.

## Tip 4: Track Ralph's Progress

Every Ralph loop emits a `progress.txt` file, committed directly to the repo.

AI agents are like super-smart experts who forget everything between tasks. Without a progress file, Ralph must explore the entire repo to understand the current state.

### What Goes In The Progress File

- Tasks completed in this session
- Decisions made and why
- Blockers encountered
- Files changed

### Progress File Structure

```markdown
# Ralph Progress Log

## Codebase Patterns (TOP - most important!)
- Migrations: Use IF NOT EXISTS
- Types: Export from actions.ts
- Tests: Mock external services in beforeEach

---

## Iteration Log
(iterations appended below)
```

**Patterns at the top** ensure they're seen first, preventing repeated mistakes.

### Why Commits Matter

Ralph should commit after each feature:
- Clean `git log` showing what changed
- Ability to `git diff` against previous work
- Rollback point if something breaks

### Cleanup

Don't keep `progress.txt` forever. Once your sprint is done, delete it. It's session-specific, not permanent documentation.

## Tip 5: Use Feedback Loops

Ralph's success depends on feedback loops. The more loops you give it, the higher quality code it produces.

### Types of Feedback Loops

| Feedback Loop | What It Catches |
|---------------|-----------------|
| TypeScript types | Type mismatches, missing props |
| Unit tests | Broken logic, regressions |
| Playwright MCP | UI bugs, broken interactions |
| ESLint / linting | Code style, potential bugs |
| Pre-commit hooks | Blocks bad commits entirely |

The best setup blocks commits unless everything passes. Ralph can't declare victory if the tests are red.

### Verification Template

```bash
npm run typecheck && npm test && npm run lint
```

Templates enforce this—never skip it.

## Tip 6: Take Small Steps

The rate at which you can get feedback is your speed limit. Never outrun your headlights.

### Context Rot

LLMs get worse as context fills up. This is called **context rot**—the longer you go, the stupider the output.

### The Tradeoff

- Larger tasks = less frequent feedback, lower quality
- Smaller tasks = higher quality, but more iterations

### Sizing PRD Items

For AFK Ralph, keep items small. For HITL Ralph, you can make items slightly larger. But always bias small.

A refactor item might be as simple as:
> "Change one function's parameters. Verify tests and types pass."

### Guidance for Prompts

```
Keep changes small and focused:
- One logical change per commit
- If a task feels too large, break it into subtasks
- Prefer multiple small commits over one large commit
- Run feedback loops after each change, not at the end

Quality over speed. Small steps compound into big progress.
```

## Tip 7: Prioritize Risky Tasks

Without explicit guidance, Ralph will pick the easiest item or the first in the list.

### Task Prioritization Order

1. **Architectural decisions** and core abstractions
2. **Integration points** between modules
3. **Unknown unknowns** and spike work
4. **Standard features** and implementation
5. **Polish, cleanup**, and quick wins

Fail fast on risky work. Save easy wins for later.

### HITL For Risky Tasks

Use HITL Ralph for early architectural decisions—the code from these tasks stays forever. Any shortcuts here cascade through the entire project.

Save AFK Ralph for when the foundation is solid.

### Guidance for Prompts

```
When choosing the next task, prioritize in this order:
1. Architectural decisions and core abstractions
2. Integration points between modules
3. Unknown unknowns and spike work
4. Standard features and implementation
5. Polish, cleanup, and quick wins

Fail fast on risky work. Save easy wins for later.
```

## Tip 8: Explicitly Define Software Quality

The agent doesn't know what kind of repo it's in. Tell it explicitly.

### Repo Types

| Repo Type | What To Say | Expected Behavior |
|-----------|-------------|-------------------|
| Prototype | "Speed over perfection. Skip edge cases." | Takes shortcuts |
| Production | "Must be maintainable. Follow best practices." | Adds tests, docs |
| Library | "Public API. Backward compatibility matters." | Careful about breaking changes |

### The "Fight Entropy" Prompt

> This codebase will outlive you. Every shortcut you take becomes
> someone else's burden. Every hack compounds into technical debt
> that slows the whole team down.
>
> You are not just writing code. You are shaping the future of this
> project. The patterns you establish will be copied. The corners
> you cut will be cut again.
>
> Fight entropy. Leave the codebase better than you found it.

### The Repo Wins

Your instructions compete with your codebase. When Ralph sees two sources of truth—what you told it and what you actually did—**the codebase wins**.

If you write "never use `any` types" but your existing code is full of `any`, Ralph will follow the code.

**Agents amplify what they see.** Poor code leads to poorer code. Low-quality tests produce unreliable feedback loops.

Keep your codebase clean before letting Ralph loose.

## Tip 9: Use Docker Sandboxes

AFK Ralph needs permissions to edit files, run commands, and commit code. What stops it from running `rm -rf ~`?

```bash
docker sandbox run claude
```

This runs Claude Code inside a container. Your current directory is mounted, but nothing else. Ralph can edit project files and commit—but can't touch your home directory, SSH keys, or system files.

For HITL Ralph, sandboxes are optional—you're watching. For AFK Ralph, especially overnight loops, they're essential.

## Tip 10: Pay To Play

Ralph is completely configurable to how much you want to spend.

### HITL Is Still Worth It

If you never run AFK Ralph, HITL Ralph still has big benefits over multi-phase planning. Running the same prompt over and over feels nicer than specifying a different prompt for each phase.

### Cost Management

- Start small: Run 10 iterations, then 10 more if incomplete
- Use Haiku for simple tasks (70-80% cheaper)
- Rotate progress files—long ones waste tokens

```bash
# Every 10 iterations, summarize
head -20 progress.txt > progress-summary.txt
echo "--- Previous summarized ---" >> progress-summary.txt
mv progress-summary.txt progress.txt
```

### The Golden Age

For the next couple of years, we're in a golden age where you can do magical things with AI faster than humans—but the market still pays human wages. The market hasn't adjusted.

Yes, you have to pay. But the rewards are there if you're willing to claim them.

## Tip 11: Make It Your Own

Ralph is just a loop. That simplicity makes it infinitely configurable.

### Swap The Task Source

| Task Source | How It Works |
|-------------|--------------|
| GitHub Issues | Ralph picks an issue, implements it |
| Linear | Ralph pulls from your sprint |
| Beads | Ralph works through a beadfile |
| PRD file | Ralph reads `prd.json` |

### Change The Output

Instead of committing directly to main, each Ralph iteration could:
- Create a branch and open a PR
- Add comments to existing issues
- Update a changelog or release notes

### Alternative Loop Types

**Test Coverage Loop**: Point Ralph at your coverage metrics. It finds uncovered lines, writes tests, and iterates until coverage hits your target.

**Duplication Loop**: Hook Ralph up to `jscpd` to find duplicate code. Ralph identifies clones, refactors into shared utilities, and reports what changed.

**Linting Loop**: Feed Ralph your linting errors. It fixes them one by one, running the linter between iterations to verify each fix.

**Entropy Loop**: Ralph scans for code smells—unused exports, dead code, inconsistent patterns—and cleans them up. Software entropy in reverse.

Any task that can be described as "look at repo, improve something, report findings" fits the Ralph pattern.

---

## Real-World Success Stories

### Geoffrey Huntley: "Cursed" Programming Language
- 3 months of Ralph loops
- Created entire programming language
- Key: PRD-based scoping

### Y Combinator Hackathon
- 6 repositories overnight
- ~$297 in API costs
- Key: Well-defined tasks

### $50K Contract for $297
- Full product implementation
- PRD-based Ralph loops
- Key: Breaking work into atomic features

---

## Common Mistakes to Avoid

### 1. Vague Tasks
**Bad:** "Improve the codebase"
**Good:** "Add JSDoc to all exported functions in src/utils/"

### 2. Infinite Loops
**Bad:** Running without `--max-iterations`
**Good:** Always capping iterations, even generously

### 3. Skipping Verification
**Bad:** "Make change and commit"
**Good:** "Make change, run tests, commit only if passing"

### 4. Giant Features
**Bad:** "Build the dashboard"
**Good:** Multiple PRD features, each completable in 1-3 iterations

### 5. Ignoring Progress File
**Bad:** Assuming Ralph remembers context
**Good:** Always injecting @progress.txt and reading it first

---

## Attribution

Based on techniques from:
- [Geoffrey Huntley](https://ghuntley.com/ralph/) - Original Ralph technique
- [Ryan Carson](https://x.com/ryancarson) - PRD-based workflows
- [Matt Pocock / AI Hero](https://www.aihero.dev/tips-for-ai-coding-with-ralph-wiggum) - The 11 Tips
