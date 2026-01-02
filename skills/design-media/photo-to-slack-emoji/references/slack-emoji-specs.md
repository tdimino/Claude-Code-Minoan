# Slack Emoji Specifications

Official requirements and best practices for Slack custom emojis.

## Official Requirements

### File Size
- **Maximum**: 64KB (strict enforcement)
- **Recommended**: Aim for 50-60KB to leave buffer
- **Enforcement**: Slack will reject uploads exceeding 64KB

### Dimensions
- **Optimal**: 128x128 pixels (square)
- **Maximum**: 256x256 pixels
- **Minimum**: No official minimum, but recommend 64x64+
- **Aspect Ratio**: Square (1:1) recommended
  - Non-square images will be cropped to square

### File Formats
- **Supported**: PNG, GIF, JPEG
- **Recommended**: PNG with transparency
- **Animated**: GIF animations supported (under 64KB)

### Color Depth
- No official limit
- Recommendation: 32-48 colors for static emojis
- More colors = larger file size

## Display Contexts

Slack displays custom emojis in multiple contexts at different sizes:

### Message Text (inline)
- **Size**: 20px × 20px
- **Context**: Within text messages
- **Example**: "Great work :thumbs_up:"

### Reactions
- **Size**: 20px × 20px
- **Context**: Added as reactions to messages
- **Example**: 👍 reaction bubbles

### Emoji Picker Preview
- **Size**: 64px × 64px
- **Context**: When browsing emoji picker
- **Example**: Grid of available emojis

### Large Preview (hover)
- **Size**: 128px × 128px
- **Context**: Hovering over emoji in picker
- **Example**: Enlarged view when selecting

## Best Practices

### Design Guidelines

1. **Simple and Clear**
   - Emojis should be recognizable at 20px size
   - Avoid intricate details that disappear when scaled down
   - Use bold, clear shapes

2. **High Contrast**
   - Ensure good contrast between foreground and background
   - Dark outlines help with visibility
   - Avoid light colors on white backgrounds

3. **Transparency**
   - Use PNG with alpha channel for best results
   - Transparent backgrounds integrate better with Slack themes
   - Consider how emoji looks on both light and dark backgrounds

4. **Consistent Style**
   - Match existing emoji style in your workspace
   - Keep branding consistent if creating a set
   - Use similar color palettes across related emojis

### Technical Optimization

1. **Color Reduction**
   - Limit to 32-48 colors for static emojis
   - Use indexed color (PNG-8) instead of true color (PNG-24) when possible
   - Posterize gradients to solid colors

2. **Compression**
   - Use PNG optimization tools (pngcrush, optipng, pngquant)
   - Enable PNG interlacing for progressive loading
   - Remove metadata (EXIF, comments) to save space

3. **Avoid**
   - Gradients (increase file size significantly)
   - Textures and noise (compress poorly)
   - Fine details that disappear at small sizes
   - Transparent layers that aren't needed

## Upload Process

### Via Web Interface

1. Go to workspace settings
2. Click "Customize" or "Customize [Workspace Name]"
3. Select "Emoji" tab
4. Click "Add Custom Emoji"
5. Upload image file (must be under 64KB)
6. Give it a name (e.g., `:my_emoji:`)
7. Click "Save"

### Naming Conventions

- Use lowercase letters, numbers, underscores, and hyphens
- No spaces allowed
- Descriptive names (`:happy_cat:` not `:hc:`)
- Consider searchability (users type to find emojis)
- Avoid conflicts with existing emoji names

### Permissions

- **Free workspaces**: All members can add emojis (default)
- **Paid workspaces**: Admins can restrict who can add emojis
- **Enterprise Grid**: Organization-level emoji management available

## Common Issues and Solutions

### Issue: "File is too large"
**Solution**:
- Reduce number of colors (try 32 colors)
- Use flat colors instead of gradients
- Simplify the design
- Use aggressive PNG compression
- Consider reducing dimensions to 112x112 or 96x96

### Issue: Emoji looks blurry
**Solution**:
- Start with higher resolution source image
- Use crisp, vector-based designs when possible
- Avoid upscaling small images
- Use proper resampling (LANCZOS) when resizing

### Issue: Details not visible at small size
**Solution**:
- Simplify the design
- Increase contrast
- Use bold outlines
- Remove fine details
- Test at 20px size before uploading

