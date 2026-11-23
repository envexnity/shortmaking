"""
render_roblox_branding.py — Blender 5.3.0 Cycles OptiX render script for Pixelate Past's
Roblox 3D Storytime Comedy rebrand (PFP + 2560x1440 Banner Backdrop).

Run via:
  "C:\\Program Files\\Blender Foundation\\Blender 5.3\\blender.exe" --background --disable-autoexec --python channel-branding/render_roblox_branding.py
"""
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

SHORTMAKING_ROOT = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking")
BRANDING_DIR = SHORTMAKING_ROOT / "channel-branding"
CHARS_DIR = SHORTMAKING_ROOT / "assets" / "roblox-r6-characters" / "characters"

sys.path.insert(0, str(SHORTMAKING_ROOT / "90 Templates & Starter Kits" / "blender-cinema-kit"))
sys.path.insert(0, str(SHORTMAKING_ROOT / "assets" / "roblox-r6-characters" / "scripts"))
import blender_cinema_lib as bcl
from build_characters import apply_personality_pose


def place_rig(arm_obj, world_pos: Vector, yaw_deg: float, scale_xyz: float = 1.0):
    """Exact world-space placement & world-Z yaw using MasterControl's rest basis."""
    pb = arm_obj.pose.bones["MasterControl"]
    rest_3x3 = arm_obj.data.bones["MasterControl"].matrix_local.to_3x3()
    inv_3x3 = rest_3x3.inverted()

    pb.location = inv_3x3 @ world_pos
    pb.rotation_mode = "XYZ"
    world_rot = Matrix.Rotation(math.radians(yaw_deg), 3, "Z")
    local_rot = inv_3x3 @ world_rot @ rest_3x3
    pb.rotation_euler = local_rot.to_euler("XYZ")
    pb.scale = (scale_xyz, scale_xyz, scale_xyz)
    bpy.context.view_layer.update()


def append_character(blend_filename: str, instance_suffix: str = ""):
    """Append the main character collection from a .blend file and return (col, primary_armature)."""
    blend_path = CHARS_DIR / blend_filename
    cid = blend_path.stem
    before_cols = set(bpy.data.collections)
    before_objs = set(bpy.data.objects)

    with bpy.data.libraries.load(str(blend_path), link=False) as (data_from, data_to):
        if cid in data_from.collections:
            data_to.collections = [cid]
        else:
            candidates = [
                c for c in data_from.collections
                if not any(skip in c for skip in ("Extra_Swaps", "Rig_Widgets", "Widgets", "Hidden", "Collection"))
            ]
            data_to.collections = [candidates[0] if candidates else data_from.collections[0]]

    new_cols = [c for c in bpy.data.collections if c not in before_cols]
    new_objs = [o for o in bpy.data.objects if o not in before_objs]

    top_col = data_to.collections[0] if data_to.collections else (new_cols[0] if new_cols else None)
    if top_col is not None:
        if instance_suffix:
            top_col.name = f"{cid}_{instance_suffix}"
        if top_col.name not in bpy.context.scene.collection.children:
            bpy.context.scene.collection.children.link(top_col)

    arm = None
    for o in new_objs:
        if o.type == "ARMATURE" and o.name.startswith("__PrimaryArmature"):
            arm = o
            o.name = f"{cid}_{instance_suffix}_Rig"
        elif o.type == "ARMATURE" and o.name.startswith("InternalArmature"):
            o.name = f"{cid}_{instance_suffix}_Internal"

    if arm and arm.animation_data:
        arm.animation_data.action = None

    return top_col, arm


def make_emissive_mat(name: str, hex_col: str, strength: float = 4.0):
    mat = bpy.data.materials.new(name)
    if bpy.app.version < (5, 0, 0):
        mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = bcl.hex_to_linear(hex_col)
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    return mat


def add_tracked_area_light(name: str, loc, target_loc, energy: float, size: float, hex_col: str, spread_deg: float, col):
    light_data = bpy.data.lights.new(name, type="AREA")
    light_data.energy = energy
    light_data.size = size
    light_data.color = bcl.hex_to_linear(hex_col)[:3]
    light_data.spread = math.radians(spread_deg)
    light_obj = bpy.data.objects.new(name, light_data)
    light_obj.location = loc
    col.objects.link(light_obj)

    target = bpy.data.objects.new(f"{name}_Target", None)
    target.location = target_loc
    col.objects.link(target)

    c = light_obj.constraints.new("TRACK_TO")
    c.target = target
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"
    return light_obj


