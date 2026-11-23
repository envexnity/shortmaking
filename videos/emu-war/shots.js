/* The Great Emu War (1932) â€” vertical 3D Kaz short. Cuts come from beats.json + pause analysis. */
const K = KAZ, T = K.THREE, PI = Math.PI;
K.config({ leftLabel: 'EMUS', rightLabel: 'WINNING', prefix: '', alertLabel: 'BULLETS FIRED', capIn: .06, capOut: .12 });
const CUT = [0, 5.40, 6.195, 9.575, 14.905, 17.895, 20.975, 22.615, 25.885, 30.615, 33.405, 36.55, 38.955, 43.855, 48.235, 49.68, 50.995, 56.089];
let n = 0;
const S = o => { const i = n++; K.shot(Object.assign({ dur: (Math.round(CUT[i + 1] * 30) - Math.round(CUT[i] * 30)) / 30 }, o)); };
const CORAL = '#ff7a66', GOLD = '#e8c56a';
const frac = x => x - Math.floor(x);
const fmt = v => Math.round(v).toLocaleString('en-US');

// ---------------------------------------------------------------- world
function outback(o = {}) {
  const sc = K.outdoor(Object.assign({ skyTop: '#6fa8dc', skyBottom: '#f4e2bb', fog: 0xefdcb4, fogNear: 30, fogFar: 140, grass: 0xc79f52, sunPos: [9, 14, 7], range: 26 }, o));
  return sc;
}
function wheat(sc, { n = 1400, x0 = -30, x1 = 30, z0 = -70, z1 = 12, seed = 3, clear = null, s = 1 } = {}) {
  const g = new T.ConeGeometry(.13, .8, 4); g.translate(0, .4, 0);
  const m = new T.InstancedMesh(g, K.mat(0xffffff), n), r = K.rng(seed), d = new T.Object3D(), c = new T.Color();
  const cols = [0xe6c062, 0xd6a948, 0xf0cf78, 0xc99a3e];
  let i = 0, guard = 0;
  while (i < n && guard++ < n * 4) {
    const x = K.lerp(x0, x1, r()), z = K.lerp(z0, z1, r());
    if (clear && clear(x, z)) continue;
    d.position.set(x, 0, z); d.rotation.set((r() - .5) * .3, r() * 3, (r() - .5) * .3); d.scale.setScalar((.7 + r() * .7) * s); d.updateMatrix();
    m.setMatrixAt(i, d.matrix); c.setHex(cols[i % 4]); m.setColorAt(i, c); i++;
  }
  m.count = i; m.receiveShadow = true; sc.add(m); return m;
}
const gum = (x, z, s = 1.6, seed = 1) => { const t = K.tree(x, z, s, seed, [0x7f9a5a, 0x8fa866, 0x6c8a4c]); t.children[0].material.color.setHex(0xd9d2c2); return t; };
function rocks(sc, { n = 30, x0 = -20, x1 = 20, z0 = -40, z1 = 8, seed = 9 } = {}) {
  const r = K.rng(seed);
  for (let i = 0; i < n; i++) { const b = K.ball(.2 + r() * .45, [0x9a7a55, 0x8a6a48, 0xa98a62][i % 3], K.lerp(x0, x1, r()), .05, K.lerp(z0, z1, r())); b.scale.y = .55; sc.add(b); }
}

// ---------------------------------------------------------------- emu
function emu({ seed = 1, s = 1 } = {}) {
  const r = K.rng(seed * 7 + 3), g = new T.Group(), p = {};
  const body = new T.Color(0x4d3e33).offsetHSL(0, 0, (r() - .5) * .08).getHex();
  p.root = new T.Group(); g.add(p.root);
  const b = K.ball(.42, body, 0, 1.18, -.05, 1); b.scale.set(1, .88, 1.38); p.root.add(b);
  const tl = K.ball(.26, body, 0, 1.12, -.62, 0); tl.scale.set(1.1, .8, 1); p.root.add(tl);
  const shag = K.ball(.3, new T.Color(body).offsetHSL(0, 0, -.04).getHex(), 0, .92, -.1, 0); shag.scale.set(1.2, .6, 1.5); p.root.add(shag);
  p.neck = new T.Group(); p.neck.position.set(0, 1.34, .4); p.root.add(p.neck);
  p.neck.add(K.cyl(.065, .12, .78, 0x6d7f95, 0, .36, 0, 6));
  p.neck.add(K.cyl(.12, .14, .22, body, 0, .02, 0, 6));
  p.head = new T.Group(); p.head.position.set(0, .78, 0); p.neck.add(p.head);
  const hd = K.ball(.135, 0x56687e, 0, 0, .03, 1); hd.scale.set(.9, .92, 1.25); p.head.add(hd);
  const tuft = K.ball(.09, 0x3d332b, 0, .09, -.04, 0); tuft.scale.set(.9, .7, 1.2); p.head.add(tuft);
  const bk = K.mesh(new T.ConeGeometry(.05, .17, 5), K.mat(0x3a332c), 0, -.025, .22); bk.rotation.x = PI / 2; p.head.add(bk);
  const ink = new T.MeshBasicMaterial({ color: 0x0e0e10 }), wh = new T.MeshBasicMaterial({ color: 0xf2efe6 });
  p.eyes = [-1, 1].map(sx => { const w = new T.Mesh(new T.SphereGeometry(.04, 8, 6), wh); w.position.set(sx * .1, .03, .08); p.head.add(w); const e = new T.Mesh(new T.SphereGeometry(.024, 8, 6), ink); e.position.set(sx * .125, .03, .1); p.head.add(e); return e; });
  const legC = 0x7d6b55;
  const leg = sx => {
    const pv = new T.Group(); pv.position.set(sx * .17, 1.0, .05);
    pv.add(K.cyl(.08, .055, .42, body, 0, -.1, 0, 6));
    pv.add(K.cyl(.036, .03, .98, legC, 0, -.5, 0, 5));
    pv.add(K.box(.16, .04, .26, legC, 0, -.98, .08));
    p.root.add(pv); return pv;
  };
  p.legL = leg(-1); p.legR = leg(1);
  g.parts = p; g.scale.setScalar(s); g.seed = r() * 10; return g;
}
function emuRun(e, ph, amp = .8) {
  const p = e.parts, s = Math.sin(ph);
  p.legL.rotation.x = s * amp; p.legR.rotation.x = -s * amp;
  p.root.position.y = Math.abs(Math.cos(ph)) * .09; p.root.rotation.x = .1;
  p.neck.rotation.x = .5 + Math.sin(ph * 2) * .08; p.head.rotation.set(-.4, 0, 0);
}
function emuIdle(e, t) {
  const p = e.parts, sd = e.seed;
  p.legL.rotation.x = p.legR.rotation.x = 0; p.root.rotation.x = 0;
  p.root.position.y = Math.sin(t * 2 + sd) * .012;
  p.neck.rotation.x = .12 + Math.sin(t * .8 + sd) * .07; p.head.rotation.set(-.12, Math.sin(t * .7 + sd * 2) * .5, 0);
}
function emuPeck(e, t) {
  const p = e.parts, sd = e.seed, k = K.smooth(K.clamp(Math.sin(t * 2.4 + sd) * 1.6 + .2));
  p.legL.rotation.x = p.legR.rotation.x = 0; p.root.rotation.x = k * .25; p.root.position.y = 0;
  p.neck.rotation.x = K.lerp(.2, 2.25, k); p.head.rotation.set(K.lerp(-.1, -1.0, k), 0, 0);
}
function flock(sc, { n = 30, cx = 0, cz = 0, rx = 8, rz = 8, seed = 5, s = 1 } = {}) {
  const r = K.rng(seed), arr = [];
  for (let i = 0; i < n; i++) {
    const e = emu({ seed: seed * 100 + i, s: s * (.9 + r() * .2) });
    const a = r() * PI * 2, d = Math.sqrt(r());
    e.position.set(cx + Math.cos(a) * d * rx, 0, cz + Math.sin(a) * d * rz); e.rotation.y = r() * PI * 2;
    e.ph = r() * 10; sc.add(e); arr.push(e);
  }
  return arr;
}

