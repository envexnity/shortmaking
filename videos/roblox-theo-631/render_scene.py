"""
render_scene.py — Multi-Set Blender 5.3.0 EEVEE RT+GI Renderer for videos/roblox-theo-631
("Theo #631 — 1 in 250,000,000 Race").

Builds 3 isolated 3D sets in pure bmesh:
  - Set 1 (Origin 0,0,0): Starter House Exterior + Dark-Haired Dad & Mom + Shaking House & Window Dust Puffs
  - Set 2 (+120,0,0): Glowing Ribbed Biological Tunnel + 60 Animated White Tadpole Sperm Racers
    (Theo #631 in red headband, #42, #12, Rival #001, 56 swarm) + Giant Hazards + Glowing Golden Egg
  - Set 3 (-120,0,0): Hospital Delivery Room + Doctor + Mom + Blonde-Haired Baby Theo + Horrified Dark-Haired Dad

Usage:
    blender --background --python videos/roblox-theo-631/render_scene.py -- --preview
    blender --background --python videos/roblox-theo-631/render_scene.py
"""
import argparse
import importlib.util
import json
import math
import random
import re
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

SHORTMAKING_ROOT = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking")
PROJ_DIR = SHORTMAKING_ROOT / "videos" / "roblox-theo-631"
REF_DIR = SHORTMAKING_ROOT / "videos" / "roblox-reel-Df1kubCJ-o0-v2"
KIT_DIR = SHORTMAKING_ROOT / "90 Templates & Starter Kits" / "blender-cinema-kit"

sys.path.insert(0, str(KIT_DIR))
sys.path.insert(0, str(REF_DIR))
sys.path.insert(0, str(PROJ_DIR))

# Ensure char_factory & props_factory resolve OUR scene_common
_spec = importlib.util.spec_from_file_location("scene_common", str(PROJ_DIR / "scene_common.py"))
sc = importlib.util.module_from_spec(_spec)
sys.modules["scene_common"] = sc
_spec.loader.exec_module(sc)

import blender_cinema_lib as bcl  # noqa: E402
import char_factory as cf  # noqa: E402
import props_factory as pf  # noqa: E402

cf.TEX_CHARS = sc.TEX_CHARS


