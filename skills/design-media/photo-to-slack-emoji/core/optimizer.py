"""
Image Optimization for Slack Emojis

Utilities to optimize images to meet Slack's strict requirements:
- Max 64KB file size
- Optimal 128x128 dimensions
- Limited color palette (32-48 colors)
"""

from PIL import Image
import os
from typing import Tuple, Optional
from io import BytesIO


def optimize_for_slack(
    image: Image.Image,
    target_size: Tuple[int, int] = (128, 128),
    max_colors: int = 48,
    target_file_size_kb: int = 60
) -> Image.Image:
    """
    Optimize an image for Slack emoji requirements.

    Args:
        image: PIL Image object to optimize
        target_size: Target dimensions (width, height)
        max_colors: Maximum number of colors to use
        target_file_size_kb: Target file size in KB (buffer below 64KB limit)

    Returns:
        Optimized PIL Image object
    """

    # Convert to RGBA if not already
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    # FIX: Center crop to square BEFORE resizing (prevents aspect ratio distortion)
    width, height = image.size
    if width != height:
        # Use smaller dimension to ensure we don't lose important content
        size = min(width, height)
        left = (width - size) // 2
        top = (height - size) // 2
        image = image.crop((left, top, left + size, top + size))

    # Resize to target dimensions (no distortion since already square)
    if image.size != target_size:
        image = image.resize(target_size, Image.Resampling.LANCZOS)

    # Quantize colors to reduce file size
    # First, separate alpha channel
    alpha = image.split()[-1]

    # Convert RGB to P mode (palette) with limited colors
    rgb_image = image.convert('RGB')
    quantized = rgb_image.quantize(colors=max_colors, method=Image.Quantize.MEDIANCUT)

    # Convert back to RGBA and restore alpha
    quantized_rgba = quantized.convert('RGBA')

    # Merge the alpha channel back
    r, g, b, _ = quantized_rgba.split()
    optimized = Image.merge('RGBA', (r, g, b, alpha))

    # Check file size and reduce colors if needed
    temp_buffer = BytesIO()
    optimized.save(temp_buffer, 'PNG', optimize=True)
    current_size_kb = len(temp_buffer.getvalue()) / 1024

    # If still too large, aggressively reduce colors
    if current_size_kb > target_file_size_kb and max_colors > 16:
        return optimize_for_slack(
            image=image,
            target_size=target_size,
            max_colors=max(16, max_colors // 2),  # Cut colors in half
            target_file_size_kb=target_file_size_kb
        )

    return optimized


def aggressive_optimize(
    input_path: str,
    output_path: str,
    target_size_kb: int = 60,
    strategies: Optional[list] = None
) -> dict:
    """
    Aggressively optimize an existing emoji image to meet size requirements.

    Args:
        input_path: Path to input image
        output_path: Path to save optimized image
        target_size_kb: Target file size in KB
        strategies: List of optimization strategies to apply
                   Options: "reduce_colors", "reduce_dimensions", "compress_png"

    Returns:
        Dict with optimization results
    """

    if strategies is None:
        strategies = ["reduce_colors", "reduce_dimensions", "compress_png"]

    image = Image.open(input_path)
    original_size = os.path.getsize(input_path) / 1024

    print(f"Original size: {original_size:.1f} KB")

    # Strategy 1: Reduce colors
    if "reduce_colors" in strategies:
        print("Applying: Reduce colors...")

        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        alpha = image.split()[-1]
        rgb_image = image.convert('RGB')

        # Try progressively fewer colors
        for num_colors in [32, 24, 16, 12, 8]:
            quantized = rgb_image.quantize(colors=num_colors, method=Image.Quantize.MEDIANCUT)
            quantized_rgba = quantized.convert('RGBA')
            r, g, b, _ = quantized_rgba.split()
            image = Image.merge('RGBA', (r, g, b, alpha))

            # Test file size
            temp_buffer = BytesIO()
            image.save(temp_buffer, 'PNG', optimize=True)
            current_size_kb = len(temp_buffer.getvalue()) / 1024

            print(f"  {num_colors} colors -> {current_size_kb:.1f} KB")

            if current_size_kb <= target_size_kb:
                break

    # Strategy 2: Reduce dimensions
    if "reduce_dimensions" in strategies:
        temp_buffer = BytesIO()
        image.save(temp_buffer, 'PNG', optimize=True)
        current_size_kb = len(temp_buffer.getvalue()) / 1024

        if current_size_kb > target_size_kb:
            print("Applying: Reduce dimensions...")

            for size in [112, 96, 80, 64]:
                image = image.resize((size, size), Image.Resampling.LANCZOS)

                temp_buffer = BytesIO()
                image.save(temp_buffer, 'PNG', optimize=True)
                current_size_kb = len(temp_buffer.getvalue()) / 1024

                print(f"  {size}x{size} -> {current_size_kb:.1f} KB")

                if current_size_kb <= target_size_kb:
                    # Resize back up to 128x128 (will be slightly blurry but meets size)
                    image = image.resize((128, 128), Image.Resampling.LANCZOS)
                    break

    # Strategy 3: PNG compression
    if "compress_png" in strategies:
        print("Applying: PNG compression...")

    # Save final optimized image
    image.save(output_path, 'PNG', optimize=True)

    final_size_kb = os.path.getsize(output_path) / 1024

    print(f"\nFinal size: {final_size_kb:.1f} KB")
    print(f"Reduction: {((original_size - final_size_kb) / original_size * 100):.1f}%")

    return {
        "original_size_kb": original_size,
        "final_size_kb": final_size_kb,
        "reduction_percent": ((original_size - final_size_kb) / original_size * 100),
        "meets_target": final_size_kb <= target_size_kb
    }


def remove_background(image: Image.Image, tolerance: int = 50) -> Image.Image:
    """
    Remove white or light backgrounds from an image.

    Args:
        image: PIL Image object
        tolerance: Color difference tolerance (0-255)

    Returns:
        Image with transparent background
    """

    # Convert to RGBA
    image = image.convert('RGBA')

    # Get pixel data
    pixels = image.load()
    width, height = image.size

    # Make white/light colors transparent
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]

            # If pixel is close to white, make it transparent
            if r > (255 - tolerance) and g > (255 - tolerance) and b > (255 - tolerance):
                pixels[x, y] = (r, g, b, 0)

    return image


