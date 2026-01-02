"""
Photo to Slack Emoji Converter

Main module for converting photos to Slack-optimized emojis using Google's
Gemini 2.5 Flash Image (Nano Banana) model.
"""

import os
import base64
from typing import Optional, Dict, List, Tuple
from PIL import Image
from io import BytesIO

from .gemini_client import GeminiImageClient
from .optimizer import optimize_for_slack
from .validators import validate_slack_emoji
from .background_remover import auto_remove_background, has_white_background


# Pre-defined style prompts
STYLE_PROMPTS = {
    "classic_emoji": """
        Transform this photo into a classic emoji style: round shape, simplified features,
        bold outlines, expressive and friendly, vibrant yellow/warm tones, minimal shading,
        white or transparent background. Focus on the subject's main expression and make it
        instantly recognizable at small sizes. Think Apple/Unicode emoji aesthetic.
    """,

    "flat_icon": """
        Transform this photo into a flat, minimalist icon: simple geometric shapes,
        solid colors, no gradients, bold clean outlines, modern flat design aesthetic,
        white background. Capture the essence of the subject with minimal detail.
        Think Material Design or iOS icon style.
    """,

    "kawaii_sticker": """
        Transform this photo into a kawaii-style sticker: cute and playful, rounded features,
        large expressive eyes, simple cel-shading, vibrant color palette, bold clean outlines,
        white background. Make it adorable and friendly with that Japanese cute aesthetic.
    """,

    "pixel_art": """
        Transform this photo into pixel art: 32x32 pixel style, retro 8-bit aesthetic,
        limited color palette (8-16 colors), chunky pixels, clear subject outline,
        simple shading, transparent or solid background. Think classic Nintendo/Sega era.
    """,

    "chibi": """
        Transform this photo into chibi anime style: super-deformed proportions with
        oversized head (head is 1/3 of total height), small body, large expressive eyes,
        simplified features, bold outlines, cute and cartoonish, vibrant anime colors,
        white background. Maintain the subject's key characteristics but make it adorable.
    """,

    "cartoon": """
        Transform this photo into a cartoon style: exaggerated features, bold black outlines,
        cel-shaded coloring, expressive and dynamic, vibrant colors, simplified details,
        white background. Think modern animated series aesthetic.
    """
}


def convert_photo_to_emoji(
    input_path: str,
    output_path: str,
    style: str = "classic_emoji",
    description: Optional[str] = None,
    custom_prompt: Optional[str] = None,
    api_key: Optional[str] = None,
    max_colors: int = 48,
    target_size: Tuple[int, int] = (128, 128),
    validate: bool = True,
    verbose: bool = True,
    remove_background: str = "auto",
    background_fuzz: int = 10
) -> Dict:
    """
    Convert a photo to a Slack-optimized emoji.

    Args:
        input_path: Path to input photo
        output_path: Path to save the generated emoji
        style: Pre-defined style ("classic_emoji", "flat_icon", "kawaii_sticker",
               "pixel_art", "chibi", "cartoon", or "custom")
        description: Optional description of the subject to guide transformation
        custom_prompt: Custom transformation prompt (used when style="custom")
        api_key: Google Gemini API key (or use GEMINI_API_KEY env var)
        max_colors: Maximum colors in output (lower = smaller file size)
        target_size: Target dimensions (width, height) - default 128x128
        validate: Whether to validate Slack requirements
        verbose: Print progress messages
        remove_background: Background removal mode - "auto" (detect and remove white),
                          "always" (always attempt removal), "never" (skip)
        background_fuzz: Fuzz tolerance for background removal (0-51, default 10)

    Returns:
        Dict with status, file_size, validation_results, and any warnings
    """

    if verbose:
        print(f"🎨 Converting photo to Slack emoji...")
        print(f"   Input: {input_path}")
        print(f"   Style: {style}")

    # Load and encode input image
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input image not found: {input_path}")

    with open(input_path, 'rb') as f:
        input_image_data = f.read()

    # Determine MIME type
    image = Image.open(BytesIO(input_image_data))
    format_lower = image.format.lower() if image.format else 'png'
    mime_type = f"image/{format_lower}"

    if verbose:
        print(f"   Input size: {image.size[0]}x{image.size[1]}")

    # Build transformation prompt
    if custom_prompt:
        prompt = custom_prompt
    elif style in STYLE_PROMPTS:
        base_prompt = STYLE_PROMPTS[style].strip()
        if description:
            prompt = f"{base_prompt}\n\nSubject description: {description}"
        else:
            prompt = base_prompt
    else:
        raise ValueError(f"Unknown style: {style}. Use 'custom' and provide custom_prompt, or choose from: {list(STYLE_PROMPTS.keys())}")

    if verbose:
        print(f"   Calling Gemini API...")

    # Call Gemini API
    client = GeminiImageClient(api_key=api_key)

    try:
        generated_image_data = client.transform_image(
            image_data=input_image_data,
            mime_type=mime_type,
            prompt=prompt
        )
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to generate image from Gemini API"
        }

    if verbose:
        print(f"   ✓ Image generated by Gemini")

    # Load generated image
    generated_image = Image.open(BytesIO(generated_image_data))

    if verbose:
        print(f"   Generated size: {generated_image.size[0]}x{generated_image.size[1]}")

    # Remove background if requested
    background_removed = False
    if remove_background != "never":
        if remove_background == "always":
            # Always attempt removal
            generated_image, background_removed = auto_remove_background(
                generated_image,
                fuzz=background_fuzz
            )
            if verbose and background_removed:
                print(f"   ✓ Removed white background (fuzz={background_fuzz})")
        elif remove_background == "auto":
            # Auto-detect and remove if white background present
            if has_white_background(generated_image):
                generated_image, background_removed = auto_remove_background(
                    generated_image,
                    fuzz=background_fuzz
                )
                if verbose and background_removed:
                    print(f"   ✓ Auto-removed white background (fuzz={background_fuzz})")

    if verbose:
        print(f"   Optimizing for Slack...")

    # Optimize for Slack requirements
    optimized_image = optimize_for_slack(
        generated_image,
        target_size=target_size,
        max_colors=max_colors,
        target_file_size_kb=60  # Leave buffer below 64KB limit
    )

    # Save optimized image
    optimized_image.save(output_path, 'PNG', optimize=True)

    # Get file size
    file_size_bytes = os.path.getsize(output_path)
    file_size_kb = file_size_bytes / 1024

    if verbose:
        print(f"   Output size: {optimized_image.size[0]}x{optimized_image.size[1]}")
        print(f"   File size: {file_size_kb:.1f} KB")

    # Validate for Slack
    validation_results = {}
    if validate:
        is_valid, validation_report = validate_slack_emoji(output_path)
        validation_results = validation_report

        if verbose:
            if is_valid:
                print(f"   ✅ Passes Slack emoji requirements!")
            else:
                print(f"   ⚠️  Validation warnings:")
                for issue in validation_report.get('issues', []):
                    print(f"      - {issue}")

    if verbose:
        print(f"   ✓ Saved to: {output_path}")

    return {
        "status": "success",
        "output_path": output_path,
        "file_size_kb": file_size_kb,
        "dimensions": optimized_image.size,
        "validation_passed": validation_results.get('valid', True),
        "validation_results": validation_results
    }


