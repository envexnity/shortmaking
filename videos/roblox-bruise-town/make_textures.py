"""
make_textures.py — Step 3 R6 2048x1024 Atlas Texture Factory for videos/roblox-bruise-town.
Reuses exact UV coordinates & Roblox Marketplace assets from assets/roblox-r6-characters:
  - Main 2 avatars preserved:
      1) Toby (01_Alex_Protagonist_atlas.png copied verbatim)
      2) Sam Unmarked (02_Noob_BestFriend_atlas.png copied verbatim)
      3) Sam Shop Jacket / Hoodie (02_Sam_ShopJacket_atlas.png: dark charcoal greasy hoodie/jacket + exact Noob head & Silly Fun face)
      4) Sam Bruised (02_Sam_Bruised_atlas.png: exact same Silly Fun face pixels kept sharp on top of deep purple/blue swollen eye rings, cheekbone welt, split lip & jaw bruises)
  - Grounded IRL Background Characters (all keeping classic Roblox faces!):
      5) Marcus Vance (bg_marcus_atlas.png): crimson/white IRL varsity letterman jacket + dark jeans + classic Skeptic face w/ permanent dark-purple black eyes, split lip & fresh purple cheek welt
      6) Mom (bg_mom_atlas.png): soft light-blue IRL hospital gown / cozy cardigan + dark pants + classic Woman face
      7) IRL Student 1 (bg_student1_atlas.png): olive/grey denim jacket + black jeans + classic Check It face
      8) IRL Student 2 (bg_student2_atlas.png): blue plaid flannel + black slacks + classic Chill face
      9) IRL Student 3 (bg_student3_atlas.png): pastel/burgundy everyday top + dark jeans + classic Woman face
     10) Auto Shop Mechanic (bg_mechanic_atlas.png): navy work jacket + charcoal pants + classic Man face
     11) Roblox Thorfinn Outro (outro_thorfinn_atlas.png): earthy brown Viking tunic + belt + dark trousers + classic Skeptic/calm face
"""
import json
import shutil
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking")
R6_DIR = ROOT / "assets" / "roblox-r6-characters"
sys.path.insert(0, str(R6_DIR / "scripts"))
import bake_textures as bt  # noqa: E402

PROJ_DIR = ROOT / "videos" / "roblox-bruise-town"
OUT_TEX = PROJ_DIR / "textures"
OUT_TEX.mkdir(parents=True, exist_ok=True)
bt.TEX_DIR = OUT_TEX


