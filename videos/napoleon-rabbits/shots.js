/* Napoleon vs. 3,000 Rabbits (1807) — vertical 3D Kaz short (28 shots, frame-locked to beats.json + words.json). */
const K = KAZ, T = K.THREE, PI = Math.PI;
K.config({ leftLabel: 'RABBITS', rightLabel: 'WHO IS WINNING', prefix: '', alertLabel: 'ATTACKERS', capIn: .06, capOut: .12 });

const CUT = [
  0, 2.25, 4.69, 5.40, 7.75, 10.51, 12.45, 15.16, 17.90, 19.95, 22.18, 24.10, 25.98, 28.20,
  30.02, 32.85, 34.61, 37.15, 39.16, 41.85, 43.64, 45.75, 47.49, 49.45, 51.26, 52.50, 53.74, 55.65, 57.315
];
let n = 0;
const S = o => {
  const i = n++;
  K.shot(Object.assign({ dur: (Math.round(CUT[i + 1] * 30) - Math.round(CUT[i] * 30)) / 30 }, o));
};
const CORAL = '#ff7a66', GOLD = '#e8c56a', BLUE = '#7cc6ff';
const frac = x => x - Math.floor(x);
const fmt = v => Math.round(v).toLocaleString('en-US');

// ---------------------------------------------------------------- world helpers
function meadow(o = {}) {
  return K.outdoor(Object.assign({
    skyTop: '#5f9cd9', skyBottom: '#f2e6c8', fog: 0xe6dcc0,
    fogNear: 26, fogFar: 130, grass: 0x6ea04b, sunPos: [10, 15, 8], range: 26,
  }, o));
}
const cypress = (x, z, s = 1.4, seed = 1) => {
  const g = new T.Group(), r = K.rng(seed);
  g.add(K.cyl(.13 * s, .18 * s, 1.3 * s, 0x5c422c, 0, .65 * s, 0, 6));
  const cols = [0x4c7c3a, 0x588a42, 0x3e6b2e];
  for (let i = 0; i < 3; i++) {
    const b = K.ball((.75 - i * .12) * s, cols[(i + Math.floor(r() * 3)) % 3], (r() - .5) * .2 * s, (1.7 + i * .75) * s, (r() - .5) * .2 * s, 0);
    b.scale.set(.9, 1.25, .9); g.add(b);
  }
  g.position.set(x, 0, z); return g;
};
function grassTufts(sc, { n = 900, x0 = -28, x1 = 28, z0 = -60, z1 = 10, seed = 3, clear = null } = {}) {
  const g = new T.ConeGeometry(.1, .42, 3); g.translate(0, .21, 0);
  const m = new T.InstancedMesh(g, K.mat(0xffffff), n), r = K.rng(seed), d = new T.Object3D(), c = new T.Color();
  const cols = [0x6ea04b, 0x7db354, 0x5d8c3e, 0x8bc25f];
  let i = 0, guard = 0;
  while (i < n && guard++ < n * 4) {
    const x = K.lerp(x0, x1, r()), z = K.lerp(z0, z1, r());
    if (clear && clear(x, z)) continue;
    d.position.set(x, 0, z); d.rotation.set((r() - .5) * .25, r() * 3, (r() - .5) * .25);
    d.scale.setScalar(.7 + r() * .7); d.updateMatrix();
    m.setMatrixAt(i, d.matrix); c.setHex(cols[i % 4]); m.setColorAt(i, c); i++;
  }
  m.count = i; m.receiveShadow = true; sc.add(m); return m;
}
function kick(cam, t, t0, amp = .09) {
  const u = (t - t0) * 30;
  if (u < 0 || u > 7) return;
  const s = (Math.floor(u) % 2 ? -1 : 1) * amp * (1 - u / 7);
  cam.position.y += s; cam.rotation.z += s * .35;
}

// ---------------------------------------------------------------- rabbit
function rabbit({ seed = 1, s = 1, col } = {}) {
  const r = K.rng(seed * 13 + 5), g = new T.Group(), p = {};
  const palette = [0xf2ede4, 0xe4d6c4, 0x9c7b5c, 0xd8c3aa, 0xc79e79];
  const bodyC = col ?? palette[Math.floor(r() * palette.length)];
  const bellyC = 0xfaf6ee;
  p.root = new T.Group(); g.add(p.root);

  const body = K.ball(.25, bodyC, 0, .27, -.04, 1); body.scale.set(.95, .92, 1.32); p.root.add(body);
  const chest = K.ball(.16, bellyC, 0, .24, .12, 1); p.root.add(chest);
  const tail = K.ball(.095, 0xffffff, 0, .25, -.34, 0); p.root.add(tail);

  p.head = new T.Group(); p.head.position.set(0, .44, .22); p.root.add(p.head);
  const hd = K.ball(.175, bodyC, 0, .02, .02, 1); hd.scale.set(1.0, .95, 1.1); p.head.add(hd);
  const snout = K.ball(.09, bellyC, 0, -.02, .14, 1); p.head.add(snout);
  const nose = K.ball(.032, 0xf28b94, 0, .01, .21, 0); p.head.add(nose);
  p.nose = nose;

  const ink = new T.MeshBasicMaterial({ color: 0x111114 }), wh = new T.MeshBasicMaterial({ color: 0xffffff });
  p.eyes = [-1, 1].map(sx => {
    const w = new T.Mesh(new T.SphereGeometry(.04, 8, 6), wh); w.position.set(sx * .11, .055, .12); p.head.add(w);
    const e = new T.Mesh(new T.SphereGeometry(.026, 8, 6), ink); e.position.set(sx * .125, .055, .148); p.head.add(e);
    return e;
  });

  p.earL = new T.Group(); p.earL.position.set(-.075, .14, -.02);
  p.earR = new T.Group(); p.earR.position.set(.075, .14, -.02);
  [p.earL, p.earR].forEach((er, idx) => {
    const outer = K.cyl(.035, .05, .3, bodyC, 0, .14, 0, 6); outer.scale.z = .55; er.add(outer);
    const inner = K.cyl(.02, .03, .22, 0xf0b2b8, 0, .14, .018, 5); inner.scale.z = .4; er.add(inner);
    er.rotation.z = (idx ? -1 : 1) * .18; er.rotation.x = -.14;
    p.head.add(er);
  });

  p.legL = K.box(.09, .08, .22, bodyC, -.14, .06, -.08); p.root.add(p.legL);
  p.legR = K.box(.09, .08, .22, bodyC, .14, .06, -.08); p.root.add(p.legR);
  p.pawL = K.ball(.055, bellyC, -.09, .06, .18, 0); p.root.add(p.pawL);
  p.pawR = K.ball(.055, bellyC, .09, .06, .18, 0); p.root.add(p.pawR);

  g.parts = p; g.scale.setScalar(s); g.seed = r() * 10; return g;
}
function rabbitHop(rb, ph, hopH = .24) {
  const p = rb.parts, u = Math.abs(Math.sin(ph));
  p.root.position.y = u * hopH;
  p.root.rotation.x = Math.cos(ph) * .22;
  p.earL.rotation.x = -.14 - u * .28; p.earR.rotation.x = -.14 - u * .28;
  p.legL.rotation.x = u * .45; p.legR.rotation.x = u * .45;
}
function rabbitIdle(rb, t) {
  const p = rb.parts, sd = rb.seed;
  p.root.position.y = Math.sin(t * 3 + sd) * .008;
  p.root.rotation.x = 0;
  p.head.rotation.y = Math.sin(t * 1.4 + sd) * .28;
  p.earL.rotation.x = -.14 + Math.sin(t * 3.5 + sd) * .08;
  p.earR.rotation.x = -.14 - Math.sin(t * 3.5 + sd) * .08;
}
function warren(sc, { n = 40, cx = 0, cz = 0, rx = 8, rz = 8, seed = 5, s = 1 } = {}) {
  const r = K.rng(seed), arr = [];
  for (let i = 0; i < n; i++) {
    const rb = rabbit({ seed: seed * 97 + i, s: s * (.85 + r() * .35) });
    const a = r() * PI * 2, d = Math.sqrt(r());
    rb.position.set(cx + Math.cos(a) * d * rx, 0, cz + Math.sin(a) * d * rz);
    rb.rotation.y = r() * PI * 2; rb.ph = r() * 10; rb.x0 = rb.position.x; rb.z0 = rb.position.z;
    sc.add(rb); arr.push(rb);
  }
  return arr;
}

