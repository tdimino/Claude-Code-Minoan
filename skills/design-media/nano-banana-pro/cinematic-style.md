# Cinematic Digital Painting Style

For **documentary-style digital paintings** matching professional artwork aesthetics with Nano Banana Pro (Gemini 3 Pro Image).

## Formula

```
"Cinematic digital painting of [subject], painterly brush strokes with visible texture, warm golden ambient lighting mixed with [accent color] glow, dramatic rim lighting creating separation, atmospheric depth of field with soft bokeh, [background details], high contrast with deep blacks and bright highlights, professional digital art quality matching documentary photography aesthetic, warm color palette with amber and golden tones, lens flare effects, atmospheric haze"
```

## Key Elements

- **Painterly brush strokes** - visible texture, not smooth digital
- **Warm golden/amber lighting** - atmospheric glow (not cool tones)
- **Dramatic rim lighting** - creates separation and depth
- **Soft bokeh depth-of-field** - atmospheric background blur
- **High contrast** - deep blacks with bright glowing highlights
- **Warm color palette** - amber, golden, orange tones
- **Temperature: 0.6** - balanced between consistency and creativity

## Example Usage

**Texty avatar** (floating smartphone with cat eyes):

```bash
python scripts/generate_image.py \
  "Cinematic digital painting of floating smartphone standing upright centered, glowing green cat eyes on screen, painterly brush strokes, warm golden lighting with green screen glow, dramatic rim lighting, soft bokeh stars, SMS bubbles showing millennial texts, cosmic space with warm nebula, phone 70% of frame vertical centered, high contrast, professional digital art" \
  --aspect-ratio 1:1 \
  --temperature 0.6
```

## Technical Notes

**Long Prompts - Fixed**: Long prompts (200+ words) previously failed silently in the save logic due to poor error handling. The script now includes:

- **Granular error handling** - Catches specific exceptions (base64.binascii.Error, IOError) instead of generic Exception
- **Debug mode** - Use `--verbose` flag to see detailed processing information
- **Warning messages** - Non-fatal errors now print warnings instead of failing silently
- **Better validation** - Checks for empty image data before attempting decode

**If images fail to save**, run with `--verbose` to see detailed debug output:

```bash
python scripts/generate_image.py "your long prompt" --verbose
```

## When to Use This Style

- **Soul avatars** - Character portraits for AI personalities
- **Documentary-style artwork** - Matching professional digital painting aesthetics
- **Warm, atmospheric scenes** - When you need golden/amber lighting
- **High-quality character work** - Professional-grade digital art
- **Cinematic compositions** - Dramatic lighting and depth

## Tips

1. **Start with the formula** - Use it as a template, fill in [subject] and [accent color]
2. **Keep temperature at 0.6** - Balances consistency with creativity
3. **Specify composition** - Include framing details ("70% of frame", "centered", "upright")
4. **Use aspect ratios** - 1:1 for avatars, 16:9 for landscapes, 9:16 for portraits
5. **Layer lighting** - Combine warm ambient + accent glow + rim lighting for depth
6. **Add atmospheric elements** - Bokeh, haze, lens flare for cinematic feel

## Related Files

- Main skill documentation: `skill.md`
- Generation script: `scripts/generate_image.py`
- Prompting guide: `references/prompting-guide.md`
