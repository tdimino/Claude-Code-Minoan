# Best Practices

Patterns and practices for building effective agents with the Claude Agent SDK.

## The Agent Loop

Agents work in a feedback loop:

```
gather context → take action → verify work → repeat
```

### Gather Context

- **Agentic search** - Use Glob, Grep, Read to find relevant files
- **Semantic search** - For large knowledge bases (requires external setup)
- **Subagents** - Spin up parallel searches with isolated contexts
- **Compaction** - SDK auto-summarizes when context fills

### Take Action

- **Tools** - Primary actions via built-in or custom tools
- **Bash** - Flexible work via terminal commands
- **Code generation** - Write scripts for complex operations
- **MCP** - Integrate external services

### Verify Work

- **Rules** - Linting, type checking, tests
- **Visual feedback** - Screenshots for UI work
- **LLM as judge** - Have another model review output
- **Parallel review** - Multiple subagents with different perspectives

```python
# Example: Parallel code review with specialized perspectives
options = ClaudeAgentOptions(
    agents={
        "compliance-reviewer": AgentDefinition(
            description="Review for compliance and security",
            prompt="Check for security vulnerabilities and compliance issues.",
            tools=["Read", "Glob", "Grep"],
            model="haiku"
        ),
        "bug-detector": AgentDefinition(
            description="Find bugs and edge cases",
            prompt="Analyze code for potential bugs, race conditions, edge cases.",
            tools=["Read", "Glob", "Grep"],
            model="haiku"
        ),
        "perf-analyzer": AgentDefinition(
            description="Analyze performance implications",
            prompt="Review for performance issues, memory leaks, inefficiencies.",
            tools=["Read", "Glob", "Grep"],
            model="haiku"
        )
    }
)
# Main agent spawns all three in parallel, synthesizes findings
```

---

## Architecture Patterns

### Read-Only Agent

For analysis without modification:

```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Glob", "Grep"],
    permission_mode="default",
    system_prompt="Analyze code. Do not make changes."
)
```

### File Operations Agent

For creating and editing files:

```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"],
    permission_mode="acceptEdits",
    cwd="/path/to/project"
)
```

### Research Agent

For web research:

```python
options = ClaudeAgentOptions(
    allowed_tools=["WebSearch", "WebFetch", "Write"],
    max_turns=20,  # Allow more iterations
    system_prompt="Research thoroughly. Cite sources."
)
```

### CI/CD Agent

For automated pipelines:

```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Write", "Edit", "Bash"],
    permission_mode="bypassPermissions",
    setting_sources=["project"],  # Use project settings only
    sandbox={"enabled": True}     # Run in sandbox
)
```

---

## Context Management

### Using Subagents

Subagents help manage context by:
- Running in isolated context windows
- Returning only relevant results
- Enabling parallel work

```python
options = ClaudeAgentOptions(
    agents={
        "searcher": AgentDefinition(
            description="Search for specific information",
            prompt="Find and return only relevant excerpts.",
            tools=["Read", "Glob", "Grep"],
            model="haiku"  # Fast for searches
        )
    }
)
```

### Automatic Compaction

The SDK automatically summarizes when context fills. Use `PreCompact` hooks to customize:

```python
async def pre_compact_hook(input_data, tool_use_id, context):
    print(f"Compacting {input_data['token_count']} tokens")
    return {}

options = ClaudeAgentOptions(
    hooks={"PreCompact": [HookMatcher(hooks=[pre_compact_hook])]}
)
```

---

## Tool Design

### Custom Tool Guidelines

1. **Clear names** - `get_weather`, not `gw`
2. **Descriptive** - Help Claude understand when to use
3. **Simple schemas** - Use type hints over complex JSON Schema
4. **Error handling** - Return `is_error: True` for failures
5. **Idempotent** - Tools may be retried

```python
@tool(
    "search_database",
    "Search the customer database by name or email. Returns matching records.",
    {"query": str, "limit": int}
)
async def search_database(args):
    try:
        results = await db.search(args["query"], limit=args.get("limit", 10))
        return {
            "content": [{"type": "text", "text": json.dumps(results)}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Search failed: {e}"}],
            "is_error": True
        }
```

---

## Security Best Practices

### Permission Layers

1. **Permission mode** - Base level of trust
2. **can_use_tool** - Fine-grained control
3. **Hooks** - Logging and modification
4. **Sandbox** - OS-level isolation

### Sandbox Configuration

```python
options = ClaudeAgentOptions(
    sandbox={
        "enabled": True,
        "autoAllowBashIfSandboxed": True,
        "excludedCommands": ["docker"],  # Always unsandboxed
        "network": {
            "allowLocalBinding": True
        }
    }
)
```

### Input Validation

```python
async def validate_inputs(tool_name, input_data, context):
    if tool_name == "Bash":
        command = input_data.get("command", "")

        # Block dangerous patterns
        dangerous = ["rm -rf /", "sudo", "chmod 777"]
        if any(d in command for d in dangerous):
            return {
                "behavior": "deny",
                "message": "Dangerous command blocked"
            }

    return {"behavior": "allow", "updatedInput": input_data}
```

