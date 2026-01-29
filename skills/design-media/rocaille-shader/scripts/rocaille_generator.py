#!/usr/bin/env python3
"""
Rocaille Shader Generator

Generate customized domain warping shaders in multiple formats.
Creates organic swirling light effects through iterative sinusoidal displacement.

Usage:
    python rocaille_generator.py --warps 5 --color rainbow --format shadertoy
    python rocaille_generator.py --warps 9 --color neon --format threejs --demo
    python rocaille_generator.py --format all --amplitude 1.5 --speed 0.5
"""

import argparse
import sys
from pathlib import Path
from textwrap import dedent

# Color scheme definitions
COLOR_SCHEMES = {
    "basic": {
        "code": "vec3 color = vec3(d * 0.1);",
        "description": "Grayscale intensity"
    },
    "rainbow": {
        "code": "vec3 color = 0.5 + 0.5 * cos(atan(v.y, v.x) + vec3(0.0, 2.094, 4.188)); color *= d * 0.15;",
        "description": "Full spectrum based on angle"
    },
    "monochrome": {
        "code": "vec3 color = vec3(0.9, 0.95, 1.0) * d * 0.15;",
        "description": "Cool white/blue tones"
    },
    "neon": {
        "code": "vec3 color = vec3(d * 0.3, d * 0.05, d * 0.4);",
        "description": "Purple/magenta neon glow"
    },
    "fire": {
        "code": "vec3 color = vec3(d * 0.4, d * 0.15, d * 0.02);",
        "description": "Warm orange/red tones"
    },
    "ocean": {
        "code": "vec3 color = vec3(d * 0.02, d * 0.2, d * 0.35);",
        "description": "Deep blue/cyan tones"
    }
}


def generate_shadertoy(warps: int, color: str, amplitude: float, speed: float) -> str:
    """Generate Shadertoy-compatible GLSL shader."""
    color_code = COLOR_SCHEMES.get(color, COLOR_SCHEMES["rainbow"])["code"]

    return dedent(f'''\
        // Rocaille Shader - Domain Warping Effect
        // Warps: {warps} | Color: {color} | Amplitude: {amplitude}

        void mainImage(out vec4 fragColor, in vec2 fragCoord) {{
            // Normalized coordinates centered at origin
            vec2 uv = (fragCoord - 0.5 * iResolution.xy) / iResolution.y;
            vec2 v = uv;

            // Time with speed multiplier
            float t = iTime * {speed};

            // Progressive domain warping
            for(int i = 0; i < {warps}; i++) {{
                v += sin(v.yx + t) / {amplitude};
            }}

            // Distance field - radial falloff from warped center
            float d = 1.0 / max(length(v), 0.001);

            // Color mapping
            {color_code}

            fragColor = vec4(color, 1.0);
        }}
    ''')


def generate_threejs(warps: int, color: str, amplitude: float, speed: float) -> str:
    """Generate Three.js ShaderMaterial code."""
    color_code = COLOR_SCHEMES.get(color, COLOR_SCHEMES["rainbow"])["code"]

    return dedent(f'''\
        // Rocaille Shader - Three.js ShaderMaterial
        // Warps: {warps} | Color: {color}

        const RocailleShader = {{
            uniforms: {{
                uTime: {{ value: 0.0 }},
                uResolution: {{ value: new THREE.Vector2(window.innerWidth, window.innerHeight) }},
                uWarpCount: {{ value: {warps} }},
                uAmplitude: {{ value: {amplitude} }},
                uSpeed: {{ value: {speed} }}
            }},

            vertexShader: `
                varying vec2 vUv;
                void main() {{
                    vUv = uv;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }}
            `,

            fragmentShader: `
                uniform float uTime;
                uniform vec2 uResolution;
                uniform int uWarpCount;
                uniform float uAmplitude;
                uniform float uSpeed;
                varying vec2 vUv;

                void main() {{
                    vec2 uv = (vUv - 0.5) * vec2(uResolution.x / uResolution.y, 1.0);
                    vec2 v = uv;
                    float t = uTime * uSpeed;

                    for(int i = 0; i < {warps}; i++) {{
                        v += sin(v.yx + t) / uAmplitude;
                    }}

                    float d = 1.0 / max(length(v), 0.001);
                    {color_code}

                    gl_FragColor = vec4(color, 1.0);
                }}
            `
        }};

        // Usage:
        // const material = new THREE.ShaderMaterial(RocailleShader);
        // const mesh = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), material);
        //
        // In animation loop:
        // material.uniforms.uTime.value = performance.now() / 1000;

        export default RocailleShader;
    ''')


