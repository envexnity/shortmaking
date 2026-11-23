"""
blender_cinema_lib.py — Blender 5.3.0 Cinematic Rendering, Lighting, Shading & Animation Kit.

Built and verified for Blender 5.3.0 (Python 3.13) on NVIDIA RTX 2050 (OptiX + OIDN GPU),
covering Track 4 (Realistic / Stylized 3D) and Track 5 (Roblox R6/R15 Blender renders).

Provides:
- Cycles OptiX GPU + OpenImageDenoise & EEVEE 5.3 Raytracing configurators (AgX - Punchy)
- Physical Multiple-Scattering Sky & Dark Studio Worlds (killing flat default grey)
- Kelvin-calibrated 3-Point Studio Lighting Rig with narrow directional spread
- Bounded Principled Volume atmospheric fog boxes (shafts without killing sky light)
- Procedural non-plastic PBR material builder (roughness breakup, bump, AO dirt, Diffuse Roughness, SSS, Coat)
- Cinema bevel + weighted normal helper for crisp edge specular catchlights
- Blender 5.3 Slotted Actions F-Curve easing, stepped on-twos, and handheld camera noise
- Multi-angle Timeline Marker camera builder with animated DOF focus empty & 7-frame impact kicks
- Blender 5.3 native scene.compositor_effects pipeline (Fog Glow, Color Balance, Dispersion, Vignette)
"""

import math
import bpy


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


def _ensure_world(scene, name: str = "CinemaWorld"):
    if scene.world is None:
        scene.world = bpy.data.worlds.new(name)
    if bpy.app.version < (5, 0, 0):
        scene.world.use_nodes = True
    return scene.world


def configure_cycles_optix(
    scene,
    res_x: int = 1080,
    res_y: int = 1920,
    fps: int = 30,
    samples: int = 48,
    adaptive_threshold: float = 0.02,
    view_transform: str = "AgX",
    look: str = "AgX - Punchy",
    motion_blur: bool = True,
    shutter: float = 0.5,
):
    """Configure Cycles on NVIDIA RTX 2050 OptiX GPU with OIDN prefiltering and bounded bounces."""
    scene.render.engine = "CYCLES"
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.resolution_percentage = 100
    scene.render.fps = fps
    scene.render.use_persistent_data = True
    scene.render.use_motion_blur = motion_blur
    scene.render.motion_blur_shutter = shutter

    prefs = bpy.context.preferences.addons["cycles"].preferences
    device_selected = False
    for backend in ("OPTIX", "CUDA"):
        try:
            prefs.compute_device_type = backend
            prefs.get_devices()
            gpu_devices = [d for d in prefs.devices if d.type == backend]
            if gpu_devices:
                for d in prefs.devices:
                    d.use = d.type == backend
                scene.cycles.device = "GPU"
                device_selected = True
                break
        except Exception:
            continue
    if not device_selected:
        scene.cycles.device = "CPU"

    scene.cycles.samples = samples
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = adaptive_threshold
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = "OPENIMAGEDENOISE"
    scene.cycles.denoising_input_passes = "RGB_ALBEDO_NORMAL"
    scene.cycles.denoising_prefilter = "ACCURATE"
    scene.cycles.denoising_use_gpu = True

    scene.cycles.use_light_tree = True
    scene.cycles.max_bounces = 6
    scene.cycles.diffuse_bounces = 3
    scene.cycles.glossy_bounces = 3
    scene.cycles.transmission_bounces = 6
    scene.cycles.volume_bounces = 1
    scene.cycles.transparent_max_bounces = 6
    scene.cycles.sample_clamp_indirect = 8.0

    scene.display_settings.display_device = "sRGB"
    scene.view_settings.view_transform = view_transform
    scene.view_settings.look = look
    scene.view_settings.exposure = 0.0


