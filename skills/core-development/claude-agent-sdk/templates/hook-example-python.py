"""
Hook Example Template (Python)

Demonstrates using hooks to intercept and modify agent behavior.
"""

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


# Pre-tool hook: Validate bash commands
async def validate_bash(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    """Block dangerous bash commands."""
    if input_data.get("tool_name") == "Bash":
        command = input_data.get("tool_input", {}).get("command", "")

        # List of dangerous patterns to block
        dangerous_patterns = [
            "rm -rf /",
            "sudo rm",
            "chmod 777",
            "> /dev/sda",
            "mkfs.",
            ":(){ :|:& };:"
        ]

        for pattern in dangerous_patterns:
            if pattern in command:
                print(f"[BLOCKED] Dangerous command: {command}")
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": f"Blocked dangerous pattern: {pattern}"
                    }
                }

    return {}


# Pre-tool hook: Log all tool usage
async def log_tool_usage(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    """Log tool calls for audit trail."""
    tool_name = input_data.get("tool_name", "unknown")
    tool_input = input_data.get("tool_input", {})
    timestamp = datetime.now().strftime("%H:%M:%S")

    print(f"[{timestamp}] TOOL: {tool_name}")

    # Log relevant details based on tool type
    if tool_name == "Bash":
        print(f"         CMD: {tool_input.get('command', 'N/A')}")
    elif tool_name in ["Read", "Write", "Edit"]:
        print(f"         FILE: {tool_input.get('file_path', 'N/A')}")
    elif tool_name == "Grep":
        print(f"         PATTERN: {tool_input.get('pattern', 'N/A')}")

    return {}


# Post-tool hook: Log results
async def log_tool_result(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    """Log tool completion."""
    tool_name = input_data.get("tool_name", "unknown")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] DONE: {tool_name}")
    return {}


# User prompt hook: Add context
async def enhance_prompt(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    """Add timestamp to user prompts."""
    original_prompt = input_data.get("prompt", "")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "updatedPrompt": f"[Request at {timestamp}]\n{original_prompt}"
        }
    }


async def main():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Bash", "Glob", "Grep"],
        permission_mode="acceptEdits",
        hooks={
            "PreToolUse": [
                # Security validation for Bash only
                HookMatcher(
                    matcher="Bash",
                    hooks=[validate_bash],
                    timeout=30
                ),
                # Logging for all tools
                HookMatcher(hooks=[log_tool_usage])
            ],
            "PostToolUse": [
                HookMatcher(hooks=[log_tool_result])
            ],
            "UserPromptSubmit": [
                HookMatcher(hooks=[enhance_prompt])
            ]
        }
    )

    print("Agent with Hooks Demo")
    print("=" * 50)
    print()

    async for message in query(
        prompt="List the Python files in this directory and show me the first 5 lines of each.",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"\n{block.text}")


if __name__ == "__main__":
    asyncio.run(main())
