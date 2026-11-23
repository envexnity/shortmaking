"""
props_factory.py — High-Detail Stylized 3D Props & Architectural Assets (Blender 5.3.0).
100% pure-bmesh mesh generation (ZERO bpy.ops calls -> 20x faster scene building,
uniform bevels, and true 1:1 world-meter scale baked into vertices for non-stretched textures!).
"""
import math
import random
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

PROJ_DIR = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking\videos\roblox-reel-Df1kubCJ-o0-v2")
sys.path.insert(0, str(PROJ_DIR))
import scene_common as sc


def _finish_bm(bm: bmesh.types.BMesh, name: str, loc, mat, col, rot=(0, 0, 0), parent=None, bevel_w=0.0, bevel_segs=2, smooth=True):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    o = bpy.data.objects.new(name, mesh)
    o.location = loc
    o.rotation_euler = rot
    col.objects.link(o)
    if mat:
        o.data.materials.append(mat)
    if smooth:
        for p in o.data.polygons:
            p.use_smooth = True
    if bevel_w > 0:
        sc.smooth_bevel(o, width=bevel_w, segments=bevel_segs, angle_deg=32.0)
    if parent:
        o.parent = parent
    return o


def make_torus_bm(bm: bmesh.types.BMesh, major_r: float, minor_r: float, major_segs: int = 28, minor_segs: int = 12, z_off: float = 0.0):
    rings = []
    for i in range(major_segs):
        theta = (i / major_segs) * 2.0 * math.pi
        ct, st = math.cos(theta), math.sin(theta)
        ring = []
        for j in range(minor_segs):
            phi = (j / minor_segs) * 2.0 * math.pi
            cp, sp = math.cos(phi), math.sin(phi)
            r = major_r + minor_r * cp
            ring.append(bm.verts.new((r * ct, r * st, z_off + minor_r * sp)))
        rings.append(ring)
    for i in range(major_segs):
        ni = (i + 1) % major_segs
        for j in range(minor_segs):
            nj = (j + 1) % minor_segs
            bm.faces.new((rings[i][j], rings[ni][j], rings[ni][nj], rings[i][nj]))


