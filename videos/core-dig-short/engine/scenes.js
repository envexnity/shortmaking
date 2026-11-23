/* Core Dig Short — 180x320 Pixel-Art Scenes + 1080x1920 Black-Pill Subtitles
 * Driven deterministically by beats.json (ElevenLabs + Whisper word timestamps).
 */
window.CORE_SHORT = (() => {
  const { PW, PH, SCALE, pCanvas, pctx, px, rect, ditherBand, ditherGradV, disk, glowOrb, pixelText, drawHudPill, drawSubtitlePill } = window.PX;
  const { drawBall } = window.CHARS;

  let BEATS = [];
  let ALL_WORDS = [];
  let TOTAL = 35.4;

  // Deterministic seeded RNG for stars, particles, rocks, snowflakes
  function seeded(seed) {
    let s = seed | 0 || 12345;
    return () => {
      s = (s * 1664525 + 1013904223) | 0;
      return (s >>> 0) / 4294967296;
    };
  }

  const PARTICLES = (() => {
    const r = seeded(777);
    return Array.from({ length: 48 }, () => ({
      x: r() * PW,
      y: r() * PH,
      vx: (r() - 0.5) * 18,
      vy: 12 + r() * 28,
      s: r() < 0.7 ? 1 : 2,
      phase: r() * 6.28,
    }));
  })();

  // Group Whisper words into 2-4 word black-pill chunks
  function buildSubtitleChunks(beats) {
    const chunks = [];
    for (const b of beats) {
      const ws = b.words || [];
      let cur = [];
      for (let i = 0; i < ws.length; i++) {
        cur.push(ws[i]);
        const txt = cur.map((x) => x.w).join(' ');
        const endsSentence = /[.?!,—]$/.test(ws[i].w);
        if (cur.length >= 3 || (cur.length >= 2 && (txt.length > 15 || endsSentence)) || i === ws.length - 1) {
          chunks.push({
            start: cur[0].start,
            end: cur[cur.length - 1].end + 0.10,
            words: cur,
          });
          cur = [];
        }
      }
    }
    return chunks;
  }

  let SUB_CHUNKS = [];

  function init(beatsData) {
    BEATS = beatsData.beats || [];
    TOTAL = beatsData.total || 35.4;
    ALL_WORDS = BEATS.flatMap((b) => b.words || []);
    SUB_CHUNKS = buildSubtitleChunks(BEATS);
    window.CORE_TOTAL = TOTAL;
    window.CORE_READY = true;
  }

  function isSpeaking(speaker, t) {
    for (const b of BEATS) {
      if (b.speaker !== speaker) continue;
      if (t >= b.start && t <= b.speechEnd) {
        // Gate by active word intervals if available
        for (const w of b.words || []) {
          if (t >= w.start - 0.03 && t <= w.end + 0.04) return true;
        }
      }
    }
    return false;
  }

  function activeBeatIndex(t) {
    if (!BEATS.length || t < BEATS[0].start) return 0;
    for (let i = 0; i < BEATS.length; i++) {
      if (t >= BEATS[i].start && t < BEATS[i].end) return i;
    }
    return BEATS.length - 1;
  }

  function blinkExpr(baseExpr, t, seed = 0) {
    // 4-frame (0.13s) blink every ~1.35s
    const cycle = (t + seed * 0.47) % 1.35;
    if (cycle > 1.22 && baseExpr !== 'sleepy' && baseExpr !== 'shiver') return 'blink';
    return baseExpr;
  }

  // Deterministic 7-frame alternating-sign impact kick
  function kickOffset(t, tImpact, ampPx = 5) {
    const f = Math.round((t - tImpact) * 30);
    if (f < 0 || f >= 7) return { x: 0, y: 0, rot: 0 };
    const decay = 1 - f / 7;
    const sign = f % 2 === 0 ? 1 : -1;
    return {
      x: sign * ampPx * 0.4 * decay,
      y: sign * ampPx * decay,
      rot: sign * 0.024 * decay,
    };
  }

  // Background painters (all 180x320)
  function bgStreet(t, snowy = false) {
    if (snowy) {
      ditherGradV(0, 0, PW, 195, ['#0f172a', '#1e293b', '#475569']);
      // Drifting pixel snow clouds
      for (let i = 0; i < 4; i++) {
        const cx = ((i * 52 + t * 8) % (PW + 40)) - 20;
        const cy = 48 + (i % 2) * 16;
        rect(cx, cy, 32, 8, '#64748b');
        rect(cx + 6, cy - 4, 18, 5, '#94a3b8');
      }
      // Frozen bushes & snow-covered houses
      rect(0, 165, PW, 30, '#334155');
      rect(14, 145, 34, 24, '#1e293b');
      rect(12, 142, 38, 5, '#e2e8f0'); // snow roof
      rect(134, 140, 36, 28, '#1e293b');
      rect(132, 137, 40, 5, '#e2e8f0');
      // Snowy street
      ditherBand(0, 195, PW, 125, '#cbd5e1', '#94a3b8', 0.35);
      rect(0, 195, PW, 3, '#f8fafc');
      // Blowing snow particles
      for (const p of PARTICLES) {
        const sx = (p.x + t * 28 + Math.sin(t * 2 + p.phase) * 6) % PW;
        const sy = (p.y + t * p.vy * 1.4) % PH;
        rect(sx, sy, p.s, p.s, '#f8fafc');
      }
    } else {
      ditherGradV(0, 0, PW, 195, ['#1d4ed8', '#38bdf8', '#7dd3fc']);
      // Crisp pixel sun
      glowOrb(148, 52, 9, '#fef9c3', '#fde047', '#38bdf8');
      // Drifting pixel clouds
      for (let i = 0; i < 4; i++) {
        const cx = ((i * 56 + t * 6) % (PW + 45)) - 25;
        const cy = 54 + (i % 2) * 18;
        rect(cx, cy, 30, 8, '#ffffff');
        rect(cx + 5, cy - 4, 18, 4, '#f8fafc');
        rect(cx + 2, cy + 7, 26, 2, '#cbd5e1');
      }
      // Houses & green hedge
      rect(10, 144, 38, 28, '#cbd5e1');
      rect(8, 136, 42, 8, '#ef4444');
      rect(22, 154, 10, 18, '#78350f');
      rect(132, 140, 38, 32, '#fde68a');
      rect(130, 132, 42, 8, '#2563eb');
      // Green hedge + sidewalk + asphalt
      ditherBand(0, 168, PW, 18, '#16a34a', '#15803d', 0.4);
      rect(0, 186, PW, 16, '#94a3b8');
      rect(0, 202, PW, 118, '#334155');
      for (let x = 8; x < PW; x += 28) rect(x, 224, 14, 3, '#facc15');
    }
  }

  function bgBackyard(t) {
    ditherGradV(0, 0, PW, 185, ['#1e3a8a', '#3b82f6', '#93c5fd']);
    glowOrb(32, 56, 8, '#fef9c3', '#fde047', '#60a5fa');
    // Wooden fence
    for (let x = 0; x < PW; x += 12) {
      rect(x, 148, 10, 38, '#92400e');
      rect(x + 1, 148, 2, 38, '#b45309');
      rect(x, 146, 10, 2, '#78350f');
    }
    // Grass lawn
    ditherBand(0, 186, PW, 26, '#22c55e', '#16a34a', 0.45);
    // Underground cross-section below lawn!
    ditherGradV(0, 212, PW, 108, ['#78350f', '#451a03', '#1c1024']);
    // Pebble pixels
    for (let i = 0; i < 18; i++) {
      const p = PARTICLES[i];
      rect(p.x, 220 + (p.y % 90), 3, 2, '#92400e');
    }
  }

  function bgSewer(t) {
    ditherGradV(0, 0, PW, PH, ['#090d1f', '#10173a', '#06281e']);
    // Brick arch pattern
    for (let y = 55; y < 230; y += 10) {
      const off = ((y / 10) & 1) * 8;
      for (let x = -8; x < PW; x += 16) {
        rect(x + off, y, 14, 8, '#1e293b');
        rect(x + off, y, 14, 1, '#334155');
      }
    }
    // Dripping green pipe
    rect(0, 62, 56, 14, '#15803d');
    rect(48, 60, 10, 18, '#16a34a');
    const dripY = 78 + ((t * 55) % 140);
    rect(52, dripY, 2, 5, '#4ade80');
    // Hole in ceiling where MC fell through!
    rect(68, 0, 44, 64, '#050814');
    // Brick walkway + toxic green canal at bottom
    rect(0, 206, PW, 14, '#475569');
    ditherBand(0, 220, PW, 100, '#15803d', '#22c55e', 0.35);
    for (let i = 0; i < 10; i++) {
      const bx = (i * 22 + t * 12) % PW;
      glowOrb(bx, 240 + (i % 3) * 14, 3, '#bbf7d0', '#4ade80', '#166534');
    }
  }

  function bgCrust(t) {
    ditherGradV(0, 0, PW, PH, ['#1e1028', '#331c42', '#190e24']);
    // Vertical dug shaft walls
    rect(0, 0, 32, PH, '#271535');
    rect(PW - 32, 0, 32, PH, '#271535');
    // Glowing cyan crystal veins (@science_in_8bit style)
    glowOrb(24, 118, 4, '#e0f2fe', '#22d3ee', '#0891b2');
    glowOrb(154, 162, 5, '#e0f2fe', '#22d3ee', '#0891b2');
    // Embedded pixel bones in rock wall
    rect(18, 220, 14, 4, '#fef3c7');
    rect(144, 92, 16, 4, '#fef3c7');
    // Rock floor
    ditherBand(0, 206, PW, 114, '#4c2c59', '#2e163b', 0.4);
  }

  function bgMagma(t) {
    ditherGradV(0, 0, PW, 210, ['#1c0916', '#450a0a', '#7c2d12', '#c2410c']);
    // Bubbling glowing magma ocean (@science_in_8bit warm amber/red dithering!)
    ditherGradV(0, 206, PW, 114, ['#fb923c', '#f97316', '#dc2626']);
    for (let i = 0; i < 12; i++) {
      const ox = (i * 19 + t * 14) % PW;
      const oy = 216 + Math.sin(t * 4 + i) * 6 + (i % 3) * 12;
      glowOrb(ox, oy, 3 + (i % 2), '#fef08a', '#facc15', '#ea580c');
    }
    // Floating heat embers
    for (let i = 0; i < 16; i++) {
      const p = PARTICLES[i];
      const ex = (p.x + Math.sin(t * 3 + p.phase) * 8 + PW) % PW;
      const ey = (210 - ((t * 32 + p.y) % 160));
      px(ex, ey, i % 2 === 0 ? '#fde047' : '#fb923c');
    }
  }

  function bgCore(t, frozen = false) {
    if (frozen) {
      ditherGradV(0, 0, PW, PH, ['#082f49', '#0369a1', '#38bdf8']);
      ditherBand(0, 208, PW, 112, '#bae6fd', '#7dd3fc', 0.4);
    } else {
      ditherGradV(0, 0, PW, PH, ['#2e1010', '#7c2d12', '#d97706']);
      ditherBand(0, 208, PW, 112, '#fbbf24', '#f59e0b', 0.35);
    }

    // Giant Retro Wall-Mounted EARTH THERMOSTAT!
    const tx = 58, ty = 78;
    rect(tx - 2, ty - 2, 68, 52, '#181124');
    rect(tx, ty, 64, 48, '#cbd5e1');
    rect(tx + 2, ty + 2, 60, 44, '#94a3b8');
    // Screen
    rect(tx + 6, ty + 6, 52, 22, '#090d1f');
    if (frozen) {
      pixelText('COOL ON', tx + 32, ty + 11, '#38bdf8', null, 'center');
      pixelText('-40°C', tx + 32, ty + 19, '#bae6fd', null, 'center');
    } else {
      pixelText('HEAT', tx + 32, ty + 11, '#ef4444', null, 'center');
      pixelText('9900F', tx + 32, ty + 19, '#fbbf24', null, 'center');
    }
    // HEAT / COOL buttons
    rect(tx + 8, ty + 32, 20, 10, '#ef4444');
    pixelText('HOT', tx + 18, ty + 35, '#ffffff', null, 'center');
    rect(tx + 36, ty + 32, 20, 10, frozen ? '#38bdf8' : '#0284c7');
    pixelText('COOL', tx + 46, ty + 35, '#ffffff', null, 'center');
  }

  function bgGeyser(t) {
    ditherGradV(0, 0, PW, PH, ['#0f172a', '#1e3a8a', '#0284c7']);
    // Vertical cyan ice/steam blast column
    const w = 44 + Math.round(Math.sin(t * 20) * 4);
    rect(90 - w / 2, 0, w, PH, '#0ea5e9');
    rect(90 - w / 4, 0, w / 2, PH, '#bae6fd');
    // Speed lines
    for (let i = 0; i < 20; i++) {
      const p = PARTICLES[i];
      const lx = 68 + (p.x % 44);
      const ly = (p.y + t * 240) % PH;
      rect(lx, ly, 2, 12, '#ffffff');
    }
  }

  function renderFrame(t) {
    const mainCanvas = document.getElementById('c');
    const ctx = mainCanvas.getContext('2d');
    const W = mainCanvas.width;
    const H = mainCanvas.height;

    const bi = activeBeatIndex(t);
    const beat = BEATS[bi] || { start: 0, end: 3, speaker: 'host' };
    const u = Math.min(1, Math.max(0, (t - beat.start) / Math.max(0.1, beat.end - beat.start)));

    // Camera zoom creep & deterministic impact kicks
    let camZoom = 1.0 + u * 0.05;
    let camX = 0, camY = 0, camRot = 0;

    // Punch-ins on key beats
    if (bi === 1) camZoom = 1.14 + u * 0.04; // MrBeast deadpan "No."
    if (bi === 3) camZoom = 1.12 + u * 0.06; // MC "Two grand? Say less."
    if (bi === 11) camZoom = 1.16 + u * 0.05; // Thermostat close-up
    if (bi === 13) camZoom = 1.08 + u * 0.06; // WORTH ITTTT!

    // Impact kicks (7-frame alternating oscillation)
    const k1 = kickOffset(t, BEATS[5]?.start - 0.12 || 11.45, 5);   // Floor collapses into sewer
    const k2 = kickOffset(t, BEATS[12]?.end - 0.15 || 27.85, 6);   // Core freezes!
    const k3 = kickOffset(t, BEATS[14]?.start - 0.25 || 29.30, 6); // Crash onto snowy street!
    camX += k1.x + k2.x + k3.x;
    camY += k1.y + k2.y + k3.y;
    camRot += k1.rot + k2.rot + k3.rot;

    // Clear 180x320 pixel canvas
    pctx.clearRect(0, 0, PW, PH);

    // Scene choreography per beat
    if (bi === 0 || bi === 1) {
      // Beat 0-1: Sunny Street — Host offers $1,000 to MrBeast -> "No."
      bgStreet(t, false);
      drawHudPill('OFFER:', '$1,000', 90, 32, '#4ade80');
      drawBall({
        role: 'host', cx: 52, cy: 178, R: 20,
        expr: blinkExpr('normal', t, 1), lookX: 1,
        isTalking: isSpeaking('host', t), t,
        outfit: 'host_hoodie', hat: 'host_cap',
        prop: 'cash_1k', propSide: 1,
      });
      drawBall({
        role: 'mrbeast', cx: 128, cy: 178, R: 20,
        expr: bi === 1 ? 'squint' : blinkExpr('squint', t, 2), lookX: -1,
        isTalking: isSpeaking('mrbeast', t), t,
        outfit: 'mrbeast_hoodie', hat: 'mrbeast_hair',
      });
    } else if (bi === 2 || bi === 3) {
      // Beat 2-3: Backyard — Host offers $2,000 to MC -> "Two grand? Say less."
      bgBackyard(t);
      drawHudPill('OFFER:', '$2,000', 90, 26, '#facc15');
      drawBall({
        role: 'host', cx: 52, cy: 170, R: 19,
        expr: blinkExpr('normal', t, 1), lookX: 1,
        isTalking: isSpeaking('host', t), t,
        outfit: 'host_hoodie', hat: 'host_cap',
        prop: 'cash_2k', propSide: 1,
      });
      drawBall({
        role: 'mc', cx: 126, cy: 170, R: 19,
        expr: bi === 3 ? 'dollar' : blinkExpr('wide', t, 3), lookX: -1,
        isTalking: isSpeaking('mc', t), t,
        outfit: 'mc_hoodie', hat: 'mc_hair',
        prop: 'shovel', propSide: 1,
      });
    } else if (bi === 4) {
      // Beat 4: Digging down -> floor snaps open!
      bgBackyard(t);
      const depth = Math.round(u * 15);
      drawHudPill('DEPTH:', `${depth}M`, 90, 26, '#ffca3a');
      // Digging hole animation
      const dropY = u > 0.65 ? Math.round((u - 0.65) / 0.35 * 60) : 0;
      rect(104, 186, 44, 30 + dropY, '#090d1f');
      drawBall({
        role: 'mc', cx: 126, cy: 176 + dropY, R: 18,
        expr: u > 0.6 ? 'wide' : blinkExpr('normal', t, 3), lookY: 1,
        isTalking: isSpeaking('mc', t), t,
        outfit: 'mc_hoodie', hat: 'mc_hair',
        prop: 'shovel', propSide: -1,
      });
    } else if (bi === 5 || bi === 6) {
      // Beat 5-6: Sewer Detour with Rat King!
      bgSewer(t);
      drawHudPill('DEPTH:', '15M', 90, 26, '#4ade80');
      drawBall({
        role: 'mc', cx: 56, cy: 186, R: 18,
        expr: bi === 6 ? 'wide' : blinkExpr('normal', t, 3), lookX: 1,
        isTalking: isSpeaking('mc', t), t,
        outfit: 'mc_hoodie', hat: 'mc_hair',
        prop: 'shovel', propSide: -1, sweat: true,
      });
      drawBall({
        role: 'rat', cx: 126, cy: 186, R: 18,
        expr: bi === 5 ? 'angry' : blinkExpr('angry', t, 4), lookX: -1,
        isTalking: isSpeaking('rat', t), t,
        outfit: 'rat_cape', hat: 'rat_crown',
        prop: 'pizza', propSide: 1,
      });
    } else if (bi === 7) {
      // Beat 7: Fossil Crust + T-Rex Skull Helmet!
      bgCrust(t);
      drawHudPill('DEPTH:', '40 KM', 90, 26, '#38bdf8');
      drawBall({
        role: 'mc', cx: 90, cy: 182, R: 22,
        expr: blinkExpr('normal', t, 3),
        isTalking: isSpeaking('mc', t), t,
        outfit: 'mc_hoodie', hat: 'dino_skull',
        prop: 'shovel', propSide: 1,
      });
    } else if (bi === 8 || bi === 9) {
      // Beat 8-9: Magma Mantle! Shovel melts!
      bgMagma(t);
      const depthKm = bi === 8 ? Math.round(1400 + u * 1500) : Math.round(2900 + u * 2200);
      drawHudPill('TEMP:', '3,700°C', 90, 26, '#fb923c');
      drawHudPill('DEPTH:', `${depthKm}KM`, 90, 42, '#ffca3a');
      // T-Rex bone raft floating on magma waves
      const bob = Math.round(Math.sin(t * 7) * 2);
      rect(64, 200 + bob, 52, 6, '#fef3c7');
      drawBall({
        role: 'mc', cx: 90, cy: 180 + bob, R: 21,
        expr: 'wide',
        isTalking: isSpeaking('mc', t), t,
        outfit: 'mc_hoodie', hat: 'dino_skull',
        prop: bi === 8 && u > 0.55 ? 'melted_shovel' : 'shovel',
        propSide: 1, sweat: true, singed: true,
      });
    } else if (bi === 10 || bi === 11 || bi === 12) {
      // Beat 10-12: Inner Core Room -> Thermostat -> Freeze!
      const isFrozen = bi === 12 && u > 0.72;
      bgCore(t, isFrozen);
      drawHudPill(isFrozen ? 'TEMP:' : '6,371KM', isFrozen ? '-40°C' : '5,500°C', 90, 36, isFrozen ? '#38bdf8' : '#facc15');
      drawBall({
        role: 'mc', cx: 52, cy: 186, R: 19,
        expr: bi === 10 ? blinkExpr('wide', t, 3) : 'normal', lookX: 1,
        isTalking: isSpeaking('mc', t), t,
        outfit: 'mc_hoodie', hat: 'dino_skull',
        sweat: !isFrozen, singed: true, icy: isFrozen,
      });
      drawBall({
        role: 'guardian', cx: 132, cy: 186, R: 19,
        expr: bi === 12 ? 'wide' : 'sleepy', lookX: -1,
        isTalking: isSpeaking('guardian', t), t,
        outfit: 'guardian_robe', hat: 'nightcap',
        glasses: true,
      });
      if (bi < 12) {
        // Floating Zzz above sleeping guardian
        const zy = 148 - ((t * 14) % 10);
        pixelText('Z', 142, zy, '#e2e8f0', '#090d1f', 'center');
      }
    } else if (bi === 13) {
      // Beat 13: Ice Geyser Launch ("WORTH ITTTT!")
      bgGeyser(t);
      drawHudPill('SPEED:', 'MACH 9', 90, 26, '#38bdf8');
      const launchY = Math.round(210 - u * 130);
      drawBall({
        role: 'mc', cx: 90, cy: launchY, R: 20,
        expr: 'wide',
        isTalking: isSpeaking('mc', t), t,
        outfit: 'mc_hoodie', hat: 'dino_skull',
        prop: 'ice_core', propSide: 1, singed: true, icy: true,
      });
    } else {
      // Beat 14-15: Frozen Street Shortchange Ending!
      bgStreet(t, true);
      drawHudPill('TEMP:', '-40°C', 90, 26, '#38bdf8');
      const hostBolting = bi === 15 && u > 0.80;
      const hostX = hostBolting ? Math.round(134 + ((u - 0.80) / 0.20) * 80) : 134;

      drawBall({
        role: 'mc', cx: 46, cy: 178 + (bi === 14 ? Math.round(Math.sin(t * 40)) : 0), R: 20,
        expr: bi === 14 ? 'shiver' : blinkExpr('squint', t, 3), lookX: 1,
        isTalking: isSpeaking('mc', t), t,
        outfit: 'mc_hoodie', hat: 'dino_skull',
        prop: 'ice_core', propSide: 1, singed: true, icy: true,
      });
      drawBall({
        role: 'host', cx: hostX, cy: 178, R: 20,
        expr: hostBolting ? 'wide' : blinkExpr('squint', t, 1), lookX: hostBolting ? 1 : -1,
        isTalking: isSpeaking('host', t), t,
        outfit: 'host_parka', hat: 'host_cap',
        prop: hostBolting ? null : 'cash_1k', propSide: -1,
      });
      if (hostBolting) {
        // Dropped frozen $1K bill in the snow!
        rect(112, 196, 12, 7, '#22c55e');
        pixelText('$1K', 118, 189, '#4ade80', '#062812', 'center');
      }
    }

    // 1) Nearest-neighbor 6x upscale of 180x320 pixel canvas onto 1080x1920 display
    ctx.save();
    ctx.fillStyle = '#08080c';
    ctx.fillRect(0, 0, W, H);
    ctx.imageSmoothingEnabled = false;
    ctx.translate(W / 2 + camX * SCALE, H / 2 + camY * SCALE);
    ctx.rotate(camRot);
    ctx.scale(camZoom, camZoom);
    ctx.drawImage(pCanvas, -W / 2, -H / 2, W, H);
    ctx.restore();

    // 2) Subtle corner vignette polish
    const vg = ctx.createRadialGradient(W * 0.5, H * 0.45, W * 0.35, W * 0.5, H * 0.5, W * 0.85);
    vg.addColorStop(0, 'rgba(0,0,0,0)');
    vg.addColorStop(1, 'rgba(4,4,12,0.38)');
    ctx.fillStyle = vg;
    ctx.fillRect(0, 0, W, H);

    // 3) 8sb2R11FeVw Black-Pill Subtitles (1080x1920 crisp typography)
    for (const ch of SUB_CHUNKS) {
      if (t >= ch.start && t <= ch.end) {
        let activeIdx = ch.words.length - 1;
        for (let i = 0; i < ch.words.length; i++) {
          if (t >= ch.words[i].start - 0.04) activeIdx = i;
        }
        drawSubtitlePill(ctx, W, ch.words, activeIdx, t - ch.start, 1365);
        break;
      }
    }
  }

  window.renderFrame = renderFrame;
  window.initCoreShort = init;
  return { init, renderFrame };
})();
