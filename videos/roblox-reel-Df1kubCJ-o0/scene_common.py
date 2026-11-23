"""
scene_common.py — Shared Blender 5.3.0 asset loader, R6 animation helpers, and 3D Roblox prop
factory for the @thedrizzleshow Bun Town Burger-Wrapper remake (Df1kubCJ-o0).
"""
import json
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Matrix, Vector

SHORTMAKING_ROOT = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking")
CAST_ROOT = SHORTMAKING_ROOT / "assets" / "roblox-r6-characters"
CHARS_DIR = CAST_ROOT / "characters"
PROJ_DIR = SHORTMAKING_ROOT / "videos" / "roblox-reel-Df1kubCJ-o0"
EXPR_DIR = PROJ_DIR / "expressions"
FRAMES_DIR = PROJ_DIR / "frames"
PREVIEWS_DIR = PROJ_DIR / "previews"
FRAMES_DIR.mkdir(parents=True, exist_ok=True)
PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(SHORTMAKING_ROOT / "90 Templates & Starter Kits" / "blender-cinema-kit"))
import blender_cinema_lib as bcl


def load_beats():
    return json.loads((PROJ_DIR / "voice" / "beats.json").read_text(encoding="utf-8"))


def beat_frame_range(beats_data, beat_id):
    fps = beats_data["fps"]
    beats = beats_data["beats"]
    for i, b in enumerate(beats):
        if b["id"] == beat_id:
            f0 = int(round(b["start"] * fps)) + 1
            if i == 0:
                f0 = 1
            if i + 1 < len(beats):
                f1 = int(round(beats[i + 1]["start"] * fps))
            else:
                f1 = int(round(beats_data["total_duration"] * fps))
            return max(1, f0), max(f0, f1)
    raise KeyError(f"Unknown beat_id: {beat_id}")


def configure_fast_eevee(scene, res_x=720, res_y=1280, samples=10, raytracing=False):
    """Fast, crisp, vibrant Blender 5.3 EEVEE setup for 30fps Roblox Cinema Shorts."""
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.resolution_percentage = 100
    scene.render.fps = 30
    scene.render.use_persistent_data = True
    scene.render.use_motion_blur = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"

    scene.eevee.taa_render_samples = samples
    scene.eevee.use_shadows = True
    if hasattr(scene.eevee, "shadow_resolution_scale"):
        scene.eevee.shadow_resolution_scale = 0.75
    if hasattr(scene.eevee, "use_raytracing"):
        scene.eevee.use_raytracing = raytracing
    if hasattr(scene.eevee, "use_fast_gi"):
        scene.eevee.use_fast_gi = raytracing

    scene.display_settings.display_device = "sRGB"
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Punchy"
    scene.view_settings.exposure = -0.18


def setup_bright_sky_world(scene, is_night=False):
    """Vibrant Roblox daytime blue sky or festive indigo party night sky."""
    w = bcl._ensure_world(scene, "RobloxWorld")
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    if is_night:
        bg.inputs["Color"].default_value = bcl.hex_to_linear("#121A3B")
        bg.inputs["Strength"].default_value = 0.65
    else:
        bg.inputs["Color"].default_value = bcl.hex_to_linear("#6CC6FF")
        bg.inputs["Strength"].default_value = 0.95
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])


def make_mat(name, hex_col, rough=0.38, metal=0.0, coat=0.14, emit_hex=None, emit_str=0.0):
    m = bpy.data.materials.get(name)
    if m is not None:
        return m
    return bcl.make_pbr_material(
        name, hex_col,
        roughness_min=max(0.08, rough - 0.05),
        roughness_max=min(0.95, rough + 0.06),
        metallic=metal,
        coat_weight=coat,
        bump_strength=0.012 if rough > 0.25 else 0.005,
        emission_hex=emit_hex,
        emission_strength=emit_str,
    )


def make_image_mat(name, img_path, rough=0.35, emit=0.0):
    m = bpy.data.materials.new(name)
    if bpy.app.version < (5, 0, 0):
        m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = rough
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 0.12
    img = bpy.data.images.load(str(img_path), check_existing=True)
    img.colorspace_settings.name = "sRGB"
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    if emit > 0.0:
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = emit
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return m


