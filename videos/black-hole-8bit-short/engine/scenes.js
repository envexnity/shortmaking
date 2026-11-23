/* Black Hole 8-Bit Countryball Short — 180x320 Scenes + 1080x1920 Black-Pill Subtitles */
window.SHORT_APP = (() => {
  const {
    PW, PH, pctx, px, rect, line, ditherBand, ditherGradV, disk, ellipse, glowOrb,
    pixelText, drawHudPill, buildSubtitleChunks, presentFrame, kickOffset, blinkExpr, isSpeaking, activeBeatIndex, seeded,
  } = window.PX;
  const { drawBall, register, OUTLINE, bayerPick } = window.CHARS;

  register({
    skins: {
      singularity: { hi: '#c084fc', lit: '#7e22ce', shade: '#3b0764' },
      warden:      { hi: '#fef08a', lit: '#eab308', shade: '#854d0e' },
    },
    outfits: {
      singularity_suit: (dx, dy, R, x, y, shade) => {
        if (Math.abs(dx) <= 1) return '#f472b6';
        return shade ? '#1e1b4b' : '#312e81';
      },
      chrome_hoodie: (dx, dy, R, x, y, shade) => {
        if (Math.abs(dx + 3) <= 0 && dy > R * 0.24 && dy < R * 0.65) return '#22d3ee';
        if (Math.abs(dx - 3) <= 0 && dy > R * 0.24 && dy < R * 0.65) return '#22d3ee';
        return shade ? '#475569' : '#94a3b8';
      },
    },
    hats: {
      astronaut_helmet: (cx, cy, R) => {
        const top = Math.round(cy - R - 2);
        rect(cx - 10, top + 2, 20, 4, '#e2e8f0');
        rect(cx - 9, top + 3, 18, 2, '#38bdf8');
        rect(cx - 1, top - 3, 2, 5, '#cbd5e1');
        disk(cx, top - 4, 2, '#ef4444');
      },
      clock_hat: (cx, cy, R, t) => {
        const ny = Math.round(cy - R - 8);
        disk(cx, ny + 2, 6, '#181124');
        disk(cx, ny + 2, 5, '#fef9c3');
        line(cx, ny + 2, cx + Math.cos(t * 25) * 4, ny + 2 + Math.sin(t * 25) * 4, '#ef4444');
      },
    },
    props: {
      space_toast: (x, y) => {
        rect(x - 1, y - 1, 10, 10, OUTLINE);
        rect(x, y, 8, 8, '#92400e');
        rect(x + 1, y + 1, 6, 6, '#facc15');
        px(x + 3, y + 3, '#22d3ee');
      },
      pocket_watch: (x, y, t) => {
        disk(x + 4, y + 3, 6, OUTLINE);
        disk(x + 4, y + 3, 5, '#fde047');
        disk(x + 4, y + 3, 3, '#ffffff');
        line(x + 4, y + 3, x + 4 + Math.cos(t * 32) * 3, y + 3 + Math.sin(t * 32) * 3, '#ef4444');
      },
    },
  });

  const STARS = (() => {
    const r = seeded(404);
    return Array.from({ length: 48 }, () => ({ x: r() * PW, y: r() * PH, sp: 15 + r() * 35, c: r() < 0.5 ? '#fde047' : '#38bdf8' }));
  })();

  let BEATS = [], SUB_CHUNKS = [];
  function init(bd) { BEATS = bd.beats || []; SUB_CHUNKS = buildSubtitleChunks(BEATS); window.CORE_READY = true; }

  function drawPocketBlackHole(cx, cy, r, t) {
    // Glowing orange/magenta accretion disk + pitch-black singularity core
    ellipse(cx, cy, r + 14, Math.max(4, Math.round(r * 0.42)), '#ea580c');
    ellipse(cx, cy, r + 9, Math.max(3, Math.round(r * 0.30)), '#facc15');
    disk(cx, cy, r + 2, '#a855f7');
    disk(cx, cy, r, '#030308');
    // Orbiting spark
    const ox = cx + Math.cos(t * 9) * (r + 11);
    const oy = cy + Math.sin(t * 9) * Math.max(3, r * 0.34);
    rect(ox, oy, 2, 2, '#ffffff');
  }

  function bgStreet(t, future = false) {
    if (future) {
      ditherGradV(0, 0, PW, 195, ['#090418', '#1e1b4b', '#311042']);
      glowOrb(146, 52, 10, '#e0f2fe', '#22d3ee', '#7e22ce');
      // Chrome futuristic skyscrapers & flying pixel cars
      rect(8, 98, 28, 76, '#334155');
      rect(12, 104, 20, 4, '#22d3ee');
      rect(12, 114, 20, 4, '#22d3ee');
      rect(142, 88, 30, 86, '#475569');
      rect(146, 94, 22, 4, '#f472b6');
      rect(146, 104, 22, 4, '#f472b6');
      const carX = ((t * 48) % (PW + 30)) - 15;
      rect(carX, 112, 12, 4, '#22d3ee');
      rect(carX + 2, 110, 6, 2, '#ffffff');
      ditherGradV(0, 174, PW, 146, ['#1e293b', '#0f172a', '#030712']);
      for (let x = 8; x < PW; x += 26) rect(x, 222, 14, 3, '#22d3ee');
    } else {
      ditherGradV(0, 0, PW, 195, ['#1d4ed8', '#38bdf8', '#7dd3fc']);
      glowOrb(148, 52, 9, '#fef9c3', '#fde047', '#38bdf8');
      for (let i = 0; i < 4; i++) {
        const cx = ((i * 54 + t * 6) % (PW + 40)) - 20;
        const cy = 54 + (i % 2) * 16;
        rect(cx, cy, 28, 7, '#ffffff');
        rect(cx + 5, cy - 3, 16, 4, '#f8fafc');
      }
      rect(8, 142, 36, 30, '#cbd5e1'); rect(6, 134, 40, 8, '#ef4444');
      rect(136, 138, 36, 34, '#fde68a'); rect(134, 130, 40, 8, '#2563eb');
      ditherBand(0, 170, PW, 16, '#16a34a', '#15803d', 0.4);
      rect(0, 186, PW, 14, '#94a3b8');
      ditherGradV(0, 200, PW, 120, ['#334155', '#1e293b', '#0f172a']);
      for (let x = 8; x < PW; x += 28) rect(x, 224, 14, 3, '#facc15');
    }
  }

  function bgAccretionInterior(t, timeDilate = false) {
    ditherGradV(0, 0, PW, PH, ['#05020d', '#1e0b36', '#431407', '#05020d']);
    for (const s of STARS) {
      const sy = (s.y + t * s.sp * (timeDilate ? 3.5 : 1)) % PH;
      px(s.x, sy, s.c);
    }
    // Giant swirling accretion ring background
    drawPocketBlackHole(90, 96, 18, t * (timeDilate ? 3 : 1));
    // Purple gravity carpet floor
    ditherBand(0, 202, PW, 118, '#3b0764', '#1e1b4b', 0.45);
    rect(0, 202, PW, 2, '#f97316');
  }

  function bgTrampolineHorizon(t) {
    ditherGradV(0, 0, PW, PH, ['#090418', '#172554', '#090418']);
    // Curved trampoline spacetime grid lines bending down in the middle!
    for (let x = 0; x <= PW; x += 15) {
      const dip = Math.exp(-Math.pow((x - 90) / 38, 2)) * 28;
      line(x, 194, x, 212 + dip, '#38bdf8');
    }
    for (let k = 0; k < 5; k++) {
      const baseY = 196 + k * 8;
      for (let x = 0; x < PW - 4; x += 4) {
        const d1 = Math.exp(-Math.pow((x - 90) / 40, 2)) * 24;
        const d2 = Math.exp(-Math.pow((x + 4 - 90) / 40, 2)) * 24;
        line(x, baseY + d1, x + 4, baseY + d2, '#22d3ee');
      }
    }
    // Bowling ball in trampoline dip
    disk(90, 208, 10, '#0f172a');
    px(86, 204, '#94a3b8');
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
    if (bi === 4 && u > 0.5) { camZoom = 1.12 + (u - 0.5) * 0.08; camRot = -0.03; camY = 6; }
    if (bi === 7) { camZoom = 1.15 + u * 0.05; camY = 5; }
    if (bi === 11) { camZoom = 1.08 + u * 0.10; camRot = Math.sin(t * 14) * 0.03; }
    if (bi === 12) { camZoom = 1.16 + u * 0.08; camRot = -0.04; camY = 6; }
    if (bi === 15 && u > 0.5) { camZoom = 1.12 + (u - 0.5) * 0.06; camX = -8; camY = 5; }

    const k1 = kickOffset(t, BEATS[5]?.start || 13, 5);
    const k2 = kickOffset(t, BEATS[12]?.start || 36, 7);
    const k3 = kickOffset(t, BEATS[13]?.start || 38, 6);
    camX += k1.x + k2.x + k3.x;
    camY += k1.y + k2.y + k3.y;
    camRot += k1.rot + k2.rot + k3.rot;

    pctx.clearRect(0, 0, PW, PH);

    if (bi === 0 || bi === 1) {
      bgStreet(t, false);
      drawHudPill('OFFER:', '$1,000', 90, 26, '#4ade80');
      drawPocketBlackHole(90, 174, 14, t);
      drawBall({ role: 'host', cx: 38, cy: 180, R: 19, expr: blinkExpr('normal', t, 1), lookX: 1, isTalking: isSpeaking(BEATS, 'host', t), t, outfit: 'host_hoodie', hat: 'host_cap', prop: 'cash_1k', propSide: 1 });
      drawBall({ role: 'mrbeast', cx: 142, cy: 180, R: 19, expr: blinkExpr('squint', t, 2), lookX: -1, isTalking: isSpeaking(BEATS, 'mrbeast', t), t, outfit: 'mrbeast_hoodie', hat: 'mrbeast_hair' });
    } else if (bi === 2 || bi === 3) {
      bgStreet(t, false);
      drawHudPill('OFFER:', '$2,000', 90, 26, '#facc15');
      drawPocketBlackHole(90, 174, 16, t);
      drawBall({ role: 'host', cx: 38, cy: 180, R: 19, expr: blinkExpr('normal', t, 1), lookX: 1, isTalking: isSpeaking(BEATS, 'host', t), t, outfit: 'host_hoodie', hat: 'host_cap', prop: 'cash_2k', propSide: 1 });
      drawBall({ role: 'mc', cx: 142, cy: 180, R: 19, expr: bi === 3 ? 'dollar' : blinkExpr('wide', t, 3), lookX: -1, isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'mc_hoodie', hat: 'astronaut_helmet' });
    } else if (bi === 4) {
      bgAccretionInterior(t, false);
      drawHudPill('GRAVITY:', '100,000 G', 90, 26, '#f97316');
      const stretch = 1.0 + u * 0.95;
      drawBall({ role: 'mc', cx: 90, cy: 175, R: 19, squashX: 1 / Math.sqrt(stretch), squashY: stretch, expr: 'wide', isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'mc_hoodie', hat: 'astronaut_helmet', sweat: true });
    } else if (bi === 5 || bi === 6) {
      bgAccretionInterior(t, false);
      drawHudPill('HEIGHT:', '3.0 METERS', 90, 26, '#a855f7');
      drawBall({ role: 'mc', cx: 52, cy: 164, R: 18, squashX: 0.65, squashY: 1.95, expr: bi === 6 ? 'wide' : 'normal', lookX: 1, isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'mc_hoodie', hat: 'astronaut_helmet', sweat: true });
      drawBall({ role: 'singularity', cx: 130, cy: 184, R: 19, expr: 'angry', lookX: -1, isTalking: isSpeaking(BEATS, 'singularity', t), t, outfit: 'singularity_suit', hat: 'clock_hat' });
    } else if (bi === 7 || bi === 8) {
      bgAccretionInterior(t, true);
      const yr = bi === 7 ? Math.round(2026 + u * 2500) : Math.round(4526 + u * 9995474);
      drawHudPill('OUTSIDE:', `YR ${yr > 99999 ? '10M' : yr}`, 90, 26, '#22d3ee');
      drawBall({ role: 'mc', cx: 88, cy: 180, R: 21, expr: 'wide', isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'mc_hoodie', hat: 'astronaut_helmet', prop: 'pocket_watch', propSide: 1, sweat: true });
    } else if (bi === 9 || bi === 10 || bi === 11) {
      bgTrampolineHorizon(t);
      drawHudPill('TIME WARP:', '10,000,000X', 90, 26, '#38bdf8');
      drawBall({ role: 'mc', cx: 48, cy: 178, R: 19, expr: bi === 10 ? 'dollar' : blinkExpr('wide', t, 3), lookX: 1, isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'mc_hoodie', hat: 'astronaut_helmet' });
      drawBall({ role: 'warden', cx: 130, cy: 178, R: 20, expr: bi === 11 ? 'wide' : blinkExpr('normal', t, 4), lookX: -1, isTalking: isSpeaking(BEATS, 'warden', t), t, outfit: 'sage_robe', hat: 'sage_wizard', glasses: true, beard: true, sweat: bi === 11 });
    } else if (bi === 12) {
      bgAccretionInterior(t, true);
      drawHudPill('WARP:', 'EJECT!', 90, 26, '#4ade80');
      drawBall({ role: 'mc', cx: 90, cy: 180 - Math.round(u * 35), R: 22, expr: 'dollar', isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'mc_hoodie', hat: 'astronaut_helmet' });
    } else {
      bgStreet(t, true);
      const isToast = bi === 15 && u > 0.56;
      drawHudPill('YEAR:', isToast ? '10,000,000' : 'FUTURE', 90, 26, isToast ? '#facc15' : '#22d3ee');
      drawBall({ role: 'mc', cx: 44, cy: 182, R: 19, expr: isToast ? 'wide' : blinkExpr('wide', t, 3), lookX: 1, isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'mc_hoodie', hat: 'astronaut_helmet', sweat: isToast });
      drawBall({ role: 'host', cx: 136, cy: 182, R: 19, expr: blinkExpr('squint', t, 1), lookX: -1, isTalking: isSpeaking(BEATS, 'host', t), t, outfit: 'chrome_hoodie', hat: 'host_cap', beard: true, prop: isToast ? 'space_toast' : 'cash_2k', propSide: -1 });
    }

    presentFrame(ctx, c.width, c.height, camX, camY, camRot, camZoom, SUB_CHUNKS, t);
  }

  window.renderFrame = renderFrame;
  window.initCoreShort = init;
})();
