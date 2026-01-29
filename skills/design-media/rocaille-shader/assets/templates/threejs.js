/**
 * Rocaille Shader - Three.js ShaderMaterial
 *
 * Domain warping with sinusoidal displacement for organic swirling effects.
 *
 * Usage:
 *   import RocailleShader from './threejs.js';
 *   const material = new THREE.ShaderMaterial(RocailleShader);
 *   const mesh = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), material);
 *   scene.add(mesh);
 *
 *   // In animation loop:
 *   material.uniforms.uTime.value = performance.now() / 1000;
 */

const RocailleShader = {
    uniforms: {
        uTime: { value: 0.0 },
        uResolution: { value: null }, // Set to new THREE.Vector2(width, height)
        uWarpCount: { value: 5 },
        uAmplitude: { value: 2.0 },
        uSpeed: { value: 1.0 },
        uColorMode: { value: 0 } // 0: rainbow, 1: basic, 2: neon, 3: fire, 4: ocean
    },

    vertexShader: /* glsl */`
        varying vec2 vUv;

        void main() {
            vUv = uv;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
    `,

    fragmentShader: /* glsl */`
        precision highp float;

        uniform float uTime;
        uniform vec2 uResolution;
        uniform int uWarpCount;
        uniform float uAmplitude;
        uniform float uSpeed;
        uniform int uColorMode;

        varying vec2 vUv;

        vec3 getColor(float d, vec2 v, int mode) {
            if (mode == 1) {
                // Basic grayscale
                return vec3(d * 0.1);
            } else if (mode == 2) {
                // Neon purple
                return vec3(d * 0.3, d * 0.05, d * 0.4);
            } else if (mode == 3) {
                // Fire
                return vec3(d * 0.4, d * 0.15, d * 0.02);
            } else if (mode == 4) {
                // Ocean
                return vec3(d * 0.02, d * 0.2, d * 0.35);
            } else {
                // Rainbow (default)
                vec3 color = 0.5 + 0.5 * cos(atan(v.y, v.x) + vec3(0.0, 2.094, 4.188));
                return color * d * 0.15;
            }
        }

        void main() {
            // Convert UV to centered coordinates with aspect ratio
            vec2 uv = (vUv - 0.5) * vec2(uResolution.x / uResolution.y, 1.0);
            vec2 v = uv;

            float t = uTime * uSpeed;

            // Domain warping loop
            for(int i = 0; i < 15; i++) {
                if (i >= uWarpCount) break;
                v += sin(v.yx + t) / uAmplitude;
            }

            // Distance field
            float d = 1.0 / max(length(v), 0.001);

            // Color mapping
            vec3 color = getColor(d, v, uColorMode);

            gl_FragColor = vec4(color, 1.0);
        }
    `
};

/**
 * Helper function to create a full-screen Rocaille effect
 *
 * @param {THREE.Scene} scene - The Three.js scene
 * @param {THREE.Camera} camera - The camera (typically OrthographicCamera for full-screen)
 * @returns {Object} - { mesh, material, update }
 */
function createRocailleEffect(scene, camera) {
    const material = new THREE.ShaderMaterial({
        ...RocailleShader,
        uniforms: {
            uTime: { value: 0.0 },
            uResolution: { value: new THREE.Vector2(window.innerWidth, window.innerHeight) },
            uWarpCount: { value: 5 },
            uAmplitude: { value: 2.0 },
            uSpeed: { value: 1.0 },
            uColorMode: { value: 0 }
        }
    });

    const geometry = new THREE.PlaneGeometry(2, 2);
    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);

    // Handle resize
    const onResize = () => {
        material.uniforms.uResolution.value.set(window.innerWidth, window.innerHeight);
    };
    window.addEventListener('resize', onResize);

    return {
        mesh,
        material,
        update: (time) => {
            material.uniforms.uTime.value = time;
        },
        setWarpCount: (count) => {
            material.uniforms.uWarpCount.value = count;
        },
        setAmplitude: (amp) => {
            material.uniforms.uAmplitude.value = amp;
        },
        setSpeed: (speed) => {
            material.uniforms.uSpeed.value = speed;
        },
        setColorMode: (mode) => {
            material.uniforms.uColorMode.value = mode;
        },
        dispose: () => {
            window.removeEventListener('resize', onResize);
            geometry.dispose();
            material.dispose();
            scene.remove(mesh);
        }
    };
}

// Export for ES modules
export { RocailleShader, createRocailleEffect };
export default RocailleShader;
