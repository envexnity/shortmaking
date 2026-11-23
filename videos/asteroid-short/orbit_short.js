/* Orbit 2D Space Short Renderer — Next-Gen Asteroid Apophis 2029 (Native 1080x1920 @ 30fps)
 * - 8sb2R11FeVw solid black-pill subtitles (58px bold sans, #FFFFFF + #FFE600 active pop, 2-3 words)
 * - Minimal on-screen text (>=90% of text from subtitles only)
 * - Rapid ~1.1-1.4s dynamic camera sub-cuts with punch-ins, Dutch tilts, and 7-frame impact KICKS
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
  const FONT_SUB = '"Segoe UI", Arial, sans-serif';
  const FONT_MONO = 'Consolas, "Courier New", monospace';

  const IMAGES = {};
  let SCENES = [];
  let BEATS = [];
  let SUB_CHUNKS = [];

  function buildWordChunks(beats) {
    const chunks = [];
    for (const b of beats || []) {
      const ws = b.words || [];
      let i = 0;
      while (i < ws.length) {
        let take = 3;
        if (i + 3 <= ws.length) {
          const s3 = ws.slice(i, i + 3).map((x) => x.w).join(' ');
          if (s3.length > 18) take = 2;
        } else {
          take = ws.length - i;
        }
        const slice = ws.slice(i, i + take);
        chunks.push({
          words: slice,
          start: slice[0].start,
          end: slice[slice.length - 1].end,
        });
        i += take;
      }
    }
    return chunks;
  }

  function buildTimeline(scenes) {
    let t = 0;
    return scenes.map((s, idx) => {
      const dur = Math.max(0.5, Number(s.dur) || 4);
      const nSub = Math.max(1, Math.round(dur / 1.25));
      const start = t;
      t += dur;
      return { ...s, idx, start, end: t, dur, nSub };
    });
  }

  const STARS = (() => {
    const r = seeded(8821);
    return Array.from({ length: 220 }, () => ({
      x: r() * 1080,
      y: r() * 1920,
      size: 0.9 + r() * 2.2,
      alpha: 0.22 + r() * 0.72,
      speed: 0.9 + r() * 2.8,
      phase: r() * Math.PI * 2,
    }));
  })();

  const FRAGMENTS = (() => {
    const r = seeded(4412);
    return Array.from({ length: 40 }, () => ({
      ang: (r() - 0.5) * 0.65,
      spd: 140 + r() * 260,
      rad: 8 + r() * 18,
      hot: r() > 0.35,
    }));
  })();

  const DUST = (() => {
    const r = seeded(3319);
    return Array.from({ length: 50 }, () => ({
      x: r() * 1080,
      y: r() * 1920,
      r: 1.4 + r() * 3.0,
      vx: 10 + r() * 22,
      vy: -14 - r() * 18,
      alpha: 0.08 + r() * 0.22,
    }));
  })();

  function applyNextGenCamera(ctx, W, H, sc, lt, subIdx, subLt, subDur) {
    const uSub = clamp(subLt / subDur);
    const globalSub = sc.idx * 5 + subIdx;

    // 7-frame deterministic alternating-sign impact KICKS on cut entry
    const frameInSub = Math.floor(subLt * 30);
    let kickY = 0;
    let kickRot = 0;
    if ((sc.idx > 0 || subIdx > 0) && frameInSub < 7) {
      const k = 1 - frameInSub / 7;
      const sign = frameInSub % 2 === 0 ? 1 : -1;
      kickY = sign * 15 * k;
      kickRot = sign * 0.016 * k;
    }

    let scale = 1.04;
    let dx = 0;
    let dy = 0;
    let rot = 0;

    if (sc.idx === 0 && subIdx === 0) {
      // Frame-0 dramatic opening hook snap-in
      const snap = easeOutCubic(clamp(subLt / 0.35));
      scale = lerp(1.28, 1.03, snap) + 0.04 * uSub;
      dy = lerp(-30, 0, snap);
    } else {
      const preset = globalSub % 4;
      if (preset === 0) {
        scale = lerp(1.02, 1.15, easeOutCubic(uSub));
        dy = lerp(18, -12, uSub);
      } else if (preset === 1) {
        scale = lerp(1.07, 1.18, uSub);
        dx = lerp(34, -14, uSub);
        dy = lerp(-18, 10, uSub);
        rot = lerp(-0.045, -0.018, uSub);
      } else if (preset === 2) {
        scale = lerp(1.16, 1.05, easeOutCubic(uSub));
        dx = lerp(-34, 16, uSub);
        dy = lerp(14, -14, uSub);
        rot = lerp(0.045, 0.015, uSub);
      } else {
        scale = lerp(1.04, 1.18, uSub);
        dx = lerp(-16, 20, uSub);
        dy = lerp(26, -8, uSub);
        rot = lerp(-0.025, 0.022, uSub);
      }
    }

    ctx.translate(W * 0.5 + dx, H * 0.5 + dy + kickY);
    ctx.rotate(rot + kickRot);
    ctx.scale(scale, scale);
    ctx.translate(-W * 0.5, -H * 0.5);
  }

  function drawVignette(ctx, W, H, strength = 0.55) {
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
    ctx.fillRect(-140, -140, W + 280, H + 280);

    if (opts.sunRays !== false) {
      ctx.save();
      const sx = 64, sy = 150;
      const sunGlow = ctx.createRadialGradient(sx, sy, 6, sx, sy, 360);
      sunGlow.addColorStop(0, 'rgba(255,245,215,0.45)');
      sunGlow.addColorStop(0.2, 'rgba(255,205,120,0.14)');
      sunGlow.addColorStop(1, 'rgba(255,205,120,0)');
      ctx.fillStyle = sunGlow;
      ctx.fillRect(0, 0, 520, 540);
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

  function drawEarthSphere(ctx, cx, cy, R, t = 0) {
    ctx.save();
    const atm = ctx.createRadialGradient(cx, cy, R * 0.84, cx, cy, R * 1.45);
    atm.addColorStop(0, 'rgba(56, 189, 248, 0.38)');
    atm.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = atm;
    ctx.beginPath();
    ctx.arc(cx, cy, R * 1.45, 0, Math.PI * 2);
    ctx.fill();

    ctx.beginPath();
    ctx.arc(cx, cy, R, 0, Math.PI * 2);
    ctx.clip();

    const og = ctx.createRadialGradient(cx - R * 0.38, cy - R * 0.35, R * 0.08, cx, cy, R * 1.25);
    og.addColorStop(0, '#38bdf8');
    og.addColorStop(0.55, '#1d4ed8');
    og.addColorStop(1, '#081229');
    ctx.fillStyle = og;
    ctx.fillRect(cx - R, cy - R, R * 2, R * 2);

    ctx.fillStyle = '#34d399';
    const drift = Math.sin(t * 0.4) * R * 0.06;
    ctx.beginPath();
    ctx.ellipse(cx - R * 0.22 + drift, cy - R * 0.16, R * 0.32, R * 0.22, 0.28, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.ellipse(cx + R * 0.24 + drift, cy + R * 0.22, R * 0.26, R * 0.32, -0.35, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = 'rgba(255,255,255,0.28)';
    ctx.beginPath();
    ctx.ellipse(cx - R * 0.08, cy - R * 0.38, R * 0.48, R * 0.09, 0.1, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  function drawAsteroidRock(ctx, cx, cy, R, t = 0, glowRed = false) {
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(t * 0.35);
    if (glowRed) {
      const g = ctx.createRadialGradient(0, 0, R * 0.4, 0, 0, R * 1.8);
      g.addColorStop(0, 'rgba(239, 68, 68, 0.58)');
      g.addColorStop(1, 'rgba(239, 68, 68, 0)');
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(0, 0, R * 1.8, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.beginPath();
    const pts = 12;
    for (let i = 0; i < pts; i++) {
      const a = (i / pts) * Math.PI * 2;
      const rad = R * (0.84 + 0.16 * Math.sin(i * 2.7 + 1.2) + 0.08 * Math.cos(i * 4.1));
      const px = Math.cos(a) * rad;
      const py = Math.sin(a) * rad * 0.78;
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.closePath();
    const rg = ctx.createRadialGradient(-R * 0.3, -R * 0.3, R * 0.1, 0, 0, R * 1.1);
    rg.addColorStop(0, glowRed ? '#fca5a5' : '#a8a29e');
    rg.addColorStop(0.55, glowRed ? '#b91c1c' : '#57534e');
    rg.addColorStop(1, '#1c1917');
    ctx.fillStyle = rg;
    ctx.fill();
    ctx.strokeStyle = glowRed ? '#ef4444' : '#d6d3d1';
    ctx.lineWidth = 3;
    ctx.stroke();

    ctx.fillStyle = 'rgba(12, 10, 9, 0.45)';
    [[-0.25, -0.12, 0.18], [0.22, 0.15, 0.15], [-0.05, 0.25, 0.12]].forEach(([dx, dy, cr]) => {
      ctx.beginPath();
      ctx.arc(dx * R, dy * R, cr * R, 0, Math.PI * 2);
      ctx.fill();
    });
    ctx.restore();
  }

  function drawSatelliteIcon(ctx, x, y, rot = 0) {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(rot);
    ctx.fillStyle = '#38bdf8';
    ctx.fillRect(-26, -6, 16, 12);
    ctx.fillRect(10, -6, 16, 12);
    ctx.fillStyle = '#e2e8f0';
    ctx.fillRect(-7, -8, 14, 16);
    ctx.restore();
  }

  function drawAstronaut(ctx, x, y, opts = {}) {
    const s = opts.scale || 1;
    const t = opts.t || 0;
    const walk = opts.walk ? Math.sin(t * 5.2) : 0;
    const beamLen = opts.beamLen || 220;
    ctx.save();
    ctx.translate(x, y);
    ctx.scale(s, s);

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

    ctx.fillStyle = '#cbd5e1';
    ctx.beginPath();
    ctx.roundRect(-21, -12, 14, 28, 4);
    ctx.fill();
    ctx.fillStyle = '#ef4444';
    ctx.fillRect(-19, -7, 4, 15);

    ctx.fillStyle = '#e2e8f0';
    ctx.beginPath();
    ctx.roundRect(-9 + walk * 4, 14, 8, 17, 3);
    ctx.roundRect(1 - walk * 4, 14, 8, 17, 3);
    ctx.fill();

    ctx.fillStyle = '#f8fafc';
    ctx.beginPath();
    ctx.roundRect(-12, -11, 24, 27, 7);
    ctx.fill();
    ctx.fillStyle = '#94a3b8';
    ctx.fillRect(-7, -3, 14, 7);

    ctx.fillStyle = '#e2e8f0';
    ctx.beginPath();
    ctx.roundRect(7, -6 - walk * 3, 12, 7, 3);
    ctx.fill();

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

  function drawRidges(ctx, W, H, palette, t) {
    const sky = ctx.createLinearGradient(0, 0, 0, H * 0.78);
    if (palette === 'hot') {
      sky.addColorStop(0, '#180404');
      sky.addColorStop(0.5, '#451208');
      sky.addColorStop(1, '#991b1b');
    } else {
      sky.addColorStop(0, '#070b19');
      sky.addColorStop(0.5, '#1e293b');
      sky.addColorStop(1, '#334155');
    }
    ctx.fillStyle = sky;
    ctx.fillRect(-140, -140, W + 280, H + 280);

    if (palette === 'hot') {
      ctx.save();
      for (let i = 0; i < 16; i++) {
        const fx = ((i * 137 + t * 180) % (W + 200)) - 100;
        const fy = 180 + ((i * 97 + t * 240) % 900);
        const lg = ctx.createLinearGradient(fx - 55, fy - 55, fx, fy);
        lg.addColorStop(0, 'rgba(251,191,36,0)');
        lg.addColorStop(1, 'rgba(251,191,36,0.85)');
        ctx.strokeStyle = lg;
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.moveTo(fx - 55, fy - 55);
        ctx.lineTo(fx, fy);
        ctx.stroke();
        ctx.fillStyle = '#fef08a';
        ctx.beginPath();
        ctx.arc(fx, fy, 4.5, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.restore();
    }

    const layers = palette === 'hot'
      ? [
          { y: H * 0.66, amp: 52, freq: 0.0045, col: '#7f1d1d', spd: 5 },
          { y: H * 0.74, amp: 46, freq: 0.0065, col: '#450a0a', spd: 12 },
          { y: H * 0.83, amp: 36, freq: 0.009, col: '#280505', spd: 20 },
          { y: H * 0.91, amp: 24, freq: 0.012, col: '#140202', spd: 30 },
        ]
      : [
          { y: H * 0.66, amp: 54, freq: 0.0045, col: '#334155', spd: 5 },
          { y: H * 0.74, amp: 46, freq: 0.0065, col: '#1e293b', spd: 12 },
          { y: H * 0.83, amp: 36, freq: 0.009, col: '#0f172a', spd: 20 },
          { y: H * 0.91, amp: 24, freq: 0.012, col: '#060a12', spd: 30 },
        ];

    layers.forEach((l, li) => {
      ctx.fillStyle = l.col;
      ctx.beginPath();
      ctx.moveTo(-140, H + 140);
      for (let x = -140; x <= W + 140; x += 18) {
        const y = l.y + Math.sin((x + t * l.spd) * l.freq + li * 1.6) * l.amp
          + Math.cos((x + t * l.spd) * l.freq * 2.1) * (l.amp * 0.34);
        ctx.lineTo(x, y);
      }
      ctx.lineTo(W + 140, H + 140);
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

  // Exact 8sb2R11FeVw Black-BG Pill Subtitles (58px Bold Geometric Sans, rgba(8,8,10,0.90), #FFFFFF + #FFE600)
  function drawNextGenSubtitlePill(ctx, W, t) {
    if (!SUB_CHUNKS || !SUB_CHUNKS.length) return;
    let ch = SUB_CHUNKS.find((c) => t >= c.start - 0.04 && t <= c.end + 0.14);
    if (!ch) return;

    const wordsChunk = ch.words;
    const activeIdx = wordsChunk.findIndex((w) => t >= w.start - 0.03 && t <= w.end + 0.08);
    const tSinceChunkStart = Math.max(0, t - ch.start);

    const fontSize = 58;
    ctx.save();
    ctx.font = `800 ${fontSize}px ${FONT_SUB}`;
    ctx.textBaseline = 'middle';

    const pieces = wordsChunk.map((w, i) => (i < wordsChunk.length - 1 ? w.w + ' ' : w.w));
    const widths = pieces.map((p) => ctx.measureText(p).width);
    const textW = widths.reduce((a, b) => a + b, 0);

    const padX = 38;
    const padY = 22;
    const boxW = textW + padX * 2;
    const boxH = fontSize + padY * 2;

    const u = Math.min(1, Math.max(0, tSinceChunkStart / 0.10));
    const c1 = 1.70158, c3 = c1 + 1;
    const popScale = u < 1 ? 0.88 + 0.12 * (1 + c3 * Math.pow(u - 1, 3) + c1 * Math.pow(u - 1, 2)) : 1;

    ctx.translate(W * 0.5, 1365);
    ctx.scale(popScale, popScale);

    ctx.fillStyle = 'rgba(8, 8, 10, 0.90)';
    ctx.shadowColor = 'rgba(0, 0, 0, 0.45)';
    ctx.shadowBlur = 18;
    ctx.beginPath();
    ctx.roundRect(-boxW * 0.5, -boxH * 0.5, boxW, boxH, 16);
    ctx.fill();
    ctx.shadowBlur = 0;

    let x = -textW * 0.5;
    ctx.textAlign = 'left';
    pieces.forEach((p, i) => {
      ctx.fillStyle = i === activeIdx ? '#FFE600' : '#FFFFFF';
      ctx.fillText(p, x, 2);
      x += widths[i];
    });
    ctx.restore();
  }

  // ---------------- Scene Archetypes (Minimal On-Screen Text) ----------------

  function renderApophisFlyby(ctx, W, H, s, lt, u) {
    drawSpaceBg(ctx, W, H, lt, { sunRays: true });
    const ex = 540, ey = 850, eR = 240;
    drawEarthSphere(ctx, ex, ey, eR, lt);

    const satR = 420;
    ctx.strokeStyle = 'rgba(56, 189, 248, 0.48)';
    ctx.lineWidth = 3.5;
    ctx.setLineDash([12, 10]);
    ctx.beginPath();
    ctx.arc(ex, ey, satR, 0, Math.PI * 2);
    ctx.stroke();
    ctx.setLineDash([]);

    for (let i = 0; i < 4; i++) {
      const a = i * (Math.PI * 0.5) + lt * 0.25 + 0.4;
      drawSatelliteIcon(ctx, ex + Math.cos(a) * satR, ey + Math.sin(a) * satR, a + Math.PI * 0.5);
    }

    ctx.fillStyle = 'rgba(15, 23, 42, 0.90)';
    ctx.strokeStyle = '#38bdf8';
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.roundRect(W * 0.5 - 120, 395, 240, 44, 12);
    ctx.fill();
    ctx.stroke();
    ctx.font = `800 22px ${FONT_MONO}`;
    ctx.fillStyle = '#38bdf8';
    ctx.textAlign = 'center';
    ctx.fillText('35,786 KM', W * 0.5, 424);

    const ax = lerp(180, 860, clamp(u * 1.15));
    const ay = lerp(610, 710, clamp(u * 1.15));
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 5;
    ctx.beginPath();
    ctx.moveTo(120, 595);
    ctx.lineTo(ax, ay);
    ctx.stroke();

    drawAsteroidRock(ctx, ax, ay, 58, lt, true);

    ctx.fillStyle = '#dc2626';
    ctx.beginPath();
    ctx.roundRect(ax - 95, ay - 108, 190, 42, 10);
    ctx.fill();
    ctx.font = `900 22px ${FONT_MONO}`;
    ctx.fillStyle = '#ffffff';
    ctx.fillText('31,600 KM', ax, ay - 80);

    ctx.font = `900 120px ${FONT_DISPLAY}`;
    ctx.fillStyle = '#ffffff';
    ctx.fillText('2029', W * 0.5, 315);
  }

  function renderNukeRule(ctx, W, H, s, lt, u) {
    drawSpaceBg(ctx, W, H, lt, { sunRays: false });
    drawEarthSphere(ctx, 810, 990, 200, lt);
    drawAsteroidRock(ctx, 350, 670, 125, lt, false);

    const mx = lerp(690, 450, clamp(u * 1.35));
    const my = lerp(890, 730, clamp(u * 1.35));
    ctx.strokeStyle = '#facc15';
    ctx.lineWidth = 4;
    ctx.setLineDash([10, 8]);
    ctx.beginPath();
    ctx.moveTo(690, 890);
    ctx.lineTo(mx, my);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.save();
    ctx.translate(mx, my);
    ctx.rotate(-2.55);
    ctx.fillStyle = '#f8fafc';
    ctx.beginPath();
    ctx.roundRect(-30, -11, 60, 22, 8);
    ctx.fill();
    ctx.fillStyle = '#ef4444';
    ctx.beginPath();
    ctx.moveTo(30, -11);
    ctx.lineTo(48, 0);
    ctx.lineTo(30, 11);
    ctx.closePath();
    ctx.fill();
    ctx.restore();

    const sp = easeOutBack(clamp((u - 0.30) * 3.5));
    ctx.save();
    ctx.translate(W * 0.5, 1130);
    ctx.rotate(-0.04);
    ctx.scale(sp, sp);
    ctx.strokeStyle = '#f5c842';
    ctx.lineWidth = 4;
    ctx.fillStyle = 'rgba(20,16,8,0.92)';
    ctx.beginPath();
    ctx.roundRect(-145, -30, 290, 58, 10);
    ctx.fill();
    ctx.stroke();
    ctx.font = `900 32px ${FONT_DISPLAY}`;
    ctx.fillStyle = '#f5c842';
    ctx.textAlign = 'center';
    ctx.fillText('THE RULE', 0, 11);
    ctx.restore();
  }

  function renderShotgunBlast(ctx, W, H, s, lt, u) {
    drawSpaceBg(ctx, W, H, lt, { sunRays: false });
    drawEarthSphere(ctx, 790, 990, 220, lt);

    const bx = 290, by = 600;
    const spread = clamp(u * 1.35);
    ctx.fillStyle = 'rgba(239, 68, 68, 0.18)';
    ctx.beginPath();
    ctx.moveTo(bx, by);
    ctx.lineTo(790 - 150, 990 + 130);
    ctx.lineTo(790 + 130, 990 - 150);
    ctx.closePath();
    ctx.fill();

    FRAGMENTS.forEach((f, idx) => {
      const dist = spread * f.spd * 1.45;
      const dir = 0.66 + f.ang * 0.55;
      const fx = bx + Math.cos(dir) * dist;
      const fy = by + Math.sin(dir) * dist;
      drawAsteroidRock(ctx, fx, fy, f.rad, lt + idx, f.hot);
    });

    ctx.textAlign = 'center';
    ctx.font = `900 108px ${FONT_DISPLAY}`;
    ctx.fillStyle = '#f5c842';
    ctx.fillText('1 → 10,000', W * 0.5, 345);
  }

  function renderKillerCard(ctx, W, H, s, lt, u) {
    ctx.fillStyle = '#1d1603';
    ctx.fillRect(-140, -140, W + 280, H + 280);
    const sg = ctx.createRadialGradient(W * 0.5, H * 0.45, 40, W * 0.5, H * 0.45, 760);
    sg.addColorStop(0, '#fef08a');
    sg.addColorStop(0.52, '#facc15');
    sg.addColorStop(0.84, '#92400e');
    sg.addColorStop(1, '#1a1202');
    ctx.fillStyle = sg;
    ctx.fillRect(-140, -140, W + 280, H + 280);

    const pop = easeOutBack(clamp(u * 4.5));
    ctx.save();
    ctx.translate(W * 0.5, H * 0.45);
    ctx.scale(pop, pop);
    ctx.textAlign = 'center';
    ctx.font = `900 44px ${FONT_SUB}`;
    ctx.fillStyle = '#1c1917';
    ctx.fillText(s.eyebrow || 'KILLER #1', 0, -80);

    ctx.font = `900 144px ${FONT_DISPLAY}`;
    ctx.fillStyle = '#0c0a09';
    ctx.fillText(s.title || 'SHOTGUN', 0, 58);
    ctx.restore();
  }

  function renderSurfaceGauge(ctx, W, H, s, lt, u) {
    drawRidges(ctx, W, H, s.palette || 'hot', lt);
    drawAstronaut(ctx, 210 + (s.walk ? lt * 14 : 0), 1140, { scale: 1.25, t: lt, walk: !!s.walk, shadow: true, beamLen: 220 });

    if (s.widget === 'thermometer') {
      const cw = 760, ch = 590, cx = (W - cw) * 0.5, cy = 285;
      ctx.fillStyle = 'rgba(20, 12, 12, 0.90)';
      ctx.strokeStyle = 'rgba(239, 68, 68, 0.35)';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.roundRect(cx, cy, cw, ch, 26);
      ctx.fill();
      ctx.stroke();

      const tx = cx + 150, ty = cy + 95, th = 375;
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

      const curTemp = Math.round(lerp(18, 400, easeOutCubic(clamp(u * 1.7))));
      ctx.textAlign = 'left';
      ctx.font = `900 148px ${FONT_DISPLAY}`;
      ctx.fillStyle = '#ffffff';
      ctx.fillText(`${curTemp}°C`, cx + 335, cy + 335);
    } else if (s.widget === 'gauge') {
      const cw = 820, ch = 480, cx = (W - cw) * 0.5, cy = 320;
      ctx.fillStyle = 'rgba(16, 18, 28, 0.92)';
      ctx.strokeStyle = 'rgba(248, 113, 113, 0.35)';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.roundRect(cx, cy, cw, ch, 26);
      ctx.fill();
      ctx.stroke();

      const bx = cx + 70, bw = cw - 140;
      ctx.textAlign = 'left';
      ctx.fillStyle = '#334155';
      ctx.beginPath();
      ctx.roundRect(bx, cy + 120, bw, 62, 12);
      ctx.fill();
      ctx.fillStyle = '#38bdf8';
      ctx.beginPath();
      ctx.roundRect(bx, cy + 120, bw, 62, 12);
      ctx.fill();
      ctx.font = `900 34px ${FONT_MONO}`;
      ctx.fillStyle = '#0f172a';
      ctx.fillText('  4,000 M/S', bx + 16, cy + 162);

      ctx.fillStyle = '#334155';
      ctx.beginPath();
      ctx.roundRect(bx, cy + 250, bw, 62, 12);
      ctx.fill();
      ctx.fillStyle = '#ef4444';
      ctx.beginPath();
      ctx.roundRect(bx, cy + 250, 32, 62, 8);
      ctx.fill();
      ctx.fillStyle = '#ffffff';
      ctx.fillText('0.2 M/S', bx + 48, cy + 292);
    }
  }

  function renderXray(ctx, W, H, s, lt, u) {
    ctx.fillStyle = '#050914';
    ctx.fillRect(-140, -140, W + 280, H + 280);
    ctx.strokeStyle = 'rgba(45, 82, 138, 0.25)';
    ctx.lineWidth = 1.5;
    for (let x = -120; x <= W + 120; x += 60) {
      ctx.beginPath(); ctx.moveTo(x, -120); ctx.lineTo(x, H + 120); ctx.stroke();
    }
    for (let y = -120; y <= H + 120; y += 60) {
      ctx.beginPath(); ctx.moveTo(-120, y); ctx.lineTo(W + 120, y); ctx.stroke();
    }

    const bx = W * 0.5, by = 520;
    ctx.strokeStyle = '#4ade80';
    ctx.lineWidth = 7;
    ctx.beginPath();
    ctx.arc(bx + 170, by + 60, 150, 0, Math.PI * 2);
    ctx.stroke();

    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 4.5;
    for (let i = -3; i <= 3; i++) {
      ctx.beginPath();
      ctx.moveTo(bx - 250, by - 90 + i * 12);
      ctx.lineTo(bx + 60, by + 40 + i * 26);
      ctx.stroke();
      ctx.fillStyle = '#ef4444';
      ctx.beginPath();
      ctx.arc(bx + 60, by + 40 + i * 26, 8, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.fillStyle = '#181014';
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.roundRect(W * 0.5 - 150, 770, 300, 62, 16);
    ctx.fill();
    ctx.stroke();
    ctx.textAlign = 'center';
    ctx.font = `900 34px ${FONT_MONO}`;
    ctx.fillStyle = '#fca5a5';
    ctx.fillText('20 KM / S', W * 0.5, 812);

    if (s.receipt) {
      const rp = easeOutBack(clamp((u - 0.1) * 3.5));
      ctx.save();
      ctx.translate(W * 0.5, 1040);
      ctx.scale(rp, rp);
      ctx.fillStyle = '#f8fafc';
      ctx.beginPath();
      ctx.roundRect(-235, -135, 470, 270, 10);
      ctx.fill();
      ctx.fillStyle = '#0f172a';
      ctx.textAlign = 'center';
      ctx.font = `900 28px ${FONT_MONO}`;
      ctx.fillText(s.receipt.header, 0, -90);
      ctx.font = `700 22px ${FONT_MONO}`;
      s.receipt.lines.forEach(([k, v], i) => {
        ctx.textAlign = 'left';
        ctx.fillText(k, -200, -38 + i * 40);
        ctx.textAlign = 'right';
        ctx.fillText(v, 200, -38 + i * 40);
      });

      ctx.translate(0, 20);
      ctx.rotate(-0.14);
      ctx.strokeStyle = '#dc2626';
      ctx.lineWidth = 5;
      ctx.fillStyle = 'rgba(255,255,255,0.94)';
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
  }

  function renderEvidence(ctx, W, H, s, lt, u) {
    drawRidges(ctx, W, H, s.palette || 'day', lt);

    const img = IMAGES[s.imgKey];
    const pw = 800, ph = 660;
    ctx.save();
    ctx.translate(W * 0.5, 740);
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

    ctx.font = `800 21px ${FONT_MONO}`;
    ctx.fillStyle = '#1e293b';
    ctx.textAlign = 'center';
    ctx.fillText((s.credit || 'NASA / JPL-Caltech').slice(0, 52), 0, ph * 0.5 + 36);
    ctx.restore();
  }

  function renderDartDeflect(ctx, W, H, s, lt, u) {
    drawSpaceBg(ctx, W, H, lt, { sunRays: true });
    const ex = 760, ey = 920;
    drawEarthSphere(ctx, ex, ey, 175, lt);

    ctx.strokeStyle = 'rgba(239, 68, 68, 0.45)';
    ctx.lineWidth = 4.5;
    ctx.setLineDash([10, 10]);
    ctx.beginPath();
    ctx.moveTo(160, 480);
    ctx.lineTo(ex, ey);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.strokeStyle = '#4ade80';
    ctx.lineWidth = 7;
    ctx.beginPath();
    ctx.moveTo(160, 480);
    ctx.quadraticCurveTo(540, 580, 940, 560);
    ctx.stroke();

    const ax = lerp(240, 860, clamp(u * 1.25));
    const ay = lerp(500, 565, clamp(u * 1.25));
    drawAsteroidRock(ctx, ax, ay, 52, lt, false);

    const sp = easeOutBack(clamp((u - 0.25) * 3.5));
    ctx.save();
    ctx.translate(W * 0.5, 1140);
    ctx.rotate(-0.04);
    ctx.scale(sp, sp);
    ctx.fillStyle = 'rgba(6, 28, 18, 0.94)';
    ctx.strokeStyle = '#4ade80';
    ctx.lineWidth = 6;
    ctx.beginPath();
    ctx.roundRect(-240, -48, 480, 96, 14);
    ctx.fill();
    ctx.stroke();
    ctx.font = `900 48px ${FONT_DISPLAY}`;
    ctx.fillStyle = '#4ade80';
    ctx.textAlign = 'center';
    ctx.fillText('DART · 2 CM/S', 0, 17);
    ctx.restore();
  }

  function renderFrameAt(ctx, W, H, t) {
    if (!BEATS.length) return;
    const clampedT = clamp(t, 0, BEATS[BEATS.length - 1].end - 0.0001);
    const sc = BEATS.find((b) => clampedT >= b.start && clampedT < b.end) || BEATS[BEATS.length - 1];
    const lt = clampedT - sc.start;
    const u = clamp(lt / sc.dur);

    const subDur = sc.dur / sc.nSub;
    const subIdx = Math.min(sc.nSub - 1, Math.floor(lt / subDur));
    const subLt = lt - subIdx * subDur;

    ctx.save();
    applyNextGenCamera(ctx, W, H, sc, lt, subIdx, subLt, subDur);

    const map = {
      apophis_flyby: renderApophisFlyby,
      nuke_rule: renderNukeRule,
      shotgun_blast: renderShotgunBlast,
      killer_card: renderKillerCard,
      surface_gauge: renderSurfaceGauge,
      xray: renderXray,
      evidence: renderEvidence,
      dart_deflect: renderDartDeflect,
    };
    const fn = map[sc.type] || renderApophisFlyby;
    fn(ctx, W, H, sc, lt, u);
    ctx.restore();

    drawVignette(ctx, W, H, 0.45);
    drawNextGenSubtitlePill(ctx, W, clampedT);
  }

  window.ORBIT = {
    register({ scenes, assets = {}, beats = [] }) {
      SCENES = scenes;
      BEATS = buildTimeline(scenes);
      SUB_CHUNKS = buildWordChunks(beats);
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
