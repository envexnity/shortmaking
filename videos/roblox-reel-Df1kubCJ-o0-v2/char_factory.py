"""
char_factory.py — Authentic Roblox Studio R15 Blocky Character & Rig Factory (Blender 5.3.0).
Every character is built procedurally in pure bmesh at true SI scale (~1.75m tall) matching Roblox Studio
R15 blocky proportions (beveled rectangular torso, head, 2-segment arms, legs, square hands, UV-mapped
2-half Roblox shirt/pants/sneaker atlases, blocky/structured Roblox UGC hair & hats, and BIG crisp
solid-black glossy-oval Roblox face decals with 4-frame blinking).

Convention: At yaw_deg=0, characters stand on z=0 facing +Y (toward cameras placed at +Y).
"""
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

PROJ_DIR = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking\videos\roblox-reel-Df1kubCJ-o0-v2")
TEX_CHARS = PROJ_DIR / "textures" / "chars"
sys.path.insert(0, str(PROJ_DIR))
import scene_common as sc


def _bind_bone(obj, arm_obj, bone_name: str):
    obj.parent = arm_obj
    obj.parent_type = "BONE"
    obj.parent_bone = bone_name
    b = arm_obj.data.bones[bone_name]
    obj.matrix_parent_inverse = (arm_obj.matrix_world @ Matrix.Translation(b.tail_local) @ b.matrix_local.to_3x3().to_4x4()).inverted()


def _make_rounded_box(name: str, size: tuple, center: tuple, bevel_w: float, segs: int, mat, col, parent_arm=None, bone_name=None, rot=(0, 0, 0)):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    sx, sy, sz = size
    cx, cy, cz = center
    rot_m = Euler(rot, "XYZ").to_matrix() if any(abs(a) > 1e-6 for a in rot) else None
    for v in bm.verts:
        p = Vector((v.co.x * sx, v.co.y * sy, v.co.z * sz))
        if rot_m is not None:
            p = rot_m @ p
        v.co = p + Vector((cx, cy, cz))
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    obj.data.materials.append(mat)
    if bevel_w > 0:
        sc.smooth_bevel(obj, width=bevel_w, segments=segs, angle_deg=32.0)
    if parent_arm and bone_name:
        _bind_bone(obj, parent_arm, bone_name)
    return obj


def _make_uv_roblox_block(
    name: str,
    size: tuple,
    center: tuple,
    bevel_w: float,
    segs: int,
    mat,
    col,
    parent_arm=None,
    bone_name: str | None = None,
    fabric_only: bool = False,
):
    """
    Create a crisp beveled Roblox Studio R15 body block with WYSIWYG 2-half UV mapping:
      - Front (+Y): left half [0.02..0.48], right-reading (+X viewer-left -> left of PNG)
      - Back (-Y):  right half [0.52..0.98]
      - Sides (±X): clean back-half [0.56..0.94] preserving Z so waistbands/shoes wrap all around
      - fabric_only=True: maps all faces cleanly into back-half fabric weave [0.60..0.90] x [0.30..0.80]
    Subdivided 2x before bevel so interior UVs have zero bevel distortion.
    """
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    sx, sy, sz = size
    cx, cy, cz = center
    for v in bm.verts:
        v.co.x = v.co.x * sx + cx
        v.co.y = v.co.y * sy + cy
        v.co.z = v.co.z * sz + cz

    bmesh.ops.subdivide_edges(bm, edges=list(bm.edges), cuts=2, use_grid_fill=True)
    uv_layer = bm.loops.layers.uv.new("UVMap")

    for f in bm.faces:
        ny, nx, nz = f.normal.y, f.normal.x, f.normal.z
        for lp in f.loops:
            vx, vy, vz = lp.vert.co
            ux_raw = max(0.0, min(1.0, 0.5 - (vx - cx) / max(0.01, sx)))
            ux_back = max(0.0, min(1.0, 0.5 + (vx - cx) / max(0.01, sx)))
            uy_raw = max(0.0, min(1.0, (vy - cy) / max(0.01, sy) + 0.5))
            vz_raw = max(0.0, min(1.0, (vz - cz) / max(0.01, sz) + 0.5))

            if fabric_only:
                u = 0.60 + 0.30 * (ux_raw if abs(ny) > 0.5 else uy_raw)
                v = 0.30 + 0.50 * vz_raw
            elif ny > 0.75:
                u = 0.02 + 0.46 * ux_raw
                v = 0.01 + 0.98 * vz_raw
            elif ny < -0.75:
                u = 0.52 + 0.46 * ux_back
                v = 0.01 + 0.98 * vz_raw
            elif abs(nx) > 0.75:
                u = 0.56 + 0.38 * uy_raw
                v = 0.01 + 0.98 * vz_raw
            else:
                u = 0.75
                v = 0.95 if nz > 0 else 0.03
            lp[uv_layer].uv = (u, v)

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    obj.data.materials.append(mat)
    if bevel_w > 0:
        sc.smooth_bevel(obj, width=bevel_w, segments=segs, angle_deg=32.0)
    if parent_arm and bone_name:
        _bind_bone(obj, parent_arm, bone_name)
    return obj


