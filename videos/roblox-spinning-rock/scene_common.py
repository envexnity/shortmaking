"""
scene_common.py — Shared Blender 5.3.0 R6 Loader, World Lighting, Camera & Animation Helpers
for videos/roblox-spinning-rock ("In This World, Everyone Lives on a Giant Spinning Rock").

Preserves the exact Aeresei R6 IK+FK V2.22 models (01_Alex_Protagonist & 02_Noob_BestFriend),
classic Roblox faces, Closest texture interpolation, smooth EEVEE AgX lighting, and snappy motion.
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Matrix, Vector

SHORTMAKING_ROOT = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking")
CAST_ROOT = SHORTMAKING_ROOT / "assets" / "roblox-r6-characters"
CHARS_DIR = CAST_ROOT / "characters"
PROJ_DIR = SHORTMAKING_ROOT / "videos" / "roblox-spinning-rock"
TEX_DIR = PROJ_DIR / "textures"
FRAMES_DIR = PROJ_DIR / "frames"
PREVIEWS_DIR = PROJ_DIR / "previews"
FRAMES_DIR.mkdir(parents=True, exist_ok=True)
PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(SHORTMAKING_ROOT / "90 Templates & Starter Kits" / "blender-cinema-kit"))
sys.path.insert(0, str(CAST_ROOT / "scripts"))
import blender_cinema_lib as bcl  # noqa: E402
from build_characters import MARKET_MANIFEST, RBX_PART_ATTACHMENTS, load_obj_to_blender_mesh  # noqa: E402

FPS = 30


def load_beats():
    return json.loads((PROJ_DIR / "voice" / "beats.json").read_text(encoding="utf-8"))


def load_words():
    return json.loads((PROJ_DIR / "voice" / "words.json").read_text(encoding="utf-8"))


def configure_eevee(scene, res_x=720, res_y=1280, samples=10):
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.resolution_percentage = 100
    scene.render.fps = FPS
    scene.render.use_persistent_data = True
    scene.render.use_motion_blur = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"

    scene.eevee.taa_render_samples = samples
    scene.eevee.use_shadows = True
    if hasattr(scene.eevee, "shadow_resolution_scale"):
        scene.eevee.shadow_resolution_scale = 0.85
    if hasattr(scene.eevee, "use_raytracing"):
        scene.eevee.use_raytracing = False
    if hasattr(scene.eevee, "use_fast_gi"):
        scene.eevee.use_fast_gi = False

    scene.display_settings.display_device = "sRGB"
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Punchy"
    scene.view_settings.exposure = -0.15


def build_switchable_world(scene):
    """Build a sky gradient world node tree whose colors/strength can switch cleanly per shot."""
    w = bcl._ensure_world(scene, "SpinRockWorld")
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")

    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[1].position = 0.45

    nt.links.new(tc.outputs["Generated"], sep.inputs["Vector"])
    nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])

    return {"world": w, "ramp": ramp, "bg": bg}


def set_world_mode(world_info: dict, mode: str):
    """Switch between @huss.hero crisp daytime blue sky, dramatic sunset red sky, and cosmic void."""
    ramp = world_info["ramp"]
    bg = world_info["bg"]
    if mode == "day":
        # Bright vibrant @huss.hero blue sky (#8FD8FF horizon -> #2A8CFF zenith)
        ramp.color_ramp.elements[0].position = 0.46
        ramp.color_ramp.elements[0].color = bcl.hex_to_linear("#93D8FF")
        ramp.color_ramp.elements[1].position = 0.68
        ramp.color_ramp.elements[1].color = bcl.hex_to_linear("#298CFF")
        bg.inputs["Strength"].default_value = 0.92
    elif mode == "sunset":
        # Dramatic @huss.hero red-orange climax sky (#EB681E horizon -> #3E0B0A zenith)
        ramp.color_ramp.elements[0].position = 0.46
        ramp.color_ramp.elements[0].color = bcl.hex_to_linear("#EB681E")
        ramp.color_ramp.elements[1].position = 0.68
        ramp.color_ramp.elements[1].color = bcl.hex_to_linear("#3A0A09")
        bg.inputs["Strength"].default_value = 0.80
    else:  # "space"
        ramp.color_ramp.elements[0].position = 0.0
        ramp.color_ramp.elements[0].color = bcl.hex_to_linear("#02040B")
        ramp.color_ramp.elements[1].position = 0.70
        ramp.color_ramp.elements[1].color = bcl.hex_to_linear("#070D1F")
        bg.inputs["Strength"].default_value = 0.35


def make_mat(name, hex_col, rough=0.42, metal=0.0, coat=0.10, emit_hex=None, emit_str=0.0):
    m = bpy.data.materials.get(name)
    if m is not None:
        return m
    return bcl.make_pbr_material(
        name, hex_col,
        roughness_min=max(0.08, rough - 0.04),
        roughness_max=min(0.95, rough + 0.05),
        metallic=metal,
        coat_weight=coat,
        bump_strength=0.010 if rough > 0.28 else 0.004,
        use_ao_node=False,
        emission_hex=emit_hex,
        emission_strength=emit_str,
    )


def make_image_mat(name, img_path: Path, rough=0.40, emit=0.08):
    m = bpy.data.materials.get(name)
    if m is not None:
        return m
    m = bpy.data.materials.new(name)
    if bpy.app.version < (5, 0, 0):
        m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = rough
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.20
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


def _link_only(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)
    return obj


def append_r6_character(
    char_id: str,
    instance_name: str,
    parent_col=None,
    atlas_filename: str | None = None,
    keep_acc: tuple = (),
    strip_all_default_acc: bool = False,
    extra_acc_key: str | None = None,
    hair_tint_hex: str | None = None,
):
    """
    Append an official Aeresei R6 IK+FK character, preserve exact rigging & faces,
    optionally swap grounded IRL outfit atlas and realistic hair/cap accessories.
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
    body_parts = {}
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
        elif o.type == "MESH":
            for pname in ("Head", "Torso", "Left Arm", "Right Arm", "Left Leg", "Right Leg"):
                if o.name.startswith(pname):
                    body_parts[pname] = o
                    if pname == "Head":
                        head_obj = o
                    break
            if o.name.startswith("Acc_"):
                if strip_all_default_acc:
                    should_keep = any(o.name.startswith(f"Acc_{k}") for k in keep_acc)
                    o.hide_viewport = not should_keep
                    o.hide_render = not should_keep
                elif keep_acc:
                    for k in keep_acc:
                        if o.name.startswith(f"Acc_{k}"):
                            o.hide_viewport = False
                            o.hide_render = False
                if hair_tint_hex and not o.hide_render and o.data.materials:
                    hm = o.data.materials[0].copy()
                    hm.name = f"Mat_{instance_name}_HairTint"
                    nt = hm.node_tree
                    for n in nt.nodes:
                        if n.type == "BSDF_PRINCIPLED":
                            for ln in list(nt.links):
                                if ln.to_node == n and ln.to_socket.name == "Base Color":
                                    nt.links.remove(ln)
                            n.inputs["Base Color"].default_value = bcl.hex_to_linear(hair_tint_hex)
                            n.inputs["Roughness"].default_value = 0.44
                    o.data.materials[0] = hm

    if arm:
        if arm.animation_data:
            arm.animation_data.action = None
        for pb in arm.pose.bones:
            pb.location = (0.0, 0.0, 0.0)
            pb.rotation_mode = "XYZ"
            pb.rotation_euler = (0.0, 0.0, 0.0)
            pb.scale = (1.0, 1.0, 1.0)

    for m in new_mats:
        if f"Mat_{char_id}_Body" in m.name:
            body_mat = m
            m.name = f"Mat_{instance_name}_Body"
            if m.node_tree:
                for n in m.node_tree.nodes:
                    if n.type == "TEX_IMAGE":
                        body_tex_node = n
                        n.interpolation = "Closest"
                    elif n.type == "BSDF_PRINCIPLED":
                        if "Specular IOR Level" in n.inputs:
                            n.inputs["Specular IOR Level"].default_value = 0.22
                        if "Coat Weight" in n.inputs:
                            n.inputs["Coat Weight"].default_value = 0.05
            break

    if atlas_filename and body_tex_node is not None:
        p = TEX_DIR / atlas_filename
        im = bpy.data.images.load(str(p), check_existing=False)
        im.name = f"{instance_name}_atlas.png"
        im.colorspace_settings.name = "sRGB"
        body_tex_node.image = im
        body_tex_node.interpolation = "Closest"

    # Optional extra IRL hair/cap from Marketplace manifest welded cleanly to Head bone
    if extra_acc_key and extra_acc_key in MARKET_MANIFEST and internal_arm and head_obj:
        entry = MARKET_MANIFEST[extra_acc_key]
        parsed = entry["parsed"]
        att_name = parsed.get("attachment_name") or "HairAttachment"
        _, part_att_pos_rbx = RBX_PART_ATTACHMENTS.get(att_name, ("Head", Vector((0.0, 5.1, 0.0))))
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

        me = load_obj_to_blender_mesh(entry["files"]["obj"], f"Mesh_{instance_name}_{extra_acc_key}", xform)
        acc_obj = bpy.data.objects.new(f"Acc_{instance_name}_{extra_acc_key}", me)
        (top_col or target_parent).objects.link(acc_obj)
        mat = make_mat(f"Mat_{instance_name}_{extra_acc_key}", hair_tint_hex or "#4A3222", rough=0.45, coat=0.06)
        if not hair_tint_hex and entry["files"].get("texture") and Path(entry["files"]["texture"]).exists():
            mat = make_image_mat(f"Mat_{instance_name}_{extra_acc_key}", Path(entry["files"]["texture"]), rough=0.44, emit=0.0)
        acc_obj.data.materials.append(mat)
        c = acc_obj.constraints.new("CHILD_OF")
        c.target = internal_arm
        c.subtarget = "Head"
        for rc in head_obj.constraints:
            if rc.type == "CHILD_OF" and rc.target == internal_arm and rc.subtarget == "Head":
                c.inverse_matrix = rc.inverse_matrix.copy()
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


