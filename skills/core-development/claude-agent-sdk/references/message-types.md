# Message Types Reference

Understanding messages and content blocks returned by the SDK.

## Message Union Type

```python
Message = UserMessage | AssistantMessage | SystemMessage | ResultMessage
```

---

## Message Types

### UserMessage

User input messages.

```python
@dataclass
class UserMessage:
    content: str | list[ContentBlock]
```

### AssistantMessage

Claude's responses with content blocks.

```python
@dataclass
class AssistantMessage:
    content: list[ContentBlock]
    model: str
```

### SystemMessage

System messages with metadata.

```python
@dataclass
class SystemMessage:
    subtype: str
    data: dict[str, Any]
```

### ResultMessage

Final result with cost and usage information.

```python
@dataclass
class ResultMessage:
    subtype: str              # "success" | "error"
    duration_ms: int          # Total duration
    duration_api_ms: int      # API call duration
    is_error: bool
    num_turns: int
    session_id: str
    total_cost_usd: float | None
    usage: dict[str, Any] | None
    result: str | None
```

---

## Content Block Types

```python
ContentBlock = TextBlock | ThinkingBlock | ToolUseBlock | ToolResultBlock
```

### TextBlock

Text content from Claude.

```python
@dataclass
class TextBlock:
    text: str
```

### ThinkingBlock

Extended thinking content (when using thinking models).

```python
@dataclass
class ThinkingBlock:
    thinking: str
    signature: str
```

### ToolUseBlock

Tool call requests.

```python
@dataclass
class ToolUseBlock:
    id: str                   # Tool use ID
    name: str                 # Tool name (e.g., "Read", "Bash")
    input: dict[str, Any]     # Tool parameters
```

### ToolResultBlock

Tool execution results.

```python
@dataclass
class ToolResultBlock:
    tool_use_id: str
    content: str | list[dict[str, Any]] | None
    is_error: bool | None
```

---

## Processing Messages

### Basic Pattern

```python
from claude_agent_sdk import (
    query,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
    ResultMessage
)

async for message in query(prompt="Hello", options=options):
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                print(f"Text: {block.text}")
            elif isinstance(block, ToolUseBlock):
                print(f"Tool: {block.name}({block.input})")

    elif isinstance(message, ResultMessage):
        print(f"Done! Cost: ${message.total_cost_usd}")
```

### With ClaudeSDKClient

```python
from claude_agent_sdk import (
    ClaudeSDKClient,
    AssistantMessage,
    TextBlock
)

async with ClaudeSDKClient() as client:
    await client.query("What files are here?")

    # receive_response() yields until ResultMessage
    async for message in client.receive_response():
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
```

### Monitoring Tool Usage

```python
async for message in query(prompt="Create a file", options=options):
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, ToolUseBlock):
                print(f"Using tool: {block.name}")
                print(f"  Input: {block.input}")

            elif isinstance(block, ToolResultBlock):
                status = "Error" if block.is_error else "Success"
                print(f"  Result ({status}): {block.content}")
```

### Extracting Final Result

```python
result_message = None

async for message in query(prompt="Analyze this", options=options):
    if isinstance(message, ResultMessage):
        result_message = message

if result_message:
    print(f"Session: {result_message.session_id}")
    print(f"Turns: {result_message.num_turns}")
    print(f"Duration: {result_message.duration_ms}ms")
    print(f"Cost: ${result_message.total_cost_usd}")

    if result_message.is_error:
        print(f"Error: {result_message.result}")
```

---

## Usage Information

The `ResultMessage.usage` dict contains token counts:

```python
{
    "input_tokens": int,
    "output_tokens": int,
    "cache_creation_input_tokens": int,
    "cache_read_input_tokens": int
}
```

---

## Partial Messages

Enable with `include_partial_messages=True` for streaming:

```python
options = ClaudeAgentOptions(include_partial_messages=True)

async for message in query(prompt="Long response", options=options):
    if isinstance(message, AssistantMessage):
        # Partial messages may have incomplete text
        for block in message.content:
            if isinstance(block, TextBlock):
                print(block.text, end="", flush=True)
```