def batch_convert(
    photos: List[Dict],
    style: str = "classic_emoji",
    api_key: Optional[str] = None,
    **kwargs
) -> List[Dict]:
    """
    Batch convert multiple photos to emojis.

    Args:
        photos: List of dicts with 'input', 'output', and optional 'description' keys
        style: Style to apply to all photos
        api_key: Google Gemini API key
        **kwargs: Additional arguments passed to convert_photo_to_emoji

    Returns:
        List of result dicts for each conversion

    Example:
        photos = [
            {"input": "cat.jpg", "output": "cat_emoji.png", "description": "happy cat"},
            {"input": "dog.jpg", "output": "dog_emoji.png", "description": "excited dog"}
        ]
        results = batch_convert(photos, style="classic_emoji")
    """

    results = []

    for i, photo_config in enumerate(photos, 1):
        print(f"\n[{i}/{len(photos)}] Processing {photo_config['input']}...")

        try:
            result = convert_photo_to_emoji(
                input_path=photo_config['input'],
                output_path=photo_config['output'],
                style=style,
                description=photo_config.get('description'),
                api_key=api_key,
                **kwargs
            )
            results.append(result)

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results.append({
                "status": "error",
                "input": photo_config['input'],
                "error": str(e)
            })

    # Summary
    success_count = sum(1 for r in results if r['status'] == 'success')
    print(f"\n{'='*60}")
    print(f"Batch conversion complete: {success_count}/{len(photos)} successful")
    print(f"{'='*60}")

    return results


def preview_styles(
    input_path: str,
    output_dir: str,
    styles: Optional[List[str]] = None,
    description: Optional[str] = None,
    api_key: Optional[str] = None
) -> List[str]:
    """
    Generate previews of the same photo in multiple styles.

    Args:
        input_path: Path to input photo
        output_dir: Directory to save style previews
        styles: List of styles to preview (default: all available styles)
        description: Subject description
        api_key: Google Gemini API key

    Returns:
        List of output file paths
    """

    if styles is None:
        styles = list(STYLE_PROMPTS.keys())

    os.makedirs(output_dir, exist_ok=True)

    input_basename = os.path.splitext(os.path.basename(input_path))[0]
    output_paths = []

    print(f"🎨 Generating style previews for {input_path}...")
    print(f"   Styles: {', '.join(styles)}")

    for style in styles:
        output_path = os.path.join(output_dir, f"{input_basename}_{style}.png")

        try:
            result = convert_photo_to_emoji(
                input_path=input_path,
                output_path=output_path,
                style=style,
                description=description,
                api_key=api_key,
                verbose=False
            )

            if result['status'] == 'success':
                print(f"   ✓ {style}: {result['file_size_kb']:.1f} KB")
                output_paths.append(output_path)
            else:
                print(f"   ✗ {style}: {result.get('error', 'Failed')}")

        except Exception as e:
            print(f"   ✗ {style}: {str(e)}")

    print(f"\n✓ Generated {len(output_paths)} style previews in {output_dir}")

    return output_paths


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 3:
        print("Usage: python photo_to_emoji.py <input_path> <output_path> [style] [description]")
        print(f"Available styles: {', '.join(STYLE_PROMPTS.keys())}")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    style = sys.argv[3] if len(sys.argv) > 3 else "classic_emoji"
    description = sys.argv[4] if len(sys.argv) > 4 else None

    result = convert_photo_to_emoji(
        input_path=input_path,
        output_path=output_path,
        style=style,
        description=description
    )

    if result['status'] == 'success':
        print(f"\n✅ Success! Emoji saved to {output_path}")
    else:
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
        sys.exit(1)
