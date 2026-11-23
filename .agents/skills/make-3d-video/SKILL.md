---
name: make-3d-video
description: This skill should be used when the user wants a narrated low-poly 3D explainer video in the 3D Kaz style (blocky characters, flat-shaded sets, corner HUD counters, italic serif captions), e.g. "make a 3D Kaz video", "make a 3D video from this voiceover", "animate this script in low-poly 3D", "make a What If video in 3D", "make this history/science video with the 3D style", or "render the 3D Kaz demo". It covers setup, voiceover timing, shot planning, scene building with the studio kit, stills QC, full render and muxing the voiceover.
---

# Make a 3D Kaz video

Build a narrated video in the 3D Kaz look: low-poly flat-shaded 3D (three.js) filmed frame by
frame in headless Chromium, with a 2D overlay of corner HUD, captions, cards and titles, encoded
with FFmpeg. One shot per beat of narration, cut in the pauses of the voiceover.

Paths below are relative to this skill's folder: `${CLAUDE_PLUGIN_ROOT}/skills/make-3d-video/`.
The engine lives in `studio/`. Read `references/kit-api.md` before writing scenes, and
`references/style-and-planning.md` before planning shots.

## 1. Set up (once per machine or session)

```bash
cd ${CLAUDE_PLUGIN_ROOT}/skills/make-3d-video/studio
node -v && ffmpeg -version | head -1          # Node 18+ and FFmpeg are required
npm install                                     # fetches three.js 0.160.0
node -e "require('playwright')" || (npm install playwright && npx playwright install chromium)
```

If the plugin folder is read-only, copy `studio/` to a writable working folder first and run
everything from the copy. If npm or the Chromium download is blocked, say so plainly and ask the
user to run setup on a machine with internet access; do not try to work around a blocked network.

Smoke-test with `node render.js examples/luck-demo --stills` and look at
`examples/luck-demo/stills/sheet.jpg`.

## 2. Intake

Collect, asking only for what is missing:
- **Narration**: a voiceover file (mp3/wav) and its script text. A script alone is fine; then
  time shots at about 2.6 words per second and render without audio.
- **Format**: 16:9 at 1280x720 by default. Offer 1920x1080, 1080x1920 (vertical) or 3840x2160.
- **HUD**: what the top-left counter and top-right status should track for this topic (see
  the style guide). Offer to hide the HUD for topics where it would be glib.

Start working as soon as the request is clear; do not wait for approval of a plan.

## 3. Time the voiceover

Put the script in `beats.txt`, one beat per line (a sentence, or a clause when a sentence runs
past ~5 seconds or changes subject mid-way). Then:

```bash
python3 studio/tools/timing.py voice.mp3 beats.txt
```

It prints each beat's start/end and a `const B = [...]` array of cut points: pauses found by
FFmpeg, matched to beats by word count with a best-fit alignment (or by word timestamps if
`faster-whisper` is installed). Read the table: a beat far longer or shorter than its word count
suggests a misplaced cut, so move it to the neighbouring pause. Merge beats under ~1.2 s.
Tell the user the timing is estimated from pauses unless word timestamps were used.

## 4. Plan the shots

Write one line per beat: setting, subject, camera move, the one thing that changes, HUD values,
caption text. Follow `references/style-and-planning.md`. Mix 3D sets with diagram shots
(map table, orbit diagram, chart card) so it never sits in one place for long. Reuse a set
across consecutive beats by building it in a shared function.

## 5. Build `shots.js`

Create a project folder (e.g. `~/videos/<slug>/`) holding `shots.js` and a copy of the voiceover.
Use the pattern from the examples:

```js
const K = KAZ, T = K.THREE, PI = Math.PI;
K.config({ leftLabel: 'YEAR', rightLabel: 'LOCATION', prefix: '', capIn: .08, capOut: .18 });
const B = [0, 2.42, 4.47 /* ...from timing.py */];
let n = 0;
const S = o => { const i = n++; K.shot(Object.assign({ dur: (Math.round(B[i + 1] * 30) - Math.round(B[i] * 30)) / 30 }, o)); };
S({ value: '1939', status: 'POLAND', caption: 'German troops invaded Poland.', setup() { /* return { scene, camera, update(t, k) } */ } });
```

Frame-rounded durations keep the video in sync with the audio. Every `update(t, k)` must be a
pure function of `t` (seconds into the shot) and `k` (0..1): no state carried between frames,
because stills jump straight to one frame. Time beats inside a shot from the timing table
(e.g. pop a label at the second the word is spoken).

The examples are worth reading before writing a similar shot:
- `examples/luck-demo`: street, kitchen, road, space; the basic kit.
- `examples/dreams`: bedroom, glowing brain, sleep chart card, floating memory islands.
- `examples/road-to-ww2`: extruded map table with arrows, dots and labels; crowds; buildings.
- `examples/two-moons`: night sky with drawn moon phases, orbit diagrams, tide bulge, beach.

## 6. QC with stills, then render

```bash
node studio/render.js <project> --stills --at 0.8      # one frame per shot -> <project>/stills/sheet.jpg
```

Look at the sheet. Check: subject framed and lit, nothing cut off by the frame edges, labels not
colliding with the HUD or captions, text readable, no black or empty shots. Fix and re-check
(`--shots 3,7` re-renders only those). Check a second moment (`--at 0.3`) for shots with
big changes. Then render:

```bash
node studio/render.js <project> --audio <project>/voice.mp3 --out <slug>.mp4 [--size 1920x1080]
```

Run long renders in the background (about 6–10 minutes per 90 s at 720p on 2 CPU cores).
Afterwards, sample frames (`ffmpeg -i out.mp4 -vf "fps=1/3,scale=384:-1,tile=5x6" -frames:v 1 sheet.jpg`)
and confirm video and audio durations match with ffprobe.

## 7. Deliver

Send the MP4. In one short message: length and shot count, anything estimated (timing, facts
added beyond the script such as dates or figures, schematic diagrams), and what has no sound
besides the voiceover. Offer changes per shot; a single shot re-renders with `--shots N`.

## Rules

- Captions are the script, verbatim. Break each into two balanced lines with `<br>`.
- Any fact added on screen that is not in the script (a date, a statistic, a number on a
  counter) must be correct; check it, and list it for the user to verify.
- Atrocities, deaths and suffering are shown without violence or gore: memorials, empty places,
  maps, people grieving. Do not render hate symbols; use plain colours for flags and banners.
  Show real perpetrators small and distant, never heroic.
- No real person's likeness, no brand logos or mascots.
- Keep the style: flat shading, soft shadows, warm haze outdoors, deep navy for night and space,
  gold for the counter prefix, coral for alarm states.