// ---------------------------------------------------------------- army
function soldier(o = {}) {
  const p = K.person(Object.assign({ shirt: 0x8c7d52, pants: 0x6e6545, hair: 0x3a2a1c, skin: 0xe0ad84 }, o));
  const h = p.parts.head, hat = 0x7a6943;
  h.add(K.cyl(.43, .43, .035, hat, 0, .43, 0, 16));
  h.add(K.cyl(.2, .25, .22, hat, 0, .55, 0, 10));
  h.add(K.cyl(.255, .255, .06, 0x3b3226, 0, .47, 0, 10));
  const flap = K.box(.035, .26, .5, hat, -.4, .56, 0); flap.rotation.z = -.35; h.add(flap);
  if (o.officer) {
    p.parts.torso.add(K.box(.08, .66, .32, 0x5a3a22, .12, 0, 0)); p.parts.torso.children[0].rotation.z = .55;
    p.parts.torso.add(K.box(.54, .07, .32, 0x5a3a22, 0, -.22, 0));
    h.add(K.box(.14, .03, .02, 0x3a2a1c, 0, .17, .238));
  }
  return p;
}
function aim(p) { p.parts.armL.rotation.set(-1.35, 0, .25); p.parts.armR.rotation.set(-1.25, 0, -.15); }
function salute(p, k) { p.parts.armR.rotation.set(-2.6 * k, 0, -.5 * k); }
function lewis() {
  const g = new T.Group();
  const sh = K.cyl(.085, .085, .85, 0x2b2d2f, 0, 0, .25, 10); sh.rotation.x = PI / 2; g.add(sh);
  const br = K.cyl(.025, .025, .25, 0x1c1c1c, 0, 0, .78, 6); br.rotation.x = PI / 2; g.add(br);
  g.add(K.box(.12, .14, .5, 0x3a3a3a, 0, -.01, -.4));
  g.add(K.box(.08, .17, .42, 0x6b4a2f, 0, -.06, -.82));
  g.add(K.cyl(.23, .23, .07, 0x34383b, 0, .12, -.28, 16));
  g.flash = new T.Mesh(new T.ConeGeometry(.16, .55, 6), new T.MeshBasicMaterial({ color: 0xffd27a, transparent: true, opacity: .95, fog: false }));
  g.flash.rotation.x = PI / 2; g.flash.position.z = 1.15; g.add(g.flash);
  g.fl2 = new T.Mesh(new T.SphereGeometry(.2, 8, 6), new T.MeshBasicMaterial({ color: 0xfff1c0, transparent: true, opacity: .8, fog: false })); g.fl2.position.z = .95; g.add(g.fl2);
  g.fire = (t, on, rate = 11) => { const v = on && frac(t * rate) < .5; g.flash.visible = g.fl2.visible = v; const s = .8 + .4 * frac(t * rate * 3.7); g.flash.scale.setScalar(s); g.fl2.scale.setScalar(s); g.position.z = g.z0 - (v ? .03 : 0); };
  g.fire(0, false); g.z0 = 0; return g;
}
function sandbags(x, z, w = 2.4) {
  const g = new T.Group();
  for (let row = 0; row < 3; row++) for (let i = 0; i < Math.round(w / .6); i++) {
    const b = K.box(.62, .3, .42, [0xc9b48a, 0xbfa97c][(i + row) % 2], -w / 2 + .3 + i * .6 + (row % 2) * .2, .15 + row * .29, 0); b.rotation.y = (i % 3 - 1) * .05; g.add(b);
  }
  g.position.set(x, 0, z); return g;
}
function truck() {
  const g = new T.Group(), body = 0x5e6b4a, dk = 0x2a2a28;
  g.add(K.box(1.8, .22, 4.8, dk, 0, .72, 0));
  g.add(K.box(1.7, 1.1, 1.2, body, 0, 1.38, .55));
  g.add(K.box(1.5, .5, .05, 0xa9cfe6, 0, 1.62, 1.16, { roughness: .3 }));
  g.add(K.box(1.25, .72, 1.25, body, 0, 1.17, 1.8));
  g.add(K.box(1.05, .6, .06, 0x1c1c1c, 0, 1.17, 2.43));
  [-.45, .45].forEach(x => g.add(K.ball(.1, 0xfff2c8, x, 1.4, 2.45, 1)));
  [-1, 1].forEach(sx => { const f = K.box(.32, .1, 1.1, dk, sx * .82, 1.0, 1.75); g.add(f); });
  g.add(K.box(1.9, .1, 2.6, 0x6b5a40, 0, .88, -1.15));
  [-1, 1].forEach(sx => g.add(K.box(.08, .45, 2.6, 0x6b5a40, sx * .91, 1.12, -1.15)));
  g.add(K.box(1.9, .45, .08, 0x6b5a40, 0, 1.12, -2.42));
  g.wheels = [];
  [[-.92, 1.65], [.92, 1.65], [-.92, -1.45], [.92, -1.45]].forEach(([x, z]) => {
    const w = new T.Group(); w.position.set(x, .44, z);
    const ty = K.cyl(.44, .44, .26, 0x1a1a1a, 0, 0, 0, 12); ty.rotation.z = PI / 2; w.add(ty);
    const hub = K.box(.28, .5, .12, 0x7a7a70, 0, 0, 0); w.add(hub); g.add(w); g.wheels.push(w);
  });
  g.spin = a => g.wheels.forEach(w => w.rotation.x = a);
  return g;
}

