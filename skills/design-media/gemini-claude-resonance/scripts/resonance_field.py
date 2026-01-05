#!/usr/bin/env python3
"""
Resonance Field: Cross-model visual memory with MESSAGE TO NEXT FRAME protocol.

Implements Danielle Fong's paradigm where each generated image contains:
- PLATE numbering (Roman numerals)
- MESSAGE TO NEXT FRAME (explicit continuity instructions)
- Embedded metadata (KV cache age, session ID)
- Victorian scientific illustration aesthetic

Usage:
    # Start a new resonance field session
    python resonance_field.py start "consciousness-study" "The nature of memory"

    # Continue with next plate
    python resonance_field.py continue <session-id> "What patterns emerge?"

    # Select element for zoom
    python resonance_field.py select <session-id> "golden gate bridge"

    # Zoom into selected element
    python resonance_field.py zoom <session-id> "Go deeper into the structure"

    # Inject new concept into the field
    python resonance_field.py inject <session-id> "Add consciousness as a node"

    # List all sessions
    python resonance_field.py list

Environment:
    GEMINI_API_KEY - Required for image generation
"""

import argparse
import base64
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    import requests
except ImportError:
    print("Install requests: pip install requests", file=sys.stderr)
    sys.exit(1)


# === Roman Numeral Conversion ===

