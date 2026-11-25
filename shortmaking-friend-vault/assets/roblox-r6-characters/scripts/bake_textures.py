"""
bake_textures.py
Bakes pixel-accurate 2048x1024 HD R6 avatar texture atlases for Aeresei's R6 IK+FK Rig V2.22
from real Roblox Marketplace Classic Shirts (585x559), Classic Pants (585x559), Classic Faces,
and Roblox BrickColor skin palettes.
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking\assets\roblox-r6-characters")
MANIFEST = json.loads((ROOT / "marketplace_assets" / "manifest.json").read_text(encoding="utf-8"))
TEX_DIR = ROOT / "textures"
TEX_DIR.mkdir(parents=True, exist_ok=True)

# Standard Roblox 585x559 Classic Shirt / Pants template boxes (x0, y0, x1, y1)
RBX_TORSO = {
    "up":    (231, 8,   359, 72),
    "front": (231, 74,  359, 202),
    "down":  (231, 204, 359, 268),
    "right": (165, 74,  229, 202),
    "left":  (361, 74,  425, 202),
    "back":  (427, 74,  555, 202),
}

RBX_RIGHT_LIMB = {
    "up":    (217, 289, 281, 353),
    "right": (19,  355, 83,  483),
    "back":  (85,  355, 149, 483),
    "left":  (151, 355, 215, 483),
    "front": (217, 355, 281, 483),
    "down":  (217, 485, 281, 549),
}

RBX_LEFT_LIMB = {
    "up":    (308, 289, 372, 353),
    "front": (308, 355, 372, 483),
    "right": (374, 355, 438, 483),
    "back":  (440, 355, 504, 483),
    "left":  (506, 355, 570, 483),
    "down":  (308, 485, 372, 549),
}

# Exact UV destination rects on 1024x512 atlas (measured directly from Blender_R6_Rig_v222.blend)
# Format: (x0, y0, x1, y1, rot_cw_90)
ATLAS_RECTS = {
    "torso": {
        "right": (25.5,  2.0,   118.5, 62.0,  True),
        "front": (25.5,  66.0,  118.5, 190.0, True),
        "left":  (25.5,  194.0, 118.5, 254.0, True),
        "back":  (25.5,  258.0, 118.5, 382.0, True),
        "up":    (151.5, 329.0, 244.5, 389.0, False),
        "down":  (252.7, 329.0, 345.7, 389.0, False),
    },
    "right_arm": {
        "back":  (175.5, 66.0,  268.5, 126.0, True),
        "right": (175.5, 130.0, 268.5, 190.0, True),
        "front": (175.5, 194.0, 268.5, 254.0, True),
        "left":  (175.5, 258.0, 268.5, 318.0, True),
        "up":    (679.5, 330.0, 724.5, 390.0, False),
        "down":  (571.5, 330.0, 616.5, 390.0, False),
    },
    "left_arm": {
        "right": (325.5, 2.0,   418.5, 62.0,  True),
        "front": (325.5, 66.0,  418.5, 126.0, True),
        "left":  (325.5, 130.0, 418.5, 190.0, True),
        "back":  (325.5, 194.0, 418.5, 254.0, True),
        "up":    (151.5, 404.0, 196.5, 464.0, False),
        "down":  (625.5, 330.0, 670.5, 390.0, False),
    },
    "right_leg": {
        "back":  (475.5, 66.0,  568.5, 126.0, True),
        "right": (475.5, 130.0, 568.5, 190.0, True),
        "front": (475.5, 194.0, 568.5, 254.0, True),
        "left":  (475.5, 258.0, 568.5, 318.0, True),
        "up":    (355.5, 330.0, 400.5, 390.0, False),
        "down":  (463.5, 330.0, 508.5, 390.0, False),
    },
    "left_leg": {
        "right": (625.5, 2.0,   718.5, 62.0,  True),
        "front": (625.5, 66.0,  718.5, 126.0, True),
        "left":  (625.5, 130.0, 718.5, 190.0, True),
        "back":  (625.5, 194.0, 718.5, 254.0, True),
        "up":    (409.5, 330.0, 454.5, 390.0, False),
        "down":  (517.5, 330.0, 562.5, 390.0, False),
    },
}

# Bounding regions on 1024x512 atlas for filling base BrickColors (with bevel margins)
PART_BASE_FILLS = {
    "torso":     [(18, 0, 128, 395), (146, 323, 352, 396)],
    "right_arm": [(166, 58, 278, 325), (566, 324, 622, 396), (674, 324, 730, 396)],
    "left_arm":  [(316, 0, 428, 265), (146, 398, 203, 472), (620, 324, 676, 396)],
    "right_leg": [(466, 58, 578, 325), (350, 324, 406, 396), (458, 324, 514, 396)],
    "left_leg":  [(616, 0, 728, 265), (404, 324, 460, 396), (512, 324, 568, 396)],
    "head":      [(880, 0, 1024, 150)],
}


def hex_rgba(hex_str: str, alpha: int = 255):
    h = hex_str.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)


def make_royal_tuxedo_shirt() -> Image.Image:
    """Create an authentic 585x559 Roblox Classic Gold-Trim Royal Tuxedo Shirt template."""
    img = Image.new("RGBA", (585, 559), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    black = (22, 24, 30, 255)
    charcoal = (34, 37, 46, 255)
    white = (242, 244, 248, 255)
    gold = (232, 188, 62, 255)
    gold_dark = (182, 138, 34, 255)
    crimson = (185, 28, 42, 255)

    # Torso solid black base
    for k, box in RBX_TORSO.items():
        d.rectangle(box, fill=black)

    # Torso front details: crisp white V-shirt, gold lapels, gold buttons, crimson pocket square
    fx0, fy0, fx1, fy1 = RBX_TORSO["front"]
    cx = (fx0 + fx1) // 2
    # White V dress shirt
    d.polygon([(cx - 26, fy0), (cx + 26, fy0), (cx, fy0 + 78)], fill=white)
    # Suit lapels
    d.polygon([(cx - 34, fy0), (cx - 24, fy0), (cx - 2, fy0 + 78), (cx - 16, fy0 + 72)], fill=charcoal, outline=gold)
    d.polygon([(cx + 34, fy0), (cx + 24, fy0), (cx + 2, fy0 + 78), (cx + 16, fy0 + 72)], fill=charcoal, outline=gold)
    # Gold bow tie
    d.polygon([(cx - 18, fy0 + 10), (cx - 2, fy0 + 17), (cx - 18, fy0 + 24)], fill=gold, outline=gold_dark)
    d.polygon([(cx + 18, fy0 + 10), (cx + 2, fy0 + 17), (cx + 18, fy0 + 24)], fill=gold, outline=gold_dark)
    d.ellipse([cx - 5, fy0 + 12, cx + 5, fy0 + 22], fill=gold, outline=gold_dark)
    # Gold waistcoat buttons
    for by in (fy0 + 86, fy0 + 104):
        d.ellipse([cx - 4, by - 4, cx + 4, by + 4], fill=gold, outline=gold_dark)
    # Gold pocket trim + crimson pocket square on chest
    d.polygon([(cx + 24, fy0 + 44), (cx + 46, fy0 + 44), (cx + 38, fy0 + 34), (cx + 28, fy0 + 38)], fill=crimson)
    d.rectangle([cx + 22, fy0 + 44, cx + 48, fy0 + 48], fill=gold)
    # Bottom gold hem accent
    d.rectangle([fx0, fy1 - 6, fx1, fy1], fill=gold_dark)

    # Torso back subtle seam + gold hem
    bx0, by0, bx1, by1 = RBX_TORSO["back"]
    d.line([( (bx0 + bx1)//2, by0 + 12), ((bx0 + bx1)//2, by1 - 8)], fill=charcoal, width=3)
    d.rectangle([bx0, by1 - 6, bx1, by1], fill=gold_dark)

    # Sleeves (leave bottom 24px transparent for hands!)
    for limb_map in (RBX_RIGHT_LIMB, RBX_LEFT_LIMB):
        d.rectangle(limb_map["up"], fill=black)
        for side in ("front", "back", "left", "right"):
            x0, y0, x1, y1 = limb_map[side]
            sleeve_end = y1 - 32
            d.rectangle([x0, y0, x1, sleeve_end], fill=black)
            # Crisp white French cuff + gold trim
            d.rectangle([x0, sleeve_end - 8, x1, sleeve_end - 3], fill=gold)
            d.rectangle([x0, sleeve_end - 3, x1, sleeve_end + 4], fill=white)
            # Gold cufflink dot on outer sleeve
            if side in ("right", "left"):
                d.ellipse([x0 + 28, sleeve_end - 1, x0 + 36, sleeve_end + 5], fill=gold)

    out_p = TEX_DIR / "custom_royal_tuxedo_585x559.png"
    img.save(out_p)
    return img


def paste_patch_with_bleed(atlas: Image.Image, patch: Image.Image, rect, scale: int = 2, bleed: int = 3):
    x0, y0, x1, y1, rot_cw = rect
    if rot_cw:
        patch = patch.transpose(Image.Transpose.ROTATE_270)
    dx0, dy0 = int(round(x0 * scale)), int(round(y0 * scale))
    dx1, dy1 = int(round(x1 * scale)), int(round(y1 * scale))
    tw, th = max(1, dx1 - dx0), max(1, dy1 - dy0)
    resized = patch.resize((tw, th), Image.Resampling.LANCZOS)

    # Create padded version with edge-clamping bleed so beveled edges never show seam cracks
    b = bleed * scale
    padded = Image.new("RGBA", (tw + 2 * b, th + 2 * b), (0, 0, 0, 0))
    padded.paste(resized, (b, b))
    # Clamp edges
    top_strip = resized.crop((0, 0, tw, 1)).resize((tw, b))
    bot_strip = resized.crop((0, th - 1, tw, th)).resize((tw, b))
    padded.paste(top_strip, (b, 0))
    padded.paste(bot_strip, (b, b + th))
    left_strip = padded.crop((b, 0, b + 1, th + 2 * b)).resize((b, th + 2 * b))
    right_strip = padded.crop((b + tw - 1, 0, b + tw, th + 2 * b)).resize((b, th + 2 * b))
    padded.paste(left_strip, (0, 0))
    padded.paste(right_strip, (b + tw, 0))

    atlas.alpha_composite(padded, (dx0 - b, dy0 - b))


def bake_character_atlas(
    char_id: str,
    body_colors: dict,
    face_key: str,
    shirt_key: str | None = None,
    pants_key: str | None = None,
    custom_shirt_img: Image.Image | None = None,
    scale: int = 2,
) -> Path:
    """
    Bake a crisp (1024*scale) x (512*scale) RGBA texture atlas for Blender_R6_Rig_v222.blend.
    Order matches authentic Roblox R6 compositing:
      1. Base BrickColor skin per limb
      2. Classic Pants (torso + legs)
      3. Classic Shirt (torso + arms)
      4. Classic Face decal on Head front
    """
    w, h = 1024 * scale, 512 * scale
    head_col = hex_rgba(body_colors["head"])
    atlas = Image.new("RGBA", (w, h), head_col)
    draw = ImageDraw.Draw(atlas)

    # 1. Fill base skin/BrickColors for each body part region
    for part_name, rects in PART_BASE_FILLS.items():
        col = hex_rgba(body_colors.get(part_name, body_colors["head"]))
        for rx0, ry0, rx1, ry1 in rects:
            draw.rectangle([rx0 * scale, ry0 * scale, rx1 * scale, ry1 * scale], fill=col)

    # Helper to load standard 585x559 template
    def load_template(key):
        if not key:
            return None
        p = MANIFEST[key]["files"]["texture"]
        im = Image.open(p).convert("RGBA")
        if im.size != (585, 559):
            im = im.resize((585, 559), Image.Resampling.LANCZOS)
        return im

    # 2. Composite Pants (torso + right_leg + left_leg)
    pants_img = load_template(pants_key)
    if pants_img is not None:
        for side, box in RBX_TORSO.items():
            paste_patch_with_bleed(atlas, pants_img.crop(box), ATLAS_RECTS["torso"][side], scale=scale)
        for side, box in RBX_RIGHT_LIMB.items():
            paste_patch_with_bleed(atlas, pants_img.crop(box), ATLAS_RECTS["right_leg"][side], scale=scale)
        for side, box in RBX_LEFT_LIMB.items():
            paste_patch_with_bleed(atlas, pants_img.crop(box), ATLAS_RECTS["left_leg"][side], scale=scale)

    # 3. Composite Shirt (torso + right_arm + left_arm)
    shirt_img = custom_shirt_img if custom_shirt_img is not None else load_template(shirt_key)
    if shirt_img is not None:
        for side, box in RBX_TORSO.items():
            paste_patch_with_bleed(atlas, shirt_img.crop(box), ATLAS_RECTS["torso"][side], scale=scale)
        for side, box in RBX_RIGHT_LIMB.items():
            paste_patch_with_bleed(atlas, shirt_img.crop(box), ATLAS_RECTS["right_arm"][side], scale=scale)
        for side, box in RBX_LEFT_LIMB.items():
            paste_patch_with_bleed(atlas, shirt_img.crop(box), ATLAS_RECTS["left_arm"][side], scale=scale)

    # 4. Composite Face Decal onto Head square
    # Measured Head front square in R6rig1_diff.png: X=[896..1024], Y=[0..128] (actual face center ~959.5, 64)
    face_path = MANIFEST[face_key]["files"]["texture"]
    face_img = Image.open(face_path).convert("RGBA")
    # Place nicely centered on the face region (slight 88% fit inside 128x128 so eyes/mouth match authentic Roblox proportions!)
    face_box_sz = int(round(110 * scale))
    face_resized = face_img.resize((face_box_sz, face_box_sz), Image.Resampling.LANCZOS)
    cx = int(round(959.5 * scale))
    cy = int(round(64.0 * scale))
    atlas.alpha_composite(face_resized, (cx - face_box_sz // 2, cy - face_box_sz // 2))

    out_path = TEX_DIR / f"{char_id}_atlas.png"
    atlas.save(out_path)
    return out_path


# Full 8-character cast configuration (shared with build_characters.py!)
CHARACTER_SPECS = [
    {
        "id": "01_Alex_Protagonist",
        "display_name": "Alex (Protagonist)",
        "role": "Main Hero / Story Narrator",
        "feminine": False,
        "body_colors": {
            "head": "#F2C9A0", "torso": "#F2C9A0",
            "left_arm": "#F2C9A0", "right_arm": "#F2C9A0",
            "left_leg": "#F2C9A0", "right_leg": "#F2C9A0",
        },
        "face": "face_check_it",
        "shirt": "shirt_denim_hoodie",
        "pants": "pants_black_white",
        "accessories": ["pal_hair"],
        "extra_accessories": ["red_roblox_cap"],  # Included hidden in collection so user can toggle!
        "pose": "hero_wave",
    },
    {
        "id": "02_Noob_BestFriend",
        "display_name": "Noob (Best Friend)",
        "role": "Classic Goofy Best Friend / Comic Relief",
        "feminine": False,
        "body_colors": {
            "head": "#F5CD30", "torso": "#0D69AC",
            "left_arm": "#F5CD30", "right_arm": "#F5CD30",
            "left_leg": "#A4BD47", "right_leg": "#A4BD47",
        },
        "face": "face_silly_fun",
        "shirt": None,
        "pants": None,
        "accessories": ["red_roblox_cap"],
        "extra_accessories": ["propeller_beanie"],
        "pose": "noob_excited",
    },
    {
        "id": "03_RichKid_Dominus",
        "display_name": "Rich Kid (Dominus)",
        "role": "Rich Flexer / Billionaire Rival",
        "feminine": False,
        "body_colors": {
            "head": "#F5D5B8", "torso": "#1B1D24",
            "left_arm": "#F5D5B8", "right_arm": "#F5D5B8",
            "left_leg": "#1B1D24", "right_leg": "#1B1D24",
        },
        "face": "face_chill",
        "shirt": "__CUSTOM_ROYAL_TUXEDO__",
        "pants": "pants_black_slacks",
        "accessories": ["dominus_empyreus", "clockwork_shades"],
        "extra_accessories": ["domino_crown"],
        "pose": "rich_flex",
    },
    {
        "id": "04_Maya_BestFriend",
        "display_name": "Maya (Best Friend)",
        "role": "Cool Girl / Smart Best Friend / Sister",
        "feminine": True,
        "body_colors": {
            "head": "#F0C4A0", "torso": "#F0C4A0",
            "left_arm": "#F0C4A0", "right_arm": "#F0C4A0",
            "left_leg": "#F0C4A0", "right_leg": "#F0C4A0",
        },
        "face": "face_sshf",
        "shirt": "shirt_pastel_jacket",
        "pants": "pants_beautiful_you",
        "accessories": ["beautiful_hair", "rose_glasses"],
        "extra_accessories": ["roblox_girl_hair", "chestnut_bun"],
        "pose": "maya_cheer",
    },
    {
        "id": "05_Dad_Principal",
        "display_name": "Dad / Principal",
        "role": "Strict Dad / Teacher / Principal",
        "feminine": False,
        "body_colors": {
            "head": "#E5B58B", "torso": "#E5B58B",
            "left_arm": "#E5B58B", "right_arm": "#E5B58B",
            "left_leg": "#E5B58B", "right_leg": "#E5B58B",
        },
        "face": "face_man",
        "shirt": "shirt_blue_plaid",
        "pants": "pants_black_slacks",
        "accessories": ["classic_fedora", "nerd_glasses"],
        "extra_accessories": ["shaggy"],
        "pose": "dad_lecture",
    },
    {
        "id": "06_Hacker_Glitch",
        "display_name": "Hacker (Chaos)",
        "role": "Chaos Hacker / Prankster Villain",
        "feminine": False,
        "body_colors": {
            "head": "#3A3E4C", "torso": "#1E2028",
            "left_arm": "#3A3E4C", "right_arm": "#3A3E4C",
            "left_leg": "#1E2028", "right_leg": "#1E2028",
        },
        "face": "face_err",
        "shirt": "shirt_guitar_black",
        "pants": "pants_ripped_skater",
        "accessories": ["void_star", "midnight_shades", "bandit_mask"],
        "extra_accessories": ["domino_crown"],
        "pose": "hacker_scheme",
    },
    {
        "id": "07_Admin_Boss",
        "display_name": "Admin (Boss)",
        "role": "Roblox Admin / Judge / Final Boss",
        "feminine": False,
        "body_colors": {
            "head": "#F2C9A0", "torso": "#1E2A44",
            "left_arm": "#F2C9A0", "right_arm": "#F2C9A0",
            "left_leg": "#1E2A44", "right_leg": "#1E2A44",
        },
        "face": "face_skeptic",
        "shirt": "shirt_moto_blue",
        "pants": "pants_black_sneak",
        "accessories": ["valkyrie_helm", "swordpack"],
        "extra_accessories": ["clockwork_shades"],
        "pose": "admin_power",
    },
    {
        "id": "08_Chloe_Rival",
        "display_name": "Chloe (Rival)",
        "role": "Popular Rival / Sassy Classmate / Karen",
        "feminine": True,
        "body_colors": {
            "head": "#EAC096", "torso": "#EAC096",
            "left_arm": "#EAC096", "right_arm": "#EAC096",
            "left_leg": "#EAC096", "right_leg": "#EAC096",
        },
        "face": "face_woman",
        "shirt": "shirt_purple_teal",
        "pants": "pants_jean_shorts",
        "accessories": ["lavender_updo", "stylish_aviators"],
        "extra_accessories": ["blonde_spiked_hair"],
        "pose": "chloe_sass",
    },
]


def main():
    tux_img = make_royal_tuxedo_shirt()
    out_specs = []
    for spec in CHARACTER_SPECS:
        custom_shirt = tux_img if spec["shirt"] == "__CUSTOM_ROYAL_TUXEDO__" else None
        shirt_key = None if custom_shirt is not None else spec["shirt"]
        atlas_path = bake_character_atlas(
            char_id=spec["id"],
            body_colors=spec["body_colors"],
            face_key=spec["face"],
            shirt_key=shirt_key,
            pants_key=spec["pants"],
            custom_shirt_img=custom_shirt,
            scale=2,
        )
        rec = dict(spec)
        rec["atlas_path"] = str(atlas_path)
        out_specs.append(rec)
        print(f"[BAKED] {spec['id']:22s} -> {atlas_path.name}")

    # Also save an expression-swap reference JSON
    (ROOT / "characters_manifest.json").write_text(json.dumps(out_specs, indent=2), encoding="utf-8")
    print(f"Saved {len(out_specs)} character specs -> {ROOT / 'characters_manifest.json'}")


if __name__ == "__main__":
    main()
