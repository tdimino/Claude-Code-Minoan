"""
Research Agent Template (Python)

Multi-agent research system that demonstrates:
- Parallel subagent execution
- Hook-based tool tracking
- File-based output coordination
- Specialized agent roles

Based on Anthropic's research-agent demo.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AgentDefinition,
    HookMatcher,
    HookContext,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
    ResultMessage
)


# Configuration
OUTPUT_DIR = Path("./research_output")
LOGS_DIR = Path("./logs")


def setup_directories():
    """Create output directories."""
    (OUTPUT_DIR / "research_notes").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "data").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "charts").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "reports").mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


class AgentTracker:
    """Tracks tool calls across agents for debugging and audit."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.transcript_path = LOGS_DIR / f"session_{session_id}" / "transcript.txt"
        self.tool_calls_path = LOGS_DIR / f"session_{session_id}" / "tool_calls.jsonl"
        self.agent_map: dict[str, str] = {}  # tool_use_id -> agent_name

        self.transcript_path.parent.mkdir(parents=True, exist_ok=True)

    async def pre_tool_use_hook(
        self,
        input_data: dict[str, Any],
        tool_use_id: str | None,
        context: HookContext
    ) -> dict[str, Any]:
        """Log tool calls before execution."""
        tool_name = input_data.get("tool_name", "unknown")
        tool_input = input_data.get("tool_input", {})
        parent_id = input_data.get("parent_tool_use_id")

        # Determine agent name from parent_tool_use_id
        agent_name = self.agent_map.get(parent_id, "LEAD")

        # Track Task tool calls to map agent IDs
        if tool_name == "Task" and tool_use_id:
            agent_type = tool_input.get("description", "SUBAGENT")
            self.agent_map[tool_use_id] = agent_type.upper()

        timestamp = datetime.now().strftime("%H:%M:%S")

        # Write to transcript
        with open(self.transcript_path, "a") as f:
            f.write(f"[{timestamp}] [{agent_name}] -> {tool_name}\n")
            if tool_name == "WebSearch":
                f.write(f"    Query: {tool_input.get('query', 'N/A')}\n")
            elif tool_name in ["Read", "Write"]:
                f.write(f"    File: {tool_input.get('file_path', 'N/A')}\n")

        return {}

    async def post_tool_use_hook(
        self,
        input_data: dict[str, Any],
        tool_use_id: str | None,
        context: HookContext
    ) -> dict[str, Any]:
        """Log tool completion."""
        tool_name = input_data.get("tool_name", "unknown")
        success = not input_data.get("is_error", False)

        timestamp = datetime.now().strftime("%H:%M:%S")
        status = "OK" if success else "ERROR"

        with open(self.transcript_path, "a") as f:
            f.write(f"[{timestamp}] <- {tool_name} [{status}]\n")

        return {}


# Define specialized subagents
def create_agents() -> dict[str, AgentDefinition]:
    """Create specialized research subagents."""
    return {
        "researcher": AgentDefinition(
            description="Web researcher that finds and summarizes information",
            prompt="""You are a research specialist. Your job is to:
1. Search the web for relevant information on the assigned topic
2. Extract key facts, statistics, and insights
3. Save your findings to research_output/research_notes/{topic}.md

Be thorough but focused. Cite sources when possible.""",
            allowed_tools=["WebSearch", "WebFetch", "Write", "Read"],
            model="sonnet"
        ),

        "data_analyst": AgentDefinition(
            description="Data analyst that extracts metrics and creates visualizations",
            prompt="""You are a data analyst. Your job is to:
1. Read the research notes from research_output/research_notes/
2. Extract key metrics and statistics
3. Create Python scripts to generate charts using matplotlib
4. Save charts to research_output/charts/
5. Save data summaries to research_output/data/

Focus on actionable insights and clear visualizations.""",
            allowed_tools=["Glob", "Read", "Bash", "Write"],
            model="sonnet"
        ),

        "report_writer": AgentDefinition(
            description="Report writer that synthesizes findings into comprehensive reports",
            prompt="""You are a report writer. Your job is to:
1. Read all research notes from research_output/research_notes/
2. Review charts from research_output/charts/
3. Synthesize findings into a comprehensive markdown report
4. Save the report to research_output/reports/{topic}_report.md

Structure the report with:
- Executive Summary
- Key Findings
- Detailed Analysis
- Data Visualizations
- Conclusions and Recommendations""",
            allowed_tools=["Glob", "Read", "Write", "Bash"],
            model="sonnet"
        )
    }


async def run_research_agent(topic: str):
    """Run the multi-agent research system."""
    setup_directories()

    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    tracker = AgentTracker(session_id)

    # Create hooks for tracking
    hooks = {
        "PreToolUse": [HookMatcher(hooks=[tracker.pre_tool_use_hook])],
        "PostToolUse": [HookMatcher(hooks=[tracker.post_tool_use_hook])]
    }

    # Configure the lead agent
    options = ClaudeAgentOptions(
        allowed_tools=["Task", "Read", "Write", "Glob"],
        agents=create_agents(),
        hooks=hooks,
        system_prompt=f"""You are a research coordinator. Your job is to:

1. Break the research topic into 2-4 subtopics
2. Spawn researcher subagents in PARALLEL to research each subtopic
3. Once research is complete, spawn a data_analyst to extract metrics
4. Finally, spawn a report_writer to create the final report

Research topic: {topic}

Output directory structure:
- research_output/research_notes/ - Research findings
- research_output/data/ - Data summaries
- research_output/charts/ - Visualizations
- research_output/reports/ - Final reports

Coordinate the agents efficiently and ensure quality output.""",
        cwd=str(Path.cwd())
    )

    print(f"Starting research on: {topic}")
    print(f"Session ID: {session_id}")
    print(f"Logs: {tracker.transcript_path}")
    print("-" * 50)

    async for message in query(
        prompt=f"Research this topic thoroughly: {topic}",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
                elif isinstance(block, ToolUseBlock):
                    if block.name == "Task":
                        agent_type = block.input.get("description", "subagent")
                        print(f"\n[Spawning {agent_type}...]")

        elif isinstance(message, ResultMessage):
            print(f"\n{'='*50}")
            print(f"Research completed in {message.duration_ms}ms")
            if message.total_cost_usd:
                print(f"Total cost: ${message.total_cost_usd:.4f}")


async def main():
    import sys

    if len(sys.argv) < 2:
        topic = "quantum computing developments in 2025"
    else:
        topic = " ".join(sys.argv[1:])

    await run_research_agent(topic)


if __name__ == "__main__":
    asyncio.run(main())