// ---------------------------------------------------------------- French army & Napoleon
function frenchPerson({ emperor = false, officer = false, shirt = 0x1b2d56 } = {}) {
  const p = K.person({ shirt, pants: 0xf0ece0, skin: 0xe6b892, hair: 0x3b2a1e });
  // Red lapel & gold trim on coat
  p.parts.torso.add(K.box(.22, .52, .32, 0xf2eee4, 0, -.02, 0));
  p.parts.torso.add(K.box(.54, .1, .32, 0xb82929, 0, .25, 0));
  if (emperor || officer) {
    [-1, 1].forEach(sx => p.parts.torso.add(K.box(.18, .08, .26, 0xe8c56a, sx * .34, .29, 0)));
    p.parts.torso.add(K.box(.55, .07, .33, 0xb82929, 0, -.18, 0));
  }
  // Black bicorne hat
  const h = p.parts.head;
  const brim = K.cyl(.38, .44, .18, 0x181a20, 0, .48, 0, 12); brim.scale.set(1.25, 1, .52); h.add(brim);
  const crown = K.cyl(.22, .24, .22, 0x181a20, 0, .56, 0, 12); crown.scale.set(1.15, 1, .58); h.add(crown);
  h.add(K.box(.08, .08, .03, 0xe8c56a, 0, .54, .14));
  h.add(K.box(.05, .05, .035, 0x2f68c4, 0, .54, .145));
  if (emperor) {
    // Signature tucked hand / riding crop option
    p.crop = K.cyl(.014, .022, .72, 0x4f3018, 0, -.58, .3, 6);
    p.crop.rotation.x = PI / 2;
    p.parts.armR.add(p.crop);
  }
  return p;
}

// ---------------------------------------------------------------- wooden cage
function cage({ open = 0, s = 1 } = {}) {
  const g = new T.Group(), wd = 0x9c7244, dk = 0x6b4b29;
  g.add(K.box(1.1, .06, .8, dk, 0, .03, 0));
  g.add(K.box(1.1, .06, .8, dk, 0, .72, 0));
  [-.52, .52].forEach(x => [-.37, .37].forEach(z => g.add(K.box(.06, .72, .06, dk, x, .37, z))));
  for (let i = -2; i <= 2; i++) {
    g.add(K.box(.04, .66, .04, wd, i * .2, .37, -.37));
    g.add(K.box(.04, .66, .04, wd, -.52, .37, i * .14));
    g.add(K.box(.04, .66, .04, wd, .52, .37, i * .14));
  }
  const door = new T.Group(); door.position.set(0, .06, .38);
  for (let i = -2; i <= 2; i++) door.add(K.box(.04, .62, .04, wd, i * .2, .31, 0));
  door.add(K.box(1.04, .05, .05, dk, 0, .62, 0));
  door.rotation.x = open * 1.65;
  g.door = door; g.add(door); g.scale.setScalar(s); return g;
}

// ---------------------------------------------------------------- royal carriage
function carriage() {
  const g = new T.Group(), blue = 0x1b3366, gold = 0xe8c56a, dk = 0x261d18;
  g.add(K.box(1.8, .18, 3.2, dk, 0, .66, 0));
  // Cabin with large open side windows
  g.add(K.box(1.75, .62, 2.35, blue, 0, 1.06, -.1));
  g.add(K.box(1.85, .12, 2.45, gold, 0, 1.98, -.1));
  g.add(K.box(1.75, .14, 2.35, blue, 0, 2.1, -.1));
  // Corner pillars leaving big window openings
  [-.82, .82].forEach(x => [-1.22, -.2, 1.02].forEach(z => g.add(K.box(.12, .65, .14, gold, x, 1.66, z))));
  g.add(K.box(1.75, .65, .12, blue, 0, 1.66, -1.22));
  // Door panel on right side
  const door = new T.Group(); door.position.set(.88, 1.06, .4);
  door.add(K.box(.08, .85, .8, gold, 0, .2, -.4));
  g.door = door; g.add(door);
  // Coachman box + horses silhouette
  g.add(K.box(1.3, .45, .7, dk, 0, 1.25, 1.5));
  g.wheels = [];
  [[-.98, 1.2, .48], [.98, 1.2, .48], [-.98, -1.05, .66], [.98, -1.05, .66]].forEach(([x, z, r]) => {
    const w = new T.Group(); w.position.set(x, r, z);
    const rim = K.cyl(r, r, .12, 0x3b2818, 0, 0, 0, 14); rim.rotation.z = PI / 2; w.add(rim);
    const hub = K.box(.16, r * 1.85, .07, gold, 0, 0, 0); w.add(hub);
    const sp2 = K.box(.16, .07, r * 1.85, gold, 0, 0, 0); w.add(sp2);
    g.add(w); g.wheels.push({ w, r });
  });
  g.spin = dist => g.wheels.forEach(({ w, r }) => w.rotation.x = dist / r);
  return g;
}

function cabbage(s = 1) {
  const g = new T.Group();
  g.add(K.ball(.22, 0x56b83f, 0, .18, 0, 1));
  g.add(K.ball(.18, 0x7be05a, .08, .24, .06, 0));
  g.add(K.ball(.18, 0x4aa335, -.08, .22, -.05, 0));
  g.scale.setScalar(s); return g;
}

