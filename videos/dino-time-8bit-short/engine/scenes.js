/* T-Rex Time Machine 8-Bit Countryball Short — 180x320 Scenes + 1080x1920 Black-Pill Subtitles */
window.SHORT_APP = (() => {
  const {
    PW, PH, pctx, px, rect, line, ditherBand, ditherGradV, disk, glowOrb,
    pixelText, drawHudPill, buildSubtitleChunks, presentFrame, kickOffset, blinkExpr, isSpeaking, activeBeatIndex,
  } = window.PX;
  const { drawBall, register, OUTLINE } = window.CHARS;

  register({
    skins: {
      trex:   { hi: '#86efac', lit: '#22c55e', shade: '#15803d' },
      raptor: { hi: '#fed7aa', lit: '#f97316', shade: '#9a3412' },
    },
    outfits: {
      safari_vest: (dx, dy, R, x, y, shade) => {
        if (Math.abs(dx) <= 2) return '#fde68a';
        return shade ? '#92400e' : '#d97706';
      },
      raptor_tie: (dx, dy, R, x, y, shade) => {
        if (Math.abs(dx) <= 1 && dy > R * 0.25) return '#ef4444';
        return shade ? '#7c2d12' : '#c2410c';
      },
    },
    hats: {
      safari_hat: (cx, cy, R) => {
        const top = Math.round(cy - R - 3);
        rect(cx - R - 4, top + 3, R * 2 + 8, 3, '#b45309');
        rect(cx - Math.round(R * 0.65), top - 3, Math.round(R * 1.3), 6, '#d97706');
        rect(cx - Math.round(R * 0.65), top + 2, Math.round(R * 1.3), 1, '#181124');
      },
    },
    props: {
      steak_smoothie: (x, y) => {
        rect(x, y - 2, 9, 11, OUTLINE);
        rect(x + 1, y - 1, 7, 9, '#ef4444');
        rect(x + 2, y - 4, 2, 3, '#ffffff');
        pixelText('BEEF', x + 4, y - 9, '#fca5a5', '#090d1f', 'center');
      },
      pigeon: (x, y, t) => {
        const bob = Math.round(Math.sin(t * 14));
        disk(x + 4, y + 3 + bob, 4, '#94a3b8');
        disk(x + 7, y + bob, 3, '#64748b');
        px(x + 8, y + bob, '#ffffff');
        rect(x + 10, y + bob, 2, 1, '#f59e0b');
        pixelText('DINO?', x + 5, y - 8, '#4ade80', '#090d1f', 'center');
      },
      cash_5: (x, y) => {
        rect(x - 1, y - 1, 13, 8, OUTLINE);
        rect(x, y, 11, 6, '#22c55e');
        pixelText('$5', x + 5, y - 7, '#4ade80', '#062812', 'center');
      },
    },
  });

  let BEATS = [], SUB_CHUNKS = [];
  function init(bd) { BEATS = bd.beats || []; SUB_CHUNKS = buildSubtitleChunks(BEATS); window.CORE_READY = true; }

  function drawCardboardTimeBox(cx, yFloor, t, active = false) {
    const w = 30, h = 42, x0 = Math.round(cx - w / 2), y0 = Math.round(yFloor - h);
    rect(x0 - 1, y0 - 1, w + 2, h + 2, OUTLINE);
    rect(x0, y0, w, h, '#d97706');
    rect(x0 + 2, y0 + 2, w - 4, h - 4, '#b45309');
    rect(x0, y0 + 18, w, 3, '#fde68a'); // packing tape
    rect(x0 + 3, y0 - 11, w - 6, 9, '#0f172a');
    pixelText('TIME', cx, y0 - 9, active ? '#22d3ee' : '#fde047', null, 'center');
    rect(x0 + 3, y0 + 6, w - 6, 10, '#f8fafc');
    pixelText('66MBC', cx, y0 + 9, '#181124', null, 'center');
  }

  function bgStreet(t) {
    ditherGradV(0, 0, PW, 195, ['#1d4ed8', '#38bdf8', '#7dd3fc']);
    glowOrb(148, 52, 9, '#fef9c3', '#fde047', '#38bdf8');
    rect(8, 142, 36, 30, '#cbd5e1'); rect(6, 134, 40, 8, '#ef4444');
    rect(136, 138, 36, 34, '#fde68a'); rect(134, 130, 40, 8, '#2563eb');
    ditherBand(0, 170, PW, 16, '#16a34a', '#15803d', 0.4);
    rect(0, 186, PW, 14, '#94a3b8');
    ditherGradV(0, 200, PW, 120, ['#334155', '#1e293b', '#0f172a']);
    for (let x = 8; x < PW; x += 28) rect(x, 224, 14, 3, '#facc15');
  }

  function bgCretaceous(t, asteroid = false) {
    ditherGradV(0, 0, PW, 196, asteroid ? ['#450a0a', '#9a3412', '#f97316'] : ['#065f46', '#10b981', '#6ee7b7']);
    // Volcano silhouette in distance
    for (let k = 0; k < 22; k++) {
      rect(24 - k, 152 + k * 2, 12 + k * 2, 2, '#334155');
    }
    glowOrb(30, 146, 5, '#fef08a', '#f97316', '#dc2626');
    // Palm ferns
    for (const fx of [14, 158]) {
      rect(fx, 136, 4, 62, '#78350f');
      rect(fx - 10, 132, 24, 6, '#15803d');
      rect(fx - 6, 127, 16, 5, '#22c55e');
    }
    if (asteroid) {
      const ay = Math.round(52 + ((t * 18) % 45));
      const ax = Math.round(138 - ((t * 14) % 40));
      glowOrb(ax, ay, 10, '#ffffff', '#fde047', '#ef4444');
    }
    ditherBand(0, 198, PW, 122, '#15803d', '#064e3b', 0.4);
    rect(0, 198, PW, 3, '#4ade80');
  }

  function drawTRexGiant(cx, cy, t, isTalking) {
    const bounce = isTalking ? Math.round(Math.abs(Math.sin(t * 24)) * -2) : 0;
    const x = Math.round(cx), y = Math.round(cy + bounce);
    // Giant green pixel T-Rex body + huge head + hilarious tiny 3px arms!
    rect(x - 16, y - 34, 36, 22, OUTLINE);
    rect(x - 15, y - 33, 34, 20, '#16a34a'); // huge head
    rect(x - 15, y - 16, 24, 4, '#fef3c7'); // teeth row!
    rect(x - 10, y - 30, 7, 7, '#ffffff');
    rect(x - 8, y - 28, 3, 3, OUTLINE);
    // Torso & tail
    rect(x - 8, y - 12, 26, 26, OUTLINE);
    rect(x - 7, y - 11, 24, 24, '#15803d');
    rect(x + 17, y - 2, 16, 12, '#15803d');
    // Tiny comical T-Rex arms!
    rect(x - 13, y - 4, 6, 3, '#22c55e');
    rect(x - 14, y - 2, 3, 3, '#fef3c7');
    // Legs
    rect(x - 4, y + 13, 8, 12, '#166534');
    rect(x + 8, y + 13, 8, 12, '#166534');
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
    if (bi === 5 || bi === 6) { camZoom = 1.08 + u * 0.06; }
    if (bi === 11) { camZoom = 1.08 + u * 0.10; camRot = Math.sin(t * 14) * 0.03; }
    if (bi === 12) { camZoom = 1.16 + u * 0.08; camRot = -0.04; camY = 6; }
    if (bi === 15 && u > 0.5) { camZoom = 1.12 + (u - 0.5) * 0.06; camX = -8; camY = 5; }

    const k1 = kickOffset(t, BEATS[5]?.start || 13, 6);
    const k2 = kickOffset(t, BEATS[12]?.start || 36, 7);
    const k3 = kickOffset(t, BEATS[13]?.start || 38, 6);
    camX += k1.x + k2.x + k3.x; camY += k1.y + k2.y + k3.y; camRot += k1.rot + k2.rot + k3.rot;

    pctx.clearRect(0, 0, PW, PH);

    if (bi === 0 || bi === 1) {
      bgStreet(t);
      drawHudPill('OFFER:', '$1,000', 90, 26, '#4ade80');
      drawCardboardTimeBox(90, 198, t, false);
      drawBall({ role: 'host', cx: 38, cy: 180, R: 19, expr: blinkExpr('normal', t, 1), lookX: 1, isTalking: isSpeaking(BEATS, 'host', t), t, outfit: 'host_hoodie', hat: 'host_cap', prop: 'cash_1k', propSide: 1 });
      drawBall({ role: 'mrbeast', cx: 142, cy: 180, R: 19, expr: blinkExpr('squint', t, 2), lookX: -1, isTalking: isSpeaking(BEATS, 'mrbeast', t), t, outfit: 'mrbeast_hoodie', hat: 'mrbeast_hair' });
    } else if (bi === 2 || bi === 3) {
      bgStreet(t);
      drawHudPill('OFFER:', '$2,000', 90, 26, '#facc15');
      drawCardboardTimeBox(90, 198, t, bi === 3);
      drawBall({ role: 'host', cx: 38, cy: 180, R: 19, expr: blinkExpr('normal', t, 1), lookX: 1, isTalking: isSpeaking(BEATS, 'host', t), t, outfit: 'host_hoodie', hat: 'host_cap', prop: 'cash_2k', propSide: 1 });
      drawBall({ role: 'mc', cx: 142, cy: 180, R: 19, expr: bi === 3 ? 'dollar' : blinkExpr('wide', t, 3), lookX: -1, isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'safari_vest', hat: 'safari_hat' });
    } else if (bi === 4) {
      bgCretaceous(t, false);
      drawHudPill('ERA:', '66M BC', 90, 26, '#4ade80');
      drawCardboardTimeBox(44, 198, t, true);
      drawBall({ role: 'mc', cx: 112, cy: 180, R: 20, expr: u > 0.5 ? 'wide' : blinkExpr('normal', t, 3), isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'safari_vest', hat: 'safari_hat', sweat: true });
    } else if (bi >= 5 && bi <= 8) {
      bgCretaceous(t, false);
      drawHudPill('THREAT:', 'T-REX!', 90, 26, '#ef4444');
      drawBall({ role: 'mc', cx: 46, cy: 180, R: 18, expr: bi === 8 ? 'wide' : blinkExpr('normal', t, 3), lookX: 1, isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'safari_vest', hat: 'safari_hat', prop: bi === 8 ? 'steak_smoothie' : null, propSide: 1, sweat: true });
      drawTRexGiant(130, 174, t, isSpeaking(BEATS, 'trex', t));
    } else if (bi === 9 || bi === 10 || bi === 11) {
      bgCretaceous(t, bi === 11);
      drawHudPill('COUNTDOWN:', bi === 11 ? 'METEOR!' : '66M BC', 90, 26, bi === 11 ? '#ef4444' : '#facc15');
      drawBall({ role: 'mc', cx: 48, cy: 180, R: 19, expr: bi === 10 ? 'dollar' : blinkExpr('wide', t, 3), lookX: 1, isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'safari_vest', hat: 'safari_hat' });
      drawBall({ role: 'raptor', cx: 130, cy: 180, R: 19, expr: bi === 11 ? 'wide' : blinkExpr('normal', t, 4), lookX: -1, isTalking: isSpeaking(BEATS, 'raptor', t), t, outfit: 'raptor_tie', glasses: true, sweat: bi === 11 });
    } else if (bi === 12) {
      bgCretaceous(t, true);
      drawHudPill('BOOP:', 'SNOOT!', 90, 26, '#4ade80');
      drawBall({ role: 'mc', cx: 74, cy: 180, R: 20, expr: 'dollar', isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'safari_vest', hat: 'safari_hat', prop: 'pigeon', propSide: 1 });
    } else {
      bgStreet(t);
      const isFive = bi === 15 && u > 0.56;
      drawHudPill('PAYOUT:', isFive ? '$5.00' : '$2,000?', 90, 26, isFive ? '#38bdf8' : '#facc15');
      drawCardboardTimeBox(90, 198, t, false);
      drawBall({ role: 'mc', cx: 40, cy: 180, R: 19, expr: isFive ? 'wide' : blinkExpr('normal', t, 3), lookX: 1, isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'safari_vest', hat: 'safari_hat', prop: 'pigeon', propSide: 1, sweat: isFive });
      drawBall({ role: 'host', cx: 140, cy: 180, R: 19, expr: blinkExpr('squint', t, 1), lookX: -1, isTalking: isSpeaking(BEATS, 'host', t), t, outfit: 'host_hoodie', hat: 'host_cap', prop: isFive ? 'cash_5' : 'cash_2k', propSide: -1 });
    }

    presentFrame(ctx, c.width, c.height, camX, camY, camRot, camZoom, SUB_CHUNKS, t);
  }

  window.renderFrame = renderFrame;
  window.initCoreShort = init;
})();