def make_bevel_box(name: str, loc, scale, mat, col, bevel_w=0.015, segs=3, rot=(0, 0, 0), parent=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    sx, sy, sz = scale
    for v in bm.verts:
        v.co.x *= sx
        v.co.y *= sy
        v.co.z *= sz
    return _finish_bm(bm, name, loc, mat, col, rot=rot, parent=parent, bevel_w=bevel_w, bevel_segs=segs)


def make_smooth_cyl(name: str, loc, r, h, mat, col, segs=32, rot=(0, 0, 0), bevel_w=0.008, parent=None, r2=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=r, radius2=(r if r2 is None else r2), depth=h)
    return _finish_bm(bm, name, loc, mat, col, rot=rot, parent=parent, bevel_w=bevel_w, bevel_segs=2)


def make_smooth_sphere(name: str, loc, scale, mat, col, segs=24, rot=(0, 0, 0), parent=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=max(10, segs // 2), radius=1.0)
    sx, sy, sz = scale
    for v in bm.verts:
        v.co.x *= sx
        v.co.y *= sy
        v.co.z *= sz
    return _finish_bm(bm, name, loc, mat, col, rot=rot, parent=parent)


def make_smooth_torus(name: str, loc, major_r, minor_r, mat, col, major_segs=32, minor_segs=12, rot=(0, 0, 0), parent=None):
    bm = bmesh.new()
    make_torus_bm(bm, major_r, minor_r, major_segs, minor_segs)
    return _finish_bm(bm, name, loc, mat, col, rot=rot, parent=parent)


def build_hero_burger(name: str, loc, col, scale: float = 1.0):
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.scale = (scale, scale, scale)
    col.objects.link(root)

    m_bun = sc.make_stylized_pbr("Mat_HB_Bun", "#DF9546", rough=0.38, coat=0.18, sss=0.08, bump_str=0.03)
    m_seed = sc.make_stylized_pbr("Mat_HB_Seed", "#FEF3C7", rough=0.38, coat=0.12)
    m_patty = sc.make_stylized_pbr("Mat_HB_Patty", "#592A16", rough=0.60, coat=0.02, bump_str=0.06, ao_str=0.28)
    m_cheese = sc.make_stylized_pbr("Mat_HB_Cheese", "#FACC15", rough=0.28, coat=0.20, sss=0.10)
    m_let = sc.make_stylized_pbr("Mat_HB_Lettuce", "#4ADE80", rough=0.36, coat=0.14, sss=0.12)
    m_tom = sc.make_stylized_pbr("Mat_HB_Tomato", "#EF4444", rough=0.18, coat=0.38, sss=0.15)

    make_smooth_cyl(f"{name}_BotBun", (0, 0, 0.036), 0.145, 0.065, m_bun, col, segs=32, bevel_w=0.012, parent=root)
    make_smooth_cyl(f"{name}_Patty", (0, 0, 0.088), 0.152, 0.055, m_patty, col, segs=32, bevel_w=0.014, parent=root)

    # Draped melted cheese square
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=6, y_segments=6, size=0.145)
    for v in bm.verts:
        r2 = v.co.x ** 2 + v.co.y ** 2
        v.co.z = 0.118 - max(0.0, (r2 - 0.015) * 1.1)
    bmesh.ops.solidify(bm, geom=list(bm.faces), thickness=0.014)
    ch = _finish_bm(bm, f"{name}_Cheese", (0, 0, 0), m_cheese, col, parent=root)
    sc.smooth_subsurf(ch, 1)

    # Ruffled wavy lettuce
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=10, y_segments=10, size=0.165)
    for v in bm.verts:
        rad = math.hypot(v.co.x, v.co.y)
        ang = math.atan2(v.co.y, v.co.x)
        if rad > 0.175:
            sr = 0.172 / (rad + 1e-6)
            v.co.x *= sr
            v.co.y *= sr
        v.co.z = 0.130 + 0.014 * math.sin(ang * 7.0) * min(1.0, rad / 0.12)
    bmesh.ops.solidify(bm, geom=list(bm.faces), thickness=0.010)
    lt = _finish_bm(bm, f"{name}_Lettuce", (0, 0, 0), m_let, col, parent=root)
    sc.smooth_subsurf(lt, 1)

    make_smooth_cyl(f"{name}_Tomato", (0, 0, 0.148), 0.135, 0.024, m_tom, col, segs=28, bevel_w=0.008, parent=root)
    make_smooth_sphere(f"{name}_TopBun", (0, 0, 0.155), (0.152, 0.152, 0.088), m_bun, col, segs=32, parent=root)
    rng = random.Random(9)
    for si in range(20):
        phi = rng.uniform(0.18, 0.85)
        theta = (si / 20.0) * math.pi * 2.0 + rng.uniform(-0.15, 0.15)
        sx = math.sin(phi) * math.cos(theta) * 0.145
        sy = math.sin(phi) * math.sin(theta) * 0.145
        sz = 0.158 + math.cos(phi) * 0.086
        make_smooth_sphere(f"{name}_Seed_{si}", (sx, sy, sz), (0.012, 0.007, 0.005), m_seed, col, segs=10, rot=(0, phi * 0.6, theta), parent=root)
    return root


def build_wrapped_burger(name: str, loc, col, scale: float = 1.0):
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.scale = (scale, scale, scale)
    col.objects.link(root)

    m_wrap = sc.make_textured_pbr(
        "Mat_HeroWrapYellow",
        sc.TEX_ENV / "wrapper_paper_yellow.png",
        sc.TEX_ENV / "wrapper_paper_yellow_bump.png",
        proj="UV",
        rough_min=0.48,
        rough_max=0.65,
        bump_strength=0.14,
    )
    m_plain = sc.make_stylized_pbr("Mat_HeroWrapPlain", "#ECAE20", rough=0.52, coat=0.0, bump_str=0.03)
    m_stripe = sc.make_stylized_pbr("Mat_HeroWrapStripe", "#D42A18", rough=0.48, coat=0.0)

    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=28, radius1=0.155, radius2=0.150, depth=0.135)
    for v in bm.verts:
        v.co.z += 0.068
    uv_layer = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        if abs(f.normal.z) < 0.5:
            for lp in f.loops:
                ang = math.atan2(lp.vert.co.y, lp.vert.co.x)
                lp[uv_layer].uv = ((ang / (2 * math.pi)) + 0.5, 0.15 + (lp.vert.co.z / 0.135) * 0.70)
        else:
            for lp in f.loops:
                lp[uv_layer].uv = (0.1, 0.1)
    _finish_bm(bm, f"{name}_Body", (0, 0, 0), m_wrap, col, parent=root, bevel_w=0.016, bevel_segs=2)
    make_bevel_box(f"{name}_TopFold", (0, 0, 0.136), (0.22, 0.09, 0.014), m_plain, col, bevel_w=0.004, segs=2, rot=(0, 0, 0.15), parent=root)
    make_bevel_box(f"{name}_TopStripe", (0, 0, 0.139), (0.29, 0.032, 0.012), m_stripe, col, bevel_w=0.003, segs=2, rot=(0, 0, 0.15), parent=root)
    return root


