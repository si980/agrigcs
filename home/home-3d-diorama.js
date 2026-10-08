/**
 * AgriGCS Home Interactive 3D Platform Diorama
 * Loaded directly from Blender 3D Model: "3d platform home.blend" (exported as GLB)
 * High-fidelity Three.js WebGL viewport with OrbitControls, calibrated PBR colors, neon lighting & interactive inspect
 */
(function() {
  function init3DDiorama() {
    const container = document.getElementById('diorama-canvas-container');
    const canvas = document.getElementById('diorama-canvas');
    const loaderEl = document.getElementById('diorama-loading');
    if (!container || !canvas) return;

    if (typeof THREE === 'undefined') {
      console.warn("Three.js not loaded yet. Retrying in 100ms...");
      setTimeout(init3DDiorama, 100);
      return;
    }

    // 1. Scene & Renderer
    const scene = new THREE.Scene();
    
    const renderer = new THREE.WebGLRenderer({
      canvas: canvas,
      antialias: true,
      alpha: true,
      powerPreference: "high-performance"
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.outputEncoding = THREE.sRGBEncoding;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.0;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    // 2. Camera Setup (matching Isometric_Camera from Blender)
    const camera = new THREE.PerspectiveCamera(38, container.clientWidth / container.clientHeight, 0.1, 100);
    const initialCamPos = new THREE.Vector3(1.2, 4.0, 6.5);
    const initialTarget = new THREE.Vector3(0, 0.35, 0);
    camera.position.copy(initialCamPos);

    // 3. OrbitControls
    const controls = new THREE.OrbitControls(camera, canvas);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;
    controls.target.copy(initialTarget);
    controls.maxPolarAngle = Math.PI / 2 - 0.05; // Don't look under ground
    controls.minDistance = 2.8;
    controls.maxDistance = 12.0;
    controls.enablePan = true;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.75;

    let isUserInteracting = false;
    let resumeTimeout;
    controls.addEventListener('start', () => {
      isUserInteracting = true;
    });
    controls.addEventListener('end', () => {
      clearTimeout(resumeTimeout);
      resumeTimeout = setTimeout(() => {
        isUserInteracting = false;
      }, 4000);
    });

    // 4. Balanced Studio & Agricultural Lighting (Prevents Washout)
    const ambientLight = new THREE.AmbientLight(0x8fa4b8, 0.55);
    scene.add(ambientLight);

    const hemisphereLight = new THREE.HemisphereLight(0x45efc5, 0x1a2634, 0.45);
    scene.add(hemisphereLight);

    // Key Warm Sun Light
    const sunLight = new THREE.DirectionalLight(0xfff7ed, 1.35);
    sunLight.position.set(6.5, 9.0, 7.5);
    sunLight.castShadow = true;
    sunLight.shadow.mapSize.width = 2048;
    sunLight.shadow.mapSize.height = 2048;
    sunLight.shadow.camera.near = 0.5;
    sunLight.shadow.camera.far = 25;
    const d = 5;
    sunLight.shadow.camera.left = -d;
    sunLight.shadow.camera.right = d;
    sunLight.shadow.camera.top = d;
    sunLight.shadow.camera.bottom = -d;
    sunLight.shadow.bias = -0.0005;
    scene.add(sunLight);

    // Sky Fill Light (Soft Cyan / Azure)
    const skyFill = new THREE.DirectionalLight(0x38bdf8, 0.55);
    skyFill.position.set(-5.0, 6.0, -3.0);
    scene.add(skyFill);

    // Neon Teal Hub Accent Point Light
    const hubNeonLight = new THREE.PointLight(0x00f5c4, 2.2, 6.0);
    hubNeonLight.position.set(1.35, 1.2, 0.5);
    scene.add(hubNeonLight);

    // Subtle Soil Glow Point Light
    const soilNeonLight = new THREE.PointLight(0x0284c7, 1.2, 5.0);
    soilNeonLight.position.set(-1.0, 0.8, -0.5);
    scene.add(soilNeonLight);

    // 5. Contact Shadow & Virtual Ground Disc
    const groundGeo = new THREE.PlaneGeometry(16, 16);
    const groundMat = new THREE.ShadowMaterial({ opacity: 0.5 });
    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -0.01;
    ground.receiveShadow = true;
    scene.add(ground);

    // 6. Vibrant PBR Material Palette Definition (Restores Rich Colors to 3D Models)
    const materialTheme = {
      'soil': { color: 0x332014, roughness: 0.95, metalness: 0.02 },
      'leafgreen': { color: 0x16a34a, roughness: 0.42, metalness: 0.05 },
      'mossgrass': { color: 0x22c55e, roughness: 0.55, metalness: 0.05 },
      'planterframeaccent': { color: 0x090d13, roughness: 0.35, metalness: 0.85 },
      'planterframe': { color: 0x141b24, roughness: 0.45, metalness: 0.75 },
      'pedestal': { color: 0x1f2937, roughness: 0.5, metalness: 0.4 },
      'solarcell': { color: 0x0c2752, roughness: 0.15, metalness: 0.9, emissive: 0x041126, emissiveIntensity: 0.3 },
      'solarframe': { color: 0x334155, roughness: 0.3, metalness: 0.8 },
      'fencepost': { color: 0x475569, roughness: 0.4, metalness: 0.6 },
      'fencewire': { color: 0x94a3b8, roughness: 0.25, metalness: 0.85 },
      'chrome': { color: 0xcfd8dc, roughness: 0.15, metalness: 0.95 },
      'stone': { color: 0x64748b, roughness: 0.85, metalness: 0.1 },
      'wiregreen': { color: 0x00f5c4, roughness: 0.3, metalness: 0.2, emissive: 0x00f5c4, emissiveIntensity: 0.7 },
      'iotteal': { color: 0x00f5c4, roughness: 0.25, metalness: 0.3, emissive: 0x00d2aa, emissiveIntensity: 0.6 },
      'iottealglow': { color: 0x00f5c4, roughness: 0.2, metalness: 0.1, emissive: 0x00f5c4, emissiveIntensity: 1.6 },
      'iotscreen': { color: 0x020810, roughness: 0.1, metalness: 0.9, emissive: 0x00b4d8, emissiveIntensity: 0.9 },
      'iotwhite': { color: 0xdbe4ee, roughness: 0.4, metalness: 0.15 }
    };

    // 7. Load Blender GLB Model
    const gltfLoader = new THREE.GLTFLoader();
    let modelRoot = null;
    const modelUrl = 'platform_diorama.glb';

    gltfLoader.load(
      modelUrl,
      (gltf) => {
        modelRoot = gltf.scene;

        const lightsToRemove = [];

        // Traverse & fix materials / strip embedded overblown lights
        modelRoot.traverse((child) => {
          // 1. Mark embedded Blender lights for removal (e.g. Sun intensity 3278 that caused white washout)
          if (child.isLight) {
            child.visible = false;
            child.intensity = 0;
            lightsToRemove.push(child);
            return;
          }

          // 2. Restore colors on meshes
          if (child.isMesh) {
            child.castShadow = true;
            child.receiveShadow = true;

            if (child.material) {
              const matName = (child.material.name || '').toLowerCase();
              let matched = false;

              for (const [key, props] of Object.entries(materialTheme)) {
                if (matName.includes(key)) {
                  child.material = child.material.clone();
                  if (props.color !== undefined) child.material.color.setHex(props.color);
                  if (props.roughness !== undefined) child.material.roughness = props.roughness;
                  if (props.metalness !== undefined) child.material.metalness = props.metalness;
                  if (props.emissive !== undefined) {
                    child.material.emissive.setHex(props.emissive);
                    child.material.emissiveIntensity = props.emissiveIntensity || 1.0;
                  }
                  child.material.needsUpdate = true;
                  matched = true;
                  break;
                }
              }

              // Object-specific overrides for high-fidelity appearance
              const objName = (child.name || '').toLowerCase();
              if (objName === 'hub_main_body') {
                child.material = child.material.clone();
                child.material.color.setHex(0x1e293b); // Slate tech chassis
                child.material.roughness = 0.35;
                child.material.metalness = 0.5;
                child.material.needsUpdate = true;
              } else if (objName.includes('dome_head')) {
                child.material = child.material.clone();
                child.material.color.setHex(0x0ea5e9); // Sky blue optical dome
                child.material.roughness = 0.1;
                child.material.metalness = 0.8;
                child.material.emissive.setHex(0x0284c7);
                child.material.emissiveIntensity = 0.4;
                child.material.needsUpdate = true;
              } else if (objName.startsWith('sensor_') && objName.includes('body')) {
                child.material = child.material.clone();
                child.material.color.setHex(0x0284c7); // High-contrast telemetry node
                child.material.roughness = 0.3;
                child.material.metalness = 0.4;
                child.material.needsUpdate = true;
              } else if (objName.includes('leaf') || objName.includes('crop')) {
                child.material = child.material.clone();
                // Subtle organic variety across crops
                const leafColors = [0x22c55e, 0x16a34a, 0x34d399, 0x15803d];
                const charCodeSum = (child.name || '').split('').reduce((acc, c) => acc + c.charCodeAt(0), 0);
                child.material.color.setHex(leafColors[charCodeSum % leafColors.length]);
                child.material.roughness = 0.4;
                child.material.metalness = 0.05;
                child.material.needsUpdate = true;
              } else if (objName.includes('soil_bed')) {
                child.material = child.material.clone();
                child.material.color.setHex(0x27170c); // Rich dark fertile soil
                child.material.roughness = 0.98;
                child.material.metalness = 0.0;
                child.material.needsUpdate = true;
              } else if (objName.includes('moss_patch')) {
                child.material = child.material.clone();
                child.material.color.setHex(0x15803d); // Deep green moss
                child.material.roughness = 0.7;
                child.material.metalness = 0.05;
                child.material.needsUpdate = true;
              }
            }
          }
        });

        // Safely remove any overblown Blender lights after traversal
        lightsToRemove.forEach(l => {
          if (l.parent) l.parent.remove(l);
        });

        scene.add(modelRoot);

        // Hide loading indicator
        if (loaderEl) {
          loaderEl.style.opacity = '0';
          setTimeout(() => { loaderEl.style.display = 'none'; }, 400);
        }

        console.log("AgriGCS 3D Platform Diorama loaded with rich PBR colors & calibrated lighting!");
      },
      (xhr) => {
        if (xhr.lengthComputable && loaderEl) {
          const percent = Math.round((xhr.loaded / xhr.total) * 100);
          const txt = loaderEl.querySelector('span');
          if (txt) txt.textContent = `Loading 3D Platform Diorama (${percent}%)...`;
        }
      },
      (err) => {
        console.error("Error loading 3D Diorama:", err);
      }
    );

    // 8. Interactive Glowing Pulse Spheres (Sensor Nodes on Field)
    const sensorHotspots = [
      { pos: new THREE.Vector3(-1.8, 0.42, 0.9), label: "LoRa Soil Probe Alpha", telemetry: "VWC: 38.4% • Temp: 24.2°C", color: 0x00f5c4 },
      { pos: new THREE.Vector3(-0.3, 0.45, -0.6), label: "Canopy Infrared Array", telemetry: "NDVI: 0.84 • LAI: 3.12", color: 0x00f5c4 },
      { pos: new THREE.Vector3(1.4, 0.85, 0.6), label: "Master Gateway Node", telemetry: "LoRaWAN 868MHz • 28ms Ping", color: 0x38bdf8 },
      { pos: new THREE.Vector3(2.1, 0.42, -0.8), label: "Root Moisture Cluster", telemetry: "Zone 4 Depth: 45cm", color: 0x00f5c4 }
    ];

    const pulseGeometry = new THREE.SphereGeometry(0.07, 16, 16);
    const pulseMeshes = [];

    sensorHotspots.forEach(spot => {
      const pulseMat = new THREE.MeshBasicMaterial({
        color: spot.color,
        transparent: true,
        opacity: 0.85
      });
      const mesh = new THREE.Mesh(pulseGeometry, pulseMat);
      mesh.position.copy(spot.pos);
      mesh.userData = { isHotspot: true, label: spot.label, telemetry: spot.telemetry };
      scene.add(mesh);
      pulseMeshes.push(mesh);

      // Outer ripple ring
      const ringGeo = new THREE.RingGeometry(0.09, 0.13, 24);
      const ringMat = new THREE.MeshBasicMaterial({
        color: spot.color,
        transparent: true,
        opacity: 0.4,
        side: THREE.DoubleSide
      });
      const ring = new THREE.Mesh(ringGeo, ringMat);
      ring.rotation.x = Math.PI / 2;
      ring.position.copy(spot.pos);
      ring.position.y -= 0.05;
      scene.add(ring);
      mesh.userData.ring = ring;
    });

    // 9. Raycasting Hover Tooltips
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2(-999, -999);
    const tooltipEl = document.getElementById('diorama-3d-tooltip');

    function onMouseMove(event) {
      const rect = canvas.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(pulseMeshes);

      if (intersects.length > 0 && tooltipEl) {
        const hit = intersects[0].object;
        tooltipEl.style.display = 'flex';
        tooltipEl.style.left = `${event.clientX - rect.left}px`;
        tooltipEl.style.top = `${event.clientY - rect.top - 15}px`;
        tooltipEl.innerHTML = `
          <div class="flex items-center gap-1.5 font-mono text-[11px] font-bold text-primary">
            <span class="w-1.5 h-1.5 rounded-full bg-primary animate-ping"></span>
            ${hit.userData.label}
          </div>
          <div class="font-mono text-[10px] text-on-surface-variant">
            ${hit.userData.telemetry}
          </div>
        `;
        canvas.style.cursor = 'pointer';
      } else if (tooltipEl) {
        tooltipEl.style.display = 'none';
        canvas.style.cursor = 'grab';
      }
    }
    canvas.addEventListener('mousemove', onMouseMove);

    // 10. Advanced Tactical HUD Controls Binding
    let targetCamPos = initialCamPos.clone();
    let targetLookAt = initialTarget.clone();
    let isTransitioningCam = false;

    function setCameraPreset(pos, target, btnId) {
      targetCamPos.copy(pos);
      targetLookAt.copy(target);
      isTransitioningCam = true;
      isUserInteracting = true;
      clearTimeout(resumeTimeout);
      resumeTimeout = setTimeout(() => { isUserInteracting = false; }, 3000);

      document.querySelectorAll('.cam-preset-btn').forEach(b => {
        b.className = 'cam-preset-btn flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-mono font-medium transition-all text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high cursor-pointer whitespace-nowrap';
      });
      const activeBtn = document.getElementById(btnId);
      if (activeBtn) {
        activeBtn.className = 'cam-preset-btn active flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-mono font-medium transition-all bg-primary/20 text-primary border border-primary/30 cursor-pointer whitespace-nowrap';
      }
    }

    const btnCamIso = document.getElementById('cam-iso');
    if (btnCamIso) {
      btnCamIso.addEventListener('click', () => {
        setCameraPreset(initialCamPos, initialTarget, 'cam-iso');
      });
    }

    const btnCamTop = document.getElementById('cam-top');
    if (btnCamTop) {
      btnCamTop.addEventListener('click', () => {
        setCameraPreset(new THREE.Vector3(0.01, 8.2, 0.01), new THREE.Vector3(0, 0.1, 0), 'cam-top');
      });
    }

    const btnCamHub = document.getElementById('cam-hub');
    if (btnCamHub) {
      btnCamHub.addEventListener('click', () => {
        setCameraPreset(new THREE.Vector3(2.0, 1.8, 1.8), new THREE.Vector3(1.35, 0.9, 0.5), 'cam-hub');
      });
    }

    // Auto-Rotate Button
    const btnRotate = document.getElementById('btn-3d-rotate');
    const txtRotate = document.getElementById('txt-3d-rotate');
    let autoRotateEnabled = true;

    if (btnRotate) {
      btnRotate.addEventListener('click', () => {
        autoRotateEnabled = !autoRotateEnabled;
        controls.autoRotate = autoRotateEnabled;
        if (txtRotate) txtRotate.textContent = autoRotateEnabled ? 'ROTATE ON' : 'ROTATE OFF';
        btnRotate.className = autoRotateEnabled
          ? 'flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-mono font-medium transition-all text-primary hover:bg-primary/20 cursor-pointer ml-0.5 whitespace-nowrap'
          : 'flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-mono font-medium transition-all text-on-surface-variant hover:text-on-surface cursor-pointer ml-0.5 whitespace-nowrap';
      });
    }

    // Viewport Reset Button
    const btnReset = document.getElementById('btn-3d-reset');
    if (btnReset) {
      btnReset.addEventListener('click', () => {
        setCameraPreset(initialCamPos, initialTarget, 'cam-iso');
      });
    }

    // Segmented Theme Shifter
    const btnCyberGlow = document.getElementById('btn-cyber-glow');
    const btnDaylight = document.getElementById('btn-daylight');

    function setTheme(isCyber) {
      if (isCyber) {
        sunLight.intensity = 1.35;
        sunLight.color.setHex(0xfff7ed);
        skyFill.intensity = 0.55;
        hubNeonLight.intensity = 2.2;
        soilNeonLight.intensity = 1.2;
        ambientLight.intensity = 0.55;
        if (btnCyberGlow) btnCyberGlow.className = 'theme-switch-btn active flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-mono font-medium transition-all bg-primary/20 text-primary border border-primary/30 cursor-pointer';
        if (btnDaylight) btnDaylight.className = 'theme-switch-btn flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-mono font-medium transition-all text-on-surface-variant hover:text-on-surface cursor-pointer';
      } else {
        sunLight.intensity = 1.7;
        sunLight.color.setHex(0xfffaed);
        skyFill.intensity = 0.7;
        hubNeonLight.intensity = 0.8;
        soilNeonLight.intensity = 0.4;
        ambientLight.intensity = 0.75;
        if (btnDaylight) btnDaylight.className = 'theme-switch-btn active flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-mono font-medium transition-all bg-primary/20 text-primary border border-primary/30 cursor-pointer';
        if (btnCyberGlow) btnCyberGlow.className = 'theme-switch-btn flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-mono font-medium transition-all text-on-surface-variant hover:text-on-surface cursor-pointer';
      }
    }

    if (btnCyberGlow) btnCyberGlow.addEventListener('click', () => setTheme(true));
    if (btnDaylight) btnDaylight.addEventListener('click', () => setTheme(false));

    // 11. Responsive Resize
    function resize() {
      const w = container.clientWidth;
      const h = container.clientHeight;
      if (w === 0 || h === 0) return;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h, false);
    }
    window.addEventListener('resize', resize);
    resize();

    // 12. Animation Loop
    let clock = new THREE.Clock();
    let frameCount = 0;
    let lastFpsTime = performance.now();
    const fpsEl = document.getElementById('hud-fps');

    function animate() {
      requestAnimationFrame(animate);
      const elapsedTime = clock.getElapsedTime();

      // FPS tracking
      frameCount++;
      const now = performance.now();
      if (now - lastFpsTime >= 1000) {
        if (fpsEl) fpsEl.textContent = Math.round((frameCount * 1000) / (now - lastFpsTime));
        frameCount = 0;
        lastFpsTime = now;
      }

      // Smooth camera interpolation toward target preset
      if (isTransitioningCam) {
        camera.position.lerp(targetCamPos, 0.08);
        controls.target.lerp(targetLookAt, 0.08);
        controls.update();
        if (camera.position.distanceTo(targetCamPos) < 0.03 && controls.target.distanceTo(targetLookAt) < 0.03) {
          isTransitioningCam = false;
        }
      }

      // Gentle pulsing on hub neon & sensor pulse rings
      hubNeonLight.intensity = 2.0 + Math.sin(elapsedTime * 3) * 0.4;
      pulseMeshes.forEach((mesh, idx) => {
        const s = 1.0 + Math.sin(elapsedTime * 4 + idx) * 0.15;
        mesh.scale.set(s, s, s);
        if (mesh.userData.ring) {
          const rs = 1.0 + Math.sin(elapsedTime * 2.5 + idx) * 0.2;
          mesh.userData.ring.scale.set(rs, rs, rs);
        }
      });

      if (autoRotateEnabled && !isUserInteracting && !isTransitioningCam) {
        controls.autoRotate = true;
      } else {
        controls.autoRotate = false;
      }

      controls.update();
      renderer.render(scene, camera);
    }
    animate();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init3DDiorama);
  } else {
    init3DDiorama();
  }
})();