def add_camera(name: str, loc, target_loc, lens: float, fstop: float, col):
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = lens
    cam_data.clip_start = 0.1
    cam_data.clip_end = 500.0
    cam_data.dof.use_dof = True
    cam_data.dof.aperture_fstop = fstop

    cam_obj = bpy.data.objects.new(name, cam_data)
    cam_obj.location = loc
    col.objects.link(cam_obj)

    focus = bpy.data.objects.new(f"{name}_Focus", None)
    focus.location = target_loc
    col.objects.link(focus)
    cam_data.dof.focus_object = focus

    c = cam_obj.constraints.new("TRACK_TO")
    c.target = focus
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"

    bpy.context.scene.camera = cam_obj
    return cam_obj


def add_bokeh_orb(name, loc, radius, hex_col, strength, col):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=radius, location=loc)
    orb = bpy.context.active_object
    orb.name = name
    for c in list(orb.users_collection):
        c.objects.unlink(orb)
    col.objects.link(orb)
    orb.data.materials.append(make_emissive_mat(f"Mat_{name}", hex_col, strength=strength))
    return orb


def build_pfp():
    print("\n=== Building Roblox Storytime PFP (1024x1024) ===")
    bcl.clear_scene()
    scene = bpy.context.scene

    bcl.configure_cycles_optix(
        scene, res_x=1024, res_y=1024, fps=30, samples=72,
        adaptive_threshold=0.015, view_transform="AgX", look="AgX - Punchy",
        motion_blur=False,
    )
    bcl.setup_dark_studio_world(scene, hex_col="#09071A", strength=0.35)

    stage_col = bpy.data.collections.new("PFP_Stage")
    scene.collection.children.link(stage_col)

    # Backdrop curved gradient wall behind subjects (rich indigo-violet wash)
    bpy.ops.mesh.primitive_plane_add(size=40.0, location=(0.0, -7.0, 3.5))
    bg = bpy.context.active_object
    bg.name = "PFP_Backdrop"
    bg.rotation_euler = (math.radians(90), 0, 0)
    for c in list(bg.users_collection):
        c.objects.unlink(bg)
    stage_col.objects.link(bg)
    bg.data.materials.append(
        bcl.make_pbr_material("Mat_PFP_BG", "#1E1645", roughness_min=0.72, roughness_max=0.90, metallic=0.0)
    )

    # Glowing circular neon halo ring behind the duo (frames the PFP inside the circle!)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=3.10, minor_radius=0.085,
        major_segments=64, minor_segments=16,
        location=(0.0, -2.8, 3.35),
        rotation=(math.radians(90), 0, 0),
    )
    ring_outer = bpy.context.active_object
    ring_outer.name = "PFP_NeonRing_Cyan"
    for c in list(ring_outer.users_collection):
        c.objects.unlink(ring_outer)
    stage_col.objects.link(ring_outer)
    ring_outer.data.materials.append(make_emissive_mat("Mat_RingCyan", "#38BDF8", strength=5.0))

    bpy.ops.mesh.primitive_torus_add(
        major_radius=2.80, minor_radius=0.050,
        major_segments=64, minor_segments=16,
        location=(0.0, -2.75, 3.35),
        rotation=(math.radians(90), 0, 0),
    )
    ring_inner = bpy.context.active_object
    ring_inner.name = "PFP_NeonRing_Gold"
    for c in list(ring_inner.users_collection):
        c.objects.unlink(ring_inner)
    stage_col.objects.link(ring_inner)
    ring_inner.data.materials.append(make_emissive_mat("Mat_RingGold", "#FBBF24", strength=4.0))

    # Party bokeh orbs in background (evokes Bun Town neon night party)
    rng = random.Random(42)
    bokeh_palette = ["#38BDF8", "#F43F5E", "#FBBF24", "#A855F7", "#22C55E"]
    for i in range(20):
        bx = rng.uniform(-5.2, 5.2)
        bz = rng.uniform(0.6, 6.8)
        if math.hypot(bx, bz - 3.35) < 2.3:
            continue
        add_bokeh_orb(
            f"PFP_Bokeh_{i}",
            (bx, rng.uniform(-5.8, -3.5), bz),
            rng.uniform(0.10, 0.24),
            bokeh_palette[i % len(bokeh_palette)],
            rng.uniform(2.5, 4.8),
            stage_col,
        )

    # Append Protagonist (Alex) front & center-left, plus Noob peeking cleanly right-behind!
    _, alex_arm = append_character("01_Alex_Protagonist.blend", "PFP")
    apply_personality_pose(alex_arm, "hero_wave")
    pbs_a = alex_arm.pose.bones
    pbs_a["LowerTorso-FK"].rotation_euler = (math.radians(2), math.radians(0), math.radians(-10))
    pbs_a["Head"].rotation_euler = (math.radians(-4), math.radians(-4), math.radians(10))
    pbs_a["RightArm_FK"].rotation_euler = (math.radians(-42), math.radians(20), math.radians(-35))
    pbs_a["LeftArm_FK"].rotation_euler = (math.radians(18), math.radians(-12), math.radians(-20))
    place_rig(alex_arm, Vector((0.75, 0.35, 0.0)), yaw_deg=-15.0, scale_xyz=1.0)

    _, noob_arm = append_character("02_Noob_BestFriend.blend", "PFP")
    apply_personality_pose(noob_arm, "noob_excited")
    pbs_n = noob_arm.pose.bones
    pbs_n["Head"].rotation_euler = (math.radians(-6), math.radians(8), math.radians(-10))
    pbs_n["RightArm_FK"].rotation_euler = (math.radians(-115), math.radians(15), math.radians(-22))
    pbs_n["LeftArm_FK"].rotation_euler = (math.radians(-120), math.radians(-18), math.radians(20))
    place_rig(noob_arm, Vector((-1.05, -0.95, 0.25)), yaw_deg=16.0, scale_xyz=0.95)

    # Balanced Storytime Studio Lighting (Zero overexposure on white hoodie + vivid indigo wash)
    add_tracked_area_light("PFP_Key", (4.5, 6.2, 6.0), (0.0, 0.0, 3.3), energy=190.0, size=3.8, hex_col="#FFE7C4", spread_deg=70, col=stage_col)
    add_tracked_area_light("PFP_Fill", (-5.0, 4.8, 4.4), (0.0, 0.0, 3.3), energy=115.0, size=4.5, hex_col="#A5B4FC", spread_deg=90, col=stage_col)
    add_tracked_area_light("PFP_RimCyan", (-3.8, -2.5, 5.5), (0.0, 0.0, 3.5), energy=290.0, size=2.4, hex_col="#38BDF8", spread_deg=55, col=stage_col)
    add_tracked_area_light("PFP_RimGold", (3.8, -2.2, 5.2), (0.0, 0.0, 3.4), energy=220.0, size=2.2, hex_col="#F59E0B", spread_deg=55, col=stage_col)
    add_tracked_area_light("PFP_BgWash", (0.0, -3.5, 3.4), (0.0, -7.0, 3.4), energy=280.0, size=5.0, hex_col="#6366F1", spread_deg=95, col=stage_col)

    # Circle-crop-safe framing (56mm lens at y=9.2 keeps both characters centered inside circle crop)
    add_camera("PFP_Camera", (0.0, 9.2, 3.45), (-0.08, -0.1, 3.35), lens=56.0, fstop=3.2, col=stage_col)

    bcl.setup_cinema_compositor(
        scene,
        glare_type="Fog Glow",
        glare_threshold=1.15,
        glare_strength=0.30,
        glare_size=0.65,
        dispersion=0.004,
        distortion=-0.008,
        lift_rgb=(0.98, 0.98, 1.03),
        gamma_rgb=(1.01, 1.00, 1.02),
        gain_rgb=(1.04, 1.02, 0.99),
        vignette=0.22,
    )

    bpy.ops.wm.save_as_mainfile(filepath=str(BRANDING_DIR / "roblox_pfp_studio.blend"))
    scene.render.filepath = str(BRANDING_DIR / "pfp_3d.png")
    bpy.ops.render.render(write_still=True)
    print(f"Saved PFP render -> {BRANDING_DIR / 'pfp_3d.png'}")