// ================================================================= 28 SHOTS
// 0. Hero Napoleon & officers in sunlit French meadow
S({
  value: '1807', status: 'NAPOLEON', sub: 'FRANCE',
  setup() {
    const sc = meadow(), cam = K.camera(44);
    grassTufts(sc, { clear: (x, z) => Math.abs(x) < 1.8 && z > -20 });
    [[-8, -18, 1.6, 2], [9, -22, 1.8, 4], [-12, -36, 2, 6], [11, -44, 2.2, 8]].forEach(a => sc.add(cypress(...a)));
    const nap = frenchPerson({ emperor: true }); nap.position.set(0, 0, 1.5); sc.add(nap);
    const o1 = frenchPerson({ officer: true }); o1.position.set(-1.35, 0, .5); sc.add(o1);
    const o2 = frenchPerson({ officer: true }); o2.position.set(1.35, 0, .5); sc.add(o2);
    return {
      scene: sc, camera: cam, update(t, k) {
        K.idle(nap, t); K.idle(o1, t + 1); K.idle(o2, t + 2);
        nap.parts.head.rotation.y = Math.sin(t * 1.2) * .18;
        nap.parts.armR.rotation.set(-1.1 * K.ramp(t, 1.0, .4), 0, -.15);
        K.dolly(cam, k, [-1.4, 1.55, 6.2], [-.7, 1.7, 4.9], [0, 1.45, 1.2]);
      }
    };
  }
});

// 1. Reverse angle: Napoleon pointing toward 3,000 distant rabbits & cages
S({
  value: (t) => fmt(Math.min(3000, 3000 * K.ramp(t, .4, 1.2))), status: 'NAPOLEON', sub: 'VS RABBITS',
  setup() {
    const sc = meadow({ fogFar: 150 }), cam = K.camera(46);
    grassTufts(sc, { n: 1000, seed: 7 });
    [[-10, -24, 1.7, 2], [11, -28, 1.9, 5]].forEach(a => sc.add(cypress(...a)));
    const nap = frenchPerson({ emperor: true }); nap.position.set(-1.1, 0, 2.8); nap.rotation.y = PI - .3; sc.add(nap);
    const o1 = frenchPerson({ officer: true }); o1.position.set(-2.3, 0, 3.3); o1.rotation.y = PI - .2; sc.add(o1);
    nap.parts.armR.rotation.set(-1.25, 0, -.15);
    const rbs = warren(sc, { n: 45, cx: 0, cz: -14, rx: 10, rz: 6, seed: 11, s: 1.15 });
    return {
      scene: sc, camera: cam, update(t, k) {
        rbs.forEach((rb, i) => { rabbitIdle(rb, t + i * .3); if (i % 3 === 0) rabbitHop(rb, t * 7 + rb.ph, .18); });
        K.dolly(cam, k, [-2.5, 2.2, 6.8], [-1.4, 2.5, 5.2], [0, 1.0, -9]);
      }
    };
  }
});

// 2. "And lost." Extreme deadpan close-up on one rabbit staring straight into the lens
S({
  value: '3,000', status: 'THE RABBITS', statusColor: CORAL, sub: 'SPOILER',
  setup() {
    const sc = meadow({ fogNear: 6, fogFar: 45 }), cam = K.camera(36);
    grassTufts(sc, { n: 600, z0: -25, z1: 4, seed: 9 });
    const rb = rabbit({ seed: 2, s: 1.85, col: 0xf5f1ea }); rb.position.set(0, 0, 0); sc.add(rb);
    return {
      scene: sc, camera: cam, update(t, k) {
        rabbitIdle(rb, 0);
        rb.parts.head.rotation.set(0, 0, K.ramp(t, .15, .2) * .28);
        rb.parts.nose.position.y = .01 + Math.sin(t * 28) * .006;
        K.dolly(cam, k, [0, 1.0, 3.2], [0, 1.02, 2.75], [0, .82, .1]);
      }
    };
  }
});

// 3. War map table: Russia & Prussia defeated
S({
  value: '1807', status: 'VICTORY', statusColor: GOLD, sub: 'TREATY OF TILSIT',
  setup() {
    const sc = K.indoor({ wall: 0xdccbb0, floor: 0x7d5330 }), cam = K.camera(42);
    const tbl = K.table({ w: 2.8, d: 2.0, h: .9, color: 0x6b4122 }); tbl.position.set(0, 0, 0); sc.add(tbl);
    const mapBase = K.box(2.4, .05, 1.6, 0x5c8ab5, 0, .93, 0); sc.add(mapBase);
    const fr = K.box(.52, .14, .65, 0x2b59a8, -.65, 1.0, .2); sc.add(fr);
    const pr = K.box(.48, .12, .5, 0x7f8690, .02, .99, -.15); sc.add(pr);
    const ru = K.box(.72, .12, .75, 0x8f9499, .68, .99, -.2); sc.add(ru);
    const lf = K.label('FRANCE', .32, BLUE); lf.position.set(-.65, 1.28, .2); sc.add(lf);
    const lp = K.label('PRUSSIA', .30, '#e6d8c0'); lp.position.set(.02, 1.25, -.15); sc.add(lp);
    const lr = K.label('RUSSIA', .30, '#e6d8c0'); lr.position.set(.68, 1.25, -.2); sc.add(lr);
    const x1 = K.label('X', .5, CORAL); x1.position.set(.02, 1.15, -.15); sc.add(x1);
    const x2 = K.label('X', .5, CORAL); x2.position.set(.68, 1.15, -.2); sc.add(x2);
    const nap = frenchPerson({ emperor: true }); nap.position.set(-.55, -.1, -1.35); nap.baseY = -.1; sc.add(nap);
    return {
      scene: sc, camera: cam, update(t, k) {
        K.idle(nap, t);
        x1.pop(K.pop(t, 1.2)); x2.pop(K.pop(t, .7));
        pr.scale.y = 1 - .45 * K.ramp(t, 1.2, .4);
        ru.scale.y = 1 - .45 * K.ramp(t, .7, .4);
        K.dolly(cam, k, [-.6, 3.2, 5.2], [.2, 2.9, 4.4], [0, .95, -.1]);
      }
    };
  }
});

