const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('../videos/emu-war/studio/node_modules/playwright');

const configPath = path.join(__dirname, 'subgoal.json');

function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const key = a.slice(2);
      const val = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : 'true';
      out[key] = val;
    }
  }
  return out;
}

const args = parseArgs(process.argv.slice(2));
const saved = fs.existsSync(configPath) ? JSON.parse(fs.readFileSync(configPath, 'utf8')) : {};

const cfg = {
  channelName: args.name || saved.channelName || 'PIXELATE PAST',
  handle: args.handle || saved.handle || '@pixelatepast',
  tagline: args.tagline || saved.tagline || 'CHAOTIC ROBLOX 3D STORYTIME SHORTS IN BLENDER',
  currentSubs: args.subs !== undefined ? Number(args.subs) : Number(saved.currentSubs ?? 18),
  goalSubs: args.goal !== undefined ? Number(args.goal) : Number(saved.goalSubs ?? 1000),
  goalLabel: args.label || saved.goalLabel || 'FIRST MILESTONE',
};

if (args.subs !== undefined || args.goal !== undefined || args.name || args.tagline || args.label || args.handle) {
  fs.writeFileSync(configPath, JSON.stringify(cfg, null, 2) + '\n', 'utf8');
  console.log('Updated subgoal.json:', cfg);
}

const onlyMode = args.only || null; // 'pfp' | 'banner' | null

function formatNum(n) {
  return Math.max(0, Math.round(n)).toLocaleString('en-US');
}

function splitWordmark(name) {
  const parts = String(name).trim().split(/\s+/);
  if (parts.length <= 1) return { first: name, second: '' };
  const second = parts.pop();
  return { first: parts.join(' '), second };
}