def configure_eevee_cinema(
    scene,
    res_x: int = 1080,
    res_y: int = 1920,
    fps: int = 30,
    samples: int = 32,
    raytracing: bool = True,
    fast_gi: bool = True,
    view_transform: str = "AgX",
    look: str = "AgX - Punchy",
    motion_blur: bool = True,
    shutter: float = 0.5,
    shadow_resolution_scale: float = 1.0,
):
    """Configure Blender 5.3 EEVEE (`BLENDER_EEVEE`) with Raytracing, Fast GI, and AgX color."""
    scene.render.engine = "BLENDER_EEVEE" if bpy.app.version >= (5, 0, 0) else "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.resolution_percentage = 100
    scene.render.fps = fps
    scene.render.use_persistent_data = True
    scene.render.use_motion_blur = motion_blur
    scene.render.motion_blur_shutter = shutter

    scene.eevee.taa_render_samples = samples
    scene.eevee.use_shadows = True
    if hasattr(scene.eevee, "shadow_resolution_scale"):
        scene.eevee.shadow_resolution_scale = shadow_resolution_scale
    if hasattr(scene.eevee, "use_raytracing"):
        scene.eevee.use_raytracing = raytracing
    if hasattr(scene.eevee, "use_fast_gi"):
        scene.eevee.use_fast_gi = fast_gi
    if hasattr(scene.eevee, "fast_gi_method"):
        scene.eevee.fast_gi_method = "GLOBAL_ILLUMINATION"

    scene.display_settings.display_device = "sRGB"
    scene.view_settings.view_transform = view_transform
    scene.view_settings.look = look
    scene.view_settings.exposure = 0.0


def configure_fast_stylized_eevee(
    scene,
    res_x: int = 720,
    res_y: int = 1280,
    fps: int = 24,
    samples: int = 8,
    exposure: float = -0.10,
    shadow_resolution_scale: float = 0.65,
    motion_blur: bool = False,
):
    """4GB-VRAM-friendly fast stylized EEVEE preset (no RT/Fast-GI overhead, 3x-6x faster)."""
    configure_eevee_cinema(
        scene,
        res_x=res_x,
        res_y=res_y,
        fps=fps,
        samples=samples,
        raytracing=False,
        fast_gi=False,
        motion_blur=motion_blur,
        shadow_resolution_scale=shadow_resolution_scale,
    )
    scene.view_settings.exposure = exposure


def setup_physical_sky(
    scene,
    sun_elevation_deg: float = 14.0,
    sun_rotation_deg: float = 35.0,
    air_density: float = 1.2,
    aerosol_density: float = 1.8,
    ozone_density: float = 1.5,
    strength: float = 0.6,
):
    """Set up Blender 5.3 physical MULTIPLE_SCATTERING sky (replaces removed NISHITA/dust_density)."""
    world = _ensure_world(scene, "CinemaPhysicalSky")
    nt = world.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = strength

    sky = nt.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "MULTIPLE_SCATTERING"
    sky.sun_disc = True
    sky.sun_elevation = math.radians(sun_elevation_deg)
    sky.sun_rotation = math.radians(sun_rotation_deg)
    sky.air_density = air_density
    sky.aerosol_density = aerosol_density
    sky.ozone_density = ozone_density

    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    return sky, bg


def setup_dark_studio_world(scene, hex_col: str = "#0c101a", strength: float = 0.12):
    """Replace flat default grey world with deep cool studio ambience for sculpted 3-point contrast."""
    world = _ensure_world(scene, "CinemaStudioWorld")
    nt = world.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = hex_to_linear(hex_col)
    bg.inputs["Strength"].default_value = strength
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    return bg


def _make_area_light(name, loc, target_obj, energy, size, temperature, spread_deg, collection):
    ldata = bpy.data.lights.new(name=f"{name}_Data", type="AREA")
    ldata.shape = "RECTANGLE"
    ldata.size = size
    ldata.size_y = size * 0.7
    ldata.energy = energy
    ldata.spread = math.radians(spread_deg)
    ldata.use_temperature = True
    ldata.temperature = temperature
    ldata.use_shadow = True

    lobj = bpy.data.objects.new(name, ldata)
    lobj.location = loc
    collection.objects.link(lobj)

    trk = lobj.constraints.new(type="TRACK_TO")
    trk.target = target_obj
    trk.track_axis = "TRACK_NEGATIVE_Z"
    trk.up_axis = "UP_Y"
    return lobj


