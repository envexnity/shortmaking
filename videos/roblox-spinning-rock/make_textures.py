"""
make_textures.py — R6 2048x1024 Atlas Texture Factory for videos/roblox-spinning-rock.
Preserves the exact 2 main R6 avatars (01_Alex_Protagonist & 02_Noob_BestFriend) verbatim,
adds clean classic Roblox expression swaps, and generates 6 grounded IRL background character
atlases inspired by @huss.hero's clean, bright everyday suburban neighborhood cast.
"""
import shutil
import sys
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking")
R6_DIR = ROOT / "assets" / "roblox-r6-characters"
DF1_EXPR = ROOT / "videos" / "roblox-reel-Df1kubCJ-o0" / "expressions"
PROJ_DIR = ROOT / "videos" / "roblox-spinning-rock"
OUT_TEX = PROJ_DIR / "textures"
OUT_TEX.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(R6_DIR / "scripts"))
import bake_textures as bt  # noqa: E402

bt.TEX_DIR = OUT_TEX


def make_irl_shirt(
    torso_col=(72, 146, 232, 255),
    sleeve_col=(72, 146, 232, 255),
    accent_col=(46, 106, 186, 255),
    collar_col=(242, 244, 248, 255),
    kind: str = "hoodie",
) -> Image.Image:
    """Create a clean 585x559 Roblox Classic Shirt template for grounded IRL outfits."""
    img = Image.new("RGBA", (585, 559), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    for _, box in bt.RBX_TORSO.items():
        d.rectangle(box, fill=torso_col)

    fx0, fy0, fx1, fy1 = bt.RBX_TORSO["front"]
    cx = (fx0 + fx1) // 2

    if kind == "hoodie":
        # Drawstrings + kangaroo pocket + bottom hem
        d.polygon([(cx - 22, fy0), (cx + 22, fy0), (cx, fy0 + 20)], fill=accent_col)
        d.rectangle([cx - 10, fy0 + 18, cx - 7, fy0 + 52], fill=collar_col)
        d.rectangle([cx + 7, fy0 + 18, cx + 10, fy0 + 52], fill=collar_col)
        d.rectangle([fx0 + 18, fy1 - 40, fx1 - 18, fy1 - 8], fill=accent_col)
        d.rectangle([fx0, fy1 - 8, fx1, fy1], fill=accent_col)
    elif kind == "tee":
        # Simple crew collar + subtle chest pocket
        d.arc([cx - 22, fy0 - 10, cx + 22, fy0 + 20], 0, 180, fill=accent_col, width=5)
        d.rectangle([cx + 16, fy0 + 26, cx + 38, fy0 + 50], fill=accent_col)
    else:  # sweater / jacket
        d.rectangle([cx - 2, fy0 + 14, cx + 2, fy1 - 6], fill=accent_col)
        d.polygon([(cx - 18, fy0), (cx + 18, fy0), (cx, fy0 + 18)], fill=collar_col)
        d.rectangle([fx0, fy1 - 8, fx1, fy1], fill=accent_col)

    sleeve_len = 82 if kind == "tee" else 98
    for limb_map in (bt.RBX_RIGHT_LIMB, bt.RBX_LEFT_LIMB):
        d.rectangle(limb_map["up"], fill=sleeve_col)
        for side in ("front", "back", "left", "right"):
            x0, y0, x1, y1 = limb_map[side]
            y_end = min(y1 - 12, y0 + sleeve_len)
            d.rectangle([x0, y0, x1, y_end], fill=sleeve_col)
            d.rectangle([x0, y_end - 6, x1, y_end], fill=accent_col)

    return img


def make_irl_pants(pant_col=(44, 62, 96, 255), shoe_col=(236, 238, 244, 255)) -> Image.Image:
    """Create a 585x559 Roblox Classic Pants template with everyday jeans/chinos & sneakers."""
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
            d.rectangle([x0, y1 - 6, x1, y1], fill=(32, 36, 44, 255))
    return img


def draw_shocked_face_decal() -> Image.Image:
    """Draw a crisp classic Roblox shocked O-mouth face decal (512x512 RGBA)."""
    im = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    blk = (18, 18, 22, 255)
    wht = (255, 255, 255, 255)
    red_m = (195, 42, 52, 255)
    dark_m = (65, 22, 28, 255)
    for cx in (184, 328):
        d.ellipse([cx - 34, 218 - 38, cx + 34, 218 + 38], fill=wht, outline=blk, width=7)
        d.ellipse([cx - 13, 218 - 16, cx + 13, 218 + 16], fill=blk)
    d.arc([148, 142, 220, 186], 200, 340, fill=blk, width=12)
    d.arc([292, 142, 364, 186], 200, 340, fill=blk, width=12)
    d.ellipse([214, 290, 298, 386], fill=dark_m, outline=blk, width=14)
    d.ellipse([232, 346, 280, 378], fill=red_m)
    return im


def bake_custom_atlas(
    char_id: str,
    body_colors: dict,
    face_key: str | None = None,
    face_img_override: Image.Image | None = None,
    shirt_key: str | None = None,
    pants_key: str | None = None,
    custom_shirt: Image.Image | None = None,
    custom_pants: Image.Image | None = None,
) -> Path:
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

    pants_img = custom_pants if custom_pants is not None else load_tpl(pants_key)
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

    if face_img_override is not None:
        face_img = face_img_override
    else:
        face_img = Image.open(bt.MANIFEST[face_key]["files"]["texture"]).convert("RGBA")
    face_box_sz = int(round(110 * scale))
    face_resized = face_img.resize((face_box_sz, face_box_sz), Image.Resampling.LANCZOS)
    cx = int(round(959.5 * scale))
    cy = int(round(64.0 * scale))
    atlas.alpha_composite(face_resized, (cx - face_box_sz // 2, cy - face_box_sz // 2))

    out_path = OUT_TEX / f"{char_id}_atlas.png"
    atlas.save(out_path)
    return out_path


def main():
    # 1. Exact Main 2 R6 avatars preserved verbatim
    for fn in ("01_Alex_Protagonist_atlas.png", "02_Noob_BestFriend_atlas.png"):
        shutil.copy2(R6_DIR / "textures" / fn, OUT_TEX / fn)
        print("[OK] Copied verbatim:", OUT_TEX / fn)

    # 2. Clean classic Roblox expression swaps for Alex & Noob (exact same body/clothes/style)
    for fn in ("alex_deadpan_atlas.png", "alex_shocked_atlas.png", "alex_determined_atlas.png"):
        src = DF1_EXPR / fn
        if src.exists():
            shutil.copy2(src, OUT_TEX / fn)
            print("[OK] Copied expression:", OUT_TEX / fn)

    bake_custom_atlas(
        "02_Noob_Shocked",
        {"head": "#F5CD30", "torso": "#0D69AC", "left_arm": "#F5CD30", "right_arm": "#F5CD30", "left_leg": "#A4BD47", "right_leg": "#A4BD47"},
        face_img_override=draw_shocked_face_decal(),
    )

    # 3. 6 Grounded IRL Background Cast (@huss.hero bright everyday street outfits + classic Roblox faces)
    def skin_dict(h):
        return {"head": h, "torso": h, "left_arm": h, "right_arm": h, "left_leg": h, "right_leg": h}

    # BG 1: Dog Walker in bright sky-blue hoodie + dark jeans + white sneakers + Chill face
    bake_custom_atlas(
        "bg_dogwalker",
        skin_dict("#E8BE96"),
        face_key="face_chill",
        custom_shirt=make_irl_shirt((82, 154, 232, 255), (82, 154, 232, 255), (52, 114, 188, 255), (242, 244, 248, 255), kind="hoodie"),
        custom_pants=make_irl_pants((42, 58, 86, 255), (240, 242, 248, 255)),
    )

    # BG 2: Neighbor Woman in soft pink sweater + blue jeans + white sneakers + Woman face
    bake_custom_atlas(
        "bg_woman_pink",
        skin_dict("#F2C9A0"),
        face_key="face_woman",
        custom_shirt=make_irl_shirt((244, 148, 186, 255), (244, 148, 186, 255), (206, 108, 148, 255), (252, 244, 248, 255), kind="sweater"),
        custom_pants=make_irl_pants((64, 96, 148, 255), (244, 246, 250, 255)),
    )

    # BG 3: Taxpayer Dad in real Roblox Blue Plaid Shirt + Black Slacks + Man face
    bake_custom_atlas(
        "bg_dad_plaid",
        skin_dict("#E5B58B"),
        face_key="face_man",
        shirt_key="shirt_blue_plaid",
        pants_key="pants_black_slacks",
    )

    # BG 4: Neighbor Guy in sage/emerald t-shirt + charcoal chinos + Skeptic face
    bake_custom_atlas(
        "bg_neighbor_green",
        skin_dict("#D8A87E"),
        face_key="face_skeptic",
        custom_shirt=make_irl_shirt((68, 184, 118, 255), (68, 184, 118, 255), (44, 142, 86, 255), (240, 246, 242, 255), kind="tee"),
        custom_pants=make_irl_pants((54, 60, 72, 255), (235, 238, 244, 255)),
    )

    # BG 5: Friend in warm coral hoodie + navy jeans + Smile face
    bake_custom_atlas(
        "bg_friend_coral",
        skin_dict("#C68E64"),
        face_key="face_smile",
        custom_shirt=make_irl_shirt((242, 126, 78, 255), (242, 126, 78, 255), (196, 88, 48, 255), (248, 242, 236, 255), kind="hoodie"),
        custom_pants=make_irl_pants((38, 48, 72, 255), (236, 238, 244, 255)),
    )

    # BG 6: Neighbor Woman in real Pastel Jacket + Beautiful You jeans + SSHF face
    bake_custom_atlas(
        "bg_woman_jacket",
        skin_dict("#F0C4A0"),
        face_key="face_sshf",
        shirt_key="shirt_pastel_jacket",
        pants_key="pants_beautiful_you",
    )

    print("[OK] Generated all R6 textures in", OUT_TEX)


if __name__ == "__main__":
    main()
