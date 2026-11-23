/* Sun High-Five 8-Bit Countryball Short — 180x320 Scenes + 1080x1920 Black-Pill Subtitles */
window.SHORT_APP = (() => {
  const {
    PW, PH, pctx, px, rect, line, ditherBand, ditherGradV, disk, glowOrb,
    pixelText, drawHudPill, buildSubtitleChunks, presentFrame, kickOffset, blinkExpr, isSpeaking, activeBeatIndex, seeded,
  } = window.PX;
  const { drawBall, register, OUTLINE } = window.CHARS;

  register({
    skins: {
      flare:  { hi: '#fef08a', lit: '#fb923c', shade: '#dc2626' },
      photon: { hi: '#ffffff', lit: '#fde047', shade: '#eab308' },
    },
    outfits: {
      flare_armor: (dx, dy, R, x, y, shade) => shade ? '#9a3412' : '#f97316',
      photon_robe: (dx, dy, R, x, y, shade) => Math.abs(dx) <= 1 ? '#ffffff' : (shade ? '#ca8a04' : '#facc15'),
    },
    hats: {
      flame_crown: (cx, cy, R, t) => {
        const fy = Math.round(cy - R - 6);
        for (let i = -2; i <= 2; i++) {
          const h = 4 + ((Math.floor(t * 14) + Math.abs(i)) % 3);
          rect(cx + i * 4 - 1, fy + (6 - h), 3, h, i % 2 === 0 ? '#fde047' : '#f97316');
        }
      },
    },
    props: {
      thermos: (x, y) => {
        rect(x, y - 2, 8, 12, OUTLINE);
        rect(x + 1, y - 1, 6, 10, '#ef4444');
        rect(x + 1, y - 3, 6, 2, '#cbd5e1');
        rect(x + 2, y + 2, 4, 4, '#fde047');
      },
      sun_thermos: (x, y, t) => {
        glowOrb(x + 4, y + 4, 8, '#ffffff', '#fde047', '#f97316');
        rect(x, y - 2, 8, 12, OUTLINE);
        rect(x + 1, y - 1, 6, 10, '#fde047');
        rect(x + 2, y + 2, 4, 4, '#ffffff');
      },
      electric_bill: (x, y) => {
        rect(x - 1, y - 1, 13, 12, OUTLINE);
        rect(x, y, 11, 10, '#f8fafc');
        rect(x + 2, y + 2, 7, 2, '#ef4444');
        rect(x + 2, y + 5, 7, 1, '#334155');
        rect(x + 2, y + 7, 5, 1, '#334155');
        pixelText('BILL', x + 5, y - 7, '#ef4444', '#090d1f', 'center');
      },
    },
  });

  const EMBERS = (() => {
    const r = seeded(555);
    return Array.from({ length: 44 }, () => ({ x: r() * PW, y: r() * PH, sp: 20 + r() * 40, ph: r() * 6.28 }));
  })();

  let BEATS = [], SUB_CHUNKS = [];
  function init(bd) { BEATS = bd.beats || []; SUB_CHUNKS = buildSubtitleChunks(BEATS); window.CORE_READY = true; }

  function bgNightStreet(t, flashBright = false) {
    if (flashBright) {
      // Blinded neighborhood at midnight by the solar thermos!
      ditherGradV(0, 0, PW, 195, ['#fef08a', '#fde047', '#fb923c']);
    } else {
      ditherGradV(0, 0, PW, 195, ['#030712', '#0f172a', '#1e1b4b']);
      for (const e of EMBERS) px(e.x, e.y % 150, '#ffffff');
      disk(146, 52, 8, '#e2e8f0');
    }
    rect(8, 142, 36, 30, flashBright ? '#fef3c7' : '#1e293b');
    rect(6, 134, 40, 8, '#ef4444');
    rect(136, 138, 36, 34, flashBright ? '#fef3c7' : '#334155');
    rect(134, 130, 40, 8, '#2563eb');
    // House windows lit up angry!
    if (flashBright) {
      rect(14, 150, 8, 8, '#fde047'); rect(144, 148, 8, 8, '#fde047');
    }
    ditherBand(0, 170, PW, 16, '#15803d', '#14532d', 0.4);
    rect(0, 186, PW, 14, '#64748b');
    ditherGradV(0, 200, PW, 120, ['#334155', '#1e293b', '#0f172a']);
    for (let x = 8; x < PW; x += 28) rect(x, 224, 14, 3, '#facc15');
  }

  function bgSolarSurface(t, deepCore = false) {
    ditherGradV(0, 0, PW, 198, deepCore ? ['#450a0a', '#9a3412', '#ea580c'] : ['#05020d', '#450a0a', '#9a3412']);
    // Giant glowing Sun hemisphere above characters!
    glowOrb(90, 96, 32, '#fef9c3', '#fde047', '#ea580c');
    // Rising solar flare plasma arcs
    ditherGradV(0, 196, PW, 124, ['#f97316', '#ea580c', '#dc2626']);
    for (const e of EMBERS) {
      const ex = (e.x + Math.sin(t * 4 + e.ph) * 6 + PW) % PW;
      const ey = (210 - ((t * e.sp + e.y) % 160));
      px(ex, ey, '#fef08a');
    }
    if (deepCore) {
      // Bouncing photon zigzag path inside Sun's basement!
      for (let i = 0; i < 6; i++) {
        line(20 + i * 25, 90 + (i % 2) * 35, 45 + i * 25, 90 + ((i + 1) % 2) * 35, '#ffffff');
      }
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

    const k1 = kickOffset(t, BEATS[5]?.start || 13, 5);
    const k2 = kickOffset(t, BEATS[12]?.start || 36, 7);
    const k3 = kickOffset(t, BEATS[13]?.start || 38, 6);
    camX += k1.x + k2.x + k3.x; camY += k1.y + k2.y + k3.y; camRot += k1.rot + k2.rot + k3.rot;

    pctx.clearRect(0, 0, PW, PH);

    if (bi === 0 || bi === 1) {
      bgNightStreet(t, false);
      drawHudPill('OFFER:', '$1,000', 90, 26, '#4ade80');
      drawBall({ role: 'host', cx: 42, cy: 180, R: 19, expr: blinkExpr('normal', t, 1), lookX: 1, isTalking: isSpeaking(BEATS, 'host', t), t, outfit: 'host_hoodie', hat: 'host_cap', prop: 'cash_1k', propSide: 1 });
      drawBall({ role: 'mrbeast', cx: 138, cy: 180, R: 19, expr: blinkExpr('squint', t, 2), lookX: -1, isTalking: isSpeaking(BEATS, 'mrbeast', t), t, outfit: 'mrbeast_hoodie', hat: 'mrbeast_hair' });
    } else if (bi === 2 || bi === 3) {
      bgNightStreet(t, false);
      drawHudPill('OFFER:', '$2,000', 90, 26, '#facc15');
      drawBall({ role: 'host', cx: 42, cy: 180, R: 19, expr: blinkExpr('normal', t, 1), lookX: 1, isTalking: isSpeaking(BEATS, 'host', t), t, outfit: 'host_hoodie', hat: 'host_cap', prop: 'cash_2k', propSide: 1 });
      drawBall({ role: 'mc', cx: 138, cy: 180, R: 19, expr: bi === 3 ? 'cool_shades' : blinkExpr('wide', t, 3), lookX: -1, isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'mc_foil', hat: 'mc_hair' });
    } else if (bi === 4) {
      bgSolarSurface(t, false);
      drawHudPill('TIME:', 'MIDNIGHT?!', 90, 26, '#fde047');
      drawBall({ role: 'mc', cx: 90, cy: 182, R: 20, expr: 'cool_shades', isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'mc_foil', hat: 'mc_hair', sweat: true });
    } else if (bi === 5 || bi === 6) {
      bgSolarSurface(t, false);
      drawHudPill('TEMP:', '5,500°C', 90, 26, '#fb923c');
      drawBall({ role: 'mc', cx: 52, cy: 182, R: 19, expr: 'cool_shades', lookX: 1, isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'mc_foil', hat: 'mc_hair', sweat: true });
      drawBall({ role: 'flare', cx: 130, cy: 182, R: 20, expr: 'angry', lookX: -1, isTalking: isSpeaking(BEATS, 'flare', t), t, outfit: 'flare_armor', hat: 'flame_crown' });
    } else if (bi === 7 || bi === 8) {
      bgSolarSurface(t, false);
      drawHudPill('CORE:', '15,000,000°C', 90, 26, '#ef4444');
      drawBall({ role: 'mc', cx: 90, cy: 182, R: 21, expr: 'wide', isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'mc_foil', hat: 'mc_hair', prop: 'thermos', propSide: 1, sweat: true });
    } else if (bi === 9 || bi === 10 || bi === 11) {
      bgSolarSurface(t, true);
      drawHudPill('PHOTON:', '100,000 YRS', 90, 26, '#fde047');
      drawBall({ role: 'mc', cx: 48, cy: 182, R: 19, expr: bi === 10 ? 'dollar' : 'cool_shades', lookX: 1, isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'mc_foil', hat: 'mc_hair', prop: 'thermos', propSide: 1 });
      drawBall({ role: 'photon', cx: 130, cy: 182, R: 19, expr: bi === 11 ? 'wide' : blinkExpr('normal', t, 4), lookX: -1, isTalking: isSpeaking(BEATS, 'photon', t), t, outfit: 'photon_robe', hat: 'sage_wizard', glasses: true, beard: true, sweat: bi === 11 });
    } else if (bi === 12) {
      bgSolarSurface(t, true);
      drawHudPill('SLAP:', 'HIGH FIVE!', 90, 26, '#4ade80');
      drawBall({ role: 'mc', cx: 90, cy: 176, R: 22, expr: 'dollar', isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'mc_foil', hat: 'mc_hair', prop: 'sun_thermos', propSide: 1 });
    } else {
      bgNightStreet(t, true);
      const isBill = bi === 15 && u > 0.56;
      drawHudPill('PAYOUT:', isBill ? '$0.01' : '$2,000', 90, 26, isBill ? '#ef4444' : '#4ade80');
      drawBall({ role: 'mc', cx: 44, cy: 182, R: 19, expr: isBill ? 'wide' : 'cool_shades', lookX: 1, isTalking: isSpeaking(BEATS, 'mc', t), t, outfit: 'mc_foil', hat: 'mc_hair', prop: 'sun_thermos', propSide: 1, sweat: isBill });
      drawBall({ role: 'host', cx: 136, cy: 182, R: 19, expr: blinkExpr('angry', t, 1), lookX: -1, isTalking: isSpeaking(BEATS, 'host', t), t, outfit: 'host_hoodie', hat: 'host_cap', prop: isBill ? 'electric_bill' : 'cash_2k', propSide: -1 });
    }

    presentFrame(ctx, c.width, c.height, camX, camY, camRot, camZoom, SUB_CHUNKS, t);
  }

  window.renderFrame = renderFrame;
  window.initCoreShort = init;
})();