def _make_head_with_face_uv(name: str, skin_hex: str, face_png: Path, col, parent_arm, bone_name="Head"):
    """
    Create a crisp beveled Roblox Studio block head (0.43 x 0.37 x 0.41m) centered at (0, 0, 1.545)
    with right-reading front (+Y) UV mapping for BIG, crisp Roblox eyes/brows/mouth decals!
    """
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    w, d, h = 0.43, 0.37, 0.41
    cz = 1.545
    for v in bm.verts:
        v.co.x *= w
        v.co.y *= d
        v.co.z = v.co.z * h + cz

    bmesh.ops.subdivide_edges(bm, edges=list(bm.edges), cuts=2, use_grid_fill=True)
    uv_layer = bm.loops.layers.uv.new("UVMap")
    u_span = w * 1.15
    v_span = h * 1.12
    for f in bm.faces:
        if f.normal.y > 0.75:
            for lp in f.loops:
                vx, _, vz = lp.vert.co
                u = 0.5 - (vx / u_span)  # Right-reading: viewer-left (+X) -> u < 0.5
                v = ((vz - (cz - 0.015)) / v_span) + 0.5
                lp[uv_layer].uv = (u, v)
        else:
            for lp in f.loops:
                lp[uv_layer].uv = (0.01, 0.01)

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    mat, tex_node = sc.make_skin_face_mat(f"Mat_{name}_Head", skin_hex, face_png)
    obj.data.materials.append(mat)
    sc.smooth_bevel(obj, width=0.032, segments=4, angle_deg=32.0)
    _bind_bone(obj, parent_arm, bone_name)
    return obj, mat, tex_node


def _prim(kind: str, name: str, loc: tuple, scale: tuple, mat, col, parent_arm, bone_name: str, rot=(0, 0, 0), segs=24):
    """Pure-bmesh primitive with scale + rotation baked into vertices around `loc` BEFORE bone binding."""
    bm = bmesh.new()
    if kind == "SPH":
        bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=max(8, segs // 2), radius=1.0)
    elif kind == "CYL":
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=1.0, radius2=1.0, depth=1.0)
    elif kind == "CONE":
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=1.0, radius2=0.12, depth=1.0)
    elif kind == "TORUS":
        maj, mn = 1.0, 0.22
        m_segs, n_segs = segs, 10
        rings = []
        for i in range(m_segs):
            th = (i / m_segs) * 2.0 * math.pi
            ct, st = math.cos(th), math.sin(th)
            ring = []
            for j in range(n_segs):
                ph = (j / n_segs) * 2.0 * math.pi
                r = maj + mn * math.cos(ph)
                ring.append(bm.verts.new((r * ct, r * st, mn * math.sin(ph))))
            rings.append(ring)
        for i in range(m_segs):
            ni = (i + 1) % m_segs
            for j in range(n_segs):
                nj = (j + 1) % n_segs
                bm.faces.new((rings[i][j], rings[ni][j], rings[ni][nj], rings[i][nj]))
    else:
        bmesh.ops.create_cube(bm, size=1.0)

    sx, sy, sz = scale
    rot_m = Euler(rot, "XYZ").to_matrix() if any(abs(a) > 1e-6 for a in rot) else None
    off = Vector(loc)
    for v in bm.verts:
        p = Vector((v.co.x * sx, v.co.y * sy, v.co.z * sz))
        if rot_m is not None:
            p = rot_m @ p
        v.co = p + off

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    o = bpy.data.objects.new(name, mesh)
    col.objects.link(o)
    for p in o.data.polygons:
        p.use_smooth = True
    if mat:
        o.data.materials.append(mat)
    if parent_arm and bone_name:
        _bind_bone(o, parent_arm, bone_name)
    return o


def _build_armature(name: str, col):
    """Exact Roblox Studio R15 Blocky Rig (~1.75m tall, shoulders at x=+-0.435, hips at x=+-0.150)."""
    arm_d = bpy.data.armatures.new(f"{name}_ArmData")
    arm = bpy.data.objects.new(f"{name}_Rig", arm_d)
    col.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm_d.edit_bones

    def add_b(bname, head, tail, parent=None, connected=False, align_vec=(0, 1, 0)):
        b = eb.new(bname)
        b.head = head
        b.tail = tail
        b.use_connect = connected
        if align_vec is not None:
            b.align_roll(Vector(align_vec))
        if parent:
            b.parent = parent
        return b

    root = add_b("Root", (0, 0, 0), (0, 0, 0.20))
    pelvis = add_b("Pelvis", (0, 0, 0.70), (0, 0, 0.86), root)
    torso = add_b("Torso", (0, 0, 0.70), (0, 0, 1.32), pelvis)
    add_b("Head", (0, 0, 1.34), (0, 0, 1.75), torso)

    # With align_roll((0,1,0)) on -Z bones, POSITIVE X rot swings forward (+Y) toward viewer!
    arm_lu = add_b("Arm_L_Upper", (0.435, 0, 1.24), (0.435, 0, 1.01), torso)
    add_b("Arm_L_Lower", (0.435, 0, 1.01), (0.435, 0, 0.68), arm_lu, connected=True)
    arm_ru = add_b("Arm_R_Upper", (-0.435, 0, 1.24), (-0.435, 0, 1.01), torso)
    add_b("Arm_R_Lower", (-0.435, 0, 1.01), (-0.435, 0, 0.68), arm_ru, connected=True)

    add_b("Leg_L", (0.150, 0, 0.70), (0.150, 0, 0.04), pelvis)
    add_b("Leg_R", (-0.150, 0, 0.70), (-0.150, 0, 0.04), pelvis)

    bpy.ops.object.mode_set(mode="OBJECT")
    return arm