def build_town_backdrop(stage_col):
    """Build stylized glowing midnight Roblox town buildings + studded street stage."""
    # Ground floor
    bpy.ops.mesh.primitive_plane_add(size=140.0, location=(0, 0, -0.24))
    floor = bpy.context.active_object
    floor.name = "Banner_Floor"
    for c in list(floor.users_collection):
        c.objects.unlink(floor)
    stage_col.objects.link(floor)
    floor.data.materials.append(
        bcl.make_pbr_material("Mat_BannerFloor", "#080A18", roughness_min=0.20, roughness_max=0.35, metallic=0.15, coat_weight=0.45)
    )

    # Studded Roblox stage platform
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -0.5, -0.12))
    deck = bpy.context.active_object
    deck.name = "Banner_StageDeck"
    deck.scale = (44.0, 9.0, 0.24)
    bpy.ops.object.transform_apply(scale=True)
    for c in list(deck.users_collection):
        c.objects.unlink(deck)
    stage_col.objects.link(deck)
    bcl.add_cinema_bevel(deck, width=0.05, segments=2)
    deck.data.materials.append(
        bcl.make_pbr_material("Mat_BannerDeck", "#151B30", roughness_min=0.25, roughness_max=0.38, metallic=0.12, coat_weight=0.35)
    )

    # Raised Roblox studs across the front edge of the street/stage
    stud_mat = bcl.make_pbr_material("Mat_BannerStud", "#232D4D", roughness_min=0.20, roughness_max=0.34, metallic=0.15, coat_weight=0.40)
    bpy.ops.mesh.primitive_cylinder_add(vertices=18, radius=0.26, depth=0.10, location=(0, 0, 0))
    proto = bpy.context.active_object
    stud_mesh = proto.data
    stud_mesh.materials.append(stud_mat)
    bpy.data.objects.remove(proto, do_unlink=True)
    for ix in range(-20, 21, 2):
        for iy in (3.2, -4.0):
            so = bpy.data.objects.new(f"BannerStud_{ix}_{iy:.0f}", stud_mesh)
            so.location = (float(ix), iy, 0.05)
            stage_col.objects.link(so)

    # Neon trim strips (cyan + gold) along the stage curb
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 3.98, -0.02))
    trim = bpy.context.active_object
    trim.name = "Banner_NeonTrim"
    trim.scale = (44.0, 0.14, 0.10)
    bpy.ops.object.transform_apply(scale=True)
    for c in list(trim.users_collection):
        c.objects.unlink(trim)
    stage_col.objects.link(trim)
    trim.data.materials.append(make_emissive_mat("Mat_TrimCyan", "#38BDF8", strength=4.0))

    # Stylized Roblox Town buildings in the distant background (flanks, keeping center dark for text)
    bldg_specs = [
        (-16.5, -13.0, 4.5, 3.5, 11.0, "#1D2442", "#FBBF24"),
        (-12.2, -14.5, 3.8, 3.2, 14.5, "#261B47", "#38BDF8"),
        (-8.5,  -16.0, 3.4, 3.0,  9.5, "#19263D", "#F43F5E"),
        ( 8.5,  -16.0, 3.4, 3.0, 10.0, "#19263D", "#38BDF8"),
        (12.2,  -14.5, 3.8, 3.2, 14.0, "#261B47", "#FBBF24"),
        (16.5,  -13.0, 4.5, 3.5, 11.5, "#1D2442", "#A855F7"),
    ]
    for idx, (bx, by, bw, bd, bh, body_hex, win_hex) in enumerate(bldg_specs):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bx, by, bh * 0.5 - 0.24))
        b = bpy.context.active_object
        b.name = f"TownBldg_{idx}"
        b.scale = (bw, bd, bh)
        bpy.ops.object.transform_apply(scale=True)
        for c in list(b.users_collection):
            c.objects.unlink(b)
        stage_col.objects.link(b)
        b.data.materials.append(bcl.make_pbr_material(f"Mat_Bldg_{idx}", body_hex, roughness_min=0.5, roughness_max=0.7))

        # Glowing cartoon windows
        win_mat = make_emissive_mat(f"Mat_Win_{idx}", win_hex, strength=3.2)
        for wz in (2.4, 4.6, 6.8):
            if wz > bh - 1.5:
                continue
            for wx_off in (-0.85, 0.85):
                bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bx + wx_off, by + bd * 0.5 + 0.04, wz))
                w = bpy.context.active_object
                w.name = f"Win_{idx}_{wz}_{wx_off}"
                w.scale = (0.75, 0.08, 0.95)
                bpy.ops.object.transform_apply(scale=True)
                for c in list(w.users_collection):
                    c.objects.unlink(w)
                stage_col.objects.link(w)
                w.data.materials.append(win_mat)

    # Festive glowing bokeh orbs / confetti across the night sky
    rng = random.Random(108)
    palette = ["#38BDF8", "#F43F5E", "#FBBF24", "#A855F7", "#34D399"]
    for i in range(44):
        ox = rng.uniform(-19.5, 19.5)
        oz = rng.uniform(1.2, 10.5)
        # Keep center safe zone dark & clean so typography pops
        if abs(ox) < 5.5 and oz < 5.8:
            continue
        add_bokeh_orb(
            f"Banner_Orb_{i}",
            (ox, rng.uniform(-11.0, -5.0), oz),
            rng.uniform(0.11, 0.30),
            palette[i % len(palette)],
            rng.uniform(2.8, 5.5),
            stage_col,
        )