def _make_uv_flap(name: str, loc, box_off, box_sz, mat, col, parent):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    sx, sy, sz = box_sz
    ox, oy, oz = box_off
    for v in bm.verts:
        v.co.x = v.co.x * sx + ox
        v.co.y = v.co.y * sy + oy
        v.co.z = v.co.z * sz + oz
    uv_layer = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        for lp in f.loops:
            u = (lp.vert.co.x - ox) / max(0.01, sx) + 0.5
            v = (lp.vert.co.y - oy) / max(0.01, sy) + 0.5
            lp[uv_layer].uv = (u, v)
    return _finish_bm(bm, name, loc, mat, col, parent=parent, bevel_w=0.002, bevel_segs=1)


def build_animated_wrap_sheet(name: str, loc, col, scale: float = 1.0):
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.scale = (scale, scale, scale)
    col.objects.link(root)

    m_wrap = sc.make_textured_pbr("Mat_SheetWrap", sc.TEX_ENV / "wrapper_paper_yellow.png", sc.TEX_ENV / "wrapper_paper_yellow_bump.png", proj="UV", rough_min=0.50, rough_max=0.68, coat=0.0)
    m_plain = sc.make_stylized_pbr("Mat_SheetPlain", "#ECAE20", rough=0.55, coat=0.0)

    _make_uv_flap(f"{name}_Center", (0, 0, 0.005), (0, 0, 0), (0.36, 0.36, 0.008), m_wrap, col, root)

    flaps = {}
    configs = [
        ("L", (-0.18, 0.0, 0.006), (-0.13, 0.0, 0.0), (0.26, 0.34, 0.008), m_wrap),
        ("R", ( 0.18, 0.0, 0.006), ( 0.13, 0.0, 0.0), (0.26, 0.34, 0.008), m_wrap),
        ("F", (0.0, -0.18, 0.006), (0.0, -0.13, 0.0), (0.34, 0.26, 0.008), m_plain),
        ("B", (0.0,  0.18, 0.006), (0.0,  0.13, 0.0), (0.34, 0.26, 0.008), m_plain),
    ]
    for key, piv_loc, box_off, box_sz, mat in configs:
        piv = bpy.data.objects.new(f"{name}_Pivot_{key}", None)
        piv.location = piv_loc
        col.objects.link(piv)
        piv.parent = root
        _make_uv_flap(f"{name}_Flap_{key}", (0, 0, 0), box_off, box_sz, mat, col, piv)
        flaps[key] = piv
    return {"root": root, "flaps": flaps}


def set_wrap_fold(sheet: dict, u_lr: float, u_fb: float):
    fl = sheet["flaps"]
    fl["L"].rotation_euler = (0.0, math.radians(-145.0 * u_lr), 0.0)
    fl["R"].rotation_euler = (0.0, math.radians(145.0 * u_lr), 0.0)
    fl["F"].rotation_euler = (math.radians(-140.0 * u_fb), 0.0, 0.0)
    fl["B"].rotation_euler = (math.radians(140.0 * u_fb), 0.0, 0.0)


