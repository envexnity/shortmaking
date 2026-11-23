/* Orbit 2D Space Short Renderer — Next-Gen Black Hole (Native 1080x1920 @ 30fps)
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
    const r = seeded(9917);
    return Array.from({ length: 240 }, () => ({
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

  function applyNextGenCamera(ctx, W, H, sc, lt, subIdx, subLt, subDur) {
    const uSub = clamp(subLt / subDur);
    const globalSub = sc.idx * 5 + subIdx;

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

  function drawSpaceBg(ctx, W, H, t) {
    const g = ctx.createLinearGradient(0, 0, W * 0.5, H);
    g.addColorStop(0, '#03040b');
    g.addColorStop(0.55, '#070a1c');
    g.addColorStop(1, '#110b29');
    ctx.fillStyle = g;
    ctx.fillRect(-140, -140, W + 280, H + 280);

    for (const st of STARS) {
      const px = (st.x + t * 2.4) % W;
      const a = st.alpha * (0.65 + 0.35 * Math.sin(t * st.speed + st.phase));
      ctx.fillStyle = `rgba(235, 244, 255, ${a.toFixed(3)})`;
      ctx.beginPath();
      ctx.arc(px, st.y, st.size, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  function drawBlackHole(ctx, cx, cy, R, t = 0) {
    ctx.save();
    const halo = ctx.createRadialGradient(cx, cy, R * 0.85, cx, cy, R * 2.15);
    halo.addColorStop(0, 'rgba(251, 146, 60, 0.72)');
    halo.addColorStop(0.28, 'rgba(234, 88, 12, 0.38)');
    halo.addColorStop(0.62, 'rgba(124, 58, 237, 0.16)');
    halo.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = halo;
    ctx.beginPath();
    ctx.arc(cx, cy, R * 2.15, 0, Math.PI * 2);
    ctx.fill();

    ctx.strokeStyle = 'rgba(253, 224, 71, 0.55)';
    ctx.lineWidth = R * 0.16;
    ctx.beginPath();
    ctx.ellipse(cx, cy - R * 0.08, R * 1.18, R * 1.04, 0, Math.PI * 1.05, Math.PI * 1.95);
    ctx.stroke();

    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(-0.14 + Math.sin(t * 0.4) * 0.02);
    const dg = ctx.createRadialGradient(0, 0, R * 0.6, 0, 0, R * 1.95);
    dg.addColorStop(0, '#fef08a');
    dg.addColorStop(0.42, '#f97316');
    dg.addColorStop(0.78, '#9a3412');
    dg.addColorStop(1, 'rgba(154,52,18,0)');
    ctx.fillStyle = dg;
    ctx.beginPath();
    ctx.ellipse(0, 0, R * 1.95, R * 0.44, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    ctx.fillStyle = '#000000';
    ctx.beginPath();
    ctx.arc(cx, cy, R * 0.78, 0, Math.PI * 2);
    ctx.fill();

    ctx.strokeStyle = '#fde047';
    ctx.lineWidth = 4.5;
    ctx.beginPath();
    ctx.arc(cx, cy, R * 0.79, 0, Math.PI * 2);
    ctx.stroke();

    ctx.save();
    ctx.translate(cx, cy + R * 0.08);
    ctx.rotate(-0.14 + Math.sin(t * 0.4) * 0.02);
    const fg = ctx.createLinearGradient(-R * 1.8, 0, R * 1.8, 0);
    fg.addColorStop(0, 'rgba(249,115,22,0)');
    fg.addColorStop(0.25, '#fde047');
    fg.addColorStop(0.5, '#ffffff');
    fg.addColorStop(0.75, '#f97316');
    fg.addColorStop(1, 'rgba(249,115,22,0)');
    ctx.fillStyle = fg;
    ctx.beginPath();
    ctx.ellipse(0, 0, R * 1.85, R * 0.14, 0, 0, Math.PI);
    ctx.fill();
    ctx.restore();

    ctx.restore();
  }

  function drawAstronaut(ctx, x, y, opts = {}) {
    const s = opts.scale || 1;
    const t = opts.t || 0;
    const walk = opts.walk ? Math.sin(t * 5.2) : 0;
    const stretchY = opts.stretchY || 1;
    const squeezeX = opts.squeezeX || 1;
    const redshift = opts.redshift || 0;
    const beamLen = opts.beamLen !== undefined ? opts.beamLen : 220;

    ctx.save();
    ctx.translate(x, y);
    ctx.scale(s * squeezeX, s * stretchY);

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

    ctx.fillStyle = redshift > 0.3 ? '#b91c1c' : '#cbd5e1';
    ctx.beginPath();
    ctx.roundRect(-21, -12, 14, 28, 4);
    ctx.fill();
    ctx.fillStyle = '#ef4444';
    ctx.fillRect(-19, -7, 4, 15);

    ctx.fillStyle = redshift > 0.3 ? '#dc2626' : '#e2e8f0';
    ctx.beginPath();
    ctx.roundRect(-9 + walk * 4, 14, 8, 17, 3);
    ctx.roundRect(1 - walk * 4, 14, 8, 17, 3);
    ctx.fill();

    ctx.fillStyle = redshift > 0.3 ? '#ef4444' : '#f8fafc';
    ctx.beginPath();
    ctx.roundRect(-12, -11, 24, 27, 7);
    ctx.fill();
    ctx.fillStyle = '#94a3b8';
    ctx.fillRect(-7, -3, 14, 7);

    ctx.fillStyle = redshift > 0.3 ? '#dc2626' : '#e2e8f0';
    ctx.beginPath();
    ctx.roundRect(7, -6 - walk * 3, 12, 7, 3);
    ctx.fill();

    ctx.fillStyle = redshift > 0.3 ? '#f87171' : '#ffffff';
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

  function drawRidges(ctx, W, H, t) {
    const sky = ctx.createLinearGradient(0, 0, 0, H * 0.78);
    sky.addColorStop(0, '#040510');
    sky.addColorStop(0.5, '#171033');
    sky.addColorStop(1, '#4c1d95');
    ctx.fillStyle = sky;
    ctx.fillRect(-140, -140, W + 280, H + 280);

    drawBlackHole(ctx, 820, 400, 95, t);

    const layers = [
      { y: H * 0.68, amp: 52, freq: 0.0045, col: '#2e1065', spd: 5 },
      { y: H * 0.76, amp: 46, freq: 0.0065, col: '#1e1b4b', spd: 12 },
      { y: H * 0.84, amp: 36, freq: 0.009, col: '#0f172a', spd: 20 },
      { y: H * 0.92, amp: 24, freq: 0.012, col: '#050814', spd: 30 },
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

  function renderBhEstablish(ctx, W, H, s, lt, u) {
    drawSpaceBg(ctx, W, H, lt);

    if (s.tidalMode) {
      drawBlackHole(ctx, W * 0.5, 1340, 270, lt);
      const stretch = 1 + 1.05 * smoothstep(clamp(u * 1.4));
      const squeeze = 1 - 0.35 * smoothstep(clamp(u * 1.4));
      drawAstronaut(ctx, W * 0.5, 650, { scale: 1.9, t: lt, stretchY: stretch, squeezeX: squeeze, beamLen: 0 });

      ctx.fillStyle = 'rgba(15, 23, 42, 0.92)';
      ctx.strokeStyle = '#38bdf8';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.roundRect(110, 445, 250, 52, 12);
      ctx.fill();
      ctx.stroke();
      ctx.font = `900 26px ${FONT_MONO}`;
      ctx.fillStyle = '#38bdf8';
      ctx.textAlign = 'center';
      ctx.fillText('100 G', 235, 480);

      ctx.fillStyle = 'rgba(40, 8, 12, 0.94)';
      ctx.strokeStyle = '#ef4444';
      ctx.beginPath();
      ctx.roundRect(670, 770, 290, 54, 12);
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = '#fca5a5';
      ctx.fillText('1,000,000 G', 815, 806);
    } else {
      drawBlackHole(ctx, 590, 880, 270, lt);
      const ax = 220, ay = 560 + Math.sin(lt * 1.6) * 12;
      drawAstronaut(ctx, ax, ay, { scale: 1.35, t: lt, beamLen: 220 });
      drawYouCallout(ctx, ax, ay, 165, 420);

      const sp = easeOutBack(clamp((u - 0.30) * 3.5));
      ctx.save();
      ctx.translate(W * 0.5, 1185);
      ctx.rotate(-0.04);
      ctx.scale(sp, sp);
      ctx.strokeStyle = '#f5c842';
      ctx.lineWidth = 4;
      ctx.fillStyle = 'rgba(20,16,8,0.92)';
      ctx.beginPath();
      ctx.roundRect(-140, -30, 280, 58, 10);
      ctx.fill();
      ctx.stroke();
      ctx.font = `900 32px ${FONT_DISPLAY}`;
      ctx.fillStyle = '#f5c842';
      ctx.textAlign = 'center';
      ctx.fillText('THE RULE', 0, 11);
      ctx.restore();
    }
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

    ctx.font = `900 132px ${FONT_DISPLAY}`;
    ctx.fillStyle = '#0c0a09';
    ctx.fillText(s.title || 'NOODLED', 0, 56);
    ctx.restore();
  }

  function renderSurfaceGauge(ctx, W, H, s, lt, u) {
    drawRidges(ctx, W, H, lt);

    if (s.widget === 'gauge') {
      const cw = 780, ch = 500, cx = (W - cw) * 0.5, cy = 320;
      ctx.fillStyle = 'rgba(20, 18, 28, 0.94)';
      ctx.strokeStyle = 'rgba(251, 191, 36, 0.35)';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.roundRect(cx, cy, cw, ch, 26);
      ctx.fill();
      ctx.stroke();

      const frac = easeOutCubic(clamp(u * 1.45));
      const dialX = W * 0.5, dialY = cy + 280, dialR = 175;
      ctx.strokeStyle = '#334155';
      ctx.lineWidth = 22;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.arc(dialX, dialY, dialR, Math.PI * 0.85, Math.PI * 2.15);
      ctx.stroke();

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

      ctx.textAlign = 'center';
      ctx.font = `900 84px ${FONT_DISPLAY}`;
      ctx.fillStyle = '#ffffff';
      ctx.fillText('1,000,000 G', dialX, dialY + 25);
    } else if (s.widget === 'time_dilation') {
      const cw = 820, ch = 360, cx = (W - cw) * 0.5, cy = 360;
      ctx.fillStyle = 'rgba(16, 12, 26, 0.94)';
      ctx.strokeStyle = 'rgba(248, 113, 113, 0.35)';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.roundRect(cx, cy, cw, ch, 26);
      ctx.fill();
      ctx.stroke();

      ctx.textAlign = 'center';
      ctx.fillStyle = '#0f172a';
      ctx.strokeStyle = '#38bdf8';
      ctx.beginPath();
      ctx.roundRect(cx + 40, cy + 70, 350, 220, 18);
      ctx.fill();
      ctx.stroke();
      ctx.font = `800 26px ${FONT_MONO}`;
      ctx.fillStyle = '#38bdf8';
      ctx.fillText('YOU', cx + 215, cy + 122);
      ctx.font = `900 80px ${FONT_DISPLAY}`;
      ctx.fillStyle = '#ffffff';
      ctx.fillText('1.0 SEC', cx + 215, cy + 225);

      const yrs = Math.round(lerp(10, 10000, easeOutCubic(clamp(u * 1.5))));
      ctx.fillStyle = '#1f0d1d';
      ctx.strokeStyle = '#facc15';
      ctx.beginPath();
      ctx.roundRect(cx + 430, cy + 70, 350, 220, 18);
      ctx.fill();
      ctx.stroke();
      ctx.font = `800 26px ${FONT_MONO}`;
      ctx.fillStyle = '#facc15';
      ctx.fillText('CREW', cx + 605, cy + 122);
      ctx.font = `900 72px ${FONT_DISPLAY}`;
      ctx.fillStyle = '#facc15';
      ctx.fillText(`${yrs.toLocaleString()} YRS`, cx + 605, cy + 225);

      drawAstronaut(ctx, 220, 1140, { scale: 1.35, t: 0, redshift: 0.85, beamLen: 180 });
    } else if (s.widget === 'escape_speed') {
      const cw = 820, ch = 460, cx = (W - cw) * 0.5, cy = 330;
      ctx.fillStyle = 'rgba(14, 16, 28, 0.94)';
      ctx.strokeStyle = 'rgba(56, 189, 248, 0.35)';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.roundRect(cx, cy, cw, ch, 26);
      ctx.fill();
      ctx.stroke();

      const bx = cx + 70, bw = cw - 140;
      ctx.textAlign = 'left';
      ctx.font = `900 30px ${FONT_MONO}`;
      ctx.fillStyle = '#334155';
      ctx.beginPath();
      ctx.roundRect(bx, cy + 80, bw, 58, 10);
      ctx.fill();
      ctx.fillStyle = '#38bdf8';
      ctx.beginPath();
      ctx.roundRect(bx, cy + 80, 32, 58, 8);
      ctx.fill();
      ctx.fillStyle = '#ffffff';
      ctx.fillText('192 KM/S', bx + 48, cy + 120);

      ctx.fillStyle = '#334155';
      ctx.beginPath();
      ctx.roundRect(bx, cy + 195, bw, 58, 10);
      ctx.fill();
      ctx.fillStyle = '#facc15';
      ctx.beginPath();
      ctx.roundRect(bx, cy + 195, bw * 0.82, 58, 10);
      ctx.fill();
      ctx.fillStyle = '#0f172a';
      ctx.fillText('  300,000 KM/S (c)', bx + 16, cy + 235);

      ctx.fillStyle = '#dc2626';
      ctx.beginPath();
      ctx.roundRect(bx, cy + 310, bw, 62, 10);
      ctx.fill();
      ctx.fillStyle = '#ffffff';
      ctx.fillText('  > 300,000 KM/S', bx + 16, cy + 352);
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

    const bx = W * 0.5, by = 480;
    const stretch = 1 + 0.52 * smoothstep(clamp(u * 1.6));
    const squeeze = 1 - 0.36 * smoothstep(clamp(u * 1.6));
    ctx.strokeStyle = '#4ade80';
    ctx.lineWidth = 7;
    ctx.beginPath();
    ctx.ellipse(bx, by - 120 * stretch, 76 * squeeze, 82 * stretch, 0, 0, Math.PI * 2);
    ctx.stroke();
    ctx.beginPath();
    ctx.roundRect(bx - 115 * squeeze, by - 20, 230 * squeeze, 230 * stretch, 44);
    ctx.stroke();

    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 6;
    [-1, 1].forEach((dir) => {
      const sx = bx + dir * 270, ex = bx + dir * 130;
      ctx.beginPath();
      ctx.moveTo(sx, by + 95);
      ctx.lineTo(ex, by + 95);
      ctx.stroke();
    });

    if (s.receipt) {
      const rp = easeOutBack(clamp((u - 0.1) * 3.5));
      ctx.save();
      ctx.translate(W * 0.5, 1020);
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
    drawRidges(ctx, W, H, lt);

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

  function renderM87Twist(ctx, W, H, s, lt, u) {
    drawSpaceBg(ctx, W, H, lt);

    const cx = W * 0.5, cy = 690;
    drawBlackHole(ctx, cx, cy, 300, lt);

    ctx.strokeStyle = 'rgba(56, 189, 248, 0.85)';
    ctx.lineWidth = 3;
    ctx.setLineDash([8, 8]);
    ctx.beginPath();
    ctx.arc(cx, cy, 85, 0, Math.PI * 2);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.textAlign = 'center';
    ctx.font = `800 22px ${FONT_MONO}`;
    ctx.fillStyle = '#38bdf8';
    ctx.fillText('PLUTO ORBIT', cx, cy + 8);

    drawAstronaut(ctx, cx - 225 + u * 65, cy - 155, { scale: 1.4, t: lt, beamLen: 210 });

    ctx.font = `900 108px ${FONT_DISPLAY}`;
    ctx.fillStyle = '#ffffff';
    ctx.fillText('M87*', W * 0.5, 295);

    const sp = easeOutBack(clamp((u - 0.28) * 3.5));
    ctx.save();
    ctx.translate(W * 0.5, 1130);
    ctx.rotate(-0.04);
    ctx.scale(sp, sp);
    ctx.fillStyle = 'rgba(24, 8, 8, 0.94)';
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 6;
    ctx.beginPath();
    ctx.roundRect(-240, -48, 480, 96, 14);
    ctx.fill();
    ctx.stroke();
    ctx.font = `900 48px ${FONT_DISPLAY}`;
    ctx.fillStyle = '#ef4444';
    ctx.fillText('ZERO EXIT', 0, 17);
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
      bh_establish: renderBhEstablish,
      killer_card: renderKillerCard,
      surface_gauge: renderSurfaceGauge,
      xray: renderXray,
      evidence: renderEvidence,
      m87_twist: renderM87Twist,
    };
    const fn = map[sc.type] || renderBhEstablish;
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
