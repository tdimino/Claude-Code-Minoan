# Common GLSL Patterns

This reference covers GLSL patterns frequently used in Rocaille and other procedural shaders.

## Coordinate Systems

### Normalized Screen Coordinates

Center origin, aspect-ratio corrected:

```glsl
vec2 uv = (fragCoord - 0.5 * iResolution.xy) / iResolution.y;
```

- Range: approximately -0.5 to 0.5 vertically
- Horizontal range depends on aspect ratio
- (0, 0) at screen center

### Alternative: 0-1 Range

```glsl
vec2 uv = fragCoord / iResolution.xy;
```

- Range: 0 to 1 both axes
- (0, 0) at bottom-left
- Useful for texture sampling

### Polar Coordinates

```glsl
float r = length(uv);           // Distance from center
float theta = atan(uv.y, uv.x); // Angle (-π to π)
```

Convert back to Cartesian:

```glsl
vec2 cartesian = r * vec2(cos(theta), sin(theta));
```

## Distance Fields

### Basic Shapes

```glsl
// Circle
float sdCircle(vec2 p, float r) {
    return length(p) - r;
}

// Box
float sdBox(vec2 p, vec2 b) {
    vec2 d = abs(p) - b;
    return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
}

// Line segment
float sdSegment(vec2 p, vec2 a, vec2 b) {
    vec2 pa = p - a, ba = b - a;
    float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    return length(pa - ba * h);
}
```

### Inverse Distance (Rocaille Base)

```glsl
float d = 1.0 / length(p);
```

Creates bright center, fading outward. The basis for Rocaille's glowing effect.

## Trigonometric Patterns

### Sinusoidal Waves

```glsl
// Horizontal waves
float wave = sin(uv.x * frequency + time);

// Circular waves (ripples)
float ripple = sin(length(uv) * frequency - time);
```

### Coordinate Swapping (Rocaille Core)

```glsl
// Creates swirling motion
vec2 displacement = sin(uv.yx + time);
```

The `.yx` swizzle is crucial - it creates rotational coupling.

### Smooth Oscillation

```glsl
// Range 0 to 1
float osc = 0.5 + 0.5 * sin(time);

// Range a to b
float osc = mix(a, b, 0.5 + 0.5 * sin(time));
```

## Color Techniques

### Rainbow from Angle

```glsl
// Full spectrum based on angle
vec3 rainbow = 0.5 + 0.5 * cos(angle + vec3(0.0, 2.094, 4.188));
```

The offsets (0, 2.094, 4.188) are 0°, 120°, 240° in radians.

### Palette Function (Inigo Quilez)

```glsl
vec3 palette(float t, vec3 a, vec3 b, vec3 c, vec3 d) {
    return a + b * cos(6.28318 * (c * t + d));
}

// Example: warm colors
vec3 color = palette(t,
    vec3(0.5), vec3(0.5),
    vec3(1.0), vec3(0.0, 0.33, 0.67)
);
```

### HSV to RGB

```glsl
vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0/3.0, 1.0/3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}
```

### Temperature Gradient

```glsl
vec3 temperature(float t) {
    // Blue (cold) to red (hot)
    return vec3(t, 0.0, 1.0 - t);
}
```

## Noise and Randomness

### Simple Hash

```glsl
float hash(vec2 p) {
    return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}
```

### Film Grain

```glsl
float grain = hash(uv + time) * 0.1;
color += grain;
```

### Value Noise

```glsl
float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f); // Smoothstep

    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));

    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}
```

## Blending and Compositing

### Smooth Minimum (Soft Union)

```glsl
float smin(float a, float b, float k) {
    float h = clamp(0.5 + 0.5 * (b - a) / k, 0.0, 1.0);
    return mix(b, a, h) - k * h * (1.0 - h);
}
```

### Screen Blend

```glsl
vec3 screen(vec3 a, vec3 b) {
    return 1.0 - (1.0 - a) * (1.0 - b);
}
```

### Additive Glow

```glsl
color += glow * glowIntensity;
```

## Post-Processing

### Vignette

```glsl
float vignette = 1.0 - length(uv) * vignetteStrength;
color *= vignette;
```

### Chromatic Aberration

```glsl
float r = texture(tex, uv + offset).r;
float g = texture(tex, uv).g;
float b = texture(tex, uv - offset).b;
vec3 color = vec3(r, g, b);
```

### Contrast Adjustment

```glsl
color = (color - 0.5) * contrast + 0.5;
```

### Gamma Correction

```glsl
color = pow(color, vec3(1.0 / 2.2));
```

## Animation Patterns

### Smooth Loop

```glsl
// Loops every 'duration' seconds
float t = mod(time, duration) / duration;
```

### Easing Functions

```glsl
// Ease in-out
float easeInOut(float t) {
    return t < 0.5
        ? 4.0 * t * t * t
        : 1.0 - pow(-2.0 * t + 2.0, 3.0) / 2.0;
}

// Smooth step (built-in)
float t = smoothstep(0.0, 1.0, t);
```

### Ping-Pong

```glsl
// Oscillates between 0 and 1
float pingPong = abs(mod(time, 2.0) - 1.0);
```

## Performance Tips

### Avoid Branching

```glsl
// Bad
if (x > 0.0) result = a;
else result = b;

// Good
result = mix(b, a, step(0.0, x));
```

### Use Built-in Functions

Built-ins like `length()`, `normalize()`, `dot()` are hardware-optimized.

### Reduce Texture Fetches

Each `texture()` call is expensive. Cache results when possible.

### Loop Unrolling

For small, fixed iteration counts, unrolled loops can be faster:

```glsl
// Instead of for loop with 3 iterations:
v += sin(v.yx + t) / 2.0;
v += sin(v.yx + t) / 2.0;
v += sin(v.yx + t) / 2.0;
```

## Common Gotchas

### Division by Zero

```glsl
// Dangerous
float d = 1.0 / length(p);

// Safe
float d = 1.0 / max(length(p), 0.001);
```

### Precision Issues

```glsl
// Use highp for coordinates
precision highp float;

// Avoid very large or small numbers
// Range ~0.001 to ~1000 is safest
```

### NaN Propagation

Check for NaN in debug:

```glsl
if (isnan(value)) color = vec3(1.0, 0.0, 1.0); // Magenta = NaN
```