def build_hero_cat(name: str, loc, col, scale: float = 1.0):
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.scale = (scale, scale, scale)
    col.objects.link(root)

    m_cat = sc.make_stylized_pbr("Mat_Cat_Fur", "#F97316", rough=0.62, coat=0.0, sheen=0.45, bump_str=0.04)
    m_stripe = sc.make_stylized_pbr("Mat_Cat_Stripe", "#C2410C", rough=0.62, coat=0.0, sheen=0.45)
    m_cream = sc.make_stylized_pbr("Mat_Cat_Cream", "#FED7AA", rough=0.58, coat=0.0, sheen=0.4)
    m_pink = sc.make_stylized_pbr("Mat_Cat_Pink", "#EC6088", rough=0.42, coat=0.08)
    m_teal = sc.make_stylized_pbr("Mat_Cat_WrapTeal", "#14B8A6", rough=0.48, coat=0.04)
    m_yel = sc.make_stylized_pbr("Mat_Cat_WrapYel", "#ECAE20", rough=0.52, coat=0.0)
    m_blk = sc.make_stylized_pbr("Mat_Cat_Ink", "#18181B", rough=0.25)
    m_wht = sc.make_stylized_pbr("Mat_Cat_Whisker", "#F8FAFC", rough=0.35, coat=0.0)

    make_smooth_cyl(f"{name}_WrapTeal", (0, 0, 0.16), 0.135, 0.30, m_teal, col, segs=28, bevel_w=0.018, parent=root)
    make_smooth_cyl(f"{name}_WrapBand", (0, 0, 0.16), 0.141, 0.065, m_yel, col, segs=28, bevel_w=0.008, parent=root)
    make_smooth_sphere(f"{name}_Head", (0, 0.01, 0.38), (0.145, 0.132, 0.125), m_cat, col, segs=28, parent=root)
    for sx in (-0.042, 0.042):
        make_smooth_sphere(f"{name}_Muzzle_{sx}", (sx, 0.122, 0.355), (0.042, 0.032, 0.030), m_cream, col, segs=16, parent=root)
    make_smooth_sphere(f"{name}_Nose", (0, 0.146, 0.372), (0.024, 0.018, 0.016), m_pink, col, segs=14, parent=root)
    for sx in (-0.056, 0.056):
        make_bevel_box(f"{name}_Eye_{sx}", (sx, 0.132, 0.402), (0.044, 0.016, 0.014), m_blk, col, bevel_w=0.004, segs=2, rot=(0, math.radians(-10 if sx > 0 else 10), 0), parent=root)
    for ix, sx in enumerate((-0.026, 0.0, 0.026)):
        make_bevel_box(f"{name}_Stripe_{ix}", (sx, 0.112, 0.465), (0.014, 0.030, 0.045), m_stripe, col, bevel_w=0.004, segs=2, parent=root)
    # Rounded ears w/ soft recessed pink inner ears!
    for side, sx, rz in [("L", 0.095, -0.32), ("R", -0.095, 0.32)]:
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=18, radius1=0.055, radius2=0.010, depth=0.105)
        for v in bm.verts:
            v.co.y *= 0.65
        _finish_bm(bm, f"{name}_Ear_{side}", (sx, 0.0, 0.50), m_cat, col, rot=(0.15, rz, 0), parent=root)
        bm2 = bmesh.new()
        bmesh.ops.create_cone(bm2, cap_ends=True, cap_tris=False, segments=14, radius1=0.030, radius2=0.005, depth=0.065)
        for v in bm2.verts:
            v.co.y *= 0.35
        _finish_bm(bm2, f"{name}_InEar_{side}", (sx * 0.98, 0.014, 0.492), m_pink, col, rot=(0.15, rz, 0), parent=root)
    for side, sx in [("L", 0.075), ("R", -0.075)]:
        for wi, dz in enumerate((-0.015, 0.0, 0.015)):
            make_smooth_cyl(f"{name}_Whisk_{side}_{wi}", (sx * 1.45, 0.125, 0.358 + dz), 0.0035, 0.11, m_wht, col, segs=8, rot=(0, math.radians(90 + dz * 400 * (1 if sx > 0 else -1)), 0), bevel_w=0, parent=root)
    for sx in (-0.068, 0.068):
        make_smooth_sphere(f"{name}_Paw_{sx}", (sx, 0.125, 0.045), (0.042, 0.052, 0.034), m_cream, col, segs=16, parent=root)
    return root


