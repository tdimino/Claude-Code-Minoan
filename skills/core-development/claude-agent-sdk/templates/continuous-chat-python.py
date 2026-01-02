"""
Continuous Chat Template (Python)

Interactive agent that maintains conversation context across multiple exchanges.
Uses ClaudeSDKClient for session persistence.
"""

import asyncio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ResultMessage
)


async def main():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
        permission_mode="acceptEdits",
        cwd="."
    )

    print("Interactive Agent (type 'quit' to exit, 'new' for fresh session)")
    print("-" * 50)

    async with ClaudeSDKClient(options=options) as client:
        turn = 0

        while True:
            # Get user input
            user_input = input(f"\n[Turn {turn + 1}] You: ").strip()

            if user_input.lower() == "quit":
                print("Goodbye!")
                break

            if user_input.lower() == "new":
                await client.disconnect()
                await client.connect()
                turn = 0
                print("Started fresh session.")
                continue

            if not user_input:
                continue

            # Send to Claude
            await client.query(user_input)
            turn += 1

            # Process response
            print(f"\n[Turn {turn}] Claude: ", end="")

            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            print(block.text, end="")

                elif isinstance(message, ResultMessage):
                    if message.is_error:
                        print(f"\n[Error: {message.result}]")

            print()  # Newline after response


if __name__ == "__main__":
    asyncio.run(main())
