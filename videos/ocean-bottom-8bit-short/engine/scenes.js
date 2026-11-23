/* Mariana Trench 8-Bit Countryball Short — 180x320 Scenes + 1080x1920 Black-Pill Subtitles */
window.SHORT_APP = (() => {
  const {
    PW, PH, pctx, px, rect, line, ditherBand, ditherGradV, disk, ellipse, glowOrb,
    pixelText, drawHudPill, buildSubtitleChunks, presentFrame, kickOffset, blinkExpr, isSpeaking, activeBeatIndex, seeded,
  } = window.PX;
  const { drawBall, register, OUTLINE } = window.CHARS;

  register({
    skins: {
      squid: { hi: '#a5f3fc', lit: '#22d3ee', shade: '#0891b2' },
      blob:  { hi: '#fbcfe8', lit: '#f472b6', shade: '#be185d' },
    },
    outfits: {
      swim_floaties: (dx, dy, R, x, y, shade) => {
        if (dy > R * 0.25 && dy < R * 0.55) return '#f97316'; // bright orange swim floatie ring!
        return shade ? '#15803d' : '#22c55e';
      },
      squid_cape: (dx, dy, R, x, y, shade) => shade ? '#1e1b4b' : '#312e81',
    },
    hats: {
      snorkel_goggles: (cx, cy, R) => {
        const top = Math.round(cy - R - 2);
        rect(cx - 10, top + 3, 20, 4, '#0f172a');
        rect(cx - 9, top + 4, 8, 2, '#38bdf8');
        rect(cx + 1, top + 4, 8, 2, '#38bdf8');
        rect(cx + R - 2, top - 6, 3, 12, '#facc15');
      },
      sleep_mask: (cx, cy, R) => {
        const top = Math.round(cy - R - 2);
        rect(cx - 10, top + 3, 20, 4, '#7e22ce');
      },
    },
    props: {
      drain_plug: (x, y) => {
        rect(x, y, 10, 6, OUTLINE);
        rect(x + 1, y + 1, 8, 4, '#facc15');
        rect(x + 3, y - 4, 4, 4, '#eab308');
        pixelText('PULL', x + 5, y - 10, '#fde047', '#090d1f', 'center');
      },
      coupon: (x, y) => {
        rect(x - 1, y - 1, 14, 9, OUTLINE);
        rect(x, y, 12, 7, '#fca5a5');
        rect(x + 2, y + 2, 8, 2, '#ef4444');
        pixelText('EXPIRED', x + 6, y - 7, '#f87171', '#090d1f', 'center');
      },
    },
  });

  const BUBBLES = (() => {
    const r = seeded(808);
    return Array.from({ length: 38 }, () => ({ x: r() * PW, y: r() * PH, sp: 16 + r() * 24, s: r() < 0.7 ? 2 : 3 }));
  })();

  let BEATS = [], SUB_CHUNKS = [];
  function init(bd) { BEATS = bd.beats || []; SUB_CHUNKS = buildSubtitleChunks(BEATS); window.CORE_READY = true; }

  function bgPier(t, drained = false) {
    ditherGradV(0, 0, PW, 185, ['#1d4ed8', '#38bdf8', '#7dd3fc']);
    glowOrb(148, 52, 9, '#fef9c3', '#fde047', '#38bdf8');
    // Wooden pier
    rect(0, 184, 180, 10, '#92400e');
    rect(18, 194, 8, 60, '#78350f');
    rect(152, 194, 8, 60, '#78350f');
    if (drained) {
      // Exposed dry seabed with stranded pixel fish & giant open drain hole (below subtitle safe zone!)
      ditherBand(0, 194, PW, 126, '#d97706', '#92400e', 0.45);
      ellipse(90, 266, 26, 8, '#030712');
      pixelText('DRAINED!', 90, 250, '#fde047', '#090d1f', 'center');
    } else {
      ditherGradV(0, 194, PW, 126, ['#0284c7', '#0369a1', '#0c4a6e']);
      for (let x = 8; x < PW; x += 22) rect(x, 196 + Math.round(Math.sin(t * 5 + x) * 2), 10, 2, '#bae6fd');
    }
  }

  function bgDeepOcean(t, abyss = false) {
    ditherGradV(0, 0, PW, PH, abyss ? ['#020617', '#090d1f', '#040711'] : ['#082f49', '#0c4a6e', '#041226']);
    for (const b of BUBBLES) {
      const by = (PH - ((t * b.sp + b.y) % PH));
      rect(b.x, by, b.s, b.s, abyss ? '#22d3ee' : '#7dd3fc');
    }
    if (abyss) {
      // Seabed sand + giant golden drain plug chain!
      ditherBand(0, 202, PW, 118, '#334155', '#1e293b', 0.4);
      rect(0, 202, PW, 2, '#64748b');
      rect(82, 196, 16, 8, '#facc15');
      line(90, 196, 90, 174, '#eab308');
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
    if (bi === 7 || bi === 8) { camZoom = 1.14 + u * 0.06; camY = 5; }
    if (bi === 11) { camZoom = 1.08 + u * 0.10; camRot = Math.sin(t * 14) * 0.03; }
    if (bi === 12) { camZoom = 1.16 + u * 0.08; camRot = -0.04; camY = 6; }
    if (bi === 15 && u > 0.5) { camZoom = 1.12 + (u - 0.5) * 0.06; camX = -8; camY = 5; }

    const k1 = kickOffset(t, BEATS[7]?.start || 18, 5);
    const k2 = kickOffset(t, BEATS[12]?.start || 36, 7);
    const k3 = kickOffset(t, BEATS[13]?.start || 38, 6);
    camX += k1.x + k2.x + k3.x; camY += k1.y + k2.y + k3.y; camRot += k1.rot + k2.rot + k3.rot;

    pctx.clearRect(0, 0, PW, PH);

    if (bi === 0 || bi === 1) {
      bgPier(t, false);
      drawHudPill('OFFER:', '$1,000', 90, 26, '#4ade80');
      drawBall({ role: 'host', cx: 42, cy: 164, R: 19, expr: blinkExpr('normal', t, 1), lookX: 1, isTalking: isSpeaking(BEATS, 'host', t), t, outfit: 'host_hoodie', hat: 'host_cap', prop: 'cash_1k', propSide: 1 });
      drawBall({ role: 'mrbeast', cx: 138, cy: 164, R: 19, expr: blinkExpr('squint', t, 2), lookX: -1, isTalking: isSpeaking(BEATS, 'mrbeast', t), t, outfit: 'mrbeast_hoodie', hat: 'mrbeast_hair' });
    } else if (bi === 2 || bi === 3) {
      bgPier(t, false);
      drawHudPill('OFFER:', '$2,000', 90, 26, '#facc15');
      drawBall({ role: 'host', cx: 42, cy: 164, R: 19, expr: blinkExpr('normal', t, 1), lookX: 1, isTalking: isSpeaking(BEATS, 'host', t), t, outfit: 'host_hoodie', hat: 'host_cap', prop: 'cash_2k', propSide: 1 });
      drawBall({ role: 'mc', cx: 138, cy: 164, R: 19, expr: bi === 3 ? 'dollar' : blinkExpr('wide', t, 3), lookX: -1, isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'swim_floaties', hat: 'snorkel_goggles' });
    } else if (bi === 4 || bi === 5 || bi === 6) {
      bgDeepOcean(t, false);
      drawHudPill('DEPTH:', '1,000M', 90, 26, '#22d3ee');
      drawBall({ role: 'mc', cx: 52, cy: 180, R: 19, expr: bi === 5 ? 'wide' : blinkExpr('normal', t, 3), lookX: 1, isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'swim_floaties', hat: 'snorkel_goggles', sweat: true, shadow: false });
      if (bi >= 5) {
        drawBall({ role: 'squid', cx: 130, cy: 180, R: 19, expr: 'angry', lookX: -1, isTalking: isSpeaking(BEATS, 'squid', t), t, outfit: 'squid_cape', hat: 'sleep_mask', shadow: false });
      }
    } else if (bi === 7 || bi === 8) {
      bgDeepOcean(t, true);
      drawHudPill('PRESSURE:', '1,000 BAR', 90, 26, '#f472b6');
      // MC squished grape-sized by 1,000 bar pressure!
      drawBall({ role: 'mc', cx: 90, cy: 188, R: 10, expr: 'wide', isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'swim_floaties', hat: 'snorkel_goggles', prop: bi === 8 ? 'drain_plug' : null, propSide: 1 });
    } else if (bi === 9 || bi === 10 || bi === 11) {
      bgDeepOcean(t, true);
      drawHudPill('DEPTH:', '11,000M', 90, 26, '#38bdf8');
      drawBall({ role: 'mc', cx: 48, cy: 184, R: 12, expr: bi === 10 ? 'dollar' : 'wide', lookX: 1, isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'swim_floaties', hat: 'snorkel_goggles' });
      drawBall({ role: 'blob', cx: 130, cy: 180, R: 21, expr: bi === 11 ? 'wide' : blinkExpr('squint', t, 4), lookX: -1, isTalking: isSpeaking(BEATS, 'blob', t), t, glasses: true, sweat: bi === 11 });
    } else if (bi === 12) {
      bgDeepOcean(t, true);
      drawHudPill('PLUG:', 'PULLED!', 90, 26, '#4ade80');
      drawBall({ role: 'mc', cx: 90, cy: 176, R: 14, expr: 'dollar', isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'swim_floaties', hat: 'snorkel_goggles', prop: 'drain_plug', propSide: 1 });
    } else {
      bgPier(t, true);
      const isCoupon = bi === 15 && u > 0.56;
      drawHudPill('OCEAN:', isCoupon ? 'COUPON?!' : '0% WATER', 90, 26, isCoupon ? '#ef4444' : '#facc15');
      drawBall({ role: 'mc', cx: 42, cy: 164, R: 19, expr: isCoupon ? 'wide' : blinkExpr('normal', t, 3), lookX: 1, isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'swim_floaties', hat: 'snorkel_goggles', prop: 'drain_plug', propSide: 1, sweat: isCoupon });
      drawBall({ role: 'host', cx: 138, cy: 164, R: 19, expr: blinkExpr('angry', t, 1), lookX: -1, isTalking: isSpeaking(BEATS, 'host', t), t, outfit: 'host_hoodie', hat: 'host_cap', prop: isCoupon ? 'coupon' : 'cash_2k', propSide: -1 });
    }

    presentFrame(ctx, c.width, c.height, camX, camY, camRot, camZoom, SUB_CHUNKS, t);
  }

  window.renderFrame = renderFrame;
  window.initCoreShort = init;
})();