// ---------------------------------------------------------------- misc
function puff(sc, x, y, z, seed = 1) {
  const r = K.rng(seed), g = new T.Group(), m = new T.MeshStandardMaterial({ color: 0xd9d2c4, flatShading: true, transparent: true, opacity: .9 });
  for (let i = 0; i < 6; i++) { const b = new T.Mesh(new T.IcosahedronGeometry(.25 + r() * .2, 0), m); b.position.set((r() - .5) * .6, (r() - .5) * .4, (r() - .5) * .6); g.add(b); }
  g.position.set(x, y, z); g.m = m; sc.add(g);
  g.at = (t, t0) => { const u = K.clamp((t - t0) / 1.4); g.visible = t > t0; g.scale.setScalar(.3 + u * 1.6); m.opacity = .9 * (1 - u); g.position.y = y + u * .8; };
  return g;
}
function tracer(sc) { const b = new T.Mesh(new T.BoxGeometry(.035, .035, 1.4), new T.MeshBasicMaterial({ color: 0xffd98a, fog: false })); sc.add(b); return b; }
function dashRing(sc, r, color = 0xff7a66, y = .06) {
  const g = new T.Group(), m = new T.MeshBasicMaterial({ color, transparent: true, opacity: .9 });
  for (let i = 0; i < 64; i += 2) { const a = (i + .5) / 64 * PI * 2; const b = new T.Mesh(new T.BoxGeometry(.18, .02, r * PI * 2 / 64), m); b.position.set(Math.cos(a) * r, y, Math.sin(a) * r); b.rotation.y = -a; g.add(b); }
  g.m = m; sc.add(g); return g;
}
function kick(cam, t, t0, amp = .08) { const u = (t - t0) * 30; if (u < 0 || u > 7) return; const s = (Math.floor(u) % 2 ? -1 : 1) * amp * (1 - u / 7); cam.position.y += s; cam.rotation.z += s * .3; }

// ================================================================= SHOTS
// 0. Soldiers march into the wheat with a machine gun
S({
  value: '20,000', status: 'THE ARMY', sub: 'NOV 1932',
  caption: 'In 1932, Australia sent soldiers<br>with machine guns into a war against birds.',
  setup() {
    const sc = outback(), cam = K.camera(46);
    wheat(sc, { clear: (x, z) => Math.abs(x) < 1.6 && z > -40 });
    sc.add(K.box(2.6, .02, 120, 0xb08a52, 0, .01, -30));
    [[-9, -20, 1.8, 2], [10, -34, 2, 4], [-14, -55, 2.2, 6], [6, -70, 2.4, 8]].forEach(a => sc.add(gum(...a)));
    const men = [0, 1, 2].map(i => { const p = soldier({ officer: i === 0 }); p.rotation.y = PI; sc.add(p); return p; });
    const gun = lewis(); men[1].add(gun); gun.position.set(-.34, 1.42, .1); gun.rotation.set(-.5, 0, .1); gun.scale.setScalar(.9);
    const em = flock(sc, { n: 14, cx: 0, cz: -38, rx: 10, rz: 5, seed: 2 });
    return {
      scene: sc, camera: cam, update(t, k) {
        men.forEach((p, i) => { p.position.set([-.0, -.75, .75][i], 0, 3.5 - [0, 1.3, 1.3][i] - t * 1.1); K.walk(p, t * 7 + i); });
        men[1].parts.armL.rotation.x = -.6; men[1].parts.armR.rotation.x = -.4;
        em.forEach(e => { e.rotation.y = 0; emuPeck(e, t); });
        em.forEach((e, i) => { const up = K.ramp(t, 3.7 + i * .05, .3); if (up > 0) { e.parts.neck.rotation.x = K.lerp(e.parts.neck.rotation.x, .05, up); e.parts.head.rotation.set(0, 0, 0); e.parts.root.rotation.x *= 1 - up; } });
        K.dolly(cam, k, [2.6, 1.0, 9.5], [1.7, 1.25, 6.4], [0, 1.6, -6]);
      }
    };
  }
});

// 1. "And lost." Close-up: one emu stares into the lens
S({
  value: '20,000', status: 'THE EMUS', statusColor: CORAL, sub: 'SPOILER',
  caption: 'And lost.',
  setup() {
    const sc = outback({ fogNear: 8, fogFar: 60 }), cam = K.camera(36);
    wheat(sc, { z0: -40, z1: 4, n: 1000, seed: 8 });
    const e = emu({ seed: 4 }); sc.add(e);
    return {
      scene: sc, camera: cam, update(t, k) {
        emuIdle(e, 0); e.parts.neck.rotation.x = .05; e.parts.head.rotation.set(0, 0, K.ramp(t, .25, .25) * .32);
        K.dolly(cam, k, [0, 2.0, 3.9], [0, 2.02, 3.4], [0, 1.85, 0]);
      }
    };
  }
});

// 2. Twenty thousand emus storm the wheat fields
S({
  value: (t) => fmt(Math.min(20000, 20000 * K.ramp(t, .1, .9))), status: 'NOBODY', sub: 'W. AUSTRALIA',
  caption: 'Twenty thousand emus had stormed<br>the wheat fields of Western Australia.',
  setup() {
    const sc = outback({ range: 40, fogFar: 170 }), cam = K.camera(48);
    wheat(sc, { n: 2600, x0: -45, x1: 45, z0: -90, z1: 20, seed: 11 });
    sc.add(K.house(-8, -48, { wall: 0xe8dcc0, roof: 0x9aa2a6, door: 0x7a4a2c }));
    sc.add(K.fence(-30, -8, 60, 0x9a8264));
    [[-18, -60, 2.2, 3], [14, -66, 2, 5], [24, -40, 1.8, 7]].forEach(a => sc.add(gum(...a)));
    const em = flock(sc, { n: 70, cx: 0, cz: -12, rx: 18, rz: 16, seed: 21 });
    em.forEach(e => { e.x0 = e.position.x; e.rotation.y = PI / 2 + (e.position.z % 1) * .1; });
    return {
      scene: sc, camera: cam, update(t, k) {
        em.forEach(e => { e.position.x = e.x0 - 14 + t * 6.5; emuRun(e, t * 13 + e.ph); });
        K.dolly(cam, k, [-6, 15, 30], [-2, 12, 23], [2, 0, -12]);
      }
    };
  }
});

