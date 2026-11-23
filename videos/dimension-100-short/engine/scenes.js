/* Travelling to the 100th Dimension — 180x320 Pixel-Art Scenes + 1080x1920 Black-Pill Subtitles
 * Driven deterministically by beats.json (ElevenLabs + Whisper word timestamps).
 */
window.DIM100_SHORT = (() => {
  const {
    PW, PH, SCALE, pCanvas, pctx,
    px, rect, line, ditherBand, ditherGradV, disk, glowOrb, drawTesseract4D,
    pixelText, drawHudPill, drawSubtitlePill,
  } = window.PX;
  const { drawBall, drawFlatSquare, drawCalculatorBlockMC } = window.CHARS;

  let BEATS = [];
  let TOTAL = 49.625;
  let SUB_CHUNKS = [];

  function seeded(seed) {
    let s = seed | 0 || 12345;
    return () => {
      s = (s * 1664525 + 1013904223) | 0;
      return (s >>> 0) / 4294967296;
    };
  }

  const PARTICLES = (() => {
    const r = seeded(100100);
    return Array.from({ length: 52 }, () => ({
      x: r() * PW,
      y: r() * PH,
      vx: (r() - 0.5) * 20,
      vy: 14 + r() * 30,
      s: r() < 0.7 ? 1 : 2,
      phase: r() * 6.28,
      col: ['#22d3ee', '#f472b6', '#fde047', '#a855f7'][(r() * 4) | 0],
    }));
  })();

  // Group Whisper words into 2-4 word black-pill chunks (Law #27)
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
            end: cur[cur.length - 1].end + 0.08,
            words: cur,
          });
          cur = [];
        }
      }
    }
    return chunks;
  }

  function init(beatsData) {
    BEATS = beatsData.beats || [];
    TOTAL = beatsData.total || 49.625;
    SUB_CHUNKS = buildSubtitleChunks(BEATS);
    window.CORE_TOTAL = TOTAL;
    window.CORE_READY = true;
  }

  function isSpeaking(speaker, t) {
    for (const b of BEATS) {
      if (b.speaker !== speaker) continue;
      if (t >= b.start && t <= b.speechEnd) {
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

  // Law #15: Deterministic 4-frame blink every ~1.3s
  function blinkExpr(baseExpr, t, seed = 0) {
    const cycle = (t + seed * 0.47) % 1.32;
    if (cycle > 1.19 && baseExpr !== 'dizzy') return 'blink';
    return baseExpr;
  }

  // Law #14: Deterministic 7-frame alternating-sign impact kick
  function kickOffset(t, tImpact, ampPx = 5) {
    const f = Math.round((t - tImpact) * 30);
    if (f < 0 || f >= 7) return { x: 0, y: 0, rot: 0 };
    const decay = 1 - f / 7;
    const sign = f % 2 === 0 ? 1 : -1;
    return {
      x: sign * ampPx * 0.45 * decay,
      y: sign * ampPx * decay,
      rot: sign * 0.025 * decay,
    };
  }

  // Draw the 8-Bit Quantum Time-Toaster Booth!
  function drawQuantumToaster(cx, yFloor, t, mode = 'idle', dialText = '3D') {
    const w = 36, h = 48;
    const x0 = Math.round(cx - w / 2);
    const y0 = Math.round(yFloor - h);

    // Outer dark plum outline + chrome toaster body
    rect(x0 - 2, y0 - 2, w + 4, h + 2, '#181124');
    rect(x0, y0, w, h, '#64748b');
    rect(x0 + 2, y0 + 2, w - 4, h - 4, '#94a3b8');
    rect(x0 + 3, y0 + 3, 3, h - 6, '#e2e8f0'); // chrome highlight

    // Glowing top toaster slots
    const slotGlow = mode === 'active' || mode === 'overdrive' ? '#f472b6' : '#22d3ee';
    rect(x0 + 6, y0 - 4, 10, 3, slotGlow);
    rect(x0 + 20, y0 - 4, 10, 3, slotGlow);

    // Top banner sign: "100D"
    rect(x0 + 4, y0 - 13, w - 8, 9, '#0f172a');
    rect(x0 + 5, y0 - 12, w - 10, 7, '#1e1b4b');
    pixelText(dialText, cx, y0 - 11, '#fde047', null, 'center');

    // Glowing portal chamber window
    rect(x0 + 6, y0 + 8, w - 12, 24, '#090d1f');
    const coilCol = mode === 'overdrive' ? '#ef4444' : mode === 'smoking' ? '#475569' : '#22d3ee';
    for (let ry = y0 + 11; ry < y0 + 30; ry += 4) {
      rect(x0 + 8, ry, w - 16, 2, coilCol);
    }

    // Side toaster lever
    const leverY = (mode === 'active' || mode === 'overdrive') ? y0 + 26 : y0 + 12;
    rect(x0 + w, y0 + 10, 3, 22, '#181124');
    rect(x0 + w + 1, leverY, 6, 4, '#ef4444');

    // Bottom control dial
    disk(cx, y0 + 39, 5, '#0f172a');
    disk(cx, y0 + 39, 3, mode === 'overdrive' ? '#ef4444' : '#38bdf8');
    px(cx + Math.round(Math.cos(t * 6) * 2), y0 + 39 + Math.round(Math.sin(t * 6) * 2), '#ffffff');

    // Smoking sparks after return
    if (mode === 'smoking') {
      for (let i = 0; i < 6; i++) {
        const sx = cx - 10 + ((i * 7 + Math.floor(t * 10)) % 20);
        const sy = y0 - 6 - ((t * 22 + i * 9) % 24);
        disk(sx, sy, 2 + (i & 1), i % 2 === 0 ? '#64748b' : '#94a3b8');
      }
    }
  }

  // --- ENVIRONMENT PAINTERS (180x320) ---

  function bgStreet3D(t, isBackyard = false) {
    ditherGradV(0, 0, PW, 192, isBackyard ? ['#1e1b4b', '#1d4ed8', '#60a5fa'] : ['#1e3a8a', '#0284c7', '#7dd3fc']);
    glowOrb(isBackyard ? 32 : 148, 52, 9, '#fef9c3', '#fde047', '#38bdf8');

    // Drifting pixel clouds
    for (let i = 0; i < 4; i++) {
      const cx = ((i * 54 + t * 7) % (PW + 44)) - 22;
      const cy = 54 + (i % 2) * 16;
      rect(cx, cy, 28, 7, '#ffffff');
      rect(cx + 5, cy - 3, 16, 4, '#f8fafc');
      rect(cx + 2, cy + 6, 24, 2, '#cbd5e1');
    }

    if (isBackyard) {
      // Backyard lab fence & hazard stripes
      for (let x = 0; x < PW; x += 12) {
        rect(x, 148, 10, 42, '#78350f');
        rect(x + 1, 148, 2, 42, '#92400e');
      }
      ditherBand(0, 190, PW, 22, '#16a34a', '#15803d', 0.45);
      ditherGradV(0, 212, PW, 108, ['#334155', '#1e293b', '#0f172a']);
      for (let x = 0; x < PW; x += 16) {
        rect(x, 212, 8, 4, '#facc15');
        rect(x + 8, 212, 8, 4, '#181124');
      }
    } else {
      // Houses & green hedge
      rect(8, 142, 36, 30, '#cbd5e1');
      rect(6, 134, 40, 8, '#ef4444');
      rect(20, 154, 9, 18, '#78350f');
      rect(136, 138, 36, 34, '#fde68a');
      rect(134, 130, 40, 8, '#2563eb');
      ditherBand(0, 170, PW, 16, '#16a34a', '#15803d', 0.4);
      rect(0, 186, PW, 14, '#94a3b8');
      ditherGradV(0, 200, PW, 120, ['#334155', '#1e293b', '#0f172a']);
      for (let x = 8; x < PW; x += 28) rect(x, 224, 14, 3, '#facc15');
    }

    // Foreground repoussoir cables at top & dark curb shadow at bottom (Pillar 2 Law #4 & #8)
    line(0, 10, PW, 18, '#0f172a');
    line(0, 14, PW, 8, '#0f172a');
    rect(0, 306, PW, 14, '#090d1f');
  }

  function bg1DLineWorld(t) {
    // Deep void collapsed into a single 1D horizontal axis at y = 178!
    ditherGradV(0, 0, PW, PH, ['#030712', '#090d1f', '#030712']);

    // Top & bottom crushing hydraulic arrows showing 3D -> 1D compression
    for (let x = 22; x < PW; x += 34) {
      const ay = 115 + Math.round(Math.sin(t * 14) * 4);
      rect(x - 1, 70, 3, ay - 70, '#1e293b');
      pixelText('V', x, ay, '#38bdf8', null, 'center');

      const by = 240 - Math.round(Math.sin(t * 14) * 4);
      rect(x - 1, by + 6, 3, 285 - by, '#1e293b');
      pixelText('^', x, by, '#38bdf8', null, 'center');
    }

    // Glowing 1D Number Line Axis
    rect(0, 175, PW, 7, '#0284c7');
    rect(0, 177, PW, 3, '#38bdf8');
    rect(0, 178, PW, 1, '#ffffff');

    // Number line tick marks (-2, -1, 0, +1, +2)
    const ticks = [
      { x: 18, lbl: '-2' },
      { x: 54, lbl: '-1' },
      { x: 90, lbl: '0' },
      { x: 126, lbl: '+1' },
      { x: 162, lbl: '+2' },
    ];
    for (const tk of ticks) {
      rect(tk.x, 172, 1, 13, '#ffffff');
      pixelText(tk.lbl, tk.x, 190, '#7dd3fc', '#030712', 'center');
    }
  }

  function bg2DFlatland(t) {
    // Classic 8-bit 2D blueprint / arcade coordinate plane
    rect(0, 0, PW, PH, '#09142b');
    // 16px coordinate grid lines
    for (let x = 0; x < PW; x += 18) rect(x, 0, 1, PH, '#132852');
    for (let y = 0; y < PH; y += 18) rect(0, y, PW, 1, '#132852');

    // Vertical Y-AXIS on left
    rect(20, 48, 2, 220, '#38bdf8');
    pixelText('Y-AXIS', 24, 58, '#38bdf8', '#050b18', 'left');

    // Floating 2D arcade question blocks
    for (let i = 0; i < 3; i++) {
      const bx = 56 + i * 24;
      const by = 112 + Math.round(Math.sin(t * 6 + i) * 2);
      rect(bx, by, 14, 14, '#ffffff');
      rect(bx + 1, by + 1, 12, 12, '#d97706');
      rect(bx + 2, by + 2, 10, 10, '#facc15');
      pixelText('?', bx + 7, by + 5, '#78350f', null, 'center');
    }

    // Glowing Magenta X-AXIS Floor Line that Sir Square guards!
    rect(0, 198, PW, 4, '#ec4899');
    rect(0, 199, PW, 2, '#fbcfe8');
    pixelText('X-AXIS (2D FLOOR)', 90, 260, '#f472b6', '#050b18', 'center');
  }

  function bg4DTesseract(t) {
    ditherGradV(0, 0, PW, PH, ['#090418', '#1e0b3b', '#311042', '#0f0722']);

    // Rotating 4D Tesseract Hypercube in center upper-midground (clear of character labels!)
    drawTesseract4D(90, 106, 25, t, '#22d3ee', '#f472b6', '#a855f7');

    // 4D curved Escher floor grid
    ditherBand(0, 204, PW, 116, '#1e1b4b', '#0f0722', 0.45);
    for (let x = -20; x <= PW + 20; x += 22) {
      line(90, 160, x, 319, '#4c1d95');
    }
    for (let y = 204; y < 310; y += 16) {
      rect(0, y, PW, 1, '#6d28d9');
    }

    // Floating W-axis coordinate markers
    pixelText('+W', 24, 88 + Math.round(Math.sin(t * 4) * 3), '#22d3ee', '#090418', 'center');
    pixelText('-W', 156, 88 - Math.round(Math.sin(t * 4) * 3), '#f472b6', '#090418', 'center');
  }

  function bg11DStringManifold(t) {
    ditherGradV(0, 0, PW, PH, ['#070312', '#170a38', '#2e1065', '#090418']);

    // 11D Calabi-Yau vibrating superstrings across background!
    const cols = ['#fde047', '#22d3ee', '#f472b6', '#a855f7'];
    for (let s = 0; s < 4; s++) {
      const baseY = 92 + s * 22;
      const col = cols[s];
      for (let x = 0; x < PW; x += 2) {
        const y = baseY + Math.sin(x * 0.08 + t * (5 + s) + s) * (8 + s * 2);
        rect(x, y, 2, 2, col);
      }
    }

    // Leaking Gravity Orbs ("G v") falling out of folded space!
    for (let i = 0; i < 7; i++) {
      const gx = 20 + i * 23;
      const gy = 140 + ((t * 36 + i * 29) % 135);
      glowOrb(gx, gy, 3, '#ffffff', '#38bdf8', '#1d4ed8');
    }

    // Cosmic platform floor
    ditherBand(0, 206, PW, 114, '#2e1065', '#1e1b4b', 0.4);
    rect(0, 206, PW, 2, '#fde047');
  }

  function bgOverdriveTunnel(t, dimNum) {
    rect(0, 0, PW, PH, '#060311');
    const cx = 90, cy = 172;
    const ringCols = ['#ef4444', '#facc15', '#22c55e', '#22d3ee', '#a855f7', '#ec4899'];

    // Concentric zooming hyper-rectangles
    for (let i = 0; i < 9; i++) {
      const phase = ((t * 3.5 + i * 0.35) % 3.0) / 3.0;
      const rw = Math.round(12 + phase * 180);
      const rh = Math.round(18 + phase * 290);
      const col = ringCols[(i + Math.floor(t * 10)) % ringCols.length];
      const x0 = cx - Math.floor(rw / 2);
      const y0 = cy - Math.floor(rh / 2);
      rect(x0, y0, rw, 2, col);
      rect(x0, y0 + rh - 2, rw, 2, col);
      rect(x0, y0, 2, rh, col);
      rect(x0 + rw - 2, y0, 2, rh, col);
    }

    // Radiating warp speed lines
    for (let i = 0; i < 16; i++) {
      const p = PARTICLES[i];
      const ang = (i / 16) * Math.PI * 2 + t * 0.8;
      const r0 = 18 + ((t * 120 + p.x) % 45);
      const r1 = r0 + 26;
      line(
        cx + Math.cos(ang) * r0,
        cy + Math.sin(ang) * r0,
        cx + Math.cos(ang) * r1,
        cy + Math.sin(ang) * r1,
        '#ffffff'
      );
    }
  }

  function bg100DCalculatorLCD(t) {
    // Retro Pocket Calculator Olive-Green LCD Screen!
    rect(0, 0, PW, PH, '#1e2923');
    // Calculator plastic bezel frame
    rect(8, 18, PW - 16, PH - 36, '#334155');
    rect(12, 22, PW - 24, PH - 44, '#0f172a');
    // Backlit olive-green LCD glass
    ditherGradV(16, 52, PW - 32, 210, ['#84a98c', '#749c75', '#52796f']);

    // Subtle 16x16 LCD macro-pixel background matrix grid
    for (let x = 16; x < PW - 16; x += 16) rect(x, 52, 1, 210, 'rgba(6, 32, 22, 0.16)');
    for (let y = 52; y < 262; y += 16) rect(16, y, PW - 32, 1, 'rgba(6, 32, 22, 0.16)');

    // Calculator top LCD status bar
    pixelText('CASIO-100D', 24, 60, '#062016', null, 'left');
    pixelText('ERR:RAM=6PX', 156, 60, '#062016', null, 'right');
    rect(22, 68, PW - 44, 2, '#062016');

    // Chunky 3-block calculator toaster on right
    const tx = 124, ty = 156;
    rect(tx, ty, 14, 14, '#062016');
    rect(tx + 16, ty, 14, 14, '#062016');
    rect(tx, ty + 16, 30, 14, '#062016');
    pixelText('100D', tx + 15, ty - 9, '#062016', null, 'center');
  }

  function renderFrame(t) {
    const mainCanvas = document.getElementById('c');
    const ctx = mainCanvas.getContext('2d');
    const W = mainCanvas.width;
    const H = mainCanvas.height;

    const bi = activeBeatIndex(t);
    const beat = BEATS[bi] || { start: 0, end: 3, speaker: 'host' };
    const u = Math.min(1, Math.max(0, (t - beat.start) / Math.max(0.1, beat.end - beat.start)));

    // Law #12 & #28: Continuous camera motion + ~1 cut/sec sub-beat punch-ins & Dutch tilts
    let camZoom = 1.0 + u * 0.05;
    let camX = 0, camY = 0, camRot = 0;

    if (bi === 0 && u > 0.52) { camZoom = 1.12 + (u - 0.52) * 0.08; camX = -4; camY = 6; }
    if (bi === 1) { camZoom = 1.18 + u * 0.04; camX = -16; camY = 8; } // MrBeast deadpan "No." close-up
    if (bi === 2 && u > 0.50) { camZoom = 1.10 + (u - 0.50) * 0.08; camX = 6; camY = 5; }
    if (bi === 3) { camZoom = 1.14 + u * 0.06; camX = -12; camY = 6; } // MC "Two grand? Fire it up."
    if (bi === 4 && u > 0.52) { camZoom = 1.12 + (u - 0.52) * 0.08; camRot = -0.03; camY = 6; } // 1D squash!
    if (bi === 6) { camZoom = 1.13 + u * 0.05; camX = 8; camY = 6; } // Dial crank
    if (bi === 7 && u > 0.50) { camZoom = 1.11 + (u - 0.50) * 0.05; camY = 5; } // Back of own head in 4D
    if (bi === 8 && u > 0.48) { camZoom = 1.13 + (u - 0.48) * 0.06; camRot = 0.03; camY = 6; } // Unluckily Klein bottle!
    if (bi === 9 && u > 0.52) { camZoom = 1.10 + (u - 0.52) * 0.06; camX = -8; camY = 5; } // "You see," origami pretzel pivot
    if (bi === 10) { camZoom = 1.13 + u * 0.05; camY = 6; }
    if (bi === 11) { camZoom = 1.05 + u * 0.10; camRot = Math.sin(t * 14) * 0.035; camY = 5; }
    if (bi === 12) { camZoom = 1.14 + u * 0.06; camRot = -0.04; camY = 6; } // TWO GRAND, BABY!
    if (bi === 13) { camZoom = 1.06 + u * 0.04; camY = 4; } // 6-pixel calculator room
    if (bi === 15 && u > 0.48) { camZoom = 1.12 + (u - 0.48) * 0.05; camX = -8; camY = 5; } // folds down to a nickel!

    // Law #14: 7-Frame Alternating-Sign Impact KICKS on major dimensional snaps
    const k1 = kickOffset(t, (BEATS[4]?.start || 10.36) + 1.55, 5); // 1D Line Squash
    const k2 = kickOffset(t, BEATS[5]?.start || 13.35, 5);           // 2D Flatland Pop
    const k3 = kickOffset(t, BEATS[7]?.start || 17.73, 5);           // 4D Tesseract Entry
    const k4 = kickOffset(t, BEATS[12]?.start || 38.55, 7);          // 100D Overdrive Breach
    const k5 = kickOffset(t, BEATS[13]?.start || 39.83, 6);          // 6-Pixel Calculator Downgrade
    const k6 = kickOffset(t, BEATS[14]?.start || 42.54, 6);          // Crash back to 3D Street
    camX += k1.x + k2.x + k3.x + k4.x + k5.x + k6.x;
    camY += k1.y + k2.y + k3.y + k4.y + k5.y + k6.y;
    camRot += k1.rot + k2.rot + k3.rot + k4.rot + k5.rot + k6.rot;

    pctx.clearRect(0, 0, PW, PH);

    // --- SCENE CHOREOGRAPHY PER BEAT ---
    if (bi === 0 || bi === 1) {
      // Beat 0-1: Sunny Street + Quantum Time-Toaster Booth — Host offers $1,000 to MrBeast -> "No."
      bgStreet3D(t, false);
      drawHudPill('OFFER:', '$1,000', 90, 26, '#4ade80');
      drawQuantumToaster(90, 200, t, 'idle', '100D');
      drawBall({
        role: 'host', cx: 38, cy: 180, R: 19,
        expr: blinkExpr('normal', t, 1), lookX: 1,
        isTalking: isSpeaking('host', t), t,
        outfit: 'host_hoodie', hat: 'host_cap',
        prop: 'cash_1k', propSide: 1,
      });
      drawBall({
        role: 'mrbeast', cx: 142, cy: 180, R: 19,
        expr: bi === 1 ? 'squint' : blinkExpr('squint', t, 2), lookX: -1,
        isTalking: isSpeaking('mrbeast', t), t,
        outfit: 'mrbeast_hoodie', hat: 'mrbeast_hair',
      });
    } else if (bi === 2 || bi === 3) {
      // Beat 2-3: Backyard Quantum Launchpad — Host offers $2,000 to MC -> "Two grand? Fire it up."
      bgStreet3D(t, true);
      drawHudPill('OFFER:', '$2,000', 90, 26, '#facc15');
      drawQuantumToaster(92, 208, t, bi === 3 ? 'active' : 'idle', '100D');
      drawBall({
        role: 'host', cx: 38, cy: 184, R: 18,
        expr: blinkExpr('normal', t, 1), lookX: 1,
        isTalking: isSpeaking('host', t), t,
        outfit: 'host_hoodie', hat: 'host_cap',
        prop: 'cash_2k', propSide: 1,
      });
      drawBall({
        role: 'mc', cx: 140, cy: 184, R: 19,
        expr: bi === 3 ? 'dollar' : blinkExpr('wide', t, 3), lookX: -1,
        isTalking: isSpeaking('mc', t), t,
        outfit: 'mc_hoodie', hat: 'mc_visor',
        prop: 'bagel', propSide: -1,
      });
    } else if (bi === 4) {
      // Beat 4: Dial starts at Dimension 1 -> 1D Line Squash!
      const is1DSquashed = u > 0.52;
      if (!is1DSquashed) {
        bgStreet3D(t, true);
        drawHudPill('DIAL:', 'DIM 1D?!', 90, 26, '#fb923c');
        drawQuantumToaster(90, 208, t, 'overdrive', '1D');
        drawBall({
          role: 'mc', cx: 90, cy: 180, R: 20,
          expr: u > 0.38 ? 'wide' : blinkExpr('normal', t, 3),
          isTalking: isSpeaking('mc', t), t,
          outfit: 'mc_hoodie', hat: 'mc_visor',
          sweat: true,
        });
      } else {
        bg1DLineWorld(t);
        drawHudPill('DIMENSION:', '1D (LINE)', 90, 26, '#38bdf8');
        // MC squashed into a 1D horizontal pancake sliding on the number line!
        const slideX = 90 + Math.round(Math.sin(t * 10) * 16);
        drawBall({
          role: 'mc', cx: slideX, cy: 174, R: 22,
          squashX: 1.65, squashY: 0.34,
          expr: 'wide',
          isTalking: isSpeaking('mc', t), t,
          outfit: 'mc_hoodie',
          sweat: true,
        });
      }
    } else if (bi === 5 || bi === 6) {
      // Beat 5-6: 2D Flatland Arcade Grid with Sir Square!
      bg2DFlatland(t);
      drawHudPill('DIMENSION:', bi === 6 ? '2D -> 4D' : '2D (FLAT)', 90, 26, '#ec4899');
      drawBall({
        role: 'mc', cx: 54, cy: 178, R: 19,
        flat2D: true,
        expr: bi === 6 ? 'normal' : 'wide', lookX: 1,
        isTalking: isSpeaking('mc', t), t,
        outfit: 'mc_hoodie', hat: 'mc_visor',
        sweat: bi === 5,
      });
      drawFlatSquare({
        cx: 132, cy: 180, size: 17,
        expr: 'angry', lookX: -1,
        isTalking: isSpeaking('flat', t), t,
      });
      if (bi === 6) {
        // Floating 2D Dimension Dial being cranked past 3D!
        rect(74, 136, 34, 20, '#0f172a');
        rect(75, 137, 32, 18, '#1e293b');
        pixelText('4D >>', 91, 144, '#fde047', null, 'center');
      }
    } else if (bi === 7 || bi === 8) {
      // Beat 7-8: 4D Tesseract Chamber — Back of Own Head + Klein Bottle Bagel!
      bg4DTesseract(t);
      const isKlein = bi === 8 && u > 0.46;
      drawHudPill('DIMENSION:', '4D (HYPER)', 90, 26, '#22d3ee');

      // MC on left staring at the back of his own head in 4D space!
      drawBall({
        role: 'mc', cx: 52, cy: 184, R: 19,
        expr: isKlein ? 'wide' : (bi === 7 ? 'wide' : blinkExpr('normal', t, 3)),
        lookX: 1,
        isTalking: isSpeaking('mc', t), t,
        outfit: 'mc_hoodie', hat: 'mc_visor',
        prop: bi === 8 ? (isKlein ? 'klein_bottle' : 'bagel') : null,
        propSide: 1,
        sweat: bi === 7 || isKlein,
      });

      if (bi === 7) {
        // Floating 4D hyperspace clone showing the BACK of MC's head!
        const cloneBob = Math.round(Math.sin(t * 6) * 3);
        drawBall({
          role: 'mc', cx: 130, cy: 180 + cloneBob, R: 19,
          backOfHead: true,
          isTalking: isSpeaking('mc', t), t,
          hat: 'mc_hair',
        });
        pixelText('YOU (4D BACK)', 130, 148 + cloneBob, '#f472b6', '#090418', 'center');
      } else {
        // Quantum Toaster floating in 4D tesseract field
        drawQuantumToaster(134, 204, t, 'active', '100D');
      }
    } else if (bi === 9) {
      // Beat 9: 11D -> 50D Calabi-Yau String Theory Warden ("You see, past Dimension Eleven...")
      bg11DStringManifold(t);
      const dimCount = Math.round(11 + u * 39);
      drawHudPill('DIMENSION:', `${dimCount}D (STRINGS)`, 90, 26, '#fde047');

      drawBall({
        role: 'mc', cx: 48, cy: 186, R: 18,
        expr: blinkExpr('wide', t, 3), lookX: 1,
        isTalking: isSpeaking('mc', t), t,
        outfit: 'mc_hoodie', hat: 'mc_visor',
      });
      drawBall({
        role: 'warden', cx: 130, cy: 184, R: 20,
        expr: blinkExpr('normal', t, 5), lookX: -1,
        isTalking: isSpeaking('warden', t), t,
        outfit: 'warden_robe', hat: 'warden_mitre',
        glasses: true, thirdEye: true,
        prop: 'origami_pretzel', propSide: -1,
      });
    } else if (bi === 10 || bi === 11 || bi === 12) {
      // Beat 10-12: Maximum Overdrive -> 88D..100D Hyper-Warp Tunnel!
      const dimVal = bi === 10
        ? Math.round(52 + u * 28)
        : bi === 11
          ? Math.round(80 + u * 19)
          : 100;
      bgOverdriveTunnel(t, dimVal);
      drawHudPill('DIMENSION:', `${dimVal}D`, 90, 26, dimVal === 100 ? '#4ade80' : '#ef4444');

      if (bi === 10) {
        drawQuantumToaster(130, 206, t, 'overdrive', `${dimVal}D`);
        drawBall({
          role: 'mc', cx: 64, cy: 184, R: 21,
          expr: 'dollar', lookX: 1,
          isTalking: isSpeaking('mc', t), t,
          outfit: 'mc_hoodie', hat: 'mc_visor',
          hyperGlitch: true,
        });
      } else if (bi === 11) {
        drawBall({
          role: 'warden', cx: 128, cy: 184, R: 19,
          expr: 'wide', lookX: -1,
          isTalking: isSpeaking('warden', t), t,
          outfit: 'warden_robe', hat: 'warden_mitre',
          glasses: true, thirdEye: true, sweat: true,
        });
        drawBall({
          role: 'mc', cx: 54, cy: 184, R: 19,
          expr: 'dollar', lookX: 1,
          isTalking: isSpeaking('mc', t), t,
          outfit: 'mc_hoodie', hat: 'mc_visor',
          hyperGlitch: true,
        });
      } else {
        // Beat 12: "TWO GRAND, BABY!" — Rocket center through 100D Prism Portal!
        drawTesseract4D(90, 175, 42, t * 2.5, '#fde047', '#22d3ee', '#f472b6');
        drawBall({
          role: 'mc', cx: 90, cy: 178, R: 23,
          expr: 'dollar',
          isTalking: isSpeaking('mc', t), t,
          outfit: 'mc_hoodie', hat: 'mc_visor',
          hyperGlitch: true,
        });
      }
    } else if (bi === 13) {
      // Beat 13: 100D Cosmic Integer Overflow -> 6-Pixel Calculator Screen!
      bg100DCalculatorLCD(t);
      drawHudPill('DIM 100D:', '6 PIXELS?!', 90, 26, '#4ade80');
      drawCalculatorBlockMC(72, 168, isSpeaking('mc', t), t);
    } else {
      // Beat 14-15: Crash Return to 3D Street & The 100D Nickel Twist!
      bgStreet3D(t, false);
      const isNickelRevealed = bi === 15 && u > 0.56;
      const hostBolting = bi === 15 && u > 0.84;
      drawHudPill(isNickelRevealed ? '3D VALUE:' : 'RETURNED:', isNickelRevealed ? '$0.05 (5¢)' : 'DIM 3D', 90, 26, isNickelRevealed ? '#38bdf8' : '#facc15');

      drawQuantumToaster(90, 200, t, 'smoking', 'ERR');

      drawBall({
        role: 'mc', cx: 38, cy: 182, R: 19,
        expr: isNickelRevealed ? 'wide' : blinkExpr('normal', t, 3), lookX: 1,
        isTalking: isSpeaking('mc', t), t,
        outfit: 'mc_hoodie', hat: 'mc_visor',
        prop: 'hypercube_100d', propSide: 1,
        hyperGlitch: true, sweat: isNickelRevealed,
      });

      const hostX = hostBolting ? Math.round(142 + ((u - 0.84) / 0.16) * 55) : 142;
      drawBall({
        role: 'host', cx: hostX, cy: 182, R: 19,
        expr: hostBolting ? 'wide' : blinkExpr('squint', t, 1),
        lookX: hostBolting ? 1 : -1,
        isTalking: isSpeaking('host', t), t,
        outfit: 'host_hoodie', hat: 'host_cap',
        prop: hostBolting ? null : (isNickelRevealed ? 'nickel_5c' : 'cash_2k'),
        propSide: -1,
      });

      if (hostBolting) {
        // Shiny 5c nickel left on the sidewalk!
        disk(122, 196, 4, '#181124');
        disk(122, 196, 3, '#e2e8f0');
        pixelText('5¢', 122, 187, '#38bdf8', '#090d1f', 'center');
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

    // 3) 8sb2R11FeVw Black-Pill Subtitles (1080x1920 crisp typography at y=1365 safe zone)
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
