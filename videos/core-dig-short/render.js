#!/usr/bin/env node
/**
 * Core Dig Short — Playwright 1080x1920 Renderer
 * Usage:
 *   node render.js --stills out/stills
 *   node render.js --audio audio/mix.wav --out out/final.mp4
 */
const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn, spawnSync } = require('child_process');

const { chromium } = require(path.resolve(__dirname, '../../videos/emu-war/studio/node_modules/playwright'));

const args = process.argv.slice(2);
const flag = (name, def = null) => {
  const i = args.indexOf('--' + name);
  if (i < 0) return def;
  return (args[i + 1] && !args[i + 1].startsWith('--')) ? args[i + 1] : true;
};

const W = 1080;
const H = 1920;
const FPS = 30;
const stillsDir = flag('stills', null);
const outVideo = flag('out', path.join(__dirname, 'out/final.mp4'));
const audioPath = flag('audio', null);

const beatsData = JSON.parse(fs.readFileSync(path.join(__dirname, 'beats.json'), 'utf8'));
const engineDir = path.join(__dirname, 'engine');

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json',
};

const srv = http.createServer((req, res) => {
  const u = decodeURIComponent(req.url.split('?')[0]);
  let fp = u === '/' ? path.join(engineDir, 'index.html') : path.join(engineDir, u.replace(/^\/+/, ''));
  if (!fs.existsSync(fp) || !fs.statSync(fp).isFile()) {
    res.writeHead(404);
    return res.end('Not found');
  }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(fp)] || 'application/octet-stream' });
  fs.createReadStream(fp).pipe(res);
});

(async () => {
  await new Promise((r) => srv.listen(0, r));
  const port = srv.address().port;
  const browser = await chromium.launch({
    args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'],
  });
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  page.on('pageerror', (e) => console.error('[pageerror]', e.message));

  await page.goto(`http://localhost:${port}/`);
  await page.evaluate((bd) => window.initCoreShort(bd), beatsData);
  await page.waitForFunction(() => window.CORE_READY === true, null, { timeout: 15000 });

  if (stillsDir) {
    const abs = path.resolve(stillsDir);
    fs.rmSync(abs, { recursive: true, force: true });
    fs.mkdirSync(abs, { recursive: true });
    // Frame 0 + midpoint of every beat
    const times = [0.05, ...beatsData.beats.map((b) => (b.start + b.end) * 0.5)];
    for (let i = 0; i < times.length; i++) {
      await page.evaluate((t) => window.renderFrame(t), times[i]);
      const p = path.join(abs, `still_${String(i).padStart(2, '0')}.jpg`);
      await page.screenshot({ path: p, type: 'jpeg', quality: 92 });
    }
    // Tile contact sheet
    spawnSync('ffmpeg', [
      '-y', '-v', 'error',
      '-i', path.join(abs, 'still_%02d.jpg'),
      '-vf', 'scale=270:480,tile=5x4',
      path.join(abs, 'sheet.jpg'),
    ], { stdio: 'inherit' });
    console.log(`Rendered ${times.length} stills + sheet.jpg in ${abs}`);
  } else {
    const absOut = path.resolve(outVideo);
    fs.mkdirSync(path.dirname(absOut), { recursive: true });
    const silentPath = audioPath ? absOut + '.silent.mp4' : absOut;
    const totalSec = beatsData.total;
    const totalFrames = Math.ceil(totalSec * FPS);

    const ff = spawn('ffmpeg', [
      '-y', '-v', 'error',
      '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'fast', '-crf', '16', '-pix_fmt', 'yuv420p',
      '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
      '-r', String(FPS), '-movflags', '+faststart',
      silentPath,
    ], { stdio: ['pipe', 'inherit', 'inherit'] });

    const ffDone = new Promise((res, rej) => ff.on('exit', (c) => (c === 0 ? res() : rej(new Error('ffmpeg exit ' + c)))));
    const t0 = Date.now();
    for (let f = 0; f < totalFrames; f++) {
      const t = f / FPS;
      await page.evaluate((time) => window.renderFrame(time), t);
      const buf = await page.screenshot({ type: 'jpeg', quality: 96 });
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
      if (f % 60 === 0 || f === totalFrames - 1) {
        console.log(`Frame ${f + 1}/${totalFrames} (${((Date.now() - t0) / 1000).toFixed(1)}s)`);
      }
    }
    ff.stdin.end();
    await ffDone;

    if (audioPath && fs.existsSync(audioPath)) {
      const mux = spawnSync('ffmpeg', [
        '-y', '-v', 'error',
        '-i', silentPath,
        '-i', path.resolve(audioPath),
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
        '-map', '0:v:0', '-map', '1:a:0', '-shortest',
        absOut,
      ], { stdio: 'inherit' });
      if (mux.status !== 0) throw new Error('ffmpeg mux exit ' + mux.status);
      fs.rmSync(silentPath, { force: true });
    }
    console.log(`Rendered ${totalFrames} frames -> ${absOut} in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
  }

  await browser.close();
  srv.close();
})();