def smoothstep(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


def lerp(a: float, b: float, u: float) -> float:
    return a + (b - a) * u


def lerp3(a: tuple, b: tuple, u: float) -> tuple:
    return (lerp(a[0], b[0], u), lerp(a[1], b[1], u), lerp(a[2], b[2], u))


def add_sun_light(name: str, elevation_deg: float, azimuth_deg: float, energy: float, color_hex: str, col=None):
    ld = bpy.data.lights.new(name=f"{name}_Data", type="SUN")
    ld.energy = energy
    ld.color = bcl.hex_to_linear(color_hex)[:3]
    ld.angle = math.radians(2.5)
    lo = bpy.data.objects.new(name, ld)
    (col or bpy.context.scene.collection).objects.link(lo)
    lo.rotation_euler = (math.radians(90.0 - elevation_deg), 0.0, math.radians(azimuth_deg))
    return lo


def add_area_light(name: str, loc, target, energy: float, size: float, color_hex: str, col=None):
    ld = bpy.data.lights.new(name=f"{name}_Data", type="AREA")
    ld.shape = "RECTANGLE"
    ld.size = size
    ld.size_y = size * 0.75
    ld.energy = energy
    ld.color = bcl.hex_to_linear(color_hex)[:3]
    ld.spread = math.radians(85.0)
    lo = bpy.data.objects.new(name, ld)
    lo.location = loc
    (col or bpy.context.scene.collection).objects.link(lo)
    q = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y")
    lo.rotation_euler = q.to_euler()
    return lo


def find_word_time(words: list[dict], target: str, default_t: float, after: float = 0.0) -> float:
    tgt = target.lower()
    for w in words:
        clean = re.sub(r"[^a-z0-9]", "", w["word"].lower())
        if clean == tgt and w["start"] >= after:
            return float(w["start"])
    return default_t


def build_story_avatar(role: str, name: str, col):
    """Build Dad, Mom, or Doctor using exact Roblox Studio R15 proportions + custom outfits & hair."""
    char_col = bpy.data.collections.new(name)
    col.children.link(char_col)
    arm = cf._build_armature(name, char_col)

    cfg = {
        "dad":    ("#F2C6A0", "dad_serious_nod.png", "shirt_dad",    "pants_dad",    "#F8FAFC", False),
        "mom":    ("#F5CBA8", "mom_serious_nod.png", "shirt_mom",    "pants_mom",    "#F8FAFC", False),
        "doctor": ("#ECC29E", "doctor_proud.png",    "shirt_doctor", "pants_doctor", "#E2E8F0", False),
    }[role]
    skin_hex, face_png, shirt_stem, pants_stem, sole_hex, short_sl = cfg

    m_skin = sc.make_stylized_pbr(f"Mat_{name}_Skin", skin_hex, rough=0.42, coat=0.05, sss=0.10)
    head_obj, head_mat, face_tex_node = cf._make_head_with_face_uv(
        f"{name}_Head", skin_hex, sc.TEX_FACES / face_png, char_col, arm, "Head"
    )
    cf._prim("CYL", f"{name}_Neck", (0, 0, 1.332), (0.102, 0.102, 0.065), m_skin, char_col, arm, "Torso", segs=20)

    m_shirt = sc.make_textured_pbr(
        f"Mat_{name}_ShirtUV", sc.TEX_CHARS / f"{shirt_stem}.png", sc.TEX_CHARS / f"{shirt_stem}_bump.png",
        proj="UV", uv_scale=(1.0, 1.0, 1.0), rough_min=0.56, rough_max=0.74, coat=0.0, ao_str=0.16, bump_strength=0.10,
    )
    m_pants = sc.make_textured_pbr(
        f"Mat_{name}_PantsUV", sc.TEX_CHARS / f"{pants_stem}.png", sc.TEX_CHARS / f"{pants_stem}_bump.png",
        proj="UV", uv_scale=(1.0, 1.0, 1.0), rough_min=0.54, rough_max=0.74, coat=0.0, ao_str=0.16, bump_strength=0.10,
    )

    cf._make_uv_roblox_block(f"{name}_Torso", (0.59, 0.30, 0.62), (0.0, 0.0, 1.01), 0.020, 3, m_shirt, char_col, arm, "Torso")
    cf._add_r15_legs(name, char_col, arm, m_pants, sole_hex=sole_hex)
    cf._add_r15_arms(name, char_col, arm, m_skin, m_shirt, short_sleeve=short_sl)

    if role == "dad":
        # Unmistakable jet-dark espresso hair (NO hat so Dad's black hair is 100% clear in Hook & Hospital!)
        m_hair = sc.make_stylized_pbr(f"Mat_{name}_BlackHair", "#151211", rough=0.40, coat=0.08)
        cf._make_rounded_box(f"{name}_HairTop", (0.458, 0.400, 0.105), (0.0, -0.006, 1.732), 0.028, 3, m_hair, char_col, arm, "Head")
        cf._make_rounded_box(f"{name}_HairBack", (0.454, 0.062, 0.29), (0.0, -0.194, 1.595), 0.018, 3, m_hair, char_col, arm, "Head")
        for sx in (-0.222, 0.222):
            cf._make_rounded_box(f"{name}_HairSide_{sx}", (0.050, 0.27, 0.21), (sx, -0.045, 1.625), 0.015, 2, m_hair, char_col, arm, "Head")
        for bi, (fx, fw, fz, rz) in enumerate([(-0.145, 0.095, 1.70, 10), (-0.055, 0.105, 1.69, 5), (0.04, 0.105, 1.695, -5), (0.135, 0.095, 1.70, -11)]):
            cf._make_rounded_box(f"{name}_Bang_{bi}", (fw, 0.070, 0.095), (fx, 0.184, fz), 0.018, 2, m_hair, char_col, arm, "Head", rot=(math.radians(8), math.radians(rz), 0))

    elif role == "mom":
        # Long dark espresso-black hair matching Dad's dark hair!
        m_hair = sc.make_stylized_pbr(f"Mat_{name}_BlackHair", "#151211", rough=0.38, coat=0.10)
        cf._make_rounded_box(f"{name}_HairTop", (0.462, 0.408, 0.105), (0.0, -0.008, 1.735), 0.030, 3, m_hair, char_col, arm, "Head")
        cf._make_rounded_box(f"{name}_HairBackLong", (0.468, 0.088, 0.56), (0.0, -0.205, 1.46), 0.026, 3, m_hair, char_col, arm, "Head")
        for sx in (-0.232, 0.232):
            cf._make_rounded_box(f"{name}_HairSideLong_{sx}", (0.068, 0.18, 0.46), (sx, -0.08, 1.50), 0.020, 2, m_hair, char_col, arm, "Head")
        for bx, rz in [(-0.12, 16), (0.12, -16)]:
            cf._make_rounded_box(f"{name}_MomBang_{bx}", (0.16, 0.055, 0.072), (bx, 0.185, 1.695), 0.016, 2, m_hair, char_col, arm, "Head", rot=(0, math.radians(rz), 0))

    elif role == "doctor":
        m_gray = sc.make_stylized_pbr(f"Mat_{name}_DocHair", "#CBD5E1", rough=0.45, coat=0.04)
        m_spec = sc.make_stylized_pbr(f"Mat_{name}_DocSpecs", "#1E293B", rough=0.22, metal=0.85)
        cf._make_rounded_box(f"{name}_DocHairTop", (0.452, 0.395, 0.085), (0.0, -0.008, 1.732), 0.024, 3, m_gray, char_col, arm, "Head")
        cf._make_rounded_box(f"{name}_DocHairBack", (0.450, 0.058, 0.24), (0.0, -0.194, 1.60), 0.016, 2, m_gray, char_col, arm, "Head")
        for sx in (-0.222, 0.222):
            cf._make_rounded_box(f"{name}_DocHairSide_{sx}", (0.048, 0.25, 0.18), (sx, -0.04, 1.62), 0.014, 2, m_gray, char_col, arm, "Head")
        for gx in (-0.078, 0.078):
            cf._prim("TORUS", f"{name}_DocSpec_{gx}", (gx, 0.194, 1.545), (0.058, 0.058, 0.016), m_spec, char_col, arm, "Head", rot=(math.radians(90), 0, 0), segs=20)
        cf._make_rounded_box(f"{name}_DocSpecBridge", (0.04, 0.014, 0.014), (0, 0.194, 1.545), 0.004, 2, m_spec, char_col, arm, "Head")

    return {
        "name": name, "kind": role, "col": char_col, "arm": arm,
        "head_obj": head_obj, "head_mat": head_mat, "face_tex_node": face_tex_node, "_last_face": None,
    }


def build_baby_theo(name: str, col):
    """Build swaddled Roblox Baby Theo with a BIG, unmistakable golden-yellow BLONDE hair tuft!"""
    root = bpy.data.objects.new(name, None)
    col.objects.link(root)

    m_blanket = sc.make_stylized_pbr(f"Mat_{name}_Blanket", "#60A5FA", rough=0.62, sheen=0.45)
    m_trim = sc.make_stylized_pbr(f"Mat_{name}_Trim", "#DBEAFE", rough=0.58, sheen=0.35)
    m_skin = sc.make_stylized_pbr(f"Mat_{name}_Skin", "#F6D0B1", rough=0.40, coat=0.05, sss=0.14)
    m_blonde = sc.make_stylized_pbr(f"Mat_{name}_BlondeHair", "#FFE01B", rough=0.34, coat=0.18, emit_hex="#FACC15", emit_str=0.22)

    # Swaddled body bundle (along Y)
    pf.make_smooth_cyl(f"{name}_Body", (0, -0.10, 0.0), 0.145, 0.34, m_blanket, col, segs=24, rot=(math.radians(90), 0, 0), bevel_w=0.025, parent=root, r2=0.11)
    pf.make_smooth_torus(f"{name}_Collar", (0, 0.06, 0.0), 0.145, 0.030, m_trim, col, major_segs=24, minor_segs=10, rot=(math.radians(90), 0, 0), parent=root)

    # Round baby head + face plane
    pf.make_smooth_sphere(f"{name}_Head", (0, 0.16, 0.03), (0.145, 0.135, 0.135), m_skin, col, segs=24, parent=root)
    m_face = sc.make_textured_pbr(
        f"Mat_{name}_Face", sc.TEX_FACES / "baby_happy.png", proj="UV",
        rough_min=0.45, rough_max=0.55, ao_str=0.0, alpha_clip=True,
    )
    bm = bmesh.new()
    v0 = bm.verts.new((-0.11, 0, -0.10))
    v1 = bm.verts.new((0.11, 0, -0.10))
    v2 = bm.verts.new((0.11, 0, 0.10))
    v3 = bm.verts.new((-0.11, 0, 0.10))
    f = bm.faces.new((v0, v1, v2, v3))
    uv = bm.loops.layers.uv.new("UVMap")
    for lp, c in zip(f.loops, [(1.0, 0.0), (0.0, 0.0), (0.0, 1.0), (1.0, 1.0)]):
        lp[uv].uv = c
    pf._finish_bm(bm, f"{name}_FaceDecal", (0, 0.296, 0.025), m_face, col, parent=root, smooth=False)

    # HUGE UNMISTAKABLE GOLDEN BLONDE HAIR TUFT!
    curls = [
        (0.0, 0.18, 0.175, (0.085, 0.075, 0.068)),
        (-0.075, 0.17, 0.155, (0.062, 0.060, 0.056)),
        (0.075, 0.17, 0.155, (0.062, 0.060, 0.056)),
        (-0.035, 0.22, 0.152, (0.052, 0.055, 0.052)),
        (0.042, 0.21, 0.160, (0.056, 0.056, 0.052)),
    ]
    for i, (cx, cy, cz, sc_c) in enumerate(curls):
        pf.make_smooth_sphere(f"{name}_BlondeCurl_{i}", (cx, cy, cz), sc_c, m_blonde, col, segs=16, parent=root)
    # Tall blonde cowlick swoop right on top!
    bm_sw = bmesh.new()
    bmesh.ops.create_cone(bm_sw, cap_ends=True, cap_tris=False, segments=16, radius1=0.052, radius2=0.008, depth=0.145)
    pf._finish_bm(bm_sw, f"{name}_BlondeCowlick", (0.01, 0.19, 0.235), m_blonde, col, rot=(math.radians(28), math.radians(-18), 0), parent=root)
    return root


# ==================== SET 1: STARTER HOUSE EXTERIOR ====================

def build_starter_house_set(scene):
    col = bpy.data.collections.new("Set_StarterHouse")
    scene.collection.children.link(col)

    m_grass = sc.make_stylized_pbr("Mat_S1_Grass", "#44C458", rough=0.78, coat=0.0, sss=0.06, bump_str=0.04)
    m_pave = sc.make_textured_pbr("Mat_S1_Pave", sc.TEX_ENV / "sidewalk_pavers.png", sc.TEX_ENV / "sidewalk_pavers_bump.png", uv_scale=(0.85, 0.85, 0.85), rough_min=0.68, rough_max=0.86)
    m_asph = sc.make_textured_pbr("Mat_S1_Asph", sc.TEX_ENV / "asphalt_speckled.png", sc.TEX_ENV / "asphalt_speckled_bump.png", uv_scale=(0.8, 0.8, 0.8), rough_min=0.74, rough_max=0.90)
    m_fence = sc.make_stylized_pbr("Mat_S1_Fence", "#F8FAFC", rough=0.48, coat=0.04)
    m_wall = sc.make_stylized_pbr("Mat_S1_HouseWall", "#FEF3C7", rough=0.64, coat=0.0, bump_str=0.04)
    m_roof = sc.make_stylized_pbr("Mat_S1_HouseRoof", "#DC2626", rough=0.52, coat=0.04, bump_str=0.04)
    m_trim = sc.make_stylized_pbr("Mat_S1_Trim", "#F8FAFC", rough=0.46)
    m_door = sc.make_stylized_pbr("Mat_S1_Door", "#7C4A22", rough=0.45, coat=0.06)
    m_knob = sc.make_stylized_pbr("Mat_S1_Knob", "#FACC15", rough=0.22, metal=0.9)
    m_win = sc.make_stylized_pbr("Mat_S1_WinLit", "#BAE6FD", rough=0.16, coat=0.35, emit_hex="#FEF08A", emit_str=0.85)
    m_dark_in = sc.make_stylized_pbr("Mat_S1_Inside", "#1E1B18", rough=0.90, coat=0.0)
    m_dust = sc.make_stylized_pbr("Mat_S1_Dust", "#E8D3B9", rough=0.92, coat=0.0, sss=0.08, ao_str=0.25)

    # Ground & street
    pf.make_bevel_box("S1_Lawn", (0, -8.0, -0.15), (42.0, 26.0, 0.30), m_grass, col, bevel_w=0.02)
    pf.make_bevel_box("S1_Walkway", (0, -0.5, -0.02), (1.7, 7.6, 0.08), m_pave, col, bevel_w=0.015)
    pf.make_bevel_box("S1_Sidewalk", (0, 3.6, -0.03), (38.0, 2.2, 0.12), m_pave, col, bevel_w=0.015)
    pf.make_bevel_box("S1_Road", (0, 7.5, -0.10), (42.0, 5.8, 0.22), m_asph, col, bevel_w=0.02)

    # White picket fence along lawn sides
    for side_x in (-5.2, 5.2):
        for z_rail in (0.35, 0.78):
            pf.make_bevel_box(f"S1_Rail_{side_x}_{z_rail}", (side_x, -2.5, z_rail), (0.08, 6.2, 0.08), m_fence, col, bevel_w=0.01)
        for pi in range(11):
            py = -5.4 + pi * 0.58
            pf.make_bevel_box(f"S1_Picket_{side_x}_{pi}", (side_x, py, 0.52), (0.14, 0.12, 1.04), m_fence, col, bevel_w=0.015)

    # Background trees & neighbor houses
    for i, (tx, ty, ts) in enumerate([(-6.4, -4.8, 1.15), (6.5, -4.6, 1.20), (-9.2, -10.5, 1.35), (8.8, -11.0, 1.30)]):
        pf.build_bumpy_tree(f"S1_Tree_{i}", (tx, ty, 0.0), col, scale=ts)
    pf.build_townhouse("S1_NeighborL", (-9.4, -7.8, 0.0), col, 4.2, 3.8, 4.4, "#93C5FD", "#1D4ED8", is_night=False)
    pf.build_townhouse("S1_NeighborR", (9.4, -7.8, 0.0), col, 4.2, 3.8, 4.6, "#A7F3D0", "#047857", is_night=False)

    # Clouds in sunny sky
    m_cloud = sc.make_stylized_pbr("Mat_S1_Cloud", "#F8FAFC", rough=0.72, coat=0.0, sss=0.10)
    for ci, (cx, cy, cz) in enumerate([(-5.5, -18, 9.2), (1.2, -20, 10.6), (6.8, -17, 8.8)]):
        for ox, oy, oz, sc_c in [(0, 0, 0, (1.8, 0.8, 0.8)), (-1.0, 0.1, -0.1, (1.2, 0.7, 0.65)), (1.0, -0.1, -0.1, (1.3, 0.7, 0.7))]:
            pf.make_smooth_sphere(f"S1_Cloud_{ci}_{ox}", (cx + ox, cy + oy, cz + oz), sc_c, m_cloud, col, segs=14)

    # HERO STARTER HOUSE (parented to HouseShakeRoot at (0, -6.2, 0))
    house_root = bpy.data.objects.new("HouseShakeRoot", None)
    house_root.location = (0.0, -6.2, 0.0)
    col.objects.link(house_root)

    # House exterior walls built around doorway opening (doorway x in [-0.55..+0.55], z in [0..2.15])
    pf.make_bevel_box("S1_HPorch", (0, 2.35, 0.12), (2.4, 1.1, 0.24), m_trim, col, bevel_w=0.02, parent=house_root)
    pf.make_bevel_box("S1_HBackWall", (0, -1.75, 1.85), (5.0, 0.35, 3.7), m_wall, col, bevel_w=0.03, parent=house_root)
    pf.make_bevel_box("S1_HSideL", (-2.35, 0.0, 1.85), (0.35, 3.8, 3.7), m_wall, col, bevel_w=0.03, parent=house_root)
    pf.make_bevel_box("S1_HSideR", (2.35, 0.0, 1.85), (0.35, 3.8, 3.7), m_wall, col, bevel_w=0.03, parent=house_root)
    pf.make_bevel_box("S1_HFrontL", (-1.52, 1.75, 1.85), (1.96, 0.35, 3.7), m_wall, col, bevel_w=0.03, parent=house_root)
    pf.make_bevel_box("S1_HFrontR", (1.52, 1.75, 1.85), (1.96, 0.35, 3.7), m_wall, col, bevel_w=0.03, parent=house_root)
    pf.make_bevel_box("S1_HFrontTop", (0.0, 1.75, 2.95), (1.16, 0.35, 1.50), m_wall, col, bevel_w=0.03, parent=house_root)
    pf.make_bevel_box("S1_HDarkInside", (0.0, 0.2, 1.65), (4.2, 3.2, 3.3), m_dark_in, col, bevel_w=0.0, parent=house_root)

    # Pitched roof + chimney
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=4, radius1=4.05, radius2=0.10, depth=2.1)
    for v in bm.verts:
        v.co.y *= 0.84
    pf._finish_bm(bm, "S1_HRoof", (0, 0, 4.72), m_roof, col, rot=(0, 0, math.radians(45)), parent=house_root, bevel_w=0.03, bevel_segs=2)
    pf.make_bevel_box("S1_HChimney", (1.4, -0.7, 5.15), (0.62, 0.62, 1.35), m_roof, col, bevel_w=0.025, parent=house_root)

    # Door frame + hinged front door
    pf.make_bevel_box("S1_DoorFrameT", (0.0, 1.88, 2.24), (1.26, 0.16, 0.14), m_trim, col, bevel_w=0.015, parent=house_root)
    for dx in (-0.60, 0.60):
        pf.make_bevel_box(f"S1_DoorFrameS_{dx}", (dx, 1.88, 1.15), (0.14, 0.16, 2.24), m_trim, col, bevel_w=0.015, parent=house_root)
    door_hinge = bpy.data.objects.new("DoorHinge", None)
    door_hinge.location = (-0.52, 1.84, 0.0)
    col.objects.link(door_hinge)
    door_hinge.parent = house_root
    pf.make_bevel_box("S1_DoorLeaf", (0.52, 0.0, 1.12), (1.04, 0.11, 2.16), m_door, col, bevel_w=0.015, parent=door_hinge)
    pf.make_smooth_sphere("S1_DoorKnob", (0.92, 0.08, 1.06), (0.055, 0.055, 0.055), m_knob, col, segs=14, parent=door_hinge)

    # Windows on left & right of front door (and side windows for wide shot readability)
    for wx in (-1.52, 1.52):
        pf.make_bevel_box(f"S1_WinFrame_{wx}", (wx, 1.92, 1.65), (1.08, 0.14, 1.08), m_trim, col, bevel_w=0.015, parent=house_root)
        pf.make_bevel_box(f"S1_WinPane_{wx}", (wx, 1.94, 1.65), (0.86, 0.12, 0.86), m_win, col, bevel_w=0.008, parent=house_root)
        pf.make_bevel_box(f"S1_WinCrossH_{wx}", (wx, 1.99, 1.65), (0.90, 0.04, 0.06), m_trim, col, bevel_w=0.005, parent=house_root)
        pf.make_bevel_box(f"S1_WinCrossV_{wx}", (wx, 1.99, 1.65), (0.06, 0.04, 0.90), m_trim, col, bevel_w=0.005, parent=house_root)

    # Dust puffs hidden until Beat 2; placed at left/right windows & chimney (none blocking door)
    dust_puffs = []
    dust_anchors = [
        (-1.60, 2.25, 1.65, -1, 0.48), (-1.78, 2.30, 1.82, -1, 0.40), (-1.45, 2.22, 1.50, -1, 0.44), (-1.90, 2.25, 2.02, -1, 0.36),
        (1.60, 2.25, 1.65, 1, 0.48), (1.78, 2.30, 1.82, 1, 0.40), (1.45, 2.22, 1.50, 1, 0.44), (1.90, 2.25, 2.02, 1, 0.36),
        (1.40, -0.70, 5.95, 0, 0.44), (1.32, -0.65, 6.22, 0, 0.38), (1.48, -0.75, 6.40, 0, 0.34), (-1.52, 2.20, 2.10, -1, 0.36),
    ]
    for di, (ax, ay, az, sx_dir, base_r) in enumerate(dust_anchors):
        p = pf.make_smooth_sphere(f"S1_Dust_{di}", (ax, ay, az), (base_r, base_r, base_r), m_dust, col, segs=14, parent=house_root)
        p.scale = (0.001, 0.001, 0.001)
        dust_puffs.append((p, (ax, ay, az), sx_dir, di))

    return {"col": col, "house_root": house_root, "door_hinge": door_hinge, "dust_puffs": dust_puffs}


