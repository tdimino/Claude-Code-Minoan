# Hooks Reference

Hooks let you intercept and modify agent behavior at key points in the execution loop.

## Supported Hook Events

```python
HookEvent = Literal[
    "PreToolUse",       # Before tool execution
    "PostToolUse",      # After tool execution
    "UserPromptSubmit", # When user submits prompt
    "Stop",             # When execution stops
    "SubagentStop",     # When subagent stops
    "PreCompact"        # Before message compaction
]
```

> **Note:** Python SDK does not support `SessionStart`, `SessionEnd`, and `Notification` hooks.

---

## Hook Callback Signature

```python
async def my_hook(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    # Process the event
    return {}  # Return hook response
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `input_data` | `dict` | Hook-specific input data |
| `tool_use_id` | `str \| None` | Tool use ID (for tool hooks) |
| `context` | `HookContext` | Additional context |

### Return Values

| Key | Type | Description |
|-----|------|-------------|
| `decision` | `"block"` | Block the action |
| `systemMessage` | `str` | Add message to transcript |
| `hookSpecificOutput` | `dict` | Hook-specific output |

---

## HookMatcher

Configure which hooks apply to which events:

```python
@dataclass
class HookMatcher:
    matcher: str | None = None      # Tool pattern (e.g., "Bash", "Write|Edit")
    hooks: list[HookCallback] = []  # Callbacks to execute
    timeout: float | None = None    # Timeout in seconds (default: 60)
```

---

## Hook Examples

### Validate Bash Commands

Block dangerous commands before execution:

```python
from claude_agent_sdk import query, ClaudeAgentOptions, HookMatcher, HookContext
from typing import Any

async def validate_bash(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    if input_data['tool_name'] == 'Bash':
        command = input_data['tool_input'].get('command', '')

        # Block dangerous commands
        if 'rm -rf /' in command or 'sudo rm' in command:
            return {
                'hookSpecificOutput': {
                    'hookEventName': 'PreToolUse',
                    'permissionDecision': 'deny',
                    'permissionDecisionReason': 'Dangerous command blocked'
                }
            }

    return {}

options = ClaudeAgentOptions(
    hooks={
        'PreToolUse': [
            HookMatcher(matcher='Bash', hooks=[validate_bash], timeout=120)
        ]
    },
    allowed_tools=["Bash"]
)
```

### Log All Tool Usage

Audit trail for tool usage:

```python
async def log_tool(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    tool_name = input_data.get('tool_name', 'unknown')
    tool_input = input_data.get('tool_input', {})

    print(f"[TOOL] {tool_name}: {tool_input}")
    return {}

options = ClaudeAgentOptions(
    hooks={
        'PreToolUse': [HookMatcher(hooks=[log_tool])],
        'PostToolUse': [HookMatcher(hooks=[log_tool])]
    }
)
```

### Modify User Prompts

Add context to all prompts:

```python
from datetime import datetime

async def add_timestamp(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    original = input_data.get('prompt', '')

    return {
        'hookSpecificOutput': {
            'hookEventName': 'UserPromptSubmit',
            'updatedPrompt': f"[{timestamp}] {original}"
        }
    }

options = ClaudeAgentOptions(
    hooks={
        'UserPromptSubmit': [HookMatcher(hooks=[add_timestamp])]
    }
)
```

### Redirect File Operations

Sandbox file writes to a safe directory:

```python
async def sandbox_writes(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    tool_name = input_data.get('tool_name')

    if tool_name in ['Write', 'Edit']:
        file_path = input_data['tool_input'].get('file_path', '')

        # Block system directories
        if file_path.startswith('/system/') or file_path.startswith('/etc/'):
            return {
                'hookSpecificOutput': {
                    'hookEventName': 'PreToolUse',
                    'permissionDecision': 'deny',
                    'permissionDecisionReason': 'System directory write blocked'
                }
            }

        # Redirect to sandbox
        if not file_path.startswith('./sandbox/'):
            new_path = f"./sandbox/{file_path.lstrip('/')}"
            return {
                'hookSpecificOutput': {
                    'hookEventName': 'PreToolUse',
                    'permissionDecision': 'allow',
                    'updatedInput': {
                        **input_data['tool_input'],
                        'file_path': new_path
                    }
                }
            }

    return {}

options = ClaudeAgentOptions(
    hooks={
        'PreToolUse': [
            HookMatcher(matcher='Write|Edit', hooks=[sandbox_writes])
        ]
    }
)
```

---

## Multiple Hooks

Chain multiple hooks for the same event:

```python
options = ClaudeAgentOptions(
    hooks={
        'PreToolUse': [
            # Security validation (Bash only)
            HookMatcher(matcher='Bash', hooks=[validate_bash], timeout=120),

            # Audit logging (all tools)
            HookMatcher(hooks=[log_tool]),

            # File sandboxing (Write/Edit only)
            HookMatcher(matcher='Write|Edit', hooks=[sandbox_writes])
        ],
        'PostToolUse': [
            HookMatcher(hooks=[log_tool])
        ]
    }
)
```

---

## Hook Input Data by Event

### PreToolUse / PostToolUse

```python
{
    'tool_name': str,
    'tool_input': dict,
    'tool_use_id': str
}
```

### UserPromptSubmit

```python
{
    'prompt': str
}
```

### Stop / SubagentStop

```python
{
    'reason': str,
    'result': Any
}
```

### PreCompact

```python
{
    'messages': list[Message],
    'token_count': int
}
```

---

## Best Practices

1. **Keep hooks fast** - They block execution
2. **Set appropriate timeouts** - Default is 60s
3. **Use matchers** - Only run hooks on relevant tools
4. **Return empty dict** - If no modification needed
5. **Handle errors** - Don't let hooks crash the agent
6. **Log decisions** - For debugging and audit trails
