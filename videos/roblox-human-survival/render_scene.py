"""
render_scene.py — Complete Multi-Set Blender 5.3.0 EEVEE RT+GI Renderer for roblox-human-survival.
Builds 3 rich stylized sets (Town Street, Dining/Kitchen Room, Bedroom + X-Ray Studio) plus custom 3D
survival-mechanic props (swirling air ribbons, 3:00 stopwatch, X-Ray lungs, eye flames, water pitcher &
stream, glass water-tank torso, broccoli+burger meal, bubbling green stomach acid vat, dream hallucinations,
3D floppy disk, stamina/fuel bars) and renders all 1,526 frames (or 16 --preview frames) crash-resumably.

Usage:
    blender --background --python videos/roblox-human-survival/render_scene.py -- --preview
    blender --background --python videos/roblox-human-survival/render_scene.py
"""
import math
import random
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Euler, Vector

SHORTMAKING_ROOT = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking")
PROJ_DIR = SHORTMAKING_ROOT / "videos" / "roblox-human-survival"
REF_DIR = SHORTMAKING_ROOT / "videos" / "roblox-reel-Df1kubCJ-o0-v2"
KIT_DIR = SHORTMAKING_ROOT / "90 Templates & Starter Kits" / "blender-cinema-kit"

# Load OUR scene_common explicitly so char_factory / props_factory share it via sys.modules["scene_common"]
import importlib.util
sys.path.insert(0, str(KIT_DIR))
sys.path.insert(0, str(REF_DIR))
sys.path.insert(0, str(PROJ_DIR))

_spec = importlib.util.spec_from_file_location("scene_common", str(PROJ_DIR / "scene_common.py"))
sc = importlib.util.module_from_spec(_spec)
sys.modules["scene_common"] = sc
_spec.loader.exec_module(sc)

import blender_cinema_lib as bcl
import char_factory as cf
import props_factory as pf


def make_uv_plane(name: str, loc, size_xy: tuple, tex_path: Path, col, rot=(0, 0, 0), emit_str: float = 1.6):
    bm = bmesh.new()
    w, h = size_xy
    # Camera at +Y looking toward -Y sees +X on viewer-LEFT and -X on viewer-RIGHT.
    v0 = bm.verts.new((w * 0.5, 0, -h * 0.5))
    v1 = bm.verts.new((-w * 0.5, 0, -h * 0.5))
    v2 = bm.verts.new((-w * 0.5, 0, h * 0.5))
    v3 = bm.verts.new((w * 0.5, 0, h * 0.5))
    f = bm.faces.new((v0, v1, v2, v3))
    uv = bm.loops.layers.uv.new("UVMap")
    uvs = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    for lp, c in zip(f.loops, uvs):
        lp[uv].uv = c
    mat = sc.make_textured_pbr(
        f"Mat_Banner_{name}", tex_path, proj="UV", rough_min=0.35, rough_max=0.45,
        ao_str=0.0, emit_str=emit_str, alpha_clip=False
    )
    return pf._finish_bm(bm, name, loc, mat, col, rot=rot, bevel_w=0.0, smooth=False)


def build_town_set(scene):
    col = bpy.data.collections.new("Set_Town")
    scene.collection.children.link(col)

    m_asph = sc.make_textured_pbr("Mat_TownAsph", sc.TEX_ENV / "asphalt_speckled.png", sc.TEX_ENV / "asphalt_speckled_bump.png", uv_scale=(0.8, 0.8, 0.8), rough_min=0.72, rough_max=0.90)
    m_pave = sc.make_textured_pbr("Mat_TownPave", sc.TEX_ENV / "sidewalk_pavers.png", sc.TEX_ENV / "sidewalk_pavers_bump.png", uv_scale=(0.85, 0.85, 0.85), rough_min=0.68, rough_max=0.86)
    m_curb = sc.make_stylized_pbr("Mat_TownCurb", "#CBD5E1", rough=0.72, coat=0.0)
    m_grass = sc.make_stylized_pbr("Mat_TownGrass", "#44C458", rough=0.76, coat=0.0, sss=0.06, bump_str=0.04)
    m_dash = sc.make_stylized_pbr("Mat_TownDash", "#F8FAFC", rough=0.65, coat=0.0)

    pf.make_bevel_box("T_Road", (0, 0, -0.15), (46, 8.2, 0.30), m_asph, col, bevel_w=0.02)
    pf.make_bevel_box("T_CurbN", (0, -4.15, -0.04), (46, 0.25, 0.16), m_curb, col, bevel_w=0.02)
    pf.make_bevel_box("T_SideN", (0, -5.6, -0.06), (46, 2.8, 0.20), m_pave, col, bevel_w=0.02)
    pf.make_bevel_box("T_SideS", (0, 5.6, -0.06), (46, 2.8, 0.20), m_pave, col, bevel_w=0.02)
    pf.make_bevel_box("T_Lawn", (0, -14.0, -0.15), (65, 16.0, 0.30), m_grass, col, bevel_w=0.02)
    for ix in range(-18, 20, 3):
        pf.make_bevel_box(f"T_Dash_{ix}", (ix, 0, 0.01), (1.3, 0.18, 0.02), m_dash, col, bevel_w=0.005)

    houses = [
        (-13.5, -9.8, 4.4, 4.0, 5.0, "#7DD3FC", "#2563EB"),
        (-8.2, -10.2, 4.6, 4.2, 5.8, "#FDE68A", "#DC2626"),
        (-2.8, -9.6, 4.2, 3.8, 5.2, "#C4B5FD", "#6D28D9"),
        (2.6, -10.0, 4.6, 4.0, 6.2, "#FCA5A5", "#0F766E"),
        (8.0, -9.7, 4.4, 4.0, 5.4, "#A7F3D0", "#EA580C"),
    ]
    for i, (hx, hy, hw, hd, hh, wc, rc) in enumerate(houses):
        pf.build_townhouse(f"T_TH_{i}", (hx, hy, 0.0), col, hw, hd, hh, wc, rc, is_night=False)
    for ti, (tx, ty, ts) in enumerate([(-10.8, -6.4, 1.15), (-5.4, -6.5, 1.05), (0.0, -6.7, 1.25), (5.5, -6.4, 1.10)]):
        pf.build_bumpy_tree(f"T_Tree_{ti}", (tx, ty, 0.0), col, scale=ts)
    for li, lx in enumerate([-6.8, -1.6, 3.8, 8.8]):
        pf.build_streetlamp(f"T_Lamp_{li}", (lx, -4.35, 0.0), col, is_night=False)

    m_mtn = sc.make_stylized_pbr("Mat_MtnTeal", "#1E4E68", rough=0.78, coat=0.0)
    m_snow = sc.make_stylized_pbr("Mat_MtnSnow", "#F1F5F9", rough=0.62, coat=0.0)
    m_cloud = sc.make_stylized_pbr("Mat_CloudWht", "#F8FAFC", rough=0.72, coat=0.0, sss=0.10)
    for mi, (mx, my, rad, mh) in enumerate([(-14, -23, 6.5, 10.5), (-5, -25, 7.2, 12.2), (5, -24, 6.8, 11.4), (14, -23, 6.2, 10.0)]):
        pf.make_smooth_cyl(f"T_Mtn_{mi}", (mx, my, mh * 0.5 - 0.2), rad, mh, m_mtn, col, segs=16, bevel_w=0.05, r2=0.3)
        pf.make_smooth_cyl(f"T_Snow_{mi}", (mx, my, mh * 0.84 - 0.2), rad * 0.34, mh * 0.34, m_snow, col, segs=16, bevel_w=0.0, r2=0.18)
    for ci, (cx, cy, cz) in enumerate([(-7, -18, 9.2), (1, -20, 10.4), (8, -18, 8.9)]):
        for ox, oy, oz, sc_c in [(0, 0, 0, (1.8, 0.8, 0.8)), (-1.1, 0.1, -0.15, (1.2, 0.7, 0.65)), (1.1, -0.1, -0.15, (1.3, 0.7, 0.7))]:
            pf.make_smooth_sphere(f"T_Cloud_{ci}_{ox}", (cx + ox, cy + oy, cz + oz), sc_c, m_cloud, col, segs=14)
    return col


