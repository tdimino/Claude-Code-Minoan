"""
Preview utilities for Slack emojis

Visualize how emojis will appear at different sizes in Slack.
"""

from PIL import Image, ImageDraw, ImageFont
from typing import List, Optional
import os


def preview_emoji(
    image_path: str,
    sizes: List[int] = [16, 32, 64, 128],
    output_path: Optional[str] = None,
    background_color: tuple = (255, 255, 255)
) -> Image.Image:
    """
    Create a preview showing emoji at different sizes (simulates Slack display).

    Args:
        image_path: Path to emoji image
        sizes: List of sizes to preview
        output_path: Optional path to save preview
        background_color: Background color (RGB tuple)

    Returns:
        PIL Image with preview grid
    """

    # Load emoji
    emoji = Image.open(image_path)

    # Convert to RGBA if needed
    if emoji.mode != 'RGBA':
        emoji = emoji.convert('RGBA')

    # Calculate canvas size
    padding = 20
    label_height = 30
    canvas_width = sum(sizes) + (len(sizes) + 1) * padding
    canvas_height = max(sizes) + 2 * padding + label_height

    # Create canvas
    canvas = Image.new('RGB', (canvas_width, canvas_height), background_color)
    draw = ImageDraw.Draw(canvas)

    # Try to load a font, fallback to default
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
    except:
        font = ImageFont.load_default()

    # Place emojis at different sizes
    x_offset = padding

    for size in sizes:
        # Resize emoji
        resized = emoji.resize((size, size), Image.Resampling.LANCZOS)

        # Calculate vertical centering
        y_offset = padding + (max(sizes) - size) // 2

        # Paste emoji (with alpha if available)
        canvas.paste(resized, (x_offset, y_offset), resized if resized.mode == 'RGBA' else None)

        # Add label
        label = f"{size}px"
        bbox = draw.textbbox((0, 0), label, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = x_offset + (size - text_width) // 2
        text_y = padding + max(sizes) + 5

        draw.text((text_x, text_y), label, fill=(100, 100, 100), font=font)

        x_offset += size + padding

    # Add title
    title = f"Emoji Preview: {os.path.basename(image_path)}"
    draw.text((padding, 5), title, fill=(50, 50, 50), font=font)

    # Save if output path provided
    if output_path:
        canvas.save(output_path)
        print(f"Preview saved to {output_path}")

    return canvas


def create_comparison_grid(
    image_paths: List[str],
    labels: Optional[List[str]] = None,
    output_path: Optional[str] = None
) -> Image.Image:
    """
    Create a comparison grid of multiple emoji variations.

    Args:
        image_paths: List of paths to emoji images
        labels: Optional labels for each emoji
        output_path: Optional path to save grid

    Returns:
        PIL Image with comparison grid
    """

    # Load all images
    images = [Image.open(path).convert('RGBA') for path in image_paths]

    if labels is None:
        labels = [os.path.basename(path) for path in image_paths]

    # Calculate grid dimensions
    cols = min(4, len(images))
    rows = (len(images) + cols - 1) // cols

    cell_size = 128
    padding = 20
    label_height = 30

    canvas_width = cols * cell_size + (cols + 1) * padding
    canvas_height = rows * (cell_size + label_height) + (rows + 1) * padding

    # Create canvas
    canvas = Image.new('RGB', (canvas_width, canvas_height), (250, 250, 250))
    draw = ImageDraw.Draw(canvas)

    # Try to load a font
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 11)
    except:
        font = ImageFont.load_default()

    # Place images in grid
    for i, (img, label) in enumerate(zip(images, labels)):
        row = i // cols
        col = i % cols

        x = padding + col * (cell_size + padding)
        y = padding + row * (cell_size + label_height + padding)

        # Resize to cell size
        resized = img.resize((cell_size, cell_size), Image.Resampling.LANCZOS)

        # Paste image
        canvas.paste(resized, (x, y), resized if resized.mode == 'RGBA' else None)

        # Add label
        label_y = y + cell_size + 5
        draw.text((x, label_y), label, fill=(80, 80, 80), font=font)

    # Save if output path provided
    if output_path:
        canvas.save(output_path)
        print(f"Comparison grid saved to {output_path}")

    return canvas


def show_transparency_overlay(
    image_path: str,
    output_path: Optional[str] = None
) -> Image.Image:
    """
    Show image with checkerboard background to visualize transparency.

    Args:
        image_path: Path to emoji image
        output_path: Optional path to save result

    Returns:
        PIL Image with checkerboard background
    """

    # Load image
    img = Image.open(image_path).convert('RGBA')
    width, height = img.size

    # Create checkerboard pattern
    checker_size = 10
    checkerboard = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(checkerboard)

    for y in range(0, height, checker_size):
        for x in range(0, width, checker_size):
            if (x // checker_size + y // checker_size) % 2:
                draw.rectangle(
                    [x, y, x + checker_size, y + checker_size],
                    fill=(220, 220, 220)
                )

    # Composite image over checkerboard
    result = Image.alpha_composite(checkerboard.convert('RGBA'), img)

    # Save if output path provided
    if output_path:
        result.save(output_path)
        print(f"Transparency preview saved to {output_path}")

    return result


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python preview.py <emoji_path> [output_path]")
        sys.exit(1)

    emoji_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    # Create preview
    preview_emoji(emoji_path, output_path=output_path)

    if output_path:
        print(f"✓ Preview saved to {output_path}")
    else:
        print("✓ Preview generated (not saved)")
