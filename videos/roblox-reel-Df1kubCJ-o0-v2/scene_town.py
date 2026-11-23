"""
scene_town.py — Set 1: Rich Multi-Depth Town Street & Park Diorama (Night Party & Sunny Day).
Renders beats: b01_hook_town, b04_party_any, b05_birthday_tue, b06_nice_rock,
               b07_while_party_1, b38_so_tonight, b44_first_shift.
"""
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

PROJ_DIR = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking\videos\roblox-reel-Df1kubCJ-o0-v2")
sys.path.insert(0, str(PROJ_DIR))
import scene_common as sc
import char_factory as cf
import props_factory as pf
import blender_cinema_lib as bcl


def build_town_set(scene):
    col = bpy.data.collections.new("Set_TownStreet")
    scene.collection.children.link(col)

    m_asph = sc.make_textured_pbr("Mat_TownAsph", sc.TEX_ENV / "asphalt_speckled.png", sc.TEX_ENV / "asphalt_speckled_bump.png", uv_scale=(0.80, 0.80, 0.80), rough_min=0.72, rough_max=0.90, coat=0.0)
    m_pave = sc.make_textured_pbr("Mat_TownPave", sc.TEX_ENV / "sidewalk_pavers.png", sc.TEX_ENV / "sidewalk_pavers_bump.png", uv_scale=(0.85, 0.85, 0.85), rough_min=0.68, rough_max=0.86, coat=0.0)
    m_curb = sc.make_stylized_pbr("Mat_TownCurb", "#CBD5E1", rough=0.72, coat=0.0)
    m_grass = sc.make_stylized_pbr("Mat_TownGrass", "#44C458", rough=0.76, coat=0.0, sss=0.06, bump_str=0.04)
    m_dash = sc.make_stylized_pbr("Mat_TownDash", "#F8FAFC", rough=0.65, coat=0.0)

    # Multi-layer ground: speckled asphalt road, raised curbs, paver sidewalks, lush green park lawn
    pf.make_bevel_box("Road", (0, 0, -0.15), (46, 8.2, 0.30), m_asph, col, bevel_w=0.02)
    pf.make_bevel_box("Curb_N", (0, -4.15, -0.04), (46, 0.25, 0.16), m_curb, col, bevel_w=0.02)
    pf.make_bevel_box("Sidewalk_N", (0, -5.6, -0.06), (46, 2.8, 0.20), m_pave, col, bevel_w=0.02)
    pf.make_bevel_box("Curb_S", (0, 4.15, -0.04), (46, 0.25, 0.16), m_curb, col, bevel_w=0.02)
    pf.make_bevel_box("Sidewalk_S", (0, 5.6, -0.06), (46, 2.8, 0.20), m_pave, col, bevel_w=0.02)
    pf.make_bevel_box("Lawn_N", (0, -14.0, -0.15), (65, 16.0, 0.30), m_grass, col, bevel_w=0.02)
    for ix in range(-18, 20, 3):
        pf.make_bevel_box(f"Dash_{ix}", (ix, 0, 0.01), (1.3, 0.18, 0.02), m_dash, col, bevel_w=0.005)

    # Background Depth Layer 1: 6 Storybook Townhouses along North Sidewalk
    houses = [
        (-13.5, -9.8, 4.4, 4.0, 5.0, "#7DD3FC", "#2563EB"),
        (-8.2, -10.2, 4.6, 4.2, 5.8, "#FDE68A", "#DC2626"),
        (-2.8, -9.6, 4.2, 3.8, 5.2, "#C4B5FD", "#6D28D9"),
        (2.6, -10.0, 4.6, 4.0, 6.2, "#FCA5A5", "#0F766E"),
        (8.0, -9.7, 4.4, 4.0, 5.4, "#A7F3D0", "#EA580C"),
        (13.4, -10.2, 4.5, 4.0, 5.6, "#FBCFE8", "#4F46E5"),
    ]
    house_objs = []
    for i, (hx, hy, hw, hd, hh, wc, rc) in enumerate(houses):
        house_objs.append(pf.build_townhouse(f"TH_{i}", (hx, hy, 0.0), col, hw, hd, hh, wc, rc, is_night=True))

    # Background Depth Layer 2: Lush Bumpy Textured Trees + Wrought-Iron Streetlamps
    for ti, (tx, ty, ts) in enumerate([(-10.8, -6.4, 1.15), (-5.4, -6.5, 1.05), (0.0, -6.7, 1.25), (5.5, -6.4, 1.10), (10.8, -6.5, 1.18)]):
        pf.build_bumpy_tree(f"TownTree_{ti}", (tx, ty, 0.0), col, scale=ts)
    for li, lx in enumerate([-6.8, -1.6, 3.8, 8.8]):
        pf.build_streetlamp(f"Lamp_{li}", (lx, -4.35, 0.0), col, is_night=True)

    # Background Depth Layer 3: Layered Snow-Capped Alpine Mountains + Fluffy Clouds
    import bmesh
    m_mtn = sc.make_stylized_pbr("Mat_MtnTeal", "#1E4E68", rough=0.78, coat=0.0, bump_str=0.06)
    m_snow = sc.make_stylized_pbr("Mat_MtnSnow", "#F1F5F9", rough=0.62, coat=0.0)
    m_cloud = sc.make_stylized_pbr("Mat_CloudWht", "#F8FAFC", rough=0.72, coat=0.0, sss=0.10)
    for mi, (mx, my, rad, mh) in enumerate([(-14, -23, 6.5, 10.5), (-5, -25, 7.2, 12.2), (5, -24, 6.8, 11.4), (14, -23, 6.2, 10.0)]):
        pf.make_smooth_cyl(f"Mtn_{mi}", (mx, my, mh * 0.5 - 0.2), rad, mh, m_mtn, col, segs=18, bevel_w=0.05, r2=0.3)
        pf.make_smooth_cyl(f"Snow_{mi}", (mx, my, mh * 0.84 - 0.2), rad * 0.34, mh * 0.34, m_snow, col, segs=18, bevel_w=0.0, r2=0.18)
    for ci, (cx, cy, cz) in enumerate([(-8, -18, 9.5), (0, -20, 10.8), (8, -18, 9.2)]):
        for ox, oy, oz, sc_c in [(0, 0, 0, (1.8, 0.8, 0.8)), (-1.1, 0.1, -0.15, (1.2, 0.7, 0.65)), (1.1, -0.1, -0.15, (1.3, 0.7, 0.7))]:
            pf.make_smooth_sphere(f"Cloud_{ci}_{ox}", (cx + ox, cy + oy, cz + oz), sc_c, m_cloud, col, segs=18)

    # Overhead Catenary String Lights + Paper Lanterns + Floating Glossy Balloons + Road Confetti
    pcols = ["#EF4444", "#FACC15", "#38BDF8", "#EC4899", "#A855F7", "#22C55E"]
    rng = random.Random(42)
    night_decor = bpy.data.collections.new("Town_NightDecor")
    col.children.link(night_decor)
    for i in range(18):
        lx = -9.5 + i * 1.12
        lz = 4.35 - math.sin((i / 17.0) * math.pi) * 0.65
        c_hex = pcols[i % len(pcols)]
        pf.make_smooth_sphere(f"Lantern_{i}", (lx, -1.8, lz), (0.16, 0.16, 0.20), sc.make_stylized_pbr(f"Mat_Lant_{c_hex}", c_hex, rough=0.30, emit_hex=c_hex, emit_str=4.2), night_decor, segs=16)
    # Foreground festive string bulbs near lower street (matches OG hook frame!)
    for i in range(14):
        lx = -4.5 + i * 0.70
        lz = 0.55 - math.sin((i / 13.0) * math.pi) * 0.25
        c_hex = pcols[(i + 2) % len(pcols)]
        pf.make_smooth_sphere(f"FgBulb_{i}", (lx, 2.55, lz), (0.065, 0.065, 0.065), sc.make_stylized_pbr(f"Mat_FgB_{c_hex}", c_hex, emit_hex=c_hex, emit_str=5.5), night_decor, segs=12)

    # Balloons & Confetti
    for bi in range(16):
        bx = -8.5 + bi * 1.15 + rng.uniform(-0.2, 0.2)
        by = -3.8 + rng.uniform(-1.5, 1.2)
        bz = 2.6 + rng.uniform(-0.2, 1.2)
        c_hex = pcols[bi % len(pcols)]
        pf.make_smooth_sphere(f"Balloon_{bi}", (bx, by, bz), (0.24, 0.24, 0.30), sc.make_stylized_pbr(f"Mat_Bal_{c_hex}", c_hex, rough=0.18, coat=0.55), col, segs=18)
    for ci in range(48):
        cx = rng.uniform(-7.0, 7.0)
        cy = rng.uniform(-2.6, 2.6)
        c_hex = pcols[ci % len(pcols)]
        pf.make_bevel_box(f"Conf_{ci}", (cx, cy, 0.012), (0.09, 0.09, 0.01), sc.make_stylized_pbr(f"Mat_Conf_{c_hex}", c_hex, rough=0.3), col, bevel_w=0.002, segs=1, rot=(0, 0, rng.uniform(0, 3)))

    # Birthday Cake & Nice Rock Props
    cake = pf.build_birthday_cake("Prop_Cake", (0.0, -1.2, 0.0), col, scale=1.05)
    rock = pf.build_nice_rock("Prop_NiceRock", (0.0, 0.0, 0.0), col, scale=1.15)

    # Night Fireworks bursts
    fw_col = bpy.data.collections.new("Town_Fireworks")
    col.children.link(fw_col)
    for fi, (fx, fy, fz, fcol) in enumerate([(-4.5, -15, 7.2, "#F472B6"), (0.5, -16, 8.2, "#38BDF8"), (5.0, -15, 7.0, "#FACC15"), (-7.0, -16, 6.2, "#A855F7")]):
        m_fw = sc.make_stylized_pbr(f"Mat_FW_{fcol}", fcol, emit_hex=fcol, emit_str=12.0)
        for ray in range(12):
            ang = ray * (2.0 * math.pi / 12.0)
            pf.make_smooth_sphere(f"FW_{fi}_{ray}", (fx + math.cos(ang) * 1.15, fy, fz + math.sin(ang) * 1.15), (0.14, 0.14, 0.14), m_fw, fw_col, segs=10)

    return {"col": col, "cake": cake, "rock": rock, "fw_col": fw_col, "night_decor": night_decor}


