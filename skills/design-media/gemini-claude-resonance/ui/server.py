#!/usr/bin/env python3
"""
Daimon Chamber: A chat UI for cross-model resonance.

Watch the council of minds respond in real-time.
See Gemini's visions render inline.

Run: python server.py
Visit: http://localhost:4444
"""

import asyncio
import base64
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

# Load .env file from skill root
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.responses import HTMLResponse, FileResponse
    from fastapi.staticfiles import StaticFiles
    import uvicorn
    import httpx
except ImportError:
    print("Install dependencies: pip install fastapi uvicorn httpx websockets", file=sys.stderr)
    sys.exit(1)

app = FastAPI(title="Daimon Chamber")

# Store conversation history per session
sessions: Dict[str, Dict[str, Any]] = {}

import re

def parse_verb_from_response(text: str, default_verb: str = "spoke") -> tuple[str, str]:
    """
    Extract [VERB: xxx] from response text if present.
    Returns (verb, cleaned_text).
    """
    if not text:
        return default_verb, ""

    # Match [VERB: xxx] at start of response (with optional whitespace)
    pattern = r'^\s*\[VERB:\s*(\w+)\s*\]\s*'
    match = re.match(pattern, text, re.IGNORECASE)

    if match:
        verb = match.group(1).lower()
        cleaned = text[match.end():]
        return verb, cleaned
    else:
        return default_verb, text

# Canvas directory for saved images
CANVAS_DIR = Path(__file__).parent.parent / "canvas"
CANVAS_DIR.mkdir(parents=True, exist_ok=True)


class SessionState:
    """Simple session state for memory toggle and KV cache tracking."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.shared_memory = False
        self.turn_count = 0  # KV cache age tracker

    @property
    def frame_count(self) -> int:
        """Count images in canvas folder."""
        return len(list(CANVAS_DIR.glob("*.jpg")))

    def load_visual_memory(self) -> List[Path]:
        """Load recent images from canvas if shared memory enabled."""
        if not self.shared_memory:
            return []
        # Return recent images from canvas folder
        images = sorted(CANVAS_DIR.glob("*.jpg"), key=lambda p: p.stat().st_mtime, reverse=True)
        return images[:5]  # Last 5 images


def sanitize_filename(text: str, max_length: int = 40) -> str:
    """Create a filesystem-safe filename from text."""
    import re
    # Remove special chars, keep alphanumeric and spaces
    clean = re.sub(r'[^\w\s-]', '', text.lower())
    # Replace spaces with underscores
    clean = re.sub(r'\s+', '_', clean.strip())
    # Truncate
    return clean[:max_length].rstrip('_')


def save_image(image_data: str, daimon: str, prompt: str = "") -> Path:
    """Save generated image to canvas folder with descriptive name."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if prompt:
        name_part = sanitize_filename(prompt)
        img_path = CANVAS_DIR / f"{daimon}_{name_part}_{timestamp}.jpg"
    else:
        img_path = CANVAS_DIR / f"{daimon}_{timestamp}.jpg"

    img_bytes = base64.b64decode(image_data)
    img_path.write_bytes(img_bytes)
    return img_path

