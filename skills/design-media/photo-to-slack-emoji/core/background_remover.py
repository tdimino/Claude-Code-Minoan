"""
Background Removal Utilities for Slack Emojis

Removes white (or other solid color) backgrounds from images using Pillow.
"""

from PIL import Image
from typing import Tuple, Optional
import numpy as np


def detect_background_color(image: Image.Image, sample_size: int = 10) -> Optional[Tuple[int, int, int]]:
    """
    Detect likely background color by sampling corner pixels.

    Args:
        image: PIL Image object
        sample_size: Number of pixels to sample from each corner

    Returns:
        RGB tuple of detected background color, or None if no consensus
    """
    img = image.convert("RGB")
    width, height = img.size

    # Sample corners
    corners = [
        (0, 0),  # Top-left
        (width - 1, 0),  # Top-right
        (0, height - 1),  # Bottom-left
        (width - 1, height - 1)  # Bottom-right
    ]

    # Collect corner pixel colors
    colors = []
    for x, y in corners:
        for dx in range(min(sample_size, width - x)):
            for dy in range(min(sample_size, height - y)):
                colors.append(img.getpixel((x + dx, y + dy)))

    # Check if most corners are similar (within 10 tolerance)
    if not colors:
        return None

    first_color = colors[0]
    similar_count = sum(
        1 for color in colors
        if all(abs(color[i] - first_color[i]) <= 10 for i in range(3))
    )

    # If >75% of sampled pixels are similar, it's likely a solid background
    if similar_count / len(colors) > 0.75:
        return first_color

    return None


def has_white_background(image: Image.Image, threshold: int = 240) -> bool:
    """
    Check if image likely has a white background.

    Args:
        image: PIL Image object
        threshold: Minimum RGB value to consider "white" (240 = nearly white)

    Returns:
        True if background appears to be white/near-white
    """
    bg_color = detect_background_color(image)
    if bg_color is None:
        return False

    # Check if detected background is white-ish
    return all(channel >= threshold for channel in bg_color)


def remove_white_background(
    image: Image.Image,
    fuzz: int = 10,
    target_color: Tuple[int, int, int] = (255, 255, 255)
) -> Image.Image:
    """
    Remove white (or specified color) background, making it transparent.

    Uses fuzz tolerance for near-matches, similar to ImageMagick's -fuzz parameter.

    Args:
        image: PIL Image object
        fuzz: Color tolerance (0-255). Higher = more aggressive removal.
              Default 10 ≈ ImageMagick's 4% fuzz
        target_color: RGB color to remove (default: white)

    Returns:
        New PIL Image with transparent background
    """
    # Convert to RGBA
    img = image.convert("RGBA")
    pixdata = img.load()

    width, height = img.size

    # Iterate through all pixels
    for y in range(height):
        for x in range(width):
            # Get current pixel RGB (ignore existing alpha)
            r, g, b, a = pixdata[x, y]

            # Check if pixel is within fuzz tolerance of target color
            should_remove = all(
                abs(pixdata[x, y][i] - target_color[i]) <= fuzz
                for i in range(3)  # Check RGB only
            )

            if should_remove:
                # Make transparent
                pixdata[x, y] = (r, g, b, 0)

    return img


def auto_remove_background(
    image: Image.Image,
    fuzz: int = 10
) -> Tuple[Image.Image, bool]:
    """
    Automatically detect and remove solid background if present.

    Args:
        image: PIL Image object
        fuzz: Color tolerance for removal

    Returns:
        Tuple of (processed_image, background_was_removed)
    """
    # Detect background color
    bg_color = detect_background_color(image)

    if bg_color is None:
        # No clear background detected, return original
        return image, False

    # Check if background is white-ish (most common case)
    is_white = all(channel >= 230 for channel in bg_color)

    if is_white:
        # Remove white background
        processed = remove_white_background(image, fuzz=fuzz, target_color=bg_color)
        return processed, True

    # For other solid backgrounds, user should specify explicitly
    return image, False


# Fuzz value reference (matching ImageMagick conventions):
# 0%   = 0   : Exact match only
# 2%   = 5   : Very tight tolerance
# 5%   = 13  : Moderate tolerance (good for clean backgrounds)
# 10%  = 26  : Aggressive removal
# 20%  = 51  : Very aggressive (may remove valid pixels)

FUZZ_PRESETS = {
    "exact": 0,
    "tight": 5,
    "normal": 10,
    "moderate": 13,
    "aggressive": 26,
    "very_aggressive": 51
}


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 3:
        print("Usage: python background_remover.py input.png output.png [fuzz]")
        print("Example: python background_remover.py cat.png cat_transparent.png 10")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    fuzz = int(sys.argv[3]) if len(sys.argv) > 3 else 10

    img = Image.open(input_path)

    print(f"Analyzing {input_path}...")

    # Detect background
    bg_color = detect_background_color(img)
    if bg_color:
        print(f"  Detected background color: RGB{bg_color}")
    else:
        print("  No solid background detected")

    # Check if white
    has_white = has_white_background(img)
    print(f"  Has white background: {has_white}")

    if has_white:
        print(f"  Removing white background (fuzz={fuzz})...")
        result = remove_white_background(img, fuzz=fuzz)
        result.save(output_path)
        print(f"✓ Saved to: {output_path}")
    else:
        print("  Skipping - no white background detected")
        print("  Use remove_white_background() directly if needed")
