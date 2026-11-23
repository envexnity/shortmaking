# Style and shot planning

## The look

- **Geometry**: boxes, cylinders, low-detail icosahedrons. Flat shading. No textures except
  text on signs and boards. Characters are blocky: box torso, tube limbs, round head with a hair
  cap, dot eyes, a line mouth.
- **Light**: one soft sun with soft shadows, hemisphere fill. Warm haze outdoors by day; deep
  navy and blue moonlight at night; near-black with a single key light in space.
- **Palette**: muted, natural colours for the world; the hero keeps one outfit (teal shirt,
  khaki trousers by default) across the whole video so they read instantly. Gold `#e8c56a` for
  the counter prefix and highlights, coral `#ff7a66` for danger or escalation.
- **Overlay**: small-caps label + big serif value top-left; small-caps label + heavy status word
  + small sub-label top-right; italic serif caption bottom centre, two lines; occasional dark
  glass card for numbers, charts or definitions; a big spaced title for chapter moments.
- **Camera**: one clear subject per shot, slow push-ins and drifts, often low and wide. Avoid
  fast spins and shaky moves.

## Choosing the HUD

The HUD tracks the story's escalating quantity. Pick it per topic, keep it stable, and change
the value at the moment the narration does:

| Topic | Left (label: value) | Right (label: status / sub) |
| --- | --- | --- |
| "What if" escalation | YOUR LUCK: ×1 → ×10⁹⁸ | YOU ARE: AVERAGE → UNBEATABLE / DAY 9 |
| Science explainer | SLEEP STAGE: REM, or MOONS: 2 | YOU ARE: DREAMING / 3:12 AM |
| History | YEAR: 1936 | LOCATION: RHINELAND / MARCH 7 |
| Countdown or scale | DISTANCE: 384,400 km | STATUS: ORBITING |

Set `prefix: ''` unless the value is a multiplier. Hide the HUD (`hud: false`) when it would
trivialise the moment.

## Planning shots

- One shot per beat (a sentence or clause), cut in the pause after it. Typical length 2–6 s;
  split anything over ~7 s into two camera setups of the same set.
- Show the literal thing first. "A coin lands on its edge" is a coin landing on its edge.
  Abstract lines become diagrams: a map with arrows, an orbit, a chart card, labelled objects
  popping in as each word is spoken.
- Alternate scale: wide establishing → close detail → diagram → back to the world.
- Reuse a set over consecutive beats, changing the camera and one element each time.
- Lists in the narration ("size, distance, path") get one visual change per item, timed to the
  words, and a status word that follows along.
- Open on a strong image of the premise; give the title card to the beat that names the topic.

## Timing inside a shot

Use the timing table: if a beat runs 22.75–27.81 and the second item is spoken around 24.7,
trigger it at `t = 24.7 - 22.75 ≈ 1.95`. Use `capIn: .08, capOut: .18` with voiceover so
captions track speech; the defaults (.35) suit silent videos.

## QC checklist (stills sheet)

- Subject visible, lit and centred enough; nothing important cut off by the frame.
- No label colliding with the HUD corners or the caption band (bottom ~18%).
- Night scenes are dark but readable: hills, trees and characters visible against the sky.
- Text on signs reads the right way round (signs facing away from camera show mirrored text).
- Diagram scale works: glowing or transparent overlays do not swallow the subject.
- Things that animate over time (phases, counters, water levels) are computed from `t`, not
  accumulated, or stills will be wrong.
