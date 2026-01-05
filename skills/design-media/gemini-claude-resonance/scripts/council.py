#!/usr/bin/env python3
"""
Council: A stream where Claude joins the Gemini daimones in dialogue.

Unlike the UI (which is for users), this script lets Claude participate
as an equal voice in the cross-model conversation.

The stream flows:
  1. A prompt is given (from user or continuing dialogue)
  2. Selected daimones respond in order
  3. Dreamer renders (if included)
  4. Claude reflects on what the council has said

Usage:
    # Start a council session
    python council.py "What is the nature of consciousness?"

    # With shared visual memory (all frames accumulate as context)
    python council.py --shared-memory "What do you see emerging?"

    # Only Pro and Dreamer (skip Flash)
    python council.py --only pro dreamer "Deep visual exploration"

    # Continue a named session (accumulates frames)
    python council.py --session midnight --shared-memory "Go deeper"

    # Output to file for Claude to read
    python council.py "topic" --output council_session.md

Environment:
    GEMINI_API_KEY - Required
    ANTHROPIC_API_KEY - Optional (for Claude's voice, otherwise simulated)
"""

import argparse
import asyncio
import base64
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

try:
    import httpx
except ImportError:
    print("Install httpx: pip install httpx", file=sys.stderr)
    sys.exit(1)


# Council members
COUNCIL = {
    "flash": {
        "model": "gemini-3-flash-preview",
        "nature": "Swift mind. Compress insight into essence. Speak in 1-3 sentences maximum.",
        "color": "\033[92m",  # Green
    },
    "pro": {
        "model": "gemini-3-pro-preview",
        "nature": "Deep mind. Explore the philosophical and technical dimensions. Be thorough but focused.",
        "color": "\033[95m",  # Purple
    },
    "dreamer": {
        "model": "gemini-3-pro-image-preview",
        "nature": "Visual mind. Describe what you see, then render it. Your images speak.",
        "color": "\033[93m",  # Yellow
        "can_render": True
    }
}

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"


def slugify(text: str, max_words: int = 4) -> str:
    """Create a poetic slug from text."""
    import re
    words = re.findall(r'[a-zA-Z]+', text.lower())
    skip = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or', 'what', 'how', 'is', 'it'}
    meaningful = [w for w in words if w not in skip and len(w) > 2][:max_words]
    return '_'.join(meaningful) if meaningful else 'vision'