# ==================== SET 2: GLOWING TUNNEL & ALL-SPERM RACERS ====================

def build_sperm_racer(
    name: str,
    col,
    head_hex: str = "#F8FAFC",
    band_hex: str | None = None,
    has_face: bool = True,
    angry_brows: bool = False,
    n_tail_segs: int = 6,
    scale: float = 1.0,
):
    """
    Explicit 3D Tadpole Sperm Racer in pure bmesh:
      - Streamlined white/pearlescent ovoid head (snout pointing +Y)
      - Neck midpiece
      - Multi-segment articulated whipping tail extending along -Y
      - Optional expressive 3D eyes/brows + colored athletic headband + trailing ribbons
    """
    root = bpy.data.objects.new(name, None)
    root.scale = (scale, scale, scale)
    col.objects.link(root)

    m_head = sc.make_stylized_pbr(
        f"Mat_{name}_SpermBody", head_hex, rough=0.20, coat=0.45, sss=0.20,
        emit_hex="#F1F5F9" if head_hex == "#F8FAFC" else head_hex,
        emit_str=0.24 if head_hex in ("#FFFFFF", "#F8FAFC") else 0.06,
    )
    m_eye = sc.make_stylized_pbr("Mat_Sperm_EyeInk", "#0F172A", rough=0.18, coat=0.55)
    m_glint = sc.make_stylized_pbr("Mat_Sperm_Glint", "#FFFFFF", emit_hex="#FFFFFF", emit_str=2.2)

    # Streamlined ovoid sperm head (slightly pointed forward snout at +Y)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=22, v_segments=14, radius=1.0)
    for v in bm.verts:
        y_n = v.co.y
        taper = 1.0 - 0.28 * max(0.0, y_n)
        v.co.x *= 0.22 * taper
        v.co.y *= 0.36
        v.co.z *= 0.20 * taper
    head_mesh = pf._finish_bm(bm, f"{name}_Head", (0, 0.05, 0), m_head, col, parent=root)

    # Midpiece collar
    pf.make_smooth_cyl(f"{name}_Collar", (0, -0.32, 0), 0.088, 0.14, m_head, col, segs=16, rot=(math.radians(90), 0, 0), bevel_w=0.01, parent=root, r2=0.108)

    # Articulated multi-segment flagellum tail along -Y
    segs = []
    parent_obj = root
    seg_len = 0.22
    for si in range(n_tail_segs):
        piv = bpy.data.objects.new(f"{name}_TailPiv_{si}", None)
        piv.location = (0.0, -0.38 if si == 0 else -seg_len * 0.90, 0.0)
        col.objects.link(piv)
        piv.parent = parent_obj
        r1 = max(0.016, 0.072 * (1.0 - (si + 1) / (n_tail_segs + 1.2)))
        r2 = max(0.022, 0.072 * (1.0 - si / (n_tail_segs + 1.2)))
        pf.make_smooth_cyl(
            f"{name}_TailSeg_{si}", (0.0, -seg_len * 0.5, 0.0), r1, seg_len, m_head, col,
            segs=10, rot=(math.radians(90), 0, 0), bevel_w=0.0, parent=piv, r2=r2,
        )
        segs.append(piv)
        parent_obj = piv

    # 3D Glossy Eyes & Brows on upper-front of head (visible from front, 3/4, and side chase!)
    brows = []
    if has_face:
        for sx in (-0.092, 0.092):
            pf.make_smooth_sphere(f"{name}_Eye_{sx}", (sx, 0.245, 0.105), (0.044, 0.030, 0.058), m_eye, col, segs=14, rot=(math.radians(-22), 0, math.radians(18 if sx < 0 else -18)), parent=root)
            pf.make_smooth_sphere(f"{name}_Glint_{sx}", (sx - 0.012, 0.270, 0.128), (0.014, 0.010, 0.016), m_glint, col, segs=8, parent=root)
            if angry_brows:
                b = pf.make_bevel_box(
                    f"{name}_Brow_{sx}", (sx, 0.235, 0.165), (0.090, 0.026, 0.024),
                    m_eye, col, bevel_w=0.006, segs=2,
                    rot=(0, math.radians(22 if sx > 0 else -22), math.radians(-12 if sx > 0 else 12)),
                    parent=root,
                )
                brows.append(b)

    # Athletic Headband + Fluttering Ribbons (elliptical fit cleanly OUTSIDE 0.22 x 0.36 x 0.20 head!)
    ribbons = []
    if band_hex:
        m_band = sc.make_stylized_pbr(f"Mat_{name}_Band_{band_hex}", band_hex, rough=0.34, coat=0.14, emit_hex=band_hex, emit_str=0.32)
        bm_hb = bmesh.new()
        pf.make_torus_bm(bm_hb, 1.0, 0.14, major_segs=32, minor_segs=10)
        for v in bm_hb.verts:
            v.co.x *= 0.232
            v.co.y *= 0.345
            v.co.z *= 0.232
        pf._finish_bm(bm_hb, f"{name}_Headband", (0.0, 0.04, 0.045), m_band, col, rot=(math.radians(-16), 0, 0), parent=root)
        for ri, rz in enumerate((-12, 16)):
            rpiv = bpy.data.objects.new(f"{name}_RibbonPiv_{ri}", None)
            rpiv.location = (-0.21, -0.18, 0.08 + ri * 0.03)
            col.objects.link(rpiv)
            rpiv.parent = root
            pf.make_bevel_box(
                f"{name}_Ribbon_{ri}", (-0.02, -0.17, 0.0), (0.056, 0.34, 0.014),
                m_band, col, bevel_w=0.004, segs=2, rot=(0, 0, math.radians(rz)), parent=rpiv,
            )
            ribbons.append(rpiv)

    return {"root": root, "head": head_mesh, "tail_segs": segs, "brows": brows, "ribbons": ribbons, "mat_head": m_head}