def build_room_set(scene):
    """Cozy textured bedroom/dining room with espresso table, bed, and window."""
    col = bpy.data.collections.new("Set_Room")
    scene.collection.children.link(col)

    m_floor = sc.make_textured_pbr("Mat_RFloor", sc.TEX_ENV / "wood_planks_honey.png", sc.TEX_ENV / "wood_planks_honey_bump.png", uv_scale=(0.65, 0.65, 0.65), rough_min=0.45, rough_max=0.62, coat=0.04)
    m_table = sc.make_textured_pbr("Mat_RTable", sc.TEX_ENV / "wood_table_espresso.png", sc.TEX_ENV / "wood_table_espresso_bump.png", uv_scale=(1.15, 1.15, 1.15), rough_min=0.42, rough_max=0.58, coat=0.05)
    m_brick = sc.make_textured_pbr("Mat_RBrick", sc.TEX_ENV / "brick_blue_wainscot.png", sc.TEX_ENV / "brick_blue_wainscot_bump.png", uv_scale=(1.05, 1.05, 1.05), rough_min=0.65, rough_max=0.82)
    m_cream = sc.make_stylized_pbr("Mat_RCream", "#F5E2C8", rough=0.75, coat=0.0)
    m_trim = sc.make_stylized_pbr("Mat_RTrim", "#F8FAFC", rough=0.42, coat=0.04)
    m_curt = sc.make_stylized_pbr("Mat_RCurt", "#EA6A20", rough=0.70, coat=0.0, sheen=0.45)
    m_steel = sc.make_stylized_pbr("Mat_RSteel", "#94A3B8", rough=0.28, metal=0.80)
    m_beam = sc.make_stylized_pbr("Mat_RBeam", "#6E4224", rough=0.62)

    pf.make_bevel_box("R_Floor", (0, 1.2, -0.10), (7.6, 8.6, 0.20), m_floor, col, bevel_w=0.01)
    pf.make_smooth_cyl("R_Rug", (0.0, 0.55, 0.008), 1.55, 0.014, sc.make_stylized_pbr("Mat_RRug", "#94A3B8", rough=0.85, sheen=0.4), col, segs=32, bevel_w=0.004)
    pf.make_bevel_box("R_WallR", (3.2, 0.4, 1.8), (0.20, 6.8, 3.8), m_cream, col, bevel_w=0.02)
    pf.make_bevel_box("R_WallL", (-3.2, 0.4, 1.8), (0.20, 6.8, 3.8), m_cream, col, bevel_w=0.02)
    pf.make_bevel_box("R_Ceil", (0, 0.4, 3.55), (7.4, 6.8, 0.20), sc.make_stylized_pbr("Mat_RCeil", "#FFF7ED", rough=0.72), col, bevel_w=0.02)

    pf.make_bevel_box("R_BackBrick", (0, -1.65, 0.55), (6.4, 0.18, 1.10), m_brick, col, bevel_w=0.01)
    pf.make_bevel_box("R_BackRail", (0, -1.55, 1.12), (6.4, 0.10, 0.07), m_trim, col, bevel_w=0.01)
    pf.make_bevel_box("R_BackTop", (0, -1.65, 3.10), (6.4, 0.18, 0.90), m_cream, col, bevel_w=0.015)
    pf.make_bevel_box("R_PierL", (-2.25, -1.65, 1.90), (1.70, 0.18, 1.60), m_cream, col, bevel_w=0.015)
    pf.make_bevel_box("R_PierR", (2.25, -1.65, 1.90), (1.70, 0.18, 1.60), m_cream, col, bevel_w=0.015)
    pf.make_bevel_box("R_WinSill", (0, -1.56, 1.11), (3.05, 0.26, 0.07), m_trim, col, bevel_w=0.01)
    pf.make_bevel_box("R_WinHead", (0, -1.58, 2.66), (3.05, 0.22, 0.08), m_trim, col, bevel_w=0.01)
    pf.make_bevel_box("R_WinMullV", (0, -1.63, 1.88), (0.06, 0.10, 1.52), m_trim, col, bevel_w=0.006)
    pf.make_bevel_box("R_WinMullH", (0, -1.63, 1.90), (2.92, 0.08, 0.05), m_trim, col, bevel_w=0.006)
    pf.make_smooth_cyl("R_CurtRod", (0, -1.44, 2.74), 0.022, 3.5, m_beam, col, rot=(0, math.radians(90), 0), bevel_w=0.004)
    for sx in (-1.38, 1.38):
        for fi in range(3):
            pf.make_smooth_cyl(f"R_Curt_{sx}_{fi}", (sx + (fi - 1) * 0.09, -1.47, 1.90), 0.075, 1.62, m_curt, col, segs=16, bevel_w=0.01)

    # Dining Table (toggleable!)
    table_col = bpy.data.collections.new("Room_Table")
    col.children.link(table_col)
    pf.make_bevel_box("R_TableTop", (0.0, 0.65, 0.695), (2.10, 0.88, 0.05), m_table, table_col, bevel_w=0.012, segs=3)
    for lx in (-0.90, 0.90):
        for ly in (0.30, 0.98):
            pf.make_smooth_cyl(f"R_TLeg_{lx}_{ly}", (lx, ly, 0.34), 0.022, 0.68, m_steel, table_col, segs=14, bevel_w=0.003)

    # Cozy Roblox Bed (toggleable!)
    bed_col = bpy.data.collections.new("Room_Bed")
    col.children.link(bed_col)
    m_bedw = sc.make_stylized_pbr("Mat_BedWood", "#7C4A22", rough=0.55)
    m_mattr = sc.make_stylized_pbr("Mat_Mattress", "#F1F5F9", rough=0.72, sheen=0.4)
    m_blanket = sc.make_stylized_pbr("Mat_Blanket", "#2563EB", rough=0.68, sheen=0.5)
    m_pillow = sc.make_stylized_pbr("Mat_Pillow", "#E0F2FE", rough=0.70, sheen=0.4)
    pf.make_bevel_box("Bed_Frame", (0.0, 0.15, 0.22), (1.35, 2.20, 0.28), m_bedw, bed_col, bevel_w=0.02)
    pf.make_bevel_box("Bed_Headboard", (0.0, -0.92, 0.65), (1.38, 0.12, 0.95), m_bedw, bed_col, bevel_w=0.02)
    pf.make_bevel_box("Bed_Mattress", (0.0, 0.15, 0.40), (1.22, 2.04, 0.18), m_mattr, bed_col, bevel_w=0.04)
    pf.make_bevel_box("Bed_Pillow", (0.0, -0.62, 0.54), (0.86, 0.40, 0.14), m_pillow, bed_col, bevel_w=0.05)
    pf.make_bevel_box("Bed_Blanket", (0.0, 0.42, 0.52), (1.26, 1.48, 0.20), m_blanket, bed_col, bevel_w=0.05)

    return {"col": col, "table_col": table_col, "bed_col": bed_col}


