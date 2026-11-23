"""
build_scene.py — Track 5 Roblox "In This World" Storytime Short (Blender 5.3.0 EEVEE, < 45s):
"In This World, Every Jump You Make Costs 100 Robux."

Builds 5 authentic Roblox R6 + Classic-Modern Stud sets inside Blender 5.3.0 (`BLENDER_EEVEE`, `AgX - Punchy`):
  - Set 0 (X=0):   Lava Obby Spawn Room (studded spawn pad, glowing lava kill-bricks, protagonist frozen on 1-stud block)
  - Set 1 (X=120): Roblox High Hallway (blue studded lockers, Rich Dominus Kids bunny-hopping, Noob & Hero walking flat-footed)
  - Set 2 (X=240): Classroom Floor Is Lava & Gravity Coil Launch (cracked lava floor, Teacher on green platform, Noob tossing blue Gravity Coil, Hero blasting through shattered roof!)
  - Set 3 (X=360): Sky Airtime Taxi-Meter Zone (vertical stud ruler tower, orbiting Roblox Tax Bot scanning airborne Hero with red laser)
  - Set 4 (X=480): Admin Gravity Ban & Free Float Twist (Roblox Admin slamming glowing Ban Hammer, Hero floating horizontally 1.2m off floor for free!)

All 12 camera cuts obey the Eye-Level Continuity Rule (y = 35-42%), 0 static holds, and lock directly to voice/words.json.
"""

import os
import sys
import json
import math
import random
import bpy
import bmesh
from mathutils import Vector, Euler

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
CINEMA_KIT = os.path.join(ROOT, "90 Templates & Starter Kits", "blender-cinema-kit")
sys.path.insert(0, CINEMA_KIT)

from blender_cinema_lib import (
    clear_scene,
    configure_eevee_cinema,
    setup_dark_studio_world,
    add_studio_3point_rig,
    make_pbr_material,
    add_cinema_bevel,
    add_animated_shot_camera,
    get_action_fcurves,
    hex_to_linear,
)

FPS = 30


def load_timing():
    words_p = os.path.join(BASE, "voice", "words.json")
    data = json.load(open(words_p, encoding="utf-8"))
    dur = float(data["duration"])
    secs = data["sections"]
    total_frames = int(round((dur + 0.45) * FPS))

    def sec_f(key, is_last=False):
        s = max(1, int(round(secs[key]["start"] * FPS)) + 1)
        e = total_frames if is_last else max(s + 20, int(round(secs[key]["end"] * FPS)))
        return s, e

    b1_0, b1_1 = sec_f("beat1")
    b2_0, b2_1 = sec_f("beat2")
    b3_0, b3_1 = sec_f("beat3")
    b4_0, b4_1 = sec_f("beat4")
    b5_0, b5_1 = sec_f("beat5")
    b6_0, b6_1 = sec_f("beat6", is_last=True)

    b2_0 = b1_1 + 1
    b3_0 = b2_1 + 1
    b4_0 = b3_1 + 1
    b5_0 = b4_1 + 1
    b6_0 = b5_1 + 1
    return total_frames, {
        "beat1": (1, b1_1),
        "beat2": (b2_0, b2_1),
        "beat3": (b3_0, b3_1),
        "beat4": (b4_0, b4_1),
        "beat5": (b5_0, b5_1),
        "beat6": (b6_0, b6_1),
    }


def make_emissive_mat(name: str, hex_col: str, strength: float = 4.5):
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


def make_roblox_plastic_mat(name: str, hex_col: str, rough_min=0.18, rough_max=0.34, metallic=0.0):
    """Glossy Roblox Studio SurfaceAppearance / SmoothPlastic with subtle Coat Weight & micro-roughness breakup."""
    return make_pbr_material(
        name=name,
        base_hex=hex_col,
        roughness_min=rough_min,
        roughness_max=rough_max,
        metallic=metallic,
        diffuse_roughness=0.25,
        bump_strength=0.03,
        noise_scale=12.0,
        weathering=0.12,
        use_ao_node=False,
        coat_weight=0.38,
        coat_roughness=0.12,
    )


def make_studded_brick(
    name: str,
    loc,
    size_xyz,
    mat,
    stud_spacing: float = 0.85,
    add_studs: bool = True,
):
    """Creates a beveled Roblox part with raised cylindrical top studs in a single joined mesh."""
    sx, sy, sz = size_xyz
    bm = bmesh.new()

    # Main brick box
    res_box = bmesh.ops.create_cube(bm, size=1.0)
    for v in res_box["verts"]:
        v.co.x *= sx
        v.co.y *= sy
        v.co.z *= sz

    if add_studs:
        nx = max(1, min(14, int(round(sx / stud_spacing))))
        ny = max(1, min(14, int(round(sy / stud_spacing))))
        start_x = -0.5 * (nx - 1) * stud_spacing
        start_y = -0.5 * (ny - 1) * stud_spacing
        top_z = sz * 0.5
        stud_h = 0.11
        stud_r = min(0.24, stud_spacing * 0.28)
        for ix in range(nx):
            for iy in range(ny):
                cx = start_x + ix * stud_spacing
                cy = start_y + iy * stud_spacing
                res_c = bmesh.ops.create_cone(
                    bm,
                    cap_ends=True,
                    cap_tris=False,
                    segments=10,
                    radius1=stud_r,
                    radius2=stud_r * 0.94,
                    depth=stud_h,
                )
                for v in res_c["verts"]:
                    v.co.x += cx
                    v.co.y += cy
                    v.co.z += top_z + stud_h * 0.5

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.data.materials.append(mat)
    bpy.context.scene.collection.objects.link(obj)
    add_cinema_bevel(obj, width=0.014, segments=2, smooth=True, weighted_normal=True)
    return obj