// 4. Generals raising goblets by a celebratory marquee tent
S({
  value: 'JULY 1807', status: 'CELEBRATING', sub: 'THE HUNT',
  setup() {
    const sc = meadow(), cam = K.camera(42);
    grassTufts(sc, { n: 700, seed: 13 });
    // Striped marquee tent
    sc.add(K.cyl(.1, .1, 3.2, 0x8a643c, -2.5, 1.6, -4, 8));
    sc.add(K.mesh(new T.ConeGeometry(3.4, 1.6, 6), K.mat(0xf2ead6), -2.5, 3.8, -4));
    sc.add(K.mesh(new T.ConeGeometry(3.45, .45, 6), K.mat(0xb82929), -2.5, 3.15, -4));
    const gens = [-1.1, 0, 1.1].map((x, i) => {
      const p = frenchPerson({ officer: true, shirt: i === 1 ? 0x1b2d56 : 0x22386b });
      p.position.set(x, 0, 0); p.rotation.y = (i - 1) * -.35;
      p.cup = K.cyl(.08, .05, .18, GOLD, 0, -.64, .12, 8);
      p.parts.armR.add(p.cup);
      sc.add(p); return p;
    });
    return {
      scene: sc, camera: cam, update(t, k) {
        const cheer = Math.sin(t * 5) * .25 + .5;
        gens.forEach((p, i) => {
          K.idle(p, t + i);
          p.parts.armR.rotation.set(-1.5 - cheer * .7, 0, -.25);
        });
        K.dolly(cam, k, [2.2, 1.7, 6.2], [.9, 1.65, 5.0], [0, 1.4, 0]);
      }
    };
  }
});

// 5. Berthier stacking wooden rabbit cages
S({
  value: (t) => fmt(Math.min(1500, 1500 * K.ramp(t, .1, 1.6))), status: 'BERTHIER', sub: 'PACKING CAGES',
  setup() {
    const sc = meadow(), cam = K.camera(42);
    grassTufts(sc, { n: 700, seed: 17 });
    const bert = frenchPerson({ officer: true }); bert.position.set(-1.05, 0, 1.0); bert.rotation.y = .55; sc.add(bert);
    bert.parts.armL.rotation.set(-1.0, 0, .2);
    bert.parts.armL.add(K.box(.4, .03, .5, 0xf2ead6, 0, -.6, .15));
    const cages = [];
    for (let r = 0; r < 3; r++) for (let c = 0; c < 2; c++) {
      const cg = cage({ s: 1.0 }); cg.position.set(.35 + c * 1.25, r * .74, -r * .1);
      const rb = rabbit({ seed: r * 10 + c + 1, s: .9 }); rb.position.set(0, .06, 0); cg.add(rb);
      sc.add(cg); cages.push(cg);
    }
    return {
      scene: sc, camera: cam, update(t, k) {
        K.idle(bert, t); bert.parts.armR.rotation.x = -.8 + Math.sin(t * 6) * .25;
        cages.forEach((cg, i) => cg.scale.setScalar(K.pop(t, i * .16)));
        K.dolly(cam, k, [-.5, 1.8, 8.0], [.1, 1.95, 6.8], [.1, 1.2, 0]);
      }
    };
  }
});

// 6. Aerial pull-back: 3,000 cages stretching across the sunny French field
S({
  value: (t) => fmt(1500 + 1500 * K.ramp(t, .0, 1.4)), status: '3,000 CAGES', sub: 'SUNNY FIELD',
  setup() {
    const sc = meadow({ range: 36, fogFar: 160 }), cam = K.camera(48);
    grassTufts(sc, { n: 1200, x0: -35, x1: 35, z0: -80, z1: 12, seed: 21 });
    [[-16, -45, 2.2, 3], [18, -50, 2.4, 7]].forEach(a => sc.add(cypress(...a)));
    for (let row = 0; row < 6; row++) for (let col = -4; col <= 4; col++) {
      const cg = cage({ s: 1.0 }); cg.position.set(col * 2.1, 0, -row * 2.6); sc.add(cg);
    }
    const nap = frenchPerson({ emperor: true }); nap.position.set(0, 0, 4.5); nap.rotation.y = PI; sc.add(nap);
    return {
      scene: sc, camera: cam, update(t, k) {
        K.idle(nap, t);
        K.dolly(cam, k, [0, 3.6, 10.5], [3.5, 11.5, 18.5], [0, .8, -5]);
      }
    };
  }
});

// 7. Cages pop open — rabbits don't run away; they turn toward Napoleon
S({
  value: '3,000', status: 'LOCKED ON', statusColor: CORAL, sub: 'WAIT WHAT?',
  setup() {
    const sc = meadow(), cam = K.camera(42);
    grassTufts(sc, { n: 700, seed: 25 });
    const cages = [], rbs = [];
    [-2.4, -.8, .8, 2.4].forEach((x, i) => {
      const cg = cage({ s: 1.05 }); cg.position.set(x, 0, -2.5); sc.add(cg); cages.push(cg);
      for (let j = 0; j < 3; j++) {
        const rb = rabbit({ seed: i * 10 + j + 20, s: 1.1 });
        rb.position.set(x + (j - 1) * .32, 0, -2.5); rb.rotation.y = PI;
        sc.add(rb); rbs.push(rb);
      }
    });
    return {
      scene: sc, camera: cam, update(t, k) {
        const op = K.ramp(t, .25, .35);
        cages.forEach(cg => cg.door.rotation.x = op * 1.65);
        const hopOut = K.ramp(t, .55, .6);
        const turn = K.ramp(t, 1.35, .45);
        rbs.forEach((rb, i) => {
          rb.position.z = -2.5 + hopOut * (1.5 + (i % 3) * .45);
          rb.rotation.y = K.lerp(PI, 0, turn);
          if (hopOut > 0 && hopOut < 1) rabbitHop(rb, t * 14 + i, .16);
          else rabbitIdle(rb, t + i);
        });
        K.dolly(cam, k, [-.8, 1.3, 4.4], [.5, 1.05, 3.2], [0, .55, -1.2]);
      }
    };
  }
});

// 8. Solid wall of fur charging across the field
S({
  value: '3,000', status: 'THE RABBITS', statusColor: CORAL, sub: 'CHARGING',
  setup() {
    const sc = meadow({ range: 30, fogFar: 130 }), cam = K.camera(46);
    grassTufts(sc, { n: 1000, seed: 31 });
    const rbs = warren(sc, { n: 75, cx: 0, cz: -14, rx: 11, rz: 7, seed: 33, s: 1.25 });
    rbs.forEach(rb => rb.rotation.y = 0);
    return {
      scene: sc, camera: cam, update(t, k) {
        rbs.forEach(rb => {
          rb.position.z = rb.z0 + t * 5.8;
          rabbitHop(rb, t * 17 + rb.ph, .28);
        });
        K.dolly(cam, k, [-2.2, 1.35, 3.6], [1.8, 1.0, 2.2], [0, .5, -4]);
      }
    };
  }
});

// 9. Over-the-shoulder behind Napoleon as the fur wave closes in
S({
  value: '3,000', status: 'THE RABBITS', statusColor: CORAL, sub: 'INCOMING',
  setup() {
    const sc = meadow({ range: 28 }), cam = K.camera(44);
    grassTufts(sc, { n: 800, seed: 37 });
    const nap = frenchPerson({ emperor: true }); nap.position.set(0, 0, 3.2); nap.rotation.y = PI; sc.add(nap);
    const rbs = warren(sc, { n: 55, cx: 0, cz: -10, rx: 8, rz: 5, seed: 39, s: 1.2 });
    rbs.forEach(rb => rb.rotation.y = 0);
    return {
      scene: sc, camera: cam, update(t, k) {
        K.idle(nap, t);
        rbs.forEach(rb => {
          rb.position.z = rb.z0 + t * 5.2;
          rabbitHop(rb, t * 18 + rb.ph, .26);
        });
        K.dolly(cam, k, [-.95, 1.9, 5.4], [-.75, 1.8, 4.6], [0, 1.0, -3]);
      }
    };
  }
});