def generate_webgl(warps: int, color: str, amplitude: float, speed: float) -> str:
    """Generate vanilla WebGL2 implementation."""
    color_code = COLOR_SCHEMES.get(color, COLOR_SCHEMES["rainbow"])["code"]

    return dedent(f'''\
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rocaille Shader - WebGL2</title>
            <style>
                * {{ margin: 0; padding: 0; }}
                canvas {{ display: block; width: 100vw; height: 100vh; }}
            </style>
        </head>
        <body>
            <canvas id="canvas"></canvas>
            <script>
                const canvas = document.getElementById('canvas');
                const gl = canvas.getContext('webgl2');

                if (!gl) {{
                    alert('WebGL2 not supported');
                    throw new Error('WebGL2 not supported');
                }}

                // Vertex shader - full screen quad
                const vertexSource = `#version 300 es
                    in vec4 aPosition;
                    void main() {{
                        gl_Position = aPosition;
                    }}
                `;

                // Fragment shader - Rocaille effect
                const fragmentSource = `#version 300 es
                    precision highp float;
                    uniform float uTime;
                    uniform vec2 uResolution;
                    out vec4 fragColor;

                    void main() {{
                        vec2 uv = (gl_FragCoord.xy - 0.5 * uResolution) / uResolution.y;
                        vec2 v = uv;
                        float t = uTime * {speed};

                        for(int i = 0; i < {warps}; i++) {{
                            v += sin(v.yx + t) / {amplitude};
                        }}

                        float d = 1.0 / max(length(v), 0.001);
                        {color_code}

                        fragColor = vec4(color, 1.0);
                    }}
                `;

                function createShader(gl, type, source) {{
                    const shader = gl.createShader(type);
                    gl.shaderSource(shader, source);
                    gl.compileShader(shader);
                    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {{
                        console.error(gl.getShaderInfoLog(shader));
                        gl.deleteShader(shader);
                        return null;
                    }}
                    return shader;
                }}

                function createProgram(gl, vertexShader, fragmentShader) {{
                    const program = gl.createProgram();
                    gl.attachShader(program, vertexShader);
                    gl.attachShader(program, fragmentShader);
                    gl.linkProgram(program);
                    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {{
                        console.error(gl.getProgramInfoLog(program));
                        gl.deleteProgram(program);
                        return null;
                    }}
                    return program;
                }}

                const vertexShader = createShader(gl, gl.VERTEX_SHADER, vertexSource);
                const fragmentShader = createShader(gl, gl.FRAGMENT_SHADER, fragmentSource);
                const program = createProgram(gl, vertexShader, fragmentShader);

                // Full screen quad
                const positions = new Float32Array([
                    -1, -1, 1, -1, -1, 1,
                    -1, 1, 1, -1, 1, 1
                ]);

                const positionBuffer = gl.createBuffer();
                gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
                gl.bufferData(gl.ARRAY_BUFFER, positions, gl.STATIC_DRAW);

                const vao = gl.createVertexArray();
                gl.bindVertexArray(vao);

                const positionLoc = gl.getAttribLocation(program, 'aPosition');
                gl.enableVertexAttribArray(positionLoc);
                gl.vertexAttribPointer(positionLoc, 2, gl.FLOAT, false, 0, 0);

                const timeLoc = gl.getUniformLocation(program, 'uTime');
                const resolutionLoc = gl.getUniformLocation(program, 'uResolution');

                function resize() {{
                    canvas.width = window.innerWidth * devicePixelRatio;
                    canvas.height = window.innerHeight * devicePixelRatio;
                    gl.viewport(0, 0, canvas.width, canvas.height);
                }}

                window.addEventListener('resize', resize);
                resize();

                function render(time) {{
                    gl.useProgram(program);
                    gl.uniform1f(timeLoc, time * 0.001);
                    gl.uniform2f(resolutionLoc, canvas.width, canvas.height);
                    gl.drawArrays(gl.TRIANGLES, 0, 6);
                    requestAnimationFrame(render);
                }}

                requestAnimationFrame(render);
            </script>
        </body>
        </html>
    ''')


