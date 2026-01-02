# Built-in Tools Reference

The Claude Agent SDK includes powerful built-in tools that give agents full computer access.

## File Tools

### Read

Read files from the filesystem. Supports text, images, PDFs, and Jupyter notebooks.

**Tool name:** `Read`

**Input:**
```python
{
    "file_path": str,       # Absolute path to read
    "offset": int | None,   # Line to start from
    "limit": int | None     # Number of lines
}
```

**Output (text):**
```python
{
    "content": str,         # File contents with line numbers
    "total_lines": int,
    "lines_returned": int
}
```

**Output (images):**
```python
{
    "image": str,       # Base64 encoded
    "mime_type": str,
    "file_size": int
}
```

### Write

Create new files.

**Tool name:** `Write`

**Input:**
```python
{
    "file_path": str,  # Absolute path
    "content": str     # Content to write
}
```

**Output:**
```python
{
    "message": str,
    "bytes_written": int,
    "file_path": str
}
```

### Edit

Make precise edits using search/replace.

**Tool name:** `Edit`

**Input:**
```python
{
    "file_path": str,           # Absolute path
    "old_string": str,          # Text to find
    "new_string": str,          # Replacement text
    "replace_all": bool | None  # Replace all occurrences
}
```

**Output:**
```python
{
    "message": str,
    "replacements": int,
    "file_path": str
}
```

---

## Search Tools

### Glob

Find files by pattern.

**Tool name:** `Glob`

**Input:**
```python
{
    "pattern": str,       # Glob pattern (e.g., "**/*.ts")
    "path": str | None    # Search directory
}
```

**Output:**
```python
{
    "matches": list[str],
    "count": int,
    "search_path": str
}
```

### Grep

Search file contents with regex.

**Tool name:** `Grep`

**Input:**
```python
{
    "pattern": str,                    # Regex pattern
    "path": str | None,                # Search path
    "glob": str | None,                # Filter files by glob
    "type": str | None,                # File type (e.g., "py")
    "output_mode": str | None,         # "content", "files_with_matches", "count"
    "-i": bool | None,                 # Case insensitive
    "-n": bool | None,                 # Show line numbers
    "-B": int | None,                  # Lines before match
    "-A": int | None,                  # Lines after match
    "-C": int | None,                  # Lines around match
    "head_limit": int | None,          # Limit results
    "multiline": bool | None           # Multiline mode
}
```

**Output (content mode):**
```python
{
    "matches": [
        {
            "file": str,
            "line_number": int | None,
            "line": str,
            "before_context": list[str] | None,
            "after_context": list[str] | None
        }
    ],
    "total_matches": int
}
```

---

## Shell Tools

### Bash

Run terminal commands.

**Tool name:** `Bash`

**Input:**
```python
{
    "command": str,                  # Command to execute
    "timeout": int | None,           # Timeout in ms (max 600000)
    "description": str | None,       # Description (5-10 words)
    "run_in_background": bool | None # Run in background
}
```

**Output:**
```python
{
    "output": str,          # stdout and stderr
    "exitCode": int,
    "killed": bool | None,  # If killed by timeout
    "shellId": str | None   # For background processes
}
```

### KillShell

Kill background shell processes.

**Tool name:** `KillShell`

**Input:**
```python
{
    "shell_id": str  # ID of shell to kill
}
```

**Output:**
```python
{
    "message": str,
    "shell_id": str
}
```

### BashOutput

Get output from background shell.

**Tool name:** `BashOutput`

**Input:**
```python
{
    "bash_id": str,       # Background shell ID
    "filter": str | None  # Regex to filter output
}
```

**Output:**
```python
{
    "output": str,
    "status": "running" | "completed" | "failed",
    "exitCode": int | None
}
```

---

## Web Tools

### WebSearch

Search the web.

**Tool name:** `WebSearch`

**Input:**
```python
{
    "query": str,
    "allowed_domains": list[str] | None,
    "blocked_domains": list[str] | None
}
```

**Output:**
```python
{
    "results": [
        {
            "title": str,
            "url": str,
            "snippet": str,
            "metadata": dict | None
        }
    ],
    "total_results": int,
    "query": str
}
```

### WebFetch

Fetch and parse web pages.

**Tool name:** `WebFetch`

**Input:**
```python
{
    "url": str,     # URL to fetch
    "prompt": str   # Prompt for processing content
}
```

**Output:**
```python
{
    "response": str,           # AI response to prompt
    "url": str,
    "final_url": str | None,   # After redirects
    "status_code": int | None
}
```

---

## Subagent Tools

### Task

Spawn subagents for specialized work.

**Tool name:** `Task`

**Input:**
```python
{
    "description": str,      # 3-5 word description
    "prompt": str,           # Task for agent
    "subagent_type": str     # Agent type to use
}
```

**Output:**
```python
{
    "result": str,
    "usage": dict | None,
    "total_cost_usd": float | None,
    "duration_ms": int | None
}
```

---

## Notebook Tools

### NotebookEdit

Edit Jupyter notebooks.

**Tool name:** `NotebookEdit`

**Input:**
```python
{
    "notebook_path": str,
    "cell_id": str | None,
    "new_source": str,
    "cell_type": "code" | "markdown" | None,
    "edit_mode": "replace" | "insert" | "delete" | None
}
```

**Output:**
```python
{
    "message": str,
    "edit_type": "replaced" | "inserted" | "deleted",
    "cell_id": str | None,
    "total_cells": int
}
```

---

## Task Management Tools

### TodoWrite

Manage task lists.

**Tool name:** `TodoWrite`

**Input:**
```python
{
    "todos": [
        {
            "content": str,
            "status": "pending" | "in_progress" | "completed",
            "activeForm": str
        }
    ]
}
```

**Output:**
```python
{
    "message": str,
    "stats": {
        "total": int,
        "pending": int,
        "in_progress": int,
        "completed": int
    }
}
```

---

## Planning Tools

### ExitPlanMode

Exit planning mode with a plan.

**Tool name:** `ExitPlanMode`

**Input:**
```python
{
    "plan": str  # Plan for user approval
}
```

**Output:**
```python
{
    "message": str,
    "approved": bool | None
}
```

---

## MCP Resource Tools

### ListMcpResources

List available MCP resources.

**Tool name:** `ListMcpResources`

**Input:**
```python
{
    "server": str | None  # Filter by server
}
```

**Output:**
```python
{
    "resources": [
        {
            "uri": str,
            "name": str,
            "description": str | None,
            "mimeType": str | None,
            "server": str
        }
    ],
    "total": int
}
```

### ReadMcpResource

Read an MCP resource.

**Tool name:** `ReadMcpResource`

**Input:**
```python
{
    "server": str,  # MCP server name
    "uri": str      # Resource URI
}
```

**Output:**
```python
{
    "contents": [
        {
            "uri": str,
            "mimeType": str | None,
            "text": str | None,
            "blob": str | None
        }
    ],
    "server": str
}
```