def make_solid_irl_shirt(
    torso_col=(42, 46, 54, 255),
    sleeve_col=(42, 46, 54, 255),
    accent_col=(28, 30, 36, 255),
    collar_col=(210, 214, 220, 255),
    varsity: bool = False,
    vik_tunic: bool = False,
) -> Image.Image:
    """Create a 585x559 Roblox Classic Shirt template for grounded IRL outfits (or Viking tunic)."""
    img = Image.new("RGBA", (585, 559), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    for k, box in bt.RBX_TORSO.items():
        d.rectangle(box, fill=torso_col)

    fx0, fy0, fx1, fy1 = bt.RBX_TORSO["front"]
    cx = (fx0 + fx1) // 2

    if varsity:
        # White snap placket + V-neck collar stripes + crimson pockets
        d.rectangle([cx - 5, fy0 + 18, cx + 5, fy1 - 8], fill=accent_col)
        for y in range(fy0 + 26, fy1 - 12, 16):
            d.ellipse([cx - 2, y - 2, cx + 2, y + 2], fill=(230, 232, 238, 255))
        d.polygon([(cx - 24, fy0), (cx + 24, fy0), (cx, fy0 + 24)], fill=collar_col)
        d.rectangle([fx0, fy1 - 10, fx1, fy1], fill=accent_col)
        d.rectangle([fx0, fy1 - 7, fx1, fy1 - 3], fill=collar_col)
        bx0, by0, bx1, by1 = bt.RBX_TORSO["back"]
        d.rectangle([bx0, by1 - 10, bx1, by1], fill=accent_col)
        d.rectangle([bx0, by1 - 7, bx1, by1 - 3], fill=collar_col)
    elif vik_tunic:
        # Rustic brown tunic with cross-laced collar & leather belt
        d.polygon([(cx - 20, fy0), (cx + 20, fy0), (cx, fy0 + 34)], fill=(58, 42, 30, 255))
        d.rectangle([fx0, fy1 - 24, fx1, fy1 - 10], fill=(48, 32, 20, 255))
        d.rectangle([cx - 8, fy1 - 25, cx + 8, fy1 - 9], fill=(165, 138, 86, 255))
        bx0, by0, bx1, by1 = bt.RBX_TORSO["back"]
        d.rectangle([bx0, by1 - 24, bx1, by1 - 10], fill=(48, 32, 20, 255))
    else:
        # Hoodie / work jacket zip + pockets + grease/seam shading
        d.rectangle([cx - 2, fy0 + 14, cx + 2, fy1 - 6], fill=accent_col)
        d.polygon([(cx - 18, fy0), (cx + 18, fy0), (cx, fy0 + 18)], fill=collar_col)
        d.rectangle([fx0 + 10, fy1 - 36, cx - 10, fy1 - 10], fill=accent_col)
        d.rectangle([cx + 10, fy1 - 36, fx1 - 10, fy1 - 10], fill=accent_col)
        d.rectangle([fx0, fy1 - 8, fx1, fy1], fill=accent_col)

    for limb_map in (bt.RBX_RIGHT_LIMB, bt.RBX_LEFT_LIMB):
        d.rectangle(limb_map["up"], fill=sleeve_col)
        for side in ("front", "back", "left", "right"):
            x0, y0, x1, y1 = limb_map[side]
            sleeve_end = y1 - 30
            d.rectangle([x0, y0, x1, sleeve_end], fill=sleeve_col)
            d.rectangle([x0, sleeve_end - 8, x1, sleeve_end], fill=accent_col)
            if varsity:
                d.rectangle([x0, sleeve_end - 6, x1, sleeve_end - 3], fill=collar_col)

    return img


def make_solid_irl_pants(pant_col=(36, 42, 54, 255), shoe_col=(228, 230, 235, 255)) -> Image.Image:
    """Create a 585x559 Roblox Classic Pants template with realistic jeans/slacks & sneakers."""
    img = Image.new("RGBA", (585, 559), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for _, box in bt.RBX_TORSO.items():
        d.rectangle(box, fill=pant_col)
    for limb_map in (bt.RBX_RIGHT_LIMB, bt.RBX_LEFT_LIMB):
        d.rectangle(limb_map["up"], fill=pant_col)
        d.rectangle(limb_map["down"], fill=shoe_col)
        for side in ("front", "back", "left", "right"):
            x0, y0, x1, y1 = limb_map[side]
            d.rectangle([x0, y0, x1, y1 - 24], fill=pant_col)
            d.rectangle([x0, y1 - 24, x1, y1], fill=shoe_col)
            d.rectangle([x0, y1 - 6, x1, y1], fill=(32, 34, 40, 255))
    return img


def bake_atlas_custom(
    char_id: str,
    body_colors: dict,
    face_key: str,
    shirt_key: str | None = None,
    pants_key: str | None = None,
    custom_shirt_img: Image.Image | None = None,
    custom_pants_img: Image.Image | None = None,
    bruise_mode: str | None = None,
) -> Path:
    """Bake 2048x1024 atlas with optional under-face bruise layer while keeping Roblox face ink crisp."""
    scale = 2
    w, h = 1024 * scale, 512 * scale
    head_col = bt.hex_rgba(body_colors["head"])
    atlas = Image.new("RGBA", (w, h), head_col)
    draw = ImageDraw.Draw(atlas)

    for part_name, rects in bt.PART_BASE_FILLS.items():
        col = bt.hex_rgba(body_colors.get(part_name, body_colors["head"]))
        for rx0, ry0, rx1, ry1 in rects:
            draw.rectangle([rx0 * scale, ry0 * scale, rx1 * scale, ry1 * scale], fill=col)

    def load_tpl(key):
        if not key:
            return None
        im = Image.open(bt.MANIFEST[key]["files"]["texture"]).convert("RGBA")
        if im.size != (585, 559):
            im = im.resize((585, 559), Image.Resampling.LANCZOS)
        return im

    pants_img = custom_pants_img if custom_pants_img is not None else load_tpl(pants_key)
    if pants_img is not None:
        for side, box in bt.RBX_TORSO.items():
            bt.paste_patch_with_bleed(atlas, pants_img.crop(box), bt.ATLAS_RECTS["torso"][side], scale=scale)
        for side, box in bt.RBX_RIGHT_LIMB.items():
            bt.paste_patch_with_bleed(atlas, pants_img.crop(box), bt.ATLAS_RECTS["right_leg"][side], scale=scale)
        for side, box in bt.RBX_LEFT_LIMB.items():
            bt.paste_patch_with_bleed(atlas, pants_img.crop(box), bt.ATLAS_RECTS["left_leg"][side], scale=scale)

    shirt_img = custom_shirt_img if custom_shirt_img is not None else load_tpl(shirt_key)
    if shirt_img is not None:
        for side, box in bt.RBX_TORSO.items():
            bt.paste_patch_with_bleed(atlas, shirt_img.crop(box), bt.ATLAS_RECTS["torso"][side], scale=scale)
        for side, box in bt.RBX_RIGHT_LIMB.items():
            bt.paste_patch_with_bleed(atlas, shirt_img.crop(box), bt.ATLAS_RECTS["right_arm"][side], scale=scale)
        for side, box in bt.RBX_LEFT_LIMB.items():
            bt.paste_patch_with_bleed(atlas, shirt_img.crop(box), bt.ATLAS_RECTS["left_arm"][side], scale=scale)

    # Paint bruise shading directly on head skin BEFORE compositing the original Roblox face lines
    if bruise_mode in ("sam_heavy", "marcus_perm"):
        bruise_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        bd = ImageDraw.Draw(bruise_layer)
        # Head front center: cx=1919, cy=128
        if bruise_mode == "sam_heavy":
            # Both eyes swollen dark purple & deep blue
            bd.ellipse([1858, 66, 1916, 114], fill=(64, 24, 96, 228))
            bd.ellipse([1922, 66, 1982, 116], fill=(56, 22, 92, 232))
            bd.ellipse([1870, 74, 1908, 102], fill=(38, 16, 68, 225))
            bd.ellipse([1930, 74, 1972, 104], fill=(38, 16, 68, 225))
            # Cheekbone bruised black/violet
            bd.ellipse([1836, 108, 1898, 152], fill=(48, 22, 74, 210))
            bd.ellipse([1944, 114, 1996, 154], fill=(78, 30, 104, 185))
            # Jaw deep welts
            bd.ellipse([1846, 160, 1906, 206], fill=(68, 26, 94, 195))
            bd.ellipse([1936, 164, 1994, 208], fill=(82, 34, 104, 185))
            # Split lip dark crimson swelling
            bd.ellipse([1896, 174, 1942, 204], fill=(122, 20, 44, 205))
        elif bruise_mode == "marcus_perm":
            # Two permanent black eyes around face_skeptic eyes (1875, 92) and (1962, 92)
            bd.ellipse([1844, 68, 1906, 118], fill=(62, 24, 92, 218))
            bd.ellipse([1932, 68, 1994, 118], fill=(62, 24, 92, 218))
            # Fresh purple welt blooming across cheek
            bd.ellipse([1948, 116, 2004, 158], fill=(104, 30, 128, 200))
            # Split lip bruise
            bd.ellipse([1906, 156, 1948, 184], fill=(118, 24, 48, 195))

        bruise_layer = bruise_layer.filter(ImageFilter.GaussianBlur(radius=8))
        atlas = Image.alpha_composite(atlas, bruise_layer)

    # Composite exact Roblox face decal cleanly on top so face expression stays 100% original
    face_path = bt.MANIFEST[face_key]["files"]["texture"]
    face_img = Image.open(face_path).convert("RGBA")
    face_box_sz = int(round(110 * scale))
    face_resized = face_img.resize((face_box_sz, face_box_sz), Image.Resampling.LANCZOS)
    cx = int(round(959.5 * scale))
    cy = int(round(64.0 * scale))
    atlas.alpha_composite(face_resized, (cx - face_box_sz // 2, cy - face_box_sz // 2))

    # Crisp split-lip slash accent on top for heavy bruise readability at 270x480
    if bruise_mode in ("sam_heavy", "marcus_perm"):
        ad = ImageDraw.Draw(atlas)
        lip_y = 186 if bruise_mode == "sam_heavy" else 172
        ad.line([(1924, lip_y - 6), (1929, lip_y + 7)], fill=(142, 16, 36, 235), width=4)

    out_path = OUT_TEX / f"{char_id}_atlas.png"
    atlas.save(out_path)
    return out_path


def main():
    # 1. Exact original main 2 avatars copied directly
    for fn in ("01_Alex_Protagonist_atlas.png", "02_Noob_BestFriend_atlas.png"):
        shutil.copy2(R6_DIR / "textures" / fn, OUT_TEX / fn)
        print("[OK] Copied original:", OUT_TEX / fn)

    # 2. Sam Shop Jacket (greasy charcoal jacket + exact Noob head & Silly Fun face)
    sam_colors = {
        "head": "#F5CD30", "torso": "#2B2E36",
        "left_arm": "#F5CD30", "right_arm": "#F5CD30",
        "left_leg": "#252932", "right_leg": "#252932",
    }
    sam_jacket = make_solid_irl_shirt(
        torso_col=(44, 48, 56, 255),
        sleeve_col=(40, 44, 52, 255),
        accent_col=(24, 26, 32, 255),
        collar_col=(62, 66, 76, 255),
    )
    sam_pants = make_solid_irl_pants(pant_col=(36, 40, 48, 255), shoe_col=(205, 208, 212, 255))
    bake_atlas_custom("02_Sam_ShopJacket", sam_colors, "face_silly_fun",
                      custom_shirt_img=sam_jacket, custom_pants_img=sam_pants)

    # 3. Sam Bruised (exact same hoodie/jacket + exact Silly Fun face + heavy purple/blue bruises)
    bake_atlas_custom("02_Sam_Bruised", sam_colors, "face_silly_fun",
                      custom_shirt_img=sam_jacket, custom_pants_img=sam_pants, bruise_mode="sam_heavy")

    # 4. Marcus Vance (IRL crimson/white varsity letterman jacket + permanent black eyes & cheek welt + classic Skeptic face)
    marcus_colors = {
        "head": "#E8BE96", "torso": "#E8BE96",
        "left_arm": "#E8BE96", "right_arm": "#E8BE96",
        "left_leg": "#E8BE96", "right_leg": "#E8BE96",
    }
    varsity_shirt = make_solid_irl_shirt(
        torso_col=(148, 24, 34, 255),
        sleeve_col=(236, 236, 240, 255),
        accent_col=(110, 18, 26, 255),
        collar_col=(242, 242, 244, 255),
        varsity=True,
    )
    marcus_pants = make_solid_irl_pants(pant_col=(38, 42, 50, 255), shoe_col=(236, 238, 242, 255))
    bake_atlas_custom("bg_marcus", marcus_colors, "face_skeptic",
                      custom_shirt_img=varsity_shirt, custom_pants_img=marcus_pants, bruise_mode="marcus_perm")

    # 5. Mom (Hospital gown / cozy light blue + dark slacks + classic Woman face)
    mom_colors = {
        "head": "#F0C4A0", "torso": "#F0C4A0",
        "left_arm": "#F0C4A0", "right_arm": "#F0C4A0",
        "left_leg": "#F0C4A0", "right_leg": "#F0C4A0",
    }
    mom_gown = make_solid_irl_shirt(
        torso_col=(148, 194, 222, 255),
        sleeve_col=(148, 194, 222, 255),
        accent_col=(118, 166, 198, 255),
        collar_col=(230, 242, 250, 255),
    )
    mom_pants = make_solid_irl_pants(pant_col=(48, 56, 68, 255), shoe_col=(220, 224, 230, 255))
    bake_atlas_custom("bg_mom", mom_colors, "face_woman", custom_shirt_img=mom_gown, custom_pants_img=mom_pants)

    # 6. 3 IRL Background Students (real Roblox Marketplace everyday outfits + classic faces)
    bake_atlas_custom(
        "bg_student1",
        {"head": "#ECC19A", "torso": "#ECC19A", "left_arm": "#ECC19A", "right_arm": "#ECC19A", "left_leg": "#ECC19A", "right_leg": "#ECC19A"},
        "face_check_it",
        shirt_key="shirt_grey_denim",
        pants_key="pants_black_sneak",
    )
    bake_atlas_custom(
        "bg_student2",
        {"head": "#D6A378", "torso": "#D6A378", "left_arm": "#D6A378", "right_arm": "#D6A378", "left_leg": "#D6A378", "right_leg": "#D6A378"},
        "face_chill",
        shirt_key="shirt_blue_plaid",
        pants_key="pants_black_slacks",
    )
    bake_atlas_custom(
        "bg_student3",
        {"head": "#F2C9A0", "torso": "#F2C9A0", "left_arm": "#F2C9A0", "right_arm": "#F2C9A0", "left_leg": "#F2C9A0", "right_leg": "#F2C9A0"},
        "face_woman",
        shirt_key="shirt_pastel_jacket",
        pants_key="pants_dark_green",
    )

    # 7. Auto Shop Mechanic Coworker (grounded IRL work clothes + Man face)
    bake_atlas_custom(
        "bg_mechanic",
        {"head": "#E5B58B", "torso": "#E5B58B", "left_arm": "#E5B58B", "right_arm": "#E5B58B", "left_leg": "#E5B58B", "right_leg": "#E5B58B"},
        "face_man",
        custom_shirt_img=make_solid_irl_shirt((34, 48, 72, 255), (34, 48, 72, 255), (22, 30, 48, 255), (180, 186, 196, 255)),
        pants_key="pants_black_slacks",
    )

    # 8. Roblox-Style Thorfinn Outro (earthy Viking tunic + classic Skeptic face)
    thorfinn_colors = {
        "head": "#F0C59B", "torso": "#F0C59B",
        "left_arm": "#F0C59B", "right_arm": "#F0C59B",
        "left_leg": "#F0C59B", "right_leg": "#F0C59B",
    }
    thorfinn_tunic = make_solid_irl_shirt(
        torso_col=(118, 86, 56, 255),
        sleeve_col=(92, 68, 46, 255),
        accent_col=(62, 44, 28, 255),
        collar_col=(48, 34, 22, 255),
        vik_tunic=True,
    )
    thorfinn_pants = make_solid_irl_pants(pant_col=(44, 38, 34, 255), shoe_col=(66, 48, 34, 255))
    bake_atlas_custom("outro_thorfinn", thorfinn_colors, "face_skeptic",
                      custom_shirt_img=thorfinn_tunic, custom_pants_img=thorfinn_pants)

    print("\n[OK] All 11 character atlases generated in", OUT_TEX)


if __name__ == "__main__":
    main()