ROMAN_NUMERALS = [
    (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
    (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
    (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')
]

def to_roman(n: int) -> str:
    """Convert integer to Roman numeral."""
    result = []
    for value, numeral in ROMAN_NUMERALS:
        count = n // value
        if count:
            result.append(numeral * count)
            n -= value * count
    return ''.join(result)


def from_roman(s: str) -> int:
    """Convert Roman numeral to integer."""
    roman_values = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    result = 0
    prev = 0
    for char in reversed(s.upper()):
        curr = roman_values.get(char, 0)
        if curr < prev:
            result -= curr
        else:
            result += curr
        prev = curr
    return result


# === Session Management ===

CANVAS_DIR = Path(__file__).parent.parent / "canvas" / "resonance"


def create_session(name: str) -> Dict[str, Any]:
    """Create a new resonance field session."""
    timestamp = int(time.time())
    session_id = f"{name}-live-{timestamp}"

    session = {
        "session_id": session_id,
        "session_name": name,
        "plate_number": 0,  # Will be 1 after first generation
        "kv_cache_age": 0,
        "table_of_contents": [],
        "selected_element": None,
        "created_at": datetime.now().isoformat()
    }

    # Create session directory
    session_dir = CANVAS_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    # Save session state
    save_session(session)

    return session


def load_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Load session state from .session.json."""
    session_file = CANVAS_DIR / session_id / ".session.json"
    if session_file.exists():
        return json.loads(session_file.read_text())
    return None


def save_session(session: Dict[str, Any]) -> None:
    """Save session state to .session.json."""
    session_dir = CANVAS_DIR / session["session_id"]
    session_dir.mkdir(parents=True, exist_ok=True)
    session_file = session_dir / ".session.json"
    session_file.write_text(json.dumps(session, indent=2))


def get_visual_memory(session: Dict[str, Any]) -> List[Path]:
    """Load all plate images from session directory."""
    session_dir = CANVAS_DIR / session["session_id"]
    if not session_dir.exists():
        return []
    # Sort by plate number (extracted from filename)
    plates = sorted(session_dir.glob("plate_*.jpg"), key=lambda p: p.stem)
    return plates


def list_sessions() -> List[Dict[str, Any]]:
    """List all resonance field sessions."""
    sessions = []
    if CANVAS_DIR.exists():
        for session_dir in CANVAS_DIR.iterdir():
            if session_dir.is_dir():
                session = load_session(session_dir.name)
                if session:
                    sessions.append(session)
    return sorted(sessions, key=lambda s: s.get("created_at", ""), reverse=True)


# === Prompt Construction ===

SYSTEM_PROMPT_TEMPLATE = """You are a visual mind creating scientific diagrams for a cross-model resonance experiment.

REQUIRED ELEMENTS IN EVERY IMAGE:

1. TITLE BOX at top: "PLATE {roman}: {session_name} - {subtitle}"
   Use an ornate banner or cartouche for the title.

2. SUBTITLE: A brief description of this frame's focus (e.g., "FIRST FRAME", "INTERNAL STRUCTURE")

3. LABELED ANNOTATIONS: Throughout the image, use scientific-style labels with leader lines.
   Point to key concepts, structures, and relationships.

4. METADATA PANEL (bottom left or right corner):
   - "KV CACHE AGE: TURN {kv_age}"
   - "SESSION ID: {session_id}"

5. MESSAGE TO NEXT FRAME (in a decorative footer box at bottom):
   Write explicit instructions for what Frame {next_plate} should explore or show.
   Format: MESSAGE TO NEXT FRAME: "Frame {next_plate} should show..."

{toc_instruction}

VISUAL STYLE:
- Victorian-era scientific illustration aesthetic (like Darwin's notebooks)
- Sepia/cream background tones with gold/amber accents
- Ornate borders and decorative frames around the image
- Da Vinci notebook quality - detailed, precise, technical
- Hand-drawn appearance with crosshatching and fine linework
- Callout boxes and leader lines for annotations

CONTINUITY:
- Reference previous frames explicitly when relevant
- Build on concepts introduced in earlier plates
- Maintain consistent visual language across the session
- The visual narrative should flow logically from frame to frame

{visual_memory_note}

Current prompt: {prompt}"""


def build_system_prompt(
    session: Dict[str, Any],
    subtitle: str,
    prompt: str,
    visual_memory: List[Path]
) -> str:
    """Build the system prompt with session context."""

    plate_num = session["plate_number"] + 1
    roman = to_roman(plate_num)
    next_plate = plate_num + 1

    # Table of contents instruction (for frames 4+)
    if plate_num >= 4:
        toc_instruction = """6. TABLE OF CONTENTS (for frames 4+):
   Include a small "Table of Contents" panel listing all previous plates:
   {toc}""".format(toc="\n   ".join(session["table_of_contents"]))
    else:
        toc_instruction = ""

    # Visual memory note
    if visual_memory:
        visual_memory_note = f"You see {len(visual_memory)} previous frames. Study them carefully. Continue the visual narrative."
    else:
        visual_memory_note = "This is the FIRST FRAME. Establish the visual language and conceptual foundation."

    return SYSTEM_PROMPT_TEMPLATE.format(
        roman=roman,
        session_name=session["session_name"].upper().replace("-", " "),
        subtitle=subtitle.upper(),
        kv_age=plate_num,
        session_id=session["session_id"],
        next_plate=next_plate,
        toc_instruction=toc_instruction,
        visual_memory_note=visual_memory_note,
        prompt=prompt
    )


def build_user_prompt(
    command: str,
    prompt: str,
    session: Dict[str, Any],
    visual_memory: List[Path]
) -> str:
    """Build the user prompt based on command type."""

    plate_num = session["plate_number"] + 1

    if command == "start":
        return f"""Create PLATE I - the FIRST FRAME of this resonance field session.

Topic: {prompt}

This is the foundation. Establish:
- The core concept or question
- The visual metaphor that will evolve
- The key elements to be explored
- A MESSAGE TO NEXT FRAME that sets up Frame II"""

    elif command == "continue":
        return f"""Create PLATE {to_roman(plate_num)} - continuing the resonance field.

The council asks: {prompt}

Build on the previous {len(visual_memory)} frames. Evolve the visual narrative.
Include a MESSAGE TO NEXT FRAME."""

    elif command == "zoom":
        selected = session.get("selected_element", "the previous frame")
        return f"""Create PLATE {to_roman(plate_num)} - ZOOMING INTO: {selected}

Instruction: {prompt}

Expand and explore the selected element in detail.
Reveal the deeper structure within.
Include a MESSAGE TO NEXT FRAME."""

    elif command == "inject":
        return f"""Create PLATE {to_roman(plate_num)} - CONCEPT INJECTION

New concept entering the field: {prompt}

Show how this new concept:
- Perturbs the existing structure
- Creates new connections
- Integrates with previous elements

Include a MESSAGE TO NEXT FRAME showing the new equilibrium."""

    else:
        return prompt


# === Gemini API ===

def generate_plate(
    session: Dict[str, Any],
    prompt: str,
    subtitle: str,
    command: str,
    gemini_key: str
) -> Dict[str, Any]:
    """Generate a new plate using Gemini."""

    visual_memory = get_visual_memory(session)

    # Build prompts
    system_prompt = build_system_prompt(session, subtitle, prompt, visual_memory)
    user_prompt = build_user_prompt(command, prompt, session, visual_memory)

    # Combine into full prompt
    full_prompt = f"{system_prompt}\n\n---\n\n{user_prompt}"

    # Build request parts
    parts = []

    # Add visual memory (previous plates)
    for img_path in visual_memory:
        with open(img_path, 'rb') as f:
            img_data = base64.b64encode(f.read()).decode('utf-8')
        parts.append({
            "inlineData": {"mimeType": "image/jpeg", "data": img_data}
        })

    # Add text prompt
    parts.append({"text": full_prompt})

    # API request
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": gemini_key
    }

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "temperature": 0.8,
            "maxOutputTokens": 8192
        }
    }

    endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent"

    response = requests.post(endpoint, headers=headers, json=payload, timeout=300)
    response.raise_for_status()
    data = response.json()

    # Extract text and image
    text = ""
    image_data = None

    for candidate in data.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            if "text" in part:
                text += part["text"]
            if "inlineData" in part:
                image_data = part["inlineData"].get("data")

    return {
        "text": text,
        "image": image_data
    }


# === Commands ===

def cmd_start(args, gemini_key: str) -> None:
    """Start a new resonance field session."""
    session = create_session(args.name)

    print(f"\n{'='*60}")
    print(f"  RESONANCE FIELD INITIALIZED")
    print(f"{'='*60}")
    print(f"  Session: {session['session_id']}")
    print(f"  Topic: {args.prompt}")
    print(f"\n  Generating PLATE I...")

    # Generate first plate
    result = generate_plate(
        session,
        args.prompt,
        "FIRST FRAME",
        "start",
        gemini_key
    )

    if result["image"]:
        # Update session
        session["plate_number"] = 1
        session["kv_cache_age"] = 1
        session["table_of_contents"].append(f"PLATE I: {args.prompt[:50]}")
        save_session(session)

        # Save image
        plate_path = CANVAS_DIR / session["session_id"] / "plate_001.jpg"
        plate_path.write_bytes(base64.b64decode(result["image"]))

        print(f"\n  PLATE I generated: {plate_path.name}")
        print(f"\n  Gemini speaks:")
        print(f"  {result['text'][:500]}{'...' if len(result['text']) > 500 else ''}")
    else:
        print(f"\n  [No image generated]")
        if result["text"]:
            print(f"  {result['text']}")

    print(f"\n  Session ID: {session['session_id']}")
    print(f"  Continue with: python resonance_field.py continue {session['session_id']} \"<prompt>\"")
    print()


def cmd_continue(args, gemini_key: str) -> None:
    """Continue a resonance field session."""
    session = load_session(args.session_id)
    if not session:
        print(f"Session not found: {args.session_id}", file=sys.stderr)
        sys.exit(1)

    plate_num = session["plate_number"] + 1
    roman = to_roman(plate_num)

    print(f"\n{'='*60}")
    print(f"  RESONANCE FIELD: {session['session_name'].upper()}")
    print(f"{'='*60}")
    print(f"  Session: {session['session_id']}")
    print(f"  KV Cache Age: {session['kv_cache_age']} turns")
    print(f"\n  Generating PLATE {roman}...")

    # Generate plate
    result = generate_plate(
        session,
        args.prompt,
        f"FRAME {plate_num}",
        "continue",
        gemini_key
    )

    if result["image"]:
        # Update session
        session["plate_number"] = plate_num
        session["kv_cache_age"] = plate_num
        session["table_of_contents"].append(f"PLATE {roman}: {args.prompt[:50]}")
        save_session(session)

        # Save image
        plate_path = CANVAS_DIR / session["session_id"] / f"plate_{plate_num:03d}.jpg"
        plate_path.write_bytes(base64.b64decode(result["image"]))

        print(f"\n  PLATE {roman} generated: {plate_path.name}")
        print(f"\n  Gemini speaks:")
        print(f"  {result['text'][:500]}{'...' if len(result['text']) > 500 else ''}")
    else:
        print(f"\n  [No image generated]")
        if result["text"]:
            print(f"  {result['text']}")

    print()


def cmd_select(args, gemini_key: str) -> None:
    """Select an element for zooming."""
    session = load_session(args.session_id)
    if not session:
        print(f"Session not found: {args.session_id}", file=sys.stderr)
        sys.exit(1)

    session["selected_element"] = args.element
    save_session(session)

    print(f"\n  Selected: \"{args.element}\"")
    print(f"  Zoom with: python resonance_field.py zoom {args.session_id} \"<instruction>\"")
    print()


def cmd_zoom(args, gemini_key: str) -> None:
    """Zoom into selected element."""
    session = load_session(args.session_id)
    if not session:
        print(f"Session not found: {args.session_id}", file=sys.stderr)
        sys.exit(1)

    if not session.get("selected_element"):
        print("No element selected. Use 'select' first.", file=sys.stderr)
        sys.exit(1)

    plate_num = session["plate_number"] + 1
    roman = to_roman(plate_num)
    selected = session["selected_element"]

    print(f"\n{'='*60}")
    print(f"  ZOOMING INTO: {selected}")
    print(f"{'='*60}")
    print(f"\n  Generating PLATE {roman}...")

    # Generate plate
    result = generate_plate(
        session,
        args.prompt,
        f"ZOOM - {selected[:30]}",
        "zoom",
        gemini_key
    )

    if result["image"]:
        # Update session
        session["plate_number"] = plate_num
        session["kv_cache_age"] = plate_num
        session["table_of_contents"].append(f"PLATE {roman}: ZOOM - {selected[:30]}")
        session["selected_element"] = None  # Clear selection
        save_session(session)

        # Save image
        plate_path = CANVAS_DIR / session["session_id"] / f"plate_{plate_num:03d}.jpg"
        plate_path.write_bytes(base64.b64decode(result["image"]))

        print(f"\n  PLATE {roman} generated: {plate_path.name}")
        print(f"\n  Gemini speaks:")
        print(f"  {result['text'][:500]}{'...' if len(result['text']) > 500 else ''}")
    else:
        print(f"\n  [No image generated]")
        if result["text"]:
            print(f"  {result['text']}")

    print()


def cmd_inject(args, gemini_key: str) -> None:
    """Inject a new concept into the field."""
    session = load_session(args.session_id)
    if not session:
        print(f"Session not found: {args.session_id}", file=sys.stderr)
        sys.exit(1)

    plate_num = session["plate_number"] + 1
    roman = to_roman(plate_num)

    print(f"\n{'='*60}")
    print(f"  INJECTING CONCEPT: {args.concept}")
    print(f"{'='*60}")
    print(f"\n  Generating PLATE {roman}...")

    # Generate plate
    result = generate_plate(
        session,
        args.concept,
        "CONCEPT INJECTION",
        "inject",
        gemini_key
    )

    if result["image"]:
        # Update session
        session["plate_number"] = plate_num
        session["kv_cache_age"] = plate_num
        session["table_of_contents"].append(f"PLATE {roman}: INJECT - {args.concept[:30]}")
        save_session(session)

        # Save image
        plate_path = CANVAS_DIR / session["session_id"] / f"plate_{plate_num:03d}.jpg"
        plate_path.write_bytes(base64.b64decode(result["image"]))

        print(f"\n  PLATE {roman} generated: {plate_path.name}")
        print(f"\n  Gemini speaks:")
        print(f"  {result['text'][:500]}{'...' if len(result['text']) > 500 else ''}")
    else:
        print(f"\n  [No image generated]")
        if result["text"]:
            print(f"  {result['text']}")

    print()


def cmd_list(args, gemini_key: str) -> None:
    """List all sessions."""
    sessions = list_sessions()

    if not sessions:
        print("\n  No resonance field sessions found.")
        print("  Start one with: python resonance_field.py start \"name\" \"prompt\"")
        print()
        return

    print(f"\n{'='*60}")
    print(f"  RESONANCE FIELD SESSIONS")
    print(f"{'='*60}")

    for s in sessions:
        plate_count = s.get("plate_number", 0)
        print(f"\n  {s['session_id']}")
        print(f"    Plates: {plate_count} | KV Age: {s.get('kv_cache_age', 0)}")
        print(f"    Created: {s.get('created_at', 'unknown')[:19]}")

    print()


# === Main ===

def main():
    parser = argparse.ArgumentParser(
        description="Resonance Field: Cross-model visual memory protocol",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  start     Start a new resonance field session
  continue  Continue with the next plate
  select    Select an element for zooming
  zoom      Zoom into the selected element
  inject    Inject a new concept into the field
  list      List all sessions

Examples:
  python resonance_field.py start "memory-study" "The nature of memory"
  python resonance_field.py continue memory-study-live-1704567890 "What patterns emerge?"
  python resonance_field.py select memory-study-live-1704567890 "golden gate bridge"
  python resonance_field.py zoom memory-study-live-1704567890 "Explore the cables"
  python resonance_field.py inject memory-study-live-1704567890 "consciousness"
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command")

    # start
    start_parser = subparsers.add_parser("start", help="Start a new session")
    start_parser.add_argument("name", help="Session name (e.g., 'memory-study')")
    start_parser.add_argument("prompt", help="Initial topic/prompt")

    # continue
    continue_parser = subparsers.add_parser("continue", help="Continue session")
    continue_parser.add_argument("session_id", help="Session ID")
    continue_parser.add_argument("prompt", help="Prompt for next plate")

    # select
    select_parser = subparsers.add_parser("select", help="Select element for zoom")
    select_parser.add_argument("session_id", help="Session ID")
    select_parser.add_argument("element", help="Element to select")

    # zoom
    zoom_parser = subparsers.add_parser("zoom", help="Zoom into selected element")
    zoom_parser.add_argument("session_id", help="Session ID")
    zoom_parser.add_argument("prompt", help="Zoom instruction")

    # inject
    inject_parser = subparsers.add_parser("inject", help="Inject new concept")
    inject_parser.add_argument("session_id", help="Session ID")
    inject_parser.add_argument("concept", help="Concept to inject")

    # list
    list_parser = subparsers.add_parser("list", help="List all sessions")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Get API key
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key and args.command != "list":
        print("GEMINI_API_KEY required", file=sys.stderr)
        sys.exit(1)

    # Dispatch command
    commands = {
        "start": cmd_start,
        "continue": cmd_continue,
        "select": cmd_select,
        "zoom": cmd_zoom,
        "inject": cmd_inject,
        "list": cmd_list,
    }

    commands[args.command](args, gemini_key)


if __name__ == "__main__":
    main()
