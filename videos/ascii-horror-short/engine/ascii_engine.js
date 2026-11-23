/* Real-Time 1080x1920 ASCII Horror Rendering Engine
 * - 72 x 80 crisp monospace cell grid (15 x 24 px/cell) backed by a 144 x 160 (2x) luminance/depth field
 * - Automated Sobel directional edge glyph selection (/, \, |, _) + luminance ramp + explicit ASCII overrides
 * - Authentic CRT phosphor glow, gentle scanlines, horizontal glitch shifts, chromatic split on impact kicks
 * - Exact 8sb2R11FeVw black-pill subtitle renderer (Law #27)
 */
window.ASCII = (() => {
  const W = 1080;
  const H = 1920;
  const COLS = 72;
  const ROWS = 80;
  const CELL_W = 15; // 72 * 15 = 1080
  const CELL_H = 24; // 80 * 24 = 1920

  // 2x supersampled virtual field for crisp Sobel edge detection
  const FW = COLS * 2; // 144
  const FH = ROWS * 2; // 160

  const fLuma = new Float32Array(FW * FH);
  const fR = new Float32Array(FW * FH);
  const fG = new Float32Array(FW * FH);
  const fB = new Float32Array(FW * FH);
  const fEdgeEnable = new Uint8Array(FW * FH); // 1 = allow Sobel edge glyph override

  const cellOverride = new Array(COLS * ROWS).fill('');
  const cellOvColor = new Int32Array(COLS * ROWS); // packed 0xRRGGBB or -1
  const cellShakeX = new Int8Array(COLS * ROWS);

  // Offscreen crisp 1080x1920 framebuffer
  const asciiCanvas = document.createElement('canvas');
  asciiCanvas.width = W;
  asciiCanvas.height = H;
  const asciiCtx = asciiCanvas.getContext('2d', { willReadFrequently: false });
  const imgData = asciiCtx.createImageData(W, H);
  const buf32 = new Uint32Array(imgData.data.buffer);

  // Downsampled glow buffer for soft GPU CRT phosphor halation
  const glowCanvas = document.createElement('canvas');
  glowCanvas.width = 270;
  glowCanvas.height = 480;
  const glowCtx = glowCanvas.getContext('2d');

  // Pre-baked crisp monospace alpha glyph atlas
  const RAMP = " .,:;-=+*#%@";
  const EXTRA = "░▒▓█/|\\_<>()[]{}^!?~`'\"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  const ALL_CHARS = Array.from(new Set((RAMP + EXTRA).split('')));
  const glyphAlpha = new Map();

  function buildGlyphAtlas() {
    const gc = document.createElement('canvas');
    gc.width = CELL_W;
    gc.height = CELL_H;
    const gctx = gc.getContext('2d', { willReadFrequently: true });
    for (const ch of ALL_CHARS) {
      gctx.clearRect(0, 0, CELL_W, CELL_H);
      if (ch === ' ') {
        glyphAlpha.set(ch, new Uint8Array(CELL_W * CELL_H));
        continue;
      }
      if (ch === '░' || ch === '▒' || ch === '▓' || ch === '█') {
        const arr = new Uint8Array(CELL_W * CELL_H);
        const dens = ch === '░' ? 0.28 : ch === '▒' ? 0.54 : ch === '▓' ? 0.78 : 0.94;
        for (let y = 1; y < CELL_H - 1; y++) {
          for (let x = 1; x < CELL_W - 1; x++) {
            const b = ((x & 1) ^ (y & 1)) * 0.5 + (((x >> 1) & 1) ^ ((y >> 1) & 1)) * 0.25;
            if (ch === '█' || b < dens) arr[y * CELL_W + x] = 240;
          }
        }
        glyphAlpha.set(ch, arr);
        continue;
      }
      gctx.fillStyle = '#ffffff';
      gctx.font = '700 21px "Cascadia Mono", "Consolas", "Courier New", monospace';
      gctx.textAlign = 'center';
      gctx.textBaseline = 'middle';
      gctx.fillText(ch, CELL_W * 0.5, CELL_H * 0.52);
      const d = gctx.getImageData(0, 0, CELL_W, CELL_H).data;
      const arr = new Uint8Array(CELL_W * CELL_H);
      for (let i = 0; i < CELL_W * CELL_H; i++) {
        // Boost thin font stroke anti-aliasing slightly so characters pop cleanly at 1080x1920
        const a = d[i * 4 + 3];
        arr[i] = a > 18 ? Math.min(255, Math.round(a * 1.18)) : 0;
      }
      glyphAlpha.set(ch, arr);
    }
  }
  buildGlyphAtlas();

  function getGlyph(ch) {
    return glyphAlpha.get(ch) || glyphAlpha.get('#');
  }

  function clearField(bgLuma = 0.03, r = 10, g = 28, b = 18) {
    fLuma.fill(bgLuma);
    fR.fill(r);
    fG.fill(g);
    fB.fill(b);
    fEdgeEnable.fill(0);
    cellOverride.fill('');
    cellOvColor.fill(-1);
    cellShakeX.fill(0);
  }

  function setPx(x, y, luma, r, g, b, edge = 1) {
    const ix = x | 0;
    const iy = y | 0;
    if (ix < 0 || ix >= FW || iy < 0 || iy >= FH) return;
    const idx = iy * FW + ix;
    fLuma[idx] = Math.max(0, Math.min(1, luma));
    fR[idx] = r;
    fG[idx] = g;
    fB[idx] = b;
    fEdgeEnable[idx] = edge;
  }

  function blendPx(x, y, luma, r, g, b, alpha = 1, edge = 1) {
    const ix = x | 0;
    const iy = y | 0;
    if (ix < 0 || ix >= FW || iy < 0 || iy >= FH) return;
    const idx = iy * FW + ix;
    const a = Math.max(0, Math.min(1, alpha));
    const inv = 1 - a;
    fLuma[idx] = Math.max(0, Math.min(1, fLuma[idx] * inv + luma * a));
    fR[idx] = fR[idx] * inv + r * a;
    fG[idx] = fG[idx] * inv + g * a;
    fB[idx] = fB[idx] * inv + b * a;
    if (edge) fEdgeEnable[idx] = 1;
  }

  function addGlowPx(x, y, lumaAdd, rAdd, gAdd, bAdd) {
    const ix = x | 0;
    const iy = y | 0;
    if (ix < 0 || ix >= FW || iy < 0 || iy >= FH) return;
    const idx = iy * FW + ix;
    fLuma[idx] = Math.min(1, fLuma[idx] + lumaAdd);
    fR[idx] = Math.min(255, fR[idx] + rAdd);
    fG[idx] = Math.min(255, fG[idx] + gAdd);
    fB[idx] = Math.min(255, fB[idx] + bAdd);
  }

  function fillBox(x, y, w, h, luma, r, g, b, edge = 1) {
    const x0 = Math.max(0, Math.round(x));
    const y0 = Math.max(0, Math.round(y));
    const x1 = Math.min(FW, Math.round(x + w));
    const y1 = Math.min(FH, Math.round(y + h));
    for (let yy = y0; yy < y1; yy++) {
      for (let xx = x0; xx < x1; xx++) {
        setPx(xx, yy, luma, r, g, b, edge);
      }
    }
  }

  function fillDisk(cx, cy, rad, luma, r, g, b, falloff = 0, edge = 1) {
    const r2 = rad * rad;
    const x0 = Math.max(0, Math.floor(cx - rad));
    const y0 = Math.max(0, Math.floor(cy - rad));
    const x1 = Math.min(FW - 1, Math.ceil(cx + rad));
    const y1 = Math.min(FH - 1, Math.ceil(cy + rad));
    for (let yy = y0; yy <= y1; yy++) {
      for (let xx = x0; xx <= x1; xx++) {
        const dx = xx - cx;
        const dy = yy - cy;
        const d2 = dx * dx + dy * dy;
        if (d2 <= r2) {
          const u = Math.sqrt(d2) / Math.max(0.5, rad);
          const shade = falloff > 0 ? Math.pow(1 - u, falloff) : 1;
          blendPx(xx, yy, luma * shade, r * (0.45 + 0.55 * shade), g * (0.45 + 0.55 * shade), b * (0.45 + 0.55 * shade), shade, edge);
        }
      }
    }
  }

  function fillCapsule(x0, y0, x1, y1, rad, luma, r, g, b, edge = 1) {
    const minX = Math.max(0, Math.floor(Math.min(x0, x1) - rad));
    const maxX = Math.min(FW - 1, Math.ceil(Math.max(x0, x1) + rad));
    const minY = Math.max(0, Math.floor(Math.min(y0, y1) - rad));
    const maxY = Math.min(FH - 1, Math.ceil(Math.max(y0, y1) + rad));
    const vx = x1 - x0;
    const vy = y1 - y0;
    const len2 = vx * vx + vy * vy || 1;
    for (let yy = minY; yy <= maxY; yy++) {
      for (let xx = minX; xx <= maxX; xx++) {
        const wx = xx - x0;
        const wy = yy - y0;
        const proj = Math.max(0, Math.min(1, (wx * vx + wy * vy) / len2));
        const px = x0 + proj * vx;
        const py = y0 + proj * vy;
        const dist = Math.hypot(xx - px, yy - py);
        if (dist <= rad) {
          const core = 1 - (dist / Math.max(0.4, rad)) * 0.45;
          setPx(xx, yy, luma * core, r * core, g * core, b * core, edge);
        }
      }
    }
  }

  function putCellChar(col, row, ch, hexColor = null) {
    if (col < 0 || col >= COLS || row < 0 || row >= ROWS) return;
    const idx = row * COLS + col;
    cellOverride[idx] = ch;
    if (hexColor) {
      cellOvColor[idx] = parseInt(hexColor.slice(1), 16);
    }
  }

  function putCellString(col, row, text, hexColor = null, center = false) {
    const startCol = center ? Math.round(col - text.length * 0.5) : Math.round(col);
    for (let i = 0; i < text.length; i++) {
      putCellChar(startCol + i, Math.round(row), text[i], hexColor);
    }
  }

  function drawAsciiBox(c0, r0, w, h, hexColor) {
    putCellChar(c0, r0, '+', hexColor);
    putCellChar(c0 + w - 1, r0, '+', hexColor);
    putCellChar(c0, r0 + h - 1, '+', hexColor);
    putCellChar(c0 + w - 1, r0 + h - 1, '+', hexColor);
    for (let c = c0 + 1; c < c0 + w - 1; c++) {
      putCellChar(c, r0, '-', hexColor);
      putCellChar(c, r0 + h - 1, '-', hexColor);
    }
    for (let r = r0 + 1; r < r0 + h - 1; r++) {
      putCellChar(c0, r, '|', hexColor);
      putCellChar(c0 + w - 1, r, '|', hexColor);
    }
  }

  function seeded(seed) {
    let s = seed | 0 || 12345;
    return () => {
      s = (s * 1664525 + 1013904223) | 0;
      return (s >>> 0) / 4294967296;
    };
  }

  // Convert 2x field -> crisp 1080x1920 ASCII glyph framebuffer with Sobel edges & CRT effects
  function renderAsciiBuffer(opts = {}) {
    const bgHex = opts.bgHex || 0x050907;
    const bgR = (bgHex >> 16) & 255;
    const bgG = (bgHex >> 8) & 255;
    const bgB = bgHex & 255;
    const bgABGR = (255 << 24) | (bgB << 16) | (bgG << 8) | bgR;
    buf32.fill(bgABGR);

    const edgeThr = opts.edgeThreshold ?? 0.21;
    const chromaShift = opts.chromaShift || 0; // px horizontal R/B split during scares
    const glitchSeed = opts.glitchSeed || 0;
    const glitchAmt = opts.glitchAmt || 0;
    const rng = glitchAmt > 0 ? seeded(glitchSeed) : null;

    // Row glitch offsets
    const rowShift = new Int8Array(ROWS);
    if (rng && glitchAmt > 0) {
      for (let r = 0; r < ROWS; r++) {
        if (rng() < glitchAmt * 0.25) {
          rowShift[r] = Math.round((rng() - 0.5) * 6 * glitchAmt);
        }
      }
    }

    for (let row = 0; row < ROWS; row++) {
      const fy = row * 2;
      const rShift = rowShift[row];
      for (let col = 0; col < COLS; col++) {
        const cIdx = row * COLS + col;
        const sCol = col - rShift;
        let ch = cellOverride[cIdx];
        let cr = 0, cg = 0, cb = 0;

        if (ch) {
          const packed = cellOvColor[cIdx];
          if (packed >= 0) {
            cr = (packed >> 16) & 255;
            cg = (packed >> 8) & 255;
            cb = packed & 255;
          } else {
            const sc = Math.max(0, Math.min(COLS - 1, sCol));
            const fx = sc * 2;
            const fi = fy * FW + fx;
            cr = fR[fi]; cg = fG[fi]; cb = fB[fi];
          }
        } else {
          const sc = Math.max(0, Math.min(COLS - 1, sCol));
          const fx = sc * 2;
          // Average 2x2 sub-block for cell luma & color
          const i00 = fy * FW + fx;
          const i10 = fy * FW + Math.min(FW - 1, fx + 1);
          const i01 = Math.min(FH - 1, fy + 1) * FW + fx;
          const i11 = Math.min(FH - 1, fy + 1) * FW + Math.min(FW - 1, fx + 1);

          const lum = (fLuma[i00] + fLuma[i10] + fLuma[i01] + fLuma[i11]) * 0.25;
          cr = (fR[i00] + fR[i10] + fR[i01] + fR[i11]) * 0.25;
          cg = (fG[i00] + fG[i10] + fG[i01] + fG[i11]) * 0.25;
          cb = (fB[i00] + fB[i10] + fB[i01] + fB[i11]) * 0.25;

          const edgeOn = fEdgeEnable[i00] | fEdgeEnable[i10] | fEdgeEnable[i01] | fEdgeEnable[i11];
          let pickedEdge = '';
          if (edgeOn && fx > 1 && fx < FW - 2 && fy > 1 && fy < FH - 2) {
            const tl = fLuma[(fy - 1) * FW + (fx - 1)];
            const tc = fLuma[(fy - 1) * FW + fx];
            const tr = fLuma[(fy - 1) * FW + (fx + 1)];
            const ml = fLuma[fy * FW + (fx - 1)];
            const mr = fLuma[fy * FW + (fx + 1)];
            const bl = fLuma[(fy + 1) * FW + (fx - 1)];
            const bc = fLuma[(fy + 1) * FW + fx];
            const br = fLuma[(fy + 1) * FW + (fx + 1)];
            const gx = (tr + 2 * mr + br) - (tl + 2 * ml + bl);
            const gy = (bl + 2 * bc + br) - (tl + 2 * tc + tr);
            const mag = Math.hypot(gx, gy);
            if (mag > edgeThr) {
              // Tangent direction is perpendicular to gradient
              const ang = Math.atan2(gy, gx) + Math.PI * 0.5;
              const deg = ((ang * 180 / Math.PI) % 180 + 180) % 180;
              if (deg < 22.5 || deg >= 157.5) pickedEdge = '_';
              else if (deg < 67.5) pickedEdge = '\\';
              else if (deg < 112.5) pickedEdge = '|';
              else pickedEdge = '/';
            }
          }

          if (pickedEdge) {
            ch = pickedEdge;
          } else {
            const level = Math.max(0, Math.min(RAMP.length - 1, Math.round(lum * (RAMP.length - 1))));
            ch = RAMP[level];
          }

          // Subtle random character corruption in glitch bands
          if (rng && glitchAmt > 0 && rShift !== 0 && rng() < 0.35) {
            ch = "░▒▓#$%&?!"[Math.floor(rng() * 9)];
          }
        }

        if (ch === ' ') continue;
        const glyph = getGlyph(ch);
        const x0 = col * CELL_W + cellShakeX[cIdx];
        const y0 = row * CELL_H;
        const rCl = Math.max(0, Math.min(255, cr | 0));
        const gCl = Math.max(0, Math.min(255, cg | 0));
        const bCl = Math.max(0, Math.min(255, cb | 0));

        if (chromaShift === 0) {
          for (let gy = 0; gy < CELL_H; gy++) {
            const py = y0 + gy;
            const scan = (py % 4 === 0) ? 0.84 : 1.0;
            const rowOff = py * W;
            const gRow = gy * CELL_W;
            for (let gx = 0; gx < CELL_W; gx++) {
              const px = x0 + gx;
              if (px < 0 || px >= W) continue;
              const a = glyph[gRow + gx];
              if (a === 0) continue;
              const af = (a / 255) * scan;
              const inv = 1 - af;
              const rr = (bgR * inv + rCl * af) | 0;
              const gg = (bgG * inv + gCl * af) | 0;
              const bb = (bgB * inv + bCl * af) | 0;
              buf32[rowOff + px] = (255 << 24) | (bb << 16) | (gg << 8) | rr;
            }
          }
        } else {
          // Chromatic RGB fringe split during jumpscares / surges
          for (let gy = 0; gy < CELL_H; gy++) {
            const py = y0 + gy;
            const scan = (py % 4 === 0) ? 0.84 : 1.0;
            const rowOff = py * W;
            const gRow = gy * CELL_W;
            for (let gx = 0; gx < CELL_W; gx++) {
              const px = x0 + gx;
              if (px < 0 || px >= W) continue;
              const aG = glyph[gRow + gx];
              const gxR = gx + chromaShift;
              const gxB = gx - chromaShift;
              const aR = (gxR >= 0 && gxR < CELL_W) ? glyph[gRow + gxR] : 0;
              const aB = (gxB >= 0 && gxB < CELL_W) ? glyph[gRow + gxB] : 0;
              if ((aR | aG | aB) === 0) continue;
              const rr = Math.min(255, (bgR * (1 - aR / 255) + rCl * (aR / 255) * scan) | 0);
              const gg = Math.min(255, (bgG * (1 - aG / 255) + gCl * (aG / 255) * scan) | 0);
              const bb = Math.min(255, (bgB * (1 - aB / 255) + bCl * (aB / 255) * scan) | 0);
              buf32[rowOff + px] = (255 << 24) | (bb << 16) | (gg << 8) | rr;
            }
          }
        }
      }
    }

    asciiCtx.putImageData(imgData, 0, 0);
  }

  // Exact 8sb2R11FeVw black-pill subtitle renderer (Law #27)
  function drawSubtitlePill(ctx, wordsChunk, activeIdx, tSinceStart, yCenter = 1365, activeColor = '#FFE600') {
    if (!wordsChunk || !wordsChunk.length) return;
    const fontSize = 58;
    ctx.save();
    ctx.font = `800 ${fontSize}px Inter, Montserrat, "Segoe UI", sans-serif`;
    ctx.textBaseline = 'middle';

    const pieces = wordsChunk.map((w, i) => (i < wordsChunk.length - 1 ? w.w + ' ' : w.w));
    const widths = pieces.map((p) => ctx.measureText(p).width);
    const textW = widths.reduce((a, b) => a + b, 0);

    const padX = 38;
    const padY = 22;
    const boxW = textW + padX * 2;
    const boxH = fontSize + padY * 2;

    const u = Math.min(1, Math.max(0, tSinceStart / 0.10));
    const c1 = 1.70158, c3 = c1 + 1;
    const popScale = u < 1 ? 0.88 + 0.12 * (1 + c3 * Math.pow(u - 1, 3) + c1 * Math.pow(u - 1, 2)) : 1;

    ctx.translate(W * 0.5, yCenter);
    ctx.scale(popScale, popScale);

    ctx.fillStyle = 'rgba(8, 8, 10, 0.92)';
    ctx.shadowColor = 'rgba(0, 0, 0, 0.55)';
    ctx.shadowBlur = 20;
    ctx.beginPath();
    ctx.roundRect(-boxW * 0.5, -boxH * 0.5, boxW, boxH, 16);
    ctx.fill();
    ctx.shadowBlur = 0;

    let x = -textW * 0.5;
    ctx.textAlign = 'left';
    pieces.forEach((p, i) => {
      ctx.fillStyle = i === activeIdx ? activeColor : '#FFFFFF';
      ctx.fillText(p, x, 2);
      x += widths[i];
    });
    ctx.restore();
  }

  function buildSubtitleChunks(beats) {
    const chunks = [];
    for (const b of beats) {
      const ws = b.words || [];
      let cur = [];
      for (let i = 0; i < ws.length; i++) {
        cur.push(ws[i]);
        const txt = cur.map((x) => x.w).join(' ');
        const endsSentence = /[.?!,—:]$/.test(ws[i].w);
        if (cur.length >= 3 || (cur.length >= 2 && (txt.length > 15 || endsSentence)) || i === ws.length - 1) {
          chunks.push({
            start: cur[0].start,
            end: cur[cur.length - 1].end + 0.08,
            words: cur,
            speaker: b.speaker,
            beatIdx: b.i,
          });
          cur = [];
        }
      }
    }
    return chunks;
  }

  function presentFrame(ctx, camX, camY, camRot, camZoom, subChunks, t, opts = {}) {
    renderAsciiBuffer(opts);

    ctx.save();
    ctx.fillStyle = '#040706';
    ctx.fillRect(0, 0, W, H);
    ctx.imageSmoothingEnabled = true;
    ctx.translate(W * 0.5 + camX, H * 0.5 + camY);
    ctx.rotate(camRot);
    ctx.scale(camZoom, camZoom);
    ctx.drawImage(asciiCanvas, -W * 0.5, -H * 0.5, W, H);

    // Subtle CRT phosphor bloom via downsampled additive pass
    const bloomAmt = opts.bloomAmt ?? 0.36;
    if (bloomAmt > 0) {
      glowCtx.clearRect(0, 0, glowCanvas.width, glowCanvas.height);
      glowCtx.drawImage(asciiCanvas, 0, 0, glowCanvas.width, glowCanvas.height);
      ctx.globalCompositeOperation = 'lighter';
      ctx.globalAlpha = bloomAmt;
      ctx.drawImage(glowCanvas, -W * 0.5, -H * 0.5, W, H);
      ctx.globalAlpha = 1.0;
      ctx.globalCompositeOperation = 'source-over';
    }
    ctx.restore();

    // Subtle CRT lens vignette
    const vg = ctx.createRadialGradient(W * 0.5, H * 0.46, W * 0.32, W * 0.5, H * 0.5, W * 0.90);
    vg.addColorStop(0, 'rgba(0,0,0,0)');
    vg.addColorStop(1, opts.vignetteCol || 'rgba(2,4,3,0.44)');
    ctx.fillStyle = vg;
    ctx.fillRect(0, 0, W, H);

    // Next-gen black-pill subtitles on top
    for (const ch of subChunks) {
      if (t >= ch.start && t <= ch.end) {
        let activeIdx = ch.words.length - 1;
        for (let i = 0; i < ch.words.length; i++) {
          if (t >= ch.words[i].start - 0.04) activeIdx = i;
        }
        const popCol = (ch.speaker === 'entity' || ch.beatIdx === 8 || ch.beatIdx >= 12) ? '#FF3344' : '#FFE600';
        drawSubtitlePill(ctx, ch.words, activeIdx, t - ch.start, 1365, popCol);
        break;
      }
    }
  }

  function kickOffset(t, tImpact, ampPx = 22) {
    const f = Math.round((t - tImpact) * 30);
    if (f < 0 || f >= 7) return { x: 0, y: 0, rot: 0, active: false };
    const decay = 1 - f / 7;
    const sign = f % 2 === 0 ? 1 : -1;
    return {
      x: sign * ampPx * 0.5 * decay,
      y: sign * ampPx * decay,
      rot: sign * 0.026 * decay,
      active: true,
    };
  }

  function activeBeatIndex(beats, t) {
    if (!beats.length || t < beats[0].start) return 0;
    for (let i = 0; i < beats.length; i++) {
      if (t >= beats[i].start && t < beats[i].end) return i;
    }
    return beats.length - 1;
  }

  return {
    W, H, COLS, ROWS, FW, FH,
    clearField, setPx, blendPx, addGlowPx, fillBox, fillDisk, fillCapsule,
    putCellChar, putCellString, drawAsciiBox,
    presentFrame, buildSubtitleChunks, kickOffset, activeBeatIndex, seeded,
    fLuma, fR, fG, fB, fEdgeEnable,
  };
})();
