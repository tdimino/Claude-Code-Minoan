"""
Simple Agent Template (Python)

A minimal working agent that reads and analyzes files.
"""

import asyncio
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ResultMessage
)


async def main():
    # Configure the agent
    options = ClaudeAgentOptions(
        # Enable file operations
        allowed_tools=["Read", "Glob", "Grep"],

        # Working directory (optional)
        cwd=".",

        # Custom system prompt (optional)
        system_prompt="You are a helpful code analysis assistant."
    )

    # Send a task to the agent
    prompt = "List all Python files in this directory and summarize what they do."

    print("Starting agent...\n")

    async for message in query(prompt=prompt, options=options):
        # Handle assistant responses
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)

        # Handle final result
        elif isinstance(message, ResultMessage):
            print(f"\n--- Done ---")
            print(f"Turns: {message.num_turns}")
            print(f"Duration: {message.duration_ms}ms")
            if message.total_cost_usd:
                print(f"Cost: ${message.total_cost_usd:.4f}")


if __name__ == "__main__":
    asyncio.run(main())
