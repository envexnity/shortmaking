/* Orbit 2D Space Survival Renderer (1920x1080 @ 30fps default)
 * Renders all 8 Orbit scene archetypes deterministically from time t (sec) and progress u (0..1).
 */
(function () {
  const DEFAULT_W = 1920;
  const DEFAULT_H = 1080;

  // Helpers
  const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
  const lerp = (a, b, t) => a + (b - a) * t;
  const smoothstep = (t) => {
    t = clamp(t);
    return t * t * (3 - 2 * t);
  };
  const easeOutCubic = (t) => 1 - Math.pow(1 - clamp(t), 3);
  const easeOutBack = (t) => {
    t = clamp(t);
    const c1 = 1.70158, c3 = c1 + 1;
    return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
  };
  const seeded = (seed) => {
    let s = seed | 0 || 12345;
    return () => {
      s = (s * 1664525 + 1013904223) | 0;
      return ((s >>> 0) / 4294967296);
    };
  };

  const FONT_DISPLAY = 'Impact, "Arial Narrow", "Bahnschrift Condensed", sans-serif';
  const FONT_UI = '"Segoe UI", Inter, system-ui, sans-serif';
  const FONT_MONO = 'Consolas, "Courier New", monospace';

  // Loaded external NASA images keyed by key
  const IMAGES = {};
  let SCENES = [];
  let BEATS = [];

  function buildTimeline(scenes) {
    let t = 0;
    return scenes.map((s, idx) => {
      const dur = Math.max(0.5, Number(s.dur) || 4);
      const start = t;
      t += dur;
      return { ...s, idx, start, end: t, dur };
    });
  }

  // Background starfield
  const STARS = (() => {
    const r = seeded(2026);
    return Array.from({ length: 240 }, () => ({
      x: r() * 1920,
      y: r() * 1080,
      size: 0.8 + r() * 2.1,
      alpha: 0.2 + r() * 0.75,
      speed: 0.8 + r() * 3.0,
      phase: r() * Math.PI * 2,
    }));
  })();

  const DUST = (() => {
    const r = seeded(8842);
    return Array.from({ length: 55 }, () => ({
      x: r() * 1920,
      y: r() * 1080,
      r: 1.2 + r() * 2.8,
      vx: 10 + r() * 26,
      vy: -5 + r() * 10,
      alpha: 0.08 + r() * 0.22,
    }));
  })();

  function drawVignette(ctx, W, H, strength = 0.65) {
    const g = ctx.createRadialGradient(W * 0.5, H * 0.5, W * 0.24, W * 0.5, H * 0.5, W * 0.72);
    g.addColorStop(0, 'rgba(0,0,0,0)');
    g.addColorStop(1, `rgba(0,0,0,${strength})`);
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);
  }

  function drawSpaceBg(ctx, W, H, t, opts = {}) {
    const g = ctx.createLinearGradient(0, 0, W * 0.4, H);
    g.addColorStop(0, '#04060d');
    g.addColorStop(0.55, '#070b18');
    g.addColorStop(1, '#0d1428');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);

    // Optional sun rays top-left (matching hd_005.jpg)
    if (opts.sunRays !== false) {
      ctx.save();
      const sx = 34, sy = 96;
      const sunGlow = ctx.createRadialGradient(sx, sy, 6, sx, sy, 380);
      sunGlow.addColorStop(0, 'rgba(255,245,215,0.45)');
      sunGlow.addColorStop(0.18, 'rgba(255,210,145,0.12)');
      sunGlow.addColorStop(1, 'rgba(255,210,145,0)');
      ctx.fillStyle = sunGlow;
      ctx.fillRect(0, 0, 500, 500);

      // Subtle star sun disc
      ctx.fillStyle = 'rgba(220,224,230,0.45)';
      ctx.beginPath();
      ctx.arc(sx, sy, 26, 0, Math.PI * 2);
      ctx.fill();

      // Subtle ray lines
      ctx.strokeStyle = 'rgba(255,255,255,0.06)';
      ctx.lineWidth = 2;
      for (let i = 0; i < 8; i++) {
        const ang = -0.3 + i * 0.24 + Math.sin(t * 0.4 + i) * 0.015;
        ctx.beginPath();
        ctx.moveTo(sx, sy);
        ctx.lineTo(sx + Math.cos(ang) * 460, sy + Math.sin(ang) * 460);
        ctx.stroke();
      }
      ctx.restore();
    }

    // Stars with gentle parallax & twinkle
    for (const st of STARS) {
      const px = (st.x + t * 2.5) % W;
      const a = st.alpha * (0.65 + 0.35 * Math.sin(t * st.speed + st.phase));
      ctx.fillStyle = `rgba(235, 244, 255, ${a.toFixed(3)})`;
      ctx.beginPath();
      ctx.arc(px, st.y, st.size, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  function drawPlanetSphere(ctx, cx, cy, R, kind = 'mars', t = 0) {
    ctx.save();
    // Outer atmospheric glow
    const glowColor = kind === 'earth' ? 'rgba(86, 165, 255, 0.28)'
      : kind === 'venus' ? 'rgba(245, 195, 95, 0.24)'
      : 'rgba(224, 114, 62, 0.26)';
    const atm = ctx.createRadialGradient(cx, cy, R * 0.85, cx, cy, R * 1.48);
    atm.addColorStop(0, glowColor);
    atm.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = atm;
    ctx.beginPath();
    ctx.arc(cx, cy, R * 1.48, 0, Math.PI * 2);
    ctx.fill();

    // Clip to sphere
    ctx.beginPath();
    ctx.arc(cx, cy, R, 0, Math.PI * 2);
    ctx.clip();

    if (kind === 'earth') {
      const og = ctx.createRadialGradient(cx - R * 0.42, cy - R * 0.35, R * 0.1, cx, cy, R * 1.2);
      og.addColorStop(0, '#3b8df2');
      og.addColorStop(0.6, '#1554a3');
      og.addColorStop(1, '#071b3d');
      ctx.fillStyle = og;
      ctx.fillRect(cx - R, cy - R, R * 2, R * 2);

      // Organic layered continents (drifting very slightly for motion)
      const shift = Math.sin(t * 0.2) * R * 0.04;
      ctx.fillStyle = '#3b9453';
      const blobs = [
        [-0.42, -0.32, 0.22, 0.26, 0.4],
        [-0.28, -0.18, 0.16, 0.22, -0.3],
        [-0.16, 0.18, 0.15, 0.26, 0.3],
        [0.18, -0.22, 0.28, 0.18, -0.2],
        [0.34, -0.05, 0.24, 0.22, 0.25],
        [0.24, 0.22, 0.18, 0.15, -0.4],
        [0.48, 0.32, 0.14, 0.11, 0.2],
      ];
      for (const [bx, by, rx, ry, rot] of blobs) {
        ctx.save();
        ctx.translate(cx + bx * R + shift, cy + by * R);
        ctx.rotate(rot);
        ctx.beginPath();
        ctx.ellipse(0, 0, rx * R, ry * R, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      }
      // Atmospheric clouds
      ctx.fillStyle = 'rgba(245,250,255,0.52)';
      for (let i = 0; i < 6; i++) {
        ctx.beginPath();
        ctx.ellipse(cx + (-0.35 + i * 0.16) * R + shift * 1.4, cy + Math.sin(i * 1.9) * 0.45 * R, R * 0.26, R * 0.036, 0.08, 0, Math.PI * 2);
        ctx.fill();
      }
      // Ice cap
      ctx.fillStyle = 'rgba(240,248,255,0.85)';
      ctx.fillRect(cx - R, cy - R, R * 2, R * 0.12);
    } else if (kind === 'venus') {
      const vg = ctx.createRadialGradient(cx - R * 0.42, cy - R * 0.3, R * 0.12, cx, cy, R * 1.15);
      vg.addColorStop(0, '#f4cf7a');
      vg.addColorStop(0.65, '#c48633');
      vg.addColorStop(1, '#4a2909');
      ctx.fillStyle = vg;
      ctx.fillRect(cx - R, cy - R, R * 2, R * 2);

      const shift = Math.sin(t * 0.25) * R * 0.05;
      for (let i = 0; i < 9; i++) {
        ctx.fillStyle = i % 2 === 0 ? 'rgba(255,232,175,0.22)' : 'rgba(92,48,12,0.22)';
        ctx.beginPath();
        ctx.ellipse(cx + shift, cy + (-0.75 + i * 0.19) * R, R * 1.15, R * 0.09, -0.06, 0, Math.PI * 2);
        ctx.fill();
      }
    } else {
      // MARS (faithful to hd_005.jpg: rich rust, lighter patches, rim craters, polar ice caps)
      const mg = ctx.createRadialGradient(cx - R * 0.48, cy - R * 0.28, R * 0.1, cx + R * 0.15, cy, R * 1.18);
      mg.addColorStop(0, '#de7b47');
      mg.addColorStop(0.52, '#ad4d26');
      mg.addColorStop(0.85, '#662711');
      mg.addColorStop(1, '#260b04');
      ctx.fillStyle = mg;
      ctx.fillRect(cx - R, cy - R, R * 2, R * 2);

      const prng = seeded(kind === 'mars' ? 911 : 333);
      const drift = Math.sin(t * 0.18) * R * 0.025;
      // Soft dust/albedo patches
      for (let i = 0; i < 24; i++) {
        const px = (prng() * 1.6 - 0.8) * R + drift;
        const py = (prng() * 1.6 - 0.8) * R;
        const rx = (0.12 + prng() * 0.26) * R;
        const ry = (0.04 + prng() * 0.11) * R;
        ctx.fillStyle = prng() > 0.45 ? 'rgba(232, 148, 96, 0.22)' : 'rgba(65, 22, 10, 0.24)';
        ctx.beginPath();
        ctx.ellipse(cx + px, cy + py, rx, ry, 0, 0, Math.PI * 2);
        ctx.fill();
      }

      // Subtle ringed craters matching hd_005.jpg
      for (let i = 0; i < 12; i++) {
        const crx = cx + (prng() * 1.4 - 0.7) * R + drift;
        const cry = cy + (prng() * 1.4 - 0.7) * R;
        const cr = (0.022 + prng() * 0.048) * R;
        ctx.strokeStyle = 'rgba(42, 14, 6, 0.45)';
        ctx.lineWidth = Math.max(1.5, R * 0.008);
        ctx.beginPath();
        ctx.arc(crx, cry, cr, 0, Math.PI * 2);
        ctx.stroke();
      }

      // North & South Polar Ice Caps
      ctx.fillStyle = 'rgba(222, 226, 232, 0.78)';
      ctx.fillRect(cx - R, cy - R, R * 2, R * 0.088);
      ctx.fillStyle = 'rgba(210, 215, 224, 0.48)';
      ctx.fillRect(cx - R, cy + R * 0.92, R * 2, R * 0.085);
    }

    // Terminator shade shadow crescent on right side
    const sh = ctx.createLinearGradient(cx - R * 0.2, cy, cx + R, cy);
    sh.addColorStop(0, 'rgba(0,0,0,0)');
    sh.addColorStop(0.55, 'rgba(10,4,2,0.18)');
    sh.addColorStop(1, 'rgba(0,0,0,0.72)');
    ctx.fillStyle = sh;
    ctx.fillRect(cx - R, cy - R, R * 2, R * 2);

    ctx.restore();

    // Crisp sunward atmospheric arc on left limb
    ctx.save();
    ctx.strokeStyle = kind === 'earth' ? 'rgba(130, 195, 255, 0.85)'
      : kind === 'venus' ? 'rgba(255, 218, 130, 0.85)'
      : 'rgba(247, 154, 102, 0.82)';
    ctx.lineWidth = Math.max(3, R * 0.015);
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.arc(cx, cy, R - 1, Math.PI * 0.72, Math.PI * 1.62);
    ctx.stroke();
    ctx.restore();
  }

  function drawAstronaut(ctx, x, y, opts = {}) {
    const scale = opts.scale || 1.0;
    const t = opts.t || 0;
    const walk = opts.walk ? Math.sin(t * 4.8) : 0;
    const flip = opts.flip ? -1 : 1;
    const tilt = opts.tilt || 0;
    const beamLen = opts.beamLen ?? 250;

    ctx.save();
    ctx.translate(x, y);
    ctx.scale(scale * flip, scale);
    ctx.rotate(tilt);

    // Headlamp conical beam
    if (beamLen > 0) {
      const flicker = 0.96 + 0.04 * Math.sin(t * 10);
      const bg = ctx.createLinearGradient(12, -32, beamLen, 10);
      bg.addColorStop(0, `rgba(255, 248, 224, ${(0.28 * flicker).toFixed(3)})`);
      bg.addColorStop(0.55, `rgba(255, 242, 200, ${(0.10 * flicker).toFixed(3)})`);
      bg.addColorStop(1, 'rgba(255, 242, 200, 0)');
      ctx.fillStyle = bg;
      ctx.beginPath();
      ctx.moveTo(10, -34);
      ctx.lineTo(beamLen, -75);
      ctx.lineTo(beamLen, 55);
      ctx.lineTo(10, -22);
      ctx.closePath();
      ctx.fill();
    }

    // Contact shadow if standing on surface
    if (opts.shadow) {
      ctx.fillStyle = 'rgba(0,0,0,0.42)';
      ctx.beginPath();
      ctx.ellipse(0, 32, 22, 6, 0, 0, Math.PI * 2);
      ctx.fill();
    }

    // Back leg
    ctx.save();
    ctx.translate(-3, 6);
    ctx.rotate(-walk * 0.45);
    ctx.fillStyle = '#cbd5e1';
    ctx.beginPath();
    ctx.roundRect(-6, 0, 12, 22, 5);
    ctx.fill();
    ctx.fillStyle = '#94a3b8';
    ctx.beginPath();
    ctx.roundRect(-6, 18, 16, 8, 3);
    ctx.fill();
    ctx.restore();

    // Backpack PLSS
    ctx.fillStyle = '#cbd5e1';
    ctx.beginPath();
    ctx.roundRect(-24, -22, 16, 30, 4);
    ctx.fill();
    ctx.fillStyle = '#94a3b8';
    ctx.fillRect(-24, -18, 5, 22);

    // Front leg
    ctx.save();
    ctx.translate(4, 6);
    ctx.rotate(walk * 0.45);
    ctx.fillStyle = '#f1f5f9';
    ctx.beginPath();
    ctx.roundRect(-6, 0, 12, 22, 5);
    ctx.fill();
    ctx.fillStyle = '#cbd5e1';
    ctx.beginPath();
    ctx.roundRect(-5, 18, 17, 8, 3);
    ctx.fill();
    ctx.restore();

    // Torso
    ctx.fillStyle = '#f8fafc';
    ctx.beginPath();
    ctx.roundRect(-12, -21, 24, 30, 8);
    ctx.fill();
    // Red mission patch bar
    ctx.fillStyle = '#ef4444';
    ctx.fillRect(-6, -13, 10, 4);

    // Front arm
    ctx.save();
    ctx.translate(6, -15);
    ctx.rotate(walk * 0.35 - 0.35);
    ctx.fillStyle = '#e2e8f0';
    ctx.beginPath();
    ctx.roundRect(-4, 0, 10, 19, 5);
    ctx.fill();
    ctx.restore();

    // Helmet
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(2, -31, 16, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#cbd5e1';
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // Visor
    const vg = ctx.createLinearGradient(0, -40, 16, -24);
    vg.addColorStop(0, '#92400e');
    vg.addColorStop(0.5, '#1e293b');
    vg.addColorStop(1, '#090d16');
    ctx.fillStyle = vg;
    ctx.beginPath();
    ctx.ellipse(9, -31, 9, 10, 0.08, 0, Math.PI * 2);
    ctx.fill();

    // Visor shine highlight
    ctx.fillStyle = 'rgba(255, 224, 170, 0.55)';
    ctx.beginPath();
    ctx.ellipse(10, -36, 3.2, 1.8, -0.5, 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();
  }

  function drawYouArrow(ctx, youX, youY, targetX, targetY, reveal = 1) {
    if (reveal <= 0.02) return;
    ctx.save();
    ctx.globalAlpha = clamp(reveal);
    ctx.font = `900 92px ${FONT_DISPLAY}`;
    ctx.fillStyle = '#ef4444';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('YOU', youX, youY);

    // Curved red arrow pointing down-right toward target
    const sx = youX + 5;
    const sy = youY + 52;
    const cx = youX + (targetX - youX) * 0.25;
    const cy = targetY - 12;
    const ex = targetX;
    const ey = targetY;

    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 7;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(sx, sy);
    ctx.quadraticCurveTo(cx, cy, ex, ey);
    ctx.stroke();

    // Arrowhead angle at t=1 from tangent (ex - cx, ey - cy)
    const ang = Math.atan2(ey - cy, ex - cx);
    ctx.fillStyle = '#ef4444';
    ctx.beginPath();
    ctx.moveTo(ex + Math.cos(ang) * 14, ey + Math.sin(ang) * 14);
    ctx.lineTo(ex - Math.cos(ang - 0.55) * 20, ey - Math.sin(ang - 0.55) * 20);
    ctx.lineTo(ex - Math.cos(ang + 0.55) * 20, ey - Math.sin(ang + 0.55) * 20);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }

  function drawBottomHeadline(ctx, W, whiteText, yellowText, y = 935, reveal = 1) {
    if (!whiteText && !yellowText) return;
    ctx.save();
    ctx.globalAlpha = clamp(reveal);
    ctx.font = `900 74px ${FONT_DISPLAY}`;
    const wPart = whiteText ? whiteText + (yellowText ? ' ' : '') : '';
    const wWidth = ctx.measureText(wPart).width;
    const yWidth = yellowText ? ctx.measureText(yellowText).width : 0;
    const total = wWidth + yWidth;
    const startX = (W - total) / 2;

    ctx.shadowColor = 'rgba(0,0,0,0.85)';
    ctx.shadowBlur = 18;
    ctx.shadowOffsetY = 4;
    ctx.textAlign = 'left';
    ctx.textBaseline = 'middle';

    if (wPart) {
      ctx.fillStyle = '#f8fafc';
      ctx.fillText(wPart, startX, y);
    }
    if (yellowText) {
      ctx.fillStyle = '#f5c842';
      ctx.fillText(yellowText, startX + wWidth, y);
    }
    ctx.restore();
  }

  function drawSurface(ctx, W, H, t, palette = 'day', scrollSpeed = 12) {
    const isCold = palette === 'cold';
    const sky = ctx.createLinearGradient(0, 0, 0, H * 0.65);
    if (isCold) {
      sky.addColorStop(0, '#0a080d');
      sky.addColorStop(0.65, '#3b2e3f');
      sky.addColorStop(1, '#58485b');
    } else {
      sky.addColorStop(0, '#120703');
      sky.addColorStop(0.55, '#59240f');
      sky.addColorStop(1, '#984620');
    }
    ctx.fillStyle = sky;
    ctx.fillRect(0, 0, W, H);

    // Subtle dusty horizon band matching hd_220.jpg / hd_234.jpg
    ctx.fillStyle = isCold ? 'rgba(184, 152, 130, 0.25)' : 'rgba(225, 146, 94, 0.26)';
    ctx.fillRect(0, 495, W, 92);

    const layers = isCold
      ? [
          { y0: 615, amp: 48, col: '#5a4d5c', f1: 0.0042, f2: 0.011, spd: 0.25 },
          { y0: 685, amp: 52, col: '#433846', f1: 0.0055, f2: 0.014, spd: 0.5 },
          { y0: 785, amp: 44, col: '#2d232f', f1: 0.0068, f2: 0.017, spd: 0.85 },
          { y0: 910, amp: 34, col: '#171019', f1: 0.0085, f2: 0.022, spd: 1.25 },
        ]
      : [
          { y0: 610, amp: 52, col: '#a44d28', f1: 0.0042, f2: 0.011, spd: 0.25 },
          { y0: 690, amp: 52, col: '#7c3417', f1: 0.0055, f2: 0.014, spd: 0.5 },
          { y0: 790, amp: 44, col: '#4f1e0c', f1: 0.0068, f2: 0.017, spd: 0.85 },
          { y0: 915, amp: 34, col: '#240c04', f1: 0.0085, f2: 0.022, spd: 1.25 },
        ];

    const ridgeHeightAt = (layerIdx, x) => {
      const L = layers[layerIdx];
      const px = x + t * scrollSpeed * L.spd;
      return L.y0
        - Math.sin(px * L.f1 + layerIdx * 1.4) * L.amp
        - Math.sin(px * L.f2 + layerIdx * 3.1) * (L.amp * 0.42);
    };

    for (let li = 0; li < layers.length; li++) {
      ctx.fillStyle = layers[li].col;
      ctx.beginPath();
      ctx.moveTo(0, H);
      for (let x = 0; x <= W; x += 16) {
        ctx.lineTo(x, ridgeHeightAt(li, x));
      }
      ctx.lineTo(W, H);
      ctx.closePath();
      ctx.fill();
    }

    // Drifting airborne dust particles
    ctx.save();
    for (const d of DUST) {
      const dx = ((d.x + t * d.vx * (isCold ? 0.6 : 1.2)) % (W + 40)) - 20;
      const dy = (d.y + t * d.vy + H) % H;
      ctx.fillStyle = isCold ? `rgba(210,220,240,${d.alpha * 0.7})` : `rgba(255,190,145,${d.alpha})`;
      ctx.beginPath();
      ctx.arc(dx, dy, d.r, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();

    return ridgeHeightAt;
  }

  // ==================== SCENE TYPE 1: orbit_establish ====================
  function renderOrbitEstablish(ctx, W, H, s, t, u) {
    ctx.save();
    const zoom = 1 + u * (s.zoomAmt ?? 0.035);
    ctx.translate(W * 0.5, H * 0.5);
    ctx.scale(zoom, zoom);
    ctx.translate(-W * 0.5, -H * 0.5);

    drawSpaceBg(ctx, W, H, t, { sunRays: s.sunRays !== false });

    if (s.horizonMode) {
      // Bottom curved Mars limb horizon (matching hd_186.jpg top-right "WHAT KILLS YOU FIRST?")
      const cx = W * 0.5;
      const cy = H + 760;
      const R = 1040;
      drawPlanetSphere(ctx, cx, cy, R, s.planet || 'mars', t);
      drawAstronaut(ctx, W * 0.5, H * 0.5 + 115 + Math.sin(t * 1.5) * 4, {
        scale: 1.05,
        t,
        beamLen: 360,
        shadow: true,
      });
    } else {
      // Giant planet sphere on right
      const cx = s.planetX ?? 1380;
      const cy = s.planetY ?? 545;
      const R = s.planetR ?? 465;
      drawPlanetSphere(ctx, cx, cy, R, s.planet || 'mars', t);

      // Tiny drifting astronaut ("YOU")
      const ax = (s.astroX ?? 490) + Math.sin(t * 0.7) * 6;
      const ay = (s.astroY ?? 650) + Math.sin(t * 1.5) * 5;
      drawAstronaut(ctx, ax, ay, {
        scale: s.astroScale ?? 0.9,
        t,
        tilt: Math.sin(t * 1.1) * 0.05,
        beamLen: 210,
      });

      if (s.showYouArrow !== false) {
        drawYouArrow(ctx, ax - 175, ay - 275, ax + 14, ay - 52, smoothstep(u * 4.5));
      }
    }

    // Top-left title block (MARS / 4TH PLANET FROM THE SUN) or top yellow header
    if (s.topHeadline) {
      ctx.save();
      ctx.font = `900 84px ${FONT_DISPLAY}`;
      ctx.fillStyle = '#f5c842';
      ctx.textAlign = 'center';
      ctx.shadowColor = 'rgba(0,0,0,0.85)';
      ctx.shadowBlur = 16;
      ctx.fillText(s.topHeadline, W * 0.5, 165);
      ctx.restore();
    }
    if (s.title) {
      ctx.save();
      ctx.font = `900 120px ${FONT_DISPLAY}`;
      ctx.fillStyle = '#f8fafc';
      ctx.textAlign = 'left';
      ctx.fillText(s.title, 82, 160);
      if (s.subtitle) {
        ctx.fillStyle = '#f5c842';
        ctx.fillRect(82, 224, 96, 4);
        ctx.font = `700 28px ${FONT_UI}`;
        ctx.fillStyle = '#cbd5e1';
        ctx.fillText(s.subtitle, 82, 265);
      }
      ctx.restore();
    }

    // Optional Rule stamp badge (e.g. "THE RULE") placed cleanly at top-right clear margin
    if (s.stamp) {
      const pop = easeOutBack(clamp((u - 0.35) * 4));
      if (pop > 0.01) {
        ctx.save();
        ctx.translate(220, 932);
        ctx.rotate(-0.04);
        ctx.scale(pop, pop);
        ctx.fillStyle = 'rgba(18, 22, 34, 0.92)';
        ctx.strokeStyle = '#f5c842';
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.roundRect(-122, -32, 244, 64, 10);
        ctx.fill();
        ctx.stroke();
        ctx.font = `900 32px ${FONT_DISPLAY}`;
        ctx.fillStyle = '#f5c842';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(s.stamp, 0, 2);
        ctx.restore();
      }
    }

    drawBottomHeadline(ctx, W, s.bottomWhite, s.bottomYellow, 935, smoothstep(u * 4));
    ctx.restore();
    drawVignette(ctx, W, H, 0.55);
  }

  // ==================== SCENE TYPE 2: planet_compare ====================
  function renderPlanetCompare(ctx, W, H, s, t, u) {
    ctx.save();
    const zoom = 1 + u * 0.03;
    ctx.translate(W * 0.5, H * 0.5);
    ctx.scale(zoom, zoom);
    ctx.translate(-W * 0.5, -H * 0.5);

    drawSpaceBg(ctx, W, H, t, { sunRays: false });

    const leftX = 640, rightX = 1320, cy = 515;
    drawPlanetSphere(ctx, leftX, cy, 310, s.leftPlanet || 'earth', t);
    drawPlanetSphere(ctx, rightX, cy, 165, s.rightPlanet || 'mars', t);

    ctx.font = `900 62px ${FONT_DISPLAY}`;
    ctx.textAlign = 'center';
    ctx.fillStyle = '#f8fafc';
    ctx.fillText(s.leftLabel || 'EARTH', leftX, cy + 375);
    ctx.fillText(s.rightLabel || 'MARS', rightX, cy + 235);

    ctx.font = `700 28px ${FONT_MONO}`;
    ctx.fillStyle = '#38bdf8';
    ctx.fillText(s.leftMetric || '1,013 mbar AIR PRESSURE', leftX, cy + 422);
    ctx.fillStyle = '#f59e0b';
    ctx.fillText(s.rightMetric || '6 mbar (0.6% OF EARTH)', rightX, cy + 282);

    if (s.title) {
      ctx.font = `900 72px ${FONT_DISPLAY}`;
      ctx.fillStyle = '#f8fafc';
      ctx.fillText(s.title, W * 0.5, 110);
    }

    ctx.restore();
    drawVignette(ctx, W, H, 0.55);
  }

  // ==================== SCENE TYPE 3: killer_card ====================
  function renderKillerCard(ctx, W, H, s, t, u) {
    // Full-screen warm yellow spotlight oval matching hd_228.jpg
    ctx.fillStyle = '#1b1402';
    ctx.fillRect(0, 0, W, H);

    ctx.save();
    const breathe = 1 + 0.025 * Math.sin(t * 2.2) + u * 0.03;
    ctx.translate(W * 0.5, H * 0.5);
    ctx.scale(1.45 * breathe, 0.92 * breathe);
    const rg = ctx.createRadialGradient(0, 0, 80, 0, 0, 680);
    rg.addColorStop(0, '#ffd84a');
    rg.addColorStop(0.55, '#f2bd1d');
    rg.addColorStop(0.85, '#966d09');
    rg.addColorStop(1, '#1b1402');
    ctx.fillStyle = rg;
    ctx.fillRect(-1000, -1000, 2000, 2000);
    ctx.restore();

    const pop = easeOutBack(clamp(u * 4.2));
    ctx.save();
    ctx.translate(W * 0.5, H * 0.5);
    ctx.scale(0.92 + 0.08 * pop, 0.92 + 0.08 * pop);

    if (s.eyebrow) {
      ctx.font = `900 34px ${FONT_UI}`;
      ctx.fillStyle = '#111827';
      ctx.textAlign = 'center';
      ctx.fillText(s.eyebrow, 0, -105);
    }

    ctx.font = `900 176px ${FONT_DISPLAY}`;
    ctx.fillStyle = '#09090b';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(s.title || 'THE THIN AIR', 0, 8);

    // Optional clean green/dark status pill placed WELL BELOW title so it never overlaps text
    if (s.statusPill) {
      const pPop = smoothstep(clamp((u - 0.15) * 4));
      ctx.globalAlpha = pPop;
      ctx.font = `800 24px ${FONT_MONO}`;
      const tw = ctx.measureText(s.statusPill).width;
      const pw = tw + 44;
      ctx.fillStyle = '#0f172a';
      ctx.strokeStyle = '#4ade80';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.roundRect(-pw / 2, 128, pw, 48, 24);
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = '#4ade80';
      ctx.fillText(s.statusPill, 0, 153);
    }
    ctx.restore();

    drawVignette(ctx, W, H, 0.45);
  }

  // ==================== SCENE TYPE 4: surface_gauge ====================
  function renderSurfaceGauge(ctx, W, H, s, t, u) {
    ctx.save();
    const zoom = 1 + u * 0.025;
    ctx.translate(W * 0.5, H * 0.5);
    ctx.scale(zoom, zoom);
    ctx.translate(-W * 0.5, -H * 0.5);

    const ridgeY = drawSurface(ctx, W, H, t, s.palette || 'day', 14);
    const astroX = s.astroX ?? (s.widget === 'thermometer' ? 1280 : 410);
    const astroY = ridgeY(2, astroX) - 18;
    drawAstronaut(ctx, astroX, astroY, {
      scale: 1.55,
      t,
      walk: true,
      beamLen: 360,
      shadow: true,
    });

    if (s.widget === 'gauge') {
      // Dark pressure gauge card matching hd_220.jpg / mars_vid4.jpg
      const cardX = 955, cardY = 295, cardW = 450, cardH = 345;
      const enter = easeOutCubic(clamp(u * 4.5));
      ctx.save();
      ctx.globalAlpha = enter;
      ctx.translate(cardX + cardW / 2, cardY + cardH / 2 + (1 - enter) * 28);
      ctx.fillStyle = 'rgba(28, 25, 31, 0.94)';
      ctx.strokeStyle = 'rgba(255,255,255,0.13)';
      ctx.lineWidth = 2;
      ctx.shadowColor = 'rgba(0,0,0,0.6)';
      ctx.shadowBlur = 28;
      ctx.beginPath();
      ctx.roundRect(-cardW / 2, -cardH / 2, cardW, cardH, 16);
      ctx.fill();
      ctx.stroke();
      ctx.shadowBlur = 0;

      ctx.font = `700 18px ${FONT_UI}`;
      ctx.fillStyle = '#cbd5e1';
      ctx.textAlign = 'center';
      ctx.fillText('AIR PRESSURE  (EARTH = 1,013)', 0, -cardH / 2 + 34);

      // Semi-circular arc track
      const acx = 0, acy = 32, aR = 148;
      ctx.strokeStyle = 'rgba(255,255,255,0.12)';
      ctx.lineWidth = 18;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.arc(acx, acy, aR, Math.PI, Math.PI * 2);
      ctx.stroke();

      // Animated value sweep from 1013 mbar down to target (e.g. 6 mbar)
      const sweepP = smoothstep(clamp(u / 0.65));
      const curMbar = Math.round(lerp(s.fromMbar ?? 1013, s.toMbar ?? 6, sweepP));
      const frac = clamp(curMbar / 1013, 0.006, 1);
      const ang = Math.PI + frac * Math.PI;

      const ag = ctx.createLinearGradient(-aR, 0, aR, 0);
      ag.addColorStop(0, '#ef4444');
      ag.addColorStop(0.25, '#f59e0b');
      ag.addColorStop(0.6, '#7dd3fc');
      ag.addColorStop(1, '#38bdf8');
      ctx.strokeStyle = ag;
      ctx.beginPath();
      ctx.arc(acx, acy, aR, Math.PI, ang);
      ctx.stroke();

      // Needle
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 5;
      ctx.beginPath();
      ctx.moveTo(acx, acy);
      ctx.lineTo(acx + Math.cos(ang) * (aR - 18), acy + Math.sin(ang) * (aR - 18));
      ctx.stroke();
      ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.arc(acx, acy, 10, 0, Math.PI * 2);
      ctx.fill();

      // Main readout + exact sub-1% percentage (NEVER rounded to 1% or 0%)
      ctx.font = `900 72px ${FONT_DISPLAY}`;
      ctx.fillStyle = '#ffffff';
      ctx.fillText(`${curMbar} mbar`, 0, 102);

      const pctText = curMbar < 10 ? `${((curMbar / 1013) * 100).toFixed(1)}% OF EARTH (<1%)` : `${Math.round((curMbar / 1013) * 100)}% OF EARTH`;
      ctx.font = `700 18px ${FONT_MONO}`;
      ctx.fillStyle = curMbar < 15 ? '#f87171' : '#94a3b8';
      ctx.fillText(pctText, 0, 146);
      ctx.restore();

      // Red warning banner beneath card once gauge reaches low pressure
      const warnEnter = smoothstep(clamp((u - 0.42) * 3.5));
      if (warnEnter > 0.01 && s.warningTop) {
        ctx.save();
        ctx.globalAlpha = warnEnter;
        ctx.textAlign = 'center';
        ctx.font = `900 42px ${FONT_DISPLAY}`;
        ctx.fillStyle = '#ef4444';
        ctx.fillText(s.warningTop, cardX + cardW / 2, cardY + cardH + 78);
        const lineW = ctx.measureText(s.warningTop).width + 20;
        ctx.fillRect(cardX + cardW / 2 - lineW / 2, cardY + cardH + 98, lineW, 4);
        if (s.warningSub) {
          ctx.font = `700 22px ${FONT_UI}`;
          ctx.fillStyle = '#f8fafc';
          ctx.fillText(s.warningSub, cardX + cardW / 2, cardY + cardH + 126);
        }
        ctx.restore();
      }
    } else if (s.widget === 'thermometer') {
      // Glowing cyan thermometer matching hd_234.jpg, with NON-OVERLAPPING stacked readouts
      const tx = 225, topY = 310, botY = 815;
      const enter = easeOutCubic(clamp(u * 4));
      ctx.save();
      ctx.globalAlpha = enter;

      // Glass tube background
      ctx.fillStyle = 'rgba(255,255,255,0.14)';
      ctx.beginPath();
      ctx.roundRect(tx - 18, topY, 36, botY - topY, 18);
      ctx.fill();

      // Bulb glow
      const bg = ctx.createRadialGradient(tx, botY + 18, 12, tx, botY + 18, 86);
      bg.addColorStop(0, 'rgba(94, 226, 255, 0.55)');
      bg.addColorStop(1, 'rgba(94, 226, 255, 0)');
      ctx.fillStyle = bg;
      ctx.beginPath();
      ctx.arc(tx, botY + 18, 86, 0, Math.PI * 2);
      ctx.fill();

      // Animated mercury fill dropping from -60C down toward -125C
      const fillFrac = lerp(0.45, 0.22, smoothstep(clamp((u - 0.3) * 2)));
      const mercTop = lerp(botY - 12, topY + 24, fillFrac);
      ctx.fillStyle = '#5ee2ff';
      ctx.beginPath();
      ctx.roundRect(tx - 11, mercTop, 22, botY - mercTop + 14, 11);
      ctx.fill();
      ctx.beginPath();
      ctx.arc(tx, botY + 18, 34, 0, Math.PI * 2);
      ctx.fill();

      // Row 1: -60°C AVERAGE (cleanly positioned upper row, zero overlap)
      ctx.textAlign = 'left';
      ctx.font = `900 108px ${FONT_DISPLAY}`;
      ctx.fillStyle = '#ffffff';
      ctx.fillText(s.tempAvg || '-60°C', 325, 430);
      ctx.font = `700 24px ${FONT_UI}`;
      ctx.fillStyle = '#cbd5e1';
      ctx.fillText(s.tempAvgSub || 'AVERAGE SURFACE TEMPERATURE', 328, 492);

      // Row 2: -125°C POLES IN WINTER (appears mid-shot stacked neatly BELOW Row 1)
      const poleShow = smoothstep(clamp((u - 0.36) * 3.5));
      if (poleShow > 0.01) {
        ctx.globalAlpha = poleShow;
        ctx.font = `900 108px ${FONT_DISPLAY}`;
        ctx.fillStyle = '#5ee2ff';
        ctx.fillText(s.tempPole || '-125°C', 325, 640);
        ctx.font = `700 24px ${FONT_UI}`;
        ctx.fillStyle = '#cbd5e1';
        ctx.fillText(s.tempPoleSub || 'POLES IN WINTER  (COLDER THAN ANTARCTICA)', 328, 702);
      }
      ctx.restore();
    } else if (s.widget === 'notice') {
      // Dry-humor DOORMAT NOTICE card matching hd_182.jpg
      const pop = easeOutBack(clamp(u * 4));
      ctx.save();
      ctx.translate(1220, 465);
      ctx.scale(pop, pop);

      // Post stake
      ctx.fillStyle = '#3f2e21';
      ctx.fillRect(-10, 115, 20, 175);

      // Card body
      ctx.fillStyle = '#f8fafc';
      ctx.shadowColor = 'rgba(0,0,0,0.55)';
      ctx.shadowBlur = 24;
      ctx.beginPath();
      ctx.roundRect(-275, -155, 550, 310, 8);
      ctx.fill();
      ctx.shadowBlur = 0;

      ctx.strokeStyle = '#94a3b8';
      ctx.lineWidth = 3;
      ctx.strokeRect(-257, -137, 514, 274);

      ctx.textAlign = 'center';
      ctx.font = `700 18px ${FONT_MONO}`;
      ctx.fillStyle = '#64748b';
      ctx.fillText('MARS LANDING OFFICE', 0, -102);

      ctx.font = `900 54px ${FONT_DISPLAY}`;
      ctx.fillStyle = '#0f172a';
      ctx.fillText('DOORMAT NOTICE', 0, -48);

      ctx.fillStyle = '#cbd5e1';
      ctx.fillRect(-190, -16, 380, 2);

      ctx.textAlign = 'left';
      ctx.font = `900 38px ${FONT_DISPLAY}`;
      ctx.fillStyle = '#1e293b';
      ctx.fillText('WIPE FEET please', -222, 36);

      ctx.font = `700 17px ${FONT_MONO}`;
      ctx.fillStyle = '#475569';
      ctx.fillText('PERCHLORATES + LUNGS = BAD DAY', -222, 92);

      // Slammed red stamp neatly placed on bottom-right corner without overlapping text
      const sPop = easeOutBack(clamp((u - 0.35) * 4.5));
      if (sPop > 0.01) {
        ctx.save();
        ctx.translate(152, 34);
        ctx.rotate(-0.18);
        ctx.scale(sPop, sPop);
        ctx.fillStyle = 'rgba(220, 38, 38, 0.12)';
        ctx.strokeStyle = '#dc2626';
        ctx.lineWidth = 5;
        ctx.strokeRect(-86, -26, 172, 52);
        ctx.textAlign = 'center';
        ctx.font = `900 30px ${FONT_DISPLAY}`;
        ctx.fillStyle = '#dc2626';
        ctx.fillText('TOXIC DUST', 0, 10);
        ctx.restore();
      }
      ctx.restore();
    } else if (s.widget === 'delay') {
      // "WHAT CAN YOU DO?" knocked-down checklist + 22 min signal delay matching hd_241.jpg right thumbnail
      ctx.save();
      ctx.font = `900 56px ${FONT_DISPLAY}`;
      ctx.fillStyle = '#f8fafc';
      ctx.textAlign = 'left';
      ctx.fillText('WHAT CAN YOU DO?', 120, 220);

      const items = s.options || [
        { q: 'HOLD YOUR BREATH?', a: 'LUNGS RUPTURE IN SECONDS' },
        { q: 'DIG UNDERGROUND?', a: 'FROZEN + TOXIC PERCHLORATES' },
        { q: 'CALL FOR HELP?', a: '22 MIN ONE-WAY RADIO DELAY' },
      ];
      items.forEach((it, idx) => {
        const reveal = smoothstep(clamp((u - idx * 0.22) * 4));
        if (reveal <= 0.01) return;
        const yy = 285 + idx * 110;
        ctx.globalAlpha = reveal;
        ctx.fillStyle = 'rgba(20, 18, 26, 0.86)';
        ctx.strokeStyle = 'rgba(239, 68, 68, 0.55)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.roundRect(120, yy, 620, 88, 12);
        ctx.fill();
        ctx.stroke();

        ctx.font = `900 34px ${FONT_DISPLAY}`;
        ctx.fillStyle = '#ef4444';
        ctx.fillText('✗', 148, yy + 53);

        ctx.font = `800 28px ${FONT_UI}`;
        ctx.fillStyle = '#f8fafc';
        ctx.fillText(it.q, 192, yy + 36);
        ctx.font = `700 20px ${FONT_MONO}`;
        ctx.fillStyle = '#f59e0b';
        ctx.fillText(it.a, 192, yy + 68);
      });
      ctx.globalAlpha = 1;

      // Signal wave arc to tiny Earth dot
      const earthX = 1660, earthY = 230;
      ctx.fillStyle = '#38bdf8';
      ctx.beginPath();
      ctx.arc(earthX, earthY, 22, 0, Math.PI * 2);
      ctx.fill();
      ctx.font = `700 20px ${FONT_MONO}`;
      ctx.fillStyle = '#bae6fd';
      ctx.textAlign = 'center';
      ctx.fillText('EARTH', earthX, earthY + 46);

      // Traveling signal pulse from astronaut to Earth
      const sigP = (t * 0.55) % 1;
      const sx = lerp(astroX, earthX, sigP);
      const sy = lerp(astroY - 35, earthY, sigP);
      ctx.strokeStyle = 'rgba(239, 68, 68, 0.4)';
      ctx.lineWidth = 3;
      ctx.setLineDash([10, 10]);
      ctx.beginPath();
      ctx.moveTo(astroX, astroY - 35);
      ctx.lineTo(earthX, earthY);
      ctx.stroke();
      ctx.setLineDash([]);

      ctx.fillStyle = '#ef4444';
      ctx.beginPath();
      ctx.arc(sx, sy, 9, 0, Math.PI * 2);
      ctx.fill();

      // Red pill callout
      ctx.fillStyle = 'rgba(28, 16, 20, 0.92)';
      ctx.strokeStyle = '#ef4444';
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.roundRect(1140, 395, 440, 64, 10);
      ctx.fill();
      ctx.stroke();
      ctx.font = `800 24px ${FONT_MONO}`;
      ctx.fillStyle = '#f87171';
      ctx.fillText('SIGNAL DELAY: UP TO 22 MIN', 1360, 435);

      ctx.restore();
    }

    ctx.restore();
    drawVignette(ctx, W, H, 0.52);
  }

  // ==================== SCENE TYPE 5: xray (+ receipt gag) ====================
  function renderXray(ctx, W, H, s, t, u) {
    ctx.save();
    const zoom = 1 + u * 0.03;
    ctx.translate(W * 0.5, H * 0.5);
    ctx.scale(zoom, zoom);
    ctx.translate(-W * 0.5, -H * 0.5);

    // Blueprint navy grid background matching hd_224.jpg
    ctx.fillStyle = '#050914';
    ctx.fillRect(0, 0, W, H);

    ctx.strokeStyle = 'rgba(42, 74, 126, 0.25)';
    ctx.lineWidth = 1;
    const step = 56;
    for (let x = 0; x <= W; x += step) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
    }
    for (let y = 0; y <= H; y += step) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
    }

    // Subtle stars on blueprint
    for (let i = 0; i < STARS.length; i += 2) {
      const st = STARS[i];
      ctx.fillStyle = `rgba(210, 230, 255, ${(st.alpha * 0.55).toFixed(2)})`;
      ctx.fillRect(st.x, st.y, 2, 2);
    }

    // Header
    ctx.font = `900 44px ${FONT_UI}`;
    ctx.fillStyle = '#f8fafc';
    ctx.textAlign = 'center';
    ctx.fillText(s.header || 'REMEMBER THAT FIZZ?', 575, 86);

    // Neon green vector head & torso diagram matching hd_224.jpg & hd_186.jpg
    const gx = 575;
    const pulse = 0.8 + 0.2 * Math.sin(t * 5);

    ctx.save();
    ctx.strokeStyle = '#4ade80';
    ctx.lineWidth = 6;
    ctx.shadowColor = 'rgba(74, 222, 128, 0.65)';
    ctx.shadowBlur = 16;

    // Head circle
    ctx.beginPath();
    ctx.arc(gx, 395, 68, 0, Math.PI * 2);
    ctx.stroke();

    // Torso rounded rect
    ctx.beginPath();
    ctx.roundRect(gx - 122, 476, 244, 330, 34);
    ctx.stroke();
    ctx.restore();

    // Glowing green hotspot (head/saliva or chest/radiation)
    const hy = s.hotspot === 'chest' ? 590 : 395;
    const hg = ctx.createRadialGradient(gx, hy, 4, gx, hy, 64 * pulse);
    hg.addColorStop(0, 'rgba(134, 239, 172, 0.9)');
    hg.addColorStop(0.4, 'rgba(74, 222, 128, 0.35)');
    hg.addColorStop(1, 'rgba(74, 222, 128, 0)');
    ctx.fillStyle = hg;
    ctx.beginPath();
    ctx.arc(gx, hy, 64 * pulse, 0, Math.PI * 2);
    ctx.fill();

    // If radiation mode, subtle pulsing X-ray waves
    if (s.hotspot === 'chest') {
      for (let r = 0; r < 3; r++) {
        const pr = ((t * 0.7 + r * 0.33) % 1);
        ctx.strokeStyle = `rgba(74, 222, 128, ${(1 - pr) * 0.45})`;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(gx, hy, 30 + pr * 90, 0, Math.PI * 2);
        ctx.stroke();
      }
    }

    // Left red callout badge & line
    const pillX = 185, pillY = hy - 95;
    ctx.fillStyle = '#151923';
    ctx.strokeStyle = 'rgba(255,255,255,0.22)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.roundRect(pillX - 130, pillY - 26, 260, 52, 26);
    ctx.fill();
    ctx.stroke();

    ctx.font = `800 22px ${FONT_UI}`;
    ctx.fillStyle = '#f8fafc';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(s.calloutLabel || 'SALIVA: BOILING', pillX, pillY + 1);

    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(pillX + 130, pillY);
    ctx.lineTo(gx, hy);
    ctx.stroke();

    // Right side gag: MARS SODA CO. receipt + CARBONATED stamp (matching mars_vid5.jpg)
    if (s.receipt) {
      const rEnter = easeOutBack(clamp((u - 0.18) * 3.8));
      if (rEnter > 0.01) {
        const rx = 1420, ry = 635;
        ctx.save();
        ctx.translate(rx, ry + (1 - rEnter) * 90);
        ctx.rotate(0.025);
        ctx.scale(rEnter, rEnter);

        const rw = 360, rh = 310;
        // Jagged receipt outline
        ctx.fillStyle = '#f8fafc';
        ctx.shadowColor = 'rgba(0,0,0,0.6)';
        ctx.shadowBlur = 24;
        ctx.beginPath();
        ctx.moveTo(-rw / 2, -rh / 2);
        for (let i = -rw / 2 + 18; i <= rw / 2; i += 18) {
          ctx.lineTo(i, -rh / 2 + ((i / 18) % 2 === 0 ? 0 : 8));
        }
        ctx.lineTo(rw / 2, rh / 2);
        for (let i = rw / 2 - 18; i >= -rw / 2; i -= 18) {
          ctx.lineTo(i, rh / 2 - ((i / 18) % 2 === 0 ? 0 : 8));
        }
        ctx.closePath();
        ctx.fill();
        ctx.shadowBlur = 0;

        ctx.fillStyle = '#0f172a';
        ctx.font = `900 24px ${FONT_MONO}`;
        ctx.textAlign = 'center';
        ctx.fillText(s.receipt.header || 'MARS SODA CO.', 0, -rh / 2 + 44);

        ctx.strokeStyle = '#94a3b8';
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        ctx.moveTo(-rw / 2 + 24, -rh / 2 + 68);
        ctx.lineTo(rw / 2 - 24, -rh / 2 + 68);
        ctx.stroke();
        ctx.setLineDash([]);

        const lines = s.receipt.lines || [
          ['SALIVA', '$0'],
          ['BUBBLES', '$0'],
          ['AIR PRESSURE', '$0'],
        ];
        ctx.font = `700 20px ${FONT_MONO}`;
        lines.forEach(([k, v], idx) => {
          const ly = -rh / 2 + 104 + idx * 36;
          ctx.textAlign = 'left';
          ctx.fillStyle = '#334155';
          ctx.fillText(k, -rw / 2 + 28, ly);
          ctx.textAlign = 'right';
          ctx.fillText(v, rw / 2 - 28, ly);
        });

        ctx.strokeStyle = '#0f172a';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(-rw / 2 + 24, rh / 2 - 74);
        ctx.lineTo(rw / 2 - 24, rh / 2 - 74);
        ctx.stroke();

        ctx.font = `900 26px ${FONT_MONO}`;
        ctx.textAlign = 'left';
        ctx.fillStyle = '#0f172a';
        ctx.fillText('TOTAL:', -rw / 2 + 28, rh / 2 - 38);
        ctx.textAlign = 'right';
        ctx.fillStyle = '#dc2626';
        ctx.fillText(s.receipt.total || 'YOU', rw / 2 - 28, rh / 2 - 38);
        ctx.restore();
      }

      if (s.receipt.stamp) {
        const sPop = easeOutBack(clamp((u - 0.45) * 4.5));
        if (sPop > 0.01) {
          ctx.save();
          ctx.translate(1420, 260);
          ctx.rotate(-0.07);
          ctx.scale(sPop, sPop);
          ctx.fillStyle = 'rgba(24, 20, 8, 0.9)';
          ctx.strokeStyle = '#f5c842';
          ctx.lineWidth = 6;
          ctx.strokeRect(-220, -56, 440, 112);
          ctx.strokeRect(-208, -46, 416, 92);
          ctx.font = `900 64px ${FONT_DISPLAY}`;
          ctx.fillStyle = '#f5c842';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(s.receipt.stamp, 0, 4);
          ctx.restore();
        }
      }
    }

    // Optional right-side metric badge (e.g. "0.64 mSv / DAY" comparing to "6 CHEST X-RAYS")
    if (s.rightCards) {
      s.rightCards.forEach((c, idx) => {
        const reveal = smoothstep(clamp((u - idx * 0.25) * 4));
        if (reveal <= 0.01) return;
        const cx = 1390, cy = 340 + idx * 190;
        ctx.save();
        ctx.globalAlpha = reveal;
        ctx.fillStyle = 'rgba(20, 25, 38, 0.92)';
        ctx.strokeStyle = idx === 1 ? '#ef4444' : '#4ade80';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.roundRect(cx - 240, cy - 72, 480, 144, 16);
        ctx.fill();
        ctx.stroke();

        ctx.textAlign = 'center';
        ctx.font = `900 58px ${FONT_DISPLAY}`;
        ctx.fillStyle = idx === 1 ? '#f87171' : '#4ade80';
        ctx.fillText(c.big, cx, cy - 12);
        ctx.font = `700 22px ${FONT_UI}`;
        ctx.fillStyle = '#cbd5e1';
        ctx.fillText(c.sub, cx, cy + 40);
        ctx.restore();
      });
    }

    ctx.restore();
    drawVignette(ctx, W, H, 0.58);
  }

  // ==================== SCENE TYPE 6: evidence (NASA photo frame + safe counters) ====================
  function renderEvidence(ctx, W, H, s, t, u) {
    ctx.save();
    const zoom = 1 + u * 0.025;
    ctx.translate(W * 0.5, H * 0.5);
    ctx.scale(zoom, zoom);
    ctx.translate(-W * 0.5, -H * 0.5);

    drawSurface(ctx, W, H, t, s.palette || 'day', 10);

    const hasCounters = Array.isArray(s.counters) && s.counters.length > 0;
    const frameCx = hasCounters ? 1165 : 960;
    const frameCy = 525;
    const frameW = hasCounters ? 880 : 1020;
    const frameH = hasCounters ? 590 : 650;

    // Optional left-side comparison cards positioned cleanly in upper-left (y=230..500)
    // so they NEVER collide with the bottom-left credit badge!
    if (hasCounters) {
      s.counters.forEach((c, idx) => {
        const pop = easeOutCubic(clamp((u - idx * 0.25) * 4));
        if (pop <= 0.01) return;
        const cx = 110;
        const cy = 230 + idx * 175;
        ctx.save();
        ctx.globalAlpha = pop;
        ctx.fillStyle = 'rgba(26, 22, 26, 0.92)';
        ctx.strokeStyle = 'rgba(255,255,255,0.14)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.roundRect(cx, cy, 385, 148, 14);
        ctx.fill();
        ctx.stroke();

        ctx.font = `700 18px ${FONT_MONO}`;
        ctx.fillStyle = '#94a3b8';
        ctx.textAlign = 'left';
        ctx.fillText(c.label, cx + 24, cy + 36);

        ctx.font = `900 72px ${FONT_DISPLAY}`;
        ctx.fillStyle = idx === 0 ? '#f8fafc' : '#4ade80';
        ctx.fillText(c.big, cx + 24, cy + 112);

        const bigW = ctx.measureText(c.big).width;
        ctx.font = `700 26px ${FONT_UI}`;
        ctx.fillStyle = '#cbd5e1';
        ctx.fillText(c.unit || '', cx + 34 + bigW, cy + 106);
        ctx.restore();
      });
    }

    // Tilted white-bordered Polaroid photo frame matching hd_182.jpg & hd_238.jpg
    const enter = easeOutCubic(clamp(u * 4.2));
    ctx.save();
    ctx.globalAlpha = enter;
    ctx.translate(frameCx, frameCy + (1 - enter) * 35);
    ctx.rotate((s.tiltDeg ?? -1.5) * Math.PI / 180);

    // Outer Polaroid frame
    ctx.fillStyle = '#f8fafc';
    ctx.shadowColor = 'rgba(0,0,0,0.68)';
    ctx.shadowBlur = 38;
    ctx.beginPath();
    ctx.roundRect(-frameW / 2 - 14, -frameH / 2 - 14, frameW + 28, frameH + 28, 6);
    ctx.fill();
    ctx.shadowBlur = 0;

    // Image interior
    const img = IMAGES[s.imgKey];
    ctx.save();
    ctx.beginPath();
    ctx.rect(-frameW / 2, -frameH / 2, frameW, frameH);
    ctx.clip();
    if (img && img.complete && img.naturalWidth > 0) {
      const iw = img.naturalWidth, ih = img.naturalHeight;
      const zoom = s.imgZoom || 1.0;
      const scale = Math.max(frameW / iw, frameH / ih) * zoom;
      const dw = iw * scale, dh = ih * scale;
      ctx.drawImage(img, -dw / 2, -dh / 2, dw, dh);
    } else {
      ctx.fillStyle = '#334155';
      ctx.fillRect(-frameW / 2, -frameH / 2, frameW, frameH);
    }
    ctx.restore();

    // Red top pill banner overlapping top border
    if (s.topTag) {
      ctx.font = `900 22px ${FONT_UI}`;
      const tw = ctx.measureText(s.topTag).width;
      ctx.fillStyle = '#dc2626';
      ctx.beginPath();
      ctx.roundRect(-frameW / 2 + 12, -frameH / 2 - 22, tw + 44, 42, 6);
      ctx.fill();
      ctx.fillStyle = '#ffffff';
      ctx.textAlign = 'left';
      ctx.textBaseline = 'middle';
      ctx.fillText(s.topTag, -frameW / 2 + 34, -frameH / 2 - 1);
    }
    ctx.restore();

    // Clean bottom-left credit pill strictly below y=920 so it NEVER hits counters
    if (s.credit) {
      ctx.save();
      ctx.font = `700 22px ${FONT_MONO}`;
      const cw = ctx.measureText(s.credit).width;
      ctx.fillStyle = 'rgba(12, 16, 26, 0.88)';
      ctx.strokeStyle = 'rgba(255,255,255,0.16)';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.roundRect(110, 938, cw + 38, 44, 8);
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = '#e2e8f0';
      ctx.textAlign = 'left';
      ctx.textBaseline = 'middle';
      ctx.fillText(s.credit, 129, 961);
      ctx.restore();
    }

    ctx.restore();
    drawVignette(ctx, W, H, 0.5);
  }

  // ==================== SCENE TYPE 7: magma_twist ====================
  function renderMagmaTwist(ctx, W, H, s, t, u) {
    ctx.save();
    const panY = -u * 35;
    ctx.translate(0, panY);

    // Night sky upper strip
    const sky = ctx.createLinearGradient(0, 0, 0, 290);
    sky.addColorStop(0, '#04060d');
    sky.addColorStop(1, '#261419');
    ctx.fillStyle = sky;
    ctx.fillRect(0, 0, W, 320);

    // Subsurface geological crust strata
    const strata = [
      { y: 270, col: '#7c3417' },
      { y: 390, col: '#4f1e0c' },
      { y: 540, col: '#2f120b' },
      { y: 710, col: '#1c0c0d' },
    ];
    strata.forEach((st, i) => {
      ctx.fillStyle = st.col;
      ctx.beginPath();
      ctx.moveTo(0, H + 80);
      for (let x = 0; x <= W; x += 24) {
        const yy = st.y + Math.sin(x * 0.008 + i * 1.9) * 18;
        ctx.lineTo(x, yy);
      }
      ctx.lineTo(W, H + 80);
      ctx.closePath();
      ctx.fill();
    });

    // Deep glowing magma pocket at y=860
    const glow = 0.85 + 0.15 * Math.sin(t * 4);
    const mg = ctx.createRadialGradient(W * 0.5, 910, 40, W * 0.5, 910, 560 * glow);
    mg.addColorStop(0, '#fef08a');
    mg.addColorStop(0.28, '#f97316');
    mg.addColorStop(0.65, 'rgba(185, 28, 28, 0.55)');
    mg.addColorStop(1, 'rgba(185, 28, 28, 0)');
    ctx.fillStyle = mg;
    ctx.beginPath();
    ctx.ellipse(W * 0.5, 930, 620, 210, 0, 0, Math.PI * 2);
    ctx.fill();

    // Tiny astronaut standing on the crust looking down
    drawAstronaut(ctx, 560, 232, { scale: 1.15, t, beamLen: 260, shadow: true });

    // Depth scale bar on right
    ctx.strokeStyle = 'rgba(255,255,255,0.4)';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(1680, 280);
    ctx.lineTo(1680, 910);
    ctx.stroke();
    ctx.font = `800 26px ${FONT_MONO}`;
    ctx.fillStyle = '#cbd5e1';
    ctx.textAlign = 'right';
    ctx.fillText('0 KM · SURFACE', 1660, 295);
    ctx.fillStyle = '#fb923c';
    ctx.fillText(s.depthLabel || '8+ KM · MAGMA?', 1660, 900);

    // Fact-check honesty badge: UNPROVEN / POSSIBLE, NOT FOUND
    ctx.fillStyle = 'rgba(24, 18, 12, 0.92)';
    ctx.strokeStyle = '#f59e0b';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.roundRect(110, 95, 620, 74, 12);
    ctx.fill();
    ctx.stroke();
    ctx.font = `900 28px ${FONT_MONO}`;
    ctx.fillStyle = '#fbbf24';
    ctx.textAlign = 'left';
    ctx.fillText(s.badgeText || 'HYPOTHESIS · UNPROVEN (NOT YET CONFIRMED)', 138, 141);

    // Callback closing punchline headline
    drawBottomHeadline(ctx, W, s.bottomWhite || 'THE DESERT DOESN’T KILL YOU.', s.bottomYellow || 'EVERYTHING ELSE DOES.', 995, smoothstep(clamp((u - 0.15) * 3.5)));

    ctx.restore();
    drawVignette(ctx, W, H, 0.52);
  }

  function renderFrameAt(ctx, W, H, t) {
    if (!BEATS.length) return;
    const clampedT = clamp(t, 0, BEATS[BEATS.length - 1].end - 0.0001);
    const sc = BEATS.find((b) => clampedT >= b.start && clampedT < b.end) || BEATS[BEATS.length - 1];
    const lt = clampedT - sc.start;
    const u = clamp(lt / sc.dur);

    const map = {
      orbit_establish: renderOrbitEstablish,
      planet_compare: renderPlanetCompare,
      killer_card: renderKillerCard,
      surface_gauge: renderSurfaceGauge,
      xray: renderXray,
      evidence: renderEvidence,
      magma_twist: renderMagmaTwist,
    };
    const fn = map[sc.type] || renderOrbitEstablish;
    fn(ctx, W, H, sc, lt, u);
  }

  window.ORBIT = {
    register({ scenes, assets = {} }) {
      SCENES = scenes;
      BEATS = buildTimeline(scenes);
      const promises = Object.entries(assets).map(([k, src]) => new Promise((res) => {
        const img = new Image();
        img.onload = () => { IMAGES[k] = img; res(); };
        img.onerror = () => { console.warn('Image failed:', src); res(); };
        img.src = src;
      }));
      return Promise.all(promises).then(() => {
        window.ORBIT_TOTAL = BEATS.length ? BEATS[BEATS.length - 1].end : 0;
        window.ORBIT_COUNT = BEATS.length;
        window.ORBIT_READY = true;
      });
    },
    renderAt(t) {
      const c = document.getElementById('c');
      const ctx = c.getContext('2d');
      renderFrameAt(ctx, c.width || DEFAULT_W, c.height || DEFAULT_H, t);
    },
    renderStill(idx, frac = 0.65) {
      const c = document.getElementById('c');
      const ctx = c.getContext('2d');
      const sc = BEATS[idx];
      if (!sc) return;
      const t = sc.start + sc.dur * clamp(frac, 0.05, 0.95);
      renderFrameAt(ctx, c.width || DEFAULT_W, c.height || DEFAULT_H, t);
    },
  };
})();
