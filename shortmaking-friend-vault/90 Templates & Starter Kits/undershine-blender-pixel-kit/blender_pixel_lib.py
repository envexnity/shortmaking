"""
blender_pixel_lib.py — Track 7: Undershine 3D-to-Pixel-Art Engine for Blender 5.3 EEVEE (with 4.2 fallback).

Implements:
- Native integer-divisor 9:16 pixel rendering (270x480 -> 4x 1080x1920, or 360x640 -> 3x)
- Razor-sharp pixel boundaries (filter_size=0.01) & crisp Sun shadows (angle=0.018 rad)
- Hue-shifted 3-band Shader-to-RGB materials with world-snapped procedural pixel grain
- Ghibli spherical-normal foliage canopies (NORMAL_EDIT RADIAL)
- Animated stylized pixel water & waterfall shaders
- Blender 5.3 Slotted Actions stepped-on-twos helper (`apply_stepped_on_twos`)
- Automated multi-angle camera rig + Timeline Marker switching (0 static holds)
- Multi-pass Compositor output (Combined, Depth16, Normal16, Mist, Emission) for t3ssel8r post-pass
"""

import os
import math
import random
import bpy
import bmesh
from mathutils import Vector, Euler


def srgb_to_linear_c(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_to_linear(hex_str: str, alpha: float = 1.0):
    h = hex_str.lstrip("#")
    r = srgb_to_linear_c(int(h[0:2], 16) / 255.0)
    g = srgb_to_linear_c(int(h[2:4], 16) / 255.0)
    b = srgb_to_linear_c(int(h[4:6], 16) / 255.0)
    return (r, g, b, alpha)


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def configure_undershine_eevee(
    scene,
    res_x: int = 270,
    res_y: int = 480,
    fps: int = 30,
    samples: int = 8,
    mist_start: float = 14.0,
    mist_depth: float = 42.0,
):
    scene.render.engine = "BLENDER_EEVEE" if bpy.app.version >= (5, 0, 0) else "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.resolution_percentage = 100
    scene.render.fps = fps
    scene.render.filter_size = 0.01  # Zero AA blur -> crisp native pixel grid
    scene.render.use_persistent_data = True  # Keep GPU buffers/textures resident across frames
    scene.render.image_settings.compression = 0  # Zero zlib CPU bottleneck on scratch frames

    scene.eevee.taa_render_samples = samples
    scene.eevee.use_shadows = True
    if hasattr(scene.eevee, "shadow_resolution_scale"):
        scene.eevee.shadow_resolution_scale = 1.0
    if hasattr(scene.eevee, "use_raytracing"):
        scene.eevee.use_raytracing = False  # Prevents screen-space RT speckle at 270x480

    # Standard color management preserves exact hue-shifted ramps cleanly
    scene.display_settings.display_device = "sRGB"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0

    # Enable passes for t3ssel8r depth/normal outlines + mist + emissive bloom
    vl = scene.view_layers[0]
    vl.use_pass_normal = True
    vl.use_pass_z = True
    vl.use_pass_mist = True
    vl.use_pass_emit = True

    # World setup + Mist range
    if scene.world is None:
        scene.world = bpy.data.worlds.new("UndershineWorld")
    if bpy.app.version < (5, 0, 0):
        scene.world.use_nodes = True
    scene.world.mist_settings.start = mist_start
    scene.world.mist_settings.depth = mist_depth
    scene.world.mist_settings.falloff = "QUADRATIC"


def setup_sky_world(
    scene,
    horizon_hex: str = "#e8a576",
    zenith_hex: str = "#384c82",
    ground_hex: str = "#222038",
    strength: float = 0.55,
):
    world = scene.world
    if bpy.app.version < (5, 0, 0):
        world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = strength

    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "LINEAR"

    # 3-stop sky gradient: ground bounce -> warm horizon -> deep sky zenith
    e0 = ramp.color_ramp.elements[0]
    e0.position = 0.0
    e0.color = hex_to_linear(ground_hex)
    e1 = ramp.color_ramp.elements[1]
    e1.position = 0.12
    e1.color = hex_to_linear(horizon_hex)
    e2 = ramp.color_ramp.elements.new(0.58)
    e2.color = hex_to_linear(zenith_hex)

    # Map Generated Z [-1..1] -> [0..1]
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = -0.15
    mr.inputs["From Max"].default_value = 0.75
    mr.inputs["To Min"].default_value = 0.0
    mr.inputs["To Max"].default_value = 1.0

    nt.links.new(tc.outputs["Generated"], sep.inputs["Vector"])
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    return bg, ramp


def make_hue_shifted_toon_mat(
    name: str,
    shadow_hex: str,
    mid_hex: str,
    lit_hex: str,
    grain_scale: float = 5.5,
    grain_amt: float = 0.14,
    snap_step: float = 0.14,
    stops=(0.14, 0.38, 0.68),
    deep_shadow_hex: str = None,
):
    """
    3-to-4 band hue-shifted Shader-to-RGB material with world-snapped procedural pixel grain.
    Eliminates smooth plastic CG look AND avoids harsh flat arcade colors.
    """
    mat = bpy.data.materials.new(name=name)
    if bpy.app.version < (5, 0, 0):
        mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    diff = nt.nodes.new("ShaderNodeBsdfDiffuse")
    diff.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    diff.inputs["Roughness"].default_value = 1.0

    s2rgb = nt.nodes.new("ShaderNodeShaderToRGB")
    rgb2bw = nt.nodes.new("ShaderNodeRGBToBW")

    # World-space texel-snapped noise so surfaces carry crisp pixel-art texture grain
    tc = nt.nodes.new("ShaderNodeTexCoord")
    snap = nt.nodes.new("ShaderNodeVectorMath")
    snap.operation = "SNAP"
    snap.inputs[1].default_value = (snap_step, snap_step, snap_step)

    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = grain_scale
    noise.inputs["Detail"].default_value = 2.0
    noise.inputs["Roughness"].default_value = 0.6

    # Center noise around 0 and scale by grain_amt
    n_sub = nt.nodes.new("ShaderNodeMath")
    n_sub.operation = "SUBTRACT"
    n_sub.inputs[1].default_value = 0.5

    n_mul = nt.nodes.new("ShaderNodeMath")
    n_mul.operation = "MULTIPLY"
    n_mul.inputs[1].default_value = grain_amt

    lum_add = nt.nodes.new("ShaderNodeMath")
    lum_add.operation = "ADD"
    lum_add.use_clamp = True

    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"

    # Build hue-shifted bands
    c_deep = hex_to_linear(deep_shadow_hex) if deep_shadow_hex else hex_to_linear(shadow_hex)
    c_shad = hex_to_linear(shadow_hex)
    c_mid = hex_to_linear(mid_hex)
    c_lit = hex_to_linear(lit_hex)

    e0 = ramp.color_ramp.elements[0]
    e0.position = 0.0
    e0.color = c_deep

    e1 = ramp.color_ramp.elements[1]
    e1.position = stops[0]
    e1.color = c_shad

    e2 = ramp.color_ramp.elements.new(stops[1])
    e2.color = c_mid

    e3 = ramp.color_ramp.elements.new(stops[2])
    e3.color = c_lit

    # Clamp direct light tint to <=0.68 so strong campfires/lanterns add rich warm color without clipping white!
    clamp_rgb = nt.nodes.new("ShaderNodeVectorMath")
    clamp_rgb.operation = "MINIMUM"
    clamp_rgb.inputs[1].default_value = (0.68, 0.68, 0.68)

    mix_warm = nt.nodes.new("ShaderNodeMix")
    mix_warm.data_type = "RGBA"
    mix_warm.blend_type = "ADD"
    mix_warm.inputs["Factor"].default_value = 0.16

    nt.links.new(diff.outputs["BSDF"], s2rgb.inputs["Shader"])
    nt.links.new(s2rgb.outputs["Color"], rgb2bw.inputs["Color"])

    nt.links.new(tc.outputs["Object"], snap.inputs[0])
    nt.links.new(snap.outputs["Vector"], noise.inputs["Vector"])
    nt.links.new(noise.outputs["Fac"], n_sub.inputs[0])
    nt.links.new(n_sub.outputs["Value"], n_mul.inputs[0])

    nt.links.new(rgb2bw.outputs["Val"], lum_add.inputs[0])
    nt.links.new(n_mul.outputs["Value"], lum_add.inputs[1])
    nt.links.new(lum_add.outputs["Value"], ramp.inputs["Fac"])

    nt.links.new(s2rgb.outputs["Color"], clamp_rgb.inputs[0])
    nt.links.new(ramp.outputs["Color"], mix_warm.inputs[6])       # A
    nt.links.new(clamp_rgb.outputs["Vector"], mix_warm.inputs[7])  # B (clamped warm fire/lantern bounce!)

    nt.links.new(mix_warm.outputs[2], out.inputs["Surface"])
    return mat


def make_emissive_mat(name: str, hex_col: str, strength: float = 5.0):
    mat = bpy.data.materials.new(name=name)
    if bpy.app.version < (5, 0, 0):
        mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = hex_to_linear(hex_col)
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    return mat


def make_water_mat(
    name: str = "Mat_Water",
    deep_hex: str = "#142942",
    mid_hex: str = "#225a78",
    lit_hex: str = "#368199",
    foam_hex: str = "#8ad4cf",
    snap_step: float = 0.16,
):
    """Serene Undershine pixel water with delicate flowing shimmer streaks & bold cast-shadow clarity."""
    mat = bpy.data.materials.new(name=name)
    if bpy.app.version < (5, 0, 0):
        mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    diff = nt.nodes.new("ShaderNodeBsdfDiffuse")
    diff.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    s2rgb = nt.nodes.new("ShaderNodeShaderToRGB")
    rgb2bw = nt.nodes.new("ShaderNodeRGBToBW")

    tc = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (1.6, 0.55, 1.0)  # Elongated flowing river streaks
    drv = mapping.inputs["Location"].driver_add("default_value", 1).driver
    drv.expression = "-frame * 0.045"

    snap = nt.nodes.new("ShaderNodeVectorMath")
    snap.operation = "SNAP"
    snap.inputs[1].default_value = (snap_step, snap_step, snap_step)

    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 2.4
    noise.inputs["Detail"].default_value = 1.5
    noise.inputs["Roughness"].default_value = 0.45

    # Sparse delicate foam/shimmer streaks (~12% surface) so cast shadows read razor-sharp!
    foam_ramp = nt.nodes.new("ShaderNodeValToRGB")
    foam_ramp.color_ramp.interpolation = "CONSTANT"
    foam_ramp.color_ramp.elements[0].position = 0.0
    foam_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    foam_ramp.color_ramp.elements[1].position = 0.72
    foam_ramp.color_ramp.elements[1].color = (0.85, 0.85, 0.85, 1.0)

    # Lighting bands on water (clearly shows shadows cast by bridge, trees & cliffs!)
    water_ramp = nt.nodes.new("ShaderNodeValToRGB")
    water_ramp.color_ramp.interpolation = "CONSTANT"
    water_ramp.color_ramp.elements[0].position = 0.0
    water_ramp.color_ramp.elements[0].color = hex_to_linear(deep_hex)
    water_ramp.color_ramp.elements[1].position = 0.28
    water_ramp.color_ramp.elements[1].color = hex_to_linear(mid_hex)
    e2 = water_ramp.color_ramp.elements.new(0.62)
    e2.color = hex_to_linear(lit_hex)

    # Suppress bright shimmer inside deep cast shadow so shadows stay dramatic
    foam_lit = nt.nodes.new("ShaderNodeMath")
    foam_lit.operation = "MULTIPLY"

    mix_foam = nt.nodes.new("ShaderNodeMix")
    mix_foam.data_type = "RGBA"
    mix_foam.inputs[7].default_value = hex_to_linear(foam_hex)

    clamp_rgb = nt.nodes.new("ShaderNodeVectorMath")
    clamp_rgb.operation = "MINIMUM"
    clamp_rgb.inputs[1].default_value = (0.55, 0.55, 0.55)

    mix_bounce = nt.nodes.new("ShaderNodeMix")
    mix_bounce.data_type = "RGBA"
    mix_bounce.blend_type = "ADD"
    mix_bounce.inputs["Factor"].default_value = 0.16

    nt.links.new(diff.outputs["BSDF"], s2rgb.inputs["Shader"])
    nt.links.new(s2rgb.outputs["Color"], rgb2bw.inputs["Color"])
    nt.links.new(rgb2bw.outputs["Val"], water_ramp.inputs["Fac"])

    nt.links.new(tc.outputs["Object"], mapping.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], snap.inputs[0])
    nt.links.new(snap.outputs["Vector"], noise.inputs["Vector"])
    nt.links.new(noise.outputs["Fac"], foam_ramp.inputs["Fac"])

    nt.links.new(foam_ramp.outputs["Color"], foam_lit.inputs[0])
    nt.links.new(rgb2bw.outputs["Val"], foam_lit.inputs[1])
    nt.links.new(foam_lit.outputs["Value"], mix_foam.inputs["Factor"])
    nt.links.new(water_ramp.outputs["Color"], mix_foam.inputs[6])

    nt.links.new(s2rgb.outputs["Color"], clamp_rgb.inputs[0])
    nt.links.new(mix_foam.outputs[2], mix_bounce.inputs[6])
    nt.links.new(clamp_rgb.outputs["Vector"], mix_bounce.inputs[7])
    nt.links.new(mix_bounce.outputs[2], out.inputs["Surface"])
    return mat