// 3. The army sends Meredith, two soldiers, two guns, 10,000 bullets
S({
  value: '20,000', status: 'THE ARMY', sub: 'ON PAPER',
  caption: 'So the army sent Major Meredith, two soldiers,<br>two machine guns, and ten thousand bullets.',
  setup() {
    const sc = outback({ fogNear: 20, fogFar: 90 }), cam = K.camera(42);
    wheat(sc, { z0: -60, z1: -6, n: 900, seed: 13 });
    const tr = truck(); tr.position.set(1.8, 0, -4.5); tr.rotation.y = -.5; sc.add(tr);
    const mer = soldier({ officer: true, shirt: 0x7d6e45 }); mer.position.set(0, 0, 0); sc.add(mer);
    const s1 = soldier(), s2 = soldier({ hair: 0x8a6a3a }); s1.position.set(-1.25, 0, -.6); s2.position.set(1.25, 0, -.6); sc.add(s1, s2);
    const g1 = lewis(), g2 = lewis(); [g1, g2].forEach((g, i) => { g.position.set(-.6 + i * 1.2, .55, 1.6); g.rotation.y = .1 - i * .2; sc.add(g); g.add(K.box(.02, .5, .02, 0x222222, .12, -.27, .5), K.box(.02, .5, .02, 0x222222, -.12, -.27, .5)); });
    const crates = [];
    for (let i = 0; i < 6; i++) { const c = K.box(.6, .36, .4, 0x6f7a4a, -2.4 + (i % 3) * .64, .18 + Math.floor(i / 3) * .37, 1.2); sc.add(c); crates.push(c); }
    const L = [K.label('MAJOR MEREDITH', .68, '#f3ead8'), K.label('×2 SOLDIERS', .62, '#f3ead8'), K.label('×2 MACHINE GUNS', .62, '#f3ead8'), K.label('10,000 BULLETS', .68, GOLD)];
    L[0].position.set(0, 2.75, 0); L[1].position.set(.85, 2.35, -.6); L[2].position.set(.75, .95, 1.75); L[3].position.set(-1.15, .72, 1.6); L.forEach(l => sc.add(l));
    const T0 = [1.2, 2.25, 3.3, 4.35];
    return {
      scene: sc, camera: cam, update(t, k) {
        [mer, s1, s2].forEach((p, i) => { K.idle(p, t + i); p.parts.head.rotation.y *= .3; });
        salute(mer, K.ramp(t, 1.2, .3) * (1 - K.ramp(t, 2.2, .3)));
        [s1, s2].forEach(p => p.scale.setScalar(K.pop(t, 2.2)));
        [g1, g2].forEach(g => g.scale.setScalar(K.pop(t, 3.25)));
        crates.forEach((c, i) => c.scale.setScalar(K.pop(t, 4.3 + i * .05)));
        L.forEach((l, i) => { l.pop(K.pop(t, T0[i])); l.material.opacity = 1 - K.ramp(t, T0[i] + 1.5, .3) * (i < 3 ? .0 : 0); });
        L[0].material.opacity = L[1].material.opacity = L[2].material.opacity = 1;
        K.dolly(cam, k, [-.2, 2.3, 11.2], [-.1, 2.0, 9.6], [-.1, 1.25, 0]);
      }
    };
  }
});

// 4. Day one: emus jog just outside the gun's range
S({
  value: '20,000', status: 'THE EMUS', statusColor: CORAL, sub: 'DAY 1',
  caption: 'On day one, the emus<br>simply ran out of range.',
  setup() {
    const sc = outback({ range: 30 }), cam = K.camera(44);
    rocks(sc, { n: 40, x0: -25, x1: 25, z0: -40, z1: 10 });
    [[-12, -30, 1.8, 3], [12, -36, 2.0, 5]].forEach(a => sc.add(gum(...a)));
    sc.add(sandbags(0, 1.0));
    const gun = lewis(); gun.position.set(0, 1.05, .8); gun.z0 = .8; gun.rotation.y = PI; sc.add(gun);
    const gn = soldier(); gn.position.set(0, 0, 2.0); gn.rotation.y = PI; aim(gn); sc.add(gn);
    const ring = dashRing(sc, 14);
    const em = flock(sc, { n: 12, cx: 0, cz: -11, rx: 7, rz: 3, seed: 31 });
    const L = K.label('OUT OF RANGE', 2.6, CORAL); L.position.set(0, 3.4, -14); sc.add(L);
    const tr = [0, 1, 2, 3, 4].map(() => tracer(sc));
    return {
      scene: sc, camera: cam, update(t, k) {
        const firing = t < 1.9;
        gun.fire(t, firing);
        tr.forEach((b, i) => { const u = frac(t * 2.2 + i / 5); b.visible = firing; b.position.set((i - 2) * .4 * u, 1.05 + u * .4, .2 - u * 13); b.rotation.y = -(i - 2) * .03; });
        const run = K.ramp(t, .4, .8);
        em.forEach(e => { e.rotation.y = PI * run; if (run > .02) { emuRun(e, t * 12 + e.ph, .7); e.position.z = e.position.z; } else emuIdle(e, t); });
        em.forEach((e, i) => { e.position.z = -11 + ((i * 37) % 7) - 3 - Math.max(0, t - .5) * 2.8; });
        ring.m.opacity = .5 + .4 * K.ramp(t, .2, .4);
        L.pop(K.pop(t, 1.9));
        K.dolly(cam, k, [.9, 3.8, 8.6], [.6, 3.9, 7.4], [0, .9, -9]);
      }
    };
  }
});

