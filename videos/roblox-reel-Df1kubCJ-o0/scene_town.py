"""
scene_town.py — Set 1: Roblox Town Party Street (Day & Vibrant Party Night).
Renders beats: b01_hook_town, b04_party_any, b05_birthday_tue, b06_nice_rock,
               b07_while_party_1, b38_so_tonight, b44_first_shift.
"""
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

PROJ_DIR = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking\videos\roblox-reel-Df1kubCJ-o0")
sys.path.insert(0, str(PROJ_DIR))
import scene_common as sc
import blender_cinema_lib as bcl


def build_town_set(scene):
    col = bpy.data.collections.new("Set_TownStreet")
    scene.collection.children.link(col)

    def box(name, loc, scale, hex_col, rough=0.45, emit_hex=None, emit_str=0.0):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
        o = sc._link_only(bpy.context.active_object, col)
        o.name = name
        o.scale = scale
        o.data.materials.append(sc.make_mat(f"Mat_T_{name[:10]}_{hex_col}", hex_col, rough=rough, emit_hex=emit_hex, emit_str=emit_str))
        return o

    # Asphalt road + sidewalks + green grass lawns
    box("Road",       (0,  0, -0.25), (60, 12, 0.5), "#334155", rough=0.72)
    box("Sidewalk_N", (0, -8, -0.15), (60,  5, 0.5), "#CBD5E1", rough=0.65)
    box("Sidewalk_S", (0,  8, -0.15), (60,  5, 0.5), "#CBD5E1", rough=0.65)
    box("Lawn_N",     (0,-20, -0.25), (80, 20, 0.5), "#4ADE80", rough=0.75)

    # Road dashed lines
    for ix in range(-22, 24, 5):
        box(f"Dash_{ix}", (ix, 0, 0.02), (2.2, 0.35, 0.04), "#F8FAFC", rough=0.6)

    # Colorful pastel Roblox houses along background (-Y = behind characters facing +Y)
    houses = [
        (-16, -15.5, 9, 8, 9, "#93C5FD", "#1D4ED8"),
        ( -5, -16.0, 9, 8, 11, "#FDE68A", "#DC2626"),
        (  6, -15.5, 9, 8, 10, "#C4B5FD", "#6D28D9"),
        ( 17, -16.0, 9, 8, 9.5, "#FCA5A5", "#0F766E"),
    ]
    for i, (hx, hy, hw, hd, hh, wall_c, roof_c) in enumerate(houses):
        box(f"House_{i}", (hx, hy, hh * 0.5), (hw, hd, hh), wall_c, rough=0.55)
        # Sloped roof pyramid/wedge
        bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=hw * 0.78, radius2=0.1, depth=3.8, location=(hx, hy, hh + 1.9), rotation=(0, 0, math.radians(45)))
        rf = sc._link_only(bpy.context.active_object, col)
        rf.name = f"Roof_{i}"
        rf.data.materials.append(sc.make_mat(f"Mat_Roof_{roof_c}", roof_c, rough=0.45))
        # Warm lit windows
        for wx in (-2.2, 2.2):
            for wz in (3.2, 6.4):
                box(f"Win_{i}_{wx}_{wz}", (hx + wx, hy + hd * 0.5 + 0.08, wz), (2.1, 0.15, 2.0), "#FEF08A", rough=0.2, emit_hex="#FEF08A", emit_str=1.2)

    # Fluffy blocky Roblox trees
    for tx, ty in [(-11, -9.8), (1.0, -9.8), (12.5, -9.8)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.55, depth=4.5, location=(tx, ty, 2.25))
        tr = sc._link_only(bpy.context.active_object, col)
        tr.data.materials.append(sc.make_mat("Mat_Trunk", "#78350F", rough=0.75))
        for ox, oy, oz, rad in [(0, 0, 5.4, 2.2), (-1.2, 0.3, 4.7, 1.5), (1.2, -0.2, 4.9, 1.6)]:
            bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=10, radius=rad, location=(tx + ox, ty + oy, oz))
            lf = sc._link_only(bpy.context.active_object, col)
            lf.data.materials.append(sc.make_mat("Mat_Leaves", "#22C55E", rough=0.60))

    # Colorful party string lights & floating balloons
    balloon_cols = ["#EF4444", "#FACC15", "#38BDF8", "#EC4899", "#A855F7", "#22C55E"]
    rng = random.Random(42)
    for bi in range(18):
        bx = -16 + bi * 1.9 + rng.uniform(-0.3, 0.3)
        by = -6.5 + rng.uniform(-2.5, 1.5)
        bz = 6.2 + rng.uniform(-0.6, 2.2)
        c_hex = balloon_cols[bi % len(balloon_cols)]
        bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=10, radius=0.62, location=(bx, by, bz))
        bl = sc._link_only(bpy.context.active_object, col)
        bl.scale = (0.85, 0.85, 1.05)
        bl.data.materials.append(sc.make_mat(f"Mat_Bal_{c_hex}", c_hex, rough=0.22, coat=0.45))

    # Festive glowing string bulbs overhead
    for li in range(20):
        lx = -18 + li * 1.9
        lz = 7.4 - math.sin((li / 19.0) * math.pi) * 1.1
        c_hex = balloon_cols[li % len(balloon_cols)]
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=0.22, location=(lx, -4.5, lz))
        lb = sc._link_only(bpy.context.active_object, col)
        lb.data.materials.append(sc.make_mat(f"Mat_Bulb_{c_hex}", c_hex, rough=0.2, emit_hex=c_hex, emit_str=4.5))

    # Confetti dots on road
    for ci in range(45):
        cx = rng.uniform(-12, 12)
        cy = rng.uniform(-4.5, 4.5)
        c_hex = balloon_cols[ci % len(balloon_cols)]
        box(f"Conf_{ci}", (cx, cy, 0.03), (0.25, 0.25, 0.02), c_hex, rough=0.3)

    # Birthday Cake prop (shown on b05_birthday_tue)
    cake_root = bpy.data.objects.new("Prop_BirthdayCake", None)
    cake_root.location = (0.0, -1.8, 0.0)
    col.objects.link(cake_root)
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=1.2, depth=1.0, location=(0, 0, 1.5))
    ck1 = sc._link_only(bpy.context.active_object, col)
    ck1.data.materials.append(sc.make_mat("Mat_CakeBlue", "#38BDF8", rough=0.35))
    ck1.parent = cake_root
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.85, depth=0.75, location=(0, 0, 2.35))
    ck2 = sc._link_only(bpy.context.active_object, col)
    ck2.data.materials.append(sc.make_mat("Mat_CakeFrost", "#F8FAFC", rough=0.35))
    ck2.parent = cake_root
    # Glowing candles
    for cx in (-0.3, 0.0, 0.3):
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.06, depth=0.45, location=(cx, 0, 2.95))
        cd = sc._link_only(bpy.context.active_object, col)
        cd.data.materials.append(sc.make_mat("Mat_Candle", "#F472B6", rough=0.4))
        cd.parent = cake_root
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.10, location=(cx, 0, 3.25))
        fl = sc._link_only(bpy.context.active_object, col)
        fl.data.materials.append(sc.make_mat("Mat_Flame", "#FACC15", emit_hex="#FDE047", emit_str=8.0))
        fl.parent = cake_root

    # Shiny Nice Rock prop (held up proudly on b06_nice_rock!)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.52, location=(0.0, 0.0, 0.0))
    rock = sc._link_only(bpy.context.active_object, col)
    rock.name = "Prop_NiceRock"
    rock.scale = (1.15, 0.90, 0.80)
    rock.data.materials.append(sc.make_mat("Mat_NiceRock", "#94A3B8", rough=0.32, metal=0.18, coat=0.35))

    # Night Fireworks bursts (visible during night beats b38, b44!)
    fw_col = bpy.data.collections.new("Town_Fireworks")
    col.children.link(fw_col)
    for fi, (fx, fy, fz, fcol) in enumerate([
        (-8, -22, 16, "#F472B6"), (0, -24, 18, "#38BDF8"), (9, -22, 15.5, "#FACC15"),
        (-13, -24, 14, "#A855F7"), (14, -24, 17, "#4ADE80"),
    ]):
        for ray in range(12):
            ang = ray * (2.0 * math.pi / 12.0)
            bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.35, location=(fx + math.cos(ang)*2.2, fy, fz + math.sin(ang)*2.2))
            sp = sc._link_only(bpy.context.active_object, fw_col)
            sp.data.materials.append(sc.make_mat(f"Mat_FW_{fcol}", fcol, emit_hex=fcol, emit_str=12.0))

    return {"col": col, "cake": cake_root, "rock": rock, "fw_col": fw_col}


