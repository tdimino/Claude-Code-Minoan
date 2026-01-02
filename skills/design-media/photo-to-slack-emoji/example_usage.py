#!/usr/bin/env python3
"""
Example usage of Photo to Slack Emoji Converter

This script demonstrates various ways to use the skill.
"""

import os
import sys

# Add parent directory to path so we can import core modules
sys.path.insert(0, os.path.dirname(__file__))

from core import (
    convert_photo_to_emoji,
    batch_convert,
    preview_styles,
    validate_slack_emoji,
    generate_report
)


def example_1_basic_conversion():
    """Example 1: Basic photo to emoji conversion"""
    print("=" * 60)
    print("EXAMPLE 1: Basic Conversion")
    print("=" * 60)

    # You'll need to provide your own photo path
    input_photo = input("Enter path to your photo (or press Enter to skip): ").strip()

    if not input_photo or not os.path.exists(input_photo):
        print("⚠️  Skipping - no valid photo provided")
        return

    output_path = "/tmp/my_emoji.png"

    result = convert_photo_to_emoji(
        input_path=input_photo,
        output_path=output_path,
        style="classic_emoji",
        description="happy face"  # Modify this based on your photo
    )

    if result['status'] == 'success':
        print(f"\n✅ Success!")
        print(f"   File size: {result['file_size_kb']:.1f} KB")
        print(f"   Saved to: {output_path}")

        # Validate
        print("\nValidation:")
        print(generate_report(output_path))
    else:
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")


def example_2_style_preview():
    """Example 2: Preview multiple styles"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Style Preview")
    print("=" * 60)

    input_photo = input("Enter path to your photo (or press Enter to skip): ").strip()

    if not input_photo or not os.path.exists(input_photo):
        print("⚠️  Skipping - no valid photo provided")
        return

    output_dir = "/tmp/style_preview/"

    print(f"\nGenerating style previews...")

    output_paths = preview_styles(
        input_path=input_photo,
        output_dir=output_dir,
        styles=["classic_emoji", "flat_icon", "kawaii_sticker", "pixel_art"],
        description="subject"  # Modify based on your photo
    )

    print(f"\n✅ Generated {len(output_paths)} style previews!")
    print(f"   Check: {output_dir}")


def example_3_batch_convert():
    """Example 3: Batch convert multiple photos"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Batch Conversion")
    print("=" * 60)

    # You'll need to provide your own photo paths
    photos = [
        {
            "input": "/path/to/photo1.jpg",
            "output": "/tmp/emoji1.png",
            "description": "subject 1"
        },
        {
            "input": "/path/to/photo2.jpg",
            "output": "/tmp/emoji2.png",
            "description": "subject 2"
        }
    ]

    # Check if photos exist
    valid_photos = [p for p in photos if os.path.exists(p['input'])]

    if not valid_photos:
        print("⚠️  No valid photos found. Update the photo paths in this script.")
        return

    print(f"Converting {len(valid_photos)} photos...")

    results = batch_convert(valid_photos, style="classic_emoji")

    success_count = sum(1 for r in results if r['status'] == 'success')
    print(f"\n✅ Successfully converted {success_count}/{len(valid_photos)} photos")


def example_4_custom_style():
    """Example 4: Custom style prompt"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Custom Style")
    print("=" * 60)

    input_photo = input("Enter path to your photo (or press Enter to skip): ").strip()

    if not input_photo or not os.path.exists(input_photo):
        print("⚠️  Skipping - no valid photo provided")
        return

    output_path = "/tmp/custom_emoji.png"

    custom_prompt = """
    Transform this into a neon glow style:
    bright neon colors (cyan, magenta, yellow),
    glowing edges with bloom effect,
    dark background,
    cyberpunk aesthetic,
    high contrast,
    futuristic vibe
    """

    result = convert_photo_to_emoji(
        input_path=input_photo,
        output_path=output_path,
        style="custom",
        custom_prompt=custom_prompt
    )

    if result['status'] == 'success':
        print(f"\n✅ Custom style emoji created!")
        print(f"   File size: {result['file_size_kb']:.1f} KB")
        print(f"   Saved to: {output_path}")


def example_5_validation_only():
    """Example 5: Validate existing emoji"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Validation")
    print("=" * 60)

    emoji_path = input("Enter path to emoji PNG to validate (or press Enter to skip): ").strip()

    if not emoji_path or not os.path.exists(emoji_path):
        print("⚠️  Skipping - no valid emoji file provided")
        return

    # Validate
    is_valid, report = validate_slack_emoji(emoji_path)

    # Print report
    print("\n" + generate_report(emoji_path))

    if is_valid:
        print("\n✅ Ready to upload to Slack!")
    else:
        print("\n❌ Fix the issues above before uploading.")