def append_character(char_id: str, instance_name: str, parent_col=None, enable_extra_acc: list | None = None, add_party_hat: bool = False, party_hat_color: str = "#EC4899"):
    """
    Append one of our rigged Aeresei R6 characters cleanly, clear any default action,
    optionally toggle on an extra accessory (like Alex's Red Roblox Cap!), and optionally
    weld a festive 3D Party Hat onto the character's head!
    Returns dict: {arm, internal_arm, body_mat, body_tex_node, objects, head_obj, col}
    """
    blend_path = CHARS_DIR / f"{char_id}.blend"
    before_cols = set(bpy.data.collections)
    before_objs = set(bpy.data.objects)
    before_mats = set(bpy.data.materials)

    with bpy.data.libraries.load(str(blend_path), link=False) as (data_from, data_to):
        data_to.collections = [char_id]

    new_cols = [c for c in bpy.data.collections if c not in before_cols]
    new_objs = [o for o in bpy.data.objects if o not in before_objs]
    new_mats = [m for m in bpy.data.materials if m not in before_mats]

    top_col = None
    for c in new_cols:
        if c.name == char_id or c.name.startswith(char_id + "."):
            if not c.name.endswith("_Accessories") and not c.name.endswith("_Extra_Swaps"):
                top_col = c
                break
    if top_col is None and new_cols:
        top_col = new_cols[0]

    target_parent = parent_col or bpy.context.scene.collection
    if top_col:
        top_col.name = instance_name
        if top_col.name not in [c.name for c in target_parent.children]:
            target_parent.children.link(top_col)

    arm = None
    internal_arm = None
    head_obj = None
    body_mat = None
    body_tex_node = None

    for o in new_objs:
        if o.type == "ARMATURE":
            if o.name.startswith("__PrimaryArmature"):
                arm = o
                o.name = f"{instance_name}_Rig"
            elif o.name.startswith("InternalArmature"):
                internal_arm = o
                o.name = f"{instance_name}_InternalArm"
        elif o.type == "MESH" and (o.name.startswith("Head_MBlocky") or o.name.startswith("Head_FBlocky")):
            head_obj = o
        # Toggle requested extra accessories on (e.g., Alex's Red Roblox Cap!)
        if enable_extra_acc and o.type == "MESH":
            for key in enable_extra_acc:
                if o.name.startswith(f"Acc_{key}"):
                    o.hide_viewport = False
                    o.hide_render = False
                    # Lift & slightly scale Red Roblox Cap so it sits boldly over Pal Hair!
                    if key == "red_roblox_cap" and char_id == "01_Alex_Protagonist":
                        for v in o.data.vertices:
                            v.co.x *= 1.12
                            v.co.y = v.co.y * 1.10 + 0.06
                            v.co.z = (v.co.z - 5.1) * 1.10 + 5.1 + 0.28
                        o.data.update()

    if arm and arm.animation_data:
        arm.animation_data.action = None

    for m in new_mats:
        if f"Mat_{char_id}_Body" in m.name:
            body_mat = m
            m.name = f"Mat_{instance_name}_Body"
            if m.node_tree:
                for n in m.node_tree.nodes:
                    if n.type == "TEX_IMAGE":
                        body_tex_node = n
                        break
            break

    # Optional festive 3D Party Hat welded to Head!
    if add_party_hat and internal_arm and head_obj:
        hat_z = 5.65 if char_id != "10_Town_Mayor" else 6.45
        bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=0.42, radius2=0.03, depth=0.95, location=(0.0, -0.02, hat_z))
        cone = bpy.context.active_object
        cone.name = f"{instance_name}_PartyHat"
        cone.data.materials.append(make_mat(f"Mat_PH_{party_hat_color}", party_hat_color, rough=0.35, coat=0.25))
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.14, location=(0.0, -0.02, hat_z + 0.50))
        pom = bpy.context.active_object
        pom.name = f"{instance_name}_PartyPom"
        pom.data.materials.append(make_mat("Mat_PartyPomYellow", "#FACC15", rough=0.55))

        for ho in (cone, pom):
            for c in list(ho.users_collection):
                c.objects.unlink(ho)
            if top_col:
                top_col.objects.link(ho)
            c_con = ho.constraints.new("CHILD_OF")
            c_con.target = internal_arm
            c_con.subtarget = "Head"
            for rc in head_obj.constraints:
                if rc.type == "CHILD_OF" and rc.target == internal_arm and rc.subtarget == "Head":
                    c_con.inverse_matrix = rc.inverse_matrix.copy()
                    break

    return {
        "name": instance_name,
        "char_id": char_id,
        "arm": arm,
        "internal_arm": internal_arm,
        "head_obj": head_obj,
        "body_mat": body_mat,
        "body_tex_node": body_tex_node,
        "objects": new_objs,
        "col": top_col,
    }