def add_padding(
    image: Image.Image,
    padding: int = 10,
    background_color: Tuple[int, int, int, int] = (255, 255, 255, 0)
) -> Image.Image:
    """
    Add padding around an image.

    Args:
        image: PIL Image object
        padding: Padding in pixels
        background_color: RGBA background color

    Returns:
        Padded image
    """

    width, height = image.size
    new_size = (width + 2 * padding, height + 2 * padding)

    # Create new image with padding
    padded = Image.new('RGBA', new_size, background_color)

    # Paste original image in center
    padded.paste(image, (padding, padding), image if image.mode == 'RGBA' else None)

    return padded


def preview_at_sizes(image: Image.Image, sizes: list = [16, 32, 64, 128]) -> dict:
    """
    Generate previews of image at different sizes (simulates Slack display).

    Args:
        image: PIL Image object
        sizes: List of sizes to preview

    Returns:
        Dict mapping size to preview image
    """

    previews = {}

    for size in sizes:
        preview = image.resize((size, size), Image.Resampling.LANCZOS)
        previews[size] = preview

    return previews


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 3:
        print("Usage: python optimizer.py <input_path> <output_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    result = aggressive_optimize(input_path, output_path, target_size_kb=60)

    if result['meets_target']:
        print(f"\n✅ Success! Optimized emoji meets Slack requirements.")
    else:
        print(f"\n⚠️  Warning: Could not meet target size. Manual editing may be needed.")