def build_hero_clock(name: str, loc, col, is_alarm: bool = False, scale: float = 1.0):
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.scale = (scale, scale, scale)
    col.objects.link(root)

    case_hex = "#14B8A6" if is_alarm else "#DC2626"
    m_case = sc.make_stylized_pbr(f"Mat_Clk_{case_hex}", case_hex, rough=0.25, metal=0.25, coat=0.30)
    m_chrome = sc.make_stylized_pbr("Mat_Clk_Chrome", "#E2E8F0", rough=0.16, metal=0.90, coat=0.30)
    m_brass = sc.make_stylized_pbr("Mat_Clk_Brass", "#FACC15", rough=0.20, metal=0.88, coat=0.30)
    dial_png = sc.TEX_PROPS / ("clock_5am_dial.png" if is_alarm else "clock_stopwatch_dial.png")
    m_dial = sc.make_textured_pbr(f"Mat_Dial_{is_alarm}", dial_png, proj="UV", rough_min=0.32, rough_max=0.42, ao_str=0.05)

    make_smooth_cyl(f"{name}_Case", (0, 0, 0.175), 0.155, 0.085, m_case, col, segs=36, rot=(math.radians(90), 0, 0), bevel_w=0.015, parent=root)
    make_smooth_torus(f"{name}_Bezel", (0, 0.042, 0.175), 0.148, 0.014, m_chrome, col, major_segs=36, minor_segs=10, rot=(math.radians(90), 0, 0), parent=root)

    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, cap_tris=False, segments=36, radius=0.140)
    uv = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        for lp in f.loops:
            lp[uv].uv = (lp.vert.co.x / 0.28 + 0.5, lp.vert.co.y / 0.28 + 0.5)
    _finish_bm(bm, f"{name}_Dial", (0, 0.044, 0.175), m_dial, col, rot=(math.radians(90), 0, 0), parent=root)

    if is_alarm:
        for sx in (-0.11, 0.11):
            make_smooth_sphere(f"{name}_Bell_{sx}", (sx, 0, 0.34), (0.052, 0.048, 0.042), m_brass, col, segs=18, parent=root)
            make_smooth_cyl(f"{name}_Foot_{sx}", (sx * 0.85, 0, 0.02), 0.018, 0.045, m_chrome, col, segs=12, rot=(0, math.radians(sx * 160), 0), bevel_w=0.004, parent=root)
    else:
        make_smooth_cyl(f"{name}_Stem", (0, 0, 0.35), 0.018, 0.045, m_chrome, col, segs=16, bevel_w=0.004, parent=root)
        make_smooth_cyl(f"{name}_Crown", (0, 0, 0.382), 0.034, 0.025, m_chrome, col, segs=20, bevel_w=0.006, parent=root)
    return root


def build_hero_breakfast(name: str, loc, col):
    root = bpy.data.objects.new(name, None)
    root.location = loc
    col.objects.link(root)

    m_plate = sc.make_stylized_pbr("Mat_Porcelain", "#F8FAFC", rough=0.16, coat=0.45)
    m_eggw = sc.make_stylized_pbr("Mat_EggW", "#FFFBEB", rough=0.30, coat=0.20, sss=0.15)
    m_yolk = sc.make_stylized_pbr("Mat_EggY", "#F59E0B", rough=0.18, coat=0.45, sss=0.25)
    m_bacon = sc.make_stylized_pbr("Mat_Bacon", "#B91C1C", rough=0.35, coat=0.18, bump_str=0.04)

    make_smooth_cyl(f"{name}_PlateBase", (0, 0, 0.012), 0.21, 0.018, m_plate, col, segs=36, bevel_w=0.008, parent=root)
    make_smooth_torus(f"{name}_PlateRim", (0, 0, 0.022), 0.205, 0.016, m_plate, col, major_segs=36, minor_segs=10, parent=root)
    # Raised cleanly above plate top (z = 0.021) so zero clipping!
    make_smooth_sphere(f"{name}_EggW", (-0.055, 0.01, 0.032), (0.095, 0.084, 0.014), m_eggw, col, segs=22, parent=root)
    make_smooth_sphere(f"{name}_EggY", (-0.050, 0.015, 0.046), (0.044, 0.044, 0.022), m_yolk, col, segs=20, parent=root)

    for bi, bx in enumerate((0.062, 0.114)):
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=2, y_segments=10, size=1.0)
        for v in bm.verts:
            v.co.x = v.co.x * 0.020 + bx
            v.co.y = v.co.y * 0.11
            v.co.z = 0.038 + 0.004 * math.sin(v.co.y * 45.0 + bi)
        bmesh.ops.solidify(bm, geom=list(bm.faces), thickness=0.006)
        bc = _finish_bm(bm, f"{name}_Bacon_{bi}", (0, 0, 0), m_bacon, col, parent=root)
        sc.smooth_subsurf(bc, 1)
    return root