def build_survival_props(scene):
    """Custom 3D gag props for each of the 5 human survival mechanics."""
    pcol = bpy.data.collections.new("Set_SurvivalProps")
    scene.collection.children.link(pcol)

    # 1. Air Swirl Spheres (translucent glowing cyan stream)
    air_col = bpy.data.collections.new("Prop_AirSwirls")
    pcol.children.link(air_col)
    m_air = sc.make_stylized_pbr("Mat_AirSwirl", "#7DD3FC", rough=0.15, emit_hex="#38BDF8", emit_str=2.2, alpha=0.55)
    air_puffs = []
    for i in range(10):
        air_puffs.append(pf.make_smooth_sphere(f"AirPuff_{i}", (0, 0.4, 1.4), (0.055, 0.055, 0.055), m_air, air_col, segs=12))

    # 2. Stopwatch (3:00 countdown) + GAME OVER banner
    sw_clock = pf.build_hero_clock("Prop_BreathStopwatch", (0.58, 0.12, 1.25), pcol, is_alarm=False, scale=1.45)
    banner_gameover = make_uv_plane("GameOverBanner", (0.0, -0.55, 1.55), (1.60, 0.80), sc.TEX_PROPS / "gameover_banner.png", pcol, emit_str=1.5)
    banner_lowh2o = make_uv_plane("LowH2OBanner", (0.0, -0.45, 1.78), (1.45, 0.72), sc.TEX_PROPS / "low_h2o_banner.png", pcol, emit_str=1.4)
    banner_savefail = make_uv_plane("SaveFailedBanner", (0.0, -0.45, 1.98), (1.50, 0.75), sc.TEX_PROPS / "save_failed_banner.png", pcol, emit_str=1.5)

    # 3. X-Ray Translucent Torso + Lungs / Water Tank / Bubbling Green Stomach Vat
    xray_col = bpy.data.collections.new("Prop_XRayChest")
    pcol.children.link(xray_col)
    m_glass_shell = sc.make_stylized_pbr("Mat_XRayShell", "#93C5FD", rough=0.12, coat=0.65, emit_hex="#38BDF8", emit_str=0.35, alpha=0.32)
    pf.make_bevel_box("XRay_TorsoShell", (0.0, 0.0, 1.01), (0.62, 0.34, 0.65), m_glass_shell, xray_col, bevel_w=0.022, segs=3)

    # Two glowing lungs
    m_lung = sc.make_stylized_pbr("Mat_LungGlow", "#38BDF8", rough=0.35, emit_hex="#38BDF8", emit_str=2.6)
    lungs = []
    for sx in (-0.13, 0.13):
        lungs.append(pf.make_smooth_sphere(f"XRay_Lung_{sx}", (sx, 0.0, 1.06), (0.10, 0.09, 0.19), m_lung, xray_col, segs=18))

    # Water Tank fill inside torso
    m_water_fill = sc.make_stylized_pbr("Mat_WaterTankFill", "#0EA5E9", rough=0.10, coat=0.80, emit_hex="#38BDF8", emit_str=1.6, alpha=0.86)
    water_fill = pf.make_bevel_box("XRay_WaterFill", (0.0, 0.0, 0.90), (0.54, 0.28, 0.44), m_water_fill, xray_col, bevel_w=0.012, segs=2)

    # Stomach Acid Vat + Bubbles + Melting Burger Chunks
    m_acid = sc.make_stylized_pbr("Mat_StomachAcid", "#22C55E", rough=0.18, emit_hex="#4ADE80", emit_str=2.4, alpha=0.86)
    acid_vat = pf.make_bevel_box("XRay_AcidVat", (0.0, 0.0, 0.88), (0.52, 0.27, 0.34), m_acid, xray_col, bevel_w=0.015, segs=2)
    acid_bubbles = []
    for bi in range(6):
        acid_bubbles.append(pf.make_smooth_sphere(f"AcidBubble_{bi}", ((bi - 2.5) * 0.07, 0.05, 0.95), (0.032, 0.032, 0.032), m_acid, xray_col, segs=12))
    acid_food = pf.build_hero_burger("XRay_MeltingBurger", (0.0, 0.02, 0.98), xray_col, scale=0.65)

    # 4. Eye Water Droplets + Eye Fire Flames (tapered fiery cones above eyes so burning eyes stay visible!)
    eye_fx_col = bpy.data.collections.new("Prop_EyeFX")
    pcol.children.link(eye_fx_col)
    m_drop = sc.make_stylized_pbr("Mat_EyeDrop", "#38BDF8", rough=0.08, coat=0.9, emit_hex="#BAE6FD", emit_str=1.6, alpha=0.88)
    m_flame = sc.make_stylized_pbr("Mat_EyeFlame", "#F97316", rough=0.25, emit_hex="#EF4444", emit_str=4.8, alpha=0.88)
    m_flame_core = sc.make_stylized_pbr("Mat_EyeFlameCore", "#FACC15", rough=0.20, emit_hex="#FEF08A", emit_str=6.5)
    eye_drops = []
    eye_flames = []
    for side in (-0.078, 0.078):
        for k in range(2):
            eye_drops.append(pf.make_smooth_sphere(f"EyeDrop_{side}_{k}", (side, 0.22, 1.54), (0.020, 0.020, 0.028), m_drop, eye_fx_col, segs=12))
        for k in range(3):
            mat_f = m_flame_core if k == 0 else m_flame
            eye_flames.append(pf.make_smooth_cyl(f"EyeFlame_{side}_{k}", (side, 0.21, 1.62 + k * 0.04), 0.032 - k * 0.007, 0.095, mat_f, eye_fx_col, segs=12, bevel_w=0.0, r2=0.003))

    # 5. Water Pitcher & Pouring Droplet Stream
    water_col = bpy.data.collections.new("Prop_WaterPour")
    pcol.children.link(water_col)
    m_pitcher = sc.make_stylized_pbr("Mat_PitcherGlass", "#38BDF8", rough=0.10, coat=0.90, emit_hex="#7DD3FC", emit_str=0.45, alpha=0.48)
    m_stream = sc.make_stylized_pbr("Mat_WaterStream", "#38BDF8", rough=0.10, coat=0.85, emit_hex="#38BDF8", emit_str=2.2, alpha=0.88)
    pitcher = pf.make_smooth_cyl("Prop_Pitcher", (0.34, 0.26, 1.72), 0.11, 0.28, m_pitcher, water_col, segs=24, rot=(0, math.radians(-52), 0), bevel_w=0.01, r2=0.125)
    water_stream = pf.make_smooth_cyl("Prop_WaterStream", (0.12, 0.24, 1.56), 0.022, 0.26, m_stream, water_col, segs=16, rot=(math.radians(-10), math.radians(-30), 0), bevel_w=0.004, r2=0.014)

    # 6. Meal Plate (Burger + Green Broccoli Plants)
    meal_col = bpy.data.collections.new("Prop_Meal")
    pcol.children.link(meal_col)
    m_plate = sc.make_stylized_pbr("Mat_MealPlate", "#F8FAFC", rough=0.18, coat=0.45)
    m_broc = sc.make_stylized_pbr("Mat_Broccoli", "#16A34A", rough=0.65, bump_str=0.05)
    pf.make_smooth_cyl("Meal_Plate", (0.0, 0.56, 0.735), 0.24, 0.025, m_plate, meal_col, segs=32, bevel_w=0.008)
    pf.build_hero_burger("Meal_Burger", (-0.06, 0.54, 0.748), meal_col, scale=0.85)
    for bx, by, bz in [(0.11, 0.58, 0.79), (0.14, 0.51, 0.78), (0.08, 0.62, 0.77)]:
        pf.make_smooth_sphere(f"Meal_Broc_{bx:.2f}", (bx, by, bz), (0.052, 0.052, 0.048), m_broc, meal_col, segs=14)

    # 7. Dream Hallucination Orbiters (giant eyeball, burger, cat, neon stars)
    dream_col = bpy.data.collections.new("Prop_Dream")
    pcol.children.link(dream_col)
    m_eyew = sc.make_stylized_pbr("Mat_DreamEyeW", "#F8FAFC", rough=0.18, emit_hex="#FFFFFF", emit_str=0.8)
    m_iris = sc.make_stylized_pbr("Mat_DreamIris", "#A855F7", rough=0.20, emit_hex="#C084FC", emit_str=1.8)
    m_star = sc.make_stylized_pbr("Mat_DreamStar", "#FACC15", rough=0.20, emit_hex="#FDE047", emit_str=3.0)
    d_eye = pf.make_smooth_sphere("Dream_Eye", (-0.42, 0.15, 1.35), (0.16, 0.16, 0.16), m_eyew, dream_col, segs=20)
    pf.make_smooth_sphere("Dream_Iris", (-0.42, 0.29, 1.35), (0.08, 0.04, 0.08), m_iris, dream_col, segs=16, parent=d_eye)
    d_burger = pf.build_hero_burger("Dream_Burger", (0.45, 0.25, 1.42), dream_col, scale=1.05)
    d_cat = pf.build_hero_cat("Dream_Cat", (0.0, -0.15, 1.62), dream_col, scale=0.92)
    d_stars = []
    for si in range(6):
        ang = si * (math.pi / 3.0)
        d_stars.append(pf.make_smooth_sphere(f"Dream_Star_{si}", (math.cos(ang) * 0.55, 0.2, 1.45 + math.sin(ang) * 0.25), (0.055, 0.055, 0.055), m_star, dream_col, segs=10))

    # 8. 3D Floppy Disk + 3D Stamina / Fuel Bars
    floppy_col = bpy.data.collections.new("Prop_Floppy")
    pcol.children.link(floppy_col)
    m_flp = sc.make_stylized_pbr("Mat_FloppyBlue", "#2563EB", rough=0.32, emit_hex="#EF4444", emit_str=0.8)
    m_flp_m = sc.make_stylized_pbr("Mat_FloppyMetal", "#E2E8F0", rough=0.18, metal=0.90)
    m_flp_lbl = sc.make_stylized_pbr("Mat_FloppyLabel", "#FEF3C7", rough=0.45)
    pf.make_bevel_box("Floppy_Body", (0, 0, 0), (0.34, 0.04, 0.36), m_flp, floppy_col, bevel_w=0.01)
    pf.make_bevel_box("Floppy_Shutter", (0.02, 0.015, 0.11), (0.18, 0.025, 0.12), m_flp_m, floppy_col, bevel_w=0.004)
    pf.make_bevel_box("Floppy_Label", (0, 0.015, -0.08), (0.24, 0.022, 0.14), m_flp_lbl, floppy_col, bevel_w=0.004)

    bar_col = bpy.data.collections.new("Prop_StatusBar")
    pcol.children.link(bar_col)
    m_bar_bg = sc.make_stylized_pbr("Mat_BarBG", "#0F172A", rough=0.40)
    m_bar_fill = sc.make_stylized_pbr("Mat_BarFill", "#15803D", rough=0.40, emit_hex="#16A34A", emit_str=0.65)
    bar_bg = pf.make_bevel_box("Bar_Frame", (0, 0, 0), (0.76, 0.05, 0.15), m_bar_bg, bar_col, bevel_w=0.01)
    bar_fill = pf.make_bevel_box("Bar_Fill", (0, 0.03, 0), (0.68, 0.05, 0.10), m_bar_fill, bar_col, bevel_w=0.005)

    return {
        "pcol": pcol,
        "air_col": air_col, "air_puffs": air_puffs,
        "sw_clock": sw_clock,
        "banner_gameover": banner_gameover,
        "banner_lowh2o": banner_lowh2o,
        "banner_savefail": banner_savefail,
        "xray_col": xray_col, "lungs": lungs, "m_lung": m_lung,
        "water_fill": water_fill, "m_water_fill": m_water_fill,
        "acid_vat": acid_vat, "acid_bubbles": acid_bubbles, "acid_food": acid_food,
        "eye_fx_col": eye_fx_col, "eye_drops": eye_drops, "eye_flames": eye_flames,
        "water_col": water_col, "pitcher": pitcher, "water_stream": water_stream,
        "meal_col": meal_col,
        "dream_col": dream_col, "d_eye": d_eye, "d_burger": d_burger, "d_cat": d_cat, "d_stars": d_stars,
        "floppy_col": floppy_col,
        "bar_col": bar_col, "bar_bg": bar_bg, "bar_fill": bar_fill, "m_bar_fill": m_bar_fill,
    }


