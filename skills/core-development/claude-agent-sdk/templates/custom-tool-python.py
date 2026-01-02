"""
Custom Tool Template (Python)

Demonstrates creating custom tools with the @tool decorator.
"""

import asyncio
from datetime import datetime
from typing import Any
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    tool,
    create_sdk_mcp_server,
    AssistantMessage,
    TextBlock
)


# Define custom tools using the @tool decorator
@tool(
    "get_current_time",
    "Get the current date and time",
    {}  # No parameters needed
)
async def get_current_time(args: dict[str, Any]) -> dict[str, Any]:
    """Returns the current date and time."""
    now = datetime.now()
    return {
        "content": [{
            "type": "text",
            "text": f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"
        }]
    }


@tool(
    "calculate",
    "Perform a mathematical calculation",
    {"expression": str}  # Simple type mapping
)
async def calculate(args: dict[str, Any]) -> dict[str, Any]:
    """Safely evaluate a math expression."""
    try:
        # Safe eval with limited builtins
        allowed = {"__builtins__": {}}
        result = eval(args["expression"], allowed)
        return {
            "content": [{
                "type": "text",
                "text": f"Result: {result}"
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error: {str(e)}"
            }],
            "is_error": True
        }


@tool(
    "lookup_data",
    "Look up data by key from a simulated database",
    {
        "type": "object",
        "properties": {
            "key": {"type": "string", "description": "The key to look up"},
            "default": {"type": "string", "description": "Default value if not found"}
        },
        "required": ["key"]
    }
)
async def lookup_data(args: dict[str, Any]) -> dict[str, Any]:
    """Simulated database lookup."""
    # Simulated data store
    data = {
        "company": "Acme Corp",
        "product": "Widget Pro",
        "version": "2.0.1"
    }

    key = args["key"]
    default = args.get("default", "Not found")
    value = data.get(key, default)

    return {
        "content": [{
            "type": "text",
            "text": f"{key}: {value}"
        }]
    }


async def main():
    # Create an MCP server with our custom tools
    my_tools_server = create_sdk_mcp_server(
        name="my_tools",
        version="1.0.0",
        tools=[get_current_time, calculate, lookup_data]
    )

    # Configure agent with the custom tools
    options = ClaudeAgentOptions(
        mcp_servers={"tools": my_tools_server},
        allowed_tools=[
            # Built-in tools
            "Read",
            "Write",
            # Custom tools (format: mcp__{server}__{tool})
            "mcp__tools__get_current_time",
            "mcp__tools__calculate",
            "mcp__tools__lookup_data"
        ],
        permission_mode="acceptEdits"
    )

    async with ClaudeSDKClient(options=options) as client:
        # Test the custom tools
        await client.query(
            "What time is it? Also calculate 15 * 23 + 7. "
            "And look up the 'product' key from the database."
        )

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)


if __name__ == "__main__":
    asyncio.run(main())
