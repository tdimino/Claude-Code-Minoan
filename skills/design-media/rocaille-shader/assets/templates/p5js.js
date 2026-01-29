/**
 * Rocaille Shader - P5.js Implementation
 *
 * Domain warping with sinusoidal displacement for organic swirling effects.
 *
 * Usage:
 * 1. Include this file in your P5.js sketch
 * 2. Call setup() and draw() as normal
 *
 * Or copy the shader code directly into your P5.js editor.
 */

// Configuration - adjust these values
const CONFIG = {
    warpCount: 5,      // Number of warp iterations (1-15)
    amplitude: 2.0,    // Warp intensity divisor
    speed: 1.0,        // Animation speed
    colorMode: 'rainbow' // 'rainbow', 'basic', 'neon', 'fire', 'ocean'
};

// Color mode GLSL code
const colorModes = {
    rainbow: `
        vec3 color = 0.5 + 0.5 * cos(atan(v.y, v.x) + vec3(0.0, 2.094, 4.188));
        color *= d * 0.15;
    `,
    basic: `
        vec3 color = vec3(d * 0.1);
    `,
    neon: `
        vec3 color = vec3(d * 0.3, d * 0.05, d * 0.4);
    `,
    fire: `
        vec3 color = vec3(d * 0.4, d * 0.15, d * 0.02);
    `,
    ocean: `
        vec3 color = vec3(d * 0.02, d * 0.2, d * 0.35);
    `
};

// Generate fragment shader with current config
function getFragmentShader() {
    return `
        precision highp float;

        uniform vec2 u_resolution;
        uniform float u_time;

        void main() {
            vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution) / u_resolution.y;
            vec2 v = uv;
            float t = u_time * ${CONFIG.speed.toFixed(1)};

            for(int i = 0; i < ${CONFIG.warpCount}; i++) {
                v += sin(v.yx + t) / ${CONFIG.amplitude.toFixed(1)};
            }

            float d = 1.0 / max(length(v), 0.001);
            ${colorModes[CONFIG.colorMode]}

            gl_FragColor = vec4(color, 1.0);
        }
    `;
}

const vertexShader = `
    attribute vec3 aPosition;

    void main() {
        vec4 positionVec4 = vec4(aPosition, 1.0);
        positionVec4.xy = positionVec4.xy * 2.0 - 1.0;
        gl_Position = positionVec4;
    }
`;

let rocailleShader;

function setup() {
    createCanvas(windowWidth, windowHeight, WEBGL);
    noStroke();

    // Create shader
    rocailleShader = createShader(vertexShader, getFragmentShader());
}

function draw() {
    shader(rocailleShader);

    // Set uniforms
    rocailleShader.setUniform('u_resolution', [width * pixelDensity(), height * pixelDensity()]);
    rocailleShader.setUniform('u_time', millis() / 1000.0);

    // Draw full-screen quad
    rect(0, 0, width, height);
}

function windowResized() {
    resizeCanvas(windowWidth, windowHeight);
}

// Helper functions to update config at runtime
function setWarpCount(count) {
    CONFIG.warpCount = Math.max(1, Math.min(15, count));
    rocailleShader = createShader(vertexShader, getFragmentShader());
}

function setAmplitude(amp) {
    CONFIG.amplitude = Math.max(0.5, Math.min(4.0, amp));
    rocailleShader = createShader(vertexShader, getFragmentShader());
}

function setSpeed(spd) {
    CONFIG.speed = Math.max(0.1, Math.min(3.0, spd));
    rocailleShader = createShader(vertexShader, getFragmentShader());
}

function setColorMode(mode) {
    if (colorModes[mode]) {
        CONFIG.colorMode = mode;
        rocailleShader = createShader(vertexShader, getFragmentShader());
    }
}

// Keyboard controls
function keyPressed() {
    if (key === '1') setColorMode('rainbow');
    if (key === '2') setColorMode('basic');
    if (key === '3') setColorMode('neon');
    if (key === '4') setColorMode('fire');
    if (key === '5') setColorMode('ocean');

    if (key === 'ArrowUp') setWarpCount(CONFIG.warpCount + 1);
    if (key === 'ArrowDown') setWarpCount(CONFIG.warpCount - 1);

    if (key === 'ArrowRight') setAmplitude(CONFIG.amplitude - 0.2);
    if (key === 'ArrowLeft') setAmplitude(CONFIG.amplitude + 0.2);
}

/*
================================================================================
STANDALONE SKETCH VERSION
================================================================================
Copy everything below into a new P5.js sketch for a self-contained version:

let rocailleShader;

const fragShader = `
    precision highp float;
    uniform vec2 u_resolution;
    uniform float u_time;

    void main() {
        vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution) / u_resolution.y;
        vec2 v = uv;
        float t = u_time;

        for(int i = 0; i < 5; i++) {
            v += sin(v.yx + t) / 2.0;
        }

        float d = 1.0 / max(length(v), 0.001);
        vec3 color = 0.5 + 0.5 * cos(atan(v.y, v.x) + vec3(0.0, 2.094, 4.188));
        color *= d * 0.15;

        gl_FragColor = vec4(color, 1.0);
    }
`;

const vertShader = `
    attribute vec3 aPosition;
    void main() {
        vec4 positionVec4 = vec4(aPosition, 1.0);
        positionVec4.xy = positionVec4.xy * 2.0 - 1.0;
        gl_Position = positionVec4;
    }
`;

function setup() {
    createCanvas(windowWidth, windowHeight, WEBGL);
    noStroke();
    rocailleShader = createShader(vertShader, fragShader);
}

function draw() {
    shader(rocailleShader);
    rocailleShader.setUniform('u_resolution', [width * pixelDensity(), height * pixelDensity()]);
    rocailleShader.setUniform('u_time', millis() / 1000.0);
    rect(0, 0, width, height);
}

function windowResized() {
    resizeCanvas(windowWidth, windowHeight);
}
*/
