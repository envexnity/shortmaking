// Orbit 2D Space Short — Next-Gen Asteroid Apophis 2029 (Minimal Text + Rapid Camera Cuts)
// Native 1080x1920 @ 30fps, synchronized to beats.json (55.722s)

(async function () {
  const [manifestResp, beatsResp] = await Promise.all([
    fetch('/assets/nasa_manifest.json').catch(() => null),
    fetch('/beats.json').catch(() => null),
  ]);
  const manifest = manifestResp && manifestResp.ok ? await manifestResp.json() : [];
  const beatsData = beatsResp && beatsResp.ok ? await beatsResp.json() : { beats: [] };
  const byKey = Object.fromEntries(manifest.map((m) => [m.key, m]));
  const creditOf = (k, fallback) => (byKey[k] && byKey[k].credit) ? `${byKey[k].credit} (${byKey[k].nasa_id})` : fallback;

  const scenes = [
    { dur: 6.968, type: 'apophis_flyby' },
    { dur: 4.489, type: 'nuke_rule' },
    { dur: 4.013, type: 'shotgun_blast' },
    { dur: 2.104, type: 'killer_card', eyebrow: 'KILLER #1', title: 'SHOTGUN' },
    {
      dur: 6.844,
      type: 'evidence',
      palette: 'day',
      imgKey: 'bennu_rubble',
      credit: creditOf('bennu_rubble', 'NASA/Goddard/UArizona (PIA23555)'),
    },
    {
      dur: 5.065,
      type: 'xray',
      receipt: {
        header: 'NUKE RECEIPT',
        lines: [
          ['1 ROCK', '10,000'],
          ['SPEED', '20 KM/S'],
          ['TOTAL', 'HITS'],
        ],
        stamp: 'BAD IDEA',
      },
    },
    { dur: 3.462, type: 'killer_card', eyebrow: 'KILLER #2', title: '400°C SKY' },
    { dur: 5.161, type: 'surface_gauge', palette: 'hot', widget: 'thermometer', walk: true },
    {
      dur: 3.885,
      type: 'evidence',
      palette: 'hot',
      imgKey: 'asteroid_crater',
      credit: creditOf('asteroid_crater', 'NASA/GSFC/ASTER (PIA03490)'),
    },
    { dur: 4.799, type: 'surface_gauge', palette: 'day', widget: 'gauge' },
    {
      dur: 4.400,
      type: 'evidence',
      palette: 'day',
      imgKey: 'dart_impact',
      credit: creditOf('dart_impact', 'NASA/STScI Hubble (PIA02122)'),
    },
    { dur: 4.532, type: 'dart_deflect' },
  ];

  await window.ORBIT.register({
    scenes,
    beats: beatsData.beats || [],
    assets: {
      bennu_rubble: '/assets/bennu_rubble.jpg',
      dart_impact: '/assets/dart_impact.jpg',
      asteroid_crater: '/assets/asteroid_crater.jpg',
    },
  });
})();