def swap_atlas(char_info: dict, atlas_filename: str):
    node = char_info.get("body_tex_node")
    if node is None:
        return
    p = TEX_DIR / atlas_filename
    img = bpy.data.images.load(str(p), check_existing=True)
    img.colorspace_settings.name = "sRGB"
    if node.image != img:
        node.image = img
        node.interpolation = "Closest"


def set_char_transform(char_info: dict, wx: float, wy: float, wz: float, yaw_deg: float, pitch_deg: float = 0.0, roll_deg: float = 0.0, scale: float = 1.0):
    """Exact world-space placement, orientation, and uniform scale around character soles (0,0,0)."""
    arm = char_info["arm"]
    pb = arm.pose.bones["MasterControl"]
    m_rest = arm.data.bones["MasterControl"].matrix_local
    m_rest_inv = m_rest.inverted()
    m_rot = Euler((math.radians(pitch_deg), math.radians(roll_deg), math.radians(yaw_deg)), "XYZ").to_matrix().to_4x4()
    m_scale = Matrix.Scale(scale, 4)
    m_desired = Matrix.Translation((wx, wy, wz)) @ m_rot @ m_scale
    m_pose = m_rest_inv @ m_desired @ m_rest
    loc, quat, sc = m_pose.decompose()
    pb.location = loc
    pb.rotation_mode = "XYZ"
    pb.rotation_euler = quat.to_euler("XYZ")
    pb.scale = sc


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