def setup_town_lights(scene):
    lcol = bpy.data.collections.new("Town_Lights")
    scene.collection.children.link(lcol)

    sun_d = bpy.data.lights.new("Sun_Town", type="SUN")
    sun_d.energy = 3.6
    sun_d.angle = math.radians(2.0)
    sun = bpy.data.objects.new("Sun_Town", sun_d)
    lcol.objects.link(sun)
    sun.rotation_euler = (math.radians(46), math.radians(15), math.radians(26))

    # Warm front key + colorful party glow + cool moonlight rim!
    area_defs = [
        ("Key_Warm", (2.5, 6.5, 4.2), (0, 0, 1.0), 420.0, 4.5, 4400, 78),
        ("Rim_Moon", (-2.2, -5.5, 5.2), (0, 0, 1.2), 750.0, 4.0, 7600, 65),
        ("Party_Pink", (-4.0, 3.2, 3.5), (0, 0, 1.0), 320.0, 3.0, 3200, 95),
        ("Party_Cyan", (4.0, 3.2, 3.5), (0, 0, 1.0), 280.0, 3.0, 7200, 95),
    ]
    plights = []
    for nm, loc, tgt, en, sz, temp, spr in area_defs:
        ld = bpy.data.lights.new(nm, type="AREA")
        ld.energy = en
        ld.size = sz
        ld.spread = math.radians(spr)
        ld.use_temperature = True
        ld.temperature = temp
        lo = bpy.data.objects.new(nm, ld)
        lcol.objects.link(lo)
        lo.location = loc
        lo.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        plights.append((nm, lo, ld, en))
    return sun, plights