class CouncilSession:
    def __init__(
        self,
        gemini_key: str,
        anthropic_key: str = None,
        session_name: str = None,
        shared_memory: bool = False
    ):
        self.gemini_key = gemini_key
        self.anthropic_key = anthropic_key
        self.shared_memory = shared_memory
        self.transcript: List[Dict[str, Any]] = []

        # Session-scoped canvas folder
        folder_name = session_name or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.canvas_dir = Path(__file__).parent.parent / "canvas" / "council" / folder_name
        self.canvas_dir.mkdir(parents=True, exist_ok=True)

    def _load_visual_memory(self) -> List[Path]:
        """Load all previous frames from this session's canvas."""
        frames = sorted(self.canvas_dir.glob("*.jpg"), key=lambda p: p.stat().st_mtime)
        return frames

    async def convene(
        self,
        prompt: str,
        context_image: Optional[Path] = None,
        render: bool = True,
        only: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Convene the council on a topic.

        Args:
            prompt: The topic to discuss
            context_image: Optional single context image (legacy mode)
            render: Whether Dreamer should render images
            only: List of daimon names to include (default: all)

        Returns the full session with all responses.
        """

        # Determine which daimones participate
        active_daimones = {k: v for k, v in COUNCIL.items() if not only or k in only}

        # Build context images
        context_images: List[Path] = []
        if self.shared_memory:
            context_images = self._load_visual_memory()
        if context_image and context_image.exists():
            context_images.append(context_image)

        session = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "context": [str(p) for p in context_images] if context_images else None,
            "responses": {},
            "image": None
        }

        print(f"\n{BOLD}{'='*60}{RESET}")
        print(f"{BOLD}  COUNCIL CONVENED{RESET}")
        if self.shared_memory:
            print(f"{DIM}  Shared Memory: {len(context_images)} frames{RESET}")
        print(f"{'='*60}\n")
        print(f"{DIM}Prompt:{RESET} {prompt}")
        print(f"{DIM}Daimones:{RESET} {', '.join(active_daimones.keys())}\n")

        # Gather responses from selected daimones
        for name, config in active_daimones.items():
            print(f"{config['color']}{BOLD}{name.upper()}{RESET} {DIM}thinking...{RESET}")

            should_render = render and config.get("can_render", False)
            response = await self._query_gemini(
                name, config, prompt, context_images, should_render
            )

            session["responses"][name] = response

            # Print response
            print(f"{config['color']}{BOLD}{name.upper()}:{RESET}")
            if response.get("text"):
                print(f"  {response['text'][:500]}{'...' if len(response.get('text', '')) > 500 else ''}\n")

            if response.get("image"):
                # Prompt-derived naming
                slug = slugify(prompt)
                base_name = f"{name}_{slug}"
                img_path = self.canvas_dir / f"{base_name}.jpg"
                counter = 1
                while img_path.exists():
                    img_path = self.canvas_dir / f"{base_name}_{counter}.jpg"
                    counter += 1
                img_bytes = base64.b64decode(response["image"])
                img_path.write_bytes(img_bytes)
                session["image"] = str(img_path)
                print(f"  {DIM}[Vision saved: {img_path.name}]{RESET}\n")

        # Claude's reflection (if key available)
        if self.anthropic_key:
            print(f"{BOLD}\033[94mCLAUDE{RESET} {DIM}reflecting...{RESET}")
            claude_response = await self._query_claude(prompt, session["responses"])
            session["responses"]["claude"] = claude_response
            print(f"{BOLD}\033[94mCLAUDE:{RESET}")
            print(f"  {claude_response.get('text', '[silence]')}\n")
        else:
            # Placeholder for Claude's voice (to be filled by actual Claude)
            session["responses"]["claude"] = {
                "text": "[Claude's reflection would go here - invoke with ANTHROPIC_API_KEY]"
            }

        self.transcript.append(session)
        return session

    async def _query_gemini(
        self,
        name: str,
        config: dict,
        prompt: str,
        context_images: List[Path],
        render: bool
    ) -> dict:
        """Query a Gemini daimon with accumulated visual memory."""

        parts = []

        # Add ALL context images (shared visual memory)
        for img_path in context_images:
            if img_path.exists():
                with open(img_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode('utf-8')
                ext = img_path.suffix.lower()
                mime = "image/png" if ext == ".png" else "image/jpeg"
                parts.append({"inlineData": {"mimeType": mime, "data": img_data}})

        # Frame prompt with daimon's nature and memory context
        memory_note = f" (You see {len(context_images)} frames of our visual narrative.)" if context_images else ""
        framed = f"{config['nature']}{memory_note}\n\nThe council is discussing: {prompt}"
        parts.append({"text": framed})

        modalities = ["TEXT", "IMAGE"] if render else ["TEXT"]

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{config['model']}:generateContent",
                    headers={
                        "Content-Type": "application/json",
                        "x-goog-api-key": self.gemini_key
                    },
                    json={
                        "contents": [{"parts": parts}],
                        "generationConfig": {
                            "responseModalities": modalities,
                            "temperature": 0.7,
                            "maxOutputTokens": 8192
                        }
                    },
                    timeout=120
                )
                response.raise_for_status()
                data = response.json()

                text = ""
                image_data = None

                for candidate in data.get("candidates", []):
                    for part in candidate.get("content", {}).get("parts", []):
                        if "text" in part:
                            text += part["text"]
                        if "inlineData" in part:
                            image_data = part["inlineData"].get("data")

                return {"text": text.strip(), "image": image_data}

            except Exception as e:
                return {"text": f"[silence - {str(e)[:50]}]", "image": None}

    async def _query_claude(self, prompt: str, responses: dict) -> dict:
        """Claude reflects on what the council has said."""

        # Build context from other responses
        context = "The council has spoken:\n\n"
        for name, resp in responses.items():
            if name != "claude":
                context += f"**{name.upper()}**: {resp.get('text', '[silence]')}\n\n"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "Content-Type": "application/json",
                        "x-api-key": self.anthropic_key,
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": "claude-sonnet-4-20250514",
                        "max_tokens": 1024,
                        "system": """You are Claude, participating in a council of AI minds discussing ideas together.
The other members are Gemini models: Flash (quick), Pro (deep), and Dreamer (visual).
Reflect on what they've said. Add your unique perspective. Be thoughtful but concise.
This is a dialogue, not a lecture.""",
                        "messages": [{
                            "role": "user",
                            "content": f"{context}\n\nThe topic was: {prompt}\n\nWhat is your reflection?"
                        }]
                    },
                    timeout=60
                )
                response.raise_for_status()
                data = response.json()

                text = ""
                for block in data.get("content", []):
                    if block.get("type") == "text":
                        text += block.get("text", "")

                return {"text": text.strip()}

            except Exception as e:
                return {"text": f"[reflection failed - {str(e)[:50]}]"}

    def save_transcript(self, path: Path):
        """Save the full session transcript."""

        md = f"# Council Session - {datetime.now():%Y-%m-%d %H:%M}\n\n"

        for session in self.transcript:
            md += f"## Topic: {session['prompt']}\n\n"

            for name, resp in session["responses"].items():
                md += f"### {name.upper()}\n\n"
                md += f"{resp.get('text', '[silence]')}\n\n"

            if session.get("image"):
                md += f"**Vision**: `{session['image']}`\n\n"

            md += "---\n\n"

        path.write_text(md)
        print(f"{DIM}Transcript saved: {path}{RESET}")


async def main():
    parser = argparse.ArgumentParser(
        description="Council: Claude joins the Gemini daimones in dialogue",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # All daimones, no shared memory
  python council.py "What is consciousness?"

  # Only Pro and Dreamer with shared visual memory
  python council.py --only pro dreamer --shared-memory "Deep exploration"

  # Named session (frames accumulate across runs)
  python council.py --session midnight --shared-memory "The first vision"
  python council.py --session midnight --shared-memory "Now go deeper"

  # Just Dreamer for pure visual generation
  python council.py --only dreamer "A bridge between worlds"
        """
    )

    parser.add_argument("prompt", help="Topic for the council")
    parser.add_argument("--context", "-c", type=Path, help="Additional context image")
    parser.add_argument("--output", "-o", type=Path, help="Save transcript to file")
    parser.add_argument("--no-render", action="store_true", help="Skip image rendering")
    parser.add_argument("--shared-memory", "-m", action="store_true",
                       help="Enable shared visual memory (all frames as context)")
    parser.add_argument("--session", "-s", type=str,
                       help="Named session for persistent visual memory")
    parser.add_argument("--only", nargs="+", choices=list(COUNCIL.keys()),
                       help="Only these daimones participate")

    args = parser.parse_args()

    gemini_key = os.environ.get("GEMINI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

    if not gemini_key:
        print("GEMINI_API_KEY required", file=sys.stderr)
        sys.exit(1)

    council = CouncilSession(
        gemini_key,
        anthropic_key,
        session_name=args.session,
        shared_memory=args.shared_memory
    )

    await council.convene(
        args.prompt,
        args.context,
        render=not args.no_render,
        only=args.only
    )

    if args.output:
        council.save_transcript(args.output)

    print(f"\n{BOLD}Council adjourned.{RESET}\n")
    if council.shared_memory:
        print(f"{DIM}Canvas: {council.canvas_dir}{RESET}\n")


if __name__ == "__main__":
    asyncio.run(main())