def swap_expression(char_info: dict, atlas_filename: str):
    """Swap a character's live face/body texture atlas (e.g. 'alex_determined_atlas.png')."""
    node = char_info.get("body_tex_node")
    if node is None:
        return
    p = EXPR_DIR / atlas_filename
    img = bpy.data.images.load(str(p), check_existing=True)
    img.colorspace_settings.name = "sRGB"
    node.image = img


def set_char_transform(char_info: dict, wx: float, wy: float, wz: float, yaw_deg: float):
    """Exact world-space placement and world-Z yaw via MasterControl rest basis."""
    arm = char_info["arm"]
    pb = arm.pose.bones["MasterControl"]
    rest_3x3 = arm.data.bones["MasterControl"].matrix_local.to_3x3()
    inv_3x3 = rest_3x3.inverted()
    pb.location = inv_3x3 @ Vector((wx, wy, wz))
    pb.rotation_mode = "XYZ"
    world_rot = Matrix.Rotation(math.radians(yaw_deg), 3, "Z")
    pb.rotation_euler = (inv_3x3 @ world_rot @ rest_3x3).to_euler("XYZ")


def set_char_pose(
    char_info: dict,
    torso_loc=(0, 0, 0),
    torso_rot=(0, 0, 0),
    head_rot=(0, 0, 0),
    rarm_rot=(0, 0, 0),
    larm_rot=(0, 0, 0),
    rleg_loc=(0, 0, 0),
    lleg_loc=(0, 0, 0),
):
    """Apply clean FK/IK pose to Aeresei R6 rig bones (rotations in degrees)."""
    pbs = char_info["arm"].pose.bones

    def srot(bname, degs):
        if bname in pbs:
            pb = pbs[bname]
            pb.rotation_mode = "XYZ"
            pb.rotation_euler = tuple(math.radians(a) for a in degs)

    def sloc(bname, loc):
        if bname in pbs:
            pbs[bname].location = loc

    sloc("LowerTorso-FK", torso_loc)
    srot("LowerTorso-FK", torso_rot)
    srot("Head", head_rot)
    srot("RightArm_FK", rarm_rot)
    srot("LeftArm_FK", larm_rot)
    sloc("RightLeg-IK", rleg_loc)
    sloc("LeftLeg-IK", lleg_loc)


def animate_party_dance(char_info: dict, t: float, phase: float = 0.0, energy: float = 1.0):
    """Lively, bouncy Roblox party dancing animation (arms pumping up, joyful bobbing!)."""
    w = 2.0 * math.pi * 2.2 * t + phase
    bob = max(0.0, math.sin(w)) * 0.28 * energy
    sway = math.sin(w * 0.5) * 10.0 * energy
    r_pump = -142.0 + math.sin(w) * 24.0 * energy
    l_pump = -142.0 - math.sin(w) * 24.0 * energy
    set_char_pose(
        char_info,
        torso_loc=(0.0, 0.0, bob),
        torso_rot=(math.sin(w) * 5.0, sway * 0.5, sway),
        head_rot=(-6.0 + math.sin(w) * 6.0, -sway * 0.6, math.cos(w * 0.5) * 8.0),
        rarm_rot=(r_pump, 16.0, -20.0),
        larm_rot=(l_pump, -16.0, 20.0),
        rleg_loc=(0.12, 0.08 * math.sin(w), max(0.0, math.sin(w)) * 0.14),
        lleg_loc=(-0.12, -0.08 * math.sin(w), max(0.0, -math.sin(w)) * 0.14),
    )