def animate_sperm_tail(sp: dict, t: float, freq: float = 22.0, amp_deg: float = 24.0, phase: float = 0.0):
    for si, piv in enumerate(sp["tail_segs"]):
        ang = amp_deg * (0.70 + 0.14 * si) * math.sin(freq * t - si * 0.85 + phase)
        piv.rotation_euler = (math.radians(ang * 0.18), 0.0, math.radians(ang))
    for ri, rpiv in enumerate(sp["ribbons"]):
        rang = 16.0 * math.sin(18.0 * t - ri * 1.1 + phase)
        rpiv.rotation_euler = (math.radians(rang * 0.4), 0.0, math.radians(rang))


def build_tunnel_race_set(scene):
    col = bpy.data.collections.new("Set_TunnelRace")
    scene.collection.children.link(col)
    OX, OZ = 120.0, 3.5

    m_tunnel = sc.make_stylized_pbr("Mat_S2_Tunnel", "#881337", rough=0.32, coat=0.28, sss=0.25, bump_str=0.05, ao_str=0.16, emit_hex="#9D174D", emit_str=0.16)
    m_rib = sc.make_stylized_pbr("Mat_S2_Rib", "#BE185D", rough=0.30, coat=0.35, emit_hex="#F43F5E", emit_str=0.45)
    m_glow_strip = sc.make_stylized_pbr("Mat_S2_GlowStrip", "#FDA4AF", emit_hex="#FB7185", emit_str=3.2)
    m_mote = sc.make_stylized_pbr("Mat_S2_Mote", "#FDE68A", emit_hex="#F9A8D4", emit_str=4.5)

    # Outer ribbed organic cylinder tunnel along +Y (y = -28 .. +112, closed ends with glowing mist!)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=32, radius1=4.5, radius2=4.5, depth=140.0)
    for f in bm.faces:
        f.normal_flip()
    pf._finish_bm(bm, "S2_TunnelWall", (OX, 42.0, OZ), m_tunnel, col, rot=(math.radians(90), 0, 0))

    # Glowing organic tunnel ribs & longitudinal bioluminescent guide rails
    for yi in range(-24, 108, 3):
        pf.make_smooth_torus(f"S2_Rib_{yi}", (OX, float(yi), OZ), 4.35, 0.14, m_rib, col, major_segs=32, minor_segs=8, rot=(math.radians(90), 0, 0))
    for ang_deg in (40, 140, 220, 320):
        ang = math.radians(ang_deg)
        sx = OX + math.cos(ang) * 4.28
        sz = OZ + math.sin(ang) * 4.28
        pf.make_bevel_box(f"S2_Strip_{ang_deg}", (sx, 42.0, sz), (0.10, 134.0, 0.10), m_glow_strip, col, bevel_w=0.02)

    # Floating bioluminescent particles inside tunnel
    rng = random.Random(631)
    for mi in range(52):
        ang = rng.uniform(0, math.pi * 2)
        rad = rng.uniform(1.8, 3.9)
        my = rng.uniform(-16.0, 88.0)
        pf.make_smooth_sphere(f"S2_Mote_{mi}", (OX + math.cos(ang) * rad, my, OZ + math.sin(ang) * rad), (0.06, 0.06, 0.06), m_mote, col, segs=8)

    # Starting Gate at Y = 4.9 (well clear of Shot 4a hero orbit!)
    m_gate = sc.make_stylized_pbr("Mat_S2_GateFrame", "#1E293B", rough=0.28, metal=0.80)
    m_bar_red = sc.make_stylized_pbr("Mat_S2_GateBar", "#EF4444", emit_hex="#EF4444", emit_str=6.5)
    m_bar_grn = sc.make_stylized_pbr("Mat_S2_GateBarGrn", "#22C55E", emit_hex="#22C55E", emit_str=7.5)
    pf.make_smooth_torus("S2_StartArch", (OX, 4.9, OZ), 4.15, 0.24, m_gate, col, major_segs=32, minor_segs=10, rot=(math.radians(90), 0, 0))
    gate_bars = []
    for gz in (OZ - 1.5, OZ, OZ + 1.5):
        gb = pf.make_smooth_cyl(f"S2_GateBar_{gz:.1f}", (OX, 4.9, gz), 0.065, 7.6, m_bar_red, col, segs=14, rot=(0, math.radians(90), 0))
        gate_bars.append(gb)

    # Giant Biological Hazards (Y = 18 .. 56)
    m_acid = sc.make_stylized_pbr("Mat_S2_Acid", "#22C55E", rough=0.14, coat=0.55, emit_hex="#4ADE80", emit_str=2.6, alpha=0.85)
    m_immune = sc.make_stylized_pbr("Mat_S2_Immune", "#DB2777", rough=0.28, coat=0.35, emit_hex="#EC4899", emit_str=1.8)
    m_spike = sc.make_stylized_pbr("Mat_S2_Spike", "#FDE047", rough=0.24, emit_hex="#FACC15", emit_str=2.8)

    hazards = []
    hazard_specs = [
        ("acid",   OX - 1.15, 22.0, OZ + 0.35, 0.88),
        ("acid",   OX + 1.25, 28.5, OZ - 0.35, 0.95),
        ("immune", OX - 1.05, 34.0, OZ + 0.25, 0.85),
        ("acid",   OX + 0.95, 40.5, OZ + 0.45, 0.92),
        ("immune", OX - 0.90, 47.0, OZ - 0.20, 0.96),
        ("acid",   OX + 1.10, 54.0, OZ + 0.15, 0.88),
    ]
    for hi, (hk, hx, hy, hz, hrad) in enumerate(hazard_specs):
        hroot = bpy.data.objects.new(f"S2_Hazard_{hi}", None)
        hroot.location = (hx, hy, hz)
        col.objects.link(hroot)
        if hk == "acid":
            pf.make_smooth_sphere(f"S2_AcidCore_{hi}", (0, 0, 0), (hrad, hrad * 1.12, hrad), m_acid, col, segs=22, parent=hroot)
            pf.make_smooth_sphere(f"S2_AcidOrb_{hi}", (hrad * 0.45, -hrad * 0.35, hrad * 0.45), (hrad * 0.28, hrad * 0.28, hrad * 0.28), m_spike, col, segs=12, parent=hroot)
        else:
            pf.make_smooth_sphere(f"S2_ImmCore_{hi}", (0, 0, 0), (hrad * 0.78, hrad * 0.78, hrad * 0.78), m_immune, col, segs=20, parent=hroot)
            for sdir in [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1), (0.7, 0.7, 0), (-0.7, -0.7, 0)]:
                v = Vector(sdir).normalized()
                q = v.to_track_quat("Z", "Y")
                pf.make_smooth_cyl(
                    f"S2_ImmSpk_{hi}_{sdir}", tuple(v * (hrad * 0.95)), 0.14, hrad * 0.55,
                    m_spike, col, segs=10, rot=q.to_euler(), parent=hroot, r2=0.02,
                )
        hazards.append((hroot, hx, hy, hz, hi))

    # GLOWING GOLDEN EGG AT FINISH LINE (Y = 82.0)
    m_egg_core = sc.make_stylized_pbr("Mat_S2_EggCore", "#FBBF24", rough=0.14, coat=0.60, emit_hex="#FDE047", emit_str=4.5)
    m_egg_halo = sc.make_stylized_pbr("Mat_S2_EggHalo", "#FEF08A", rough=0.20, emit_hex="#FEF08A", emit_str=2.2, alpha=0.35)
    egg_root = bpy.data.objects.new("S2_GoldenEgg", None)
    egg_root.location = (OX, 82.0, OZ)
    col.objects.link(egg_root)
    pf.make_smooth_sphere("S2_EggSphere", (0, 0, 0), (2.20, 2.20, 2.20), m_egg_core, col, segs=36, parent=egg_root)
    pf.make_smooth_sphere("S2_EggCorona", (0, 0, 0), (2.52, 2.52, 2.52), m_egg_halo, col, segs=32, parent=egg_root)
    for ei in range(12):
        ang = ei * math.pi * 2.0 / 12.0
        pf.make_smooth_sphere(f"S2_EggMote_{ei}", (math.cos(ang) * 2.90, -0.5, math.sin(ang) * 2.90), (0.14, 0.14, 0.14), m_spike, col, segs=10, parent=egg_root)

    # HERO THEO (#631), NAMED RIVALS (#42, #12, #001), AND 56 WHITE TADPOLE SWARM SPERM!
    theo = build_sperm_racer("Sperm_Theo_631", col, head_hex="#FFFFFF", band_hex="#EF4444", has_face=True, angry_brows=True, n_tail_segs=6, scale=1.18)
    s42 = build_sperm_racer("Sperm_42", col, head_hex="#F8FAFC", band_hex="#06B6D4", has_face=True, angry_brows=False, n_tail_segs=5, scale=1.08)
    s12 = build_sperm_racer("Sperm_12", col, head_hex="#F8FAFC", band_hex="#F97316", has_face=True, angry_brows=False, n_tail_segs=5, scale=1.08)
    s001 = build_sperm_racer("Sperm_001", col, head_hex="#FFFFFF", band_hex="#A855F7", has_face=True, angry_brows=True, n_tail_segs=6, scale=1.15)
    for init_sp, ix in ((theo, OX), (s42, OX - 1.35), (s12, OX + 1.35), (s001, OX + 0.85)):
        init_sp["root"].location = (ix, 2.5, OZ)

    swarm = []
    for ci in range(56):
        ang = rng.uniform(0, math.pi * 2)
        rad = rng.uniform(0.55, 3.35)
        sx = OX + math.cos(ang) * rad
        sz = OZ + math.sin(ang) * rad
        sy = rng.uniform(-1.5, 2.9)
        if abs(sx - OX) < 0.75 and abs(sz - OZ) < 0.65 and sy > 1.4:
            sx += 1.15 if sx >= OX else -1.15
        sp = build_sperm_racer(
            f"Swarm_{ci:02d}", col, head_hex="#F8FAFC", band_hex=None,
            has_face=(ci < 14), angry_brows=False, n_tail_segs=4, scale=rng.uniform(0.88, 1.08),
        )
        sp["root"].location = (sx, sy, sz)
        swarm.append({
            "sp": sp, "x0": sx, "y0": sy, "z0": sz,
            "speed": rng.uniform(8.8, 13.8), "phase": rng.uniform(0, math.pi * 2),
            "drop_t": rng.uniform(16.9, 23.2),
        })

    # Bright Tunnel Lighting (cover -14..+90 so reverse shots are never dark!)
    for li, ly in enumerate(range(-14, 92, 8)):
        lt = bpy.data.objects.new(f"S2_Light_{li}", bpy.data.lights.new(f"S2_Pt_{li}", type="POINT"))
        lt.location = (OX + (1.2 if li % 2 == 0 else -1.2), float(ly), OZ + 2.4)
        lt.data.energy = 320.0 if ly < 70 else 650.0
        lt.data.color = bcl.hex_to_linear("#FFE4E6" if ly < 70 else "#FEF08A")[:3]
        lt.data.shadow_soft_size = 1.2
        col.objects.link(lt)

    return {
        "col": col, "OX": OX, "OZ": OZ, "gate_bars": gate_bars, "m_bar_grn": m_bar_grn,
        "hazards": hazards, "egg_root": egg_root,
        "theo": theo, "s42": s42, "s12": s12, "s001": s001, "swarm": swarm,
    }