def _add_r15_legs(prefix: str, col, arm, pants_mat, sole_hex="#F1F5F9"):
    """Crisp beveled Roblox R15 leg blocks with stitched denim/slacks/sneaker UVs + flat sole."""
    m_sole = sc.make_stylized_pbr(f"Mat_{prefix}_Sole_{sole_hex}", sole_hex, rough=0.55, coat=0.04)
    for side, sx, bname in [("L", 0.150, "Leg_L"), ("R", -0.150, "Leg_R")]:
        _make_uv_roblox_block(
            f"{prefix}_Leg_{side}", (0.282, 0.288, 0.676), (sx, 0.0, 0.362),
            0.018, 3, pants_mat, col, arm, bname, fabric_only=False,
        )
        _make_rounded_box(
            f"{prefix}_Sole_{side}", (0.286, 0.302, 0.026), (sx, 0.004, 0.013),
            0.007, 2, m_sole, col, arm, bname,
        )


def _add_r15_arms(prefix: str, col, arm, skin_mat, sleeve_mat, short_sleeve=True, dress_cuff_mat=None):
    """Authentic crisp beveled Roblox Studio R15 2-segment blocky arms & square hands."""
    for side, sx, ub, lb in [("L", 0.435, "Arm_L_Upper", "Arm_L_Lower"), ("R", -0.435, "Arm_R_Upper", "Arm_R_Lower")]:
        if short_sleeve:
            _make_uv_roblox_block(
                f"{prefix}_Sleeve_{side}", (0.268, 0.268, 0.215), (sx, 0, 1.212),
                0.016, 3, sleeve_mat, col, arm, ub, fabric_only=True,
            )
            _make_uv_roblox_block(
                f"{prefix}_SleeveHem_{side}", (0.272, 0.272, 0.020), (sx, 0, 1.112),
                0.005, 2, sleeve_mat, col, arm, ub, fabric_only=True,
            )
            _make_rounded_box(
                f"{prefix}_UpperArm_{side}", (0.252, 0.252, 0.106), (sx, 0, 1.058),
                0.016, 3, skin_mat, col, arm, ub,
            )
            _make_rounded_box(
                f"{prefix}_Forearm_{side}", (0.250, 0.250, 0.220), (sx, 0, 0.900),
                0.016, 3, skin_mat, col, arm, lb,
            )
        else:
            _make_uv_roblox_block(
                f"{prefix}_UpperSleeve_{side}", (0.264, 0.264, 0.312), (sx, 0, 1.164),
                0.016, 3, sleeve_mat, col, arm, ub, fabric_only=True,
            )
            _make_uv_roblox_block(
                f"{prefix}_LowerSleeve_{side}", (0.258, 0.258, 0.220), (sx, 0, 0.900),
                0.016, 3, sleeve_mat, col, arm, lb, fabric_only=True,
            )
            if dress_cuff_mat:
                _make_rounded_box(
                    f"{prefix}_DressCuff_{side}", (0.250, 0.250, 0.026), (sx, 0, 0.798),
                    0.006, 2, dress_cuff_mat, col, arm, lb,
                )
        # Crisp blocky Roblox R15 Hand
        _make_rounded_box(
            f"{prefix}_Hand_{side}", (0.242, 0.242, 0.112), (sx, 0, 0.734),
            0.016, 3, skin_mat, col, arm, lb,
        )


def _add_party_hat(prefix: str, col, arm, z_base=1.76, hat_hex="#EC4899", stripe_hex="#FACC15", scale=1.0):
    m_hat = sc.make_stylized_pbr(f"Mat_{prefix}_PHat_{hat_hex}", hat_hex, rough=0.36, coat=0.22)
    m_band = sc.make_stylized_pbr(f"Mat_{prefix}_PBand_{stripe_hex}", stripe_hex, rough=0.36, coat=0.25)
    m_pom = sc.make_stylized_pbr(f"Mat_{prefix}_PPom", "#FEF08A", rough=0.60, sheen=0.4)
    _prim("CONE", f"{prefix}_PHCone", (0, -0.01, z_base + 0.19 * scale), (0.13 * scale, 0.13 * scale, 0.42 * scale), m_hat, col, arm, "Head", segs=24)
    _prim("TORUS", f"{prefix}_PHBand", (0, -0.01, z_base + 0.03 * scale), (0.125 * scale, 0.125 * scale, 0.06 * scale), m_band, col, arm, "Head", segs=24)
    _prim("SPH", f"{prefix}_PHPom", (0, -0.01, z_base + 0.41 * scale), (0.055 * scale, 0.055 * scale, 0.055 * scale), m_pom, col, arm, "Head", segs=16)


