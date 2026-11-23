// Orbit 2D Space Short — Next-Gen Black Hole (Minimal Text + Rapid Camera Cuts)
// Native 1080x1920 @ 30fps, synchronized to beats.json (52.868s)

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
    { dur: 4.667, type: 'bh_establish' },
    { dur: 3.351, type: 'bh_establish', tidalMode: true },
    { dur: 2.297, type: 'killer_card', eyebrow: 'KILLER #1', title: 'NOODLED' },
    { dur: 3.650, type: 'surface_gauge', widget: 'gauge' },
    {
      dur: 3.643,
      type: 'xray',
      receipt: {
        header: 'GRAVITY RECEIPT',
        lines: [
          ['BOOTS', '1,000,000 G'],
          ['HELMET', '100 G'],
          ['TIME', '0.08 SEC'],
        ],
        stamp: 'NOODLED',
      },
    },
    {
      dur: 3.809,
      type: 'evidence',
      imgKey: 'sgra_center',
      credit: creditOf('sgra_center', 'NASA/JPL-Caltech (PIA25440)'),
    },
    { dur: 2.312, type: 'killer_card', eyebrow: 'KILLER #2', title: 'TIME BREAKS' },
    { dur: 6.222, type: 'surface_gauge', widget: 'time_dilation' },
    {
      dur: 5.047,
      type: 'evidence',
      imgKey: 'm87_jet',
      credit: creditOf('m87_jet', 'NASA/JPL-Caltech/Chandra (PIA20865)'),
    },
    { dur: 6.021, type: 'surface_gauge', widget: 'escape_speed' },
    {
      dur: 4.593,
      type: 'evidence',
      imgKey: 'm87_eht',
      credit: creditOf('m87_eht', 'NASA/JPL-Caltech/EHT (PIA23122)'),
    },
    { dur: 7.256, type: 'm87_twist' },
  ];

  await window.ORBIT.register({
    scenes,
    beats: beatsData.beats || [],
    assets: {
      m87_eht: '/assets/m87_eht.jpg',
      m87_jet: '/assets/m87_jet.jpg',
      sgra_center: '/assets/sgra_center.jpg',
    },
  });
})();