def animate_walk(char_info: dict, t: float, phase: float = 0.0, speed: float = 5.5, stride: float = 0.35, arm_amp: float = 28.0):
    w = speed * t + phase
    bob = abs(math.sin(w)) * 0.12
    sw = math.sin(w)
    set_char_pose(
        char_info,
        torso_loc=(0.0, 0.0, bob),
        torso_rot=(2.5, 0.0, sw * 4.0),
        head_rot=(-2.0 + math.sin(w * 2) * 2.5, 0.0, -sw * 3.0),
        rarm_rot=(sw * arm_amp, 4.0, -8.0),
        larm_rot=(-sw * arm_amp, -4.0, 8.0),
        rleg_loc=(0.0, -sw * stride, max(0.0, -sw) * 0.24),
        lleg_loc=(0.0,  sw * stride, max(0.0,  sw) * 0.24),
    )


def animate_idle(char_info: dict, t: float, phase: float = 0.0, head_yaw: float = 0.0, head_pitch: float = 0.0):
    w = 2.6 * t + phase
    bob = math.sin(w) * 0.04
    set_char_pose(
        char_info,
        torso_loc=(0.0, 0.0, bob),
        torso_rot=(math.sin(w * 0.5) * 2.0, 0.0, math.cos(w * 0.5) * 2.5),
        head_rot=(head_pitch + math.sin(w) * 2.5, 0.0, head_yaw + math.sin(w * 0.7) * 4.0),
        rarm_rot=(math.sin(w) * 4.0, 3.0, -7.0),
        larm_rot=(-math.sin(w) * 4.0, -3.0, 7.0),
    )