### Issue: Transparency not working
**Solution**:
- Ensure PNG format with alpha channel (RGBA)
- Check that transparency was preserved during editing
- Avoid JPEG (doesn't support transparency)
- Use PNG-24 or PNG-32 for full transparency

### Issue: Colors look different after upload
**Solution**:
- Use sRGB color space
- Avoid embedded color profiles
- Preview on both light and dark Slack themes
- Test with typical background colors

## Animated GIF Emojis

### Additional Requirements
- Still must be under 64KB (very challenging!)
- Typical frame count: 8-15 frames maximum
- Typical FPS: 10-15 frames per second
- Total duration: 1-2 seconds recommended

### Optimization Strategies
1. Limit to 10-12 frames total
2. Use very limited color palette (8-16 colors)
3. Optimize each frame individually
4. Use frame disposal methods wisely
5. Consider lossy GIF compression

### Tools
- gifsicle - CLI GIF optimizer
- ImageMagick - Convert and optimize
- Photoshop "Save for Web" - Manual optimization
- Online tools (ezgif.com) - Web-based optimization

## Emoji Sets and Consistency

### Creating a Set
- Maintain consistent size across all emojis
- Use same color palette
- Match stylistic approach (outline width, shading)
- Design for 20px display size

### Naming Sets
- Use prefixes for related emojis
  - `:brand_logo_blue:`, `:brand_logo_red:`
  - `:team_alice:`, `:team_bob:`, `:team_charlie:`
- Makes searching and organizing easier

## Advanced Techniques

### Skin Tone Variations
- Create separate emojis for different skin tones
- Name with suffixes: `:wave_light:`, `:wave_medium:`, `:wave_dark:`
- Slack doesn't have built-in skin tone picker for custom emojis

### Seasonal Variants
- Create seasonal versions of popular emojis
- Example: `:logo_default:`, `:logo_halloween:`, `:logo_christmas:`
- Update description or pin announcement when releasing

### Branded Emojis
- Use company colors and style
- Consider trademark and copyright
- Maintain consistency with brand guidelines
- Great for internal culture and engagement

## Testing Checklist

Before uploading:
- [ ] File size under 64KB
- [ ] Dimensions are 128x128 (or smaller square)
- [ ] Format is PNG with transparency
- [ ] Recognizable at 20px size
- [ ] High contrast against light backgrounds
- [ ] High contrast against dark backgrounds
- [ ] No fine details that disappear when small
- [ ] Colors are vibrant and clear
- [ ] Outline is visible and crisp
- [ ] Transparent background (if applicable)
- [ ] Descriptive, searchable name chosen

## Resources

### Official Slack Documentation
- [Add custom emoji](https://slack.com/help/articles/206870177-Add-custom-emoji)
- [Customize your workspace](https://slack.com/help/articles/206845317-Customize-your-workspace)

### Community Resources
- [Slackmojis](https://slackmojis.com/) - Free emoji collection
- [Emoji Builder](https://emoji.build/) - Online emoji creator
- [Custom Emoji Guide](https://slack.com/intl/en-in/blog/collaboration/custom-emoji-guide)

### Optimization Tools
- [TinyPNG](https://tinypng.com/) - PNG compression
- [PNGOUT](http://advsys.net/ken/utils.htm) - Advanced PNG optimizer
- [ImageOptim](https://imageoptim.com/) - Mac image optimizer
- [pngquant](https://pngquant.org/) - Color quantization

## Legal Considerations

### Copyright
- Only upload images you have rights to use
- Don't use copyrighted characters without permission
- Celebrity images may require rights clearance
- Respect trademark rights

### Content Policy
- Follow Slack's Acceptable Use Policy
- Respect workplace professional standards
- Avoid offensive or inappropriate content
- Consider cultural sensitivity

### Ownership
- Custom emojis uploaded to workspace are shared
- Anyone in workspace can use uploaded emojis
- Workspace owners can remove emojis
- Emojis don't transfer if you leave workspace

## Statistics and Limits

### Per Workspace
- **No official emoji limit** (practically unlimited)
- Most workspaces have 100-1000 custom emojis
- Large workspaces can have 5000+ emojis

### Per Upload Session
- Upload one emoji at a time via web UI
- Bulk upload requires admin tools or API

### Usage Analytics
- Slack doesn't provide emoji usage statistics (by default)
- Third-party apps can track emoji usage
- Popular emojis often become cultural touchstones

## Future-Proofing

### Design for Scale
- Create emojis at 256x256, downscale to 128x128
- Keep source files (PSD, AI) for future edits
- Document color codes for consistency
- Consider how emoji might evolve

### Slack Updates
- Slack may change requirements in future
- Stay updated with Slack changelog
- Test emojis when Slack updates UI
- Be prepared to update popular emojis

## Conclusion

Creating great Slack emojis is both art and science:
- **Art**: Design appealing, expressive, recognizable icons
- **Science**: Optimize file size, colors, and dimensions

Follow these specifications and best practices to create emojis that:
- Meet technical requirements (under 64KB)
- Look great at all display sizes (20px to 128px)
- Work on both light and dark themes
- Enhance workplace communication and culture

Happy emoji creating! 🎨