def add_studio_3point_rig(
    target_loc=(0.0, 0.0, 1.0),
    radius: float = 4.5,
    key_energy: float = 900.0,
    rim_energy: float = 1400.0,
    fill_energy: float = 180.0,
    key_temp: float = 4400.0,
    rim_temp: float = 7600.0,
    fill_temp: float = 6800.0,
    collection=None,
):
    """Create a Kelvin-calibrated 3-point rig (warm key, cool directional rim, subtle soft fill)."""
    col = collection or bpy.context.scene.collection
    tx, ty, tz = target_loc

    target = bpy.data.objects.new("LightRig_Target", None)
    target.location = target_loc
    col.objects.link(target)

    # Camera typically looks from -Y toward origin: Key front-right, Fill front-left, Rim back-left
    key = _make_area_light(
        "Cinema_KeyLight",
        (tx + radius * 0.75, ty - radius * 0.72, tz + radius * 0.62),
        target,
        energy=key_energy,
        size=1.8,
        temperature=key_temp,
        spread_deg=70.0,
        collection=col,
    )
    fill = _make_area_light(
        "Cinema_FillLight",
        (tx - radius * 0.90, ty - radius * 0.65, tz + radius * 0.30),
        target,
        energy=fill_energy,
        size=3.6,
        temperature=fill_temp,
        spread_deg=115.0,
        collection=col,
    )
    rim = _make_area_light(
        "Cinema_RimLight",
        (tx - radius * 0.55, ty + radius * 0.85, tz + radius * 0.78),
        target,
        energy=rim_energy,
        size=1.6,
        temperature=rim_temp,
        spread_deg=55.0,
        collection=col,
    )
    return {"target": target, "key": key, "fill": fill, "rim": rim}


def add_bounded_fog_volume(
    name: str = "AtmosFog",
    location=(0.0, 0.0, 3.0),
    scale=(18.0, 18.0, 9.0),
    density: float = 0.015,
    anisotropy: float = 0.62,
    tint_hex: str = "#9cb8d8",
    collection=None,
):
    """Add a bounded Principled Volume cube (gives volumetric shafts without blocking sky sun)."""
    col = collection or bpy.context.scene.collection
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    box = bpy.context.active_object
    box.name = name
    box.scale = scale
    box.display_type = "WIRE"

    if col not in box.users_collection:
        col.objects.link(box)

    mat = bpy.data.materials.new(name=f"{name}_VolMat")
    if bpy.app.version < (5, 0, 0):
        mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    vol = nt.nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs["Color"].default_value = hex_to_linear(tint_hex)
    vol.inputs["Density"].default_value = density
    vol.inputs["Anisotropy"].default_value = anisotropy

    nt.links.new(vol.outputs["Volume"], out.inputs["Volume"])
    box.data.materials.append(mat)
    return box