def _add_alex_hair_and_cap(prefix: str, col, arm):
    """Chunky Roblox UGC brown swept hair hugging square head + Red Roblox Baseball Cap."""
    m_hair = sc.make_stylized_pbr(f"Mat_{prefix}_Hair", "#3E2416", rough=0.46, coat=0.06)
    m_cap = sc.make_stylized_pbr(f"Mat_{prefix}_CapRed", "#C41E1E", rough=0.56, coat=0.08, sheen=0.28)
    m_cap_d = sc.make_stylized_pbr(f"Mat_{prefix}_CapDark", "#8B1414", rough=0.60, coat=0.05)

    # Top crown, back slab, and sideburn hair slabs hugging square 0.43 x 0.37 head
    _make_rounded_box(f"{prefix}_HairTop", (0.452, 0.392, 0.088), (0.0, -0.005, 1.725), 0.022, 3, m_hair, col, arm, "Head")
    _make_rounded_box(f"{prefix}_HairBack", (0.452, 0.058, 0.29), (0.0, -0.194, 1.595), 0.018, 3, m_hair, col, arm, "Head")
    for sx in (-0.222, 0.222):
        _make_rounded_box(f"{prefix}_HairSide_{sx}", (0.048, 0.27, 0.21), (sx, -0.048, 1.625), 0.015, 2, m_hair, col, arm, "Head")
    # 5 structured chunky Roblox fringe bangs well above brows (z >= 1.67)
    for bi, (fx, fw, fz, rz) in enumerate([(-0.145, 0.09, 1.695, 12), (-0.065, 0.10, 1.685, 6), (0.01, 0.10, 1.690, -4), (0.095, 0.095, 1.685, -10), (0.165, 0.08, 1.700, -14)]):
        _make_rounded_box(f"{prefix}_Bang_{bi}", (fw, 0.065, 0.085), (fx, 0.186, fz), 0.016, 2, m_hair, col, arm, "Head", rot=(math.radians(8), math.radians(rz), 0))

    # Structured Roblox UGC Red Cap + front visor brim
    _make_rounded_box(f"{prefix}_CapDome", (0.465, 0.415, 0.150), (0.0, -0.01, 1.815), 0.055, 4, m_cap, col, arm, "Head")
    _make_rounded_box(f"{prefix}_CapPanel", (0.28, 0.04, 0.10), (0.0, 0.182, 1.795), 0.015, 2, m_cap, col, arm, "Head")
    _prim("SPH", f"{prefix}_CapBtn", (0.0, -0.01, 1.894), (0.032, 0.032, 0.018), m_cap_d, col, arm, "Head", segs=14)
    _make_rounded_box(f"{prefix}_CapBrim", (0.435, 0.275, 0.026), (0.0, 0.215, 1.742), 0.010, 3, m_cap, col, arm, "Head", rot=(math.radians(6), 0, 0))
    _make_rounded_box(f"{prefix}_CapBrimTrim", (0.440, 0.278, 0.010), (0.0, 0.216, 1.734), 0.004, 2, m_cap_d, col, arm, "Head", rot=(math.radians(6), 0, 0))


def _add_mustache(prefix: str, col, arm, hex_col="#261B17", z=1.482):
    m = sc.make_stylized_pbr(f"Mat_{prefix}_Mustache", hex_col, rough=0.45)
    _prim("SPH", f"{prefix}_MustL", (0.048, 0.192, z), (0.054, 0.024, 0.020), m, col, arm, "Head", rot=(0, math.radians(-14), 0), segs=14)
    _prim("SPH", f"{prefix}_MustR", (-0.048, 0.192, z), (0.054, 0.024, 0.020), m, col, arm, "Head", rot=(0, math.radians(14), 0), segs=14)