// 5. The ambush at the dam
S({
  value: '20,000', status: 'THE ARMY', sub: 'DAY 3',
  caption: 'Two days later, he ambushed<br>a thousand of them at a dam.',
  setup() {
    const sc = outback({ range: 30, fogFar: 120 }), cam = K.camera(46);
    const bank = K.mesh(new T.TorusGeometry(7.2, .9, 5, 28), K.mat(0xa88a5a), 0, .05, -14); bank.rotation.x = PI / 2; bank.scale.z = .45; sc.add(bank);
    const water = K.mesh(new T.CircleGeometry(7, 28), new T.MeshStandardMaterial({ color: 0x4f8fb5, roughness: .2, metalness: .1 }), 0, .14, -14); water.rotation.x = -PI / 2; sc.add(water);
    [[-10, -20, 2, 3], [9, -24, 2.2, 5], [-4, -30, 1.8, 7]].forEach(a => sc.add(gum(...a)));
    const bush = [[-1.6, 3.2], [1.4, 3.6], [0, 2.6], [-2.8, 4.4], [2.8, 4.2]].map(([x, z], i) => { const b = K.ball(.7 + (i % 2) * .2, [0x6f8a4c, 0x7f9a5a][i % 2], x, .45, z, 1); sc.add(b); return b; });
    const gun = lewis(); gun.position.set(.2, .95, 3.1); gun.rotation.y = PI; sc.add(gun);
    const hats = [-.6, 1.0].map(x => { const s = soldier(); s.position.set(x, -.75, 4.3); s.rotation.y = PI; sc.add(s); return s; });
    const em = flock(sc, { n: 60, cx: 0, cz: -32, rx: 14, rz: 8, seed: 41 });
    return {
      scene: sc, camera: cam, update(t, k) {
        em.forEach(e => { e.rotation.y = Math.atan2(-e.position.x * .02, 1); e.position.z = e.z0 ?? (e.z0 = e.position.z); e.position.z = e.z0 + t * 2.4; emuRun(e, t * 7 + e.ph, .45); });
        hats.forEach((h, i) => { h.position.y = -.75 + K.ramp(t, 1.4 + i * .2, .4) * .25; });
        K.dolly(cam, k, [.4, 2.6, 9.4], [.3, 2.9, 7.9], [0, .6, -14]);
      }
    };
  }
});

// 6. The gun jams after twelve
S({
  value: '20,000', status: 'THE EMUS', statusColor: CORAL, sub: 'DAY 3',
  alert: { label: 'EMUS HIT', value: (t) => Math.min(12, Math.floor(K.clamp(t / .62) * 12)) },
  caption: 'The gun jammed after twelve.',
  setup() {
    const sc = outback({ fogNear: 8, fogFar: 50 }), cam = K.camera(40);
    [[-1.6, 1.2], [1.6, 1.4], [-2.4, -1]].forEach(([x, z], i) => sc.add(K.ball(.8, [0x6f8a4c, 0x7f9a5a][i % 2], x, .4, z, 1)));
    const gun = lewis(); gun.position.set(0, .95, 0); gun.rotation.y = PI / 2 + .55; gun.z0 = 0; sc.add(gun);
    sc.add(sandbags(0, .5, 1.8));
    const smoke = puff(sc, -.9, 1.15, .4, 3);
    const L = K.label('JAMMED', .75, CORAL); L.position.set(.15, 1.65, 0); sc.add(L);
    return {
      scene: sc, camera: cam, update(t, k) {
        gun.fire(t, t < .62, 13);
        const jt = t - .62; gun.rotation.z = jt > 0 ? Math.sin(jt * 40) * .04 * Math.exp(-jt * 6) : 0;
        smoke.at(t, .64);
        L.pop(K.pop(t, .66));
        K.dolly(cam, k, [1.1, 1.75, 4.4], [.9, 1.6, 3.7], [.25, 1.2, 0]);
        kick(cam, t, .64, .05);
      }
    };
  }
});

// 7. New plan: mount the gun on a truck
S({
  value: '20,000', status: 'THE ARMY', sub: 'NEW PLAN',
  caption: 'Luckily, he had a new plan:<br>mount the gun on a truck.',
  setup() {
    const sc = outback({ range: 24 }), cam = K.camera(44);
    wheat(sc, { n: 900, z0: -60, z1: -8, seed: 17 });
    const tr = truck(); sc.add(tr);
    const mer = soldier({ officer: true, shirt: 0x7d6e45 }); mer.position.set(-2.2, 0, 2.4); mer.rotation.y = .5; sc.add(mer);
    const gun = lewis(); gun.position.set(0, 2.0, -.9); tr.add(gun);
    const gnr = soldier(); gnr.position.set(0, .93, -1.9); aim(gnr); tr.add(gnr);
    const bulb = K.label('!', 1.4, GOLD); bulb.position.set(-2.2, 3.0, 2.4); sc.add(bulb);
    return {
      scene: sc, camera: cam, update(t, k) {
        K.idle(mer, t); mer.parts.head.rotation.y = .6;
        mer.parts.armR.rotation.set(-1.2 * K.ramp(t, 1.9, .3), 0, -.4);
        bulb.pop(K.pop(t, .9));
        const on = K.ramp(t, 2.0, .5);
        gun.scale.setScalar(K.pop(t, 2.0)); gnr.scale.setScalar(K.pop(t, 2.1));
        tr.position.set(K.lerp(-6, 0, K.smooth(t / 1.8)), 0, 0); tr.rotation.y = PI / 2; tr.spin(-tr.position.x / .44);
        K.dolly(cam, k, [5.5, 2.3, 8.5], [4.2, 2.6, 7.0], [-.5, 1.4, 0]);
      }
    };
  }
});

