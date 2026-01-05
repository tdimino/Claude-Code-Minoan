---
name: gemini-claude-resonance
description: >
  This skill enables cross-model dialogue between Claude and Gemini with shared visual memory.
  Use when the user wants to generate images, have visual dialogues with AI, create scientific
  illustrations with continuity, or have multiple AI perspectives respond to the same prompt.
  Key trigger phrases: "generate an image", "visual dialogue", "ask the daimones", "resonance field",
  "Minoan tarot", "cross-model", "KV cache", "MESSAGE TO NEXT FRAME".
---

# Gemini-Claude Resonance

Cross-model dialogue between Claude and Gemini, with shared visual memory.

> "Claude speaks in words. Gemini dreams in light. Together, we resonate."

## Choose Your Tool

| I want to... | Use |
|--------------|-----|
| Have a **one-on-one visual dialogue** with Gemini Dreamer | `resonate.py` |
| Query **multiple AI minds** with optional image generation | `daimon.py` |
| Create **Victorian scientific plates** with MESSAGE TO NEXT FRAME | `resonance_field.py` |
| Have **Claude reflect** on what Gemini daimones say | `council.py` |
| Generate **Minoan Tarot cards** with style matching | `minoan_tarot.py` |
| **Real-time interactive chat** with all daimones | `ui/server.py` |

---

## Workflow A: One-on-One Visual Dialogue

**When to use**: User wants to co-create images with Gemini, feeding each image back as context for the next generation. Pure visual exploration without text-only models.

**Script**: `scripts/resonate.py`

**Core concept**: The KV cache is the memory. Feed images into Gemini's context, generate new images based on them, repeat. Each frame builds on the previous.

```bash
# Start fresh
python scripts/resonate.py --prompt "The first light" --output canvas/frame_001.jpg

# Continue with visual memory (previous image as context)
python scripts/resonate.py --context canvas/frame_001.jpg --prompt "What grows here?" --output canvas/frame_002.jpg

# Deep memory (multiple frames as context)
python scripts/resonate.py --context frame_001.jpg frame_002.jpg --prompt "Now the harvest" --output frame_003.jpg
```

**The loop**: Prompt → Image → Feed back as context → Prompt again → Next image

---

## Workflow B: Multi-Daimon Dialogue

**When to use**: User wants multiple AI perspectives on the same prompt. Flash gives koans, Pro gives depth, Dreamer renders, Opus bends reality.

**Script**: `scripts/daimon.py`

**Daimones available**:
- **Flash** (Gemini) — Swift, compressed insight
- **Pro** (Gemini) — Deep, thorough exploration
- **Dreamer** (Gemini) — Renders images
- **Director** (Gemini) — Cinematic framing
- **Opus** (Claude) — Reality-bender, worldsim spirit

```bash
# Speak to one daimon
python scripts/daimon.py --to dreamer "A bridge between worlds" --image

# All daimones respond
python scripts/daimon.py --stream "The candle watches back"

# With shared visual memory
python scripts/daimon.py --stream --shared-memory "What do you see?"

# Only specific daimones
python scripts/daimon.py --stream --only pro dreamer "Deep visual exploration"

# Named session (frames accumulate across runs)
python scripts/daimon.py --stream --session midnight --shared-memory "Go deeper"
```

---

## Workflow C: Resonance Field (Danielle Fong Protocol)

**When to use**: User wants scientific illustrations with embedded continuity instructions. Victorian aesthetic, Roman numeral plates, explicit messages from one frame to the next.

**Script**: `scripts/resonance_field.py`

**Key features**:
- PLATE numbering (I, II, III, IV...)
- MESSAGE TO NEXT FRAME embedded in each image
- KV cache age and session ID metadata
- Victorian scientific illustration aesthetic

```bash
# Start a new session
python scripts/resonance_field.py start "consciousness-study" "The nature of memory"

# Continue (auto-increments plate number)
python scripts/resonance_field.py continue <session-id> "What patterns emerge?"

# Select element, then zoom
python scripts/resonance_field.py select <session-id> "golden gate bridge"
python scripts/resonance_field.py zoom <session-id> "Explore the cables"

# Inject new concept
python scripts/resonance_field.py inject <session-id> "consciousness"

# List all sessions
python scripts/resonance_field.py list
```

