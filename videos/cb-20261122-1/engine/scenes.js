/* Lightning Bolt 8-Bit Countryball Short — 180x320 Scenes + 1080x1920 Black-Pill Subtitles */
window.SHORT_APP = (() => {
  const {
    PW, PH, pctx, px, rect, line, ditherBand, ditherGradV, disk, glowOrb,
    pixelText, drawHudPill, buildSubtitleChunks, presentFrame, kickOffset, blinkExpr, isSpeaking, activeBeatIndex, seeded,
  } = window.PX;
  const { drawBall, register, OUTLINE } = window.CHARS;

  register({
    skins: {
      cloud: { hi: '#cbd5e1', lit: '#64748b', shade: '#334155' },
      volt:  { hi: '#ffffff', lit: '#38bdf8', shade: '#0284c7' },
    },
    outfits: {
      cloud_coat: (dx, dy, R, x, y, shade) => shade ? '#1e293b' : '#475569',
      volt_robe:  (dx, dy, R, x, y, shade) => Math.abs(dx) <= 1 ? '#fde047' : (shade ? '#0369a1' : '#0ea5e9'),
    },
    hats: {
      static_hair: (cx, cy, R, t) => {
        const top = Math.round(cy - R - 2);
        // Spiky upright electrified pixel hair!
        rect(cx - 8, top, 17, 3, '#3b2314');
        rect(cx - 7, top - 6, 3, 6, '#4e2f1b');
        rect(cx - 2, top - 8, 3, 8, '#3b2314');
        rect(cx + 3, top - 7, 3, 7, '#4e2f1b');
        if (Math.floor(t * 16) % 2 === 0) {
          px(cx - 6, top - 8, '#38bdf8');
          px(cx + 5, top - 9, '#fde047');
        }
      },
      cloud_puff: (cx, cy, R, t) => {
        const top = Math.round(cy - R - 3);
        disk(cx - 6, top + 2, 5, '#e2e8f0');
        disk(cx, top, 6, '#f8fafc');
        disk(cx + 6, top + 2, 5, '#cbd5e1');
        if (Math.floor(t * 10) % 3 === 0) {
          px(cx - 1, top + 3, '#fde047');
          px(cx, top + 4, '#fde047');
        }
      },
      volt_crown: (cx, cy, R, t) => {
        const top = Math.round(cy - R - 5);
        rect(cx - 8, top + 3, 17, 2, '#fde047');
        rect(cx - 6, top, 2, 3, '#38bdf8');
        rect(cx, top - 2, 2, 5, '#fde047');
        rect(cx + 5, top, 2, 3, '#38bdf8');
        glowOrb(cx + 1, top - 4 + Math.round(Math.sin(t * 8)), 2, '#ffffff', '#fde047', '#38bdf8');
      },
    },
    props: {
      umbrella: (x, y) => {
        // Metal umbrella (walking antenna!)
        line(x + 4, y - 8, x + 4, y + 8, '#cbd5e1');
        rect(x + 3, y - 10, 3, 2, '#fde047');
        rect(x - 3, y - 7, 15, 3, '#ef4444');
        rect(x - 1, y - 9, 11, 2, '#dc2626');
      },
      jar_empty: (x, y) => {
        rect(x, y - 2, 9, 11, OUTLINE);
        rect(x + 1, y - 1, 7, 9, '#bae6fd');
        rect(x + 2, y + 1, 5, 6, '#38bdf8');
        rect(x + 1, y - 3, 7, 2, '#f59e0b');
      },
      jar_lightning: (x, y, t) => {
        glowOrb(x + 4, y + 4, 9, '#ffffff', '#38bdf8', '#fde047');
        rect(x, y - 2, 9, 11, OUTLINE);
        rect(x + 1, y - 1, 7, 9, Math.floor(t * 20) % 2 ? '#fde047' : '#38bdf8');
        rect(x + 2, y + 1, 5, 6, '#ffffff');
        rect(x + 1, y - 3, 7, 2, '#f59e0b');
      },
      fried_bill: (x, y) => {
        rect(x - 1, y - 1, 13, 12, OUTLINE);
        rect(x, y, 11, 10, '#f8fafc');
        rect(x + 2, y + 2, 7, 2, '#ef4444');
        rect(x + 2, y + 5, 7, 1, '#334155');
        rect(x + 2, y + 7, 5, 1, '#334155');
        pixelText('-$2K', x + 5, y - 7, '#ef4444', '#090d1f', 'center');
      },
    },
  });

  const DROPS = (() => {
    const r = seeded(777);
    return Array.from({ length: 42 }, () => ({ x: r() * PW, y: r() * PH, sp: 60 + r() * 90, ph: r() * 6.28 }));
  })();

  let BEATS = [], SUB_CHUNKS = [];
  function init(bd) { BEATS = bd.beats || []; SUB_CHUNKS = buildSubtitleChunks(BEATS); window.CORE_READY = true; }

  function drawBolt(x0, y0, x1, y1, colCore = '#ffffff', colGlow = '#38bdf8') {
    const mx = Math.round((x0 + x1) * 0.5) + 6;
    const my = Math.round((y0 + y1) * 0.5);
    line(x0 - 1, y0, mx - 1, my, colGlow);
    line(mx - 1, my, x1 - 1, y1, colGlow);
    line(x0 + 1, y0, mx + 1, my, colGlow);
    line(mx + 1, my, x1 + 1, y1, colGlow);
    line(x0, y0, mx, my, colCore);
    line(mx, my, x1, y1, colCore);
  }

  function bgStormStreet(t, friedGrid = false) {
    const flash = friedGrid && Math.floor(t * 14) % 4 === 0;
    ditherGradV(0, 0, PW, 195, flash ? ['#1e293b', '#334155', '#0284c7'] : ['#030712', '#0f172a', '#1e1b4b']);
    // Rain streaks
    for (const d of DROPS) {
      const rx = (d.x - t * 25 + PW * 10) % PW;
      const ry = (d.y + t * d.sp) % 190;
      line(rx, ry, rx - 1, ry + 4, '#60a5fa');
    }
    // Houses + sparking toasters when friedGrid is true!
    rect(8, 142, 36, 30, '#1e293b');
    rect(6, 134, 40, 8, '#ef4444');
    rect(136, 138, 36, 34, '#334155');
    rect(134, 130, 40, 8, '#2563eb');
    if (friedGrid) {
      const spk = Math.floor(t * 24) % 2 === 0;
      rect(14, 150, 8, 8, spk ? '#fde047' : '#38bdf8');
      rect(144, 148, 8, 8, spk ? '#38bdf8' : '#fde047');
      if (spk) {
        drawBolt(18, 150, 32, 128, '#ffffff', '#fde047');
        drawBolt(148, 148, 134, 122, '#ffffff', '#38bdf8');
      }
      // Sparking toaster silhouettes on sidewalk
      rect(28, 178, 9, 7, '#cbd5e1');
      rect(30, 176, 5, 2, '#f97316');
      rect(142, 178, 9, 7, '#cbd5e1');
      rect(144, 176, 5, 2, '#f97316');
    } else {
      rect(14, 150, 8, 8, '#facc15');
      rect(144, 148, 8, 8, '#facc15');
    }
    ditherBand(0, 170, PW, 16, '#15803d', '#14532d', 0.4);
    rect(0, 186, PW, 14, '#64748b');
    ditherGradV(0, 200, PW, 120, ['#334155', '#1e293b', '#0f172a']);
    for (let x = 8; x < PW; x += 28) rect(x, 224, 14, 3, '#facc15');
  }

  function bgThunderCore(t, megaBolt = false) {
    ditherGradV(0, 0, PW, 198, ['#09051a', '#1e1b4b', '#312e81']);
    // Storm cloud ceiling
    for (let x = 12; x < PW; x += 28) {
      disk(x, 56 + Math.round(Math.sin(t * 3 + x) * 2), 18, '#334155');
      disk(x + 10, 60, 14, '#475569');
    }
    // Electric plasma arcs across the storm chamber
    if (megaBolt || Math.floor(t * 10) % 3 === 0) {
      drawBolt(34, 66, 90, 145, '#ffffff', '#38bdf8');
      drawBolt(144, 66, 94, 140, '#ffffff', '#fde047');
    }
    if (megaBolt) {
      glowOrb(90, 118, 20, '#ffffff', '#38bdf8', '#fde047');
    }
    ditherGradV(0, 196, PW, 124, ['#1e293b', '#0f172a', '#020617']);
    for (const d of DROPS) {
      const ex = (d.x + Math.sin(t * 6 + d.ph) * 5 + PW) % PW;
      const ey = (210 - ((t * d.sp * 0.5 + d.y) % 140));
      px(ex, ey, d.ph > 3.14 ? '#fde047' : '#38bdf8');
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

    const k1 = kickOffset(t, BEATS[7]?.start || 18, 6);
    const k2 = kickOffset(t, BEATS[12]?.start || 32, 7);
    const k3 = kickOffset(t, BEATS[13]?.start || 34, 5);
    camX += k1.x + k2.x + k3.x; camY += k1.y + k2.y + k3.y; camRot += k1.rot + k2.rot + k3.rot;

    pctx.clearRect(0, 0, PW, PH);

    if (bi === 0 || bi === 1) {
      bgStormStreet(t, false);
      drawHudPill('OFFER:', '$1,000', 90, 26, '#4ade80');
      drawBall({ role: 'host', cx: 42, cy: 180, R: 19, expr: blinkExpr('normal', t, 1), lookX: 1, isTalking: isSpeaking(BEATS, 'host', t), t, outfit: 'host_hoodie', hat: 'host_cap', prop: 'cash_1k', propSide: 1 });
      drawBall({ role: 'mrbeast', cx: 138, cy: 180, R: 19, expr: blinkExpr('squint', t, 2), lookX: -1, isTalking: isSpeaking(BEATS, 'mrbeast', t), t, outfit: 'mrbeast_hoodie', hat: 'mrbeast_hair' });
    } else if (bi === 2 || bi === 3) {
      bgStormStreet(t, false);
      drawHudPill('OFFER:', '$2,000', 90, 26, '#facc15');
      drawBall({ role: 'host', cx: 42, cy: 180, R: 19, expr: blinkExpr('normal', t, 1), lookX: 1, isTalking: isSpeaking(BEATS, 'host', t), t, outfit: 'host_hoodie', hat: 'host_cap', prop: 'cash_2k', propSide: 1 });
      drawBall({ role: 'mc', cx: 138, cy: 180, R: 19, expr: bi === 3 ? 'cool_shades' : blinkExpr('wide', t, 3), lookX: -1, isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'mc_hoodie', hat: 'mc_hair', prop: bi === 3 ? 'umbrella' : null, propSide: -1 });
    } else if (bi === 4) {
      bgThunderCore(t, false);
      drawHudPill('STATIC:', '100,000 V', 90, 26, '#38bdf8');
      drawBall({ role: 'mc', cx: 90, cy: 182, R: 20, expr: 'wide', isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'mc_hoodie', hat: 'static_hair', prop: 'umbrella', propSide: 1, sweat: true });
    } else if (bi === 5 || bi === 6) {
      bgThunderCore(t, false);
      drawHudPill('BOLT:', '30,000°C', 90, 26, '#fde047');
      drawBall({ role: 'mc', cx: 50, cy: 182, R: 19, expr: blinkExpr('wide', t, 2), lookX: 1, isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'mc_hoodie', hat: 'static_hair', prop: bi === 5 ? 'umbrella' : null, propSide: 1, sweat: true });
      drawBall({ role: 'cloud', cx: 132, cy: 182, R: 20, expr: 'angry', lookX: -1, isTalking: isSpeaking(BEATS, 'cloud', t), t, outfit: 'cloud_coat', hat: 'cloud_puff' });
    } else if (bi === 7 || bi === 8) {
      bgThunderCore(t, true);
      drawHudPill('HEAT:', '5X THE SUN', 90, 26, '#fb923c');
      const hatGone = bi === 8 && u > 0.55;
      drawBall({ role: 'mc', cx: 90, cy: 182, R: 21, expr: 'wide', isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'mc_hoodie', hat: hatGone ? null : 'static_hair', prop: 'jar_empty', propSide: 1, sweat: true });
    } else if (bi === 9 || bi === 10 || bi === 11) {
      bgThunderCore(t, false);
      drawHudPill('AMPS:', '30,000 A', 90, 26, '#38bdf8');
      drawBall({ role: 'mc', cx: 48, cy: 182, R: 19, expr: bi === 10 ? 'dollar' : 'cool_shades', lookX: 1, isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'mc_hoodie', hat: 'mc_hair', prop: 'jar_empty', propSide: 1 });
      drawBall({ role: 'volt', cx: 132, cy: 182, R: 19, expr: bi === 11 ? 'wide' : blinkExpr('normal', t, 4), lookX: -1, isTalking: isSpeaking(BEATS, 'volt', t), t, outfit: 'volt_robe', hat: 'volt_crown', glasses: true, beard: true, sweat: bi === 11 });
    } else if (bi === 12) {
      bgThunderCore(t, true);
      drawHudPill('VOLTS:', '300 MILLION', 90, 26, '#fde047');
      drawBall({ role: 'mc', cx: 90, cy: 176, R: 22, expr: 'dollar', isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'mc_hoodie', hat: 'static_hair', prop: 'jar_lightning', propSide: 1 });
    } else {
      bgStormStreet(t, true);
      const isBill = bi === 15 && u > 0.48;
      drawHudPill(isBill ? 'PAYOUT:' : 'GRID:', isBill ? '$0.00' : 'FRIED!', 90, 26, isBill ? '#ef4444' : '#fde047');
      drawBall({ role: 'mc', cx: 44, cy: 182, R: 19, expr: isBill ? 'wide' : 'cool_shades', lookX: 1, isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'mc_hoodie', hat: 'static_hair', prop: 'jar_lightning', propSide: 1, sweat: isBill });
      drawBall({ role: 'host', cx: 136, cy: 182, R: 19, expr: blinkExpr('angry', t, 1), lookX: -1, isTalking: isSpeaking(BEATS, 'host', t), t, outfit: 'host_hoodie', hat: 'host_cap', prop: isBill ? 'fried_bill' : 'cash_2k', propSide: -1 });
    }

    presentFrame(ctx, c.width, c.height, camX, camY, camRot, camZoom, SUB_CHUNKS, t);
  }

  window.renderFrame = renderFrame;
  window.initCoreShort = init;
})();