def interactive_mode():
    """Interactive mode - guide user through conversion"""
    print("=" * 60)
    print("PHOTO TO SLACK EMOJI - INTERACTIVE MODE")
    print("=" * 60)

    # Get input photo
    input_photo = input("\nEnter path to your photo: ").strip()

    if not os.path.exists(input_photo):
        print(f"❌ Error: File not found - {input_photo}")
        return

    # Get output path
    default_output = "/tmp/emoji.png"
    output_path = input(f"\nEnter output path (default: {default_output}): ").strip()
    if not output_path:
        output_path = default_output

    # Choose style
    print("\nAvailable styles:")
    styles = [
        "1. classic_emoji (round, expressive)",
        "2. flat_icon (minimalist, geometric)",
        "3. kawaii_sticker (cute, playful)",
        "4. pixel_art (retro 8-bit)",
        "5. chibi (anime super-deformed)",
        "6. cartoon (exaggerated features)",
        "7. line_art (black outline only)",
        "8. sticker_pack (messaging app style)",
        "9. memoji (3D avatar)",
        "10. retro_emoji (vintage smiley)"
    ]

    for style in styles:
        print(f"   {style}")

    style_map = {
        "1": "classic_emoji",
        "2": "flat_icon",
        "3": "kawaii_sticker",
        "4": "pixel_art",
        "5": "chibi",
        "6": "cartoon",
        "7": "line_art",
        "8": "sticker_pack",
        "9": "memoji",
        "10": "retro_emoji"
    }

    style_choice = input("\nChoose style (1-10, default: 1): ").strip() or "1"
    style = style_map.get(style_choice, "classic_emoji")

    # Get description
    description = input("\nDescribe the subject (e.g., 'happy cat', 'smiling person'): ").strip()

    # Convert
    print(f"\n🎨 Converting photo to {style} style...")

    result = convert_photo_to_emoji(
        input_path=input_photo,
        output_path=output_path,
        style=style,
        description=description if description else None
    )

    if result['status'] == 'success':
        print(f"\n✅ Success!")
        print(f"   File size: {result['file_size_kb']:.1f} KB")
        print(f"   Dimensions: {result['dimensions'][0]}x{result['dimensions'][1]}")
        print(f"   Saved to: {output_path}")

        if result['validation_passed']:
            print(f"   ✅ Ready to upload to Slack!")
        else:
            print(f"   ⚠️  Validation issues - check report")

        # Show validation report
        print("\nValidation Report:")
        print(generate_report(output_path))
    else:
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")


def main():
    """Main menu"""
    print("\n" + "=" * 60)
    print("PHOTO TO SLACK EMOJI CONVERTER - EXAMPLES")
    print("=" * 60)

    print("\nChoose an example:")
    print("  1. Basic conversion (one photo → one emoji)")
    print("  2. Style preview (test multiple styles)")
    print("  3. Batch conversion (multiple photos)")
    print("  4. Custom style (your own prompt)")
    print("  5. Validation only (check existing emoji)")
    print("  6. Interactive mode (guided conversion)")
    print("  0. Exit")

    choice = input("\nEnter choice (0-6): ").strip()

    if choice == "1":
        example_1_basic_conversion()
    elif choice == "2":
        example_2_style_preview()
    elif choice == "3":
        example_3_batch_convert()
    elif choice == "4":
        example_4_custom_style()
    elif choice == "5":
        example_5_validation_only()
    elif choice == "6":
        interactive_mode()
    elif choice == "0":
        print("\nGoodbye!")
        return
    else:
        print("\n❌ Invalid choice")

    # Ask to run another
    again = input("\n\nRun another example? (y/n): ").strip().lower()
    if again == 'y':
        main()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
