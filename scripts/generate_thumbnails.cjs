#!/usr/bin/env node
/**
 * Generate high-CTR YouTube 16:9 (1280x720) & Shorts/Reels 9:16 (1080x1920)
 * custom thumbnails for all 5 completed videos in videos/.
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const SCRATCH = String.raw`C:\Users\AFADAZIO\.gemini\antigravity\brain\8abe9e7e-6957-455f-b650-44c930ebc0e4\scratch`;

function resolvePlaywright() {
  const candidates = [
    path.join(ROOT, 'videos/emu-war/studio/node_modules/playwright'),
    'playwright',
  ];
  for (const c of candidates) {
    try { return require(c); } catch {}
  }
  throw new Error('Playwright not found');
}

function toDataUrl(filePath) {
  const ext = path.extname(filePath).toLowerCase() === '.png' ? 'image/png' : 'image/jpeg';
  const buf = fs.readFileSync(filePath);
  return `data:${ext};base64,${buf.toString('base64')}`;
}

const ASSETS = {
  emuClose: toDataUrl(path.join(SCRATCH, 'thumb_refs/emu_close.png')),
  emuSoldier: toDataUrl(path.join(SCRATCH, 'thumb_refs/emu_hero2.png')),
  marsGlobe: toDataUrl(path.join(ROOT, 'videos/mars-orbit/assets/mars_globe.jpg')),
  venusClouds: toDataUrl(path.join(ROOT, 'videos/venus-short/assets/venus_clouds.jpg')),
  venusVolcano: toDataUrl(path.join(ROOT, 'videos/venus-short/assets/venus_volcano.jpg')),
  bennuRubble: toDataUrl(path.join(ROOT, 'videos/asteroid-short/assets/bennu_rubble.jpg')),
  dartImpact: toDataUrl(path.join(ROOT, 'videos/asteroid-short/assets/dart_impact.jpg')),
  m87Eht: toDataUrl(path.join(ROOT, 'videos/black-hole-short/assets/m87_eht.jpg')),
  m87Jet: toDataUrl(path.join(ROOT, 'videos/black-hole-short/assets/m87_jet.jpg')),
};

const HTML = `<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><style>body{margin:0;background:#000;overflow:hidden}</style></head>
<body>
<canvas id="c"></canvas>
<script>
const IMGS = {};
function loadImages(map) {
  return Promise.all(Object.entries(map).map(([k, src]) => new Promise((res) => {
    const img = new Image();
    img.onload = () => { IMGS[k] = img; res(); };
    img.src = src;
  })));
}

function drawStars(ctx, W, H, seed = 42) {
  let s = seed;
  const rnd = () => { s = (s * 1664525 + 1013904223) | 0; return (s >>> 0) / 4294967296; };
  for (let i = 0; i < 180; i++) {
    ctx.fillStyle = 'rgba(235,244,255,' + (0.2 + rnd() * 0.75).toFixed(2) + ')';
    ctx.beginPath();
    ctx.arc(rnd() * W, rnd() * H, 0.8 + rnd() * 2.2, 0, Math.PI * 2);
    ctx.fill();
  }
}

function drawAstronaut(ctx, x, y, sc = 1, rot = 0, stretchY = 1) {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(rot);
  ctx.scale(sc, sc * stretchY);
  ctx.shadowColor = 'rgba(255, 255, 255, 0.45)';
  ctx.shadowBlur = 18;
  // Backpack
  ctx.fillStyle = '#cbd5e1';
  ctx.beginPath(); ctx.roundRect(-24, -14, 15, 34, 5); ctx.fill();
  // Legs
  ctx.fillStyle = '#e2e8f0';
  ctx.beginPath(); ctx.roundRect(-10, 16, 9, 22, 4); ctx.roundRect(2, 16, 9, 22, 4); ctx.fill();
  // Torso
  ctx.fillStyle = '#ffffff';
  ctx.beginPath(); ctx.roundRect(-14, -15, 28, 33, 8); ctx.fill();
  // Arm raised in alarm
  ctx.fillStyle = '#f1f5f9';
  ctx.beginPath(); ctx.roundRect(11, -18, 13, 9, 4); ctx.fill();
  // Helmet
  ctx.fillStyle = '#ffffff';
  ctx.beginPath(); ctx.arc(1, -27, 19, 0, Math.PI * 2); ctx.fill();
  // Visor
  ctx.shadowBlur = 0;
  ctx.fillStyle = '#0f172a';
  ctx.beginPath(); ctx.roundRect(-4, -36, 21, 16, 7); ctx.fill();
  ctx.fillStyle = 'rgba(245, 158, 11, 0.75)';
  ctx.beginPath(); ctx.ellipse(9, -29, 6, 3.5, -0.35, 0, Math.PI * 2); ctx.fill();
  ctx.restore();
}

function drawArrow(ctx, x1, y1, cx, cy, x2, y2, color = '#ff2438', width = 10) {
  ctx.save();
  ctx.strokeStyle = '#000000';
  ctx.lineWidth = width + 7;
  ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(x1, y1); ctx.quadraticCurveTo(cx, cy, x2, y2); ctx.stroke();

  ctx.strokeStyle = color;
  ctx.lineWidth = width;
  ctx.beginPath(); ctx.moveTo(x1, y1); ctx.quadraticCurveTo(cx, cy, x2, y2); ctx.stroke();

  const ang = Math.atan2(y2 - cy, x2 - cx);
  const hs = width * 2.5;
  ctx.fillStyle = color;
  ctx.strokeStyle = '#000000';
  ctx.lineWidth = 4;
  ctx.beginPath();
  ctx.moveTo(x2 + Math.cos(ang) * hs * 0.4, y2 + Math.sin(ang) * hs * 0.4);
  ctx.lineTo(x2 - Math.cos(ang - 0.55) * hs, y2 - Math.sin(ang - 0.55) * hs);
  ctx.lineTo(x2 - Math.cos(ang + 0.55) * hs, y2 - Math.sin(ang + 0.55) * hs);
  ctx.closePath();
  ctx.stroke();
  ctx.fill();
  ctx.restore();
}

function drawBigTitle(ctx, lines, x, y, size, align = 'left') {
  ctx.save();
  ctx.font = \`900 \${size}px Impact, "Arial Black", sans-serif\`;
  ctx.textAlign = align;
  ctx.textBaseline = 'top';
  ctx.lineJoin = 'round';
  ctx.miterLimit = 2;
  lines.forEach((ln, idx) => {
    const yy = y + idx * (size * 1.06);
    ctx.shadowColor = 'rgba(0,0,0,0.85)';
    ctx.shadowBlur = 20;
    ctx.shadowOffsetY = 6;
    ctx.lineWidth = Math.max(10, size * 0.16);
    ctx.strokeStyle = '#050507';
    ctx.strokeText(ln.text, x, yy);
    ctx.shadowBlur = 0; ctx.shadowOffsetY = 0;
    ctx.fillStyle = ln.color || '#FFFFFF';
    ctx.fillText(ln.text, x, yy);
  });
  ctx.restore();
}

function drawBadge(ctx, text, x, y, bg = '#ef4444', fg = '#ffffff', size = 34, rot = -0.04, align = 'center') {
  ctx.save();
  ctx.font = \`900 \${size}px Impact, "Arial Black", sans-serif\`;
  const tw = ctx.measureText(text).width;
  const pw = tw + 48;
  const ph = size + 24;
  ctx.translate(x, y);
  ctx.rotate(rot);
  ctx.shadowColor = 'rgba(0,0,0,0.75)';
  ctx.shadowBlur = 18;
  ctx.fillStyle = bg;
  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = 4;
  const bx = align === 'left' ? 0 : -pw / 2;
  ctx.beginPath(); ctx.roundRect(bx, -ph / 2, pw, ph, 14); ctx.fill(); ctx.stroke();
  ctx.shadowBlur = 0;
  ctx.fillStyle = fg;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(text, align === 'left' ? pw / 2 : 0, 2);
  ctx.restore();
}

function drawVignette(ctx, W, H, str = 0.55) {
  const g = ctx.createRadialGradient(W * 0.5, H * 0.5, W * 0.2, W * 0.5, H * 0.5, Math.max(W, H) * 0.72);
  g.addColorStop(0, 'rgba(0,0,0,0)');
  g.addColorStop(1, \`rgba(0,0,0,\${str})\`);
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, W, H);
}

function drawPlanetCircle(ctx, img, cx, cy, r, rimCol = 'rgba(251,146,60,0.65)') {
  ctx.save();
  const glow = ctx.createRadialGradient(cx, cy, r * 0.75, cx, cy, r * 1.42);
  glow.addColorStop(0, rimCol);
  glow.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = glow;
  ctx.beginPath(); ctx.arc(cx, cy, r * 1.42, 0, Math.PI * 2); ctx.fill();

  ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.clip();
  const sc = Math.max((2 * r) / img.width, (2 * r) / img.height);
  const dw = img.width * sc, dh = img.height * sc;
  ctx.drawImage(img, cx - dw / 2, cy - dh / 2, dw, dh);
  // 3D shadow terminator
  const sh = ctx.createLinearGradient(cx - r, cy - r * 0.4, cx + r, cy + r * 0.5);
  sh.addColorStop(0, 'rgba(255,255,255,0.08)');
  sh.addColorStop(0.55, 'rgba(0,0,0,0.05)');
  sh.addColorStop(1, 'rgba(0,0,0,0.72)');
  ctx.fillStyle = sh;
  ctx.fillRect(cx - r, cy - r, 2 * r, 2 * r);
  ctx.restore();

  ctx.save();
  ctx.strokeStyle = rimCol;
  ctx.lineWidth = 5;
  ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.stroke();
  ctx.restore();
}

window.renderThumb = function(slug, mode) {
  const isV = mode === '9x16';
  const W = isV ? 1080 : 1280;
  const H = isV ? 1920 : 720;
  const c = document.getElementById('c');
  c.width = W; c.height = H;
  const ctx = c.getContext('2d');
  ctx.clearRect(0, 0, W, H);

  if (slug === 'emu-war') {
    // Rich golden outback dusk backdrop + soldier crop + staring Emu
    const bg = ctx.createLinearGradient(0, 0, W, H);
    bg.addColorStop(0, '#1e3a5f'); bg.addColorStop(0.55, '#c27d38'); bg.addColorStop(1, '#5a3210');
    ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H);

    // Draw soldier hero crop blurred slightly on left
    const sol = IMGS.emuSoldier;
    ctx.save();
    ctx.globalAlpha = 0.48;
    // crop middle strip y=520..1450 of 1080x1920
    if (isV) {
      ctx.drawImage(sol, 0, 420, 1080, 1100, -140, 260, 900, 920);
    } else {
      ctx.drawImage(sol, 0, 500, 1080, 1000, -80, 40, 820, 760);
    }
    ctx.restore();

    // Crisp Emu closeup cropped cleanly above old subtitle y=300..1460
    const emu = IMGS.emuClose;
    ctx.save();
    const rx = isV ? W * 0.54 : W * 0.72;
    const ry = isV ? H * 0.58 : H * 0.54;
    const rr = isV ? 390 : 295;
    const glow = ctx.createRadialGradient(rx, ry, rr * 0.3, rx, ry, rr * 1.35);
    glow.addColorStop(0, 'rgba(255, 220, 60, 0.55)'); glow.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = glow; ctx.beginPath(); ctx.arc(rx, ry, rr * 1.35, 0, Math.PI * 2); ctx.fill();

    ctx.beginPath(); ctx.arc(rx, ry, rr, 0, Math.PI * 2); ctx.clip();
    ctx.drawImage(emu, 160, 500, 760, 840, rx - rr, ry - rr, rr * 2, rr * 2.15);
    ctx.restore();
    ctx.save();
    ctx.strokeStyle = '#FFE600'; ctx.lineWidth = 8;
    ctx.beginPath(); ctx.arc(rx, ry, rr, 0, Math.PI * 2); ctx.stroke();
    ctx.restore();

    drawVignette(ctx, W, H, 0.45);
    if (isV) {
      drawBadge(ctx, '1932 · TRUE STORY', W * 0.5, 195, '#0f172a', '#FFE600', 40, -0.02);
      drawBigTitle(ctx, [
        { text: '20,000 EMUS', color: '#FFE600' },
        { text: 'BEAT THE ARMY?!', color: '#FFFFFF' },
      ], W * 0.5, 275, 112, 'center');
      drawArrow(ctx, 250, 600, 310, 760, 470, 840, '#ff2438', 13);
      drawBadge(ctx, '10,000 BULLETS · 0 WINS', W * 0.5, 1610, '#ef4444', '#FFFFFF', 50, -0.03);
    } else {
      drawBadge(ctx, '1932 · TRUE STORY', 72, 85, '#0f172a', '#FFE600', 30, -0.02, 'left');
      drawBigTitle(ctx, [
        { text: 'ARMY vs', color: '#FFFFFF' },
        { text: '20,000 BIRDS', color: '#FFE600' },
      ], 72, 165, 108, 'left');
      drawBadge(ctx, 'THEY LOST?!', 72, 485, '#ef4444', '#FFFFFF', 54, -0.04, 'left');
      drawArrow(ctx, 430, 485, 580, 430, 665, 310, '#ff2438', 11);
    }
  }
  else if (slug === 'mars-orbit') {
    const bg = ctx.createLinearGradient(0, 0, 0, H);
    bg.addColorStop(0, '#04060e'); bg.addColorStop(0.6, '#140a08'); bg.addColorStop(1, '#2b0d06');
    ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H);
    drawStars(ctx, W, H, 101);

    if (isV) {
      drawPlanetCircle(ctx, IMGS.marsGlobe, W * 0.52, 1060, 410, 'rgba(249, 115, 22, 0.72)');
      drawAstronaut(ctx, 250, 880, 3.2, -0.22);
      drawVignette(ctx, W, H, 0.42);
      drawBadge(ctx, 'IT IS NOT THE COLD', W * 0.5, 210, '#ef4444', '#FFFFFF', 42, -0.02);
      drawBigTitle(ctx, [
        { text: 'SALIVA BOILS', color: '#FFE600' },
        { text: 'IN 1 SECOND', color: '#FFFFFF' },
      ], W * 0.5, 295, 112, 'center');
      drawArrow(ctx, 430, 620, 350, 710, 290, 765, '#ff2438', 13);
      drawBadge(ctx, 'PRESSURE: 0.006 BAR', W * 0.5, 1590, '#0f172a', '#FFE600', 48, 0.01);
    } else {
      drawPlanetCircle(ctx, IMGS.marsGlobe, 910, 375, 275, 'rgba(249, 115, 22, 0.75)');
      drawAstronaut(ctx, 645, 420, 2.75, -0.2);
      drawVignette(ctx, W, H, 0.4);
      drawBadge(ctx, 'IT IS NOT THE COLD', 68, 92, '#ef4444', '#FFFFFF', 32, -0.02, 'left');
      drawBigTitle(ctx, [
        { text: 'BOILS AT', color: '#FFFFFF' },
        { text: '37°C BODY HEAT', color: '#FFE600' },
      ], 68, 175, 96, 'left');
      drawBadge(ctx, '0.006 BAR · NASA DATA', 68, 495, '#0f172a', '#38bdf8', 36, 0, 'left');
      drawArrow(ctx, 450, 445, 540, 405, 600, 365, '#ff2438', 11);
    }
  }
  else if (slug === 'venus-short') {
    const bg = ctx.createLinearGradient(0, 0, W, H);
    bg.addColorStop(0, '#0a0502'); bg.addColorStop(0.55, '#431407'); bg.addColorStop(1, '#9a3412');
    ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H);
    drawStars(ctx, W, H, 202);

    if (isV) {
      drawPlanetCircle(ctx, IMGS.venusClouds, W * 0.54, 1080, 405, 'rgba(251, 191, 36, 0.85)');
      drawAstronaut(ctx, 255, 960, 3.1, 0.35);
      drawVignette(ctx, W, H, 0.42);
      drawBadge(ctx, 'EARTH’S EVIL TWIN', W * 0.5, 210, '#0f172a', '#facc15', 42, -0.02);
      drawBigTitle(ctx, [
        { text: 'CRUSHED', color: '#ff3b30' },
        { text: 'IN 0.5 SEC', color: '#FFFFFF' },
      ], W * 0.5, 295, 128, 'center');
      drawArrow(ctx, 470, 650, 365, 760, 300, 845, '#ff2438', 13);
      drawBadge(ctx, '92 BAR · 465°C LEAD MELTS', W * 0.5, 1595, '#ef4444', '#FFFFFF', 46, 0.01);
    } else {
      drawPlanetCircle(ctx, IMGS.venusClouds, 920, 370, 275, 'rgba(251, 191, 36, 0.85)');
      drawAstronaut(ctx, 645, 410, 2.7, 0.32);
      drawVignette(ctx, W, H, 0.4);
      drawBadge(ctx, '92 BAR PRESSURE', 68, 92, '#ef4444', '#FFFFFF', 34, -0.02, 'left');
      drawBigTitle(ctx, [
        { text: 'CRUSHED', color: '#FFE600' },
        { text: 'IN 0.5 SEC?!', color: '#FFFFFF' },
      ], 68, 175, 108, 'left');
      drawBadge(ctx, '465°C · MELTS LEAD', 68, 495, '#0f172a', '#facc15', 38, 0, 'left');
      drawArrow(ctx, 430, 460, 530, 415, 600, 375, '#ff2438', 11);
    }
  }
  else if (slug === 'asteroid-short') {
    const bg = ctx.createLinearGradient(0, 0, W, H);
    bg.addColorStop(0, '#03050c'); bg.addColorStop(0.6, '#1e0b09'); bg.addColorStop(1, '#450a0a');
    ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H);
    drawStars(ctx, W, H, 303);

    // Draw glowing Blue Earth + Bennu rubble asteroid + crimson impact trajectory
    const ex = isV ? 820 : 1070;
    const ey = isV ? 1240 : 495;
    const er = isV ? 175 : 135;
    // Earth glow
    ctx.save();
    const eg = ctx.createRadialGradient(ex, ey, er*0.4, ex, ey, er*1.6);
    eg.addColorStop(0, 'rgba(56,189,248,0.65)'); eg.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = eg; ctx.beginPath(); ctx.arc(ex, ey, er*1.6, 0, Math.PI*2); ctx.fill();
    const efill = ctx.createRadialGradient(ex - er*0.3, ey - er*0.3, er*0.1, ex, ey, er);
    efill.addColorStop(0, '#60a5fa'); efill.addColorStop(0.6, '#1d4ed8'); efill.addColorStop(1, '#0f172a');
    ctx.fillStyle = efill; ctx.beginPath(); ctx.arc(ex, ey, er, 0, Math.PI*2); ctx.fill();
    ctx.fillStyle = '#22c55e';
    ctx.beginPath(); ctx.ellipse(ex - er*0.2, ey - er*0.15, er*0.35, er*0.25, 0.3, 0, Math.PI*2); ctx.fill();
    ctx.beginPath(); ctx.ellipse(ex + er*0.25, ey + er*0.2, er*0.28, er*0.32, -0.4, 0, Math.PI*2); ctx.fill();
    ctx.restore();

    // Asteroid hero photo
    const ax = isV ? 370 : 750;
    const ay = isV ? 910 : 295;
    const ar = isV ? 255 : 195;
    drawPlanetCircle(ctx, IMGS.bennuRubble, ax, ay, ar, 'rgba(239, 68, 68, 0.9)');

    // Crimson shotgun pellet shower lines toward Earth
    ctx.save();
    for (let i = 0; i < 14; i++) {
      const ang = (i - 6.5) * 0.055;
      ctx.strokeStyle = 'rgba(239, 68, 68, 0.72)';
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.moveTo(ax + ar * 0.4, ay + ar * 0.25);
      ctx.lineTo(ex - er*0.4 + Math.cos(ang)*30, ey + Math.sin(ang)*90);
      ctx.stroke();
    }
    ctx.restore();

    drawVignette(ctx, W, H, 0.42);
    if (isV) {
      drawBadge(ctx, 'APRIL 13, 2029 · APOPHIS', W * 0.5, 205, '#0f172a', '#FFE600', 40, -0.02);
      drawBigTitle(ctx, [
        { text: 'NEVER NUKE', color: '#ff3b30' },
        { text: 'AN ASTEROID!', color: '#FFFFFF' },
      ], W * 0.5, 290, 114, 'center');
      drawBadge(ctx, '1 ROCK → 10,000 PELLETS', W * 0.5, 1590, '#ef4444', '#FFFFFF', 46, -0.01);
    } else {
      drawBadge(ctx, 'FRI APR 13, 2029', 68, 88, '#0f172a', '#FFE600', 32, -0.02, 'left');
      drawBigTitle(ctx, [
        { text: 'DON’T NUKE', color: '#ff3b30' },
        { text: 'THIS ROCK?!', color: '#FFFFFF' },
      ], 68, 170, 102, 'left');
      drawBadge(ctx, '1 → 10,000 PELLETS', 68, 490, '#ef4444', '#FFFFFF', 40, -0.03, 'left');
      drawArrow(ctx, 435, 375, 510, 325, 570, 295, '#FFE600', 11);
    }
  }
  else if (slug === 'black-hole-short') {
    const bg = ctx.createLinearGradient(0, 0, W, H);
    bg.addColorStop(0, '#020206'); bg.addColorStop(0.5, '#12071e'); bg.addColorStop(1, '#260b07');
    ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H);
    drawStars(ctx, W, H, 404);

    const bx = isV ? W * 0.54 : 890;
    const by = isV ? 1040 : 375;
    const br = isV ? 395 : 275;

    // EHT M87* glow circle blended smoothly
    drawPlanetCircle(ctx, IMGS.m87Eht, bx, by, br, 'rgba(249, 115, 22, 0.92)');
    // Pure black inner void
    ctx.fillStyle = '#000000';
    ctx.beginPath(); ctx.arc(bx, by, br * 0.42, 0, Math.PI * 2); ctx.fill();

    // Stretched astronaut falling in
    if (isV) {
      drawAstronaut(ctx, 250, 815, 2.75, 0.72, 1.65);
      drawVignette(ctx, W, H, 0.45);
      drawBadge(ctx, '1,000,000× GRAVITY', W * 0.5, 205, '#ef4444', '#FFFFFF', 44, -0.02);
      drawBigTitle(ctx, [
        { text: 'WHAT HAPPENS', color: '#FFFFFF' },
        { text: 'IF YOU FALL IN?', color: '#FFE600' },
      ], W * 0.5, 290, 104, 'center');
      drawArrow(ctx, 370, 620, 315, 700, 285, 755, '#ff2438', 13);
      drawBadge(ctx, 'SPAGHETTIFIED · ZERO EXIT', W * 0.5, 1595, '#0f172a', '#FFE600', 46, 0.01);
    } else {
      drawAstronaut(ctx, 635, 360, 2.45, 0.75, 1.65);
      drawVignette(ctx, W, H, 0.42);
      drawBadge(ctx, '1,000,000× GRAVITY', 68, 88, '#ef4444', '#FFFFFF', 34, -0.02, 'left');
      drawBigTitle(ctx, [
        { text: 'FALL INTO A', color: '#FFFFFF' },
        { text: 'BLACK HOLE?!', color: '#FFE600' },
      ], 68, 170, 102, 'left');
      drawBadge(ctx, 'TIME FREEZES · NO EXIT', 68, 490, '#0f172a', '#FFE600', 38, 0, 'left');
      drawArrow(ctx, 450, 420, 535, 390, 595, 365, '#ff2438', 11);
    }
  }
};
window.__load = () => loadImages(${JSON.stringify(ASSETS)});
</script>
</body>
</html>`;

async function main() {
  const { chromium } = resolvePlaywright();
  const browser = await chromium.launch({ headless: true, args: ['--ignore-gpu-blocklist'] });
  const page = await browser.newPage();
  await page.setContent(HTML, { waitUntil: 'load' });
  await page.evaluate(() => window.__load());

  const targets = [
    { slug: 'emu-war', dir: path.join(ROOT, 'videos/emu-war/out') },
    { slug: 'mars-orbit', dir: path.join(ROOT, 'videos/mars-orbit/out') },
    { slug: 'venus-short', dir: path.join(ROOT, 'videos/venus-short/out') },
    { slug: 'asteroid-short', dir: path.join(ROOT, 'videos/asteroid-short/out') },
    { slug: 'black-hole-short', dir: path.join(ROOT, 'videos/black-hole-short/out') },
  ];

  for (const t of targets) {
    fs.mkdirSync(t.dir, { recursive: true });
    for (const mode of ['16x9', '9x16']) {
      const w = mode === '9x16' ? 1080 : 1280;
      const h = mode === '9x16' ? 1920 : 720;
      await page.setViewportSize({ width: w, height: h });
      await page.evaluate(([s, m]) => window.renderThumb(s, m), [t.slug, mode]);
      const outPath = path.join(t.dir, `thumb_${mode}.jpg`);
      await page.screenshot({ path: outPath, type: 'jpeg', quality: 94 });
      console.log('Generated:', outPath);
    }
  }
  await browser.close();
}

main().catch((err) => { console.error(err); process.exit(1); });
