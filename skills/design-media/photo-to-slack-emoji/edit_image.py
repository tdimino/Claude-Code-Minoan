#!/usr/bin/env python3
"""
Simple Image Editor using Gemini Nano Banana

Edit any image with natural language prompts.
"""

import sys
from pathlib import Path
from core.gemini_client import GeminiImageClient
from core.optimizer import optimize_for_slack
from PIL import Image
import io


def edit_image(input_path: str, output_path: str, edit_prompt: str, optimize: bool = False):
    """
    Edit an image using Gemini's nano banana model.

    Args:
        input_path: Path to input image
        output_path: Path to save edited image
        edit_prompt: Text description of the edit (e.g., "add a party hat")
        optimize: Whether to optimize for Slack (resize to 128x128, compress)
    """

    # Load input image
    with open(input_path, 'rb') as f:
        image_data = f.read()

    # Detect MIME type
    mime_type = "image/jpeg"
    if input_path.lower().endswith('.png'):
        mime_type = "image/png"
    elif input_path.lower().endswith('.webp'):
        mime_type = "image/webp"

    print(f"Editing image: {input_path}")
    print(f"Edit prompt: {edit_prompt}")

    # Edit image with Gemini
    client = GeminiImageClient()
    edited_data = client.edit_image(
        image_data=image_data,
        mime_type=mime_type,
        edit_prompt=edit_prompt
    )

    print(f"✓ Image edited successfully")

    # Optimize for Slack if requested
    if optimize:
        print("Optimizing for Slack...")
        img = Image.open(io.BytesIO(edited_data))

        # Resize to 128x128
        img = img.resize((128, 128), Image.Resampling.LANCZOS)

        # Save optimized
        output_buffer = io.BytesIO()
        img.save(output_buffer, format='PNG', optimize=True)
        edited_data = output_buffer.getvalue()

        file_size_kb = len(edited_data) / 1024
        print(f"✓ Optimized: {file_size_kb:.1f}KB")

        if file_size_kb > 64:
            print(f"⚠ Warning: File size exceeds Slack's 64KB limit")

    # Save output
    with open(output_path, 'wb') as f:
        f.write(edited_data)

    print(f"✓ Saved to: {output_path}")
    print(f"  Size: {len(edited_data) / 1024:.1f}KB")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python edit_image.py <input_image> <output_image> <edit_prompt> [--optimize]")
        print("\nExamples:")
        print("  python edit_image.py cat.jpg cat_with_hat.png 'add a party hat'")
        print("  python edit_image.py emoji.png emoji_sunglasses.png 'add sunglasses' --optimize")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    edit_prompt = sys.argv[3]
    optimize = "--optimize" in sys.argv

    edit_image(input_path, output_path, edit_prompt, optimize=optimize)
