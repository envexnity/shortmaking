/* Speed of Light 8-Bit Countryball Short — 180x320 Scenes + 1080x1920 Black-Pill Subtitles */
window.SHORT_APP = (() => {
  const {
    PW, PH, pctx, px, rect, line, ditherBand, ditherGradV, disk, ellipse, glowOrb,
    pixelText, drawHudPill, buildSubtitleChunks, presentFrame, kickOffset, blinkExpr, isSpeaking, activeBeatIndex, seeded,
  } = window.PX;
  const { drawBall, register, OUTLINE } = window.CHARS;

  register({
    skins: {
      photon:   { hi: '#ffffff', lit: '#fde047', shade: '#eab308' },
      einstein: { hi: '#fef3c7', lit: '#f5cba7', shade: '#c28d66' },
    },
    outfits: {
      runner_suit: (dx, dy, R, x, y, shade) => Math.abs(dx) <= 1 ? '#38bdf8' : (shade ? '#15803d' : '#22c55e'),
      photon_suit: (dx, dy, R, x, y, shade) => shade ? '#ca8a04' : '#facc15',
      lab_coat:    (dx, dy, R, x, y, shade) => Math.abs(dx) <= 1 ? '#38bdf8' : (shade ? '#cbd5e1' : '#f8fafc'),
    },
    hats: {
      sweatband: (cx, cy, R) => {
        const top = Math.round(cy - R * 0.48);
        rect(cx - Math.round(R * 0.92), top, Math.round(R * 1.84), 3, '#ef4444');
        rect(cx + Math.round(R * 0.72), top + 2, 4, 2, '#dc2626');
      },
      einstein_hair: (cx, cy, R) => {
        const top = Math.round(cy - R - 2);
        disk(cx - 10, top + 6, 5, '#e2e8f0');
        disk(cx + 10, top + 6, 5, '#e2e8f0');
        disk(cx - 5, top + 1, 5, '#f8fafc');
        disk(cx + 5, top + 1, 5, '#f8fafc');
        rect(cx - 8, top + 2, 17, 3, '#ffffff');
      },
    },
    props: {
      sneakers: (x, y, t) => {
        rect(x - 1, y + 1, 11, 6, OUTLINE);
        rect(x, y + 2, 9, 4, '#ef4444');
        rect(x, y + 5, 9, 2, Math.floor(t * 14) % 2 ? '#38bdf8' : '#fde047');
        rect(x + 2, y + 2, 3, 2, '#ffffff');
      },
      stopwatch: (x, y) => {
        disk(x + 4, y + 4, 5, OUTLINE);
        disk(x + 4, y + 4, 4, '#f8fafc');
        rect(x + 3, y - 2, 3, 2, '#facc15');
        line(x + 4, y + 4, x + 4, y + 1, '#ef4444');
        line(x + 4, y + 4, x + 6, y + 4, '#0f172a');
      },
      taco_half: (x, y) => {
        rect(x - 1, y + 2, 11, 6, OUTLINE);
        rect(x, y + 3, 9, 4, '#facc15');
        rect(x + 1, y + 2, 7, 2, '#22c55e');
        rect(x + 2, y + 3, 5, 2, '#991b1b');
        pixelText('1/2', x + 4, y - 6, '#facc15', '#090d1f', 'center');
      },
    },
  });

  const STARS = (() => {
    const r = seeded(888);
    return Array.from({ length: 44 }, () => ({ x: r() * PW, y: r() * PH, sp: 80 + r() * 140, c: r() > 0.5 ? '#38bdf8' : '#ffffff' }));
  })();

  let BEATS = [], SUB_CHUNKS = [];
  function init(bd) { BEATS = bd.beats || []; SUB_CHUNKS = buildSubtitleChunks(BEATS); window.CORE_READY = true; }

  function bgStreet(t, future2076 = false) {
    if (future2076) {
      ditherGradV(0, 0, PW, 195, ['#090218', '#2e1065', '#4c1d95']);
      for (const s of STARS) px(s.x, s.y % 130, '#e879f9');
      // Neon skyline towers
      rect(10, 108, 28, 64, '#1e1b4b'); rect(16, 114, 16, 4, '#22d3ee'); rect(16, 124, 16, 4, '#f472b6');
      rect(138, 100, 32, 72, '#1e1b4b'); rect(144, 108, 20, 4, '#fde047'); rect(144, 120, 20, 4, '#22d3ee');
      // Hovering flying cars!
      const car1X = Math.round((t * 75) % (PW + 30)) - 15;
      const car2X = PW - Math.round((t * 58 + 60) % (PW + 30));
      rect(car1X, 82, 16, 6, '#38bdf8'); rect(car1X + 3, 79, 8, 3, '#bae6fd'); rect(car1X - 4, 84, 4, 2, '#f472b6');
      rect(car2X, 118, 16, 6, '#f472b6'); rect(car2X + 4, 115, 8, 3, '#fbcfe8'); rect(car2X + 16, 120, 4, 2, '#22d3ee');
      ditherBand(0, 170, PW, 16, '#0f172a', '#1e1b4b', 0.4);
      rect(0, 186, PW, 14, '#22d3ee');
      ditherGradV(0, 200, PW, 120, ['#1e1b4b', '#090d1f', '#020617']);
      for (let x = 8; x < PW; x += 28) rect(x, 224, 14, 3, '#e879f9');
    } else {
      ditherGradV(0, 0, PW, 195, ['#030712', '#0f172a', '#1e1b4b']);
      for (const s of STARS) px(s.x, s.y % 145, '#ffffff');
      disk(146, 54, 8, '#e2e8f0');
      rect(8, 142, 36, 30, '#1e293b'); rect(6, 134, 40, 8, '#ef4444');
      rect(136, 138, 36, 34, '#334155'); rect(134, 130, 40, 8, '#2563eb');
      ditherBand(0, 170, PW, 16, '#15803d', '#14532d', 0.4);
      rect(0, 186, PW, 14, '#64748b');
      ditherGradV(0, 200, PW, 120, ['#334155', '#1e293b', '#0f172a']);
      for (let x = 8; x < PW; x += 28) rect(x, 224, 14, 3, '#facc15');
    }
  }

  function bgWarpSpeed(t, pancakeEarth = false) {
    ditherGradV(0, 0, PW, 198, ['#040214', '#1e1b4b', '#312e81']);
    // Relativistic blueshifted horizontal speed streaks!
    for (const s of STARS) {
      const sx = ((s.x - t * s.sp) % PW + PW) % PW;
      const sy = Math.round(s.y % 190);
      line(sx, sy, Math.min(PW - 1, sx + 10), sy, s.c);
    }
    if (pancakeEarth) {
      // Length-contracted pancake Earth in the sky!
      ellipse(90, 96, 34, 8, '#2563eb');
      ellipse(86, 95, 14, 4, '#22c55e');
      ellipse(98, 97, 10, 3, '#22c55e');
      pixelText('SQUISHED!', 90, 76, '#38bdf8', '#090d1f', 'center');
    } else {
      glowOrb(148, 92, 10, '#ffffff', '#fde047', '#38bdf8');
    }
    ditherGradV(0, 196, PW, 124, ['#312e81', '#1e1b4b', '#090d1f']);
    // Moving track grid lines
    const off = Math.round((t * 90) % 24);
    for (let x = 0; x < PW + 24; x += 24) {
      const lx = x - off;
      rect(lx, 204, 12, 3, '#38bdf8');
    }
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
    if (bi === 4 && u > 0.5) { camZoom = 1.12 + (u - 0.5) * 0.08; camRot = -0.03; camY = 5; }
    if (bi === 7) { camZoom = 1.14 + u * 0.06; camY = 5; }
    if (bi === 11) { camZoom = 1.08 + u * 0.10; camRot = Math.sin(t * 14) * 0.03; }
    if (bi === 12) { camZoom = 1.16 + u * 0.08; camRot = -0.04; camY = 6; }
    if (bi === 15 && u > 0.5) { camZoom = 1.12 + (u - 0.5) * 0.06; camX = -8; camY = 5; }

    const k1 = kickOffset(t, BEATS[7]?.start || 18, 5);
    const k2 = kickOffset(t, BEATS[12]?.start || 31, 7);
    const k3 = kickOffset(t, BEATS[13]?.start || 33, 5);
    camX += k1.x + k2.x + k3.x; camY += k1.y + k2.y + k3.y; camRot += k1.rot + k2.rot + k3.rot;

    pctx.clearRect(0, 0, PW, PH);

    if (bi === 0 || bi === 1) {
      bgStreet(t, false);
      drawHudPill('OFFER:', '$1,000', 90, 26, '#4ade80');
      drawBall({ role: 'host', cx: 42, cy: 180, R: 19, expr: blinkExpr('normal', t, 1), lookX: 1, isTalking: isSpeaking(BEATS, 'host', t), t, outfit: 'host_hoodie', hat: 'host_cap', prop: 'cash_1k', propSide: 1 });
      drawBall({ role: 'mrbeast', cx: 138, cy: 180, R: 19, expr: blinkExpr('squint', t, 2), lookX: -1, isTalking: isSpeaking(BEATS, 'mrbeast', t), t, outfit: 'mrbeast_hoodie', hat: 'mrbeast_hair' });
    } else if (bi === 2 || bi === 3) {
      bgStreet(t, false);
      drawHudPill('OFFER:', '$2,000', 90, 26, '#facc15');
      drawBall({ role: 'host', cx: 42, cy: 180, R: 19, expr: blinkExpr('normal', t, 1), lookX: 1, isTalking: isSpeaking(BEATS, 'host', t), t, outfit: 'host_hoodie', hat: 'host_cap', prop: 'cash_2k', propSide: 1 });
      drawBall({ role: 'mc', cx: 138, cy: 180, R: 19, expr: bi === 3 ? 'cool_shades' : blinkExpr('wide', t, 3), lookX: -1, isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'runner_suit', hat: 'sweatband', prop: bi === 3 ? 'sneakers' : null, propSide: -1 });
    } else if (bi === 4) {
      bgWarpSpeed(t, false);
      drawHudPill('SPEED:', '300,000 KM/S', 90, 26, '#38bdf8');
      drawBall({ role: 'mc', cx: 90, cy: 182, R: 20, expr: 'wide', isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'runner_suit', hat: 'sweatband', prop: 'sneakers', propSide: 1, sweat: true });
    } else if (bi === 5 || bi === 6) {
      bgWarpSpeed(t, false);
      drawHudPill('PACE:', '100% LIGHT', 90, 26, '#fde047');
      drawBall({ role: 'mc', cx: 50, cy: 182, R: 19, expr: 'cool_shades', lookX: 1, isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'runner_suit', hat: 'sweatband', sweat: true });
      drawBall({ role: 'photon', cx: 132, cy: 182, R: 19, expr: 'angry', lookX: -1, isTalking: isSpeaking(BEATS, 'photon', t), t, outfit: 'photon_suit', sweat: true });
    } else if (bi === 7 || bi === 8) {
      bgWarpSpeed(t, true);
      drawHudPill(bi === 8 ? 'CLOCK:' : 'EARTH:', bi === 8 ? 'FROZEN!' : 'PANCAKE!', 90, 26, '#38bdf8');
      drawBall({ role: 'mc', cx: 90, cy: 182, R: 21, expr: 'wide', isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'runner_suit', hat: 'sweatband', prop: 'stopwatch', propSide: 1, sweat: true });
    } else if (bi === 9 || bi === 10 || bi === 11) {
      bgWarpSpeed(t, true);
      drawHudPill('TIME:', '1S = 50 YRS', 90, 26, '#a855f7');
      drawBall({ role: 'mc', cx: 48, cy: 182, R: 19, expr: bi === 10 ? 'dollar' : 'cool_shades', lookX: 1, isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'runner_suit', hat: 'sweatband', prop: 'sneakers', propSide: 1 });
      drawBall({ role: 'einstein', cx: 132, cy: 182, R: 19, expr: bi === 11 ? 'wide' : blinkExpr('normal', t, 4), lookX: -1, isTalking: isSpeaking(BEATS, 'einstein', t), t, outfit: 'lab_coat', hat: 'einstein_hair', glasses: true, beard: true, sweat: bi === 11 });
    } else if (bi === 12) {
      bgWarpSpeed(t, false);
      drawHudPill('FINISH:', '99.9% C!', 90, 26, '#4ade80');
      drawBall({ role: 'mc', cx: 90, cy: 176, R: 22, expr: 'dollar', isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'runner_suit', hat: 'sweatband', prop: 'sneakers', propSide: 1 });
    } else {
      bgStreet(t, true);
      const isTaco = bi === 15 && u > 0.48;
      drawHudPill(isTaco ? 'PRIZE:' : 'YEAR:', isTaco ? '1/2 TACO' : '2076 AD', 90, 26, isTaco ? '#ef4444' : '#22d3ee');
      drawBall({ role: 'mc', cx: 44, cy: 182, R: 19, expr: isTaco ? 'wide' : 'cool_shades', lookX: 1, isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'runner_suit', hat: 'sweatband', prop: 'stopwatch', propSide: 1, sweat: isTaco });
      // Host is 50 years older with a grey beard!
      drawBall({ role: 'host', cx: 136, cy: 182, R: 19, expr: blinkExpr('squint', t, 1), lookX: -1, isTalking: isSpeaking(BEATS, 'host', t), t, outfit: 'host_hoodie', hat: 'host_cap', beard: true, glasses: true, prop: isTaco ? 'taco_half' : 'cash_2k', propSide: -1 });
    }

    presentFrame(ctx, c.width, c.height, camX, camY, camRot, camZoom, SUB_CHUNKS, t);
  }

  window.renderFrame = renderFrame;
  window.initCoreShort = init;
})();