def generate_p5js(warps: int, color: str, amplitude: float, speed: float) -> str:
    """Generate P5.js shader mode code."""
    color_code = COLOR_SCHEMES.get(color, COLOR_SCHEMES["rainbow"])["code"]

    return dedent(f'''\
        // Rocaille Shader - P5.js Implementation
        // Warps: {warps} | Color: {color}

        let rocailleShader;

        const fragShader = `
            precision highp float;
            uniform vec2 u_resolution;
            uniform float u_time;

            void main() {{
                vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution) / u_resolution.y;
                vec2 v = uv;
                float t = u_time * {speed};

                for(int i = 0; i < {warps}; i++) {{
                    v += sin(v.yx + t) / {amplitude};
                }}

                float d = 1.0 / max(length(v), 0.001);
                {color_code}

                gl_FragColor = vec4(color, 1.0);
            }}
        `;

        const vertShader = `
            attribute vec3 aPosition;
            void main() {{
                vec4 positionVec4 = vec4(aPosition, 1.0);
                positionVec4.xy = positionVec4.xy * 2.0 - 1.0;
                gl_Position = positionVec4;
            }}
        `;

        function setup() {{
            createCanvas(windowWidth, windowHeight, WEBGL);
            noStroke();
            rocailleShader = createShader(vertShader, fragShader);
        }}

        function draw() {{
            shader(rocailleShader);
            rocailleShader.setUniform('u_resolution', [width * pixelDensity(), height * pixelDensity()]);
            rocailleShader.setUniform('u_time', millis() / 1000.0);
            rect(0, 0, width, height);
        }}

        function windowResized() {{
            resizeCanvas(windowWidth, windowHeight);
        }}
    ''')


