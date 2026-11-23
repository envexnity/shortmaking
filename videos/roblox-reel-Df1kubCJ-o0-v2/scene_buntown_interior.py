"""
scene_buntown_interior.py — Set 4: Bun Town Diner Interior (True SI Scale 1 BU = 1m).
Glossy cream ceramic floor tiles, teal-and-cream logo counter, glass kitchen pass-through,
fabric pennant bunting, wrapped clipboard & tie gag, 22-person midnight crowd rush,
26 arcing flying burgers, diegetic 3D LED 7-segment burger scoreboard (001 -> 400),
stunned Mayor close-up, and colossal wrapped-burger wall finale!

Renders beats:
  b26_interview, b27_one_burger, b28_whenever, b29_already_wrap, b30_clipboard_tie,
  b31_impressed, b32_one_question, b33_never_cooked, b42_hired, b43_already_start,
  b45_midnight_rush, b46_one_of_me, b47_huss_climax, b48_400_burgers,
  b49_mayor_stared, b50_final_callback, b51_final_huss.
"""
import math
import random
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

PROJ_DIR = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking\videos\roblox-reel-Df1kubCJ-o0-v2")
sys.path.insert(0, str(PROJ_DIR))
import scene_common as sc
import char_factory as cf
import props_factory as pf
import blender_cinema_lib as bcl


def _make_uv_plane(name: str, loc, w: float, h: float, mat, col):
    bm = bmesh.new()
    v0 = bm.verts.new(( w * 0.5, 0.0, -h * 0.5))
    v1 = bm.verts.new((-w * 0.5, 0.0, -h * 0.5))
    v2 = bm.verts.new((-w * 0.5, 0.0,  h * 0.5))
    v3 = bm.verts.new(( w * 0.5, 0.0,  h * 0.5))
    f = bm.faces.new((v0, v1, v2, v3))
    uv = bm.loops.layers.uv.new("UVMap")
    for lp, uvc in zip(f.loops, [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]):
        lp[uv].uv = uvc
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    o = bpy.data.objects.new(name, mesh)
    o.location = loc
    col.objects.link(o)
    o.data.materials.append(mat)
    return o


SEG_MAP = {
    0: (1, 1, 1, 1, 1, 1, 0),
    1: (0, 1, 1, 0, 0, 0, 0),
    2: (1, 1, 0, 1, 1, 0, 1),
    3: (1, 1, 1, 1, 0, 0, 1),
    4: (0, 1, 1, 0, 0, 1, 1),
    5: (1, 0, 1, 1, 0, 1, 1),
    6: (1, 0, 1, 1, 1, 1, 1),
    7: (1, 1, 1, 0, 0, 0, 0),
    8: (1, 1, 1, 1, 1, 1, 1),
    9: (1, 1, 1, 1, 0, 1, 1),
}


def build_3d_scoreboard(name: str, loc, col):
    """Diegetic 3D wall-mounted LED 3-digit counter (001 -> 400) facing +Y camera."""
    root = bpy.data.objects.new(name, None)
    root.location = loc
    col.objects.link(root)

    m_case = sc.make_stylized_pbr("Mat_SB_Case", "#111827", rough=0.35, metal=0.4)
    m_trim = sc.make_stylized_pbr("Mat_SB_Trim", "#FACC15", rough=0.25, metal=0.6)
    m_led = sc.make_stylized_pbr("Mat_SB_LED", "#FFE600", emit_hex="#FFE600", emit_str=7.5)

    pf.make_bevel_box(f"{name}_Frame", (0, 0, 0), (1.36, 0.10, 0.56), m_case, col, bevel_w=0.015, parent=root)
    pf.make_bevel_box(f"{name}_Border", (0, 0.01, 0), (1.30, 0.09, 0.50), m_trim, col, bevel_w=0.01, parent=root)
    pf.make_bevel_box(f"{name}_Face", (0, 0.025, 0), (1.20, 0.08, 0.42), m_case, col, bevel_w=0.008, parent=root)

    # 3 digits placed left-to-right from +Y camera (hundreds at +X, tens at 0, ones at -X!)
    digits = []
    # 7-segment coords (x_off, z_off, is_horiz) relative to digit center
    # a=top, b=top-right(-X), c=bot-right(-X), d=bot, e=bot-left(+X), f=top-left(+X), g=mid
    seg_geom = [
        (0.0,   0.13, True),   # a
        (-0.08, 0.065, False), # b
        (-0.08,-0.065, False), # c
        (0.0,  -0.13, True),   # d
        (0.08, -0.065, False), # e
        (0.08,  0.065, False), # f
        (0.0,   0.0, True),    # g
    ]
    for di, dx in enumerate((0.32, 0.0, -0.32)):
        segs = []
        for si, (ox, oz, horiz) in enumerate(seg_geom):
            sc_xyz = (0.14, 0.025, 0.032) if horiz else (0.032, 0.025, 0.12)
            s_obj = pf.make_bevel_box(f"{name}_D{di}_S{si}", (dx + ox, 0.068, oz), sc_xyz, m_led, col, bevel_w=0.004, segs=1, parent=root)
            segs.append(s_obj)
        digits.append(segs)
    return {"root": root, "digits": digits}