def make_roblox_r6_avatar(
    name: str,
    loc,
    rot_z_deg: float,
    mats: dict,
    torso_mat,
    legs_mat,
    arms_mat,
    head_mat,
    role: str = "hero",
    scale: float = 1.0,
):
    """
    Builds an articulated blocky Roblox R6 character rig:
      - Root Empty at feet (z = 0)
      - LeftLeg / RightLeg pivots at hip (z = 1.05m)
      - Torso block (z = 1.05..2.10m) with top collar stud
      - LeftArm / RightArm pivots at shoulder (z = 1.95m)
      - Head pivot at neck (z = 2.15m) with classic cylindrical beveled Roblox head + 3D eyes/brows/mouth + role hat/prop!
    Returns dict of rig parts for animation.
    """
    col = bpy.context.scene.collection
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.rotation_euler = (0.0, 0.0, math.radians(rot_z_deg))
    root.scale = (scale, scale, scale)
    col.objects.link(root)

    # Legs (pivots at hip z = 1.05)
    legs = {}
    for side, lx in [("L", -0.27), ("R", 0.27)]:
        lpiv = bpy.data.objects.new(f"{name}_Leg_{side}", None)
        lpiv.location = (lx, 0.0, 1.05)
        lpiv.parent = root
        col.objects.link(lpiv)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, -0.52))
        lmesh = bpy.context.active_object
        lmesh.name = f"{name}_LegMesh_{side}"
        lmesh.scale = (0.50, 0.52, 1.04)
        lmesh.data.materials.append(legs_mat)
        lmesh.parent = lpiv
        add_cinema_bevel(lmesh, width=0.018, segments=2)
        legs[side] = lpiv

    # Torso (center z = 1.58)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 1.58))
    torso = bpy.data.objects.new(f"{name}_TorsoPivot", None)
    torso.location = (0.0, 0.0, 1.05)
    torso.parent = root
    col.objects.link(torso)

    t_box = bpy.context.active_object
    t_box.name = f"{name}_TorsoBox"
    t_box.location = (0.0, 0.0, 0.53)
    t_box.scale = (1.04, 0.54, 1.05)
    t_box.data.materials.append(torso_mat)
    t_box.parent = torso
    add_cinema_bevel(t_box, width=0.022, segments=2)

    # Arms (pivots at shoulder z = 0.92 relative to torso pivot)
    arms = {}
    for side, ax in [("L", -0.78), ("R", 0.78)]:
        apiv = bpy.data.objects.new(f"{name}_Arm_{side}", None)
        apiv.location = (ax, 0.0, 0.92)
        apiv.parent = torso
        col.objects.link(apiv)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, -0.42))
        amesh = bpy.context.active_object
        amesh.name = f"{name}_ArmMesh_{side}"
        amesh.scale = (0.48, 0.50, 1.02)
        amesh.data.materials.append(arms_mat)
        amesh.parent = apiv
        add_cinema_bevel(amesh, width=0.018, segments=2)
        arms[side] = apiv

    # Head (pivot at neck z = 1.08 relative to torso pivot)
    hpiv = bpy.data.objects.new(f"{name}_Head", None)
    hpiv.location = (0.0, 0.0, 1.08)
    hpiv.parent = torso
    col.objects.link(hpiv)

    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.36, depth=0.66, location=(0.0, 0.0, 0.35))
    hmesh = bpy.context.active_object
    hmesh.name = f"{name}_HeadCyl"
    hmesh.data.materials.append(head_mat)
    hmesh.parent = hpiv
    add_cinema_bevel(hmesh, width=0.055, segments=3)

    # Top head stud
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.16, depth=0.08, location=(0.0, 0.0, 0.71))
    hstud = bpy.context.active_object
    hstud.data.materials.append(head_mat)
    hstud.parent = hpiv

    # Classic Roblox Face (facing -Y)
    for ex in (-0.13, 0.13):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ex, -0.35, 0.40))
        eye = bpy.context.active_object
        eye.scale = (0.065, 0.03, 0.11)
        eye.data.materials.append(mats["face_ink"])
        eye.parent = hpiv

        # Expressive brow
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ex, -0.36, 0.50))
        brow = bpy.context.active_object
        brow.scale = (0.10, 0.03, 0.032)
        brow_tilt = math.radians(14 if role in ("hero", "teacher") else (-16 if role in ("dominus", "admin") else 0))
        brow.rotation_euler = (0.0, brow_tilt * (1 if ex > 0 else -1), 0.0)
        brow.data.materials.append(mats["face_ink"])
        brow.parent = hpiv

    # Mouth (open O-mouth for shock on hero/teacher, grin on noob/dominus)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -0.355, 0.23))
    mouth = bpy.context.active_object
    if role in ("hero", "teacher"):
        mouth.scale = (0.15, 0.03, 0.10)
    else:
        mouth.scale = (0.22, 0.03, 0.045)
    mouth.data.materials.append(mats["face_ink"])
    mouth.parent = hpiv

    # Role Accessories
    if role == "hero":
        # Classic spiky dark brown hair cap + glowing Robux badge on hoodie chest
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.03, 0.68))
        hair = bpy.context.active_object
        hair.scale = (0.76, 0.78, 0.22)
        hair.data.materials.append(mats["hair_brown"])
        hair.parent = hpiv
        add_cinema_bevel(hair, width=0.03, segments=2)

    elif role == "noob":
        # Glowing Blue Gravity Coil in right hand!
        coil = bpy.data.objects.new(f"{name}_GravityCoil", None)
        coil.location = (0.0, -0.25, -0.75)
        coil.parent = arms["R"]
        col.objects.link(coil)
        for c_i in range(4):
            bpy.ops.mesh.primitive_torus_add(
                major_radius=0.22, minor_radius=0.055, major_segments=14, minor_segments=6, location=(0.0, -c_i * 0.11, 0.0)
            )
            ring = bpy.context.active_object
            ring.rotation_euler = (math.radians(80), 0.0, 0.0)
            ring.data.materials.append(mats["neon_cyan"])
            ring.parent = coil

    elif role == "dominus":
        # Golden Dominus Crown Hood + Winged Horns
        bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.48, radius2=0.36, depth=0.78, location=(0.0, 0.0, 0.42))
        hood = bpy.context.active_object
        hood.data.materials.append(mats["gold"])
        hood.parent = hpiv
        for sx in (-1, 1):
            bpy.ops.mesh.primitive_cone_add(
                vertices=6, radius1=0.14, radius2=0.03, depth=0.65, location=(sx * 0.48, 0.0, 0.68)
            )
            horn = bpy.context.active_object
            horn.rotation_euler = (0.0, sx * math.radians(38), 0.0)
            horn.data.materials.append(mats["neon_gold"])
            horn.parent = hpiv

    elif role == "admin":
        # Glowing Crimson-Gold Admin Crown & Giant Ban Hammer in Right Hand!
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.42, depth=0.32, location=(0.0, 0.0, 0.78))
        crown = bpy.context.active_object
        crown.data.materials.append(mats["neon_gold"])
        crown.parent = hpiv

        hammer = bpy.data.objects.new(f"{name}_BanHammer", None)
        hammer.location = (0.0, -0.2, -0.82)
        hammer.parent = arms["R"]
        col.objects.link(hammer)

        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8, radius=0.07, depth=1.85, location=(0.0, -0.55, 0.0), rotation=(math.radians(90), 0, 0)
        )
        shaft = bpy.context.active_object
        shaft.data.materials.append(mats["dark_metal"])
        shaft.parent = hammer

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -1.35, 0.0))
        hhead = bpy.context.active_object
        hhead.scale = (0.78, 0.48, 0.48)
        hhead.data.materials.append(mats["neon_red"])
        hhead.parent = hammer
        add_cinema_bevel(hhead, width=0.025, segments=2)

    return {"root": root, "torso": torso, "head": hpiv, "arms": arms, "legs": legs, "mouth": mouth}


