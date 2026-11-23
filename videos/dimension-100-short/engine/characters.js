/* Countryball-style 8-bit Character Renderer (NO MOUTH, Skin Tones + Clothes + Dimensional Forms)
 * Logical 180x320 pixel canvas.
 * Supports:
 *  - Standard 3D dithered Countryballs (Host, MrBeast, MC, 11D String Warden)
 *  - 1D Pancake Squash & 2D Flatland Unshaded Cross-Section
 *  - 4D Back-of-Head Clone Ball
 *  - 2D Sir Square Boss (drawFlatSquare)
 *  - 100D 6-Pixel Calculator Block MC (drawCalculatorBlockMC)
 */
window.CHARS = (() => {
  const { pctx, px, rect, line, disk, glowOrb, pixelText } = window.PX;
  const OUTLINE = '#181124';

  const SKINS = {
    host:    { hi: '#fde2c4', lit: '#f2c29b', shade: '#ce9268' },
    mrbeast: { hi: '#fde5cc', lit: '#f5cba7', shade: '#d49d74' },
    mc:      { hi: '#f3caa0', lit: '#db9f67', shade: '#b3743f' },
    warden:  { hi: '#f5d0fe', lit: '#d8b4fe', shade: '#9333ea' },
  };

  function bayerPick(x, y, colA, colB, thr = 2) {
    const b = ((y & 1) << 1) | ((x ^ y) & 1);
    return b < thr ? colB : colA;
  }

  function drawOutfitPixel(outfit, dx, dy, R, x, y, opts) {
    if (dy <= R * 0.20) return null;
    const shade = !opts.flat2D && (dx > R * 0.18 || dy > R * 0.68);

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
      if (opts.hyperGlitch && ((dx * 11 + dy * 7) & 15) === 0) {
        return ((dx + dy) & 1) ? '#22d3ee' : '#f472b6';
      }
      if (Math.abs(dx + 3) <= 0 && dy > R * 0.24 && dy < R * 0.62) return '#f8fafc';
      if (Math.abs(dx - 3) <= 0 && dy > R * 0.24 && dy < R * 0.62) return '#f8fafc';
      return shade ? '#15803d' : '#22c55e';
    }

    if (outfit === 'warden_robe') {
      if (Math.abs(dx) <= 1) return '#facc15';
      if (Math.abs(Math.abs(dx) - Math.round(dy * 0.5)) <= 1) return '#38bdf8';
      return ((dx + 20) & 3) < 2 ? '#311042' : '#581c87';
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
        // X_X eyes
        line(ex - 2, ey - 2, ex + 2, ey + 2, OUTLINE);
        line(ex - 2, ey + 2, ex + 2, ey - 2, OUTLINE);
        continue;
      }

      const h = expr === 'wide' ? eh + 2 : expr === 'squint' ? Math.max(3, eh - 2) : eh;
      const w = expr === 'wide' ? ew + 1 : ew;
      const x0 = ex - Math.floor(w / 2);
      const y0 = ey - Math.floor(h / 2);

      // 1px dark outline
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
  }

  function drawHeadwear(cx, cy, R, hat, t = 0) {
    if (!hat) return;
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
    } else if (hat === 'mc_hair' || hat === 'mc_visor') {
      const top = Math.round(cy - R - 2);
      rect(cx - Math.round(R * 0.65), top + 1, Math.round(R * 1.3), 4, '#3b2314');
      rect(cx - 5, top - 2, 3, 3, '#3b2314');
      rect(cx + 1, top - 3, 3, 4, '#4e2f1b');
      rect(cx + 5, top - 1, 3, 2, '#3b2314');
      if (hat === 'mc_visor') {
        // Glowing cyan 100D quantum goggles strapped above eyes
        const vy = top + 4;
        rect(cx - 9, vy, 18, 4, '#0f172a');
        rect(cx - 8, vy + 1, 7, 2, '#22d3ee');
        rect(cx + 1, vy + 1, 7, 2, '#f472b6');
      }
    } else if (hat === 'warden_mitre') {
      // Cosmic 11D Wizard Mitre + Floating Golden Halo Orb
      const ny = Math.round(cy - R - 7);
      rect(cx - 9, ny + 5, 19, 3, '#facc15');
      rect(cx - 7, ny + 1, 15, 4, '#581c87');
      rect(cx - 4, ny - 3, 9, 4, '#7e22ce');
      rect(cx - 2, ny - 6, 5, 3, '#a855f7');
      glowOrb(cx, ny - 8 + Math.round(Math.sin(t * 6)), 2, '#ffffff', '#fde047', '#a855f7');
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
    } else if (prop === 'bagel') {
      // Toasted golden pixel bagel with hole
      disk(x + 4, y + 3, 5, OUTLINE);
      disk(x + 4, y + 3, 4, '#d97706');
      disk(x + 4, y + 2, 3, '#fbbf24');
      rect(x + 3, y + 2, 2, 2, '#181124'); // bagel hole
      px(x + 2, y + 1, '#fef3c7'); // sesame seeds
      px(x + 6, y + 2, '#fef3c7');
    } else if (prop === 'klein_bottle') {
      // Self-intersecting neon cyan/magenta 4D Klein bottle!
      glowOrb(x + 4, y + 3, 7, '#f0abfc', '#22d3ee', '#7e22ce');
      rect(x + 1, y, 7, 8, '#06b6d4');
      rect(x + 2, y + 1, 5, 6, '#67e8f9');
      // Neck looping back through its own side in 4D
      line(x + 4, y, x + 4, y - 4, '#f472b6');
      line(x + 4, y - 4, x + 9, y - 2, '#f472b6');
      line(x + 9, y - 2, x + 5, y + 4, '#f472b6');
      px(x + 3, y + 2, '#ffffff');
    } else if (prop === 'origami_pretzel') {
      // 11D Calabi-Yau folded golden space pretzel
      glowOrb(x + 4, y + 3, 6, '#fef08a', '#f59e0b', '#9333ea');
      line(x, y + 2, x + 8, y + 2, '#fde047');
      line(x + 1, y - 2, x + 7, y + 6, '#38bdf8');
      line(x + 7, y - 2, x + 1, y + 6, '#f472b6');
    } else if (prop === 'hypercube_100d') {
      // Glowing miniature 100D tesseract cube
      glowOrb(x + 4, y + 3, 6, '#ffffff', '#22d3ee', '#ec4899');
      rect(x + 1, y, 7, 7, '#f472b6');
      rect(x + 2, y + 1, 5, 5, '#22d3ee');
      rect(x + 3, y + 2, 3, 3, '#ffffff');
    } else if (prop === 'nickel_5c') {
      // Shiny silver 5c nickel coin
      disk(x + 4, y + 3, 5, OUTLINE);
      disk(x + 4, y + 3, 4, '#94a3b8');
      disk(x + 3, y + 2, 3, '#e2e8f0');
      pixelText('5¢', x + 4, y - 6, '#38bdf8', '#090d1f', 'center');
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
      thirdEye = false,
      squashX = 1.0,
      squashY = 1.0,
      flat2D = false,
      backOfHead = false,
      hyperGlitch = false,
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
    const rY = Math.max(3, Math.round(R * sy));
    const by = Math.round(cy + bobY);
    const bx = Math.round(cx);

    // Ground contact shadow ellipse (Law #11 / Visual QA #7)
    if (!flat2D && rY > 5) {
      pctx.fillStyle = 'rgba(8, 6, 18, 0.45)';
      for (let dx = -Math.round(rX * 0.85); dx <= Math.round(rX * 0.85); dx++) {
        for (let dy = -2; dy <= 2; dy++) {
          if ((dx * dx) / (rX * rX * 0.72) + (dy * dy) / 4 <= 1) {
            pctx.fillRect(bx + dx, Math.round(cy + rY + 1 + dy), 1, 1);
          }
        }
      }
    }

    // Sphere pixels
    for (let dy = -rY - 1; dy <= rY + 1; dy++) {
      for (let dx = -rX - 1; dx <= rX + 1; dx++) {
        const nx = dx / rX;
        const ny = dy / rY;
        const d2 = nx * nx + ny * ny;

        if (d2 > 1.12) continue;
        if (d2 > (flat2D ? 0.90 : 0.96)) {
          px(bx + dx, by + dy, flat2D ? '#ffffff' : OUTLINE);
          continue;
        }

        const x = bx + dx;
        const y = by + dy;

        if (backOfHead) {
          // 4D Back-of-head clone: brown hair on top, green hoodie on bottom!
          if (ny < 0.18) {
            px(x, y, bayerPick(x, y, '#4e2f1b', '#3b2314', 2));
          } else {
            px(x, y, bayerPick(x, y, '#22c55e', '#15803d', 2));
          }
          continue;
        }

        const clothCol = outfit ? drawOutfitPixel(outfit, dx, dy, rY, x, y, { flat2D, hyperGlitch }) : null;
        if (clothCol) {
          px(x, y, clothCol);
          continue;
        }

        if (role === 'warden' && dy > rY * 0.22) {
          px(x, y, bayerPick(x, y, '#fef08a', '#f59e0b', 1));
          continue;
        }

        if (flat2D) {
          px(x, y, skin.lit);
          continue;
        }

        const light = -0.55 * nx - 0.65 * ny;
        let col = skin.lit;
        if (light > 0.56) col = skin.hi;
        else if (light > 0.05) col = skin.lit;
        else if (light > -0.32) col = bayerPick(x, y, skin.lit, skin.shade, 2);
        else col = skin.shade;

        if (hyperGlitch && ((x * 13 + y * 17 + Math.floor(t * 15)) & 31) === 0) {
          col = '#22d3ee';
        }

        px(x, y, col);
      }
    }

    if (backOfHead) {
      // Hoodie seam line on back of head
      line(bx - Math.round(rX * 0.7), by + 3, bx + Math.round(rX * 0.7), by + 3, '#14532d');
      drawHeadwear(bx, by, rY, hat, t);
      return;
    }

    if (!flat2D && rY > 6) {
      px(bx - Math.round(rX * 0.45), by - Math.round(rY * 0.48), '#ffffff');
      px(bx - Math.round(rX * 0.38), by - Math.round(rY * 0.54), '#ffffff');
    }

    if (role === 'mrbeast') {
      const gy = by + Math.round(rY * 0.16);
      rect(bx - 4, gy, 9, 1, '#5c3a21');
      rect(bx - 2, gy + 2, 5, 2, '#5c3a21');
    }

    // Countryball Eyes
    if (rY >= 5) {
      drawEyes(bx, by, Math.min(rX, rY), expr, lookX, lookY);
    }

    if (glasses) {
      const sep = Math.max(4, Math.round(rX * 0.36));
      for (const s of [-1, 1]) {
        const ex = bx + s * sep;
        const ey = Math.round(by - rY * 0.06);
        rect(ex - 4, ey - 3, 8, 1, '#fde047');
        rect(ex - 4, ey + 3, 8, 1, '#fde047');
        rect(ex - 4, ey - 2, 1, 5, '#fde047');
        rect(ex + 3, ey - 2, 1, 5, '#fde047');
      }
      rect(bx - 1, Math.round(by - rY * 0.06), 3, 1, '#fde047');
    }

    if (thirdEye) {
      // Glowing 11D quantum third eye on forehead!
      const ty = Math.round(by - rY * 0.44);
      rect(bx - 2, ty - 1, 5, 3, '#181124');
      rect(bx - 1, ty, 3, 1, '#22d3ee');
      px(bx, ty, '#ffffff');
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

  // Flat 2D Geometric Square Character ("Sir Square") in Dimension 2
  function drawFlatSquare(opts) {
    const {
      cx = 128,
      cy = 180,
      size = 18,
      expr = 'angry',
      lookX = -1,
      isTalking = false,
      t = 0,
    } = opts;
    const pulse = isTalking ? Math.abs(Math.sin(t * 28)) : 0;
    const w = Math.round(size * (1 - 0.05 * pulse));
    const h = Math.round(size * (1 + 0.08 * pulse));
    const bx = Math.round(cx);
    const by = Math.round(cy - pulse * 2);

    // 2px crisp white + dark 2D plane border
    rect(bx - w - 2, by - h - 2, (w + 2) * 2, (h + 2) * 2, '#ffffff');
    rect(bx - w - 1, by - h - 1, (w + 1) * 2, (h + 1) * 2, OUTLINE);
    // Flat 2D magenta/cyan split body
    rect(bx - w, by - h, w * 2, h * 2, '#ec4899');
    rect(bx - w, by + 3, w * 2, h - 3, '#be185d');

    // Tiny flat 2D gold crown
    const ky = by - h - 7;
    rect(bx - 6, ky + 3, 13, 3, '#facc15');
    rect(bx - 6, ky, 3, 3, '#facc15');
    rect(bx - 1, ky - 1, 3, 4, '#fde047');
    rect(bx + 4, ky, 3, 3, '#facc15');

    drawEyes(bx, by, size * 0.9, expr, lookX, 0);
  }

  // 100D Integer Overflow -> Chunky 6-Macro-Pixel Calculator Block MC!
  function drawCalculatorBlockMC(cx, cy, isTalking, t) {
    const BS = 14; // 14x14 pixel macro-blocks with 2px LCD grid gap
    const gap = 2;
    const step = BS + gap;
    const pulseY = isTalking ? (Math.floor(t * 14) % 2) * -3 : 0;
    const x0 = Math.round(cx - step);
    const y0 = Math.round(cy - step * 1.5 + pulseY);

    // 2x3 grid = 6 literal giant pixels!
    const grid = [
      ['#4e2f1b', '#3b2314'], // Row 0: 2 hair/head top pixels
      ['#f3caa0', '#db9f67'], // Row 1: 2 face skin pixels
      ['#22c55e', '#15803d'], // Row 2: 2 green hoodie pixels
    ];

    // Outer LCD shadow frame
    rect(x0 - 3, y0 - 3, step * 2 + 4, step * 3 + 4, '#062016');

    for (let r = 0; r < 3; r++) {
      for (let c = 0; c < 2; c++) {
        const bx = x0 + c * step;
        const by = y0 + r * step;
        rect(bx, by, BS, BS, grid[r][c]);
        // Inner 1px highlight
        rect(bx + 1, by + 1, BS - 2, 1, 'rgba(255,255,255,0.25)');
      }
    }

    // 2 blocky single-macro-pixel eyes on Row 1
    rect(x0 + 3, y0 + step + 3, 8, 8, '#ffffff');
    rect(x0 + 5, y0 + step + 5, 4, 4, '#052e16');

    rect(x0 + step + 3, y0 + step + 3, 8, 8, '#ffffff');
    rect(x0 + step + 5, y0 + step + 5, 4, 4, '#052e16');

    // Label tag pointing to the 6 blocks
    pixelText('6 PIXELS', cx, y0 - 10, '#4ade80', '#022c22', 'center');
  }

  return { drawBall, drawFlatSquare, drawCalculatorBlockMC };
})();
