// Orbit 2D Space Short — "What Would Actually Kill You First on Venus?"
// Native 1080x1920 @ 30fps, synchronized to beats.json (47.782s)

(async function () {
  const [manifestResp, beatsResp] = await Promise.all([
    fetch('/assets/nasa_manifest.json').catch(() => null),
    fetch('/beats.json').catch(() => null),
  ]);
  const manifest = manifestResp && manifestResp.ok ? await manifestResp.json() : [];
  const beatsData = beatsResp && beatsResp.ok ? await beatsResp.json() : { beats: [] };
  const byKey = Object.fromEntries(manifest.map((m) => [m.key, m]));
  const creditOf = (k, fallback) => (byKey[k] && byKey[k].credit) ? `${byKey[k].credit} (${byKey[k].nasa_id})` : fallback;
  const words = (beatsData.beats || []).flatMap((b) => b.words || []);

  const scenes = [
    // Beat 0: 0.000 -> 5.569
    {
      dur: 5.569,
      type: 'orbit_establish',
      planet: 'venus',
      title: 'VENUS',
      subtitle: 'EARTH’S TWIN SISTER · 2ND FROM THE SUN',
      bottomWhite: 'JUST A WARM',
      bottomYellow: 'GETAWAY',
      stamp: 'THE RULE',
      showYouArrow: true,
      zoomAmt: 0.045,
    },
    // Beat 1: 5.569 -> 8.760
    {
      dur: 3.191,
      type: 'orbit_establish',
      planet: 'venus',
      horizonMode: true,
      topHeadline: 'THEN YOUR SUIT IMPLODES',
      subPill: '0.5 SECOND COLLAPSE',
      crush: true,
      bottomWhite: 'LIKE A SODA CAN',
      bottomYellow: 'IN HALF A SECOND',
      zoomAmt: 0.06,
    },
    // Beat 2: 8.760 -> 10.502
    {
      dur: 1.742,
      type: 'killer_card',
      eyebrow: 'KILLER #1',
      title: 'THE CRUSH',
      sub: '92 BAR PRESSURE',
    },
    // Beat 3: 10.502 -> 16.139
    {
      dur: 5.637,
      type: 'surface_gauge',
      palette: 'day',
      widget: 'gauge',
      fromBar: 1,
      toBar: 92,
      warningTop: '92× EARTH · LIKE 900m UNDERWATER',
      bottomWhite: 'NO SUBMARINE.',
      bottomYellow: 'JUST YOU.',
    },
    // Beat 4: 16.139 -> 19.333
    {
      dur: 3.194,
      type: 'xray',
      header: 'INSTANT IMPLOSION',
      calloutLabel: 'HELMET: CRUSHED INWARD',
      receipt: {
        header: 'VENUS PRESSURE CO.',
        lines: [
          ['TITANIUM HELMET', 'FOLDED'],
          ['OCEAN EQUIV.', '900 METERS'],
          ['AIR PRESSURE', '92 BAR'],
        ],
        total: '0.5 SEC',
        stamp: 'CRUSHED',
      },
    },
    // Beat 5: 19.333 -> 22.627
    {
      dur: 3.294,
      type: 'killer_card',
      eyebrow: 'KILLER #2',
      title: '465°C OVEN',
      sub: 'HOTTER THAN MERCURY',
    },
    // Beat 6: 22.627 -> 28.211
    {
      dur: 5.584,
      type: 'surface_gauge',
      palette: 'hot',
      widget: 'thermometer',
      walk: true,
      bottomWhite: 'HOT ENOUGH TO',
      bottomYellow: 'MELT LEAD AT YOUR BOOTS',
    },
    // Beat 7A: 28.211 -> 31.400
    {
      dur: 3.189,
      type: 'evidence',
      palette: 'day',
      imgKey: 'venus_clouds',
      topTag: 'NASA MARINER 10 · SULFURIC ACID CLOUDS',
      badgeTop: 'CLOUD DECK: CONCENTRATED H₂SO₄',
      credit: creditOf('venus_clouds', 'NASA/JPL-Caltech (PIA00072)'),
      bottomWhite: 'SULFURIC ACID',
      bottomYellow: 'CLOUDS ABOVE',
    },
    // Beat 7B: 31.400 -> 34.561
    {
      dur: 3.161,
      type: 'evidence',
      palette: 'hot',
      imgKey: 'venus_volcano',
      topTag: 'NASA MAGELLAN RADAR · USHAS MONS VOLCANO',
      badgeTop: 'ACID RAIN BOILS MID-AIR BEFORE LANDING',
      credit: creditOf('venus_volcano', 'NASA/JPL (PIA00272)'),
      bottomWhite: 'ACID RAIN:',
      bottomYellow: 'CANCELLED BY HEAT',
    },
    // Beat 8: 34.561 -> 37.520
    {
      dur: 2.959,
      type: 'evidence',
      palette: 'hot',
      imgKey: 'venus_magellan',
      topTag: 'WHAT CAN YOU DO? · DIG A BUNKER?',
      badgeTop: 'SURFACE ROCKS GLOW AT 465°C',
      credit: creditOf('venus_magellan', 'NASA/JPL (PIA00478)'),
      bottomWhite: 'DIG A BUNKER?',
      bottomYellow: 'THE ROCKS GLOW',
    },
    // Beat 9: 37.520 -> 42.108
    {
      dur: 4.588,
      type: 'surface_gauge',
      palette: 'hot',
      widget: 'bunker_radio',
      cardTop: 'CALL EARTH FOR RESCUE?',
      midStat: '15 MIN SIGNAL DELAY',
      bottomTag: 'PHONE MELTED IN 0.4 SECONDS',
      bottomWhite: 'NOBODY HEARS YOU',
      bottomYellow: 'FOR 15 MINUTES',
    },
    // Beat 10: 42.108 -> 47.782
    {
      dur: 5.674,
      type: 'cloud_twist',
      bottomWhite: 'ROOM TEMP CLOUDS.',
      bottomYellow: 'BATTERY ACID AIR.',
    },
  ];

  await window.ORBIT.register({
    scenes,
    words,
    assets: {
      venus_magellan: '/assets/venus_magellan.jpg',
      venus_clouds: '/assets/venus_clouds.jpg',
      venus_volcano: '/assets/venus_volcano.jpg',
    },
  });
})();
