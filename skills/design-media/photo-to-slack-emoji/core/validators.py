"""
Slack Emoji Validators

Validate images against Slack's emoji requirements.
"""

import os
from PIL import Image
from typing import Tuple, Dict


# Slack emoji requirements
SLACK_EMOJI_MAX_SIZE_KB = 64
SLACK_EMOJI_OPTIMAL_DIMENSIONS = (128, 128)
SLACK_EMOJI_MAX_DIMENSION = 256


def validate_slack_emoji(image_path: str) -> Tuple[bool, Dict]:
    """
    Validate an image against Slack emoji requirements.

    Slack Requirements:
    - Max file size: 64KB (strict)
    - Optimal dimensions: 128x128
    - Max dimension: 256x256
    - Format: PNG, GIF, or JPEG (PNG with transparency recommended)

    Args:
        image_path: Path to image file

    Returns:
        Tuple of (is_valid, validation_report)
        - is_valid: True if passes all requirements
        - validation_report: Dict with detailed results
    """

    issues = []
    warnings = []

    # Check file exists
    if not os.path.exists(image_path):
        return False, {
            "valid": False,
            "issues": ["File not found"],
            "warnings": [],
            "details": {}
        }

    # Check file size
    file_size_bytes = os.path.getsize(image_path)
    file_size_kb = file_size_bytes / 1024

    if file_size_kb > SLACK_EMOJI_MAX_SIZE_KB:
        issues.append(
            f"File size {file_size_kb:.1f} KB exceeds Slack's {SLACK_EMOJI_MAX_SIZE_KB} KB limit"
        )
    elif file_size_kb > (SLACK_EMOJI_MAX_SIZE_KB * 0.9):
        warnings.append(
            f"File size {file_size_kb:.1f} KB is close to limit. Consider further optimization."
        )

    # Check image properties
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            format_name = img.format
            mode = img.mode

            # Check dimensions
            if width > SLACK_EMOJI_MAX_DIMENSION or height > SLACK_EMOJI_MAX_DIMENSION:
                issues.append(
                    f"Dimensions {width}x{height} exceed max {SLACK_EMOJI_MAX_DIMENSION}x{SLACK_EMOJI_MAX_DIMENSION}"
                )

            if (width, height) != SLACK_EMOJI_OPTIMAL_DIMENSIONS:
                warnings.append(
                    f"Dimensions {width}x{height} differ from optimal {SLACK_EMOJI_OPTIMAL_DIMENSIONS[0]}x{SLACK_EMOJI_OPTIMAL_DIMENSIONS[1]}"
                )

            # Check aspect ratio
            if width != height:
                warnings.append(
                    f"Non-square aspect ratio ({width}x{height}). Slack displays emojis as squares."
                )

            # Check format
            if format_name not in ['PNG', 'GIF', 'JPEG', 'JPG']:
                warnings.append(
                    f"Format {format_name} may not be supported. Use PNG for best results."
                )

            # Check transparency support
            if mode != 'RGBA' and format_name == 'PNG':
                warnings.append(
                    "PNG without alpha channel. Consider using transparency for better appearance."
                )

            details = {
                "file_size_kb": round(file_size_kb, 2),
                "file_size_bytes": file_size_bytes,
                "dimensions": (width, height),
                "format": format_name,
                "mode": mode,
                "aspect_ratio": f"{width}:{height}",
                "is_square": width == height
            }

    except Exception as e:
        issues.append(f"Failed to read image: {str(e)}")
        details = {}

    is_valid = len(issues) == 0

    return is_valid, {
        "valid": is_valid,
        "issues": issues,
        "warnings": warnings,
        "details": details
    }


def validate_dimensions(width: int, height: int, is_emoji: bool = True) -> Tuple[bool, Dict]:
    """
    Validate image dimensions.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        is_emoji: True for emoji validation, False for general GIF

    Returns:
        Tuple of (passes, info_dict)
    """

    if is_emoji:
        max_dim = SLACK_EMOJI_MAX_DIMENSION
        optimal = SLACK_EMOJI_OPTIMAL_DIMENSIONS
    else:
        max_dim = 480
        optimal = (480, 480)

    issues = []

    if width > max_dim or height > max_dim:
        issues.append(f"Dimensions {width}x{height} exceed max {max_dim}x{max_dim}")

    if width != height:
        issues.append(f"Non-square aspect ratio ({width}x{height})")

    passes = len(issues) == 0

    return passes, {
        "valid": passes,
        "dimensions": (width, height),
        "max_dimension": max_dim,
        "optimal_dimensions": optimal,
        "is_square": width == height,
        "issues": issues
    }


def check_file_size(file_path: str, max_size_kb: int = 64) -> Tuple[bool, Dict]:
    """
    Check if file meets size requirement.

    Args:
        file_path: Path to file
        max_size_kb: Maximum allowed size in KB

    Returns:
        Tuple of (passes, info_dict)
    """

    if not os.path.exists(file_path):
        return False, {
            "valid": False,
            "error": "File not found"
        }

    file_size_bytes = os.path.getsize(file_path)
    file_size_kb = file_size_bytes / 1024

    passes = file_size_kb <= max_size_kb

    return passes, {
        "valid": passes,
        "file_size_kb": round(file_size_kb, 2),
        "file_size_bytes": file_size_bytes,
        "max_size_kb": max_size_kb,
        "under_limit": passes,
        "percent_of_limit": round((file_size_kb / max_size_kb) * 100, 1)
    }


def is_slack_ready(image_path: str, is_emoji: bool = True) -> bool:
    """
    Quick check if image is ready to upload to Slack.

    Args:
        image_path: Path to image file
        is_emoji: True for emoji validation, False for general GIF

    Returns:
        True if ready to upload, False otherwise
    """

    is_valid, _ = validate_slack_emoji(image_path) if is_emoji else check_file_size(image_path, max_size_kb=2048)

    return is_valid


def generate_report(image_path: str) -> str:
    """
    Generate a human-readable validation report.

    Args:
        image_path: Path to image file

    Returns:
        Formatted string report
    """

    is_valid, report = validate_slack_emoji(image_path)

    lines = [
        "=" * 60,
        "SLACK EMOJI VALIDATION REPORT",
        "=" * 60,
        f"File: {os.path.basename(image_path)}",
        ""
    ]

    if is_valid:
        lines.append("✅ STATUS: READY TO UPLOAD")
    else:
        lines.append("❌ STATUS: NOT READY")

    lines.append("")
    lines.append("DETAILS:")

    details = report.get('details', {})
    if details:
        lines.append(f"  File Size:    {details['file_size_kb']} KB (limit: 64 KB)")
        lines.append(f"  Dimensions:   {details['dimensions'][0]}x{details['dimensions'][1]} (optimal: 128x128)")
        lines.append(f"  Format:       {details['format']}")
        lines.append(f"  Color Mode:   {details['mode']}")
        lines.append(f"  Square:       {'Yes' if details['is_square'] else 'No'}")

    if report['issues']:
        lines.append("")
        lines.append("ISSUES (must fix):")
        for issue in report['issues']:
            lines.append(f"  ❌ {issue}")

    if report['warnings']:
        lines.append("")
        lines.append("WARNINGS (recommended fixes):")
        for warning in report['warnings']:
            lines.append(f"  ⚠️  {warning}")

    lines.append("=" * 60)

    return "\n".join(lines)


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python validators.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]

    print(generate_report(image_path))
