# Rocaille Shader - Complete Breakdown

This document provides a step-by-step breakdown of the Rocaille domain warping technique, showing how each layer builds upon the previous to create organic, swirling light effects.

## The 8-Step Progression

### Step 01: Coordinate System

Set up normalized UV coordinates centered at the origin with aspect ratio correction.

```glsl
vec2 uv = (fragCoord - 0.5 * iResolution.xy) / iResolution.y;
vec2 v = uv;
```

**What this does:**
- `fragCoord` is the pixel position (0 to resolution)
- Subtracting `0.5 * iResolution.xy` centers the origin
- Dividing by `iResolution.y` normalizes to -0.5 to 0.5 range (vertically)
- Result: coordinate system where (0,0) is screen center

### Step 02: Distance Field

Create a radial falloff from the center using inverse distance.

```glsl
float d = 1.0 / length(v);
fragColor = vec4(vec3(d * 0.1), 1.0);
```

**What this does:**
- `length(v)` gives distance from origin (0 at center, increasing outward)
- `1.0 / length(v)` inverts: infinite at center, approaching 0 at edges
- Multiply by 0.1 to control intensity
- Creates a bright point at center fading to darkness

**Visual result:** Single bright spot in the center, falling off radially.

### Step 03: Single Warp

Apply the first sinusoidal displacement.

```glsl
v += sin(v.yx + t) / 1.0;
```

**Breaking down the formula:**
- `v.yx` swaps x and y coordinates (creates rotation/swirl)
- `+ t` adds time for animation
- `sin()` creates smooth oscillation between -1 and 1
- `/ 1.0` controls amplitude (dividing by 1 = full strength)
- `+=` adds the displacement to original coordinates

**Visual result:** The distance field now wobbles and shifts, creating a single wave distortion.

### Step 04: Two Warps

Apply the displacement twice.

```glsl
for(int i = 0; i < 2; i++) {
    v += sin(v.yx + t) / 2.0;
}
```

**What changes:**
- Each iteration uses the already-displaced coordinates
- Division by 2.0 reduces each warp's strength
- Compound effect: warp of a warp

**Visual result:** More complex distortion patterns emerge. The single wave becomes interleaved.

### Step 05: Five Warps

The sweet spot for organic effects.

```glsl
for(int i = 0; i < 5; i++) {
    v += sin(v.yx + t) / 2.0;
}
```

**What happens:**
- Five iterations of coordinate displacement
- Each iteration compounds on the previous
- Patterns become organic and flowing

**Visual result:** Smooth, organic swirling patterns. This is the "classic" Rocaille look.

### Step 06: Nine Warps

Pushing toward complexity.

```glsl
for(int i = 0; i < 9; i++) {
    v += sin(v.yx + t) / 2.0;
}
```

**What happens:**
- Near the edge of stable patterns
- Very complex, intertwined forms
- Can start to show aliasing at lower resolutions

**Visual result:** Highly intricate, almost fractal-like swirling patterns.

### Step 07: Basic Coloring

Add color based on the distance field.

```glsl
float d = 1.0 / length(v);
vec3 color = vec3(d * 0.2, d * 0.1, d * 0.05);
fragColor = vec4(color, 1.0);
```

**Color mapping approach:**
- Use `d` (distance) to drive color channels differently
- Higher multiplier = brighter that channel
- Example creates warm orange/yellow tones

**Visual result:** Colored version of the warped pattern, monochromatic gradient.

### Step 08: Rainbow Colors

Full spectrum coloring based on angle.

```glsl
vec3 color = 0.5 + 0.5 * cos(atan(v.y, v.x) + vec3(0.0, 2.094, 4.188));
```

**Breaking down the rainbow:**
- `atan(v.y, v.x)` gives angle from center (-π to π)
- Adding `vec3(0, 2.094, 4.188)` offsets R, G, B by 120° each
- `cos()` maps angle to smooth color wave
- `0.5 + 0.5 *` shifts from -1,1 to 0,1 range

**Visual result:** Full rainbow spectrum following the swirl patterns.

## The Core Formula Explained

```glsl
v += sin(v.yx + t) / amplitude;
```

### Why `v.yx`?

Swapping x and y creates a coupling between horizontal and vertical movement:
- Horizontal position affects vertical displacement
- Vertical position affects horizontal displacement
- This coupling creates rotation/swirl rather than simple waves

### Why Divide by Amplitude?

The divisor controls how much each iteration displaces:
- `/ 1.0` = Full strength, dramatic warping
- `/ 2.0` = Standard, balanced warping
- `/ 4.0` = Subtle, gentle warping

Lower divisors (stronger warping) can cause:
- More dramatic distortion
- Potential pattern breakdown at high iterations
- More aliasing artifacts

### Why Iterate?

Each iteration warps already-warped coordinates:
- Iteration 1: Simple wave
- Iteration 2: Wave of a wave
- Iteration N: Deeply nested transformation

The compound effect creates organic complexity that would be impossible to describe with a single formula.

## Variation Techniques

### Changing the Base Shape

Replace `1.0 / length(v)` with:

```glsl
// Rings
float d = sin(length(v) * 10.0);

// Diamond
float d = 1.0 / (abs(v.x) + abs(v.y));

// Square
float d = 1.0 / max(abs(v.x), abs(v.y));

// Cross
float d = 1.0 / min(abs(v.x), abs(v.y));
```

### Modifying the Warp

```glsl
// Asymmetric warp
v += sin(v.yx * vec2(1.0, 1.5) + t) / 2.0;

// Different frequencies per axis
v.x += sin(v.y * 2.0 + t) / 2.0;
v.y += sin(v.x * 3.0 + t) / 2.0;

// Exponential falloff
v += sin(v.yx + t) / (2.0 + float(i));
```

### Time Variations

```glsl
// Different speed per axis
float tx = t * 1.0;
float ty = t * 0.7;
v += sin(v.yx + vec2(tx, ty)) / 2.0;

// Pulsing amplitude
float amp = 2.0 + sin(t * 0.5);
v += sin(v.yx + t) / amp;
```

## Performance Considerations

### Iteration Count vs. Quality

| Warps | GPU Load | Visual Complexity | Recommended Use |
|-------|----------|-------------------|-----------------|
| 1-3   | Low      | Subtle           | Backgrounds, mobile |
| 4-6   | Medium   | Balanced         | Main effects |
| 7-9   | High     | Complex          | Desktop, hero visuals |
| 10+   | Very High| Chaotic          | Experimental |

### Optimization Tips

1. **Reduce iterations on mobile:** Cap at 5 warps
2. **Lower resolution:** Render at 0.5x and upscale
3. **Simplify color:** Basic coloring cheaper than rainbow
4. **Cache sin lookups:** Minimal impact in modern GPUs but helps on older hardware