def animate_avatar_idle_and_talk(rig: dict, start_f: int, end_f: int, panic: bool = False, walk_speed: float = 0.0, hop_amp: float = 0.0):
    """Animates snappy Roblox R6 limb swings, head turns, and panic/hopping motion (zero frozen holds)."""
    root = rig["root"]
    base_loc = Vector(root.location)
    for f in range(start_f, end_f + 1, 2):
        t = (f - start_f) / 30.0
        # Walk or hop translation
        dx = walk_speed * t
        dz = abs(math.sin(t * 7.5)) * hop_amp if hop_amp > 0.0 else abs(math.sin(t * 6.0)) * (0.06 if walk_speed != 0 else 0.02)
        root.location = (base_loc.x + dx, base_loc.y, base_loc.z + dz)
        root.keyframe_insert(data_path="location", frame=f)

        # Arm & leg swing
        amp_arm = 0.75 if panic else (0.55 if (walk_speed != 0 or hop_amp > 0) else 0.14)
        freq = 11.0 if panic else 6.5
        s = math.sin(t * freq)
        if panic:
            rig["arms"]["L"].rotation_euler = (math.radians(-135 + 22 * s), 0.0, math.radians(-12))
            rig["arms"]["R"].rotation_euler = (math.radians(-135 - 22 * s), 0.0, math.radians(12))
        else:
            rig["arms"]["L"].rotation_euler = (amp_arm * s, 0.0, 0.0)
            rig["arms"]["R"].rotation_euler = (-amp_arm * s, 0.0, 0.0)
        rig["arms"]["L"].keyframe_insert(data_path="rotation_euler", frame=f)
        rig["arms"]["R"].keyframe_insert(data_path="rotation_euler", frame=f)

        amp_leg = 0.50 if (walk_speed != 0 or hop_amp > 0) else (0.18 if panic else 0.03)
        rig["legs"]["L"].rotation_euler = (-amp_leg * s, 0.0, 0.0)
        rig["legs"]["R"].rotation_euler = (amp_leg * s, 0.0, 0.0)
        rig["legs"]["L"].keyframe_insert(data_path="rotation_euler", frame=f)
        rig["legs"]["R"].keyframe_insert(data_path="rotation_euler", frame=f)

        # Head look / nod
        rig["head"].rotation_euler = (0.08 * math.sin(t * 4.2), 0.0, 0.16 * math.cos(t * 3.5))
        rig["head"].keyframe_insert(data_path="rotation_euler", frame=f)


def build_set0_lava_obby(mats, b1_0, b1_1):
    """Set 0 (X=0): Roblox Lava Obby Spawn Room — Hero stranded on 1-stud safe island surrounded by glowing lava kill-bricks."""
    ox, oy, oz = 0.0, 0.0, 0.0
    add_studio_3point_rig(target_loc=(ox, oy, 1.5), radius=5.5, key_energy=1100.0, rim_energy=1600.0, fill_energy=240.0)

    # Dark studded obby arena floor & walls
    make_studded_brick("S0_Floor", (ox, oy, -0.55), (16.0, 16.0, 0.5), mats["dark_slate"], stud_spacing=1.0)
    make_studded_brick("S0_BackWall", (ox, oy + 7.5, 3.5), (16.0, 0.6, 8.0), mats["navy_wall"], add_studs=False)

    # Glowing neon red/orange Lava Kill-Bricks checkerboard around the center safe pad
    for ix in range(-3, 4):
        for iy in range(-2, 4):
            if ix == 0 and iy == 0:
                continue
            lx = ox + ix * 2.0
            ly = oy + iy * 2.0
            mat_l = mats["neon_red"] if (ix + iy) % 2 == 0 else mats["neon_orange"]
            make_studded_brick(f"S0_Lava_{ix}_{iy}", (lx, ly, -0.18), (1.78, 1.78, 0.28), mat_l, stud_spacing=0.88)

    # Center Safe Spawn Pad (2x2 studs) under Hero
    make_studded_brick("S0_SafePad", (ox, oy, -0.05), (1.75, 1.75, 0.52), mats["stud_grey"], stud_spacing=0.85)

    # Distant Obby Goal Checkpoints behind Hero
    for idx, (gx, gy, gz) in enumerate([(-2.8, 3.8, 1.1), (0.0, 4.8, 1.8), (2.8, 3.8, 1.1)]):
        make_studded_brick(f"S0_GoalPad_{idx}", (ox + gx, oy + gy, gz), (2.2, 2.2, 0.45), mats["stud_green"], stud_spacing=0.85)

    # Hero R6 Avatar panicking on the tiny safe block!
    hero = make_roblox_r6_avatar(
        "S0_Hero", (ox, oy, 0.22), 0.0, mats,
        torso_mat=mats["hero_blue"], legs_mat=mats["dark_slate"], arms_mat=mats["skin_yellow"], head_mat=mats["skin_yellow"], role="hero"
    )
    animate_avatar_idle_and_talk(hero, b1_0, b1_1, panic=True)