def set_town_mode(scene, sun, plights, props, is_night: bool):
    if is_night:
        sc.setup_stylized_sky_world(scene, "night", strength=0.45)
        sun.data.energy = 0.55
        sun.data.color = bcl.hex_to_linear("#93C5FD")[:3]
        for nm, _, ld, base_e in plights:
            ld.energy = base_e
            if nm == "Party_Pink":
                ld.use_temperature = False
                ld.color = bcl.hex_to_linear("#F472B6")[:3]
            elif nm == "Party_Cyan":
                ld.use_temperature = False
                ld.color = bcl.hex_to_linear("#38BDF8")[:3]
        props["fw_col"].hide_viewport = False
        props["fw_col"].hide_render = False
        props["night_decor"].hide_viewport = False
        props["night_decor"].hide_render = False
        scene.view_settings.exposure = -0.10
    else:
        sc.setup_stylized_sky_world(scene, "day", strength=0.65)
        sun.data.energy = 2.6
        sun.data.color = bcl.hex_to_linear("#FFF7E6")[:3]
        for nm, _, ld, base_e in plights:
            if "Party_" in nm:
                ld.energy = 20.0
            else:
                ld.energy = base_e * 0.55
        props["fw_col"].hide_viewport = True
        props["fw_col"].hide_render = True
        props["night_decor"].hide_viewport = True
        props["night_decor"].hide_render = True
        scene.view_settings.exposure = -0.15


