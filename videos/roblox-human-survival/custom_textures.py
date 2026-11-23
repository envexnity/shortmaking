"""
custom_textures.py — Generates custom expressive Roblox R15 survival faces and 3D UI/prop textures
for videos/roblox-human-survival, building cleanly on the Df1kubCJ-o0-v2 face library.
"""
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SHORTMAKING_ROOT = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking")
REF_DIR = SHORTMAKING_ROOT / "videos" / "roblox-reel-Df1kubCJ-o0-v2"
PROJ_DIR = SHORTMAKING_ROOT / "videos" / "roblox-human-survival"

TEX_FACES = PROJ_DIR / "textures" / "faces"
TEX_PROPS = PROJ_DIR / "textures" / "props"
TEX_FACES.mkdir(parents=True, exist_ok=True)
TEX_PROPS.mkdir(parents=True, exist_ok=True)


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
    brow_brown = (48, 28, 18, 255)

    lx, rx_pos = 342, 682
    ey = 470

    def draw_eyes(state: str, erx=58, ery=74, col=(18, 18, 24, 255)):
        if state == "open":
            draw_glossy_eye(d, lx, ey, erx, ery, col=col)
            draw_glossy_eye(d, rx_pos, ey, erx, ery, col=col)
        elif state == "half":
            draw_glossy_eye(d, lx, ey + 14, erx, ery // 2, col=col)
            draw_glossy_eye(d, rx_pos, ey + 14, erx, ery // 2, col=col)
            d.line([(lx - erx - 8, ey + 4), (lx + erx + 8, ey + 4)], fill=blk, width=18)
            d.line([(rx_pos - erx - 8, ey + 4), (rx_pos + erx + 8, ey + 4)], fill=blk, width=18)
        elif state == "closed":
            d.arc([lx - erx - 8, ey - 18, lx + erx + 8, ey + 44], 15, 165, fill=blk, width=22)
            d.arc([rx_pos - erx - 8, ey - 18, rx_pos + erx + 8, ey + 44], 15, 165, fill=blk, width=22)

    bstate = "half" if kind.endswith("_half") else ("closed" if kind.endswith("_closed") else "open")
    base = kind.replace("_half", "").replace("_closed", "")

    if base == "alex_inhale_o":
        draw_eyes(bstate, 60, 78)
        d.arc([240, 265, 425, 355], 195, 345, fill=brow_brown, width=32)
        d.arc([599, 265, 784, 355], 195, 345, fill=brow_brown, width=32)
        d.ellipse([442, 650, 582, 790], fill=dark_red, outline=blk, width=20)
        d.ellipse([474, 725, 550, 775], fill=tongue)

    elif base == "alex_cheek_puff":
        draw_eyes(bstate, 64, 86)
        d.line([(235, 340), (415, 386)], fill=brow_brown, width=36)
        d.line([(789, 340), (609, 386)], fill=brow_brown, width=36)
        # Puffed red cheeks + tight curved breath-hold line
        d.ellipse([240, 620, 380, 740], fill=(242, 128, 120, 175))
        d.ellipse([644, 620, 784, 740], fill=(242, 128, 120, 175))
        d.arc([370, 660, 654, 740], 195, 345, fill=blk, width=26)
        d.arc([345, 655, 395, 725], 105, 255, fill=blk, width=18)
        d.arc([629, 655, 679, 725], 285, 75, fill=blk, width=18)

    elif base == "alex_burning_eyes":
        # Fiery red-orange irritated eyes + panic mouth!
        for ex in (lx, rx_pos):
            d.ellipse([ex - 88, ey - 96, ex + 88, ey + 96], fill=(255, 110, 60, 190))
            d.ellipse([ex - 68, ey - 82, ex + 68, ey + 82], fill=(255, 235, 225, 255), outline=(220, 38, 38, 255), width=14)
            # Bloodshot lines
            d.line([(ex - 58, ey - 20), (ex - 26, ey - 8)], fill=(239, 68, 68, 255), width=8)
            d.line([(ex + 58, ey + 15), (ex + 24, ey + 4)], fill=(239, 68, 68, 255), width=8)
            draw_glossy_eye(d, ex, ey, 34, 42, col=(185, 28, 28, 255))
        d.line([(235, 310), (415, 372)], fill=brow_brown, width=38)
        d.line([(789, 310), (609, 372)], fill=brow_brown, width=38)
        d.rounded_rectangle([386, 650, 638, 775], radius=50, fill=dark_red, outline=blk, width=20)
        d.ellipse([440, 718, 584, 764], fill=tongue)

    elif base == "alex_blurry_squint":
        draw_eyes("half", 62, 68)
        d.line([(235, 352), (420, 382)], fill=brow_brown, width=34)
        d.line([(789, 352), (604, 382)], fill=brow_brown, width=34)
        d.line([(402, 705), (622, 695)], fill=blk, width=26)

    elif base == "alex_gulp_o":
        draw_eyes(bstate, 58, 74)
        d.arc([248, 295, 420, 365], 195, 345, fill=brow_brown, width=32)
        d.arc([604, 295, 776, 365], 195, 345, fill=brow_brown, width=32)
        d.ellipse([435, 650, 589, 785], fill=(56, 189, 248, 255), outline=blk, width=20)
        d.ellipse([468, 675, 535, 730], fill=(224, 242, 254, 230))

    elif base == "alex_chewing":
        draw_eyes(bstate, 58, 72)
        d.line([(245, 340), (415, 348)], fill=brow_brown, width=32)
        d.line([(609, 348), (779, 340)], fill=brow_brown, width=32)
        # Wide open mouth with big white blocky "tiny rocks" (teeth)!
        d.rounded_rectangle([360, 635, 664, 790], radius=44, fill=dark_red, outline=blk, width=20)
        for tx in range(386, 640, 52):
            d.rounded_rectangle([tx, 645, tx + 42, 690], radius=8, fill=wht, outline=blk, width=5)
            d.rounded_rectangle([tx, 738, tx + 42, 780], radius=8, fill=wht, outline=blk, width=5)

    elif base == "alex_sleep_closed":
        d.arc([lx - 66, ey - 10, lx + 66, ey + 55], 15, 165, fill=blk, width=24)
        d.arc([rx_pos - 66, ey - 10, rx_pos + 66, ey + 55], 15, 165, fill=blk, width=24)
        d.line([(255, 355), (415, 345)], fill=brow_brown, width=26)
        d.line([(609, 345), (769, 355)], fill=brow_brown, width=26)
        d.ellipse([475, 675, 550, 745], fill=dark_red, outline=blk, width=18)

    elif base == "alex_exhausted_bags":
        # Heavy dark under-eye bags + droopy half eyes
        for ex in (lx, rx_pos):
            d.arc([ex - 68, ey + 18, ex + 68, ey + 96], 10, 170, fill=(92, 76, 128, 220), width=18)
        draw_eyes("half", 58, 70)
        d.line([(245, 378), (415, 330)], fill=brow_brown, width=30)
        d.line([(779, 378), (609, 330)], fill=brow_brown, width=30)
        pts = [(375, 712), (435, 682), (512, 714), (589, 682), (649, 710)]
        d.line(pts, fill=blk, width=26, joint="curve")

    elif base == "alex_glitch_dead":
        # Classic Roblox X _ X knockout face
        for ex in (lx, rx_pos):
            d.line([(ex - 52, ey - 52), (ex + 52, ey + 52)], fill=blk, width=26)
            d.line([(ex + 52, ey - 52), (ex - 52, ey + 52)], fill=blk, width=26)
        d.line([(245, 350), (415, 315)], fill=brow_brown, width=28)
        d.line([(779, 350), (609, 315)], fill=brow_brown, width=28)
        pts = [(368, 708), (425, 672), (482, 716), (540, 672), (598, 716), (656, 676)]
        d.line(pts, fill=blk, width=24, joint="curve")
        d.pieslice([525, 690, 620, 795], 0, 180, fill=tongue, outline=blk, width=14)

    return im


def make_prop_signs():
    f_big = get_font(120)
    f_med = get_font(74)

    # 1. GAME OVER banner
    im = Image.new("RGBA", (1024, 512), (24, 12, 22, 245))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([14, 14, 1010, 498], radius=36, fill=(24, 12, 22, 255), outline=(239, 68, 68, 255), width=18)
    d.text((512, 200), "GAME OVER", fill=(239, 68, 68, 255), font=f_big, anchor="mm")
    d.text((512, 350), "LUNGS SHUT DOWN (3:00)", fill=(255, 255, 255, 255), font=f_med, anchor="mm")
    im.save(TEX_PROPS / "gameover_banner.png")

    # 2. SAVE FAILED banner
    im = Image.new("RGBA", (1024, 512), (20, 16, 36, 245))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([14, 14, 1010, 498], radius=36, fill=(20, 16, 36, 255), outline=(250, 204, 21, 255), width=18)
    d.text((512, 200), "SAVE FAILED!", fill=(250, 204, 21, 255), font=f_big, anchor="mm")
    d.text((512, 350), "DATA NOT SAVED", fill=(248, 113, 113, 255), font=f_med, anchor="mm")
    im.save(TEX_PROPS / "save_failed_banner.png")

    # 3. LOW H2O sign
    im = Image.new("RGBA", (1024, 512), (12, 24, 42, 245))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([14, 14, 1010, 498], radius=36, fill=(12, 24, 42, 255), outline=(56, 189, 248, 255), width=18)
    d.text((512, 200), "TANK: 12%", fill=(239, 68, 68, 255), font=f_big, anchor="mm")
    d.text((512, 350), "REFILL H2O NOW!", fill=(56, 189, 248, 255), font=f_med, anchor="mm")
    im.save(TEX_PROPS / "low_h2o_banner.png")


def main():
    # Copy all existing faces from reference project so blinks & standard faces work seamlessly
    ref_faces = REF_DIR / "textures" / "faces"
    if ref_faces.exists():
        for p in ref_faces.glob("*.png"):
            shutil.copy2(p, TEX_FACES / p.name)

    custom_faces = [
        "alex_inhale_o", "alex_inhale_o_half", "alex_inhale_o_closed",
        "alex_cheek_puff", "alex_cheek_puff_half", "alex_cheek_puff_closed",
        "alex_burning_eyes",
        "alex_blurry_squint",
        "alex_gulp_o", "alex_gulp_o_half", "alex_gulp_o_closed",
        "alex_chewing", "alex_chewing_half", "alex_chewing_closed",
        "alex_sleep_closed",
        "alex_exhausted_bags",
        "alex_glitch_dead",
    ]
    for cf_name in custom_faces:
        make_custom_face(cf_name).save(TEX_FACES / f"{cf_name}.png")

    make_prop_signs()
    print(f"Prepared {len(list(TEX_FACES.glob('*.png')))} faces and custom prop banners.")


if __name__ == "__main__":
    main()