def build_set1_school_hallway(mats, b2_0, b2_1):
    """Set 1 (X=120): Roblox High Hallway — Rich Dominus Kids bunny-hopping while Hero & Noob shuffle flat-footed."""
    ox, oy, oz = 120.0, 0.0, 0.0
    add_studio_3point_rig(target_loc=(ox, oy, 1.6), radius=6.2, key_energy=1200.0, rim_energy=1500.0, fill_energy=280.0)

    make_studded_brick("S1_HallFloor", (ox, oy, -0.25), (18.0, 12.0, 0.5), mats["stud_grey"], stud_spacing=1.0)
    make_studded_brick("S1_HallWall", (ox, oy + 4.2, 3.2), (18.0, 0.6, 7.0), mats["navy_wall"], add_studs=False)

    # Row of blue & gold Roblox High school lockers along the back wall
    for i, lx in enumerate(range(-7, 8, 2)):
        lmat = mats["hero_blue"] if i % 2 == 0 else mats["gold"]
        make_studded_brick(f"S1_Locker_{i}", (ox + lx, oy + 3.4, 1.75), (1.55, 0.85, 3.4), lmat, add_studs=False)

    # Hero & Noob walking slowly with 0 jump height on the left/foreground
    hero = make_roblox_r6_avatar(
        "S1_Hero", (ox - 2.6, oy - 0.8, 0.0), -25.0, mats,
        torso_mat=mats["hero_blue"], legs_mat=mats["dark_slate"], arms_mat=mats["skin_yellow"], head_mat=mats["skin_yellow"], role="hero"
    )
    animate_avatar_idle_and_talk(hero, b2_0, b2_1, panic=False, walk_speed=0.55, hop_amp=0.0)

    noob = make_roblox_r6_avatar(
        "S1_Noob", (ox - 4.2, oy + 0.3, 0.0), -20.0, mats,
        torso_mat=mats["noob_blue"], legs_mat=mats["noob_green"], arms_mat=mats["skin_yellow"], head_mat=mats["skin_yellow"], role="noob"
    )
    animate_avatar_idle_and_talk(noob, b2_0, b2_1, panic=False, walk_speed=0.52, hop_amp=0.0)

    # Two Rich Dominus Kids bunny-hopping 1.45m high down the hallway!
    dom1 = make_roblox_r6_avatar(
        "S1_Dominus1", (ox + 0.4, oy + 0.6, 0.0), 18.0, mats,
        torso_mat=mats["gold"], legs_mat=mats["dark_metal"], arms_mat=mats["gold"], head_mat=mats["dark_metal"], role="dominus"
    )
    animate_avatar_idle_and_talk(dom1, b2_0, b2_1, panic=False, walk_speed=0.75, hop_amp=1.35)

    dom2 = make_roblox_r6_avatar(
        "S1_Dominus2", (ox + 2.4, oy + 1.4, 0.0), -15.0, mats,
        torso_mat=mats["dark_metal"], legs_mat=mats["gold"], arms_mat=mats["gold"], head_mat=mats["dark_metal"], role="dominus"
    )
    animate_avatar_idle_and_talk(dom2, b2_0, b2_1, panic=False, walk_speed=-0.45, hop_amp=1.20)


