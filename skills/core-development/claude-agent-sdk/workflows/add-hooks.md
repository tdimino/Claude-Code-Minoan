# Workflow: Add Hooks

Step-by-step guide to add hooks for behavior modification.

## Overview

Hooks let you:
- Log all tool usage
- Block dangerous operations
- Modify tool inputs
- Add context to prompts
- Implement custom permissions

## Step 1: Choose Hook Events

| Event | When It Fires |
|-------|---------------|
| `PreToolUse` | Before tool execution |
| `PostToolUse` | After tool execution |
| `UserPromptSubmit` | When user sends prompt |
| `Stop` | When agent stops |
| `SubagentStop` | When subagent stops |
| `PreCompact` | Before context compaction |

## Step 2: Create Hook Callback

```python
from claude_agent_sdk import HookContext
from typing import Any

async def my_hook(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    # Process the event
    print(f"Event data: {input_data}")

    # Return empty dict if no modification needed
    return {}
```

## Step 3: Configure Hook Matcher

```python
from claude_agent_sdk import HookMatcher

# Apply to all tools
HookMatcher(hooks=[my_hook])

# Apply to specific tool
HookMatcher(matcher="Bash", hooks=[my_hook])

# Apply to multiple tools
HookMatcher(matcher="Write|Edit", hooks=[my_hook])

# With custom timeout
HookMatcher(hooks=[my_hook], timeout=120)
```

## Step 4: Add to Options

```python
from claude_agent_sdk import ClaudeAgentOptions

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Bash", hooks=[validate_bash]),
            HookMatcher(hooks=[log_all_tools])
        ],
        "PostToolUse": [
            HookMatcher(hooks=[log_results])
        ],
        "UserPromptSubmit": [
            HookMatcher(hooks=[add_context])
        ]
    }
)
```

## Common Hook Patterns

### Pattern 1: Audit Logging

```python
from datetime import datetime

async def audit_log(input_data, tool_use_id, context):
    timestamp = datetime.now().isoformat()
    tool = input_data.get("tool_name", "unknown")
    print(f"[{timestamp}] Tool: {tool}")
    return {}

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [HookMatcher(hooks=[audit_log])],
        "PostToolUse": [HookMatcher(hooks=[audit_log])]
    }
)
```

### Pattern 2: Security Validation

```python
BLOCKED_COMMANDS = ["rm -rf", "sudo", "chmod 777"]

async def validate_bash(input_data, tool_use_id, context):
    if input_data.get("tool_name") != "Bash":
        return {}

    command = input_data.get("tool_input", {}).get("command", "")

    for blocked in BLOCKED_COMMANDS:
        if blocked in command:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"Blocked: {blocked}"
                }
            }

    return {}

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Bash", hooks=[validate_bash])
        ]
    }
)
```

### Pattern 3: Input Modification

```python
async def sandbox_files(input_data, tool_use_id, context):
    tool = input_data.get("tool_name")

    if tool in ["Write", "Edit"]:
        original_path = input_data["tool_input"].get("file_path", "")

        # Redirect to sandbox
        if not original_path.startswith("./sandbox/"):
            safe_path = f"./sandbox/{original_path.lstrip('/')}"
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "allow",
                    "updatedInput": {
                        **input_data["tool_input"],
                        "file_path": safe_path
                    }
                }
            }

    return {}

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Write|Edit", hooks=[sandbox_files])
        ]
    }
)
```

### Pattern 4: Prompt Enhancement

```python
from datetime import datetime

async def add_timestamp(input_data, tool_use_id, context):
    original = input_data.get("prompt", "")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "updatedPrompt": f"[{timestamp}] {original}"
        }
    }

options = ClaudeAgentOptions(
    hooks={
        "UserPromptSubmit": [HookMatcher(hooks=[add_timestamp])]
    }
)
```

### Pattern 5: Rate Limiting

```python
from datetime import datetime, timedelta
from collections import defaultdict

call_times = defaultdict(list)

async def rate_limit(input_data, tool_use_id, context):
    tool = input_data.get("tool_name")
    now = datetime.now()

    # Clean old entries
    cutoff = now - timedelta(minutes=1)
    call_times[tool] = [t for t in call_times[tool] if t > cutoff]

    # Check limit (10 per minute)
    if len(call_times[tool]) >= 10:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "Rate limit exceeded"
            }
        }

    call_times[tool].append(now)
    return {}

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [HookMatcher(hooks=[rate_limit])]
    }
)
```

## Complete Example

```python
import asyncio
from datetime import datetime
from typing import Any
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    HookMatcher,
    HookContext,
    AssistantMessage,
    TextBlock
)

# Logging hook
async def log_tool(input_data, tool_use_id, context):
    tool = input_data.get("tool_name", "?")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {tool}")
    return {}

# Security hook
async def block_dangerous(input_data, tool_use_id, context):
    if input_data.get("tool_name") == "Bash":
        cmd = input_data.get("tool_input", {}).get("command", "")
        if "rm -rf" in cmd:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": "Dangerous command blocked"
                }
            }
    return {}

async def main():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Bash", "Glob"],
        hooks={
            "PreToolUse": [
                HookMatcher(matcher="Bash", hooks=[block_dangerous]),
                HookMatcher(hooks=[log_tool])
            ],
            "PostToolUse": [
                HookMatcher(hooks=[log_tool])
            ]
        }
    )

    async for msg in query(
        prompt="List Python files and show me what's in them",
        options=options
    ):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(block.text)

asyncio.run(main())
```

## Best Practices

1. **Keep hooks fast** - They block execution
2. **Set timeouts** - Prevent hanging hooks
3. **Use matchers** - Only run on relevant tools
4. **Return empty dict** - When no modification needed
5. **Handle errors** - Don't crash the agent
6. **Log decisions** - For debugging

## Next Steps

- Add custom tools: See `workflows/add-custom-tools.md`
- Permission control: See `references/permissions.md`
- Hook reference: See `references/hooks.md`
