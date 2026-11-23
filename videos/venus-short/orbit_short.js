/* Orbit 2D Space Short Renderer (Native 1080x1920 @ 30fps)
 * Respects YouTube Shorts 9:16 safe zones (top y>=170, bottom captions y<=1540, right x<=930).
 */
(function () {
  const DEFAULT_W = 1080;
  const DEFAULT_H = 1920;

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

  const IMAGES = {};
  let SCENES = [];
  let BEATS = [];
  let WORDS = [];

  function buildTimeline(scenes) {
    let t = 0;
    return scenes.map((s, idx) => {
      const dur = Math.max(0.5, Number(s.dur) || 4);
      const start = t;
      t += dur;
      return { ...s, idx, start, end: t, dur };
    });
  }

  const STARS = (() => {
    const r = seeded(7711);
    return Array.from({ length: 220 }, () => ({
      x: r() * 1080,
      y: r() * 1920,
      size: 0.9 + r() * 2.2,
      alpha: 0.22 + r() * 0.72,
      speed: 0.9 + r() * 2.8,
      phase: r() * Math.PI * 2,
    }));
  })();

  const DUST = (() => {
    const r = seeded(3319);
    return Array.from({ length: 50 }, () => ({
      x: r() * 1080,
      y: r() * 1920,
      r: 1.4 + r() * 3.0,
      vx: 8 + r() * 20,
      vy: -14 - r() * 18,
      alpha: 0.08 + r() * 0.22,
    }));
  })();

  function drawVignette(ctx, W, H, strength = 0.58) {
    const g = ctx.createRadialGradient(W * 0.5, H * 0.48, W * 0.25, W * 0.5, H * 0.48, H * 0.65);
    g.addColorStop(0, 'rgba(0,0,0,0)');
    g.addColorStop(1, `rgba(0,0,0,${strength})`);
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);
  }

  function drawSpaceBg(ctx, W, H, t, opts = {}) {
    const g = ctx.createLinearGradient(0, 0, W * 0.5, H);
    g.addColorStop(0, '#04060e');
    g.addColorStop(0.55, '#080e1f');
    g.addColorStop(1, '#101830');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);

    if (opts.sunRays !== false) {
      ctx.save();
      const sx = 64, sy = 150;
      const sunGlow = ctx.createRadialGradient(sx, sy, 6, sx, sy, 360);
      sunGlow.addColorStop(0, 'rgba(255,245,215,0.48)');
      sunGlow.addColorStop(0.2, 'rgba(255,205,120,0.14)');
      sunGlow.addColorStop(1, 'rgba(255,205,120,0)');
      ctx.fillStyle = sunGlow;
      ctx.fillRect(0, 0, 520, 540);
      ctx.fillStyle = 'rgba(245,235,210,0.52)';
      ctx.beginPath();
      ctx.arc(sx, sy, 22, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = 'rgba(255,240,200,0.07)';
      ctx.lineWidth = 2;
      for (let i = 0; i < 8; i++) {
        const ang = -0.25 + i * 0.23 + Math.sin(t * 0.5 + i) * 0.015;
        ctx.beginPath();
        ctx.moveTo(sx, sy);
        ctx.lineTo(sx + Math.cos(ang) * 440, sy + Math.sin(ang) * 440);
        ctx.stroke();
      }
      ctx.restore();
    }

    for (const st of STARS) {
      const px = (st.x + t * 2.4) % W;
      const a = st.alpha * (0.65 + 0.35 * Math.sin(t * st.speed + st.phase));
      ctx.fillStyle = `rgba(235, 244, 255, ${a.toFixed(3)})`;
      ctx.beginPath();
      ctx.arc(px, st.y, st.size, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  function drawPlanetSphere(ctx, cx, cy, R, kind = 'venus', t = 0) {
    ctx.save();
    const glowColor = kind === 'earth' ? 'rgba(86, 165, 255, 0.32)'
      : kind === 'mercury' ? 'rgba(180, 185, 195, 0.22)'
      : 'rgba(245, 185, 78, 0.34)';
    const atm = ctx.createRadialGradient(cx, cy, R * 0.84, cx, cy, R * 1.48);
    atm.addColorStop(0, glowColor);
    atm.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = atm;
    ctx.beginPath();
    ctx.arc(cx, cy, R * 1.48, 0, Math.PI * 2);
    ctx.fill();

    ctx.beginPath();
    ctx.arc(cx, cy, R, 0, Math.PI * 2);
    ctx.clip();

    if (kind === 'earth') {
      const og = ctx.createRadialGradient(cx - R * 0.42, cy - R * 0.35, R * 0.1, cx, cy, R * 1.2);
      og.addColorStop(0, '#60a5fa');
      og.addColorStop(0.55, '#1d4ed8');
      og.addColorStop(1, '#0b193d');
      ctx.fillStyle = og;
      ctx.fillRect(cx - R, cy - R, R * 2, R * 2);
      ctx.fillStyle = '#34d399';
      const drift = (t * 8) % (R * 0.3);
      ctx.beginPath();
      ctx.ellipse(cx - R * 0.22 + drift * 0.3, cy - R * 0.15, R * 0.28, R * 0.22, 0.3, 0, Math.PI * 2);
      ctx.fill();
      ctx.beginPath();
      ctx.ellipse(cx + R * 0.25 + drift * 0.3, cy + R * 0.22, R * 0.24, R * 0.3, -0.4, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = 'rgba(255,255,255,0.28)';
      ctx.beginPath();
      ctx.ellipse(cx - R * 0.1, cy - R * 0.4, R * 0.46, R * 0.08, 0.12, 0, Math.PI * 2);
      ctx.fill();
    } else if (kind === 'mercury') {
      const mg = ctx.createRadialGradient(cx - R * 0.4, cy - R * 0.35, R * 0.08, cx, cy, R * 1.2);
      mg.addColorStop(0, '#d1d5db');
      mg.addColorStop(0.55, '#6b7280');
      mg.addColorStop(1, '#1f2937');
      ctx.fillStyle = mg;
      ctx.fillRect(cx - R, cy - R, R * 2, R * 2);
      ctx.fillStyle = 'rgba(30, 35, 45, 0.35)';
      [[-0.25, -0.1, 0.14], [0.22, 0.18, 0.18], [-0.08, 0.32, 0.11]].forEach(([dx, dy, rr]) => {
        ctx.beginPath();
        ctx.arc(cx + dx * R, cy + dy * R, rr * R, 0, Math.PI * 2);
        ctx.fill();
      });
    } else {
      // Venus swirling amber sulfuric clouds
      const vg = ctx.createRadialGradient(cx - R * 0.38, cy - R * 0.34, R * 0.08, cx, cy, R * 1.24);
      vg.addColorStop(0, '#fde68a');
      vg.addColorStop(0.45, '#e69d35');
      vg.addColorStop(0.78, '#9a4a12');
      vg.addColorStop(1, '#2b1004');
      ctx.fillStyle = vg;
      ctx.fillRect(cx - R, cy - R, R * 2, R * 2);

      // Animated cloud swirl bands
      const bandShift = Math.sin(t * 0.45) * R * 0.06;
      const bands = [
        { y: -0.52, h: 0.15, col: 'rgba(254, 243, 199, 0.28)' },
        { y: -0.24, h: 0.18, col: 'rgba(217, 119, 6, 0.28)' },
        { y: 0.06, h: 0.22, col: 'rgba(253, 224, 71, 0.22)' },
        { y: 0.38, h: 0.16, col: 'rgba(120, 53, 15, 0.32)' },
      ];
      bands.forEach((b, i) => {
        ctx.fillStyle = b.col;
        ctx.beginPath();
        ctx.ellipse(cx + bandShift * (i % 2 ? 1 : -1), cy + b.y * R, R * 1.12, R * b.h, -0.1, 0, Math.PI * 2);
        ctx.fill();
      });
    }

    // Crisp rim highlight
    const rim = ctx.createRadialGradient(cx - R * 0.28, cy - R * 0.28, R * 0.65, cx, cy, R);
    rim.addColorStop(0, 'rgba(255,255,255,0)');
    rim.addColorStop(0.92, 'rgba(255,236,190,0.06)');
    rim.addColorStop(1, 'rgba(255,245,215,0.34)');
    ctx.fillStyle = rim;
    ctx.fillRect(cx - R, cy - R, R * 2, R * 2);
    ctx.restore();
  }

  function drawAstronaut(ctx, x, y, opts = {}) {
    const s = opts.scale || 1;
    const t = opts.t || 0;
    const walk = opts.walk ? Math.sin(t * 5.2) : 0;
    const crush = opts.crush || 0; // 0..1 suit compression gag
    const beamLen = opts.beamLen || 220;
    ctx.save();
    ctx.translate(x, y);
    ctx.scale(s * (1 - crush * 0.28), s * (1 - crush * 0.12));

    if (opts.shadow) {
      ctx.fillStyle = 'rgba(0,0,0,0.44)';
      ctx.beginPath();
      ctx.ellipse(0, 32, 24, 7, 0, 0, Math.PI * 2);
      ctx.fill();
    }

    if (beamLen > 0) {
      const flick = 1 + 0.05 * Math.sin(t * 9.5);
      const bg = ctx.createLinearGradient(12, -16, 12 + beamLen * flick, -4);
      bg.addColorStop(0, 'rgba(255, 248, 220, 0.34)');
      bg.addColorStop(0.55, 'rgba(255, 244, 200, 0.11)');
      bg.addColorStop(1, 'rgba(255, 244, 200, 0)');
      ctx.fillStyle = bg;
      ctx.beginPath();
      ctx.moveTo(10, -18);
      ctx.lineTo(10 + beamLen * flick, -52);
      ctx.lineTo(10 + beamLen * flick, 26);
      ctx.closePath();
      ctx.fill();
    }

    // PLSS Backpack
    ctx.fillStyle = '#cbd5e1';
    ctx.beginPath();
    ctx.roundRect(-21, -12, 14, 28, 4);
    ctx.fill();
    ctx.fillStyle = '#ef4444';
    ctx.fillRect(-19, -7, 4, 15);

    // Legs
    ctx.fillStyle = '#e2e8f0';
    ctx.beginPath();
    ctx.roundRect(-9 + walk * 4, 14, 8, 17, 3);
    ctx.roundRect(1 - walk * 4, 14, 8, 17, 3);
    ctx.fill();

    // Torso
    ctx.fillStyle = '#f8fafc';
    ctx.beginPath();
    ctx.roundRect(-12, -11, 24, 27, 7);
    ctx.fill();
    ctx.fillStyle = '#94a3b8';
    ctx.fillRect(-7, -3, 14, 7);

    // Arm
    ctx.fillStyle = '#e2e8f0';
    ctx.beginPath();
    ctx.roundRect(7, -6 - walk * 3, 12, 7, 3);
    ctx.fill();

    // Helmet & Visor
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(1, -21, 16, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#0f172a';
    ctx.beginPath();
    ctx.roundRect(-3, -29, 18, 14, 7);
    ctx.fill();
    ctx.fillStyle = 'rgba(245, 158, 11, 0.65)';
    ctx.beginPath();
    ctx.ellipse(9, -23, 5, 3, -0.35, 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();
  }

  function drawYouCallout(ctx, astroX, astroY, textX, textY) {
    ctx.save();
    ctx.font = `900 44px ${FONT_DISPLAY}`;
    ctx.fillStyle = '#ef4444';
    ctx.textAlign = 'center';
    ctx.fillText('YOU', textX, textY);

    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 4.5;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(textX, textY + 14);
    ctx.quadraticCurveTo(lerp(textX, astroX, 0.5) - 24, lerp(textY, astroY, 0.5), astroX - 24, astroY - 40);
    ctx.stroke();

    const ex = astroX - 24, ey = astroY - 40;
    ctx.beginPath();
    ctx.moveTo(ex - 14, ey - 2);
    ctx.lineTo(ex, ey);
    ctx.lineTo(ex - 6, ey - 15);
    ctx.stroke();
    ctx.restore();
  }

  function drawRidges(ctx, W, H, palette, t) {
    const sky = ctx.createLinearGradient(0, 0, 0, H * 0.78);
    if (palette === 'hot') {
      sky.addColorStop(0, '#140504');
      sky.addColorStop(0.5, '#3b1207');
      sky.addColorStop(1, '#7c2d12');
    } else if (palette === 'cloud') {
      sky.addColorStop(0, '#070b1a');
      sky.addColorStop(0.55, '#1e293b');
      sky.addColorStop(1, '#b45309');
    } else {
      // Venus amber sulfuric day
      sky.addColorStop(0, '#180c04');
      sky.addColorStop(0.5, '#542608');
      sky.addColorStop(1, '#b45309');
    }
    ctx.fillStyle = sky;
    ctx.fillRect(0, 0, W, H);

    // Acid dust band
    ctx.fillStyle = palette === 'hot' ? 'rgba(239, 68, 68, 0.18)' : 'rgba(251, 191, 36, 0.20)';
    ctx.fillRect(0, H * 0.62, W, 140);

    const layers = palette === 'hot'
      ? [
          { y: H * 0.66, amp: 52, freq: 0.0045, col: '#7f1d1d', spd: 5 },
          { y: H * 0.74, amp: 46, freq: 0.0065, col: '#450a0a', spd: 12 },
          { y: H * 0.83, amp: 36, freq: 0.009, col: '#280505', spd: 20 },
          { y: H * 0.91, amp: 24, freq: 0.012, col: '#140202', spd: 30 },
        ]
      : [
          { y: H * 0.66, amp: 54, freq: 0.0045, col: '#92400e', spd: 5 },
          { y: H * 0.74, amp: 46, freq: 0.0065, col: '#692a07', spd: 12 },
          { y: H * 0.83, amp: 36, freq: 0.009, col: '#3d1704', spd: 20 },
          { y: H * 0.91, amp: 24, freq: 0.012, col: '#1c0901', spd: 30 },
        ];

    layers.forEach((l, li) => {
      ctx.fillStyle = l.col;
      ctx.beginPath();
      ctx.moveTo(0, H);
      for (let x = 0; x <= W; x += 18) {
        const y = l.y + Math.sin((x + t * l.spd) * l.freq + li * 1.6) * l.amp
          + Math.cos((x + t * l.spd) * l.freq * 2.1) * (l.amp * 0.34);
        ctx.lineTo(x, y);
      }
      ctx.lineTo(W, H);
      ctx.closePath();
      ctx.fill();
    });

    for (const d of DUST) {
      const px = (d.x + t * d.vx) % W;
      const py = (d.y + t * d.vy + H) % H;
      ctx.fillStyle = `rgba(254, 215, 130, ${d.alpha})`;
      ctx.beginPath();
      ctx.arc(px, py, d.r, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  function drawBottomHeadline(ctx, W, whiteText, yellowText, yBase, prog = 1) {
    ctx.save();
    ctx.globalAlpha = clamp(prog);
    ctx.textAlign = 'center';
    ctx.font = `900 62px ${FONT_DISPLAY}`;
    const lineH = 68;
    const drawTxt = (txt, yy, col) => {
      ctx.lineJoin = 'round';
      ctx.miterLimit = 2;
      ctx.lineWidth = 10;
      ctx.strokeStyle = 'rgba(0,0,0,0.88)';
      ctx.strokeText(txt, W * 0.5, yy);
      ctx.fillStyle = col;
      ctx.fillText(txt, W * 0.5, yy);
    };
    if (whiteText && yellowText) {
      drawTxt(whiteText, yBase - lineH * 0.5, '#ffffff');
      drawTxt(yellowText, yBase + lineH * 0.65, '#f5c842');
    } else if (whiteText || yellowText) {
      drawTxt(whiteText || yellowText, yBase, yellowText ? '#f5c842' : '#ffffff');
    }
    ctx.restore();
  }

  function drawKineticCaptions(ctx, W, t) {
    if (!WORDS || !WORDS.length) return;
    // Find chunk of up to 4 words around current time t
    const idx = WORDS.findIndex((w) => t >= w.start - 0.04 && t <= w.end + 0.22);
    if (idx < 0) return;
    const chunkIdx = Math.floor(idx / 3);
    const slice = WORDS.slice(chunkIdx * 3, chunkIdx * 3 + 3);
    const y = 1485; // Safe above YouTube Shorts bottom overlay (y > 1550)

    ctx.save();
    ctx.font = `900 44px ${FONT_DISPLAY}`;
    ctx.textAlign = 'center';
    const text = slice.map((w) => w.w.toUpperCase()).join(' ');
    const tw = ctx.measureText(text).width + 44;
    ctx.fillStyle = 'rgba(8, 12, 24, 0.78)';
    ctx.strokeStyle = 'rgba(255,255,255,0.16)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.roundRect(W * 0.5 - tw * 0.5, y - 42, tw, 58, 14);
    ctx.fill();
    ctx.stroke();

    // Draw each word, highlighting active spoken word in Orbit gold
    const widths = slice.map((w) => ctx.measureText(w.w.toUpperCase() + ' ').width);
    const totalW = widths.reduce((a, b) => a + b, 0) - ctx.measureText(' ').width;
    let cx = W * 0.5 - totalW * 0.5;
    ctx.textAlign = 'left';
    slice.forEach((w, i) => {
      const active = t >= w.start - 0.05 && t <= w.end + 0.08;
      const wordStr = w.w.toUpperCase();
      ctx.fillStyle = active ? '#f5c842' : '#f8fafc';
      ctx.fillText(wordStr, cx, y);
      cx += widths[i];
    });
    ctx.restore();
  }

  // ---------------- Scene Archetypes (Native 1080x1920) ----------------

  function renderOrbitEstablish(ctx, W, H, s, lt, u) {
    drawSpaceBg(ctx, W, H, lt, { sunRays: true });
    ctx.save();
    const zoom = 1 + (s.zoomAmt || 0.04) * u;
    ctx.translate(W * 0.5, H * 0.5);
    ctx.scale(zoom, zoom);
    ctx.translate(-W * 0.5, -H * 0.5);

    if (s.horizonMode) {
      // Giant curved planetary horizon at bottom half
      drawPlanetSphere(ctx, W * 0.5, 1980, 1140, 'venus', lt);
      const crush = s.crush ? smoothstep(clamp((u - 0.35) * 2.5)) : 0;
      const shake = crush > 0 && crush < 0.9 ? Math.sin(lt * 55) * 7 : 0;
      drawAstronaut(ctx, 540 + shake, 800 + Math.sin(lt * 1.8) * 10, { scale: 1.45, t: lt, beamLen: 280, crush });

      // Top headline
      ctx.textAlign = 'center';
      ctx.font = `900 74px ${FONT_DISPLAY}`;
      ctx.fillStyle = '#f5c842';
      ctx.fillText(s.topHeadline || 'THE CRUSH', W * 0.5, 310);
      if (s.subPill) {
        ctx.fillStyle = 'rgba(239, 68, 68, 0.92)';
        ctx.beginPath();
        ctx.roundRect(W * 0.5 - 210, 345, 420, 52, 26);
        ctx.fill();
        ctx.font = `800 24px ${FONT_UI}`;
        ctx.fillStyle = '#ffffff';
        ctx.fillText(s.subPill, W * 0.5, 379);
      }
      drawBottomHeadline(ctx, W, s.bottomWhite, s.bottomYellow, 1210, smoothstep(u * 3.5));
    } else {
      // Giant Venus orb center-low + tiny floating astronaut upper-left
      drawPlanetSphere(ctx, 640, 1020, 440, s.planet || 'venus', lt);
      const ax = 240;
      const ay = 680 + Math.sin(lt * 1.6) * 12;
      drawAstronaut(ctx, ax, ay, { scale: 1.25, t: lt, beamLen: 240 });
      if (s.showYouArrow !== false) drawYouCallout(ctx, ax, ay, 175, 535);

      ctx.textAlign = 'center';
      ctx.font = `900 132px ${FONT_DISPLAY}`;
      ctx.fillStyle = '#ffffff';
      ctx.fillText(s.title || 'VENUS', W * 0.5, 305);
      ctx.font = `700 28px ${FONT_UI}`;
      ctx.fillStyle = '#fcd34d';
      ctx.fillText(s.subtitle || 'EARTH’S TWIN SISTER · 2ND FROM THE SUN', W * 0.5, 355);

      drawBottomHeadline(ctx, W, s.bottomWhite, s.bottomYellow, 1290, smoothstep(u * 3));
      if (s.stamp) {
        const sp = easeOutBack(clamp((u - 0.35) * 3.5));
        ctx.save();
        ctx.translate(W * 0.5, 1385);
        ctx.rotate(-0.04);
        ctx.scale(sp, sp);
        ctx.strokeStyle = '#f5c842';
        ctx.lineWidth = 4;
        ctx.fillStyle = 'rgba(20,16,8,0.88)';
        ctx.beginPath();
        ctx.roundRect(-140, -30, 280, 58, 10);
        ctx.fill();
        ctx.stroke();
        ctx.font = `900 32px ${FONT_DISPLAY}`;
        ctx.fillStyle = '#f5c842';
        ctx.textAlign = 'center';
        ctx.fillText(s.stamp, 0, 11);
        ctx.restore();
      }
    }
    ctx.restore();
    drawVignette(ctx, W, H, 0.52);
  }

  function renderKillerCard(ctx, W, H, s, lt, u) {
    const zoom = 1 + 0.045 * u;
    ctx.save();
    ctx.translate(W * 0.5, H * 0.5);
    ctx.scale(zoom, zoom);
    ctx.translate(-W * 0.5, -H * 0.5);

    ctx.fillStyle = '#1d1603';
    ctx.fillRect(0, 0, W, H);
    const sg = ctx.createRadialGradient(W * 0.5, H * 0.45, 40, W * 0.5, H * 0.45, 760);
    sg.addColorStop(0, '#fef08a');
    sg.addColorStop(0.52, '#facc15');
    sg.addColorStop(0.84, '#92400e');
    sg.addColorStop(1, '#1a1202');
    ctx.fillStyle = sg;
    ctx.fillRect(0, 0, W, H);

    const pop = easeOutBack(clamp(u * 4.5));
    ctx.translate(W * 0.5, H * 0.45);
    ctx.scale(pop, pop);
    ctx.textAlign = 'center';
    ctx.font = `900 44px ${FONT_UI}`;
    ctx.fillStyle = '#1c1917';
    ctx.fillText(s.eyebrow || 'KILLER #1', 0, -90);

    ctx.font = `900 138px ${FONT_DISPLAY}`;
    ctx.fillStyle = '#0c0a09';
    ctx.fillText(s.title || 'THE CRUSH', 0, 55);

    if (s.sub) {
      ctx.fillStyle = '#0c0a09';
      ctx.beginPath();
      ctx.roundRect(-210, 96, 420, 58, 29);
      ctx.fill();
      ctx.font = `800 30px ${FONT_MONO}`;
      ctx.fillStyle = '#facc15';
      ctx.fillText(s.sub, 0, 136);
    }
    ctx.restore();
  }

  function renderSurfaceGauge(ctx, W, H, s, lt, u) {
    ctx.save();
    const zoom = 1 + 0.03 * u;
    ctx.translate(W * 0.5, H * 0.5);
    ctx.scale(zoom, zoom);
    ctx.translate(-W * 0.5, -H * 0.5);

    drawRidges(ctx, W, H, s.palette || 'day', lt);
    drawAstronaut(ctx, 210 + (s.walk ? lt * 12 : 0), 1245, { scale: 1.15, t: lt, walk: !!s.walk, shadow: true, beamLen: 210 });

    if (s.widget === 'gauge') {
      const cw = 840, ch = 560, cx = (W - cw) * 0.5, cy = 260;
      ctx.fillStyle = 'rgba(20, 18, 24, 0.93)';
      ctx.strokeStyle = 'rgba(251, 191, 36, 0.3)';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.roundRect(cx, cy, cw, ch, 26);
      ctx.fill();
      ctx.stroke();

      ctx.font = `800 26px ${FONT_UI}`;
      ctx.fillStyle = '#cbd5e1';
      ctx.textAlign = 'center';
      ctx.fillText('SURFACE AIR PRESSURE (EARTH = 1 BAR)', W * 0.5, cy + 56);

      const val = lerp(s.fromBar || 1, s.toBar || 92, easeOutCubic(clamp(u * 1.45)));
      const dialX = W * 0.5, dialY = cy + 290, dialR = 170;
      ctx.strokeStyle = '#334155';
      ctx.lineWidth = 22;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.arc(dialX, dialY, dialR, Math.PI * 0.85, Math.PI * 2.15);
      ctx.stroke();

      const frac = clamp(val / 100);
      ctx.strokeStyle = '#ef4444';
      ctx.beginPath();
      ctx.arc(dialX, dialY, dialR, Math.PI * 0.85, lerp(Math.PI * 0.85, Math.PI * 2.15, frac));
      ctx.stroke();

      const ang = lerp(Math.PI * 0.85, Math.PI * 2.15, frac);
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 6;
      ctx.beginPath();
      ctx.moveTo(dialX, dialY);
      ctx.lineTo(dialX + Math.cos(ang) * (dialR - 34), dialY + Math.sin(ang) * (dialR - 34));
      ctx.stroke();

      ctx.font = `900 92px ${FONT_DISPLAY}`;
      ctx.fillStyle = '#ffffff';
      ctx.fillText(`${Math.round(val)} BAR`, dialX, dialY + 25);

      ctx.font = `800 28px ${FONT_MONO}`;
      ctx.fillStyle = '#fca5a5';
      ctx.fillText(s.warningTop || '92× EARTH · LIKE 900m UNDERWATER', W * 0.5, cy + 502);
    } else if (s.widget === 'thermometer') {
      const cw = 840, ch = 640, cx = (W - cw) * 0.5, cy = 240;
      ctx.fillStyle = 'rgba(20, 12, 12, 0.93)';
      ctx.strokeStyle = 'rgba(239, 68, 68, 0.35)';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.roundRect(cx, cy, cw, ch, 26);
      ctx.fill();
      ctx.stroke();

      ctx.font = `800 26px ${FONT_UI}`;
      ctx.fillStyle = '#fca5a5';
      ctx.textAlign = 'center';
      ctx.fillText('GREENHOUSE OVEN · 2× FARTHER THAN MERCURY', W * 0.5, cy + 56);

      // Vertical thermometer on left, big spaced temperatures on right (zero overlap)
      const tx = cx + 165, ty = cy + 120, th = 390;
      ctx.fillStyle = '#1e293b';
      ctx.beginPath();
      ctx.roundRect(tx - 24, ty, 48, th, 24);
      ctx.fill();
      ctx.beginPath();
      ctx.arc(tx, ty + th + 16, 46, 0, Math.PI * 2);
      ctx.fill();

      const fillFrac = clamp(0.15 + 0.85 * easeOutCubic(clamp(u * 1.4)));
      const fh = th * fillFrac;
      const tg = ctx.createLinearGradient(0, ty + th, 0, ty);
      tg.addColorStop(0, '#f59e0b');
      tg.addColorStop(1, '#ef4444');
      ctx.fillStyle = tg;
      ctx.beginPath();
      ctx.roundRect(tx - 15, ty + th - fh, 30, fh + 14, 15);
      ctx.fill();
      ctx.beginPath();
      ctx.arc(tx, ty + th + 16, 36, 0, Math.PI * 2);
      ctx.fill();

      // Lead melting marker at 327C (~70% height)
      const leadY = ty + th * 0.30;
      ctx.strokeStyle = '#facc15';
      ctx.lineWidth = 3;
      ctx.setLineDash([8, 6]);
      ctx.beginPath();
      ctx.moveTo(tx + 36, leadY);
      ctx.lineTo(tx + 240, leadY);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.font = `800 22px ${FONT_MONO}`;
      ctx.fillStyle = '#facc15';
      ctx.textAlign = 'left';
      ctx.fillText('LEAD MELTS: 327°C', tx + 44, leadY - 12);

      // Huge Surface Temp cleanly separated on right column
      const curTemp = Math.round(lerp(20, 465, easeOutCubic(clamp(u * 1.75))));
      ctx.textAlign = 'left';
      ctx.font = `900 132px ${FONT_DISPLAY}`;
      ctx.fillStyle = '#ffffff';
      ctx.fillText(`${curTemp}°C`, cx + 445, cy + 360);
      ctx.font = `800 26px ${FONT_UI}`;
      ctx.fillStyle = '#f87171';
      ctx.fillText('SURFACE TEMPERATURE', cx + 445, cy + 412);
    } else if (s.widget === 'bunker_radio') {
      const cw = 840, ch = 560, cx = (W - cw) * 0.5, cy = 270;
      ctx.fillStyle = 'rgba(18, 12, 16, 0.93)';
      ctx.strokeStyle = 'rgba(248, 113, 113, 0.35)';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.roundRect(cx, cy, cw, ch, 26);
      ctx.fill();
      ctx.stroke();

      ctx.textAlign = 'center';
      ctx.font = `900 40px ${FONT_DISPLAY}`;
      ctx.fillStyle = '#ffffff';
      ctx.fillText(s.cardTop || 'WHAT CAN YOU DO?', W * 0.5, cy + 72);

      // Earth <-> Venus radio wave arc
      const rx = cx + 190, ex = cx + 650, ry = cy + 260;
      drawPlanetSphere(ctx, rx, ry, 58, 'venus', lt);
      drawPlanetSphere(ctx, ex, ry, 58, 'earth', lt);
      const pulse = (lt * 0.9) % 1;
      ctx.strokeStyle = 'rgba(250, 204, 21, 0.35)';
      ctx.lineWidth = 4;
      ctx.setLineDash([12, 10]);
      ctx.beginPath();
      ctx.moveTo(rx + 74, ry);
      ctx.lineTo(ex - 74, ry);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = '#facc15';
      ctx.beginPath();
      ctx.arc(lerp(rx + 74, ex - 74, pulse), ry, 10, 0, Math.PI * 2);
      ctx.fill();

      ctx.font = `900 72px ${FONT_DISPLAY}`;
      ctx.fillStyle = '#facc15';
      ctx.fillText(s.midStat || '15 MIN SIGNAL DELAY', W * 0.5, cy + 415);

      ctx.fillStyle = '#dc2626';
      ctx.beginPath();
      ctx.roundRect(W * 0.5 - 260, cy + 455, 520, 56, 12);
      ctx.fill();
      ctx.font = `900 28px ${FONT_MONO}`;
      ctx.fillStyle = '#ffffff';
      ctx.fillText(s.bottomTag || 'PHONE MELTED IN 0.4 SECONDS', W * 0.5, cy + 493);
    }

    drawBottomHeadline(ctx, W, s.bottomWhite, s.bottomYellow, 1040, smoothstep(u * 3));
    ctx.restore();
    drawVignette(ctx, W, H, 0.42);
  }

  function renderXray(ctx, W, H, s, lt, u) {
    ctx.save();
    const zoom = 1 + 0.03 * u;
    ctx.translate(W * 0.5, H * 0.5);
    ctx.scale(zoom, zoom);
    ctx.translate(-W * 0.5, -H * 0.5);

    ctx.fillStyle = '#050914';
    ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = 'rgba(45, 82, 138, 0.25)';
    ctx.lineWidth = 1.5;
    for (let x = 0; x <= W; x += 60) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
    }
    for (let y = 0; y <= H; y += 60) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
    }

    ctx.textAlign = 'center';
    ctx.font = `900 72px ${FONT_DISPLAY}`;
    ctx.fillStyle = '#ffffff';
    ctx.fillText(s.header || 'INSTANT IMPLOSION', W * 0.5, 290);

    // Neon green helmet/torso blueprint centered in upper-mid
    const bx = W * 0.5, by = 640;
    ctx.strokeStyle = '#4ade80';
    ctx.lineWidth = 7;
    const squeeze = 1 - 0.14 * smoothstep(clamp((u - 0.2) * 2.2));
    ctx.beginPath();
    ctx.ellipse(bx, by - 115, 92 * squeeze, 98, 0, 0, Math.PI * 2);
    ctx.stroke();
    ctx.beginPath();
    ctx.roundRect(bx - 135 * squeeze, by, 270 * squeeze, 270, 56);
    ctx.stroke();

    // Glowing crush / heat hotspot
    const pulse = 0.78 + 0.22 * Math.sin(lt * 8);
    const hg = ctx.createRadialGradient(bx, by - 115, 10, bx, by - 115, 125 * pulse);
    hg.addColorStop(0, 'rgba(239, 68, 68, 0.92)');
    hg.addColorStop(1, 'rgba(239, 68, 68, 0)');
    ctx.fillStyle = hg;
    ctx.beginPath();
    ctx.arc(bx, by - 115, 125 * pulse, 0, Math.PI * 2);
    ctx.fill();

    // Callout pill
    ctx.fillStyle = '#181014';
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.roundRect(W * 0.5 - 230, 960, 460, 66, 16);
    ctx.fill();
    ctx.stroke();
    ctx.font = `900 32px ${FONT_MONO}`;
    ctx.fillStyle = '#fca5a5';
    ctx.fillText(s.calloutLabel || 'TITANIUM HELMET: CRUSHED', W * 0.5, 1004);

    if (s.receipt) {
      const rp = easeOutBack(clamp((u - 0.1) * 3.5));
      ctx.save();
      ctx.translate(W * 0.5, 1210);
      ctx.scale(rp, rp);
      ctx.fillStyle = '#f8fafc';
      ctx.beginPath();
      ctx.roundRect(-240, -155, 480, 310, 10);
      ctx.fill();
      ctx.fillStyle = '#0f172a';
      ctx.textAlign = 'center';
      ctx.font = `900 28px ${FONT_MONO}`;
      ctx.fillText(s.receipt.header, 0, -108);
      ctx.font = `700 23px ${FONT_MONO}`;
      s.receipt.lines.forEach(([k, v], i) => {
        ctx.textAlign = 'left';
        ctx.fillText(k, -205, -52 + i * 42);
        ctx.textAlign = 'right';
        ctx.fillText(v, 205, -52 + i * 42);
      });
      ctx.fillStyle = '#dc2626';
      ctx.textAlign = 'left';
      ctx.font = `900 28px ${FONT_MONO}`;
      ctx.fillText('SURVIVAL TIME', -205, 92);
      ctx.textAlign = 'right';
      ctx.fillText(s.receipt.total, 205, 92);

      // Stamp
      ctx.translate(0, 12);
      ctx.rotate(-0.14);
      ctx.strokeStyle = '#dc2626';
      ctx.lineWidth = 5;
      ctx.fillStyle = 'rgba(255,255,255,0.92)';
      ctx.beginPath();
      ctx.roundRect(-145, -34, 290, 64, 8);
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = '#dc2626';
      ctx.textAlign = 'center';
      ctx.font = `900 36px ${FONT_DISPLAY}`;
      ctx.fillText(s.receipt.stamp, 0, 12);
      ctx.restore();
    }

    ctx.restore();
    drawVignette(ctx, W, H, 0.45);
  }

  function renderEvidence(ctx, W, H, s, lt, u) {
    ctx.save();
    const zoom = 1 + 0.03 * u;
    ctx.translate(W * 0.5, H * 0.5);
    ctx.scale(zoom, zoom);
    ctx.translate(-W * 0.5, -H * 0.5);

    drawRidges(ctx, W, H, s.palette || 'day', lt);

    // Top NASA Mission Red Pill
    ctx.fillStyle = '#dc2626';
    ctx.beginPath();
    ctx.roundRect(W * 0.5 - 410, 215, 820, 62, 16);
    ctx.fill();
    ctx.font = `900 26px ${FONT_MONO}`;
    ctx.fillStyle = '#ffffff';
    ctx.textAlign = 'center';
    ctx.fillText(s.topTag || 'NASA MAGELLAN · MARINER 10 MISSIONS', W * 0.5, 255);

    // Upper stat cards well above bottom credit tag (Orbit QA Trap #3)
    if (s.badgeTop) {
      ctx.fillStyle = 'rgba(18, 14, 22, 0.92)';
      ctx.strokeStyle = '#facc15';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.roundRect(W * 0.5 - 390, 305, 780, 92, 16);
      ctx.fill();
      ctx.stroke();
      ctx.font = `900 36px ${FONT_DISPLAY}`;
      ctx.fillStyle = '#facc15';
      ctx.fillText(s.badgeTop, W * 0.5, 363);
    }

    // Real NASA photo tilted Polaroid frame
    const img = IMAGES[s.imgKey];
    const pw = 760, ph = 620;
    ctx.save();
    ctx.translate(W * 0.5, 760);
    ctx.rotate(Math.sin(lt * 0.7) * 0.015 - 0.02);
    ctx.fillStyle = '#f8fafc';
    ctx.shadowColor = 'rgba(0,0,0,0.65)';
    ctx.shadowBlur = 32;
    ctx.beginPath();
    ctx.roundRect(-pw * 0.5 - 18, -ph * 0.5 - 18, pw + 36, ph + 78, 12);
    ctx.fill();
    ctx.shadowBlur = 0;

    if (img) {
      const iw = img.naturalWidth || img.width;
      const ih = img.naturalHeight || img.height;
      const sc = Math.max(pw / iw, ph / ih);
      const dw = iw * sc, dh = ih * sc;
      ctx.save();
      ctx.beginPath();
      ctx.rect(-pw * 0.5, -ph * 0.5, pw, ph);
      ctx.clip();
      ctx.drawImage(img, -dw * 0.5, -dh * 0.5, dw, dh);
      ctx.restore();
    }

    // Bottom Polaroid credit strip (clear separation from upper cards)
    ctx.font = `800 22px ${FONT_MONO}`;
    ctx.fillStyle = '#1e293b';
    ctx.textAlign = 'center';
    ctx.fillText(s.credit || 'NASA / JPL-Caltech', 0, ph * 0.5 + 36);
    ctx.restore();

    drawBottomHeadline(ctx, W, s.bottomWhite, s.bottomYellow, 1245, smoothstep(u * 3));
    ctx.restore();
    drawVignette(ctx, W, H, 0.42);
  }

  function renderCloudTwist(ctx, W, H, s, lt, u) {
    ctx.save();
    const zoom = 1 + 0.04 * u;
    ctx.translate(W * 0.5, H * 0.5);
    ctx.scale(zoom, zoom);
    ctx.translate(-W * 0.5, -H * 0.5);

    drawRidges(ctx, W, H, 'cloud', lt);

    // Cloud band layer at 50 km
    ctx.fillStyle = 'rgba(253, 224, 71, 0.16)';
    ctx.fillRect(0, 740, W, 240);

    // Upper metric badge
    ctx.fillStyle = 'rgba(15, 23, 42, 0.92)';
    ctx.strokeStyle = '#38bdf8';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.roundRect(W * 0.5 - 400, 240, 800, 120, 18);
    ctx.fill();
    ctx.stroke();
    ctx.textAlign = 'center';
    ctx.font = `900 44px ${FONT_DISPLAY}`;
    ctx.fillStyle = '#38bdf8';
    ctx.fillText('50 KM ALTITUDE · CLOUD DECK', W * 0.5, 294);
    ctx.font = `800 30px ${FONT_MONO}`;
    ctx.fillStyle = '#e2e8f0';
    ctx.fillText('PRESSURE: 1 BAR  |  TEMP: 25°C (ROOM TEMP)', W * 0.5, 340);

    // Floating astronaut
    drawAstronaut(ctx, W * 0.5, 620 + Math.sin(lt * 2.2) * 14, { scale: 1.5, t: lt, beamLen: 260 });

    // Callback stamp slam
    const sp = easeOutBack(clamp((u - 0.35) * 3.5));
    ctx.save();
    ctx.translate(W * 0.5, 920);
    ctx.rotate(-0.05);
    ctx.scale(sp, sp);
    ctx.fillStyle = 'rgba(24, 8, 8, 0.94)';
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 6;
    ctx.beginPath();
    ctx.roundRect(-390, -52, 780, 104, 14);
    ctx.fill();
    ctx.stroke();
    ctx.font = `900 46px ${FONT_DISPLAY}`;
    ctx.fillStyle = '#ef4444';
    ctx.fillText('DO NOT BREATHE THE BATTERY ACID', 0, 17);
    ctx.restore();

    drawBottomHeadline(ctx, W, s.bottomWhite || 'NICE WEATHER.', s.bottomYellow || 'DEADLY AIR.', 1210, smoothstep(u * 3));
    ctx.restore();
    drawVignette(ctx, W, H, 0.45);
  }

  function renderFrameAt(ctx, W, H, t) {
    if (!BEATS.length) return;
    const clampedT = clamp(t, 0, BEATS[BEATS.length - 1].end - 0.0001);
    const sc = BEATS.find((b) => clampedT >= b.start && clampedT < b.end) || BEATS[BEATS.length - 1];
    const lt = clampedT - sc.start;
    const u = clamp(lt / sc.dur);

    const map = {
      orbit_establish: renderOrbitEstablish,
      killer_card: renderKillerCard,
      surface_gauge: renderSurfaceGauge,
      xray: renderXray,
      evidence: renderEvidence,
      cloud_twist: renderCloudTwist,
    };
    const fn = map[sc.type] || renderOrbitEstablish;
    fn(ctx, W, H, sc, lt, u);
    drawKineticCaptions(ctx, W, clampedT);
  }

  window.ORBIT = {
    register({ scenes, assets = {}, words = [] }) {
      SCENES = scenes;
      BEATS = buildTimeline(scenes);
      WORDS = words;
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
