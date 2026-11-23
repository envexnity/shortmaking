/* 15-Beat Horror ASCII Scenes — 1080x1920 (72x80 ASCII grid + 144x160 2x shader field) */
window.SHORT_APP = (() => {
  const A = window.ASCII;
  const {
    W, H, COLS, ROWS, FW, FH,
    clearField, setPx, blendPx, addGlowPx, fillBox, fillDisk, fillCapsule,
    putCellChar, putCellString, drawAsciiBox,
    presentFrame, buildSubtitleChunks, kickOffset, activeBeatIndex, seeded,
  } = A;

  let BEATS = [];
  let SUB_CHUNKS = [];
  const NOISE_PARTICLES = (() => {
    const r = seeded(1999);
    return Array.from({ length: 90 }, () => ({
      x: r() * FW,
      y: r() * FH,
      sp: 8 + r() * 24,
      ph: r() * 6.28,
    }));
  })();

  function init(bd) {
    BEATS = bd.beats || [];
    SUB_CHUNKS = buildSubtitleChunks(BEATS);
    window.CORE_READY = true;
  }

  // Smooth procedural 3D perspective corridor renderer into the 144x160 2x field
  function drawCorridor3D(t, opts = {}) {
    const vpX = FW * 0.5 + (opts.vpShiftX || 0);
    const vpY = (opts.vpY ?? FH * 0.40) + (opts.vpShiftY || 0);
    const colBase = opts.colBase || [24, 210, 108];
    const colHi = opts.colHi || [185, 255, 215];
    const bright = opts.bright ?? 1.0;
    const zScroll = opts.zScroll || 0;
    const flicker = opts.flicker ?? 1.0;

    for (let y = 0; y < FH; y++) {
      for (let x = 0; x < FW; x++) {
        const dx = (x - vpX) / (FW * 0.5);
        const dy = (y - vpY) / (FH * 0.45);
        const ax = Math.abs(dx);
        const ay = Math.abs(dy);
        const distWall = Math.max(ax * 1.12, ay * 0.92);

        if (distWall < 0.22) {
          // Far back doorway — optional backlit fog glow so foreground silhouettes pop cleanly!
          const backGlow = opts.backGlow ?? 0.04;
          const rim = distWall > 0.19 ? Math.max(0.45, backGlow) : backGlow;
          setPx(x, y, rim * bright, colBase[0] * (0.45 + 0.55 * rim), colBase[1] * (0.45 + 0.55 * rim), colBase[2] * (0.45 + 0.55 * rim), 1);
          continue;
        }

        const depth = 1.0 / Math.max(0.18, distWall);
        const z = depth * 1.65 + zScroll;
        const rib = Math.abs(Math.sin(z * 2.2)) > 0.92 ? 1 : 0;
        const isWall = ax * 1.12 >= ay * 0.92;
        const isCeil = !isWall && dy < 0;
        const isFloor = !isWall && dy > 0;

        // Distance attenuation
        let lum = Math.max(0.06, Math.min(0.92, (0.95 - depth * 0.14))) * bright * flicker;

        if (isCeil) {
          // Overhead fluorescent strip lights down center
          const inTube = ax < 0.16 && (Math.sin(z * 1.8) > 0.15);
          if (inTube) {
            lum = Math.min(1.0, (0.85 + 0.15 * Math.sin(t * 25)) * bright * flicker);
            setPx(x, y, lum, colHi[0], colHi[1], colHi[2], 1);
            continue;
          }
          lum *= 0.65;
        } else if (isFloor) {
          // Concrete floor grid seams + wet reflections
          const tileGrid = (Math.abs(Math.sin(z * 3.0)) > 0.90) || (Math.abs(dx / Math.max(0.15, dy) % 0.45) < 0.05);
          lum *= tileGrid ? 0.85 : 0.48;
        } else {
          // Side concrete wall panels + door ribs
          lum *= rib ? 1.15 : 0.72;
        }

        // Flashlight vignette falloff in dark mode
        if (opts.flashlight) {
          const rBeam = Math.hypot((x - (vpX + Math.sin(t * 1.8) * 6)) * 1.1, y - vpY);
          const beam = Math.max(0.15, 1.0 - rBeam / 68.0);
          lum *= beam * 1.15;
        }

        const r = colBase[0] * (0.45 + 0.55 * lum);
        const g = colBase[1] * (0.45 + 0.55 * lum);
        const b = colBase[2] * (0.45 + 0.55 * lum);
        setPx(x, y, lum, r, g, b, rib ? 1 : 0);
      }
    }
  }

  // Draw a tall gaunt horror silhouette/entity with articulated limbs, ribcage, eyes & teeth
  function drawEntity(cx, cy, scale, t, opts = {}) {
    const colBody = opts.colBody || [16, 42, 26];
    const colEdge = opts.colEdge || [65, 235, 145];
    const eyeCol = opts.eyeCol || [255, 55, 65];
    const jawOpen = opts.jawOpen || 0;
    const shadowOnly = !!opts.shadowOnly;
    const lumaVal = shadowOnly ? 0.12 : (opts.luma ?? 0.52);

    const headR = 7.5 * scale;
    const headY = cy - 28 * scale;
    const torsoTop = headY + headR * 1.15;
    const torsoBot = cy + 6 * scale;
    const shW = 13 * scale;

    // Subtle unnatural neck/head tilt sway
    const tiltX = Math.sin(t * 3.1 + (opts.phase || 0)) * 2.2 * scale;

    // Long crooked arms hanging past knees
    const armSway = Math.sin(t * 4.2 + (opts.phase || 0)) * 3.0 * scale;
    fillCapsule(cx - shW, torsoTop + 2 * scale, cx - shW - 5 * scale + armSway, cy + 20 * scale, 2.3 * scale, lumaVal, colBody[0], colBody[1], colBody[2]);
    fillCapsule(cx + shW, torsoTop + 2 * scale, cx + shW + 5 * scale - armSway, cy + 20 * scale, 2.3 * scale, lumaVal, colBody[0], colBody[1], colBody[2]);
    // Long fingers
    for (let f = -1; f <= 1; f++) {
      fillCapsule(cx - shW - 5 * scale + armSway, cy + 20 * scale, cx - shW - (6 + f * 2) * scale + armSway, cy + 27 * scale, 1.0 * scale, lumaVal * 1.2, colEdge[0], colEdge[1], colEdge[2]);
      fillCapsule(cx + shW + 5 * scale - armSway, cy + 20 * scale, cx + shW + (6 + f * 2) * scale - armSway, cy + 27 * scale, 1.0 * scale, lumaVal * 1.2, colEdge[0], colEdge[1], colEdge[2]);
    }

    // Legs
    fillCapsule(cx - 5 * scale, torsoBot, cx - 6 * scale, cy + 36 * scale, 2.6 * scale, lumaVal, colBody[0], colBody[1], colBody[2]);
    fillCapsule(cx + 5 * scale, torsoBot, cx + 6 * scale, cy + 36 * scale, 2.6 * scale, lumaVal, colBody[0], colBody[1], colBody[2]);

    // Torso
    fillCapsule(cx, torsoTop + 2 * scale, cx, torsoBot, shW * 0.65, lumaVal, colBody[0], colBody[1], colBody[2]);
    if (!shadowOnly) {
      // Rim edge highlight along shoulders & skull
      for (let r = 0; r < 4; r++) {
        const ry = torsoTop + (4 + r * 5.2) * scale;
        fillCapsule(cx - shW * 0.48, ry, cx + shW * 0.48, ry, 0.9 * scale, 0.72, colEdge[0], colEdge[1], colEdge[2]);
      }
    }

    // Elongated skull / head
    fillCapsule(cx + tiltX, headY - 2 * scale, cx + tiltX * 0.5, headY + 4 * scale + jawOpen * 4 * scale, headR, shadowOnly ? 0.10 : 0.75, colEdge[0] * 0.55, colEdge[1] * 0.55, colEdge[2] * 0.55);

    // Eyes (explicit crisp ASCII glyphs + edge=0 glow so Sobel never swallows them!)
    if (!opts.noEyes) {
      const eyeY = headY - 1.5 * scale;
      const eyeOff = Math.max(3.6, 3.4 * scale);
      const ecHex = `#${((1 << 24) | (eyeCol[0] << 16) | (eyeCol[1] << 8) | eyeCol[2]).toString(16).slice(1)}`;
      const cL = Math.round((cx + tiltX - eyeOff) * 0.5);
      const cR = Math.round((cx + tiltX + eyeOff) * 0.5);
      const rE = Math.round(eyeY * 0.5);
      if (opts.blink) {
        fillCapsule(cx + tiltX - eyeOff - 2 * scale, eyeY, cx + tiltX - eyeOff + 2 * scale, eyeY, 0.9 * scale, 0.95, eyeCol[0], eyeCol[1], eyeCol[2], 0);
        fillCapsule(cx + tiltX + eyeOff - 2 * scale, eyeY, cx + tiltX + eyeOff + 2 * scale, eyeY, 0.9 * scale, 0.95, eyeCol[0], eyeCol[1], eyeCol[2], 0);
        putCellChar(cL, rE, '-', ecHex);
        putCellChar(cR, rE, '-', ecHex);
      } else {
        fillDisk(cx + tiltX - eyeOff, eyeY, Math.max(2.0, 2.2 * scale), 0.98, eyeCol[0], eyeCol[1], eyeCol[2], 0.5, 0);
        fillDisk(cx + tiltX + eyeOff, eyeY, Math.max(2.0, 2.2 * scale), 0.98, eyeCol[0], eyeCol[1], eyeCol[2], 0.5, 0);
        putCellChar(cL, rE, scale > 0.9 ? 'O' : 'o', ecHex);
        putCellChar(cR, rE, scale > 0.9 ? 'O' : 'o', ecHex);
      }
    }

    // Unhinged screaming mouth when jawOpen > 0
    if (jawOpen > 0.15) {
      fillCapsule(cx + tiltX * 0.5, headY + 3.5 * scale, cx + tiltX * 0.5, headY + (5.5 + jawOpen * 6) * scale, 3.0 * scale, 0.06, 12, 4, 6);
      const cellC = Math.round((cx + tiltX * 0.5) * 0.5);
      const cellR = Math.round((headY + 5 * scale) * 0.5);
      putCellString(cellC, cellR, 'V#W#V', '#fff1f2', true);
    }
  }

  // Retro CRT terminal desk drawing inside the 2x field
  function drawCrtTerminal(t, screenMode = 'green', wipeX = -1, glare = true) {
    // Desk surface in lower mid
    fillBox(0, 108, FW, 52, 0.18, 22, 48, 35, 1);
    for (let x = 0; x < FW; x += 6) {
      fillCapsule(x, 108, x + 2, 108, 0.8, 0.35, 55, 130, 88);
    }

    // CRT Outer Housing Bezel (crisp legible steel/phosphor rim even when unplugged)
    const bx = 18, by = 28, bw = 108, bh = 82;
    const isRed = screenMode === 'red';
    const isDead = screenMode === 'dead';
    const bezCol = isRed ? [220, 75, 80] : isDead ? [125, 160, 175] : [65, 130, 95];
    fillBox(bx, by, bw, bh, isDead ? 0.44 : 0.38, bezCol[0], bezCol[1], bezCol[2], 1);
    fillBox(bx + 3, by + 3, bw - 6, bh - 6, isDead ? 0.24 : 0.18, bezCol[0] * 0.45, bezCol[1] * 0.45, bezCol[2] * 0.45, 1);

    // Inner Curved Glass Viewport
    const sx = bx + 9, sy = by + 9, sw = bw - 18, sh = bh - 20;
    const scCol = isRed ? [255, 88, 92] : isDead ? [110, 155, 175] : [45, 245, 135];

    for (let y = sy; y < sy + sh; y++) {
      const ny = (y - sy) / sh;
      for (let x = sx; x < sx + sw; x++) {
        const nx = (x - sx) / sw;
        const distCenter = Math.hypot((nx - 0.5) * 2, (ny - 0.5) * 2);
        let lum = 0.08;
        if (!isDead) {
          // Mini ASCII corridor inside the monitor!
          const ax = Math.abs(nx - 0.5) * 2;
          const ay = Math.abs(ny - 0.45) * 2;
          const wallD = Math.max(ax, ay);
          lum = wallD < 0.25 ? 0.18 : Math.min(0.92, 0.26 + (1 - distCenter * 0.4) * 0.50);
          if (Math.abs(Math.sin((1 / Math.max(0.22, wallD)) * 2.5)) > 0.90) lum += 0.22;
          if (wipeX >= 0 && Math.abs(nx - wipeX) < 0.16) {
            lum += 0.35;
          }
          if (isRed) {
            lum *= 0.85 + 0.30 * Math.sin(t * 18 + y * 0.4);
          }
        } else {
          // Crisp glass reflection & subtle dark outline on unplugged CRT
          lum = Math.max(0.10, 0.26 - distCenter * 0.10);
        }
        if (glare && Math.abs((nx - 0.25) + (ny - 0.2) * 0.7) < 0.06) lum += 0.24;
        setPx(x, y, Math.min(0.96, lum), scCol[0] * lum, scCol[1] * lum, scCol[2] * lum, 1);
      }
    }

    // Power LED bottom-right of bezel
    if (screenMode === 'red') {
      fillDisk(bx + bw - 12, by + bh - 6, 2.2, 0.95, 255, 50, 60, 0.6);
    } else if (screenMode === 'green') {
      fillDisk(bx + bw - 12, by + bh - 6, 2.0, 0.90, 80, 255, 140, 0.6);
    }

    // Guard's keyboard silhouette on desk
    fillBox(26, 114, 92, 16, 0.28, 42, 85, 62, 1);
    for (let kx = 30; kx < 114; kx += 6) {
      fillBox(kx, 117, 4, 3, 0.55, 95, 195, 135, 0);
      fillBox(kx, 122, 4, 3, 0.50, 85, 175, 120, 0);
    }
  }

  // Draw an articulated ASCII hand (used for breaker, static wipe, cord pull, claws, POV ending)
  function drawAsciiHand(wx, wy, scale, angle, open = 0.5, col = [145, 235, 185], luma = 0.72) {
    const cos = Math.cos(angle);
    const sin = Math.sin(angle);
    const rot = (dx, dy) => [wx + (dx * cos - dy * sin) * scale, wy + (dx * sin + dy * cos) * scale];

    // Wrist & palm
    const [px, py] = rot(0, -10);
    fillCapsule(wx, wy, px, py, 6.2 * scale, luma, col[0], col[1], col[2]);

    // 5 fingers radiating cleanly
    const fingers = [
      { ang: -0.65 - open * 0.25, len: 10 },
      { ang: -0.25 - open * 0.10, len: 14 },
      { ang:  0.00,                len: 15.5 },
      { ang:  0.24 + open * 0.10,  len: 14 },
      { ang:  0.50 + open * 0.18,  len: 11.5 },
    ];
    for (const f of fingers) {
      const a = angle + f.ang;
      const bx = px + Math.sin(f.ang) * 4.5 * scale;
      const by = py - Math.cos(f.ang) * 3.0 * scale;
      const tx = bx + Math.sin(a) * f.len * scale;
      const ty = by - Math.cos(a) * f.len * scale;
      fillCapsule(bx, by, tx, ty, 1.8 * scale, luma * 1.12, col[0] * 1.15, col[1] * 1.15, col[2] * 1.15);
    }
  }

  function renderFrame(t) {
    const c = document.getElementById('c');
    const ctx = c.getContext('2d');
    const bi = activeBeatIndex(BEATS, t);
    const beat = BEATS[bi] || { start: 0, end: 3.5 };
    const u = Math.min(1, Math.max(0, (t - beat.start) / Math.max(0.1, beat.end - beat.start)));

    // Subtle base motion every frame (Law #12 & #28)
    let camX = Math.sin(t * 2.2) * 3.5;
    let camY = Math.cos(t * 1.7) * 3.5;
    let camRot = Math.sin(t * 1.3) * 0.006;
    let camZoom = 1.015 + u * 0.065;

    let renderOpts = {
      bgHex: 0x040907,
      edgeThreshold: 0.20,
      chromaShift: 0,
      glitchSeed: Math.floor(t * 30),
      glitchAmt: 0,
      bloomAmt: 0.36,
      vignetteCol: 'rgba(2,5,4,0.46)',
    };

    // Apply deterministic 7-frame alternating-sign impact KICKS on horror shocks!
    const tLights = 4.74;   // "slams"
    const tLunge  = 14.28;  // "three feet"
    const tCord   = 16.09;  // "ripped"
    const tRed    = 20.38;  // "blood red"
    const tCrawl  = 30.12;  // "crawl through"
    const tExit   = 32.55;  // "Found the exit"

    const kicks = [
      kickOffset(t, tLights, 18),
      kickOffset(t, tLunge, 34),
      kickOffset(t, tCord, 22),
      kickOffset(t, tRed, 32),
      kickOffset(t, tCrawl, 24),
      kickOffset(t, tExit, 36),
    ];
    let anyKick = false;
    for (const k of kicks) {
      if (k.active) {
        camX += k.x;
        camY += k.y;
        camRot += k.rot;
        anyKick = true;
      }
    }
    if (anyKick) {
      renderOpts.chromaShift = 4;
      renderOpts.glitchAmt = 0.85;
    }

    clearField(0.04, 10, 26, 18);

    // =========================================================================
    // SHOT 0 (0.04 - 4.66s): PARADOX HOOK — 3D ASCII Hallway + Two Extra Shadows
    // =========================================================================
    if (bi === 0) {
      const subCut = t >= 2.52; // Hard angle/zoom punch when he says "ASCII"
      if (subCut) {
        camZoom = 1.10 + ((t - 2.52) / 2.14) * 0.08;
        camRot = -0.04; // Dutch tilt
      } else {
        camZoom = 1.02 + (t / 2.52) * 0.06;
      }
      drawCorridor3D(t, {
        colBase: [32, 232, 122],
        colHi: [195, 255, 225],
        bright: 0.98,
        backGlow: 0.42, // Backlit fog doorway so both dark shadow figures read immediately at Frame 0!
        flashlight: true,
        zScroll: t * 0.35,
      });

      // Two tall unnatural pitch-dark shadows silhouetted against the glowing back wall
      const eyeGlow = t >= 3.38; // crimson eye flare on "two extra shadows"
      drawEntity(FW * 0.41, FH * 0.42, subCut ? 0.68 : 0.58, t, {
        shadowOnly: true,
        colBody: [4, 10, 8],
        colEdge: [28, 185, 98],
        eyeCol: eyeGlow ? [255, 55, 65] : [215, 255, 225],
        noEyes: false,
        luma: 0.02,
        phase: 0.0,
      });
      drawEntity(FW * 0.61, FH * 0.43, subCut ? 0.63 : 0.54, t, {
        shadowOnly: true,
        colBody: [4, 10, 8],
        colEdge: [28, 185, 98],
        eyeCol: eyeGlow ? [255, 55, 65] : [215, 255, 225],
        noEyes: false,
        luma: 0.02,
        phase: 1.9,
      });

      // Safe interior terminal corner tags (clear of zoom edges & top UI)
      putCellString(12, 12, 'CAM-03', '#6ee7b7');
      putCellString(55, 12, (Math.floor(t * 2) % 2 === 0) ? '* REC' : '  REC', '#ef4444');
    }

    // =========================================================================
    // SHOT 1 (4.66 - 6.19s): He slams on the overhead lights!
    // =========================================================================
    else if (bi === 1) {
      const snapped = t >= tLights;
      camZoom = snapped ? 1.14 + u * 0.08 : 1.04 + u * 0.06;
      if (snapped) {
        renderOpts.bgHex = 0x161206;
        clearField(0.18, 85, 68, 22);
      }
      // Industrial wall breaker box
      const col = snapped ? [252, 211, 77] : [60, 215, 130];
      fillBox(44, 34, 56, 74, snapped ? 0.62 : 0.38, col[0], col[1], col[2], 1);
      fillBox(52, 42, 40, 58, snapped ? 0.44 : 0.22, col[0] * 0.7, col[1] * 0.7, col[2] * 0.7, 1);
      // Lever moving down -> UP on snap
      const levY = snapped ? 54 : 84;
      fillCapsule(72, 70, 96, levY, 4.2, 0.92, 255, 248, 190);
      drawAsciiHand(108, snapped ? 66 : 96, 1.35, -0.55, 0.2, snapped ? [255, 235, 140] : [130, 240, 175], 0.80);

      if (snapped && (t - tLights) < 0.28) {
        // Spark burst around breaker
        const sp = (t - tLights) / 0.28;
        for (let k = 0; k < 10; k++) {
          const ang = k * 0.628;
          fillDisk(96 + Math.cos(ang) * sp * 28, 54 + Math.sin(ang) * sp * 28, 2.2, 0.98, 255, 252, 215, 0.5);
        }
      }
      putCellString(36, 22, snapped ? '[ LIGHTS: ON ]' : '[ LIGHTS: OFF ]', snapped ? '#fef08a' : '#6ee7b7', true);
    }

    // =========================================================================
    // SHOT 2 (6.19 - 8.00s): Empty concrete. Zero footsteps.
    // =========================================================================
    else if (bi === 2) {
      renderOpts.bgHex = 0x120f06;
      renderOpts.vignetteCol = 'rgba(18,14,4,0.35)';
      camZoom = 1.02 + u * 0.10;
      camX = Math.sin(u * Math.PI) * 14;
      drawCorridor3D(t, {
        colBase: [242, 198, 86],
        colHi: [255, 250, 220],
        bright: 1.05,
        flashlight: false,
        zScroll: 1.2 + u * 0.8,
        flicker: 0.96 + 0.04 * Math.sin(t * 50),
      });
      putCellString(7, 11, 'HALL-03', '#fde68a');
    }

    // =========================================================================
    // SHOT 3 (8.00 - 10.70s): Silent green symbols humming on CRT monitor
    // =========================================================================
    else if (bi === 3) {
      camZoom = 1.02 + u * 0.11;
      camRot = 0.02 - u * 0.03;
      drawCrtTerminal(t, 'green', -1, true);
      // Subtle ambient phosphor particles floating in dark office
      for (let i = 0; i < 24; i++) {
        const p = NOISE_PARTICLES[i];
        const py = (p.y + t * p.sp) % 108;
        addGlowPx(p.x, py, 0.14, 15, 75, 42);
      }
      putCellString(36, 17, 'CAM-03 // LIVE', '#34d399', true);
    }

    // =========================================================================
    // SHOT 4 (10.70 - 12.43s): He leans closer to wipe off the static
    // =========================================================================
    else if (bi === 4) {
      camZoom = 1.15 + u * 0.18;
      camY = 18;
      const wipeX = 0.15 + u * 0.72;
      drawCrtTerminal(t, 'green', wipeX, true);
      // Classic ASCII static noise streaks being wiped away
      const rng = seeded(Math.floor(t * 24) + 77);
      for (let r = 20; r < 40; r++) {
        for (let c0 = 15; c0 < 57; c0++) {
          const nx = (c0 - 15) / 42;
          if (nx > wipeX - 0.05 && rng() < 0.34) {
            putCellChar(c0, r, '@#%*=+;:.'[Math.floor(rng() * 9)], '#6ee7b7');
          }
        }
      }
      drawAsciiHand(28 + wipeX * 82, 92, 1.45, -0.25, 0.15, [155, 250, 195], 0.85);
    }

    // =========================================================================
    // SHOT 5 (12.43 - 14.02s): Wall inside the text blinks— (4f blink @ 13.33s!)
    // =========================================================================
    else if (bi === 5) {
      camZoom = 1.05 + u * 0.16;
      camRot = -0.03 * u;
      // Macro concrete wall ASCII matrix
      for (let y = 0; y < FH; y++) {
        for (let x = 0; x < FW; x++) {
          const brick = ((Math.floor(y / 14) % 2 === 0 ? x : x + 10) % 20 < 2) || (y % 14 < 2);
          const lum = brick ? 0.18 : 0.34 + 0.08 * Math.sin(x * 0.12 + y * 0.1 + t * 2);
          setPx(x, y, lum, 22, 165, 92, brick ? 1 : 0);
        }
      }
      // Eyes emerge out of the text wall, then 4-frame blink right at "blinks" (13.33s)!
      const eyeAppear = Math.min(1, u * 2.2);
      const blinkDt = t - 13.30; // 2-frame anticipation lead!
      const isBlinking = blinkDt >= 0 && blinkDt < 0.14;
      const eyeC = [255, 55, 68];

      if (eyeAppear > 0.2) {
        if (isBlinking) {
          fillCapsule(34, 66, 58, 66, 2.2, 0.96, eyeC[0], eyeC[1], eyeC[2]);
          fillCapsule(86, 66, 110, 66, 2.2, 0.96, eyeC[0], eyeC[1], eyeC[2]);
          putCellString(23, 33, '-----', '#ff6b6b', true);
          putCellString(49, 33, '-----', '#ff6b6b', true);
        } else {
          // Giant hyper-salient staring eyes carved inside the brick text
          fillDisk(46, 66, 13 * eyeAppear, 0.88, eyeC[0], eyeC[1], eyeC[2], 0.5);
          fillDisk(98, 66, 13 * eyeAppear, 0.88, eyeC[0], eyeC[1], eyeC[2], 0.5);
          fillDisk(46, 66, 5.2, 0.08, 12, 4, 6, 0);
          fillDisk(98, 66, 5.2, 0.08, 12, 4, 6, 0);
          fillDisk(46, 66, 1.8, 1.0, 255, 240, 240, 0);
          fillDisk(98, 66, 1.8, 1.0, 255, 240, 240, 0);
        }
      }
    }

    // =========================================================================
    // SHOT 6 (14.02 - 15.57s): Steps three feet out of the dark (LUNGE + KICK!)
    // =========================================================================
    else if (bi === 6) {
      const lunged = t >= tLunge - 0.04;
      renderOpts.bgHex = lunged ? 0x160406 : 0x050907;
      camZoom = lunged ? 1.12 + (u - 0.2) * 0.12 : 1.04 + u * 0.08;
      camRot = lunged ? 0.055 : -0.025;
      if (lunged) renderOpts.glitchAmt = 0.45;

      drawCorridor3D(t, {
        colBase: lunged ? [215, 44, 55] : [28, 215, 110],
        colHi: lunged ? [255, 200, 200] : [185, 255, 215],
        bright: lunged ? 0.88 : 0.85,
        backGlow: 0.05,
        flashlight: true,
        zScroll: lunged ? 2.4 : 0.8,
      });

      drawEntity(FW * 0.5, FH * 0.54, lunged ? 1.18 : 0.84, t, {
        colBody: lunged ? [38, 6, 12] : [14, 48, 30],
        colEdge: lunged ? [255, 95, 105] : [65, 245, 155],
        eyeCol: [255, 245, 248],
        jawOpen: lunged ? 1.0 : 0.2,
        luma: 0.78,
      });
    }

    // =========================================================================
    // SHOT 7 (15.57 - 18.15s): Luckily, he ripped the power cord straight out!
    // =========================================================================
    else if (bi === 7) {
      const pulled = t >= tCord;
      renderOpts.bgHex = pulled ? 0x050b12 : 0x08100c;
      camZoom = pulled ? 1.10 + u * 0.08 : 1.02 + u * 0.08;
      camRot = pulled ? -0.025 : 0.02;

      const colWall = pulled ? [68, 165, 235] : [55, 215, 130];
      // Wall outlet plate
      fillBox(44, 42, 42, 60, 0.42, colWall[0], colWall[1], colWall[2], 1);
      fillBox(57, 56, 16, 12, 0.12, 10, 22, 18, 1);
      fillBox(57, 76, 16, 12, 0.12, 10, 22, 18, 1);

      const pullDx = pulled ? Math.min(36, (t - tCord) * 65) : 0;
      const plugX = 64 + pullDx;
      // Prongs + heavy plug + hanging cord + hand
      fillBox(plugX - 8, 58, 9, 2.5, 0.90, 245, 250, 255, 0);
      fillBox(plugX - 8, 63, 9, 2.5, 0.90, 245, 250, 255, 0);
      fillBox(plugX, 54, 16, 16, 0.72, 180, 235, 255, 1);
      for (let k = 0; k < 18; k++) {
        const kx = plugX + 16 + k * 2.2;
        const ky = 62 + k * 3.2 + Math.sin(k * 0.6 + t * 14) * (pulled ? 4 : 1);
        fillDisk(kx, ky, 2.4, 0.65, colWall[0], colWall[1], colWall[2], 0.3);
      }
      drawAsciiHand(plugX + 18, 72, 1.35, -0.6, 0.15, [185, 240, 255], 0.82);

      // Electric sparks when snapped!
      if (pulled && (t - tCord) < 0.45) {
        const sp = (t - tCord) / 0.45;
        for (let i = 0; i < 8; i++) {
          const ang = (i - 3.5) * 0.32;
          const sx = 63 + Math.cos(ang) * sp * 22;
          const sy = 62 + Math.sin(ang) * sp * 22;
          fillDisk(sx, sy, 2.0, 0.98, 255, 252, 175, 0.4);
          putCellChar(Math.round(sx * 0.5), Math.round(sy * 0.5), '*+!'[i % 3], '#fef08a');
        }
      }
    }

    // =========================================================================
    // SHOT 8 (18.15 - 21.09s): Unluckily, unplugged screen stayed on -> BLOOD RED!
    // =========================================================================
    else if (bi === 8) {
      const turnedRed = t >= tRed - 0.12;
      renderOpts.bgHex = turnedRed ? 0x1a0305 : 0x050908;
      renderOpts.vignetteCol = turnedRed ? 'rgba(30,2,4,0.52)' : 'rgba(2,5,4,0.48)';
      camZoom = turnedRed ? 1.14 + (u - 0.5) * 0.16 : 1.03 + u * 0.08;
      camRot = turnedRed ? -0.055 : 0.015;
      if (turnedRed) renderOpts.glitchAmt = 0.65;

      drawCrtTerminal(t, turnedRed ? 'red' : 'dead', -1, true);
      // Dangling unplugged cord off left side of desk
      for (let k = 0; k < 14; k++) {
        fillDisk(18 - k * 1.1, 95 + k * 2.4 + Math.sin(k + t * 5) * 1.5, 1.8, 0.48, turnedRed ? 240 : 90, 80, 95, 0.3);
      }

      if (turnedRed) {
        // Skull emerging inside CRT glass!
        fillDisk(72, 62, 14, 0.85, 255, 70, 80, 0.4);
        fillDisk(66, 59, 3.2, 0.06, 20, 4, 6, 0);
        fillDisk(78, 59, 3.2, 0.06, 20, 4, 6, 0);
        fillDisk(66, 59, 1.2, 1.0, 255, 240, 240, 0);
        fillDisk(78, 59, 1.2, 1.0, 255, 240, 240, 0);
        putCellString(36, 35, 'VVVVV', '#fff1f2', true);
        putCellString(36, 17, '[ NO POWER SOURCE ]', '#ff6b6b', true);
      } else {
        putCellString(36, 17, '[ POWER: 0V ]', '#94a3b8', true);
      }
    }

    // =========================================================================
    // SHOT 9 (21.09 - 24.12s): "You see," — normal camera traps light (sealed photo)
    // =========================================================================
    else if (bi === 9) {
      renderOpts.bgHex = 0x040911;
      camZoom = 1.02 + u * 0.10;
      camRot = 0.015 * Math.sin(u * Math.PI);

      // Sealed cyan photographic glass frame
      const fx = 28, fy = 30, fw = 88, fh = 76;
      fillBox(fx, fy, fw, fh, 0.72, 56, 189, 248, 1);
      fillBox(fx + 5, fy + 5, fw - 10, fh - 10, 0.22, 14, 58, 92, 1);
      // Light rays bouncing cleanly off the sealed glass
      for (let i = 0; i < 5; i++) {
        const yOff = 44 + i * 11;
        const pulse = ((t * 1.6 + i * 0.2) % 1);
        const rx = 8 + pulse * 18;
        fillCapsule(rx, yOff - 6, rx + 8, yOff, 1.6, 0.92, 186, 230, 253);
        fillCapsule(rx + 8, yOff, rx, yOff + 6, 1.4, 0.75, 125, 211, 252);
      }
      // Trapped still figure inside the glass
      drawEntity(72, 74, 0.65, 0, { colBody: [28, 98, 145], colEdge: [125, 211, 252], noEyes: true, luma: 0.55 });
      putCellString(36, 12, '[ SEALED GLASS ]', '#7dd3fc', true);
    }

    // =========================================================================
    // SHOT 10 (24.12 - 27.40s): Raw ASCII symbols split the picture into bars
    // =========================================================================
    else if (bi === 10) {
      camZoom = 1.05 + u * 0.12;
      const spread = u * 16;
      // Vertical ASCII lattice bars bowing apart from center!
      for (let colIdx = -5; colIdx <= 5; colIdx++) {
        const side = colIdx === 0 ? 1 : Math.sign(colIdx);
        const gap = Math.abs(colIdx) < 2 ? spread * side : spread * 0.45 * side;
        const bx = FW * 0.5 + colIdx * 10 + gap;
        const glow = Math.abs(colIdx) <= 1 ? 0.92 : 0.60;
        const cr = colIdx === 0 || Math.abs(colIdx) === 1 ? 245 : 42;
        const cg = colIdx === 0 || Math.abs(colIdx) === 1 ? 75 : 225;
        const cb = colIdx === 0 || Math.abs(colIdx) === 1 ? 95 : 135;
        fillCapsule(bx, 20, bx + gap * 0.25, 114, 2.2, glow, cr, cg, cb);
      }
      // Dark void peeking behind split bars
      if (u > 0.35) {
        fillBox(FW * 0.5 - spread * 0.8, 30, spread * 1.6, 76, 0.06, 22, 4, 8, 0);
      }
      putCellString(36, 12, '[ CHAR GRID: OPEN ]', '#34d399', true);
    }

    // =========================================================================
    // SHOT 11 (27.40 - 30.73s): Gaps big enough for something to crawl through!
    // =========================================================================
    else if (bi === 11) {
      renderOpts.bgHex = 0x120306;
      camZoom = 1.08 + u * 0.18;
      camRot = -0.04 * u;
      const openAmt = 0.45 + 0.55 * Math.min(1, u * 1.25);
      const gapW = 22 + openAmt * 26;

      // Crimson abyssal tunnel behind the pried-apart text bars
      drawCorridor3D(t, {
        colBase: [230, 48, 65],
        colHi: [255, 205, 205],
        bright: 0.95,
        zScroll: t * 1.4,
      });

      // Vertical glowing green/white text bars bending outward left & right
      for (let i = 0; i < 4; i++) {
        const lx = FW * 0.5 - gapW - i * 11;
        const rx = FW * 0.5 + gapW + i * 11;
        fillCapsule(lx + 4, 16, lx - 4, 118, 2.5, 0.88, 65, 240, 150);
        fillCapsule(rx - 4, 16, rx + 4, 118, 2.5, 0.88, 65, 240, 150);
      }

      // Pale claws gripping the inner bars and prying them open!
      const clawReach = Math.min(1, Math.max(0, (u - 0.15) * 1.5));
      if (clawReach > 0.05) {
        drawAsciiHand(FW * 0.5 - gapW + 4, 68, 1.35 * clawReach, 1.4, 0.65, [255, 195, 195], 0.92);
        drawAsciiHand(FW * 0.5 + gapW - 4, 68, 1.35 * clawReach, -1.4, 0.65, [255, 195, 195], 0.92);
        // Eyes peering from center gap
        fillDisk(FW * 0.5 - 6, 58, 2.8, 0.98, 255, 245, 245, 0.4);
        fillDisk(FW * 0.5 + 6, 58, 2.8, 0.98, 255, 245, 245, 0.4);
      }
    }

    // =========================================================================
    // SHOT 12 (30.73 - 32.55s): His dead monitor types one final line:
    // =========================================================================
    else if (bi === 12) {
      renderOpts.bgHex = 0x140305;
      camZoom = 1.18 + u * 0.14;
      drawCrtTerminal(t, 'red', -1, false);

      // Character-by-character typing inside the bezel!
      const line1 = '> DOORWAY: OPEN';
      const charsVis = Math.min(line1.length, Math.floor(u * (line1.length + 3)));
      const cursor = (Math.floor(t * 6) % 2 === 0) ? '_' : ' ';
      putCellString(21, 24, '> CAM-03: BREACHED', '#fca5a5');
      putCellString(21, 28, line1.slice(0, charsVis) + cursor, '#ffffff');
    }

    // =========================================================================
    // SHOT 13 (32.55 - 33.86s): [ENTITY] "Found the exit." (FULL SCREEN SCARE!)
    // =========================================================================
    else if (bi === 13) {
      renderOpts.bgHex = 0x240508;
      renderOpts.vignetteCol = 'rgba(24,0,0,0.52)';
      renderOpts.glitchAmt = 0.72;
      renderOpts.chromaShift = 5;
      renderOpts.bloomAmt = 0.48;
      camZoom = 1.06 + u * 0.20;
      camRot = Math.sin(t * 28) * 0.025;

      // High-contrast pulsing crimson static background so skull silhouette & video luma pop cleanly
      for (let y = 0; y < FH; y++) {
        for (let x = 0; x < FW; x++) {
          const rDist = Math.hypot((x - FW * 0.5) / (FW * 0.55), (y - FH * 0.42) / (FH * 0.5));
          const wave = 0.26 + 0.16 * Math.sin(rDist * 14.0 - t * 22.0);
          setPx(x, y, Math.max(0.14, wave), 225, 62, 68, 0);
        }
      }

      // Full-screen screaming ASCII skull / entity face bursting straight at camera!
      const s = 1.65 + u * 0.48;
      fillDisk(FW * 0.5, FH * 0.36, 26 * s, 0.88, 255, 118, 115, 0.35);
      fillBox(FW * 0.5 - 13 * s, FH * 0.36, 26 * s, 25 * s, 0.78, 255, 92, 95, 1);

      // Deep hollow eye sockets with blazing pinprick pupils
      fillDisk(FW * 0.5 - 11 * s, FH * 0.33, 6.8 * s, 0.03, 18, 4, 6, 0);
      fillDisk(FW * 0.5 + 11 * s, FH * 0.33, 6.8 * s, 0.03, 18, 4, 6, 0);
      fillDisk(FW * 0.5 - 11 * s, FH * 0.33, 2.8, 1.0, 255, 255, 255, 0, 0);
      fillDisk(FW * 0.5 + 11 * s, FH * 0.33, 2.8, 1.0, 255, 255, 255, 0, 0);
      putCellString(Math.round((FW * 0.5 - 11 * s) * 0.5), Math.round((FH * 0.33) * 0.5), '(@)', '#ffffff', true);
      putCellString(Math.round((FW * 0.5 + 11 * s) * 0.5), Math.round((FH * 0.33) * 0.5), '(@)', '#ffffff', true);

      // Unhinged cavernous jaw
      fillCapsule(FW * 0.5, FH * 0.43, FW * 0.5, FH * 0.56, 9.5 * s, 0.03, 18, 4, 6);
      putCellString(36, 34, 'VVVVVVVVV', '#ffffff', true);
      putCellString(36, 43, '^^^^^^^^^', '#ffffff', true);
    }

    // =========================================================================
    // SHOT 14 (33.86 - 36.83s): POV hands already turning into ASCII!
    // =========================================================================
    else {
      // Starts dark blue-slate hallway floor, then sweeps wave-by-wave into glowing pure ASCII!
      const waveU = Math.max(0, Math.min(1, (t - 34.45) / 1.85));
      renderOpts.bgHex = waveU > 0.45 ? 0x050e0a : 0x06090f;
      camZoom = 1.04 + u * 0.14;
      camY = 8 - u * 10;

      // Dark floor planks / corridor perspective behind his hands
      for (let y = 0; y < FH; y++) {
        for (let x = 0; x < FW; x++) {
          const fl = Math.max(0.05, 0.14 * (y / FH));
          setPx(x, y, fl, 24, 48, 42, 0);
        }
      }

      // Guard's trembling left & right hands held out in POV
      const trembleX = Math.sin(t * 36) * 1.4;
      const trembleY = Math.cos(t * 31) * 1.4;
      drawAsciiHand(40 + trembleX, 106 + trembleY, 1.85, -0.22, 0.6, [175, 198, 225], 0.72);
      drawAsciiHand(104 - trembleX, 106 - trembleY, 1.85, 0.22, 0.6, [175, 198, 225], 0.72);

      // Wave-by-wave classic ASCII infection sweeping down from fingertips -> wrists!
      const sweepY = 48 + waveU * 76; // 2x coords (rows 24 -> 62)
      const rng = seeded(Math.floor(t * 24) + 19);
      for (let row = 16; row < 64; row++) {
        const fy = row * 2;
        if (fy <= sweepY) {
          for (let col = 8; col < 64; col++) {
            const fx = col * 2;
            const lum = A.fLuma[fy * FW + fx];
            if (lum > 0.25) {
              const isCrimson = rng() < 0.24 || (waveU > 0.78 && rng() < 0.40);
              const colHex = isCrimson ? '#ff4455' : '#34d399';
              const gCh = '@#%&$*+=?!:.'[Math.floor(rng() * 12)];
              putCellChar(col, row, gCh, colHex);
            }
          }
        }
      }

      // On the final 0.55s ("ASCII."), crimson eyes flicker open in the background dark!
      if (waveU > 0.70) {
        fillDisk(63, 30, 2.8, 0.98, 255, 55, 70, 0.4);
        fillDisk(81, 30, 2.8, 0.98, 255, 55, 70, 0.4);
        renderOpts.glitchAmt = 0.40;
      }
    }

    presentFrame(ctx, camX, camY, camRot, camZoom, SUB_CHUNKS, t, renderOpts);
  }

  window.renderFrame = renderFrame;
  window.initCoreShort = init;
})();