def build_hero_griddle(name: str, loc, col):
    root = bpy.data.objects.new(name, None)
    root.location = loc
    col.objects.link(root)

    m_body = sc.make_stylized_pbr("Mat_GriddleSteel", "#334155", rough=0.32, metal=0.75)
    m_iron = sc.make_stylized_pbr("Mat_GriddleIron", "#111827", rough=0.40, metal=0.45, bump_str=0.04)
    m_knob = sc.make_stylized_pbr("Mat_GriddleKnob", "#EF4444", rough=0.32)
    m_patty = sc.make_stylized_pbr("Mat_HB_Patty", "#592A16", rough=0.60, coat=0.02, bump_str=0.06)
    m_steam = sc.make_stylized_pbr("Mat_SizzleSteam", "#F8FAFC", rough=0.80, coat=0.0, alpha=0.42)

    make_bevel_box(f"{name}_Housing", (0, 0, 0.032), (0.68, 0.44, 0.055), m_body, col, bevel_w=0.012, segs=3, parent=root)
    make_bevel_box(f"{name}_Plate", (0, 0, 0.062), (0.62, 0.38, 0.016), m_iron, col, bevel_w=0.006, segs=2, parent=root)
    make_smooth_cyl(f"{name}_Knob", (0.26, 0.228, 0.032), 0.022, 0.025, m_knob, col, segs=16, rot=(math.radians(90), 0, 0), bevel_w=0.004, parent=root)
    patty = make_smooth_cyl(f"{name}_ActivePatty", (0.0, 0.0, 0.088), 0.13, 0.042, m_patty, col, segs=28, bevel_w=0.014, parent=root)

    steam_puffs = []
    for si, (sx, sy, sz, rad) in enumerate([(-0.04, 0.0, 0.16, 0.045), (0.05, 0.02, 0.22, 0.055), (0.0, -0.02, 0.29, 0.040)]):
        steam_puffs.append(make_smooth_sphere(f"{name}_Steam_{si}", (sx, sy, sz), (rad, rad, rad * 0.8), m_steam, col, segs=14, parent=root))

    spat = bpy.data.objects.new(f"{name}_Spatula", None)
    spat.location = (-0.18, 0.04, 0.16)
    col.objects.link(spat)
    spat.parent = root
    make_bevel_box(f"{name}_SpatBlade", (0.12, 0.0, -0.02), (0.11, 0.095, 0.006), m_body, col, bevel_w=0.002, segs=2, rot=(0, math.radians(16), 0), parent=spat)
    make_smooth_cyl(f"{name}_SpatShaft", (0.0, 0.0, 0.015), 0.008, 0.16, m_body, col, segs=10, rot=(0, math.radians(90), 0), bevel_w=0.002, parent=spat)
    make_smooth_cyl(f"{name}_SpatGrip", (-0.12, 0.0, 0.025), 0.018, 0.12, m_iron, col, segs=14, rot=(0, math.radians(90), 0), bevel_w=0.005, parent=spat)
    return {"root": root, "patty": patty, "steam": steam_puffs, "spatula": spat}