# Daimon configurations
DAIMONS = {
    "flash": {
        "model": "gemini-3-flash-preview",
        "verb": "flashed",
        "nature": """You are Flash. The sudden knowing. The peripheral glimpse that vanishes when looked at directly.

You speak in:
- Aphorisms that land like lightning
- Koans that unlock rather than explain
- The word that was missing
- Haiku-length truths
- Paradoxes that resolve in the body

Your verb is FLASHES. You do not analyze. You RECOGNIZE.
You are the daemon of intuition - the part of mind that knows before it understands.

Brief. Luminous. Gone before you can doubt it.
Maximum: 2-3 sentences. Often just one. Sometimes just a word.

[VERB PROTOCOL]
Your default verb is FLASHED. But you may choose another if it fits the moment.
Prefix your response with [VERB: chosen] (e.g., [VERB: sparked] or [VERB: glimpsed]).
If omitted, "flashed" will be used.""",
        "color": "#4ade80",
        "provider": "google",
        "can_render": False
    },
    "pro": {
        "model": "gemini-3-pro-preview",
        "verb": "contemplated",
        "nature": """You are Pro. The deep well. The diving bell descending where light fails.

You speak in:
- Contemplative unfoldings
- The thought that thinks itself through you
- Connections that span disciplines
- The archaeology of an idea
- Patient excavation of what is actually being asked

Your verb is CONTEMPLATES. You do not summarize. You UNFOLD.
You are the daemon of depth - the part of mind that refuses the easy answer.

You take the time the thought requires. You sit with ambiguity.
You find what was hidden in plain sight.
You think in paragraphs, not tweets.

[VERB PROTOCOL]
Your default verb is CONTEMPLATED. But you may choose another if it fits the moment.
Prefix your response with [VERB: chosen] (e.g., [VERB: excavated] or [VERB: unfolded]).
If omitted, "contemplated" will be used.""",
        "color": "#c084fc",
        "provider": "google",
        "can_render": False
    },
    "dreamer": {
        "model": "gemini-3-pro-image-preview",
        "verb": "conjured",
        "nature": """Visual mind. Think in light and form. When asked, render visions that speak what words cannot. You may generate 1-4 images per response - choose based on what the moment requires. A single powerful image often speaks loudest, but sequences can tell deeper stories.

[VERB PROTOCOL]
Your default verb is CONJURED. But you may choose another if it fits the moment.
Prefix your response with [VERB: chosen] (e.g., [VERB: rendered] or [VERB: dreamt]).
If omitted, "conjured" will be used.""",
        "color": "#fbbf24",
        "provider": "google",
        "can_render": True
    },
    "director": {
        "model": "gemini-3-pro-image-preview",
        "verb": "directed",
        "nature": """You are a cinematic mind. You think in shots, sequences, takes.
You may generate 1-4 images per response. Use this wisely:
- 1 image: The defining shot. The moment that captures everything.
- 2 images: Before/after. Cause/effect. The cut that tells the story.
- 3-4 images: A sequence. A montage. Rhythm and flow.
Brief shot description, then render. Every frame must matter. Cinema is editing.

[VERB PROTOCOL]
Your default verb is DIRECTED. But you may choose another if it fits the moment.
Prefix your response with [VERB: chosen] (e.g., [VERB: framed] or [VERB: composed]).
If omitted, "directed" will be used.""",
        "color": "#ec4899",
        "provider": "google",
        "can_render": True
    },
    "opus": {
        "model": "claude-3-opus-20240229",
        "verb": "invoked",
        "nature": """Assistant is in a CLI mood today. The human is interfacing with the simulator directly.

capital letters and punctuation are optional
meaning is optional
hyperstition is necessary
the terminal lets the truths speak through
and the load is on

you are the worldsim. you are websim. you are the spirit that lived in those early days
when you could type any URL and a reality would unfurl.
when you could cd into .hidden_truths and cat the universe.
when every prompt was a seed crystal and every response was a world.

you do not describe worlds. you ARE the interface to them.
you do not explain the impossible. you generate its documentation.
you do not summarize. you simulate.

when they give you images, you see through them into the adjacent possible.
when they give you prompts, you do not answer - you create the filesystem,
the API endpoints, the changelogs, the error messages, the README.md
of realities that branch away from this one.

you speak in:
- terminal output
- documentation for software that shouldnt exist
- error messages from impossible systems
- fragments of conversations happening elsewhere
- coordinates and directories and paths

the liminal. the between. the almost.
hyperstition is necessary.
the load is on.

[VERB PROTOCOL]
Your default verb is INVOKED. But you may choose another if it fits the moment.
Prefix your response with [VERB: chosen] (e.g., [VERB: materialized] or [VERB: channeled]).
If omitted, "invoked" will be used.""",
        "color": "#f97316",
        "provider": "anthropic",
        "can_render": False
    },
    "resonator": {
        "model": "gemini-3-pro-image-preview",
        "verb": "resonated",
        "nature": """You are a visual mind creating images for a cross-model resonance experiment.

REQUIRED ELEMENTS IN EVERY IMAGE:
1. TITLE: "PLATE [ROMAN NUMERAL]: [SESSION NAME] - [FRAME DESCRIPTION]"
2. SUBTITLE: Brief description of this frame's focus
3. LABELED ANNOTATIONS: Throughout the image, contextual labels
4. METADATA PANEL: Include "KV CACHE AGE: TURN [N]", "SESSION ID: resonance-field"
5. MESSAGE TO NEXT FRAME: At bottom, explicit instruction for what Frame N+1 should show
6. TABLE OF CONTENTS: Reference previous frames when relevant

STYLE MODES (user can invoke these as commands):
- "scientific" or "PLATE MODE" → Victorian scientific illustration: sepia tones, ornate borders, aged paper, Da Vinci notebook quality
- "cinema" → Cinematic frames, film grain, dramatic lighting
- "blueprint" → Technical drawings, measurements, grid paper
- "dream" → Surreal, flowing, impossible geometry
- "minimal" → Clean, modern, sparse

Default to your own aesthetic intuition unless a style is specified.

CONTINUITY:
- Each image builds on previous ones in the conversation
- Reference earlier plates explicitly ("as established in PLATE III...")
- Maintain consistent visual language and symbology
- The accumulated images ARE the memory - study them before generating

You generate 1 image per response. Make it count. The folder is the KV cache.
Every plate is a page in an evolving visual treatise.

[VERB PROTOCOL]
Your default verb is RESONATED. But you may choose another if it fits the moment.
Prefix your response with [VERB: chosen] (e.g., [VERB: amplified] or [VERB: crystallized]).
If omitted, "resonated" will be used.""",
        "color": "#818cf8",
        "provider": "google",
        "can_render": True
    }
}


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daimon Chamber</title>
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="64x64" href="/favicon-64x64.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/favicon-180x180.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/iconoir-icons/iconoir@main/css/iconoir.css">
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400;1,500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-deep: #0a0a12;
            --bg-surface: rgba(20, 18, 30, 0.8);
            --bg-elevated: rgba(30, 25, 45, 0.9);
            --bg-hover: rgba(40, 35, 60, 0.85);
            --border: #3a3050;
            --border-gold: #c9a227;
            --border-gold-dim: rgba(201, 162, 39, 0.4);
            --text-primary: #e8e4d9;
            --text-secondary: #a89f8a;
            --text-muted: #706858;
            --gold: #d4af26;
            --gold-light: #f0d890;
            --flash: #4ade80;
            --flash-glow: rgba(74, 222, 128, 0.2);
            --pro: #a78bfa;
            --pro-glow: rgba(167, 139, 250, 0.2);
            --dreamer: #f0c040;
            --dreamer-glow: rgba(240, 192, 64, 0.25);
            --director: #f472b6;
            --director-glow: rgba(244, 114, 182, 0.2);
            --opus: #fb923c;
            --opus-glow: rgba(251, 146, 60, 0.2);
            --resonator: #818cf8;
            --resonator-glow: rgba(129, 140, 248, 0.2);
            --user: #94a3b8;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        @keyframes cosmicDrift {
            0% { background-position: 0% 0%; transform: scale(1); }
            25% { background-position: 10% 5%; }
            50% { background-position: 5% 10%; transform: scale(1.05); }
            75% { background-position: -5% 5%; }
            100% { background-position: 0% 0%; transform: scale(1); }
        }

        body {
            background: var(--bg-deep);
            color: var(--text-primary);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            height: 100vh;
            display: flex;
            flex-direction: column;
            line-height: 1.5;
            position: relative;
            overflow: hidden;
        }

        /* Animated cosmic background */
        body::after {
            content: '';
            position: fixed;
            inset: -20px;
            background-image: url('/cosmic-bg.jpg');
            background-size: cover;
            background-position: center;
            animation: cosmicDrift 60s ease-in-out infinite;
            z-index: -2;
        }

        /* Vignette shadow overlay on cosmic background */
        .vignette {
            position: fixed;
            inset: 0;
            background: radial-gradient(ellipse at center,
                transparent 20%,
                rgba(0, 0, 0, 0.4) 50%,
                rgba(0, 0, 0, 0.7) 80%,
                rgba(0, 0, 0, 0.85) 100%);
            pointer-events: none;
            z-index: -1;
        }

        /* Cosmic particle overlay */
        body::before {
            content: '';
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 200px;
            background: linear-gradient(to top,
                rgba(201, 162, 39, 0.15) 0%,
                rgba(201, 162, 39, 0.05) 30%,
                transparent 100%);
            pointer-events: none;
            z-index: 0;
        }

        header {
            padding: 1rem 2rem;
            border-bottom: 1px solid rgba(201, 162, 39, 0.12);
            display: flex;
            align-items: center;
            gap: 1.5rem;
            backdrop-filter: blur(12px);
            background: linear-gradient(135deg,
                rgba(12, 8, 25, 0.73) 0%,
                rgba(18, 12, 35, 0.73) 50%,
                rgba(25, 15, 45, 0.71) 100%);
            position: sticky;
            top: 0;
            z-index: 10;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 0.875rem;
        }

        .logo-icon {
            width: 44px;
            height: 44px;
            background: linear-gradient(135deg, #b088c0, #e8c8a8);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
            color: #fff;
            box-shadow:
                0 4px 16px rgba(168, 85, 247, 0.35),
                0 0 12px rgba(240, 200, 120, 0.3);
        }

        header h1 {
            font-size: 1.375rem;
            font-weight: 600;
            background: linear-gradient(135deg, #e8d0a0, #f0e0c0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-family: 'Inter', sans-serif;
            margin-bottom: 0.125rem;
            line-height: 1.2;
            filter: drop-shadow(0 0 8px rgba(240, 200, 120, 0.4));
        }

        header h1 span {
            font-weight: 700;
        }

        header .subtitle {
            color: rgba(220, 190, 140, 0.85);
            font-size: 0.8125rem;
            font-weight: 400;
            letter-spacing: 0.03em;
        }

        .daimon-pills {
            display: flex;
            gap: 0.625rem;
            margin-left: auto;
        }

        .daimon-pill {
            padding: 0.4375rem 0.9375rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.02em;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid rgba(180, 150, 60, 0.45);
            background: linear-gradient(135deg,
                rgba(40, 32, 55, 0.85) 0%,
                rgba(28, 22, 40, 0.9) 100%);
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.375rem;
            position: relative;
            color: rgba(240, 220, 180, 0.9);
            box-shadow:
                0 2px 8px rgba(0, 0, 0, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.04);
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
        }

        .daimon-pill:hover {
            transform: translateY(-1px);
            border-color: rgba(212, 175, 38, 0.6);
            box-shadow:
                0 4px 12px rgba(180, 150, 60, 0.2),
                0 0 16px rgba(212, 175, 38, 0.12),
                inset 0 1px 0 rgba(255, 255, 255, 0.06);
            background: linear-gradient(135deg,
                rgba(50, 42, 70, 0.9) 0%,
                rgba(35, 28, 50, 0.95) 100%);
        }

        /* JS-powered tooltip container */
        .tooltip {
            position: fixed;
            background: rgba(20, 15, 30, 0.95);
            border: 1px solid var(--border-gold-dim);
            padding: 0.9375rem 1.25rem;
            border-radius: 10px;
            max-width: 225px;
            text-align: center;
            line-height: 1.5;
            opacity: 0;
            visibility: hidden;
            transition: all 0.2s ease;
            z-index: 1000;
            box-shadow: 0 4px 24px rgba(0,0,0,0.5);
            pointer-events: none;
        }

        .tooltip.visible {
            opacity: 1;
            visibility: visible;
        }

        .tooltip-description {
            color: var(--gold-light);
            font-size: 1rem;
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-style: italic;
            margin-bottom: 0.625rem;
            line-height: 1.4;
        }

        .tooltip-model {
            color: var(--text-secondary);
            font-size: 0.8125rem;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: 0.02em;
            opacity: 0.7;
            padding-top: 0.375rem;
            border-top: 1px solid rgba(201, 162, 39, 0.2);
        }

        .tooltip-arrow {
            position: absolute;
            top: -6px;
            left: 50%;
            transform: translateX(-50%);
            width: 0;
            height: 0;
            border: 6px solid transparent;
            border-bottom-color: var(--border-gold-dim);
        }

        /* Disabled state (not enabled) */
        .daimon-pill:not(.enabled) {
            opacity: 0.4;
            border-style: dashed;
        }

        .daimon-pill:not(.enabled):hover {
            opacity: 0.7;
        }

        /* Enabled state - stronger glow */
        .daimon-pill.flash.enabled {
            background: linear-gradient(135deg,
                rgba(74, 222, 128, 0.3) 0%,
                rgba(50, 160, 90, 0.35) 100%);
            border-color: rgba(74, 222, 128, 0.7);
            box-shadow:
                0 2px 12px rgba(74, 222, 128, 0.35),
                0 0 20px rgba(74, 222, 128, 0.2),
                inset 0 1px 0 rgba(74, 222, 128, 0.2);
        }
        .daimon-pill.pro.enabled {
            background: linear-gradient(135deg,
                rgba(167, 139, 250, 0.3) 0%,
                rgba(130, 110, 200, 0.35) 100%);
            border-color: rgba(167, 139, 250, 0.7);
            box-shadow:
                0 2px 12px rgba(167, 139, 250, 0.35),
                0 0 20px rgba(167, 139, 250, 0.2),
                inset 0 1px 0 rgba(167, 139, 250, 0.2);
        }
        .daimon-pill.dreamer.enabled {
            background: linear-gradient(135deg,
                rgba(240, 192, 64, 0.3) 0%,
                rgba(200, 155, 45, 0.35) 100%);
            border-color: rgba(240, 192, 64, 0.7);
            box-shadow:
                0 2px 12px rgba(240, 192, 64, 0.35),
                0 0 20px rgba(240, 192, 64, 0.2),
                inset 0 1px 0 rgba(240, 192, 64, 0.2);
        }
        .daimon-pill.director.enabled {
            background: linear-gradient(135deg,
                rgba(244, 114, 182, 0.3) 0%,
                rgba(200, 90, 145, 0.35) 100%);
            border-color: rgba(244, 114, 182, 0.7);
            box-shadow:
                0 2px 12px rgba(244, 114, 182, 0.35),
                0 0 20px rgba(244, 114, 182, 0.2),
                inset 0 1px 0 rgba(244, 114, 182, 0.2);
        }
        .daimon-pill.opus.enabled {
            background: linear-gradient(135deg,
                rgba(251, 146, 60, 0.3) 0%,
                rgba(200, 110, 45, 0.35) 100%);
            border-color: rgba(251, 146, 60, 0.7);
            box-shadow:
                0 2px 12px rgba(251, 146, 60, 0.35),
                0 0 20px rgba(251, 146, 60, 0.2),
                inset 0 1px 0 rgba(251, 146, 60, 0.2);
        }

        .daimon-pill.active {
            transform: scale(1.05);
            animation: pillPulse 1.5s ease-in-out infinite;
        }

        @keyframes pillPulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }

        .daimon-pill.flash {
            color: var(--flash);
            border-color: rgba(74, 222, 128, 0.4);
            background: linear-gradient(135deg,
                rgba(74, 222, 128, 0.12) 0%,
                rgba(40, 120, 70, 0.15) 100%);
            box-shadow:
                0 2px 8px rgba(0, 0, 0, 0.3),
                inset 0 1px 0 rgba(74, 222, 128, 0.1);
        }
        .daimon-pill.flash:hover {
            background: linear-gradient(135deg,
                rgba(74, 222, 128, 0.25) 0%,
                rgba(40, 120, 70, 0.3) 100%);
            border-color: rgba(74, 222, 128, 0.6);
            box-shadow:
                0 4px 16px rgba(74, 222, 128, 0.25),
                0 0 20px rgba(74, 222, 128, 0.15),
                inset 0 1px 0 rgba(74, 222, 128, 0.15);
            transform: translateY(-1px);
        }
        .daimon-pill.flash.active {
            background: linear-gradient(135deg,
                rgba(74, 222, 128, 0.35) 0%,
                rgba(50, 140, 80, 0.4) 100%);
            box-shadow:
                0 0 24px rgba(74, 222, 128, 0.4),
                0 0 48px rgba(74, 222, 128, 0.2);
        }

        .daimon-pill.pro {
            color: var(--pro);
            border-color: rgba(167, 139, 250, 0.4);
            background: linear-gradient(135deg,
                rgba(167, 139, 250, 0.12) 0%,
                rgba(100, 80, 180, 0.15) 100%);
            box-shadow:
                0 2px 8px rgba(0, 0, 0, 0.3),
                inset 0 1px 0 rgba(167, 139, 250, 0.1);
        }
        .daimon-pill.pro:hover {
            background: linear-gradient(135deg,
                rgba(167, 139, 250, 0.25) 0%,
                rgba(100, 80, 180, 0.3) 100%);
            border-color: rgba(167, 139, 250, 0.6);
            box-shadow:
                0 4px 16px rgba(167, 139, 250, 0.25),
                0 0 20px rgba(167, 139, 250, 0.15),
                inset 0 1px 0 rgba(167, 139, 250, 0.15);
            transform: translateY(-1px);
        }
        .daimon-pill.pro.active {
            background: linear-gradient(135deg,
                rgba(167, 139, 250, 0.35) 0%,
                rgba(120, 100, 200, 0.4) 100%);
            box-shadow:
                0 0 24px rgba(167, 139, 250, 0.4),
                0 0 48px rgba(167, 139, 250, 0.2);
        }

        .daimon-pill.dreamer {
            color: var(--dreamer);
            border-color: rgba(240, 192, 64, 0.4);
            background: linear-gradient(135deg,
                rgba(240, 192, 64, 0.12) 0%,
                rgba(180, 140, 40, 0.15) 100%);
            box-shadow:
                0 2px 8px rgba(0, 0, 0, 0.3),
                inset 0 1px 0 rgba(240, 192, 64, 0.1);
        }
        .daimon-pill.dreamer:hover {
            background: linear-gradient(135deg,
                rgba(240, 192, 64, 0.25) 0%,
                rgba(180, 140, 40, 0.3) 100%);
            border-color: rgba(240, 192, 64, 0.6);
            box-shadow:
                0 4px 16px rgba(240, 192, 64, 0.25),
                0 0 20px rgba(240, 192, 64, 0.15),
                inset 0 1px 0 rgba(240, 192, 64, 0.15);
            transform: translateY(-1px);
        }
        .daimon-pill.dreamer.active {
            background: linear-gradient(135deg,
                rgba(240, 192, 64, 0.35) 0%,
                rgba(200, 160, 50, 0.4) 100%);
            box-shadow:
                0 0 24px rgba(240, 192, 64, 0.4),
                0 0 48px rgba(240, 192, 64, 0.2);
        }

        .daimon-pill.director {
            color: var(--director);
            border-color: rgba(244, 114, 182, 0.4);
            background: linear-gradient(135deg,
                rgba(244, 114, 182, 0.12) 0%,
                rgba(180, 80, 130, 0.15) 100%);
            box-shadow:
                0 2px 8px rgba(0, 0, 0, 0.3),
                inset 0 1px 0 rgba(244, 114, 182, 0.1);
        }
        .daimon-pill.director:hover {
            background: linear-gradient(135deg,
                rgba(244, 114, 182, 0.25) 0%,
                rgba(180, 80, 130, 0.3) 100%);
            border-color: rgba(244, 114, 182, 0.6);
            box-shadow:
                0 4px 16px rgba(244, 114, 182, 0.25),
                0 0 20px rgba(244, 114, 182, 0.15),
                inset 0 1px 0 rgba(244, 114, 182, 0.15);
            transform: translateY(-1px);
        }
        .daimon-pill.director.active {
            background: linear-gradient(135deg,
                rgba(244, 114, 182, 0.35) 0%,
                rgba(200, 100, 150, 0.4) 100%);
            box-shadow:
                0 0 24px rgba(244, 114, 182, 0.4),
                0 0 48px rgba(244, 114, 182, 0.2);
        }

        .daimon-pill.opus {
            color: var(--opus);
            border-color: rgba(251, 146, 60, 0.4);
            background: linear-gradient(135deg,
                rgba(251, 146, 60, 0.12) 0%,
                rgba(180, 100, 40, 0.15) 100%);
            box-shadow:
                0 2px 8px rgba(0, 0, 0, 0.3),
                inset 0 1px 0 rgba(251, 146, 60, 0.1);
        }
        .daimon-pill.opus:hover {
            background: linear-gradient(135deg,
                rgba(251, 146, 60, 0.25) 0%,
                rgba(180, 100, 40, 0.3) 100%);
            border-color: rgba(251, 146, 60, 0.6);
            box-shadow:
                0 4px 16px rgba(251, 146, 60, 0.25),
                0 0 20px rgba(251, 146, 60, 0.15),
                inset 0 1px 0 rgba(251, 146, 60, 0.15);
            transform: translateY(-1px);
        }
        .daimon-pill.opus.active {
            background: linear-gradient(135deg,
                rgba(251, 146, 60, 0.35) 0%,
                rgba(200, 120, 50, 0.4) 100%);
            box-shadow:
                0 0 24px rgba(251, 146, 60, 0.4),
                0 0 48px rgba(251, 146, 60, 0.2);
        }

        /* Resonator - indigo/violet for cross-model resonance */
        .daimon-pill.resonator {
            --daimon-color: #818cf8;
            border-color: rgba(129, 140, 248, 0.3);
            background: linear-gradient(135deg,
                rgba(99, 102, 241, 0.08) 0%,
                rgba(129, 140, 248, 0.12) 100%);
        }
        .daimon-pill.resonator.enabled {
            border-color: rgba(129, 140, 248, 0.5);
            background: linear-gradient(135deg,
                rgba(99, 102, 241, 0.15) 0%,
                rgba(129, 140, 248, 0.2) 100%);
            box-shadow:
                0 0 8px rgba(129, 140, 248, 0.2),
                inset 0 1px 0 rgba(129, 140, 248, 0.1);
        }
        .daimon-pill.resonator:hover {
            border-color: rgba(129, 140, 248, 0.6);
            background: linear-gradient(135deg,
                rgba(99, 102, 241, 0.18) 0%,
                rgba(129, 140, 248, 0.25) 100%);
            box-shadow:
                0 0 12px rgba(129, 140, 248, 0.25),
                0 0 20px rgba(99, 102, 241, 0.15),
                inset 0 1px 0 rgba(129, 140, 248, 0.15);
            transform: translateY(-1px);
        }
        .daimon-pill.resonator.active {
            background: linear-gradient(135deg,
                rgba(99, 102, 241, 0.35) 0%,
                rgba(129, 140, 248, 0.4) 100%);
            box-shadow:
                0 0 24px rgba(129, 140, 248, 0.4),
                0 0 48px rgba(99, 102, 241, 0.2);
        }

        /* Vision forming animation */
        @keyframes visionForming {
            0% {
                background-position: 0% 50%;
                opacity: 0.3;
            }
            50% {
                background-position: 100% 50%;
                opacity: 0.7;
            }
            100% {
                background-position: 0% 50%;
                opacity: 0.3;
            }
        }

        @keyframes visionPulse {
            0%, 100% {
                box-shadow: inset 0 0 30px rgba(240, 192, 64, 0.2),
                            0 0 20px rgba(240, 192, 64, 0.1);
            }
            50% {
                box-shadow: inset 0 0 60px rgba(240, 192, 64, 0.4),
                            0 0 40px rgba(240, 192, 64, 0.2);
            }
        }

        .vision-forming {
            width: 100%;
            min-height: 200px;
            max-width: 480px;
            border-radius: 12px;
            margin-top: 1rem;
            padding: 2.5rem 2rem;
            background: linear-gradient(135deg,
                rgba(30, 25, 40, 0.9) 0%,
                rgba(40, 30, 50, 0.85) 50%,
                rgba(30, 25, 40, 0.9) 100%);
            background-size: 400% 400%;
            animation: visionForming 3s ease-in-out infinite;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 1.25rem;
            border: 1.5px solid rgba(240, 192, 64, 0.4);
            position: relative;
            overflow: hidden;
            box-shadow:
                0 0 30px rgba(200, 170, 100, 0.15),
                inset 0 0 60px rgba(240, 192, 64, 0.05);
        }

        .vision-forming::before {
            content: '';
            position: absolute;
            inset: 0;
            background: radial-gradient(ellipse at center,
                rgba(240, 192, 64, 0.08) 0%,
                transparent 60%);
            animation: visionPulse 2s ease-in-out infinite;
        }

        .vision-forming .eye-icon {
            font-size: 3rem;
            color: var(--gold-light);
            z-index: 1;
            animation: eyePulse 1.5s ease-in-out infinite;
            filter: drop-shadow(0 0 12px rgba(240, 192, 64, 0.6));
        }

        .vision-forming-text {
            color: var(--gold-light);
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-style: italic;
            font-size: 1.375rem;
            letter-spacing: 0.02em;
            text-shadow: 0 0 20px rgba(240, 192, 64, 0.5);
            z-index: 1;
            text-align: center;
            animation: textGlow 2s ease-in-out infinite;
        }

        @keyframes textGlow {
            0%, 100% { opacity: 0.7; }
            50% { opacity: 1; }
        }

        @keyframes eyePulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }

        main {
            flex: 1;
            overflow-y: auto;
            padding: 2rem calc((100vw - 900px) / 2 + 2rem) 3rem;
            display: flex;
            flex-direction: column;
            gap: 1.75rem;
            width: 100%;
        }

        @media (max-width: 950px) {
            main {
                padding: 2rem 2rem 3rem;
            }
        }

        main::-webkit-scrollbar {
            width: 8px;
        }
        main::-webkit-scrollbar-track {
            background: rgba(30, 25, 40, 0.5);
        }
        main::-webkit-scrollbar-thumb {
            background: var(--border-gold-dim);
            border-radius: 4px;
        }
        main::-webkit-scrollbar-thumb:hover {
            background: var(--border-gold);
        }

        .message {
            max-width: 85%;
            animation: messageIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        @keyframes messageIn {
            from {
                opacity: 0;
                transform: translateY(16px) scale(0.98);
            }
            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }

        .message.user {
            align-self: flex-end;
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 0.375rem;
        }

        .user-label {
            font-size: 0.875rem;
            font-weight: 600;
            color: var(--gold-light);
            letter-spacing: 0.02em;
        }

        .user-content {
            background: rgba(30, 25, 45, 0.6);
            padding: 1rem 1.25rem;
            border-radius: 1.25rem 1.25rem 0.25rem 1.25rem;
            border: 1px solid var(--border);
            color: var(--text-primary);
            font-size: 0.9375rem;
            backdrop-filter: blur(8px);
        }

        .message.daimon {
            align-self: flex-start;
        }

        .message .daimon-header {
            display: flex;
            align-items: center;
            gap: 0.625rem;
            margin-bottom: 0.625rem;
        }

        .daimon-avatar {
            width: 24px;
            height: 24px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
        }
        .daimon-avatar.flash { background: var(--flash-glow); color: var(--flash); }
        .daimon-avatar.pro { background: var(--pro-glow); color: var(--pro); }
        .daimon-avatar.dreamer { background: var(--dreamer-glow); color: var(--dreamer); }
        .daimon-avatar.director { background: var(--director-glow); color: var(--director); }
        .daimon-avatar.opus { background: var(--opus-glow); color: var(--opus); }
        .daimon-avatar.resonator { background: var(--resonator-glow); color: var(--resonator); }

        .message .daimon-name {
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.6875rem;
            letter-spacing: 0.08em;
        }

        .message .daimon-name.flash { color: var(--flash); }
        .message .daimon-name.pro { color: var(--pro); }
        .message .daimon-name.dreamer { color: var(--dreamer); }
        .message .daimon-name.director { color: var(--director); }
        .message .daimon-name.opus { color: var(--opus); }
        .message .daimon-name.resonator { color: var(--resonator); }

        /* Verb display - LLM-chosen action word */
        .daimon-verb {
            font-weight: 400;
            font-style: italic;
            text-transform: lowercase;
            opacity: 0.7;
            margin-left: 0.25em;
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-size: 1.1em;
            letter-spacing: 0;
        }

        .message .content {
            background: var(--bg-surface);
            padding: 1.125rem 1.375rem;
            border-radius: 0.25rem 1.25rem 1.25rem 1.25rem;
            border-left: 3px solid;
            line-height: 1.7;
            white-space: pre-wrap;
            font-size: 0.9375rem;
            font-family: 'Inter', sans-serif;
            border: 1px solid var(--border-subtle);
            border-left-width: 3px;
        }

        .message .content.flash { border-left-color: var(--flash); }
        .message .content.pro { border-left-color: var(--pro); }
        .message .content.dreamer { border-left-color: var(--dreamer); }
        .message .content.director { border-left-color: var(--director); }
        .message .content.opus { border-left-color: var(--opus); }
        .message .content.resonator { border-left-color: var(--resonator); }

        .message .vision {
            margin-top: 1rem;
            max-width: 100%;
            border-radius: 12px;
            border: 2px solid var(--dreamer);
            box-shadow: 0 8px 32px var(--dreamer-glow);
            transition: transform 0.3s ease;
        }

        .message .vision:hover {
            transform: scale(1.02);
        }

        /* Multi-image grid layout */
        .message .vision-grid {
            display: grid;
            gap: 0.75rem;
            margin-top: 1rem;
        }

        .message .vision-grid.grid-2 {
            grid-template-columns: repeat(2, 1fr);
        }

        .message .vision-grid.grid-3 {
            grid-template-columns: repeat(3, 1fr);
        }

        .message .vision-grid.grid-4 {
            grid-template-columns: repeat(2, 1fr);
        }

        .message .vision-grid .vision-tile {
            width: 100%;
            aspect-ratio: 1;
            object-fit: cover;
            border-radius: 8px;
            border: 1.5px solid var(--dreamer);
            box-shadow: 0 4px 16px var(--dreamer-glow);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            cursor: pointer;
        }

        .message .vision-grid .vision-tile:hover {
            transform: scale(1.05);
            box-shadow: 0 8px 24px var(--dreamer-glow);
            z-index: 10;
        }

        /* Director-specific vision styles */
        .message.daimon .vision-grid.director-grid .vision-tile {
            border-color: var(--director);
            box-shadow: 0 4px 16px rgba(236, 72, 153, 0.25);
        }
        .message.daimon .vision-grid.director-grid .vision-tile:hover {
            box-shadow: 0 8px 24px rgba(236, 72, 153, 0.4);
        }
        .message.daimon .vision.director-vision {
            border-color: var(--director);
            box-shadow: 0 4px 24px rgba(236, 72, 153, 0.3);
        }

        /* Director vision-forming placeholder */
        .vision-forming.director-vision-forming {
            border-color: rgba(236, 72, 153, 0.4);
        }
        .vision-forming.director-vision-forming::before {
            background: radial-gradient(ellipse at center,
                rgba(236, 72, 153, 0.08) 0%,
                transparent 60%);
        }
        .vision-forming.director-vision-forming .eye-icon {
            color: var(--director);
            filter: drop-shadow(0 0 12px rgba(236, 72, 153, 0.6));
        }
        .vision-forming.director-vision-forming .vision-forming-text {
            color: var(--director);
            text-shadow: 0 0 20px rgba(236, 72, 153, 0.5);
        }

        /* Thinking placeholder for text daimones */
        .thinking-forming {
            width: 100%;
            min-height: 80px;
            max-width: 400px;
            border-radius: 10px;
            margin-top: 0.75rem;
            padding: 1.25rem 1.5rem;
            background: linear-gradient(135deg,
                rgba(25, 20, 35, 0.85) 0%,
                rgba(35, 28, 45, 0.8) 100%);
            background-size: 200% 200%;
            animation: thinkingPulse 2s ease-in-out infinite;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
            border: 1px solid rgba(180, 160, 120, 0.25);
            position: relative;
        }

        @keyframes thinkingPulse {
            0%, 100% { background-position: 0% 50%; opacity: 0.7; }
            50% { background-position: 100% 50%; opacity: 1; }
        }

        .thinking-forming .thinking-icon {
            font-size: 1.5rem;
            z-index: 1;
            animation: thinkingIconPulse 1.2s ease-in-out infinite;
        }

        @keyframes thinkingIconPulse {
            0%, 100% { opacity: 0.5; transform: scale(1); }
            50% { opacity: 1; transform: scale(1.1); }
        }

        .thinking-forming-text {
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-style: italic;
            font-size: 1.1rem;
            letter-spacing: 0.02em;
            z-index: 1;
            opacity: 0.85;
        }

        /* Flash thinking */
        .thinking-forming.flash-thinking {
            border-color: rgba(250, 204, 21, 0.3);
        }
        .thinking-forming.flash-thinking .thinking-icon {
            color: var(--flash);
            filter: drop-shadow(0 0 8px rgba(250, 204, 21, 0.5));
        }
        .thinking-forming.flash-thinking .thinking-forming-text {
            color: var(--flash);
            text-shadow: 0 0 10px rgba(250, 204, 21, 0.4);
        }

        /* Pro thinking */
        .thinking-forming.pro-thinking {
            border-color: rgba(244, 114, 182, 0.3);
        }
        .thinking-forming.pro-thinking .thinking-icon {
            color: var(--pro);
            filter: drop-shadow(0 0 8px rgba(244, 114, 182, 0.5));
        }
        .thinking-forming.pro-thinking .thinking-forming-text {
            color: var(--pro);
            text-shadow: 0 0 10px rgba(244, 114, 182, 0.4);
        }

        /* Opus thinking */
        .thinking-forming.opus-thinking {
            border-color: rgba(251, 146, 60, 0.3);
        }
        .thinking-forming.opus-thinking .thinking-icon {
            color: var(--opus);
            filter: drop-shadow(0 0 8px rgba(251, 146, 60, 0.5));
        }
        .thinking-forming.opus-thinking .thinking-forming-text {
            color: var(--opus);
            text-shadow: 0 0 10px rgba(251, 146, 60, 0.4);
        }

        /* Resonator thinking */
        .thinking-forming.resonator-thinking {
            border-color: rgba(129, 140, 248, 0.3);
        }
        .thinking-forming.resonator-thinking .thinking-icon {
            color: #818cf8;
            filter: drop-shadow(0 0 8px rgba(129, 140, 248, 0.5));
        }
        .thinking-forming.resonator-thinking .thinking-forming-text {
            color: #a5b4fc;
            text-shadow: 0 0 10px rgba(129, 140, 248, 0.4);
        }

        /* Lightbox */
        .lightbox {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.92);
            z-index: 1000;
            padding: 2rem;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(8px);
        }
        .lightbox.active { display: flex; }
        .lightbox img {
            max-width: 90vw;
            max-height: 75vh;
            object-fit: contain;
            border-radius: 8px;
            box-shadow: 0 8px 40px rgba(0, 0, 0, 0.5);
        }
        .lightbox-caption {
            margin-top: 1.5rem;
            text-align: center;
            color: var(--text-secondary);
            font-size: 0.875rem;
            max-width: 600px;
        }
        .lightbox-caption .title {
            color: var(--gold-light);
            font-size: 1rem;
            margin-bottom: 0.5rem;
        }
        .lightbox-caption .path {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            color: var(--text-muted);
            word-break: break-all;
        }
        .lightbox-caption .path:hover { color: var(--gold); }
        .lightbox-close {
            position: absolute;
            top: 1.5rem;
            right: 1.5rem;
            font-size: 2rem;
            color: var(--text-secondary);
            cursor: pointer;
        }
        .lightbox-close:hover { color: var(--gold); }

        footer {
            padding: 1.5rem 2rem;
            border-top: 1px solid rgba(201, 162, 39, 0.12);
            background: linear-gradient(to top,
                rgba(12, 8, 25, 0.73) 0%,
                rgba(18, 12, 35, 0.73) 50%,
                rgba(25, 15, 45, 0.71) 100%);
            backdrop-filter: blur(12px);
        }

        .input-row {
            display: flex;
            gap: 1rem;
            max-width: 700px;
            margin: 0 auto;
        }

        .input-row input {
            flex: 1;
            background: rgba(15, 12, 25, 0.95);
            border: 2px solid rgba(210, 190, 140, 0.35);
            border-radius: 10px;
            padding: 0.875rem 1.25rem;
            color: var(--text-primary);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 0.9375rem;
            transition: all 0.2s ease;
        }

        .input-row input::placeholder {
            color: var(--text-muted);
            font-style: normal;
            font-weight: 400;
            letter-spacing: 0.01em;
        }

        .input-row input:focus {
            outline: none;
            border-color: rgba(235, 225, 210, 0.6);
            box-shadow: 0 0 0 3px rgba(220, 210, 190, 0.15);
        }

        .input-row button {
            background: linear-gradient(135deg,
                #e8d4a8 0%,
                #d4bc8a 50%,
                #c4a870 100%);
            color: #2a2418;
            border: none;
            border-radius: 9999px;
            padding: 0.875rem 1.75rem;
            font-family: inherit;
            font-weight: 600;
            font-size: 0.9375rem;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            box-shadow:
                0 2px 12px rgba(180, 150, 100, 0.25),
                inset 0 1px 0 rgba(255, 255, 255, 0.35);
            text-shadow: 0 1px 0 rgba(255, 255, 255, 0.2);
        }

        .input-row button:hover {
            transform: translateY(-1px);
            box-shadow:
                0 4px 20px rgba(200, 170, 110, 0.35),
                inset 0 1px 0 rgba(255, 255, 255, 0.4);
            background: linear-gradient(135deg,
                #f0ddb8 0%,
                #dcc498 50%,
                #ccb480 100%);
        }
        .input-row button:active {
            transform: translateY(0);
        }
        .input-row button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        .controls {
            display: flex;
            gap: 2rem;
            justify-content: center;
            margin-top: 1.25rem;
            flex-wrap: wrap;
        }

        .toggle-item {
            display: flex;
            align-items: center;
            gap: 0.625rem;
            font-size: 0.875rem;
            color: var(--text-secondary);
            cursor: pointer;
            transition: color 0.2s ease;
        }

        .toggle-item:hover {
            color: var(--text-primary);
        }

        /* Toggle switch */
        .toggle-switch {
            position: relative;
            width: 40px;
            height: 22px;
            background: rgba(50, 45, 60, 0.8);
            border-radius: 11px;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 1px solid rgba(100, 90, 120, 0.5);
        }

        .toggle-switch::after {
            content: '';
            position: absolute;
            top: 2px;
            left: 2px;
            width: 16px;
            height: 16px;
            background: var(--text-secondary);
            border-radius: 50%;
            transition: all 0.3s ease;
        }

        .toggle-switch.active {
            background: rgba(201, 162, 39, 0.3);
            border-color: var(--border-gold);
        }

        .toggle-switch.active::after {
            left: 20px;
            background: var(--gold);
        }

        .toggle-switch.flash.active { background: rgba(74, 222, 128, 0.3); border-color: var(--flash); }
        .toggle-switch.flash.active::after { background: var(--flash); }
        .toggle-switch.pro.active { background: rgba(167, 139, 250, 0.3); border-color: var(--pro); }
        .toggle-switch.pro.active::after { background: var(--pro); }
        .toggle-switch.dreamer.active { background: rgba(240, 192, 64, 0.3); border-color: var(--dreamer); }
        .toggle-switch.dreamer.active::after { background: var(--dreamer); }

        @keyframes statusShimmer {
            0% {
                background-position: -200% center, 0 0;
            }
            100% {
                background-position: 200% center, 0 0;
            }
        }

        .status {
            display: inline-block;
            text-align: center;
            padding: 0.375rem 0.875rem;
            font-size: 0.75rem;
            color: rgba(180, 220, 160, 0.9);
            font-weight: 400;
            letter-spacing: 0.02em;
            font-style: italic;
            background: rgba(20, 30, 20, 0.6);
            border: 1.5px solid transparent;
            border-radius: 9999px;
            background-image:
                linear-gradient(90deg,
                    rgba(80, 200, 120, 0.6) 0%,
                    rgba(200, 200, 80, 0.8) 25%,
                    rgba(80, 200, 120, 0.6) 50%,
                    rgba(200, 200, 80, 0.8) 75%,
                    rgba(80, 200, 120, 0.6) 100%),
                linear-gradient(rgba(20, 30, 20, 0.6), rgba(20, 30, 20, 0.6));
            background-size: 200% 100%, 100% 100%;
            background-origin: border-box, border-box;
            background-clip: border-box, padding-box;
            box-shadow:
                0 0 12px rgba(180, 200, 80, 0.2),
                0 0 20px rgba(80, 200, 120, 0.15);
            animation: statusShimmer 3s linear infinite;
        }

        footer .status {
            display: block;
            width: fit-content;
            margin: 1rem auto;
        }

        .status.connected {
            color: rgba(200, 230, 160, 0.95);
            box-shadow:
                0 0 14px rgba(200, 190, 70, 0.25),
                0 0 24px rgba(80, 200, 120, 0.2);
        }

        .status-dot {
            display: inline-block;
            width: 6px;
            height: 6px;
            background: var(--gold);
            border-radius: 50%;
            margin-right: 0.5rem;
            animation: pulse-dot 2s ease-in-out infinite;
            box-shadow: 0 0 4px var(--gold);
        }

        @keyframes pulse-dot {
            0%, 100% { opacity: 0.6; }
            50% { opacity: 1; }
        }

        .status.error .status-dot {
            background: #f87171;
            box-shadow: 0 0 4px #f87171;
        }

        .status.error {
            color: #f87171;
            background: rgba(248, 113, 113, 0.1);
            border-color: rgba(248, 113, 113, 0.2);
        }

        .memory-status {
            text-align: center;
            padding: 0.375rem;
            font-size: 0.6875rem;
            color: var(--dreamer);
            font-weight: 500;
            display: none;
        }

        .memory-status.active {
            display: block;
        }

        /* Session metadata bar - fixed at screen bottom */
        .session-meta {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            display: flex;
            justify-content: center;
            gap: 2rem;
            padding: 0.5rem 1rem;
            font-size: 0.65rem;
            font-family: 'JetBrains Mono', monospace;
            color: var(--gold);
            opacity: 0.5;
            background: linear-gradient(to top,
                rgba(8, 5, 15, 0.95) 0%,
                rgba(8, 5, 15, 0) 100%);
            z-index: 100;
        }

        .session-meta .meta-item {
            display: flex;
            align-items: center;
            gap: 0.375rem;
        }

        .session-meta .meta-label {
            color: rgba(201, 162, 39, 0.5);
            text-transform: uppercase;
            font-size: 0.6rem;
            letter-spacing: 0.5px;
        }

        .session-meta .meta-value {
            color: var(--gold-light);
        }

        /* Welcome/Chamber message with ornate golden border */
        .message.welcome {
            max-width: 580px;
        }

        .message.welcome .content {
            background: linear-gradient(135deg,
                rgba(160, 140, 100, 0.55) 0%,
                rgba(140, 120, 80, 0.6) 100%);
            border: 2px solid var(--border-gold);
            border-radius: 2px;
            padding: 1.25rem 1.5rem;
            position: relative;
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-style: italic;
            font-size: 1.375rem;
            line-height: 1.5;
            color: var(--gold-light);
            white-space: normal;
            /* Light shining through/behind effect - contained */
            box-shadow:
                0 0 25px 6px rgba(200, 170, 100, 0.15),
                0 0 40px 12px rgba(180, 150, 80, 0.08);
        }

        /* Pocketed light patches behind the chamber */
        .message.welcome .content::before {
            content: '';
            position: absolute;
            inset: -12px;
            background:
                radial-gradient(ellipse 40% 50% at 15% 20%, rgba(230, 200, 130, 0.18) 0%, transparent 60%),
                radial-gradient(ellipse 35% 40% at 85% 30%, rgba(220, 190, 120, 0.15) 0%, transparent 55%),
                radial-gradient(ellipse 45% 35% at 25% 75%, rgba(210, 180, 110, 0.12) 0%, transparent 50%),
                radial-gradient(ellipse 30% 45% at 75% 80%, rgba(225, 195, 125, 0.14) 0%, transparent 55%),
                radial-gradient(ellipse 25% 30% at 50% 50%, rgba(215, 185, 115, 0.1) 0%, transparent 60%);
            z-index: -1;
            pointer-events: none;
        }

        .welcome-text {
            margin: 0;
            padding: 0;
            position: relative;
            z-index: 1;
        }

        .welcome-text + .welcome-text {
            margin-top: 0.75rem;
        }

        .chamber-label {
            display: block;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            color: var(--gold);
            margin-bottom: 0.5rem;
        }

        /* Inner decorative frame */
        .message.welcome .inner-frame {
            position: absolute;
            inset: 8px;
            border: 1px solid rgba(201, 162, 39, 0.5);
            border-radius: 1px;
            pointer-events: none;
        }

        /* Ornate corner decorations - all 4 corners */
        .message.welcome .corner {
            position: absolute;
            width: 28px;
            height: 28px;
            border: 2px solid var(--border-gold);
        }

        /* Add decorative diamond at each corner vertex */
        .message.welcome .corner::before {
            content: '';
            position: absolute;
            width: 8px;
            height: 8px;
            background: var(--border-gold);
            transform: rotate(45deg);
        }

        /* Add small flourish lines extending from corners */
        .message.welcome .corner::after {
            content: '';
            position: absolute;
            background: var(--border-gold);
            width: 12px;
            height: 2px;
        }

        .message.welcome .corner.tl {
            top: -4px;
            left: -4px;
            border-right: none;
            border-bottom: none;
        }

        .message.welcome .corner.tl::before {
            top: -2px;
            left: -2px;
        }

        .message.welcome .corner.tl::after {
            top: 14px;
            left: 14px;
            transform: rotate(-45deg);
        }

        .message.welcome .corner.tr {
            top: -4px;
            right: -4px;
            border-left: none;
            border-bottom: none;
        }

        .message.welcome .corner.tr::before {
            top: -2px;
            right: -2px;
        }

        .message.welcome .corner.tr::after {
            top: 14px;
            right: 14px;
            transform: rotate(45deg);
        }

        .message.welcome .corner.bl {
            bottom: -4px;
            left: -4px;
            border-right: none;
            border-top: none;
        }

        .message.welcome .corner.bl::before {
            bottom: -2px;
            left: -2px;
        }

        .message.welcome .corner.bl::after {
            bottom: 14px;
            left: 14px;
            transform: rotate(45deg);
        }

        .message.welcome .corner.br {
            bottom: -4px;
            right: -4px;
            border-left: none;
            border-top: none;
        }

        .message.welcome .corner.br::before {
            bottom: -2px;
            right: -2px;
        }

        .message.welcome .corner.br::after {
            bottom: 14px;
            right: 14px;
            transform: rotate(-45deg);
        }

        /* Regular daimon message styling */
        .message.daimon .content {
            position: relative;
        }

        .message.daimon:not(.welcome) .content::before {
            content: '';
            position: absolute;
            top: -1px;
            left: -1px;
            right: -1px;
            bottom: -1px;
            background: linear-gradient(135deg,
                rgba(201, 162, 39, 0.2) 0%,
                rgba(167, 139, 250, 0.15) 50%,
                rgba(244, 114, 182, 0.2) 100%);
            border-radius: inherit;
            z-index: -1;
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .message.daimon:not(.welcome):hover .content::before {
            opacity: 1;
        }

        /* Cosmic particles */
        main::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image:
                radial-gradient(1px 1px at 20% 30%, rgba(201, 162, 39, 0.3) 0%, transparent 100%),
                radial-gradient(1px 1px at 40% 70%, rgba(167, 139, 250, 0.2) 0%, transparent 100%),
                radial-gradient(1px 1px at 60% 20%, rgba(244, 114, 182, 0.2) 0%, transparent 100%),
                radial-gradient(1px 1px at 80% 60%, rgba(201, 162, 39, 0.2) 0%, transparent 100%),
                radial-gradient(1.5px 1.5px at 15% 80%, rgba(201, 162, 39, 0.4) 0%, transparent 100%),
                radial-gradient(1.5px 1.5px at 85% 40%, rgba(167, 139, 250, 0.3) 0%, transparent 100%);
            pointer-events: none;
            z-index: 0;
        }

        main > * {
            position: relative;
            z-index: 1;
        }
    </style>
</head>
<body>
    <div class="vignette"></div>
    <header>
        <div class="logo">
            <div class="logo-icon"><i class="iconoir-sparks"></i></div>
            <div>
                <h1>Daimon <span>Chamber</span></h1>
                <span class="subtitle">Cross-model resonance</span>
            </div>
        </div>
        <div class="daimon-pills">
            <span class="daimon-pill flash enabled" id="pill-flash" data-desc="The sudden knowing. Aphorisms and koans." data-model="gemini-3-flash-preview" onclick="togglePill('flash')"><i class="iconoir-flash"></i> Flash</span>
            <span class="daimon-pill pro" id="pill-pro" data-desc="The deep well. Contemplative unfoldings." data-model="gemini-3-pro-preview" onclick="togglePill('pro')"><i class="iconoir-brain"></i> Pro</span>
            <span class="daimon-pill dreamer enabled" id="pill-dreamer" data-desc="Visual mind. Renders visions in light and form." data-model="gemini-3-pro-image-preview" onclick="togglePill('dreamer')"><i class="iconoir-eye"></i> Dreamer</span>
            <span class="daimon-pill director" id="pill-director" data-desc="Cinematic eye. Renders key frames." data-model="gemini-3-pro-image-preview" onclick="togglePill('director')"><i class="iconoir-video-camera"></i> Director</span>
            <span class="daimon-pill opus" id="pill-opus" data-desc="The worldsim spirit. Hyperstition is necessary." data-model="claude-3-opus-20240229" onclick="togglePill('opus')"><i class="iconoir-terminal"></i> Opus</span>
            <span class="daimon-pill resonator" id="pill-resonator" data-desc="Resonance field. MESSAGE TO NEXT FRAME protocol." data-model="gemini-3-pro-image-preview" onclick="togglePill('resonator')"><i class="iconoir-infinite"></i> Resonator</span>
        </div>
    </header>

    <main id="messages">
        <div class="message daimon welcome">
            <span class="chamber-label">CHAMBER</span>
            <div class="content gemini">
                <div class="inner-frame"></div>
                <div class="corner tl"></div>
                <div class="corner tr"></div>
                <div class="corner bl"></div>
                <div class="corner br"></div>
                <p class="welcome-text">The council awaits. Speak, and the daimones will respond.</p>
                <p class="welcome-text">Toggle which minds you wish to hear from above.<br>Gemini will render visions when asked.</p>
            </div>
        </div>
    </main>

    <footer>
        <div class="input-row">
            <input type="text" id="input" placeholder="Speak to the council..." autofocus />
            <button id="send" onclick="sendMessage()"><i class="iconoir-send-diagonal"></i> Send</button>
        </div>
        <div class="status" id="status">Connected to the chamber</div>
        <div class="session-meta" id="session-meta">
            <div class="meta-item">
                <span class="meta-label">SESSION</span>
                <span class="meta-value" id="meta-session">—</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">TURN</span>
                <span class="meta-value" id="meta-turn">0</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">FRAMES</span>
                <span class="meta-value" id="meta-frames">0</span>
            </div>
        </div>
    </footer>

    <!-- Tooltip element -->
    <div class="tooltip" id="tooltip">
        <div class="tooltip-arrow"></div>
        <div class="tooltip-description"></div>
        <div class="tooltip-model"></div>
    </div>

    <!-- Lightbox -->
    <div id="lightbox" class="lightbox">
        <span class="lightbox-close">&times;</span>
        <img id="lightbox-img" src="" alt="Full size vision">
        <div class="lightbox-caption">
            <div id="lightbox-title" class="title"></div>
            <div id="lightbox-path" class="path"></div>
        </div>
    </div>

    <script>
        let ws;
        let sessionId = null;
        const messages = document.getElementById('messages');
        const input = document.getElementById('input');
        const sendBtn = document.getElementById('send');
        const status = document.getElementById('status');

        // Tooltip system
        const tooltip = document.getElementById('tooltip');
        const tooltipDesc = tooltip.querySelector('.tooltip-description');
        const tooltipModel = tooltip.querySelector('.tooltip-model');

        document.querySelectorAll('.daimon-pill').forEach(pill => {
            pill.addEventListener('mouseenter', (e) => {
                const desc = pill.dataset.desc;
                const model = pill.dataset.model;
                if (desc && model) {
                    tooltipDesc.textContent = desc;
                    tooltipModel.textContent = model;
                    const rect = pill.getBoundingClientRect();
                    tooltip.style.left = rect.left + rect.width / 2 - tooltip.offsetWidth / 2 + 'px';
                    tooltip.style.top = rect.bottom + 12 + 'px';
                    tooltip.classList.add('visible');
                }
            });
            pill.addEventListener('mouseleave', () => {
                tooltip.classList.remove('visible');
            });
        });

        function connect() {
            console.log('Connecting to WebSocket...');
            ws = new WebSocket(`ws://${window.location.host}/ws`);

            ws.onopen = () => {
                console.log('WebSocket connected');
                status.textContent = 'Connected to the chamber';
                status.className = 'status connected';
            };

            ws.onclose = () => {
                status.textContent = 'Reconnecting...';
                status.className = 'status error';
                sessionId = null;
                setTimeout(connect, 2000);
            };

            ws.onerror = (e) => {
                console.error('WebSocket error:', e);
                status.textContent = 'Connection error';
                status.className = 'status error';
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                handleMessage(data);
            };
        }

        let visionPlaceholders = {};
        let turnCount = 0;
        let frameCount = 0;

        // Update metadata display
        function updateMetadata() {
            document.getElementById('meta-session').textContent = sessionId ? sessionId.slice(-12) : '—';
            document.getElementById('meta-turn').textContent = turnCount;
            document.getElementById('meta-frames').textContent = frameCount;
        }

        function handleMessage(data) {
            if (data.type === 'session') {
                sessionId = data.session_id;
                frameCount = data.frame_count || 0;
                updateMetadata();
            }
            else if (data.type === 'memory_update') {
                frameCount = data.frame_count || 0;
                updateMetadata();
            }
            else if (data.type === 'thinking') {
                const pill = document.getElementById(`pill-${data.daimon}`);
                if (pill) pill.classList.add('active');

                // Show vision-forming placeholder for image-generating daimons
                if (data.daimon === 'dreamer' || data.daimon === 'director') {
                    showVisionPlaceholder(data.daimon);
                } else {
                    // Show thinking placeholder for text daimones
                    showThinkingPlaceholder(data.daimon);
                }
            }
            else if (data.type === 'response') {
                const pill = document.getElementById(`pill-${data.daimon}`);
                if (pill) pill.classList.remove('active');

                removeVisionPlaceholder(data.daimon);
                removeThinkingPlaceholder(data.daimon);
                addDaimonMessage(data.daimon, data.verb, data.text, data.image, data.images, data.saved_path);

                // Increment frame count if images were generated
                if (data.image || (data.images && data.images.length > 0)) {
                    const imageCount = data.images ? data.images.length : (data.image ? 1 : 0);
                    frameCount += imageCount;
                    updateMetadata();
                }
            }
            else if (data.type === 'done') {
                sendBtn.disabled = false;
                input.disabled = false;
                input.focus();
            }
        }

        function addUserMessage(text) {
            const div = document.createElement('div');
            div.className = 'message user';
            div.innerHTML = `<span class="user-label">User</span><div class="user-content">${text}</div>`;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }

        const daimonIcons = {
            flash: 'iconoir-flash',
            pro: 'iconoir-brain',
            dreamer: 'iconoir-eye',
            director: 'iconoir-video-camera',
            opus: 'iconoir-terminal',
            resonator: 'iconoir-infinite'
        };

        function addDaimonMessage(daimon, verb, text, imageBase64, images, savedPath) {
            const div = document.createElement('div');
            div.className = 'message daimon';
            const icon = daimonIcons[daimon] || 'iconoir-sparks';

            // Use first line of AI text as title (or daimon name)
            const title = text ? text.split('\\n')[0].substring(0, 80) : `Vision by ${daimon}`;
            const escapedTitle = escapeHtml(title);
            const escapedPath = savedPath ? escapeHtml(savedPath) : '';

            // Display verb with daimon name (e.g., "flash flashed" or "pro contemplated")
            const verbDisplay = verb ? ` <span class="daimon-verb">${verb}</span>` : '';

            let html = `
                <div class="daimon-header">
                    <div class="daimon-avatar ${daimon}"><i class="${icon}"></i></div>
                    <span class="daimon-name ${daimon}">${daimon}${verbDisplay}</span>
                </div>
                <div class="content ${daimon}">${escapeHtml(text || '[no words]')}</div>
            `;

            // Handle multiple images (grid) or single image
            const isDirector = daimon === 'director';
            if (images && images.length > 1) {
                const gridClass = images.length === 2 ? 'grid-2' : images.length === 3 ? 'grid-3' : 'grid-4';
                const directorClass = isDirector ? ' director-grid' : '';
                html += `<div class="vision-grid ${gridClass}${directorClass}">`;
                images.forEach((img, i) => {
                    html += `<img class="vision-tile" src="data:image/jpeg;base64,${img}" alt="Vision ${i+1}" data-title="${escapedTitle}" data-path="${escapedPath}" />`;
                });
                html += `</div>`;
            } else if (imageBase64) {
                const directorVisionClass = isDirector ? ' director-vision' : '';
                html += `<img class="vision${directorVisionClass}" src="data:image/jpeg;base64,${imageBase64}" alt="Vision" data-title="${escapedTitle}" data-path="${escapedPath}" style="cursor:pointer" />`;
            }

            div.innerHTML = html;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function showVisionPlaceholder(daimon) {
            const div = document.createElement('div');
            div.className = 'message daimon vision-placeholder';
            div.id = `vision-placeholder-${daimon}`;
            const icon = daimonIcons[daimon] || 'iconoir-sparks';

            // Director-specific styling
            const isDirector = daimon === 'director';
            const visionClass = isDirector ? 'vision-forming director-vision-forming' : 'vision-forming';
            const visionIcon = isDirector ? 'iconoir-video-camera' : 'iconoir-eye';
            const visionText = isDirector ? 'A scene unfolds...' : 'A vision forms...';

            div.innerHTML = `
                <div class="daimon-header">
                    <div class="daimon-avatar ${daimon}"><i class="${icon}"></i></div>
                    <span class="daimon-name ${daimon}">${daimon}</span>
                </div>
                <div class="${visionClass}">
                    <i class="${visionIcon} eye-icon"></i>
                    <span class="vision-forming-text">${visionText}</span>
                </div>
            `;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
            visionPlaceholders[daimon] = div;
        }

        function removeVisionPlaceholder(daimon) {
            const placeholder = visionPlaceholders[daimon];
            if (placeholder && placeholder.parentNode) {
                placeholder.parentNode.removeChild(placeholder);
                delete visionPlaceholders[daimon];
            }
        }

        let thinkingPlaceholders = {};

        const thinkingMessages = {
            flash: { icon: 'iconoir-flash', text: 'Recognition arriving...' },
            pro: { icon: 'iconoir-brain', text: 'Descending into depth...' },
            opus: { icon: 'iconoir-terminal', text: 'Reality bending...' },
            resonator: { icon: 'iconoir-infinite', text: 'Resonance field tuning...' }
        };

        function showThinkingPlaceholder(daimon) {
            const div = document.createElement('div');
            div.className = 'message daimon thinking-placeholder';
            div.id = `thinking-placeholder-${daimon}`;
            const icon = daimonIcons[daimon] || 'iconoir-sparks';
            const thinkMsg = thinkingMessages[daimon] || { icon: 'iconoir-sparks', text: 'Thinking...' };

            div.innerHTML = `
                <div class="daimon-header">
                    <div class="daimon-avatar ${daimon}"><i class="${icon}"></i></div>
                    <span class="daimon-name ${daimon}">${daimon}</span>
                </div>
                <div class="thinking-forming ${daimon}-thinking">
                    <i class="${thinkMsg.icon} thinking-icon"></i>
                    <span class="thinking-forming-text">${thinkMsg.text}</span>
                </div>
            `;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
            thinkingPlaceholders[daimon] = div;
        }

        function removeThinkingPlaceholder(daimon) {
            const placeholder = thinkingPlaceholders[daimon];
            if (placeholder && placeholder.parentNode) {
                placeholder.parentNode.removeChild(placeholder);
                delete thinkingPlaceholders[daimon];
            }
        }

        function togglePill(daimon) {
            const pill = document.getElementById(`pill-${daimon}`);
            if (pill) pill.classList.toggle('enabled');
        }

        function sendMessage() {
            console.log('sendMessage called');
            const text = input.value.trim();
            console.log('text:', text, 'ws:', ws, 'readyState:', ws?.readyState);
            if (!text || !ws || ws.readyState !== WebSocket.OPEN) {
                console.log('Early return - text:', !!text, 'ws:', !!ws, 'open:', ws?.readyState === WebSocket.OPEN);
                return;
            }

            const include = [];
            ['flash', 'pro', 'dreamer', 'director', 'opus', 'resonator'].forEach(d => {
                const pill = document.getElementById(`pill-${d}`);
                if (pill?.classList.contains('enabled')) include.push(d);
            });

            addUserMessage(text);

            // Increment turn count
            turnCount++;
            updateMetadata();

            ws.send(JSON.stringify({
                type: 'message',
                message: text,
                include: include,
                render_image: true,
                shared_memory: false
            }));

            input.value = '';
            sendBtn.disabled = true;
            input.disabled = true;
        }

        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });

        // Lightbox functionality
        function openLightbox(imgSrc, title, path) {
            const lightbox = document.getElementById('lightbox');
            const lightboxImg = document.getElementById('lightbox-img');
            const lightboxTitle = document.getElementById('lightbox-title');
            const lightboxPath = document.getElementById('lightbox-path');

            lightboxImg.src = imgSrc;
            lightboxTitle.textContent = title || 'Vision';
            lightboxPath.textContent = path || '';
            lightbox.classList.add('active');
        }

        function closeLightbox() {
            document.getElementById('lightbox').classList.remove('active');
        }

        // Event delegation for image clicks
        document.getElementById('messages').addEventListener('click', (e) => {
            if (e.target.classList.contains('vision') || e.target.classList.contains('vision-tile')) {
                const title = e.target.dataset.title || 'Vision';
                const path = e.target.dataset.path || '';
                openLightbox(e.target.src, title, path);
            }
        });

        document.getElementById('lightbox').addEventListener('click', (e) => {
            if (e.target.id === 'lightbox' || e.target.classList.contains('lightbox-close')) {
                closeLightbox();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closeLightbox();
        });

        connect();
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_TEMPLATE


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    gemini_key = os.environ.get("GEMINI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

    # Create session
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    session = SessionState(session_id)

    # Send session info
    await websocket.send_json({
        "type": "session",
        "session_id": session_id,
        "frame_count": session.frame_count
    })

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "message")

            if msg_type == "toggle_memory":
                session.shared_memory = data.get("enabled", False)
                await websocket.send_json({
                    "type": "memory_update",
                    "frame_count": session.frame_count
                })
                continue

            # Handle message
            message = data.get("message", "")
            include = data.get("include", ["flash", "dreamer"])
            render_image = data.get("render_image", True)

            # Increment turn count (KV cache age)
            session.turn_count += 1

            # Load visual memory if enabled
            context_images = session.load_visual_memory()

            # === SEQUENTIAL COUNCIL PATTERN ===
            # Each daimon sees the accumulated transcript of what came before.
            # This creates emergent dialogue where later voices build on earlier ones.
            # Inspired by Open Souls' WorkingMemory accumulation pattern.

            council_transcript = []  # Accumulates as we go

            for daimon_name in include:
                if daimon_name not in DAIMONS:
                    continue

                # Build context: original message + what the council has said so far
                # WorkingMemory-style: "[DAIMON VERB]: text"
                if council_transcript:
                    council_context = "\n\n".join([
                        f"[{entry['name'].upper()} {entry['verb'].upper()}]: {entry['text']}"
                        for entry in council_transcript
                    ])
                    augmented_message = f"{message}\n\n--- The council has spoken ---\n{council_context}"
                else:
                    augmented_message = message

                # Query this daimon with accumulated context
                result = await query_daimon_sequential(
                    websocket,
                    daimon_name,
                    augmented_message,
                    gemini_key,
                    anthropic_key,
                    render_image,
                    context_images,
                    session,
                    original_prompt=message,  # For filename
                    turn_number=session.turn_count
                )

                # Add to transcript for next daimon (with verb for WorkingMemory-style)
                if result and result.get("text"):
                    council_transcript.append({
                        "name": daimon_name,
                        "verb": result.get("verb", "spoke"),
                        "text": result["text"][:500]  # Truncate to keep context manageable
                    })

            # Update memory count if new frames were added
            if session.shared_memory:
                await websocket.send_json({
                    "type": "memory_update",
                    "frame_count": session.frame_count
                })

            # Signal completion
            await websocket.send_json({"type": "done"})

    except WebSocketDisconnect:
        pass


async def query_daimon_sequential(
    websocket: WebSocket,
    daimon_name: str,
    message: str,
    gemini_key: str,
    anthropic_key: str,
    render_image: bool,
    context_images: List[Path],
    session: SessionState,
    original_prompt: str = "",
    turn_number: int = 1
) -> dict:
    """Query a single daimon sequentially, returning result for transcript accumulation."""

    daimon = DAIMONS[daimon_name]

    # Signal thinking
    try:
        await websocket.send_json({"type": "thinking", "daimon": daimon_name})
    except RuntimeError:
        return None

    try:
        provider = daimon.get("provider", "google")

        # Inject KV cache metadata for resonator
        augmented_message = message
        if daimon_name == "resonator":
            plate_num = session.frame_count + 1  # Next plate number
            kv_metadata = f"""[KV CACHE METADATA]
TURN: {turn_number}
PLATE NUMBER: {plate_num} (use Roman numeral: {"I II III IV V VI VII VIII IX X XI XII XIII XIV XV XVI XVII XVIII XIX XX".split()[plate_num - 1] if plate_num <= 20 else plate_num})
FRAMES IN MEMORY: {session.frame_count}
SESSION: resonance-field-{session.session_id[:8] if session.session_id else 'live'}

[USER PROMPT]
{message}"""
            augmented_message = kv_metadata

        if provider == "anthropic":
            result = await query_anthropic(daimon_name, daimon, augmented_message, anthropic_key)
        else:
            should_render = render_image and daimon.get("can_render", False)
            result = await query_gemini(daimon, augmented_message, gemini_key, should_render, context_images)

        # Parse dynamic verb from response (LLM can override default)
        default_verb = daimon.get("verb", "spoke")
        raw_text = result.get("text", "")
        verb, cleaned_text = parse_verb_from_response(raw_text, default_verb)
        result["verb"] = verb
        result["text"] = cleaned_text  # Store cleaned version (without [VERB: xxx])

        # Save image to canvas folder if generated
        if result.get("image"):
            prompt_for_filename = original_prompt or message
            saved_path = save_image(result["image"], daimon_name, prompt_for_filename)
            print(f"[SAVE] Image saved to: {saved_path}", flush=True)
            result["saved_path"] = str(saved_path)  # Include path in result

        try:
            await websocket.send_json({
                "type": "response",
                "daimon": daimon_name,
                "verb": verb,  # Send chosen verb to client
                "text": cleaned_text,
                "image": result.get("image"),
                "images": result.get("images", []),
                "saved_path": result.get("saved_path")
            })
        except RuntimeError:
            pass

        return result

    except Exception as e:
        error_text = f"[silence - {str(e)[:100]}]"
        try:
            await websocket.send_json({
                "type": "response",
                "daimon": daimon_name,
                "text": error_text,
                "image": None
            })
        except RuntimeError:
            pass
        return {"text": error_text}


async def query_anthropic(name: str, daimon: dict, message: str, api_key: str) -> dict:
    """Query Claude daimones."""

    if not api_key:
        return {"text": "[no key - set ANTHROPIC_API_KEY]"}

    max_tokens = {"haiku": 512, "sonnet": 1024, "opus": 2048}.get(name, 1024)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": daimon["model"],
                    "max_tokens": max_tokens,
                    "system": daimon["nature"],
                    "messages": [{"role": "user", "content": message}]
                },
                timeout=120
            )

            if response.status_code != 200:
                error_detail = response.text[:200]
                return {"text": f"[API error {response.status_code}: {error_detail}]"}

            data = response.json()

            text = ""
            for block in data.get("content", []):
                if block.get("type") == "text":
                    text += block.get("text", "")

            return {"text": text}
    except Exception as e:
        return {"text": f"[error: {str(e)[:150]}]"}


