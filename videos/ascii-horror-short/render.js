#!/usr/bin/env node
/**
 * 4-Worker Parallel Playwright Renderer for ascii-horror-short (1080x1920 @ 30fps)
 * Usage:
 *   node render.js --stills out/stills
 *   node render.js --audio audio/mix.wav --out out/ascii_horror_short.mp4
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
const outVideo = flag('out', path.join(__dirname, 'out/ascii_horror_short.mp4'));
const audioPath = flag('audio', null);
const workers = parseInt(flag('workers', '4'), 10) || 4;

const beatsData = JSON.parse(fs.readFileSync(path.join(__dirname, 'beats.json'), 'utf8'));
const engineDir = path.join(__dirname, 'engine');

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json',
};

(async () => {
  const totalSec = beatsData.total;
  const totalFrames = Math.ceil(totalSec * FPS);

  const frameMap = new Map();
  let nextToWrite = 0;
  let ff = null;
  let ffDraining = false;

  const flushFrames = () => {
    if (!ff || ffDraining) return;
    while (frameMap.has(nextToWrite)) {
      const buf = frameMap.get(nextToWrite);
      frameMap.delete(nextToWrite);
      nextToWrite++;
      const ok = ff.stdin.write(buf);
      if (nextToWrite % 150 === 0 || nextToWrite === totalFrames) {
        console.log(`  [ascii-horror-short] Frame ${nextToWrite}/${totalFrames}`);
      }
      if (!ok) {
        ffDraining = true;
        ff.stdin.once('drain', () => {
          ffDraining = false;
          flushFrames();
        });
        return;
      }
    }
  };

  const srv = http.createServer((req, res) => {
    const u = decodeURIComponent(req.url.split('?')[0]);
    if (req.method === 'POST' && u.startsWith('/frame/')) {
      const idx = parseInt(u.slice('/frame/'.length), 10);
      const chunks = [];
      req.on('data', (c) => chunks.push(c));
      req.on('end', () => {
        frameMap.set(idx, Buffer.concat(chunks));
        flushFrames();
        res.writeHead(200);
        res.end('ok');
      });
      return;
    }
    if (u === '/ready-to-write') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ nextToWrite }));
      return;
    }
    const fp = u === '/' ? path.join(engineDir, 'index.html') : path.join(engineDir, u.replace(/^\/+/, ''));
    if (!fs.existsSync(fp) || !fs.statSync(fp).isFile()) {
      res.writeHead(404);
      return res.end('Not found');
    }
    res.writeHead(200, { 'Content-Type': MIME[path.extname(fp)] || 'application/octet-stream' });
    fs.createReadStream(fp).pipe(res);
  });

  await new Promise((r) => srv.listen(0, r));
  const port = srv.address().port;
  const browser = await chromium.launch({ headless: true });

  if (stillsDir) {
    const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
    page.on('pageerror', (e) => console.error('[pageerror]', e.message));
    await page.goto(`http://localhost:${port}/`);
    await page.evaluate((bd) => window.initCoreShort(bd), beatsData);
    await page.waitForFunction(() => window.CORE_READY === true, null, { timeout: 15000 });

    const abs = path.resolve(stillsDir);
    fs.rmSync(abs, { recursive: true, force: true });
    fs.mkdirSync(abs, { recursive: true });
    // Frame 0 + key action timestamps across all 15 beats
    const times = [
      0.03, // Frame 0 hook
      3.55, // Beat 0: two extra shadows + crimson eyes
      5.15, // Beat 1: lights slammed on
      7.00, // Beat 2: empty concrete hallway
      9.20, // Beat 3: CRT monitor green hallway
      11.60, // Beat 4: hand wiping static
      13.10, // Beat 5: eyes in brick text
      14.55, // Beat 6: monster lunge
      16.70, // Beat 7: cord ripped out + sparks
      20.60, // Beat 8: blood-red unplugged CRT + skull
      22.60, // Beat 9: sealed photograph
      26.00, // Beat 10: ASCII bars splitting
      30.25, // Beat 11: claws crawling through
      31.90, // Beat 12: > DOORWAY: OPEN
      33.10, // Beat 13: Found the exit. full-screen face
      36.40, // Beat 14: hands turning into ASCII
    ];
    for (let i = 0; i < times.length; i++) {
      await page.evaluate((t) => window.renderFrame(t), times[i]);
      const p = path.join(abs, `still_${String(i).padStart(2, '0')}.jpg`);
      await page.screenshot({ path: p, type: 'jpeg', quality: 92 });
    }
    spawnSync('ffmpeg', [
      '-y', '-v', 'error',
      '-i', path.join(abs, 'still_%02d.jpg'),
      '-vf', 'scale=270:480,tile=4x4',
      path.join(abs, 'sheet.jpg'),
    ], { stdio: 'inherit' });
    console.log(`Rendered ${times.length} stills + sheet.jpg in ${abs}`);
  } else {
    const absOut = path.resolve(outVideo);
    fs.mkdirSync(path.dirname(absOut), { recursive: true });
    const silentPath = audioPath ? absOut + '.silent.mp4' : absOut;

    ff = spawn('ffmpeg', [
      '-y', '-v', 'error',
      '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', '-pix_fmt', 'yuv420p',
      '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
      '-r', String(FPS), '-movflags', '+faststart',
      silentPath,
    ], { stdio: ['pipe', 'inherit', 'inherit'] });

    const ffDone = new Promise((res, rej) => ff.on('exit', (c) => (c === 0 ? res() : rej(new Error('ffmpeg exit ' + c)))));
    const t0 = Date.now();

    const workerPages = await Promise.all(
      Array.from({ length: workers }, async () => {
        const p = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
        p.on('pageerror', (e) => console.error('[pageerror]', e.message));
        await p.goto(`http://localhost:${port}/`);
        await p.evaluate((bd) => window.initCoreShort(bd), beatsData);
        await p.waitForFunction(() => window.CORE_READY === true, null, { timeout: 15000 });
        return p;
      })
    );

    await Promise.all(
      workerPages.map((p, w) =>
        p.evaluate(
          async ({ startIdx, step, total, fps }) => {
            const c = document.getElementById('c');
            for (let f = startIdx; f < total; f += step) {
              if ((f - startIdx) % (step * 8) === 0) {
                while (true) {
                  const st = await fetch('/ready-to-write').then((r) => r.json());
                  if (f - st.nextToWrite < 40) break;
                  await new Promise((r) => setTimeout(r, 15));
                }
              }
              window.renderFrame(f / fps);
              const blob = await new Promise((r) => c.toBlob(r, 'image/jpeg', 0.95));
              await fetch(`/frame/${f}`, { method: 'POST', body: blob });
            }
          },
          { startIdx: w, step: workers, total: totalFrames, fps: FPS }
        )
      )
    );

    while (nextToWrite < totalFrames) {
      flushFrames();
      if (nextToWrite < totalFrames) await new Promise((r) => setTimeout(r, 10));
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
    console.log(`[ascii-horror-short] RENDERED ${totalFrames} frames -> ${absOut} in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
  }

  await browser.close();
  srv.close();
})();