# ==================== REUSABLE 3D ROBLOX PROPS ====================

def _link_only(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)
    return obj


def build_burger(name: str, loc, col, scale=1.0):
    """Chunky colorful 3D Roblox Burger (bun bottom, patty, cheese, lettuce, tomato, sesame top bun)."""
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.scale = (scale, scale, scale)
    col.objects.link(root)

    parts = [
        ("BotBun",  "CYL", (0, 0, 0.08), (0.42, 0.42, 0.14), "#D9964B"),
        ("Patty",   "CYL", (0, 0, 0.20), (0.44, 0.44, 0.13), "#5C2C16"),
        ("Cheese",  "BOX", (0, 0, 0.27), (0.72, 0.72, 0.04), "#FACC15"),
        ("Lettuce", "CYL", (0, 0, 0.31), (0.46, 0.46, 0.06), "#4ADE80"),
        ("Tomato",  "CYL", (0, 0, 0.35), (0.40, 0.40, 0.05), "#EF4444"),
        ("TopBun",  "SPH", (0, 0, 0.37), (0.43, 0.43, 0.22), "#E29B4A"),
    ]
    for pname, kind, ploc, psc, col_hex in parts:
        if kind == "CYL":
            bpy.ops.mesh.primitive_cylinder_add(vertices=18, radius=1.0, depth=1.0, location=ploc)
        elif kind == "BOX":
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=ploc)
        else:
            bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=1.0, location=ploc)
        o = _link_only(bpy.context.active_object, col)
        o.name = f"{name}_{pname}"
        o.scale = psc
        o.data.materials.append(make_mat(f"Mat_Burg_{pname}", col_hex, rough=0.45, coat=0.12))
        o.parent = root
    return root


def build_wrapped_burger(name: str, loc, col, scale=1.0):
    """Iconic Bun Town Yellow-Wrapped Burger cylinder with crisp red wrapper stripe!"""
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.scale = (scale, scale, scale)
    col.objects.link(root)

    bpy.ops.mesh.primitive_cylinder_add(vertices=18, radius=0.46, depth=0.42, location=(0, 0, 0.21))
    body = _link_only(bpy.context.active_object, col)
    body.name = f"{name}_Wrap"
    body.data.materials.append(make_mat("Mat_WrapYellow", "#FCD34D", rough=0.52, coat=0.08))
    body.parent = root

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.21))
    stripe = _link_only(bpy.context.active_object, col)
    stripe.name = f"{name}_Stripe"
    stripe.scale = (0.94, 0.14, 0.435)
    stripe.data.materials.append(make_mat("Mat_WrapRed", "#E11D48", rough=0.48))
    stripe.parent = root
    return root


def build_cat(name: str, loc, col, wrapped=True):
    """Cute blocky Roblox Orange Tabby Cat (wrapped snugly in teal/yellow burger paper!)."""
    root = bpy.data.objects.new(name, None)
    root.location = loc
    col.objects.link(root)

    mat_cat = make_mat("Mat_CatOrange", "#F97316", rough=0.50)
    mat_cream = make_mat("Mat_CatCream", "#FED7AA", rough=0.50)
    mat_wrap = make_mat("Mat_CatWrap", "#14B8A6", rough=0.45)
    mat_wrap_y = make_mat("Mat_WrapYellow", "#FCD34D", rough=0.52)
    mat_blk = make_mat("Mat_CatBlk", "#18181B", rough=0.30)

    def box(nm, p, sc, m, rot=(0, 0, 0)):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=p)
        o = _link_only(bpy.context.active_object, col)
        o.name = f"{name}_{nm}"
        o.scale = sc
        o.rotation_euler = rot
        o.data.materials.append(m)
        o.parent = root
        return o

    # Body (wrapped like a snug burrito if wrapped!)
    box("Body", (0, 0, 0.42), (0.68, 0.65, 0.84), mat_wrap if wrapped else mat_cat)
    if wrapped:
        box("WrapStripe", (0, 0.01, 0.42), (0.71, 0.68, 0.18), mat_wrap_y)
    # Head
    box("Head", (0, 0.05, 1.05), (0.72, 0.66, 0.62), mat_cat)
    # Ears
    box("EarL", (-0.24, 0.05, 1.44), (0.18, 0.16, 0.24), mat_cat, rot=(0, 0.15, 0))
    box("EarR", ( 0.24, 0.05, 1.44), (0.18, 0.16, 0.24), mat_cat, rot=(0, -0.15, 0))
    # Cute squinty cozy eyes & nose
    box("EyeL", (-0.16, 0.39, 1.08), (0.14, 0.03, 0.05), mat_blk)
    box("EyeR", ( 0.16, 0.39, 1.08), (0.14, 0.03, 0.05), mat_blk)
    box("Snout", (0.0, 0.39, 0.96), (0.18, 0.06, 0.12), mat_cream)
    box("Nose",  (0.0, 0.42, 0.99), (0.08, 0.03, 0.06), make_mat("Mat_CatPink", "#F472B6", rough=0.4))
    return root


