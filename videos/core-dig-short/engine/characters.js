/* Countryball-style 8-bit Character Renderer (NO MOUTH, Skin Tones + Clothes + Accessories)
 * Logical 180x320 pixel canvas.
 */
window.CHARS = (() => {
  const { pctx, px, rect, disk, glowOrb, pixelText } = window.PX;
  const OUTLINE = '#181124';

  const SKINS = {
    host:     { hi: '#fde2c4', lit: '#f2c29b', shade: '#ce9268' },
    mrbeast:  { hi: '#fde5cc', lit: '#f5cba7', shade: '#d49d74' },
    mc:       { hi: '#f3caa0', lit: '#db9f67', shade: '#b3743f' },
    rat:      { hi: '#cbd5e1', lit: '#9ca3af', shade: '#64748b' },
    guardian: { hi: '#fed7aa', lit: '#fb923c', shade: '#c2410c' },
  };

  function bayerPick(x, y, colA, colB, thr = 2) {
    const b = ((y & 1) << 1) | ((x ^ y) & 1);
    return b < thr ? colB : colA;
  }

  function drawOutfitPixel(outfit, dx, dy, R, x, y, opts) {
    // Only cover lower hemisphere (dy > R * 0.22)
    if (dy <= R * 0.20) return null;
    const shade = dx > R * 0.18 || dy > R * 0.68;

    if (outfit === 'host_hoodie') {
      // Drawstrings + yellow $ badge
      if (Math.abs(dx + 3) <= 0 && dy > R * 0.24 && dy < R * 0.65) return '#f8fafc';
      if (Math.abs(dx - 3) <= 0 && dy > R * 0.24 && dy < R * 0.65) return '#f8fafc';
      if (Math.abs(dx) <= 1 && dy >= R * 0.22 && dy <= R * 0.34) return '#1e1b2e';
      if (dx >= -2 && dx <= 2 && dy >= R * 0.48 && dy <= R * 0.72) {
        if ((Math.abs(dx) <= 1 && (dy === Math.round(R * 0.5) || dy === Math.round(R * 0.6))) || dx === 0) {
          return '#facc15';
        }
      }
      return shade ? '#9f1239' : '#e11d48';
    }

    if (outfit === 'host_parka') {
      if (dy <= R * 0.35) return bayerPick(x, y, '#f1f5f9', '#cbd5e1', 1); // fur trim
      if (Math.abs(dx) <= 0) return '#94a3b8'; // zipper
      return shade ? '#172554' : '#1e40af';
    }

    if (outfit === 'mrbeast_hoodie') {
      // Iconic cyan & pink chest logo
      if (dy >= R * 0.40 && dy <= R * 0.76 && Math.abs(dx) <= R * 0.34) {
        if (dx < 0 && dy < R * 0.62) return '#22d3ee';
        if (dx >= 0 && dy >= R * 0.48) return '#ec4899';
      }
      return shade ? '#0f172a' : '#27272a';
    }

    if (outfit === 'mc_hoodie') {
      if (opts.singed && ((dx * 7 + dy * 13) & 7) === 0) return '#27272a';
      if (opts.icy && dy > R * 0.72 && ((dx + dy) & 1) === 0) return '#bae6fd';
      if (Math.abs(dx + 3) <= 0 && dy > R * 0.24 && dy < R * 0.62) return '#f8fafc';
      if (Math.abs(dx - 3) <= 0 && dy > R * 0.24 && dy < R * 0.62) return '#f8fafc';
      return shade ? '#15803d' : '#22c55e';
    }

    if (outfit === 'rat_cape') {
      if (dy <= R * 0.34) {
        return (Math.abs(dx) % 4 === 0) ? '#1e293b' : '#f8fafc';
      }
      return shade ? '#7f1d1d' : '#dc2626';
    }

    if (outfit === 'guardian_robe') {
      if (Math.abs(dx) <= 1) return '#fbbf24';
      return ((dx + 20) & 3) < 2 ? '#1e3a8a' : '#3b82f6';
    }

    return null;
  }

  function drawEyes(cx, cy, R, expr, lookX = 0, lookY = 0) {
    const sep = Math.max(4, Math.round(R * 0.36));
    const ey = Math.round(cy - R * 0.06);
    const ew = Math.max(4, Math.round(R * 0.30));
    const eh = Math.max(4, Math.round(R * 0.28));

    for (const side of [-1, 1]) {
      const ex = Math.round(cx + side * sep);

      if (expr === 'blink') {
        rect(ex - Math.floor(ew / 2), ey, ew, 1, OUTLINE);
        continue;
      }

      if (expr === 'sleepy') {
        // Curved shut eye U
        rect(ex - Math.floor(ew / 2), ey, ew, 1, OUTLINE);
        px(ex - Math.floor(ew / 2), ey - 1, OUTLINE);
        px(ex + Math.floor(ew / 2) - 1, ey - 1, OUTLINE);
        continue;
      }

      if (expr === 'shiver') {
        // > < squeezed eyes
        if (side === -1) {
          px(ex - 2, ey - 2, OUTLINE); px(ex, ey - 1, OUTLINE);
          px(ex + 1, ey, OUTLINE);
          px(ex, ey + 1, OUTLINE); px(ex - 2, ey + 2, OUTLINE);
        } else {
          px(ex + 2, ey - 2, OUTLINE); px(ex, ey - 1, OUTLINE);
          px(ex - 1, ey, OUTLINE);
          px(ex, ey + 1, OUTLINE); px(ex + 2, ey + 2, OUTLINE);
        }
        continue;
      }

      // White eye box with 1px dark outline (classic Countryball oval)
      const h = expr === 'wide' ? eh + 2 : expr === 'squint' ? Math.max(3, eh - 2) : eh;
      const w = expr === 'wide' ? ew + 1 : ew;
      const x0 = ex - Math.floor(w / 2);
      const y0 = ey - Math.floor(h / 2);

      // Outline
      rect(x0 - 1, y0, w + 2, h, OUTLINE);
      rect(x0, y0 - 1, w, h + 2, OUTLINE);
      // White fill
      rect(x0, y0, w, h, '#ffffff');

      if (expr === 'dollar') {
        // Green $ inside white eyes
        rect(ex - 1, ey - 2, 3, 1, '#16a34a');
        px(ex - 1, ey - 1, '#16a34a');
        rect(ex - 1, ey, 3, 1, '#16a34a');
        px(ex + 1, ey + 1, '#16a34a');
        rect(ex - 1, ey + 2, 3, 1, '#16a34a');
        px(ex, ey - 3, '#16a34a');
        px(ex, ey + 3, '#16a34a');
      } else {
        // Crisp 2x2 pupil (or 1x1 pinpoint when wide/shocked)
        const ps = expr === 'wide' ? 1 : 2;
        const pxOff = Math.max(-1, Math.min(1, Math.round(lookX)));
        const pyOff = Math.max(-1, Math.min(1, Math.round(lookY)));
        rect(ex + pxOff - (ps > 1 ? 1 : 0), ey + pyOff, ps, ps, OUTLINE);
      }

      // Angry slanted brow cut
      if (expr === 'angry') {
        for (let k = -1; k <= w; k++) {
          const by = side === -1 ? (y0 - 1 + Math.floor(k * 0.45)) : (y0 - 1 + Math.floor((w - 1 - k) * 0.45));
          rect(x0 + k, by - 2, 1, 2, OUTLINE);
        }
      } else if (expr === 'squint') {
        rect(x0 - 1, y0 - 1, w + 2, 2, OUTLINE);
      }
    }
  }

  function drawHeadwear(cx, cy, R, hat) {
    if (!hat) return;
    if (hat === 'host_cap') {
      // Backwards red cap
      const top = Math.round(cy - R - 2);
      rect(cx - Math.round(R * 0.7), top, Math.round(R * 1.4), 5, '#ef4444');
      rect(cx - Math.round(R * 0.6), top - 1, Math.round(R * 1.2), 2, '#dc2626');
      // Backwards brim sticking left
      rect(cx - Math.round(R * 1.15), top + 3, Math.round(R * 0.6), 3, '#991b1b');
      // Outline top
      rect(cx - Math.round(R * 0.6), top - 2, Math.round(R * 1.2), 1, OUTLINE);
    } else if (hat === 'mrbeast_hair') {
      const top = Math.round(cy - R - 1);
      rect(cx - Math.round(R * 0.72), top, Math.round(R * 1.44), 5, '#6b4423');
      rect(cx - Math.round(R * 0.5), top - 2, Math.round(R * 1.0), 3, '#543318');
      px(cx + 2, top + 4, '#6b4423');
      px(cx - 3, top + 4, '#6b4423');
    } else if (hat === 'mc_hair') {
      const top = Math.round(cy - R - 2);
      rect(cx - Math.round(R * 0.65), top + 1, Math.round(R * 1.3), 4, '#3b2314');
      // Messy spiky tufts
      rect(cx - 5, top - 2, 3, 3, '#3b2314');
      rect(cx + 1, top - 3, 3, 4, '#4e2f1b');
      rect(cx + 5, top - 1, 3, 2, '#3b2314');
    } else if (hat === 'dino_skull') {
      // T-Rex bone skull helmet perched above eyes!
      const sy = Math.round(cy - R - 5);
      const sw = Math.round(R * 1.5);
      rect(cx - Math.round(sw * 0.45), sy, sw, 8, '#fef3c7');
      rect(cx - Math.round(sw * 0.35), sy - 2, Math.round(sw * 0.8), 3, '#fde68a');
      // Hollow dark dino eye socket
      rect(cx - 3, sy + 2, 4, 3, OUTLINE);
      // Nostril
      px(cx + Math.round(sw * 0.45), sy + 2, OUTLINE);
      // Jagged teeth overhang
      for (let tx = cx - 4; tx <= cx + Math.round(sw * 0.45); tx += 3) {
        rect(tx, sy + 8, 2, 2, '#fef3c7');
        px(tx, sy + 10, OUTLINE);
      }
      // Top outline
      rect(cx - Math.round(sw * 0.35), sy - 3, Math.round(sw * 0.8), 1, OUTLINE);
    } else if (hat === 'rat_crown') {
      // Mouse ears
      disk(cx - Math.round(R * 0.68), cy - Math.round(R * 0.72), 5, OUTLINE);
      disk(cx - Math.round(R * 0.68), cy - Math.round(R * 0.72), 4, '#9ca3af');
      disk(cx - Math.round(R * 0.68), cy - Math.round(R * 0.72), 2, '#f472b6');

      disk(cx + Math.round(R * 0.68), cy - Math.round(R * 0.72), 5, OUTLINE);
      disk(cx + Math.round(R * 0.68), cy - Math.round(R * 0.72), 4, '#9ca3af');
      disk(cx + Math.round(R * 0.68), cy - Math.round(R * 0.72), 2, '#f472b6');

      // Tiny gold 3-point crown
      const ky = Math.round(cy - R - 5);
      rect(cx - 5, ky + 3, 11, 3, '#facc15');
      rect(cx - 5, ky, 2, 3, '#facc15');
      rect(cx - 1, ky - 1, 3, 4, '#fde047');
      rect(cx + 4, ky, 2, 3, '#facc15');
      px(cx, ky + 4, '#ef4444'); // ruby gem
    } else if (hat === 'nightcap') {
      const ny = Math.round(cy - R - 4);
      rect(cx - Math.round(R * 0.6), ny + 2, Math.round(R * 1.2), 4, '#1e3a8a');
      rect(cx - Math.round(R * 0.4), ny - 1, Math.round(R * 0.8), 3, '#3b82f6');
      rect(cx + Math.round(R * 0.3), ny + 1, 5, 4, '#1e3a8a');
      disk(cx + Math.round(R * 0.75), ny + 4, 2, '#f8fafc');
    }
  }

  function drawProp(prop, pxX, pxY, t = 0) {
    if (!prop) return;
    const x = Math.round(pxX);
    const y = Math.round(pxY + Math.sin(t * 5) * 1.0);

    if (prop === 'cash_1k' || prop === 'cash_2k') {
      const count = prop === 'cash_2k' ? 2 : 1;
      for (let i = 0; i < count; i++) {
        const bx = x + i * 2, by = y - i * 3;
        rect(bx - 1, by - 1, 14, 9, OUTLINE);
        rect(bx, by, 12, 7, '#22c55e');
        rect(bx + 1, by + 1, 10, 5, '#15803d');
        pixelText(prop === 'cash_2k' ? '$2K' : '$1K', bx + 6, by - 7, '#4ade80', '#062812', 'center');
      }
    } else if (prop === 'shovel') {
      // Tiny yellow beach shovel
      rect(x - 1, y - 10, 3, 12, OUTLINE);
      rect(x, y - 9, 1, 10, '#facc15');
      rect(x - 2, y - 11, 5, 2, '#eab308');
      rect(x - 3, y + 1, 7, 6, OUTLINE);
      rect(x - 2, y + 2, 5, 4, '#facc15');
      rect(x - 1, y + 6, 3, 2, '#eab308');
    } else if (prop === 'melted_shovel') {
      // Dripping melted yellow/orange puddle!
      rect(x - 3, y + 4, 9, 3, '#facc15');
      rect(x - 1, y + 7, 5, 2, '#f97316');
      px(x + 1, y + 1 + ((Math.floor(t * 8)) % 4), '#fde047');
    } else if (prop === 'pizza') {
      // Pixel pizza slice
      rect(x - 1, y - 1, 10, 3, '#d97706'); // crust
      rect(x, y + 2, 8, 2, '#facc15');
      rect(x + 1, y + 4, 6, 2, '#facc15');
      rect(x + 2, y + 6, 4, 2, '#eab308');
      rect(x + 3, y + 8, 2, 1, '#eab308');
      px(x + 2, y + 3, '#ef4444');
      px(x + 5, y + 4, '#ef4444');
    } else if (prop === 'ice_core') {
      glowOrb(x + 3, y + 3, 5, '#e0f2fe', '#38bdf8', '#0284c7');
      rect(x, y, 7, 7, '#38bdf8');
      rect(x + 1, y + 1, 5, 5, '#7dd3fc');
      px(x + 2, y + 2, '#ffffff');
    }
  }

  function drawBall(opts) {
    const {
      role = 'mc',
      cx = 90,
      cy = 180,
      R = 20,
      expr = 'normal',
      lookX = 0,
      lookY = 0,
      isTalking = false,
      t = 0,
      outfit = null,
      hat = null,
      prop = null,
      propSide = 1,
      sweat = false,
      singed = false,
      icy = false,
      glasses = false,
    } = opts;

    const skin = SKINS[role] || SKINS.mc;

    // Squash & stretch talk bounce (no mouth!)
    let sy = 1, sx = 1, bobY = 0;
    if (isTalking) {
      const pulse = Math.abs(Math.sin(t * 28));
      sy = 1 + 0.08 * pulse;
      sx = 1 / sy;
      bobY = -Math.round(pulse * 2.0);
    }

    const rX = Math.round(R * sx);
    const rY = Math.round(R * sy);
    const by = Math.round(cy + bobY);
    const bx = Math.round(cx);

    // Subtle ground shadow ellipse underneath
    pctx.fillStyle = 'rgba(8, 6, 18, 0.45)';
    for (let dx = -Math.round(rX * 0.85); dx <= Math.round(rX * 0.85); dx++) {
      for (let dy = -2; dy <= 2; dy++) {
        if ((dx * dx) / (rX * rX * 0.72) + (dy * dy) / 4 <= 1) {
          pctx.fillRect(bx + dx, Math.round(cy + R + 1 + dy), 1, 1);
        }
      }
    }

    // Draw sphere pixel by pixel with 1px dark plum-navy outline & Bayer dithered shading
    for (let dy = -rY - 1; dy <= rY + 1; dy++) {
      for (let dx = -rX - 1; dx <= rX + 1; dx++) {
        const nx = dx / rX;
        const ny = dy / rY;
        const d2 = nx * nx + ny * ny;

        if (d2 > 1.12) continue;
        if (d2 > 0.96) {
          px(bx + dx, by + dy, OUTLINE);
          continue;
        }

        const x = bx + dx;
        const y = by + dy;

        // Check clothing lower hemisphere
        const clothCol = outfit ? drawOutfitPixel(outfit, dx, dy, rY, x, y, { singed, icy }) : null;
        if (clothCol) {
          px(x, y, clothCol);
          continue;
        }

        // Guardian fluffy white beard (no mouth!)
        if (role === 'guardian' && dy > rY * 0.20) {
          px(x, y, bayerPick(x, y, '#f8fafc', '#cbd5e1', 1));
          continue;
        }

        // Lighting
        const light = -0.55 * nx - 0.65 * ny;
        let col = skin.lit;
        if (light > 0.56) col = skin.hi;
        else if (light > 0.05) col = skin.lit;
        else if (light > -0.32) col = bayerPick(x, y, skin.lit, skin.shade, 2);
        else col = skin.shade;

        if (icy && ny < -0.55 && ((x + y) & 1) === 0) col = '#bae6fd';
        if (singed && ((dx === -6 && dy === -2) || (dx === 7 && dy === -3) || (dx === 5 && dy === 2))) col = '#3f3f46';

        px(x, y, col);
      }
    }

    // Specular 2px highlight upper-left
    px(bx - Math.round(rX * 0.45), by - Math.round(rY * 0.48), '#ffffff');
    px(bx - Math.round(rX * 0.38), by - Math.round(rY * 0.54), '#ffffff');

    // MrBeast subtle goatee/mustache pixels (no mouth)
    if (role === 'mrbeast') {
      const gy = by + Math.round(rY * 0.16);
      rect(bx - 4, gy, 9, 1, '#5c3a21');
      rect(bx - 2, gy + 2, 5, 2, '#5c3a21');
    }

    // Rat King pink whiskers
    if (role === 'rat') {
      for (const s of [-1, 1]) {
        rect(bx + s * Math.round(rX * 0.52), by + 1, 3, 1, '#f472b6');
        rect(bx + s * Math.round(rX * 0.55), by + 3, 3, 1, '#f472b6');
      }
    }

    // Countryball Eyes
    drawEyes(bx, by, Math.min(rX, rY), expr, lookX, lookY);

    // Optional round silver glasses (Core Guardian)
    if (glasses) {
      const sep = Math.max(4, Math.round(rX * 0.36));
      for (const s of [-1, 1]) {
        const ex = bx + s * sep;
        const ey = Math.round(by - rY * 0.06);
        rect(ex - 4, ey - 3, 8, 1, '#e2e8f0');
        rect(ex - 4, ey + 3, 8, 1, '#e2e8f0');
        rect(ex - 4, ey - 2, 1, 5, '#e2e8f0');
        rect(ex + 3, ey - 2, 1, 5, '#e2e8f0');
      }
      rect(bx - 1, Math.round(by - rY * 0.06), 3, 1, '#e2e8f0');
    }

    // Sweat drop
    if (sweat) {
      const sxp = bx + Math.round(rX * 0.65);
      const syp = by - Math.round(rY * 0.40) + Math.round((t * 12) % 4);
      px(sxp, syp - 1, '#e0f2fe');
      rect(sxp - 1, syp, 3, 2, '#38bdf8');
      px(sxp, syp + 2, '#0284c7');
    }

    // Headwear
    drawHeadwear(bx, by, rY, hat);

    // Floating prop
    if (prop) {
      drawProp(prop, bx + propSide * (rX + 10) - (propSide < 0 ? 10 : 0), by - 2, t);
    }
  }

  return { drawBall };
})();
