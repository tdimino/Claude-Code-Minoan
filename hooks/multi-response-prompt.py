#!/usr/bin/env python3
"""
Hook to inject multi-response generation instructions into Claude Code prompts.
Requests 5 alternative responses sampled from distribution tails (p < 0.10 each).

Trigger: Add "/5x" to the end of your message.
"""
import json
import sys

input_data = json.load(sys.stdin)
prompt = input_data.get("prompt", "")

# Only activate if trigger phrase is present
if "/5x" in prompt:
    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": "Generate 5 responses to the user query, each within a separate <response> tag. Each <response> must include a <text> and a numeric <probability>. Please sample at random from the tails of the distribution, such that the probability of each response is less than 0.10."
        }
    }
    print(json.dumps(output))

sys.exit(0)