def build_clock(name: str, loc, col, scale=1.0, color_hex="#14B8A6"):
    """Classic retro alarm clock / stopwatch prop."""
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.scale = (scale, scale, scale)
    col.objects.link(root)

    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.45, depth=0.22, location=(0, 0, 0.48), rotation=(math.radians(90), 0, 0))
    body = _link_only(bpy.context.active_object, col)
    body.name = f"{name}_Body"
    body.data.materials.append(make_mat(f"Mat_Clock_{color_hex}", color_hex, rough=0.28, metal=0.25, coat=0.3))
    body.parent = root

    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.37, depth=0.24, location=(0, 0.01, 0.48), rotation=(math.radians(90), 0, 0))
    face = _link_only(bpy.context.active_object, col)
    face.name = f"{name}_Face"
    face.data.materials.append(make_mat("Mat_ClockFace", "#F8FAFC", rough=0.35))
    face.parent = root

    # Hands
    for nm, rz, ln in [("HandH", 0.6, 0.22), ("HandM", -0.3, 0.30)]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.14, 0.48))
        h = _link_only(bpy.context.active_object, col)
        h.name = f"{name}_{nm}"
        h.scale = (0.04, 0.03, ln)
        h.rotation_euler = (0, rz, 0)
        h.data.materials.append(make_mat("Mat_ClockHand", "#DC2626", rough=0.3))
        h.parent = root

    # Twin alarm bells on top
    for sx in (-0.30, 0.30):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=10, radius=0.14, location=(sx, 0, 0.92))
        b = _link_only(bpy.context.active_object, col)
        b.name = f"{name}_Bell_{sx:+.1f}"
        b.data.materials.append(make_mat("Mat_ClockBell", "#EAB308", rough=0.22, metal=0.75))
        b.parent = root
    return root


def set_camera_look(cam_obj, pos, target, lens=35.0, roll_deg=0.0):
    cam_obj.data.lens = lens
    cam_obj.location = Vector(pos)
    q = (Vector(target) - Vector(pos)).to_track_quat("-Z", "Y")
    if abs(roll_deg) > 1e-4:
        q = q @ Euler((0.0, 0.0, math.radians(roll_deg)), "XYZ").to_quaternion()
    cam_obj.rotation_euler = q.to_euler()


def render_frame(scene, frame_num: int, preview_tag: str | None = None):
    """Render either a numbered production frame (skip if already rendered!) or a named Gate-1 preview."""
    if preview_tag:
        out_p = PREVIEWS_DIR / f"{preview_tag}.png"
        scene.render.filepath = str(out_p)
        bpy.ops.render.render(write_still=True)
        print(f"  [PREVIEW] {out_p.name}")
    else:
        out_p = FRAMES_DIR / f"f_{frame_num:04d}.png"
        if out_p.exists() and out_p.stat().st_size > 8000:
            return
        scene.render.filepath = str(out_p)
        bpy.ops.render.render(write_still=True)