def make_foliage_tree(
    name: str,
    loc,
    scale: float,
    canopy_mat,
    trunk_mat,
    seed: int = 0,
    pine: bool = False,
    collection=None,
):
    """
    Creates an Undershine / Ghibli stylized 3D pixel tree with spherical transferred normals
    so canopy shadows stay lush, chunky, and painterly without noisy triangle speckles.
    """
    rng = random.Random(seed)
    col = collection or bpy.context.scene.collection
    parent = bpy.data.objects.new(name, None)
    parent.location = loc
    parent.rotation_euler = (0.0, 0.0, rng.uniform(0, math.tau))
    parent.scale = (scale, scale, scale)
    col.objects.link(parent)

    # Trunk
    bm_t = bmesh.new()
    trunk_h = 2.4 if not pine else 1.8
    bmesh.ops.create_cone(
        bm_t,
        cap_ends=True,
        cap_tris=False,
        segments=7,
        radius1=0.28,
        radius2=0.14,
        depth=trunk_h,
    )
    for v in bm_t.verts:
        v.co.z += trunk_h * 0.5
        if v.co.z > trunk_h * 0.4:
            v.co.x += 0.12 * math.sin(v.co.z * 1.4 + seed)
    mesh_t = bpy.data.meshes.new(f"{name}_TrunkMesh")
    bm_t.to_mesh(mesh_t)
    bm_t.free()
    obj_t = bpy.data.objects.new(f"{name}_Trunk", mesh_t)
    obj_t.data.materials.append(trunk_mat)
    obj_t.parent = parent
    col.objects.link(obj_t)

    # Canopy
    bm_c = bmesh.new()
    if pine:
        tiers = [
            (1.35, 1.30, 1.25),
            (2.25, 1.05, 1.15),
            (3.05, 0.78, 1.05),
            (3.75, 0.50, 0.90),
        ]
        for zc, rad, h in tiers:
            res = bmesh.ops.create_cone(
                bm_c,
                cap_ends=True,
                cap_tris=False,
                segments=8,
                radius1=rad,
                radius2=rad * 0.12,
                depth=h,
            )
            for v in res["verts"]:
                v.co.z += zc
                if v.co.z < zc:
                    v.co.x *= rng.uniform(0.90, 1.10)
                    v.co.y *= rng.uniform(0.90, 1.10)
        center_z = 2.6
    else:
        # Fluffy multi-puff oak/Ghibli canopy
        puffs = [
            (0.0, 0.0, 2.85, 1.25),
            (0.75, 0.35, 2.55, 0.92),
            (-0.72, 0.40, 2.50, 0.88),
            (0.25, -0.78, 2.60, 0.90),
            (-0.45, -0.55, 2.95, 0.85),
            (0.15, 0.15, 3.50, 0.82),
        ]
        for px, py, pz, pr in puffs:
            res = bmesh.ops.create_icosphere(bm_c, subdivisions=2, radius=pr)
            for v in res["verts"]:
                v.co.x = v.co.x * rng.uniform(0.92, 1.08) + px
                v.co.y = v.co.y * rng.uniform(0.92, 1.08) + py
                v.co.z = v.co.z * 0.82 + pz
        center_z = 2.75

    mesh_c = bpy.data.meshes.new(f"{name}_CanopyMesh")
    bm_c.to_mesh(mesh_c)
    bm_c.free()
    for poly in mesh_c.polygons:
        poly.use_smooth = True

    obj_c = bpy.data.objects.new(f"{name}_Canopy", mesh_c)
    obj_c.data.materials.append(canopy_mat)
    obj_c.parent = parent
    col.objects.link(obj_c)

    # Ghibli Spherical Normal Edit target (invisible empty at canopy core -> smooth painterly shading!)
    norm_empty = bpy.data.objects.new(f"{name}_NormCenter", None)
    norm_empty.location = (0.0, 0.0, center_z - 0.35)
    norm_empty.parent = parent
    col.objects.link(norm_empty)

    mod = obj_c.modifiers.new(name="GhibliSphericalNormals", type="NORMAL_EDIT")
    mod.mode = "RADIAL"
    mod.target = norm_empty
    mod.mix_factor = 0.85

    # Gentle breeze sway on canopy
    drv = obj_c.driver_add("rotation_euler", 0).driver
    drv.expression = f"0.025 * sin(frame * 0.07 + {seed:.2f})"
    drv2 = obj_c.driver_add("rotation_euler", 1).driver
    drv2.expression = f"0.02 * cos(frame * 0.055 + {seed * 1.3:.2f})"
    return parent