def build_set2_classroom_coil(mats, b3_0, b4_1):
    """Set 2 (X=240): Classroom Floor Is Lava + Noob Tossing Gravity Coil + Hero Launching Through Roof!"""
    ox, oy, oz = 240.0, 0.0, 0.0
    add_studio_3point_rig(target_loc=(ox, oy, 2.0), radius=6.8, key_energy=1250.0, rim_energy=1700.0, fill_energy=260.0)

    # Cracked glowing lava classroom floor
    make_studded_brick("S2_LavaBase", (ox, oy, -0.35), (16.0, 14.0, 0.4), mats["neon_red"], stud_spacing=1.0)
    for ix in range(-2, 3):
        for iy in range(-1, 3):
            make_studded_brick(
                f"S2_CrackTile_{ix}_{iy}",
                (ox + ix * 2.4, oy + iy * 2.2, -0.10),
                (1.85, 1.75, 0.32),
                mats["neon_orange"] if (ix + iy) % 2 == 0 else mats["dark_slate"],
                stud_spacing=0.85,
            )

    # High Safe Green Spawn Platform on right (ox + 3.2, oy + 1.8, z = 1.65) with Teacher waving
    make_studded_brick("S2_SafeDeskPlatform", (ox + 3.0, oy + 1.8, 0.85), (3.4, 3.0, 1.7), mats["stud_green"], stud_spacing=0.85)
    teacher = make_roblox_r6_avatar(
        "S2_Teacher", (ox + 3.0, oy + 1.8, 1.70), 22.0, mats,
        torso_mat=mats["hair_brown"], legs_mat=mats["dark_slate"], arms_mat=mats["skin_yellow"], head_mat=mats["skin_yellow"], role="teacher"
    )
    animate_avatar_idle_and_talk(teacher, b3_0, b4_1, panic=True)

    # Left Safe Desk Block with Hero & Noob Best Friend holding the glowing blue Gravity Coil
    make_studded_brick("S2_HeroDesk", (ox - 1.2, oy - 0.4, 0.35), (3.8, 2.4, 0.7), mats["stud_grey"], stud_spacing=0.85)

    noob = make_roblox_r6_avatar(
        "S2_NoobFriend", (ox - 2.2, oy - 0.3, 0.70), -28.0, mats,
        torso_mat=mats["noob_blue"], legs_mat=mats["noob_green"], arms_mat=mats["skin_yellow"], head_mat=mats["skin_yellow"], role="noob"
    )
    animate_avatar_idle_and_talk(noob, b3_0, b4_1, panic=False)

    hero = make_roblox_r6_avatar(
        "S2_HeroCoil", (ox - 0.4, oy - 0.3, 0.70), 10.0, mats,
        torso_mat=mats["hero_blue"], legs_mat=mats["dark_slate"], arms_mat=mats["skin_yellow"], head_mat=mats["skin_yellow"], role="hero"
    )

    # Shattered Roof Beams at z = 5.4 above Hero
    for rx in (-3.2, 2.8):
        make_studded_brick(f"S2_RoofBeam_{rx}", (ox + rx, oy, 5.4), (3.8, 4.5, 0.55), mats["dark_slate"], stud_spacing=0.9)

    # Hero launches straight UP through the roof on Beat 4 second half ("Unluckily, it launched me straight through the roof")!
    mid_b4 = b3_0 + int((b4_1 - b3_0) * 0.68)
    for f in range(b3_0, b4_1 + 1):
        if f < mid_b4:
            z_h = 0.70 + 0.04 * abs(math.sin(f * 0.3))
            rot_y = 0.0
        else:
            u = (f - mid_b4) / max(1, b4_1 - mid_b4)
            z_h = 0.70 + 8.2 * (u ** 1.5)
            rot_y = u * math.radians(25)
        hero["root"].location = (ox - 0.4, oy - 0.3, z_h)
        hero["root"].rotation_euler = (0.0, rot_y, math.radians(10))
        hero["root"].keyframe_insert(data_path="location", frame=f)
        hero["root"].keyframe_insert(data_path="rotation_euler", frame=f)
        hero["arms"]["L"].rotation_euler = (math.radians(-150), 0, 0)
        hero["arms"]["R"].rotation_euler = (math.radians(-150), 0, 0)
        hero["arms"]["L"].keyframe_insert(data_path="rotation_euler", frame=f)
        hero["arms"]["R"].keyframe_insert(data_path="rotation_euler", frame=f)


def build_set3_sky_taxbot(mats, b5_0, b5_1):
    """Set 3 (X=360): Sky Airtime Taxi-Meter Zone — Vertical Stud Ruler Tower & Orbiting Roblox Tax Bot Drone."""
    ox, oy, oz = 360.0, 0.0, 0.0
    add_studio_3point_rig(target_loc=(ox, oy, 3.5), radius=6.5, key_energy=1250.0, rim_energy=1800.0, fill_energy=260.0)

    # Vertical Neon Stud Ruler Pillar on right (ox + 2.3, oy + 1.2) showing every stud of airtime!
    make_studded_brick("S3_RulerTower", (ox + 2.3, oy + 1.2, 4.0), (0.95, 0.95, 12.0), mats["dark_slate"], add_studs=False)
    for tick_i in range(10):
        tz = -1.0 + tick_i * 1.1
        tmat = mats["neon_red"] if tick_i % 2 == 0 else mats["neon_gold"]
        make_studded_brick(f"S3_RulerTick_{tick_i}", (ox + 1.65, oy + 1.2, tz), (0.65, 0.35, 0.22), tmat, add_studs=False)

    # Airborne Hero soaring upward while flailing arms
    hero = make_roblox_r6_avatar(
        "S3_AirHero", (ox - 0.5, oy, 1.5), 8.0, mats,
        torso_mat=mats["hero_blue"], legs_mat=mats["dark_slate"], arms_mat=mats["skin_yellow"], head_mat=mats["skin_yellow"], role="hero"
    )

    # Roblox Tax Bot Drone (golden/black hovering scanner drone + red scanner beam)
    bot = bpy.data.objects.new("S3_TaxBot", None)
    bpy.context.scene.collection.objects.link(bot)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.58, location=(0, 0, 0))
    bcore = bpy.context.active_object
    bcore.data.materials.append(mats["dark_metal"])
    bcore.parent = bot

    bpy.ops.mesh.primitive_torus_add(major_radius=0.78, minor_radius=0.10, major_segments=16, minor_segments=6, location=(0, 0, 0))
    bring = bpy.context.active_object
    bring.data.materials.append(mats["neon_gold"])
    bring.parent = bot

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=12, radius=0.24, depth=0.35, location=(-0.48, -0.2, 0.0), rotation=(0, math.radians(90), 0)
    )
    beye = bpy.context.active_object
    beye.data.materials.append(mats["neon_red"])
    beye.parent = bot

    # Red laser scanner beam from Tax Bot to Hero
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.06, depth=1.9, location=(-1.25, -0.1, 0.0), rotation=(0, math.radians(90), 0)
    )
    beam = bpy.context.active_object
    beam.data.materials.append(mats["neon_red"])
    beam.parent = bot

    for f in range(b5_0, b5_1 + 1):
        u = (f - b5_0) / max(1, b5_1 - b5_0)
        hz = 1.2 + 3.2 * u
        hero["root"].location = (ox - 0.55, oy, hz)
        hero["root"].rotation_euler = (0.12 * math.sin(f * 0.25), 0.08 * math.cos(f * 0.2), math.radians(12))
        hero["root"].keyframe_insert(data_path="location", frame=f)
        hero["root"].keyframe_insert(data_path="rotation_euler", frame=f)

        s = math.sin(f * 0.45)
        hero["arms"]["L"].rotation_euler = (math.radians(-135 + 28 * s), 0, math.radians(-18))
        hero["arms"]["R"].rotation_euler = (math.radians(-135 - 28 * s), 0, math.radians(18))
        hero["arms"]["L"].keyframe_insert(data_path="rotation_euler", frame=f)
        hero["arms"]["R"].keyframe_insert(data_path="rotation_euler", frame=f)

        bot.location = (ox + 1.25, oy - 0.35 + 0.3 * math.sin(f * 0.15), hz + 1.35)
        bot.keyframe_insert(data_path="location", frame=f)