---

## Performance

### Model Selection

- **opus** - Complex reasoning, long context
- **sonnet** - Balanced performance (default)
- **haiku** - Fast, cost-effective for simple tasks

```python
options = ClaudeAgentOptions(
    model="sonnet",  # Main agent
    agents={
        "analyzer": AgentDefinition(
            description="Quick file analysis",
            tools=["Read"],
            model="haiku"  # Faster subagent
        )
    }
)
```

### Limiting Turns

Prevent runaway agents:

```python
options = ClaudeAgentOptions(max_turns=10)
```

### Tool Selection

Only enable needed tools:

```python
# Bad: All tools enabled
options = ClaudeAgentOptions(allowed_tools=["*"])

# Good: Only what's needed
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Glob", "Grep"]
)
```

---

## Testing Agents

### Development Mode

```python
options = ClaudeAgentOptions(
    permission_mode="default",  # Manual approval
    max_turns=5,                # Limit iterations
    cwd="./test-sandbox"        # Safe directory
)
```

### Production Mode

```python
options = ClaudeAgentOptions(
    permission_mode="acceptEdits",
    sandbox={"enabled": True},
    can_use_tool=production_validator,
    hooks={"PreToolUse": [HookMatcher(hooks=[audit_logger])]}
)
```

### Evaluations

Build test sets based on real usage:
- Track failure cases
- Measure success rates
- Identify tool gaps
- Improve prompts based on failures

---

## Audit Logging

Production agents should track all tool calls for debugging and compliance.

### Hook-Based Audit Trail

```python
from datetime import datetime
from dataclasses import dataclass, asdict
import json

@dataclass
class ToolCall:
    timestamp: str
    agent_id: str
    tool_name: str
    success: bool | None = None
    error: str | None = None

class AuditTracker:
    def __init__(self, output_dir: Path):
        self.log_file = output_dir / f"audit_{datetime.now():%Y%m%d_%H%M%S}.jsonl"
        self.pending: dict[str, ToolCall] = {}
        self.subagents: dict[str, str] = {}  # tool_use_id -> agent_name

    def _log(self, event: str, data: dict):
        with open(self.log_file, "a") as f:
            f.write(json.dumps({"event": event, **data}) + "\n")

    async def pre_tool_use_hook(self, input_data, tool_use_id, context):
        tool_name = input_data.get("tool_name", "unknown")
        parent_id = input_data.get("parent_tool_use_id")

        # Track which agent made this call
        agent_id = self.subagents.get(parent_id, "MAIN")

        # Track Task spawns
        if tool_name == "Task" and tool_use_id:
            desc = input_data.get("tool_input", {}).get("description", "SUBAGENT")
            self.subagents[tool_use_id] = desc.upper()

        self.pending[tool_use_id] = ToolCall(
            timestamp=datetime.now().isoformat(),
            agent_id=agent_id,
            tool_name=tool_name
        )
        self._log("tool_start", {"agent": agent_id, "tool": tool_name})
        return {}

    async def post_tool_use_hook(self, input_data, tool_use_id, context):
        if tool_use_id in self.pending:
            call = self.pending.pop(tool_use_id)
            call.success = not input_data.get("is_error", False)
            if call.success is False:
                call.error = str(input_data.get("output", ""))[:500]
            self._log("tool_complete", asdict(call))
        return {}

# Usage
tracker = AuditTracker(Path("./logs"))
options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [HookMatcher(hooks=[tracker.pre_tool_use_hook])],
        "PostToolUse": [HookMatcher(hooks=[tracker.post_tool_use_hook])]
    }
)
```

### Subagent Lifecycle Tracking

Track when subagents spawn and complete:

```python
async def subagent_start_hook(self, input_data, tool_use_id, context):
    agent_type = input_data.get("agent_type", "unknown")
    self._log("subagent_start", {
        "agent_type": agent_type,
        "tool_use_id": tool_use_id
    })
    return {}

async def subagent_stop_hook(self, input_data, tool_use_id, context):
    transcript_path = input_data.get("agent_transcript_path")
    self._log("subagent_stop", {
        "tool_use_id": tool_use_id,
        "transcript": transcript_path
    })
    return {}

hooks = {
    "SubagentStart": [HookMatcher(hooks=[subagent_start_hook])],
    "SubagentStop": [HookMatcher(hooks=[subagent_stop_hook])]
}
```

---

## Template Reference

See `templates/` for working examples:

| Template | Description |
|----------|-------------|
| `simple-agent-python.py` | Minimal agent setup |
| `continuous-chat-python.py` | Multi-turn conversations |
| `custom-tool-python.py` | Custom tool with @tool decorator |
| `hook-example-python.py` | Hook implementation |
| `research-agent-python.py` | Multi-agent research system |
| `agent-with-tracking-python.py` | Production tracking |
| `session-api-typescript.ts` | V2 Session API (TypeScript) |
