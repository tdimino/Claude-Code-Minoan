"""
Photo to Slack Emoji - Core Modules
"""

from .photo_to_emoji import (
    convert_photo_to_emoji,
    batch_convert,
    preview_styles,
    STYLE_PROMPTS
)

from .gemini_client import GeminiImageClient

from .optimizer import (
    optimize_for_slack,
    aggressive_optimize,
    remove_background,
    add_padding,
    preview_at_sizes
)

from .validators import (
    validate_slack_emoji,
    validate_dimensions,
    check_file_size,
    is_slack_ready,
    generate_report
)

from .preview import (
    preview_emoji,
    create_comparison_grid,
    show_transparency_overlay
)

__all__ = [
    # Main conversion functions
    'convert_photo_to_emoji',
    'batch_convert',
    'preview_styles',
    'STYLE_PROMPTS',

    # API client
    'GeminiImageClient',

    # Optimization
    'optimize_for_slack',
    'aggressive_optimize',
    'remove_background',
    'add_padding',
    'preview_at_sizes',

    # Validation
    'validate_slack_emoji',
    'validate_dimensions',
    'check_file_size',
    'is_slack_ready',
    'generate_report',

    # Preview
    'preview_emoji',
    'create_comparison_grid',
    'show_transparency_overlay'
]