def build_set4_admin_float(mats, b6_0, b6_1):
    """Set 4 (X=480): Admin Gravity Ban Hammer & Zero-G Free Float To Class!"""
    ox, oy, oz = 480.0, 0.0, 0.0
    add_studio_3point_rig(target_loc=(ox, oy, 1.6), radius=6.2, key_energy=1300.0, rim_energy=1750.0, fill_energy=280.0)

    make_studded_brick("S4_Floor", (ox, oy, -0.25), (18.0, 12.0, 0.5), mats["stud_grey"], stud_spacing=1.0)
    make_studded_brick("S4_Wall", (ox, oy + 4.2, 3.2), (18.0, 0.6, 7.0), mats["navy_wall"], add_studs=False)

    # Glowing Admin Anvil Console Pedestal
    make_studded_brick("S4_AdminAnvil", (ox - 1.2, oy + 0.4, 0.55), (1.5, 1.2, 1.1), mats["neon_gold"], stud_spacing=0.75)

    admin = make_roblox_r6_avatar(
        "S4_Admin", (ox - 1.2, oy + 1.45, 0.0), 0.0, mats,
        torso_mat=mats["dark_metal"], legs_mat=mats["dark_slate"], arms_mat=mats["gold"], head_mat=mats["skin_yellow"], role="admin"
    )

    # Stunned Dominus Kid watching on the right
    dom = make_roblox_r6_avatar(
        "S4_StunnedDominus", (ox + 2.6, oy + 1.2, 0.0), 28.0, mats,
        torso_mat=mats["gold"], legs_mat=mats["dark_metal"], arms_mat=mats["gold"], head_mat=mats["dark_metal"], role="dominus"
    )
    animate_avatar_idle_and_talk(dom, b6_0, b6_1, panic=True)

    # Hero floating weightlessly 1.35m above the studded floor with zero gravity!
    hero = make_roblox_r6_avatar(
        "S4_FloatHero", (ox - 2.2, oy - 0.4, 1.45), -90.0, mats,
        torso_mat=mats["hero_blue"], legs_mat=mats["dark_slate"], arms_mat=mats["skin_yellow"], head_mat=mats["skin_yellow"], role="hero"
    )
    # Glowing cyan zero-gravity hover rings around Hero's boots
    for side in ("L", "R"):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.38, minor_radius=0.055, major_segments=14, minor_segments=6, location=(0, 0, -0.95))
        hring = bpy.context.active_object
        hring.data.materials.append(mats["neon_cyan"])
        hring.parent = hero["legs"][side]

    for f in range(b6_0, b6_1 + 1):
        u = (f - b6_0) / max(1, b6_1 - b6_0)
        # Admin slams Ban Hammer down in first 25 frames!
        slam_u = min(1.0, (f - b6_0) / 16.0)
        admin["arms"]["R"].rotation_euler = (math.radians(-130 + 115 * slam_u), 0, 0)
        admin["arms"]["R"].keyframe_insert(data_path="rotation_euler", frame=f)

        # Hero floats smoothly left -> right 1.15m off the ground facing camera (-Y) in a chill zero-G hover!
        hx = ox - 0.4 + 2.2 * u
        hz = 1.05 + 0.18 * math.sin(f * 0.20)
        hero["root"].location = (hx, oy - 0.25, hz)
        hero["root"].rotation_euler = (0.0, math.radians(10 * math.sin(f * 0.14)), math.radians(-12 + 24 * u))
        hero["root"].keyframe_insert(data_path="location", frame=f)
        hero["root"].keyframe_insert(data_path="rotation_euler", frame=f)
        hero["arms"]["L"].rotation_euler = (math.radians(-35), 0.0, math.radians(-48))
        hero["arms"]["R"].rotation_euler = (math.radians(-35), 0.0, math.radians(48))
        hero["arms"]["L"].keyframe_insert(data_path="rotation_euler", frame=f)
        hero["arms"]["R"].keyframe_insert(data_path="rotation_euler", frame=f)


