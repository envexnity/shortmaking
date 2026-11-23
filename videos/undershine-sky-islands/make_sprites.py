"""
make_sprites.py — Procedural 16-Bit / 32-Bit High-Detail 2D Pixel-Art Sprite & Planetary Texture Generator
for Track 7 Undershine 2.5D Hybrid ("3D Terrain & Background + 2D Pixel-Art Sprites + Full Spherical Planet Balls").

Generates into `sprites/`:
  1. `planet_ball_w1..w4.png` (512x256 equirectangular pixel-art planetary textures for full spherical UV balls)
  2. `tree_oak_a.png`, `tree_oak_b.png`, `tree_pine_a.png`, `tree_gold_a.png`, `bush_cluster.png`, `flower_patch.png`
  3. `cottage_house.png`, `windmill_tower.png`, `windmill_rotor.png`, `stone_bridge_sprite.png`
  4. `viaduct_arch_sprite.png`, `brass_train_sprite.png`, `hanging_lantern_sprite.png`
  5. `sanctuary_tower_sprite.png`, `astrolabe_ring_sprite.png`, `marble_pavilion_sprite.png`
  6. `iron_chain_sprite.png`, `quarry_crane_sprite.png`, `crystal_cyan.png`, `crystal_amber.png`
  7. `char_baker.png`, `char_railworker.png`, `char_scholar.png`, `char_miner.png`
"""
import os
import math
import random
import numpy as np
from PIL import Image, ImageDraw

BASE = os.path.dirname(os.path.abspath(__file__))
SPRITES_DIR = os.path.join(BASE, "sprites")
os.makedirs(SPRITES_DIR, exist_ok=True)

INK = (24, 19, 38, 255)  # #181326 deep plum-indigo pixel outline (never pure #000000)


