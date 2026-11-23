/* 5 Billionaires Build Superintelligence for $1 Trillion — 180x320 Pixel Countryball Short */
window.SHORT_APP = (() => {
  const {
    PW, PH, pctx, px, rect, line, ditherBand, ditherGradV, disk, ellipse, glowOrb,
    pixelText, drawHudPill, buildSubtitleChunks, presentFrame, kickOffset, blinkExpr, isSpeaking, activeBeatIndex, seeded,
  } = window.PX;
  const { drawBall, register, OUTLINE, bayerPick } = window.CHARS;

  register({
    skins: {
      sam:    { hi: '#fde5cc', lit: '#f5cba7', shade: '#d49d74' },
      jensen: { hi: '#fae0c3', lit: '#ecc196', shade: '#c28e5c' },
      elon:   { hi: '#fde2c4', lit: '#f2c29b', shade: '#ce9268' },
      zuck:   { hi: '#fef0e4', lit: '#f5d0b5', shade: '#cfa284' },
      dario:  { hi: '#f6d2ad', lit: '#dfa875', shade: '#b37a49' },
      llama:  { hi: '#ffffff', lit: '#e2e8f0', shade: '#94a3b8' },
    },
    outfits: {
      sam_blazer: (dx, dy, R, x, y, shade) => {
        if (Math.abs(dx) <= 2 && dy < R * 0.55) return '#f8fafc';
        if (dx >= 2 && dx <= 5 && dy >= R * 0.36 && dy <= R * 0.56) return '#2dd4bf';
        return shade ? '#0f172a' : '#1e293b';
      },
      jensen_leather: (dx, dy, R, x, y, shade) => {
        if (Math.abs(dx) <= 1 && dy < R * 0.50) return '#76b900';
        // Iconic diagonal silver zipper
        if (Math.abs(dx - Math.round((dy - R * 0.25) * 0.45)) <= 0 && dy > R * 0.24) return '#cbd5e1';
        return shade ? '#09090b' : ((x + y) & 3 ? '#18181b' : '#27272a');
      },
      elon_jacket: (dx, dy, R, x, y, shade) => {
        // White X logo on chest
        if (dy >= R * 0.34 && dy <= R * 0.68 && Math.abs(dx) <= 3) {
          const cy0 = Math.round(R * 0.50);
          if (Math.abs(Math.abs(dx) - Math.abs(dy - cy0)) <= 0) return '#ffffff';
        }
        return shade ? '#090d16' : '#18181b';
      },
      zuck_chain: (dx, dy, R, x, y, shade) => {
        // Gold chain necklace
        if (dy >= R * 0.24 && dy <= R * 0.42 && Math.abs(dx) <= 5) {
          if (Math.abs(dy - Math.round(R * 0.36 - Math.abs(dx) * 0.35)) <= 0) return '#facc15';
        }
        if (dx >= 3 && dx <= 5 && dy >= R * 0.48 && dy <= R * 0.60) return '#38bdf8';
        return shade ? '#111827' : '#1f2937';
      },
      dario_cardigan: (dx, dy, R, x, y, shade) => {
        if (Math.abs(dx) <= 2 && dy < R * 0.65) return '#f8fafc';
        // Claude starburst pin
        if (dx >= 3 && dx <= 5 && dy >= R * 0.38 && dy <= R * 0.52) return '#f59e0b';
        return shade ? '#9a3412' : '#d97757';
      },
    },
    hats: {
      sam_hair: (cx, cy, R) => {
        const top = Math.round(cy - R - 1);
        rect(cx - Math.round(R * 0.7), top, Math.round(R * 1.4), 4, '#6b4f3a');
        rect(cx - Math.round(R * 0.4), top - 2, Math.round(R * 0.9), 3, '#8c6b52');
      },
      jensen_hair: (cx, cy, R) => {
        const top = Math.round(cy - R - 1);
        rect(cx - Math.round(R * 0.72), top, Math.round(R * 1.44), 4, '#cbd5e1');
        rect(cx - Math.round(R * 0.55), top - 2, Math.round(R * 1.1), 2, '#e2e8f0');
      },
      elon_hair: (cx, cy, R) => {
        const top = Math.round(cy - R - 1);
        rect(cx - Math.round(R * 0.68), top, Math.round(R * 1.36), 4, '#3f2a1d');
        rect(cx - 4, top - 2, 9, 2, '#543828');
      },
      zuck_curls: (cx, cy, R) => {
        const top = Math.round(cy - R - 2);
        for (let ox = -8; ox <= 8; ox += 4) {
          disk(cx + ox, top + 2 + (Math.abs(ox) >> 2), 4, '#7c4a2d');
        }
        disk(cx - 3, top, 4, '#925838');
        disk(cx + 3, top, 4, '#925838');
      },
      dario_curls: (cx, cy, R) => {
        const top = Math.round(cy - R - 2);
        for (let ox = -7; ox <= 7; ox += 3) {
          disk(cx + ox, top + 2, 3, '#291d18');
        }
        rect(cx - 6, top, 13, 3, '#3b2922');
      },
    },
    props: {
      trillion_case: (x, y) => {
        rect(x - 1, y - 1, 16, 11, OUTLINE);
        rect(x + 4, y - 3, 6, 2, '#facc15');
        rect(x, y, 14, 9, '#eab308');
        rect(x + 1, y + 1, 12, 7, '#22c55e');
        pixelText('$1T', x + 7, y + 2, '#ffffff', '#052e16', 'center');
      },
      gpu_brick: (x, y, t) => {
        rect(x - 1, y - 2, 13, 12, OUTLINE);
        rect(x, y - 1, 11, 10, '#1e293b');
        const pulse = Math.floor(t * 8) % 2;
        rect(x + 1, y + 1, 9, 2, pulse ? '#76b900' : '#a3e635');
        rect(x + 1, y + 5, 9, 2, '#76b900');
      },
      claude_book: (x, y) => {
        rect(x - 1, y - 2, 12, 13, OUTLINE);
        rect(x, y - 1, 10, 11, '#d97757');
        rect(x + 1, y + 1, 8, 2, '#fef3c7');
        rect(x + 1, y + 5, 6, 1, '#fef3c7');
        rect(x + 1, y + 7, 7, 1, '#fef3c7');
      },
      soot_puff: (x, y, t) => {
        disk(x + 4, y + 2 - Math.round((t * 6) % 3), 3, '#64748b');
        disk(x + 7, y + 4, 2, '#94a3b8');
      },
    },
  });

  const STARS = (() => {
    const r = seeded(2026);
    return Array.from({ length: 40 }, () => ({ x: Math.floor(r() * PW), y: Math.floor(r() * 165), ph: r() * 6.28 }));
  })();

  let BEATS = [], SUB_CHUNKS = [];
  function init(bd) { BEATS = bd.beats || []; SUB_CHUNKS = buildSubtitleChunks(BEATS); window.CORE_READY = true; }

  function bgArena(t, prizeCol = '#facc15') {
    ditherGradV(0, 0, PW, 198, ['#040614', '#131836', '#1e1b4b']);
    for (const s of STARS) if (Math.sin(t * 3 + s.ph) > -0.3) px(s.x, s.y, '#38bdf8');
    // Big AI Arena Vault Arch
    rect(16, 48, 148, 126, '#0f172a');
    rect(18, 50, 144, 122, '#1e1b4b');
    rect(26, 56, 128, 26, '#090d1f');
    rect(27, 57, 126, 24, '#111827');
    pixelText('SUPER AI RACE', 90, 61, '#38bdf8', '#050814', 'center');
    pixelText('PRIZE: $1 TRILLION', 90, 70, prizeCol, '#050814', 'center');
    // Spotlight cones
    ditherBand(20, 84, 140, 88, '#1e1b4b', '#312e81', 0.35);
    // Floor
    rect(0, 174, PW, 12, '#334155');
    ditherGradV(0, 186, PW, 134, ['#1e293b', '#0f172a', '#020617']);
    for (let x = 6; x < PW; x += 24) rect(x, 206, 12, 2, '#38bdf8');
  }

  function bgServerLab(t, accent = '#2dd4bf', catMeme = false) {
    ditherGradV(0, 0, PW, 186, ['#050814', '#0f172a', '#172554']);
    // 3 server racks
    for (const rx of [16, 132]) {
      rect(rx, 64, 32, 114, '#090d1f');
      rect(rx + 2, 66, 28, 110, '#1e293b');
      for (let ry = 72; ry < 168; ry += 12) {
        rect(rx + 5, ry, 22, 6, '#0f172a');
        const on = ((ry + Math.floor(t * 9)) % 3) !== 0;
        rect(rx + 7, ry + 2, 4, 2, on ? accent : '#475569');
        rect(rx + 14, ry + 2, 8, 2, catMeme ? '#f472b6' : '#38bdf8');
      }
    }
    // Center monitor
    rect(54, 58, 72, 54, '#090d1f');
    rect(57, 61, 66, 48, catMeme ? '#4c0519' : '#042f2e');
    if (catMeme) {
      // Cute 8-bit Cat face on screen!
      rect(79, 72, 22, 18, '#fb923c');
      rect(79, 67, 5, 5, '#fb923c'); rect(96, 67, 5, 5, '#fb923c');
      rect(83, 77, 3, 3, '#090d1f'); rect(94, 77, 3, 3, '#090d1f');
      rect(88, 82, 4, 2, '#f472b6');
      pixelText('MEOW.JPG', 90, 96, '#fde047', '#090d1f', 'center');
    } else {
      pixelText('GPT-10', 90, 70, '#2dd4bf', '#042f2e', 'center');
      const barW = Math.min(54, 12 + Math.floor((t * 36) % 52));
      rect(63, 84, 54, 8, '#0f172a');
      rect(64, 85, barW, 6, '#2dd4bf');
      pixelText('TRAINING', 90, 97, '#f8fafc', '#042f2e', 'center');
    }
    rect(0, 178, PW, 10, '#334155');
    ditherGradV(0, 188, PW, 132, ['#1e293b', '#0f172a', '#020617']);
  }

  function bgGpuMeltdown(t, melted = false) {
    ditherGradV(0, 0, PW, 184, melted ? ['#1c0404', '#450a0a', '#7f1d1d'] : ['#051408', '#0f2912', '#14532d']);
    // Giant NVIDIA GPU monolith
    const sink = melted ? Math.min(48, Math.floor((t % 3) * 18)) : 0;
    const gx = 96, gy = 66 + sink;
    if (gy < 176) {
      const h = Math.min(110, 178 - gy);
      rect(gx, gy, 54, h, OUTLINE);
      rect(gx + 2, gy + 2, 50, Math.max(2, h - 4), '#18181b');
      for (let ry = gy + 8; ry < gy + h - 8; ry += 14) {
        rect(gx + 6, ry, 42, 6, melted ? '#ef4444' : '#76b900');
      }
      if (h > 18) pixelText(melted ? 'HOT!' : '1M GPU', gx + 27, gy + 6, '#ffffff', '#09090b', 'center');
    }
    if (melted) {
      // Glowing lava puddle on floor!
      ellipse(123, 182, 42, 7, '#dc2626');
      ellipse(123, 182, 28, 4, '#facc15');
      for (let i = 0; i < 6; i++) {
        const sx = 96 + ((i * 11 + Math.floor(t * 25)) % 52);
        const sy = 174 - ((Math.floor(t * 38) + i * 9) % 36);
        px(sx, sy, '#fde047');
      }
    }
    rect(0, 178, PW, 10, melted ? '#7f1d1d' : '#1e293b');
    ditherGradV(0, 188, PW, 132, ['#1e293b', '#0f172a', '#020617']);
  }

  function bgSpaceLaunch(t, crash = false, u = 0) {
    ditherGradV(0, 0, PW, 194, ['#02040e', '#0c1438', '#1e1b4b']);
    for (const s of STARS) px(s.x, s.y, '#ffffff');
    // Pixel Moon top right!
    const mx = 136, my = 86;
    disk(mx, my, 20, '#cbd5e1');
    disk(mx - 6, my - 5, 4, '#94a3b8');
    disk(mx + 5, my + 4, 5, '#94a3b8');

    if (!crash) {
      // Rocket launching upright on left-center!
      const ry = 138 - Math.round((t * 28) % 36);
      rect(112, ry, 14, 34, '#f8fafc');
      rect(114, ry - 6, 10, 6, '#e2e8f0');
      rect(117, ry - 10, 4, 4, '#ef4444');
      pixelText('X', 119, ry + 12, '#090d1f', null, 'center');
      // Exhaust flame
      rect(114, ry + 34, 10, 10 + (Math.floor(t * 16) % 5), '#f97316');
      rect(116, ry + 34, 6, 6, '#fde047');
    } else {
      // Sideways crash into the Moon + KABOOM!
      if (u < 0.45) {
        const rx = Math.round(70 + u * 110);
        const ry = Math.round(126 - u * 80);
        rect(rx, ry, 24, 10, '#f8fafc');
        rect(rx + 24, ry + 2, 6, 6, '#ef4444');
        rect(rx - 10, ry + 2, 10, 6, '#f97316');
      } else {
        const r = 12 + Math.round((u - 0.45) * 34);
        glowOrb(mx - 6, my + 2, Math.min(24, r), '#ffffff', '#fde047', '#ef4444');
        pixelText('KABOOM!', mx - 6, my - 26, '#fde047', '#450a0a', 'center');
      }
    }
    rect(0, 178, PW, 10, '#334155');
    ditherGradV(0, 188, PW, 132, ['#1e293b', '#0f172a', '#020617']);
  }

  function bgToastBots(t) {
    ditherGradV(0, 0, PW, 184, ['#071226', '#1e3a8a', '#1e1b4b']);
    // Digital Llama bot swarm arguing about TOAST!
    const botXs = [26, 64, 118, 150];
    botXs.forEach((bx, idx) => {
      const by = 92 + (idx % 2) * 26 + Math.round(Math.abs(Math.sin(t * 8 + idx)) * -8);
      rect(bx - 8, by, 16, 12, OUTLINE);
      rect(bx - 7, by + 1, 14, 10, '#f8fafc');
      rect(bx - 5, by - 4, 3, 4, '#f8fafc'); rect(bx + 2, by - 4, 3, 4, '#f8fafc');
      rect(bx - 4, by + 4, 2, 2, '#090d1f'); rect(bx + 2, by + 4, 2, 2, '#090d1f');
      // Speech bubble TOAST!
      rect(bx - 13, by - 17, 26, 10, '#ffffff');
      pixelText(idx % 2 === 0 ? 'TOAST' : 'BREAD', bx, by - 14, '#dc2626', null, 'center');
    });
    rect(0, 178, PW, 10, '#334155');
    ditherGradV(0, 188, PW, 132, ['#1e293b', '#0f172a', '#020617']);
  }

  function bgClaudeSanctuary(t, refused = false) {
    ditherGradV(0, 0, PW, 184, ['#1f1209', '#431407', '#7c2d12']);
    // Claude Sunburst Halo Screen
    const cx = 126, cy = 96;
    rect(92, 62, 68, 56, OUTLINE);
    rect(94, 64, 64, 52, refused ? '#450a0a' : '#29170b');
    if (!refused) {
      glowOrb(cx, cy - 8, 9, '#fef3c7', '#f59e0b', '#d97757');
      pixelText('ETHICS: 100%', cx, 104, '#4ade80', '#090d1f', 'center');
    } else {
      pixelText('SORRY!', cx, 74, '#f87171', '#090d1f', 'center');
      pixelText('I CANNOT', cx, 86, '#ffffff', '#090d1f', 'center');
      pixelText('THINK!', cx, 96, '#facc15', '#090d1f', 'center');
    }
    rect(0, 178, PW, 10, '#78350f');
    ditherGradV(0, 188, PW, 132, ['#29170b', '#1c1008', '#090d1f']);
  }

  function bgJetToaster(t) {
    ditherGradV(0, 0, PW, 190, ['#020617', '#1e1b4b', '#312e81']);
    for (const s of STARS) px(s.x, s.y, '#38bdf8');
    // Flying chrome pixel toaster with green GPUs + huge jet flames (positioned cleanly above Host!)
    const bob = Math.round(Math.sin(t * 14) * 3);
    const tx = 86, ty = 88 + bob;
    // Left & right GPU jet pods
    rect(tx - 16, ty + 6, 14, 18, OUTLINE); rect(tx - 15, ty + 7, 12, 16, '#76b900');
    rect(tx + 50, ty + 6, 14, 18, OUTLINE); rect(tx + 51, ty + 7, 12, 16, '#76b900');
    // Jet exhaust flames
    const fl = 12 + (Math.floor(t * 24) % 8);
    rect(tx - 13, ty + 24, 8, fl, '#f97316'); rect(tx - 11, ty + 24, 4, fl - 4, '#fde047');
    rect(tx + 53, ty + 24, 8, fl, '#f97316'); rect(tx + 55, ty + 24, 4, fl - 4, '#fde047');
    // Chrome toaster body
    rect(tx, ty, 48, 30, OUTLINE);
    rect(tx + 2, ty + 2, 44, 26, '#e2e8f0');
    rect(tx + 4, ty + 4, 40, 10, '#f8fafc');
    // Burnt toast popping out the top!
    rect(tx + 12, ty - 14 - Math.round(Math.abs(Math.sin(t * 7)) * 6), 24, 14, '#78350f');
    rect(tx + 14, ty - 12 - Math.round(Math.abs(Math.sin(t * 7)) * 6), 20, 10, '#451a03');
    pixelText('10B GPUS', tx + 24, ty + 16, '#090d1f', null, 'center');
    rect(0, 178, PW, 10, '#334155');
    ditherGradV(0, 188, PW, 132, ['#1e293b', '#0f172a', '#020617']);
  }

  function renderFrame(t) {
    const c = document.getElementById('c');
    const ctx = c.getContext('2d');
    const bi = activeBeatIndex(BEATS, t);
    const beat = BEATS[bi] || { start: 0, end: 3, speaker: 'host' };
    const u = Math.min(1, Math.max(0, (t - beat.start) / Math.max(0.1, beat.end - beat.start)));

    // Continuous rapid camera motion & punch-ins (never crop HUD pill or edge characters!)
    let camZoom = 1.01 + u * 0.05, camX = 0, camY = 0, camRot = 0;
    if (bi === 0 && u > 0.5) { camZoom = 1.06 + (u - 0.5) * 0.06; camY = -2; }
    if (bi === 1) { camZoom = 1.06 + u * 0.06; camX = 4; camY = 2; }
    if (bi === 2) { camZoom = 1.08 + u * 0.05; camX = 4; camRot = -0.02; }
    if (bi === 3) { camZoom = 1.06 + u * 0.06; camX = 4; camY = 2; }
    if (bi === 4) { camZoom = 1.09 + u * 0.06; camX = 4; camRot = 0.025; }
    if (bi === 5) { camZoom = 1.06 + u * 0.06; camX = 4; }
    if (bi === 6) { camZoom = u > 0.45 ? 1.11 + (u - 0.45) * 0.06 : 1.05 + u * 0.05; camRot = u > 0.45 ? -0.035 : 0.02; }
    if (bi === 7) { camZoom = 1.06 + u * 0.06; camRot = Math.sin(t * 10) * 0.02; }
    if (bi === 8) { camZoom = 1.06 + u * 0.05; camX = 4; }
    if (bi === 9) { camZoom = u > 0.48 ? 1.10 + (u - 0.48) * 0.06 : 1.05 + u * 0.04; camX = 4; }
    if (bi === 10) { camZoom = 1.04 + u * 0.06; camY = -2; }
    if (bi === 11) { camZoom = 1.02 + u * 0.05; camY = 3; }
    if (bi === 12) { camZoom = u > 0.40 ? 1.04 + (u - 0.40) * 0.03 : 1.01 + u * 0.03; camX = 0; }

    // 7-frame impact KICKS on explosions & final reveal
    const k1 = kickOffset(t, (BEATS[4]?.start || 12) + 0.35, 5);
    const k2 = kickOffset(t, (BEATS[6]?.start || 18) + (BEATS[6]?.end - BEATS[6]?.start) * 0.45, 7);
    const k3 = kickOffset(t, BEATS[12]?.start || 36, 6);
    camX += k1.x + k2.x + k3.x; camY += k1.y + k2.y + k3.y; camRot += k1.rot + k2.rot + k3.rot;

    pctx.clearRect(0, 0, PW, PH);

    if (bi === 0) {
      bgArena(t, '#4ade80');
      drawHudPill('PRIZE:', '$1,000,000,000,000', 90, 32, '#4ade80');
      // All 5 billionaires lined up across the arena!
      drawBall({ role: 'sam', cx: 26, cy: 174, R: 13, expr: blinkExpr('normal', t, 1), isTalking: false, t, outfit: 'sam_blazer', hat: 'sam_hair' });
      drawBall({ role: 'jensen', cx: 56, cy: 174, R: 13, expr: blinkExpr('squint', t, 2), isTalking: false, t, outfit: 'jensen_leather', hat: 'jensen_hair', glasses: true });
      drawBall({ role: 'elon', cx: 88, cy: 174, R: 13, expr: blinkExpr('normal', t, 3), isTalking: false, t, outfit: 'elon_jacket', hat: 'elon_hair' });
      drawBall({ role: 'zuck', cx: 120, cy: 174, R: 13, expr: blinkExpr('wide', t, 4), isTalking: false, t, outfit: 'zuck_chain', hat: 'zuck_curls' });
      drawBall({ role: 'dario', cx: 152, cy: 174, R: 13, expr: blinkExpr('normal', t, 5), isTalking: false, t, outfit: 'dario_cardigan', hat: 'dario_curls', glasses: true });
      drawBall({ role: 'host', cx: 90, cy: 130, R: 15, expr: 'dollar', isTalking: isSpeaking(BEATS, 'host', t), t, outfit: 'host_hoodie', hat: 'host_cap', prop: 'trillion_case', propSide: 1 });
    } else if (bi === 1 || bi === 2) {
      const cat = bi === 2;
      bgServerLab(t, '#2dd4bf', cat);
      drawHudPill('SAM:', cat ? 'CAT MEMES?!' : 'GPT-10', 90, 32, cat ? '#f472b6' : '#2dd4bf');
      drawBall({ role: 'sam', cx: 88, cy: 174, R: 20, expr: cat ? 'wide' : blinkExpr('normal', t, 1), lookX: cat ? 0 : 1, isTalking: isSpeaking(BEATS, 'sam', t), t, outfit: 'sam_blazer', hat: 'sam_hair', sweat: cat });
    } else if (bi === 3 || bi === 4) {
      const melted = bi === 4;
      bgGpuMeltdown(t, melted);
      drawHudPill('JENSEN:', melted ? 'MELTDOWN!' : '1M GPUS', 90, 32, melted ? '#ef4444' : '#76b900');
      drawBall({ role: 'jensen', cx: 52, cy: 174, R: 20, expr: melted ? 'wide' : 'cool_shades', lookX: 1, isTalking: isSpeaking(BEATS, 'jensen', t), t, outfit: 'jensen_leather', hat: 'jensen_hair', glasses: !melted, prop: 'gpu_brick', propSide: 1, sweat: melted });
    } else if (bi === 5 || bi === 6) {
      const crash = bi === 6;
      bgSpaceLaunch(t, crash, u);
      drawHudPill('ELON:', crash && u > 0.45 ? 'MOON CRASH!' : 'GROK ROCKET', 90, 32, crash ? '#ef4444' : '#38bdf8');
      drawBall({ role: 'elon', cx: 48, cy: 174, R: 20, expr: crash && u > 0.4 ? 'dizzy' : blinkExpr('wide', t, 3), lookX: 1, isTalking: isSpeaking(BEATS, 'elon', t), t, outfit: 'elon_jacket', hat: 'elon_hair', sweat: crash });
    } else if (bi === 7) {
      bgToastBots(t);
      drawHudPill('ZUCK:', 'LLAMA SWARM', 90, 32, '#38bdf8');
      drawBall({ role: 'zuck', cx: 90, cy: 174, R: 20, expr: u > 0.5 ? 'wide' : blinkExpr('squint', t, 4), isTalking: isSpeaking(BEATS, 'zuck', t), t, outfit: 'zuck_chain', hat: 'zuck_curls', sweat: u > 0.45 });
    } else if (bi === 8 || bi === 9) {
      const refused = bi === 9 && u > 0.48;
      bgClaudeSanctuary(t, refused);
      drawHudPill('DARIO:', refused ? 'REFUSED!' : 'CLAUDE SAFE', 90, 32, refused ? '#f87171' : '#f59e0b');
      drawBall({ role: 'dario', cx: 50, cy: 174, R: 20, expr: refused ? 'dizzy' : blinkExpr('normal', t, 5), lookX: 1, isTalking: isSpeaking(BEATS, 'dario', t), t, outfit: 'dario_cardigan', hat: 'dario_curls', glasses: true, prop: 'claude_book', propSide: 1, sweat: refused });
    } else if (bi === 10) {
      bgJetToaster(t);
      drawHudPill('PHYSICS:', 'BAD CODE!', 90, 32, '#facc15');
      drawBall({ role: 'host', cx: 36, cy: 176, R: 17, expr: blinkExpr('squint', t, 1), lookX: 1, isTalking: isSpeaking(BEATS, 'host', t), t, outfit: 'host_hoodie', hat: 'host_cap' });
    } else if (bi === 11) {
      bgArena(t, '#ef4444');
      drawHudPill('RESULTS:', 'ALL FAILED!', 90, 32, '#ef4444');
      drawBall({ role: 'sam', cx: 26, cy: 178, R: 13, expr: 'angry', lookX: 1, isTalking: isSpeaking(BEATS, 'sam', t), t, outfit: 'sam_blazer', hat: 'sam_hair', prop: 'soot_puff', propSide: 1 });
      drawBall({ role: 'jensen', cx: 56, cy: 178, R: 13, expr: 'blink', isTalking: false, t, outfit: 'jensen_leather', hat: 'jensen_hair', glasses: true });
      drawBall({ role: 'elon', cx: 88, cy: 178, R: 13, expr: 'dizzy', isTalking: false, t, outfit: 'elon_jacket', hat: 'elon_hair' });
      drawBall({ role: 'zuck', cx: 120, cy: 178, R: 13, expr: 'wide', isTalking: false, t, outfit: 'zuck_chain', hat: 'zuck_curls', sweat: true });
      drawBall({ role: 'dario', cx: 152, cy: 178, R: 13, expr: 'squint', isTalking: false, t, outfit: 'dario_cardigan', hat: 'dario_curls', glasses: true });
    } else {
      bgArena(t, '#4ade80');
      drawHudPill('WINNER:', 'JENSEN ($1T)', 90, 32, '#4ade80');
      const handed = u > 0.35;
      drawBall({ role: 'host', cx: 30, cy: 176, R: 15, expr: blinkExpr('normal', t, 1), lookX: 1, isTalking: isSpeaking(BEATS, 'host', t), t, outfit: 'host_hoodie', hat: 'host_cap', prop: handed ? null : 'trillion_case', propSide: 1 });
      drawBall({ role: 'jensen', cx: 80, cy: 168, R: 19, expr: handed ? 'dollar' : 'cool_shades', isTalking: false, t, outfit: 'jensen_leather', hat: 'jensen_hair', prop: handed ? 'trillion_case' : 'gpu_brick', propSide: 1 });
      drawBall({ role: 'sam', cx: 138, cy: 180, R: 11, expr: 'angry', lookX: -1, isTalking: false, t, outfit: 'sam_blazer', hat: 'sam_hair' });
      drawBall({ role: 'elon', cx: 158, cy: 180, R: 11, expr: 'dizzy', lookX: -1, isTalking: false, t, outfit: 'elon_jacket', hat: 'elon_hair' });
    }

    presentFrame(ctx, c.width, c.height, camX, camY, camRot, camZoom, SUB_CHUNKS, t);
  }

  window.renderFrame = renderFrame;
  window.initCoreShort = init;
})();
