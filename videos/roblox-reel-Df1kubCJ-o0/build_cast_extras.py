"""
build_cast_extras.py
Creates:
  1. Custom 585x559 Classic Roblox Shirts for 09_BunTown_Manager (Burgundy Suit + Yellow Tie + Badge)
     and 10_Town_Mayor (Navy Suit + Purple/Gold Mayor Sash).
  2. Crisp Roblox-style expressive face decals (512x512 RGBA) for Alex (5 expressions),
     Manager (4 expressions), and Mayor (3 expressions), baked into 2048x1024 HD R6 atlases
     using our exact verified bake_textures.py UV mapping!
  3. Builds 09_BunTown_Manager.blend and 10_Town_Mayor.blend in assets/roblox-r6-characters/characters/
     using Aeresei's verified R6 IK + FK Blender Rig V2.22.
"""
import json
import math
import sys
from pathlib import Path
from PIL import Image, ImageDraw

SHORTMAKING_ROOT = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking")
CAST_ROOT = SHORTMAKING_ROOT / "assets" / "roblox-r6-characters"
PROJ_DIR = SHORTMAKING_ROOT / "videos" / "roblox-reel-Df1kubCJ-o0"
EXPR_DIR = PROJ_DIR / "expressions"
EXPR_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(CAST_ROOT / "scripts"))
import bake_textures as bt