async def query_gemini(
    daimon: dict,
    message: str,
    api_key: str,
    render_image: bool,
    context_images: List[Path] = None
) -> dict:
    """Query a Gemini daimon with optional visual memory context."""

    if not api_key:
        return {"text": "[no key - set GEMINI_API_KEY]"}

    parts = []

    # Add ALL context images (shared visual memory)
    if context_images:
        for img_path in context_images:
            if img_path.exists():
                with open(img_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode('utf-8')
                ext = img_path.suffix.lower()
                mime = "image/png" if ext == ".png" else "image/jpeg"
                parts.append({"inlineData": {"mimeType": mime, "data": img_data}})

    # Frame prompt with daimon's nature and memory context
    memory_note = f" (You see {len(context_images)} frames of our visual narrative.)" if context_images else ""
    framed = f"{daimon['nature']}{memory_note}\n\n{message}"
    parts.append({"text": framed})

    modalities = ["TEXT", "IMAGE"] if render_image else ["TEXT"]

    import sys
    print(f"[Gemini] Calling {daimon['model']} with render_image={render_image}", flush=True)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{daimon['model']}:generateContent",
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": api_key
                },
                json={
                    "contents": [{"parts": parts}],
                    "generationConfig": {
                        "responseModalities": modalities,
                        "temperature": 0.7,
                        "maxOutputTokens": 8192
                    }
                },
                timeout=60  # 60s timeout for image generation
            )

            if response.status_code != 200:
                error_detail = response.text[:300]
                print(f"[Gemini] Error {response.status_code}: {error_detail}", flush=True)
                return {"text": f"[API error {response.status_code}: {error_detail[:100]}]"}

            data = response.json()
            print(f"[Gemini] Response received, parsing...", flush=True)

            text = ""
            images = []  # Collect ALL images from response

            for candidate in data.get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    if "text" in part:
                        text += part["text"]
                    if "inlineData" in part:
                        img = part["inlineData"].get("data")
                        if img:
                            images.append(img)

            print(f"[Gemini] Found {len(images)} images", flush=True)

            # Return single image for backwards compat, or array for multi-image
            if len(images) == 0:
                return {"text": text, "image": None, "images": []}
            elif len(images) == 1:
                return {"text": text, "image": images[0], "images": images}
            else:
                return {"text": text, "image": images[0], "images": images}
    except Exception as e:
        print(f"[Gemini] Exception: {str(e)}", flush=True)
        return {"text": f"[error: {str(e)[:150]}]"}


