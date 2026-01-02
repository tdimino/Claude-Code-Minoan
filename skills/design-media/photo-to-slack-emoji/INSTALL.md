# Installation Guide

Quick setup guide for the Photo to Slack Emoji Converter skill.

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Google Gemini API key (already configured in the skill)

## Installation Steps

### 1. Install Python Dependencies

```bash
cd ~/.claude/skills/photo-to-slack-emoji
pip install -r requirements.txt
```

This installs:
- `Pillow` - Image processing library
- `google-genai` - Google Gemini API client
- `requests` - HTTP requests library

### 2. Verify Installation

Test that the skill is working:

```bash
python -c "from core import convert_photo_to_emoji; print('✅ Installation successful!')"
```

If you see "✅ Installation successful!", you're ready to go!

### 3. Run Examples

Try the interactive example script:

```bash
python example_usage.py
```

Or use the skill directly in Python:

```python
from core import convert_photo_to_emoji

result = convert_photo_to_emoji(
    input_path="/path/to/your/photo.jpg",
    output_path="/tmp/emoji.png",
    style="classic_emoji",
    description="happy face"
)

print(f"✅ Emoji created: {result['file_size_kb']:.1f} KB")
```

## Quick Test

Create a test emoji from any photo you have:

```python
from core import convert_photo_to_emoji

# Replace with your own photo path
convert_photo_to_emoji(
    input_path="~/Downloads/my_photo.jpg",
    output_path="~/Desktop/test_emoji.png",
    style="classic_emoji"
)
```

Check `~/Desktop/test_emoji.png` - it should be a Slack-ready emoji!

## Using the Skill in Claude Code

Once installed, you can invoke the skill in Claude Code sessions:

```
You: Transform my cat photo into a Slack emoji
Claude: [Uses the photo-to-slack-emoji skill]
```

Or directly:

```
You: Use the photo-to-slack-emoji skill to convert ~/Photos/dog.jpg to a kawaii style emoji
```

## Troubleshooting

### ImportError: No module named 'PIL'

**Solution**: Install Pillow
```bash
pip install Pillow
```

### ImportError: No module named 'google.genai'

**Solution**: Install google-genai
```bash
pip install google-genai
```

### API Authentication Error

**Solution**: The API key is pre-configured. If you see authentication errors:
1. Check internet connection
2. Verify the API key hasn't been revoked
3. Contact admin if issues persist

### File Not Found Error

**Solution**: Use absolute paths or verify the file exists:
```python
import os
photo_path = os.path.expanduser("~/Photos/my_photo.jpg")
print(f"File exists: {os.path.exists(photo_path)}")
```

## Next Steps

1. Read `README.md` for usage examples
2. Review `skill.md` for complete documentation
3. Check `templates/style_examples.md` for style guide
4. Run `example_usage.py` for interactive demos

## Support

For issues or questions:
- Check documentation in `skill.md`
- Review examples in `example_usage.py`
- Read API docs in `references/gemini-api-docs.md`
- See Slack requirements in `references/slack-emoji-specs.md`

Happy emoji creating! 🎨
