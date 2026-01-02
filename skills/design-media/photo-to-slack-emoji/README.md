# Photo to Slack Emoji Converter

Transform any photo into a perfect Slack emoji using Google's **Gemini 3 Pro Image (Nano Banana Pro)** AI model.

## Features

- 🤖 **AI-Powered Transformation**: Gemini automatically identifies subjects and transforms them to emoji style
- 🎨 **10 Pre-Built Styles**: Classic emoji, flat icon, kawaii, pixel art, chibi, cartoon, and more
- ✅ **Slack Optimized**: Automatic compression and validation for Slack's strict 64KB limit
- 🔍 **Subject Detection**: AI understands what's in your photo without manual editing
- 📦 **Batch Processing**: Convert multiple photos at once
- 🎭 **Style Preview**: Test multiple styles on one photo to find the perfect look

## Quick Start

### Installation

1. Install dependencies:
```bash
pip install pillow google-genai requests
```

2. API key is already configured (internal company use)

3. Start converting photos!

### Basic Usage

```python
from core import convert_photo_to_emoji

# Convert a photo to classic emoji style
result = convert_photo_to_emoji(
    input_path="~/Photos/my_cat.jpg",
    output_path="~/Desktop/cat_emoji.png",
    style="classic_emoji",
    description="happy cat face"
)

print(f"✅ Emoji created: {result['file_size_kb']:.1f} KB")
```

### Command Line Usage

```bash
cd ~/.claude/skills/photo-to-slack-emoji

# Basic conversion
python -m core.photo_to_emoji input.jpg output.png

# With style and description
python -m core.photo_to_emoji input.jpg output.png classic_emoji "happy dog"
```

## Available Styles

1. **classic_emoji** - Round, expressive, Apple/Unicode style (best for faces)
2. **flat_icon** - Minimalist, geometric, Material Design (best for objects)
3. **kawaii_sticker** - Cute, playful, large eyes (best for animals)
4. **pixel_art** - Retro 8-bit, chunky pixels (best for icons)
5. **chibi** - Anime super-deformed, oversized head (best for characters)
6. **cartoon** - Exaggerated features, bold outlines (best for dynamic subjects)
7. **line_art** - Black and white outline only (best for simple shapes)
8. **sticker_pack** - Messaging app style with shadow (best for reactions)
9. **memoji** - 3D-rendered avatar style (best for portraits)
10. **retro_emoji** - Vintage 1970s yellow smiley (best for expressions)

See `templates/style_examples.md` for detailed style guide with examples.

## Examples

### Example 1: Pet Photo

```python
from core import convert_photo_to_emoji

convert_photo_to_emoji(
    input_path="~/Photos/golden_retriever.jpg",
    output_path="~/Desktop/happy_dog.png",
    style="classic_emoji",
    description="happy golden retriever smiling"
)
```

**Result**: Round, friendly dog face emoji, 52KB, perfect for Slack

### Example 2: Logo to Icon

```python
convert_photo_to_emoji(
    input_path="~/Documents/company_logo.png",
    output_path="~/Desktop/company_icon.png",
    style="flat_icon",
    description="company logo"
)
```

**Result**: Minimalist flat icon, 28KB, clean and professional

### Example 3: Portrait to Chibi

```python
convert_photo_to_emoji(
    input_path="~/Photos/headshot.jpg",
    output_path="~/Desktop/avatar.png",
    style="chibi",
    description="person with glasses and beard"
)
```

**Result**: Cute anime-style avatar, 48KB, expressive and fun

### Example 4: Batch Convert Team Photos

```python
from core import batch_convert

team_photos = [
    {"input": "alice.jpg", "output": "alice_emoji.png", "description": "smiling woman"},
    {"input": "bob.jpg", "output": "bob_emoji.png", "description": "man with beard"},
    {"input": "charlie.jpg", "output": "charlie_emoji.png", "description": "person with glasses"}
]

results = batch_convert(team_photos, style="classic_emoji")
```

### Example 5: Preview All Styles

```python
from core import preview_styles

# Generate 4 different style variations
preview_styles(
    input_path="~/Photos/cat.jpg",
    output_dir="~/Desktop/cat_styles/",
    styles=["classic_emoji", "kawaii_sticker", "pixel_art", "cartoon"],
    description="orange cat"
)
```

## Advanced Features

### Custom Prompts

Create your own unique style:

```python
convert_photo_to_emoji(
    input_path="photo.jpg",
    output_path="emoji.png",
    style="custom",
    custom_prompt="""
    Transform into neon glow style: bright neon colors,
    glowing edges, dark background, cyberpunk aesthetic,
    high contrast, futuristic vibe
    """
)
```

### Aggressive Optimization

If emoji exceeds 64KB:

```python
from core import aggressive_optimize

aggressive_optimize(
    input_path="emoji_large.png",
    output_path="emoji_optimized.png",
    target_size_kb=60,
    strategies=["reduce_colors", "reduce_dimensions", "compress_png"]
)
```

### Validation

Check if emoji meets Slack requirements:

