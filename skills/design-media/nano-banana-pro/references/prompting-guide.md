# Nano Banana Pro Prompting Guide

Best practices for creating high-quality images with Google's Nano Banana Pro (Gemini 3 Pro Image).

## Table of Contents

- [Core Prompt Structure](#core-prompt-structure)
- [Best Practices](#best-practices)
- [Lighting Techniques](#lighting-techniques)
- [Multi-Turn Editing](#multi-turn-editing)
- [Common Pitfalls](#common-pitfalls)
- [Example Prompts](#example-prompts)

## Core Prompt Structure

The most effective prompt structure follows this pattern:

```
[Subject] + [Style/Medium] + [Lighting Details] + [Camera/Composition] + [Quality Modifiers]
```

### Formula Breakdown

**For Image Generation:**
```
Subject + Action + Environment + Art Style + Lighting + Details
```

**For Image Editing:**
```
Action/Change + Specific Element + Desired Style/Effect + Relevant Details
```

**Key Editing Action Words:**
- **Add** - Insert new elements
- **Change** - Modify existing elements
- **Make** - Transform properties
- **Remove** - Delete elements
- **Replace** - Swap one element for another

## Best Practices

### 1. Be Specific, Not Vague

❌ Bad: "a cat"
✅ Good: "fluffy orange British shorthair kitten sitting on a marble countertop, soft morning light"

### 2. Use Layered Descriptions

Add depth by describing:
- **Atmosphere** - mood, weather, time of day
- **Materials** - textures, finishes, composition
- **Mood** - emotional tone, feeling

✅ Example: "Cozy coffee shop interior, warm amber lighting, rain visible through large windows, steam rising from ceramic mug on reclaimed wood table"

### 3. Leverage Cinematic Language

Nano Banana Pro responds very well to film terminology:

**Focal Length:**
- "wide-angle 24mm lens" (expansive scenes)
- "50mm standard lens" (natural perspective)
- "85mm portrait lens" (flattering portraits)
- "telephoto 200mm" (compressed backgrounds)

**Aperture & Depth:**
- "f/1.4 shallow depth of field, bokeh background"
- "f/8 sharp throughout"
- "macro close-up, extreme shallow DOF"

**Camera Angles:**
- "low-angle shot looking up"
- "overhead bird's eye view"
- "Dutch angle tilt"
- "over-the-shoulder perspective"

### 4. Describe Lighting Carefully

Lighting is one of the strongest influence factors.

**Quality:**
- "soft diffused north-facing window light"
- "harsh direct sunlight with hard shadows"
- "even studio lighting, no shadows"

**Direction:**
- "single key light from camera left at 45 degrees"
- "backlit silhouette with rim lighting"
- "three-point lighting setup"

**Color Temperature:**
- "warm golden hour sunlight, 3200K"
- "cool blue twilight, 6500K"
- "mixed lighting, warm practicals, cool ambient"

### 5. Avoid Overloading

Too many conflicting instructions can confuse the model.

❌ Bad: "photorealistic and illustrated and painted and abstract sunset over mountains with buildings and forest and ocean"

✅ Good: "photorealistic sunset over mountain range, soft golden light, few scattered clouds, foreground pine forest"

### 6. Use Negative Prompts (When Needed)

Specify what you don't want:
- "no blur"
- "no extra limbs"
- "no low detail"
- "no text overlays"
- "no watermarks"

## Lighting Techniques

### Natural Lighting

**Golden Hour:**
```
"golden hour sunlight, warm orange glow, long soft shadows, 30 minutes before sunset"
```

**Blue Hour:**
```
"blue hour twilight, deep blue sky gradient to orange horizon, city lights beginning to glow"
```

**Overcast:**
```
"overcast day, even diffused lighting, soft shadows, gray clouds"
```

### Studio Lighting

**Three-Point Setup:**
```
"studio three-point lighting, key light camera left, fill light camera right, rim light behind subject"
```

**Dramatic:**
```
"single dramatic key light, hard shadows, Rembrandt lighting pattern"
```

### Stylized Lighting

**Neon/Cyberpunk:**
```
"neon lighting, cyan and magenta glow, reflective wet surfaces, night scene"
```

**Cinematic:**
```
"cinematic color grading, teal and orange palette, film grain, anamorphic lens flares"
```

## Multi-Turn Editing

Nano Banana Pro excels at conversational, iterative refinement.

### Workflow

1. **Start Broad:**
   - "Generate a modern office workspace"

2. **Refine Specifics:**
   - "Make the desk wooden instead of metal"
   - "Add more plants near the window"

3. **Fine-Tune Details:**
   - "Make the lighting warmer"
   - "Add a laptop on the desk"

### Multi-Turn Best Practices

- Each edit should reference **one specific change**
- Be explicit about what to keep vs. change
- Use positional language: "in the foreground", "to the left", "in the background"

**Example Sequence:**

Turn 1: "Modern minimalist living room, large windows, neutral colors"
Turn 2: "Add a blue velvet sofa against the left wall"
Turn 3: "Change the sofa color to emerald green"
Turn 4: "Add warm sunset lighting through the windows"

## Common Pitfalls

### 1. Vague Style Instructions

❌ "make it look good"
✅ "photorealistic architectural photography style, sharp details, professional color grading"

### 2. Conflicting Requests

❌ "photorealistic illustration" (contradiction)
✅ Pick one: "photorealistic" OR "illustrated style"

### 3. Insufficient Context

❌ "add birds"
✅ "add three birds flying in the upper right background sky"

### 4. Overly Complex First Prompt

❌ Starting with a 500-word prompt with 20 requirements
✅ Start simple, iterate with follow-ups

## Example Prompts

### Photorealistic Portrait

```
Professional headshot portrait of a woman in her 30s, natural smile, soft studio lighting
with octagonal softbox from camera left, neutral gray background, 85mm lens at f/2.8,
sharp focus on eyes, subtle bokeh background, commercial photography quality
```

### Product Photography

```
High-end product photography of a luxury watch on black marble surface, dramatic single
key light from top-left creating hard shadows, reflective surface showing watch details,
macro lens, f/5.6 for sharpness, commercial advertising quality, 4K resolution
```

### Landscape

```
Dramatic mountain landscape at sunset, jagged peaks silhouetted against vibrant orange
and purple sky, foreground alpine meadow with wildflowers, wide-angle 24mm lens,
f/11 for deep depth of field, no clouds in sky, national geographic style
```

### Architectural

```
Modern minimalist residential architecture, clean white walls, floor-to-ceiling glass
windows, concrete and wood accents, afternoon natural light creating geometric shadows,
architectural photography, straight-on perspective, symmetrical composition, sharp focus
throughout
```

### Illustration Style

```
Cozy children's book illustration of a forest cottage, warm and inviting, watercolor
style with soft edges, dappled sunlight through trees, whimsical mushrooms in foreground,
hand-drawn aesthetic, warm color palette dominated by greens and browns
```

### Abstract/Artistic

```
Abstract expressionist composition, bold brushstrokes in deep blues and vibrant oranges,
dynamic movement suggesting ocean waves, textured paint application, contemporary art
gallery quality, non-representational
```

## Technical Details for Best Results

### Resolution Pathways

- **1K**: Quick iterations, faster generation
- **2K**: Balanced quality and speed
- **4K**: Maximum detail, professional output (costs more)

### Aspect Ratios

- **1:1** - Square, social media posts
- **16:9** - Widescreen, presentations, video thumbnails
- **9:16** - Vertical, mobile, stories
- **4:3** - Standard, classic photography
- **3:4** - Portrait orientation

### Temperature Settings

- **0.3-0.5**: Precise, consistent, photorealistic
- **0.7** (default): Balanced creativity and consistency
- **0.8-1.0**: More creative variation, artistic styles

## Advanced Techniques

### Reference Image Consistency

Upload up to 14 reference images to maintain:
- Character consistency across scenes
- Brand visual identity
- Specific product angles
- Style matching

### Grounding with Google Search

Enable grounding for:
- Factual accuracy (real locations, maps)
- Current events
- Specific products or people
- Technical diagrams requiring real-world data

### Text Rendering

For legible text in images:
- Keep text under **25 characters** for best clarity
- Specify exact wording in quotes
- Request specific font styles if needed
- Example: "Add text 'GRAND OPENING' in bold sans-serif font at the top"

## Quality Optimization Tips

1. **Start with high-quality inputs** when editing (min 1024px)
2. **Iterate gradually** rather than making all changes at once
3. **Use specific terminology** from photography/cinematography
4. **Reference real-world examples** in your prompts
5. **Test different temperatures** for your use case
6. **Leverage multi-turn** for complex compositions