def make_pbr_material(
    name: str,
    base_hex: str,
    roughness_min: float = 0.32,
    roughness_max: float = 0.62,
    metallic: float = 0.0,
    diffuse_roughness: float = 0.45,
    bump_strength: float = 0.08,
    bump_distance: float = 0.015,
    noise_scale: float = 8.0,
    weathering: float = 0.28,
    use_ao_node: bool = False,
    ao_samples: int = 8,
    coat_weight: float = 0.0,
    coat_roughness: float = 0.1,
    sheen_weight: float = 0.0,
    sss_weight: float = 0.0,
    sss_scale: float = 0.015,
    sss_radius=(1.0, 0.28, 0.14),
    emission_hex: str = None,
    emission_strength: float = 0.0,
):
    """
    Build a non-plastic procedural PBR material with dual-frequency albedo weathering,
    noise-modulated roughness breakup, micro-surface bump, and Blender 5.3 BSDF physics.

    Note: Leave `use_ao_node=False` (default) when rendering on Cycles OptiX (RTX 2050):
    `ShaderNodeAmbientOcclusion` triggers `OPTIX_SHADER_RAYTRACE` PTX compilation that can stall >200s.
    Use `use_ao_node=True` only for EEVEE-only scenes.
    """
    mat = bpy.data.materials.new(name=name)
    if bpy.app.version < (5, 0, 0):
        mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")

    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Diffuse Roughness"].default_value = diffuse_roughness
    bsdf.inputs["Coat Weight"].default_value = coat_weight
    bsdf.inputs["Coat Roughness"].default_value = coat_roughness
    bsdf.inputs["Sheen Weight"].default_value = sheen_weight
    bsdf.inputs["Subsurface Weight"].default_value = sss_weight
    bsdf.inputs["Subsurface Scale"].default_value = sss_scale
    bsdf.inputs["Subsurface Radius"].default_value = sss_radius

    if emission_hex and emission_strength > 0.0:
        bsdf.inputs["Emission Color"].default_value = hex_to_linear(emission_hex)
        bsdf.inputs["Emission Strength"].default_value = emission_strength

    # Object-space procedural micro-detail
    tc = nt.nodes.new("ShaderNodeTexCoord")
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = noise_scale
    noise.inputs["Detail"].default_value = 6.0
    noise.inputs["Roughness"].default_value = 0.58

    # Roughness variation (prevents uniform plastic sheen)
    rmap = nt.nodes.new("ShaderNodeMapRange")
    rmap.clamp = True
    rmap.inputs["From Min"].default_value = 0.25
    rmap.inputs["From Max"].default_value = 0.75
    rmap.inputs["To Min"].default_value = roughness_min
    rmap.inputs["To Max"].default_value = roughness_max

    # Micro-bump
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = bump_strength
    bump.inputs["Distance"].default_value = bump_distance

    nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
    nt.links.new(noise.outputs["Fac"], rmap.inputs["Value"])
    nt.links.new(rmap.outputs["Result"], bsdf.inputs["Roughness"])

    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    base_col = hex_to_linear(base_hex)
    patina_col = (
        base_col[0] * 0.62,
        base_col[1] * 0.62,
        base_col[2] * 0.68,
        1.0,
    )

    if use_ao_node:
        # Opt-in EEVEE crevice AO darkening
        ao = nt.nodes.new("ShaderNodeAmbientOcclusion")
        ao.samples = ao_samples
        ao.inputs["Color"].default_value = base_col
        ao.inputs["Distance"].default_value = 0.35

        ao_dark = nt.nodes.new("ShaderNodeMix")
        ao_dark.data_type = "RGBA"
        ao_dark.blend_type = "MULTIPLY"
        ao_dark.inputs[0].default_value = weathering
        ao_dark.inputs[6].default_value = base_col
        ao_dark.inputs[7].default_value = (
            base_col[0] * 0.22,
            base_col[1] * 0.22,
            base_col[2] * 0.28,
            1.0,
        )

        ao_mix = nt.nodes.new("ShaderNodeMix")
        ao_mix.data_type = "RGBA"
        nt.links.new(ao.outputs["AO"], ao_mix.inputs[0])
        nt.links.new(ao_dark.outputs[2], ao_mix.inputs[6])
        ao_mix.inputs[7].default_value = base_col
        nt.links.new(ao_mix.outputs[2], bsdf.inputs["Base Color"])
    else:
        # Dual-frequency macro noise weathering (zero OPTIX_SHADER_RAYTRACE overhead)
        macro_noise = nt.nodes.new("ShaderNodeTexNoise")
        macro_noise.inputs["Scale"].default_value = max(0.5, noise_scale * 0.28)
        macro_noise.inputs["Detail"].default_value = 4.0
        macro_noise.inputs["Roughness"].default_value = 0.55

        w_map = nt.nodes.new("ShaderNodeMapRange")
        w_map.clamp = True
        w_map.inputs["From Min"].default_value = 0.30
        w_map.inputs["From Max"].default_value = 0.72
        w_map.inputs["To Min"].default_value = 0.0
        w_map.inputs["To Max"].default_value = weathering

        albedo_mix = nt.nodes.new("ShaderNodeMix")
        albedo_mix.data_type = "RGBA"
        albedo_mix.blend_type = "MIX"
        albedo_mix.inputs[6].default_value = base_col
        albedo_mix.inputs[7].default_value = patina_col

        nt.links.new(tc.outputs["Object"], macro_noise.inputs["Vector"])
        nt.links.new(macro_noise.outputs["Fac"], w_map.inputs["Value"])
        nt.links.new(w_map.outputs["Result"], albedo_mix.inputs[0])
        nt.links.new(albedo_mix.outputs[2], bsdf.inputs["Base Color"])

    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def add_cinema_bevel(
    obj,
    width: float = 0.015,
    segments: int = 2,
    angle_deg: float = 30.0,
    smooth: bool = True,
    weighted_normal: bool = True,
):
    """Eliminate razor-sharp CG edges by adding angled Bevel + Smooth + Weighted Normals."""
    if obj.type != "MESH":
        return obj
    if smooth:
        for poly in obj.data.polygons:
            poly.use_smooth = True

    bev = obj.modifiers.new(name="CinemaBevel", type="BEVEL")
    bev.width = width
    bev.segments = segments
    bev.limit_method = "ANGLE"
    bev.angle_limit = math.radians(angle_deg)
    bev.harden_normals = False

    if weighted_normal:
        wn = obj.modifiers.new(name="CinemaWeightedNormal", type="WEIGHTED_NORMAL")
        wn.keep_sharp = True
    return obj