// 10. "Luckily, the Emperor laughed..."
S({
  value: '3,000', status: 'LUCKILY', sub: 'NAPOLEON LAUGHS',
  setup() {
    const sc = meadow(), cam = K.camera(38);
    grassTufts(sc, { n: 600, seed: 41 });
    const nap = frenchPerson({ emperor: true }); nap.position.set(0, 0, 0); sc.add(nap);
    const rbs = warren(sc, { n: 8, cx: 0, cz: 2.0, rx: 1.6, rz: .8, seed: 43, s: 1.15 });
    rbs.forEach(rb => rb.rotation.y = PI);
    return {
      scene: sc, camera: cam, update(t, k) {
        nap.parts.head.rotation.x = -.22 + Math.sin(t * 16) * .08;
        nap.parts.torso.rotation.x = -.1 + Math.sin(t * 16) * .04;
        nap.parts.armL.rotation.set(-.5, 0, -.3);
        rbs.forEach(rb => rabbitHop(rb, t * 12 + rb.ph, .18));
        K.dolly(cam, k, [.8, 1.75, 3.4], [.45, 1.72, 2.75], [0, 1.5, 0]);
      }
    };
  }
});

// 11. Swatting rabbits back with riding crop
S({
  value: '3,000', status: 'NAPOLEON', sub: 'RIDING CROP',
  setup() {
    const sc = meadow(), cam = K.camera(42);
    grassTufts(sc, { n: 600, seed: 47 });
    const nap = frenchPerson({ emperor: true }); nap.position.set(-.4, 0, 0); nap.rotation.y = .5; sc.add(nap);
    const rbs = warren(sc, { n: 7, cx: .95, cz: 1.4, rx: .9, rz: .7, seed: 49, s: 1.05 });
    rbs.forEach(rb => rb.rotation.y = -2.4);
    return {
      scene: sc, camera: cam, update(t, k) {
        const sw = Math.sin(t * 11);
        nap.parts.armR.rotation.set(-1.3 + sw * .7, sw * .5, -.4);
        nap.parts.torso.rotation.y = sw * .2;
        rbs.forEach((rb, i) => {
          const bounce = Math.max(0, Math.sin(t * 7 + i)) * .45;
          rb.position.x = rb.x0 + bounce; rb.position.z = rb.z0 + bounce * .6;
          rabbitHop(rb, t * 15 + rb.ph, .24);
        });
        K.dolly(cam, k, [2.7, 1.5, 5.4], [2.1, 1.45, 4.5], [.2, 1.0, .5]);
        kick(cam, t, .55, .05); kick(cam, t, 1.15, .05);
      }
    };
  }
});

// 12. "Unluckily, there were 3,000..." — tactical pincer flank from above
S({
  value: '3,000', status: 'UNLUCKILY', statusColor: CORAL, sub: 'PINCER FLANK',
  setup() {
    const sc = meadow({ range: 30 }), cam = K.camera(48);
    grassTufts(sc, { n: 900, seed: 53 });
    const nap = frenchPerson({ emperor: true }); nap.position.set(0, 0, 0); sc.add(nap);
    const leftFlank = warren(sc, { n: 32, cx: -6, cz: -2, rx: 2.4, rz: 4, seed: 55, s: 1.2 });
    const rightFlank = warren(sc, { n: 32, cx: 6, cz: -2, rx: 2.4, rz: 4, seed: 57, s: 1.2 });
    return {
      scene: sc, camera: cam, update(t, k) {
        K.idle(nap, t); nap.parts.head.rotation.y = Math.sin(t * 7) * .6;
        const u = K.smooth(t / 2.0);
        leftFlank.forEach(rb => {
          const ang = K.lerp(.4, 1.8, u);
          rb.position.x = rb.x0 + u * 4.5; rb.position.z = rb.z0 + Math.sin(u * PI) * 2.8;
          rb.rotation.y = ang; rabbitHop(rb, t * 18 + rb.ph, .24);
        });
        rightFlank.forEach(rb => {
          const ang = K.lerp(-.4, -1.8, u);
          rb.position.x = rb.x0 - u * 4.5; rb.position.z = rb.z0 + Math.sin(u * PI) * 2.8;
          rb.rotation.y = ang; rabbitHop(rb, t * 18 + rb.ph, .24);
        });
        K.dolly(cam, k, [0, 12.5, 9.5], [0, 9.5, 7.2], [0, .6, 0]);
      }
    };
  }
});

// 13. Boot-level low shot: rabbits swarming Napoleon's boots
S({
  value: '3,000', status: 'FLANKED', statusColor: CORAL, sub: 'BOOT LEVEL',
  setup() {
    const sc = meadow({ fogNear: 8, fogFar: 55 }), cam = K.camera(40);
    grassTufts(sc, { n: 700, seed: 59 });
    const nap = frenchPerson({ emperor: true }); nap.position.set(0, 0, 0); sc.add(nap);
    const rbs = warren(sc, { n: 22, cx: 0, cz: 0, rx: 1.9, rz: 1.2, seed: 61, s: 1.05 })
      .filter(rb => Math.hypot(rb.position.x, rb.position.z) > .6 && rb.position.z < 1.1);
    rbs.forEach(rb => rb.rotation.y = Math.atan2(-rb.position.x, -rb.position.z));
    return {
      scene: sc, camera: cam, update(t, k) {
        nap.parts.legL.rotation.x = Math.sin(t * 14) * .25;
        nap.parts.legR.rotation.x = -Math.sin(t * 14) * .25;
        rbs.forEach(rb => {
          const rush = K.ramp(t, 0, 1.4);
          rb.position.x = rb.x0 * (1 - .38 * rush); rb.position.z = rb.z0 * (1 - .38 * rush);
          rabbitHop(rb, t * 20 + rb.ph, .18);
        });
        K.dolly(cam, k, [-.9, .95, 3.9], [.4, .9, 3.2], [0, .55, 0]);
      }
    };
  }
});