// 8. Emus run 50 km/h, the truck bounces and falls behind
S({
  value: '20,000', status: 'THE EMUS', statusColor: CORAL, sub: '50 KM/H',
  caption: 'Unluckily, emus can run fifty kilometres an hour,<br>over ground no truck could handle.',
  setup() {
    const sc = outback({ range: 30, fogNear: 25, fogFar: 120 }), cam = K.camera(46);
    rocks(sc, { n: 140, x0: -40, x1: 160, z0: -12, z1: 10, seed: 19 });
    for (let i = 0; i < 9; i++) sc.add(gum(-20 + i * 22, -18 - (i % 3) * 5, 1.7 + (i % 2) * .4, 40 + i));
    const em = flock(sc, { n: 9, cx: 0, cz: -1, rx: 4, rz: 2.5, seed: 51 });
    em.forEach(e => { e.x0 = e.position.x; e.rotation.y = PI / 2; });
    const tr = truck(); tr.rotation.y = PI / 2; sc.add(tr);
    const gun = lewis(); gun.position.set(0, 2.0, -.9); tr.add(gun);
    const gnr = soldier(); gnr.position.set(0, .93, -1.9); aim(gnr); tr.add(gnr);
    const L = K.label('50 KM/H', 1.05, GOLD);
    sc.add(L);
    return {
      scene: sc, camera: cam, update(t, k) {
        const ex = 6 + t * 13.9, tx = t * 7.5;
        em.forEach(e => { e.position.x = e.x0 + ex; emuRun(e, t * 18 + e.ph, .95); });
        const bump = t > 3.0 ? 1 : .35;
        tr.position.set(tx, Math.abs(Math.sin(t * 9)) * .16 * bump, 1.5); tr.rotation.z = Math.sin(t * 7.3) * .05 * bump; tr.rotation.x = Math.sin(t * 5.1) * .04 * bump; tr.spin(-tx / .44);
        gnr.position.y = .93 + Math.abs(Math.sin(t * 9 + .4)) * .12 * bump; gnr.rotation.z = Math.sin(t * 8) * .12 * bump;
        L.position.set(ex - 1.4, 2.55, -1); L.pop(K.pop(t, 1.7));
        const cx = K.lerp(tx + 3, ex - 3, K.smooth(k * 1.1));
        cam.position.set(cx - 2, 3.0, 16.5); cam.lookAt(cx + 1, 1.1, 0);
      }
    };
  }
});

// 9. Every flock posted a tall lookout
S({
  value: '20,000', status: 'THE EMUS', statusColor: CORAL, sub: 'LOOKOUTS',
  caption: 'You see, every flock<br>posted a tall lookout.',
  setup() {
    const sc = outback({ fogNear: 18, fogFar: 90 }), cam = K.camera(42);
    wheat(sc, { n: 1100, z0: -50, z1: 6, seed: 23, clear: (x, z) => x * x + (z + 2) * (z + 2) < 9 });
    const mound = K.ball(2.2, 0xa88a5a, 0, -1.5, -2, 1); mound.scale.y = .5; sc.add(mound);
    const look = emu({ seed: 77, s: 1.25 }); look.position.set(0, .0, -2); look.rotation.y = .3; sc.add(look);
    const em = flock(sc, { n: 10, cx: 0, cz: -2, rx: 5, rz: 4, seed: 61 }).filter(e => Math.hypot(e.position.x, e.position.z + 2) > 2.2);
    const L = K.label('LOOKOUT', 1.1, GOLD); L.position.set(0, 3.55, -2); sc.add(L);
    return {
      scene: sc, camera: cam, update(t, k) {
        em.forEach(e => emuPeck(e, t));
        emuIdle(look, t); look.parts.neck.rotation.x = -.05; look.parts.head.rotation.y = Math.sin(t * 1.3) * .9;
        L.pop(K.pop(t, 2.15));
        K.dolly(cam, k, [3.5, 1.3, 7.5], [2.6, 1.5, 5.9], [0, 2.0, -2]);
      }
    };
  }
});

// 10. Guns appear -- the flock scatters in every direction (top-down)
S({
  value: '20,000', status: 'THE EMUS', statusColor: CORAL, sub: 'SCATTERING',
  caption: 'The moment the guns appeared,<br>they scattered in every direction,',
  setup() {
    const sc = outback({ range: 30, sunPos: [6, 18, 4] }), cam = K.camera(50);
    rocks(sc, { n: 50, x0: -14, x1: 14, z0: -16, z1: 14, seed: 71 });
    const em = flock(sc, { n: 34, cx: 0, cz: -2, rx: 3.6, rz: 3.6, seed: 81 });
    em.forEach(e => { e.p0 = e.position.clone(); const a = Math.atan2(e.p0.x, e.p0.z + 2) + (e.ph % 1 - .5) * .4; e.dir = [Math.sin(a), Math.cos(a)]; e.rot0 = e.rotation.y; });
    const tr = truck(); tr.rotation.y = PI; sc.add(tr);
    const gun = lewis(); gun.position.set(0, 2.0, -.9); gun.rotation.y = 0; tr.add(gun);
    return {
      scene: sc, camera: cam, update(t, k) {
        const ty = K.smooth((t - .3) / .9); tr.position.set(0, 0, K.lerp(18, 9, ty)); tr.spin(tr.position.z / .44);
        const go = Math.max(0, t - 1.45);
        em.forEach(e => {
          if (go <= 0) { emuPeck(e, t); e.rotation.y = e.rot0; return; }
          e.rotation.y = Math.atan2(e.dir[0], e.dir[1]);
          const d = 7.5 * go; e.position.set(e.p0.x + e.dir[0] * d, 0, e.p0.z + e.dir[1] * d); emuRun(e, t * 17 + e.ph, .9);
        });
        K.dolly(cam, k, [0, 26, 9], [0, 23, 8], [0, 0, 0]);
      }
    };
  }
});

// 11. Like catching spilled marbles
S({
  value: '20,000', status: 'THE EMUS', statusColor: CORAL, sub: 'SCATTERING',
  caption: 'like trying to catch<br>a bag of spilled marbles.',
  setup() {
    const sc = K.indoor({ floor: 0x9c6a3c }), cam = K.camera(46);
    for (let i = 0; i < 16; i++) sc.add(K.box(.02, .005, 30, 0x7a4f2a, -8 + i * .55, .003, 0));
    const r = K.rng(5), cols = [0xe0503c, 0x3c7ae0, 0xf0c040, 0x40b070, 0xb050d0, 0xf08a30, 0x30c0d0];
    const mb = []; for (let i = 0; i < 46; i++) { const m = K.mesh(new T.SphereGeometry(.06, 14, 10), new T.MeshStandardMaterial({ color: cols[i % 7], roughness: .15, metalness: .1 })); const a = r() * PI * 2, v = 1.2 + r() * 2.4; m.d = [Math.cos(a), Math.sin(a)]; m.v = v; m.dl = r() * .15; sc.add(m); mb.push(m); }
    const bag = K.ball(.22, 0x8a6a4a, 0, .2, 0, 1); bag.scale.set(1, 1.2, 1); sc.add(bag);
    const hand = new T.Group(); const arm = K.cyl(.08, .08, 1.2, 0x8c7d52, 0, 0, -.6, 7); arm.rotation.x = PI / 2; hand.add(arm, K.ball(.11, 0xe0ad84, 0, 0, 0, 1)); sc.add(hand);
    return {
      scene: sc, camera: cam, update(t, k) {
        const t0 = 1.2;
        bag.rotation.z = -K.ramp(t, .9, .3) * 1.3; bag.position.set(K.ramp(t, .9, .3) * .1, .2, 0);
        mb.forEach(m => { const u = Math.max(0, t - t0 - m.dl), kk = 1.6, d = m.v / kk * (1 - Math.exp(-kk * u)); m.position.set(m.d[0] * d, .06 + (u < .25 ? Math.abs(Math.sin(u * 25)) * .05 : 0), m.d[1] * d); m.rotation.set(d * 5, 0, d * 3); m.visible = u > 0 || true; if (u <= 0) m.position.set((m.d[0]) * .08, .14, m.d[1] * .08); });
        const hk = K.ramp(t, 1.6, .5); const tgt = mb[3]; const ux = Math.max(0, t - 1.9);
        hand.position.set(K.lerp(1.4, tgt.position.x + .25 * Math.sin(ux * 6), hk), .14, K.lerp(1.6, tgt.position.z + .35, hk)); hand.rotation.y = .6;
        K.dolly(cam, k, [0, 3.4, 3.2], [0, 3.0, 2.7], [0, 0, -.2]);
      }
    };
  }
});

