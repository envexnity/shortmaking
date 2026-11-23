const path = require('path');
const { runPixelRender } = require(path.resolve(__dirname, '../../scripts/pixel_short_kit/fast_render'));

const args = process.argv.slice(2);
const flag = (name, def = null) => {
  const i = args.indexOf('--' + name);
  if (i < 0) return def;
  return (args[i + 1] && !args[i + 1].startsWith('--')) ? args[i + 1] : true;
};

runPixelRender({
  projectDir: __dirname,
  stillsDir: flag('stills', null),
  audioPath: flag('audio', null),
  outVideo: flag('out', path.join(__dirname, 'out/sun_touch_8bit_short.mp4')),
  workers: parseInt(flag('workers', '4'), 10) || 4,
}).catch((e) => { console.error(e); process.exit(1); });
