# Custom Tools Reference

Create custom tools for your agents using the `@tool` decorator or MCP servers.

## The @tool Decorator

Define tools with type-safe schemas:

```python
from claude_agent_sdk import tool
from typing import Any

@tool("tool_name", "Description of what the tool does", {"param": str})
async def my_tool(args: dict[str, Any]) -> dict[str, Any]:
    return {
        "content": [{
            "type": "text",
            "text": f"Result: {args['param']}"
        }]
    }
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Unique tool identifier |
| `description` | `str` | What the tool does |
| `input_schema` | `type \| dict` | Parameter schema |

### Input Schema Options

**1. Simple type mapping (recommended):**

```python
{"name": str, "count": int, "enabled": bool}
```

**2. JSON Schema (for complex validation):**

```python
{
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "count": {"type": "integer", "minimum": 0}
    },
    "required": ["name"]
}
```

### Return Format

Tools must return a dictionary with `content` array:

```python
{
    "content": [
        {"type": "text", "text": "Result message"}
    ]
}
```

For errors:

```python
{
    "content": [{"type": "text", "text": "Error: Invalid input"}],
    "is_error": True
}
```

---

## Creating MCP Servers

Use `create_sdk_mcp_server()` to bundle tools into an in-process MCP server:

```python
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions

@tool("add", "Add two numbers", {"a": float, "b": float})
async def add(args):
    return {
        "content": [{
            "type": "text",
            "text": f"Sum: {args['a'] + args['b']}"
        }]
    }

@tool("multiply", "Multiply two numbers", {"a": float, "b": float})
async def multiply(args):
    return {
        "content": [{
            "type": "text",
            "text": f"Product: {args['a'] * args['b']}"
        }]
    }

# Create the MCP server
calculator = create_sdk_mcp_server(
    name="calculator",
    version="1.0.0",
    tools=[add, multiply]
)

# Use with Claude
options = ClaudeAgentOptions(
    mcp_servers={"calc": calculator},
    allowed_tools=["mcp__calc__add", "mcp__calc__multiply"]
)
```

### Tool Naming Convention

MCP tools follow the pattern: `mcp__{server_name}__{tool_name}`

```python
# Server name: "calc"
# Tool name: "add"
# Full tool name: "mcp__calc__add"
```

---

## MCP Server Configurations

### Stdio Server (External Process)

```python
from claude_agent_sdk import ClaudeAgentOptions

options = ClaudeAgentOptions(
    mcp_servers={
        "myserver": {
            "type": "stdio",  # Optional, default
            "command": "python",
            "args": ["-m", "my_mcp_server"],
            "env": {"API_KEY": "xxx"}
        }
    }
)
```

### SSE Server (Server-Sent Events)

```python
options = ClaudeAgentOptions(
    mcp_servers={
        "remote": {
            "type": "sse",
            "url": "https://mcp.example.com/sse",
            "headers": {"Authorization": "Bearer xxx"}
        }
    }
)
```

### HTTP Server (REST)

```python
options = ClaudeAgentOptions(
    mcp_servers={
        "api": {
            "type": "http",
            "url": "https://mcp.example.com/api",
            "headers": {"Authorization": "Bearer xxx"}
        }
    }
)
```

### SDK Server (In-Process)

```python
my_server = create_sdk_mcp_server("name", tools=[...])

options = ClaudeAgentOptions(
    mcp_servers={"name": my_server}
)
```

---

## Complete Example: Weather Tool

```python
import asyncio
import httpx
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    tool,
    create_sdk_mcp_server,
    AssistantMessage,
    TextBlock
)
from typing import Any

@tool(
    "get_weather",
    "Get current weather for a city",
    {
        "city": str,
        "units": str  # "celsius" or "fahrenheit"
    }
)
async def get_weather(args: dict[str, Any]) -> dict[str, Any]:
    city = args["city"]
    units = args.get("units", "celsius")

    # Example API call (replace with real weather API)
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.weather.example.com/{city}",
            params={"units": units}
        )

        if response.status_code != 200:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error: Could not get weather for {city}"
                }],
                "is_error": True
            }

        data = response.json()
        return {
            "content": [{
                "type": "text",
                "text": f"Weather in {city}: {data['temp']}° {data['condition']}"
            }]
        }

@tool("get_forecast", "Get 5-day forecast", {"city": str})
async def get_forecast(args: dict[str, Any]) -> dict[str, Any]:
    # Implementation here
    return {
        "content": [{
            "type": "text",
            "text": f"5-day forecast for {args['city']}: ..."
        }]
    }

async def main():
    weather_server = create_sdk_mcp_server(
        name="weather",
        version="1.0.0",
        tools=[get_weather, get_forecast]
    )

    options = ClaudeAgentOptions(
        mcp_servers={"weather": weather_server},
        allowed_tools=[
            "mcp__weather__get_weather",
            "mcp__weather__get_forecast"
        ]
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("What's the weather in Tokyo?")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

asyncio.run(main())
```

---

## Best Practices

1. **Clear descriptions** - Help Claude understand when to use the tool
2. **Input validation** - Use JSON Schema for complex validation
3. **Error handling** - Return `is_error: True` for failures
4. **Async functions** - All tool handlers must be async
5. **Idempotent operations** - Tools may be retried
6. **Minimal side effects** - Keep tools focused and predictable