// 14. "You see, Berthier hadn't caught wild hares..." — wild hare bolts away!
S({
  value: 'WILD HARES', status: 'RUN AWAY', sub: 'NOT THESE',
  setup() {
    const sc = meadow({ grass: 0x5c8244 }), cam = K.camera(42);
    grassTufts(sc, { n: 800, seed: 63 });
    [[-6, -12, 1.6, 2], [6, -16, 1.8, 5]].forEach(a => sc.add(cypress(...a)));
    const hare = rabbit({ seed: 8, s: 1.35, col: 0x7a5b3e }); hare.position.set(1.4, 0, 1.2); hare.rotation.y = -PI * .78; sc.add(hare);
    const L = K.label('WILD HARE', .7, '#f3ead8'); sc.add(L);
    return {
      scene: sc, camera: cam, update(t, k) {
        const bolt = K.ramp(t, .35, 2.2);
        hare.position.set(1.4 - bolt * 6.5, 0, 1.2 - bolt * 9.5);
        rabbitHop(hare, t * 22, .32);
        L.position.set(hare.position.x, 1.45, hare.position.z);
        K.dolly(cam, k, [2.0, 1.35, 5.2], [0.2, 1.55, 4.8], [hare.position.x * .7, .7, hare.position.z * .7]);
      }
    };
  }
});

// 15. Farm pen: Berthier paying farmer for plump tame rabbits
S({
  value: '3,000', status: 'TAME PETS', statusColor: GOLD, sub: 'FARM RABBITS',
  setup() {
    const sc = meadow(), cam = K.camera(42);
    grassTufts(sc, { n: 700, seed: 67 });
    sc.add(K.house(-5.5, -9, { wall: 0xead8b5, roof: 0xa64b3a, door: 0x6b4423, rot: .4 }));
    sc.add(K.fence(-3.5, -2.5, 7, 0x9c764c));
    const bert = frenchPerson({ officer: true }); bert.position.set(-.8, 0, 0); bert.rotation.y = PI / 2 - .2; sc.add(bert);
    const farm = K.person({ shirt: 0x8f6b47, pants: 0x4f463a, hair: 0x705638 });
    farm.position.set(.8, 0, 0); farm.rotation.y = -PI / 2 + .2;
    farm.parts.head.add(K.cyl(.42, .42, .04, 0xd9b864, 0, .44, 0, 14), K.cyl(.22, .25, .18, 0xd9b864, 0, .54, 0, 10));
    sc.add(farm);
    const bag = K.ball(.2, GOLD, 0, 1.05, .3, 0); sc.add(bag);
    const rbs = warren(sc, { n: 10, cx: 0, cz: -1.4, rx: 2.0, rz: .8, seed: 69, s: 1.1 });
    return {
      scene: sc, camera: cam, update(t, k) {
        K.idle(bert, t); K.idle(farm, t + 1);
        bert.parts.armR.rotation.set(-1.1, 0, -.3); farm.parts.armL.rotation.set(-1.1, 0, .3);
        bag.position.x = K.lerp(-.32, .32, K.ramp(t, .3, .9));
        rbs.forEach(rb => rabbitIdle(rb, t));
        K.dolly(cam, k, [-.3, 1.7, 6.8], [.2, 1.65, 5.8], [0, 1.15, -.3]);
      }
    };
  }
});

// 16. Rabbit POV: Coat != Hunter
S({
  value: 'RABBIT POV', status: 'NOT A HUNTER', sub: 'JUST A COAT',
  setup() {
    const sc = K.indoor({ wall: 0x22293e, floor: 0x353f5e, window: false }), cam = K.camera(42);
    const coatMan = frenchPerson({ emperor: true }); coatMan.position.set(0, 0, -.6); sc.add(coatMan);
    const rb1 = rabbit({ seed: 3, s: 1.4 }); rb1.position.set(-1.0, 0, 2.0); rb1.rotation.y = PI - .4; sc.add(rb1);
    const rb2 = rabbit({ seed: 7, s: 1.4 }); rb2.position.set(1.0, 0, 2.0); rb2.rotation.y = -PI + .4; sc.add(rb2);
    return {
      scene: sc, camera: cam, update(t, k) {
        K.idle(coatMan, t);
        rabbitIdle(rb1, t); rabbitIdle(rb2, t + 1);
        K.dolly(cam, k, [0, 1.15, 5.4], [0, 1.3, 4.5], [0, 1.35, -.2]);
      }
    };
  }
});

// 17. Waiter Napoleon serving a giant green cabbage on a silver platter!
S({
  value: 'DINNER TIME', status: 'THE WAITER', statusColor: GOLD, sub: 'CABBAGE!',
  setup() {
    const sc = K.indoor({ wall: 0x2b3654, floor: 0x455275, window: false }), cam = K.camera(42);
    const waiter = frenchPerson({ emperor: true }); waiter.position.set(0, 0, -.5); sc.add(waiter);
    waiter.parts.armL.rotation.set(-1.45, 0, .2); waiter.parts.armR.rotation.set(-1.45, 0, -.2);
    const tray = K.cyl(.52, .45, .04, 0xd8dde6, 0, 1.42, .42, 16, { metalness: .6, roughness: .25 }); sc.add(tray);
    const cab = cabbage(1.6); cab.position.set(0, 1.32, .42); sc.add(cab);
    const rbs = warren(sc, { n: 8, cx: 0, cz: 1.8, rx: 1.5, rz: .8, seed: 71, s: 1.15 });
    rbs.forEach(rb => rb.rotation.y = PI);
    return {
      scene: sc, camera: cam, update(t, k) {
        cab.rotation.y = t * 1.4;
        rbs.forEach(rb => rabbitHop(rb, t * 14 + rb.ph, .25));
        K.dolly(cam, k, [-.7, 1.75, 5.1], [.5, 1.6, 4.1], [0, 1.3, .2]);
      }
    };
  }
});

// 18. Close-up: rabbits clinging to Napoleon's jacket and chewing gold buttons
S({
  value: '3,000', status: 'SWARMED', statusColor: CORAL, sub: 'CHEWING BUTTONS',
  setup() {
    const sc = meadow(), cam = K.camera(38);
    grassTufts(sc, { n: 500, seed: 73 });
    const nap = frenchPerson({ emperor: true }); nap.position.set(0, 0, 0); sc.add(nap);
    const cling1 = rabbit({ seed: 11, s: .72 }); cling1.position.set(-.18, .92, .25); cling1.rotation.set(-.3, 0, .2); nap.add(cling1);
    const cling2 = rabbit({ seed: 12, s: .68 }); cling2.position.set(.2, 1.15, .22); cling2.rotation.set(-.4, -.3, -.2); nap.add(cling2);
    const cling3 = rabbit({ seed: 14, s: .75 }); cling3.position.set(0, 1.38, -.22); cling3.rotation.set(.2, PI, 0); nap.add(cling3);
    const groundRbs = warren(sc, { n: 12, cx: 0, cz: .5, rx: 1.4, rz: 1.0, seed: 75, s: 1.1 });
    return {
      scene: sc, camera: cam, update(t, k) {
        nap.parts.armL.rotation.set(-1.6 + Math.sin(t * 16) * .5, 0, -.5);
        nap.parts.armR.rotation.set(-1.6 - Math.sin(t * 16) * .5, 0, .5);
        nap.parts.head.rotation.set(-.1, Math.sin(t * 12) * .45, 0);
        cling1.parts.head.rotation.x = Math.sin(t * 24) * .25;
        cling2.parts.head.rotation.x = Math.cos(t * 22) * .25;
        groundRbs.forEach(rb => rabbitHop(rb, t * 18 + rb.ph, .24));
        K.dolly(cam, k, [-.7, 1.5, 4.3], [.4, 1.45, 3.5], [0, 1.25, .1]);
      }
    };
  }
});