def get_action_fcurves(obj):
    """Return all F-Curves for obj across Blender 5.3 Slotted Actions and 4.x legacy Actions."""
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


def set_keyframe_easing(
    obj,
    data_path: str = None,
    interpolation: str = "BEZIER",
    easing: str = "EASE_IN_OUT",
):
    """Set non-linear keyframe interpolation & easing on Slotted Actions (kills robotic motion)."""
    for fc in get_action_fcurves(obj):
        if data_path and fc.data_path != data_path:
            continue
        for kp in fc.keyframe_points:
            kp.interpolation = interpolation
            kp.easing = easing


def apply_stepped_on_twos(obj, step: int = 2, data_path: str = None):
    """Apply STEPPED modifier on twos (15fps character motion inside 30fps camera/world)."""
    for fc in get_action_fcurves(obj):
        if data_path and fc.data_path != data_path:
            continue
        mod = fc.modifiers.new(type="STEPPED")
        mod.frame_step = step


def add_handheld_camera_noise(
    cam_obj,
    rot_strength: float = 0.005,
    loc_strength: float = 0.012,
    scale: float = 34.0,
    phase: float = 0.0,
):
    """Add organic low-frequency handheld camera breathing without jittery high-freq shake."""
    for fc in get_action_fcurves(cam_obj):
        if fc.data_path == "rotation_euler" and fc.array_index in (0, 2):
            mod = fc.modifiers.new(type="NOISE")
            mod.scale = scale
            mod.strength = rot_strength
            mod.phase = phase + fc.array_index * 11.7
            mod.blend_type = "ADD"
        elif fc.data_path == "location" and fc.array_index in (0, 2):
            mod = fc.modifiers.new(type="NOISE")
            mod.scale = scale * 1.15
            mod.strength = loc_strength
            mod.phase = phase + fc.array_index * 7.3
            mod.blend_type = "ADD"