def draw_roblox_face(kind: str) -> Image.Image:
    """Draw crisp 512x512 RGBA classic Roblox expressions with expressive brows/mouths/mustache."""
    im = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    blk = (18, 18, 22, 255)
    wht = (255, 255, 255, 255)
    red_m = (195, 42, 52, 255)
    dark_m = (65, 22, 28, 255)
    must_brown = (42, 28, 22, 255)
    must_gray = (130, 134, 144, 255)

    def eye(cx, cy, rx=20, ry=28, white_ring=False):
        if white_ring:
            d.ellipse([cx - rx - 8, cy - ry - 6, cx + rx + 8, cy + ry + 6], fill=wht, outline=blk, width=7)
            d.ellipse([cx - rx//2, cy - ry//2, cx + rx//2, cy + ry//2], fill=blk)
        else:
            d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=blk)
            d.ellipse([cx - rx + 6, cy - ry + 6, cx - rx + 16, cy - ry + 16], fill=wht)

    if kind == "alex_determined":
        eye(186, 228, 18, 24)
        eye(326, 228, 18, 24)
        # Fierce V eyebrows
        d.line([(146, 178), (222, 206)], fill=blk, width=18)
        d.line([(366, 178), (290, 206)], fill=blk, width=18)
        # Gritted determined frown/line
        d.arc([206, 304, 306, 354], 195, 345, fill=blk, width=14)

    elif kind == "alex_deadpan":
        eye(186, 232, 16, 20)
        eye(326, 232, 16, 20)
        # Flat deadpan lids & brows
        d.line([(152, 198), (218, 198)], fill=blk, width=12)
        d.line([(294, 198), (360, 198)], fill=blk, width=12)
        d.line([(208, 326), (304, 326)], fill=blk, width=14)

    elif kind == "alex_shocked":
        eye(184, 218, 26, 32, white_ring=True)
        eye(328, 218, 26, 32, white_ring=True)
        # High shocked brows
        d.arc([148, 142, 220, 186], 200, 340, fill=blk, width=12)
        d.arc([292, 142, 364, 186], 200, 340, fill=blk, width=12)
        # Big O mouth
        d.ellipse([214, 290, 298, 386], fill=dark_m, outline=blk, width=14)
        d.ellipse([232, 346, 280, 378], fill=red_m)

    elif kind == "alex_sad_almost":
        eye(186, 234, 17, 22)
        eye(326, 234, 17, 22)
        # Sad upturned inner brows
        d.line([(150, 202), (216, 178)], fill=blk, width=13)
        d.line([(362, 202), (296, 178)], fill=blk, width=13)
        # Wobbly "almost" mouth
        pts = [(200, 336), (222, 320), (244, 336), (268, 320), (290, 336), (312, 322)]
        d.line(pts, fill=blk, width=13, joint="curve")

    elif kind == "alex_smug":
        eye(186, 228, 17, 22)
        eye(326, 228, 17, 22)
        # Confident angled smug brows
        d.line([(152, 192), (218, 198)], fill=blk, width=13)
        d.line([(294, 188), (360, 172)], fill=blk, width=13)
        # Big confident crooked smirk
        d.arc([186, 266, 336, 356], 20, 155, fill=blk, width=16)

    elif kind.startswith("manager_"):
        if kind == "manager_happy":
            eye(188, 222, 18, 24)
            eye(324, 222, 18, 24)
            d.arc([154, 172, 222, 204], 200, 340, fill=must_brown, width=14)
            d.arc([290, 172, 358, 204], 200, 340, fill=must_brown, width=14)
            d.pieslice([216, 294, 296, 368], 0, 180, fill=red_m, outline=blk, width=10)
        elif kind == "manager_shocked":
            eye(186, 214, 24, 30, white_ring=True)
            eye(326, 214, 24, 30, white_ring=True)
            d.arc([150, 144, 222, 182], 200, 340, fill=must_brown, width=14)
            d.arc([290, 144, 362, 182], 200, 340, fill=must_brown, width=14)
            d.ellipse([226, 316, 286, 384], fill=red_m, outline=blk, width=12)
        elif kind == "manager_stern":
            eye(188, 228, 18, 22)
            eye(324, 228, 18, 22)
            d.line([(150, 182), (222, 204)], fill=must_brown, width=16)
            d.line([(362, 182), (290, 204)], fill=must_brown, width=16)
            d.line([(218, 334), (294, 334)], fill=blk, width=12)
        elif kind == "manager_thrilled":
            eye(188, 218, 20, 26)
            eye(324, 218, 20, 26)
            d.arc([150, 162, 224, 196], 200, 340, fill=must_brown, width=14)
            d.arc([288, 162, 362, 196], 200, 340, fill=must_brown, width=14)
            d.pieslice([204, 296, 308, 386], 0, 180, fill=red_m, outline=blk, width=11)
        # Signature manager handlebar mustache
        d.ellipse([196, 262, 260, 306], fill=must_brown)
        d.ellipse([252, 262, 316, 306], fill=must_brown)

    elif kind.startswith("mayor_"):
        if kind == "mayor_happy":
            eye(188, 222, 18, 24)
            eye(324, 222, 18, 24)
            d.arc([152, 170, 222, 204], 200, 340, fill=must_gray, width=16)
            d.arc([290, 170, 360, 204], 200, 340, fill=must_gray, width=16)
            d.pieslice([210, 298, 302, 372], 0, 180, fill=red_m, outline=blk, width=10)
        elif kind == "mayor_shocked":
            eye(186, 214, 26, 32, white_ring=True)
            eye(326, 214, 26, 32, white_ring=True)
            d.arc([146, 140, 222, 178], 200, 340, fill=must_gray, width=16)
            d.arc([290, 140, 366, 178], 200, 340, fill=must_gray, width=16)
            d.ellipse([222, 318, 290, 392], fill=red_m, outline=blk, width=12)
        elif kind == "mayor_confused":
            eye(188, 226, 20, 24, white_ring=True)
            eye(324, 226, 20, 24, white_ring=True)
            d.line([(148, 182), (220, 168)], fill=must_gray, width=16)
            d.line([(292, 168), (364, 182)], fill=must_gray, width=16)
            d.arc([214, 328, 298, 376], 190, 350, fill=blk, width=13)
        # Signature distinguished gray Mayor mustache
        d.ellipse([186, 264, 262, 312], fill=must_gray, outline=(85, 88, 96, 255), width=4)
        d.ellipse([250, 264, 326, 312], fill=must_gray, outline=(85, 88, 96, 255), width=4)

    return im


def make_manager_shirt() -> Image.Image:
    """585x559 Roblox Classic Burgundy Bun Town Manager Suit + Yellow Tie + Gold Nameplate."""
    im = Image.new("RGBA", (585, 559), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    burgundy = (138, 24, 38, 255)
    burg_dark = (104, 16, 28, 255)
    white = (246, 244, 240, 255)
    gold = (240, 198, 52, 255)
    gold_d = (192, 148, 28, 255)

    for box in bt.RBX_TORSO.values():
        d.rectangle(box, fill=burgundy)

    fx0, fy0, fx1, fy1 = bt.RBX_TORSO["front"]
    cx = (fx0 + fx1) // 2
    # White dress shirt V
    d.polygon([(cx - 24, fy0), (cx + 24, fy0), (cx, fy0 + 76)], fill=white)
    # Lapels
    d.polygon([(cx - 34, fy0), (cx - 22, fy0), (cx - 2, fy0 + 76), (cx - 16, fy0 + 70)], fill=burg_dark, outline=gold)
    d.polygon([(cx + 34, fy0), (cx + 22, fy0), (cx + 2, fy0 + 76), (cx + 16, fy0 + 70)], fill=burg_dark, outline=gold)
    # Bright Yellow Manager Tie (so wrapping it in yellow burger paper is a great visual gag!)
    d.polygon([(cx - 8, fy0 + 4), (cx + 8, fy0 + 4), (cx + 5, fy0 + 18), (cx - 5, fy0 + 18)], fill=gold, outline=gold_d)
    d.polygon([(cx - 5, fy0 + 18), (cx + 5, fy0 + 18), (cx + 9, fy0 + 70), (cx, fy0 + 82), (cx - 9, fy0 + 70)], fill=gold, outline=gold_d)
    # Gold Manager Nameplate badge on left chest
    d.rectangle([cx + 18, fy0 + 36, cx + 48, fy0 + 50], fill=gold, outline=gold_d, width=2)
    # Suit buttons
    for by in (fy0 + 88, fy0 + 106):
        d.ellipse([cx - 4, by - 4, cx + 4, by + 4], fill=gold)

    # Sleeves
    for lm in (bt.RBX_RIGHT_LIMB, bt.RBX_LEFT_LIMB):
        d.rectangle(lm["up"], fill=burgundy)
        for side in ("front", "back", "left", "right"):
            x0, y0, x1, y1 = lm[side]
            se = y1 - 30
            d.rectangle([x0, y0, x1, se], fill=burgundy)
            d.rectangle([x0, se - 6, x1, se], fill=gold)
            d.rectangle([x0, se, x1, se + 6], fill=white)
    return im


def make_mayor_shirt() -> Image.Image:
    """585x559 Roblox Classic Navy Mayor Suit + Royal Purple & Gold Diagonal Sash."""
    im = Image.new("RGBA", (585, 559), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    navy = (28, 42, 78, 255)
    navy_d = (18, 28, 54, 255)
    white = (246, 246, 250, 255)
    purple = (108, 42, 168, 255)
    gold = (242, 198, 56, 255)

    for box in bt.RBX_TORSO.values():
        d.rectangle(box, fill=navy)

    fx0, fy0, fx1, fy1 = bt.RBX_TORSO["front"]
    cx = (fx0 + fx1) // 2
    d.polygon([(cx - 24, fy0), (cx + 24, fy0), (cx, fy0 + 74)], fill=white)
    # Diagonal Purple & Gold Mayor Sash!
    d.polygon([(fx1 - 26, fy0), (fx1, fy0), (fx0 + 26, fy1), (fx0, fy1)], fill=purple)
    d.line([(fx1 - 26, fy0), (fx0, fy1)], fill=gold, width=4)
    d.line([(fx1, fy0), (fx0 + 26, fy1)], fill=gold, width=4)
    # Gold Medal / Mayor Pin
    d.ellipse([cx - 10, fy0 + 52, cx + 10, fy0 + 72], fill=gold, outline=navy_d, width=2)
    # Gold belt buckle at waist
    d.rectangle([fx0, fy1 - 12, fx1, fy1], fill=navy_d)
    d.rectangle([cx - 10, fy1 - 12, cx + 10, fy1], fill=gold)

    for lm in (bt.RBX_RIGHT_LIMB, bt.RBX_LEFT_LIMB):
        d.rectangle(lm["up"], fill=navy)
        for side in ("front", "back", "left", "right"):
            x0, y0, x1, y1 = lm[side]
            se = y1 - 30
            d.rectangle([x0, y0, x1, se], fill=navy)
            d.rectangle([x0, se - 6, x1, se], fill=gold)
            d.rectangle([x0, se, x1, se + 5], fill=white)
    return im


def bake_with_custom_face(atlas_out: Path, body_colors: dict, face_img: Image.Image, shirt_key=None, pants_key=None, custom_shirt=None, scale: int = 2):
    w, h = 1024 * scale, 512 * scale
    head_col = bt.hex_rgba(body_colors["head"])
    atlas = Image.new("RGBA", (w, h), head_col)
    draw = ImageDraw.Draw(atlas)

    for part_name, rects in bt.PART_BASE_FILLS.items():
        col = bt.hex_rgba(body_colors.get(part_name, body_colors["head"]))
        for rx0, ry0, rx1, ry1 in rects:
            draw.rectangle([rx0 * scale, ry0 * scale, rx1 * scale, ry1 * scale], fill=col)

    def load_tpl(k):
        if not k:
            return None
        p = bt.MANIFEST[k]["files"]["texture"]
        im = Image.open(p).convert("RGBA")
        return im.resize((585, 559), Image.Resampling.LANCZOS) if im.size != (585, 559) else im

    pants_img = load_tpl(pants_key)
    if pants_img is not None:
        for side, box in bt.RBX_TORSO.items():
            bt.paste_patch_with_bleed(atlas, pants_img.crop(box), bt.ATLAS_RECTS["torso"][side], scale=scale)
        for side, box in bt.RBX_RIGHT_LIMB.items():
            bt.paste_patch_with_bleed(atlas, pants_img.crop(box), bt.ATLAS_RECTS["right_leg"][side], scale=scale)
        for side, box in bt.RBX_LEFT_LIMB.items():
            bt.paste_patch_with_bleed(atlas, pants_img.crop(box), bt.ATLAS_RECTS["left_leg"][side], scale=scale)

    shirt_img = custom_shirt if custom_shirt is not None else load_tpl(shirt_key)
    if shirt_img is not None:
        for side, box in bt.RBX_TORSO.items():
            bt.paste_patch_with_bleed(atlas, shirt_img.crop(box), bt.ATLAS_RECTS["torso"][side], scale=scale)
        for side, box in bt.RBX_RIGHT_LIMB.items():
            bt.paste_patch_with_bleed(atlas, shirt_img.crop(box), bt.ATLAS_RECTS["right_arm"][side], scale=scale)
        for side, box in bt.RBX_LEFT_LIMB.items():
            bt.paste_patch_with_bleed(atlas, shirt_img.crop(box), bt.ATLAS_RECTS["left_arm"][side], scale=scale)

    face_box_sz = int(round(112 * scale))
    fr = face_img.resize((face_box_sz, face_box_sz), Image.Resampling.LANCZOS)
    cx = int(round(959.5 * scale))
    cy = int(round(64.0 * scale))
    atlas.alpha_composite(fr, (cx - face_box_sz // 2, cy - face_box_sz // 2))
    atlas.save(atlas_out)
    print(f"[BAKED EXPR] {atlas_out.name}")


def main():
    # 1. Alex 5 expressions (matching 01_Alex_Protagonist outfit!)
    alex_colors = {k: "#F2C9A0" for k in ("head", "torso", "left_arm", "right_arm", "left_leg", "right_leg")}
    for kind in ("alex_determined", "alex_deadpan", "alex_shocked", "alex_sad_almost", "alex_smug"):
        bake_with_custom_face(
            EXPR_DIR / f"{kind}_atlas.png", alex_colors, draw_roblox_face(kind),
            shirt_key="shirt_denim_hoodie", pants_key="pants_black_white",
        )

    # 2. Manager 4 expressions
    mgr_shirt = make_manager_shirt()
    mgr_colors = {k: "#DFA67B" for k in ("head", "torso", "left_arm", "right_arm", "left_leg", "right_leg")}
    for kind in ("manager_happy", "manager_shocked", "manager_stern", "manager_thrilled"):
        bake_with_custom_face(
            EXPR_DIR / f"{kind}_atlas.png", mgr_colors, draw_roblox_face(kind),
            custom_shirt=mgr_shirt, pants_key="pants_black_slacks",
        )

    # 3. Mayor 3 expressions
    mayor_shirt = make_mayor_shirt()
    mayor_colors = {k: "#E8BA92" for k in ("head", "torso", "left_arm", "right_arm", "left_leg", "right_leg")}
    for kind in ("mayor_happy", "mayor_shocked", "mayor_confused"):
        bake_with_custom_face(
            EXPR_DIR / f"{kind}_atlas.png", mayor_colors, draw_roblox_face(kind),
            custom_shirt=mayor_shirt, pants_key="pants_black_slacks",
        )

    print("All 12 expressive character atlases baked cleanly!")


if __name__ == "__main__":
    main()
