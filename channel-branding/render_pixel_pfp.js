#!/usr/bin/env node
/**
 * Pixel-Art Countryball Channel PFP Renderer (100x100 native -> 800x800 8x nearest-neighbor)
 * Matches the exact @science_in_8bit / Countryball style of core-dig-short & dimension-100-short.
 * Output: channel-branding/pfp.png
 */
const fs = require('fs');
const path = require('path');
const { chromium } = require(path.resolve(__dirname, '../videos/emu-war/studio/node_modules/playwright'));

const OUT_PATH = path.join(__dirname, 'pfp.png');
const OUT_SIZE = 800;
const PW = 100;
const PH = 100;

const HTML = `<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: ${OUT_SIZE}px; height: ${OUT_SIZE}px; overflow: hidden; background: #090418; }
  canvas { display: block; width: ${OUT_SIZE}px; height: ${OUT_SIZE}px; }
</style>
</head>
<body>
<canvas id="out" width="${OUT_SIZE}" height="${OUT_SIZE}"></canvas>
<script>
(() => {
  const PW = ${PW}, PH = ${PH};
  const pCanvas = document.createElement('canvas');
  pCanvas.width = PW;
  pCanvas.height = PH;
  const pctx = pCanvas.getContext('2d');
  pctx.imageSmoothingEnabled = false;

  const BAYER2 = [[0, 2], [3, 1]];
  const OUTLINE = '#181124';

  function px(x, y, col) {
    pctx.fillStyle = col;
    pctx.fillRect(Math.round(x), Math.round(y), 1, 1);
  }
  function rect(x, y, w, h, col) {
    pctx.fillStyle = col;
    pctx.fillRect(Math.round(x), Math.round(y), Math.round(w), Math.round(h));
  }
  function line(x0, y0, x1, y1, col) {
    let ix0 = Math.round(x0), iy0 = Math.round(y0);
    const ix1 = Math.round(x1), iy1 = Math.round(y1);
    const dx = Math.abs(ix1 - ix0), dy = -Math.abs(iy1 - iy0);
    const sx = ix0 < ix1 ? 1 : -1, sy = iy0 < iy1 ? 1 : -1;
    let err = dx + dy, steps = 0;
    pctx.fillStyle = col;
    while (steps++ < 300) {
      pctx.fillRect(ix0, iy0, 1, 1);
      if (ix0 === ix1 && iy0 === iy1) break;
      const e2 = 2 * err;
      if (e2 >= dy) { err += dy; ix0 += sx; }
      if (e2 <= dx) { err += dx; iy0 += sy; }
    }
  }
  function bayerPick(x, y, colA, colB, thr = 2) {
    const b = ((y & 1) << 1) | ((x ^ y) & 1);
    return b < thr ? colB : colA;
  }
  function ditherGradV(x, y, w, h, stops) {
    const bands = stops.length - 1;
    const bandH = h / bands;
    for (let i = 0; i < bands; i++) {
      const y0 = Math.round(y + i * bandH);
      const y1 = Math.round(y + (i + 1) * bandH);
      const bh = y1 - y0;
      const cA = stops[i], cB = stops[i + 1];
      for (let dy = 0; dy < bh; dy++) {
        const u = dy / Math.max(1, bh);
        const thr = u < 0.25 ? 0 : u < 0.5 ? 1 : u < 0.75 ? 2 : 3;
        pctx.fillStyle = cA;
        pctx.fillRect(x, y0 + dy, w, 1);
        if (thr > 0) {
          pctx.fillStyle = cB;
          for (let dx = 0; dx < w; dx++) {
            if (BAYER2[(y0 + dy) & 1][(x + dx) & 1] < thr) pctx.fillRect(x + dx, y0 + dy, 1, 1);
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
        if (dx * dx + dy * dy <= ir * ir + ir * 0.4) pctx.fillRect(icx + dx, icy + dy, 1, 1);
      }
    }
  }
  function glowOrb(cx, cy, r, coreCol, midCol, haloCol) {
    const icx = Math.round(cx), icy = Math.round(cy);
    pctx.fillStyle = haloCol;
    const r3 = r + 2;
    for (let dy = -r3; dy <= r3; dy++) {
      for (let dx = -r3; dx <= r3; dx++) {
        const d2 = dx * dx + dy * dy;
        if (d2 <= r3 * r3 && d2 > r * r && ((dx + dy) & 1) === 0) pctx.fillRect(icx + dx, icy + dy, 1, 1);
      }
    }
    disk(icx, icy, r, midCol);
    disk(icx - 1, icy - 1, Math.max(1, r - 2), coreCol);
    px(icx - 1, icy - 1, '#ffffff');
  }

  // 1. Deep Cosmic 8-Bit Dithered Sky
  ditherGradV(0, 0, PW, PH, ['#060314', '#140b34', '#1e1b4b', '#0f172a']);

  // Subtle retro perspective floor arc at bottom inside circle
  for (let y = 74; y < PH; y += 5) rect(0, y, PW, 1, '#312e81');
  for (let x = -20; x <= PW + 20; x += 14) line(50, 58, x, 99, '#312e81');

  // 2. Twinkling pixel stars & glowing cosmic orbs
  const stars = [
    [16, 22, '#fde047'], [82, 20, '#22d3ee'], [22, 74, '#f472b6'],
    [78, 72, '#fde047'], [12, 48, '#ffffff'], [87, 46, '#ffffff'],
    [32, 14, '#a855f7'], [68, 14, '#22d3ee'],
  ];
  for (const [sx, sy, col] of stars) {
    px(sx, sy, col);
    px(sx - 1, sy, col); px(sx + 1, sy, col);
    px(sx, sy - 1, col); px(sx, sy + 1, col);
    px(sx, sy, '#ffffff');
  }
  glowOrb(20, 28, 3, '#fef08a', '#facc15', '#ea580c');
  glowOrb(80, 29, 3, '#e0f2fe', '#22d3ee', '#7e22ce');

  // 3. Rotating 4D Tesseract Wireframe Halo behind Hero
  {
    const aXW = 0.65, aYW = 0.42, aXZ = 0.35;
    const cXW = Math.cos(aXW), sXW = Math.sin(aXW);
    const cYW = Math.cos(aYW), sYW = Math.sin(aYW);
    const cXZ = Math.cos(aXZ), sXZ = Math.sin(aXZ);
    const pts = [];
    for (let i = 0; i < 16; i++) {
      let x = (i & 1) ? 1 : -1;
      let y = (i & 2) ? 1 : -1;
      let z = (i & 4) ? 1 : -1;
      let w = (i & 8) ? 1 : -1;
      let nx = x * cXW - w * sXW, nw = x * sXW + w * cXW; x = nx; w = nw;
      let ny = y * cYW - w * sYW; nw = y * sYW + w * cYW; y = ny; w = nw;
      nx = x * cXZ - z * sXZ; let nz = x * sXZ + z * cXZ; x = nx; z = nz;
      const wp = 1 / (2.5 - w * 0.6);
      const zp = 1 / (3.0 - z * 0.45);
      pts.push({ x: 50 + x * 34 * wp * zp * 3.8, y: 47 + y * 34 * wp * zp * 3.8 });
    }
    for (let i = 0; i < 16; i++) {
      for (let bit = 0; bit < 4; bit++) {
        const j = i ^ (1 << bit);
        if (i < j) {
          const col = bit === 3 ? '#a855f7' : ((i & 8) ? '#22d3ee' : '#f472b6');
          line(pts[i].x, pts[i].y, pts[j].x, pts[j].y, col);
        }
      }
    }
    for (const p of pts) rect(p.x - 1, p.y - 1, 2, 2, '#ffffff');
  }

  // 4. Hero MC Countryball (Centered at 50, 55, R = 24 — bold & unmistakable at 36px avatar!)
  const cx = 50, cy = 55, R = 24;

  // Ground contact shadow
  pctx.fillStyle = 'rgba(6, 3, 18, 0.55)';
  for (let dx = -20; dx <= 20; dx++) {
    for (let dy = -2; dy <= 2; dy++) {
      if ((dx * dx) / 400 + (dy * dy) / 4 <= 1) pctx.fillRect(cx + dx, cy + R + 2 + dy, 1, 1);
    }
  }

  for (let dy = -R - 1; dy <= R + 1; dy++) {
    for (let dx = -R - 1; dx <= R + 1; dx++) {
      const nx = dx / R, ny = dy / R;
      const d2 = nx * nx + ny * ny;
      if (d2 > 1.09) continue;
      if (d2 > 0.94) { px(cx + dx, cy + dy, OUTLINE); continue; }

      const x = cx + dx, y = cy + dy;
      // Green hoodie lower hemisphere
      if (dy > R * 0.22) {
        if (Math.abs(dx + 4) <= 0 && dy > R * 0.25 && dy < R * 0.66) { px(x, y, '#f8fafc'); continue; }
        if (Math.abs(dx - 4) <= 0 && dy > R * 0.25 && dy < R * 0.66) { px(x, y, '#f8fafc'); continue; }
        const shade = dx > R * 0.18 || dy > R * 0.68;
        px(x, y, shade ? '#15803d' : '#22c55e');
        continue;
      }

      const light = -0.55 * nx - 0.65 * ny;
      let col = '#db9f67';
      if (light > 0.54) col = '#f3caa0';
      else if (light > 0.05) col = '#db9f67';
      else if (light > -0.32) col = bayerPick(x, y, '#db9f67', '#b3743f', 2);
      else col = '#b3743f';
      px(x, y, col);
    }
  }

  // Upper-left specular pixels
  rect(cx - 12, cy - 12, 2, 2, '#ffffff');
  px(cx - 9, cy - 14, '#ffffff');

  // Big expressive Countryball eyes (classic no-mouth)
  for (const s of [-1, 1]) {
    const ex = cx + s * 9;
    const ey = cy - 2;
    const ew = 8, eh = 8;
    const x0 = ex - 4, y0 = ey - 4;
    rect(x0 - 1, y0, ew + 2, eh, OUTLINE);
    rect(x0, y0 - 1, ew, eh + 2, OUTLINE);
    rect(x0, y0, ew, eh, '#ffffff');
    // Crisp 2x2 pupil + 1px catchlight? No catchlight, pure Countryball 3x3 pupil!
    rect(ex - 1, ey - 1, 3, 3, OUTLINE);
  }

  // Spiky brown hair + Cyan/Magenta 100D Quantum Visor
  const top = cy - R - 2;
  rect(cx - 15, top + 1, 30, 5, '#3b2314');
  rect(cx - 8, top - 3, 4, 4, '#3b2314');
  rect(cx + 0, top - 4, 4, 5, '#4e2f1b');
  rect(cx + 7, top - 2, 4, 3, '#3b2314');
  // Visor band
  rect(cx - 11, top + 5, 22, 5, '#0f172a');
  rect(cx - 10, top + 6, 9, 3, '#22d3ee');
  rect(cx + 1, top + 6, 9, 3, '#f472b6');

  // 5. Crisp Pixel-Art Circular Frame Ring (fits cleanly inside YouTube circle crop)
  for (let y = 0; y < PH; y++) {
    for (let x = 0; x < PW; x++) {
      const dx = x - 49.5, dy = y - 49.5;
      const r = Math.sqrt(dx * dx + dy * dy);
      if (r >= 45.5 && r <= 47.8) {
        px(x, y, ((x + y) & 1) ? '#fde047' : '#f59e0b');
      } else if (r >= 43.8 && r < 45.5) {
        px(x, y, '#181124');
      }
    }
  }

  // Nearest-neighbor 8x upscale to 800x800
  const out = document.getElementById('out');
  const ctx = out.getContext('2d');
  ctx.imageSmoothingEnabled = false;
  ctx.drawImage(pCanvas, 0, 0, ${OUT_SIZE}, ${OUT_SIZE});
  window.PFP_READY = true;
})();
</script>
</body>
</html>`;

(async () => {
  const browser = await chromium.launch({
    args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'],
  });
  const page = await browser.newPage({ viewport: { width: OUT_SIZE, height: OUT_SIZE }, deviceScaleFactor: 1 });
  await page.setContent(HTML);
  await page.waitForFunction(() => window.PFP_READY === true, null, { timeout: 10000 });
  await page.screenshot({ path: OUT_PATH, type: 'png' });
  await browser.close();
  console.log('Rendered pixel PFP ->', OUT_PATH);
})();
