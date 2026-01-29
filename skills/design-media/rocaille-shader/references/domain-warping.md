# Domain Warping Theory

Domain warping is a technique for creating complex, organic patterns by transforming the input coordinates of a function before evaluating it. This document covers the mathematical foundation and practical applications.

## Core Concept

Instead of evaluating a function `f(p)` directly, we first transform the coordinates:

```
result = f(p + g(p))
```

Where:
- `p` is the original coordinate
- `g(p)` is a displacement function
- `f()` is the final evaluation function

The displacement `g(p)` "warps" the domain of `f`, hence "domain warping."

## Mathematical Foundation

### Basic Domain Warping

The simplest form uses noise or trigonometric functions:

```glsl
// Using noise
vec2 warped = p + fbm(p);
float result = fbm(warped);

// Using sin
vec2 warped = p + sin(p.yx * frequency);
float result = 1.0 / length(warped);
```

### Nested Domain Warping

Applying the warp multiple times creates more complex patterns:

```glsl
vec2 q = p + g(p);
vec2 r = q + g(q);
vec2 s = r + g(r);
float result = f(s);
```

Each layer adds more organic complexity.

### The Rocaille Formula

The Rocaille technique uses a specific warping function:

```glsl
g(p) = sin(p.yx + time) / amplitude
```

Key properties:
1. **Coordinate swap (`p.yx`)**: Creates rotational coupling
2. **Time offset**: Enables animation
3. **Amplitude divisor**: Controls warp strength
4. **Sine function**: Smooth, bounded displacement (-1 to 1)

## Why Coordinate Swapping Works

When we write `sin(p.yx + t)`:

```glsl
displacement.x = sin(p.y + t);
displacement.y = sin(p.x + t);
```

This creates a feedback loop:
- X position affects Y displacement
- Y position affects X displacement
- The result is rotational/swirling motion rather than linear waves

Without the swap (`sin(p.xy + t)`), you get parallel waves instead of swirls.

## Amplitude Control

The divisor in `sin(p.yx + t) / amplitude` determines warp intensity:

| Amplitude | Effect |
|-----------|--------|
| 0.5 | Extreme distortion, may break pattern |
| 1.0 | Strong warping, dramatic effect |
| 2.0 | Balanced (standard Rocaille) |
| 4.0 | Subtle, gentle motion |
| 8.0 | Nearly imperceptible |

## Iteration Effects

Each iteration compounds the warping:

```
Iteration 1: p' = p + g(p)
Iteration 2: p'' = p' + g(p') = p + g(p) + g(p + g(p))
Iteration 3: p''' = p'' + g(p'') = ...
```

The compound effect:
- **1-2 iterations**: Simple wave patterns
- **3-5 iterations**: Organic, flowing shapes
- **6-9 iterations**: Complex, almost fractal detail
- **10+ iterations**: Chaotic, potentially unstable

## Inigo Quilez's Formulation

Inigo Quilez popularized domain warping with FBM (Fractional Brownian Motion):

```glsl
float pattern(vec2 p) {
    vec2 q = vec2(
        fbm(p + vec2(0.0, 0.0)),
        fbm(p + vec2(5.2, 1.3))
    );

    vec2 r = vec2(
        fbm(p + 4.0*q + vec2(1.7, 9.2)),
        fbm(p + 4.0*q + vec2(8.3, 2.8))
    );

    return fbm(p + 4.0*r);
}
```

This uses:
- FBM as the warping function (instead of sin)
- Different offset vectors for variety
- Scale multipliers (4.0) to control warp magnitude

## Comparison: FBM vs Sinusoidal Warping

| Aspect | FBM Warping | Sinusoidal (Rocaille) |
|--------|-------------|----------------------|
| Computation | Expensive (multiple octaves) | Cheap (single sin) |
| Pattern | Cloudy, natural | Swirling, flowing |
| Animation | Requires noise evolution | Natural with time offset |
| Control | Many parameters | Few parameters |
| Use case | Terrain, clouds | Light effects, UI |

## Practical Applications

### Backgrounds and Ambience

Low iteration counts for subtle movement:

```glsl
for(int i = 0; i < 3; i++) {
    uv += sin(uv.yx + time * 0.5) / 4.0;
}
```

### Hero Visuals

Standard iteration count with color:

```glsl
for(int i = 0; i < 5; i++) {
    uv += sin(uv.yx + time) / 2.0;
}
vec3 color = 0.5 + 0.5 * cos(atan(uv.y, uv.x) + vec3(0, 2, 4));
```

### Music Visualizers

React to audio input:

```glsl
float bass = audioData.x;
for(int i = 0; i < 7; i++) {
    uv += sin(uv.yx + time) / (2.0 - bass);
}
```

### Loading Indicators

Simplified for performance:

```glsl
uv += sin(uv.yx + time * 2.0) / 3.0;
uv += sin(uv.yx + time * 2.0) / 3.0;
```

## Combining with Other Techniques

### With Noise

```glsl
for(int i = 0; i < 5; i++) {
    uv += sin(uv.yx + time + noise(uv * 10.0)) / 2.0;
}
```

### With Distance Fields

```glsl
float sdf = sdCircle(uv, 0.3);
for(int i = 0; i < 5; i++) {
    uv += sin(uv.yx + time) / 2.0;
}
sdf = mix(sdf, sdCircle(uv, 0.3), 0.5);
```

### With Post-Processing

```glsl
// Warped coordinates
for(int i = 0; i < 5; i++) {
    uv += sin(uv.yx + time) / 2.0;
}

// Apply bloom
vec3 color = texture(scene, uv).rgb;
color += blur(scene, uv) * 0.5;
```

## References

- Inigo Quilez: [Domain Warping](https://iquilezles.org/articles/warp/)
- Riccardo Scalco: [Coordinate Spaces Tutorial](https://www.riccardoscalco.it/blog/)
- The Art of Code: [Procedural Patterns](https://www.youtube.com/c/TheArtofCodeIsCool)