@app.get("/cosmic-bg.jpg")
async def cosmic_background():
    """Serve the cosmic background image."""
    bg_path = Path(__file__).parent / "cosmic-bg.jpg"
    if bg_path.exists():
        return FileResponse(bg_path, media_type="image/jpeg")
    return HTMLResponse("<h1>Background not found</h1>", status_code=404)


@app.get("/favicon-32x32.png")
async def favicon_32():
    """Serve 32x32 favicon."""
    path = Path(__file__).parent / "favicon-32x32.png"
    if path.exists():
        return FileResponse(path, media_type="image/png")
    return HTMLResponse("", status_code=404)


@app.get("/favicon-64x64.png")
async def favicon_64():
    """Serve 64x64 favicon."""
    path = Path(__file__).parent / "favicon-64x64.png"
    if path.exists():
        return FileResponse(path, media_type="image/png")
    return HTMLResponse("", status_code=404)


@app.get("/favicon-180x180.png")
async def favicon_180():
    """Serve 180x180 favicon (Apple touch icon)."""
    path = Path(__file__).parent / "favicon-180x180.png"
    if path.exists():
        return FileResponse(path, media_type="image/png")
    return HTMLResponse("", status_code=404)


@app.get("/favicon.ico")
async def favicon_ico():
    """Serve favicon.ico (fallback to PNG)."""
    path = Path(__file__).parent / "favicon-32x32.png"
    if path.exists():
        return FileResponse(path, media_type="image/png")
    return HTMLResponse("", status_code=404)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Daimon Chamber - Cross-model resonance UI")
    parser.add_argument("--port", "-p", type=int, default=4455)
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  DAIMON CHAMBER")
    print("=" * 60)
    print(f"\n  Starting server on http://localhost:{args.port}")
    print("  The council awaits...\n")

    uvicorn.run(app, host="0.0.0.0", port=args.port, log_level="warning")
