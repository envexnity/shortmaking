"""
build_scene.py — Step 4: Full 9:16 Roblox R6 Story + Thorfinn Outro in @Arseluz27 Pixel Art Style
(Blender 5.3.0 EEVEE, 270x480 native multi-pass -> 4x 1080x1920 pixel post-process).

Preserves the exact original 2 main R6 avatars (01_Alex_Protagonist as Toby, 02_Noob_BestFriend as Sam)
with classic Roblox faces & grounded IRL outfits for all background characters.

Usage:
  blender.exe --background --disable-autoexec --python build_scene.py -- --stills
  blender.exe --background --disable-autoexec --python build_scene.py -- --range 1 1000
"""
import argparse
import json
import math
import os
import random
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
KIT_DIR = ROOT / "90 Templates & Starter Kits" / "undershine-blender-pixel-kit"
R6_DIR = ROOT / "assets" / "roblox-r6-characters"
CHARS_DIR = R6_DIR / "characters"
TEX_DIR = BASE / "textures"
PASSES_DIR = BASE / "passes"
VOICE_DIR = BASE / "voice"

sys.path.insert(0, str(KIT_DIR))
sys.path.insert(0, str(R6_DIR / "scripts"))

import blender_pixel_lib as bpl  # noqa: E402
from build_characters import MARKET_MANIFEST, RBX_PART_ATTACHMENTS, load_obj_to_blender_mesh  # noqa: E402

FPS = 15
RES_X = 270
RES_Y = 480


def load_beats():
    data = json.loads((VOICE_DIR / "beats.json").read_text(encoding="utf-8"))
    return data


def make_roblox_part_mat(name: str, hex_col: str, rough: float = 0.45, emit_str: float = 0.0, metallic: float = 0.0):
    """Crisp pixel-friendly Roblox material with subtle stud/surface shading."""
    mat = bpy.data.materials.new(name=name)
    if bpy.app.version < (5, 0, 0):
        mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    if emit_str > 0.0:
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = bpl.hex_to_linear(hex_col)
        em.inputs["Strength"].default_value = emit_str
        nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
        return mat

    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = bpl.hex_to_linear(hex_col)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metallic
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.25
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def make_box(name: str, loc, size, mat, col, rot=(0, 0, 0), bevel_w: float = 0.04, studs: bool = False):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    sx, sy, sz = size
    for v in bm.verts:
        v.co.x *= sx
        v.co.y *= sy
        v.co.z *= sz
    if studs and sx >= 1.0 and sy >= 1.0:
        nx = max(1, min(10, int(round(sx / 1.4))))
        ny = max(1, min(10, int(round(sy / 1.4))))
        for ix in range(nx):
            for iy in range(ny):
                px = -sx * 0.5 + (ix + 0.5) * (sx / nx)
                py = -sy * 0.5 + (iy + 0.5) * (sy / ny)
                res = bmesh.ops.create_cone(
                    bm, cap_ends=True, cap_tris=False, segments=10,
                    radius1=0.28, radius2=0.26, depth=0.14
                )
                for v in res["verts"]:
                    v.co.x += px
                    v.co.y += py
                    v.co.z += sz * 0.5 + 0.07
    me = bpy.data.meshes.new(f"{name}_Mesh")
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = loc
    obj.rotation_euler = rot
    col.objects.link(obj)
    obj.data.materials.append(mat)
    if bevel_w > 0 and not studs:
        bev = obj.modifiers.new("Bevel", "BEVEL")
        bev.width = bevel_w
        bev.segments = 1
    return obj


def make_cyl(name: str, loc, r1: float, r2: float, depth: float, mat, col, rot=(0, 0, 0), segs: int = 12):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=r1, radius2=r2, depth=depth)
    me = bpy.data.meshes.new(f"{name}_Mesh")
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = loc
    obj.rotation_euler = rot
    col.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def place_rig_master_control(arm_obj, world_pos: Vector, yaw_deg: float, scale: float = 1.0):
    """Exact world-space placement, world-Z yaw, and uniform scale via MasterControl's rest basis."""
    pb = arm_obj.pose.bones["MasterControl"]
    rest_3x3 = arm_obj.data.bones["MasterControl"].matrix_local.to_3x3()
    inv_3x3 = rest_3x3.inverted()

    pb.location = inv_3x3 @ world_pos
    pb.rotation_mode = "XYZ"
    world_rot = Matrix.Rotation(math.radians(yaw_deg), 3, "Z")
    local_rot = inv_3x3 @ world_rot @ rest_3x3
    pb.rotation_euler = local_rot.to_euler("XYZ")
    pb.scale = (scale, scale, scale)


def key_rig_world(arm_obj, frame: int, world_pos: Vector, yaw_deg: float, scale: float = 1.0):
    place_rig_master_control(arm_obj, world_pos, yaw_deg, scale=scale)
    pb = arm_obj.pose.bones["MasterControl"]
    pb.keyframe_insert(data_path="location", frame=frame)
    pb.keyframe_insert(data_path="rotation_euler", frame=frame)
    pb.keyframe_insert(data_path="scale", frame=frame)


def key_pose_bones(arm_obj, frame: int, pose_dict: dict):
    """pose_dict: {bone_name: (rx, ry, rz)} or {bone_name: (rx, ry, rz, lx, ly, lz)}"""
    pbs = arm_obj.pose.bones
    for bname, vals in pose_dict.items():
        if bname not in pbs:
            continue
        pb = pbs[bname]
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = (math.radians(vals[0]), math.radians(vals[1]), math.radians(vals[2]))
        pb.keyframe_insert(data_path="rotation_euler", frame=frame)
        if len(vals) >= 6:
            pb.location = (vals[3], vals[4], vals[5])
            pb.keyframe_insert(data_path="location", frame=frame)


