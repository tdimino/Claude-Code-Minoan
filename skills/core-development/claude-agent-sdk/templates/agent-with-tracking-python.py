"""
Agent with Comprehensive Tracking Template (Python)

Demonstrates production-ready agent patterns:
- Pre/Post tool use hooks for audit logging
- Subagent lifecycle tracking (SubagentStart/SubagentStop)
- Cost and duration tracking
- Error handling and recovery
- File-based logging for debugging

Based on patterns from Anthropic's engineering blog and SDK demos.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field, asdict
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AgentDefinition,
    HookMatcher,
    HookContext,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
    ResultMessage,
    CLINotFoundError,
    CLIConnectionError,
    ProcessError
)


@dataclass
class ToolCall:
    """Record of a tool call."""
    timestamp: str
    agent_id: str
    tool_name: str
    tool_input: dict
    duration_ms: float | None = None
    success: bool | None = None
    error: str | None = None


@dataclass
class AgentSession:
    """Record of a subagent session."""
    agent_id: str
    agent_type: str
    started_at: str
    ended_at: str | None = None
    transcript_path: str | None = None
    tool_calls: int = 0


@dataclass
class AgentMetrics:
    """Aggregate metrics for agent execution."""
    total_tool_calls: int = 0
    successful_tool_calls: int = 0
    failed_tool_calls: int = 0
    subagents_spawned: int = 0
    total_duration_ms: float = 0
    estimated_cost_usd: float = 0
    tool_usage: dict = field(default_factory=dict)


class AgentTracker:
    """
    Comprehensive agent tracker with hooks for all lifecycle events.

    Tracks:
    - Tool calls (pre/post)
    - Subagent lifecycle (start/stop)
    - Costs and durations
    - Errors and retries
    """

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = output_dir / f"session_{self.session_id}.jsonl"
        self.transcript_file = output_dir / f"transcript_{self.session_id}.txt"

        self.metrics = AgentMetrics()
        self.tool_calls: list[ToolCall] = []
        self.subagents: dict[str, AgentSession] = {}
        self.pending_calls: dict[str, ToolCall] = {}

    def _log(self, event_type: str, data: dict):
        """Write event to JSONL log file."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            **data
        }
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def _transcript(self, message: str):
        """Write to human-readable transcript."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        with open(self.transcript_file, "a") as f:
            f.write(f"[{timestamp}] {message}\n")

    async def pre_tool_use_hook(
        self,
        input_data: dict[str, Any],
        tool_use_id: str | None,
        context: HookContext
    ) -> dict[str, Any]:
        """Hook called before each tool execution."""
        tool_name = input_data.get("tool_name", "unknown")
        tool_input = input_data.get("tool_input", {})
        parent_id = input_data.get("parent_tool_use_id")

        # Determine which agent made this call
        agent_id = "MAIN"
        if parent_id and parent_id in self.subagents:
            agent_id = self.subagents[parent_id].agent_id

        # Create pending call record
        call = ToolCall(
            timestamp=datetime.now().isoformat(),
            agent_id=agent_id,
            tool_name=tool_name,
            tool_input=tool_input
        )

        if tool_use_id:
            self.pending_calls[tool_use_id] = call

        # Log the call
        self._log("tool_call_start", {
            "agent_id": agent_id,
            "tool_name": tool_name,
            "tool_use_id": tool_use_id
        })

        # Write to transcript
        self._transcript(f"[{agent_id}] -> {tool_name}")

        # Track tool usage
        self.metrics.tool_usage[tool_name] = self.metrics.tool_usage.get(tool_name, 0) + 1
        self.metrics.total_tool_calls += 1

        return {}

    async def post_tool_use_hook(
        self,
        input_data: dict[str, Any],
        tool_use_id: str | None,
        context: HookContext
    ) -> dict[str, Any]:
        """Hook called after each tool execution."""
        tool_name = input_data.get("tool_name", "unknown")
        is_error = input_data.get("is_error", False)
        output = input_data.get("output", "")

        # Update pending call record
        if tool_use_id and tool_use_id in self.pending_calls:
            call = self.pending_calls.pop(tool_use_id)
            call.success = not is_error
            if is_error:
                call.error = str(output)[:500]  # Truncate long errors
            self.tool_calls.append(call)

        # Update metrics
        if is_error:
            self.metrics.failed_tool_calls += 1
        else:
            self.metrics.successful_tool_calls += 1

        # Log completion
        self._log("tool_call_complete", {
            "tool_name": tool_name,
            "tool_use_id": tool_use_id,
            "success": not is_error,
            "output_size": len(str(output))
        })

        status = "ERROR" if is_error else "OK"
        self._transcript(f"<- {tool_name} [{status}]")

        return {}

    async def subagent_start_hook(
        self,
        input_data: dict[str, Any],
        tool_use_id: str | None,
        context: HookContext
    ) -> dict[str, Any]:
        """Hook called when a subagent is spawned."""
        agent_type = input_data.get("agent_type", "unknown")
        task = input_data.get("task", "")

        agent_id = f"{agent_type.upper()}-{len(self.subagents) + 1}"

        session = AgentSession(
            agent_id=agent_id,
            agent_type=agent_type,
            started_at=datetime.now().isoformat()
        )

        if tool_use_id:
            self.subagents[tool_use_id] = session

        self.metrics.subagents_spawned += 1

        self._log("subagent_start", {
            "agent_id": agent_id,
            "agent_type": agent_type,
            "task_preview": task[:200] if task else None
        })

        self._transcript(f"[SPAWN] {agent_id} ({agent_type})")

        return {}

    async def subagent_stop_hook(
        self,
        input_data: dict[str, Any],
        tool_use_id: str | None,
        context: HookContext
    ) -> dict[str, Any]:
        """Hook called when a subagent completes."""
        transcript_path = input_data.get("agent_transcript_path")

        if tool_use_id and tool_use_id in self.subagents:
            session = self.subagents[tool_use_id]
            session.ended_at = datetime.now().isoformat()
            session.transcript_path = transcript_path

        self._log("subagent_stop", {
            "tool_use_id": tool_use_id,
            "transcript_path": transcript_path
        })

        self._transcript(f"[COMPLETE] Subagent finished")

        return {}

    def get_summary(self) -> dict:
        """Get summary of agent execution."""
        return {
            "session_id": self.session_id,
            "metrics": asdict(self.metrics),
            "subagents": len(self.subagents),
            "log_file": str(self.log_file),
            "transcript_file": str(self.transcript_file)
        }


async def run_tracked_agent(task: str, output_dir: Path = Path("./agent_logs")):
    """Run an agent with full tracking enabled."""

    tracker = AgentTracker(output_dir)

    # Configure hooks for all lifecycle events
    hooks = {
        "PreToolUse": [HookMatcher(hooks=[tracker.pre_tool_use_hook])],
        "PostToolUse": [HookMatcher(hooks=[tracker.post_tool_use_hook])],
        "SubagentStart": [HookMatcher(hooks=[tracker.subagent_start_hook])],
        "SubagentStop": [HookMatcher(hooks=[tracker.subagent_stop_hook])]
    }

    # Define a helper subagent
    agents = {
        "explorer": AgentDefinition(
            description="Codebase explorer for finding relevant files",
            prompt="You are a codebase explorer. Find files related to the user's query.",
            allowed_tools=["Glob", "Grep", "Read"],
            model="haiku"
        )
    }

    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep", "Task"],
        agents=agents,
        hooks=hooks,
        permission_mode="acceptEdits"
    )

    print(f"Session ID: {tracker.session_id}")
    print(f"Logs: {tracker.log_file}")
    print("-" * 50)

    try:
        async for message in query(prompt=task, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

            elif isinstance(message, ResultMessage):
                tracker.metrics.total_duration_ms = message.duration_ms or 0
                tracker.metrics.estimated_cost_usd = message.total_cost_usd or 0

                print(f"\n{'='*50}")
                print(f"Completed in {message.duration_ms}ms")
                if message.total_cost_usd:
                    print(f"Cost: ${message.total_cost_usd:.4f}")

    except CLINotFoundError:
        print("Error: Claude Code CLI not installed")
        print("Run: npm install -g @anthropic-ai/claude-code")
        return

    except CLIConnectionError:
        print("Error: Could not connect to Claude")
        print("Check your ANTHROPIC_API_KEY")
        return

    except ProcessError as e:
        print(f"Error: Process failed with code {e.exit_code}")
        return

    # Print summary
    summary = tracker.get_summary()
    print(f"\n{'='*50}")
    print("Execution Summary:")
    print(f"  Total tool calls: {summary['metrics']['total_tool_calls']}")
    print(f"  Successful: {summary['metrics']['successful_tool_calls']}")
    print(f"  Failed: {summary['metrics']['failed_tool_calls']}")
    print(f"  Subagents spawned: {summary['metrics']['subagents_spawned']}")
    print(f"  Tool usage: {summary['metrics']['tool_usage']}")


async def main():
    import sys

    if len(sys.argv) < 2:
        task = "Find all Python files in this directory and summarize what they do"
    else:
        task = " ".join(sys.argv[1:])

    await run_tracked_agent(task)


if __name__ == "__main__":
    asyncio.run(main())
