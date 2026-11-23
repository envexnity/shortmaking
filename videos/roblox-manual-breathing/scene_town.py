"""
scene_town.py — Roblox Town Street & Cafe Patio Set for roblox-manual-breathing.
Renders beats: b01_timer..b10_eating and b14_dont_realize.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

SHORTMAKING_ROOT = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking")
V2_DIR = SHORTMAKING_ROOT / "videos" / "roblox-reel-Df1kubCJ-o0-v2"
PROJ_DIR = SHORTMAKING_ROOT / "videos" / "roblox-manual-breathing"

sys.path.insert(0, str(PROJ_DIR))
sys.path.insert(0, str(V2_DIR))

import scene_common as sc
sc.PROJ_DIR = PROJ_DIR
sc.FRAMES_DIR = PROJ_DIR / "frames"
sc.PREVIEWS_DIR = PROJ_DIR / "previews"
sc.FRAMES_DIR.mkdir(parents=True, exist_ok=True)
sc.PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)

import char_factory as cf
import props_factory as pf
import scene_town as v2_town
import props_custom as pc
import blender_cinema_lib as bcl


def main():
    preview_only = "--preview" in sys.argv
    bcl.clear_scene()
    scene = bpy.context.scene
    res = (720, 1280)
    sc.configure_stylized_eevee(
        scene,
        res_x=res[0],
        res_y=res[1],
        samples=(12 if preview_only else 8),
        raytracing=True,
        fast_gi=True,
        motion_blur=False,
        exposure=-0.12,
    )

    beats_data = sc.load_beats()
    props = v2_town.build_town_set(scene)
    sun, plights = v2_town.setup_town_lights(scene)
    v2_town.set_town_mode(scene, sun, plights, props, is_night=False)

    # Hide party cake/rock from v2 town set
    sc.set_hidden_tree(props["cake"], True)
    sc.set_hidden_tree(props["rock"], True)

    cast_col = bpy.data.collections.new("Town_Cast")
    scene.collection.children.link(cast_col)

    alex = cf.create_character("alex", "Alex", cast_col)
    friend = cf.create_character("teal_friend", "Friend_Teal", cast_col)
    mint = cf.create_character("mint_girl", "Town_Mint", cast_col)
    rock = cf.create_character("rock_guy", "Town_Rock", cast_col)

    prop_col = bpy.data.collections.new("Town_CustomProps")
    scene.collection.children.link(prop_col)

    plate_timer_ok = pc.make_emissive_plate_obj("Plate_TimerOK", "plate_timer_ok.png", (0, 0, -10), 0.88, 0.30, prop_col)
    plate_timer_low = pc.make_emissive_plate_obj("Plate_TimerLow", "plate_timer_low.png", (0, 0, -10), 0.92, 0.32, prop_col)
    plate_logout = pc.make_emissive_plate_obj("Plate_Logout", "plate_logout.png", (0, 0, -10), 1.35, 0.46, prop_col)
    plate_nopause = pc.make_emissive_plate_obj("Plate_NoPause", "plate_no_pause.png", (0, 0, -10), 1.15, 0.40, prop_col)
    plate_auto = pc.make_emissive_plate_obj("Plate_AutoOn", "plate_auto_on.png", (0, 0, -10), 1.05, 0.36, prop_col)

    wisps = pc.build_air_wisps("Town_Air", prop_col, count=10)
    lungs = pc.build_xray_lungs("Town_Lungs", prop_col)
    pause_btn = pc.build_arcade_button("PausePedestal", (0, 0, -10), prop_col, cap_hex="#EF4444", emit_hex="#FF3344", plate_png="plate_no_pause.png")

    # Bistro Cafe Table + Burger for b10_eating
    cafe_root = bpy.data.objects.new("Cafe_Setup", None)
    cafe_root.location = (0, 0, -10)
    prop_col.objects.link(cafe_root)
    m_wood = sc.make_textured_pbr("Mat_CafeWood", sc.TEX_ENV / "wood_table_espresso.png", sc.TEX_ENV / "wood_table_espresso_bump.png", uv_scale=(1.0, 1.0, 1.0))
    m_steel = sc.make_stylized_pbr("Mat_CafeSteel", "#94A3B8", rough=0.28, metal=0.8)
    pf.make_smooth_cyl("Cafe_Top", (0, 0, 0.78), 0.55, 0.05, m_wood, prop_col, segs=32, bevel_w=0.01, parent=cafe_root)
    pf.make_smooth_cyl("Cafe_Leg", (0, 0, 0.39), 0.045, 0.76, m_steel, prop_col, segs=16, parent=cafe_root)
    pf.build_hero_burger("Cafe_Burger", (0.0, -0.05, 0.81), prop_col, scale=0.95).parent = cafe_root

    cam_d = bpy.data.cameras.new("Cam")
    cam_obj = bpy.data.objects.new("Cam", cam_d)
    scene.collection.children[0].objects.link(cam_obj)
    scene.camera = cam_obj

    town_beats = [
        "b01_timer", "b02_resets", "b03_pull_gas", "b04_lungs", "b05_face_holes",
        "b06_stop_black", "b07_logout", "b08_no_pause", "b09_walking", "b10_eating",
        "b14_dont_realize",
    ]

    def reset_props():
        for obj in (plate_timer_ok, plate_timer_low, plate_logout, plate_nopause, plate_auto):
            obj.location = (0, 0, -10)
            obj.scale = (1, 1, 1)
            obj.rotation_euler = (math.radians(90), 0, 0)
        for w in wisps:
            w.location = (0, 0, -10)
        lungs["root"].location = (0, 0, -10)
        pause_btn["root"].location = (0, 0, -10)
        pause_btn["cap"].location = (0, 0, 0.96)
        cafe_root.location = (0, 0, -10)
        sc.set_hidden_tree(alex["arm"], False)
        sc.set_hidden_tree(friend["arm"], False)
        sc.set_hidden_tree(mint["arm"], False)
        sc.set_hidden_tree(rock["arm"], False)
        cf.set_char_transform(mint, -2.6, -4.8, 0.0, 15.0)
        cf.set_char_transform(rock, 2.8, -5.0, 0.0, -20.0)
        cf.set_char_transform(friend, 1.9, -4.6, 0.0, -15.0)
        cf.pose_char(friend)
        cf.pose_char(mint)
        cf.pose_char(rock)
        cf.set_face(friend, "crowd_happy_1.png")
        cf.set_face(mint, "crowd_happy_2.png")
        cf.set_face(rock, "crowd_rock_guy.png")
        v2_town.set_town_mode(scene, sun, plights, props, is_night=False)

    def update_state(bid: str, u: float, f: int):
        reset_props()
        t = f / 30.0
        cf.set_char_transform(alex, 0.0, 0.0, 0.0, 0.0)

        # Background idle motion so world is alive
        cf.pose_char(mint, torso_rot=(0, 0, math.sin(t * 2.4) * 5.0), arm_l=(12 + math.sin(t * 3.0) * 12, 0, 10))
        cf.pose_char(rock, torso_rot=(0, 0, math.cos(t * 2.1) * 4.0), arm_r=(18 + math.cos(t * 2.8) * 10, 0, -10))

        if bid == "b01_timer":
            cf.set_face_with_blink(alex, "alex_deadpan", f, seed=1)
            breath = math.sin(u * math.pi * 2.0) * 0.025
            cf.pose_char(alex, pelvis_z=breath, arm_l=(8, 0, 12), arm_r=(8, 0, -12))
            plate_timer_ok.location = (0.0, 0.0, 2.15 + math.sin(u * 6.0) * 0.03)
            sc.set_camera_look(cam_obj, (0.15 - 0.15 * u, 3.35 - 0.55 * u, 1.48), (0.0, 0.0, 1.38), lens=35.0)

        elif bid == "b02_resets":
            cf.set_face_with_blink(alex, "alex_determined", f, seed=2)
            pop = 1.0 + 0.24 * max(0.0, 1.0 - abs(u - 0.45) * 4.0)
            plate_timer_ok.location = (0.0, 0.0, 2.12)
            plate_timer_ok.scale = (pop, pop, pop)
            cf.pose_char(alex, pelvis_z=0.03 * math.sin(u * math.pi), arm_l=(18, 0, 16), arm_r=(18, 0, -16))
            pc.animate_air_wisps(wisps, (0.0, 0.0, 1.48), t, speed=2.2, exhale=False)
            sc.set_camera_look(cam_obj, (-0.25 + 0.25 * u, 2.15 - 0.35 * u, 1.50), (0.0, 0.0, 1.48), lens=38.0)

        elif bid == "b03_pull_gas":
            cf.set_face_with_blink(alex, "alex_focus_squint", f, seed=3)
            inhale_phase = math.sin(u * math.pi * 3.0)
            cf.pose_char(alex, pelvis_z=0.02 * inhale_phase, torso_rot=(-4.0 * inhale_phase, 0, 0), arm_l=(22, 0, 20), arm_r=(22, 0, -20))
            pc.animate_air_wisps(wisps, (0.0, 0.0, 1.48), t, speed=2.4, exhale=False)
            if u < 0.50:
                lu = u / 0.50
                sc.set_camera_look(cam_obj, (1.65 - 0.25 * lu, 1.65 - 0.20 * lu, 1.48), (0.0, 0.10, 1.36), lens=34.0)
            else:
                lu = (u - 0.50) / 0.50
                sc.set_camera_look(cam_obj, (-1.15 + 0.30 * lu, 1.85 - 0.35 * lu, 1.25), (0.0, 0.05, 1.38), lens=32.0)

        elif bid == "b04_lungs":
            cf.set_face_with_blink(alex, "alex_shocked_wide", f, seed=4)
            pulse = 1.0 + 0.16 * math.sin(u * math.pi * 4.0)
            lungs["root"].location = (0.0, 0.0, 0.0)
            lungs["l"].scale = (pulse, pulse, pulse)
            lungs["r"].scale = (pulse, pulse, pulse)
            cf.pose_char(alex, arm_l=(16, 0, 24), arm_r=(16, 0, -24))
            sc.set_camera_look(cam_obj, (0.0, 1.72 - 0.24 * u, 1.24), (0.0, 0.05, 1.18), lens=35.0)

        elif bid == "b05_face_holes":
            cf.set_face_with_blink(alex, "alex_focus_squint", f, seed=5)
            cf.pose_char(alex, head_rot=(0, 8.0 * math.sin(u * math.pi), 0), arm_r=(108, 12, -16), forearm_r=(42, 0, 0))
            pc.animate_air_wisps(wisps, (0.0, 0.0, 1.48), t, speed=2.8, exhale=False)
            sc.set_camera_look(cam_obj, (0.22 - 0.18 * u, 0.96 - 0.16 * u, 1.54), (0.0, 0.15, 1.50), lens=24.0)

        elif bid == "b06_stop_black":
            # Dramatic darkening as friend holds breath
            scene.view_settings.exposure = -0.15 - 0.72 * u
            sun.data.energy = 2.4 - 1.8 * u
            sc.set_hidden_tree(alex["arm"], True)
            cf.set_char_transform(friend, 0.0, 0.0, 0.0, 0.0)
            cf.set_face(friend, "crowd_hungry.png")
            wobble = math.sin(u * 26.0) * 6.0 * u
            cf.pose_char(friend, torso_rot=(-8.0 * u, 0, wobble), head_rot=(-10.0 * u, 0, wobble), arm_l=(125, -24, 14), forearm_l=(65, -20, 0), arm_r=(125, 24, -14), forearm_r=(65, 20, 0))
            plate_timer_low.location = (0.0, 0.0, 2.15)
            flash = 1.0 + 0.15 * abs(math.sin(u * math.pi * 6.0))
            plate_timer_low.scale = (flash, flash, flash)
            sc.set_camera_look(cam_obj, (0.0, 2.15 - 0.45 * u, 1.42), (0.0, 0.0, 1.38), lens=32.0, roll_deg=7.5 * u)

        elif bid == "b07_logout":
            scene.view_settings.exposure = -0.68
            sun.data.energy = 0.7
            sc.set_hidden_tree(alex["arm"], True)
            fall = min(1.0, u * 2.2)
            fall_ease = 1.0 - (1.0 - fall) ** 3
            cf.set_char_transform(friend, 0.0, -0.35 * fall_ease, 0.18 * fall_ease, 0.0)
            friend["arm"].rotation_euler = (math.radians(-86.0 * fall_ease), 0.0, math.radians(10.0 * fall_ease))
            cf.set_face(friend, "crowd_hungry.png")
            cf.pose_char(friend, arm_l=(90, 0, 35), arm_r=(90, 0, -35), leg_l=(12, 0, 10), leg_r=(12, 0, -10))
            pop = min(1.05, 0.4 + u * 2.8)
            plate_logout.location = (0.0, -0.1, 1.38 + 0.08 * math.sin(u * 8.0))
            plate_logout.scale = (pop, pop, pop)
            kick = int(u * 45)
            sc.set_camera_look(cam_obj, (0.0, 2.75 - 0.25 * u, 1.85), (0.0, -0.25, 0.65), lens=30.0, kick_offset=(kick if kick < 7 else -1), kick_amp=0.06)

        elif bid == "b08_no_pause":
            cf.set_face_with_blink(alex, "alex_determined", f, seed=8)
            pause_btn["root"].location = (0.0, 0.55, 0.0)
            pause_btn["root"].scale = (0.78, 0.78, 0.78)
            plate_nopause.location = (0.0, 0.0, 2.08)
            slam = max(0.0, math.sin(u * math.pi * 2.0))
            pause_btn["cap"].location = (0.0, 0.0, 0.96 - 0.05 * slam)
            cf.pose_char(alex, torso_rot=(18.0 * slam, 0, 0), arm_l=(82 + 24 * slam, -18, 12), forearm_l=(28, -10, 0), arm_r=(82 + 24 * slam, 18, -12), forearm_r=(28, 10, 0))
            kick = int((u - 0.25) * 35) if 0.25 <= u <= 0.55 else -1
            sc.set_camera_look(cam_obj, (0.95 - 0.22 * u, 2.45 - 0.28 * u, 1.56), (0.0, 0.25, 1.24), lens=32.0, kick_offset=kick, kick_amp=0.04)

        elif bid == "b09_walking":
            cf.set_face_with_blink(alex, "alex_deadpan", f, seed=9)
            wx = -0.9 + 1.8 * u
            cf.set_char_transform(alex, wx, 0.15, 0.0, -78.0)
            step = math.sin(u * math.pi * 6.0)
            cf.pose_char(alex, pelvis_z=abs(step) * 0.04, arm_l=(32 * step, 0, 10), arm_r=(-32 * step, 0, -10), leg_l=(-36 * step, 0, 0), leg_r=(36 * step, 0, 0))
            plate_auto.location = (wx, 0.15, 2.12)
            pc.animate_air_wisps(wisps, (wx, 0.25, 1.48), t, speed=2.2, exhale=False)
            sc.set_camera_look(cam_obj, (wx + 0.35, 2.45 - 0.25 * u, 1.35), (wx, 0.15, 1.25), lens=34.0)

        elif bid == "b10_eating":
            cf.set_face_with_blink(alex, "alex_smug", f, seed=10)
            cafe_root.location = (0.0, 0.62, 0.0)
            chew = abs(math.sin(u * math.pi * 6.0))
            cf.pose_char(alex, torso_rot=(8.0, 0, 0), head_rot=(8.0 * chew, 0, 0), arm_r=(95 + 14 * chew, 22, -12), forearm_r=(62, 10, 0), arm_l=(55, -16, 10))
            pc.animate_air_wisps(wisps, (0.0, 0.0, 1.50), t, speed=2.5, exhale=False)
            sc.set_camera_look(cam_obj, (-0.55 + 0.15 * u, 1.85 - 0.22 * u, 1.42), (0.0, 0.35, 1.25), lens=32.0)

        elif bid == "b14_dont_realize":
            cf.set_char_transform(alex, 0.12, 0.0, 0.0, 20.0)
            cf.set_char_transform(mint, -0.86, 0.12, 0.0, -32.0)
            cf.set_char_transform(rock, 1.05, -0.45, 0.0, 25.0)
            plate_auto.location = (0.12, 0.0, 2.10)
            plate_auto.scale = (0.82, 0.82, 0.82)
            if u < 0.72:
                cf.set_face_with_blink(alex, "alex_smug", f, seed=14)
                cf.pose_char(alex, arm_l=(18, 0, 14), arm_r=(42 + 12 * math.sin(t * 6.0), 0, -18))
                cf.pose_char(mint, arm_l=(65 + 18 * math.sin(t * 5.0), -18, 12))
            else:
                cf.set_face(alex, "alex_shocked_wide.png")
                cf.pose_char(alex, head_rot=(-8.0, 0, 12.0), arm_l=(82, 0, 24), arm_r=(82, 0, -24))
                cf.pose_char(mint, arm_l=(95, -24, 15), forearm_l=(25, 0, 0))
            if u < 0.52:
                lu = u / 0.52
                sc.set_camera_look(cam_obj, (-0.28, 3.45 - 0.30 * lu, 1.44), (-0.32, 0.0, 1.30), lens=30.0)
            else:
                lu = (u - 0.52) / 0.48
                sc.set_camera_look(cam_obj, (0.18, 2.15 - 0.35 * lu, 1.46), (0.12, 0.0, 1.40), lens=34.0)

    if preview_only:
        for pid in ("b01_timer", "b04_lungs", "b07_logout", "b08_no_pause", "b14_dont_realize"):
            fa, fb = sc.beat_frame_range(beats_data, pid)
            fm = (fa + fb) // 2
            u = (fm - fa) / max(1, fb - fa)
            update_state(pid, u, fm)
            sc.render_frame(scene, fm, preview_tag=f"prev_{pid}")
        return

    for bid in town_beats:
        fa, fb = sc.beat_frame_range(beats_data, bid)
        print(f"[scene_town] Rendering {bid}: frames {fa}..{fb}")
        for f in range(fa, fb + 1):
            u = (f - fa) / max(1, fb - fa)
            update_state(bid, u, f)
            sc.render_frame(scene, f)


if __name__ == "__main__":
    main()