function buildHtml(mode, w, h) {
  const pct = cfg.goalSubs > 0 ? Math.min(100, Math.max(0, (cfg.currentSubs / cfg.goalSubs) * 100)) : 0;
  const pctText = pct >= 10 || pct === 0 ? `${Math.round(pct)}%` : `${pct.toFixed(1)}%`;
  const barWidth = pct > 0 ? Math.max(2.5, pct) : 0;
  const { first, second } = splitWordmark(cfg.channelName);

  if (mode === 'pfp') {
    return `<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: ${w}px;
    height: ${h}px;
    overflow: hidden;
    background: #09071a;
    position: relative;
  }
  .bg-img {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  /* Subtle radial polish + crisp circle-safe framing glow */
  .pfp-vignette {
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 50% 48%, rgba(0,0,0,0) 48%, rgba(7, 5, 20, 0.42) 85%, rgba(7, 5, 20, 0.72) 100%);
    pointer-events: none;
  }
</style>
</head>
<body>
  <img class="bg-img" src="/pfp_3d.png" onload="window.IMG_DONE = true" />
  <div class="pfp-vignette"></div>
  <script>
    const check = () => { if (window.IMG_DONE) window.DONE = true; else setTimeout(check, 20); };
    check();
  </script>
</body>
</html>`;
  }

  return `<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: ${w}px;
    height: ${h}px;
    overflow: hidden;
    background: #070514;
    font-family: 'Montserrat', 'Segoe UI', system-ui, -apple-system, sans-serif;
    position: relative;
  }
  .bg-img {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  .banner-vignette {
    position: absolute;
    inset: 0;
    background:
      radial-gradient(ellipse 46% 38% at 50% 50%, rgba(7, 5, 20, 0.84) 0%, rgba(7, 5, 20, 0.46) 62%, rgba(7, 5, 20, 0.16) 100%),
      linear-gradient(180deg, rgba(7, 5, 20, 0.48) 0%, rgba(7, 5, 20, 0.0) 32%, rgba(7, 5, 20, 0.0) 68%, rgba(7, 5, 20, 0.52) 100%);
    pointer-events: none;
  }

  /* YouTube Safe Area: 1546 x 423 centered in 2560 x 1440 */
  .safe-zone {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    width: 1120px;
    height: 360px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    pointer-events: none;
  }

  .eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 6px 18px;
    border-radius: 999px;
    background: rgba(56, 189, 248, 0.16);
    border: 1.5px solid rgba(56, 189, 248, 0.55);
    color: #7dd3fc;
    font-size: 15px;
    font-weight: 800;
    letter-spacing: 0.20em;
    text-transform: uppercase;
    margin-bottom: 12px;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.45);
  }

  .title {
    font-size: 88px;
    font-weight: 900;
    letter-spacing: 0.06em;
    line-height: 0.96;
    color: #f8fafc;
    text-shadow:
      0 6px 26px rgba(0, 0, 0, 0.85),
      0 3px 0 rgba(15, 23, 42, 0.95);
    margin-bottom: 10px;
  }
  .title span.accent {
    background: linear-gradient(180deg, #fef08a 0%, #fbbf24 55%, #f59e0b 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: none;
    filter: drop-shadow(0 6px 22px rgba(251, 191, 36, 0.42));
  }

  .tagline {
    font-size: 19px;
    font-weight: 800;
    letter-spacing: 0.18em;
    color: #e2e8f0;
    text-shadow: 0 2px 12px rgba(0, 0, 0, 0.95);
    margin-bottom: 22px;
  }

  .subgoal-card {
    width: 720px;
    padding: 14px 22px 16px;
    border-radius: 16px;
    background: rgba(8, 8, 16, 0.90);
    border: 2px solid rgba(56, 189, 248, 0.55);
    box-shadow:
      0 14px 40px rgba(0, 0, 0, 0.72),
      0 0 24px rgba(56, 189, 248, 0.16),
      inset 0 1px 0 rgba(255, 255, 255, 0.10);
  }

  .subgoal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
  }

  .subgoal-left {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .goal-pill {
    background: linear-gradient(135deg, #f43f5e 0%, #e11d48 100%);
    color: #ffffff;
    font-size: 12px;
    font-weight: 900;
    letter-spacing: 0.14em;
    padding: 4px 11px;
    border-radius: 7px;
    text-transform: uppercase;
    box-shadow: 0 2px 10px rgba(244, 63, 94, 0.45);
  }

  .goal-label {
    font-size: 15px;
    font-weight: 800;
    letter-spacing: 0.10em;
    color: #e2e8f0;
    text-transform: uppercase;
  }

  .subgoal-counts {
    font-size: 19px;
    font-weight: 900;
    letter-spacing: 0.04em;
    color: #f8fafc;
  }
  .subgoal-counts .cur {
    color: #fde047;
  }
  .subgoal-counts .pct {
    margin-left: 8px;
    font-size: 14px;
    font-weight: 800;
    color: #94a3b8;
  }

  .bar-track {
    position: relative;
    width: 100%;
    height: 16px;
    border-radius: 999px;
    background: rgba(30, 41, 59, 0.95);
    border: 1px solid rgba(148, 163, 184, 0.25);
    overflow: hidden;
  }

  .bar-fill {
    height: 100%;
    width: ${barWidth}%;
    border-radius: 999px;
    background: linear-gradient(90deg, #38bdf8 0%, #f43f5e 52%, #fde047 100%);
    box-shadow: 0 0 18px rgba(56, 189, 248, 0.75);
  }

  .bar-ticks {
    position: absolute;
    inset: 0;
    display: flex;
    justify-content: space-evenly;
    pointer-events: none;
  }
  .bar-ticks span {
    width: 1.5px;
    height: 100%;
    background: rgba(7, 5, 20, 0.5);
  }
</style>
</head>
<body>
  <img class="bg-img" src="/banner_3d.png" onload="window.IMG_DONE = true" />
  <div class="banner-vignette"></div>
  <div class="safe-zone">
    <div class="eyebrow">${cfg.handle} &bull; ROBLOX 3D STORYTIME SHORTS</div>
    <div class="title">${first}${second ? ` <span class="accent">${second}</span>` : ''}</div>
    <div class="tagline">${cfg.tagline}</div>
    <div class="subgoal-card">
      <div class="subgoal-header">
        <div class="subgoal-left">
          <span class="goal-pill">${cfg.goalLabel}</span>
          <span class="goal-label">ROAD TO ${formatNum(cfg.goalSubs)} SUBSCRIBERS</span>
        </div>
        <div class="subgoal-counts">
          <span class="cur">${formatNum(cfg.currentSubs)}</span> / ${formatNum(cfg.goalSubs)}
          <span class="pct">(${pctText})</span>
        </div>
      </div>
      <div class="bar-track">
        <div class="bar-fill"></div>
        <div class="bar-ticks"><span></span><span></span><span></span></div>
      </div>
    </div>
  </div>
  <script>
    const check = () => { if (window.IMG_DONE) window.DONE = true; else setTimeout(check, 20); };
    check();
  </script>
</body>
</html>`;
}

(async () => {
  const jobs = [];
  if (!onlyMode || onlyMode === 'pfp') jobs.push(['pfp', 1024, 1024]);
  if (!onlyMode || onlyMode === 'banner') jobs.push(['banner', 2560, 1440]);

  const srv = http.createServer((q, r) => {
    const u = q.url.split('?')[0];
    if (u === '/pfp') { r.writeHead(200, { 'Content-Type': 'text/html' }); return r.end(buildHtml('pfp', 1024, 1024)); }
    if (u === '/banner') { r.writeHead(200, { 'Content-Type': 'text/html' }); return r.end(buildHtml('banner', 2560, 1440)); }
    if (u === '/pfp_3d.png' || u === '/banner_3d.png') {
      const f = path.join(__dirname, u.slice(1));
      if (!fs.existsSync(f)) { r.writeHead(404); return r.end('Missing ' + f); }
      r.writeHead(200, { 'Content-Type': 'image/png' });
      return fs.createReadStream(f).pipe(r);
    }
    r.writeHead(404);
    r.end();
  });

  await new Promise((r) => srv.listen(0, r));
  const port = srv.address().port;
  const browser = await chromium.launch({
    args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'],
  });

  for (const [name, w, h] of jobs) {
    const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
    await page.goto(`http://localhost:${port}/${name}`);
    await page.waitForFunction('window.DONE === true');
    await page.screenshot({ path: path.join(__dirname, `${name}.png`), type: 'png' });
    await page.close();
    console.log(`saved ${name}.png (${w}x${h})`);
  }

  await browser.close();
  srv.close();
})();