def setup_lights(scene):
    lcol = bpy.data.collections.new("Scene_Lights")
    scene.collection.children.link(lcol)

    def add_area(name, loc, tgt, energy, size, temp, spread_deg=85):
        ld = bpy.data.lights.new(name, type="AREA")
        ld.energy = energy
        ld.size = size
        ld.spread = math.radians(spread_deg)
        ld.use_temperature = True
        ld.temperature = temp
        lo = bpy.data.objects.new(name, ld)
        lcol.objects.link(lo)
        lo.location = loc
        lo.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        return lo, ld

    key_o, key_d = add_area("KeyLight", (1.6, 2.8, 3.2), (0, 0.1, 1.15), 260.0, 2.4, 5200, 82)
    fill_o, fill_d = add_area("FillLight", (-2.2, 2.5, 2.0), (0, 0.1, 1.25), 95.0, 3.2, 6400, 105)
    rim_o, rim_d = add_area("RimLight", (-1.0, -3.0, 2.8), (0, 0.1, 1.30), 340.0, 2.4, 7200, 68)
    return {"key": (key_o, key_d), "fill": (fill_o, fill_d), "rim": (rim_o, rim_d)}


def set_col_visible(col, visible: bool):
    col.hide_viewport = not visible
    col.hide_render = not visible


def hide_all_gags(props):
    set_col_visible(props["air_col"], False)
    sc.set_hidden_tree(props["sw_clock"], True)
    props["banner_gameover"].hide_render = True
    props["banner_lowh2o"].hide_render = True
    props["banner_savefail"].hide_render = True
    sc.set_hidden_tree(props["acid_food"], True)
    set_col_visible(props["xray_col"], False)
    set_col_visible(props["eye_fx_col"], False)
    set_col_visible(props["water_col"], False)
    set_col_visible(props["meal_col"], False)
    set_col_visible(props["dream_col"], False)
    set_col_visible(props["floppy_col"], False)
    set_col_visible(props["bar_col"], False)


def set_torso_visible(alex, visible: bool):
    for obj in alex["arm"].children:
        if obj.type == "MESH" and obj.parent_bone == "Torso":
            obj.hide_viewport = not visible
            obj.hide_render = not visible