// 12. 986 birds, ~10 bullets each -- casings pile up
S({
  value: (t) => fmt(20000 - 986 * K.ramp(t, 1.0, 1.0)), status: 'THE ARMY?', sub: 'DEC 1932',
  alert: { label: 'BULLETS FIRED', value: (t) => fmt(9860 * K.ramp(t, .3, 3.6)) },
  caption: 'By December, the army claimed 986 birds,<br>at roughly ten bullets each.',
  setup() {
    const sc = outback({ fogNear: 10, fogFar: 60 }), cam = K.camera(42);
    rocks(sc, { n: 20, x0: -8, x1: 8, z0: -14, z1: 2 });
    const r = K.rng(9), cas = [];
    for (let i = 0; i < 260; i++) { const c = K.cyl(.025, .025, .12, 0xd9a83a, 0, 0, 0, 6, { metalness: .6, roughness: .35 }); const a = r() * PI * 2, d = Math.pow(r(), .7) * 1.1; c.p = [Math.cos(a) * d, Math.sin(a) * d]; c.h = Math.max(0, .55 - d * .5) * r() + .03; c.ti = .3 + (i / 260) * 3.4; c.rotation.set(r() * 3, r() * 3, PI / 2); sc.add(c); cas.push(c); }
    const em = emu({ seed: 99 }); em.position.set(2.6, 0, -2.5); em.rotation.y = -.6; sc.add(em);
    const L = K.label('10 BULLETS = 1 EMU', .48, GOLD); L.position.set(.25, 1.08, 0); sc.add(L);
    return {
      scene: sc, camera: cam, update(t, k) {
        cas.forEach(c => { const u = K.clamp((t - c.ti) / .3); c.visible = t > c.ti; c.position.set(c.p[0], c.h + (1 - u) * 1.6, c.p[1]); });
        emuIdle(em, t); em.parts.head.rotation.y = -.5;
        L.pop(K.pop(t, 3.2));
        K.dolly(cam, k, [.6, 2.4, 5.4], [.4, 2.0, 4.4], [.5, .5, -.6]);
      }
    };
  }
});

// 13. "The invulnerability of tanks" -- an emu strolls through tracer fire
S({
  value: '19,014', status: 'THE EMUS', statusColor: CORAL, sub: 'TANK MODE',
  caption: 'Meredith admitted the emus could face<br>machine guns with the invulnerability of tanks.',
  setup() {
    const sc = outback({ mood: 'dust' }), cam = K.camera(40);
    rocks(sc, { n: 40, x0: -12, x1: 12, z0: -30, z1: 6, seed: 3 });
    [[-7, -16, 1.8, 5], [8, -20, 2, 9]].forEach(a => sc.add(gum(...a)));
    const e = emu({ seed: 13, s: 1.1 }); sc.add(e);
    const tr = [...Array(9)].map(() => tracer(sc));
    const L = K.label('INVULNERABLE', .72, GOLD); L.position.set(0, 2.85, 0); sc.add(L);
    return {
      scene: sc, camera: cam, update(t, k) {
        e.position.set(0, 0, -3.6 + t * .85); emuRun(e, t * 6, .45); e.parts.root.position.y *= .4; e.parts.neck.rotation.x = .1; e.parts.head.rotation.set(-.05, 0, 0);
        tr.forEach((b, i) => { const u = frac(t * 1.7 + i * .37); const side = i % 2 ? 1 : -1; b.position.set(side * (.9 + (i % 3) * .5), .6 + (i % 4) * .45, e.position.z - 18 + u * 30); });
        L.position.z = e.position.z; L.pop(K.pop(t, 2.8));
        K.dolly(cam, k, [1.2, 1.35, 7.6], [.7, 1.5, 5.9], [0, 1.55, -2]);
      }
    };
  }
});

// 14. The soldiers went home (dusk)
S({
  value: '19,014', status: 'THE EMUS', statusColor: CORAL, sub: 'ARMY LEAVES',
  caption: 'The soldiers went home.',
  setup() {
    const sc = outback({ mood: 'dusk', fogNear: 30, fogFar: 160 }), cam = K.camera(44);
    wheat(sc, { n: 1600, x0: -40, x1: 40, z0: -90, z1: 10, seed: 29, clear: (x) => Math.abs(x) < 2.4 });
    sc.add(K.box(3.6, .02, 200, 0x9a7a4a, 0, .01, -60));
    const tr = truck(); tr.rotation.y = PI; sc.add(tr);
    const gnr = soldier(); gnr.position.set(0, .93, -1.8); gnr.rotation.y = PI; tr.add(gnr);
    return {
      scene: sc, camera: cam, update(t, k) {
        tr.position.set(0, Math.abs(Math.sin(t * 8)) * .04, -6 - t * 5); tr.spin(t * 11);
        gnr.parts.head.rotation.x = .3;
        K.dolly(cam, k, [1.8, 1.4, 4.5], [1.4, 1.5, 3.8], [0, 1.2, -14]);
      }
    };
  }
});