# ==================== SET 3: HOSPITAL DELIVERY ROOM ====================

def build_hospital_set(scene):
    col = bpy.data.collections.new("Set_Hospital")
    scene.collection.children.link(col)
    OX = -120.0

    m_floor = sc.make_textured_pbr("Mat_S3_Tile", sc.TEX_ENV / "tile_cream_diner.png", sc.TEX_ENV / "tile_cream_diner_bump.png", uv_scale=(1.2, 1.2, 1.2), rough_min=0.25, rough_max=0.40)
    m_wall = sc.make_stylized_pbr("Mat_S3_Wall", "#E0F2FE", rough=0.65, coat=0.04)
    m_wain = sc.make_stylized_pbr("Mat_S3_Wain", "#38BDF8", rough=0.50, coat=0.06)
    m_sheet = sc.make_stylized_pbr("Mat_S3_Sheet", "#F8FAFC", rough=0.72, sheen=0.35)
    m_blank = sc.make_stylized_pbr("Mat_S3_Blanket", "#0EA5E9", rough=0.70, sheen=0.45)
    m_steel = sc.make_stylized_pbr("Mat_S3_Steel", "#94A3B8", rough=0.25, metal=0.85)
    m_mon_bg = sc.make_stylized_pbr("Mat_S3_MonBg", "#0F172A", rough=0.22)
    m_mon_ln = sc.make_stylized_pbr("Mat_S3_MonLine", "#22C55E", emit_hex="#22C55E", emit_str=4.0)
    m_board = sc.make_stylized_pbr("Mat_S3_ClipBoard", "#78350F", rough=0.46)
    m_paper = sc.make_textured_pbr("Mat_S3_ClipPaper", sc.TEX_PROPS / "clipboard_dna.png", proj="UV", rough_min=0.45, rough_max=0.58, ao_str=0.02, emit_str=0.25)

    # Room shell
    pf.make_bevel_box("S3_Floor", (OX, 0.0, -0.10), (7.2, 7.2, 0.20), m_floor, col, bevel_w=0.01)
    pf.make_bevel_box("S3_BackWall", (OX, -2.8, 1.9), (7.2, 0.25, 3.8), m_wall, col, bevel_w=0.01)
    pf.make_bevel_box("S3_BackWain", (OX, -2.66, 0.52), (7.2, 0.06, 1.04), m_wain, col, bevel_w=0.01)
    pf.make_bevel_box("S3_SideWallL", (OX - 3.4, 0.0, 1.9), (0.25, 7.2, 3.8), m_wall, col, bevel_w=0.01)
    pf.make_bevel_box("S3_SideWallR", (OX + 3.4, 0.0, 1.9), (0.25, 7.2, 3.8), m_wall, col, bevel_w=0.01)

    # Hospital bed on left-back (Mom resting)
    bed_x, bed_y = OX - 1.35, -1.35
    pf.make_bevel_box("S3_BedFrame", (bed_x, bed_y, 0.36), (1.35, 2.05, 0.20), m_steel, col, bevel_w=0.02)
    pf.make_bevel_box("S3_Headboard", (bed_x, bed_y - 1.00, 0.78), (1.38, 0.12, 0.90), m_steel, col, bevel_w=0.02)
    pf.make_bevel_box("S3_Mattress", (bed_x, bed_y, 0.56), (1.28, 1.95, 0.26), m_sheet, col, bevel_w=0.04)
    pf.make_bevel_box("S3_Blanket", (bed_x, bed_y + 0.26, 0.62), (1.30, 1.35, 0.28), m_blank, col, bevel_w=0.05)
    pf.make_bevel_box("S3_Pillow", (bed_x, bed_y - 0.68, 0.75), (0.86, 0.42, 0.16), m_sheet, col, bevel_w=0.05)

    # Vital monitor + IV pole
    pf.make_bevel_box("S3_MonStand", (OX - 2.35, -1.95, 0.65), (0.45, 0.42, 1.30), m_steel, col, bevel_w=0.02)
    pf.make_bevel_box("S3_MonBox", (OX - 2.35, -1.95, 1.48), (0.58, 0.24, 0.44), m_mon_bg, col, bevel_w=0.02)
    pf.make_bevel_box("S3_MonECG", (OX - 2.35, -1.82, 1.48), (0.46, 0.02, 0.04), m_mon_ln, col, bevel_w=0.005)
    pf.make_smooth_cyl("S3_IVPole", (OX - 2.35, -0.75, 1.05), 0.028, 2.1, m_steel, col, segs=12)

    # Characters in Hospital Room
    doctor = build_story_avatar("doctor", "Doctor_Hosp", col)
    dad_hosp = build_story_avatar("dad", "Dad_Hosp", col)
    mom_hosp = build_story_avatar("mom", "Mom_Hosp", col)
    baby = build_baby_theo("Baby_Theo_Blonde", col)

    # Doctor stands center-left facing +Y toward camera/Dad, holding Baby Theo + Clipboard!
    cf.set_char_transform(doctor, OX - 0.18, -0.25, 0.0, yaw_deg=12.0)
    cf.set_char_transform(dad_hosp, OX + 0.92, 0.55, 0.0, yaw_deg=-24.0)
    # Mom sits resting propped in hospital bed
    cf.set_char_transform(mom_hosp, bed_x, bed_y - 0.40, 0.30, yaw_deg=18.0)
    # Initialize Baby Theo cleanly inside Hospital set (never at Set 1 origin!)
    baby.location = (OX - 0.14, 0.28, 1.08)
    baby.scale = (1.12, 1.12, 1.12)

    # Clipboard attached to Doctor's Left Hand (Arm_L_Lower)
    clip_root = bpy.data.objects.new("S3_Clipboard", None)
    col.objects.link(clip_root)
    cf._bind_bone(clip_root, doctor["arm"], "Arm_L_Lower")
    clip_root.location = (0.44, 0.18, 0.72)
    clip_root.rotation_euler = (math.radians(-65), math.radians(-10), math.radians(-24))
    pf.make_bevel_box("S3_ClipWood", (0, 0, 0), (0.36, 0.025, 0.46), m_board, col, bevel_w=0.008, parent=clip_root)
    bm = bmesh.new()
    v0 = bm.verts.new((-0.155, 0.016, -0.195))
    v1 = bm.verts.new((0.155, 0.016, -0.195))
    v2 = bm.verts.new((0.155, 0.016, 0.195))
    v3 = bm.verts.new((-0.155, 0.016, 0.195))
    f = bm.faces.new((v0, v1, v2, v3))
    uv = bm.loops.layers.uv.new("UVMap")
    for lp, c in zip(f.loops, [(1.0, 0.0), (0.0, 0.0), (0.0, 1.0), (1.0, 1.0)]):
        lp[uv].uv = c
    pf._finish_bm(bm, "S3_ClipSheet", (0, 0, 0), m_paper, col, parent=clip_root, smooth=False)
    bm_b = bmesh.new()
    b0 = bm_b.verts.new((0.155, -0.016, -0.195))
    b1 = bm_b.verts.new((-0.155, -0.016, -0.195))
    b2 = bm_b.verts.new((-0.155, -0.016, 0.195))
    b3 = bm_b.verts.new((0.155, -0.016, 0.195))
    fb = bm_b.faces.new((b0, b1, b2, b3))
    uvb = bm_b.loops.layers.uv.new("UVMap")
    for lp, c in zip(fb.loops, [(1.0, 0.0), (0.0, 0.0), (0.0, 1.0), (1.0, 1.0)]):
        lp[uvb].uv = c
    pf._finish_bm(bm_b, "S3_ClipSheetBack", (0, 0, 0), m_paper, col, parent=clip_root, smooth=False)

    # Clinical overhead area lights
    add_area_light("S3_KeyLight", (OX + 0.5, 2.2, 2.9), target=(OX, -0.2, 1.15), energy=220.0, size=2.4, color_hex="#FFFFFF", col=col)
    add_area_light("S3_RimLight", (OX - 1.5, -1.8, 2.6), target=(OX + 0.2, 0.2, 1.1), energy=140.0, size=1.8, color_hex="#BAE6FD", col=col)

    return {"col": col, "OX": OX, "doctor": doctor, "dad": dad_hosp, "mom": mom_hosp, "baby": baby}