def setup_12_storytime_cameras(scene, spans):
    """
    12 high-retention Roblox Storytime cameras (~2.8-3.4s average cadence, Eye-Level Continuity y=35-42%,
    Dutch tilts, 7-frame impact KICKS, and zero static holds).
    """
    scene.timeline_markers.clear()

    b1_0, b1_1 = spans["beat1"]
    b2_0, b2_1 = spans["beat2"]
    b3_0, b3_1 = spans["beat3"]
    b4_0, b4_1 = spans["beat4"]
    b5_0, b5_1 = spans["beat5"]
    b6_0, b6_1 = spans["beat6"]

    # Sub-split beats so visual cuts happen every ~2.5-3.4 seconds
    b1_a = b1_0 + int((b1_1 - b1_0) * 0.32)
    b1_b = b1_0 + int((b1_1 - b1_0) * 0.62)
    b2_a = b2_0 + int((b2_1 - b2_0) * 0.54)
    b3_a = b3_0 + int((b3_1 - b3_0) * 0.55)
    b4_a = b4_0 + int((b4_1 - b4_0) * 0.46)
    b5_a = b5_0 + int((b5_1 - b5_0) * 0.50)
    b6_a = b6_0 + int((b6_1 - b6_0) * 0.45)

    shots = [
        # Beat 1: Hook (Set 0 Lava Obby, X=0; Hero root.z=0.22 -> face z=2.65)
        {"name": "00_Hook_WideObby", "start": b1_0, "end": b1_a, "lens": 28.0,
         "pos_start": (0.0, -6.2, 3.10), "pos_end": (0.0, -5.2, 2.85),
         "tgt_start": (0.0, 0.0, 1.85), "tgt_end": (0.0, 0.0, 1.95), "roll": 0.0, "orbit": 6.0},
        {"name": "01_Hook_ExceptMe_CU", "start": b1_a + 1, "end": b1_b, "lens": 38.0,
         "pos_start": (0.45, -3.55, 2.68), "pos_end": (-0.25, -3.05, 2.72),
         "tgt_start": (0.0, 0.0, 2.48), "tgt_end": (0.0, 0.0, 2.54), "roll": 4.5, "orbit": 0.0},
        {"name": "02_Hook_ZeroRobux_Dutch", "start": b1_b + 1, "end": b1_1, "lens": 28.0,
         "pos_start": (-2.8, -5.0, 3.35), "pos_end": (2.4, -4.5, 2.85),
         "tgt_start": (0.0, 0.1, 1.75), "tgt_end": (0.0, 0.2, 1.85), "roll": -7.0, "orbit": 0.0,
         "kick_frame": b1_b + 18},

        # Beat 2: Baseline Roblox High (Set 1, X=120; root.z=0 -> face z=2.48)
        {"name": "03_School_BunnyHop", "start": b2_0, "end": b2_a, "lens": 30.0,
         "pos_start": (117.0, -6.6, 2.55), "pos_end": (119.4, -6.0, 2.65),
         "tgt_start": (119.2, 0.4, 2.05), "tgt_end": (120.8, 0.6, 2.15), "roll": 0.0, "orbit": 0.0},
        {"name": "04_School_DominusLow", "start": b2_a + 1, "end": b2_1, "lens": 26.0,
         "pos_start": (121.8, -4.4, 1.25), "pos_end": (120.4, -3.9, 1.45),
         "tgt_start": (121.0, 0.8, 2.45), "tgt_end": (121.2, 0.8, 2.65), "roll": 5.0, "orbit": 0.0},

        # Beat 3: Floor Is Lava Complication (Set 2, X=240; Hero on desk root.z=0.70 -> face z=3.15)
        {"name": "05_Lava_CrackWide", "start": b3_0, "end": b3_a, "lens": 27.0,
         "pos_start": (237.2, -6.4, 3.25), "pos_end": (239.0, -5.6, 2.95),
         "tgt_start": (240.4, 0.5, 2.05), "tgt_end": (241.0, 0.8, 2.25), "roll": -5.5, "orbit": 0.0,
         "kick_frame": b3_0 + 8},
        {"name": "06_Lava_BalanceZero_CU", "start": b3_a + 1, "end": b3_1, "lens": 36.0,
         "pos_start": (238.8, -4.2, 3.18), "pos_end": (239.6, -3.5, 3.22),
         "tgt_start": (239.6, -0.3, 2.95), "tgt_end": (239.6, -0.3, 3.02), "roll": 6.5, "orbit": 0.0},

        # Beat 4: "Luckily / Unluckily" Gravity Coil Launch (Set 2, X=240; Noob & Hero on desk root.z=0.70 -> face z=3.15)
        {"name": "07_Luckily_GravityCoil", "start": b4_0, "end": b4_a, "lens": 30.0,
         "pos_start": (236.8, -4.8, 2.85), "pos_end": (238.0, -4.2, 2.95),
         "tgt_start": (238.6, -0.3, 2.55), "tgt_end": (239.1, -0.3, 2.65), "roll": 0.0, "orbit": 0.0},
        {"name": "08_Unluckily_RoofBlast", "start": b4_a + 1, "end": b4_1, "lens": 25.0,
         "pos_start": (239.6, -6.2, 2.60), "pos_end": (239.6, -7.0, 6.40),
         "tgt_start": (239.6, -0.3, 2.85), "tgt_end": (239.6, -0.3, 7.60), "roll": -8.0, "orbit": 0.0,
         "kick_frame": b4_a + 12},

        # Beat 5: "You see," Sky Airtime Tax Bot (Set 3, X=360; Hero root.z=1.2..4.4 -> face z=3.68..6.88)
        {"name": "09_YouSee_TaxBotTrack", "start": b5_0, "end": b5_a, "lens": 28.0,
         "pos_start": (359.8, -6.2, 3.45), "pos_end": (360.2, -5.8, 4.95),
         "tgt_start": (360.3, 0.2, 3.25), "tgt_end": (360.4, 0.2, 4.75), "roll": 0.0, "orbit": 0.0},
        {"name": "10_Debt_Negative4000_Macro", "start": b5_a + 1, "end": b5_1, "lens": 34.0,
         "pos_start": (358.5, -4.8, 5.25), "pos_end": (359.2, -4.2, 6.45),
         "tgt_start": (359.8, 0.0, 4.95), "tgt_end": (359.9, 0.0, 6.15), "roll": 8.5, "orbit": 0.0,
         "kick_frame": b5_a + 18},

        # Beat 6: Admin Gravity Ban & Free Float Twist (Set 4, X=480)
        {"name": "11_Admin_BanAndFloat", "start": b6_0, "end": b6_a, "lens": 28.0,
         "pos_start": (477.2, -5.8, 2.55), "pos_end": (478.4, -5.0, 2.65),
         "tgt_start": (478.8, 0.8, 2.05), "tgt_end": (479.4, 0.6, 2.15), "roll": -4.0, "orbit": 0.0,
         "kick_frame": b6_0 + 10},
        {"name": "12_Twist_FloatForFree", "start": b6_a + 1, "end": b6_1, "lens": 28.0,
         "pos_start": (478.8, -6.2, 2.55), "pos_end": (481.2, -5.6, 2.65),
         "tgt_start": (479.6, 0.2, 2.05), "tgt_end": (481.6, 0.3, 2.15), "roll": 0.0, "orbit": 0.0},
    ]

    meta_shots = []
    for s in shots:
        cam, _ = add_animated_shot_camera(
            scene,
            name=s["name"],
            start_frame=s["start"],
            end_frame=s["end"],
            pos_start=s["pos_start"],
            pos_end=s["pos_end"],
            target_start=s["tgt_start"],
            target_end=s["tgt_end"],
            lens=s["lens"],
            use_dof=False,
            roll_deg=s["roll"],
            orbit_deg=s["orbit"],
            kick_frame=s.get("kick_frame"),
            kick_amp=0.18,
            handheld=0.35,
        )
        cam.data.clip_end = 75.0  # Isolates the 5 sets (spaced 120m apart!)
        meta_shots.append({
            "name": s["name"],
            "start_frame": s["start"],
            "end_frame": s["end"],
            "start_sec": round((s["start"] - 1) / float(FPS), 3),
            "end_sec": round(s["end"] / float(FPS), 3),
        })

    with open(os.path.join(BASE, "shots_meta.json"), "w", encoding="utf-8") as f:
        json.dump({"fps": FPS, "total_frames": scene.frame_end, "shots": meta_shots}, f, indent=2)
    return meta_shots


