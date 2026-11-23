"""
scene_common.py — Shared Blender 5.3.0 Look-Dev, Stylized Textured PBR Shader,
Smooth Bevel, EEVEE RT+GI, Camera Grammar, and Crash-Resumable Render Engine for roblox-human-survival.
Reuses validated asset/texture libraries from roblox-reel-Df1kubCJ-o0-v2 plus custom project faces & prop banners.
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Vector

SHORTMAKING_ROOT = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking")
REF_DIR = SHORTMAKING_ROOT / "videos" / "roblox-reel-Df1kubCJ-o0-v2"
PROJ_DIR = SHORTMAKING_ROOT / "videos" / "roblox-human-survival"

TEX_ENV = REF_DIR / "textures" / "env"
TEX_CHARS = REF_DIR / "textures" / "chars"
TEX_REF_PROPS = REF_DIR / "textures" / "props"
TEX_FACES = PROJ_DIR / "textures" / "faces"
TEX_PROPS = PROJ_DIR / "textures" / "props"

FRAMES_DIR = PROJ_DIR / "frames"
PREVIEWS_DIR = PROJ_DIR / "previews"
FRAMES_DIR.mkdir(parents=True, exist_ok=True)
PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(SHORTMAKING_ROOT / "90 Templates & Starter Kits" / "blender-cinema-kit"))
import blender_cinema_lib as bcl


def load_beats():
    return json.loads((PROJ_DIR / "voice" / "beats.json").read_text(encoding="utf-8"))


def load_words():
    return json.loads((PROJ_DIR / "voice" / "words.json").read_text(encoding="utf-8"))


def beat_frame_range(beats_data, beat_id):
    fps = beats_data["fps"]
    beats = beats_data["beats"]
    for i, b in enumerate(beats):
        if b["id"] == beat_id:
            f0 = 1 if i == 0 else int(round(b["start"] * fps)) + 1
            if i + 1 < len(beats):
                f1 = int(round(beats[i + 1]["start"] * fps))
            else:
                f1 = int(round(beats_data["total_duration"] * fps))
            return max(1, f0), max(f0, f1)
    raise KeyError(f"Unknown beat_id: {beat_id}")


def configure_stylized_eevee(
    scene,
    res_x: int = 720,
    res_y: int = 1280,
    samples: int = 12,
    raytracing: bool = True,
    fast_gi: bool = True,
    motion_blur: bool = False,
    exposure: float = -0.08,
):
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.resolution_percentage = 100
    scene.render.fps = 30
    scene.render.use_persistent_data = True
    scene.render.use_motion_blur = motion_blur
    scene.render.motion_blur_shutter = 0.5
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"

    scene.eevee.taa_render_samples = samples
    scene.eevee.use_shadows = True
    if hasattr(scene.eevee, "shadow_resolution_scale"):
        scene.eevee.shadow_resolution_scale = 1.0
    if hasattr(scene.eevee, "use_raytracing"):
        scene.eevee.use_raytracing = raytracing
    if hasattr(scene.eevee, "use_fast_gi"):
        scene.eevee.use_fast_gi = fast_gi
    if hasattr(scene.eevee, "fast_gi_method"):
        scene.eevee.fast_gi_method = "GLOBAL_ILLUMINATION"

    scene.display_settings.display_device = "sRGB"
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Punchy"
    scene.view_settings.exposure = exposure


def setup_stylized_sky_world(scene, mode: str = "day", strength: float = 0.72):
    w = bcl._ensure_world(scene, f"World_{mode}")
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = strength

    if mode == "day":
        tc = nt.nodes.new("ShaderNodeTexCoord")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.0
        ramp.color_ramp.elements[0].color = bcl.hex_to_linear("#BAE6FD")
        ramp.color_ramp.elements[1].position = 0.48
        ramp.color_ramp.elements[1].color = bcl.hex_to_linear("#3898EC")
        nt.links.new(tc.outputs["Generated"], sep.inputs["Vector"])
        nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
        bg.inputs["Strength"].default_value = min(0.75, strength)
    elif mode == "night":
        tc = nt.nodes.new("ShaderNodeTexCoord")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.0
        ramp.color_ramp.elements[0].color = bcl.hex_to_linear("#1E1B4B")
        ramp.color_ramp.elements[1].position = 0.55
        ramp.color_ramp.elements[1].color = bcl.hex_to_linear("#090D24")
        nt.links.new(tc.outputs["Generated"], sep.inputs["Vector"])
        nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    elif mode == "dream":
        tc = nt.nodes.new("ShaderNodeTexCoord")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.0
        ramp.color_ramp.elements[0].color = bcl.hex_to_linear("#581C87")
        ramp.color_ramp.elements[1].position = 0.60
        ramp.color_ramp.elements[1].color = bcl.hex_to_linear("#0F172A")
        nt.links.new(tc.outputs["Generated"], sep.inputs["Vector"])
        nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    else:
        bg.inputs["Color"].default_value = bcl.hex_to_linear("#FFF4E4")

    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])


def _load_img(path: Path, is_data: bool = False):
    img = bpy.data.images.load(str(path), check_existing=True)
    img.colorspace_settings.name = "Non-Color" if is_data else "sRGB"
    return img


def make_stylized_pbr(
    name: str,
    hex_col: str,
    rough: float = 0.42,
    metal: float = 0.0,
    coat: float = 0.04,
    sheen: float = 0.0,
    sss: float = 0.0,
    bump_str: float = 0.02,
    ao_str: float = 0.22,
    emit_hex: str | None = None,
    emit_str: float = 0.0,
    alpha: float = 1.0,
):
    m = bpy.data.materials.get(name)
    if m is not None:
        return m
    m = bcl.make_pbr_material(
        name,
        hex_col,
        roughness_min=max(0.08, rough - 0.07),
        roughness_max=min(0.96, rough + 0.08),
        metallic=metal,
        diffuse_roughness=0.45,
        bump_strength=bump_str,
        bump_distance=0.010,
        noise_scale=12.0,
        weathering=ao_str,
        use_ao_node=True,
        coat_weight=coat,
        sheen_weight=sheen,
        sss_weight=sss,
        sss_scale=0.015,
        emission_hex=emit_hex,
        emission_strength=emit_str,
    )
    if alpha < 0.999:
        for n in m.node_tree.nodes:
            if n.type == "BSDF_PRINCIPLED":
                n.inputs["Alpha"].default_value = alpha
        if hasattr(m, "surface_render_method"):
            m.surface_render_method = "BLENDED"
    return m


def make_textured_pbr(
    name: str,
    tex_path: Path,
    bump_path: Path | None = None,
    tint_hex: str | None = None,
    proj: str = "BOX",
    uv_scale: tuple = (1.0, 1.0, 1.0),
    rough_min: float = 0.36,
    rough_max: float = 0.62,
    metallic: float = 0.0,
    coat: float = 0.0,
    sheen: float = 0.0,
    ao_str: float = 0.22,
    bump_strength: float = 0.14,
    emit_str: float = 0.0,
    alpha_clip: bool = False,
):
    m = bpy.data.materials.get(name)
    if m is not None:
        return m
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Diffuse Roughness"].default_value = 0.42
    bsdf.inputs["Coat Weight"].default_value = coat
    bsdf.inputs["Sheen Weight"].default_value = sheen

    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = uv_scale
    nt.links.new(tc.outputs["Object" if proj == "BOX" else "UV"], mp.inputs["Vector"])

    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = _load_img(tex_path, is_data=False)
    if proj == "BOX":
        tex.projection = "BOX"
        tex.projection_blend = 0.15
    nt.links.new(mp.outputs["Vector"], tex.inputs["Vector"])

    col_out = tex.outputs["Color"]
    if tint_hex:
        t_mix = nt.nodes.new("ShaderNodeMix")
        t_mix.data_type = "RGBA"
        t_mix.blend_type = "MULTIPLY"
        t_mix.inputs[0].default_value = 1.0
        t_mix.inputs[7].default_value = bcl.hex_to_linear(tint_hex)
        nt.links.new(col_out, t_mix.inputs[6])
        col_out = t_mix.outputs[2]

    if ao_str > 0.001:
        ao = nt.nodes.new("ShaderNodeAmbientOcclusion")
        ao.samples = 8
        ao.inputs["Distance"].default_value = 0.25
        ao_dark = nt.nodes.new("ShaderNodeMix")
        ao_dark.data_type = "RGBA"
        ao_dark.blend_type = "MULTIPLY"
        ao_dark.inputs[0].default_value = ao_str
        ao_dark.inputs[7].default_value = (0.28, 0.28, 0.34, 1.0)
        nt.links.new(col_out, ao_dark.inputs[6])

        ao_mix = nt.nodes.new("ShaderNodeMix")
        ao_mix.data_type = "RGBA"
        nt.links.new(ao.outputs["AO"], ao_mix.inputs[0])
        nt.links.new(ao_dark.outputs[2], ao_mix.inputs[6])
        nt.links.new(col_out, ao_mix.inputs[7])
        col_out = ao_mix.outputs[2]

    nt.links.new(col_out, bsdf.inputs["Base Color"])

    if emit_str > 0.0:
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = emit_str

    if alpha_clip:
        nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])

    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 9.0
    noise.inputs["Detail"].default_value = 5.0
    rmap = nt.nodes.new("ShaderNodeMapRange")
    rmap.clamp = True
    rmap.inputs["From Min"].default_value = 0.25
    rmap.inputs["From Max"].default_value = 0.75
    rmap.inputs["To Min"].default_value = rough_min
    rmap.inputs["To Max"].default_value = rough_max
    nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
    nt.links.new(noise.outputs["Fac"], rmap.inputs["Value"])
    nt.links.new(rmap.outputs["Result"], bsdf.inputs["Roughness"])

    if bump_path and bump_path.exists():
        btex = nt.nodes.new("ShaderNodeTexImage")
        btex.image = _load_img(bump_path, is_data=True)
        if proj == "BOX":
            btex.projection = "BOX"
            btex.projection_blend = 0.15
        nt.links.new(mp.outputs["Vector"], btex.inputs["Vector"])
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = bump_strength
        bump.inputs["Distance"].default_value = 0.012
        nt.links.new(btex.outputs["Color"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return m


def make_skin_face_mat(name: str, skin_hex: str, face_png: Path):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Diffuse Roughness"].default_value = 0.35
    bsdf.inputs["Subsurface Weight"].default_value = 0.14
    bsdf.inputs["Subsurface Scale"].default_value = 0.015
    bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.28, 0.14)
    bsdf.inputs["Coat Weight"].default_value = 0.0
    bsdf.inputs["Coat Roughness"].default_value = 0.50

    tc = nt.nodes.new("ShaderNodeTexCoord")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = _load_img(face_png, is_data=False)
    tex.extension = "CLIP"
    nt.links.new(tc.outputs["UV"], tex.inputs["Vector"])

    skin_col = bcl.hex_to_linear(skin_hex)
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion")
    ao.samples = 8
    ao.inputs["Distance"].default_value = 0.18
    ao_mix = nt.nodes.new("ShaderNodeMix")
    ao_mix.data_type = "RGBA"
    ao_mix.inputs[6].default_value = (skin_col[0] * 0.72, skin_col[1] * 0.68, skin_col[2] * 0.68, 1.0)
    ao_mix.inputs[7].default_value = skin_col
    nt.links.new(ao.outputs["AO"], ao_mix.inputs[0])

    fmix = nt.nodes.new("ShaderNodeMix")
    fmix.data_type = "RGBA"
    nt.links.new(tex.outputs["Alpha"], fmix.inputs[0])
    nt.links.new(ao_mix.outputs[2], fmix.inputs[6])
    nt.links.new(tex.outputs["Color"], fmix.inputs[7])
    nt.links.new(fmix.outputs[2], bsdf.inputs["Base Color"])

    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 14.0
    rmap = nt.nodes.new("ShaderNodeMapRange")
    rmap.clamp = True
    rmap.inputs["From Min"].default_value = 0.25
    rmap.inputs["From Max"].default_value = 0.75
    rmap.inputs["To Min"].default_value = 0.36
    rmap.inputs["To Max"].default_value = 0.46
    nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
    nt.links.new(noise.outputs["Fac"], rmap.inputs["Value"])

    rough_mix = nt.nodes.new("ShaderNodeMix")
    rough_mix.data_type = "FLOAT"
    rough_mix.inputs[3].default_value = 0.62
    nt.links.new(tex.outputs["Alpha"], rough_mix.inputs[0])
    nt.links.new(rmap.outputs["Result"], rough_mix.inputs[2])
    nt.links.new(rough_mix.outputs[0], bsdf.inputs["Roughness"])

    spec_mix = nt.nodes.new("ShaderNodeMix")
    spec_mix.data_type = "FLOAT"
    spec_mix.inputs[2].default_value = 0.26
    spec_mix.inputs[3].default_value = 0.04
    nt.links.new(tex.outputs["Alpha"], spec_mix.inputs[0])
    nt.links.new(spec_mix.outputs[0], bsdf.inputs["Specular IOR Level"])

    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return m, tex


def smooth_bevel(obj, width: float = 0.016, segments: int = 3, angle_deg: float = 32.0):
    if obj.type != "MESH":
        return obj
    for p in obj.data.polygons:
        p.use_smooth = True
    bev = obj.modifiers.new("Bevel", "BEVEL")
    bev.width = width
    bev.segments = segments
    bev.limit_method = "ANGLE"
    bev.angle_limit = math.radians(angle_deg)
    bev.harden_normals = False
    wn = obj.modifiers.new("WeightedNormal", "WEIGHTED_NORMAL")
    wn.keep_sharp = True
    return obj


def smooth_subsurf(obj, levels: int = 2):
    if obj.type != "MESH":
        return obj
    for p in obj.data.polygons:
        p.use_smooth = True
    sub = obj.modifiers.new("Subsurf", "SUBSURF")
    sub.levels = levels
    sub.render_levels = levels
    return obj


def link_only(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)
    return obj


def set_hidden_tree(obj, hide: bool):
    obj.hide_viewport = hide
    obj.hide_render = hide
    for ch in obj.children:
        set_hidden_tree(ch, hide)


def set_camera_look(cam_obj, pos, target, lens=35.0, roll_deg=0.0, fstop=3.2, focus_dist=None, kick_offset=-1, kick_amp=0.04):
    p = Vector(pos)
    t = Vector(target)
    roll = roll_deg
    if 0 <= kick_offset < 7:
        decay = 1.0 - kick_offset / 7.0
        sign = 1.0 if (kick_offset % 2 == 0) else -1.0
        p.z += sign * kick_amp * decay
        roll += sign * 1.15 * decay

    cam_obj.data.lens = lens
    cam_obj.location = p
    q = (t - p).to_track_quat("-Z", "Y")
    if abs(roll) > 1e-4:
        q = q @ Euler((0.0, 0.0, math.radians(roll)), "XYZ").to_quaternion()
    cam_obj.rotation_euler = q.to_euler()
    cam_obj.data.dof.use_dof = True
    cam_obj.data.dof.aperture_fstop = fstop
    cam_obj.data.dof.focus_distance = focus_dist if focus_dist else (t - p).length


def render_frame(scene, frame_num: int, preview_tag: str | None = None):
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
