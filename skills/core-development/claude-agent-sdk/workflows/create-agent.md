# Workflow: Create a New Agent

Step-by-step guide to create an agent from scratch.

## Step 1: Set Up Project

```bash
# Create project directory
mkdir my-agent && cd my-agent

# Initialize Python project with uv
uv init
uv add claude-agent-sdk

# Set API key
export ANTHROPIC_API_KEY=your-key-here
```

## Step 2: Create Agent File

Create `agent.py`:

```python
import asyncio
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ResultMessage
)

async def run_agent(task: str):
    options = ClaudeAgentOptions(
        # 1. Choose tools your agent needs
        allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"],

        # 2. Set permission level
        permission_mode="acceptEdits",  # Auto-approve file changes

        # 3. Set working directory
        cwd=".",

        # 4. (Optional) Custom system prompt
        system_prompt="You are a helpful assistant."
    )

    async for message in query(prompt=task, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)

        elif isinstance(message, ResultMessage):
            print(f"\nCompleted in {message.duration_ms}ms")
            if message.total_cost_usd:
                print(f"Cost: ${message.total_cost_usd:.4f}")

if __name__ == "__main__":
    task = "Analyze the code in this directory and create a README.md"
    asyncio.run(run_agent(task))
```

## Step 3: Choose Your Agent Type

### One-Shot Agent (query)

For independent tasks:

```python
from claude_agent_sdk import query

async for message in query(prompt="Fix bugs in main.py"):
    process(message)
```

### Conversational Agent (ClaudeSDKClient)

For multi-turn interactions:

```python
from claude_agent_sdk import ClaudeSDKClient

async with ClaudeSDKClient(options) as client:
    await client.query("What files are here?")
    async for msg in client.receive_response():
        process(msg)

    await client.query("Show me the largest file")
    async for msg in client.receive_response():
        process(msg)
```

## Step 4: Configure Tools

Match tools to your agent's purpose:

| Purpose | Tools |
|---------|-------|
| Code analysis | `Read`, `Glob`, `Grep` |
| File editing | `Read`, `Write`, `Edit` |
| Build/test | `Bash`, `Read`, `Write` |
| Research | `WebSearch`, `WebFetch` |
| Full coding | All of the above |

```python
# Read-only analysis agent
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Glob", "Grep"]
)

# Full development agent
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"]
)
```

## Step 5: Set Permissions

Choose appropriate permission level:

```python
# Interactive - prompts for each action
permission_mode="default"

# Auto-approve file changes
permission_mode="acceptEdits"

# Planning only - no execution
permission_mode="plan"

# Full automation (use with caution)
permission_mode="bypassPermissions"
```

## Step 6: Run Your Agent

```bash
# Run directly
uv run python agent.py

# Or with task argument
uv run python agent.py "Create unit tests for utils.py"
```

## Step 7: Add Error Handling

```python
from claude_agent_sdk import (
    CLINotFoundError,
    ProcessError,
    CLIConnectionError
)

async def run_agent(task: str):
    try:
        async for message in query(prompt=task, options=options):
            process(message)

    except CLINotFoundError:
        print("Error: Claude Code CLI not installed")
        print("Run: npm install -g @anthropic-ai/claude-code")

    except CLIConnectionError:
        print("Error: Could not connect to Claude")
        print("Check your ANTHROPIC_API_KEY")

    except ProcessError as e:
        print(f"Error: Process failed with code {e.exit_code}")
        print(e.stderr)
```

## Next Steps

- Add custom tools: See `references/custom-tools.md`
- Add hooks: See `references/hooks.md`
- Add subagents: See `references/subagents.md`
- Review templates: See `templates/` directory