def main():
    preview_only = "--preview" in sys.argv
    bcl.clear_scene()
    scene = bpy.context.scene
    res = (1080, 1920) if preview_only else (720, 1280)
    sc.configure_stylized_eevee(scene, res_x=res[0], res_y=res[1], samples=(16 if preview_only else 12), raytracing=True, fast_gi=True, motion_blur=False)

    beats_data = sc.load_beats()
    props = build_town_set(scene)
    sun, plights = setup_town_lights(scene)

    cast_col = bpy.data.collections.new("Town_Cast")
    scene.collection.children.link(cast_col)

    # 5 Bespoke Town Party Characters + Neighbor + Mayor!
    c_teal = cf.create_character("teal_friend", "Crowd_Teal", cast_col, party_hat="#FACC15")
    c_grandma = cf.create_character("grandma", "Crowd_Grandma", cast_col, party_hat="#EC4899")
    c_mint = cf.create_character("mint_girl", "Crowd_Mint", cast_col, party_hat="#38BDF8")
    c_rock = cf.create_character("rock_guy", "Crowd_Rock", cast_col, party_hat=None)
    c_purple = cf.create_character("purple_hoodie", "Crowd_Purple", cast_col, party_hat="#22C55E")
    c_neighbor = cf.create_character("neighbor", "Crowd_Neighbor", cast_col)
    c_mayor = cf.create_character("mayor", "Crowd_Mayor", cast_col)

    crowd = [c_teal, c_grandma, c_mint, c_rock, c_purple, c_neighbor, c_mayor]

    cam_d = bpy.data.cameras.new("Cam_Town")
    cam = bpy.data.objects.new("Cam_Town", cam_d)
    scene.collection.objects.link(cam)
    scene.camera = cam

    bcl.setup_cinema_compositor(
        scene, glare_threshold=1.65, glare_strength=0.12, dispersion=0.0010,
        lift_rgb=(0.985, 0.990, 1.015), gamma_rgb=(1.0, 1.0, 1.0), gain_rgb=(1.02, 1.01, 0.98),
        vignette=0.14,
    )

    town_beats = [
        ("b01_hook_town", True),
        ("b04_party_any", False),
        ("b05_birthday_tue", False),
        ("b06_nice_rock", True),
        ("b07_while_party_1", True),
        ("b38_so_tonight", True),
        ("b44_first_shift", True),
    ]

    for bid, is_night in town_beats:
        f0, f1 = sc.beat_frame_range(beats_data, bid)
        set_town_mode(scene, sun, plights, props, is_night=is_night)

        # Toggle props
        sc.set_hidden_tree(props["cake"], bid != "b05_birthday_tue")
        props["rock"].hide_viewport = (bid != "b06_nice_rock")
        props["rock"].hide_render = (bid != "b06_nice_rock")

        frames_to_render = [(f0 + f1) // 2] if preview_only else list(range(f0, f1 + 1))
        for f in frames_to_render:
            u = (f - f0) / max(1, (f1 - f0))
            t = f / 30.0

            if bid in ("b01_hook_town", "b07_while_party_1", "b38_so_tonight"):
                spots = [
                    (c_purple, (-1.65, -0.55, 0.0, 12)),
                    (c_mint,   (-0.55, -0.25, 0.0, 6)),
                    (c_teal,   (0.55, -0.35, 0.0, -5)),
                    (c_rock,   (1.55, -0.70, 0.0, -14)),
                    (c_grandma,(-1.10, -1.85, 0.0, 8)),
                    (c_neighbor,(0.10, -1.75, 0.0, 0)),
                    (c_mayor,  (1.25, -1.95, 0.0, -8)),
                ]
                for idx, (ch, (wx, wy, wz, yaw)) in enumerate(spots):
                    cf.set_char_transform(ch, wx, wy, wz, yaw)
                    cf.animate_party_dance(ch, t, phase=idx * 0.9, energy=1.0)
                if bid == "b01_hook_town":
                    sc.set_camera_look(cam, (0.0, 4.9 - 0.9 * u, 1.45), (0.0, -0.6, 1.25), lens=32.0, fstop=3.2)
                elif bid == "b07_while_party_1":
                    sc.set_camera_look(cam, (-1.2 + 2.4 * u, 4.4, 1.55), (0.0, -0.6, 1.20), lens=34.0, fstop=3.2)
                else:
                    sc.set_camera_look(cam, (0.5 - 1.0 * u, 5.2, 1.35), (0.0, -1.5, 2.20), lens=28.0, fstop=3.8)

            elif bid == "b04_party_any":
                # Sunny day park: Grandma & Teal Heart Friend cheering in front of bumpy green trees!
                spots = [
                    (c_grandma, (-0.55, -1.2, 0.0, 8)),
                    (c_teal,    (0.55, -1.2, 0.0, -8)),
                    (c_mint,    (-1.75, -2.5, 0.0, 14)),
                    (c_purple,  (1.75, -2.4, 0.0, -14)),
                    (c_neighbor,(0.0, -3.2, 0.0, 0)),
                    (c_rock,    (-2.8, -3.5, 0.0, 10)),
                    (c_mayor,   (2.8, -3.5, 0.0, -10)),
                ]
                for idx, (ch, (wx, wy, wz, yaw)) in enumerate(spots):
                    cf.set_char_transform(ch, wx, wy, wz, yaw)
                    cf.animate_party_dance(ch, t, phase=idx * 0.85, energy=1.05)
                sc.set_camera_look(cam, (0.0, 3.3 - 0.45 * u, 1.25), (0.0, -1.2, 1.22), lens=36.0, fstop=3.2)

            elif bid == "b05_birthday_tue":
                # Mayor + Mint Girl cheering beside multi-tier glowing Birthday Cake!
                cf.set_char_transform(c_mayor, -0.95, -1.2, 0.0, 14)
                cf.set_char_transform(c_mint,   0.95, -1.2, 0.0, -14)
                cf.set_char_transform(c_grandma, -2.1, -2.4, 0.0, 10)
                cf.set_char_transform(c_teal,    2.1, -2.4, 0.0, -10)
                cf.set_char_transform(c_neighbor, 0.0, -2.8, 0.0, 0)
                cf.set_char_transform(c_rock,   -3.0, -3.2, 0.0, 0)
                cf.set_char_transform(c_purple,  3.0, -3.2, 0.0, 0)
                for idx, ch in enumerate(crowd):
                    cf.animate_party_dance(ch, t, phase=idx * 0.7, energy=0.95)
                sc.set_camera_look(cam, (0.25 - 0.5 * u, 3.0 - 0.35 * u, 1.32), (0.0, -1.2, 1.05), lens=35.0, fstop=3.0)

            elif bid == "b06_nice_rock":
                # Rock Guy front & center proudly holding up the shiny sculpted Nice Rock!
                cf.set_char_transform(c_rock, 0.0, 0.35, 0.0, 0)
                cf.pose_char(
                    c_rock,
                    pelvis_z=0.02 * math.sin(t * 6.0),
                    torso_rot=(0, 0, -5),
                    head_rot=(-4, 0, 4),
                    arm_l=(82.0 + 4 * math.sin(t * 7.0), 0, -10),
                    forearm_l=(18.0, 0, 0),
                    arm_r=(18, 0, 16),
                    forearm_r=(25, 0, 0),
                )
                props["rock"].scale = (0.68, 0.68, 0.68)
                props["rock"].location = (0.44, 0.94, 1.28 + 0.02 * math.sin(t * 6.0))
                props["rock"].rotation_euler = (t * 1.4, t * 0.9, 0.2)
                for idx, (ch, (wx, wy)) in enumerate([(c_purple, (-1.4, -1.8)), (c_mint, (-0.5, -2.1)), (c_teal, (1.2, -1.9)), (c_grandma, (2.1, -2.2)), (c_neighbor, (-2.2, -2.5)), (c_mayor, (0.3, -2.8))]):
                    cf.set_char_transform(ch, wx, wy, 0.0, 0)
                    cf.animate_party_dance(ch, t, phase=idx * 1.1, energy=0.85)
                sc.set_camera_look(cam, (0.12, 3.1 - 0.35 * u, 1.24), (0.10, 0.35, 1.18), lens=40.0, fstop=2.8)

            elif bid == "b44_first_shift":
                cf.set_char_transform(c_mayor, 0.0, 0.20, 0.0, 0)
                cf.animate_party_dance(c_mayor, t, phase=0.2, energy=1.1)
                for idx, (ch, (wx, wy)) in enumerate([(c_grandma, (-1.1, -0.9)), (c_teal, (1.1, -0.9)), (c_mint, (-1.9, -1.5)), (c_purple, (1.9, -1.5)), (c_rock, (-0.5, -2.1)), (c_neighbor, (0.6, -2.1))]):
                    cf.set_char_transform(ch, wx, wy, 0.0, 0)
                    cf.animate_party_dance(ch, t, phase=idx * 0.85, energy=1.15)
                sc.set_camera_look(cam, (-0.3 + 0.6 * u, 4.1 - 0.55 * u, 1.38), (0.0, -0.4, 1.35), lens=32.0, fstop=3.2)

            if preview_only:
                sc.render_frame(scene, f, preview_tag=f"town_{bid}")
                break
            else:
                sc.render_frame(scene, f)


if __name__ == "__main__":
    main()