def create_character(kind: str, name: str, col, party_hat: str | None = None):
    """
    Build a complete Roblox Studio R15 Blocky character with UV-mapped 2-half shirt/pants atlases,
    blocky Roblox arms/legs/square hands, Roblox UGC accessories, and BIG crisp dark-oval Roblox face decal.
    kind: 'alex' | 'manager' | 'mayor' | 'neighbor' | 'rock_guy' | 'grandma' | 'teal_friend' | 'mint_girl' | 'purple_hoodie'
    """
    char_col = bpy.data.collections.new(name)
    col.children.link(char_col)
    arm = _build_armature(name, char_col)

    skin_map = {
        "alex": "#F2C6A0",
        "manager": "#D9A378",
        "mayor": "#ECC4A2",
        "neighbor": "#F2C6A0",
        "rock_guy": "#C68B59",
        "grandma": "#EAC09E",
        "teal_friend": "#C98D60",
        "mint_girl": "#F3C8A6",
        "purple_hoodie": "#A46B46",
    }
    face_map = {
        "alex": "alex_determined.png",
        "manager": "manager_happy_welcome.png",
        "mayor": "mayor_party_cheer.png",
        "neighbor": "neighbor_grin.png",
        "rock_guy": "crowd_rock_guy.png",
        "grandma": "crowd_grandma.png",
        "teal_friend": "crowd_happy_1.png",
        "mint_girl": "crowd_happy_2.png",
        "purple_hoodie": "crowd_happy_1.png",
    }
    sole_map = {
        "alex": "#F1F5F9",
        "manager": "#18181B",
        "mayor": "#18181B",
        "neighbor": "#F1F5F9",
        "rock_guy": "#F1F5F9",
        "grandma": "#27272A",
        "teal_friend": "#F1F5F9",
        "mint_girl": "#F1F5F9",
        "purple_hoodie": "#F1F5F9",
    }

    skin_hex = skin_map[kind]
    m_skin = sc.make_stylized_pbr(f"Mat_{name}_Skin", skin_hex, rough=0.42, coat=0.05, sss=0.10)
    head_obj, head_mat, face_tex_node = _make_head_with_face_uv(
        f"{name}_Head", skin_hex, sc.TEX_FACES / face_map[kind], char_col, arm, "Head"
    )
    # Recessed neck peg connecting Torso to Head
    _prim("CYL", f"{name}_Neck", (0, 0, 1.332), (0.102, 0.102, 0.065), m_skin, char_col, arm, "Torso", segs=20)

    # UV-mapped Roblox 2-half Shirt & Pants materials
    shirt_tex = TEX_CHARS / f"shirt_{kind}.png"
    shirt_bump = TEX_CHARS / f"shirt_{kind}_bump.png"
    pants_tex = TEX_CHARS / f"pants_{kind}.png"
    pants_bump = TEX_CHARS / f"pants_{kind}_bump.png"

    m_shirt = sc.make_textured_pbr(
        f"Mat_{name}_ShirtUV", shirt_tex, shirt_bump, proj="UV",
        uv_scale=(1.0, 1.0, 1.0), rough_min=0.58, rough_max=0.76, coat=0.0, ao_str=0.16, bump_strength=0.10,
    )
    m_pants = sc.make_textured_pbr(
        f"Mat_{name}_PantsUV", pants_tex, pants_bump, proj="UV",
        uv_scale=(1.0, 1.0, 1.0), rough_min=0.56, rough_max=0.76, coat=0.0, ao_str=0.16, bump_strength=0.10,
    )

    # Core Roblox R15 Torso + Legs + Arms
    _make_uv_roblox_block(f"{name}_Torso", (0.59, 0.30, 0.62), (0.0, 0.0, 1.01), 0.020, 3, m_shirt, char_col, arm, "Torso")
    _add_r15_legs(name, char_col, arm, m_pants, sole_hex=sole_map[kind])

    extras = {}

    if kind == "alex":
        _add_r15_arms(name, char_col, arm, m_skin, m_shirt, short_sleeve=True)
        _add_alex_hair_and_cap(name, char_col, arm)

    elif kind == "manager":
        m_white = sc.make_stylized_pbr(f"Mat_{name}_CuffW", "#F8FAFC", rough=0.45)
        m_tie = sc.make_stylized_pbr(f"Mat_{name}_TieGold", "#FACC15", rough=0.28, coat=0.22)
        m_hair = sc.make_stylized_pbr(f"Mat_{name}_Hair", "#281C18", rough=0.46)
        _add_r15_arms(name, char_col, arm, m_skin, m_shirt, short_sleeve=False, dress_cuff_mat=m_white)

        # Thin 3D swappable Gold Tie + Wrapped Tie Gag sitting flush on front (+Y=0.156) of Torso
        _make_rounded_box(f"{name}_TieKnot", (0.068, 0.024, 0.055), (0, 0.158, 1.245), 0.008, 2, m_tie, char_col, arm, "Torso")
        tie_blade = _make_rounded_box(f"{name}_TieBlade", (0.072, 0.018, 0.27), (0, 0.157, 1.085), 0.008, 2, m_tie, char_col, arm, "Torso")

        m_wrap_y = sc.make_stylized_pbr(f"Mat_{name}_TieWrapY", "#ECAE20", rough=0.50, coat=0.0)
        m_wrap_r = sc.make_stylized_pbr(f"Mat_{name}_TieWrapR", "#D42A18", rough=0.46, coat=0.0)
        tie_wrap = _make_rounded_box(f"{name}_TieWrapped", (0.125, 0.048, 0.34), (0, 0.165, 1.115), 0.014, 3, m_wrap_y, char_col, arm, "Torso")
        tie_wrap_stripe = _make_rounded_box(f"{name}_TieWrapStripe", (0.129, 0.052, 0.052), (0, 0.166, 1.115), 0.006, 2, m_wrap_r, char_col, arm, "Torso")
        extras["tie_wrapped"] = tie_wrap
        extras["tie_wrap_stripe"] = tie_wrap_stripe
        extras["tie_blade"] = tie_blade

        # Side/back curls hugging square head (bald smooth top matching OG!) + neat mustache
        for sx in (-0.222, 0.222):
            for az, ay in [(1.62, 0.01), (1.55, -0.06), (1.65, -0.08)]:
                _prim("SPH", f"{name}_Curl_{sx}_{az}", (sx, ay, az), (0.052, 0.072, 0.072), m_hair, char_col, arm, "Head", segs=14)
        _make_rounded_box(f"{name}_BackHair", (0.44, 0.055, 0.21), (0, -0.194, 1.595), 0.018, 2, m_hair, char_col, arm, "Head")
        _add_mustache(name, char_col, arm, hex_col="#261B17", z=1.482)

    elif kind == "mayor":
        m_white = sc.make_stylized_pbr(f"Mat_{name}_CuffW", "#F8FAFC", rough=0.45)
        m_sash = sc.make_stylized_pbr(f"Mat_{name}_Sash", "#6D28D9", rough=0.38, sheen=0.50)
        m_gold = sc.make_stylized_pbr(f"Mat_{name}_Gold", "#F59E0B", rough=0.22, metal=0.80, coat=0.30)
        m_tophat = sc.make_stylized_pbr(f"Mat_{name}_TopHat", "#14161D", rough=0.30, coat=0.22)
        m_gray_h = sc.make_stylized_pbr(f"Mat_{name}_GrayHair", "#B8C0CC", rough=0.48)
        _add_r15_arms(name, char_col, arm, m_skin, m_shirt, short_sleeve=False, dress_cuff_mat=m_white)

        # Diagonal Sash hugging front/back of 0.30m blocky Torso cleanly
        _make_rounded_box(f"{name}_Sash", (0.112, 0.322, 0.65), (0.0, 0.0, 1.00), 0.012, 2, m_sash, char_col, arm, "Torso", rot=(0, math.radians(-38), 0))
        _make_rounded_box(f"{name}_SashGold", (0.138, 0.312, 0.645), (0.0, 0.0, 1.00), 0.010, 2, m_gold, char_col, arm, "Torso", rot=(0, math.radians(-38), 0))
        _prim("CYL", f"{name}_Rosette", (-0.195, 0.165, 0.81), (0.064, 0.064, 0.024), m_gold, char_col, arm, "Torso", rot=(math.radians(90), 0, 0), segs=20)

        for x in (-0.17, -0.09, 0.0, 0.09, 0.17):
            _prim("SPH", f"{name}_HairF_{x:.2f}", (x, 0.175, 1.715), (0.056, 0.050, 0.048), m_gray_h, char_col, arm, "Head", segs=12)
        for sx in (-0.222, 0.222):
            _make_rounded_box(f"{name}_HairS_{sx}", (0.046, 0.26, 0.16), (sx, -0.03, 1.63), 0.014, 2, m_gray_h, char_col, arm, "Head")
        _add_mustache(name, char_col, arm, hex_col="#9CA3AF", z=1.482)
        _prim("CYL", f"{name}_TopHatBrim", (0, 0, 1.765), (0.29, 0.29, 0.030), m_tophat, char_col, arm, "Head", segs=32)
        _prim("CYL", f"{name}_TopHatCrown", (0, 0, 1.96), (0.195, 0.195, 0.36), m_tophat, char_col, arm, "Head", segs=32)
        _prim("CYL", f"{name}_TopHatBand", (0, 0, 1.805), (0.202, 0.202, 0.052), m_gold, char_col, arm, "Head", segs=32)
        _add_party_hat(name, char_col, arm, z_base=2.14, hat_hex="#06B6D4", stripe_hex="#EC4899", scale=0.82)

    elif kind == "neighbor":
        m_ginger = sc.make_stylized_pbr(f"Mat_{name}_Ginger", "#C2591C", rough=0.50, coat=0.02)
        _add_r15_arms(name, char_col, arm, m_skin, m_shirt, short_sleeve=True)
        _make_rounded_box(f"{name}_HairTop", (0.45, 0.39, 0.075), (0, -0.01, 1.73), 0.020, 2, m_ginger, char_col, arm, "Head")
        _make_rounded_box(f"{name}_HairBack", (0.44, 0.052, 0.24), (0, -0.192, 1.61), 0.015, 2, m_ginger, char_col, arm, "Head")
        for i in range(7):
            fx = -0.15 + i * 0.05
            _prim("CONE", f"{name}_Spike_{i}", (fx, 0.185, 1.71), (0.048, 0.045, 0.12), m_ginger, char_col, arm, "Head", rot=(0.32, -fx * 1.3, 0), segs=12)
        for sx in (-0.220, 0.220):
            _make_rounded_box(f"{name}_SideH_{sx}", (0.044, 0.24, 0.18), (sx, -0.03, 1.63), 0.014, 2, m_ginger, char_col, arm, "Head")
        _add_party_hat(name, char_col, arm, z_base=1.78, hat_hex="#14B8A6", stripe_hex="#FACC15", scale=1.05)

        m_red = sc.make_stylized_pbr(f"Mat_{name}_BlowerRed", "#EF4444", rough=0.35)
        m_wht = sc.make_stylized_pbr(f"Mat_{name}_BlowerWht", "#F8FAFC", rough=0.38)
        _prim("CYL", f"{name}_Blower", (-0.04, 0.295, 1.41), (0.024, 0.024, 0.24), m_red, char_col, arm, "Head", rot=(math.radians(82), 0, math.radians(-18)), segs=14)
        _prim("CYL", f"{name}_BlowerTip", (-0.075, 0.405, 1.395), (0.028, 0.028, 0.06), m_wht, char_col, arm, "Head", rot=(math.radians(82), 0, math.radians(-18)), segs=14)

        m_cup = sc.make_stylized_pbr(f"Mat_{name}_PartyCup", "#06B6D4", rough=0.25, coat=0.30)
        _prim("CYL", f"{name}_Cup", (-0.435, 0.14, 0.72), (0.088, 0.088, 0.20), m_cup, char_col, arm, "Arm_R_Lower", rot=(math.radians(15), 0, 0), segs=20)
        _prim("CYL", f"{name}_CupLid", (-0.435, 0.16, 0.81), (0.098, 0.098, 0.022), m_wht, char_col, arm, "Arm_R_Lower", rot=(math.radians(15), 0, 0), segs=20)
        _prim("CYL", f"{name}_Straw", (-0.435, 0.18, 0.89), (0.012, 0.012, 0.16), m_red, char_col, arm, "Arm_R_Lower", rot=(math.radians(25), 0, 0), segs=10)

    else:
        _add_r15_arms(name, char_col, arm, m_skin, m_shirt, short_sleeve=False)

        if kind == "rock_guy":
            m_beanie = sc.make_textured_pbr(f"Mat_{name}_Beanie", sc.TEX_ENV / "fabric_knit_rib.png", sc.TEX_ENV / "fabric_knit_rib_bump.png", tint_hex="#94A3B8", uv_scale=(2.6, 2.6, 2.6), rough_min=0.70, rough_max=0.88, coat=0.0, sheen=0.45)
            m_beard = sc.make_stylized_pbr(f"Mat_{name}_Beard", "#18181B", rough=0.50, coat=0.0)
            _make_rounded_box(f"{name}_BeanieDome", (0.46, 0.41, 0.16), (0, -0.01, 1.80), 0.058, 4, m_beanie, char_col, arm, "Head")
            _make_rounded_box(f"{name}_BeanieCuff", (0.475, 0.425, 0.065), (0, -0.01, 1.725), 0.022, 3, m_beanie, char_col, arm, "Head")
            _prim("SPH", f"{name}_BeaniePom", (0, -0.01, 1.895), (0.055, 0.055, 0.055), sc.make_stylized_pbr("Mat_PomW", "#F1F5F9", coat=0.0), char_col, arm, "Head", segs=14)
            _prim("CONE", f"{name}_Goatee", (0, 0.182, 1.33), (0.072, 0.048, 0.14), m_beard, char_col, arm, "Head", rot=(math.radians(175), 0, 0), segs=14)

        elif kind == "grandma":
            m_gh = sc.make_stylized_pbr(f"Mat_{name}_WhiteHair", "#E2E8F0", rough=0.55, coat=0.0)
            m_spec = sc.make_stylized_pbr(f"Mat_{name}_Specs", "#334155", rough=0.25, metal=0.8)
            _make_rounded_box(f"{name}_HairCap", (0.45, 0.40, 0.085), (0, -0.01, 1.735), 0.024, 3, m_gh, char_col, arm, "Head")
            for cx_g in (-0.16, -0.09, -0.03, 0.03, 0.09, 0.16):
                _prim("SPH", f"{name}_GrandmaCurl_{cx_g:.2f}", (cx_g, 0.175, 1.715), (0.052, 0.046, 0.046), m_gh, char_col, arm, "Head", segs=12)
            for sx in (-0.222, 0.222):
                _make_rounded_box(f"{name}_GrandmaSide_{sx}", (0.048, 0.26, 0.18), (sx, -0.02, 1.63), 0.015, 2, m_gh, char_col, arm, "Head")
            _prim("SPH", f"{name}_TopBun", (0, -0.05, 1.845), (0.11, 0.11, 0.088), m_gh, char_col, arm, "Head", segs=18)
            for gx in (-0.076, 0.076):
                _prim("TORUS", f"{name}_Spec_{gx}", (gx, 0.194, 1.545), (0.058, 0.058, 0.016), m_spec, char_col, arm, "Head", rot=(math.radians(90), 0, 0), segs=20)
            _make_rounded_box(f"{name}_SpecBridge", (0.04, 0.014, 0.014), (0, 0.194, 1.545), 0.004, 2, m_spec, char_col, arm, "Head")

        elif kind == "teal_friend":
            m_bl = sc.make_stylized_pbr(f"Mat_{name}_BlondeCurls", "#FACC15", rough=0.45)
            _make_rounded_box(f"{name}_HairBase", (0.45, 0.39, 0.075), (0, -0.01, 1.735), 0.022, 2, m_bl, char_col, arm, "Head")
            for i in range(9):
                ang = (i / 9.0) * math.pi * 2.0
                _prim("SPH", f"{name}_Curl_{i}", (math.cos(ang) * 0.16, math.sin(ang) * 0.145, 1.755), (0.082, 0.082, 0.082), m_bl, char_col, arm, "Head", segs=14)
            _prim("SPH", f"{name}_CurlTop", (0, 0, 1.805), (0.125, 0.115, 0.075), m_bl, char_col, arm, "Head", segs=16)

        elif kind == "mint_girl":
            m_dk = sc.make_stylized_pbr(f"Mat_{name}_DarkHair", "#1E1B18", rough=0.42)
            _make_rounded_box(f"{name}_HairCap", (0.45, 0.40, 0.085), (0, -0.01, 1.735), 0.022, 3, m_dk, char_col, arm, "Head")
            _make_rounded_box(f"{name}_HairBack", (0.45, 0.056, 0.25), (0, -0.194, 1.61), 0.016, 2, m_dk, char_col, arm, "Head")
            for bx in (-0.12, 0.0, 0.12):
                _make_rounded_box(f"{name}_GirlBang_{bx}", (0.13, 0.05, 0.055), (bx, 0.184, 1.705), 0.012, 2, m_dk, char_col, arm, "Head")
            for sx in (-0.255, 0.255):
                _prim("SPH", f"{name}_Pigtail_{sx}", (sx, -0.02, 1.56), (0.072, 0.072, 0.155), m_dk, char_col, arm, "Head", rot=(0, math.radians(-16 if sx > 0 else 16), 0), segs=16)

        elif kind == "purple_hoodie":
            m_dk = sc.make_stylized_pbr(f"Mat_{name}_CoilHair", "#261B17", rough=0.48)
            _make_rounded_box(f"{name}_HairTop", (0.45, 0.39, 0.082), (0, -0.01, 1.735), 0.024, 3, m_dk, char_col, arm, "Head")
            _make_rounded_box(f"{name}_HairBack", (0.45, 0.052, 0.22), (0, -0.192, 1.62), 0.015, 2, m_dk, char_col, arm, "Head")
            m_hood_c = sc.make_stylized_pbr(f"Mat_{name}_HoodRim", "#5B21B6", rough=0.62)
            _make_rounded_box(f"{name}_HoodRim", (0.46, 0.24, 0.07), (0, -0.07, 1.34), 0.022, 3, m_hood_c, char_col, arm, "Torso")

        if party_hat:
            _add_party_hat(name, char_col, arm, z_base=1.76, hat_hex=party_hat, stripe_hex="#FACC15", scale=0.95)

    return {
        "name": name,
        "kind": kind,
        "col": char_col,
        "arm": arm,
        "head_obj": head_obj,
        "head_mat": head_mat,
        "face_tex_node": face_tex_node,
        "extras": extras,
        "_last_face": None,
    }


