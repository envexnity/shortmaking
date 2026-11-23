/* 180x320 Native Pixel-Art Canvas Engine (6x nearest-neighbor upscale to 1080x1920)
 * Inspired by @science_in_8bit's hi-bit pixel density, 2x2 Bayer dithering, 4D Tesseract wireframes, and glowing halos.
 */
window.PX = (() => {
  const PW = 180;
  const PH = 320;
  const SCALE = 6; // 180*6 = 1080, 320*6 = 1920

  // Offscreen 180x320 buffer
  const pCanvas = document.createElement('canvas');
  pCanvas.width = PW;
  pCanvas.height = PH;
  const pctx = pCanvas.getContext('2d', { willReadFrequently: false });
  pctx.imageSmoothingEnabled = false;

  // 2x2 Bayer threshold matrix
  const BAYER2 = [
    [0, 2],
    [3, 1],
  ];

  // Compact 4x5 uppercase bitmap pixel font (matching @science_in_8bit crisp HUD text)
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
    ' ': ['0000','0000','0000','0000','0000'],
  };

  function px(x, y, col) {
    pctx.fillStyle = col;
    pctx.fillRect(Math.round(x), Math.round(y), 1, 1);
  }

  function rect(x, y, w, h, col) {
    pctx.fillStyle = col;
    pctx.fillRect(Math.round(x), Math.round(y), Math.round(w), Math.round(h));
  }

  // Integer Bresenham line for crisp 1px pixel-art wireframes & tesseracts
  function line(x0, y0, x1, y1, col) {
    let ix0 = Math.round(x0), iy0 = Math.round(y0);
    const ix1 = Math.round(x1), iy1 = Math.round(y1);
    const dx = Math.abs(ix1 - ix0);
    const dy = -Math.abs(iy1 - iy0);
    const sx = ix0 < ix1 ? 1 : -1;
    const sy = iy0 < iy1 ? 1 : -1;
    let err = dx + dy;
    pctx.fillStyle = col;
    let steps = 0;
    while (steps++ < 400) {
      pctx.fillRect(ix0, iy0, 1, 1);
      if (ix0 === ix1 && iy0 === iy1) break;
      const e2 = 2 * err;
      if (e2 >= dy) { err += dy; ix0 += sx; }
      if (e2 <= dx) { err += dx; iy0 += sy; }
    }
  }

  function ditherBand(x, y, w, h, colA, colB, density = 0.5) {
    const ix = Math.round(x), iy = Math.round(y), iw = Math.round(w), ih = Math.round(h);
    pctx.fillStyle = colA;
    pctx.fillRect(ix, iy, iw, ih);
    pctx.fillStyle = colB;
    const thr = Math.round(density * 4);
    for (let dy = 0; dy < ih; dy++) {
      for (let dx = 0; dx < iw; dx++) {
        if (BAYER2[(iy + dy) & 1][(ix + dx) & 1] < thr) {
          pctx.fillRect(ix + dx, iy + dy, 1, 1);
        }
      }
    }
  }

  function ditherGradV(x, y, w, h, stops) {
    const bands = stops.length - 1;
    const bandH = h / bands;
    for (let i = 0; i < bands; i++) {
      const y0 = Math.round(y + i * bandH);
      const y1 = Math.round(y + (i + 1) * bandH);
      const bh = y1 - y0;
      const cA = stops[i];
      const cB = stops[i + 1];
      for (let dy = 0; dy < bh; dy++) {
        const u = dy / Math.max(1, bh);
        const thr = u < 0.25 ? 0 : u < 0.5 ? 1 : u < 0.75 ? 2 : 3;
        pctx.fillStyle = cA;
        pctx.fillRect(x, y0 + dy, w, 1);
        if (thr > 0) {
          pctx.fillStyle = cB;
          for (let dx = 0; dx < w; dx++) {
            if (BAYER2[(y0 + dy) & 1][(x + dx) & 1] < thr) {
              pctx.fillRect(x + dx, y0 + dy, 1, 1);
            }
          }
        }
      }
    }
  }

  function disk(cx, cy, r, col) {
    const icx = Math.round(cx), icy = Math.round(cy), ir = Math.round(r);
    pctx.fillStyle = col;
    for (let dy = -ir; dy <= ir; dy++) {
      for (let dx = -ir; dx <= ir; dx++) {
        if (dx * dx + dy * dy <= ir * ir + ir * 0.4) {
          pctx.fillRect(icx + dx, icy + dy, 1, 1);
        }
      }
    }
  }

  function glowOrb(cx, cy, r, coreCol, midCol, haloCol) {
    const icx = Math.round(cx), icy = Math.round(cy);
    pctx.fillStyle = haloCol;
    const r3 = r + 3;
    for (let dy = -r3; dy <= r3; dy++) {
      for (let dx = -r3; dx <= r3; dx++) {
        const d2 = dx * dx + dy * dy;
        if (d2 <= r3 * r3 && d2 > r * r && ((dx + dy) & 1) === 0) {
          pctx.fillRect(icx + dx, icy + dy, 1, 1);
        }
      }
    }
    disk(icx, icy, r, midCol);
    disk(icx - 1, icy - 1, Math.max(1, r - 2), coreCol);
    px(icx - Math.max(1, Math.floor(r * 0.4)), icy - Math.max(1, Math.floor(r * 0.4)), '#ffffff');
  }

  // Real 4D Tesseract (16 vertices, 32 edges) rotated in XW, YW, and XZ planes
  function drawTesseract4D(cx, cy, scale, t, colA = '#22d3ee', colB = '#f472b6', colConnect = '#a855f7') {
    const aXW = t * 1.15;
    const aYW = t * 0.75;
    const aXZ = t * 0.55;
    const cosXW = Math.cos(aXW), sinXW = Math.sin(aXW);
    const cosYW = Math.cos(aYW), sinYW = Math.sin(aYW);
    const cosXZ = Math.cos(aXZ), sinXZ = Math.sin(aXZ);

    const pts = [];
    for (let i = 0; i < 16; i++) {
      let x = (i & 1) ? 1 : -1;
      let y = (i & 2) ? 1 : -1;
      let z = (i & 4) ? 1 : -1;
      let w = (i & 8) ? 1 : -1;

      // Rotate in XW
      let nx = x * cosXW - w * sinXW;
      let nw = x * sinXW + w * cosXW;
      x = nx; w = nw;

      // Rotate in YW
      let ny = y * cosYW - w * sinYW;
      nw = y * sinYW + w * cosYW;
      y = ny; w = nw;

      // Rotate in XZ
      nx = x * cosXZ - z * sinXZ;
      let nz = x * sinXZ + z * cosXZ;
      x = nx; z = nz;

      // 4D -> 3D -> 2D perspective projection
      const wPersp = 1 / (2.6 - w * 0.65);
      const zPersp = 1 / (3.2 - z * 0.45);
      const px2 = cx + x * scale * wPersp * zPersp * 3.8;
      const py2 = cy + y * scale * wPersp * zPersp * 3.8;
      pts.push({ x: px2, y: py2, w });
    }

    // Draw 32 edges connecting vertices differing by 1 bit
    for (let i = 0; i < 16; i++) {
      for (let bit = 0; bit < 4; bit++) {
        const j = i ^ (1 << bit);
        if (i < j) {
          const c = bit === 3 ? colConnect : ((i & 8) ? colA : colB);
          line(pts[i].x, pts[i].y, pts[j].x, pts[j].y, c);
        }
      }
    }
    // Bright vertex sparks
    for (let i = 0; i < 16; i++) {
      rect(pts[i].x - 1, pts[i].y - 1, 2, 2, '#ffffff');
    }
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

    for (let i = 0; i < s.length; i++) {
      const g = FONT4X5[s[i]] || FONT4X5[' '];
      const gx = ox + i * 5;
      if (shadowCol) {
        pctx.fillStyle = shadowCol;
        for (let r = 0; r < 5; r++) {
          for (let c = 0; c < 4; c++) {
            if (g[r][c] === '1') pctx.fillRect(gx + c + 1, oy + r + 1, 1, 1);
          }
        }
      }
      pctx.fillStyle = col;
      for (let r = 0; r < 5; r++) {
        for (let c = 0; c < 4; c++) {
          if (g[r][c] === '1') pctx.fillRect(gx + c, oy + r, 1, 1);
        }
      }
    }
  }

  // @science_in_8bit-style compact retro pill counter at top safe zone
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

  // Exact 8sb2R11FeVw Black-Background Subtitle Pill on 1080x1920 overlay
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

  return {
    PW, PH, SCALE, pCanvas, pctx,
    px, rect, line, ditherBand, ditherGradV, disk, glowOrb, drawTesseract4D,
    pixelText, textWidth, drawHudPill, drawSubtitlePill,
  };
})();