def smootherstep(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * u * (u * (u * 6.0 - 15.0) + 10.0)


def add_multi_angle_shot(
    scene,
    name: str,
    start_frame: int,
    end_frame: int,
    pos_start,
    pos_end,
    target_start,
    target_end,
    lens: float = 45.0,
    ortho_scale: float = None,
    roll_deg: float = 0.0,
    orbit_deg: float = 0.0,
    kick_frame: int = None,
    kick_amp: float = 0.14,
):
    """
    Creates a dedicated camera with smooth non-linear motion (zero static holds!),
    optional orbital arc, Dutch roll, impact kick, and binds it to a Timeline Marker
    so Blender switches cleanly across multi-angle shots during render.
    """
    cam_data = bpy.data.cameras.new(f"{name}_Data")
    if ortho_scale is not None:
        cam_data.type = "ORTHO"
        cam_data.ortho_scale = ortho_scale
    else:
        cam_data.type = "PERSP"
        cam_data.lens = lens
    cam_data.clip_start = 0.1
    cam_data.clip_end = 200.0

    cam_obj = bpy.data.objects.new(name, cam_data)
    scene.collection.objects.link(cam_obj)

    p0 = Vector(pos_start)
    p1 = Vector(pos_end)
    t0 = Vector(target_start)
    t1 = Vector(target_end)

    span = max(1, end_frame - start_frame)
    for f in range(start_frame, end_frame + 1):
        u = (f - start_frame) / span
        s = smootherstep(u)

        tgt = t0.lerp(t1, s)
        pos = p0.lerp(p1, s)

        if abs(orbit_deg) > 0.01:
            ang = math.radians(orbit_deg * s)
            rel = pos - tgt
            cos_a, sin_a = math.cos(ang), math.sin(ang)
            pos = Vector((
                tgt.x + rel.x * cos_a - rel.y * sin_a,
                tgt.y + rel.x * sin_a + rel.y * cos_a,
                pos.z,
            ))

        # Optional 7-frame alternating-sign impact kick
        roll_extra = 0.0
        if kick_frame is not None:
            k = f - kick_frame
            if 0 <= k < 7:
                decay = 1.0 - k / 7.0
                sign = 1.0 if (k % 2 == 0) else -1.0
                pos.z += sign * kick_amp * decay
                roll_extra = sign * 1.4 * decay

        direction = (tgt - pos).normalized()
        rot_quat = direction.to_track_quat("-Z", "Y")
        rot_mat = rot_quat.to_matrix().to_4x4()
        if abs(roll_deg + roll_extra) > 0.001:
            rot_mat = rot_mat @ Euler((0.0, 0.0, math.radians(roll_deg + roll_extra))).to_matrix().to_4x4()

        if ortho_scale is not None:
            # Style 24 (3D-Master-Vault) / Undershine World-Space Texel Grid Snap
            res_major = max(1, scene.render.resolution_y)
            unit_px = ortho_scale / float(res_major)
            rot3 = rot_mat.to_3x3()
            right_v = rot3 @ Vector((1.0, 0.0, 0.0))
            up_v = rot3 @ Vector((0.0, 1.0, 0.0))
            fwd_v = rot3 @ Vector((0.0, 0.0, -1.0))
            rx = round(pos.dot(right_v) / unit_px) * unit_px
            ry = round(pos.dot(up_v) / unit_px) * unit_px
            rz = pos.dot(fwd_v)
            pos = right_v * rx + up_v * ry + fwd_v * rz

        cam_obj.location = pos
        cam_obj.rotation_euler = rot_mat.to_euler()
        cam_obj.keyframe_insert(data_path="location", frame=f)
        cam_obj.keyframe_insert(data_path="rotation_euler", frame=f)

    # Bind camera to timeline marker
    marker = scene.timeline_markers.new(f"M_{name}", frame=start_frame)
    marker.camera = cam_obj
    if scene.camera is None:
        scene.camera = cam_obj
    return cam_obj


def get_action_fcurves(obj):
    """Return F-Curves across Blender 5.3 Slotted Actions (channelbag) and 4.x legacy Actions."""
    ad = getattr(obj, "animation_data", None)
    if not ad or not ad.action:
        return []
    act = ad.action
    if hasattr(act, "layers"):
        slot = ad.action_slot
        out = []
        for layer in act.layers:
            for strip in layer.strips:
                cb = strip.channelbag(slot)
                if cb:
                    out.extend(list(cb.fcurves))
        return out
    return list(getattr(act, "fcurves", []))


def apply_stepped_on_twos(obj, step: int = 2, data_path: str = None):
    """Step character animation on twos (15fps) inside a 30fps world/camera timeline."""
    for fc in get_action_fcurves(obj):
        if data_path and fc.data_path != data_path:
            continue
        mod = fc.modifiers.new(type="STEPPED")
        mod.frame_step = step


def set_action_interpolation(holder, interpolation: str = "CONSTANT"):
    """Set keyframe interpolation across all F-Curves on an Object, Light, or NodeTree (Blender 5.3 Slotted Actions safe)."""
    for fc in get_action_fcurves(holder):
        for kp in fc.keyframe_points:
            kp.interpolation = interpolation


def setup_passes_compositor(scene, passes_dir: str, depth_max: float = 55.0):
    """
    Exports 5 synchronized per-frame passes as portable PNGs (no EXR codec required):
      - img_####.png   (8-bit color-managed sRGB beauty)
      - depth_####.png (16-bit normalized linear depth 0..depth_max)
      - norm_####.png  (16-bit remapped XYZ normal 0..1)
      - mist_####.png  (8-bit mist factor 0..1)
      - emit_####.png  (8-bit emissive pass for warm bloom)
    Supports both Blender 5.3 (`compositor_effects`, `file_output_items`, `Emission`) and Blender 4.x.
    """
    os.makedirs(passes_dir, exist_ok=True)

    if bpy.app.version >= (5, 0, 0):
        ng = bpy.data.node_groups.new("UndershinePasses", "CompositorNodeTree")
        ng.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        if hasattr(scene, "compositor_effects"):
            scene.compositor_effects.clear()
            eff = scene.compositor_effects.new("UndershinePasses")
            eff.node_group = ng
        else:
            scene.compositing_node_group = ng

        nt = ng
        nt.nodes.clear()

        rl = nt.nodes.new("CompositorNodeRLayers")
        out = nt.nodes.new("NodeGroupOutput")
        nt.links.new(rl.outputs["Image"], out.inputs["Image"])

        emit_out = rl.outputs.get("Emission") or rl.outputs.get("Emit")

        # 1) 8-bit sRGB beauty + mist + emit output node (compression=0 avoids zlib CPU bottleneck)
        fo8 = nt.nodes.new("CompositorNodeOutputFile")
        fo8.directory = passes_dir
        fo8.file_name = ""
        fo8.format.media_type = "IMAGE"
        fo8.format.file_format = "PNG"
        fo8.format.color_mode = "RGB"
        fo8.format.color_depth = "8"
        fo8.format.compression = 0
        fo8.file_output_items.clear()
        fo8.file_output_items.new("RGBA", "img_####")
        fo8.file_output_items.new("FLOAT", "mist_####")
        fo8.file_output_items.new("RGBA", "emit_####")

        nt.links.new(rl.outputs["Image"], fo8.inputs[0])
        nt.links.new(rl.outputs["Mist"], fo8.inputs[1])
        nt.links.new(emit_out, fo8.inputs[2])

        # 2) 16-bit linear Depth & Normal output node (save_as_render=False keeps data linear!)
        fo16 = nt.nodes.new("CompositorNodeOutputFile")
        fo16.directory = passes_dir
        fo16.file_name = ""
        fo16.format.media_type = "IMAGE"
        fo16.format.file_format = "PNG"
        fo16.format.color_mode = "RGB"
        fo16.format.color_depth = "16"
        fo16.format.compression = 0
        fo16.file_output_items.clear()
        d_item = fo16.file_output_items.new("FLOAT", "depth_####")
        n_item = fo16.file_output_items.new("RGBA", "norm_####")
        d_item.save_as_render = False
        n_item.save_as_render = False

        # Normalize Depth [0..depth_max] -> [0..1]
        d_map = nt.nodes.new("ShaderNodeMapRange")
        d_map.clamp = True
        d_map.inputs["From Min"].default_value = 0.0
        d_map.inputs["From Max"].default_value = depth_max
        d_map.inputs["To Min"].default_value = 0.0
        d_map.inputs["To Max"].default_value = 1.0
        nt.links.new(rl.outputs["Depth"], d_map.inputs["Value"])
        nt.links.new(d_map.outputs["Result"], fo16.inputs[0])

        # Remap Normal [-1..1] -> [0..1] per channel: N * 0.5 + 0.5
        sep_n = nt.nodes.new("CompositorNodeSeparateColor")
        cmb_n = nt.nodes.new("CompositorNodeCombineColor")
        for ch in ("Red", "Green", "Blue"):
            m = nt.nodes.new("ShaderNodeMath")
            m.operation = "MULTIPLY_ADD"
            m.use_clamp = True
            m.inputs[1].default_value = 0.5
            m.inputs[2].default_value = 0.5
            nt.links.new(sep_n.outputs[ch], m.inputs[0])
            nt.links.new(m.outputs["Value"], cmb_n.inputs[ch])
        nt.links.new(rl.outputs["Normal"], sep_n.inputs["Image"])
        nt.links.new(cmb_n.outputs["Image"], fo16.inputs[1])
        return

    # Blender 4.x fallback
    scene.use_nodes = True
    nt = scene.node_tree
    nt.nodes.clear()

    rl = nt.nodes.new("CompositorNodeRLayers")
    comp = nt.nodes.new("CompositorNodeComposite")
    nt.links.new(rl.outputs["Image"], comp.inputs["Image"])

    # 1) 8-bit sRGB beauty + mist + emit output node
    fo8 = nt.nodes.new("CompositorNodeOutputFile")
    fo8.base_path = passes_dir
    fo8.format.file_format = "PNG"
    fo8.format.color_mode = "RGB"
    fo8.format.color_depth = "8"
    fo8.file_slots.clear()
    fo8.file_slots.new("img_")
    fo8.file_slots.new("mist_")
    fo8.file_slots.new("emit_")

    nt.links.new(rl.outputs["Image"], fo8.inputs[0])
    nt.links.new(rl.outputs["Mist"], fo8.inputs[1])
    nt.links.new(rl.outputs["Emit"], fo8.inputs[2])

    # 2) 16-bit linear Depth & Normal output node
    fo16 = nt.nodes.new("CompositorNodeOutputFile")
    fo16.base_path = passes_dir
    fo16.format.file_format = "PNG"
    fo16.format.color_mode = "RGB"
    fo16.format.color_depth = "16"
    fo16.file_slots.clear()
    fo16.file_slots.new("depth_")
    fo16.file_slots.new("norm_")

    # Normalize Depth [0..depth_max] -> [0..1]
    d_map = nt.nodes.new("CompositorNodeMapRange")
    d_map.use_clamp = True
    d_map.inputs["From Min"].default_value = 0.0
    d_map.inputs["From Max"].default_value = depth_max
    d_map.inputs["To Min"].default_value = 0.0
    d_map.inputs["To Max"].default_value = 1.0
    nt.links.new(rl.outputs["Depth"], d_map.inputs["Value"])
    nt.links.new(d_map.outputs["Value"], fo16.inputs[0])

    # Remap Normal [-1..1] -> [0..1] per channel: N * 0.5 + 0.5
    sep_n = nt.nodes.new("CompositorNodeSeparateColor")
    cmb_n = nt.nodes.new("CompositorNodeCombineColor")
    for ch in ("Red", "Green", "Blue"):
        m = nt.nodes.new("CompositorNodeMath")
        m.operation = "MULTIPLY_ADD"
        m.use_clamp = True
        m.inputs[1].default_value = 0.5
        m.inputs[2].default_value = 0.5
        nt.links.new(sep_n.outputs[ch], m.inputs[0])
        nt.links.new(m.outputs["Value"], cmb_n.inputs[ch])
    nt.links.new(rl.outputs["Normal"], sep_n.inputs["Image"])
    nt.links.new(cmb_n.outputs["Image"], fo16.inputs[1])
