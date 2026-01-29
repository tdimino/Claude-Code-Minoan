// Rocaille Shader - Shadertoy Compatible
// Domain warping with sinusoidal displacement
//
// Parameters to customize:
// - WARP_COUNT: Number of iterations (1-15)
// - AMPLITUDE: Warp intensity divisor (1.0 = strong, 4.0 = subtle)
// - SPEED: Animation speed multiplier

#define WARP_COUNT 5
#define AMPLITUDE 2.0
#define SPEED 1.0

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    // Normalized coordinates centered at origin
    vec2 uv = (fragCoord - 0.5 * iResolution.xy) / iResolution.y;
    vec2 v = uv;

    // Time with speed multiplier
    float t = iTime * SPEED;

    // Progressive domain warping
    // Each iteration displaces coordinates using the previous result
    for(int i = 0; i < WARP_COUNT; i++) {
        v += sin(v.yx + t) / AMPLITUDE;
    }

    // Distance field - inverse distance creates bright center
    float d = 1.0 / max(length(v), 0.001);

    // Rainbow coloring based on angle
    // The vec3 offsets (0, 2.094, 4.188) are 0°, 120°, 240° in radians
    vec3 color = 0.5 + 0.5 * cos(atan(v.y, v.x) + vec3(0.0, 2.094, 4.188));

    // Apply distance field to color intensity
    color *= d * 0.15;

    fragColor = vec4(color, 1.0);
}

/*
VARIATIONS:

// Basic (grayscale)
vec3 color = vec3(d * 0.1);

// Monochrome (cool white)
vec3 color = vec3(0.9, 0.95, 1.0) * d * 0.15;

// Neon (purple/magenta)
vec3 color = vec3(d * 0.3, d * 0.05, d * 0.4);

// Fire (warm orange)
vec3 color = vec3(d * 0.4, d * 0.15, d * 0.02);

// Ocean (deep blue)
vec3 color = vec3(d * 0.02, d * 0.2, d * 0.35);

BASE SHAPE VARIATIONS:

// Rings
float d = sin(length(v) * 10.0);

// Diamond
float d = 1.0 / (abs(v.x) + abs(v.y));

// Square
float d = 1.0 / max(abs(v.x), abs(v.y));
*/