def set_scoreboard_value(sb: dict, val: int):
    v = max(0, min(999, int(val)))
    ds = [v // 100, (v // 10) % 10, v % 10]
    for d_idx, d_val in enumerate(ds):
        mask = SEG_MAP[d_val]
        for s_idx, on in enumerate(mask):
            obj = sb["digits"][d_idx][s_idx]
            obj.hide_viewport = not on
            obj.hide_render = not on


def build_interior_set(scene):
    col = bpy.data.collections.new("Set_BunTownInt")
    scene.collection.children.link(col)

    m_floor = sc.make_textured_pbr("Mat_IntFloor", sc.TEX_ENV / "tile_cream_diner.png", sc.TEX_ENV / "tile_cream_diner_bump.png", uv_scale=(0.80, 0.80, 0.80), rough_min=0.30, rough_max=0.45, coat=0.14)
    m_wall = sc.make_stylized_pbr("Mat_IntWall", "#FAF0DE", rough=0.68, coat=0.0, bump_str=0.02)
    m_teal = sc.make_stylized_pbr("Mat_IntTeal", "#0D9488", rough=0.42, coat=0.12)
    m_cream = sc.make_stylized_pbr("Mat_IntCream", "#FBF6EC", rough=0.35, coat=0.14)
    m_steel = sc.make_stylized_pbr("Mat_IntSteel", "#CBD5E1", rough=0.24, metal=0.85)
    m_wood = sc.make_stylized_pbr("Mat_IntWood", "#92400E", rough=0.58, coat=0.0)
    m_wht = sc.make_stylized_pbr("Mat_IntWht", "#F8FAFC", rough=0.55, coat=0.0)
    m_glass = sc.make_stylized_pbr("Mat_IntGlass", "#E0F2FE", rough=0.08, coat=0.40, alpha=0.22)
    m_wrap_y = sc.make_stylized_pbr("Mat_IntWrapY", "#ECAE20", rough=0.52, coat=0.0)
    m_wrap_r = sc.make_stylized_pbr("Mat_IntWrapR", "#D42A18", rough=0.48, coat=0.0)

    # Diner Shell (Floor z=0, Counter y=0, Kitchen back y=-2.8, Front entrance y=+5.2)
    pf.make_bevel_box("Floor", (0, 1.2, -0.10), (11.0, 10.5, 0.20), m_floor, col, bevel_w=0.01)
    pf.make_bevel_box("Wall_Back", (0, -3.2, 2.0), (11.0, 0.25, 4.2), m_wall, col)
    pf.make_bevel_box("Wall_L", (-4.8, 1.2, 2.0), (0.25, 10.5, 4.2), m_wall, col)
    pf.make_bevel_box("Wall_R", ( 4.8, 1.2, 2.0), (0.25, 10.5, 4.2), m_wall, col)
    pf.make_bevel_box("Ceiling", (0, 1.2, 3.85), (11.0, 10.5, 0.20), m_wht, col)
    # Front windowed wall behind camera for reflections & b45 crowd entry
    pf.make_bevel_box("Wall_FrontL", (-3.2, 5.4, 2.0), (3.4, 0.25, 4.2), m_wall, col)
    pf.make_bevel_box("Wall_FrontR", ( 3.2, 5.4, 2.0), (3.4, 0.25, 4.2), m_wall, col)
    pf.make_bevel_box("Front_Glass", (0.0, 5.4, 1.5), (3.2, 0.06, 2.9), m_glass, col)
    # Teal architectural wainscoting stripe along all walls
    pf.make_bevel_box("TealStripe_B", (0, -3.06, 2.50), (10.6, 0.06, 0.22), m_teal, col, bevel_w=0.01)
    pf.make_bevel_box("TealStripe_L", (-4.66, 1.2, 2.50), (0.06, 10.2, 0.22), m_teal, col, bevel_w=0.01)
    pf.make_bevel_box("TealStripe_R", ( 4.66, 1.2, 2.50), (0.06, 10.2, 0.22), m_teal, col, bevel_w=0.01)

    # Framed Bun Town Wall Art on Back/Side Walls
    m_art = sc.make_textured_pbr("Mat_WallArt", sc.TEX_PROPS / "wall_burger_frame.png", proj="UV", rough_min=0.40, rough_max=0.50, coat=0.0, ao_str=0.04)
    for ax, ay, az in [(-1.85, -3.02, 2.10), (1.85, -3.02, 2.10)]:
        pf.make_bevel_box(f"ArtFrame_{ax}", (ax, ay - 0.02, az), (0.72, 0.05, 0.72), m_teal, col, bevel_w=0.01)
        _make_uv_plane(f"ArtCanvas_{ax}", (ax, ay + 0.02, az), 0.60, 0.60, m_art, col)

    # Glass-and-Steel Kitchen Pass-Through Shelf behind Counter (y = -1.45, z = 1.50)!
    pf.make_bevel_box("PassThrough_Frame", (0, -1.50, 1.55), (5.2, 0.14, 0.06), m_steel, col, bevel_w=0.008)
    pf.make_bevel_box("PassThrough_Low", (0, -1.50, 0.92), (5.2, 0.45, 0.06), m_steel, col, bevel_w=0.008)
    for px in (-2.4, -0.8, 0.8, 2.4):
        pf.make_smooth_cyl(f"PassPost_{px}", (px, -1.50, 1.25), 0.032, 0.65, m_steel, col, segs=16, bevel_w=0.004)
    for sx in (-1.6, -0.45, 0.45, 1.6):
        pf.build_wrapped_burger(f"ShelfWB_{sx}", (sx, -1.48, 1.58), col, scale=0.88)
        pf.build_wrapped_burger(f"ShelfWB_L_{sx}", (sx, -1.48, 0.96), col, scale=0.88)

    # Colorful Ceiling Fabric Triangular Bunting Flags!
    bunt_cols = ["#0D9488", "#FACC15", "#EF4444", "#38BDF8"]
    for bi in range(13):
        bx = -3.3 + bi * 0.55
        bm_f = bmesh.new()
        bmesh.ops.create_cone(bm_f, cap_ends=True, cap_tris=False, segments=3, radius1=0.18, radius2=0.01, depth=0.34)
        for v in bm_f.verts:
            v.co.y *= 0.25
        pf._finish_bm(bm_f, f"Bunt_{bi}", (bx, 0.95, 2.85), sc.make_stylized_pbr(f"Mat_Bunt_{bunt_cols[bi % 4]}", bunt_cols[bi % 4], rough=0.58, coat=0.0, sheen=0.35), col, rot=(math.radians(180), 0, 0))

    # ==================== ICONIC BUN TOWN SERVICE COUNTER (y = 0.0, top at z = 0.78m) ====================
    pf.make_bevel_box("Counter_Base", (0, 0.0, 0.36), (6.0, 0.84, 0.72), m_teal, col, bevel_w=0.018, segs=3)
    pf.make_bevel_box("Counter_Top",  (0, 0.0, 0.75), (6.15, 0.96, 0.08), m_cream, col, bevel_w=0.016, segs=3)
    pf.make_bevel_box("Counter_Trim", (0, 0.43, 0.58), (6.04, 0.04, 0.07), m_wht, col, bevel_w=0.006)
    pf.make_smooth_cyl("Counter_Medallion", (-0.48, 0.44, 0.36), 0.29, 0.04, m_teal, col, segs=32, rot=(math.radians(90), 0, 0), bevel_w=0.01)
    m_logo = sc.make_textured_pbr("Mat_CounterLogo", sc.TEX_PROPS / "buntown_logo_circle.png", proj="UV", rough_min=0.28, rough_max=0.38, coat=0.0, emit_str=0.04, ao_str=0.02, alpha_clip=True)
    _make_uv_plane("Counter_LogoPlane", (-0.48, 0.466, 0.36), 0.54, 0.54, m_logo, col)

    # Ketchup & Mustard Squeeze Bottles
    for bx, col_h in [(0.75, "#DC2626"), (0.94, "#FACC15")]:
        m_c = sc.make_stylized_pbr(f"Mat_Cond_{col_h}", col_h, rough=0.26, coat=0.30)
        pf.make_smooth_cyl(f"CondBtl_{col_h}", (bx, 0.25, 0.89), 0.055, 0.20, m_c, col, segs=20, bevel_w=0.01)
        pf.make_smooth_cyl(f"CondCap_{col_h}", (bx, 0.25, 1.02), 0.048, 0.08, m_c, col, segs=18, bevel_w=0.0, r2=0.01)

    # Counter Interview Props: Hero Burger, Wrapped Burger, Normal Clipboard, Wrapped Clipboard!
    c_burger = pf.build_hero_burger("Counter_Burger", (-0.22, 0.16, 0.79), col, scale=1.02)
    c_wrapped = pf.build_wrapped_burger("Counter_WrappedBurger", (-0.22, 0.16, 0.79), col, scale=1.04)

    clip_norm = bpy.data.objects.new("Prop_ClipNormal", None)
    clip_norm.location = (0.36, 0.14, 0.795)
    col.objects.link(clip_norm)
    pf.make_bevel_box("ClipWood", (0, 0, 0.012), (0.28, 0.38, 0.022), m_wood, col, bevel_w=0.005, parent=clip_norm)
    pf.make_bevel_box("ClipPaper", (0, -0.01, 0.026), (0.24, 0.32, 0.008), m_wht, col, bevel_w=0.002, parent=clip_norm)
    pf.make_bevel_box("ClipMetal", (0, 0.17, 0.032), (0.12, 0.04, 0.016), m_steel, col, bevel_w=0.004, parent=clip_norm)

    clip_wrap = bpy.data.objects.new("Prop_ClipWrapped", None)
    clip_wrap.location = (0.36, 0.14, 0.795)
    col.objects.link(clip_wrap)
    pf.make_bevel_box("ClipWrapY", (0, 0, 0.018), (0.32, 0.42, 0.038), m_wrap_y, col, bevel_w=0.010, parent=clip_wrap)
    pf.make_bevel_box("ClipWrapR", (0, 0, 0.022), (0.325, 0.055, 0.040), m_wrap_r, col, bevel_w=0.004, parent=clip_wrap)

    # Animated POV Wrap Sheet on counter for Alex's climax wrap
    pov_sheet = pf.build_animated_wrap_sheet("Counter_POVSheet", (0.0, 0.14, 0.794), col, scale=1.05)

    # Colossal Multi-Column Wall of Wrapped Burgers on Counter framing Alex cleanly on both sides for b50!
    wall_burgers = []
    for col_x in (0.44, 0.78, -0.56, -0.88):
        for row_z in range(10):
            wb = pf.build_wrapped_burger(f"FinalWall_{col_x:.2f}_{row_z}", (col_x, 0.12, 0.79 + row_z * 0.140), col, scale=0.88)
            wall_burgers.append(wb)

    # 26 Flying Wrapped Burgers for b48_400_burgers ("400 burgers. One minute.")
    flying_burgers = []
    rng = random.Random(77)
    for fi in range(26):
        wb = pf.build_wrapped_burger(f"FlyWB_{fi}", (0, 0, 1.1), col, scale=0.92)
        flying_burgers.append((
            wb,
            rng.uniform(-2.6, 2.6),
            rng.uniform(1.1, 4.2),
            rng.uniform(0.45, 0.95),
            rng.uniform(0.0, 1.0),
        ))

    # Diegetic 3D LED Burger Scoreboard mounted on upper back wall!
    scoreboard = build_3d_scoreboard("SB_400", (0.0, -3.02, 2.34), col)

    # Balanced Stylized Diner Lighting (prevents white-wall GI washout; keeps faces & black eyes crisp!)
    sc.setup_stylized_sky_world(scene, "interior", strength=0.14)
    for nm, loc, tgt, en, sz, temp, spr in [
        ("Int_KeyFront",  (0.4, 2.2, 2.75), (0.0, -0.3, 1.25), 115.0, 3.2, 4600, 82),
        ("Int_CrowdFill", (0.0, 4.5, 3.35), (0.0, 2.2, 1.0),   130.0, 4.5, 4800, 95),
        ("Int_RimBack",   (0.0, -2.5, 2.95), (0.0, 0.0, 1.35), 210.0, 3.0, 7200, 68),
    ]:
        ld = bpy.data.lights.new(nm, type="AREA")
        ld.energy = en
        ld.size = sz
        ld.spread = math.radians(spr)
        ld.use_temperature = True
        ld.temperature = temp
        lo = bpy.data.objects.new(nm, ld)
        col.objects.link(lo)
        lo.location = loc
        lo.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()

    return {
        "c_burger": c_burger,
        "c_wrapped": c_wrapped,
        "clip_norm": clip_norm,
        "clip_wrap": clip_wrap,
        "pov_sheet": pov_sheet,
        "wall_burgers": wall_burgers,
        "flying_burgers": flying_burgers,
        "scoreboard": scoreboard,
    }


def main():
    preview_only = "--preview" in sys.argv
    bcl.clear_scene()
    scene = bpy.context.scene
    res = (1080, 1920) if preview_only else (720, 1280)
    sc.configure_stylized_eevee(scene, res_x=res[0], res_y=res[1], samples=(16 if preview_only else 12), raytracing=True, fast_gi=True, motion_blur=False, exposure=-0.34)

    beats_data = sc.load_beats()
    props = build_interior_set(scene)

    cast_col = bpy.data.collections.new("Int_Cast")
    scene.collection.children.link(cast_col)

    alex = cf.create_character("alex", "Alex", cast_col)
    manager = cf.create_character("manager", "Manager", cast_col)
    mayor = cf.create_character("mayor", "Mayor", cast_col)

    # 22 Party-Hatted Hungry Crowd Characters for Midnight 400-Person Rush!
    rush_crowd = []
    rng = random.Random(99)
    kinds = ["teal_friend", "grandma", "mint_girl", "rock_guy", "purple_hoodie", "neighbor"]
    hats = ["#EC4899", "#FACC15", "#38BDF8", "#A855F7", "#22C55E", "#EF4444"]
    for ri in range(22):
        kd = kinds[ri % len(kinds)]
        ht = hats[ri % len(hats)] if kd != "neighbor" else None
        rc = cf.create_character(kd, f"Rush_{ri}", cast_col, party_hat=ht)
        col_i = ri % 5
        row_i = ri // 5
        rx = -1.65 + col_i * 0.82 + rng.uniform(-0.10, 0.10)
        ry = 1.05 + row_i * 0.60 + rng.uniform(-0.08, 0.08)
        cf.set_char_transform(rc, rx, ry, 0.0, 180.0 + rng.uniform(-16, 16))
        rush_crowd.append((rc, rx, ry, ri * 0.65))

    cam_d = bpy.data.cameras.new("Cam_Int")
    cam = bpy.data.objects.new("Cam_Int", cam_d)
    scene.collection.objects.link(cam)
    scene.camera = cam

    bcl.setup_cinema_compositor(
        scene, glare_threshold=2.0, glare_strength=0.08, dispersion=0.0008,
        lift_rgb=(0.992, 0.995, 1.005), gamma_rgb=(1.0, 1.0, 1.0), gain_rgb=(1.01, 1.01, 0.99),
        vignette=0.12,
    )

    int_beats = [
        "b26_interview", "b27_one_burger", "b28_whenever", "b29_already_wrap",
        "b30_clipboard_tie", "b31_impressed", "b32_one_question", "b33_never_cooked",
        "b42_hired", "b43_already_start", "b45_midnight_rush", "b46_one_of_me",
        "b47_huss_climax", "b48_400_burgers", "b49_mayor_stared",
        "b50_final_callback", "b51_final_huss",
    ]
    preview_keep = {"b30_clipboard_tie", "b45_midnight_rush", "b48_400_burgers", "b49_mayor_stared", "b50_final_callback", "b51_final_huss"}

    for bid in int_beats:
        binfo = sc.beat_info(beats_data, bid)
        f0, f1 = sc.beat_frame_range(beats_data, bid)
        is_huss = "huss" in bid

        # Visibility toggles per beat
        show_mgr = bid in ("b27_one_burger", "b28_whenever", "b29_already_wrap", "b30_clipboard_tie", "b31_impressed", "b32_one_question", "b42_hired")
        show_alex = bid in ("b26_interview", "b33_never_cooked", "b43_already_start", "b46_one_of_me", "b47_huss_climax", "b48_400_burgers", "b50_final_callback", "b51_final_huss")
        show_mayor = bid in ("b45_midnight_rush", "b48_400_burgers", "b49_mayor_stared")
        show_crowd = bid in ("b45_midnight_rush", "b48_400_burgers", "b49_mayor_stared")

        sc.set_hidden_tree(manager["arm"], not show_mgr)
        sc.set_hidden_tree(alex["arm"], not show_alex)
        sc.set_hidden_tree(mayor["arm"], not show_mayor)
        for ri, (rc, _, _, _) in enumerate(rush_crowd):
            sc.set_hidden_tree(rc["arm"], not (show_crowd and (bid != "b49_mayor_stared" or ri < 6)))

        wrap_b = bid in ("b29_already_wrap", "b30_clipboard_tie", "b31_impressed", "b32_one_question", "b42_hired", "b43_already_start", "b48_400_burgers")
        wrap_c = bid in ("b30_clipboard_tie", "b31_impressed", "b32_one_question")
        wrap_t = bid in ("b30_clipboard_tie", "b31_impressed", "b32_one_question")

        sc.set_hidden_tree(props["c_burger"], wrap_b or bid in ("b45_midnight_rush", "b47_huss_climax", "b49_mayor_stared", "b50_final_callback", "b51_final_huss"))
        sc.set_hidden_tree(props["c_wrapped"], (not wrap_b) or bid in ("b45_midnight_rush", "b47_huss_climax", "b49_mayor_stared", "b50_final_callback", "b51_final_huss"))
        sc.set_hidden_tree(props["clip_norm"], wrap_c or (not show_mgr))
        sc.set_hidden_tree(props["clip_wrap"], (not wrap_c) or (not show_mgr))

        if show_mgr:
            manager["extras"]["tie_wrapped"].hide_viewport = not wrap_t
            manager["extras"]["tie_wrapped"].hide_render = not wrap_t
            manager["extras"]["tie_wrap_stripe"].hide_viewport = not wrap_t
            manager["extras"]["tie_wrap_stripe"].hide_render = not wrap_t
            manager["extras"]["tie_blade"].hide_viewport = wrap_t
            manager["extras"]["tie_blade"].hide_render = wrap_t
        else:
            manager["extras"]["tie_wrapped"].hide_viewport = True
            manager["extras"]["tie_wrapped"].hide_render = True
            manager["extras"]["tie_wrap_stripe"].hide_viewport = True
            manager["extras"]["tie_wrap_stripe"].hide_render = True
            manager["extras"]["tie_blade"].hide_viewport = True
            manager["extras"]["tie_blade"].hide_render = True

        sc.set_hidden_tree(alex["arm"], not show_alex)
        if show_alex:
            cf.set_pov_arms_only(alex, bid == "b51_final_huss")

        sc.set_hidden_tree(props["pov_sheet"]["root"], bid not in ("b43_already_start", "b46_one_of_me", "b47_huss_climax", "b50_final_callback", "b51_final_huss"))
        for wb in props["wall_burgers"]:
            sc.set_hidden_tree(wb, bid not in ("b48_400_burgers", "b50_final_callback", "b51_final_huss"))
        for wb, _, _, _, _ in props["flying_burgers"]:
            sc.set_hidden_tree(wb, bid != "b48_400_burgers")
        sc.set_hidden_tree(props["scoreboard"]["root"], bid != "b48_400_burgers")

        huss_frames = [int(round(ht * 30.0)) + 1 for ht in binfo.get("huss_hit_times", [])]

        frames_to_render = [(f0 + f1) // 2] if preview_only else list(range(f0, f1 + 1))
        for f in frames_to_render:
            if preview_only and bid not in preview_keep:
                continue
            u = (f - f0) / max(1, (f1 - f0))
            t = f / 30.0

            kick_off = -1
            if is_huss and huss_frames:
                diffs = [f - hf for hf in huss_frames if f >= hf]
                if diffs:
                    kick_off = min(diffs)

            if bid == "b26_interview":
                cf.set_char_transform(alex, 0.0, 1.75 - 0.55 * u, 0.0, 180.0)
                cf.set_face_with_blink(alex, "alex_determined", f, seed=31)
                step = math.sin(t * 10.0)
                cf.pose_char(alex, arm_l=(20 * step, 0, -8), forearm_l=(15, 0, 0), arm_r=(-20 * step, 0, 8), forearm_r=(15, 0, 0), leg_l=(22 * step, 0, 0), leg_r=(-22 * step, 0, 0))
                sc.set_camera_look(cam, (0.35, 4.1 - 0.45 * u, 1.38), (0.0, 0.5, 1.15), lens=34.0, fstop=3.4)

            elif bid in ("b27_one_burger", "b28_whenever", "b29_already_wrap", "b30_clipboard_tie", "b31_impressed", "b32_one_question", "b42_hired"):
                cf.set_char_transform(manager, 0.0, -0.78, 0.0, 0.0)
                if bid in ("b27_one_burger", "b28_whenever"):
                    cf.set_face_with_blink(manager, "manager_happy_welcome", f, seed=32)
                    cf.pose_char(manager, head_rot=(4, 0, 0), arm_l=(40, 14, -22), forearm_l=(20, 0, 0), arm_r=(40, -14, 22), forearm_r=(20, 0, 0))
                elif bid in ("b29_already_wrap", "b30_clipboard_tie"):
                    cf.set_face(manager, "manager_shocked_o.png")
                    cf.pose_char(manager, head_rot=(-4, 0, 0), arm_l=(58, -6, -16), forearm_l=(22, 0, 0), arm_r=(58, 6, 16), forearm_r=(22, 0, 0))
                elif bid == "b31_impressed":
                    cf.set_face(manager, "manager_suspicious_squint.png")
                    cf.pose_char(manager, head_rot=(4, 0, -6), arm_l=(36, -10, -6), forearm_l=(18, 0, 0), arm_r=(36, 10, 6), forearm_r=(18, 0, 0))
                elif bid == "b32_one_question":
                    cf.set_face(manager, "manager_stern_question.png")
                    cf.pose_char(manager, head_rot=(6, 0, 0), arm_l=(62, -14, -10), forearm_l=(28, 0, 0), arm_r=(20, 6, 8), forearm_r=(18, 0, 0))
                elif bid == "b42_hired":
                    cf.set_face(manager, "manager_thrilled_hired.png")
                    cf.pose_char(manager, pelvis_z=0.04 * abs(math.sin(t * 9.0)), arm_l=(132, 0, -22), forearm_l=(24, 0, 0), arm_r=(132, 0, 22), forearm_r=(24, 0, 0))

                if bid == "b27_one_burger":
                    sc.set_camera_look(cam, (-0.18, 1.45 - 0.16 * u, 1.15), (-0.16, 0.16, 0.88), lens=44.0, fstop=2.8)
                elif bid == "b30_clipboard_tie":
                    sc.set_camera_look(cam, (0.06, 1.88 - 0.18 * u, 1.24), (0.04, -0.45, 1.18), lens=38.0, fstop=3.2)
                else:
                    sc.set_camera_look(cam, (0.0, 2.15 - 0.20 * u, 1.32), (0.0, -0.55, 1.25), lens=38.0, fstop=3.2)

            elif bid == "b33_never_cooked":
                cf.set_char_transform(alex, 0.0, -0.78, 0.0, 0.0)
                cf.set_face_with_blink(alex, "alex_deadpan", f, seed=33)
                cf.pose_char(alex, arm_l=(6, 0, -5), forearm_l=(6, 0, 0), arm_r=(6, 0, 5), forearm_r=(6, 0, 0))
                sc.set_camera_look(cam, (0.0, 1.98 - 0.18 * u, 1.34), (0.0, -0.65, 1.28), lens=42.0, fstop=2.8)

            elif bid in ("b43_already_start", "b46_one_of_me"):
                cf.set_char_transform(alex, 0.0, -0.78, 0.0, 0.0)
                cf.set_face_with_blink(alex, "alex_determined" if bid == "b46_one_of_me" else "alex_smug", f, seed=34)
                pf.set_wrap_fold(props["pov_sheet"], 0.25 + 0.35 * abs(math.sin(t * 14.0)), 0.0)
                cf.pose_char(alex, torso_rot=(6, 0, 0), arm_l=(56, -24, -10), forearm_l=(36, -12, 0), arm_r=(56, 24, 10), forearm_r=(36, 12, 0))
                sc.set_camera_look(cam, (0.0, 1.92 - 0.26 * u, 1.32), (0.0, -0.60, 1.24), lens=38.0, fstop=3.0)

            elif bid == "b45_midnight_rush":
                # Camera behind counter looking toward entrance (+Y) so all 22 party faces & Mayor rush right toward lens!
                cf.set_char_transform(mayor, -0.25, 1.35, 0.0, 172.0)
                cf.set_face(mayor, "mayor_party_cheer.png")
                cf.animate_party_dance(mayor, t, phase=0.1, energy=1.0)
                for idx_c, (rc, rx, ry, ph) in enumerate(rush_crowd):
                    cf.set_char_transform(rc, rx * 1.15, ry + 0.85, 0.0, 175.0 + (idx_c % 5 - 2) * 5.0)
                    cf.animate_party_dance(rc, t, phase=ph, energy=0.95)
                sc.set_camera_look(cam, (1.45 - 0.35 * u, -0.78, 1.88), (-0.10, 2.25, 1.15), lens=24.0, fstop=4.5)

            elif bid == "b47_huss_climax":
                # Alternating front intensity + top-down POV wrap per HUSS hit!
                cf.set_char_transform(alex, 0.0, -0.82, 0.0, 0.0)
                cf.set_face(alex, "alex_determined.png")
                pulse = 0.5 + 0.5 * math.sin(t * 32.0)
                pf.set_wrap_fold(props["pov_sheet"], 0.35 + 0.50 * pulse, 0.2 + 0.35 * pulse)
                cf.pose_char(alex, torso_rot=(8, 0, 0), arm_l=(60 + 14 * pulse, -24, -10), forearm_l=(36, -12, 0), arm_r=(60 - 14 * pulse, 24, 10), forearm_r=(36, 12, 0))
                if int(u * 3) % 2 == 1:
                    cf.set_pov_arms_only(alex, True)
                    cf.set_char_transform(alex, 0.0, -0.30, -0.08, 0.0)
                    cf.pose_char(alex, torso_rot=(0, 0, 0), arm_l=(48 + 4 * pulse, -26 - 8 * pulse, 0), forearm_l=(12 + 14 * pulse, -14, 0), arm_r=(48 + 4 * pulse, 26 + 8 * pulse, 0), forearm_r=(12 + 14 * pulse, 14, 0))
                    sc.set_camera_look(cam, (0.0, -0.32, 1.61 - 0.05 * u), (0.0, 0.16, 0.81), lens=24.0, fstop=4.0, kick_offset=kick_off, kick_amp=0.03)
                else:
                    cf.set_pov_arms_only(alex, False)
                    sc.set_camera_look(cam, (0.0, 1.75 - 0.15 * u, 1.32), (0.0, -0.55, 1.15), lens=38.0, fstop=3.2, kick_offset=kick_off, kick_amp=0.03)

            elif bid == "b48_400_burgers":
                # 26 Golden Wrapped Burgers flying over parted cheering crowd + 3D Scoreboard climbing 001 -> 400!
                cnt_val = int(round(1 + 399 * min(1.0, u / 0.85) ** 0.85))
                set_scoreboard_value(props["scoreboard"], cnt_val)
                cf.set_char_transform(alex, 0.0, -0.78, 0.0, 0.0)
                cf.set_face(alex, "alex_determined.png")
                fl = math.sin(t * 28.0)
                cf.pose_char(alex, arm_l=(110 + 25 * fl, 0, -20), forearm_l=(25, 0, 0), arm_r=(110 - 25 * fl, 0, 20), forearm_r=(25, 0, 0))
                cf.set_char_transform(mayor, -0.82, 1.15, 0.0, 148.0)
                cf.set_face(mayor, "mayor_stunned_o.png")
                cf.animate_party_dance(mayor, t, phase=0.0, energy=0.5)
                for idx_c, (rc, rx, ry, ph) in enumerate(rush_crowd):
                    rx_part = (rx - 0.42) if rx < 0.0 else (rx + 0.42)
                    cf.set_char_transform(rc, rx_part, ry + 0.15, 0.0, 165.0 + (idx_c % 5) * 6.0)
                    cf.animate_party_dance(rc, t, phase=ph, energy=1.05)
                for wb, tx, ty, pk, ph in props["flying_burgers"]:
                    fu = (u * 1.4 + ph) % 1.0
                    wb.location = (tx * fu, 0.15 + (ty - 0.15) * fu, 0.90 + 4.0 * pk * fu * (1.0 - fu))
                    wb.rotation_euler = (fu * 6.0, fu * 4.5, ph * 3.0)
                sc.set_camera_look(cam, (0.35 - 0.25 * u, 4.75 - 0.30 * u, 2.86), (0.0, -0.75, 1.56), lens=24.0, fstop=4.5)

            elif bid == "b49_mayor_stared":
                # Iconic stunned Mayor close-up! (Mayor stands at (0, 1.25, 0) facing +Y camera!)
                cf.set_char_transform(mayor, 0.0, 1.25, 0.0, 0.0)
                cf.set_face(mayor, "mayor_stunned_o.png" if u < 0.52 else "mayor_confused_frown.png")
                cf.pose_char(mayor, head_rot=(-4, 0, 0), arm_l=(6, 0, -5), forearm_l=(6, 0, 0), arm_r=(6, 0, 5), forearm_r=(6, 0, 0))
                bg_spots = [(-1.10, 0.72), (-0.58, 0.68), (0.58, 0.68), (1.10, 0.72), (-1.45, 0.92), (1.45, 0.92)]
                for (rc, _, _, _), (bx, by) in zip(rush_crowd[:6], bg_spots):
                    cf.set_char_transform(rc, bx, by, 0.0, 0.0)
                    cf.pose_char(rc, head_rot=(0, 0, 0), arm_l=(6, 0, -5), arm_r=(6, 0, 5))
                sc.set_camera_look(cam, (0.0, 2.85 - 0.25 * u, 1.48), (0.0, 1.25, 1.44), lens=44.0, fstop=2.8)

            elif bid == "b50_final_callback":
                cf.set_char_transform(alex, -0.10, -0.78, 0.0, 0.0)
                cf.set_face_with_blink(alex, "alex_smug", f, seed=38)
                pf.set_wrap_fold(props["pov_sheet"], 0.15, 0.0)
                cf.pose_char(alex, head_rot=(-3, 0, -4), arm_l=(52, -22, -10), forearm_l=(36, -10, 0), arm_r=(52, 22, 10), forearm_r=(36, 10, 0))
                sc.set_camera_look(cam, (0.05, 1.95 - 0.18 * u, 1.32), (0.0, -0.55, 1.24), lens=36.0, fstop=3.2)

            elif bid == "b51_final_huss":
                cf.set_char_transform(alex, 0.0, -0.30, -0.08, 0.0)
                pulse = 0.5 + 0.5 * math.sin(t * 34.0)
                pf.set_wrap_fold(props["pov_sheet"], 0.45 + 0.50 * pulse, 0.25 + 0.40 * pulse)
                cf.pose_char(alex, torso_rot=(0, 0, 0), arm_l=(48 + 4 * pulse, -26 - 8 * pulse, 0), forearm_l=(12 + 14 * pulse, -14, 0), arm_r=(48 + 4 * pulse, 26 + 8 * pulse, 0), forearm_r=(12 + 14 * pulse, 14, 0))
                sc.set_camera_look(cam, (0.0, -0.32, 1.61 - 0.05 * u), (0.0, 0.16, 0.81), lens=24.0, fstop=4.0, kick_offset=kick_off, kick_amp=0.03)

            if preview_only:
                sc.render_frame(scene, f, preview_tag=f"int_{bid}")
                break
            else:
                sc.render_frame(scene, f)


if __name__ == "__main__":
    main()
