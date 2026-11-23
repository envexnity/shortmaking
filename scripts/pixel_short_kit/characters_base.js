/* Shared Countryball 8-bit Character Renderer (NO MOUTH, Skin Tones + Clothes + Extensible Hats & Props)
 * Supports registering custom skins, outfits, hats, and props via CHARS.register(...)
 */
window.CHARS = (() => {
  const { pctx, px, rect, line, disk, ellipse, glowOrb, pixelText } = window.PX;
  const OUTLINE = '#181124';

  const SKINS = {
    host:     { hi: '#fde2c4', lit: '#f2c29b', shade: '#ce9268' },
    mrbeast:  { hi: '#fde5cc', lit: '#f5cba7', shade: '#d49d74' },
    mc:       { hi: '#f3caa0', lit: '#db9f67', shade: '#b3743f' },
    trickster:{ hi: '#e9d5ff', lit: '#c084fc', shade: '#7e22ce' },
    sage:     { hi: '#fef08a', lit: '#facc15', shade: '#ca8a04' },
  };

  const CUSTOM_OUTFITS = {};
  const CUSTOM_HATS = {};
  const CUSTOM_PROPS = {};

  function register({ skins = {}, outfits = {}, hats = {}, props = {} }) {
    Object.assign(SKINS, skins);
    Object.assign(CUSTOM_OUTFITS, outfits);
    Object.assign(CUSTOM_HATS, hats);
    Object.assign(CUSTOM_PROPS, props);
  }

  function bayerPick(x, y, colA, colB, thr = 2) {
    const b = ((y & 1) << 1) | ((x ^ y) & 1);
    return b < thr ? colB : colA;
  }

  function drawOutfitPixel(outfit, dx, dy, R, x, y, opts) {
    if (dy <= R * 0.20) return null;
    const shade = dx > R * 0.18 || dy > R * 0.68;

    if (CUSTOM_OUTFITS[outfit]) {
      return CUSTOM_OUTFITS[outfit](dx, dy, R, x, y, shade, opts);
    }

    if (outfit === 'host_hoodie') {
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

    if (outfit === 'mrbeast_hoodie') {
      if (dy >= R * 0.40 && dy <= R * 0.76 && Math.abs(dx) <= R * 0.34) {
        if (dx < 0 && dy < R * 0.62) return '#22d3ee';
        if (dx >= 0 && dy >= R * 0.48) return '#ec4899';
      }
      return shade ? '#0f172a' : '#27272a';
    }

    if (outfit === 'mc_hoodie') {
      if (Math.abs(dx + 3) <= 0 && dy > R * 0.24 && dy < R * 0.62) return '#f8fafc';
      if (Math.abs(dx - 3) <= 0 && dy > R * 0.24 && dy < R * 0.62) return '#f8fafc';
      return shade ? '#15803d' : '#22c55e';
    }

    if (outfit === 'mc_foil') {
      return shade ? '#64748b' : ((x + y) & 1 ? '#cbd5e1' : '#e2e8f0');
    }

    if (outfit === 'sage_robe') {
      if (Math.abs(dx) <= 1) return '#facc15';
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
      if (expr === 'dizzy') {
        line(ex - 2, ey - 2, ex + 2, ey + 2, OUTLINE);
        line(ex - 2, ey + 2, ex + 2, ey - 2, OUTLINE);
        continue;
      }
      if (expr === 'cool_shades') {
        // Dollar-store dark pixel sunglasses!
        rect(ex - 4, ey - 3, 9, 6, '#090d1f');
        rect(ex - 3, ey - 2, 7, 4, '#1e293b');
        px(ex - 2, ey - 1, '#38bdf8');
        px(ex - 1, ey - 2, '#ffffff');
        continue;
      }

      const h = expr === 'wide' ? eh + 2 : expr === 'squint' ? Math.max(3, eh - 2) : eh;
      const w = expr === 'wide' ? ew + 1 : ew;
      const x0 = ex - Math.floor(w / 2);
      const y0 = ey - Math.floor(h / 2);

      rect(x0 - 1, y0, w + 2, h, OUTLINE);
      rect(x0, y0 - 1, w, h + 2, OUTLINE);
      rect(x0, y0, w, h, '#ffffff');

      if (expr === 'dollar') {
        rect(ex - 1, ey - 2, 3, 1, '#16a34a');
        px(ex - 1, ey - 1, '#16a34a');
        rect(ex - 1, ey, 3, 1, '#16a34a');
        px(ex + 1, ey + 1, '#16a34a');
        rect(ex - 1, ey + 2, 3, 1, '#16a34a');
        px(ex, ey - 3, '#16a34a');
        px(ex, ey + 3, '#16a34a');
      } else {
        const ps = expr === 'wide' ? 1 : 2;
        const pxOff = Math.max(-1, Math.min(1, Math.round(lookX)));
        const pyOff = Math.max(-1, Math.min(1, Math.round(lookY)));
        rect(ex + pxOff - (ps > 1 ? 1 : 0), ey + pyOff, ps, ps, OUTLINE);
      }

      if (expr === 'angry') {
        for (let k = -1; k <= w; k++) {
          const by = side === -1 ? (y0 - 1 + Math.floor(k * 0.45)) : (y0 - 1 + Math.floor((w - 1 - k) * 0.45));
          rect(x0 + k, by - 2, 1, 2, OUTLINE);
        }
      } else if (expr === 'squint') {
        rect(x0 - 1, y0 - 1, w + 2, 2, OUTLINE);
      }
    }
    if (expr === 'cool_shades') {
      rect(cx - 2, ey - 2, 5, 2, '#090d1f');
    }
  }

  function drawHeadwear(cx, cy, R, hat, t = 0) {
    if (!hat) return;
    if (CUSTOM_HATS[hat]) {
      CUSTOM_HATS[hat](cx, cy, R, t);
      return;
    }
    if (hat === 'host_cap') {
      const top = Math.round(cy - R - 2);
      rect(cx - Math.round(R * 0.7), top, Math.round(R * 1.4), 5, '#ef4444');
      rect(cx - Math.round(R * 0.6), top - 1, Math.round(R * 1.2), 2, '#dc2626');
      rect(cx - Math.round(R * 1.15), top + 3, Math.round(R * 0.6), 3, '#991b1b');
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
      rect(cx - 5, top - 2, 3, 3, '#3b2314');
      rect(cx + 1, top - 3, 3, 4, '#4e2f1b');
      rect(cx + 5, top - 1, 3, 2, '#3b2314');
    } else if (hat === 'sage_wizard') {
      const ny = Math.round(cy - R - 6);
      rect(cx - 10, ny + 4, 21, 3, '#facc15');
      rect(cx - 7, ny, 15, 4, '#1e3a8a');
      rect(cx - 4, ny - 4, 9, 4, '#2563eb');
      glowOrb(cx, ny - 6 + Math.round(Math.sin(t * 6)), 2, '#ffffff', '#fde047', '#38bdf8');
    }
  }

  function drawProp(prop, pxX, pxY, t = 0) {
    if (!prop) return;
    const x = Math.round(pxX);
    const y = Math.round(pxY + Math.sin(t * 5) * 1.0);
    if (CUSTOM_PROPS[prop]) {
      CUSTOM_PROPS[prop](x, y, t);
      return;
    }
    if (prop === 'cash_1k' || prop === 'cash_2k') {
      const count = prop === 'cash_2k' ? 2 : 1;
      for (let i = 0; i < count; i++) {
        const bx = x + i * 2, by = y - i * 3;
        rect(bx - 1, by - 1, 14, 9, OUTLINE);
        rect(bx, by, 12, 7, '#22c55e');
        rect(bx + 1, by + 1, 10, 5, '#15803d');
        pixelText(prop === 'cash_2k' ? '$2K' : '$1K', bx + 6, by - 7, '#4ade80', '#062812', 'center');
      }
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
      glasses = false,
      beard = false,
      squashX = 1.0,
      squashY = 1.0,
      shadow = true,
    } = opts;

    const skin = SKINS[role] || SKINS.mc;
    let sy = squashY, sx = squashX, bobY = 0;
    if (isTalking) {
      const pulse = Math.abs(Math.sin(t * 28));
      sy *= (1 + 0.08 * pulse);
      sx *= (1 / (1 + 0.06 * pulse));
      bobY = -Math.round(pulse * 2.0);
    }

    const rX = Math.max(4, Math.round(R * sx));
    const rY = Math.max(4, Math.round(R * sy));
    const by = Math.round(cy + bobY);
    const bx = Math.round(cx);

    if (shadow) {
      pctx.fillStyle = 'rgba(8, 6, 18, 0.45)';
      for (let dx = -Math.round(rX * 0.85); dx <= Math.round(rX * 0.85); dx++) {
        for (let dy = -2; dy <= 2; dy++) {
          if ((dx * dx) / (rX * rX * 0.72) + (dy * dy) / 4 <= 1) {
            pctx.fillRect(bx + dx, Math.round(cy + rY + 1 + dy), 1, 1);
          }
        }
      }
    }

    for (let dy = -rY - 1; dy <= rY + 1; dy++) {
      for (let dx = -rX - 1; dx <= rX + 1; dx++) {
        const nx = dx / rX, ny = dy / rY;
        const d2 = nx * nx + ny * ny;
        if (d2 > 1.12) continue;
        if (d2 > 0.96) { px(bx + dx, by + dy, OUTLINE); continue; }

        const x = bx + dx, y = by + dy;
        const clothCol = outfit ? drawOutfitPixel(outfit, dx, dy, rY, x, y, opts) : null;
        if (clothCol) { px(x, y, clothCol); continue; }

        if (beard && dy > rY * 0.22) {
          px(x, y, bayerPick(x, y, '#f8fafc', '#cbd5e1', 1));
          continue;
        }

        const light = -0.55 * nx - 0.65 * ny;
        let col = skin.lit;
        if (light > 0.56) col = skin.hi;
        else if (light > 0.05) col = skin.lit;
        else if (light > -0.32) col = bayerPick(x, y, skin.lit, skin.shade, 2);
        else col = skin.shade;
        px(x, y, col);
      }
    }

    if (rY > 7) {
      px(bx - Math.round(rX * 0.45), by - Math.round(rY * 0.48), '#ffffff');
      px(bx - Math.round(rX * 0.38), by - Math.round(rY * 0.54), '#ffffff');
    }

    if (role === 'mrbeast') {
      const gy = by + Math.round(rY * 0.16);
      rect(bx - 4, gy, 9, 1, '#5c3a21');
      rect(bx - 2, gy + 2, 5, 2, '#5c3a21');
    }

    if (rY >= 6) {
      drawEyes(bx, by, Math.min(rX, rY), expr, lookX, lookY);
    }

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

    if (sweat) {
      const sxp = bx + Math.round(rX * 0.65);
      const syp = by - Math.round(rY * 0.40) + Math.round((t * 12) % 4);
      px(sxp, syp - 1, '#e0f2fe');
      rect(sxp - 1, syp, 3, 2, '#38bdf8');
      px(sxp, syp + 2, '#0284c7');
    }

    drawHeadwear(bx, by, rY, hat, t);

    if (prop) {
      drawProp(prop, bx + propSide * (rX + 10) - (propSide < 0 ? 10 : 0), by - 2, t);
    }
  }

  return { drawBall, register, OUTLINE, bayerPick };
})();