def main():
    preview_only = "--preview" in sys.argv
    bcl.clear_scene()
    scene = bpy.context.scene
    res = (720, 1280)
    sc.configure_stylized_eevee(scene, res_x=res[0], res_y=res[1], samples=(12 if preview_only else 10), raytracing=True, fast_gi=True, motion_blur=False, exposure=-0.10)

    beats_data = sc.load_beats()
    total_frames = int(round(beats_data["total_duration"] * 30))

    town_col = build_town_set(scene)
    room = build_room_set(scene)
    props = build_survival_props(scene)
    lights = setup_lights(scene)

    cast_col = bpy.data.collections.new("Cast")
    scene.collection.children.link(cast_col)
    alex = cf.create_character("alex", "Alex", cast_col)
    friend1 = cf.create_character("teal_friend", "Friend1", cast_col)
    friend2 = cf.create_character("mint_girl", "Friend2", cast_col)
    cf.set_face(friend1, "crowd_happy_1.png")
    cf.set_face(friend2, "crowd_happy_2.png")

    cam_d = bpy.data.cameras.new("Cam_Main")
    cam = bpy.data.objects.new("Cam_Main", cam_d)
    scene.collection.objects.link(cam)
    scene.camera = cam

    bcl.setup_cinema_compositor(
        scene, glare_threshold=1.60, glare_strength=0.12, dispersion=0.0010,
        lift_rgb=(0.99, 0.994, 1.01), gamma_rgb=(1.0, 1.0, 1.0), gain_rgb=(1.01, 1.005, 0.99),
        vignette=0.14,
    )

    # Key kick frames (7-frame impact shakes on major reveals!)
    kick_starts = [
        int(10.48 * 30),  # instant game over
        int(19.05 * 30),  # eyes literally start burning
        int(27.95 * 30),  # organs start failing
        int(46.65 * 30),  # stops saving data
        int(50.10 * 30),  # character breaking down
    ]

    preview_frames = [
        25,    # Breath town hook + air swirls
        105,   # Face holes CU
        177,   # While eating rapid cut
        192,   # Traveling rapid cut
        215,   # Even sleeping rapid cut
        255,   # Three minutes stopwatch + cheek puff
        294,   # Lungs shut down X-ray
        326,   # Instant GAME OVER
        390,   # Slam skin over eyeballs
        485,   # Keep eyes wet (droplets)
        538,   # Vision blurry
        580,   # Eyes burning flames
        660,   # Pour clear liquid
        738,   # Glass water tank torso
        820,   # Tank 12% low warning
        910,   # Meal (burger + broccoli)
        972,   # Tiny rocks (teeth) chewing CU
        1045,  # Bubbling stomach acid vat
        1118,  # Fuel + power walk
        1205,  # Dark room sleep
        1315,  # Hallucinate 8 hours dream
        1395,  # Brain stops saving data (floppy)
        1450,  # Stamina bar 0%
        1505,  # Breaking down collapse
    ]

    frames_to_render = preview_frames if preview_only else list(range(1, total_frames + 1))

    for f in frames_to_render:
        t = (f - 1) / 30.0
        hide_all_gags(props)
        set_torso_visible(alex, True)
        sc.set_hidden_tree(friend1["arm"], True)
        sc.set_hidden_tree(friend2["arm"], True)
        lights["key"][1].color = (1.0, 1.0, 1.0)
        lights["key"][1].energy = 260.0
        lights["rim"][1].color = (1.0, 1.0, 1.0)
        lights["rim"][1].energy = 340.0

        # Active kick offset if within 7 frames of any impact
        kick_off = -1
        for ks in kick_starts:
            if ks <= f < ks + 7:
                kick_off = f - ks
                break

        # ---- WORLD 1: BREATHING (0.00 - 11.45s) ----
        if t < 2.54:
            # 1a: Town hook + air swirls entering face
            u = t / 2.54
            sc.setup_stylized_sky_world(scene, "day", 0.72)
            set_col_visible(town_col, True)
            set_col_visible(room["col"], False)
            set_col_visible(props["air_col"], True)
            sc.set_hidden_tree(friend1["arm"], False)
            sc.set_hidden_tree(friend2["arm"], False)
            cf.set_char_transform(friend1, -1.35, -1.8, 0.0, 10)
            cf.set_char_transform(friend2, 1.40, -1.9, 0.0, -12)
            cf.animate_party_dance(friend1, t, 0.0, 0.5)
            cf.animate_party_dance(friend2, t, 1.2, 0.5)

            cf.set_char_transform(alex, 0.0, 0.0, 0.0, 0)
            breath = math.sin(t * 5.0)
            cf.pose_char(alex, pelvis_z=0.02 * breath, torso_rot=(breath * 4.0, 0, 0), head_rot=(-4 + breath * 3.0, 0, 0), arm_l=(14, 0, 14), forearm_l=(25, 0, 0), arm_r=(14, 0, -14), forearm_r=(25, 0, 0))
            cf.set_face_with_blink(alex, "alex_inhale_o", f, 1)
            for idx, ap in enumerate(props["air_puffs"]):
                p = ((t * 1.4 + idx * 0.1) % 1.0)
                ang = idx * 1.3 + t * 5.0
                rad = (1.0 - p) * 0.48
                ap.location = (math.cos(ang) * rad, 0.18 + (1.0 - p) * 0.55, 1.42 + math.sin(ang) * rad * 0.6)
                sc_p = 0.4 + 0.8 * (1.0 - p)
                ap.scale = (sc_p, sc_p, sc_p)
            fstop_blur = 0.6 + 2.6 * min(1.0, u * 3.0)
            sc.set_camera_look(cam, (0.0, 1.65 + 0.75 * u, 1.46), (0.0, 0.0, 1.42), lens=36.0, fstop=fstop_blur)

        elif t < 4.29:
            # 1b: Holes in face CU
            u = (t - 2.54) / (4.29 - 2.54)
            sc.setup_stylized_sky_world(scene, "day", 0.72)
            set_col_visible(town_col, True)
            set_col_visible(room["col"], False)
            set_col_visible(props["air_col"], True)
            cf.set_char_transform(alex, 0.0, 0.0, 0.0, 0)
            cf.pose_char(alex, head_rot=(-3 + math.sin(t * 7.0) * 3.0, 0, 0), arm_l=(22, 0, 18), forearm_l=(35, 0, 0), arm_r=(22, 0, -18), forearm_r=(35, 0, 0))
            cf.set_face_with_blink(alex, "alex_inhale_o", f, 2)
            for idx, ap in enumerate(props["air_puffs"]):
                p = ((t * 1.9 + idx * 0.1) % 1.0)
                ang = idx * 1.4 + t * 6.0
                rad = (1.0 - p) * 0.34
                ap.location = (math.cos(ang) * rad, 0.19 + (1.0 - p) * 0.42, 1.43 + math.sin(ang) * rad * 0.5)
                sc_p = 0.35 + 0.75 * (1.0 - p)
                ap.scale = (sc_p, sc_p, sc_p)
            sc.set_camera_look(cam, (0.18 - 0.32 * u, 1.38 - 0.18 * u, 1.54), (0.0, 0.12, 1.50), lens=46.0, fstop=2.4)

        elif t < 5.70:
            # 1c: Non-stop town walk
            u = (t - 4.29) / (5.70 - 4.29)
            sc.setup_stylized_sky_world(scene, "day", 0.72)
            set_col_visible(town_col, True)
            set_col_visible(room["col"], False)
            set_col_visible(props["air_col"], True)
            wx = -0.35 + 0.7 * u
            cf.set_char_transform(alex, wx, 0.0, 0.0, -15)
            w = t * 8.0
            cf.pose_char(alex, pelvis_z=abs(math.sin(w)) * 0.05, torso_rot=(4, 0, math.sin(w) * 4), arm_l=(math.sin(w) * 28, 0, 10), arm_r=(-math.sin(w) * 28, 0, -10), leg_l=(-math.sin(w) * 24, 0, 0), leg_r=(math.sin(w) * 24, 0, 0))
            cf.set_face(alex, "alex_determined.png")
            for idx, ap in enumerate(props["air_puffs"]):
                p = ((t * 1.7 + idx * 0.1) % 1.0)
                ap.location = (wx + math.cos(idx) * 0.18 * (1 - p), 0.18 + (1 - p) * 0.4, 1.44)
                ap.scale = (0.5, 0.5, 0.5)
            sc.set_camera_look(cam, (wx + 0.25, 2.35 - 0.3 * u, 1.40), (wx, 0.0, 1.32), lens=34.0)

        elif t < 6.10:
            # 1d: While eating (rapid cut!)
            u = (t - 5.70) / 0.40
            sc.setup_stylized_sky_world(scene, "interior", 0.55)
            set_col_visible(town_col, False)
            set_col_visible(room["col"], True)
            set_col_visible(room["table_col"], True)
            set_col_visible(room["bed_col"], False)
            set_col_visible(props["meal_col"], True)
            set_col_visible(props["air_col"], True)
            cf.set_char_transform(alex, 0.0, 0.0, 0.0, 0)
            cf.pose_char(alex, torso_rot=(8, 0, 0), arm_l=(65, -20, 0), forearm_l=(55, 0, 0), arm_r=(65, 20, 0), forearm_r=(55, 0, 0))
            cf.set_face(alex, "alex_chewing.png")
            for idx, ap in enumerate(props["air_puffs"]):
                p = ((t * 2.0 + idx * 0.12) % 1.0)
                ap.location = (math.cos(idx) * 0.22 * (1 - p), 0.22 + (1 - p) * 0.35, 1.46)
                ap.scale = (0.45, 0.45, 0.45)
            sc.set_camera_look(cam, (0.28, 2.05 - 0.25 * u, 1.46), (0.0, 0.2, 1.28), lens=35.0)

        elif t < 6.65:
            # 1e: Traveling (rapid cut!)
            u = (t - 6.10) / 0.55
            sc.setup_stylized_sky_world(scene, "day", 0.72)
            set_col_visible(town_col, True)
            set_col_visible(room["col"], False)
            set_col_visible(props["air_col"], True)
            wx = 0.5 - 1.0 * u
            cf.set_char_transform(alex, wx, -0.3, 0.0, 75)
            w = t * 13.0
            cf.pose_char(alex, pelvis_z=abs(math.sin(w)) * 0.08, torso_rot=(12, 0, 0), arm_l=(math.sin(w) * 45, 0, 12), forearm_l=(55, 0, 0), arm_r=(-math.sin(w) * 45, 0, -12), forearm_r=(55, 0, 0), leg_l=(-math.sin(w) * 35, 0, 0), leg_r=(math.sin(w) * 35, 0, 0))
            cf.set_face(alex, "alex_inhale_o.png")
            for idx, ap in enumerate(props["air_puffs"]):
                p = ((t * 2.2 + idx * 0.1) % 1.0)
                ap.location = (wx - 0.25 * (1 - p), -0.3, 1.45)
                ap.scale = (0.5, 0.5, 0.5)
            sc.set_camera_look(cam, (wx - 0.2, 2.35, 1.38), (wx, -0.3, 1.30), lens=32.0, roll_deg=-4.0)

        elif t < 7.63:
            # 1f: Even sleeping (rapid cut! Head cleanly on pillow at y=-0.65, face UP!)
            u = (t - 6.65) / (7.63 - 6.65)
            sc.setup_stylized_sky_world(scene, "night", 0.35)
            set_col_visible(town_col, False)
            set_col_visible(room["col"], True)
            set_col_visible(room["table_col"], False)
            set_col_visible(room["bed_col"], True)
            set_col_visible(props["air_col"], True)
            cf.set_char_transform(alex, 0.0, 0.90, 0.70, 0)
            alex["arm"].rotation_euler = (math.radians(90), 0, 0)
            cf.pose_char(alex, arm_l=(10, 0, 12), arm_r=(10, 0, -12))
            cf.set_face(alex, "alex_sleep_closed.png")
            for idx, ap in enumerate(props["air_puffs"]):
                p = ((t * 1.5 + idx * 0.12) % 1.0)
                ap.location = (math.cos(idx) * 0.16 * (1 - p), -0.62, 0.92 + (1 - p) * 0.38)
                ap.scale = (0.45, 0.45, 0.45)
            sc.set_camera_look(cam, (0.45, 0.95 - 0.18 * u, 1.85), (0.0, -0.58, 0.80), lens=34.0)

        elif t < 9.27:
            # 1g: Stop for three minutes -> cheek puff + giant red stopwatch fully framed!
            u = (t - 7.63) / (9.27 - 7.63)
            sc.setup_stylized_sky_world(scene, "interior", 0.50)
            set_col_visible(town_col, False)
            set_col_visible(room["col"], True)
            set_col_visible(room["table_col"], False)
            set_col_visible(room["bed_col"], False)
            sc.set_hidden_tree(props["sw_clock"], False)
            props["sw_clock"].scale = (1.18, 1.18, 1.18)
            props["sw_clock"].location = (0.36, 0.24, 1.24 + 0.03 * math.sin(t * 18.0))
            props["sw_clock"].rotation_euler = (0, 0, math.radians(-12))
            cf.set_char_transform(alex, -0.22, 0.0, 0.0, 0)
            cf.pose_char(alex, head_rot=(4, 0, math.sin(t * 25.0) * 3.0), arm_l=(85, -35, 10), forearm_l=(80, 0, 0), arm_r=(85, 35, -10), forearm_r=(80, 0, 0))
            cf.set_face(alex, "alex_cheek_puff.png")
            sc.set_camera_look(cam, (0.04, 2.38 - 0.30 * u, 1.44), (0.04, 0.05, 1.38), lens=35.0)

        elif t < 10.30:
            # 1h: Lungs shut down X-ray
            u = (t - 9.27) / (10.30 - 9.27)
            sc.setup_stylized_sky_world(scene, "night", 0.25)
            set_col_visible(town_col, False)
            set_col_visible(room["col"], True)
            set_col_visible(room["table_col"], False)
            set_col_visible(room["bed_col"], False)
            set_torso_visible(alex, False)
            set_col_visible(props["xray_col"], True)
            for lg in props["lungs"]:
                lg.hide_render = False
                lg.hide_viewport = False
            props["water_fill"].hide_render = True
            props["acid_vat"].hide_render = True
            for ab in props["acid_bubbles"]:
                ab.hide_render = True
            # Lungs shrink & flicker dark red as they shut down!
            shrink = max(0.35, 1.0 - 0.65 * u)
            for lg in props["lungs"]:
                lg.scale = (shrink, shrink, shrink)
            em_str = 0.25 if u > 0.55 else 2.8 * (1.0 - u)
            for n in props["m_lung"].node_tree.nodes:
                if n.type == "BSDF_PRINCIPLED":
                    n.inputs["Emission Strength"].default_value = em_str
                    n.inputs["Emission Color"].default_value = (1.0, 0.15, 0.15, 1.0) if u > 0.45 else (0.22, 0.74, 0.97, 1.0)
            cf.set_char_transform(alex, 0.0, 0.0, 0.0, 0)
            cf.pose_char(alex, arm_l=(24, 0, 18), arm_r=(24, 0, -18))
            cf.set_face(alex, "alex_shocked_wide.png")
            sc.set_camera_look(cam, (0.0, 1.95 - 0.25 * u, 1.24), (0.0, 0.0, 1.16), lens=38.0)

        elif t < 11.45:
            # 1i: Instant GAME OVER! (Both fallen Alex & right-reading banner cleanly in frame!)
            u = (t - 10.30) / (11.45 - 10.30)
            sc.setup_stylized_sky_world(scene, "night", 0.30)
            set_col_visible(town_col, False)
            set_col_visible(room["col"], True)
            set_col_visible(room["table_col"], False)
            set_col_visible(room["bed_col"], False)
            props["banner_gameover"].hide_render = False
            props["banner_gameover"].scale = (0.76, 0.76, 0.76)
            props["banner_gameover"].location = (0.0, -0.35, 2.08)
            lights["key"][1].color = (1.0, 0.35, 0.35)
            lights["key"][1].energy = 320.0
            cf.set_char_transform(alex, 0.0, 0.10, 0.20, 0)
            alex["arm"].rotation_euler = (math.radians(-35), 0, math.radians(15))
            cf.pose_char(alex, arm_l=(40, 0, 45), arm_r=(35, 0, -45), leg_l=(20, 0, 15), leg_r=(-10, 0, -15))
            cf.set_face(alex, "alex_glitch_dead.png")
            sc.set_camera_look(cam, (0.0, 2.75 + 0.15 * u, 1.48), (0.0, 0.0, 1.25), lens=32.0, roll_deg=-5.0, kick_offset=kick_off, kick_amp=0.07)

        # ---- WORLD 2: BLINKING (11.45 - 20.15s) ----
        elif t < 15.06:
            # 2a: Slam skin over eyeballs every few seconds (rapid exaggerated blink slams!)
            u = (t - 11.45) / (15.06 - 11.45)
            sc.setup_stylized_sky_world(scene, "day", 0.72)
            set_col_visible(town_col, False)
            set_col_visible(room["col"], True)
            set_col_visible(room["table_col"], False)
            set_col_visible(room["bed_col"], False)
            cf.set_char_transform(alex, 0.0, 0.0, 0.0, 0)
            cycle = (f % 16)
            if cycle in (0, 1, 2):
                cf.set_face(alex, "alex_deadpan_closed.png")
                head_nod = 6.0
            elif cycle in (3, 15):
                cf.set_face(alex, "alex_deadpan_half.png")
                head_nod = 2.0
            else:
                cf.set_face(alex, "alex_shocked_wide.png")
                head_nod = -2.0
            cf.pose_char(alex, head_rot=(head_nod, 0, 0), arm_l=(15, 0, 12), arm_r=(15, 0, -12))
            punch = 0.04 if cycle in (0, 1) else 0.0
            sc.set_camera_look(cam, (0.08 - 0.16 * u, 1.32 - punch - 0.12 * u, 1.54), (0.0, 0.12, 1.50), lens=50.0, fstop=2.2)

        elif t < 17.30:
            # 2b: Keep eyes wet (3D water droplets!)
            u = (t - 15.06) / (17.30 - 15.06)
            sc.setup_stylized_sky_world(scene, "day", 0.72)
            set_col_visible(town_col, False)
            set_col_visible(room["col"], True)
            set_col_visible(room["table_col"], False)
            set_col_visible(room["bed_col"], False)
            set_col_visible(props["eye_fx_col"], True)
            for ef in props["eye_flames"]:
                ef.hide_render = True
            for di, ed in enumerate(props["eye_drops"]):
                ed.hide_render = False
                side = -0.10 if di < 2 else 0.10
                ed.location = (side + (di % 2 - 0.5) * 0.04, 0.24, 1.50 + math.sin(t * 8.0 + di) * 0.03)
            cf.set_char_transform(alex, 0.0, 0.0, 0.0, -18)
            cf.pose_char(alex, head_rot=(-4, 0, 0))
            cf.set_face_with_blink(alex, "alex_deadpan", f, 3)
            sc.set_camera_look(cam, (-0.42 + 0.15 * u, 1.35, 1.54), (0.0, 0.12, 1.50), lens=48.0, fstop=2.2)

        elif t < 18.50:
            # 2c: Vision gets blurry (recognizable optical bokeh blur!)
            u = (t - 17.30) / (18.50 - 17.30)
            sc.setup_stylized_sky_world(scene, "interior", 0.55)
            set_col_visible(town_col, False)
            set_col_visible(room["col"], True)
            set_col_visible(room["table_col"], False)
            set_col_visible(room["bed_col"], False)
            cf.set_char_transform(alex, 0.0, 0.0, 0.0, 0)
            cf.pose_char(alex, head_rot=(6, 0, -4), arm_l=(35, -10, 12), arm_r=(35, 10, -12))
            cf.set_face(alex, "alex_blurry_squint.png")
            sc.set_camera_look(cam, (0.0, 1.65 - 0.15 * u, 1.54), (0.0, 0.12, 1.50), lens=44.0, fstop=0.95, focus_dist=0.58)

        elif t < 20.15:
            # 2d: Eyes literally start burning! (Flames rise above eyes so burning eyes remain visible!)
            u = (t - 18.50) / (20.15 - 18.50)
            sc.setup_stylized_sky_world(scene, "night", 0.35)
            set_col_visible(town_col, False)
            set_col_visible(room["col"], True)
            set_col_visible(room["table_col"], False)
            set_col_visible(room["bed_col"], False)
            set_col_visible(props["eye_fx_col"], True)
            for ed in props["eye_drops"]:
                ed.hide_render = True
            for fi, ef in enumerate(props["eye_flames"]):
                ef.hide_render = False
                side = -0.075 if fi < 3 else 0.075
                k = fi % 3
                ef.location = (side + math.sin(t * 22.0 + fi) * 0.015, 0.22 + k * 0.02, 1.63 + k * 0.045 + abs(math.sin(t * 18.0 + k)) * 0.03)
            lights["key"][1].color = (1.0, 0.55, 0.25)
            lights["key"][1].energy = 320.0
            cf.set_char_transform(alex, 0.0, 0.0, 0.0, 0)
            cf.pose_char(alex, torso_rot=(-8, 0, 0), head_rot=(-10, 0, math.sin(t * 20.0) * 6.0), arm_l=(145, 0, 28), forearm_l=(20, 0, 0), arm_r=(145, 0, -28), forearm_r=(20, 0, 0))
            cf.set_face(alex, "alex_burning_eyes.png")
            sc.set_camera_look(cam, (0.0, 1.75 - 0.22 * u, 1.52), (0.0, 0.10, 1.48), lens=38.0, roll_deg=5.0, kick_offset=kick_off, kick_amp=0.06)

        # ---- WORLD 3: WATER / LIQUID TANK (20.15 - 28.86s) ----
        elif t < 23.62:
            # 3a: Pour clear liquid down throat
            u = (t - 20.15) / (23.62 - 20.15)
            sc.setup_stylized_sky_world(scene, "day", 0.65)
            set_col_visible(town_col, False)
            set_col_visible(room["col"], True)
            set_col_visible(room["table_col"], True)
            set_col_visible(room["bed_col"], False)
            set_col_visible(props["water_col"], True)
            cf.set_char_transform(alex, 0.0, 0.0, 0.0, 0)
            gulp_tilt = -26.0 - 6.0 * math.sin(t * 10.0)
            cf.pose_char(alex, head_rot=(gulp_tilt, 0, 0), arm_l=(110, -24, -10), forearm_l=(55, 0, 0), arm_r=(25, 0, -18))
            cf.set_face(alex, "alex_gulp_o.png")
            props["pitcher"].location = (0.28, 0.26, 1.78 + 0.02 * math.sin(t * 10.0))
            props["water_stream"].location = (0.08, 0.25, 1.57)
            sc.set_camera_look(cam, (-0.35 + 0.45 * u, 2.05 - 0.22 * u, 1.50), (0.0, 0.10, 1.42), lens=36.0)

        elif t < 25.54:
            # 3b: Character mostly made of liquid (75% Glass Water Tank Torso!)
            u = (t - 23.62) / (25.54 - 23.62)
            sc.setup_stylized_sky_world(scene, "day", 0.70)
            set_col_visible(town_col, False)
            set_col_visible(room["col"], True)
            set_col_visible(room["table_col"], False)
            set_col_visible(room["bed_col"], False)
            set_torso_visible(alex, False)
            set_col_visible(props["xray_col"], True)
            for lg in props["lungs"]:
                lg.hide_render = True
            props["acid_vat"].hide_render = True
            props["acid_food"].hide_render = True
            for ab in props["acid_bubbles"]:
                ab.hide_render = True
            props["water_fill"].hide_render = False
            props["water_fill"].scale = (1.0, 1.0, 1.0 + 0.06 * math.sin(t * 7.0))
            props["water_fill"].location = (0.0, 0.0, 0.90 + 0.015 * math.sin(t * 7.0))
            for n in props["m_water_fill"].node_tree.nodes:
                if n.type == "BSDF_PRINCIPLED":
                    n.inputs["Base Color"].default_value = (0.05, 0.65, 0.95, 1.0)
                    n.inputs["Emission Color"].default_value = (0.22, 0.74, 0.97, 1.0)
            cf.set_char_transform(alex, 0.0, 0.0, 0.0, 0)
            cf.pose_char(alex, arm_l=(20, 0, 18), arm_r=(20, 0, -18))
            cf.set_face_with_blink(alex, "alex_deadpan", f, 4)
            sc.set_camera_look(cam, (0.35 - 0.70 * u, 2.10, 1.24), (0.0, 0.0, 1.15), lens=36.0)

        elif t < 28.86:
            # 3c: Tank drains to 12% red danger + organs failing!
            u = (t - 25.54) / (28.86 - 25.54)
            sc.setup_stylized_sky_world(scene, "night", 0.38)
            set_col_visible(town_col, False)
            set_col_visible(room["col"], True)
            set_col_visible(room["table_col"], False)
            set_col_visible(room["bed_col"], False)
            set_torso_visible(alex, False)
            set_col_visible(props["xray_col"], True)
            for lg in props["lungs"]:
                lg.hide_render = True
            props["acid_vat"].hide_render = True
            props["acid_food"].hide_render = True
            for ab in props["acid_bubbles"]:
                ab.hide_render = True
            props["water_fill"].hide_render = False
            fill_lvl = max(0.18, 1.0 - 0.82 * u)
            props["water_fill"].scale = (1.0, 1.0, fill_lvl)
            props["water_fill"].location = (0.0, 0.0, 0.70 + 0.20 * fill_lvl)
            if u > 0.35:
                props["banner_lowh2o"].hide_render = False
                props["banner_lowh2o"].scale = (0.82, 0.82, 0.82)
                props["banner_lowh2o"].location = (0.0, -0.35, 2.15)
                lights["key"][1].color = (1.0, 0.45, 0.45)
                for n in props["m_water_fill"].node_tree.nodes:
                    if n.type == "BSDF_PRINCIPLED":
                        n.inputs["Base Color"].default_value = (0.94, 0.25, 0.25, 1.0)
                        n.inputs["Emission Color"].default_value = (0.94, 0.25, 0.25, 1.0)
            cf.set_char_transform(alex, 0.0, 0.0, 0.0, 0)
            cf.pose_char(alex, torso_rot=(12, 0, 0), arm_l=(55, -35, 0), forearm_l=(55, 0, 0), arm_r=(55, 35, 0), forearm_r=(55, 0, 0))
            cf.set_face(alex, "alex_almost_wobbly.png")
            sc.set_camera_look(cam, (0.0, 2.65 - 0.22 * u, 1.50), (0.0, 0.0, 1.44), lens=32.0, roll_deg=-4.0 * u, kick_offset=kick_off, kick_amp=0.05)

        # ---- WORLD 4: EATING / TINY ROCKS / STOMACH ACID (28.86 - 38.05s) ----
        elif t < 31.60:
            # 4a: Crush dead plants and animals at table
            u = (t - 28.86) / (31.60 - 28.86)
            sc.setup_stylized_sky_world(scene, "day", 0.68)
            set_col_visible(town_col, False)
            set_col_visible(room["col"], True)
            set_col_visible(room["table_col"], True)
            set_col_visible(room["bed_col"], False)
            set_col_visible(props["meal_col"], True)
            cf.set_char_transform(alex, 0.0, 0.0, 0.0, 0)
            cf.pose_char(alex, torso_rot=(8, 0, 0), arm_l=(62, -18, 0), forearm_l=(42, 0, 0), arm_r=(62, 18, 0), forearm_r=(42, 0, 0))
            cf.set_face_with_blink(alex, "alex_chewing", f, 5)
            sc.set_camera_look(cam, (-0.30 + 0.30 * u, 2.05 - 0.35 * u, 1.48), (0.0, 0.35, 1.15), lens=35.0)

        elif t < 33.22:
            # 4b: Tiny rocks in mouth CU (teeth chomping!)
            u = (t - 31.60) / (33.22 - 31.60)
            sc.setup_stylized_sky_world(scene, "day", 0.68)
            set_col_visible(town_col, False)
            set_col_visible(room["col"], True)
            set_col_visible(room["table_col"], True)
            set_col_visible(room["bed_col"], False)
            set_col_visible(props["meal_col"], True)
            cf.set_char_transform(alex, 0.0, 0.0, 0.0, 0)
            chomp = math.sin(t * 20.0) * 5.0
            cf.pose_char(alex, head_rot=(chomp, 0, 0), arm_l=(72, -22, 0), forearm_l=(55, 0, 0), arm_r=(72, 22, 0), forearm_r=(55, 0, 0))
            cf.set_face(alex, "alex_chewing.png")
            sc.set_camera_look(cam, (0.12 - 0.22 * u, 1.32 - 0.12 * u, 1.46), (0.0, 0.14, 1.42), lens=50.0, fstop=2.2)

        elif t < 36.44:
            # 4c: Stomach acid melts them down
            u = (t - 33.22) / (36.44 - 33.22)
            sc.setup_stylized_sky_world(scene, "night", 0.35)
            set_col_visible(town_col, False)
            set_col_visible(room["col"], True)
            set_col_visible(room["table_col"], False)
            set_col_visible(room["bed_col"], False)
            set_torso_visible(alex, False)
            set_col_visible(props["xray_col"], True)
            for lg in props["lungs"]:
                lg.hide_render = True
            props["water_fill"].hide_render = True
            props["acid_vat"].hide_render = False
            sc.set_hidden_tree(props["acid_food"], False)
            for bi, ab in enumerate(props["acid_bubbles"]):
                ab.hide_render = False
                ab.location = ((bi - 2.5) * 0.075, 0.06, 0.78 + ((t * 1.6 + bi * 0.2) % 0.28))
            melt_s = max(0.18, 0.65 * (1.0 - 0.72 * u))
            props["acid_food"].scale = (melt_s, melt_s, melt_s)
            props["acid_food"].location = (0.0, 0.02, 1.02 - 0.15 * u)
            props["acid_food"].rotation_euler = (t * 1.5, t * 2.1, 0)
            cf.set_char_transform(alex, 0.0, 0.0, 0.0, 0)
            cf.pose_char(alex, arm_l=(20, 0, 16), arm_r=(20, 0, -16))
            cf.set_face_with_blink(alex, "alex_smug", f, 6)
            sc.set_camera_look(cam, (0.0, 1.80 - 0.26 * u, 1.24), (0.0, 0.0, 1.12), lens=38.0)

        elif t < 38.05:
            # 4d: Turn into fuel -> keep walking around!
            u = (t - 36.44) / (38.05 - 36.44)
            sc.setup_stylized_sky_world(scene, "day", 0.75)
            set_col_visible(town_col, True)
            set_col_visible(room["col"], False)
            set_col_visible(props["bar_col"], True)
            wx = -0.5 + 1.0 * u
            cf.set_char_transform(alex, wx, 0.0, 0.0, -25)
            w = t * 10.0
            cf.pose_char(alex, pelvis_z=abs(math.sin(w)) * 0.06, torso_rot=(6, 0, 0), arm_l=(math.sin(w) * 35, 0, 10), arm_r=(-math.sin(w) * 35, 0, -10), leg_l=(-math.sin(w) * 28, 0, 0), leg_r=(math.sin(w) * 28, 0, 0))
            cf.set_face(alex, "alex_smug.png")
            props["bar_bg"].location = (wx, 0.08, 2.04)
            fill_w = min(1.0, 0.3 + 0.7 * u)
            props["bar_fill"].scale = (fill_w, 1.0, 1.0)
            props["bar_fill"].location = (wx + 0.34 * (1.0 - fill_w), 0.11, 2.04)
            for n in props["m_bar_fill"].node_tree.nodes:
                if n.type == "BSDF_PRINCIPLED":
                    n.inputs["Base Color"].default_value = (0.04, 0.55, 0.15, 1.0)
                    n.inputs["Emission Color"].default_value = (0.05, 0.75, 0.20, 1.0)
            sc.set_camera_look(cam, (wx + 0.35, 2.45 - 0.3 * u, 1.44), (wx, 0.0, 1.38), lens=34.0)

        # ---- WORLD 5: SLEEP / HALLUCINATE / BREAKDOWN (38.05 - 50.87s) ----
        elif t < 42.13:
            # 5a: Lie down in dark room, go unconscious (head cleanly on pillow!)
            u = (t - 38.05) / (42.13 - 38.05)
            sc.setup_stylized_sky_world(scene, "night", 0.28)
            set_col_visible(town_col, False)
            set_col_visible(room["col"], True)
            set_col_visible(room["table_col"], False)
            set_col_visible(room["bed_col"], True)
            lights["key"][1].energy = 140.0 * (1.0 - 0.35 * u)
            lights["key"][1].color = (0.65, 0.75, 1.0)
            cf.set_char_transform(alex, 0.0, 0.90, 0.70, 0)
            alex["arm"].rotation_euler = (math.radians(90), 0, 0)
            cf.pose_char(alex, arm_l=(8, 0, 10), arm_r=(8, 0, -10))
            cf.set_face(alex, "alex_sleep_closed.png")
            sc.set_camera_look(cam, (-0.50 + 0.95 * u, 1.40 - 0.22 * u, 1.88), (0.0, -0.58, 0.80), lens=34.0)

        elif t < 45.37:
            # 5b: Hallucinate 8 hours straight (psychedelic floating dream props above sleeping Alex!)
            u = (t - 42.13) / (45.37 - 42.13)
            sc.setup_stylized_sky_world(scene, "dream", 0.65)
            set_col_visible(town_col, False)
            set_col_visible(room["col"], True)
            set_col_visible(room["table_col"], False)
            set_col_visible(room["bed_col"], True)
            set_col_visible(props["dream_col"], True)
            lights["key"][1].color = (0.85, 0.45, 1.0)
            lights["key"][1].energy = 240.0
            lights["rim"][1].color = (0.20, 0.90, 1.0)
            lights["rim"][1].energy = 380.0
            cf.set_char_transform(alex, 0.0, 0.90, 0.70, 0)
            alex["arm"].rotation_euler = (math.radians(90), 0, 0)
            cf.set_face(alex, "alex_sleep_closed.png")
            props["d_eye"].location = (-0.42 + 0.10 * math.sin(t * 2.5), 0.15, 1.32 + 0.10 * math.cos(t * 3.0))
            props["d_eye"].rotation_euler = (0, 0, math.sin(t * 2.0) * 0.4)
            props["d_burger"].location = (0.44, 0.20, 1.38 + 0.12 * math.sin(t * 3.2))
            props["d_burger"].rotation_euler = (t * 1.4, t * 2.2, 0)
            props["d_cat"].location = (0.0, -0.10, 1.60 + 0.10 * math.sin(t * 4.0))
            props["d_cat"].rotation_euler = (0, 0, t * 2.0)
            for si, st in enumerate(props["d_stars"]):
                ang = si * (math.pi / 3.0) + t * 2.5
                st.location = (math.cos(ang) * 0.58, 0.15, 1.42 + math.sin(ang) * 0.28)
            sc.set_camera_look(cam, (0.0, 2.05 - 0.30 * u, 1.68), (0.0, -0.25, 1.12), lens=32.0, roll_deg=7.5 * math.sin(u * math.pi))

        elif t < 47.57:
            # 5c: Brain stops saving data (exhausted upright in bed + visible Floppy + SAVE FAILED clearly above head!)
            u = (t - 45.37) / (47.57 - 45.37)
            sc.setup_stylized_sky_world(scene, "day", 0.65)
            set_col_visible(town_col, False)
            set_col_visible(room["col"], True)
            set_col_visible(room["table_col"], False)
            set_col_visible(room["bed_col"], True)
            set_col_visible(props["floppy_col"], True)
            props["banner_savefail"].hide_render = False
            props["banner_savefail"].scale = (0.82, 0.82, 0.82)
            props["banner_savefail"].location = (0.0, -0.45, 2.68)
            for obj in props["floppy_col"].objects:
                obj.rotation_euler = (0, 0, math.sin(t * 4.0) * 0.45)
                obj.location = (0.48, 0.10, 1.65 + 0.05 * math.sin(t * 6.0))
            cf.set_char_transform(alex, -0.20, -0.35, 0.49, 0)
            cf.pose_char(alex, torso_rot=(8, 0, 0), head_rot=(-4, 0, 0), arm_l=(30, 0, 15), arm_r=(30, 0, -15), leg_l=(-88, 0, 0), leg_r=(-88, 0, 0))
            cf.set_face(alex, "alex_exhausted_bags.png")
            sc.set_camera_look(cam, (0.0, 2.65 - 0.20 * u, 1.78), (0.0, -0.35, 1.75), lens=32.0, kick_offset=kick_off, kick_amp=0.05)

        elif t < 49.11:
            # 5d: Stamina bar hits zero!
            u = (t - 47.57) / (49.11 - 47.57)
            sc.setup_stylized_sky_world(scene, "interior", 0.50)
            set_col_visible(town_col, False)
            set_col_visible(room["col"], True)
            set_col_visible(room["table_col"], False)
            set_col_visible(room["bed_col"], False)
            set_col_visible(props["bar_col"], True)
            props["bar_bg"].location = (0.0, 0.08, 1.98)
            rem = max(0.08, 0.85 * (1.0 - u))
            props["bar_fill"].scale = (rem, 1.0, 1.0)
            props["bar_fill"].location = (0.34 * (1.0 - rem), 0.11, 1.98)
            for n in props["m_bar_fill"].node_tree.nodes:
                if n.type == "BSDF_PRINCIPLED":
                    n.inputs["Base Color"].default_value = (0.78, 0.03, 0.03, 1.0)
                    n.inputs["Emission Color"].default_value = (0.85, 0.03, 0.03, 1.0)
            cf.set_char_transform(alex, 0.0, 0.0, 0.0, 0)
            cf.pose_char(alex, pelvis_z=-0.08 * u, torso_rot=(18 * u, 0, 0), head_rot=(10 * u, 0, 0), arm_l=(15, 0, 12), arm_r=(15, 0, -12))
            cf.set_face(alex, "alex_exhausted_bags.png")
            sc.set_camera_look(cam, (0.0, 2.15 - 0.25 * u, 1.48), (0.0, 0.0, 1.42), lens=35.0)

        else:
            # 5e: Character starts breaking down (glitch jitter + collapse cleanly centered!)
            u = min(1.0, (t - 49.11) / max(0.2, beats_data["total_duration"] - 49.11))
            sc.setup_stylized_sky_world(scene, "night", 0.32)
            set_col_visible(town_col, False)
            set_col_visible(room["col"], True)
            set_col_visible(room["table_col"], False)
            set_col_visible(room["bed_col"], False)
            lights["key"][1].color = (1.0, 0.35, 0.35)
            lights["key"][1].energy = 280.0
            fall_ang = -38.0 * min(1.0, u * 1.25)
            jit = math.sin(t * 55.0) * 14.0
            cf.set_char_transform(alex, 0.0, 0.0, 0.18 * min(1.0, u * 1.2), jit * 0.3)
            alex["arm"].rotation_euler = (math.radians(fall_ang), math.radians(jit * 0.4), math.radians(12))
            cf.pose_char(alex, torso_rot=(0, jit, 0), head_rot=(jit, -jit, 0), arm_l=(40 + jit, 0, 42), arm_r=(35 - jit, 0, -42))
            cf.set_face(alex, "alex_glitch_dead.png")
            sc.set_camera_look(cam, (0.20, 2.75 - 0.20 * u, 1.55 - 0.10 * u), (0.0, 0.0, 1.05), lens=32.0, roll_deg=-7.0 * u, kick_offset=kick_off, kick_amp=0.07)

        if preview_only:
            sc.render_frame(scene, f, preview_tag=f"prev_{f:04d}")
        else:
            sc.render_frame(scene, f)
            if f % 100 == 0:
                print(f"  Rendered frame {f}/{total_frames} ({f * 100 // total_frames}%)")


if __name__ == "__main__":
    main()