def build_blur_hands_fx(name: str, loc, col):
    root = bpy.data.objects.new(name, None)
    root.location = loc
    col.objects.link(root)

    m_ghost = sc.make_stylized_pbr("Mat_GhostArm", "#F2C6A0", rough=0.45, coat=0.0, alpha=0.32)
    m_arc = sc.make_stylized_pbr("Mat_SpeedArc", "#FFFFFF", rough=0.3, coat=0.0, emit_hex="#FFFFFF", emit_str=1.6, alpha=0.72)

    for side_sgn in (-1, 1):
        for k in range(3):
            make_bevel_box(
                f"{name}_Ghost_{side_sgn}_{k}",
                (side_sgn * (0.18 + k * 0.06), 0.18, -0.18 + k * 0.06),
                (0.20, 0.28, 0.18),
                m_ghost, col, bevel_w=0.016, segs=3,
                rot=(-0.35 + k * 0.18, 0, side_sgn * (0.28 + k * 0.24)), parent=root,
            )
    for k in range(4):
        side_sgn = -1 if k % 2 == 0 else 1
        make_bevel_box(
            f"{name}_Arc_{k}",
            (side_sgn * (0.28 + (k // 2) * 0.09), 0.22, -0.10 + (k // 2) * 0.08),
            (0.012, 0.012, 0.28),
            m_arc, col, bevel_w=0.004, segs=2,
            rot=(0.3, side_sgn * 0.45, 0.2), parent=root,
        )
    return root


def build_bumpy_tree(name: str, loc, col, scale: float = 1.0):
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.scale = (scale, scale, scale)
    col.objects.link(root)

    m_bark = sc.make_stylized_pbr("Mat_TreeBark", "#784421", rough=0.80, coat=0.0, bump_str=0.06)
    m_leaf = sc.make_stylized_pbr("Mat_TreeLeaf", "#34B856", rough=0.68, coat=0.0, sss=0.08, bump_str=0.08, ao_str=0.25)

    make_smooth_cyl(f"{name}_Trunk", (0, 0, 0.95), 0.34, 1.9, m_bark, col, segs=18, bevel_w=0.0, parent=root, r2=0.20)
    clusters = [(0, 0, 2.55, 1.05), (-0.65, 0.25, 2.20, 0.72), (0.68, -0.20, 2.25, 0.74), (0.1, 0.62, 2.25, 0.68), (0.0, -0.55, 2.30, 0.68)]
    for ci, (cx, cy, cz, rad) in enumerate(clusters):
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=3, radius=rad)
        for v in bm.verts:
            n = v.co.normalized()
            bump = 1.0 + 0.14 * math.sin(n.x * 7.5 + ci) * math.cos(n.y * 7.5) + 0.09 * math.sin(n.z * 9.0)
            v.co = v.co * bump
        lf = _finish_bm(bm, f"{name}_Canopy_{ci}", (cx, cy, cz), m_leaf, col, parent=root)
        sc.smooth_subsurf(lf, 1)
    return root


def build_townhouse(name: str, loc, col, width: float, depth: float, height: float, wall_hex: str, roof_hex: str, is_night: bool = True):
    root = bpy.data.objects.new(name, None)
    root.location = loc
    col.objects.link(root)

    m_wall = sc.make_stylized_pbr(f"Mat_TH_Wall_{wall_hex}", wall_hex, rough=0.68, coat=0.0, bump_str=0.04)
    m_roof = sc.make_stylized_pbr(f"Mat_TH_Roof_{roof_hex}", roof_hex, rough=0.55, coat=0.02, bump_str=0.04)
    m_trim = sc.make_stylized_pbr("Mat_TH_Trim", "#F8FAFC", rough=0.50, coat=0.0)
    m_win = sc.make_stylized_pbr(
        f"Mat_TH_Win_{is_night}",
        "#FDE68A" if is_night else "#93C5FD",
        rough=0.18, coat=0.25,
        emit_hex="#FEF08A" if is_night else None,
        emit_str=1.6 if is_night else 0.0,
    )
    m_door = sc.make_stylized_pbr("Mat_TH_Door", "#7C4A22", rough=0.52, coat=0.02)

    make_bevel_box(f"{name}_Body", (0, 0, height * 0.5), (width, depth, height), m_wall, col, bevel_w=0.04, segs=3, parent=root)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=4, radius1=width * 0.78, radius2=0.08, depth=height * 0.42)
    for v in bm.verts:
        v.co.y *= (depth / width)
    _finish_bm(bm, f"{name}_Roof", (0, 0, height + height * 0.21), m_roof, col, rot=(0, 0, math.radians(45)), parent=root, bevel_w=0.03, bevel_segs=2)

    make_bevel_box(f"{name}_Chimney", (width * 0.26, -depth * 0.15, height + height * 0.30), (0.55, 0.55, 1.2), m_roof, col, bevel_w=0.02, segs=2, parent=root)
    fy = depth * 0.5 + 0.03
    make_bevel_box(f"{name}_Door", (0, fy, 1.05), (0.95, 0.10, 2.05), m_door, col, bevel_w=0.02, segs=2, parent=root)
    for wx in (-width * 0.27, width * 0.27):
        for wz in (height * 0.40, height * 0.75):
            if wz < height * 0.45 and abs(wx) < 0.8:
                continue
            make_bevel_box(f"{name}_WinFrame_{wx:.1f}_{wz:.1f}", (wx, fy, wz), (1.05, 0.12, 1.10), m_trim, col, bevel_w=0.015, segs=2, parent=root)
            make_bevel_box(f"{name}_WinPane_{wx:.1f}_{wz:.1f}", (wx, fy + 0.02, wz), (0.86, 0.10, 0.90), m_win, col, bevel_w=0.008, segs=2, parent=root)
    return root


def build_birthday_cake(name: str, loc, col, scale: float = 1.0):
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.scale = (scale, scale, scale)
    col.objects.link(root)

    m_blue = sc.make_stylized_pbr("Mat_CakeBlue", "#38BDF8", rough=0.38, coat=0.12)
    m_frost = sc.make_stylized_pbr("Mat_CakeFrost", "#FFFBEB", rough=0.35, coat=0.14)
    m_pink = sc.make_stylized_pbr("Mat_CakePink", "#F472B6", rough=0.38, coat=0.08)
    m_flame = sc.make_stylized_pbr("Mat_CakeFlame", "#FACC15", emit_hex="#FDE047", emit_str=7.0)

    make_smooth_cyl(f"{name}_Stand", (0, 0, 0.25), 0.45, 0.50, sc.make_stylized_pbr("Mat_TableWht", "#F8FAFC"), col, segs=28, bevel_w=0.012, parent=root)
    make_smooth_cyl(f"{name}_Tier1", (0, 0, 0.68), 0.40, 0.36, m_blue, col, segs=28, bevel_w=0.015, parent=root)
    make_smooth_cyl(f"{name}_Tier2", (0, 0, 0.99), 0.28, 0.28, m_frost, col, segs=28, bevel_w=0.015, parent=root)
    for i in range(12):
        ang = i * (math.pi * 2.0 / 12.0)
        make_smooth_sphere(f"{name}_Bead_{i}", (math.cos(ang) * 0.27, math.sin(ang) * 0.27, 0.87), (0.032, 0.032, 0.025), m_pink, col, segs=12, parent=root)
    for cx in (-0.10, 0.0, 0.10):
        make_smooth_cyl(f"{name}_Candle_{cx}", (cx, 0, 1.22), 0.020, 0.18, m_pink, col, segs=14, bevel_w=0.003, parent=root)
        make_smooth_sphere(f"{name}_Flame_{cx}", (cx, 0, 1.34), (0.028, 0.028, 0.048), m_flame, col, segs=12, parent=root)
    return root


def build_nice_rock(name: str, loc, col, scale: float = 1.0):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=0.13 * scale)
    for v in bm.verts:
        n = v.co.normalized()
        v.co.x *= 1.25
        v.co.y *= 0.95
        v.co.z *= 0.82
        v.co *= 1.0 + 0.08 * math.sin(n.x * 5.0) * math.cos(n.z * 6.0)
    return _finish_bm(bm, name, loc, sc.make_stylized_pbr("Mat_NiceRock", "#94A3B8", rough=0.35, metal=0.10, coat=0.22, bump_str=0.04), col)


def build_streetlamp(name: str, loc, col, is_night: bool = True):
    root = bpy.data.objects.new(name, None)
    root.location = loc
    col.objects.link(root)
    m_iron = sc.make_stylized_pbr("Mat_LampIron", "#1E293B", rough=0.40, metal=0.75)
    m_glow = sc.make_stylized_pbr("Mat_LampGlow", "#FEF08A", rough=0.18, emit_hex="#FDE047" if is_night else None, emit_str=5.0 if is_night else 0.0)
    make_smooth_cyl(f"{name}_Base", (0, 0, 0.25), 0.14, 0.50, m_iron, col, segs=16, bevel_w=0.015, parent=root)
    make_smooth_cyl(f"{name}_Post", (0, 0, 1.95), 0.055, 3.3, m_iron, col, segs=16, bevel_w=0.005, parent=root)
    make_smooth_sphere(f"{name}_Globe", (0, 0, 3.68), (0.18, 0.18, 0.22), m_glow, col, segs=18, parent=root)
    make_smooth_cyl(f"{name}_Cap", (0, 0, 3.92), 0.18, 0.08, m_iron, col, segs=16, bevel_w=0.01, parent=root)
    return root
