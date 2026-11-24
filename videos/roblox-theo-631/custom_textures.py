"""
custom_textures.py — Copies validated Roblox R15 clothing/faces from reference project
and generates custom 1024x1024 Roblox face decals, outfit atlases, and hospital clipboard texture
for videos/roblox-theo-631.
"""
import random
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SHORTMAKING_ROOT = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking")
REF_DIR = SHORTMAKING_ROOT / "videos" / "roblox-reel-Df1kubCJ-o0-v2"
PROJ_DIR = SHORTMAKING_ROOT / "videos" / "roblox-theo-631"

TEX_FACES = PROJ_DIR / "textures" / "faces"
TEX_CHARS = PROJ_DIR / "textures" / "chars"
TEX_PROPS = PROJ_DIR / "textures" / "props"
for d in (TEX_FACES, TEX_CHARS, TEX_PROPS):
    d.mkdir(parents=True, exist_ok=True)


def get_font(size: int):
    for p in ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/impact.ttf"]:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def draw_glossy_eye(d: ImageDraw.ImageDraw, cx: int, cy: int, rx: int, ry: int, col=(18, 18, 24, 255)):
    wht = (255, 255, 255, 255)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=col)
    cr = max(12, int(rx * 0.36))
    d.ellipse([cx - int(rx * 0.56), cy - int(ry * 0.56), cx - int(rx * 0.56) + cr, cy - int(ry * 0.56) + cr], fill=wht)
    sr = max(6, rx // 6)
    d.ellipse([cx + int(rx * 0.25), cy + int(ry * 0.22), cx + int(rx * 0.25) + sr, cy + int(ry * 0.22) + sr], fill=(225, 235, 255, 200))


def make_custom_face(kind: str) -> Image.Image:
    S = 1024
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    blk = (22, 20, 26, 255)
    dark_red = (108, 22, 32, 255)
    tongue = (224, 92, 106, 255)
    wht = (255, 255, 255, 255)
    brow_dark = (26, 22, 22, 255)
    brow_gray = (120, 128, 140, 255)

    lx, rx_pos = 342, 682
    ey = 470

    def draw_eyes(state: str, erx=58, ery=74, lash=False):
        if state == "open":
            draw_glossy_eye(d, lx, ey, erx, ery)
            draw_glossy_eye(d, rx_pos, ey, erx, ery)
            if lash:
                for ex, sgn in ((lx, -1), (rx_pos, 1)):
                    d.line([(ex + sgn * (erx - 6), ey - ery + 22), (ex + sgn * (erx + 28), ey - ery - 4)], fill=blk, width=14)
                    d.line([(ex + sgn * (erx - 2), ey - ery + 42), (ex + sgn * (erx + 32), ey - ery + 22)], fill=blk, width=12)
        elif state == "half":
            draw_glossy_eye(d, lx, ey + 14, erx, ery // 2)
            draw_glossy_eye(d, rx_pos, ey + 14, erx, ery // 2)
            d.line([(lx - erx - 8, ey + 4), (lx + erx + 8, ey + 4)], fill=blk, width=18)
            d.line([(rx_pos - erx - 8, ey + 4), (rx_pos + erx + 8, ey + 4)], fill=blk, width=18)
        elif state == "closed":
            d.arc([lx - erx - 8, ey - 18, lx + erx + 8, ey + 44], 15, 165, fill=blk, width=22)
            d.arc([rx_pos - erx - 8, ey - 18, rx_pos + erx + 8, ey + 44], 15, 165, fill=blk, width=22)

    bstate = "half" if kind.endswith("_half") else ("closed" if kind.endswith("_closed") else "open")
    base = kind.replace("_half", "").replace("_closed", "")

    if base == "dad_serious_nod":
        draw_eyes(bstate, 60, 76)
        d.line([(235, 326), (416, 368)], fill=brow_dark, width=38)
        d.line([(789, 326), (608, 368)], fill=brow_dark, width=38)
        d.line([(395, 702), (629, 702)], fill=blk, width=28)

    elif base == "mom_serious_nod":
        draw_eyes(bstate, 58, 76, lash=True)
        d.line([(240, 328), (415, 362)], fill=brow_dark, width=30)
        d.line([(784, 328), (609, 362)], fill=brow_dark, width=30)
        d.line([(405, 700), (619, 700)], fill=(150, 48, 72, 255), width=26)

    elif base == "doctor_proud":
        draw_eyes(bstate, 56, 72)
        d.arc([246, 305, 420, 376], 195, 345, fill=brow_gray, width=30)
        d.arc([604, 305, 778, 376], 195, 345, fill=brow_gray, width=30)
        d.arc([386, 620, 638, 755], 15, 165, fill=blk, width=28)

    elif base == "doctor_shocked":
        for ex in (lx, rx_pos):
            d.ellipse([ex - 80, ey - 94, ex + 80, ey + 94], fill=wht, outline=blk, width=18)
            d.ellipse([ex - 26, ey - 30, ex + 26, ey + 30], fill=blk)
            d.ellipse([ex - 16, ey - 20, ex - 2, ey - 6], fill=wht)
        d.arc([236, 232, 424, 324], 195, 345, fill=brow_gray, width=34)
        d.arc([600, 232, 788, 324], 195, 345, fill=brow_gray, width=34)
        d.ellipse([424, 650, 600, 810], fill=dark_red, outline=blk, width=20)
        d.ellipse([462, 735, 562, 795], fill=tongue)

    elif base == "dad_horrified":
        for ex in (lx, rx_pos):
            d.ellipse([ex - 86, ey - 102, ex + 86, ey + 102], fill=wht, outline=blk, width=20)
            d.ellipse([ex - 20, ey - 22, ex + 20, ey + 22], fill=blk)
            d.ellipse([ex - 12, ey - 14, ex - 2, ey - 4], fill=wht)
        # Sweat drops
        d.polygon([(835, 290), (805, 375), (865, 375)], fill=(125, 211, 252, 240))
        d.ellipse([805, 345, 865, 415], fill=(125, 211, 252, 240), outline=(14, 116, 144, 240), width=6)
        d.line([(230, 286), (416, 252)], fill=brow_dark, width=36)
        d.line([(794, 286), (608, 252)], fill=brow_dark, width=36)
        d.rounded_rectangle([378, 635, 646, 815], radius=56, fill=dark_red, outline=blk, width=22)
        d.rectangle([404, 645, 620, 682], fill=wht)
        d.ellipse([440, 742, 584, 800], fill=tongue)

    elif base == "baby_happy":
        d.arc([lx - 58, ey - 20, lx + 58, ey + 45], 195, 345, fill=blk, width=22)
        d.arc([rx_pos - 58, ey - 20, rx_pos + 58, ey + 45], 195, 345, fill=blk, width=22)
        d.ellipse([235, 555, 355, 635], fill=(244, 114, 182, 165))
        d.ellipse([669, 555, 789, 635], fill=(244, 114, 182, 165))
        d.arc([410, 610, 614, 725], 15, 165, fill=blk, width=24)

    return im


def _new_fabric_atlas(hex_col: str, seed: int = 1):
    S = 1024
    h = hex_col.lstrip("#")
    base = (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    col = Image.new("RGB", (S, S), base)
    bump = Image.new("L", (S, S), 132)
    dc, db = ImageDraw.Draw(col), ImageDraw.Draw(bump)
    rng = random.Random(seed)
    for y in range(0, S, 10):
        delta = rng.randint(-5, 5)
        c2 = tuple(max(0, min(255, v + delta)) for v in base)
        dc.line([(0, y), (S, y)], fill=c2, width=2)
        db.line([(0, y), (S, y)], fill=128 + delta * 3, width=2)
    return col, bump


def _save_char_tex(stem: str, col: Image.Image, bump: Image.Image):
    col.save(TEX_CHARS / f"{stem}.png")
    bump.filter(ImageFilter.GaussianBlur(0.8)).save(TEX_CHARS / f"{stem}_bump.png")


def gen_extra_outfits():
    # Doctor: crisp white lab coat over teal surgical scrubs + stethoscope + dark slacks
    s_c, s_b = _new_fabric_atlas("#F8FAFC", seed=201)
    dc, db = ImageDraw.Draw(s_c), ImageDraw.Draw(s_b)
    # Teal V-neck scrubs underneath
    dc.polygon([(176, 0), (336, 0), (256, 360)], fill=(13, 148, 136))
    # Lab coat lapels & center placket
    dc.polygon([(176, 0), (136, 0), (226, 360), (256, 360)], fill=(226, 232, 240), outline=(148, 163, 184), width=4)
    dc.polygon([(336, 0), (376, 0), (286, 360), (256, 360)], fill=(226, 232, 240), outline=(148, 163, 184), width=4)
    dc.line([(256, 360), (256, 1024)], fill=(148, 163, 184), width=6)
    # Stethoscope loop
    dc.arc([152, -40, 360, 290], 10, 170, fill=(30, 41, 59), width=16)
    dc.ellipse([236, 276, 276, 316], fill=(148, 163, 184), outline=(51, 65, 85), width=5)
    # Breast pocket + pen
    dc.rectangle([332, 340, 418, 430], fill=(241, 245, 249), outline=(148, 163, 184), width=4)
    dc.line([(360, 308), (360, 342)], fill=(37, 99, 235), width=10)
    _save_char_tex("shirt_doctor", s_c, s_b)

    p_c, p_b = _new_fabric_atlas("#0F766E", seed=202)
    dc, db = ImageDraw.Draw(p_c), ImageDraw.Draw(p_b)
    dc.rectangle([0, 860, 1024, 1024], fill=(241, 245, 249))
    dc.rectangle([0, 992, 1024, 1024], fill=(203, 213, 225))
    _save_char_tex("pants_doctor", p_c, p_b)

    # Dad: clean navy-slate casual jacket over white tee + dark jeans
    s_c, s_b = _new_fabric_atlas("#1E3A5F", seed=203)
    dc, db = ImageDraw.Draw(s_c), ImageDraw.Draw(s_b)
    dc.polygon([(192, 0), (320, 0), (256, 310)], fill=(248, 250, 252))
    dc.line([(256, 310), (256, 1024)], fill=(15, 23, 42), width=10)
    dc.rectangle([0, 945, 1024, 1024], fill=(15, 23, 42))
    _save_char_tex("shirt_dad", s_c, s_b)

    p_c, p_b = _new_fabric_atlas("#1E293B", seed=204)
    dc, db = ImageDraw.Draw(p_c), ImageDraw.Draw(p_b)
    dc.rectangle([0, 865, 1024, 1024], fill=(248, 250, 252))
    dc.rectangle([0, 990, 1024, 1024], fill=(203, 213, 225))
    _save_char_tex("pants_dad", p_c, p_b)

    # Mom: coral-rose sweater + medium denim jeans
    s_c, s_b = _new_fabric_atlas("#E11D48", seed=205)
    dc, db = ImageDraw.Draw(s_c), ImageDraw.Draw(s_b)
    dc.arc([170, -45, 342, 125], 0, 180, fill=(255, 241, 242), width=26)
    dc.rectangle([0, 945, 1024, 1024], fill=(190, 18, 60))
    _save_char_tex("shirt_mom", s_c, s_b)

    p_c, p_b = _new_fabric_atlas("#1D4ED8", seed=206)
    dc, db = ImageDraw.Draw(p_c), ImageDraw.Draw(p_b)
    dc.rectangle([0, 865, 1024, 1024], fill=(248, 250, 252))
    dc.rectangle([0, 990, 1024, 1024], fill=(226, 232, 240))
    _save_char_tex("pants_mom", p_c, p_b)


def make_prop_textures():
    f_big = get_font(104)
    f_med = get_font(64)
    f_sm = get_font(48)

    im = Image.new("RGBA", (1024, 1280), (248, 250, 252, 255))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([24, 24, 1000, 1256], radius=24, fill=(248, 250, 252, 255), outline=(51, 65, 85, 255), width=14)
    d.rectangle([24, 24, 1000, 220], fill=(14, 116, 144, 255))
    d.text((512, 122), "DELIVERY CHART #631", fill=(255, 255, 255, 255), font=f_med, anchor="mm")
    d.text((100, 340), "DAD HAIR:   BLACK", fill=(30, 41, 59, 255), font=f_med)
    d.text((100, 460), "MOM HAIR:   BLACK", fill=(30, 41, 59, 255), font=f_med)
    d.line([(90, 590), (934, 590)], fill=(148, 163, 184, 255), width=8)
    d.rounded_rectangle([85, 670, 939, 980], radius=24, fill=(254, 242, 242, 255), outline=(220, 38, 38, 255), width=16)
    d.text((512, 770), "BABY: BLONDE?!", fill=(220, 38, 38, 255), font=f_big, anchor="mm")
    d.text((512, 895), "DNA MATCH: ???", fill=(185, 28, 28, 255), font=f_med, anchor="mm")
    d.text((512, 1120), "ODDS: 1 IN 250,000,000", fill=(71, 85, 105, 255), font=f_sm, anchor="mm")
    im.save(TEX_PROPS / "clipboard_dna.png")


def main():
    ref_faces = REF_DIR / "textures" / "faces"
    if ref_faces.exists():
        for p in ref_faces.glob("*.png"):
            shutil.copy2(p, TEX_FACES / p.name)
    ref_chars = REF_DIR / "textures" / "chars"
    if ref_chars.exists():
        for p in ref_chars.glob("*.png"):
            shutil.copy2(p, TEX_CHARS / p.name)

    custom_faces = [
        "dad_serious_nod", "dad_serious_nod_half", "dad_serious_nod_closed",
        "mom_serious_nod", "mom_serious_nod_half", "mom_serious_nod_closed",
        "doctor_proud", "doctor_proud_half", "doctor_proud_closed",
        "doctor_shocked",
        "dad_horrified",
        "baby_happy",
    ]
    for cf in custom_faces:
        make_custom_face(cf).save(TEX_FACES / f"{cf}.png")

    gen_extra_outfits()
    make_prop_textures()
    print(f"STEP 3 TEXTURES COMPLETE: {len(list(TEX_FACES.glob('*.png')))} faces, {len(list(TEX_CHARS.glob('*.png')))} chars, {len(list(TEX_PROPS.glob('*.png')))} props.")


if __name__ == "__main__":
    main()