# ==================== MAIN ANIMATION & RENDER DRIVER ====================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=0)
    args, _ = parser.parse_known_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])

    beats_data = sc.load_beats()
    words = sc.load_words()
    beats = {b["id"]: b for b in beats_data["beats"]}
    fps = beats_data["fps"]
    total_dur = beats_data["total_duration"]
    total_frames = int(round(total_dur * fps))

    scene = bpy.context.scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    sc.configure_stylized_eevee(scene, res_x=720, res_y=1280, samples=12, raytracing=True, fast_gi=True)

    cam_data = bpy.data.cameras.new("MainCam")
    cam = bpy.data.objects.new("MainCam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam

    # Sun light for Set 1 Exterior
    sun = add_sun_light("S1_Sun", elevation_deg=44.0, azimuth_deg=35.0, energy=3.4, color_hex="#FFF7ED")

    # Build all 3 isolated sets
    s1 = build_starter_house_set(scene)
    dad1 = build_story_avatar("dad", "Dad_Hook", s1["col"])
    mom1 = build_story_avatar("mom", "Mom_Hook", s1["col"])

    s2 = build_tunnel_race_set(scene)
    s3 = build_hospital_set(scene)

    # Extract exact word-synced timestamps
    t_b01s, t_b01e = beats["b01_teamwork"]["start"], beats["b01_teamwork"]["end"]
    t_b02s, t_b02e = beats["b02_huss"]["start"], beats["b02_huss"]["clip_end"]
    t_b03s = beats["b03_deadliest_race"]["start"]
    t_b04s = beats["b04_theo_intro"]["start"]
    t_b05s = beats["b05_countdown_go"]["start"]
    t_go = beats["b05_countdown_go"]["countdown_ticks"][-1]["start"]
    t_b06s = beats["b06_dropping"]["start"]
    t_42 = find_word_time(words, "42", t_b06s + 2.8, after=t_b06s)
    t_gone = find_word_time(words, "gone", t_42 + 0.35, after=t_42)
    t_12 = find_word_time(words, "12", t_gone + 0.30, after=t_gone)
    t_cooked = find_word_time(words, "cooked", t_12 + 0.35, after=t_12)
    t_b07s = beats["b07_neck_and_neck"]["start"]
    t_b08s, t_b08e = beats["b08_climax_win"]["start"], beats["b08_climax_win"]["end"]
    t_won = find_word_time(words, "won", t_b08s + 1.5, after=t_b08s)
    t_b09s = beats["b09_hospital_doctor"]["start"]
    t_b10s = beats["b10_dad_twist"]["start"]

    huss_frames = [int(round(h * fps)) + 1 for h in beats["b02_huss"]["huss_hit_times"]]
    slam_frame = int(round((t_b02s - 0.14) * fps)) + 1
    bump_frame = int(round((t_b06s + 1.72) * fps)) + 1
    cooked_frame = int(round(t_cooked * fps)) + 1
    egg_hit_frame = int(round(t_won * fps)) + 1
    flash_center_frame = int(round((t_b08e + 0.04) * fps)) + 1
    dad_horror_frame = int(round(t_b10s * fps)) + 1

    # Cut boundaries for shots.json
    cut_times = [
        0.0, 1.85, 3.30, t_b02s, t_b03s, t_b03s + 1.85, t_b04s, t_b04s + 2.95,
        t_b05s, t_b06s, t_b06s + 1.65, t_42 - 0.15, t_12 - 0.15,
        t_b07s, t_b07s + 1.20, t_b08s, t_b08s + 2.15,
        t_b09s, t_b09s + 1.35, t_b10s,
    ]
    cut_frames = [max(0, int(round(ct * fps))) for ct in cut_times]

    shots_meta = {
        "shots": [
            {"id": i + 1, "a": cut_frames[i], "b": (cut_frames[i + 1] if i + 1 < len(cut_frames) else total_frames)}
            for i in range(len(cut_frames))
        ],
        "planned": [[max(0, flash_center_frame - 6), min(total_frames, flash_center_frame + 6)]],
        "impact_frames": [bump_frame, cooked_frame, egg_hit_frame],
        "egg_hit_frame": egg_hit_frame,
        "flash_center_frame": flash_center_frame,
        "shake_frames": huss_frames + [slam_frame, bump_frame, cooked_frame, egg_hit_frame, dad_horror_frame],
        "cut_frames": cut_frames,
    }
    (PROJ_DIR / "voice" / "shots.json").write_text(json.dumps(shots_meta, indent=2), encoding="utf-8")

    # Helper to compute active kick offset
    def get_kick(f_idx: int) -> int:
        best = 999
        for kf in shots_meta["shake_frames"]:
            d = f_idx - kf
            if 0 <= d < 7 and d < best:
                best = d
        return best if best < 7 else -1

    active_world = [None]

    def set_frame_state(f_idx: int):
        t = (f_idx - 1) / float(fps)
        kick = get_kick(f_idx)

        # ---- SET 1: HOOK STARTER HOUSE (0 .. t_b03s) ----
        if t < t_b03s:
            if active_world[0] != "day":
                sc.setup_world(scene, "day")
                sun.hide_render = False
                active_world[0] = "day"

            # Reset house shake & dust puffs outside b02
            if t < t_b02s:
                s1["house_root"].location = (0.0, -6.2, 0.0)
                s1["house_root"].rotation_euler = (0.0, 0.0, 0.0)
                for p, _, _, _ in s1["dust_puffs"]:
                    p.scale = (0.001, 0.001, 0.001)

            if t < 1.85:
                # Shot 1a: Walking side-by-side toward Starter House (zero arm overlap + house framed!)
                u = smoothstep(t / 1.85)
                wy = lerp(2.20, -1.65, u)
                cf.set_char_transform(dad1, 0.64, wy, 0.0, yaw_deg=180.0)
                cf.set_char_transform(mom1, -0.64, wy, 0.0, yaw_deg=180.0)
                for ch, ph in ((dad1, 0.0), (mom1, math.pi)):
                    sw = math.sin(t * 10.5 + ph)
                    cf.pose_char(ch, pelvis_z=abs(sw) * 0.04, arm_l=(sw * 24, 0, 0), arm_r=(-sw * 24, 0, 0), leg_l=(-sw * 26, 0, 0), leg_r=(sw * 26, 0, 0))
                cf.set_face_with_blink(dad1, "dad_serious_nod", f_idx, seed=1)
                cf.set_face_with_blink(mom1, "mom_serious_nod", f_idx, seed=2)
                s1["door_hinge"].rotation_euler = (0, 0, 0)
                sc.set_camera_look(cam, (2.45 - 0.35 * u, -3.95, 1.62), (0.0, wy - 0.8, 1.25), lens=30.0)

            elif t < 3.30:
                # Shot 1b: Stop, face each other & camera (+48 / -48 deg!), serious nod, door swings open behind
                u = smoothstep((t - 1.85) / 1.45)
                cf.set_char_transform(dad1, 0.62, -2.25, 0.0, yaw_deg=48.0)
                cf.set_char_transform(mom1, -0.62, -2.25, 0.0, yaw_deg=-48.0)
                nod = math.sin(smoothstep((u - 0.25) / 0.55) * math.pi) * 24.0 if u > 0.25 else 0.0
                cf.pose_char(dad1, head_rot=(-nod, 0, 0), arm_l=(10, 0, 0), arm_r=(10, 0, 0))
                cf.pose_char(mom1, head_rot=(-nod, 0, 0), arm_l=(10, 0, 0), arm_r=(10, 0, 0))
                cf.set_face_with_blink(dad1, "dad_serious_nod", f_idx, seed=1)
                cf.set_face_with_blink(mom1, "mom_serious_nod", f_idx, seed=2)
                s1["door_hinge"].rotation_euler = (0, 0, math.radians(-82.0 * smoothstep((u - 0.4) / 0.6)))
                sc.set_camera_look(cam, (0.0, 0.95 - 0.35 * u, 1.42), (0.0, -2.25, 1.28), lens=34.0 + 3.0 * u)

            elif t < t_b02s:
                # Shot 1c: Turn & step inside house; door SLAMS shut!
                u = smoothstep((t - 3.30) / max(0.2, t_b02s - 3.30))
                wy = lerp(-2.25, -5.85, min(1.0, u / 0.72))
                sw = math.sin(t * 12.0) * (1.0 if u < 0.72 else 0.0)
                cf.set_char_transform(dad1, 0.28, wy, 0.0, yaw_deg=180.0)
                cf.set_char_transform(mom1, -0.28, wy, 0.0, yaw_deg=180.0)
                cf.pose_char(dad1, arm_l=(sw * 22, 0, 0), arm_r=(-sw * 22, 0, 0), leg_l=(-sw * 24, 0, 0), leg_r=(sw * 24, 0, 0))
                cf.pose_char(mom1, arm_l=(-sw * 22, 0, 0), arm_r=(sw * 22, 0, 0), leg_l=(sw * 24, 0, 0), leg_r=(-sw * 24, 0, 0))
                door_open = 1.0 - smoothstep((u - 0.68) / 0.22)
                s1["door_hinge"].rotation_euler = (0, 0, math.radians(-82.0 * door_open))
                sc.set_camera_look(cam, (1.65 - 0.25 * u, -1.35, 1.52), (0.0, -4.35, 1.40), lens=32.0, kick_offset=kick, kick_amp=0.06)

            else:
                # Shot 2: b02_huss — Dad & Mom are INSIDE the closed house while it violently shakes + window dust puffs!
                u = (t - t_b02s) / max(0.1, t_b03s - t_b02s)
                cf.set_char_transform(dad1, 0.28, -6.2, 0.0, yaw_deg=180.0)
                cf.set_char_transform(mom1, -0.28, -6.2, 0.0, yaw_deg=180.0)
                s1["door_hinge"].rotation_euler = (0, 0, 0)
                pulse = sum(math.exp(-((t - ht) * 18.0) ** 2) for ht in beats["b02_huss"]["huss_hit_times"])
                sx_j = math.sin(f_idx * 2.7) * (0.14 + 0.16 * pulse)
                sz_j = abs(math.cos(f_idx * 3.1)) * (0.08 + 0.10 * pulse)
                ry_j = math.cos(f_idx * 2.4) * (3.5 + 3.5 * pulse)
                s1["house_root"].location = (sx_j, -6.2, sz_j)
                s1["house_root"].rotation_euler = (0.0, math.radians(ry_j), 0.0)
                for p, (ax, ay, az), sx_dir, di in s1["dust_puffs"]:
                    pu = (u * 1.45 + di * 0.06) % 1.0
                    sc_p = 0.25 + 1.05 * math.sin(pu * math.pi)
                    p.scale = (sc_p, sc_p, sc_p)
                    p.location = (ax + sx_dir * pu * 1.35, ay + pu * 0.65, az + pu * 0.85)
                sc.set_camera_look(cam, (0.35, 3.2 - 0.45 * u, 2.15), (0.0, -5.8, 2.25), lens=28.0, kick_offset=kick, kick_amp=0.09)

        # ---- SET 2: GLOWING TUNNEL & SPERM RACE (t_b03s .. t_b09s) ----
        elif t < t_b09s:
            if active_world[0] != "tunnel":
                sc.setup_world(scene, "tunnel")
                sun.hide_render = True
                active_world[0] = "tunnel"

            OX, OZ = s2["OX"], s2["OZ"]

            # Gate barrier state (red closed -> green retracted on GO!)
            if t < t_go:
                for gb in s2["gate_bars"]:
                    gb.scale = (1.0, 1.0, 1.0)
            else:
                ug = smoothstep((t - t_go) / 0.20)
                for gb in s2["gate_bars"]:
                    gb.data.materials[0] = s2["m_bar_grn"]
                    gb.scale = (max(0.01, 1.0 - ug), 1.0, 1.0)

            # Rotate & pulse hazards and Golden Egg
            for hroot, hx, hy, hz, hi in s2["hazards"]:
                hroot.location = (hx + math.sin(t * 2.4 + hi) * 0.55, hy, hz + math.cos(t * 2.0 + hi) * 0.45)
                hroot.rotation_euler = (t * 0.9, t * 1.3, 0.0)
            s2["egg_root"].rotation_euler = (0.0, t * 0.45, t * 0.35)

            # Compute Hero Theo (x, y, z) along the race
            if t < t_go:
                # Twitching eagerly at gate
                ty = 2.65
                tx = OX
                tz = OZ + math.sin(t * 5.0) * 0.04
                t_freq, t_amp = 24.0, 20.0
            elif t < t_b07s:
                # Racing through hazards (t_go .. t_b07s) -> Y: 2.65 -> 56.0
                ur = (t - t_go) / max(0.1, t_b07s - t_go)
                ty = lerp(2.65, 56.0, ur)
                # Dodge curve weaving cleanly past hazards
                tx = OX + math.sin((ty - 14.0) * 0.22) * 1.15
                tz = OZ + math.cos((ty - 14.0) * 0.18) * 0.35
                t_freq, t_amp = 28.0, 26.0
            elif t < t_b08s:
                # Neck-and-neck burst (t_b07s .. t_b08s) -> Y: 56.0 -> 70.0
                ur = smoothstep((t - t_b07s) / max(0.1, t_b08s - t_b07s))
                ty = lerp(56.0, 70.0, ur)
                tx = OX - 0.56 + 0.14 * ur
                tz = OZ
                t_freq, t_amp = 32.0, 28.0
            else:
                # Slow-motion climax lunge straight into Golden Egg at Y=82.0! (surface at Y=79.55 -> snout touches at Y=79.15!)
                uc = smoothstep((t - t_b08s) / max(0.2, t_won - t_b08s))
                ty = lerp(70.0, 79.15, uc)
                tx = lerp(OX - 0.42, OX, uc)
                tz = OZ
                t_freq, t_amp = 10.0 if t < t_won else 4.0, 24.0

            s2["theo"]["root"].location = (tx, ty, tz)
            yaw_theo = -math.cos((ty - 14.0) * 0.22) * 14.0 if (t_go <= t < t_b07s) else 0.0
            s2["theo"]["root"].rotation_euler = (0.0, 0.0, math.radians(yaw_theo))
            animate_sperm_tail(s2["theo"], t, freq=t_freq, amp_deg=t_amp, phase=0.0)

            # Sperm #42 (cyan band) -> gets blasted by spiky immune cell right in frame!
            if t < t_go:
                s2["s42"]["root"].location = (OX - 1.35, 2.35, OZ + 0.35)
                s2["s42"]["root"].rotation_euler = (0, 0, 0)
            elif t < t_42:
                u42 = (t - t_go) / max(0.1, t_42 - t_go)
                s2["s42"]["root"].location = (OX - 1.15, lerp(2.35, 34.0, u42), OZ + 0.25)
                s2["s42"]["root"].rotation_euler = (0, 0, 0)
            else:
                ug = (t - t_42) / 0.55
                s2["s42"]["root"].location = (OX - 1.15 - ug * 2.4, 34.0 + ug * 1.2, OZ + 0.25 + ug * 1.8)
                s2["s42"]["root"].rotation_euler = (ug * 4.5, ug * 6.0, ug * 3.5)
            animate_sperm_tail(s2["s42"], t, freq=26.0, amp_deg=24.0, phase=1.4)

            # Sperm #12 (orange band) -> gets zapped/cooked at t_12..t_cooked!
            if t < t_go:
                s2["s12"]["root"].location = (OX + 1.35, 2.45, OZ + 0.30)
                s2["s12"]["root"].rotation_euler = (0, 0, 0)
            elif t < t_12:
                u12 = (t - t_go) / max(0.1, t_12 - t_go)
                s2["s12"]["root"].location = (OX + 1.05, lerp(2.45, 40.2, u12), OZ + 0.42)
                s2["s12"]["root"].rotation_euler = (0, 0, 0)
            else:
                uc = (t - t_12) / 0.65
                s2["s12"]["root"].location = (OX + 1.05 + uc * 2.4, 40.2 - uc * 2.0, OZ + 0.42 - uc * 1.8)
                s2["s12"]["root"].rotation_euler = (uc * 7.5, uc * 5.0, uc * 6.0)
            animate_sperm_tail(s2["s12"], t, freq=26.0, amp_deg=24.0, phase=2.6)

            # Rival #001 (purple band) -> neck-and-neck sprint with Theo in b07-b08!
            if t < t_go:
                s2["s001"]["root"].location = (OX + 0.85, 2.55, OZ - 0.15)
            elif t < t_b07s:
                u1 = (t - t_go) / max(0.1, t_b07s - t_go)
                s2["s001"]["root"].location = (OX + 0.65, lerp(2.55, 55.9, u1), OZ - 0.10)
            elif t < t_b08s:
                u1 = smoothstep((t - t_b07s) / max(0.1, t_b08s - t_b07s))
                s2["s001"]["root"].location = (OX + 0.56, lerp(55.9, 69.8, u1), OZ)
            else:
                u1 = smoothstep((t - t_b08s) / max(0.2, t_won - t_b08s))
                s2["s001"]["root"].location = (OX + 0.72, lerp(69.8, 77.2, u1), OZ - 0.12)
            animate_sperm_tail(s2["s001"], t, freq=t_freq * 0.96, amp_deg=24.0, phase=3.1)

            # Animate all 56 swarm tadpole sperm!
            for item in s2["swarm"]:
                sp = item["sp"]
                if t < t_go:
                    sp["root"].location = (
                        item["x0"] + math.sin(t * 7.0 + item["phase"]) * 0.08,
                        item["y0"] + math.cos(t * 8.0 + item["phase"]) * 0.10,
                        item["z0"] + math.sin(t * 6.0 + item["phase"]) * 0.07,
                    )
                    sp["root"].rotation_euler = (0, 0, 0)
                else:
                    dt_race = t - t_go
                    sy = item["y0"] + dt_race * item["speed"] * (0.45 if t >= t_b08s else 1.0)
                    if t > item["drop_t"]:
                        sy -= (t - item["drop_t"]) * 9.5
                        sz_off = -min(4.0, (t - item["drop_t"]) * 2.5)
                    else:
                        sz_off = 0.0
                    sp["root"].location = (
                        item["x0"] + math.sin(t * 4.5 + item["phase"]) * 0.28,
                        min(73.2, sy),
                        item["z0"] + sz_off + math.cos(t * 4.0 + item["phase"]) * 0.18,
                    )
                animate_sperm_tail(sp, t, freq=22.0, amp_deg=22.0, phase=item["phase"])

            # Camera Cuts across Beats 3-8
            if t < t_b03s + 1.85:
                # 3a: Wide look down glowing tunnel at 60 sperm behind gate
                u = (t - t_b03s) / 1.85
                sc.set_camera_look(cam, (OX + 0.4, 8.8 - 1.2 * u, OZ + 1.65), (OX, 2.0, OZ), lens=26.0)
            elif t < t_b04s:
                # 3b: Rapid zoom right into Theo in middle of pack
                u = smoothstep((t - (t_b03s + 1.85)) / max(0.2, t_b04s - (t_b03s + 1.85)))
                sc.set_camera_look(cam, (OX + lerp(0.5, 0.45, u), lerp(7.6, 4.1, u), OZ + lerp(1.5, 0.32, u)), (OX, 2.75, OZ + 0.06), lens=lerp(28.0, 44.0, u))
            elif t < t_b04s + 2.95:
                # 4a: Hero spotlight slow-orbit on Theo INSIDE gate (Y < 4.9 -> zero gate bar blocking!)
                u = (t - t_b04s) / 2.95
                ang = lerp(-0.55, 0.52, u)
                sc.set_camera_look(cam, (tx + math.sin(ang) * 1.72, ty + math.cos(ang) * 1.72, tz + 0.22), (tx, ty + 0.02, tz + 0.06), lens=34.0, fstop=2.4)
            elif t < t_b05s:
                # 4b: Reverse-angle over Theo looking at massive swarm behind him
                u = (t - (t_b04s + 2.95)) / max(0.2, t_b05s - (t_b04s + 2.95))
                sc.set_camera_look(cam, (tx - 0.65, ty + 1.85 - 0.35 * u, tz + 0.55), (OX, 0.8, OZ), lens=28.0)
            elif t < t_b06s:
                # 5: 3... 2... 1... GO! Gate drops & swarm blasts forward
                u = (t - t_b05s) / max(0.1, t_b06s - t_b05s)
                sc.set_camera_look(cam, (OX + 1.85, 6.2 + 2.0 * u, OZ + 1.25), (OX, 3.8 + 2.5 * u, OZ), lens=28.0)
            elif t < t_b06s + 1.65:
                # 6a: Front-quarter chase cam as swarm rockets through hazards
                sc.set_camera_look(cam, (tx + 1.45, ty + 3.1, tz + 0.72), (tx, ty + 0.4, tz), lens=30.0)
            elif t < t_42 - 0.15:
                # 6b: Tight dodge past green acid hazard + bump rival!
                sc.set_camera_look(cam, (tx - 1.35, ty + 2.4, tz + 0.55), (tx, ty + 0.2, tz), lens=32.0, kick_offset=kick, kick_amp=0.07)
            elif t < t_12 - 0.15:
                # 6c: Sperm 42? Gone! (track #42 + spiky immune cell hazard clearly in frame!)
                p42 = s2["s42"]["root"].location
                sc.set_camera_look(cam, (OX + 0.25, p42.y + 3.6, OZ + 0.85), (OX - 0.95, 34.2, OZ + 0.35), lens=28.0, kick_offset=kick, kick_amp=0.06)
            elif t < t_b07s:
                # 6d: Sperm 12? Cooked! (track #12 + acid hazard clearly in frame!)
                p12 = s2["s12"]["root"].location
                sc.set_camera_look(cam, (OX - 0.25, p12.y + 3.6, OZ + 0.85), (OX + 0.95, 40.2, OZ + 0.40), lens=28.0, kick_offset=kick, kick_amp=0.07)
            elif t < t_b07s + 1.20:
                # 7a: Tight chase cam behind Theo drafting & speed-bursting toward Golden Egg!
                u = (t - t_b07s) / 1.20
                sc.set_camera_look(cam, (tx, ty - 2.35, tz + 0.55), (OX, 82.0, OZ), lens=lerp(34.0, 23.0, u))
            elif t < t_b08s:
                # 7b: Neck-and-neck chase shot looking FORWARD at Theo, Rival #001, AND glowing Golden Egg straight ahead!
                u = (t - (t_b07s + 1.20)) / max(0.1, t_b08s - (t_b07s + 1.20))
                sc.set_camera_look(cam, (OX - 1.35 + 0.35 * u, ty - 2.65, OZ + 0.55), (OX + 0.10, 82.0, OZ), lens=30.0 + 4.0 * u)
            elif t < t_b08s + 2.15:
                # 8a: Slow-motion lunge side-chase toward glowing Golden Egg
                u = (t - t_b08s) / 2.15
                sc.set_camera_look(cam, (tx - 2.15, ty + 0.65, tz + 0.35), (OX, lerp(ty + 2.2, 81.2, u), OZ), lens=34.0)
            else:
                # 8b: Dramatic climax lunge right up to Golden Egg surface (strictly OUTSIDE egg radius 2.52!)
                u = smoothstep((t - (t_b08s + 2.15)) / max(0.2, t_b09s - (t_b08s + 2.15)))
                sc.set_camera_look(cam, (OX + 2.45 - 0.25 * u, 76.2, OZ + 0.45), (OX, 80.2, OZ), lens=34.0, kick_offset=kick, kick_amp=0.08)

            # Anti-lens-occlusion guard: keep background swarm sperm clear of camera lens!
            cam_p = cam.location
            for item in s2["swarm"]:
                sp_r = item["sp"]["root"]
                if (sp_r.location - cam_p).length < 1.55:
                    sp_r.location.z -= 2.4
                    sp_r.location.x += 2.2 if sp_r.location.x >= cam_p.x else -2.2

        # ---- SET 3: HOSPITAL DELIVERY ROOM (t_b09s .. end) ----
        else:
            if active_world[0] != "hospital":
                sc.setup_world(scene, "hospital")
                sun.hide_render = True
                active_world[0] = "hospital"

            OX = s3["OX"]
            # Mom propped comfortably in bed with warm happy smile
            cf.pose_char(s3["mom"], pelvis_z=-0.22, torso_rot=(-26, 0, 0), head_rot=(10, 0, 0), arm_l=(35, 0, 12), arm_r=(35, 0, -12))
            cf.set_face(s3["mom"], "crowd_happy_2.png")

            # Position blonde Baby Theo cradled cleanly in Doctor's forearms
            s3["baby"].location = (OX - 0.14, 0.28, 1.08)
            s3["baby"].scale = (1.12, 1.12, 1.12)
            s3["baby"].rotation_euler = (math.radians(-12), math.radians(-8), math.radians(14))

            if t < t_b09s + 1.35:
                # 9a: Doctor proudly holding up blonde-haired Baby Theo!
                u = (t - t_b09s) / 1.35
                cf.pose_char(s3["doctor"], arm_l=(42, -26, 0), forearm_l=(55, -24, 0), arm_r=(44, 24, 0), forearm_r=(54, 22, 0), head_rot=(-4, -8, 0))
                cf.set_face_with_blink(s3["doctor"], "doctor_proud", f_idx, seed=5)
                cf.pose_char(s3["dad"], arm_l=(12, 0, 0), arm_r=(12, 0, 0), head_rot=(4, 14, 0))
                cf.set_face(s3["dad"], "dad_serious_nod.png")
                sc.set_camera_look(cam, (OX - 0.15 + 0.12 * u, 2.35 - 0.35 * u, 1.38), (OX - 0.15, 0.12, 1.24), lens=34.0)

            elif t < t_b10s:
                # 9b: Doctor looks at clipboard -> SHOCKED O_O face!
                u = (t - (t_b09s + 1.35)) / max(0.1, t_b10s - (t_b09s + 1.35))
                if u < 0.45:
                    cf.pose_char(s3["doctor"], arm_l=(44, -22, 0), forearm_l=(48, -16, 0), arm_r=(44, 24, 0), forearm_r=(54, 22, 0), head_rot=(-22, 22, 0))
                else:
                    cf.pose_char(s3["doctor"], arm_l=(44, -22, 0), forearm_l=(48, -16, 0), arm_r=(44, 24, 0), forearm_r=(54, 22, 0), head_rot=(6, -6, 0))
                cf.set_face(s3["doctor"], "doctor_shocked.png" if u > 0.35 else "doctor_proud.png")
                sc.set_camera_look(cam, (OX - 0.25, 1.80 - 0.28 * u, 1.44), (OX - 0.05, -0.05, 1.34), lens=38.0)

            else:
                # 10: Hard cut + Dutch tilt + punch-in on DARK-HAIRED DAD staring in pure HORROR (hands clear of face!)
                u = smoothstep((t - t_b10s) / max(0.2, total_dur - t_b10s))
                cf.pose_char(s3["dad"], torso_rot=(-10, 0, 0), head_rot=(6, 16, 0), arm_l=(42, -20, -24), forearm_l=(38, 0, 0), arm_r=(42, 20, 24), forearm_r=(38, 0, 0))
                cf.set_face(s3["dad"], "dad_horrified.png")
                sc.set_camera_look(
                    cam,
                    (OX + 0.58 - 0.08 * u, 2.22 - 0.48 * u, 1.50),
                    (OX + 0.88, 0.55, 1.46),
                    lens=lerp(40.0, 52.0, u),
                    roll_deg=7.5,
                    kick_offset=kick,
                    kick_amp=0.06,
                )

    if args.preview:
        preview_frames = [
            ("p01_walk",        max(1, int(round(0.85 * fps)))),
            ("p02_nod",         max(1, int(round(2.55 * fps)))),
            ("p03_house_shake", huss_frames[1] if len(huss_frames) > 1 else max(1, int(round(5.2 * fps)))),
            ("p04_tunnel_gate", max(1, int(round((t_b03s + 0.7) * fps)))),
            ("p05_theo_hero",   max(1, int(round((t_b04s + 1.4) * fps)))),
            ("p06_race_haz",    max(1, int(round((t_b06s + 1.1) * fps)))),
            ("p07_sperm42",     max(1, int(round((t_42 + 0.15) * fps)))),
            ("p08_neck_egg",    max(1, int(round((t_b07s + 1.7) * fps)))),
            ("p09_climax_egg",  egg_hit_frame),
            ("p10_hosp_baby",   max(1, int(round((t_b09s + 0.65) * fps)))),
            ("p11_doc_shock",   max(1, int(round((t_b09s + 2.05) * fps)))),
            ("p12_dad_horror",  max(1, int(round((t_b10s + 1.0) * fps)))),
        ]
        print(f"Rendering {len(preview_frames)} preview stills...")
        for tag, fnum in preview_frames:
            set_frame_state(fnum)
            sc.render_frame(scene, fnum, preview_tag=tag)
        print("PREVIEW STILLS COMPLETE.")
        return

    f_start = max(1, args.start)
    f_end = total_frames if args.end <= 0 else min(total_frames, args.end)
    print(f"Rendering full sequence frames {f_start}..{f_end} (total {total_frames} @ {fps}fps)...")
    for fnum in range(f_start, f_end + 1):
        out_p = sc.FRAMES_DIR / f"f_{fnum:04d}.png"
        if out_p.exists() and out_p.stat().st_size > 8000:
            continue
        set_frame_state(fnum)
        sc.render_frame(scene, fnum)
        if fnum % 60 == 0:
            print(f"  rendered frame {fnum}/{f_end}")
    print("FULL RENDER COMPLETE.")


if __name__ == "__main__":
    main()