def animate_argue(char_info: dict, t: float, phase: float = 0.0):
    w = 7.5 * t + phase
    set_char_pose(
        char_info,
        torso_loc=(0.0, 0.0, abs(math.sin(w)) * 0.09),
        torso_rot=(6.0 + math.sin(w) * 4.0, 0.0, math.sin(w * 0.5) * 6.0),
        head_rot=(-6.0 + math.sin(w * 1.3) * 7.0, 0.0, math.cos(w) * 8.0),
        rarm_rot=(-95.0 + math.sin(w) * 32.0, 12.0, -14.0),
        larm_rot=(-80.0 - math.cos(w) * 28.0, -12.0, 14.0),
    )


def set_camera_look(cam_obj, pos, target, lens=32.0, roll_deg=0.0, shake_k: int | None = None, shake_amp: float = 0.14):
    """Set camera position, target look-at, lens, Dutch roll, and optional 7-frame deterministic KICK."""
    p = Vector(pos)
    t = Vector(target)
    r_extra = 0.0
    if shake_k is not None and 0 <= shake_k < 7:
        decay = 1.0 - shake_k / 7.0
        sign = 1.0 if (shake_k % 2 == 0) else -1.0
        p.z += sign * shake_amp * decay
        p.x += sign * shake_amp * 0.45 * decay
        r_extra = sign * 1.8 * decay

    cam_obj.data.lens = lens
    cam_obj.location = p
    q = (t - p).to_track_quat("-Z", "Y")
    total_roll = roll_deg + r_extra
    if abs(total_roll) > 1e-4:
        q = q @ Euler((0.0, 0.0, math.radians(total_roll)), "XYZ").to_quaternion()
    cam_obj.rotation_euler = q.to_euler()


def set_hidden_tree(obj, hide: bool):
    obj.hide_viewport = hide
    obj.hide_render = hide
    for ch in obj.children:
        set_hidden_tree(ch, hide)


def render_frame(scene, frame_num: int, preview_tag: str | None = None):
    if preview_tag:
        out_p = PREVIEWS_DIR / f"{preview_tag}.png"
        scene.render.filepath = str(out_p)
        bpy.ops.render.render(write_still=True)
        print(f"  [STILL] {out_p.name}")
    else:
        out_p = FRAMES_DIR / f"f_{frame_num:04d}.png"
        if out_p.exists() and out_p.stat().st_size > 8000:
            return
        scene.render.filepath = str(out_p)
        bpy.ops.render.render(write_still=True)