```python
from core import validate_slack_emoji, generate_report

# Detailed validation
is_valid, report = validate_slack_emoji("emoji.png")

if is_valid:
    print("✅ Ready to upload!")
else:
    print("❌ Issues found:")
    for issue in report['issues']:
        print(f"  - {issue}")

# Or generate readable report
print(generate_report("emoji.png"))
```

### Preview at Different Sizes

See how your emoji looks at Slack's display sizes:

```python
from core import preview_emoji

# Create preview grid showing 16px, 32px, 64px, 128px
preview_emoji("emoji.png", output_path="preview.png")
```

## File Structure

```
photo-to-slack-emoji/
├── README.md                   # This file
├── skill.md                    # Skill documentation for Claude
├── core/
│   ├── __init__.py            # Module exports
│   ├── photo_to_emoji.py      # Main conversion logic
│   ├── gemini_client.py       # Gemini API client (with API key)
│   ├── optimizer.py           # Image optimization
│   ├── validators.py          # Slack requirement validation
│   └── preview.py             # Preview utilities
├── templates/
│   ├── style_prompts.json     # Pre-defined style templates
│   └── style_examples.md      # Visual style guide
└── references/
    ├── gemini-api-docs.md     # Gemini API documentation
    └── slack-emoji-specs.md   # Slack emoji requirements
```

## Requirements

- Python 3.7+
- PIL/Pillow (image processing)
- google-genai (Gemini API client)
- requests (HTTP requests)

## Slack Upload Process

After creating your emoji:

1. Go to your Slack workspace
2. Click workspace name → "Customize [Workspace]"
3. Select "Emoji" tab
4. Click "Add Custom Emoji"
5. Upload your PNG file (must be under 64KB)
6. Give it a name like `:my_cat:` or `:happy_dog:`
7. Click "Save"

Your emoji is now available to everyone in the workspace!

## Tips for Best Results

### Photo Selection
- ✅ Well-lit, clear subject
- ✅ Simple background (or easy to isolate subject)
- ✅ Subject facing camera
- ✅ High resolution source (will be downscaled)
- ❌ Cluttered backgrounds
- ❌ Low lighting or blurry
- ❌ Very small or distant subjects

### Style Selection
- **Faces**: classic_emoji, chibi, memoji, retro_emoji
- **Animals**: kawaii_sticker, classic_emoji, cartoon
- **Objects**: flat_icon, pixel_art, line_art
- **Characters**: chibi, cartoon, sticker_pack
- **Logos**: flat_icon, line_art

### Description Tips
- Be specific: "happy golden retriever" not just "dog"
- Include key features: "person with glasses and beard"
- Mention expressions: "smiling", "excited", "surprised"
- Keep it simple for better results

### File Size Management
- Start with simple styles (flat_icon, pixel_art)
- Use fewer colors (max_colors=32)
- Simplify the subject description
- Avoid gradients and textures

## Troubleshooting

### Problem: File too large (>64KB)

**Solutions**:
1. Use simpler style: `style="flat_icon"` or `style="pixel_art"`
2. Reduce colors: `max_colors=32`
3. Simplify description: "cat" instead of "fluffy Persian cat with blue eyes"
4. Run aggressive optimization:
   ```python
   from core import aggressive_optimize
   aggressive_optimize("emoji.png", "emoji_small.png", target_size_kb=60)
   ```

### Problem: Subject not identified correctly

**Solutions**:
1. Provide specific description: `description="orange tabby cat face"`
2. Crop photo to focus on subject before converting
3. Use better-lit, clearer source photo
4. Try custom prompt with explicit subject

### Problem: Style doesn't match expectation

**Solutions**:
1. Try different style preset
2. Use `preview_styles()` to test multiple styles
3. Write custom prompt for precise control
4. Review `templates/style_examples.md` for style characteristics

### Problem: Emoji looks blurry at small size

**Solutions**:
1. Use simpler style with bolder features
2. Increase contrast in description
3. Use classic_emoji (optimized for small sizes)
4. Test with `preview_emoji()` before uploading

## API Key Management

The API key is pre-configured for internal company use. If you need to use a different key:

```python
# Method 1: Pass directly
convert_photo_to_emoji(..., api_key="your-key-here")

# Method 2: Environment variable
import os
os.environ['GEMINI_API_KEY'] = "your-key-here"
convert_photo_to_emoji(...)
```

## Cost

Google Gemini 2.5 Flash Image pricing:
- **$30 per 1 million output tokens**
- **Each image = 1290 tokens**
- **~$0.039 per emoji created**

Very affordable for emoji creation!

## Support

For issues or questions:
- Review `skill.md` for detailed documentation
- Check `templates/style_examples.md` for style guide
- Read `references/slack-emoji-specs.md` for Slack requirements
- See `references/gemini-api-docs.md` for API details

## License

Internal company use. API key included for authorized users only.

## Credits

Built with:
- **Google Gemini 2.5 Flash Image** - AI image generation
- **PIL/Pillow** - Image processing
- **Claude Code Skills** - Skill framework

Inspired by the Slack community's creativity in custom emojis! 🎨