def setup_town_lights(scene):
    lcol = bpy.data.collections.new("Town_Lights")
    scene.collection.children.link(lcol)

    sun_d = bpy.data.lights.new("Sun_Town", type="SUN")
    sun_d.energy = 3.2
    sun_d.angle = math.radians(1.5)
    sun = bpy.data.objects.new("Sun_Town", sun_d)
    lcol.objects.link(sun)
    sun.rotation_euler = (math.radians(48), math.radians(15), math.radians(28))

    # Colorful party area lights for night mode
    plights = []
    for nm, loc, col_hex, en in [
        ("PartyLight_Pink", (-6, 6, 8), "#F472B6", 1200),
        ("PartyLight_Cyan", ( 6, 6, 8), "#38BDF8", 1200),
        ("PartyLight_Gold", ( 0, 8, 9), "#FACC15", 900),
    ]:
        ld = bpy.data.lights.new(nm, type="AREA")
        ld.size = 5.0
        ld.energy = en
        ld.color = bcl.hex_to_linear(col_hex)[:3]
        lo = bpy.data.objects.new(nm, ld)
        lcol.objects.link(lo)
        lo.location = loc
        lo.rotation_euler = (Vector((0, -2, 2.5)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        plights.append(lo)

    return {"sun": sun, "plights": plights}


def set_lighting_mode(scene, lights, night: bool):
    sc.setup_bright_sky_world(scene, is_night=night)
    lights["sun"].data.energy = 0.65 if night else 3.2
    for pl in lights["plights"]:
        pl.data.energy = 1500.0 if night else 320.0


def set_hidden_tree(obj, hide: bool):
    obj.hide_viewport = hide
    obj.hide_render = hide
    for ch in obj.children:
        set_hidden_tree(ch, hide)


def main():
    preview_only = "--preview" in sys.argv
    bcl.clear_scene()
    scene = bpy.context.scene
    sc.configure_fast_eevee(scene, res_x=720, res_y=1280, samples=10, raytracing=False)

    beats_data = sc.load_beats()
    props = build_town_set(scene)
    lights = setup_town_lights(scene)

    cast_col = bpy.data.collections.new("Town_Cast")
    scene.collection.children.link(cast_col)

    # Append our rigged Roblox R6 cast wearing festive 3D Party Hats!
    cast_specs = [
        ("04_Maya_BestFriend", "Maya",  "#EC4899", (-3.2,  0.2, 0.0,  10)),
        ("08_Chloe_Rival",     "Chloe", "#38BDF8", ( 3.0,  0.4, 0.0, -12)),
        ("02_Noob_BestFriend", "Noob",  "#FACC15", ( 0.0, -0.5, 0.0,   0)),
        ("05_Dad_Principal",   "Dad",   "#22C55E", (-6.2, -1.8, 0.0,  15)),
        ("06_Hacker_Glitch",   "Hacker","#A855F7", ( 6.2, -1.8, 0.0, -15)),
        ("07_Admin_Boss",      "Admin", "#EF4444", (-2.0, -3.5, 0.0,   5)),
        ("10_Town_Mayor",      "Mayor", "#FACC15", ( 2.5, -3.2, 0.0,  -6)),
    ]
    chars = {}
    for cid, name, ph_col, _ in cast_specs:
        chars[name] = sc.append_character(cid, name, cast_col, add_party_hat=True, party_hat_color=ph_col)

    # Camera
    cam_d = bpy.data.cameras.new("Cam_Town")
    cam = bpy.data.objects.new("Cam_Town", cam_d)
    scene.collection.objects.link(cam)
    scene.camera = cam

    bcl.setup_cinema_compositor(
        scene, glare_threshold=1.5, glare_strength=0.18, dispersion=0.001,
        lift_rgb=(0.99, 0.99, 1.0), gamma_rgb=(1.0, 1.0, 1.0), gain_rgb=(1.02, 1.02, 1.01),
        vignette=0.12,
    )

    town_beats = [
        "b01_hook_town", "b04_party_any", "b05_birthday_tue", "b06_nice_rock",
        "b07_while_party_1", "b38_so_tonight", "b44_first_shift",
    ]

    for bid in town_beats:
        f0, f1 = sc.beat_frame_range(beats_data, bid)
        is_night = bid in ("b06_nice_rock", "b07_while_party_1", "b38_so_tonight", "b44_first_shift")
        set_lighting_mode(scene, lights, night=is_night)
        props["fw_col"].hide_viewport = not is_night
        props["fw_col"].hide_render = not is_night
        set_hidden_tree(props["cake"], bid != "b05_birthday_tue")
        props["rock"].hide_viewport = (bid != "b06_nice_rock")
        props["rock"].hide_render = (bid != "b06_nice_rock")

        # Default placements
        for _, name, _, (px, py, pz, yaw) in cast_specs:
            sc.set_char_transform(chars[name], px, py, pz, yaw)

        frames_to_render = [(f0 + f1) // 2] if preview_only else list(range(f0, f1 + 1))
        for f in frames_to_render:
            u = (f - f0) / max(1, (f1 - f0))
            t = f / 30.0

            # Animate dancing crowd
            for idx, (_, name, _, _) in enumerate(cast_specs):
                sc.animate_party_dance(chars[name], t, phase=idx * 0.9, energy=1.1)

            if bid == "b01_hook_town":
                # Opening party street push-in across cheering crowd!
                sc.set_camera_look(cam, (-1.8 + 3.6 * u, 11.8 - 1.5 * u, 3.6), (0.0, -1.0, 2.7), lens=32.0)

            elif bid == "b04_party_any":
                # Maya + Noob + Chloe cheering with balloons!
                sc.set_char_transform(chars["Maya"],  -1.6, 0.6, 0.0,  6)
                sc.set_char_transform(chars["Noob"],   1.6, 0.6, 0.0, -6)
                sc.set_camera_look(cam, (0.0, 9.5 - 1.2 * u, 3.3), (0.0, 0.2, 3.0), lens=36.0)

            elif bid == "b05_birthday_tue":
                # Mayor & Chloe celebrating with glowing birthday cake ("A birthday. A Tuesday.")!
                sc.set_char_transform(chars["Mayor"], -1.8, -0.4, 0.0, 12)
                sc.set_char_transform(chars["Chloe"],  1.8, -0.4, 0.0, -12)
                sc.set_camera_look(cam, (-0.8 + 1.6 * u, 8.8 - 0.8 * u, 3.4), (0.0, -0.8, 2.8), lens=35.0)

            elif bid == "b06_nice_rock":
                # Dad proudly holding up a shiny gray rock while everyone cheers!
                sc.set_char_transform(chars["Dad"], 0.0, 1.5, 0.0, 0.0)
                sc.set_char_pose(
                    chars["Dad"],
                    torso_loc=(0, 0, 0.12 * abs(math.sin(t * 7.0))),
                    head_rot=(-8, 0, 4 * math.sin(t * 5.0)),
                    rarm_rot=(-105, 10, -10),
                    larm_rot=(-140, -12, 16),
                )
                props["rock"].location = (1.15, 2.55, 3.65 + 0.14 * abs(math.sin(t * 7.0)))
                props["rock"].rotation_euler = (0.3, t * 2.0, 0.4)
                sc.set_camera_look(cam, (0.4, 9.6 - 1.2 * u, 3.35), (0.35, 1.5, 3.3), lens=34.0)

            elif bid == "b07_while_party_1":
                # Party crowd dancing in street, swift pan right at end!
                sc.set_char_transform(chars["Maya"], 0.0, 1.4, 0.0, -15)
                sc.set_camera_look(cam, (-1.0 + 3.0 * u, 9.0, 3.4), (0.5 * u, 0.5, 2.9), lens=34.0)

            elif bid == "b38_so_tonight":
                # Vibrant night party crowd with fireworks!
                sc.set_camera_look(cam, (-2.2 + 4.4 * u, 11.5 - 1.2 * u, 3.8), (0.0, -0.5, 3.1), lens=32.0)

            elif bid == "b44_first_shift":
                # Saturday night — biggest party of the year led by the Mayor!
                sc.set_char_transform(chars["Mayor"], 0.0, 1.8, 0.0, 0.0)
                sc.animate_party_dance(chars["Mayor"], t, phase=0.0, energy=1.3)
                sc.set_camera_look(cam, (-0.8 + 1.6 * u, 9.6 - 1.6 * u, 3.4), (0.0, 1.2, 3.2), lens=34.0)

            bpy.context.view_layer.update()
            sc.render_frame(scene, f, preview_tag=f"town_{bid}" if preview_only else None)

    print("scene_town.py COMPLETE!")


if __name__ == "__main__":
    main()
