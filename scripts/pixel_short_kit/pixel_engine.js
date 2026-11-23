/* Shared 180x320 Native Pixel-Art Canvas Engine (Uint32Array Framebuffer -> 6x nearest-neighbor upscale to 1080x1920)
 * Eliminates 50,000+ Canvas2D fillRect DOM calls per frame via direct Uint32Array writes + single putImageData().
 */
window.PX = (() => {
  const PW = 180;
  const PH = 320;
  const SCALE = 6;

  const pCanvas = document.createElement('canvas');
  pCanvas.width = PW;
  pCanvas.height = PH;
  const pctxReal = pCanvas.getContext('2d', { willReadFrequently: false });
  pctxReal.imageSmoothingEnabled = false;

  const imgData = pctxReal.createImageData(PW, PH);
  const buf32 = new Uint32Array(imgData.data.buffer);
  const buf8 = imgData.data;

  // Color parser cache -> packed 0xAABBGGRR (little-endian) + alpha
  const colCache = new Map();
  function parseColor(col) {
    let v = colCache.get(col);
    if (v !== undefined) return v;
    if (typeof col === 'string' && col.startsWith('#')) {
      let hex = col.slice(1);
      if (hex.length === 3) hex = hex[0]+hex[0]+hex[1]+hex[1]+hex[2]+hex[2];
      const r = parseInt(hex.slice(0, 2), 16) & 255;
      const g = parseInt(hex.slice(2, 4), 16) & 255;
      const b = parseInt(hex.slice(4, 6), 16) & 255;
      v = { abgr: (255 << 24) | (b << 16) | (g << 8) | r, r, g, b, a: 1.0 };
    } else if (typeof col === 'string' && col.startsWith('rgba(')) {
      const m = col.match(/rgba\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*\)/i);
      if (m) {
        const r = Math.round(+m[1]), g = Math.round(+m[2]), b = Math.round(+m[3]), a = +m[4];
        v = { abgr: ((Math.round(a * 255) & 255) << 24) | (b << 16) | (g << 8) | r, r, g, b, a };
      }
    }
    if (!v) v = { abgr: 0xff000000, r: 0, g: 0, b: 0, a: 1.0 };
    colCache.set(col, v);
    return v;
  }

  function setPixelABGR(ix, iy, cObj) {
    if (ix < 0 || ix >= PW || iy < 0 || iy >= PH) return;
    if (cObj.a >= 0.999) {
      buf32[iy * PW + ix] = cObj.abgr;
    } else if (cObj.a > 0) {
      const off = (iy * PW + ix) * 4;
      const inv = 1 - cObj.a;
      buf8[off]     = (buf8[off] * inv + cObj.r * cObj.a) | 0;
      buf8[off + 1] = (buf8[off + 1] * inv + cObj.g * cObj.a) | 0;
      buf8[off + 2] = (buf8[off + 2] * inv + cObj.b * cObj.a) | 0;
      buf8[off + 3] = 255;
    }
  }

  function fillRectFast(x, y, w, h, col) {
    const cObj = typeof col === 'string' ? parseColor(col) : col;
    const x0 = Math.max(0, Math.round(x));
    const y0 = Math.max(0, Math.round(y));
    const x1 = Math.min(PW, Math.round(x) + Math.round(w));
    const y1 = Math.min(PH, Math.round(y) + Math.round(h));
    if (x0 >= x1 || y0 >= y1) return;
    if (cObj.a >= 0.999) {
      const abgr = cObj.abgr;
      for (let yy = y0; yy < y1; yy++) {
        const row = yy * PW;
        for (let xx = x0; xx < x1; xx++) buf32[row + xx] = abgr;
      }
    } else {
      for (let yy = y0; yy < y1; yy++) {
        for (let xx = x0; xx < x1; xx++) setPixelABGR(xx, yy, cObj);
      }
    }
  }

  // Drop-in pctx proxy so existing pctx.clearRect / pctx.fillRect calls write straight into buf32!
  let _curFill = parseColor('#000000');
  const pctx = {
    set fillStyle(v) { _curFill = parseColor(v); },
    get fillStyle() { return _curFill; },
    clearRect(x, y, w, h) {
      if (x === 0 && y === 0 && w >= PW && h >= PH) {
        buf32.fill(0);
      } else {
        fillRectFast(x, y, w, h, { abgr: 0, r: 0, g: 0, b: 0, a: 1 });
      }
    },
    fillRect(x, y, w, h) {
      fillRectFast(x, y, w, h, _curFill);
    },
  };

  const BAYER2 = [[0, 2], [3, 1]];

  const FONT4X5 = {
    '0': ['0110','1001','1001','1001','0110'],
    '1': ['0010','0110','0010','0010','0111'],
    '2': ['0110','1001','0010','0100','1111'],
    '3': ['1110','0001','0110','0001','1110'],
    '4': ['1001','1001','1111','0001','0001'],
    '5': ['1111','1000','1110','0001','1110'],
    '6': ['0111','1000','1110','1001','0110'],
    '7': ['1111','0001','0010','0100','0100'],
    '8': ['0110','1001','0110','1001','0110'],
    '9': ['0110','1001','0111','0001','1110'],
    'A': ['0110','1001','1111','1001','1001'],
    'B': ['1110','1001','1110','1001','1110'],
    'C': ['0111','1000','1000','1000','0111'],
    'D': ['1110','1001','1001','1001','1110'],
    'E': ['1111','1000','1110','1000','1111'],
    'F': ['1111','1000','1110','1000','1000'],
    'G': ['0111','1000','1011','1001','0111'],
    'H': ['1001','1001','1111','1001','1001'],
    'I': ['0111','0010','0010','0010','0111'],
    'J': ['0011','0001','0001','1001','0110'],
    'K': ['1001','1010','1100','1010','1001'],
    'L': ['1000','1000','1000','1000','1111'],
    'M': ['1001','1111','1111','1001','1001'],
    'N': ['1001','1101','1011','1001','1001'],
    'O': ['0110','1001','1001','1001','0110'],
    'P': ['1110','1001','1110','1000','1000'],
    'Q': ['0110','1001','1001','0110','0011'],
    'R': ['1110','1001','1110','1010','1001'],
    'S': ['0111','1000','0110','0001','1110'],
    'T': ['1111','0100','0100','0100','0100'],
    'U': ['1001','1001','1001','1001','0110'],
    'V': ['1001','1001','1001','0110','0110'],
    'W': ['1001','1001','1111','1111','1001'],
    'X': ['1001','0110','0110','0110','1001'],
    'Y': ['1001','1001','0110','0010','0010'],
    'Z': ['1111','0010','0100','1000','1111'],
    '$': ['0111','1100','0110','0011','1110'],
    '¢': ['0010','0111','1010','0111','0010'],
    ':': ['0000','0100','0000','0100','0000'],
    '.': ['0000','0000','0000','0000','0100'],
    ',': ['0000','0000','0000','0100','1000'],
    '-': ['0000','0000','1110','0000','0000'],
    '+': ['0000','0100','1110','0100','0000'],
    '=': ['0000','1111','0000','1111','0000'],
    '/': ['0001','0010','0100','1000','0000'],
    '!': ['0100','0100','0100','0000','0100'],
    '?': ['0110','1001','0010','0000','0010'],
    '°': ['0110','0110','0000','0000','0000'],
    '|': ['0100','0100','0100','0100','0100'],
    '^': ['0100','1010','0000','0000','0000'],
    '>': ['1000','0100','0010','0100','1000'],
    '<': ['0010','0100','1000','0100','0010'],
    '(': ['0010','0100','0100','0100','0010'],
    ')': ['0100','0010','0010','0010','0100'],
    '%': ['1001','0010','0100','1001','0000'],
    ' ': ['0000','0000','0000','0000','0000'],
  };

  function px(x, y, col) {
    setPixelABGR(Math.round(x), Math.round(y), parseColor(col));
  }

  function rect(x, y, w, h, col) {
    fillRectFast(x, y, w, h, col);
  }

  function line(x0, y0, x1, y1, col) {
    const cObj = parseColor(col);
    let ix0 = Math.round(x0), iy0 = Math.round(y0);
    const ix1 = Math.round(x1), iy1 = Math.round(y1);
    const dx = Math.abs(ix1 - ix0), dy = -Math.abs(iy1 - iy0);
    const sx = ix0 < ix1 ? 1 : -1, sy = iy0 < iy1 ? 1 : -1;
    let err = dx + dy, steps = 0;
    while (steps++ < 400) {
      setPixelABGR(ix0, iy0, cObj);
      if (ix0 === ix1 && iy0 === iy1) break;
      const e2 = 2 * err;
      if (e2 >= dy) { err += dy; ix0 += sx; }
      if (e2 <= dx) { err += dx; iy0 += sy; }
    }
  }

  function ditherBand(x, y, w, h, colA, colB, density = 0.5) {
    const ix = Math.round(x), iy = Math.round(y), iw = Math.round(w), ih = Math.round(h);
    const cA = parseColor(colA), cB = parseColor(colB);
    const thr = Math.round(density * 4);
    const x0 = Math.max(0, ix), y0 = Math.max(0, iy);
    const x1 = Math.min(PW, ix + iw), y1 = Math.min(PH, iy + ih);
    for (let yy = y0; yy < y1; yy++) {
      const row = yy * PW;
      const bRow = BAYER2[yy & 1];
      for (let xx = x0; xx < x1; xx++) {
        buf32[row + xx] = bRow[xx & 1] < thr ? cB.abgr : cA.abgr;
      }
    }
  }

  function ditherGradV(x, y, w, h, stops) {
    const bands = stops.length - 1;
    const bandH = h / bands;
    const x0 = Math.max(0, Math.round(x)), x1 = Math.min(PW, Math.round(x + w));
    for (let i = 0; i < bands; i++) {
      const y0 = Math.round(y + i * bandH);
      const y1 = Math.round(y + (i + 1) * bandH);
      const bh = y1 - y0;
      const cA = parseColor(stops[i]).abgr, cB = parseColor(stops[i + 1]).abgr;
      for (let dy = 0; dy < bh; dy++) {
        const yy = y0 + dy;
        if (yy < 0 || yy >= PH) continue;
        const u = dy / Math.max(1, bh);
        const thr = u < 0.25 ? 0 : u < 0.5 ? 1 : u < 0.75 ? 2 : 3;
        const row = yy * PW;
        const bRow = BAYER2[yy & 1];
        for (let xx = x0; xx < x1; xx++) {
          buf32[row + xx] = (thr > 0 && bRow[xx & 1] < thr) ? cB : cA;
        }
      }
    }
  }

  function disk(cx, cy, r, col) {
    const icx = Math.round(cx), icy = Math.round(cy), ir = Math.round(r);
    const cObj = parseColor(col);
    const lim = ir * ir + ir * 0.4;
    for (let dy = -ir; dy <= ir; dy++) {
      const yy = icy + dy;
      if (yy < 0 || yy >= PH) continue;
      for (let dx = -ir; dx <= ir; dx++) {
        if (dx * dx + dy * dy <= lim) setPixelABGR(icx + dx, yy, cObj);
      }
    }
  }

  function ellipse(cx, cy, rx, ry, col) {
    const icx = Math.round(cx), icy = Math.round(cy);
    const irx = Math.max(1, Math.round(rx)), iry = Math.max(1, Math.round(ry));
    const cObj = parseColor(col);
    for (let dy = -iry; dy <= iry; dy++) {
      const yy = icy + dy;
      if (yy < 0 || yy >= PH) continue;
      for (let dx = -irx; dx <= irx; dx++) {
        if ((dx * dx) / (irx * irx) + (dy * dy) / (iry * iry) <= 1.0) setPixelABGR(icx + dx, yy, cObj);
      }
    }
  }

  function glowOrb(cx, cy, r, coreCol, midCol, haloCol) {
    const icx = Math.round(cx), icy = Math.round(cy);
    const cHalo = parseColor(haloCol);
    const r3 = r + 3;
    for (let dy = -r3; dy <= r3; dy++) {
      for (let dx = -r3; dx <= r3; dx++) {
        const d2 = dx * dx + dy * dy;
        if (d2 <= r3 * r3 && d2 > r * r && ((dx + dy) & 1) === 0) setPixelABGR(icx + dx, icy + dy, cHalo);
      }
    }
    disk(icx, icy, r, midCol);
    disk(icx - 1, icy - 1, Math.max(1, r - 2), coreCol);
    px(icx - Math.max(1, Math.floor(r * 0.4)), icy - Math.max(1, Math.floor(r * 0.4)), '#ffffff');
  }

  function textWidth(str) {
    return Math.max(0, str.length * 5 - 1);
  }

  function pixelText(str, x, y, col = '#ffffff', shadowCol = '#0d0c18', align = 'left') {
    const s = String(str).toUpperCase();
    const tw = textWidth(s);
    let ox = Math.round(x);
    if (align === 'center') ox = Math.round(x - tw / 2);
    else if (align === 'right') ox = Math.round(x - tw);
    const oy = Math.round(y);
    const cMain = parseColor(col);
    const cShad = shadowCol ? parseColor(shadowCol) : null;

    for (let i = 0; i < s.length; i++) {
      const g = FONT4X5[s[i]] || FONT4X5[' '];
      const gx = ox + i * 5;
      if (cShad) {
        for (let r = 0; r < 5; r++) {
          for (let c = 0; c < 4; c++) {
            if (g[r][c] === '1') setPixelABGR(gx + c + 1, oy + r + 1, cShad);
          }
        }
      }
      for (let r = 0; r < 5; r++) {
        for (let c = 0; c < 4; c++) {
          if (g[r][c] === '1') setPixelABGR(gx + c, oy + r, cMain);
        }
      }
    }
  }

  function drawHudPill(label, value, cx = 90, y = 26, accentCol = '#ffca3a') {
    const txt = label ? `${label} ${value}` : String(value);
    const tw = textWidth(txt);
    const pw = Math.max(66, tw + 14);
    const ph = 13;
    const x0 = Math.round(cx - pw / 2);
    rect(x0 + 1, y, pw - 2, ph, '#4c3f91');
    rect(x0, y + 1, pw, ph - 2, '#4c3f91');
    rect(x0 + 1, y + 1, pw - 2, ph - 2, '#0d102a');
    rect(x0 + 2, y + 2, pw - 4, 1, '#1e2761');

    if (label) {
      const lw = textWidth(label);
      const totalW = lw + 5 + textWidth(value);
      const sx = Math.round(cx - totalW / 2);
      pixelText(label, sx, y + 4, '#cbd5e1', '#070917', 'left');
      pixelText(value, sx + lw + 5, y + 4, accentCol, '#070917', 'left');
    } else {
      pixelText(value, cx, y + 4, accentCol, '#070917', 'center');
    }
  }

  function drawSubtitlePill(ctx, W, wordsChunk, activeIdx, tSinceStart, yCenter = 1365) {
    if (!wordsChunk || !wordsChunk.length) return;
    const fontSize = 58;
    ctx.save();
    ctx.font = `800 ${fontSize}px Inter, "Segoe UI", Arial, sans-serif`;
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
          chunks.push({ start: cur[0].start, end: cur[cur.length - 1].end + 0.08, words: cur });
          cur = [];
        }
      }
    }
    return chunks;
  }

  function presentFrame(ctx, W, H, camX, camY, camRot, camZoom, subChunks, t) {
    // Single putImageData upload for the entire 180x320 framebuffer!
    pctxReal.putImageData(imgData, 0, 0);

    ctx.save();
    ctx.fillStyle = '#08080c';
    ctx.fillRect(0, 0, W, H);
    ctx.imageSmoothingEnabled = false;
    ctx.translate(W / 2 + camX * SCALE, H / 2 + camY * SCALE);
    ctx.rotate(camRot);
    ctx.scale(camZoom, camZoom);
    ctx.drawImage(pCanvas, -W / 2, -H / 2, W, H);
    ctx.restore();

    const vg = ctx.createRadialGradient(W * 0.5, H * 0.45, W * 0.35, W * 0.5, H * 0.5, W * 0.85);
    vg.addColorStop(0, 'rgba(0,0,0,0)');
    vg.addColorStop(1, 'rgba(4,4,12,0.38)');
    ctx.fillStyle = vg;
    ctx.fillRect(0, 0, W, H);

    for (const ch of subChunks) {
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

  function kickOffset(t, tImpact, ampPx = 5) {
    const f = Math.round((t - tImpact) * 30);
    if (f < 0 || f >= 7) return { x: 0, y: 0, rot: 0 };
    const decay = 1 - f / 7;
    const sign = f % 2 === 0 ? 1 : -1;
    return { x: sign * ampPx * 0.45 * decay, y: sign * ampPx * decay, rot: sign * 0.025 * decay };
  }

  function blinkExpr(baseExpr, t, seed = 0) {
    const cycle = (t + seed * 0.47) % 1.32;
    if (cycle > 1.19 && baseExpr !== 'dizzy' && baseExpr !== 'cool_shades') return 'blink';
    return baseExpr;
  }

  function isSpeaking(beats, speaker, t) {
    for (const b of beats) {
      if (b.speaker !== speaker) continue;
      if (t >= b.start && t <= b.speechEnd) {
        for (const w of b.words || []) {
          if (t >= w.start - 0.03 && t <= w.end + 0.04) return true;
        }
      }
    }
    return false;
  }

  function activeBeatIndex(beats, t) {
    if (!beats.length || t < beats[0].start) return 0;
    for (let i = 0; i < beats.length; i++) {
      if (t >= beats[i].start && t < beats[i].end) return i;
    }
    return beats.length - 1;
  }

  function seeded(seed) {
    let s = seed | 0 || 12345;
    return () => {
      s = (s * 1664525 + 1013904223) | 0;
      return (s >>> 0) / 4294967296;
    };
  }

  return {
    PW, PH, SCALE, pCanvas, pctx,
    px, rect, line, ditherBand, ditherGradV, disk, ellipse, glowOrb,
    pixelText, textWidth, drawHudPill, drawSubtitlePill,
    buildSubtitleChunks, presentFrame, kickOffset, blinkExpr, isSpeaking, activeBeatIndex, seeded,
  };
})();
