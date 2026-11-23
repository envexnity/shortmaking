"""
textures_factory.py — High-Resolution (1024-2048px) Stylized Painted Texture,
Prop Graphic, and BIG Expressive Face Library Generator for Df1kubCJ-o0 Remake v2.
Copies every visual texture, clothing detail, signage, and dial from the OG reel.
"""
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROJ_DIR = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking\videos\roblox-reel-Df1kubCJ-o0-v2")
TEX_ENV = PROJ_DIR / "textures" / "env"
TEX_FACES = PROJ_DIR / "textures" / "faces"
TEX_PROPS = PROJ_DIR / "textures" / "props"
TEX_CHARS = PROJ_DIR / "textures" / "chars"
for d in (TEX_ENV, TEX_FACES, TEX_PROPS, TEX_CHARS):
    d.mkdir(parents=True, exist_ok=True)


def get_font(size: int, bold: bool = True):
    candidates = (
        ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/calibrib.ttf"]
        if bold
        else ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"]
    )
    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def add_grain(im: Image.Image, amp: int = 8, seed: int = 1) -> Image.Image:
    rng = random.Random(seed)
    w, h = im.size
    px = im.load()
    # Fast low-res noise upscaled softly for painterly warmth
    nw, nh = max(64, w // 4), max(64, h // 4)
    noise = Image.new("L", (nw, nh))
    npx = noise.load()
    for y in range(nh):
        for x in range(nw):
            npx[x, y] = 128 + rng.randint(-amp * 2, amp * 2)
    noise = noise.resize((w, h), Image.Resampling.BILINEAR)
    # Blend subtly via RGB math in PIL
    import numpy as np
    arr = np.array(im, dtype=np.int16)
    narr = np.array(noise, dtype=np.int16) - 128
    if arr.ndim == 3 and arr.shape[2] >= 3:
        arr[:, :, :3] = np.clip(arr[:, :, :3] + (narr[:, :, None] // 2), 0, 255)
    return Image.fromarray(arr.astype(np.uint8), mode=im.mode)


# ==================== 1. ENVIRONMENT & CLOTHING TEXTURES ====================

def gen_wood_planks(path_base: Path, palette: list[tuple[int, int, int]], seed: int = 10, rows: int = 8, cols: int = 3):
    S = 1024
    col_im = Image.new("RGB", (S, S), palette[0])
    bump_im = Image.new("L", (S, S), 175)
    dc = ImageDraw.Draw(col_im)
    db = ImageDraw.Draw(bump_im)
    rng = random.Random(seed)
    rh = S // rows
    cw = S // cols
    for r in range(rows):
        y0, y1 = r * rh, (r + 1) * rh
        off = (r % 2) * (cw // 2) + rng.randint(-28, 28)
        for c in range(-1, cols + 1):
            x0, x1 = c * cw + off, (c + 1) * cw + off
            base_c = rng.choice(palette)
            shift = rng.randint(-10, 10)
            c_plank = tuple(max(0, min(255, v + shift)) for v in base_c)
            dc.rectangle([x0, y0, x1, y1], fill=c_plank)
            db.rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 2], fill=rng.randint(170, 200))
            # Organic wood grain lines along X
            for _ in range(18):
                gy = rng.randint(y0 + 5, max(y0 + 6, y1 - 5))
                gx0 = rng.randint(x0, x0 + cw // 2)
                gx1 = min(x1 - 4, gx0 + rng.randint(80, cw))
                gc = tuple(max(0, min(255, v - rng.randint(10, 24))) for v in c_plank)
                dc.line([(gx0, gy), (gx1, gy)], fill=gc, width=rng.randint(1, 3))
                db.line([(gx0, gy), (gx1, gy)], fill=145, width=2)
            # Crisp dark plank joint seam
            seam_c = tuple(max(0, v - 52) for v in palette[0])
            dc.rectangle([x0, y0, x1, y0 + 4], fill=seam_c)
            dc.rectangle([x0, y0, x0 + 4, y1], fill=seam_c)
            db.rectangle([x0, y0, x1, y0 + 4], fill=45)
            db.rectangle([x0, y0, x0 + 4, y1], fill=45)
    col_im = add_grain(col_im, 7, seed)
    col_im.save(str(path_base) + ".png")
    bump_im.filter(ImageFilter.GaussianBlur(0.8)).save(str(path_base) + "_bump.png")


def gen_brick_wainscot():
    S = 1024
    col_im = Image.new("RGB", (S, S), (195, 224, 238))  # Soft grout
    bump_im = Image.new("L", (S, S), 70)
    dc = ImageDraw.Draw(col_im)
    db = ImageDraw.Draw(bump_im)
    rng = random.Random(22)
    rows, cols = 10, 5
    rh, cw = S // rows, S // cols
    pad = 7
    base_bricks = [(56, 138, 188), (64, 148, 198), (50, 130, 178), (72, 154, 204)]
    for r in range(rows):
        off = (cw // 2) if (r % 2 == 1) else 0
        for c in range(-1, cols + 1):
            x0, y0 = c * cw + off + pad, r * rh + pad
            x1, y1 = (c + 1) * cw + off - pad, (r + 1) * rh - pad
            bc = rng.choice(base_bricks)
            dc.rounded_rectangle([x0, y0, x1, y1], radius=8, fill=bc)
            # Highlight top bevel edge
            hi = tuple(min(255, v + 22) for v in bc)
            dc.line([(x0 + 8, y0 + 3), (x1 - 8, y0 + 3)], fill=hi, width=3)
            db.rounded_rectangle([x0, y0, x1, y1], radius=8, fill=rng.randint(190, 220))
    col_im = add_grain(col_im, 6, 22)
    col_im.save(TEX_ENV / "brick_blue_wainscot.png")
    bump_im.filter(ImageFilter.GaussianBlur(1.2)).save(TEX_ENV / "brick_blue_wainscot_bump.png")


def gen_diner_tiles():
    S = 1024
    col_im = Image.new("RGB", (S, S), (205, 194, 174))  # Warm taupe grout
    bump_im = Image.new("L", (S, S), 65)
    dc = ImageDraw.Draw(col_im)
    db = ImageDraw.Draw(bump_im)
    rng = random.Random(33)
    n = 8
    ts = S // n
    pad = 5
    for r in range(n):
        for c in range(n):
            x0, y0 = c * ts + pad, r * ts + pad
            x1, y1 = (c + 1) * ts - pad, (r + 1) * ts - pad
            v = rng.randint(-6, 6)
            tile_c = (242 + v, 232 + v, 214 + v)
            dc.rounded_rectangle([x0, y0, x1, y1], radius=8, fill=tile_c)
            db.rounded_rectangle([x0, y0, x1, y1], radius=8, fill=220)
    col_im = add_grain(col_im, 4, 33)
    col_im.save(TEX_ENV / "tile_cream_diner.png")
    bump_im.filter(ImageFilter.GaussianBlur(1.0)).save(TEX_ENV / "tile_cream_diner_bump.png")


def gen_asphalt_speckled():
    S = 1024
    col_im = Image.new("RGB", (S, S), (46, 51, 64))
    bump_im = Image.new("L", (S, S), 128)
    dc = ImageDraw.Draw(col_im)
    db = ImageDraw.Draw(bump_im)
    rng = random.Random(44)
    # Matching OG speckled asphalt aggregate dots!
    for _ in range(2600):
        x = rng.randint(0, S - 1)
        y = rng.randint(0, S - 1)
        rad = rng.choice([2, 2, 3, 4, 5])
        tone = rng.choice([(78, 84, 98), (98, 106, 122), (34, 38, 48), (125, 134, 148)])
        dc.ellipse([x - rad, y - rad, x + rad, y + rad], fill=tone)
        db.ellipse([x - rad, y - rad, x + rad, y + rad], fill=175 if tone[0] > 70 else 95)
    col_im = add_grain(col_im, 6, 44)
    col_im.save(TEX_ENV / "asphalt_speckled.png")
    bump_im.filter(ImageFilter.GaussianBlur(0.8)).save(TEX_ENV / "asphalt_speckled_bump.png")


def gen_sidewalk_pavers():
    S = 1024
    col_im = Image.new("RGB", (S, S), (150, 158, 172))
    bump_im = Image.new("L", (S, S), 65)
    dc = ImageDraw.Draw(col_im)
    db = ImageDraw.Draw(bump_im)
    rng = random.Random(55)
    rows, cols = 8, 4
    rh, cw = S // rows, S // cols
    pad = 5
    for r in range(rows):
        off = (cw // 2) if (r % 2 == 1) else 0
        for c in range(-1, cols + 1):
            x0, y0 = c * cw + off + pad, r * rh + pad
            x1, y1 = (c + 1) * cw + off - pad, (r + 1) * rh - pad
            s = rng.randint(-12, 12)
            pc = (204 + s, 210 + s, 222 + s)
            dc.rounded_rectangle([x0, y0, x1, y1], radius=6, fill=pc)
            db.rounded_rectangle([x0, y0, x1, y1], radius=6, fill=205)
    col_im = add_grain(col_im, 5, 55)
    col_im.save(TEX_ENV / "sidewalk_pavers.png")
    bump_im.filter(ImageFilter.GaussianBlur(1.0)).save(TEX_ENV / "sidewalk_pavers_bump.png")


def gen_wrapper_paper():
    S = 1024
    # Rich golden-amber wax paper (stays saturated under AgX, never washes to pale cream!)
    col_im = Image.new("RGB", (S, S), (236, 174, 32))
    bump_im = Image.new("L", (S, S), 140)
    dc = ImageDraw.Draw(col_im)
    db = ImageDraw.Draw(bump_im)
    # Iconic OG double-lined vibrant red-orange wax paper stripes
    cy = S // 2
    red_band = (212, 42, 24)
    red_thin = (224, 68, 34)
    dc.rectangle([0, cy - 42, S, cy + 42], fill=red_band)
    dc.rectangle([0, cy - 82, S, cy - 62], fill=red_thin)
    dc.rectangle([0, cy + 62, S, cy + 82], fill=red_thin)
    # Subtle folded paper crease lines for tactile wax paper sheen
    rng = random.Random(66)
    for _ in range(44):
        x0, y0 = rng.randint(0, S), rng.randint(0, S)
        ang = rng.uniform(0, math.pi * 2)
        ln = rng.randint(90, 280)
        x1, y1 = int(x0 + math.cos(ang) * ln), int(y0 + math.sin(ang) * ln)
        db.line([(x0, y0), (x1, y1)], fill=rng.choice([85, 195]), width=rng.randint(2, 5))
    col_im = add_grain(col_im, 6, 66)
    col_im.save(TEX_ENV / "wrapper_paper_yellow.png")
    bump_im.filter(ImageFilter.GaussianBlur(1.2)).save(TEX_ENV / "wrapper_paper_yellow_bump.png")


def gen_fabrics():
    S = 1024
    # 1. White cotton jersey knit with soft heather weave & crisp rib texture
    cot = Image.new("RGB", (S, S), (236, 238, 242))
    cot_b = Image.new("L", (S, S), 128)
    dc = ImageDraw.Draw(cot)
    db = ImageDraw.Draw(cot_b)
    for x in range(0, S, 8):
        dc.line([(x, 0), (x, S)], fill=(224, 227, 234), width=3)
        db.line([(x, 0), (x, S)], fill=165, width=3)
    for y in range(0, S, 10):
        dc.line([(0, y), (S, y)], fill=(230, 233, 238), width=2)
    cot = add_grain(cot, 5, 71)
    cot.save(TEX_ENV / "fabric_cotton_white.png")
    cot_b.filter(ImageFilter.GaussianBlur(0.7)).save(TEX_ENV / "fabric_cotton_white_bump.png")

    # 2. Deep indigo denim twill with pronounced weave & golden stitch flecks
    den = Image.new("RGB", (S, S), (28, 52, 106))
    den_b = Image.new("L", (S, S), 128)
    dd = ImageDraw.Draw(den)
    ddb = ImageDraw.Draw(den_b)
    for k in range(-S, S * 2, 9):
        dd.line([(k, 0), (k + S, S)], fill=(42, 74, 142), width=3)
        ddb.line([(k, 0), (k + S, S)], fill=175, width=3)
    for k in range(-S, S * 2, 18):
        dd.line([(k, S), (k + S, 0)], fill=(22, 42, 88), width=2)
    den = add_grain(den, 8, 72)
    den.save(TEX_ENV / "fabric_denim_indigo.png")
    den_b.filter(ImageFilter.GaussianBlur(0.6)).save(TEX_ENV / "fabric_denim_indigo_bump.png")

    # 3. Burgundy & Navy tailored wool suits + Knit Sweater
    for fname, base_c, alt_c, seed in [
        ("fabric_suit_burgundy", (134, 26, 44), (112, 18, 34), 73),
        ("fabric_suit_navy", (24, 38, 72), (34, 52, 92), 74),
        ("fabric_knit_rib", (215, 215, 220), (185, 185, 195), 75),
    ]:
        im = Image.new("RGB", (S, S), base_c)
        bm = Image.new("L", (S, S), 128)
        di = ImageDraw.Draw(im)
        dbi = ImageDraw.Draw(bm)
        step = 16 if "knit" in fname else 8
        for x in range(0, S, step):
            di.line([(x, 0), (x, S)], fill=alt_c, width=3 if "knit" in fname else 2)
            dbi.line([(x, 0), (x, S)], fill=175 if "knit" in fname else 150, width=3 if "knit" in fname else 2)
        im = add_grain(im, 5, seed)
        im.save(TEX_ENV / f"{fname}.png")
        bm.filter(ImageFilter.GaussianBlur(0.8)).save(TEX_ENV / f"{fname}_bump.png")


# ==================== 2. CLOCK DIALS & BUN TOWN SIGNAGE ====================

def gen_clock_dials():
    for fname, is_alarm in [("clock_stopwatch_dial.png", False), ("clock_5am_dial.png", True)]:
        S = 1024
        im = Image.new("RGB", (S, S), (250, 248, 242))
        d = ImageDraw.Draw(im)
        cx, cy = S // 2, S // 2
        d.ellipse([28, 28, S - 28, S - 28], fill=(252, 250, 246), outline=(42, 48, 58), width=14)
        # Red 4-second sector wedge on stopwatch
        if not is_alarm:
            d.pieslice([110, 110, S - 110, S - 110], start=-90, end=-66, fill=(254, 202, 202))
        for i in range(60):
            ang = math.radians(i * 6 - 90)
            is_maj = (i % 5 == 0)
            r0 = 365 if is_maj else 400
            r1 = 445
            d.line(
                [(cx + math.cos(ang) * r0, cy + math.sin(ang) * r0),
                 (cx + math.cos(ang) * r1, cy + math.sin(ang) * r1)],
                fill=(30, 34, 42),
                width=16 if is_maj else 6,
            )
        if is_alarm:
            # 5:00 hands
            f = get_font(66)
            d.text((cx - 88, cy + 120), "5:00 AM", fill=(20, 140, 130), font=f)
            # Hour hand -> 5, Minute hand -> 12
            a_hr = math.radians(5 * 30 - 90)
            d.line([(cx, cy), (cx + math.cos(a_hr) * 230, cy + math.sin(a_hr) * 230)], fill=(25, 30, 38), width=26)
            d.line([(cx, cy), (cx, cy - 340)], fill=(25, 30, 38), width=18)
        else:
            # Stopwatch red sweeping hand around 4s
            a_sw = math.radians(24 - 90)
            d.line([(cx, cy), (cx + math.cos(a_sw) * 355, cy + math.sin(a_sw) * 355)], fill=(225, 35, 45), width=20)
        d.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=(225, 35, 45), outline=(25, 28, 34), width=6)
        im.save(TEX_PROPS / fname)


def draw_smiling_burger_badge(d: ImageDraw.ImageDraw, cx: int, cy: int, rad: int):
    # Circular teal ring + warm cream center + cute smiling cartoon burger
    d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=(20, 148, 138), outline=(250, 245, 232), width=max(6, rad // 14))
    ir = int(rad * 0.84)
    d.ellipse([cx - ir, cy - ir, cx + ir, cy + ir], fill=(250, 246, 235))
    bw = int(rad * 0.62)
    # Top bun
    d.pieslice([cx - bw, cy - int(rad * 0.50), cx + bw, cy + int(rad * 0.08)], 180, 360, fill=(235, 162, 74), outline=(42, 26, 18), width=4)
    # Eyes & happy smile on top bun!
    d.ellipse([cx - bw // 3 - 7, cy - int(rad * 0.30), cx - bw // 3 + 7, cy - int(rad * 0.18)], fill=(30, 24, 22))
    d.ellipse([cx + bw // 3 - 7, cy - int(rad * 0.30), cx + bw // 3 + 7, cy - int(rad * 0.18)], fill=(30, 24, 22))
    d.arc([cx - 18, cy - int(rad * 0.24), cx + 18, cy - int(rad * 0.10)], 15, 165, fill=(30, 24, 22), width=4)
    # Lettuce, patty, bottom bun
    d.rectangle([cx - bw - 6, cy - int(rad * 0.12), cx + bw + 6, cy - int(rad * 0.02)], fill=(74, 200, 100))
    d.rounded_rectangle([cx - bw - 3, cy - int(rad * 0.02), cx + bw + 3, cy + int(rad * 0.14)], radius=8, fill=(110, 52, 26))
    d.rounded_rectangle([cx - bw + 2, cy + int(rad * 0.14), cx + bw - 2, cy + int(rad * 0.32)], radius=12, fill=(224, 152, 68), outline=(42, 26, 18), width=3)


def gen_prop_graphics():
    # 1. Circular Bun Town Logo Badge
    S = 1024
    logo = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dl = ImageDraw.Draw(logo)
    draw_smiling_burger_badge(dl, S // 2, S // 2, 480)
    logo.save(TEX_PROPS / "buntown_logo_circle.png")

    # 2. Marquee Sign: BUN TOWN
    sw, sh = 1600, 440
    sm = Image.new("RGB", (sw, sh), (252, 246, 232))
    dm = ImageDraw.Draw(sm)
    dm.rounded_rectangle([14, 14, sw - 14, sh - 14], radius=36, fill=(252, 246, 232), outline=(18, 138, 130), width=20)
    dm.rounded_rectangle([38, 38, sw - 38, sh - 38], radius=24, outline=(228, 82, 52), width=8)
    f_bt = get_font(195)
    txt = "BUN TOWN"
    bb = dm.textbbox((0, 0), txt, font=f_bt)
    dm.text(((sw - (bb[2] - bb[0])) // 2 + 6, (sh - (bb[3] - bb[1])) // 2 - 22), txt, fill=(228, 82, 52), font=f_bt)
    dm.text(((sw - (bb[2] - bb[0])) // 2, (sh - (bb[3] - bb[1])) // 2 - 28), txt, fill=(16, 128, 120), font=f_bt)
    sm.save(TEX_PROPS / "sign_buntown_marquee.png")

    # 3. NOW HIRING: BURGER WRAPPER Poster
    hw, hh = 900, 1100
    hi = Image.new("RGB", (hw, hh), (252, 248, 238))
    dh = ImageDraw.Draw(hi)
    dh.rounded_rectangle([16, 16, hw - 16, hh - 16], radius=24, fill=(252, 248, 238), outline=(22, 30, 42), width=12)
    dh.rectangle([40, 40, hw - 40, 260], fill=(225, 58, 52))
    f_nh = get_font(104)
    f_bw = get_font(118)
    f_sm = get_font(54)
    for t, y, col, fn in [
        ("NOW HIRING", 88, (255, 255, 255), f_nh),
        ("BURGER", 370, (24, 30, 42), f_bw),
        ("WRAPPER", 520, (24, 30, 42), f_bw),
        ("APPLY INSIDE!", 760, (16, 132, 124), f_sm),
        ("MUST BE FAST", 860, (110, 115, 125), f_sm),
    ]:
        bb = dh.textbbox((0, 0), t, font=fn)
        dh.text(((hw - (bb[2] - bb[0])) // 2, y), t, fill=col, font=fn)
    hi.save(TEX_PROPS / "sign_now_hiring.png")

    # 4. Official Rejection Letter Card (exact OG match!)
    lw, lh = 1000, 1240
    lt = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    dlt = ImageDraw.Draw(lt)
    dlt.rounded_rectangle([24, 24, lw - 24, lh - 24], radius=54, fill=(252, 249, 242, 255), outline=(210, 204, 192, 255), width=10)
    draw_smiling_burger_badge(dlt, lw // 2, 195, 118)
    f_l1 = get_font(76, bold=False)
    f_l2 = get_font(94, bold=True)
    lines = [
        ("Thank you for", 420, f_l1, (38, 42, 52, 255)),
        ("wrapping", 555, f_l2, (20, 24, 32, 255)),
        ("my tie.", 705, f_l2, (20, 24, 32, 255)),
    ]
    for txt_l, ly, fn, col in lines:
        bb = dlt.textbbox((0, 0), txt_l, font=fn)
        dlt.text(((lw - (bb[2] - bb[0])) // 2, ly), txt_l, fill=col, font=fn)
    # Handwritten signature squiggle like OG
    dlt.line([(320, 960), (430, 930), (500, 965), (610, 925), (685, 955)], fill=(70, 95, 145, 255), width=10, joint="curve")
    lt.save(TEX_PROPS / "letter_tie.png")

    # 5. Wall Art Picture Frame inside Bun Town
    fw, fh = 800, 800
    fa = Image.new("RGB", (fw, fh), (242, 232, 212))
    dfa = ImageDraw.Draw(fa)
    draw_smiling_burger_badge(dfa, fw // 2, fh // 2, 290)
    fa.save(TEX_PROPS / "wall_burger_frame.png")

    # 6. Scoreboard Digit Atlas / Display Base
    sb = Image.new("RGB", (1024, 512), (18, 24, 34))
    dsb = ImageDraw.Draw(sb)
    dsb.rounded_rectangle([18, 18, 1006, 494], radius=32, fill=(18, 24, 34), outline=(245, 195, 45), width=16)
    f_hd = get_font(76)
    hdr = "ORDERS FILLED"
    bb = dsb.textbbox((0, 0), hdr, font=f_hd)
    dsb.text(((1024 - (bb[2] - bb[0])) // 2, 48), hdr, fill=(20, 195, 180), font=f_hd)
    sb.save(TEX_PROPS / "scoreboard_bg.png")


# ==================== 3. AUTHENTIC ROBLOX STUDIO 2-HALF CLOTHING ATLASES ====================

def _hex_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _adj(c: tuple[int, int, int], d: int) -> tuple[int, int, int]:
    return tuple(max(0, min(255, v + d)) for v in c)


def _new_fabric_atlas(base_hex: str, seed: int = 80, weave_step: int = 10, rib_v: bool = False):
    S = 1024
    c0 = _hex_rgb(base_hex)
    c1 = _adj(c0, -14)
    c2 = _adj(c0, 10)
    col = Image.new("RGB", (S, S), c0)
    bump = Image.new("L", (S, S), 128)
    dc, db = ImageDraw.Draw(col), ImageDraw.Draw(bump)
    if rib_v:
        for x in range(0, S, weave_step):
            dc.line([(x, 0), (x, S)], fill=c1, width=max(2, weave_step // 4))
            db.line([(x, 0), (x, S)], fill=165, width=max(2, weave_step // 4))
    else:
        for x in range(0, S, weave_step):
            dc.line([(x, 0), (x, S)], fill=c1, width=2)
            db.line([(x, 0), (x, S)], fill=148, width=2)
        for y in range(0, S, weave_step):
            dc.line([(0, y), (S, y)], fill=c2, width=1)
    # Subtle center divider seam between Front [0..512] and Back/Sides [512..1024]
    col = add_grain(col, 5, seed)
    return col, bump


def _draw_stitch(d: ImageDraw.ImageDraw, db: ImageDraw.ImageDraw, p0: tuple, p1: tuple, col: tuple, w: int = 4):
    d.line([p0, p1], fill=col, width=w)
    db.line([p0, p1], fill=82, width=w + 2)


def _draw_collar(dc, db, col_rib, seam_c, v_neck=False):
    # Front half centered at x=256, back half centered at x=768
    if v_neck:
        dc.polygon([(145, 0), (367, 0), (256, 360)], fill=(246, 248, 252), outline=seam_c)
        dc.polygon([(256, 260), (200, 0), (145, 0)], fill=col_rib)
        dc.polygon([(256, 260), (312, 0), (367, 0)], fill=col_rib)
    else:
        dc.pieslice([155, -72, 357, 86], 0, 180, fill=col_rib, outline=seam_c, width=6)
        dc.pieslice([178, -56, 334, 62], 0, 180, fill=_adj(col_rib, -18))
        # Rib tick marks along crew neck
        for ang_deg in range(15, 170, 12):
            a = math.radians(ang_deg)
            dc.line([(256 + math.cos(a) * 78, math.sin(a) * 58), (256 + math.cos(a) * 98, math.sin(a) * 80)], fill=seam_c, width=3)
        dc.pieslice([667, -42, 869, 46], 0, 180, fill=col_rib, outline=seam_c, width=5)
    db.arc([155, -72, 357, 86], 0, 180, fill=215, width=18)


def _draw_shoe_band(dc, db, shoe_c, sole_c=(244, 246, 250), lace_c=(235, 240, 248), is_dress=False):
    # Bottom 16% (y=860..1024) across BOTH halves (front & back/sides wrap around lower leg)
    y0 = 860
    dc.rectangle([0, y0, 1024, 1024], fill=shoe_c)
    db.rectangle([0, y0, 1024, 1024], fill=175)
    dc.rectangle([0, y0, 1024, y0 + 12], fill=_adj(shoe_c, -28))
    if not is_dress:
        # Crisp Roblox white midsole band along bottom + lace bars on front half (x=140..372)
        dc.rectangle([0, 976, 1024, 1024], fill=sole_c)
        dc.rectangle([0, 972, 1024, 978], fill=_adj(shoe_c, -25))
        # Rounded sneaker tongue & laces on front
        dc.rounded_rectangle([185, y0 + 14, 327, 965], radius=16, fill=_adj(shoe_c, 16), outline=_adj(shoe_c, -25), width=4)
        for ly in (888, 912, 936):
            dc.line([(204, ly), (308, ly)], fill=lace_c, width=7)
    else:
        dc.rectangle([0, 992, 1024, 1024], fill=_adj(shoe_c, 18))


def _save_char_tex(stem: str, col: Image.Image, bump: Image.Image):
    col.save(TEX_CHARS / f"{stem}.png")
    bump.filter(ImageFilter.GaussianBlur(0.8)).save(TEX_CHARS / f"{stem}_bump.png")


def gen_roblox_char_textures():
    # 1. ALEX (White ribbed crewneck cotton + indigo denim jeans w/ stitched pockets & dark navy sneakers)
    s_c, s_b = _new_fabric_atlas("#ECEEF2", seed=101, weave_step=9, rib_v=True)
    dc, db = ImageDraw.Draw(s_c), ImageDraw.Draw(s_b)
    _draw_collar(dc, db, (226, 230, 236), (172, 178, 188))
    for sx in (36, 476, 548, 988):
        _draw_stitch(dc, db, (sx, 0), (sx, 1024), (200, 206, 216), 3)
    _draw_stitch(dc, db, (0, 968), (1024, 968), (186, 192, 204), 4)
    _draw_stitch(dc, db, (0, 990), (1024, 990), (196, 202, 212), 3)
    _save_char_tex("shirt_alex", s_c, s_b)

    p_c, p_b = _new_fabric_atlas("#1C346A", seed=102, weave_step=8)
    dc, db = ImageDraw.Draw(p_c), ImageDraw.Draw(p_b)
    dc.rectangle([0, 0, 1024, 92], fill=(22, 40, 82))
    _draw_stitch(dc, db, (0, 92), (1024, 92), (62, 102, 176), 5)
    for lx in (95, 415, 620, 920):
        dc.rectangle([lx - 14, 4, lx + 14, 96], fill=(32, 58, 118), outline=(14, 26, 56), width=3)
    dc.arc([20, 48, 195, 250], 0, 95, fill=(92, 134, 210), width=5)
    dc.arc([317, 48, 492, 250], 85, 180, fill=(92, 134, 210), width=5)
    _draw_stitch(dc, db, (40, 100), (40, 855), (68, 106, 182), 5)
    _draw_stitch(dc, db, (472, 100), (472, 855), (68, 106, 182), 5)
    _draw_stitch(dc, db, (0, 836), (1024, 836), (82, 120, 196), 4)
    _draw_shoe_band(dc, db, (20, 34, 72))
    _save_char_tex("pants_alex", p_c, p_b)

    # 2. MANAGER (Burgundy suit jacket w/ white shirt V, notched lapels, pocket square, buttons + dark slacks)
    s_c, s_b = _new_fabric_atlas("#861A2C", seed=103, weave_step=9)
    dc, db = ImageDraw.Draw(s_c), ImageDraw.Draw(s_b)
    # White V shirt + dark burgundy lapels
    dc.polygon([(172, 0), (340, 0), (256, 370)], fill=(248, 250, 252))
    dc.polygon([(172, 0), (125, 0), (225, 370), (256, 370)], fill=(102, 16, 32), outline=(66, 10, 20), width=4)
    dc.polygon([(340, 0), (387, 0), (287, 370), (256, 370)], fill=(102, 16, 32), outline=(66, 10, 20), width=4)
    # Pocket square on viewer left (+X -> right side of front half x=338..420)
    dc.polygon([(336, 322), (424, 322), (410, 286), (376, 304), (350, 288)], fill=(245, 185, 35))
    dc.rectangle([330, 320, 428, 336], fill=(78, 12, 24))
    _draw_stitch(dc, db, (256, 370), (256, 1024), (66, 10, 20), 6)
    for by in (560, 740):
        dc.ellipse([238, by - 18, 274, by + 18], fill=(245, 178, 32), outline=(140, 88, 12), width=4)
    _draw_stitch(dc, db, (0, 980), (1024, 980), (66, 10, 20), 4)
    _save_char_tex("shirt_manager", s_c, s_b)

    p_c, p_b = _new_fabric_atlas("#34111C", seed=104, weave_step=10)
    dc, db = ImageDraw.Draw(p_c), ImageDraw.Draw(p_b)
    _draw_stitch(dc, db, (256, 0), (256, 860), (68, 28, 40), 5)
    _draw_shoe_band(dc, db, (22, 22, 26), is_dress=True)
    _save_char_tex("pants_manager", p_c, p_b)

    # 3. MAYOR (Navy double-breasted suit + white shirt V + brass buttons + belt & gold buckle + navy slacks)
    s_c, s_b = _new_fabric_atlas("#182648", seed=105, weave_step=9)
    dc, db = ImageDraw.Draw(s_c), ImageDraw.Draw(s_b)
    dc.polygon([(180, 0), (332, 0), (256, 330)], fill=(248, 250, 252))
    dc.polygon([(180, 0), (130, 0), (226, 330), (256, 330)], fill=(16, 26, 52), outline=(10, 16, 36), width=4)
    dc.polygon([(332, 0), (382, 0), (286, 330), (256, 330)], fill=(16, 26, 52), outline=(10, 16, 36), width=4)
    for bx in (188, 324):
        for by in (520, 680):
            dc.ellipse([bx - 16, by - 16, bx + 16, by + 16], fill=(245, 182, 36), outline=(146, 94, 14), width=3)
    dc.rectangle([0, 910, 1024, 1010], fill=(20, 22, 30))
    dc.rounded_rectangle([206, 918, 306, 1002], radius=10, outline=(245, 182, 36), width=12)
    _save_char_tex("shirt_mayor", s_c, s_b)

    p_c, p_b = _new_fabric_atlas("#182648", seed=106, weave_step=10)
    dc, db = ImageDraw.Draw(p_c), ImageDraw.Draw(p_b)
    _draw_stitch(dc, db, (256, 0), (256, 860), (42, 60, 104), 5)
    _draw_shoe_band(dc, db, (20, 22, 28), is_dress=True)
    _save_char_tex("pants_mayor", p_c, p_b)

    # 4. NEIGHBOR (Hot pink shirt w/ yellow lightning bolt + emerald green pants w/ dark sneakers)
    s_c, s_b = _new_fabric_atlas("#EC2E7A", seed=107, weave_step=9)
    dc, db = ImageDraw.Draw(s_c), ImageDraw.Draw(s_b)
    _draw_collar(dc, db, (210, 28, 102), (175, 18, 82))
    # Crisp iconic lightning bolt on chest
    bolt = [(274, 285), (195, 475), (252, 475), (222, 650), (322, 435), (264, 435)]
    dc.polygon(bolt, fill=(250, 204, 21), outline=(217, 119, 6), width=5)
    _draw_stitch(dc, db, (0, 972), (1024, 972), (185, 22, 88), 4)
    _save_char_tex("shirt_neighbor", s_c, s_b)

    p_c, p_b = _new_fabric_atlas("#15803D", seed=108, weave_step=9)
    dc, db = ImageDraw.Draw(p_c), ImageDraw.Draw(p_b)
    dc.rectangle([0, 0, 1024, 86], fill=(16, 102, 48))
    _draw_stitch(dc, db, (45, 92), (45, 855), (34, 168, 84), 4)
    _draw_stitch(dc, db, (467, 92), (467, 855), (34, 168, 84), 4)
    _draw_shoe_band(dc, db, (44, 54, 72))
    _save_char_tex("pants_neighbor", p_c, p_b)

    # 5. CROWD: Rock Guy, Grandma, Teal Friend (white heart), Mint Girl, Purple Hoodie
    s_c, s_b = _new_fabric_atlas("#EA580C", seed=109, weave_step=12, rib_v=True)
    dc, db = ImageDraw.Draw(s_c), ImageDraw.Draw(s_b)
    _draw_collar(dc, db, (194, 65, 12), (154, 52, 10))
    dc.rectangle([0, 930, 1024, 1024], fill=(208, 72, 12))
    _save_char_tex("shirt_rock_guy", s_c, s_b)
    p_c, p_b = _new_fabric_atlas("#334155", seed=110, weave_step=9)
    dc, db = ImageDraw.Draw(p_c), ImageDraw.Draw(p_b)
    _draw_stitch(dc, db, (48, 0), (48, 855), (72, 86, 108), 4)
    _draw_shoe_band(dc, db, (24, 30, 42))
    _save_char_tex("pants_rock_guy", p_c, p_b)

    s_c, s_b = _new_fabric_atlas("#A855F7", seed=111, weave_step=12, rib_v=True)
    dc, db = ImageDraw.Draw(s_c), ImageDraw.Draw(s_b)
    dc.polygon([(176, 0), (336, 0), (256, 260)], fill=(248, 250, 252))
    dc.line([(256, 260), (256, 1024)], fill=(126, 34, 206), width=14)
    for by in (380, 560, 740, 910):
        dc.ellipse([240, by - 16, 272, by + 16], fill=(226, 232, 240), outline=(107, 33, 168), width=4)
    _save_char_tex("shirt_grandma", s_c, s_b)
    p_c, p_b = _new_fabric_atlas("#4C1D95", seed=112, weave_step=10)
    dc, db = ImageDraw.Draw(p_c), ImageDraw.Draw(p_b)
    _draw_shoe_band(dc, db, (30, 24, 58), is_dress=True)
    _save_char_tex("pants_grandma", p_c, p_b)

    s_c, s_b = _new_fabric_atlas("#14B8A6", seed=113, weave_step=11, rib_v=True)
    dc, db = ImageDraw.Draw(s_c), ImageDraw.Draw(s_b)
    _draw_collar(dc, db, (15, 148, 136), (13, 120, 110))
    # Crisp centered white heart on chest!
    hc_x, hc_y = 256, 445
    dc.ellipse([hc_x - 86, hc_y - 72, hc_x + 4, hc_y + 18], fill=(250, 252, 255))
    dc.ellipse([hc_x - 4, hc_y - 72, hc_x + 86, hc_y + 18], fill=(250, 252, 255))
    dc.polygon([(hc_x - 82, hc_y - 8), (hc_x + 82, hc_y - 8), (hc_x, hc_y + 92)], fill=(250, 252, 255))
    dc.rectangle([0, 940, 1024, 1024], fill=(15, 148, 136))
    _save_char_tex("shirt_teal_friend", s_c, s_b)
    p_c, p_b = _new_fabric_atlas("#CBD5E1", seed=114, weave_step=9)
    dc, db = ImageDraw.Draw(p_c), ImageDraw.Draw(p_b)
    _draw_stitch(dc, db, (50, 0), (50, 855), (148, 163, 184), 4)
    _draw_stitch(dc, db, (462, 0), (462, 855), (148, 163, 184), 4)
    _draw_shoe_band(dc, db, (30, 41, 59))
    _save_char_tex("pants_teal_friend", p_c, p_b)

    s_c, s_b = _new_fabric_atlas("#5EEAD4", seed=115, weave_step=10)
    dc, db = ImageDraw.Draw(s_c), ImageDraw.Draw(s_b)
    _draw_collar(dc, db, (45, 212, 191), (20, 184, 166))
    dc.rectangle([0, 955, 1024, 1024], fill=(236, 72, 153))
    _save_char_tex("shirt_mint_girl", s_c, s_b)
    p_c, p_b = _new_fabric_atlas("#EC4899", seed=116, weave_step=9)
    dc, db = ImageDraw.Draw(p_c), ImageDraw.Draw(p_b)
    # Top 42% pink pleated skirt/shorts, middle skin knees, white socks, pink sneakers!
    dc.rectangle([0, 420, 1024, 790], fill=(243, 200, 166))
    dc.rectangle([0, 790, 1024, 865], fill=(248, 250, 252))
    for px in range(40, 512, 70):
        _draw_stitch(dc, db, (px, 0), (px, 415), (190, 24, 93), 4)
    _draw_shoe_band(dc, db, (236, 72, 153))
    _save_char_tex("pants_mint_girl", p_c, p_b)

    s_c, s_b = _new_fabric_atlas("#7C3AED", seed=117, weave_step=10)
    dc, db = ImageDraw.Draw(s_c), ImageDraw.Draw(s_b)
    _draw_collar(dc, db, (91, 33, 182), (76, 29, 149))
    # Drawstrings + kangaroo pocket + ribbed bottom band
    for dx in (212, 300):
        dc.line([(dx, 45), (dx, 305)], fill=(248, 250, 252), width=12)
        dc.ellipse([dx - 8, 298, dx + 8, 318], fill=(226, 232, 240))
    dc.polygon([(95, 650), (417, 650), (445, 920), (67, 920)], fill=(109, 40, 217), outline=(76, 29, 149), width=5)
    dc.rectangle([0, 930, 1024, 1024], fill=(91, 33, 182))
    _save_char_tex("shirt_purple_hoodie", s_c, s_b)
    p_c, p_b = _new_fabric_atlas("#1E293B", seed=118, weave_step=9)
    dc, db = ImageDraw.Draw(p_c), ImageDraw.Draw(p_b)
    _draw_stitch(dc, db, (50, 0), (50, 855), (51, 65, 85), 4)
    _draw_shoe_band(dc, db, (15, 23, 42))
    _save_char_tex("pants_purple_hoodie", p_c, p_b)


# ==================== 4. BIG EXPRESSIVE ROBLOX STUDIO 2K FACE LIBRARY ====================

def draw_glossy_eye(d: ImageDraw.ImageDraw, cx: int, cy: int, rx: int, ry: int, sclera_ring: bool = False):
    """Authentic Roblox Studio solid glossy-black vertical oval eye with bright white upper-left catchlight."""
    blk = (18, 18, 24, 255)
    wht = (255, 255, 255, 255)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=blk)
    cr = max(12, int(rx * 0.36))
    d.ellipse([cx - int(rx * 0.56), cy - int(ry * 0.56), cx - int(rx * 0.56) + cr, cy - int(ry * 0.56) + cr], fill=wht)
    sr = max(6, rx // 6)
    d.ellipse([cx + int(rx * 0.25), cy + int(ry * 0.22), cx + int(rx * 0.25) + sr, cy + int(ry * 0.22) + sr], fill=(225, 235, 255, 200))


def make_face_base(kind: str) -> Image.Image:
    """
    1024x1024 RGBA face overlay.
    Designed to span ~76% of the front face of our rounded-bevel head so eyes/brows/mouths read BIG and crisp!
    """
    S = 1024
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    blk = (22, 20, 26, 255)
    dark_red = (108, 22, 32, 255)
    tongue = (224, 92, 106, 255)
    wht = (255, 255, 255, 255)
    brow_brown = (48, 28, 18, 255)
    brow_gray = (128, 134, 146, 255)

    lx, rx_pos = 342, 682
    ey = 470

    # --- BLINK HELPERS ---
    def draw_eyes_state(blink_state: str, erx=58, ery=76, sclera=False):
        if blink_state == "open":
            draw_glossy_eye(d, lx, ey, erx, ery, sclera_ring=sclera)
            draw_glossy_eye(d, rx_pos, ey, erx, ery, sclera_ring=sclera)
        elif blink_state == "half":
            # Lower half visible with thick upper lid line
            draw_glossy_eye(d, lx, ey + 14, erx, ery // 2, sclera_ring=False)
            draw_glossy_eye(d, rx_pos, ey + 14, erx, ery // 2, sclera_ring=False)
            d.line([(lx - erx - 8, ey + 4), (lx + erx + 8, ey + 4)], fill=blk, width=18)
            d.line([(rx_pos - erx - 8, ey + 4), (rx_pos + erx + 8, ey + 4)], fill=blk, width=18)
        elif blink_state == "closed":
            d.arc([lx - erx - 6, ey - 18, lx + erx + 6, ey + 44], 15, 165, fill=blk, width=20)
            d.arc([rx_pos - erx - 6, ey - 18, rx_pos + erx + 6, ey + 44], 15, 165, fill=blk, width=20)

    def draw_open_smile(x0: int, y_top: int, x1: int, y_bot: int, has_teeth: bool = True, has_tongue: bool = True):
        """Draw a crisp D-shaped open mouth whose flat top edge is strictly at y_top."""
        h = y_bot - y_top
        bbox = [x0, y_top - h, x1, y_bot]
        d.pieslice(bbox, 0, 180, fill=dark_red)
        if has_teeth:
            th = max(18, int(h * 0.28))
            d.rectangle([x0 + 18, y_top + 4, x1 - 18, y_top + th], fill=wht)
        if has_tongue:
            tw = int((x1 - x0) * 0.48)
            cxm = (x0 + x1) // 2
            d.ellipse([cxm - tw // 2, y_bot - int(h * 0.44), cxm + tw // 2, y_bot - 6], fill=tongue)
        d.pieslice(bbox, 0, 180, fill=None, outline=blk, width=18)

    # --- ALEX EXPRESSIONS (BIG, EXPRESSIVE, CLEAN) ---
    if kind.startswith("alex_"):
        bstate = "half" if kind.endswith("_half") else ("closed" if kind.endswith("_closed") else "open")
        base = kind.replace("_half", "").replace("_closed", "")
        if base == "alex_determined":
            draw_eyes_state(bstate, 62, 78)
            # Bold fierce angled eyebrows
            d.line([(230, 315), (415, 382)], fill=brow_brown, width=40)
            d.line([(794, 315), (609, 382)], fill=brow_brown, width=40)
            # Determined gritted slight frown
            d.arc([385, 670, 639, 765], 195, 345, fill=blk, width=28)

        elif base == "alex_deadpan":
            draw_eyes_state(bstate, 58, 70)
            # Flat straight deadpan brows
            d.line([(240, 348), (415, 348)], fill=brow_brown, width=32)
            d.line([(609, 348), (784, 348)], fill=brow_brown, width=32)
            # Straight flat deadpan mouth
            d.line([(390, 700), (634, 700)], fill=blk, width=28)

        elif base == "alex_focus_squint":
            draw_eyes_state("half" if bstate == "open" else bstate, 60, 72)
            d.line([(230, 330), (418, 388)], fill=brow_brown, width=38)
            d.line([(794, 330), (606, 388)], fill=brow_brown, width=38)
            d.line([(405, 700), (619, 700)], fill=blk, width=28)

        elif base == "alex_shocked_wide":
            draw_eyes_state(bstate, 64, 88)
            d.arc([240, 245, 425, 340], 195, 345, fill=brow_brown, width=32)
            d.arc([599, 245, 784, 340], 195, 345, fill=brow_brown, width=32)
            # Crisp wide shocked mouth
            d.rounded_rectangle([396, 650, 628, 770], radius=52, fill=dark_red, outline=blk, width=20)
            d.ellipse([442, 712, 582, 760], fill=tongue)

        elif base == "alex_almost_wobbly":
            draw_eyes_state(bstate, 60, 76)
            # Upturned vulnerable worried brows
            d.line([(242, 372), (410, 314)], fill=brow_brown, width=32)
            d.line([(782, 372), (614, 314)], fill=brow_brown, width=32)
            # Iconic OG wobbly squiggle mouth
            pts = [(360, 708), (412, 672), (464, 712), (512, 672), (562, 712), (612, 672), (664, 706)]
            d.line(pts, fill=blk, width=28, joint="curve")

        elif base == "alex_smug":
            draw_eyes_state(bstate, 58, 72)
            d.line([(245, 350), (412, 362)], fill=brow_brown, width=32)
            d.line([(608, 342), (784, 305)], fill=brow_brown, width=32)
            # Confident crooked smirk
            d.arc([365, 585, 675, 750], 18, 152, fill=blk, width=28)

    # --- MANAGER EXPRESSIONS (3D mustache added on mesh, so keep mouth lower) ---
    elif kind.startswith("manager_"):
        bstate = "closed" if kind.endswith("_closed") else "open"
        base = kind.replace("_closed", "")
        if base == "manager_happy_welcome":
            draw_eyes_state(bstate, 56, 70)
            d.arc([252, 312, 420, 382], 195, 345, fill=brow_brown, width=32)
            d.arc([604, 312, 772, 382], 195, 345, fill=brow_brown, width=32)
            draw_open_smile(395, 700, 629, 805, has_teeth=False, has_tongue=True)

        elif base == "manager_shocked_o":
            draw_eyes_state(bstate, 64, 88)
            d.arc([248, 242, 420, 332], 195, 345, fill=brow_brown, width=32)
            d.arc([604, 242, 776, 332], 195, 345, fill=brow_brown, width=32)
            # Big shocked open O mouth with pink tongue (just like og_hero_plate_3 top-right!)
            d.ellipse([426, 665, 598, 835], fill=dark_red, outline=blk, width=20)
            d.ellipse([460, 752, 564, 818], fill=tongue)

        elif base == "manager_suspicious_squint":
            draw_eyes_state("half", 56, 64)
            d.line([(245, 322), (420, 376)], fill=brow_brown, width=34)
            d.line([(779, 342), (604, 342)], fill=brow_brown, width=34)
            d.line([(412, 725), (608, 712)], fill=blk, width=26)

        elif base == "manager_stern_question":
            draw_eyes_state(bstate, 54, 66)
            d.line([(242, 314), (422, 376)], fill=brow_brown, width=36)
            d.line([(782, 314), (602, 376)], fill=brow_brown, width=36)
            d.arc([408, 705, 616, 790], 195, 345, fill=blk, width=26)

        elif base == "manager_thrilled_hired":
            draw_eyes_state(bstate, 60, 74)
            d.arc([242, 286, 425, 366], 195, 345, fill=brow_brown, width=32)
            d.arc([599, 286, 782, 366], 195, 345, fill=brow_brown, width=32)
            draw_open_smile(374, 700, 650, 825, has_teeth=True, has_tongue=True)

    # --- MAYOR EXPRESSIONS (3D gray mustache on mesh) ---
    elif kind.startswith("mayor_"):
        if kind == "mayor_party_cheer":
            draw_eyes_state("open", 56, 70)
            d.arc([248, 306, 425, 382], 195, 345, fill=brow_gray, width=34)
            d.arc([599, 306, 776, 382], 195, 345, fill=brow_gray, width=34)
            draw_open_smile(385, 702, 639, 815, has_teeth=True, has_tongue=True)

        elif kind == "mayor_stunned_o":
            draw_eyes_state("open", 64, 88)
            d.arc([242, 236, 425, 326], 195, 345, fill=brow_gray, width=34)
            d.arc([599, 236, 782, 326], 195, 345, fill=brow_gray, width=34)
            d.ellipse([432, 675, 592, 845], fill=dark_red, outline=blk, width=20)
            d.ellipse([466, 765, 558, 828], fill=tongue)

        elif kind == "mayor_confused_frown":
            draw_eyes_state("open", 58, 78)
            d.line([(242, 332), (420, 302)], fill=brow_gray, width=34)
            d.line([(604, 302), (782, 332)], fill=brow_gray, width=34)
            d.arc([406, 710, 618, 795], 195, 345, fill=blk, width=26)

    # --- PARTY NEIGHBOR & CROWD ---
    elif kind == "neighbor_grin":
        draw_eyes_state("open", 60, 76)
        d.arc([248, 296, 425, 376], 195, 345, fill=(180, 82, 24, 255), width=32)
        d.arc([599, 296, 776, 376], 195, 345, fill=(180, 82, 24, 255), width=32)
        draw_open_smile(366, 668, 658, 808, has_teeth=True, has_tongue=True)

    elif kind == "crowd_happy_1":
        draw_eyes_state("open", 58, 74)
        d.arc([252, 312, 420, 378], 195, 345, fill=blk, width=28)
        d.arc([604, 312, 772, 378], 195, 345, fill=blk, width=28)
        draw_open_smile(374, 668, 650, 800, has_teeth=True, has_tongue=True)

    elif kind == "crowd_happy_2":
        # Joyful ^ ^ laugh eyes!
        d.arc([272, 412, 412, 525], 195, 345, fill=blk, width=28)
        d.arc([612, 412, 752, 525], 195, 345, fill=blk, width=28)
        draw_open_smile(378, 668, 646, 798, has_teeth=True, has_tongue=True)

    elif kind == "crowd_grandma":
        draw_eyes_state("open", 56, 74)
        d.arc([258, 306, 415, 368], 195, 345, fill=brow_gray, width=26)
        d.arc([609, 306, 766, 368], 195, 345, fill=brow_gray, width=26)
        draw_open_smile(390, 672, 634, 790, has_teeth=True, has_tongue=True)

    elif kind == "crowd_rock_guy":
        draw_eyes_state("open", 58, 76)
        d.line([(258, 342), (415, 342)], fill=blk, width=28)
        d.line([(609, 342), (766, 342)], fill=blk, width=28)
        draw_open_smile(392, 668, 632, 775, has_teeth=True, has_tongue=False)

    elif kind == "crowd_hungry":
        draw_eyes_state("open", 60, 74)
        d.arc([248, 302, 420, 378], 195, 345, fill=blk, width=28)
        d.arc([604, 302, 776, 378], 195, 345, fill=blk, width=28)
        d.ellipse([415, 645, 609, 805], fill=dark_red, outline=blk, width=18)
        d.ellipse([454, 735, 570, 792], fill=tongue)

    return im


def main():
    print("Generating Roblox Studio clothing atlases + bold dark-oval face decals (reusing existing env/prop textures)...")
    if not (TEX_ENV / "wood_planks_honey.png").exists():
        gen_wood_planks(TEX_ENV / "wood_planks_honey", [(196, 128, 68), (186, 118, 60), (206, 138, 76)], seed=11, rows=9, cols=3)
        gen_wood_planks(TEX_ENV / "wood_table_espresso", [(92, 58, 34), (82, 50, 28), (104, 66, 40)], seed=12, rows=6, cols=2)
        gen_brick_wainscot()
        gen_diner_tiles()
        gen_asphalt_speckled()
        gen_sidewalk_pavers()
        gen_wrapper_paper()
        gen_fabrics()
    if not (TEX_PROPS / "clock_stopwatch_dial.png").exists():
        gen_clock_dials()
        gen_prop_graphics()
    gen_roblox_char_textures()

    face_kinds = [
        "alex_determined", "alex_determined_half", "alex_determined_closed",
        "alex_deadpan", "alex_deadpan_half", "alex_deadpan_closed",
        "alex_focus_squint", "alex_focus_squint_half", "alex_focus_squint_closed",
        "alex_shocked_wide", "alex_almost_wobbly", "alex_almost_wobbly_closed",
        "alex_smug", "alex_smug_half", "alex_smug_closed",
        "manager_happy_welcome", "manager_happy_welcome_closed",
        "manager_shocked_o", "manager_suspicious_squint", "manager_stern_question", "manager_thrilled_hired",
        "mayor_party_cheer", "mayor_stunned_o", "mayor_confused_frown",
        "neighbor_grin",
        "crowd_happy_1", "crowd_happy_2", "crowd_grandma", "crowd_rock_guy", "crowd_hungry",
    ]
    for fk in face_kinds:
        make_face_base(fk).save(TEX_FACES / f"{fk}.png")

    print(f"Generated {len(list(TEX_CHARS.glob('*.png')))} char atlases, {len(face_kinds)} Roblox face decals.")


if __name__ == "__main__":
    main()