def set_char_transform(ch: dict, wx: float, wy: float, wz: float, yaw_deg: float):
    arm = ch["arm"]
    arm.location = (wx, wy, wz)
    arm.rotation_mode = "XYZ"
    arm.rotation_euler = (0.0, 0.0, math.radians(yaw_deg))


def pose_char(
    ch: dict,
    pelvis_z: float = 0.0,
    torso_rot=(0, 0, 0),
    head_rot=(0, 0, 0),
    arm_l=(0, 0, 0),
    forearm_l=(0, 0, 0),
    arm_r=(0, 0, 0),
    forearm_r=(0, 0, 0),
    leg_l=(0, 0, 0),
    leg_r=(0, 0, 0),
):
    pbs = ch["arm"].pose.bones

    def set_b(bname, degs, loc=None):
        if bname in pbs:
            pb = pbs[bname]
            pb.rotation_mode = "XYZ"
            pb.rotation_euler = tuple(math.radians(a) for a in degs)
            if loc is not None:
                pb.location = loc

    if "Pelvis" in pbs:
        pbs["Pelvis"].location = (0.0, pelvis_z, 0.0)
    set_b("Torso", torso_rot)
    set_b("Head", head_rot)
    set_b("Arm_L_Upper", arm_l)
    set_b("Arm_L_Lower", forearm_l)
    set_b("Arm_R_Upper", arm_r)
    set_b("Arm_R_Lower", forearm_r)
    set_b("Leg_L", leg_l)
    set_b("Leg_R", leg_r)