def spawn_r6_rig(
    char_label: str,
    base_blend_name: str,
    base_col_name: str,
    cast_root,
    atlas_path: Path | None = None,
    strip_accessories: bool = False,
    keep_acc_prefixes: tuple = (),
    extra_hair_key: str | None = None,
    hair_tint_hex: str | None = None,
):
    """Append an official Aeresei R6 character rig, optionally swap atlas/hair, and return rig info dict."""
    blend_path = CHARS_DIR / base_blend_name
    before_cols = set(bpy.data.collections)
    before_objs = set(bpy.data.objects)

    with bpy.data.libraries.load(str(blend_path), link=False) as (data_from, data_to):
        data_to.collections = [base_col_name]

    new_cols = [c for c in bpy.data.collections if c not in before_cols]
    new_objs = [o for o in bpy.data.objects if o not in before_objs]

    top_col = None
    for c in new_cols:
        if c.name.startswith(base_col_name):
            top_col = c
            break
    if top_col is None and new_cols:
        top_col = new_cols[0]
    if top_col:
        top_col.name = f"Col_{char_label}"
        cast_root.children.link(top_col)

    primary_arm = None
    internal_arm = None
    body_parts = {}
    acc_objs = []

    for o in new_objs:
        if o.type == "ARMATURE" and o.name.startswith("__PrimaryArmature"):
            primary_arm = o
            o.name = f"{char_label}_Rig"
            if o.animation_data:
                o.animation_data.action = None
            for pb in o.pose.bones:
                pb.location = (0.0, 0.0, 0.0)
                pb.rotation_mode = "XYZ"
                pb.rotation_euler = (0.0, 0.0, 0.0)
        elif o.type == "ARMATURE" and o.name.startswith("InternalArmature"):
            internal_arm = o
            o.name = f"{char_label}_InternalArm"
        elif o.type == "MESH":
            for pname in ("Head", "Torso", "Left Arm", "Right Arm", "Left Leg", "Right Leg"):
                if o.name.startswith(pname):
                    body_parts[pname] = o
                    break
            if o.name.startswith("Acc_"):
                acc_objs.append(o)

    # Swap body texture atlas if provided (cloning material so each character is isolated)
    if atlas_path is not None and body_parts:
        ref_part = next(iter(body_parts.values()))
        if ref_part.data.materials:
            new_mat = ref_part.data.materials[0].copy()
            new_mat.name = f"Mat_{char_label}_Body"
            img = bpy.data.images.load(str(atlas_path), check_existing=False)
            img.name = f"{char_label}_atlas.png"
            img.colorspace_settings.name = "sRGB"
            img.pack()
            for n in new_mat.node_tree.nodes:
                if n.type == "TEX_IMAGE":
                    n.image = img
                    n.interpolation = "Closest"
                elif n.type == "BSDF_PRINCIPLED":
                    if "Specular IOR Level" in n.inputs:
                        n.inputs["Specular IOR Level"].default_value = 0.22
                    if "Coat Weight" in n.inputs:
                        n.inputs["Coat Weight"].default_value = 0.05
                elif n.type == "MAP_RANGE":
                    n.inputs["To Min"].default_value = 0.42
                    n.inputs["To Max"].default_value = 0.56
            for part_obj in body_parts.values():
                part_obj.data.materials.clear()
                part_obj.data.materials.append(new_mat)
    elif body_parts:
        # Even for original main 2 avatars, tune pixel-crisp roughness & closest tex interpolation
        ref_part = next(iter(body_parts.values()))
        if ref_part.data.materials:
            mat = ref_part.data.materials[0]
            for n in mat.node_tree.nodes:
                if n.type == "TEX_IMAGE":
                    n.interpolation = "Closest"
                elif n.type == "BSDF_PRINCIPLED":
                    if "Specular IOR Level" in n.inputs:
                        n.inputs["Specular IOR Level"].default_value = 0.22
                    if "Coat Weight" in n.inputs:
                        n.inputs["Coat Weight"].default_value = 0.05

    # Clean/filter accessories if needed
    for ao in acc_objs:
        if strip_accessories:
            keep = any(ao.name.startswith(p) for p in keep_acc_prefixes)
            if not keep:
                ao.hide_viewport = True
                ao.hide_render = True
        if hair_tint_hex and not ao.hide_render and ao.data.materials:
            hmat = ao.data.materials[0].copy()
            hmat.name = f"Mat_{char_label}_Hair"
            nt = hmat.node_tree
            for n in nt.nodes:
                if n.type == "BSDF_PRINCIPLED":
                    # Disconnect image if tinting solid hair or multiply warm golden-blonde
                    for ln in list(nt.links):
                        if ln.to_node == n and ln.to_socket.name == "Base Color":
                            nt.links.remove(ln)
                    n.inputs["Base Color"].default_value = bpl.hex_to_linear(hair_tint_hex)
                    n.inputs["Roughness"].default_value = 0.45
            ao.data.materials[0] = hmat

    # Attach optional extra Marketplace hair from manifest
    if extra_hair_key and extra_hair_key in MARKET_MANIFEST and internal_arm and "Head" in body_parts:
        entry = MARKET_MANIFEST[extra_hair_key]
        parsed = entry["parsed"]
        att_name = parsed.get("attachment_name") or "HairAttachment"
        part_name, part_att_pos_rbx = RBX_PART_ATTACHMENTS.get(att_name, ("Head", Vector((0.0, 5.1, 0.0))))
        m_part_att = Matrix.Translation(part_att_pos_rbx)
        cf = parsed.get("attachment_cframe")
        if cf and cf.get("pos"):
            p = cf["pos"]
            r = cf.get("rot") or [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
            m_acc_att = Matrix((
                (r[0][0], r[0][1], r[0][2], p[0]),
                (r[1][0], r[1][1], r[1][2], p[1]),
                (r[2][0], r[2][1], r[2][2], p[2]),
                (0.0, 0.0, 0.0, 1.0),
            ))
        else:
            m_acc_att = Matrix.Identity(4)
        sc = parsed.get("scale", [1.0, 1.0, 1.0])
        off = parsed.get("offset", [0.0, 0.0, 0.0])
        m_weld_rbx = m_part_att @ m_acc_att.inverted()
        m_rbx_to_bl = Matrix.Rotation(math.radians(90.0), 4, "X")

        def xform(v: Vector) -> Vector:
            vh = Vector((v.x * sc[0] + off[0], v.y * sc[1] + off[1], v.z * sc[2] + off[2]))
            return m_rbx_to_bl @ (m_weld_rbx @ vh)

        me = load_obj_to_blender_mesh(entry["files"]["obj"], f"Mesh_{char_label}_{extra_hair_key}", xform)
        acc_obj = bpy.data.objects.new(f"Acc_{char_label}_{extra_hair_key}", me)
        (top_col or cast_root).objects.link(acc_obj)
        mat = make_roblox_part_mat(f"Mat_{char_label}_{extra_hair_key}", hair_tint_hex or "#4B3624", rough=0.45)
        if not hair_tint_hex and entry["files"].get("texture") and os.path.exists(entry["files"]["texture"]):
            nt = mat.node_tree
            bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
            tex = nt.nodes.new("ShaderNodeTexImage")
            im = bpy.data.images.load(entry["files"]["texture"], check_existing=False)
            im.colorspace_settings.name = "sRGB"
            tex.image = im
            tex.interpolation = "Closest"
            nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        acc_obj.data.materials.append(mat)
        c = acc_obj.constraints.new("CHILD_OF")
        c.target = internal_arm
        c.subtarget = "Head"
        for rc in body_parts["Head"].constraints:
            if rc.type == "CHILD_OF" and rc.target == internal_arm and rc.subtarget == "Head":
                c.inverse_matrix = rc.inverse_matrix.copy()
                break

    return {
        "label": char_label,
        "rig": primary_arm,
        "internal": internal_arm,
        "parts": body_parts,
        "col": top_col or cast_root,
    }


def add_head_hood_prop(char_info, col, mat):
    """Attach a blocky hoodie hood shell on Sam's head that can pull/flip back cleanly."""
    # Create empty pivot attached to InternalArmature Head bone at back-top of head
    pivot = bpy.data.objects.new(f"{char_info['label']}_HoodPivot", None)
    col.objects.link(pivot)
    c = pivot.constraints.new("CHILD_OF")
    c.target = char_info["internal"]
    c.subtarget = "Head"
    for rc in char_info["parts"]["Head"].constraints:
        if rc.type == "CHILD_OF" and rc.target == char_info["internal"] and rc.subtarget == "Head":
            c.inverse_matrix = rc.inverse_matrix.copy()
            break
    # Head center in rig coords: (0, 0, 4.5), size (1.2, 1.2, 1.2)
    pivot.location = (0.0, -0.55, 4.65)

    # Hood shell sits over top/sides/brow when rotation_euler.x == 0, flips back at rotation_euler.x == -115 deg
    top = make_box(f"{char_info['label']}_HoodTop", (0.0, 0.52, 0.56), (1.38, 1.42, 0.24), mat, col)
    back = make_box(f"{char_info['label']}_HoodBack", (0.0, -0.10, 0.02), (1.38, 0.22, 1.28), mat, col)
    side_l = make_box(f"{char_info['label']}_HoodSideL", (0.64, 0.45, 0.02), (0.16, 1.28, 1.28), mat, col)
    side_r = make_box(f"{char_info['label']}_HoodSideR", (-0.64, 0.45, 0.02), (0.16, 1.28, 1.28), mat, col)
    brim = make_box(f"{char_info['label']}_HoodBrim", (0.0, 1.15, 0.34), (1.38, 0.22, 0.36), mat, col)
    for part in (top, back, side_l, side_r, brim):
        part.parent = pivot
    return pivot


def attach_shield_to_arm(char_info, col, wood_mat, iron_mat):
    """Attach a Roblox wooden Viking round shield onto Thorfinn's torso/arm for the outro."""
    pivot = bpy.data.objects.new(f"{char_info['label']}_ShieldPivot", None)
    col.objects.link(pivot)
    c = pivot.constraints.new("CHILD_OF")
    c.target = char_info["internal"]
    c.subtarget = "Torso"
    for rc in char_info["parts"]["Torso"].constraints:
        if rc.type == "CHILD_OF" and rc.target == char_info["internal"] and rc.subtarget == "Torso":
            c.inverse_matrix = rc.inverse_matrix.copy()
            break
    pivot.location = (0.15, -0.68, 3.0)
    pivot.rotation_euler = (math.radians(90), math.radians(15), 0.0)
    disc = make_cyl("Thorfinn_ShieldWood", (0, 0, 0), 1.45, 1.45, 0.16, wood_mat, col, segs=14)
    rim = make_cyl("Thorfinn_ShieldRim", (0, 0, 0), 1.54, 1.54, 0.10, iron_mat, col, segs=14)
    boss = make_cyl("Thorfinn_ShieldBoss", (0, 0, -0.10), 0.36, 0.16, 0.22, iron_mat, col, segs=10)
    for p in (disc, rim, boss):
        p.parent = pivot
    return pivot


def attach_cape_to_torso(char_info, col, mat):
    pivot = bpy.data.objects.new(f"{char_info['label']}_CapePivot", None)
    col.objects.link(pivot)
    c = pivot.constraints.new("CHILD_OF")
    c.target = char_info["internal"]
    c.subtarget = "Torso"
    for rc in char_info["parts"]["Torso"].constraints:
        if rc.type == "CHILD_OF" and rc.target == char_info["internal"] and rc.subtarget == "Torso":
            c.inverse_matrix = rc.inverse_matrix.copy()
            break
    pivot.location = (0.0, -0.52, 3.95)
    cape = make_box("Thorfinn_Cape", (0.0, -0.18, -1.65), (2.2, 0.16, 3.3), mat, col, rot=(math.radians(10), 0, 0))
    cape.parent = pivot
    drv = cape.driver_add("rotation_euler", 0).driver
    drv.expression = "0.18 + 0.08 * sin(frame * 0.25)"
    return pivot


def build_sets(scene):
    """Build all 6 Roblox Stud / Pixel Sets spaced 60 units apart along X."""
    sets_col = bpy.data.collections.new("WorldSets")
    scene.collection.children.link(sets_col)

    # Shared Roblox materials
    m_asphalt = make_roblox_part_mat("M_Asphalt", "#303542", rough=0.75)
    m_stripe = make_roblox_part_mat("M_YellowStripe", "#E8B932", rough=0.5)
    m_sidewalk = make_roblox_part_mat("M_Sidewalk", "#9BA1AD", rough=0.65)
    m_brick_wall = make_roblox_part_mat("M_SchoolBrick", "#9E4F45", rough=0.65)
    m_locker = make_roblox_part_mat("M_LockerBlue", "#31639C", rough=0.4)
    m_locker_trim = make_roblox_part_mat("M_LockerDark", "#203B5E", rough=0.5)
    m_grass = make_roblox_part_mat("M_Grass", "#4A8746", rough=0.75)
    m_gravel = make_roblox_part_mat("M_Gravel", "#767980", rough=0.8)
    m_bleacher_wood = make_roblox_part_mat("M_Bleacher", "#A67C52", rough=0.6)
    m_metal = make_roblox_part_mat("M_Metal", "#6A7280", rough=0.35, metallic=0.45)

    m_shop_floor = make_roblox_part_mat("M_ShopFloor", "#42464F", rough=0.7)
    m_shop_wall = make_roblox_part_mat("M_ShopWall", "#5E6470", rough=0.65)
    m_red_tool = make_roblox_part_mat("M_RedTool", "#C93232", rough=0.35)
    m_car_blue = make_roblox_part_mat("M_CarBlue", "#2E5B88", rough=0.3)

    m_hosp_wall = make_roblox_part_mat("M_HospWall", "#E8EEF2", rough=0.6)
    m_hosp_floor = make_roblox_part_mat("M_HospFloor", "#C6D3DC", rough=0.45)
    m_bed_sheet = make_roblox_part_mat("M_BedSheet", "#D5E6F2", rough=0.7)
    m_bed_frame = make_roblox_part_mat("M_BedFrame", "#A5B2BD", rough=0.4)
    m_monitor_glow = make_roblox_part_mat("M_MonitorGlow", "#45C8FF", emit_str=3.5)
    m_pill_orange = make_roblox_part_mat("M_PillOrange", "#FF7B24", emit_str=1.2)
    m_pill_cap = make_roblox_part_mat("M_PillCap", "#F2F4F7", rough=0.4)

    m_apt_wall = make_roblox_part_mat("M_AptWall", "#C2B9AD", rough=0.7)
    m_apt_floor = make_roblox_part_mat("M_AptFloor", "#7C5A40", rough=0.65)
    m_counter = make_roblox_part_mat("M_Counter", "#DCD6CC", rough=0.45)
    m_wood_dark = make_roblox_part_mat("M_WoodDark", "#4D3728", rough=0.6)
    m_door_white = make_roblox_part_mat("M_DoorWhite", "#E5E0D6", rough=0.55)
    m_envelope = make_roblox_part_mat("M_Envelope", "#F0E6CE", rough=0.7)
    m_duffel = make_roblox_part_mat("M_Duffel", "#2D333D", rough=0.7)
    m_coffee_mug = make_roblox_part_mat("M_Mug", "#F2EFE9", rough=0.35)
    m_coffee_dark = make_roblox_part_mat("M_Coffee", "#241610", rough=0.2)

    m_sun_glow = make_roblox_part_mat("M_SunGlow", "#FFE066", emit_str=6.5)
    m_sunset_water = make_roblox_part_mat("M_SunsetWater", "#D67735", rough=0.25)
    m_wheat_gold = make_roblox_part_mat("M_WheatGold", "#B67C32", rough=0.75)

    # ------------------------------------------------------------
    # SET 0 (X=0): School Parking Lot & Locker Hallway
    # ------------------------------------------------------------
    make_box("S0_Asphalt", (0, 0, -0.25), (42, 34, 0.5), m_asphalt, sets_col, studs=True)
    for sx in (-6, 0, 6):
        make_box(f"S0_Line_{sx}", (sx, 2, 0.02), (0.35, 7.0, 0.05), m_stripe, sets_col)
    make_box("S0_Sidewalk", (0, -7.5, 0.15), (40, 6, 0.4), m_sidewalk, sets_col, studs=True)
    make_box("S0_SchoolWall", (0, -10.5, 6.0), (36, 1.2, 12.0), m_brick_wall, sets_col)
    # Lockers along school exterior/hallway wall
    for lx in range(-10, 12, 3):
        make_box(f"S0_Locker_{lx}", (lx, -9.2, 3.2), (2.2, 1.3, 6.2), m_locker, sets_col)
        make_box(f"S0_LockerSlot_{lx}", (lx, -8.52, 4.8), (1.2, 0.08, 0.5), m_locker_trim, sets_col)
    # School front doors
    make_box("S0_DoorFrame", (0, -9.7, 3.5), (4.8, 0.5, 7.0), m_locker_trim, sets_col)
    make_box("S0_CarBody", (-11, 5.5, 1.6), (4.5, 8.5, 2.4), m_car_blue, sets_col)
    make_box("S0_CarCab", (-11, 5.5, 3.3), (4.0, 4.4, 1.6), m_car_blue, sets_col)

    # ------------------------------------------------------------
    # SET 1 (X=60): Bleachers & Gravel Corner + Stoop Walk
    # ------------------------------------------------------------
    make_box("S1_Grass", (60, 0, -0.25), (42, 36, 0.5), m_grass, sets_col, studs=True)
    make_box("S1_Gravel", (60, 0, 0.02), (18, 16, 0.08), m_gravel, sets_col, studs=True)
    # Tiered bleachers behind at Y=-8
    for tier in range(4):
        make_box(f"S1_BleachStep_{tier}", (60, -7.0 - tier * 1.6, 1.1 + tier * 1.1), (18, 1.5, 0.35), m_bleacher_wood, sets_col)
        make_box(f"S1_BleachPost_{tier}", (52 + tier * 5.2, -9.5, 2.4), (0.4, 5.5, 4.8), m_metal, sets_col)
    # Stoop/porch steps at X=68, Y=5 for "washed the gravel out of my palms"
    make_box("S1_Porch", (71, 6, 0.6), (8, 6, 1.2), m_sidewalk, sets_col)

    # ------------------------------------------------------------
    # SET 2 (X=120): Auto Shop & Morning Kitchen Table
    # ------------------------------------------------------------
    make_box("S2_Floor", (120, 0, -0.25), (40, 32, 0.5), m_shop_floor, sets_col, studs=True)
    make_box("S2_BackWall", (120, -9.5, 6.0), (36, 1.0, 12.0), m_shop_wall, sets_col)
    # Car on lift / open hood
    make_box("S2_Car", (116, -2.0, 1.4), (4.4, 8.2, 2.2), m_car_blue, sets_col)
    make_box("S2_CarHood", (116, 1.4, 3.2), (3.8, 2.6, 0.2), m_car_blue, sets_col, rot=(math.radians(42), 0, 0))
    # Red mechanic tool cabinet
    make_box("S2_ToolBox", (124.5, -5.5, 2.0), (4.2, 2.0, 4.0), m_red_tool, sets_col)
    # Overhead shop warm light strip
    make_box("S2_ShopLamp", (120, -1.0, 9.2), (8.0, 0.8, 0.3), make_roblox_part_mat("M_ShopGlow", "#FFF2CC", emit_str=4.0), sets_col)

    # Morning kitchen sub-area at X=132 (same set offset slightly right)
    make_box("S2_KitWall", (134, -7.5, 5.5), (14, 0.8, 11.0), m_apt_wall, sets_col)
    make_box("S2_KitTable", (134, 0.0, 2.2), (5.0, 3.4, 0.25), m_wood_dark, sets_col)
    for tx, ty in ((131.8, -1.4), (136.2, -1.4), (131.8, 1.4), (136.2, 1.4)):
        make_box(f"S2_Tleg_{tx}_{ty}", (tx, ty, 1.1), (0.25, 0.25, 2.2), m_wood_dark, sets_col)
    make_box("S2_Chair", (134, -2.5, 1.2), (2.2, 2.0, 0.25), m_wood_dark, sets_col)
    # Black coffee mug on table
    make_cyl("S2_Mug", (133.4, -0.4, 2.65), 0.28, 0.26, 0.65, m_coffee_mug, sets_col)
    make_cyl("S2_Coffee", (133.4, -0.4, 2.95), 0.24, 0.24, 0.06, m_coffee_dark, sets_col)

    # ------------------------------------------------------------
    # SET 3 (X=180): Hospital Room (Winter)
    # ------------------------------------------------------------
    make_box("S3_Floor", (180, 0, -0.25), (30, 26, 0.5), m_hosp_floor, sets_col)
    make_box("S3_BackWall", (180, -8.5, 5.5), (26, 0.8, 11.0), m_hosp_wall, sets_col)
    make_box("S3_SideWall", (171, 0.0, 5.5), (0.8, 18.0, 11.0), m_hosp_wall, sets_col)
    # Hospital bed
    make_box("S3_BedFrame", (179, -2.5, 1.1), (4.4, 8.2, 0.6), m_bed_frame, sets_col)
    make_box("S3_Mattress", (179, -2.5, 1.7), (4.1, 7.8, 0.8), m_bed_sheet, sets_col)
    make_box("S3_Pillow", (179, -5.6, 2.3), (2.8, 1.5, 0.45), m_hosp_wall, sets_col)
    # Glowing vital monitor + stand
    make_box("S3_MonStand", (175.2, -5.5, 2.2), (0.35, 0.35, 4.4), m_metal, sets_col)
    make_box("S3_MonBox", (175.2, -5.5, 4.6), (2.0, 0.8, 1.5), m_bed_frame, sets_col)
    make_box("S3_MonScreen", (175.2, -5.06, 4.6), (1.6, 0.1, 1.1), m_monitor_glow, sets_col)
    # Bedside table + 3 orange prescription bottles
    make_box("S3_SideTable", (183.0, -4.2, 1.2), (2.2, 2.2, 2.4), m_hosp_wall, sets_col)
    for bi, bx in enumerate((182.3, 183.0, 183.7)):
        make_cyl(f"S3_Pill_{bi}", (bx, -4.0, 2.75), 0.22, 0.22, 0.65, m_pill_orange, sets_col)
        make_cyl(f"S3_PillCap_{bi}", (bx, -4.0, 3.12), 0.24, 0.24, 0.12, m_pill_cap, sets_col)

    # ------------------------------------------------------------
    # SET 4 (X=240): Tuesday Apartment (Bathroom Door, Kitchen Counter & Front Door)
    # ------------------------------------------------------------
    make_box("S4_Floor", (240, 0, -0.25), (34, 28, 0.5), m_apt_floor, sets_col)
    make_box("S4_BackWallL", (233.5, -7.0, 5.5), (9.0, 0.8, 11.0), m_apt_wall, sets_col)
    make_box("S4_BackWallR", (246.5, -7.0, 5.5), (9.0, 0.8, 11.0), m_apt_wall, sets_col)
    make_box("S4_DoorHeader", (240.0, -7.0, 8.8), (4.4, 0.8, 4.4), m_apt_wall, sets_col)
    # Animated Bathroom Door hinged at X=238.0, Y=-7.0
    bath_hinge = bpy.data.objects.new("S4_BathHinge", None)
    bath_hinge.location = (238.0, -7.0, 0.0)
    sets_col.objects.link(bath_hinge)
    bath_door = make_box("S4_BathDoor", (1.9, 0.0, 3.3), (3.8, 0.35, 6.6), m_door_white, sets_col)
    bath_door.parent = bath_hinge
    # Glowing sink vanity inside bathroom behind door (Y=-10.5)
    make_box("S4_BathRoomBG", (240.0, -11.5, 5.0), (9.0, 0.6, 10.0), m_hosp_wall, sets_col)
    make_box("S4_MirrorGlow", (240.0, -11.0, 5.2), (3.6, 0.15, 2.6), make_roblox_part_mat("M_BathGlow", "#CFE7FA", emit_str=2.2), sets_col)

    # Kitchen Counter at X=245.5, Y=-3.0 with 3 orange prescription bottles + torn crumpled envelope on floor!
    make_box("S4_Counter", (246.0, -3.2, 1.6), (6.5, 2.6, 3.2), m_wood_dark, sets_col)
    make_box("S4_CounterTop", (246.0, -3.2, 3.3), (6.7, 2.8, 0.25), m_counter, sets_col)
    for bi, bx in enumerate((244.4, 245.3, 246.2)):
        make_cyl(f"S4_Pill_{bi}", (bx, -2.7, 3.85), 0.24, 0.24, 0.78, m_pill_orange, sets_col)
        make_cyl(f"S4_PillCap_{bi}", (bx, -2.7, 4.28), 0.26, 0.26, 0.14, m_pill_cap, sets_col)
    # Torn envelope on floor near counter
    make_box("S4_EnvA", (244.2, -0.5, 0.05), (1.1, 0.75, 0.06), m_envelope, sets_col, rot=(0, 0, math.radians(18)))
    make_box("S4_EnvB", (245.1, -0.2, 0.07), (0.65, 0.55, 0.06), m_envelope, sets_col, rot=(0, 0, math.radians(-28)))
    # Duffel bag beside Sam/door
    duffel = make_box("S4_DuffelBag", (236.5, 1.5, 0.7), (2.2, 1.2, 1.3), m_duffel, sets_col)
    # Front exit doorway at X=232.0, Y=4.5
    make_box("S4_FrontWall", (230.0, 6.0, 5.5), (12.0, 0.8, 11.0), m_apt_wall, sets_col)
    make_box("S4_FrontDoorGlow", (233.5, 6.4, 3.5), (3.8, 0.3, 6.8), make_roblox_part_mat("M_ExitWarm", "#FFDFA0", emit_str=3.2), sets_col)

    # ------------------------------------------------------------
    # SET 5 (X=300): Roblox Thorfinn Sunset Outro (@Arseluz27 JgOivTwLM7U_6s mood)
    # ------------------------------------------------------------
    make_box("S5_CliffGround", (300, 0, -0.5), (34, 26, 1.0), m_wheat_gold, sets_col, studs=True)
    make_box("S5_SeaPlane", (300, -35, -3.0), (140, 60, 0.5), m_sunset_water, sets_col)
    # Huge warm sunset sun orb on the horizon behind Thorfinn (-Y direction)
    make_cyl("S5_SunDisc", (300, -52, 8.5), 11.0, 11.0, 1.0, m_sun_glow, sets_col, rot=(math.radians(90), 0, 0), segs=24)
    # Swaying wheat stalks along the cliff edge for golden rim atmosphere
    rng = random.Random(42)
    for wi in range(28):
        wx = 292.0 + rng.uniform(0, 16.0)
        wy = rng.uniform(-7.0, 4.0)
        stalk = make_box(f"S5_Wheat_{wi}", (wx, wy, 0.65), (0.14, 0.14, 1.4), m_wheat_gold, sets_col)
        drv = stalk.driver_add("rotation_euler", 0).driver
        drv.expression = f"0.12 * sin(frame * 0.22 + {wi * 0.4:.2f})"

    return {
        "col": sets_col,
        "bath_hinge": bath_hinge,
        "duffel": duffel,
    }


def setup_lighting(scene):
    lcol = bpy.data.collections.new("Lighting")
    scene.collection.children.link(lcol)

    # Crisp directional Sun light (sharp @Arseluz27 pixel shadows!)
    sun_d = bpy.data.lights.new("Sun_Key", type="SUN")
    sun_d.energy = 3.2
    sun_d.color = (1.0, 0.94, 0.85)
    sun_d.angle = math.radians(1.4)
    sun_o = bpy.data.objects.new("Sun_Key", sun_d)
    lcol.objects.link(sun_o)
    sun_o.rotation_euler = (math.radians(52), math.radians(18), math.radians(-35))

    def add_area(name, loc, target, energy, color, sx=10.0, sy=6.0):
        ld = bpy.data.lights.new(name, type="AREA")
        ld.energy = energy
        ld.color = color
        ld.size = sx
        ld.size_y = sy
        lo = bpy.data.objects.new(name, ld)
        lcol.objects.link(lo)
        lo.location = loc
        lo.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        return lo

    # Per-set fills & atmospheric rims
    add_area("L_S0_Fill", (0, 14, 9), (0, 0, 2.5), 450, (0.92, 0.96, 1.0))
    add_area("L_S1_Fill", (60, 14, 9), (60, 0, 2.5), 480, (0.95, 0.97, 1.0))
    add_area("L_S2_Warm", (122, 8, 8), (120, -1, 2.5), 620, (1.0, 0.88, 0.72))
    add_area("L_S2_Kit",  (134, 8, 8), (134, -1, 2.5), 480, (1.0, 0.92, 0.80))
    add_area("L_S3_Hosp", (180, 10, 8), (180, -3, 2.5), 550, (0.85, 0.94, 1.0))
    # Tuesday apartment: moody overcast cool fill + warm kitchen accent
    add_area("L_S4_Mood", (240, 12, 8), (240, -2, 2.5), 340, (0.76, 0.84, 1.0))
    add_area("L_S4_Counter", (245, 5, 7), (245, -3, 3.0), 320, (1.0, 0.88, 0.72))
    # Set 5 Sunset Outro: blazing golden amber rim behind Roblox Thorfinn!
    add_area("L_S5_GoldenRim", (300, -14, 7.5), (300, 0, 3.0), 2200, (1.0, 0.68, 0.24), sx=14.0, sy=6.0)
    add_area("L_S5_FrontFill", (300, 10, 5.5), (300, 0, 3.2), 260, (1.0, 0.84, 0.65), sx=8.0, sy=5.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", action="store_true", help="Render 6 keyframe stills across Sets 0-5 for Gate 1 QA")
    ap.add_argument("--range", nargs=2, type=int, metavar=("START", "END"), help="Render frame range")
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    args = ap.parse_args(argv)

    beats_data = load_beats()
    beats = {b["id"]: b for b in beats_data["beats"]}
    story_dur = float(beats_data["story_duration"])
    outro_start = float(beats_data["outro_start"])
    total_dur = float(beats_data["total_duration"])

    total_frames = int(round(total_dur * FPS))

    def f_at(t_sec: float) -> int:
        return max(1, min(total_frames, int(round(t_sec * FPS)) + 1))

    bpl.clear_scene()
    scene = bpy.context.scene
    bpl.configure_undershine_eevee(
        scene, res_x=RES_X, res_y=RES_Y, fps=FPS, samples=6, mist_start=26.0, mist_depth=75.0
    )
    bpl.setup_sky_world(scene, horizon_hex="#f0b67d", zenith_hex="#557ec4", ground_hex="#2c2d3d", strength=0.65)
    scene.frame_start = 1
    scene.frame_end = total_frames
    bpl.setup_passes_compositor(scene, str(PASSES_DIR), depth_max=60.0)

    sets_info = build_sets(scene)
    setup_lighting(scene)

    cast_root = bpy.data.collections.new("Roblox_Cast")
    scene.collection.children.link(cast_root)

    # ============================================================
    # Spawn Original Main 2 Avatars + IRL Background Cast
    # ============================================================
    # Set 0: Parking lot
    marcus_s0 = spawn_r6_rig("Marcus_S0", "01_Alex_Protagonist.blend", "01_Alex_Protagonist", cast_root,
                             TEX_DIR / "bg_marcus_atlas.png", strip_accessories=True, keep_acc_prefixes=("Acc_pal_hair",), hair_tint_hex="#2B1F19")
    stu1_s0 = spawn_r6_rig("Stu1_S0", "01_Alex_Protagonist.blend", "01_Alex_Protagonist", cast_root,
                           TEX_DIR / "bg_student1_atlas.png", strip_accessories=True, extra_hair_key="brown_charmer_hair")
    stu2_s0 = spawn_r6_rig("Stu2_S0", "01_Alex_Protagonist.blend", "01_Alex_Protagonist", cast_root,
                           TEX_DIR / "bg_student2_atlas.png", strip_accessories=True, extra_hair_key="shaggy")
    stu3_s0 = spawn_r6_rig("Stu3_S0", "04_Maya_BestFriend.blend", "04_Maya_BestFriend", cast_root,
                           TEX_DIR / "bg_student3_atlas.png", strip_accessories=True, keep_acc_prefixes=("Acc_beautiful_hair",))
    toby_s0 = spawn_r6_rig("Toby_S0", "01_Alex_Protagonist.blend", "01_Alex_Protagonist", cast_root,
                           TEX_DIR / "01_Alex_Protagonist_atlas.png")

    # Set 1: Bleachers
    toby_s1 = spawn_r6_rig("Toby_S1", "01_Alex_Protagonist.blend", "01_Alex_Protagonist", cast_root,
                           TEX_DIR / "01_Alex_Protagonist_atlas.png")
    marcus_s1 = spawn_r6_rig("Marcus_S1", "01_Alex_Protagonist.blend", "01_Alex_Protagonist", cast_root,
                             TEX_DIR / "bg_marcus_atlas.png", strip_accessories=True, keep_acc_prefixes=("Acc_pal_hair",), hair_tint_hex="#2B1F19")
    sam_s1 = spawn_r6_rig("Sam_S1", "02_Noob_BestFriend.blend", "02_Noob_BestFriend", cast_root,
                          TEX_DIR / "02_Noob_BestFriend_atlas.png")

    # Set 2: Auto Shop & Morning Kitchen
    sam_s2 = spawn_r6_rig("Sam_S2", "02_Noob_BestFriend.blend", "02_Noob_BestFriend", cast_root,
                          TEX_DIR / "02_Sam_ShopJacket_atlas.png")
    mech_s2 = spawn_r6_rig("Mech_S2", "01_Alex_Protagonist.blend", "01_Alex_Protagonist", cast_root,
                           TEX_DIR / "bg_mechanic_atlas.png", strip_accessories=True, keep_acc_prefixes=("Acc_pal_hair",), hair_tint_hex="#332A24")
    toby_s2 = spawn_r6_rig("Toby_S2", "01_Alex_Protagonist.blend", "01_Alex_Protagonist", cast_root,
                           TEX_DIR / "01_Alex_Protagonist_atlas.png")

    # Set 3: Hospital Room
    mom_s3 = spawn_r6_rig("Mom_S3", "04_Maya_BestFriend.blend", "04_Maya_BestFriend", cast_root,
                          TEX_DIR / "bg_mom_atlas.png", strip_accessories=True, extra_hair_key="chestnut_bun")
    sam_s3 = spawn_r6_rig("Sam_S3", "02_Noob_BestFriend.blend", "02_Noob_BestFriend", cast_root,
                          TEX_DIR / "02_Sam_ShopJacket_atlas.png")
    toby_s3 = spawn_r6_rig("Toby_S3", "01_Alex_Protagonist.blend", "01_Alex_Protagonist", cast_root,
                           TEX_DIR / "01_Alex_Protagonist_atlas.png")

    # Set 4: Tuesday Apartment & Bruised Face Climax
    sam_s4 = spawn_r6_rig("Sam_S4", "02_Noob_BestFriend.blend", "02_Noob_BestFriend", cast_root,
                          TEX_DIR / "02_Sam_Bruised_atlas.png", strip_accessories=True)
    hood_mat = make_roblox_part_mat("M_SamHood", "#262932", rough=0.65)
    sam_hood = add_head_hood_prop(sam_s4, sam_s4["col"], hood_mat)
    toby_s4 = spawn_r6_rig("Toby_S4", "01_Alex_Protagonist.blend", "01_Alex_Protagonist", cast_root,
                           TEX_DIR / "01_Alex_Protagonist_atlas.png")

    # Set 5: Roblox Thorfinn Sunset Outro
    thorfinn_s5 = spawn_r6_rig("Thorfinn_S5", "01_Alex_Protagonist.blend", "01_Alex_Protagonist", cast_root,
                               TEX_DIR / "outro_thorfinn_atlas.png", strip_accessories=True, extra_hair_key="blonde_spiked_hair", hair_tint_hex="#D6A84C")
    attach_shield_to_arm(thorfinn_s5, thorfinn_s5["col"], make_roblox_part_mat("M_ShieldWood", "#6B4A2E", 0.65), make_roblox_part_mat("M_ShieldIron", "#5E6470", 0.35, metallic=0.6))
    attach_cape_to_torso(thorfinn_s5, thorfinn_s5["col"], make_roblox_part_mat("M_ThorfinnCape", "#524132", 0.72))

    # ============================================================
    # Pose & Animate Characters Across Story Beats
    # ============================================================
    # Set 0 placements & shove animation (0 .. 33s)
    f0 = f_at(beats["b01_intro"]["start"])
    f_shove = f_at(beats["b02_rule"]["start"] + 1.4)
    f_recoil = f_at(beats["b03_instantly"]["start"] + 1.0)
    key_rig_world(toby_s0["rig"], f0, Vector((-4.5, 1.5, 0.0)), -18.0)
    key_pose_bones(toby_s0["rig"], f0, {"Head": (0, 0, 12), "LeftArm_FK": (10, 0, -10), "RightArm_FK": (10, 0, 10)})

    key_rig_world(stu2_s0["rig"], f0, Vector((4.8, -4.5, 0.0)), 14.0)
    key_rig_world(stu3_s0["rig"], f0, Vector((-6.2, -5.0, 0.0)), -20.0)
    key_pose_bones(stu2_s0["rig"], f0, {"RightArm_FK": (-25, 0, 15), "LeftArm_FK": (-25, 0, -15)})

    key_rig_world(marcus_s0["rig"], f0, Vector((-1.4, -1.8, 0.0)), -75.0)
    key_pose_bones(marcus_s0["rig"], f0, {"RightArm_FK": (-20, 0, 12), "LeftArm_FK": (12, 0, -10)})
    key_pose_bones(marcus_s0["rig"], f_shove, {"RightArm_FK": (-95, 10, 5), "LeftArm_FK": (-75, -10, -5), "LowerTorso-FK": (12, 0, 0)})
    key_pose_bones(marcus_s0["rig"], f_recoil, {"RightArm_FK": (-55, 0, 20), "Head": (-12, 0, 18)})

    key_rig_world(stu1_s0["rig"], f0, Vector((1.6, -1.8, 0.0)), 78.0)
    key_rig_world(stu1_s0["rig"], f_shove, Vector((1.8, -1.8, 0.0)), 78.0)
    key_rig_world(stu1_s0["rig"], f_recoil, Vector((3.3, -1.8, 0.0)), 78.0)
    key_pose_bones(stu1_s0["rig"], f_recoil, {"LowerTorso-FK": (-18, 0, 0), "RightArm_FK": (-65, 0, 25), "LeftArm_FK": (-65, 0, -25)})

    # Set 1 placements (Sam unmarked & bleachers confrontation)
    f_b6 = f_at(beats["b06_sam_intro"]["start"])
    f_b8 = f_at(beats["b08_bleachers"]["start"])
    f_b8_hit = f_at(beats["b08_bleachers"]["start"] + 3.2)
    f_b9 = f_at(beats["b09_welt"]["start"])
    f_b10 = f_at(beats["b10_why_ask"]["start"])

    # During b06: Sam standing proudly in sunshine beside Toby
    key_rig_world(sam_s1["rig"], f_b6, Vector((58.2, 0.0, 0.0)), -8.0, scale=1.07)
    key_pose_bones(sam_s1["rig"], f_b6, {"Head": (-4, 0, 8), "RightArm_FK": (8, 0, 10), "LeftArm_FK": (8, 0, -10)})
    key_rig_world(toby_s1["rig"], f_b6, Vector((61.0, 0.5, 0.0)), 14.0)
    key_pose_bones(toby_s1["rig"], f_b6, {"Head": (-5, 0, -12)})

    # During b08-b09: Marcus shoves Sam twice, Sam stands rock solid without lifting a finger
    key_rig_world(marcus_s1["rig"], f_b8, Vector((62.2, -1.0, 0.0)), 76.0)
    key_pose_bones(marcus_s1["rig"], f_b8, {"RightArm_FK": (-85, 0, 0), "LeftArm_FK": (-85, 0, 0)})
    key_pose_bones(marcus_s1["rig"], f_b8_hit, {"RightArm_FK": (-100, 10, 0), "LowerTorso-FK": (14, 0, 0)})
    key_rig_world(marcus_s1["rig"], f_b9, Vector((63.6, -1.0, 0.0)), 65.0)
    key_pose_bones(marcus_s1["rig"], f_b9, {"Head": (-10, 0, -18), "RightArm_FK": (-45, 18, -28)})

    key_rig_world(sam_s1["rig"], f_b8, Vector((59.8, -1.0, 0.0)), -75.0, scale=1.07)
    key_pose_bones(sam_s1["rig"], f_b8, {"RightArm_FK": (6, 0, 8), "LeftArm_FK": (6, 0, -8)})
    key_pose_bones(sam_s1["rig"], f_b9, {"Head": (4, 0, 12), "RightArm_FK": (12, 0, 8)})

    key_rig_world(toby_s1["rig"], f_b8, Vector((57.6, -1.6, 0.0)), -50.0)
    # b10-b12: Toby & Sam sitting/talking on stoop (X=70, Y=5.5)
    key_rig_world(toby_s1["rig"], f_b10, Vector((71.6, 4.4, 1.2)), 10.0)
    key_pose_bones(toby_s1["rig"], f_b10, {"Head": (-6, 0, -25), "RightArm_FK": (-55, -18, 12), "LeftArm_FK": (-55, 18, -12)})
    key_rig_world(sam_s1["rig"], f_b10, Vector((69.2, 4.4, 1.2)), -15.0, scale=1.07)
    key_pose_bones(sam_s1["rig"], f_b10, {"Head": (4, 0, 20), "RightArm_FK": (14, 0, 12), "LeftArm_FK": (14, 0, -12)})

    # Set 2 placements (Auto Shop + Morning Kitchen)
    f_b7 = f_at(beats["b07_sam_work"]["start"])
    f_b14 = f_at(beats["b14_night_shifts"]["start"])
    key_rig_world(sam_s2["rig"], f_b7, Vector((118.2, 1.8, 0.0)), -120.0, scale=1.07)
    key_pose_bones(sam_s2["rig"], f_b7, {"LowerTorso-FK": (14, 0, 0), "RightArm_FK": (-75, 0, 0), "LeftArm_FK": (-65, 0, 0)})
    key_rig_world(mech_s2["rig"], f_b7, Vector((121.8, -1.5, 0.0)), 65.0)
    key_pose_bones(mech_s2["rig"], f_b7, {"RightArm_FK": (-80, 0, 10)})

    # b14: Sam exhausted at morning kitchen table (X=134, Y=-2.0)
    key_rig_world(sam_s2["rig"], f_b14, Vector((134.0, -2.0, 0.0)), 0.0, scale=1.07)
    key_pose_bones(sam_s2["rig"], f_b14, {"LowerTorso-FK": (12, 0, 0), "Head": (12, 0, 0), "RightArm_FK": (-72, 18, -12), "LeftArm_FK": (-35, 0, -12)})
    key_rig_world(toby_s2["rig"], f_b14, Vector((131.5, 3.0, 0.0)), 145.0)

    # Set 3 placements (Hospital Room - Mom reclining upright against pillows under blanket)
    f_b13 = f_at(beats["b13_mom_sick"]["start"])
    key_rig_world(mom_s3["rig"], f_b13, Vector((179.0, -4.6, 1.1)), 0.0)
    key_pose_bones(mom_s3["rig"], f_b13, {"LowerTorso-FK": (-16, 0, 0), "Head": (10, 0, 0), "RightArm_FK": (-20, 0, 12), "LeftArm_FK": (-20, 0, -12)})
    key_rig_world(sam_s3["rig"], f_b13, Vector((182.6, -1.2, 0.0)), 135.0, scale=1.07)
    key_pose_bones(sam_s3["rig"], f_b13, {"Head": (12, 0, -10), "RightArm_FK": (-30, 0, 10)})
    key_rig_world(toby_s3["rig"], f_b13, Vector((175.4, -1.2, 0.0)), -135.0)
    key_pose_bones(toby_s3["rig"], f_b13, {"Head": (10, 0, 10)})

    # Set 4 placements (Tuesday Apartment Climax: 93.75s .. 189.94s)
    f_b16 = f_at(beats["b16_apartment"]["start"])
    f_b17_open = f_at(beats["b17_knock"]["start"] + 4.8)
    f_b18_pull = f_at(beats["b18_hood"]["start"] + 3.0)
    f_b19_shock = f_at(beats["b19_breath"]["start"])
    f_b21_yell = f_at(beats["b21_who_did"]["start"])
    f_b22_grab = f_at(beats["b22_nobody"]["start"])
    f_b26_walk = f_at(beats["b26_ending"]["start"] + 4.5)
    f_b26_exit = f_at(beats["b26_ending"]["end"])

    # Bathroom door animates cracked -> swung open
    sets_info["bath_hinge"].rotation_euler = (0, 0, 0)
    sets_info["bath_hinge"].keyframe_insert(data_path="rotation_euler", frame=f_b16)
    sets_info["bath_hinge"].rotation_euler = (0, 0, math.radians(-18))
    sets_info["bath_hinge"].keyframe_insert(data_path="rotation_euler", frame=f_b17_open)
    sets_info["bath_hinge"].rotation_euler = (0, 0, math.radians(-82))
    sets_info["bath_hinge"].keyframe_insert(data_path="rotation_euler", frame=f_b18_pull - 8)

    # Sam starts behind door (Y=-8.2), steps out into hallway (Y=-4.6) with head down & hood on
    key_rig_world(sam_s4["rig"], f_b16, Vector((240.2, -8.4, 0.0)), 0.0, scale=1.07)
    key_rig_world(sam_s4["rig"], f_b17_open, Vector((240.2, -4.8, 0.0)), 0.0, scale=1.07)
    key_pose_bones(sam_s4["rig"], f_b17_open, {"Head": (24, 0, 0), "RightArm_FK": (6, 0, 12), "LeftArm_FK": (6, 0, -12)})

    # Hood flips cleanly back/hidden at f_b18_pull and Sam lifts his bruised face!
    sam_hood.rotation_euler = (0.0, 0.0, 0.0)
    sam_hood.keyframe_insert(data_path="rotation_euler", frame=f_b16)
    sam_hood.keyframe_insert(data_path="rotation_euler", frame=f_b18_pull - 4)
    sam_hood.rotation_euler = (math.radians(-125), 0.0, 0.0)
    sam_hood.keyframe_insert(data_path="rotation_euler", frame=f_b18_pull + 3)

    key_pose_bones(sam_s4["rig"], f_b18_pull + 3, {"Head": (2, 0, 0), "RightArm_FK": (10, 0, 12), "LeftArm_FK": (10, 0, -12)})
    key_pose_bones(sam_s4["rig"], f_b22_grab, {"Head": (4, 0, -10), "RightArm_FK": (-78, -14, 10), "LeftArm_FK": (-78, 14, -10)})
    key_rig_world(sam_s4["rig"], f_b22_grab, Vector((240.2, -4.6, 0.0)), 0.0, scale=1.07)

    # Keep Toby offset to viewer-right (X=237.6) so he NEVER blocks the center camera line to Sam!
    key_rig_world(toby_s4["rig"], f_b16, Vector((237.8, -1.8, 0.0)), 155.0)
    key_pose_bones(toby_s4["rig"], f_b16, {"RightArm_FK": (-85, 0, 0), "Head": (-4, 0, 0)})
    key_rig_world(toby_s4["rig"], f_b18_pull, Vector((238.4, -3.2, 0.0)), 145.0)
    key_pose_bones(toby_s4["rig"], f_b18_pull, {"RightArm_FK": (-128, 0, -12), "Head": (-8, 0, 0)})
    key_rig_world(toby_s4["rig"], f_b19_shock + 6, Vector((237.5, -2.0, 0.0)), 150.0)
    key_pose_bones(toby_s4["rig"], f_b19_shock + 6, {"LowerTorso-FK": (-10, 0, 0), "RightArm_FK": (-45, 0, 25), "LeftArm_FK": (-45, 0, -25)})
    key_pose_bones(toby_s4["rig"], f_b21_yell, {"LowerTorso-FK": (8, 0, 0), "RightArm_FK": (-95, 18, 15), "LeftArm_FK": (-95, -18, -15)})

    # Sam squeezes Toby's shoulder, picks up duffel bag, walks out front door into light
    key_rig_world(sam_s4["rig"], f_b26_walk, Vector((237.2, 1.0, 0.0)), 45.0, scale=1.07)
    key_pose_bones(sam_s4["rig"], f_b26_walk, {"Head": (-6, 0, 10), "RightArm_FK": (15, 0, 12), "LeftArm_FK": (-25, 0, -10)})
    key_rig_world(sam_s4["rig"], f_b26_exit, Vector((233.6, 5.2, 0.0)), 38.0, scale=1.07)
    sets_info["duffel"].location = (236.5, 1.5, 0.7)
    sets_info["duffel"].keyframe_insert(data_path="location", frame=f_b26_walk - 5)
    sets_info["duffel"].location = (233.1, 5.0, 1.8)
    sets_info["duffel"].keyframe_insert(data_path="location", frame=f_b26_exit)

    # Set 5: Roblox Thorfinn Sunset Outro
    f_out0 = f_at(outro_start)
    f_out_mid = f_at(outro_start + 4.8)
    f_out_end = total_frames
    key_rig_world(thorfinn_s5["rig"], f_out0, Vector((300.0, 0.0, 0.0)), 12.0, scale=1.05)
    key_pose_bones(thorfinn_s5["rig"], f_out0, {"Head": (4, 0, -10), "RightArm_FK": (8, 0, 10), "LeftArm_FK": (8, 0, -10)})
    key_pose_bones(thorfinn_s5["rig"], f_out_mid, {"Head": (-3, 0, 4), "LowerTorso-FK": (-4, 0, 0)})
    key_pose_bones(thorfinn_s5["rig"], f_out_end, {"Head": (-5, 0, 6)})

    # ============================================================
    # Multi-Angle Camera Shots (Zero Static Holds, Locked to beats.json)
    # ============================================================
    def shot_spec(name, t0, t1, p0, p1, tgt0, tgt1, lens=40.0, roll=0.0, orbit=0.0, kick_t=None):
        sf = f_at(t0)
        ef = total_frames if t1 >= total_dur - 0.05 else max(sf + 2, f_at(t1) - 1)
        return (name, sf, ef, p0, p1, tgt0, tgt1, lens, roll, orbit, f_at(kick_t) if kick_t else None)

    shots = [
        shot_spec("01_Parking_Wide",    0.00, beats["b02_rule"]["start"],
                  (10.0, 13.0, 5.5), (7.5, 10.5, 4.8), (0.0, -2.0, 2.8), (-0.5, -2.0, 3.0), lens=35.0),
        shot_spec("02_Parking_Shove",   beats["b02_rule"]["start"], beats["b03_instantly"]["start"],
                  (4.0, 6.2, 3.8), (3.0, 4.8, 3.6), (0.2, -1.8, 3.0), (0.5, -1.8, 3.2), lens=38.0, kick_t=beats["b02_rule"]["start"] + 1.4),
        shot_spec("03_Marcus_BruiseCU", beats["b03_instantly"]["start"], beats["b04_marcus"]["start"],
                  (2.6, 1.8, 4.0), (1.8, 1.2, 4.1), (-1.4, -1.8, 3.6), (-1.4, -1.8, 3.8), lens=44.0),
        shot_spec("04_Marcus_Hallway",  beats["b04_marcus"]["start"], beats["b05_town_rule"]["start"],
                  (-5.8, 6.2, 3.6), (-4.0, 4.8, 3.8), (-1.0, -2.5, 3.0), (-0.5, -2.2, 3.2), lens=38.0, orbit=-10.0),
        shot_spec("05_Town_Students",   beats["b05_town_rule"]["start"], beats["b06_sam_intro"]["start"],
                  (-8.5, 5.8, 4.2), (-5.0, 6.5, 3.8), (0.0, -4.0, 3.0), (-1.5, -2.5, 3.0), lens=36.0),
        shot_spec("06_Sam_HeroIntro",   beats["b06_sam_intro"]["start"], beats["b07_sam_work"]["start"],
                  (59.8, 7.6, 3.2), (59.0, 5.8, 3.6), (59.0, 0.0, 3.2), (58.6, 0.0, 3.5), lens=40.0),
        shot_spec("07_AutoShop_Work",   beats["b07_sam_work"]["start"], beats["b08_bleachers"]["start"],
                  (124.5, 8.2, 4.2), (121.0, 6.8, 3.8), (118.5, 0.5, 2.8), (118.5, 1.2, 3.2), lens=38.0, orbit=12.0),
        shot_spec("08_Bleachers_Shove", beats["b08_bleachers"]["start"], beats["b09_welt"]["start"],
                  (63.8, 7.2, 3.8), (62.2, 5.6, 3.6), (60.2, -1.0, 3.0), (60.0, -1.0, 3.3), lens=38.0, kick_t=beats["b08_bleachers"]["start"] + 3.2),
        shot_spec("09_Sam_Unmarked",    beats["b09_welt"]["start"], beats["b10_why_ask"]["start"],
                  (63.5, 4.2, 4.0), (62.2, 3.6, 4.1), (60.2, -1.0, 3.5), (59.8, -1.0, 3.8), lens=44.0),
        shot_spec("10_Porch_Talk",      beats["b10_why_ask"]["start"], beats["b11_no_enemies_sam"]["start"],
                  (73.8, 11.2, 3.8), (72.2, 9.6, 3.8), (70.5, 4.4, 3.4), (70.3, 4.4, 3.6), lens=40.0),
        shot_spec("11_Sam_QuoteSmile",  beats["b11_no_enemies_sam"]["start"], beats["b12_strongest"]["start"],
                  (68.2, 9.2, 4.0), (68.6, 8.0, 4.1), (69.2, 4.4, 3.8), (69.2, 4.4, 4.0), lens=48.0),
        shot_spec("12_Sam_Strongest",   beats["b12_strongest"]["start"], beats["b13_mom_sick"]["start"],
                  (70.5, 10.5, 3.2), (70.2, 8.8, 3.8), (69.5, 4.4, 3.8), (69.5, 4.4, 4.1), lens=40.0),
        shot_spec("13_Hospital_Room",   beats["b13_mom_sick"]["start"], beats["b14_night_shifts"]["start"],
                  (183.0, 7.5, 4.8), (180.5, 5.5, 4.4), (179.0, -3.5, 2.8), (179.5, -3.5, 2.8), lens=36.0, orbit=-8.0),
        shot_spec("14_Morning_Coffee",  beats["b14_night_shifts"]["start"], beats["b15_tuesday"]["start"],
                  (136.6, 5.2, 4.0), (135.2, 3.6, 3.9), (134.0, -1.5, 3.4), (133.8, -1.6, 3.6), lens=42.0),
        shot_spec("15_Tuesday_Snap",    beats["b15_tuesday"]["start"], beats["b16_apartment"]["start"],
                  (243.5, 5.0, 4.2), (242.5, 3.5, 4.0), (240.0, -5.5, 3.2), (240.0, -5.5, 3.4), lens=38.0, kick_t=beats["b15_tuesday"]["start"]),
        shot_spec("16_Apt_DoorKnock",   beats["b16_apartment"]["start"], beats["b17_knock"]["start"],
                  (243.8, 3.8, 3.8), (242.2, 2.4, 3.6), (239.4, -4.5, 3.2), (239.8, -5.5, 3.4), lens=38.0),
        shot_spec("17_Bath_DoorCrack",  beats["b17_knock"]["start"], beats["b18_hood"]["start"],
                  (242.6, 0.5, 3.8), (241.6, -0.4, 4.0), (240.2, -5.0, 3.6), (240.2, -4.8, 3.8), lens=42.0),
        shot_spec("18_Hood_Pull",       beats["b18_hood"]["start"], beats["b19_breath"]["start"],
                  (242.5, -0.4, 4.2), (241.8, -1.0, 4.3), (240.2, -4.6, 3.8), (240.2, -4.6, 4.0), lens=44.0, kick_t=beats["b18_hood"]["start"] + 3.0),
        shot_spec("19_Cant_Breathe",    beats["b19_breath"]["start"], beats["b20_bruised_face"]["start"],
                  (241.2, -0.2, 4.4), (240.8, -0.8, 4.5), (240.2, -4.6, 4.1), (240.2, -4.6, 4.3), lens=48.0),
        shot_spec("20_Bruised_FaceCU",  beats["b20_bruised_face"]["start"], beats["b21_who_did"]["start"],
                  (241.4, -0.2, 4.4), (240.4, -0.8, 4.5), (240.2, -4.6, 4.2), (240.2, -4.6, 4.3), lens=50.0, orbit=8.0),
        shot_spec("21_Toby_Yelling",    beats["b21_who_did"]["start"], beats["b22_nobody"]["start"],
                  (241.5, -5.2, 4.0), (240.8, -4.6, 4.0), (237.8, -2.0, 3.6), (237.6, -2.0, 3.8), lens=42.0, roll=-3.0),
        shot_spec("22_Sam_QuietSmile",  beats["b22_nobody"]["start"], beats["b23_remember_rule"]["start"],
                  (242.0, 0.2, 4.1), (241.2, -0.6, 4.2), (240.2, -4.6, 3.8), (240.2, -4.6, 4.0), lens=45.0),
        shot_spec("23_Remember_Rule",   beats["b23_remember_rule"]["start"], beats["b24_counter_bottles"]["start"],
                  (239.2, 1.5, 4.2), (239.6, 0.4, 4.0), (239.2, -3.5, 3.5), (239.6, -4.2, 3.8), lens=40.0),
        shot_spec("24_Counter_Bottles", beats["b24_counter_bottles"]["start"], beats["b25_dad_truth"]["start"],
                  (243.0, 2.2, 4.6), (244.4, 0.4, 3.4), (245.3, -2.6, 3.8), (244.6, -0.6, 1.2), lens=42.0),
        shot_spec("25_Dad_Truth_Wide",  beats["b25_dad_truth"]["start"], beats["b26_ending"]["start"],
                  (236.2, 3.8, 4.0), (237.8, 2.2, 3.8), (240.5, -3.5, 3.4), (240.2, -4.4, 3.8), lens=36.0, orbit=-8.0),
        shot_spec("26_Walk_Out_Door",   beats["b26_ending"]["start"], outro_start,
                  (239.8, -2.5, 3.4), (237.0, 1.4, 3.8), (236.5, 2.2, 3.4), (233.6, 5.2, 3.8), lens=38.0),
        # Set 5: Roblox Thorfinn Sunset Outro (10.30s, wide/medium sunset framing like @Arseluz27!)
        shot_spec("27_Thorfinn_Silhouette", outro_start, outro_start + 3.2,
                  (303.2, 9.8, 3.2), (301.8, 7.6, 3.5), (300.0, -8.0, 3.8), (300.0, -10.0, 4.0), lens=36.0, kick_t=outro_start + 0.1),
        shot_spec("28_Thorfinn_FaceGlow",   outro_start + 3.2, outro_start + 6.8,
                  (298.8, 7.2, 3.8), (301.0, 5.6, 4.0), (300.0, -8.0, 4.0), (300.0, -10.0, 4.2), lens=42.0, orbit=12.0),
        shot_spec("29_Thorfinn_HeroSun",    outro_start + 6.8, total_dur,
                  (302.5, 9.5, 2.2), (300.4, 7.2, 3.0), (300.0, -12.0, 4.2), (300.0, -15.0, 4.6), lens=34.0, kick_t=outro_start + 6.85),
    ]

    # Ensure strictly continuous frame coverage 1..total_frames
    for i in range(len(shots)):
        name, sf, ef, p0, p1, t0, t1, lens, roll, orbit, kf = shots[i]
        if i + 1 < len(shots):
            ef = max(sf, shots[i + 1][1] - 1)
        else:
            ef = total_frames
        bpl.add_multi_angle_shot(
            scene, name, sf, ef, p0, p1, t0, t1,
            lens=lens, roll_deg=roll, orbit_deg=orbit, kick_frame=kf, kick_amp=0.14
        )

    if args.stills:
        still_frames = [
            f_at(beats["b03_instantly"]["start"] + 1.5),   # Marcus bruised face in parking lot
            f_at(beats["b08_bleachers"]["start"] + 2.0),   # Sam unmarked stepping between Toby & Marcus
            f_at(beats["b14_night_shifts"]["start"] + 3.0),# Sam morning coffee unmarked
            f_at(beats["b13_mom_sick"]["start"] + 3.5),    # Mom in hospital bed + 3 orange pill bottles
            f_at(beats["b20_bruised_face"]["start"] + 3.0),# Sam bruised face close-up reveal
            f_at(outro_start + 4.5),                       # Roblox Thorfinn sunset outro
        ]
        for fr in still_frames:
            scene.frame_set(fr)
            bpy.ops.render.render(write_still=False)
        print("[OK] Gate 1 Stills rendered to", PASSES_DIR, "frames:", still_frames)
        return

    if args.range:
        s_f, e_f = args.range
        scene.frame_start = max(1, s_f)
        scene.frame_end = min(total_frames, e_f)
        bpy.ops.render.render(animation=True)
        print(f"[OK] Rendered range {scene.frame_start}..{scene.frame_end}")
        return

    bpy.ops.render.render(animation=True)
    print(f"[OK] Rendered full animation 1..{total_frames}")


if __name__ == "__main__":
    main()