// 19. Generals running in circles swarmed by rabbits
S({
  value: '3,000', status: 'PANIC', statusColor: CORAL, sub: 'GENERALS FLEE',
  setup() {
    const sc = meadow({ range: 26 }), cam = K.camera(44);
    grassTufts(sc, { n: 800, seed: 79 });
    const gens = [-1.8, 0, 1.8].map((x, i) => {
      const p = frenchPerson({ officer: true }); p.position.set(x, 0, -i * 1.2);
      const c = rabbit({ seed: 30 + i, s: .7 }); c.position.set(0, 1.1, .24); p.add(c);
      sc.add(p); return p;
    });
    const rbs = warren(sc, { n: 32, cx: 0, cz: 0, rx: 5, rz: 4, seed: 81, s: 1.15 });
    return {
      scene: sc, camera: cam, update(t, k) {
        gens.forEach((p, i) => {
          const ang = t * 2.2 + i * 2.1;
          p.position.x = Math.cos(ang) * 2.6; p.position.z = Math.sin(ang) * 2.0;
          p.rotation.y = -ang;
          K.walk(p, t * 13 + i, .75);
          p.parts.armL.rotation.x = -2.3 + Math.sin(t * 14 + i) * .4;
          p.parts.armR.rotation.x = -2.3 - Math.sin(t * 14 + i) * .4;
        });
        rbs.forEach(rb => rabbitHop(rb, t * 18 + rb.ph, .25));
        K.dolly(cam, k, [-2.5, 3.2, 8.8], [1.2, 2.7, 7.2], [0, 1.1, 0]);
      }
    };
  }
});

// 20. Napoleon sprinting backward toward his royal carriage
S({
  value: '3,000', status: 'RETREAT', statusColor: CORAL, sub: 'TO THE CARRIAGE',
  setup() {
    const sc = meadow({ range: 30 }), cam = K.camera(44);
    grassTufts(sc, { n: 700, seed: 83, clear: (x, z) => Math.abs(x) < 2.2 });
    sc.add(K.box(3.4, .02, 80, 0x9c8258, 0, .01, -20));
    const car = carriage(); car.position.set(0, 0, -4.5); car.rotation.y = PI / 2; car.door.rotation.y = 1.1; sc.add(car);
    const nap = frenchPerson({ emperor: true }); nap.position.set(0, 0, 3.0); sc.add(nap);
    const rbs = warren(sc, { n: 28, cx: 0, cz: 5.5, rx: 3.5, rz: 2.5, seed: 85, s: 1.15 });
    rbs.forEach(rb => rb.rotation.y = PI);
    return {
      scene: sc, camera: cam, update(t, k) {
        const z = K.lerp(3.0, -2.5, K.smooth(t / 2.0));
        nap.position.set(0, 0, z); K.walk(nap, -t * 14, .7);
        nap.parts.armL.rotation.x = -1.2; nap.parts.armR.rotation.x = -1.2;
        rbs.forEach(rb => { rb.position.z = rb.z0 - t * 3.8; rabbitHop(rb, t * 19 + rb.ph, .26); });
        K.dolly(cam, k, [4.5, 2.1, 5.2], [3.6, 1.9, .8], [0, 1.2, -1.5]);
      }
    };
  }
});

// 21. Carriage door slams shut in front of leaping rabbit!
S({
  value: '3,000', status: 'RETREAT', statusColor: CORAL, sub: 'DOOR SLAMMED',
  setup() {
    const sc = meadow(), cam = K.camera(38);
    grassTufts(sc, { n: 500, seed: 87 });
    sc.add(K.box(3.4, .02, 40, 0x9c8258, 0, .01, 0));
    const car = carriage(); car.position.set(0, 0, 0); sc.add(car);
    const nap = frenchPerson({ emperor: true }); nap.position.set(0, .65, 0); nap.rotation.y = PI / 2; K.sit(nap); sc.add(nap);
    const rb = rabbit({ seed: 19, s: 1.3 }); rb.position.set(2.5, 0, .1); rb.rotation.y = -PI / 2; sc.add(rb);
    return {
      scene: sc, camera: cam, update(t, k) {
        const slam = K.ramp(t, .45, .15);
        car.door.rotation.y = K.lerp(1.2, 0, slam);
        const lp = K.ramp(t, .62, .35);
        rb.position.set(K.lerp(2.5, 1.15, lp), Math.sin(lp * PI) * 1.1, .1);
        K.dolly(cam, k, [3.6, 1.75, 3.8], [3.0, 1.65, 2.9], [.4, 1.3, 0]);
        kick(cam, t, .6, .11);
      }
    };
  }
});

// 22. Rabbits chasing the carriage wheels down the road
S({
  value: '3,000', status: 'IN PURSUIT', statusColor: CORAL, sub: 'FULL GALLOP',
  setup() {
    const sc = meadow({ range: 35, fogFar: 130 }), cam = K.camera(44);
    sc.add(K.box(240, .02, 3.6, 0x9c8258, 40, .01, 0));
    for (let i = -2; i < 12; i++) sc.add(cypress(i * 12, -5.5 - (i % 2) * 2, 1.7, 20 + i));
    const car = carriage(); car.rotation.y = PI / 2; sc.add(car);
    const rbs = warren(sc, { n: 22, cx: -3.2, cz: 0, rx: 2.2, rz: 1.5, seed: 89, s: 1.2 });
    rbs.forEach(rb => rb.rotation.y = PI / 2);
    return {
      scene: sc, camera: cam, update(t, k) {
        const cx = t * 9.5;
        car.position.set(cx, Math.abs(Math.sin(t * 14)) * .05, 0); car.spin(cx);
        rbs.forEach((rb, i) => {
          rb.position.x = rb.x0 + cx + (i % 3) * .2;
          rabbitHop(rb, t * 22 + rb.ph, .32);
        });
        cam.position.set(cx - 1.2, 2.0, 9.6 - k * 1.4); cam.lookAt(cx - 1.2, 1.15, 0);
      }
    };
  }
});

