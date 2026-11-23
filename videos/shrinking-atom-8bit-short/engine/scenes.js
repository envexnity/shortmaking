/* Shrinking Smaller Than an Atom 8-Bit Countryball Short — 180x320 Scenes + 1080x1920 Black-Pill Subtitles */
window.SHORT_APP = (() => {
  const {
    PW, PH, pctx, px, rect, line, ditherBand, ditherGradV, disk, ellipse, glowOrb,
    pixelText, drawHudPill, buildSubtitleChunks, presentFrame, kickOffset, blinkExpr, isSpeaking, activeBeatIndex,
  } = window.PX;
  const { drawBall, register, OUTLINE } = window.CHARS;

  register({
    skins: {
      mite:  { hi: '#bbf7d0', lit: '#4ade80', shade: '#15803d' },
      quark: { hi: '#bae6fd', lit: '#38bdf8', shade: '#0284c7' },
    },
    outfits: {
      mite_bib: (dx, dy, R, x, y, shade) => shade ? '#7f1d1d' : '#ef4444',
      quark_robe: (dx, dy, R, x, y, shade) => Math.abs(dx) <= 1 ? '#fde047' : (shade ? '#0369a1' : '#0ea5e9'),
    },
    hats: {
      mite_antennae: (cx, cy, R) => {
        const top = Math.round(cy - R - 4);
        line(cx - 5, top + 4, cx - 9, top - 3, '#22c55e');
        line(cx + 5, top + 4, cx + 9, top - 3, '#22c55e');
        disk(cx - 9, top - 3, 2, '#fde047');
        disk(cx + 9, top - 3, 2, '#fde047');
      },
      atom_halo: (cx, cy, R, t) => {
        const hy = Math.round(cy - R - 7);
        ellipse(cx, hy, 9, 3, '#22d3ee');
        px(cx + Math.cos(t * 14) * 9, hy + Math.sin(t * 14) * 3, '#fde047');
      },
    },
    props: {
      shrink_ray: (x, y) => {
        rect(x - 2, y, 12, 6, OUTLINE);
        rect(x - 1, y + 1, 10, 4, '#38bdf8');
        rect(x + 9, y + 2, 4, 2, '#f472b6');
      },
      proton_orb: (x, y) => {
        glowOrb(x + 4, y + 3, 5, '#fef08a', '#ef4444', '#f97316');
        pixelText('P+', x + 4, y - 8, '#fca5a5', '#090d1f', 'center');
      },
      micro_cash: (x, y) => {
        // Literally 3x2 pixels of cash!
        rect(x + 3, y + 4, 4, 2, '#4ade80');
        pixelText('TINY $', x + 5, y - 6, '#4ade80', '#062812', 'center');
      },
    },
  });

  let BEATS = [], SUB_CHUNKS = [];
  function init(bd) { BEATS = bd.beats || []; SUB_CHUNKS = buildSubtitleChunks(BEATS); window.CORE_READY = true; }

  function bgStreet(t, giantBills = false) {
    ditherGradV(0, 0, PW, 195, ['#1d4ed8', '#38bdf8', '#7dd3fc']);
    glowOrb(148, 52, 9, '#fef9c3', '#fde047', '#38bdf8');
    rect(8, 142, 36, 30, '#cbd5e1'); rect(6, 134, 40, 8, '#ef4444');
    rect(136, 138, 36, 34, '#fde68a'); rect(134, 130, 40, 8, '#2563eb');
    ditherBand(0, 170, PW, 16, '#16a34a', '#15803d', 0.4);
    rect(0, 186, PW, 14, '#94a3b8');
    ditherGradV(0, 200, PW, 120, ['#334155', '#1e293b', '#0f172a']);
    for (let x = 8; x < PW; x += 28) rect(x, 224, 14, 3, '#facc15');
    if (giantBills) {
      // Giant skyscraper-sized $100 dollar bill prop behind tiny MC!
      rect(64, 114, 52, 26, OUTLINE);
      rect(66, 116, 48, 22, '#22c55e');
      rect(68, 118, 44, 18, '#15803d');
      pixelText('$100', 90, 125, '#bbf7d0', '#062812', 'center');
    }
  }

  function bgCarpetMite(t) {
    ditherGradV(0, 0, PW, PH, ['#1e1b4b', '#312e81', '#1e1b4b']);
    // Giant woven carpet fibers!
    for (let x = 6; x < PW; x += 14) {
      rect(x, 190, 8, 130, '#4c1d95');
      rect(x + 2, 182, 4, 10, '#6d28d9');
    }
    rect(0, 206, PW, 114, '#3b0764');
  }

  function bgAtomVoid(t, fastElectron = false) {
    ditherGradV(0, 0, PW, PH, ['#030712', '#090d1f', '#020617']);
    // Giant stadium-wide empty atom orbit rings + tiny central nucleus marble!
    for (const r of [42, 68]) {
      for (let a = 0; a < 24; a++) {
        const ang = (a / 24) * Math.PI * 2 + t * 0.5;
        px(90 + Math.cos(ang) * r, 140 + Math.sin(ang) * (r * 0.45), '#1e3a8a');
      }
    }
    // Glowing tiny nucleus cluster in center
    glowOrb(90, 136, 4, '#ffffff', '#ef4444', '#f97316');
    glowOrb(95, 139, 3, '#fef08a', '#38bdf8', '#1d4ed8');
    // Fast orbiting glowing blue electron clipping past MC!
    const spd = fastElectron ? 14 : 6;
    const ex = 90 + Math.cos(t * spd) * 64;
    const ey = 148 + Math.sin(t * spd) * 28;
    glowOrb(ex, ey, 4, '#ffffff', '#22d3ee', '#0284c7');
    // Translucent quantum energy floor
    rect(0, 204, PW, 2, '#22d3ee');
    ditherBand(0, 206, PW, 114, '#090d1f', '#0f172a', 0.4);
  }

  function renderFrame(t) {
    const c = document.getElementById('c');
    const ctx = c.getContext('2d');
    const bi = activeBeatIndex(BEATS, t);
    const beat = BEATS[bi] || { start: 0, end: 3, speaker: 'host' };
    const u = Math.min(1, Math.max(0, (t - beat.start) / Math.max(0.1, beat.end - beat.start)));

    let camZoom = 1.0 + u * 0.05, camX = 0, camY = 0, camRot = 0;
    if (bi === 1) { camZoom = 1.18 + u * 0.04; camX = -14; camY = 6; }
    if (bi === 3) { camZoom = 1.14 + u * 0.06; camX = -10; camY = 6; }
    if (bi === 5 || bi === 6) { camZoom = 1.10 + u * 0.06; }
    if (bi === 11) { camZoom = 1.08 + u * 0.10; camRot = Math.sin(t * 14) * 0.03; }
    if (bi === 12) { camZoom = 1.16 + u * 0.08; camRot = -0.04; camY = 6; }
    if (bi === 15 && u > 0.5) { camZoom = 1.12 + (u - 0.5) * 0.06; camX = -8; camY = 5; }

    const k1 = kickOffset(t, BEATS[4]?.start || 10, 5);
    const k2 = kickOffset(t, BEATS[12]?.start || 36, 7);
    const k3 = kickOffset(t, BEATS[13]?.start || 38, 6);
    camX += k1.x + k2.x + k3.x; camY += k1.y + k2.y + k3.y; camRot += k1.rot + k2.rot + k3.rot;

    pctx.clearRect(0, 0, PW, PH);

    if (bi === 0 || bi === 1) {
      bgStreet(t, false);
      drawHudPill('OFFER:', '$1,000', 90, 26, '#4ade80');
      drawBall({ role: 'host', cx: 42, cy: 180, R: 19, expr: blinkExpr('normal', t, 1), lookX: 1, isTalking: isSpeaking(BEATS, 'host', t), t, outfit: 'host_hoodie', hat: 'host_cap', prop: 'shrink_ray', propSide: 1 });
      drawBall({ role: 'mrbeast', cx: 138, cy: 180, R: 19, expr: blinkExpr('squint', t, 2), lookX: -1, isTalking: isSpeaking(BEATS, 'mrbeast', t), t, outfit: 'mrbeast_hoodie', hat: 'mrbeast_hair' });
    } else if (bi === 2 || bi === 3) {
      bgStreet(t, false);
      drawHudPill('OFFER:', '$2,000', 90, 26, '#facc15');
      drawBall({ role: 'host', cx: 42, cy: 180, R: 19, expr: blinkExpr('normal', t, 1), lookX: 1, isTalking: isSpeaking(BEATS, 'host', t), t, outfit: 'host_hoodie', hat: 'host_cap', prop: 'shrink_ray', propSide: 1 });
      drawBall({ role: 'mc', cx: 138, cy: 180, R: 19, expr: bi === 3 ? 'dollar' : blinkExpr('wide', t, 3), lookX: -1, isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'mc_hoodie', hat: 'mc_hair' });
    } else if (bi === 4 || bi === 5 || bi === 6) {
      bgCarpetMite(t);
      drawHudPill('SCALE:', '0.1 MM (BUG)', 90, 26, '#4ade80');
      drawBall({ role: 'mc', cx: 48, cy: 184, R: 14, expr: 'wide', lookX: 1, isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'mc_hoodie', hat: 'mc_hair', sweat: true });
      if (bi >= 5) {
        drawBall({ role: 'mite', cx: 128, cy: 176, R: 24, expr: 'angry', lookX: -1, isTalking: isSpeaking(BEATS, 'mite', t), t, outfit: 'mite_bib', hat: 'mite_antennae' });
      }
    } else if (bi === 7 || bi === 8) {
      bgAtomVoid(t, bi === 8);
      drawHudPill('SCALE:', '1 ANGSTROM', 90, 26, '#22d3ee');
      drawBall({ role: 'mc', cx: 90, cy: 184, R: 18, expr: 'wide', isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'mc_hoodie', hat: 'mc_hair', sweat: true });
    } else if (bi === 9 || bi === 10 || bi === 11) {
      bgAtomVoid(t, true);
      drawHudPill('EMPTY SPACE:', '99.9%', 90, 26, '#fde047');
      drawBall({ role: 'mc', cx: 48, cy: 184, R: 18, expr: bi === 10 ? 'dollar' : blinkExpr('wide', t, 3), lookX: 1, isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'mc_hoodie', hat: 'mc_hair' });
      drawBall({ role: 'quark', cx: 130, cy: 184, R: 19, expr: bi === 11 ? 'wide' : blinkExpr('normal', t, 4), lookX: -1, isTalking: isSpeaking(BEATS, 'quark', t), t, outfit: 'quark_robe', hat: 'atom_halo', glasses: true, sweat: bi === 11 });
    } else if (bi === 12) {
      bgAtomVoid(t, true);
      drawHudPill('GRABBED:', 'PROTON!', 90, 26, '#ef4444');
      drawBall({ role: 'mc', cx: 90, cy: 180, R: 20, expr: 'dollar', isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'mc_hoodie', hat: 'mc_hair', prop: 'proton_orb', propSide: 1 });
    } else {
      bgStreet(t, bi === 13);
      const isMicro = bi === 15 && u > 0.56;
      drawHudPill('PAYOUT:', isMicro ? 'QUARK-SIZED' : 'NORMAL', 90, 26, isMicro ? '#22d3ee' : '#facc15');
      drawBall({ role: 'mc', cx: 42, cy: 180, R: 19, expr: isMicro ? 'wide' : blinkExpr('normal', t, 3), lookX: 1, isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'mc_hoodie', hat: 'mc_hair', prop: 'proton_orb', propSide: 1, sweat: isMicro });
      drawBall({ role: 'host', cx: 138, cy: 180, R: 19, expr: blinkExpr('squint', t, 1), lookX: -1, isTalking: isSpeaking(BEATS, 'host', t), t, outfit: 'host_hoodie', hat: 'host_cap', prop: isMicro ? 'micro_cash' : 'cash_2k', propSide: -1 });
    }

    presentFrame(ctx, c.width, c.height, camX, camY, camRot, camZoom, SUB_CHUNKS, t);
  }

  window.renderFrame = renderFrame;
  window.initCoreShort = init;
})();