def set_face(ch: dict, face_filename: str):
    if ch.get("_last_face") == face_filename:
        return
    p = sc.TEX_FACES / face_filename
    if not p.exists():
        return
    img = bpy.data.images.load(str(p), check_existing=True)
    img.colorspace_settings.name = "sRGB"
    ch["face_tex_node"].image = img
    ch["_last_face"] = face_filename


def set_face_with_blink(ch: dict, base_stem: str, frame_num: int, seed: int = 0):
    """Apply crisp 4-frame periodic blinks when _half/_closed variants exist."""
    period = 56 + (seed * 13) % 27
    phase = (frame_num + seed * 17) % period
    chosen = f"{base_stem}.png"
    if phase in (0, 3) and (sc.TEX_FACES / f"{base_stem}_half.png").exists():
        chosen = f"{base_stem}_half.png"
    elif phase in (1, 2) and (sc.TEX_FACES / f"{base_stem}_closed.png").exists():
        chosen = f"{base_stem}_closed.png"
    set_face(ch, chosen)


def set_pov_arms_only(ch: dict, arms_only: bool):
    """For 1st-person top-down POV shots, hide head/torso/legs so ONLY blocky forearms & hands reach into frame."""
    arm = ch["arm"]
    for obj in arm.children:
        if obj.type != "MESH":
            continue
        is_arm_part = obj.parent_bone in ("Arm_L_Upper", "Arm_L_Lower", "Arm_R_Upper", "Arm_R_Lower")
        hide = arms_only and (not is_arm_part)
        obj.hide_viewport = hide
        obj.hide_render = hide


def animate_party_dance(ch: dict, t: float, phase: float = 0.0, energy: float = 1.0):
    w = 2.0 * math.pi * 2.15 * t + phase
    bob = max(0.0, math.sin(w)) * 0.075 * energy
    sway = math.sin(w * 0.5) * 8.0 * energy
    pose_char(
        ch,
        pelvis_z=bob,
        torso_rot=(math.sin(w) * 5.0, sway * 0.5, sway),
        head_rot=(-6.0 + math.sin(w) * 6.0, -sway * 0.6, math.cos(w * 0.5) * 7.0),
        arm_l=(144.0 + math.sin(w) * 16.0 * energy, 0.0, 20.0),
        forearm_l=(18.0 + math.cos(w) * 14.0, 0.0, 0.0),
        arm_r=(144.0 - math.sin(w) * 16.0 * energy, 0.0, -20.0),
        forearm_r=(18.0 - math.cos(w) * 14.0, 0.0, 0.0),
        leg_l=(math.sin(w) * 14.0 * energy, 0.0, 0.0),
        leg_r=(-math.sin(w) * 14.0 * energy, 0.0, 0.0),
    )
