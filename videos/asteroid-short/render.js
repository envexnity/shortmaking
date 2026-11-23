#!/usr/bin/env node
/**
 * Native 9:16 Orbit 2D Space Short Renderer (1080x1920 @ 30fps)
 * Usage:
 *   node render.js scenes.js --stills stills [--at 0.65]
 *   node render.js scenes.js --out out/video_raw.mp4 [--fps 30] [--size 1080x1920] [--audio audio/mix.wav]
 */
const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn, spawnSync } = require('child_process');

function resolvePlaywright() {
  const candidates = [
    'playwright',
    path.resolve(__dirname, 'node_modules/playwright'),
    path.resolve(__dirname, '../../videos/emu-war/studio/node_modules/playwright'),
  ];
  for (const c of candidates) {
    try { return require(c); } catch {}
  }
  throw new Error('Playwright not found.');
}

const { chromium } = resolvePlaywright();
const args = process.argv.slice(2);
const flag = (name, def = null) => {
  const i = args.indexOf('--' + name);
  if (i < 0) return def;
  return (args[i + 1] && !args[i + 1].startsWith('--')) ? args[i + 1] : true;
};

const scenesArg = args.find((a, idx) => !a.startsWith('--') && !(args[idx - 1] || '').startsWith('--'));
if (!scenesArg) {
  console.error('Usage: node render.js <scenes.js> --stills <dir> | --out <file.mp4>');
  process.exit(1);
}

const scenesPath = path.resolve(scenesArg);
const projectDir = path.dirname(scenesPath);
const [W, H] = String(flag('size', '1080x1920')).split('x').map(Number);
const FPS = Number(flag('fps', 30));
const stillsDir = flag('stills', null);
const outVideo = flag('out', path.join(projectDir, 'out/video_raw.mp4'));
const audioPath = flag('audio', null);
const stillFrac = Number(flag('at', 0.65));

if (spawnSync('ffmpeg', ['-version']).status !== 0) throw new Error('ffmpeg not on PATH');

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.png': 'image/png',
  '.json': 'application/json',
};

const srv = http.createServer((req, res) => {
  const u = decodeURIComponent(req.url.split('?')[0]);
  let filePath = null;
  if (u === '/') filePath = path.join(projectDir, 'page.html');
  else if (u === '/orbit_short.js') filePath = path.join(projectDir, 'orbit_short.js');
  else if (u === '/scenes.js') filePath = scenesPath;
  else {
    const rel = u.replace(/^\/+/, '');
    const candidate = path.resolve(projectDir, rel);
    if (candidate.startsWith(projectDir) && fs.existsSync(candidate) && fs.statSync(candidate).isFile()) {
      filePath = candidate;
    }
  }
  if (!filePath || !fs.existsSync(filePath)) {
    res.writeHead(404);
    return res.end('Not found');
  }
  const ext = path.extname(filePath).toLowerCase();
  res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream' });
  fs.createReadStream(filePath).pipe(res);
});

function ff(ffArgs) {
  return new Promise((res, rej) => {
    const p = spawn('ffmpeg', ['-y', '-v', 'error', ...ffArgs], { stdio: ['ignore', 'inherit', 'inherit'] });
    p.on('exit', (c) => (c === 0 ? res() : rej(new Error('ffmpeg exited ' + c))));
  });
}

(async () => {
  await new Promise((r) => srv.listen(0, r));
  const port = srv.address().port;
  const browser = await chromium.launch({
    args: ['--ignore-gpu-blocklist'],
  });
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  page.on('pageerror', (e) => console.error('[pageerror]', e.message));

  await page.goto(`http://localhost:${port}/`);
  await page.waitForFunction(() => window.ORBIT_READY === true, null, { timeout: 30000 });
  await page.evaluate(([w, h]) => {
    const c = document.getElementById('c');
    c.width = w;
    c.height = h;
  }, [W, H]);

  const totalSec = await page.evaluate(() => window.ORBIT_TOTAL);
  const count = await page.evaluate(() => window.ORBIT_COUNT);

  if (stillsDir) {
    const absStills = path.resolve(stillsDir);
    fs.rmSync(absStills, { recursive: true, force: true });
    fs.mkdirSync(absStills, { recursive: true });
    for (let i = 0; i < count; i++) {
      await page.evaluate(([idx, f]) => window.ORBIT.renderStill(idx, f), [i, stillFrac]);
      const p = path.join(absStills, `scene_${String(i).padStart(2, '0')}.jpg`);
      await page.screenshot({ path: p, type: 'jpeg', quality: 92 });
    }
    const cols = Math.min(4, count);
    const rows = Math.ceil(count / cols);
    await ff([
      '-framerate', '1',
      '-start_number', '0',
      '-i', path.join(absStills, 'scene_%02d.jpg'),
      '-vf', `scale=270:480,tile=${cols}x${rows}`,
      '-frames:v', '1',
      '-q:v', '3',
      path.join(absStills, 'sheet.jpg'),
    ]);
    console.log(`Stills written (${count} scenes) -> ${path.join(absStills, 'sheet.jpg')}`);
  } else {
    const absOut = path.resolve(outVideo);
    fs.mkdirSync(path.dirname(absOut), { recursive: true });
    const silentPath = audioPath ? absOut + '.silent.mp4' : absOut;
    const totalFrames = Math.round(totalSec * FPS);
    const enc = spawn('ffmpeg', [
      '-y', '-v', 'error',
      '-f', 'image2pipe',
      '-framerate', String(FPS),
      '-c:v', 'mjpeg',
      '-i', '-',
      '-c:v', 'libx264',
      '-crf', '18',
      '-preset', 'medium',
      '-pix_fmt', 'yuv420p',
      '-r', String(FPS),
      '-movflags', '+faststart',
      silentPath,
    ], { stdio: ['pipe', 'inherit', 'inherit'] });

    const done = new Promise((r) => enc.on('exit', r));
    const t0 = Date.now();
    for (let f = 0; f < totalFrames; f++) {
      const t = f / FPS;
      await page.evaluate((tt) => window.ORBIT.renderAt(tt), t);
      const buf = await page.screenshot({ type: 'jpeg', quality: 90 });
      if (!enc.stdin.write(buf)) await new Promise((r) => enc.stdin.once('drain', r));
      if (f % 30 === 0 || f === totalFrames - 1) {
        console.log(`Frame ${f + 1}/${totalFrames} (${((Date.now() - t0) / 1000).toFixed(1)}s)`);
      }
    }
    enc.stdin.end();
    await done;

    if (audioPath) {
      await ff([
        '-i', silentPath,
        '-i', path.resolve(audioPath),
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-map', '0:v:0',
        '-map', '1:a:0',
        '-shortest',
        absOut,
      ]);
      fs.rmSync(silentPath, { force: true });
    }
    console.log(`Rendered -> ${absOut}`);
  }

  await browser.close();
  srv.close();
})();