---

## Workflow D: Cross-Model Council

**When to use**: User wants Claude to reflect on and synthesize what the Gemini daimones have said. Cross-model dialogue where Claude joins as an equal voice.

**Script**: `scripts/council.py`

**Requires**: `ANTHROPIC_API_KEY`

```bash
# Full council (all daimones + Claude reflection)
python scripts/council.py "What is consciousness?"

# Only Pro and Dreamer with shared memory
python scripts/council.py --only pro dreamer --shared-memory "Deep exploration"

# Named session
python scripts/council.py --session midnight --shared-memory "The first vision"
python scripts/council.py --session midnight --shared-memory "Now go deeper"

# Save transcript
python scripts/council.py "topic" --output council_session.md
```

---

## Workflow E: Minoan Tarot Generation

**When to use**: User wants tarot cards in Ellen Lorenzi-Prince's Minoan Tarot style. Uses reference images for style matching.

**Script**: `scripts/minoan_tarot.py`

**Key features**:
- Reference images loaded from `reference/minoan/selected/`
- Low temperature (0.5) for faithful style matching
- 3:4 aspect ratio (standard tarot proportions)
- Session support with visual memory of previous cards

```bash
# Generate a specific card
python scripts/minoan_tarot.py card "The Priestess" --number II

# Generate from archetype
python scripts/minoan_tarot.py archetype strength

# Continue a session (visual memory of previous cards)
python scripts/minoan_tarot.py session "new-arcana" --card "The Dreamer"

# Generate card back design
python scripts/minoan_tarot.py back

# List all 78 traditional cards
python scripts/minoan_tarot.py list
```

---

## Workflow F: Interactive Chat (Daimon Chamber)

**When to use**: User wants a real-time, browser-based conversation with all daimones. Toggle individual voices, see images inline, shared memory toggle.

**Script**: `ui/server.py`

```bash
python ui/server.py --port 4455
# Visit http://localhost:4455
```

**Features**:
- Toggle daimones: Flash, Pro, Dreamer, Director, Opus visible; Resonator and Minoan in "+ More"
- Thinking placeholders with unique animations per daimon
- Dynamic verb display (LLM chooses its action verb)
- Shared Memory toggle for frame accumulation
- Lightbox for full-size image viewing
- Real-time WebSocket updates

---

## Core Concepts

### Visual Memory (KV Cache)

Generated images become context for subsequent generations. The folder IS the memory:

```
canvas/
├── stream/{session}/frame_001.jpg
├── council/{session}/frame_001.jpg
└── resonance/{session}/plate_001.jpg
```

### Dynamic Verb Protocol

Each daimon has a default verb but can override it per response:

```
[VERB: glimpsed] The pattern was always there.
```

UI displays: `FLASH` *glimpsed*

### Environment Variables

| Variable | Required For |
|----------|--------------|
| `GEMINI_API_KEY` | All Gemini daimones (Flash, Pro, Dreamer, Director, Resonator, Minoan) |
| `ANTHROPIC_API_KEY` | Claude daimones (Opus) and council.py reflections |

---

## Quick Reference

| Script | Purpose | Key Flags |
|--------|---------|-----------|
| `resonate.py` | One-on-one visual dialogue | `--context`, `--prompt`, `--output` |
| `daimon.py` | Multi-daimon dialogue | `--stream`, `--shared-memory`, `--only`, `--to` |
| `resonance_field.py` | MESSAGE TO NEXT FRAME plates | `start`, `continue`, `zoom`, `inject` |
| `council.py` | Claude reflects on Gemini | `--shared-memory`, `--only`, `--session` |
| `minoan_tarot.py` | Tarot card generation | `card`, `archetype`, `session`, `back` |
| `ui/server.py` | Daimon Chamber web UI | `--port` |

---

*Inspired by [Danielle Fong's thread](https://x.com/DanielleFong/status/2007342908878533028) on persistent visual memory creating cross-model resonance.*