def generate_interactive_demo(warps: int, color: str, amplitude: float, speed: float) -> str:
    """Generate interactive HTML demo with controls."""
    return dedent(f'''\
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rocaille Shader - Interactive Demo</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
                canvas {{ display: block; width: 100vw; height: 100vh; }}

                #controls {{
                    position: fixed;
                    top: 20px;
                    left: 20px;
                    background: rgba(0, 0, 0, 0.8);
                    padding: 20px;
                    border-radius: 12px;
                    color: white;
                    min-width: 280px;
                    backdrop-filter: blur(10px);
                }}

                #controls h2 {{
                    margin-bottom: 15px;
                    font-size: 18px;
                    font-weight: 600;
                }}

                .control-group {{
                    margin-bottom: 15px;
                }}

                .control-group label {{
                    display: block;
                    margin-bottom: 5px;
                    font-size: 12px;
                    color: #aaa;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}

                .control-group input[type="range"] {{
                    width: 100%;
                    margin-bottom: 5px;
                }}

                .control-group .value {{
                    font-size: 14px;
                    font-weight: 500;
                    color: #fff;
                }}

                .presets {{
                    display: flex;
                    gap: 8px;
                    flex-wrap: wrap;
                    margin-top: 15px;
                }}

                .presets button {{
                    padding: 8px 12px;
                    border: none;
                    border-radius: 6px;
                    background: #333;
                    color: white;
                    cursor: pointer;
                    font-size: 12px;
                    transition: background 0.2s;
                }}

                .presets button:hover {{
                    background: #555;
                }}

                #fps {{
                    position: fixed;
                    bottom: 20px;
                    left: 20px;
                    background: rgba(0, 0, 0, 0.6);
                    padding: 8px 12px;
                    border-radius: 6px;
                    color: #0f0;
                    font-family: monospace;
                    font-size: 14px;
                }}

                #help {{
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    background: rgba(0, 0, 0, 0.6);
                    padding: 8px 12px;
                    border-radius: 6px;
                    color: #888;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <canvas id="canvas"></canvas>

            <div id="controls">
                <h2>Rocaille Shader</h2>

                <div class="control-group">
                    <label>Warp Iterations</label>
                    <input type="range" id="warps" min="1" max="15" value="{warps}">
                    <span class="value" id="warps-value">{warps}</span>
                </div>

                <div class="control-group">
                    <label>Amplitude</label>
                    <input type="range" id="amplitude" min="0.5" max="4" step="0.1" value="{amplitude}">
                    <span class="value" id="amplitude-value">{amplitude}</span>
                </div>

                <div class="control-group">
                    <label>Speed</label>
                    <input type="range" id="speed" min="0.1" max="3" step="0.1" value="{speed}">
                    <span class="value" id="speed-value">{speed}</span>
                </div>

                <div class="control-group">
                    <label>Color Mode</label>
                    <select id="colorMode">
                        <option value="rainbow" {"selected" if color == "rainbow" else ""}>Rainbow</option>
                        <option value="basic" {"selected" if color == "basic" else ""}>Basic</option>
                        <option value="monochrome" {"selected" if color == "monochrome" else ""}>Monochrome</option>
                        <option value="neon" {"selected" if color == "neon" else ""}>Neon</option>
                        <option value="fire" {"selected" if color == "fire" else ""}>Fire</option>
                        <option value="ocean" {"selected" if color == "ocean" else ""}>Ocean</option>
                    </select>
                </div>

                <div class="presets">
                    <button onclick="setPreset(2, 2.0, 1.0, 'basic')">Subtle</button>
                    <button onclick="setPreset(5, 2.0, 1.0, 'rainbow')">Classic</button>
                    <button onclick="setPreset(9, 1.5, 0.8, 'neon')">Intense</button>
                    <button onclick="setPreset(12, 1.0, 0.5, 'fire')">Chaos</button>
                </div>
            </div>

            <div id="fps">-- FPS</div>
            <div id="help">F: Fullscreen | S: Screenshot | H: Hide controls</div>

            <script>
                const canvas = document.getElementById('canvas');
                const gl = canvas.getContext('webgl2');

                if (!gl) {{
                    alert('WebGL2 not supported');
                    throw new Error('WebGL2 not supported');
                }}

                // Shader source templates
                const vertexSource = `#version 300 es
                    in vec4 aPosition;
                    void main() {{ gl_Position = aPosition; }}
                `;

                const colorCodes = {{
                    basic: 'vec3 color = vec3(d * 0.1);',
                    rainbow: 'vec3 color = 0.5 + 0.5 * cos(atan(v.y, v.x) + vec3(0.0, 2.094, 4.188)); color *= d * 0.15;',
                    monochrome: 'vec3 color = vec3(0.9, 0.95, 1.0) * d * 0.15;',
                    neon: 'vec3 color = vec3(d * 0.3, d * 0.05, d * 0.4);',
                    fire: 'vec3 color = vec3(d * 0.4, d * 0.15, d * 0.02);',
                    ocean: 'vec3 color = vec3(d * 0.02, d * 0.2, d * 0.35);'
                }};

                function getFragmentSource(warps, amplitude, speed, colorMode) {{
                    return `#version 300 es
                        precision highp float;
                        uniform float uTime;
                        uniform vec2 uResolution;
                        out vec4 fragColor;

                        void main() {{
                            vec2 uv = (gl_FragCoord.xy - 0.5 * uResolution) / uResolution.y;
                            vec2 v = uv;
                            float t = uTime * ${{speed.toFixed(1)}};

                            for(int i = 0; i < ${{warps}}; i++) {{
                                v += sin(v.yx + t) / ${{amplitude.toFixed(1)}};
                            }}

                            float d = 1.0 / max(length(v), 0.001);
                            ${{colorCodes[colorMode]}}

                            fragColor = vec4(color, 1.0);
                        }}
                    `;
                }}

                function createShader(gl, type, source) {{
                    const shader = gl.createShader(type);
                    gl.shaderSource(shader, source);
                    gl.compileShader(shader);
                    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {{
                        console.error(gl.getShaderInfoLog(shader));
                        gl.deleteShader(shader);
                        return null;
                    }}
                    return shader;
                }}

                function createProgram(gl, vertexShader, fragmentShader) {{
                    const program = gl.createProgram();
                    gl.attachShader(program, vertexShader);
                    gl.attachShader(program, fragmentShader);
                    gl.linkProgram(program);
                    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {{
                        console.error(gl.getProgramInfoLog(program));
                        gl.deleteProgram(program);
                        return null;
                    }}
                    return program;
                }}

                // State
                let program, timeLoc, resolutionLoc;
                let currentWarps = {warps};
                let currentAmplitude = {amplitude};
                let currentSpeed = {speed};
                let currentColorMode = '{color}';

                function rebuildShader() {{
                    if (program) gl.deleteProgram(program);

                    const vertexShader = createShader(gl, gl.VERTEX_SHADER, vertexSource);
                    const fragmentShader = createShader(gl, gl.FRAGMENT_SHADER,
                        getFragmentSource(currentWarps, currentAmplitude, currentSpeed, currentColorMode));

                    program = createProgram(gl, vertexShader, fragmentShader);
                    timeLoc = gl.getUniformLocation(program, 'uTime');
                    resolutionLoc = gl.getUniformLocation(program, 'uResolution');
                }}

                // Setup geometry
                const positions = new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]);
                const positionBuffer = gl.createBuffer();
                gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
                gl.bufferData(gl.ARRAY_BUFFER, positions, gl.STATIC_DRAW);

                const vao = gl.createVertexArray();
                gl.bindVertexArray(vao);
                gl.enableVertexAttribArray(0);
                gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);

                rebuildShader();

                // Controls
                const warpsInput = document.getElementById('warps');
                const amplitudeInput = document.getElementById('amplitude');
                const speedInput = document.getElementById('speed');
                const colorModeSelect = document.getElementById('colorMode');

                warpsInput.oninput = () => {{
                    currentWarps = parseInt(warpsInput.value);
                    document.getElementById('warps-value').textContent = currentWarps;
                    rebuildShader();
                }};

                amplitudeInput.oninput = () => {{
                    currentAmplitude = parseFloat(amplitudeInput.value);
                    document.getElementById('amplitude-value').textContent = currentAmplitude.toFixed(1);
                    rebuildShader();
                }};

                speedInput.oninput = () => {{
                    currentSpeed = parseFloat(speedInput.value);
                    document.getElementById('speed-value').textContent = currentSpeed.toFixed(1);
                    rebuildShader();
                }};

                colorModeSelect.onchange = () => {{
                    currentColorMode = colorModeSelect.value;
                    rebuildShader();
                }};

                window.setPreset = (warps, amplitude, speed, colorMode) => {{
                    currentWarps = warps;
                    currentAmplitude = amplitude;
                    currentSpeed = speed;
                    currentColorMode = colorMode;

                    warpsInput.value = warps;
                    amplitudeInput.value = amplitude;
                    speedInput.value = speed;
                    colorModeSelect.value = colorMode;

                    document.getElementById('warps-value').textContent = warps;
                    document.getElementById('amplitude-value').textContent = amplitude.toFixed(1);
                    document.getElementById('speed-value').textContent = speed.toFixed(1);

                    rebuildShader();
                }};

                // Keyboard shortcuts
                document.addEventListener('keydown', (e) => {{
                    if (e.key === 'f' || e.key === 'F') {{
                        if (!document.fullscreenElement) {{
                            canvas.requestFullscreen();
                        }} else {{
                            document.exitFullscreen();
                        }}
                    }} else if (e.key === 's' || e.key === 'S') {{
                        const link = document.createElement('a');
                        link.download = `rocaille-${{currentWarps}}-${{currentColorMode}}.png`;
                        link.href = canvas.toDataURL('image/png');
                        link.click();
                    }} else if (e.key === 'h' || e.key === 'H') {{
                        const controls = document.getElementById('controls');
                        controls.style.display = controls.style.display === 'none' ? 'block' : 'none';
                    }}
                }});

                // Resize handler
                function resize() {{
                    canvas.width = window.innerWidth * devicePixelRatio;
                    canvas.height = window.innerHeight * devicePixelRatio;
                    gl.viewport(0, 0, canvas.width, canvas.height);
                }}
                window.addEventListener('resize', resize);
                resize();

                // FPS counter
                let frameCount = 0;
                let lastTime = performance.now();
                const fpsEl = document.getElementById('fps');

                // Render loop
                function render(time) {{
                    gl.useProgram(program);
                    gl.uniform1f(timeLoc, time * 0.001);
                    gl.uniform2f(resolutionLoc, canvas.width, canvas.height);
                    gl.drawArrays(gl.TRIANGLES, 0, 6);

                    // FPS
                    frameCount++;
                    if (time - lastTime >= 1000) {{
                        fpsEl.textContent = frameCount + ' FPS';
                        frameCount = 0;
                        lastTime = time;
                    }}

                    requestAnimationFrame(render);
                }}

                requestAnimationFrame(render);
            </script>
        </body>
        </html>
    ''')