def smootherstep(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * u * (u * (u * 6.0 - 15.0) + 10.0)


def add_animated_shot_camera(
    scene,
    name: str,
    start_frame: int,
    end_frame: int,
    pos_start,
    pos_end,
    target_start,
    target_end,
    lens: float = 50.0,
    fstop: float = 2.8,
    use_dof: bool = True,
    aperture_blades: int = 7,
    roll_deg: float = 0.0,
    orbit_deg: float = 0.0,
    kick_frame: int = None,
    kick_amp: float = 0.12,
    handheld: float = 0.0,
):
    """
    Create a dedicated cinematic camera with smootherstep motion, animated DOF focus target,
    optional orbital sweep, 7-frame impact kick, subtle handheld noise, and timeline marker cut.
    """
    from mathutils import Vector, Euler

    cam_data = bpy.data.cameras.new(f"{name}_Data")
    cam_data.type = "PERSP"
    cam_data.lens = lens
    cam_data.clip_start = 0.08
    cam_data.clip_end = 500.0
    cam_data.dof.use_dof = use_dof
    cam_data.dof.aperture_fstop = fstop
    cam_data.dof.aperture_blades = aperture_blades

    focus_empty = bpy.data.objects.new(f"{name}_Focus", None)
    scene.collection.objects.link(focus_empty)
    cam_data.dof.focus_object = focus_empty

    cam_obj = bpy.data.objects.new(name, cam_data)
    scene.collection.objects.link(cam_obj)

    p0, p1 = Vector(pos_start), Vector(pos_end)
    t0, t1 = Vector(target_start), Vector(target_end)

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

        roll_extra = 0.0
        if kick_frame is not None:
            k = f - kick_frame
            if 0 <= k < 7:
                decay = 1.0 - k / 7.0
                sign = 1.0 if (k % 2 == 0) else -1.0
                pos.z += sign * kick_amp * decay
                roll_extra = sign * 1.35 * decay

        direction = (tgt - pos).normalized()
        rot_quat = direction.to_track_quat("-Z", "Y")
        rot_mat = rot_quat.to_matrix().to_4x4()
        if abs(roll_deg + roll_extra) > 0.001:
            rot_mat = rot_mat @ Euler((0.0, 0.0, math.radians(roll_deg + roll_extra))).to_matrix().to_4x4()

        focus_empty.location = tgt
        focus_empty.keyframe_insert(data_path="location", frame=f)

        cam_obj.location = pos
        cam_obj.rotation_euler = rot_mat.to_euler()
        cam_obj.keyframe_insert(data_path="location", frame=f)
        cam_obj.keyframe_insert(data_path="rotation_euler", frame=f)

    if handheld > 0.0:
        add_handheld_camera_noise(
            cam_obj,
            rot_strength=0.005 * handheld,
            loc_strength=0.012 * handheld,
        )

    marker = scene.timeline_markers.new(f"M_{name}", frame=start_frame)
    marker.camera = cam_obj
    if scene.camera is None:
        scene.camera = cam_obj
    return cam_obj, focus_empty


def setup_cinema_compositor(
    scene,
    glare_type: str = "Fog Glow",
    glare_threshold: float = 1.25,
    glare_strength: float = 0.22,
    glare_size: float = 0.65,
    dispersion: float = 0.005,
    distortion: float = -0.01,
    lift_rgb=(0.98, 0.99, 1.02),
    gamma_rgb=(1.0, 1.0, 1.0),
    gain_rgb=(1.03, 1.01, 0.98),
    vignette: float = 0.18,
):
    """
    Build Blender 5.3 native scene.compositor_effects pipeline:
    Render Layers -> Fog Glow Glare -> Color Balance (Lift/Gamma/Gain) -> Lens Dispersion -> Soft Vignette -> Group Output.
    """
    scene.compositor_effects.clear()
    ng = bpy.data.node_groups.new("CinemaPostTree", "CompositorNodeTree")
    ng.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")

    eff = scene.compositor_effects.new("CinemaPost")
    eff.node_group = ng

    rl = ng.nodes.new("CompositorNodeRLayers")
    out = ng.nodes.new("NodeGroupOutput")

    glare = ng.nodes.new("CompositorNodeGlare")
    glare.inputs["Type"].default_value = glare_type
    glare.inputs["Quality"].default_value = "High"
    glare.inputs["Threshold"].default_value = glare_threshold
    glare.inputs["Strength"].default_value = glare_strength
    glare.inputs["Size"].default_value = glare_size

    cb = ng.nodes.new("CompositorNodeColorBalance")
    cb.inputs["Type"].default_value = "Lift/Gamma/Gain"
    cb_by_id = {inp.identifier: inp for inp in cb.inputs}
    cb_by_id["Color Lift"].default_value = (*lift_rgb, 1.0)
    cb_by_id["Color Gamma"].default_value = (*gamma_rgb, 1.0)
    cb_by_id["Color Gain"].default_value = (*gain_rgb, 1.0)

    lens = ng.nodes.new("CompositorNodeLensdist")
    lens.inputs["Type"].default_value = "Radial"
    lens.inputs["Distortion"].default_value = distortion
    lens.inputs["Dispersion"].default_value = dispersion
    lens.inputs["Fit"].default_value = True

    ng.links.new(rl.outputs["Image"], glare.inputs["Image"])
    ng.links.new(glare.outputs["Image"], cb.inputs["Image"])
    ng.links.new(cb.outputs["Image"], lens.inputs["Image"])

    if vignette > 0.0:
        mask = ng.nodes.new("CompositorNodeEllipseMask")
        mask.inputs["Position"].default_value = (0.5, 0.5)
        mask.inputs["Size"].default_value = (0.92, 0.92)

        blur = ng.nodes.new("CompositorNodeBlur")
        blur.inputs["Type"].default_value = "Gaussian"
        blur.inputs["Size"].default_value = (260.0, 260.0)
        blur.inputs["Extend Bounds"].default_value = True

        vig_mix = ng.nodes.new("ShaderNodeMix")
        vig_mix.data_type = "RGBA"
        vig_mix.blend_type = "MULTIPLY"
        vig_mix.clamp_result = True
        vig_mix.inputs[0].default_value = vignette

        ng.links.new(mask.outputs["Mask"], blur.inputs["Image"])
        ng.links.new(lens.outputs["Image"], vig_mix.inputs[6])
        ng.links.new(blur.outputs["Image"], vig_mix.inputs[7])
        ng.links.new(vig_mix.outputs[2], out.inputs["Image"])
    else:
        ng.links.new(lens.outputs["Image"], out.inputs["Image"])

    return ng