def main():
    clear_scene()
    total_frames, spans = load_timing()
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = total_frames

    # Render at 540x960 in Blender 5.3 EEVEE (AgX - Punchy, 180-deg motion blur) for fast 2-worker rendering,
    # then post_and_mux.py upscales to 1080x1920 and applies In-This-World zooms, RGB split, HUD & pop captions!
    configure_eevee_cinema(
        scene,
        res_x=540,
        res_y=960,
        fps=FPS,
        samples=16,
        raytracing=False,
        fast_gi=False,
        view_transform="AgX",
        look="AgX - Punchy",
        motion_blur=True,
        shutter=0.5,
    )
    setup_dark_studio_world(scene, "#12182b", strength=0.32)

    mats = {
        "skin_yellow": make_roblox_plastic_mat("Rbx_SkinYellow", "#F5CD30", rough_min=0.22, rough_max=0.36),
        "hero_blue": make_roblox_plastic_mat("Rbx_HeroBlue", "#1E66D0", rough_min=0.20, rough_max=0.35),
        "noob_blue": make_roblox_plastic_mat("Rbx_NoobBlue", "#0D69AC", rough_min=0.20, rough_max=0.34),
        "noob_green": make_roblox_plastic_mat("Rbx_NoobGreen", "#4B974B", rough_min=0.20, rough_max=0.34),
        "stud_grey": make_roblox_plastic_mat("Rbx_StudGrey", "#787F8C", rough_min=0.24, rough_max=0.40),
        "stud_green": make_roblox_plastic_mat("Rbx_StudGreen", "#28B458", rough_min=0.20, rough_max=0.34),
        "dark_slate": make_roblox_plastic_mat("Rbx_DarkSlate", "#232733", rough_min=0.25, rough_max=0.42),
        "navy_wall": make_roblox_plastic_mat("Rbx_NavyWall", "#182238", rough_min=0.30, rough_max=0.48),
        "hair_brown": make_roblox_plastic_mat("Rbx_HairBrown", "#4A2E1E", rough_min=0.28, rough_max=0.45),
        "gold": make_roblox_plastic_mat("Rbx_Gold", "#E8B938", rough_min=0.14, rough_max=0.26, metallic=0.82),
        "dark_metal": make_roblox_plastic_mat("Rbx_DarkMetal", "#1A1C24", rough_min=0.18, rough_max=0.32, metallic=0.75),
        "face_ink": make_roblox_plastic_mat("Rbx_FaceInk", "#121016", rough_min=0.15, rough_max=0.25),
        "neon_red": make_emissive_mat("Rbx_NeonRed", "#FF2A2A", strength=4.2),
        "neon_orange": make_emissive_mat("Rbx_NeonOrange", "#FF7B1A", strength=3.8),
        "neon_cyan": make_emissive_mat("Rbx_NeonCyan", "#28F0FF", strength=4.2),
        "neon_gold": make_emissive_mat("Rbx_NeonGold", "#FFD838", strength=3.6),
    }

    build_set0_lava_obby(mats, spans["beat1"][0], spans["beat1"][1])
    build_set1_school_hallway(mats, spans["beat2"][0], spans["beat2"][1])
    build_set2_classroom_coil(mats, spans["beat3"][0], spans["beat4"][1])
    build_set3_sky_taxbot(mats, spans["beat5"][0], spans["beat5"][1])
    build_set4_admin_float(mats, spans["beat6"][0], spans["beat6"][1])

    meta_shots = setup_12_storytime_cameras(scene, spans)

    frames_dir = os.path.join(BASE, "frames")
    os.makedirs(frames_dir, exist_ok=True)
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"

    blend_path = os.path.join(BASE, "roblox_jump_tax.blend")
    if "--range" not in sys.argv:
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        print(f"[OK] Saved Blender 5.3 Roblox scene -> {blend_path} ({total_frames} frames)")

    if "--preview" in sys.argv:
        mids = [s["start_frame"] + (s["end_frame"] - s["start_frame"]) // 2 for s in meta_shots]
        for f in mids:
            scene.frame_set(f)
            scene.render.filepath = os.path.join(frames_dir, f"f_{f:04d}.png")
            bpy.ops.render.render(write_still=True)
        print(f"[OK] Rendered {len(mids)} Roblox preview stills!")
    elif "--range" in sys.argv:
        idx = sys.argv.index("--range")
        scene.frame_start = int(sys.argv[idx + 1])
        scene.frame_end = int(sys.argv[idx + 2])
        scene.render.filepath = os.path.join(frames_dir, "f_")
        bpy.ops.render.render(animation=True)
        print(f"[OK] Rendered frames {scene.frame_start}..{scene.frame_end}!")
    else:
        scene.render.filepath = os.path.join(frames_dir, "f_")
        bpy.ops.render.render(animation=True)
        print(f"[OK] Rendered all {total_frames} Roblox frames!")


if __name__ == "__main__":
    main()