// 23. Rabbits leaping straight through the carriage windows!
S({
  value: '3,000', status: 'BREACHED', statusColor: CORAL, sub: 'IN THE COACH',
  setup() {
    const sc = meadow({ range: 24 }), cam = K.camera(38);
    sc.add(K.box(120, .02, 3.6, 0x9c8258, 20, .01, 0));
    const car = carriage(); car.rotation.y = PI / 2; sc.add(car);
    const nap = frenchPerson({ emperor: true }); nap.position.set(-.2, .72, 0); K.sit(nap); car.add(nap);
    const leapers = [0, 1, 2, 3, 4].map(i => {
      const rb = rabbit({ seed: 91 + i, s: 1.15 }); sc.add(rb); return rb;
    });
    return {
      scene: sc, camera: cam, update(t, k) {
        const cx = t * 6.0;
        car.position.set(cx, Math.abs(Math.sin(t * 12)) * .04, 0); car.spin(cx);
        nap.parts.head.rotation.y = Math.sin(t * 18) * .5;
        leapers.forEach((rb, i) => {
          const u = K.clamp((t - i * .26) / .75);
          rb.position.set(cx - .4 + (i - 2) * .25, K.lerp(.2, 1.72, u) + Math.sin(u * PI) * .9, K.lerp(2.8, .1, u));
          rb.rotation.y = PI; rb.parts.root.rotation.x = -.4 + u * .8;
        });
        cam.position.set(cx + 1.6, 2.0, 5.4 - k * .8); cam.lookAt(cx, 1.4, 0);
      }
    };
  }
});

// 24. Dusk: French army retreats down the dusty road
S({
  value: '3,000', status: 'THE RABBITS', statusColor: CORAL, sub: 'ARMY FLEES',
  setup() {
    const sc = meadow({ mood: 'dusk', fogNear: 28, fogFar: 150, grass: 0x5d7a3c }), cam = K.camera(44);
    sc.add(K.box(3.8, .02, 180, 0x8f744c, 0, .01, -50));
    const car = carriage(); car.rotation.y = PI; sc.add(car);
    return {
      scene: sc, camera: cam, update(t, k) {
        const z = -4 - t * 6.5;
        car.position.set(0, Math.abs(Math.sin(t * 10)) * .04, z); car.spin(-z);
        K.dolly(cam, k, [1.6, 1.5, 4.4], [1.2, 1.6, 3.6], [0, 1.2, -14]);
      }
    };
  }
});

// 25. Dusk reverse angle: row of rabbits sitting calmly by the fence
S({
  value: '3,000', status: 'THE RABBITS', statusColor: CORAL, sub: 'STILL HERE',
  setup() {
    const sc = meadow({ mood: 'dusk', fogNear: 20, fogFar: 130, grass: 0x5d7a3c }), cam = K.camera(40);
    grassTufts(sc, { n: 700, z0: -40, z1: -1, seed: 93 });
    sc.add(K.fence(-10, -.6, 20, 0x6a5a44));
    const rbs = [...Array(7)].map((_, i) => {
      const rb = rabbit({ seed: 200 + i, s: 1.25 });
      rb.position.set(-3.3 + i * 1.1, 0, -1.3 - (i % 2) * .25);
      sc.add(rb); return rb;
    });
    return {
      scene: sc, camera: cam, update(t, k) {
        rbs.forEach((rb, i) => { rabbitIdle(rb, t + i); rb.rotation.y = (i - 3) * -.06; });
        K.dolly(cam, k, [0, 1.15, 7.6], [0, 1.25, 6.4], [0, .85, -1.3]);
      }
    };
  }
});

// 26. Navy trophy pedestal: Napoleon conquered Europe...
S({
  value: '1807', status: 'CONQUERED EUROPE', statusColor: GOLD, sub: 'UNSTOPPABLE?',
  setup() {
    const sc = new T.Scene(); sc.background = K.skyGradient('#14203f', '#3b4f7e'); sc.fog = new T.Fog(0x2a3860, 12, 36);
    K.lights(sc, { sun: 0xfff0d8, sunI: 2.8, sky: 0xbfd2ff, ground: 0x3a3020, hemiI: 1.0, pos: [3, 8, 7], range: 8 });
    sc.add(K.cyl(2.6, 2.9, .3, 0x262c42, 0, .15, 0, 28));
    sc.add(K.cyl(1.1, 1.3, 1.1, 0xd8cdb8, 0, .85, 0, 16));
    const nap = frenchPerson({ emperor: true }); nap.baseY = 1.4; nap.position.set(0, 1.4, 0); sc.add(nap);
    const globe = K.planet({ radius: .52, seed: 12, ice: false, cracks: 0, atmosphere: 0x7ab8ff });
    globe.position.set(-.85, 2.35, .55); sc.add(globe);
    return {
      scene: sc, camera: cam0(), update(t, k) {
        K.idle(nap, t); globe.rotation.y = t * 1.2;
        K.dolly(this.camera, k, [-1.2, 2.7, 7.6], [.4, 2.55, 6.2], [0, 2.25, 0]);
      }
    };
    function cam0() { return K.camera(42); }
  }
});

// 27. ...defeated by dinner time: giant rabbit hops onto the pedestal with cabbage!
S({
  value: '3,000', status: 'UNDEFEATED', statusColor: GOLD, sub: 'DINNER TIME',
  setup() {
    const sc = new T.Scene(); sc.background = K.skyGradient('#14203f', '#3b4f7e'); sc.fog = new T.Fog(0x2a3860, 12, 36);
    K.lights(sc, { sun: 0xfff0d8, sunI: 2.8, sky: 0xbfd2ff, ground: 0x3a3020, hemiI: 1.0, pos: [3, 8, 7], range: 8 });
    sc.add(K.cyl(2.6, 2.9, .3, 0x262c42, 0, .15, 0, 28));
    sc.add(K.cyl(1.1, 1.3, 1.1, 0xd8cdb8, 0, .85, 0, 16));
    const bicorne = K.cyl(.5, .58, .25, 0x181a20, 0, 1.52, 0, 12); bicorne.scale.set(1.25, 1, .52); sc.add(bicorne);
    const rb = rabbit({ seed: 5, s: 1.75, col: 0xf5f1ea }); rb.position.set(0, 1.62, 0); sc.add(rb);
    const cab = cabbage(1.0); cab.position.set(.48, 1.5, .55); sc.add(cab);
    const glowR = new T.Mesh(new T.CircleGeometry(2.8, 48), new T.MeshBasicMaterial({ color: 0xffd36a, transparent: true, opacity: .0, depthWrite: false }));
    glowR.position.set(0, 2.3, -1.2); sc.add(glowR);
    return {
      scene: sc, camera: cam0(), update(t, k) {
        rabbitIdle(rb, t);
        const hopIn = K.ramp(t, .0, .35);
        rb.position.y = 1.62 + Math.sin(hopIn * PI) * .55;
        rb.parts.head.rotation.set(0, Math.sin(t * 2.5) * .18, K.ramp(t, .6, .25) * .22);
        glowR.material.opacity = .18 * K.ramp(t, .5, .45);
        K.dolly(this.camera, k, [.8, 2.7, 6.6], [-.3, 2.55, 5.4], [0, 2.15, 0]);
        kick(this.camera, t, .35, .06);
      }
    };
    function cam0() { return K.camera(42); }
  }
});