def main():
    parser = argparse.ArgumentParser(
        description='Generate Rocaille domain warping shaders',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s --warps 5 --color rainbow --format shadertoy
  %(prog)s --warps 9 --color neon --format threejs
  %(prog)s --format all --amplitude 1.5 --speed 0.5
  %(prog)s --warps 7 --demo
        '''
    )

    parser.add_argument('--warps', '-w', type=int, default=5,
                        help='Number of warp iterations (1-15, default: 5)')
    parser.add_argument('--color', '-c', type=str, default='rainbow',
                        choices=list(COLOR_SCHEMES.keys()),
                        help='Color scheme (default: rainbow)')
    parser.add_argument('--format', '-f', type=str, default='shadertoy',
                        choices=['shadertoy', 'threejs', 'webgl', 'p5js', 'all'],
                        help='Output format (default: shadertoy)')
    parser.add_argument('--amplitude', '-a', type=float, default=2.0,
                        help='Warp intensity divisor (default: 2.0)')
    parser.add_argument('--speed', '-s', type=float, default=1.0,
                        help='Animation speed multiplier (default: 1.0)')
    parser.add_argument('--demo', '-d', action='store_true',
                        help='Generate interactive HTML demo')
    parser.add_argument('--output', '-o', type=str,
                        help='Output file path (prints to stdout if not specified)')

    args = parser.parse_args()

    # Validate warps
    if args.warps < 1 or args.warps > 15:
        print("Warning: Warp count should be between 1-15 for best results", file=sys.stderr)

    generators = {
        'shadertoy': (generate_shadertoy, '.glsl'),
        'threejs': (generate_threejs, '.js'),
        'webgl': (generate_webgl, '.html'),
        'p5js': (generate_p5js, '.js'),
    }

    outputs = []

    if args.demo:
        outputs.append(('interactive', generate_interactive_demo(
            args.warps, args.color, args.amplitude, args.speed), '.html'))
    elif args.format == 'all':
        for name, (gen_func, ext) in generators.items():
            outputs.append((name, gen_func(args.warps, args.color, args.amplitude, args.speed), ext))
    else:
        gen_func, ext = generators[args.format]
        outputs.append((args.format, gen_func(args.warps, args.color, args.amplitude, args.speed), ext))

    # Output
    if args.output and len(outputs) == 1:
        Path(args.output).write_text(outputs[0][1])
        print(f"Written to {args.output}", file=sys.stderr)
    elif args.output and len(outputs) > 1:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        for name, content, ext in outputs:
            filepath = output_dir / f"rocaille-{name}{ext}"
            filepath.write_text(content)
            print(f"Written {filepath}", file=sys.stderr)
    else:
        for name, content, ext in outputs:
            if len(outputs) > 1:
                print(f"\n{'='*60}\n{name.upper()}{ext}\n{'='*60}\n")
            print(content)


if __name__ == '__main__':
    main()
