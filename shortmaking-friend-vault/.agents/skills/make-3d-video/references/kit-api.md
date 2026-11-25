# 3D Kaz kit reference

`shots.js` runs in the studio page after three.js and `kit.js`. The kit is the global `KAZ`
(alias it as `K`). `K.THREE` is three.js r160. Units are metres: a person is about 2 m tall,
ground is y = 0, people face +z.

## Registering shots

```js
K.config({ leftLabel, rightLabel, prefix, alertLabel, hud, capIn, capOut })   // defaults for every shot
K.shot({
  dur: 4.2,                       // seconds (round to frames: Math.round(x*30)/30)
  setup(K) {                      // called once, lazily, before the shot's first frame
    const scene = K.outdoor(), camera = K.camera(38);
    return { scene, camera, update(t, k) { /* t: seconds into shot, k: 0..1 */ } };
  },
  // overlay (all optional). value/status/sub/statusColor/card/alert.value may be functions (t, k) => ...
  value: '1,000',  leftLabel: 'YOUR LUCK',     // top-left counter: label + big serif value (HTML ok, e.g. 10<sup>9</sup>)
  status: 'LUCKY', statusColor: '#ff7a66', sub: 'DAY 3', rightLabel: 'YOU ARE',   // top-right block
  alert: { label: 'THINGS BROKEN', value: (t, k) => Math.round(k * 40) },        // coral counter under the value
  caption: 'Line one,<br>line two.', capIn: .08, capOut: .18,                     // italic serif, fades in/out
  card: '<h4>Small caps title</h4><b>Big serif value</b>',                        // dark glass card, centre
  title: 'Two Moons',             // large spaced title, centre
  hud: false, vignette: false,
});
```

The renderer calls `update(t, k)` then renders. Keep `update` a pure function of `t`.
After a shot is finished its scene is disposed, so shots must not share live objects; share
builder functions instead.

## Maths and timing

| Function | Use |
| --- | --- |
| `clamp(x, a=0, b=1)`, `lerp(a, b, t)`, `smooth(x)` | basics; `smooth` is smoothstep on 0..1 |
| `ramp(t, start, len=.5)` | 0 before `start`, eases to 1 over `len` s. The workhorse for timed events |
| `pop(t, t0, len=.35)` | springy 0→1 scale for popping things in; safe for `setScalar` |
| `rng(seed)` | seeded random `() => 0..1`; use it, never `Math.random`, so frames are repeatable |

## Materials and primitives

`mat(color, opts)` flat-shaded standard material. `glow(color, intensity)` emissive.
`mesh(geom, mat, x, y, z)` with shadows on. `box(w,h,d,color,x,y,z,opts)`,
`cyl(rTop,rBottom,h,color,x,y,z,segments=8,opts)`, `ball(r,color,x,y,z,detail=0,opts)`
(icosahedron; detail 0–2 keeps it faceted).

## Sets

| Function | Notes |
| --- | --- |
| `outdoor({ skyTop, skyBottom, fog, fogNear, fogFar, grass, sunPos, range, mood })` | sky gradient, haze, sun with soft shadows, endless grass. `mood`: `'dusk'`, `'night'`, `'dust'`. `range` = shadow area half-size |
| `indoor({ wall, floor, window, mood })` | room with floor, back wall (z=-4), left wall (x=-6), optional lit window |
| `space({ stars, seed })` | near-black background, key light, starfield |
| `lights(scene, { sun, sunI, sky, ground, hemiI, pos, range })` | hemisphere + shadowed sun, for custom scenes |
| `skyGradient(top, bottom)` | texture for `scene.background` |
| `road({ width, length, z, x, along })` | road with pavements and centre dashes; `along: 'x'` turns it |

To remove the default grass (e.g. for a beach with water below y=0):
`scene.remove(scene.children.find(o => o.isMesh && o.geometry.type === 'PlaneGeometry'))`.

## Props

`tree(x, z, scale, seed, leafColors)`, `house(x, z, { wall, roof, door, rot })`,
`fence(x, z, length, color)`, `car(color)`, `trafficLight()` (`.set(0..1)` red→green),
`table({ w, d, h, color })` (`.top` = height), `chair(color)`, `sofa(color)`, `bed(color)`,
`mug(x,y,z)`, `plate(x,y,z)`, `coin(r)`, `mountain(x, z, scale, color)`.

## People

`person({ shirt, pants, skin, hair, longHair })` returns a group with `.parts`:
`legL legR armL armR` (pivots at hip/shoulder; rotate `.rotation.x` to swing), `torso`, `head`
(rotate x to nod/look up, y to turn), `eyes` (array; scale y down to close), `mouth`.
Set `.baseY` when standing on something.

- `walk(person, phase, amp=.55)`: phase = t × 7 to stroll, × 10–12 to run. Move `.position` yourself.
- `idle(person, t)`: breathing and a slow look around.
- `sit(person)`: seated pose; lower the person by about 0.3–0.35.
- `crowd(n, { seed, spread })`: a group of varied people.
- Lying down: `p.rotation.x = -Math.PI/2`, raise to the mattress height.
- Soldier/helmet, suit, waving: see `examples/road-to-ww2` and `examples/dreams`.

## Space

- `planet({ radius, seed, land, sea, ice, cracks, atmosphere })`: faceted globe; `.setCracks(heat 0..1, t)` makes glowing cracks. Use `cracks: 0` for a plain Earth.
- `blackHole(radius)`: black sphere with a glowing tilted disk.

## Text in the scene

- `label(text, size=1, color)`: camera-facing sprite drawn on top of everything. `.pop(scale)`.
- `sign(text, w, h, { bg, color, font })`: flat panel with text (road signs, banners, boards).

## Camera

`camera(fov=38)`; `dolly(cam, k, from[3], to[3], lookAt[3])` eases between two positions.
Slow moves read best: shift the camera 10–20% of its distance over a shot.

## Recipes in the examples

- Map table with extruded countries, labels, arrows and pulsing dots: `mapScene()` in `examples/road-to-ww2`. Countries are `[lon, lat]` polygons; add your own to `POLY`.
- Data card with an animated bar chart, or an SVG line chart: shots 11 in `road-to-ww2` and `chart()` in `dreams`.
- Moon in the sky with a correct phase drawn on canvas (`skyMoon`, `drawMoon`), orbit rings, tide bulge from several bodies (`system().tide`), beach with rising water (`beach().level`): `examples/two-moons`.
- Glowing brain with sparks, floating islands of memories, dream sky: `examples/dreams`.
- Smoke puffs, tanks, fortress gate, candlelit memorial: `examples/road-to-ww2`.

## Renderer

```
node render.js <project> --stills [--at 0.6] [--shots 0,4]    stills + sheet.jpg
node render.js <project> [--shots 2,5] [--size WxH] [--fps 30] [--audio file] [--out name.mp4]
```

Each shot is encoded to `out/shots/shotNNN.mp4`, then joined without re-encoding and muxed with
the audio. `--shots` re-renders only those shots and rejoins. Page errors in `shots.js` are
printed as `[shots.js error]` and fail the render.

The overlay scales with the frame (`--u` CSS unit), so vertical and 4K renders keep proportions;
frame shots for the aspect you render.
