# Workflow: Add Custom Tools

Step-by-step guide to add custom tools to your agent.

## Overview

Custom tools let your agent:
- Call external APIs
- Access databases
- Perform specialized computations
- Integrate with your systems

## Step 1: Define a Tool

Use the `@tool` decorator:

```python
from claude_agent_sdk import tool
from typing import Any

@tool(
    "tool_name",           # Unique identifier
    "What this tool does", # Description for Claude
    {"param": str}         # Input schema
)
async def my_tool(args: dict[str, Any]) -> dict[str, Any]:
    # Tool implementation
    result = process(args["param"])

    return {
        "content": [{
            "type": "text",
            "text": f"Result: {result}"
        }]
    }
```

## Step 2: Create Input Schema

### Simple Types (Recommended)

```python
# Basic types
{"name": str, "count": int, "enabled": bool}

# Example
@tool("greet", "Greet a user", {"name": str, "formal": bool})
async def greet(args):
    ...
```

### JSON Schema (Complex Validation)

```python
{
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "Search query"
        },
        "limit": {
            "type": "integer",
            "minimum": 1,
            "maximum": 100,
            "default": 10
        }
    },
    "required": ["query"]
}
```

## Step 3: Return Results

### Success Response

```python
return {
    "content": [{
        "type": "text",
        "text": "Your result here"
    }]
}
```

### Error Response

```python
return {
    "content": [{
        "type": "text",
        "text": "Error: Something went wrong"
    }],
    "is_error": True
}
```

### Structured Data

```python
import json

return {
    "content": [{
        "type": "text",
        "text": json.dumps({
            "status": "success",
            "data": result_data
        }, indent=2)
    }]
}
```

## Step 4: Create MCP Server

Bundle tools into an MCP server:

```python
from claude_agent_sdk import create_sdk_mcp_server

# Define tools
@tool("search", "Search database", {"query": str})
async def search(args):
    ...

@tool("update", "Update record", {"id": int, "data": dict})
async def update(args):
    ...

# Create server
my_server = create_sdk_mcp_server(
    name="my_tools",
    version="1.0.0",
    tools=[search, update]
)
```

## Step 5: Configure Agent

```python
from claude_agent_sdk import ClaudeAgentOptions

options = ClaudeAgentOptions(
    mcp_servers={"db": my_server},
    allowed_tools=[
        # Built-in tools
        "Read",
        "Write",
        # Custom tools: mcp__{server}__{tool}
        "mcp__db__search",
        "mcp__db__update"
    ]
)
```

## Complete Example

```python
import asyncio
import httpx
from typing import Any
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    tool,
    create_sdk_mcp_server,
    AssistantMessage,
    TextBlock
)

# Tool 1: Get weather
@tool(
    "get_weather",
    "Get current weather for a city",
    {"city": str, "units": str}
)
async def get_weather(args: dict[str, Any]) -> dict[str, Any]:
    city = args["city"]
    units = args.get("units", "celsius")

    # Call weather API (example)
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.weather.example.com/{city}",
            params={"units": units}
        )

        if response.status_code != 200:
            return {
                "content": [{"type": "text", "text": f"Error: {response.status_code}"}],
                "is_error": True
            }

        data = response.json()
        return {
            "content": [{
                "type": "text",
                "text": f"Weather in {city}: {data['temp']}° {data['condition']}"
            }]
        }

# Tool 2: Simple calculation
@tool("calc", "Calculate expression", {"expr": str})
async def calc(args: dict[str, Any]) -> dict[str, Any]:
    try:
        result = eval(args["expr"], {"__builtins__": {}})
        return {"content": [{"type": "text", "text": f"= {result}"}]}
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {e}"}],
            "is_error": True
        }

# Create server and configure agent
async def main():
    server = create_sdk_mcp_server(
        name="utils",
        tools=[get_weather, calc]
    )

    options = ClaudeAgentOptions(
        mcp_servers={"utils": server},
        allowed_tools=[
            "mcp__utils__get_weather",
            "mcp__utils__calc"
        ]
    )

    async with ClaudeSDKClient(options) as client:
        await client.query("What's the weather in Tokyo? Also, what's 15 * 23?")

        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

asyncio.run(main())
```

## Best Practices

1. **Descriptive names** - Help Claude understand the tool
2. **Clear descriptions** - Explain when and how to use
3. **Input validation** - Check args before processing
4. **Error handling** - Return `is_error: True` for failures
5. **Async operations** - All handlers must be async
6. **Idempotent** - Tools may be retried

## Next Steps

- Add hooks for tool monitoring: See `references/hooks.md`
- External MCP servers: See `references/custom-tools.md`
- Permission control: See `references/permissions.md`