def build_banner():
    print("\n=== Building Roblox Storytime Banner (2560x1440) ===")
    bcl.clear_scene()
    scene = bpy.context.scene

    bcl.configure_cycles_optix(
        scene, res_x=2560, res_y=1440, fps=30, samples=64,
        adaptive_threshold=0.018, view_transform="AgX", look="AgX - Punchy",
        motion_blur=False,
    )
    bcl.setup_dark_studio_world(scene, hex_col="#070514", strength=0.28)

    stage_col = bpy.data.collections.new("Banner_Stage")
    scene.collection.children.link(stage_col)
    build_town_backdrop(stage_col)

    # Flank the central 1546x423 text safe zone with expressive Roblox Storytime characters!
    # Camera is at +Y looking toward -Y -> +X is viewer LEFT, -X is viewer RIGHT.
    cast_slots = [
        # Left Flank (Party / Chaos Crew)
        ("04_Maya_BestFriend.blend",   "maya_cheer",    Vector((10.6, -0.8, 0.0)),  20.0),
        ("02_Noob_BestFriend.blend",   "noob_excited",  Vector(( 7.6,  0.1, 0.0)),  15.0),
        ("08_Chloe_Rival.blend",       "chloe_sass",    Vector(( 4.8, -1.4, 0.0)),  10.0),
        # Right Flank (Protagonist & Villains)
        ("06_Hacker_Glitch.blend",     "hacker_scheme", Vector((-4.8, -1.4, 0.0)), -10.0),
        ("01_Alex_Protagonist.blend",  "hero_wave",     Vector((-7.6,  0.1, 0.0)), -15.0),
        ("03_RichKid_Dominus.blend",   "rich_flex",     Vector((-10.6, -0.8, 0.0)), -20.0),
    ]

    for blend_file, pose_name, pos, yaw in cast_slots:
        _, arm = append_character(blend_file, "Banner")
        if arm:
            apply_personality_pose(arm, pose_name)
            place_rig(arm, pos, yaw_deg=yaw, scale_xyz=1.0)

    # Lights: Left party magenta/cyan key + Right golden hero key + inner Hacker rim + overhead fill
    add_tracked_area_light("Ban_Key_Left",  (11.5, 8.0, 8.5),  (7.5, 0.0, 2.5),  energy=640.0, size=5.0, hex_col="#FFE4BA", spread_deg=68, col=stage_col)
    add_tracked_area_light("Ban_Key_Right", (-11.5, 8.0, 8.5), (-7.5, 0.0, 2.5), energy=640.0, size=5.0, hex_col="#FFE4BA", spread_deg=68, col=stage_col)
    add_tracked_area_light("Ban_Hacker_Pop",(-4.8, 4.5, 5.2),  (-4.8, -1.4, 2.6), energy=320.0, size=2.4, hex_col="#A855F7", spread_deg=55, col=stage_col)
    add_tracked_area_light("Ban_Rim_Cyan",  (10.5, -4.5, 6.5), (7.5, 0.0, 2.8),  energy=520.0, size=4.0, hex_col="#38BDF8", spread_deg=60, col=stage_col)
    add_tracked_area_light("Ban_Rim_Pink",  (-10.5, -4.5, 6.5),(-7.5, 0.0, 2.8), energy=560.0, size=4.0, hex_col="#F43F5E", spread_deg=60, col=stage_col)
    add_tracked_area_light("Ban_Soft_Fill", (0.0, 12.0, 7.0),  (0.0, 0.0, 2.5),  energy=220.0, size=10.0, hex_col="#93C5FD", spread_deg=95, col=stage_col)

    # Wide 2560x1440 camera framing characters cleanly in the 423px vertical safe band
    add_camera("Banner_Camera", (0.0, 24.5, 2.85), (0.0, -0.5, 2.35), lens=36.0, fstop=5.6, col=stage_col)

    bcl.setup_cinema_compositor(
        scene,
        glare_type="Fog Glow",
        glare_threshold=1.18,
        glare_strength=0.28,
        glare_size=0.68,
        dispersion=0.004,
        distortion=-0.008,
        lift_rgb=(0.98, 0.98, 1.03),
        gamma_rgb=(1.0, 1.0, 1.01),
        gain_rgb=(1.03, 1.01, 0.99),
        vignette=0.25,
    )

    bpy.ops.wm.save_as_mainfile(filepath=str(BRANDING_DIR / "roblox_banner_studio.blend"))
    scene.render.filepath = str(BRANDING_DIR / "banner_3d.png")
    bpy.ops.render.render(write_still=True)
    print(f"Saved Banner 3D render -> {BRANDING_DIR / 'banner_3d.png'}")


if __name__ == "__main__":
    build_pfp()
    build_banner()