// 15. The emus stayed (dusk, a line of emus watching from the fence)
S({
  value: '19,014', status: 'THE EMUS', statusColor: CORAL, sub: 'STILL HERE',
  caption: 'The emus stayed.',
  setup() {
    const sc = outback({ mood: 'dusk', fogNear: 20, fogFar: 140 }), cam = K.camera(42);
    wheat(sc, { n: 1400, x0: -30, x1: 30, z0: -70, z1: -2, seed: 31 });
    sc.add(K.fence(-12, -.5, 24, 0x6a5a44));
    const em = [...Array(7)].map((_, i) => { const e = emu({ seed: 200 + i }); e.position.set(-4.2 + i * 1.4, 0, -1.6 - (i % 2) * .4); sc.add(e); return e; });
    return {
      scene: sc, camera: cam, update(t, k) {
        em.forEach((e, i) => { emuIdle(e, t + i); e.rotation.y = (i - 3) * -.05; e.parts.head.rotation.y = Math.sin(t * 1.5 + i) * .25; });
        K.dolly(cam, k, [0, 1.6, 10.5], [0, 1.7, 9.4], [0, 1.6, -1.6]);
      }
    };
  }
});

// 16. The coat of arms -- undefeated
S({
  value: '19,014', status: (t) => t > 3.45 ? 'UNDEFEATED' : 'THE EMUS', statusColor: (t) => t > 3.45 ? GOLD : CORAL, sub: 'SINCE 1908',
  caption: "And today, the emu is on Australia's<br>coat of arms. Undefeated.",
  setup() {
    const sc = new T.Scene(); sc.background = K.skyGradient('#14203f', '#3b4f7e'); sc.fog = new T.Fog(0x2a3860, 14, 40);
    K.lights(sc, { sun: 0xfff0d8, sunI: 2.8, sky: 0xbfd2ff, ground: 0x3a3020, hemiI: 1.0, pos: [3, 8, 7], range: 8 });
    const base = K.cyl(3.6, 3.8, .3, 0x2a2f45, 0, .15, 0, 32); sc.add(base);
    // shield
    const sh = new T.Shape(); sh.moveTo(-.85, 1.1); sh.lineTo(.85, 1.1); sh.lineTo(.85, -.2); sh.quadraticCurveTo(.8, -.9, 0, -1.2); sh.quadraticCurveTo(-.8, -.9, -.85, -.2); sh.lineTo(-.85, 1.1);
    const sg = new T.ExtrudeGeometry(sh, { depth: .14, bevelEnabled: true, bevelSize: .06, bevelThickness: .04, bevelSegments: 1 });
    const shield = K.mesh(sg, K.mat(0xd9a83a, { metalness: .5, roughness: .4 }), 0, 1.75, -.2); sc.add(shield);
    const inner = K.mesh(new T.ExtrudeGeometry(sh, { depth: .05, bevelEnabled: false }), K.mat(0xc23a3a), 0, 1.75, -.02); inner.scale.set(.85, .85, 1); sc.add(inner);
    const band = K.box(1.3, .25, .06, 0xf3ead8, 0, 2.05, .05); sc.add(band);
    // seven-pointed star
    const st = new T.Shape(); for (let i = 0; i < 14; i++) { const a = PI / 2 + i * PI / 7, rr = i % 2 ? .16 : .38; i ? st.lineTo(Math.cos(a) * rr, Math.sin(a) * rr) : st.moveTo(Math.cos(a) * rr, Math.sin(a) * rr); }
    const star = K.mesh(new T.ExtrudeGeometry(st, { depth: .08, bevelEnabled: false }), new T.MeshStandardMaterial({ color: 0xffd36a, emissive: 0x7a5200, emissiveIntensity: .6, metalness: .5, roughness: .3 }), 0, 3.45, -.2); sc.add(star);
    // wattle sprigs
    const r = K.rng(4); for (let i = 0; i < 26; i++) { const a = PI * (.05 + .9 * (i / 25)); sc.add(K.ball(.07 + r() * .05, 0xf2c230, Math.cos(a) * 1.25, .5 + Math.sin(a) * -.05 + r() * .25, .4 + r() * .2, 0)); }
    // kangaroo
    const roo = new T.Group(), rc = 0xb5764a;
    const rb = K.ball(.42, rc, 0, 1.2, 0, 1); rb.scale.set(.9, 1.35, .85); roo.add(rb);
    const rh = K.ball(.18, rc, 0, 2.02, .1, 1); rh.scale.set(.9, 1, 1.3); roo.add(rh);
    [-1, 1].forEach(sx => { const ear = K.mesh(new T.ConeGeometry(.06, .25, 4), K.mat(rc), sx * .09, 2.25, .02); ear.rotation.z = -sx * .2; roo.add(ear); });
    const sn = K.mesh(new T.ConeGeometry(.08, .2, 5), K.mat(0x9a6038), 0, 1.98, .32); sn.rotation.x = PI / 2; roo.add(sn);
    const rk = new T.MeshBasicMaterial({ color: 0x111111 }); [-1, 1].forEach(sx => { const e = new T.Mesh(new T.SphereGeometry(.025, 8, 6), rk); e.position.set(sx * .08, 2.07, .25); roo.add(e); });
    [-1, 1].forEach(sx => { roo.add(K.ball(.24, rc, sx * .22, .65, 0, 1)); roo.add(K.box(.12, .07, .55, 0x9a6038, sx * .2, .33, .15)); const arm = K.cyl(.05, .04, .4, rc, sx * .25, 1.35, .3, 6); arm.rotation.x = -.9; roo.add(arm); });
    const tail = K.cyl(.12, .04, 1.3, rc, 0, .45, -.7, 6); tail.rotation.x = 1.1; roo.add(tail);
    roo.position.set(-1.45, .3, 0); roo.rotation.y = .5; sc.add(roo);
    const e = emu({ seed: 5, s: 1.08 }); e.position.set(1.45, .3, 0); e.rotation.y = -.5; sc.add(e);
    const glowR = new T.Mesh(new T.CircleGeometry(3.4, 48), new T.MeshBasicMaterial({ color: 0xffd36a, transparent: true, opacity: .0, depthWrite: false })); glowR.position.set(0, 2.0, -1.2); sc.add(glowR);
    return {
      scene: sc, camera: cam0(), update(t, k) {
        emuIdle(e, t); e.parts.neck.rotation.x = -.04;
        const look = K.ramp(t, 3.35, .25); e.parts.head.rotation.set(0, K.lerp(-.4, .55, look), look * .22);
        star.rotation.y = t * .6;
        glowR.material.opacity = .14 * K.ramp(t, 3.4, .5);
        K.dolly(this.camera, k, [-1.2, 2.2, 12.6], [.4, 2.3, 10.8], [0, 1.75, 0]);
      }
    };
    function cam0() { return K.camera(44); }
  }
});