def hex_rgba(h: str, a: int = 255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


BAYER4 = np.array([
    [0,  8,  2, 10],
    [12, 4, 14,  6],
    [3, 11,  1,  9],
    [15, 7, 13,  5],
], dtype=np.float32) / 16.0 - 0.5


def add_plum_pixel_outline(img: Image.Image, ink_rgba=INK,exempt_bottom: bool = False) -> Image.Image:
    """Adds a crisp 1-pixel #181326 plum silhouette outline around opaque sprite pixels."""
    arr = np.array(img, dtype=np.uint8)
    alpha = arr[:, :, 3] > 128
    H, W = alpha.shape
    up = np.pad(alpha[1:, :], ((0, 1), (0, 0)), constant_values=False)
    dn = np.pad(alpha[:-1, :], ((1, 0), (0, 0)), constant_values=False)
    lt = np.pad(alpha[:, 1:], ((0, 0), (0, 1)), constant_values=False)
    rt = np.pad(alpha[:, :-1], ((0, 0), (1, 0)), constant_values=False)
    border = (~alpha) & (up | dn | lt | rt)
    if exempt_bottom:
        border[-2:, :] = False
    out = arr.copy()
    out[border] = ink_rgba
    return Image.fromarray(out, mode="RGBA")


def save_sprite(name: str, img: Image.Image, outline: bool = True, exempt_bottom: bool = False):
    if outline:
        img = add_plum_pixel_outline(img, exempt_bottom=exempt_bottom)
    path = os.path.join(SPRITES_DIR, name)
    img.save(path, "PNG")
    return path


# =============================================================================
# 1. FULL SPHERICAL PLANET BALL TEXTURES (512x256 Equirectangular Pixel Art)
# =============================================================================
def generate_planet_ball_textures():
    W, H = 512, 256
    y_idx, x_idx = np.mgrid[0:H, 0:W].astype(np.float32)
    lon = (x_idx / W) * math.tau
    lat = ((y_idx / H) - 0.5) * math.pi
    # 3D unit sphere coordinates so texture wraps seamlessly with ZERO seam at lon=0/2pi!
    sx = np.cos(lat) * np.cos(lon)
    sy = np.cos(lat) * np.sin(lon)
    sz = np.sin(lat)

    def fbm3(seed_off: float):
        v = (
            0.50 * np.sin(sx * 4.2 + sy * 3.8 + seed_off) * np.cos(sz * 4.5 - sy * 3.1)
            + 0.28 * np.cos(sx * 9.5 - sz * 8.2 + seed_off * 1.7) * np.sin(sy * 9.1 + sx * 7.4)
            + 0.14 * np.sin(sx * 19.0 + sy * 17.5 - sz * 16.0 + seed_off * 2.3)
            + 0.08 * np.cos(sy * 34.0 - sx * 31.0 + sz * 29.0)
        )
        return (v - v.min()) / max(1e-5, (v.max() - v.min()))

    bayer = np.tile(BAYER4, (H // 4 + 1, W // 4 + 1))[:H, :W]

    configs = [
        # World 1: Windmill Steppe (lush emerald continents, golden highland steppes, deep sapphire rivers, white cloud bands)
        ("planet_ball_w1.png", 1.1, [
            (0.28, "#16324f"), (0.36, "#286684"), (0.44, "#3b704c"),
            (0.62, "#6ea352"), (0.78, "#c9a85c"), (0.90, "#f0df9c"), (1.01, "#ffffff"),
        ], "#f5eedc", False),
        # World 2: Midnight Rail (twilight indigo ocean, slate mountain ridges, frost cloud bands, glowing amber railway belt!)
        ("planet_ball_w2.png", 2.8, [
            (0.30, "#121833"), (0.45, "#233259"), (0.60, "#46486e"),
            (0.75, "#787696"), (0.88, "#a6bddb"), (1.01, "#dceeff"),
        ], "#c7ddf5", "rail_belt"),
        # World 3: Clockwork Sanctuary (turquoise hot-spring seas, white marble continents, golden forests & cyan rings)
        ("planet_ball_w3.png", 4.3, [
            (0.34, "#153d54"), (0.48, "#297a8c"), (0.58, "#64c2ba"),
            (0.70, "#d8cfc2"), (0.84, "#e6b35a"), (1.01, "#fff3cc"),
        ], "#e8fff9", "cyan_meridian"),
        # World 4: Ballast Quarry (cracked obsidian crust, ash storm bands, glowing molten sky-stone & lava fissures)
        ("planet_ball_w4.png", 6.1, [
            (0.24, "#ff4d1c"), (0.32, "#ff9e38"), (0.42, "#241d30"),
            (0.64, "#3b354d"), (0.82, "#5e546b"), (1.01, "#8a7c8f"),
        ], "#45f0e5", "quarry_veins"),
    ]

    for fname, seed_off, stops, cloud_hex, special in configs:
        n = fbm3(seed_off) + bayer * 0.045
        # Swirl atmospheric cloud layer
        clouds = np.sin(lat * 7.5 + np.sin(lon * 3.0 + seed_off) * 0.9) * np.cos(lon * 4.0 - lat * 3.0 + n * 4.0)
        clouds = (clouds - clouds.min()) / max(1e-5, clouds.max() - clouds.min()) + bayer * 0.05

        out = np.zeros((H, W, 4), dtype=np.uint8)
        out[:, :, 3] = 255
        prev_t = -1.0
        for thr, hex_c in stops:
            mask = (n >= prev_t) & (n < thr)
            out[mask] = hex_rgba(hex_c)
            prev_t = thr

        # Ice / storm polar caps
        pole = (np.abs(lat) + n * 0.18 + bayer * 0.04) > 1.28
        out[pole] = hex_rgba(cloud_hex)

        # Wisp cloud bands
        c_mask = (clouds > 0.77) & (~pole)
        out[c_mask] = hex_rgba(cloud_hex)

        if special == "rail_belt":
            # Glowing golden railway ring circling equator
            eq = np.abs(lat - 0.08 * np.sin(lon * 2.0)) < 0.035
            out[eq] = hex_rgba("#ffbd4a")
        elif special == "cyan_meridian":
            ring = (np.abs(lat) < 0.03) | (np.abs(np.sin(lon * 2.0)) < 0.025)
            out[ring] = hex_rgba("#45f0e5")
        elif special == "quarry_veins":
            vein = (np.abs(n - 0.52) < 0.016)
            out[vein] = hex_rgba("#45f0e5")

        Image.fromarray(out, mode="RGBA").save(os.path.join(SPRITES_DIR, fname), "PNG")


# =============================================================================
# 2. DETAILED 2D PIXEL-ART TREES, BUSHES & FLOWERS
# =============================================================================
def make_detailed_tree_sprite(name: str, palette_canopy, palette_trunk, pine: bool = False, seed: int = 1):
    rng = random.Random(seed)
    W, H = (96, 144) if pine else (120, 148)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = img.load()

    c_deep, c_shad, c_mid, c_lit, c_rim = [hex_rgba(c) for c in palette_canopy]
    t_shad, t_mid, t_lit = [hex_rgba(c) for c in palette_trunk]

    cx = W // 2
    # 1. Detailed gnarled trunk with bark ridges & root flare at bottom (y = H-4)
    trunk_top = 56 if not pine else 42
    for y in range(trunk_top, H - 2):
        u = (y - trunk_top) / max(1, (H - 3 - trunk_top))
        half_w = int(round(4.5 + 3.5 * (u ** 1.6) + (4.5 * max(0.0, u - 0.78) * 3.5)))
        curve_x = int(round(2.5 * math.sin(u * 3.8 + seed)))
        for dx in range(-half_w, half_w + 1):
            x = cx + curve_x + dx
            if 2 <= x < W - 2:
                # Bark vertical groove texture
                ridge = ((dx + int(y * 0.25)) % 3 == 0)
                if dx < -half_w * 0.35:
                    col = t_shad
                elif dx > half_w * 0.30 or (ridge and dx > 0):
                    col = t_lit
                else:
                    col = t_mid
                px[x, y] = col

    # Branch forks under canopy
    if not pine:
        for side, bx_dir in [(-1, -14), (1, 15)]:
            for step in range(18):
                bx = cx + int(bx_dir * (step / 18.0))
                by = trunk_top + 14 - step
                for w_off in range(-2, 3):
                    if 2 <= bx + w_off < W - 2 and 2 <= by < H - 2:
                        px[bx + w_off, by] = t_shad if w_off < 0 else t_mid

    # 2. Multi-cluster scalloped pixel-art foliage canopy
    clusters = []
    if pine:
        tiers = [(24, 14, 16), (40, 20, 18), (58, 26, 20), (78, 31, 22), (96, 35, 20)]
        for ty, rx, ry in tiers:
            for sub in range(5):
                ox = cx + int(rng.uniform(-rx * 0.55, rx * 0.55))
                oy = ty + int(rng.uniform(-3, 5))
                clusters.append((ox, oy, int(rx * 0.52), int(ry * 0.58)))
    else:
        # Lush Ghibli oak puff clusters
        base_blobs = [
            (cx, 34, 26, 22), (cx - 20, 46, 22, 20), (cx + 21, 46, 22, 20),
            (cx - 28, 62, 20, 18), (cx + 28, 62, 20, 18), (cx, 56, 26, 22),
            (cx - 14, 70, 22, 18), (cx + 15, 70, 22, 18), (cx, 24, 20, 16),
        ]
        for bx, by, brx, bry in base_blobs:
            clusters.append((bx, by, brx, bry))
            for _ in range(3):
                clusters.append((
                    bx + rng.randint(-10, 10),
                    by + rng.randint(-7, 7),
                    int(brx * rng.uniform(0.55, 0.78)),
                    int(bry * rng.uniform(0.55, 0.78)),
                ))

    for y in range(4, H - 18):
        for x in range(4, W - 4):
            best_val = -1.0
            local_lit = 0.0
            for bx, by, brx, bry in clusters:
                nx = (x - bx) / max(1.0, float(brx))
                ny = (y - by) / max(1.0, float(bry))
                d2 = nx * nx + ny * ny
                # Scalloped pixel leaf edge perturbation
                scallop = 0.12 * math.sin(x * 0.85 + by) * math.cos(y * 0.85 + bx)
                if d2 + scallop <= 1.0:
                    # Sun from upper-right (+x, -y)
                    sub_lit = 0.52 + 0.34 * nx - 0.42 * ny + (1.0 - d2) * 0.18
                    if sub_lit > best_val:
                        best_val = sub_lit
                        local_lit = sub_lit
            if best_val >= 0.0:
                # Global canopy spherical normal lighting + ordered Bayer dither + leaf cluster pixel grain
                gx = (x - cx) / (W * 0.44)
                gy = (y - 52.0) / 46.0
                g_lit = 0.48 + 0.28 * gx - 0.36 * gy
                lit = 0.55 * local_lit + 0.45 * g_lit + BAYER4[y % 4, x % 4] * 0.13
                leaf_dot = ((x // 2 + y // 2) % 3 == 0) * 0.04
                lit += leaf_dot
                if lit < 0.24:
                    px[x, y] = c_deep
                elif lit < 0.44:
                    px[x, y] = c_shad
                elif lit < 0.66:
                    px[x, y] = c_mid
                elif lit < 0.86:
                    px[x, y] = c_lit
                else:
                    px[x, y] = c_rim

    save_sprite(name, img, outline=True, exempt_bottom=True)


def make_bush_and_flower_sprites():
    # Lush berry bush sprite (64x48)
    W, H = 64, 48
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = img.load()
    c_deep, c_shad, c_mid, c_lit = [hex_rgba(c) for c in ("#13222e", "#224a45", "#437a50", "#8ec25b")]
    c_berry = hex_rgba("#ff6363")
    c_gold = hex_rgba("#ffe066")
    blobs = [(32, 24, 16, 14), (19, 29, 13, 12), (45, 29, 13, 12), (26, 33, 14, 11), (38, 33, 14, 11)]
    for y in range(6, H - 2):
        for x in range(4, W - 4):
            inside = False
            best_l = 0.0
            for bx, by, rx, ry in blobs:
                nx, ny = (x - bx) / rx, (y - by) / ry
                if nx * nx + ny * ny <= 1.0:
                    inside = True
                    best_l = max(best_l, 0.5 + 0.3 * nx - 0.4 * ny)
            if inside:
                v = best_l + BAYER4[y % 4, x % 4] * 0.14
                px[x, y] = c_deep if v < 0.30 else (c_shad if v < 0.50 else (c_mid if v < 0.72 else c_lit))
                if (x * 7 + y * 13) % 47 == 0 and 14 < y < H - 8:
                    px[x, y] = c_berry if (x + y) % 2 == 0 else c_gold
    save_sprite("bush_cluster.png", img, outline=True, exempt_bottom=True)

    # Wildflower & tall grass tuft sprite (48x36)
    W, H = 48, 36
    img2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(img2)
    rng = random.Random(55)
    for bx in range(8, W - 8, 3):
        h = rng.randint(11, 22)
        lean = rng.randint(-4, 4)
        col = hex_rgba("#437a50" if bx % 2 == 0 else "#8ec25b")
        d2.line([(bx, H - 2), (bx + lean, H - 2 - h)], fill=col, width=2)
        if bx % 6 == 2:
            fcol = hex_rgba("#ffdf59" if bx % 4 == 0 else "#ff8278")
            fx, fy = bx + lean, H - 3 - h
            d2.rectangle([fx - 2, fy - 2, fx + 2, fy + 2], fill=fcol)
            d2.point((fx, fy), fill=hex_rgba("#fff9d6"))
    save_sprite("flower_patch.png", img2, outline=True, exempt_bottom=True)


# =============================================================================
# 3. DETAILED 2D PIXEL-ART HOUSES, WINDMILLS, TRAINS, TOWERS & QUARRY SPRITES
# =============================================================================
def draw_brick_textured_rect(px, x0, y0, x1, y1, c_shad, c_mid, c_lit, brick_w=8, brick_h=4):
    for y in range(max(0, y0), min(y1, 256)):
        row = (y - y0) // brick_h
        is_mortar_h = ((y - y0) % brick_h == 0)
        for x in range(max(0, x0), min(x1, 256)):
            u_x = (x - x0) / max(1, (x1 - x0))
            is_mortar_v = (((x - x0) + (row % 2) * (brick_w // 2)) % brick_w == 0)
            if is_mortar_h or is_mortar_v:
                col = c_shad
            else:
                v = u_x + BAYER4[y % 4, x % 4] * 0.18
                col = c_shad if v < 0.25 else (c_mid if v < 0.72 else c_lit)
            px[x, y] = col


def make_architecture_sprites():
    # --- A. Cozy Half-Timbered Baker's Cottage (144x136) ---
    W, H = 144, 136
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = img.load()
    d = ImageDraw.Draw(img)

    # Stone chimney on left
    draw_brick_textured_rect(px, 24, 18, 40, 80, hex_rgba("#2b2840"), hex_rgba("#656078"), hex_rgba("#9e958b"), 6, 4)
    # Stone foundation base
    draw_brick_textured_rect(px, 20, 108, 124, 134, hex_rgba("#242238"), hex_rgba("#5a566e"), hex_rgba("#8f867d"), 8, 5)
    # Warm plaster cottage walls
    draw_brick_textured_rect(px, 24, 64, 120, 108, hex_rgba("#7a6868"), hex_rgba("#c9b59c"), hex_rgba("#f0dfc8"), 12, 6)

    # Oak timber framing beams
    t_dark, t_mid, t_lit = hex_rgba("#291926"), hex_rgba("#633e34"), hex_rgba("#9c6b4e")
    for bx in (24, 56, 88, 116):
        d.rectangle([bx, 64, bx + 4, 108], fill=t_mid, outline=t_dark)
    for by in (64, 86, 105):
        d.rectangle([22, by, 121, by + 3], fill=t_mid, outline=t_dark)

    # Pitched terracotta shingled roof with scallop tiles
    r_deep, r_shad, r_mid, r_lit = hex_rgba("#381629"), hex_rgba("#752734"), hex_rgba("#ad3e42"), hex_rgba("#e37254")
    for y in range(22, 66):
        u = (y - 22) / 44.0
        half_w = int(12 + u * 56)
        cx = 72
        tile_row = (y - 22) // 5
        for x in range(cx - half_w, cx + half_w + 1):
            ux = (x - (cx - half_w)) / max(1, 2 * half_w)
            is_seam = ((y - 22) % 5 == 0) or (((x + tile_row * 4) % 8) == 0)
            if is_seam:
                px[x, y] = r_deep if ux < 0.5 else r_shad
            else:
                v = ux + BAYER4[y % 4, x % 4] * 0.15
                px[x, y] = r_shad if v < 0.30 else (r_mid if v < 0.72 else r_lit)

    # Arched oak door + two glowing multipane amber windows + flower boxes
    d.rounded_rectangle([63, 86, 81, 128], radius=7, fill=t_mid, outline=t_dark, width=2)
    d.ellipse([75, 106, 78, 109], fill=hex_rgba("#ffda66"))
    for wx in (33, 95):
        d.rectangle([wx, 72, wx + 18, 92], fill=hex_rgba("#fff0a8"), outline=t_dark, width=2)
        d.rectangle([wx + 2, 74, wx + 16, 90], outline=hex_rgba("#ff9d3b"), width=2)
        d.line([(wx + 9, 72), (wx + 9, 92)], fill=t_dark, width=2)
        d.line([(wx, 82), (wx + 18, 82)], fill=t_dark, width=2)
        # Window flower box
        d.rectangle([wx - 2, 92, wx + 20, 97], fill=t_mid, outline=t_dark)
        for fx in range(wx, wx + 19, 4):
            d.rectangle([fx, 89, fx + 3, 92], fill=hex_rgba("#437a50"))
            d.point((fx + 1, 89), fill=hex_rgba("#ff6b6b" if fx % 2 == 0 else "#ffe066"))
    save_sprite("cottage_house.png", img, outline=True, exempt_bottom=True)

    # --- B. Windmill Tower (128x184) & Rotating 4-Sail Rotor Sprite (168x168) ---
    W, H = 128, 184
    wimg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wpx = wimg.load()
    wd = ImageDraw.Draw(wimg)
    # Stone masonry base
    draw_brick_textured_rect(wpx, 28, 126, 100, 182, hex_rgba("#242238"), hex_rgba("#635e75"), hex_rgba("#a89b8e"), 9, 6)
    # Tapered timber & shingle octagonal tower
    for y in range(44, 126):
        u = (y - 44) / 82.0
        hw = int(23 + u * 12)
        for x in range(64 - hw, 64 + hw + 1):
            ux = (x - (64 - hw)) / max(1, 2 * hw)
            plank = ((x - 64) % 6 == 0) or ((y - 44) % 14 == 0)
            if plank:
                wpx[x, y] = t_dark
            else:
                v = ux + BAYER4[y % 4, x % 4] * 0.16
                wpx[x, y] = t_dark if v < 0.22 else (t_mid if v < 0.70 else t_lit)
    # Conical red shingle cap
    for y in range(12, 46):
        u = (y - 12) / 34.0
        hw = int(3 + u * 25)
        for x in range(64 - hw, 64 + hw + 1):
            ux = (x - (64 - hw)) / max(1, 2 * hw)
            wpx[x, y] = r_shad if ux < 0.35 else (r_mid if ux < 0.72 else r_lit)
    # Wooden balcony deck at y=124 + glowing windows
    wd.rectangle([18, 122, 110, 128], fill=t_lit, outline=t_dark, width=2)
    for post_x in range(20, 110, 10):
        wd.rectangle([post_x, 110, post_x + 2, 122], fill=t_mid)
    wd.rectangle([18, 108, 110, 111], fill=t_lit, outline=t_dark)
    for wy in (66, 96, 144):
        wd.rounded_rectangle([55, wy, 73, wy + 18], radius=4, fill=hex_rgba("#fff0a8"), outline=t_dark, width=2)
        wd.line([(64, wy), (64, wy + 18)], fill=t_dark, width=2)
        wd.line([(55, wy + 9), (73, wy + 9)], fill=t_dark, width=2)
    save_sprite("windmill_tower.png", wimg, outline=True, exempt_bottom=True)

    # Windmill 4-Blade Sail Rotor Sprite (168x168, centered at 84,84)
    RW = 168
    rimg = Image.new("RGBA", (RW, RW), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rimg)
    cx = RW // 2
    s_shad, s_mid, s_lit = hex_rgba("#8c7c78"), hex_rgba("#d9ccb8"), hex_rgba("#fff7e6")
    # Vertical and horizontal spars + lattice canvas sails
    rd.rectangle([cx - 3, 8, cx + 3, RW - 8], fill=t_mid, outline=t_dark)
    rd.rectangle([8, cx - 3, RW - 8, cx + 3], fill=t_mid, outline=t_dark)
    # Top/Bottom sails
    rd.rectangle([cx + 4, 12, cx + 26, cx - 12], fill=s_lit, outline=t_dark, width=2)
    rd.rectangle([cx - 26, cx + 12, cx - 4, RW - 12], fill=s_mid, outline=t_dark, width=2)
    for gy in range(18, cx - 12, 9):
        rd.line([(cx + 4, gy), (cx + 26, gy)], fill=t_mid, width=1)
    for gy in range(cx + 18, RW - 12, 9):
        rd.line([(cx - 26, gy), (cx - 4, gy)], fill=t_mid, width=1)
    # Left/Right sails
    rd.rectangle([12, cx - 26, cx - 12, cx - 4], fill=s_lit, outline=t_dark, width=2)
    rd.rectangle([cx + 12, cx + 4, RW - 12, cx + 26], fill=s_mid, outline=t_dark, width=2)
    for gx in range(18, cx - 12, 9):
        rd.line([(gx, cx - 26), (gx, cx - 4)], fill=t_mid, width=1)
    for gx in range(cx + 18, RW - 12, 9):
        rd.line([(gx, cx + 4), (gx, cx + 26)], fill=t_mid, width=1)
    rd.ellipse([cx - 9, cx - 9, cx + 9, cx + 9], fill=hex_rgba("#ffbd4a"), outline=t_dark, width=2)
    save_sprite("windmill_rotor.png", rimg, outline=True)

    # --- C. Detailed 16-Bit Brass Steam Train & Dining Carriage Sprite (240x96) ---
    TW, TH = 240, 96
    timg = Image.new("RGBA", (TW, TH), (0, 0, 0, 0))
    tpx = timg.load()
    td = ImageDraw.Draw(timg)
    gold_s, gold_m, gold_l = hex_rgba("#4a2d33"), hex_rgba("#b87c3b"), hex_rgba("#ffd66b")
    iron_s, iron_m, iron_l = hex_rgba("#191829"), hex_rgba("#3e3c54"), hex_rgba("#7a7691")

    # Passenger dining carriage on left (x = 10..108)
    draw_brick_textured_rect(tpx, 12, 30, 106, 74, r_deep, r_mid, r_lit, 10, 6)
    td.rectangle([8, 24, 110, 31], fill=iron_m, outline=INK, width=2)
    td.rectangle([12, 54, 106, 58], fill=gold_l)
    for wx in (20, 46, 72):
        td.rounded_rectangle([wx, 36, wx + 18, 52], radius=3, fill=hex_rgba("#fff2b2"), outline=INK, width=2)
        # Tiny pixel passenger silhouette sipping hot soup inside window!
        td.ellipse([wx + 6, 40, wx + 12, 46], fill=hex_rgba("#523240"))
        td.rectangle([wx + 4, 46, wx + 14, 51], fill=hex_rgba("#523240"))

    # Coupling link
    td.rectangle([106, 62, 118, 68], fill=iron_m, outline=INK)

    # Locomotive cab & brass boiler on right (x = 116..226)
    draw_brick_textured_rect(tpx, 116, 22, 154, 74, r_deep, r_mid, r_lit, 8, 6)
    td.rounded_rectangle([124, 30, 146, 48], radius=3, fill=hex_rgba("#fff2b2"), outline=INK, width=2)
    draw_brick_textured_rect(tpx, 154, 38, 214, 72, gold_s, gold_m, gold_l, 12, 5)
    # Brass boiler bands
    for bx in (164, 182, 200):
        td.rectangle([bx, 37, bx + 3, 72], fill=gold_l, outline=INK)
    # Smokestack + steam dome
    td.polygon([(194, 38), (206, 38), (210, 14), (190, 14)], fill=iron_m, outline=INK)
    td.rounded_rectangle([170, 28, 184, 39], radius=5, fill=gold_l, outline=INK)
    # Glowing amber headlamp & cowcatcher on nose (right side x = 214..234)
    td.rectangle([214, 42, 226, 56], fill=hex_rgba("#fff5c0"), outline=gold_s, width=2)
    td.polygon([(214, 72), (234, 78), (214, 78)], fill=iron_l, outline=INK)
    # Spoked driving wheels along bottom (y = 66..90)
    for wx in (26, 58, 90, 134, 166, 198):
        td.ellipse([wx - 11, 66, wx + 11, 88], fill=r_mid, outline=INK, width=2)
        td.ellipse([wx - 7, 70, wx + 7, 84], fill=iron_s, outline=gold_l, width=1)
        td.ellipse([wx - 3, 74, wx + 3, 80], fill=gold_l)
    td.rectangle([132, 75, 202, 79], fill=gold_l, outline=INK)
    save_sprite("brass_train_sprite.png", timg, outline=True)

    # --- D. Clockwork Sanctuary Golden Pagoda Spire (144x240) & Rotating Astrolabe Ring (136x72) ---
    SW, SH = 144, 240
    simg = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    spx = simg.load()
    sd = ImageDraw.Draw(simg)
    m_shad, m_mid, m_lit = hex_rgba("#2f2f4d"), hex_rgba("#8f8da8"), hex_rgba("#ebe3d5")
    c_cyan, c_core = hex_rgba("#2be8de"), hex_rgba("#d9fffc")

    # Tier 1 marble colonnade base
    draw_brick_textured_rect(spx, 28, 156, 116, 236, m_shad, m_mid, m_lit, 10, 6)
    for px_col in range(34, 112, 14):
        sd.rectangle([px_col, 164, px_col + 5, 228], fill=m_lit, outline=m_shad)
    # Tier 2 burnished gold clockwork core
    draw_brick_textured_rect(spx, 40, 92, 104, 156, gold_s, gold_m, gold_l, 8, 5)
    # Giant glowing cyan clockwork dial on Tier 2
    sd.ellipse([52, 104, 92, 144], fill=hex_rgba("#16233b"), outline=gold_l, width=3)
    sd.ellipse([58, 110, 86, 138], outline=c_cyan, width=2)
    sd.line([(72, 124), (72, 112)], fill=c_core, width=2)
    sd.line([(72, 124), (83, 124)], fill=gold_l, width=2)
    # Tier 3 upper marble lantern & golden spire tip
    draw_brick_textured_rect(spx, 50, 42, 94, 92, m_shad, m_mid, m_lit, 8, 5)
    sd.polygon([(72, 6), (56, 42), (88, 42)], fill=gold_l, outline=gold_s)
    # Glowing cyan vertical rune conduits
    for rx in (46, 72, 98):
        sd.rectangle([rx - 1, 46, rx + 1, 232], fill=c_cyan)
    # Pagoda eaves between tiers
    for ey, ew in [(152, 54), (90, 44), (40, 32)]:
        sd.polygon([(72 - ew, ey + 6), (72 + ew, ey + 6), (72 + ew - 8, ey - 3), (72 - ew + 8, ey - 3)], fill=gold_l, outline=gold_s)
    save_sprite("sanctuary_tower_sprite.png", simg, outline=True, exempt_bottom=True)

    # Marble Garden Pavilion Sprite (144x128)
    pimg = Image.new("RGBA", (144, 128), (0, 0, 0, 0))
    ppx = pimg.load()
    pd = ImageDraw.Draw(pimg)
    draw_brick_textured_rect(ppx, 16, 102, 128, 126, m_shad, m_mid, m_lit, 10, 5)
    for cx_p in (26, 54, 88, 114):
        draw_brick_textured_rect(ppx, cx_p, 52, cx_p + 8, 102, m_shad, m_mid, m_lit, 4, 8)
    # Curved golden temple roof
    for y in range(20, 54):
        u = (y - 20) / 34.0
        hw = int(14 + (u ** 0.75) * 52)
        for x in range(72 - hw, 72 + hw + 1):
            ux = (x - (72 - hw)) / max(1, 2 * hw)
            ppx[x, y] = gold_s if ux < 0.25 else (gold_m if ux < 0.68 else gold_l)
    # Hanging warm lanterns between columns
    for lx in (42, 72, 102):
        pd.line([(lx, 52), (lx, 62)], fill=INK, width=2)
        pd.rounded_rectangle([lx - 5, 62, lx + 5, 75], radius=3, fill=hex_rgba("#fff0a8"), outline=hex_rgba("#ff9d3b"), width=2)
    save_sprite("marble_pavilion_sprite.png", pimg, outline=True, exempt_bottom=True)

    # --- E. Colossal Pixel-Art Iron Anchor Chain & Glowing Sky-Stone Crystal Sprites ---
    CW, CH = 56, 200
    cimg = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cimg)
    for lk in range(7):
        y0 = 6 + lk * 27
        is_sever = (lk == 3)
        c_out = hex_rgba("#ff521c") if is_sever else iron_m
        c_hi = hex_rgba("#fff0a8") if is_sever else iron_l
        cd.rounded_rectangle([12, y0, 44, y0 + 32], radius=10, fill=c_out, outline=INK, width=2)
        cd.rounded_rectangle([20, y0 + 7, 36, y0 + 25], radius=5, fill=(0, 0, 0, 0), outline=INK, width=2)
        cd.line([(16, y0 + 5), (16, y0 + 26)], fill=c_hi, width=2)
    save_sprite("iron_chain_sprite.png", cimg, outline=True)

    # Multifaceted Glowing Sky-Stone Crystal Clusters (72x96)
    for cname, cols in [
        ("crystal_cyan.png", ("#185a6e", "#2bb8c2", "#64f5eb", "#e0fffc")),
        ("crystal_amber.png", ("#5e2228", "#cc522b", "#ff9e3b", "#fff3ba")),
    ]:
        kimg = Image.new("RGBA", (72, 96), (0, 0, 0, 0))
        kd = ImageDraw.Draw(kimg)
        c0, c1, c2, c3 = [hex_rgba(c) for c in cols]
        shards = [
            [(36, 8), (24, 34), (27, 88), (45, 88), (48, 34)],
            [(16, 28), (10, 48), (18, 90), (30, 88), (26, 44)],
            [(56, 24), (46, 44), (44, 88), (58, 90), (63, 46)],
        ]
        for poly in shards:
            kd.polygon(poly, fill=c1, outline=INK)
            # Right sunlit facet & bright ridge line
            mid_x = poly[0][0]
            kd.polygon([poly[0], poly[3], poly[4]], fill=c2)
            kd.line([poly[0], poly[2]], fill=c3, width=2)
        save_sprite(cname, kimg, outline=True, exempt_bottom=True)

    # Hanging Lantern Sprite (48x72)
    limg = Image.new("RGBA", (48, 72), (0, 0, 0, 0))
    ld = ImageDraw.Draw(limg)
    ld.rectangle([22, 2, 26, 24], fill=iron_m)
    ld.polygon([(12, 26), (36, 26), (30, 18), (18, 18)], fill=iron_l, outline=INK)
    ld.rounded_rectangle([14, 26, 34, 54], radius=4, fill=hex_rgba("#fff3ba"), outline=hex_rgba("#ff9d3b"), width=2)
    ld.line([(24, 26), (24, 54)], fill=iron_s, width=2)
    ld.polygon([(12, 54), (36, 54), (28, 62), (20, 62)], fill=iron_m, outline=INK)
    save_sprite("hanging_lantern_sprite.png", limg, outline=True)


# =============================================================================
# 4. DETAILED 16-BIT RPG 2D CHARACTER SPRITES (48x64)
# =============================================================================
def make_rpg_character_sprites():
    roles = [
        ("char_baker.png", "#a83842", "#e37254", "#4a3228", "#f7d5b5", "bread"),
        ("char_railworker.png", "#2b4570", "#5278b8", "#2b2638", "#f7d5b5", "hammer"),
        ("char_scholar.png", "#e0d6c8", "#f5CA56", "#382438", "#f7d5b5", "lantern"),
        ("char_miner.png", "#2e2c42", "#59546e", "#1c1a2b", "#d4c5b4", "mask_pick"),
    ]
    for fname, cloak_s, cloak_l, hair_c, skin_c, prop in roles:
        W, H = 48, 64
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        cs, cl = hex_rgba(cloak_s), hex_rgba(cloak_l)
        hc, sc = hex_rgba(hair_c), hex_rgba(skin_c)

        # Boots & legs (y = 48..61)
        d.rectangle([17, 48, 22, 61], fill=hex_rgba("#2b1e28"))
        d.rectangle([26, 48, 31, 61], fill=hex_rgba("#3d2b38"))
        # Flowing pixel-art cloak & tunic (y = 26..51)
        d.polygon([(16, 26), (32, 26), (36, 50), (12, 50)], fill=cs)
        d.polygon([(22, 26), (32, 26), (35, 50), (20, 50)], fill=cl)
        # Belt & buckle
        d.rectangle([15, 39, 33, 42], fill=hex_rgba("#382428"))
        d.rectangle([22, 39, 26, 42], fill=hex_rgba("#ffda66"))
        # Head & Hood/Hair (y = 10..26)
        d.rounded_rectangle([16, 11, 32, 26], radius=5, fill=sc)
        d.polygon([(14, 16), (24, 8), (34, 16), (33, 23), (30, 14), (18, 14), (15, 23)], fill=hc)
        # Crisp 16-bit RPG pixel eyes
        d.rectangle([20, 17, 22, 21], fill=INK)
        d.rectangle([27, 17, 29, 21], fill=INK)

        if prop == "bread":
            # Warm golden bread basket held in front
            d.rounded_rectangle([28, 32, 41, 41], radius=3, fill=hex_rgba("#e8a84e"), outline=hex_rgba("#8c5230"))
            d.ellipse([30, 29, 39, 35], fill=hex_rgba("#ffd97d"))
        elif prop == "hammer":
            # Iron rail hammer + glowing hot rail spike
            d.rectangle([34, 20, 37, 44], fill=hex_rgba("#7a523b"))
            d.rectangle([30, 17, 42, 23], fill=hex_rgba("#8a889e"))
            d.rectangle([32, 54, 43, 59], fill=hex_rgba("#ffbd4a"))
        elif prop == "lantern":
            # Glowing cyan sanctuary lantern
            d.line([(35, 32), (35, 40)], fill=INK, width=2)
            d.rounded_rectangle([31, 40, 39, 50], radius=2, fill=hex_rgba("#d4fffc"), outline=hex_rgba("#2be8de"), width=2)
        elif prop == "mask_pick":
            # Glowing cyan respirator visor + sky-stone crystal
            d.rectangle([19, 19, 30, 24], fill=hex_rgba("#45f0e5"))
            d.polygon([(36, 30), (32, 38), (36, 45), (41, 38)], fill=hex_rgba("#64f5eb"))

        save_sprite(fname, img, outline=True, exempt_bottom=True)


def main():
    generate_planet_ball_textures()
    # Trees for all biomes
    make_detailed_tree_sprite(
        "tree_oak_a.png",
        ("#12212e", "#1f4242", "#3b6e4c", "#74a653", "#b8d96c"),
        ("#1f1424", "#5c3b33", "#96664b"),
        pine=False,
        seed=11,
    )
    make_detailed_tree_sprite(
        "tree_oak_b.png",
        ("#142430", "#244a45", "#437850", "#82b359", "#c7e376"),
        ("#1f1424", "#634036", "#9e6d52"),
        pine=False,
        seed=29,
    )
    make_detailed_tree_sprite(
        "tree_pine_a.png",
        ("#0f1a29", "#1a333d", "#2b574a", "#588c56", "#8fc26b"),
        ("#1c1221", "#52342d", "#855842"),
        pine=True,
        seed=43,
    )
    make_detailed_tree_sprite(
        "tree_gold_a.png",
        ("#29172b", "#5e2d33", "#a65838", "#e39848", "#ffe074"),
        ("#1f1424", "#5c3b33", "#96664b"),
        pine=False,
        seed=71,
    )
    make_bush_and_flower_sprites()
    make_architecture_sprites()
    make_rpg_character_sprites()
    print(f"[OK] Generated detailed 2D pixel-art sprite library + 4 spherical planet textures -> {SPRITES_DIR}")


if __name__ == "__main__":
    main()
