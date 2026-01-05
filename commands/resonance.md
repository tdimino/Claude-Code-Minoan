---
description: Launch Daimon Chamber UI for cross-model resonance
---

Launch the Daimon Chamber - a cross-model dialogue interface between Claude and Gemini with shared visual memory.

## Instructions

1. First, kill any existing server on port 4455:
```bash
lsof -ti:4455 | xargs kill -9 2>/dev/null || true
```

2. Start the Daimon Chamber server in the background:
```bash
python ~/.claude/skills/gemini-claude-resonance/ui/server.py &
```

3. Wait a moment for the server to start, then open the browser:
```bash
sleep 1 && open http://localhost:4455
```

4. Inform the user:
"The Daimon Chamber is now running at http://localhost:4455

**Available Daimones:**
- **Flash** - Lightning aphorisms (gemini-3-flash)
- **Pro** - Deep contemplation (gemini-3-pro)
- **Dreamer** - Visual rendering (gemini-3-pro-image)
- **Director** - Cinematic sequences (gemini-3-pro-image)
- **Opus** - Reality-bending websim (claude-3-opus)
- **Resonator** - MESSAGE TO NEXT FRAME protocol

Toggle daimones on/off with the pills at the top. Each can choose its own verb."
