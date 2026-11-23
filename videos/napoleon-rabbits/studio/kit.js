/* 3D Kaz studio kit + Next-Gen 8sb2R11FeVw Word-Synced Black Pill Subtitles. */
(function () {
  const q = new URLSearchParams(location.search);
  const W = +q.get('w') || 1080, H = +q.get('h') || 1920, FPS = +q.get('fps') || 30;
  const stage = document.getElementById('stage');
  stage.style.width = W + 'px'; stage.style.height = H + 'px';
  document.documentElement.style.setProperty('--u', Math.min(W, H) / 720);
  const canvas = document.getElementById('c'); canvas.width = W; canvas.height = H;

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
  renderer.setSize(W, H, false);
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.15;

  // ---------- maths ----------
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const smooth = x => { x = clamp(x); return x * x * (3 - 2 * x); };
  const lerp = (a, b, t) => a + (b - a) * t;
  const ramp = (t, start, len = .5) => smooth((t - start) / len);
  function rng(seed) { let s = seed >>> 0; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }

  // ---------- primitives ----------
  const mat = (c, o = {}) => new THREE.MeshStandardMaterial(Object.assign({ color: c, flatShading: true, roughness: .9, metalness: 0 }, o));
  const glow = (c, intensity = 2) => new THREE.MeshStandardMaterial({ color: 0x111111, emissive: c, emissiveIntensity: intensity });
  function mesh(g, m, x = 0, y = 0, z = 0) { const o = new THREE.Mesh(g, m); o.position.set(x, y, z); o.castShadow = true; o.receiveShadow = true; return o; }
  const box = (w, h, d, c, x = 0, y = 0, z = 0, o) => mesh(new THREE.BoxGeometry(w, h, d), mat(c, o), x, y, z);
  const cyl = (rt, rb, h, c, x = 0, y = 0, z = 0, seg = 8, o) => mesh(new THREE.CylinderGeometry(rt, rb, h, seg), mat(c, o), x, y, z);
  const ball = (r, c, x = 0, y = 0, z = 0, detail = 0, o) => mesh(new THREE.IcosahedronGeometry(r, detail), mat(c, o), x, y, z);

  // ---------- environment ----------
  function skyGradient(top, bottom) {
    const cv = document.createElement('canvas'); cv.width = 4; cv.height = 256; const g = cv.getContext('2d');
    const gr = g.createLinearGradient(0, 0, 0, 256); gr.addColorStop(0, top); gr.addColorStop(1, bottom);
    g.fillStyle = gr; g.fillRect(0, 0, 4, 256); const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; return t;
  }
  function lights(scene, { sun = 0xfff0d8, sunI = 2.6, sky = 0xbfd9ff, ground = 0x8a7a60, hemiI = 1.1, pos = [6, 10, 5], range = 18 } = {}) {
    scene.add(new THREE.HemisphereLight(sky, ground, hemiI));
    const d = new THREE.DirectionalLight(sun, sunI); d.position.set(...pos); d.castShadow = true;
    d.shadow.mapSize.set(2048, 2048); d.shadow.radius = 6; d.shadow.bias = -0.0005; d.shadow.normalBias = 0.03;
    const c = d.shadow.camera; c.left = -range; c.right = range; c.top = range; c.bottom = -range; c.near = .5; c.far = 80;
    scene.add(d); scene.add(d.target); return d;
  }
  function outdoor({ skyTop = '#7fb4e6', skyBottom = '#e9e2cf', fog = 0xe2dccb, fogNear = 16, fogFar = 70, grass = 0x6dae4a, sunPos = [7, 11, 6], range = 18, mood } = {}) {
    if (mood === 'dusk') { skyTop = '#2b3a67'; skyBottom = '#f2a65a'; fog = 0xd99a6c; }
    if (mood === 'night') { skyTop = '#070b1a'; skyBottom = '#1d2748'; fog = 0x141a30; }
    if (mood === 'dust') { skyTop = '#b9a57c'; skyBottom = '#e6d3a8'; fog = 0xd9c49a; fogFar = 40; grass = 0x8a7a4a; }
    const sc = new THREE.Scene(); sc.background = skyGradient(skyTop, skyBottom); sc.fog = new THREE.Fog(fog, fogNear, fogFar);
    const night = mood === 'night';
    lights(sc, night ? { sun: 0x9fb4ff, sunI: .9, sky: 0x33406a, ground: 0x10131f, hemiI: .7, pos: sunPos, range } : { pos: sunPos, range });
    const g = mesh(new THREE.PlaneGeometry(400, 400), mat(grass)); g.rotation.x = -Math.PI / 2; sc.add(g);
    return sc;
  }
  function indoor({ wall = 0xe6d6b8, floor = 0xa9713f, window: win = true, mood } = {}) {
    if (mood === 'night') { wall = 0x39406a; floor = 0x2a2d4a; }
    const sc = new THREE.Scene(); const bg = mood === 'night' ? 0x1c2038 : 0xd9c7a6;
    sc.background = new THREE.Color(bg); sc.fog = new THREE.Fog(bg, 9, 22);
    lights(sc, mood === 'night'
      ? { sun: 0x8fa2ff, sunI: 1.1, sky: 0x4a5590, ground: 0x15182a, hemiI: .8, pos: [3, 6, 4], range: 7 }
      : { sun: 0xffe2b8, sunI: 2.4, sky: 0xfff1dc, ground: 0x9a6a3c, hemiI: 1.25, pos: [3, 6, 4], range: 7 });
    const fl = mesh(new THREE.PlaneGeometry(30, 30), mat(floor)); fl.rotation.x = -Math.PI / 2; sc.add(fl);
    sc.add(box(30, 6, .2, wall, 0, 3, -4)); sc.add(box(.2, 6, 30, wall, -6, 3, 0));
    if (win) {
      sc.add(box(2.2, 1.5, .08, 0xbfe0f2, 2.6, 2.3, -3.88, { emissive: mood === 'night' ? 0x223366 : 0xbfe0f2, emissiveIntensity: .6 }));
      sc.add(box(2.5, .12, .14, 0xf3ead8, 2.6, 1.5, -3.84));
    }
    return sc;
  }
  function space({ stars = 1400, seed = 42 } = {}) {
    const sc = new THREE.Scene(); sc.background = new THREE.Color(0x05060d);
    sc.add(new THREE.AmbientLight(0x4a5878, .5));
    const d = new THREE.DirectionalLight(0xfff2e0, 3); d.position.set(-6, 3, 5); sc.add(d);
    const r = rng(seed), sp = [];
    for (let i = 0; i < stars; i++) { const v = new THREE.Vector3(r() - .5, r() - .5, r() - .5).normalize().multiplyScalar(60 + r() * 30); sp.push(v.x, v.y, v.z); }
    const sg = new THREE.BufferGeometry(); sg.setAttribute('position', new THREE.Float32BufferAttribute(sp, 3));
    sc.add(new THREE.Points(sg, new THREE.PointsMaterial({ color: 0xdfe6ff, size: .28, sizeAttenuation: true, transparent: true, opacity: .85 })));
    return sc;
  }
  function road({ width = 7, length = 300, z = -100, x = 0, along = 'z' } = {}) {
    const g = new THREE.Group();
    g.add(box(width, .04, length, 0x3d4046, 0, .02, 0));
    g.add(box(2, .12, length, 0xc9c2b4, width / 2 + 1, .06, 0)); g.add(box(2, .12, length, 0xc9c2b4, -width / 2 - 1, .06, 0));
    for (let i = 0; i < length / 4; i++) g.add(box(.16, .05, 1.6, 0xf2ead6, 0, .045, -length / 2 + i * 4));
    g.position.set(x, 0, z); if (along === 'x') g.rotation.y = Math.PI / 2; return g;
  }

  // ---------- props ----------
  function tree(x = 0, z = 0, s = 1, seed = 1, leaf = [0x4f9a3a, 0x5fae44, 0x438a35]) {
    const r = rng(seed), g = new THREE.Group();
    g.add(cyl(.14 * s, .2 * s, 1.5 * s, 0x6b4a2f, 0, .75 * s, 0, 6));
    for (let i = 0; i < 3; i++) {
      const m = ball((.75 + r() * .35) * s, leaf[i % leaf.length], (r() - .5) * .7 * s, (1.7 + i * .45 + r() * .2) * s, (r() - .5) * .7 * s);
      m.rotation.set(r() * 3, r() * 3, r() * 3); g.add(m);
    }
    g.position.set(x, 0, z); return g;
  }
  function house(x = 0, z = 0, { wall = 0xe9dcc0, roof = 0x3f6f8f, door = 0x2f5e86, rot = 0 } = {}) {
    const g = new THREE.Group();
    g.add(box(6, 3, 5, wall, 0, 1.5, 0));
    const rf = mesh(new THREE.ConeGeometry(4.6, 2, 4), mat(roof), 0, 4, 0); rf.rotation.y = Math.PI / 4; rf.scale.set(1, 1, .86); g.add(rf);
    g.add(box(1, 2, .1, door, 0, 1, 2.52));
    g.add(box(1.2, 1, .1, 0xa9cfe6, -1.9, 1.7, 2.52, { roughness: .3 })); g.add(box(1.2, 1, .1, 0xa9cfe6, 1.9, 1.7, 2.52, { roughness: .3 }));
    g.add(box(1.4, .12, .5, 0xb9ad98, 0, .06, 2.8));
    g.position.set(x, 0, z); g.rotation.y = rot; return g;
  }
  function fence(x = 0, z = 0, length = 4, color = 0xf5f1e6) {
    const g = new THREE.Group(); const n = Math.round(length / .5);
    for (let i = 0; i <= n; i++) g.add(box(.08, .6, .08, color, i * .5, .3, 0));
    g.add(box(length, .07, .05, color, length / 2, .48, 0)); g.position.set(x, 0, z); return g;
  }
  function car(color = 0x2f6fb8) {
    const g = new THREE.Group(); const dark = new THREE.Color(color).multiplyScalar(.7).getHex();
    g.add(box(1.7, .6, 3.8, color, 0, .6, 0)); g.add(box(1.5, .55, 1.9, dark, 0, 1.15, -.2));
    [[-.85, 1.2], [.85, 1.2], [-.85, -1.2], [.85, -1.2]].forEach(([x, z]) => { const w = cyl(.32, .32, .22, 0x1a1a1a, x, .32, z, 10); w.rotation.z = Math.PI / 2; g.add(w); });
    return g;
  }
  function table({ w = 2.2, d = 1.2, h = .8, color = 0x7a4a26 } = {}) {
    const g = new THREE.Group(), leg = new THREE.Color(color).multiplyScalar(.75).getHex();
    g.add(box(w, .09, d, color, 0, h - .045, 0));
    [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(([sx, sz]) => g.add(box(.1, h - .09, .1, leg, sx * (w / 2 - .1), (h - .09) / 2, sz * (d / 2 - .1))));
    g.top = h; return g;
  }
  function chair(color = 0x7a4a26) {
    const g = new THREE.Group(), leg = new THREE.Color(color).multiplyScalar(.75).getHex();
    g.add(box(.55, .06, .55, color, 0, .48, 0)); g.add(box(.55, .6, .06, color, 0, .8, -.25));
    [[-.23, -.23], [.23, -.23], [-.23, .23], [.23, .23]].forEach(([x, z]) => g.add(box(.06, .48, .06, leg, x, .24, z)));
    return g;
  }
  function mountain(x = 0, z = 0, s = 1, color = 0x8f98a3) {
    const g = new THREE.Group(); const m = mesh(new THREE.ConeGeometry(6 * s, 9 * s, 5), mat(color), 0, 4.5 * s, 0); g.add(m);
    const cap = mesh(new THREE.ConeGeometry(2.05 * s, 3 * s, 5), mat(0xf4f6f8), 0, 7.52 * s, 0); g.add(cap); g.position.set(x, 0, z); return g;
  }

  // ---------- character ----------
  function person({ shirt = 0x2f9c8c, pants = 0xb9a57c, skin = 0xe2b48c, hair = 0x4a3324, longHair = false } = {}) {
    const g = new THREE.Group(), p = {};
    const limb = (c, len, r) => { const piv = new THREE.Group(); piv.add(cyl(r, r * .9, len, c, 0, -len / 2, 0, 7)); return piv; };
    p.legL = limb(pants, .8, .1); p.legL.position.set(-.13, .82, 0);
    p.legR = limb(pants, .8, .1); p.legR.position.set(.13, .82, 0);
    [p.legL, p.legR].forEach(l => { l.add(box(.2, .09, .3, 0x3a2f2a, 0, -.8, .05)); g.add(l); });
    p.torso = box(.52, .62, .3, shirt, 0, 1.12, 0); g.add(p.torso);
    p.armL = limb(shirt, .58, .075); p.armL.position.set(-.34, 1.38, 0);
    p.armR = limb(shirt, .58, .075); p.armR.position.set(.34, 1.38, 0);
    [p.armL, p.armR].forEach(a => { a.add(mesh(new THREE.SphereGeometry(.085, 7, 5), mat(skin), 0, -.62, 0)); g.add(a); });
    p.head = new THREE.Group(); p.head.position.set(0, 1.5, 0);
    const sk = mesh(new THREE.SphereGeometry(.24, 20, 14), mat(skin, { flatShading: false }), 0, .24, 0); sk.scale.set(1, 1.12, 1); p.head.add(sk);
    const bk = mesh(new THREE.SphereGeometry(.235, 12, 10), mat(hair), 0, longHair ? .2 : .27, -.06); bk.scale.set(1.02, longHair ? 1.35 : 1.05, 1); p.head.add(bk);
    const hr = mesh(new THREE.SphereGeometry(.255, 10, 8, 0, Math.PI * 2, 0, Math.PI * .46), mat(hair), 0, .27, -.015); hr.scale.set(1, 1.12, 1); p.head.add(hr);
    const ink = new THREE.MeshBasicMaterial({ color: 0x1a1512 });
    p.eyes = [-.085, .085].map(x => { const e = new THREE.Mesh(new THREE.SphereGeometry(.026, 8, 6), ink); e.position.set(x, .25, .225); p.head.add(e); return e; });
    p.mouth = new THREE.Mesh(new THREE.BoxGeometry(.09, .016, .01), ink); p.mouth.position.set(0, .13, .232); p.head.add(p.mouth);
    g.add(p.head); g.parts = p; g.baseY = 0; return g;
  }
  function walk(pn, phase, amp = .55) {
    const p = pn.parts, s = Math.sin(phase) * amp;
    p.legL.rotation.x = s; p.legR.rotation.x = -s; p.armL.rotation.x = -s * .8; p.armR.rotation.x = s * .8;
    pn.position.y = pn.baseY + Math.abs(Math.cos(phase)) * .035;
  }
  function idle(pn, t) {
    const p = pn.parts; pn.position.y = pn.baseY + Math.sin(t * 2.2) * .008;
    p.head.rotation.y = Math.sin(t * .9) * .35; p.armL.rotation.z = -.06; p.armR.rotation.z = .06;
  }
  function sit(pn) { const p = pn.parts; p.legL.rotation.x = p.legR.rotation.x = -1.45; p.armL.rotation.x = p.armR.rotation.x = -.5; }
  function crowd(n = 8, { seed = 5, spread = 1.1 } = {}) {
    const r = rng(seed), g = new THREE.Group(), shirts = [0xc25b4a, 0x4a6fc2, 0xd9a441, 0x7a5fb0, 0x4f9a6a, 0xd97a9a], hairs = [0x2a1d14, 0x4a3324, 0xb08a4a, 0x151515];
    for (let i = 0; i < n; i++) {
      const pn = person({ shirt: shirts[Math.floor(r() * 6)], pants: [0x3d4a66, 0x6b5a48, 0x2f2f33][Math.floor(r() * 3)], hair: hairs[Math.floor(r() * 4)], longHair: r() > .55 });
      pn.position.set((i % 4) * spread + (r() - .5) * .4, 0, -Math.floor(i / 4) * spread + (r() - .5) * .4); pn.rotation.y = (r() - .5) * .8; g.add(pn);
    }
    return g;
  }

  function planet({ radius = 3, seed = 42, land = [0x5f9a4a, 0x7c8f45, 0xa08552, 0x8a6a44], sea = [0x2f6fb0, 0x285f9e, 0x3a82c4], ice = true, cracks = 0, atmosphere = 0x6fb0ff } = {}) {
    const g = new THREE.Group(), r = rng(seed), R = radius, k = R / 3;
    const geo = new THREE.IcosahedronGeometry(R, 3), pos = geo.attributes.position, col = [], c = new THREE.Color();
    const n3 = v => Math.sin(v.x / k * 1.3 + 1.7) * Math.cos(v.y / k * 1.1 - .4) + Math.sin(v.z / k * 1.5 + v.x / k * .7) * .8 + Math.cos(v.y / k * 2.3 + v.z / k) * .4;
    for (let i = 0; i < pos.count; i += 3) {
      const ctr = new THREE.Vector3().fromBufferAttribute(pos, i).add(new THREE.Vector3().fromBufferAttribute(pos, i + 1)).add(new THREE.Vector3().fromBufferAttribute(pos, i + 2)).divideScalar(3);
      const polar = ice && Math.abs(ctr.y) > R * .905;
      c.set(polar ? 0xeef2f4 : (n3(ctr) > .25 ? land[Math.floor(r() * land.length)] : sea[Math.floor(r() * sea.length)]));
      for (let j = 0; j < 3; j++) col.push(c.r, c.g, c.b);
    }
    geo.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
    g.add(new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ vertexColors: true, flatShading: true, roughness: .85 })));
    if (atmosphere !== null) g.add(new THREE.Mesh(new THREE.SphereGeometry(R * 1.073, 48, 32), new THREE.MeshBasicMaterial({ color: atmosphere, transparent: true, opacity: .1, side: THREE.BackSide, blending: THREE.AdditiveBlending })));
    return g;
  }

  // ---------- text ----------
  function label(text, size = 1, color = '#ffffff', font = '800 58px Inter, Arial, sans-serif') {
    const mc = document.createElement('canvas').getContext('2d'); mc.font = font; const w = Math.ceil(mc.measureText(text).width) + 48;
    const c = document.createElement('canvas'); c.width = w; c.height = 128; const g = c.getContext('2d');
    g.font = font; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillStyle = color; g.fillText(text, w / 2, 68);
    const tx = new THREE.CanvasTexture(c); tx.colorSpace = THREE.SRGBColorSpace;
    const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: tx, transparent: true, depthTest: false, depthWrite: false, fog: false }));
    s.sy = size * .4; s.sx = s.sy * w / 128; s.scale.set(s.sx, s.sy, 1); s.renderOrder = 10;
    s.pop = k => s.scale.set(s.sx * k, s.sy * k, 1); return s;
  }
  function sign(text, w = 2.4, h = .6, { bg = '#f3ead8', color = '#1c1c22', font = '800 70px Inter, Arial, sans-serif' } = {}) {
    const c = document.createElement('canvas'); c.width = 512; c.height = 128; const g = c.getContext('2d');
    g.fillStyle = bg; g.fillRect(0, 0, 512, 128); g.font = font; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillStyle = color; g.fillText(text, 256, 68);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
    return new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: t, side: THREE.DoubleSide }));
  }
  const pop = (t, t0, len = .35) => { const r = ramp(t, t0, len); return Math.max(.001, r * (1 + .3 * Math.sin(r * Math.PI))); };

  // ---------- camera ----------
  function camera(fov = 38) { return new THREE.PerspectiveCamera(fov, W / H, .05, 400); }
  function dolly(cam, k, from, to, look) {
    const e = smooth(k); cam.position.set(lerp(from[0], to[0], e), lerp(from[1], to[1], e), lerp(from[2], to[2], e)); cam.lookAt(look[0], look[1], look[2]);
  }

  // ---------- subtitle pill chunks ----------
  let subChunks = null;
  function buildChunks(words, beats) {
    const chunks = [];
    if (!words || !words.length) return chunks;
    // Group words per beat into 2-4 word chunks (split on punctuation or max 3 words / ~19 chars)
    const beatBounds = beats && beats.length ? beats : [{ start: 0, end: 9999 }];
    for (let bi = 0; bi < beatBounds.length; bi++) {
      const b = beatBounds[bi];
      const nextStart = bi + 1 < beatBounds.length ? beatBounds[bi + 1].start : 9999;
      const bw = words.filter(w => {
        const mid = (w.s + w.e) * 0.5;
        return mid >= b.start - 0.06 && mid < nextStart - 0.04;
      });
      if (!bw.length) continue;
      let cur = [];
      let chars = 0;
      for (let i = 0; i < bw.length; i++) {
        const w = bw[i];
        cur.push(w);
        chars += w.w.length + 1;
        const endsClause = /[,.;:!?—]$/.test(w.w);
        const rem = bw.length - 1 - i;
        if ((cur.length >= 3 || (cur.length >= 2 && (endsClause || chars >= 17))) && rem !== 1) {
          chunks.push({ words: cur, start: cur[0].s, end: cur[cur.length - 1].e });
          cur = []; chars = 0;
        }
      }
      if (cur.length) chunks.push({ words: cur, start: cur[0].s, end: cur[cur.length - 1].e });
    }
    // Extend each chunk end smoothly up to next chunk start (or +0.25s) with no blink gap
    for (let i = 0; i < chunks.length; i++) {
      const lim = i + 1 < chunks.length ? chunks[i + 1].start : chunks[i].end + 0.35;
      chunks[i].dispStart = Math.max(0, chunks[i].start - 0.04);
      chunks[i].dispEnd = Math.min(lim - 0.01, chunks[i].end + 0.25);
      if (i + 1 < chunks.length && chunks[i + 1].start - chunks[i].end < 0.35) {
        chunks[i].dispEnd = chunks[i + 1].start - 0.02;
      }
    }
    return chunks;
  }

  function renderSubtitlePill(tg) {
    const wrap = $('pillWrap'), pill = $('pill');
    if (!subChunks && window.KAZ_WORDS) subChunks = buildChunks(window.KAZ_WORDS, window.KAZ_BEATS);
    if (!subChunks || !subChunks.length) { wrap.style.display = 'none'; return; }
    let active = null;
    for (let i = 0; i < subChunks.length; i++) {
      if (tg >= subChunks[i].dispStart && tg <= subChunks[i].dispEnd) { active = subChunks[i]; break; }
    }
    if (!active) { wrap.style.display = 'none'; return; }
    wrap.style.display = 'flex';
    const dt = Math.max(0, tg - active.dispStart);
    const u = Math.min(1, dt / 0.10);
    const c1 = 1.70158, c3 = c1 + 1;
    const popScale = u < 1 ? 0.88 + 0.12 * (1 + c3 * Math.pow(u - 1, 3) + c1 * Math.pow(u - 1, 2)) : 1;
    pill.style.transform = `scale(${popScale.toFixed(4)})`;
    pill.style.opacity = Math.min(1, dt / 0.05).toFixed(3);
    pill.innerHTML = active.words.map(w => {
      const on = tg >= w.s - 0.03 && tg <= w.e + 0.04;
      return `<span class="w${on ? ' on' : ''}">${w.w.replace(/</g, '&lt;')}</span>`;
    }).join('');
  }

  // ---------- shots + overlay ----------
  const shots = [], cfg = { leftLabel: 'RABBITS', rightLabel: 'WHO IS WINNING', prefix: '', alertLabel: '', hud: true };
  const $ = id => document.getElementById(id);
  const K = {
    W, H, FPS, THREE, renderer, clamp, smooth, lerp, ramp, rng, mat, glow, mesh, box, cyl, ball,
    skyGradient, lights, outdoor, indoor, space, road, tree, house, fence, car, table, chair, mountain,
    person, walk, idle, sit, crowd, planet, label, sign, pop, camera, dolly,
    config(o) { Object.assign(cfg, o); },
    shot(def) { shots.push(def); },
  };
  window.KAZ = K;

  window.KAZ_INFO = () => ({ durs: shots.map(s => s.dur), fps: FPS, w: W, h: H });
  window.KAZ_DRAW = function (si, f) {
    let t0 = 0;
    for (let i = 0; i < si; i++) t0 += shots[i].dur;
    const s = shots[si], t = f / FPS, k = t / s.dur, tg = t0 + t;
    if (!s._live) s._live = s.setup(K);
    const show = cfg.hud && s.hud !== false;
    $('hl').style.display = $('hr').style.display = show ? '' : 'none';
    if (show) {
      $('ll').textContent = s.leftLabel || cfg.leftLabel; $('rl').textContent = s.rightLabel || cfg.rightLabel;
      const val = typeof s.value === 'function' ? s.value(t, k) : s.value;
      $('val').innerHTML = (val == null ? '' : '<span class="x">' + cfg.prefix + '</span>' + val);
      $('val').style.transform = `scale(${1 + .18 * (1 - smooth(t / .35))})`;
      const fv = v => typeof v === 'function' ? v(t, k) : v;
      $('status').textContent = fv(s.status) || ''; $('status').style.color = fv(s.statusColor) || '#f3ead8';
      $('sub').textContent = fv(s.sub) || '';
      const a = s.alert; $('al').style.display = a ? '' : 'none';
      if (a) { $('all').textContent = a.label || cfg.alertLabel; $('alv').textContent = typeof a.value === 'function' ? a.value(t, k) : a.value; }
    }
    renderSubtitlePill(tg);
    const card = typeof s.card === 'function' ? s.card(t, k) : s.card;
    $('card').style.display = card ? '' : 'none'; if (card) { $('card').innerHTML = card; $('card').style.opacity = smooth((t - .2) / .4) * (1 - smooth((t - (s.dur - .3)) / .3)); }
    $('title').innerHTML = s.title || ''; $('title').style.opacity = s.title ? smooth((t - .2) / .5) * (1 - smooth((t - (s.dur - .4)) / .4)) : 0;
    $('vig').style.opacity = s.vignette === false ? 0 : 1;
    const L = s._live; L.update && L.update(t, k);
    renderer.render(L.scene, L.camera);
    return new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
  };
  window.KAZ_FREE = function (si) {
    const L = shots[si]._live; if (!L) return;
    L.scene.traverse(o => { if (o.geometry) o.geometry.dispose(); if (o.material) [].concat(o.material).forEach(m => { if (m.map) m.map.dispose(); m.dispose(); }); });
    if (L.scene.background && L.scene.background.dispose) L.scene.background.dispose();
    renderer.renderLists.dispose(); shots[si]._live = null;
  };
})();
