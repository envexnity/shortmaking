#!/usr/bin/env node
/**
 * Orbit 2D Space Video Renderer
 * Usage:
 *   node render.js <scenes.js> --stills <out_dir> [--at 0.68]
 *   node render.js <scenes.js> --out <video_raw.mp4> [--fps 30] [--size 1920x1080] [--audio <mix.wav>]
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
  throw new Error('Playwright not found. Install playwright or ensure videos/emu-war/studio/node_modules/playwright exists.');
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
const kitDir = __dirname;
const [W, H] = String(flag('size', '1920x1080')).split('x').map(Number);
const FPS = Number(flag('fps', 30));
const stillsDir = flag('stills', null);
const outVideo = flag('out', path.join(projectDir, 'out/video_raw.mp4'));
const audioPath = flag('audio', null);
const stillFrac = Number(flag('at', 0.68));

if (!fs.existsSync(scenesPath)) throw new Error('Missing scenes file: ' + scenesPath);
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
  if (u === '/') filePath = path.join(kitDir, 'page.html');
  else if (u === '/orbit.js') filePath = path.join(kitDir, 'orbit.js');
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
    args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'],
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
      '-vf', `scale=480:270,tile=${cols}x${rows}`,
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
      const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
      if (!enc.stdin.write(buf)) await new Promise((r) => enc.stdin.once('drain', r));
      if (f % 150 === 0 || f === totalFrames - 1) {
        console.log(`Frame ${f + 1}/${totalFrames} (${((Date.now() - t0) / 1000).toFixed(1)}s)`);
      }
    }
    enc.stdin.end();
    const exitCode = await done;
    if (exitCode !== 0) throw new Error('FFmpeg failed with exit code ' + exitCode);

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
    console.log(`Rendered ${totalFrames} frames (${totalSec.toFixed(2)}s @ ${W}x${H}/${FPS}fps) -> ${absOut}`);
  }

  await browser.close();
  srv.close();
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
