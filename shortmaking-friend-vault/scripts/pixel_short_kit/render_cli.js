/**
 * Shared CLI entry point for fast 4-worker pixel short rendering.
 * Usage:
 *   node render_cli.js <projectDir> [--stills <dir>] [--audio <wav>] [--out <mp4>] [--workers 4]
 */
const path = require('path');
const { runPixelRender } = require('./fast_render');

const args = process.argv.slice(2);
const projectDir = path.resolve(args[0] || process.cwd());
const flag = (name, def = null) => {
  const i = args.indexOf('--' + name);
  if (i < 0) return def;
  return (args[i + 1] && !args[i + 1].startsWith('--')) ? args[i + 1] : true;
};

const stillsDir = flag('stills', null);
const audioPath = flag('audio', null);
const outVideo = flag('out', path.join(projectDir, 'out', path.basename(projectDir).replace(/-/g, '_') + '.mp4'));
const workers = parseInt(flag('workers', '4'), 10) || 4;

runPixelRender({ projectDir, stillsDir, audioPath, outVideo, workers }).catch((err) => {
  console.error(err);
  process.exit(1);
});
