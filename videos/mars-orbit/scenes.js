// Orbit 2D Space Video Scenes — "What Would Kill You First On Mars?"
// Registered asynchronously with assets loaded cleanly by orbit.js

(async function () {
  const manifestResp = await fetch('/assets/nasa_manifest.json').catch(() => null);
  const manifest = manifestResp && manifestResp.ok ? await manifestResp.json() : [];
  const byKey = Object.fromEntries(manifest.map((m) => [m.key, m]));

  const creditOf = (k, fallback) => (byKey[k] && byKey[k].credit) ? `${byKey[k].credit} (${byKey[k].nasa_id})` : fallback;

  // Frame-accurate beat-aligned durations summing to 144.475s (beats.json total)
  const scenes = [
    // Beat 0 (0.00 -> 10.069s)
    {
      dur: 4.200,
      type: 'orbit_establish',
      planet: 'mars',
      title: 'MARS',
      subtitle: '4TH PLANET FROM THE SUN',
      bottomWhite: 'JUST A COLD',
      bottomYellow: 'DESERT',
      stamp: 'THE RULE',
      showYouArrow: true,
      planetX: 1380,
      planetY: 545,
      planetR: 465,
      astroX: 485,
      astroY: 645,
      zoomAmt: 0.04,
    },
    {
      dur: 5.869,
      type: 'planet_compare',
      title: 'DESERTS DON’T KILL ASTRONAUTS — THAT’S THE RULE',
      leftPlanet: 'earth',
      rightPlanet: 'mars',
      leftLabel: 'EARTH',
      rightLabel: 'MARS',
      leftMetric: '1,013 mbar · THICK AIR',
      rightMetric: '6 mbar · 53% EARTH RADIUS',
    },
    // Beat 1 (10.069 -> 14.324s)
    {
      dur: 4.255,
      type: 'orbit_establish',
      planet: 'mars',
      horizonMode: true,
      topHeadline: 'WHAT KILLS YOU FIRST?',
      bottomWhite: 'YOUR TONGUE STARTS TO',
      bottomYellow: 'FIZZ',
      zoomAmt: 0.055,
    },
    // Beat 2 (14.324 -> 16.117s)
    {
      dur: 1.793,
      type: 'killer_card',
      eyebrow: 'KILLER #1',
      title: 'THE THIN AIR',
    },
    // Beat 3 (16.117 -> 30.393s)
    {
      dur: 14.276,
      type: 'surface_gauge',
      palette: 'day',
      widget: 'gauge',
      fromMbar: 1013,
      toMbar: 6,
      warningTop: 'WATER BOILS AT 37°C',
      warningSub: 'YOUR EXACT BODY TEMPERATURE',
    },
    // Beat 4 (30.393 -> 40.007s)
    {
      dur: 6.200,
      type: 'xray',
      header: 'REMEMBER THAT FIZZ?',
      hotspot: 'mouth',
      calloutLabel: 'SALIVA: BOILING',
    },
    {
      dur: 3.414,
      type: 'xray',
      header: 'REMEMBER THAT FIZZ?',
      hotspot: 'mouth',
      calloutLabel: 'SALIVA: BOILING',
      receipt: {
        header: 'MARS SODA CO.',
        lines: [
          ['SALIVA', '$0'],
          ['BUBBLES', '$0'],
          ['AIR PRESSURE', '$0'],
        ],
        total: 'YOU',
        stamp: 'CARBONATED',
      },
    },
    // Beat 5 (40.007 -> 43.509s)
    {
      dur: 3.502,
      type: 'killer_card',
      eyebrow: 'KILLER #2',
      title: 'THE COLD',
      statusPill: 'SUIT: PATCHED ✓',
    },
    // Beat 6 (43.509 -> 57.851s)
    {
      dur: 14.342,
      type: 'surface_gauge',
      palette: 'cold',
      widget: 'thermometer',
      tempAvg: '-60°C',
      tempAvgSub: 'AVERAGE SURFACE TEMPERATURE',
      tempPole: '-125°C',
      tempPoleSub: 'POLES IN WINTER  (COLDER THAN ANTARCTICA)',
    },
    // Beat 7 (57.851 -> 62.448s)
    {
      dur: 4.597,
      type: 'killer_card',
      eyebrow: 'KILLER #3',
      title: 'TOXIC DUST',
      statusPill: 'HEATER: ON ✓',
    },
    // Beat 8 (62.448 -> 78.242s)
    {
      dur: 11.400,
      type: 'evidence',
      palette: 'day',
      imgKey: 'phoenix_scoop',
      topTag: 'PHOENIX LANDER · 2008 · MARTIAN SOIL IN ITS SCOOP',
      credit: creditOf('phoenix_scoop', 'NASA/JPL-Caltech/University of Arizona'),
      tiltDeg: -1.4,
    },
    {
      dur: 4.394,
      type: 'surface_gauge',
      palette: 'day',
      widget: 'notice',
      astroX: 430,
    },
    // Beat 9 (78.242 -> 83.560s)
    {
      dur: 5.318,
      type: 'killer_card',
      eyebrow: 'KILLER #4',
      title: 'RADIATION',
      statusPill: 'AIRLOCK: SEALED ✓',
    },
    // Beat 10 (83.560 -> 96.872s)
    {
      dur: 13.312,
      type: 'xray',
      header: 'CHEST X-RAY ×6 EVERY DAY',
      hotspot: 'chest',
      calloutLabel: 'NO MAGNETIC FIELD',
      rightCards: [
        { big: '0.64 mSv/day', sub: 'NASA CURIOSITY RAD MEASUREMENT' },
        { big: '6 CHEST X-RAYS', sub: 'EQUIVALENT DOSE EVERY 24H' },
      ],
    },
    // Beat 11 (96.872 -> 112.296s)
    {
      dur: 15.424,
      type: 'evidence',
      palette: 'day',
      imgKey: 'opportunity_rover',
      imgZoom: 1.24,
      topTag: 'OPPORTUNITY · 2004–2018 · SOLAR PANELS BURIED IN DUST',
      credit: creditOf('opportunity_rover', 'NASA/JPL-Caltech/Cornell'),
      tiltDeg: 1.1,
      counters: [
        { big: '90', unit: 'days', label: 'BUILT TO LAST' },
        { big: '14.4', unit: 'years', label: 'ACTUALLY LASTED' },
      ],
    },
    // Beat 12 (112.296 -> 126.790s)
    {
      dur: 8.050,
      type: 'surface_gauge',
      palette: 'day',
      widget: 'delay',
      astroX: 980,
      options: [
        { q: 'HOLD YOUR BREATH?', a: 'LUNGS RUPTURE IN SECONDS' },
        { q: 'DIG UNDERGROUND?', a: 'FROZEN ROCK + PERCHLORATES' },
        { q: 'CALL FOR HELP?', a: 'UP TO 22 MIN ONE-WAY DELAY' },
      ],
    },
    {
      dur: 6.444,
      type: 'evidence',
      palette: 'cold',
      imgKey: 'mars_globe',
      imgZoom: 1.0,
      topTag: 'UP TO 401 MILLION KM BETWEEN MARS & EARTH',
      credit: creditOf('mars_globe', 'NASA/JPL/MSSS'),
      tiltDeg: -0.9,
    },
    // Beat 13 (126.790 -> 139.154s)
    {
      dur: 5.800,
      type: 'evidence',
      palette: 'cold',
      imgKey: 'alba_mons',
      imgZoom: 1.26,
      topTag: 'ALBA MONS · TECTONIC FRACTURES & POSSIBLE MELT',
      credit: creditOf('alba_mons', 'NASA/JPL-Caltech/ASU'),
      tiltDeg: 1.2,
    },
    {
      dur: 6.564,
      type: 'magma_twist',
      depthLabel: '8+ KM · SILICATE MELT?',
      badgeText: 'ALBA MONS MAGMA · UNPROVEN (HYPOTHESIS)',
      bottomWhite: 'DEEP LIQUID WATER:',
      bottomYellow: 'POSSIBLE, NOT FOUND',
    },
    // Beat 14 (139.154 -> 144.475s)
    {
      dur: 5.321,
      type: 'orbit_establish',
      planet: 'mars',
      title: 'MARS',
      subtitle: 'AVERAGE DEATH TIME WITHOUT A SUIT: ~90 SECONDS',
      bottomWhite: 'THE DESERT DOESN’T KILL YOU.',
      bottomYellow: 'EVERYTHING ELSE DOES.',
      showYouArrow: true,
      planetX: 1380,
      planetY: 525,
      planetR: 440,
      astroX: 470,
      astroY: 625,
      zoomAmt: -0.025,
    },
  ];

  await window.ORBIT.register({
    scenes,
    assets: {
      phoenix_scoop: '/assets/phoenix_scoop.jpg',
      opportunity_rover: '/assets/opportunity_rover.jpg',
      alba_mons: '/assets/alba_mons.jpg',
      cerberus_fossae: '/assets/cerberus_fossae.jpg',
      mars_globe: '/assets/mars_globe.jpg',
    },
  });
})();
