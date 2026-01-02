# Troubleshooting Guide

Common errors and solutions for the Claude Agent SDK.

## Error Types

### CLINotFoundError

**Error:** Claude Code CLI is not installed or not in PATH.

```python
CLINotFoundError: Claude Code not found
```

**Solutions:**

1. Install Claude Code CLI:
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

2. Verify installation:
   ```bash
   claude --version
   ```

3. Check PATH includes npm global bin:
   ```bash
   npm config get prefix
   # Add {prefix}/bin to PATH
   ```

---

### CLIConnectionError

**Error:** Failed to connect to Claude Code.

```python
CLIConnectionError: Failed to connect to Claude Code
```

**Solutions:**

1. Check API key is set:
   ```bash
   echo $ANTHROPIC_API_KEY
   ```

2. Verify API key is valid at console.anthropic.com

3. Check network connectivity

4. For Bedrock/Vertex:
   ```bash
   export CLAUDE_CODE_USE_BEDROCK=1
   # or
   export CLAUDE_CODE_USE_VERTEX=1
   ```

---

### ProcessError

**Error:** Claude Code process failed.

```python
ProcessError: Process failed with exit code 1
```

**Solutions:**

1. Check stderr output:
   ```python
   options = ClaudeAgentOptions(
       stderr=lambda msg: print(f"STDERR: {msg}")
   )
   ```

2. Run with debug output:
   ```python
   try:
       async for msg in query(prompt="test", options=options):
           print(msg)
   except ProcessError as e:
       print(f"Exit code: {e.exit_code}")
       print(f"Stderr: {e.stderr}")
   ```

3. Check working directory exists and is accessible

---

### CLIJSONDecodeError

**Error:** Failed to parse JSON response.

```python
CLIJSONDecodeError: Failed to parse line: ...
```

**Solutions:**

1. Check for corrupted response (network issues)

2. Update Claude Code CLI:
   ```bash
   npm update -g @anthropic-ai/claude-code
   ```

3. Check for version mismatch between SDK and CLI

---

## Common Issues

### Tool Not Found

**Problem:** Tool calls fail with "tool not found"

**Solutions:**

1. Check tool is in `allowed_tools`:
   ```python
   options = ClaudeAgentOptions(
       allowed_tools=["Read", "Write", "Bash"]  # Explicit list
   )
   ```

2. For MCP tools, use full name:
   ```python
   allowed_tools=["mcp__server__tool"]
   ```

3. Check tool isn't in `disallowed_tools`

---

### Permission Denied

**Problem:** Tools blocked by permissions

**Solutions:**

1. Use appropriate permission mode:
   ```python
   options = ClaudeAgentOptions(
       permission_mode="acceptEdits"  # For file operations
   )
   ```

2. Check `can_use_tool` handler:
   ```python
   async def debug_permissions(tool, input, ctx):
       print(f"Permission check: {tool} -> {input}")
       return {"behavior": "allow", "updatedInput": input}

   options = ClaudeAgentOptions(can_use_tool=debug_permissions)
   ```

3. For sandbox issues:
   ```python
   options = ClaudeAgentOptions(
       sandbox={
           "enabled": True,
           "allowUnsandboxedCommands": True
       }
   )
   ```

---

### Session Not Found

**Problem:** Resume fails with invalid session ID

**Solutions:**

1. Check session ID is correct:
   ```python
   async for msg in query(prompt="test"):
       if hasattr(msg, "session_id"):
           print(f"Session: {msg.session_id}")
   ```

2. Sessions expire - create new session if stale

3. Use `fork_session=True` to fork instead of continue:
   ```python
   options = ClaudeAgentOptions(
       resume="old-session-id",
       fork_session=True
   )
   ```

---

### Timeout Issues

**Problem:** Operations timing out

**Solutions:**

1. Increase hook timeout:
   ```python
   HookMatcher(hooks=[my_hook], timeout=120)
   ```

2. Increase bash timeout:
   ```python
   # In tool input
   {"command": "long-running-cmd", "timeout": 300000}
   ```

3. Use background execution:
   ```python
   {"command": "long-cmd", "run_in_background": True}
   ```

---

### Context Overflow

**Problem:** Context window exceeded

**Solutions:**

1. Use subagents for large tasks:
   ```python
   agents={
       "processor": AgentDefinition(
           description="Process large files",
           tools=["Read"],
           model="sonnet"
       )
   }
   ```

2. Limit response size:
   ```python
   options = ClaudeAgentOptions(max_turns=10)
   ```

3. Monitor compaction:
   ```python
   async def compact_logger(input_data, tool_use_id, ctx):
       print(f"Compacting: {input_data['token_count']} tokens")
       return {}

   hooks={"PreCompact": [HookMatcher(hooks=[compact_logger])]}
   ```

---

### Asyncio Cleanup Issues

**Problem:** RuntimeWarning about coroutines

**Solutions:**

1. Don't use `break` in message loops:
   ```python
   # Bad
   async for msg in client.receive_response():
       if found_what_i_need:
           break  # Can cause issues

   # Good
   result = None
   async for msg in client.receive_response():
       if found_what_i_need:
           result = msg
       # Let loop complete naturally
   ```

2. Use context manager:
   ```python
   async with ClaudeSDKClient() as client:
       # Auto-cleanup on exit
   ```

---

## Debugging Tips

### Enable Verbose Output

```python
options = ClaudeAgentOptions(
    stderr=lambda msg: print(f"[DEBUG] {msg}")
)
```

### Log All Messages

```python
async for message in query(prompt="test", options=options):
    print(f"Type: {type(message).__name__}")
    print(f"Content: {message}")
    print("---")
```

### Inspect Tool Calls

```python
async def debug_hook(input_data, tool_use_id, ctx):
    print(f"Tool: {input_data.get('tool_name')}")
    print(f"Input: {input_data.get('tool_input')}")
    return {}

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [HookMatcher(hooks=[debug_hook])],
        "PostToolUse": [HookMatcher(hooks=[debug_hook])]
    }
)
```

### Check Environment

```python
import os
import shutil

print(f"API Key set: {bool(os.environ.get('ANTHROPIC_API_KEY'))}")
print(f"Claude CLI: {shutil.which('claude')}")
print(f"Python: {sys.version}")
```
