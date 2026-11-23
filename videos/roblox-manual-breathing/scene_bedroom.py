"""
scene_bedroom.py — Cozy Bedroom & Dramatic Red Alert Manual Mode Set for roblox-manual-breathing.
Renders beats: b11_sleeping, b12_auto_force, b13_20k_times, b15_manual_mode, b16_good_luck.
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
import scene_room as v2_room
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
        exposure=-0.14,
    )

    beats_data = sc.load_beats()
    props = v2_room.build_room_set(scene)
    v2_room.setup_room_lights(scene)

    # Hide v2 burger-wrapping table/props cleanly
    for obj in bpy.data.objects:
        if any(k in obj.name for k in ("TableTop", "TLeg_", "WrapSheet", "CenterBurger", "CenterWrapped", "UnwrapStack", "TowerWB", "Alarm_5AM", "Stopwatch", "Breakfast", "BluePlate", "NeighborCat", "Griddle", "CookedPatty", "BlurHands")):
            sc.set_hidden_tree(obj, True)

    # Add extra dramatic alert lights for b15/b16
    lcol = bpy.data.collections.get("Room_Lights") or scene.collection
    alert_ld = bpy.data.lights.new("Alert_Red", type="AREA")
    alert_ld.energy = 0.0
    alert_ld.size = 2.0
    alert_ld.color = (1.0, 0.14, 0.18)
    alert_lo = bpy.data.objects.new("Alert_Red", alert_ld)
    lcol.objects.link(alert_lo)
    alert_lo.location = (0.0, 1.85, 2.25)
    alert_lo.rotation_euler = (Vector((0.0, 0.2, 1.1)) - Vector(alert_lo.location)).to_track_quat("-Z", "Y").to_euler()

    rim_ld = bpy.data.lights.new("Alert_CyanRim", type="AREA")
    rim_ld.energy = 0.0
    rim_ld.size = 1.8
    rim_ld.color = (0.20, 0.80, 1.0)
    rim_lo = bpy.data.objects.new("Alert_CyanRim", rim_ld)
    lcol.objects.link(rim_lo)
    rim_lo.location = (-1.3, -0.8, 2.0)
    rim_lo.rotation_euler = (Vector((0.0, 0.1, 1.3)) - Vector(rim_lo.location)).to_track_quat("-Z", "Y").to_euler()

    cast_col = bpy.data.collections.new("Bedroom_Cast")
    scene.collection.children.link(cast_col)
    alex = cf.create_character("alex", "Alex", cast_col)

    prop_col = bpy.data.collections.new("Bedroom_CustomProps")
    scene.collection.children.link(prop_col)

    bed = pc.build_bed("Cozy_Bed", (0.85, 0.35, 0.0), prop_col)
    plate_zzz = pc.make_emissive_plate_obj("Plate_Zzz", "plate_zzz.png", (0, 0, -10), 0.72, 0.26, prop_col)
    plate_auto = pc.make_emissive_plate_obj("Plate_Auto", "plate_auto_on.png", (0, 0, -10), 1.05, 0.36, prop_col)
    plate_20k = pc.make_emissive_plate_obj("Plate_20K", "plate_20k.png", (0, 0, -10), 1.25, 0.42, prop_col)
    plate_manual = pc.make_emissive_plate_obj("Plate_Manual", "plate_manual.png", (0, 0, -10), 1.22, 0.42, prop_col)

    wisps = pc.build_air_wisps("Bed_Air", prop_col, count=10)
    lungs = pc.build_xray_lungs("Bed_Lungs", prop_col)
    breathe_btn = pc.build_arcade_button("BreatheBtn", (0, 0, -10), prop_col, cap_hex="#EF4444", emit_hex="#FF2233", plate_png="plate_breathe.png")

    cam_d = bpy.data.cameras.new("Cam")
    cam_obj = bpy.data.objects.new("Cam", cam_d)
    scene.collection.children[0].objects.link(cam_obj)
    scene.camera = cam_obj

    room_lights = [o for o in bpy.data.objects if o.type == "LIGHT" and o.name.startswith("Room_")]
    base_energies = {o.name: o.data.energy for o in room_lights}

    def set_alert_lighting(is_alert: bool, pulse: float = 1.0):
        if is_alert:
            for o in room_lights:
                o.data.energy = base_energies[o.name] * 0.22
            alert_ld.energy = 240.0 + 180.0 * pulse
            rim_ld.energy = 190.0
            scene.view_settings.exposure = -0.22
        else:
            for o in room_lights:
                o.data.energy = base_energies[o.name]
            alert_ld.energy = 0.0
            rim_ld.energy = 0.0
            scene.view_settings.exposure = -0.14

    def reset_props():
        bed.location = (0, 0, -10)
        for obj in (plate_zzz, plate_auto, plate_20k, plate_manual):
            obj.location = (0, 0, -10)
            obj.scale = (1, 1, 1)
            obj.rotation_euler = (math.radians(90), 0, 0)
        for w in wisps:
            w.location = (0, 0, -10)
        lungs["root"].location = (0, 0, -10)
        breathe_btn["root"].location = (0, 0, -10)
        breathe_btn["cap"].location = (0, 0, 0.96)
        alex["arm"].rotation_euler = (0, 0, 0)
        set_alert_lighting(False)

    def update_state(bid: str, u: float, f: int):
        reset_props()
        t = f / 30.0
        cf.set_char_transform(alex, 0.0, 0.0, 0.0, 0.0)

        if bid == "b11_sleeping":
            bed.location = (0.0, 0.35, 0.0)
            # +90 deg X rotation maps local +Z (head) to -Y (onto the pillow!) and +Y (face) to +Z (facing up!)
            cf.set_char_transform(alex, 0.0, 1.12, 0.58, 0.0)
            alex["arm"].rotation_euler = (math.radians(90.0), 0.0, 0.0)
            cf.set_face(alex, "alex_deadpan_closed.png")
            breath = math.sin(u * math.pi * 3.0)
            cf.pose_char(alex, pelvis_z=0.02 * breath, arm_l=(8, 0, 14), arm_r=(8, 0, -14))
            plate_zzz.location = (0.28, -0.48, 0.96 + 0.06 * u)
            plate_zzz.scale = (0.80, 0.80, 0.80)
            plate_zzz.rotation_euler = (math.radians(48), math.radians(-12), math.radians(-18))
            for wi, w in enumerate(wisps):
                wu = ((t * 1.1) + wi / len(wisps)) % 1.0
                w.location = (math.sin(wu * 5 + wi) * 0.08, -0.32 + 0.12 * wu, 0.82 + 0.48 * wu)
                ws = 0.45 + 0.45 * math.sin(wu * math.pi)
                w.scale = (ws, ws, ws)
            sc.set_camera_look(cam_obj, (-0.55 + 0.25 * u, 0.75 - 0.15 * u, 1.85), (0.0, -0.15, 0.65), lens=30.0)

        elif bid == "b12_auto_force":
            cf.set_face_with_blink(alex, "alex_deadpan", f, seed=12)
            cycle = math.sin(u * math.pi * 4.0)
            exh = cycle < 0.0
            cf.pose_char(alex, pelvis_z=0.03 * cycle, torso_rot=(-5.0 * cycle, 0, 0), arm_l=(20, 0, 16 + 6 * cycle), arm_r=(20, 0, -16 - 6 * cycle))
            lungs["root"].location = (0.0, 0.0, 0.0)
            p = 1.0 + 0.18 * cycle
            lungs["l"].scale = (p, p, p)
            lungs["r"].scale = (p, p, p)
            plate_auto.location = (0.0, 0.0, 2.12)
            pc.animate_air_wisps(wisps, (0.0, 0.0, 1.48), t, speed=2.2, exhale=exh)
            if u < 0.50:
                lu = u / 0.50
                sc.set_camera_look(cam_obj, (0.25 - 0.50 * lu, 2.25 - 0.35 * lu, 1.38), (0.0, 0.0, 1.28), lens=34.0)
            else:
                lu = (u - 0.50) / 0.50
                ang = math.radians(-26 + 52 * lu)
                sc.set_camera_look(cam_obj, (math.sin(ang) * 1.85, math.cos(ang) * 1.85, 1.40), (0.0, 0.0, 1.28), lens=34.0)

        elif bid == "b13_20k_times":
            cf.set_face_with_blink(alex, "alex_focus_squint", f, seed=13)
            cycle = math.sin(u * math.pi * 8.0)
            cf.pose_char(alex, pelvis_z=0.035 * cycle, arm_l=(26, 0, 20), arm_r=(26, 0, -20))
            plate_20k.location = (0.0, 0.0, 2.15)
            pop = 0.88 + 0.12 * abs(math.sin(u * math.pi * 6.0))
            plate_20k.scale = (pop, pop, pop)
            pc.animate_air_wisps(wisps, (0.0, 0.0, 1.48), t, speed=3.6, exhale=(cycle < 0))
            sc.set_camera_look(cam_obj, (-0.55 + 1.10 * u, 2.35 - 0.40 * u, 1.48), (0.0, 0.0, 1.44), lens=32.0)

        elif bid == "b15_manual_mode":
            pulse = 0.5 + 0.5 * math.sin(u * math.pi * 8.0)
            set_alert_lighting(True, pulse)
            breathe_btn["root"].location = (0.0, 0.62, 0.0)
            plate_manual.location = (0.0, 0.0, 2.04)
            plate_manual.scale = (0.86 + 0.08 * pulse, 0.86 + 0.08 * pulse, 0.86)
            cf.set_face(alex, "alex_shocked_wide.png")
            if u < 0.45:
                lu = u / 0.45
                cf.pose_char(alex, head_rot=(-8, 0, math.sin(u * 30) * 6), arm_l=(118, -22, 24), forearm_l=(55, 0, 0), arm_r=(118, 22, -24), forearm_r=(55, 0, 0))
                kick = int(lu * 24)
                sc.set_camera_look(cam_obj, (0.15, 2.25 - 0.35 * lu, 1.48), (0.0, 0.25, 1.34), lens=30.0, roll_deg=-8.0, kick_offset=(kick if kick < 7 else -1), kick_amp=0.05)
            else:
                lu = (u - 0.45) / 0.55
                mash = max(0.0, math.sin(lu * math.pi * 4.0))
                breathe_btn["cap"].location = (0.0, 0.0, 0.96 - 0.05 * mash)
                cf.pose_char(alex, torso_rot=(16.0 * mash, 0, 0), arm_l=(86 + 22 * mash, -18, 12), forearm_l=(24, -10, 0), arm_r=(86 + 22 * mash, 18, -12), forearm_r=(24, 10, 0))
                sc.set_camera_look(cam_obj, (-0.75 + 0.25 * lu, 1.95 - 0.25 * lu, 1.18), (0.0, 0.35, 1.14), lens=28.0, roll_deg=6.0)

        elif bid == "b16_good_luck":
            pulse = 0.5 + 0.5 * math.sin(u * math.pi * 6.0)
            set_alert_lighting(True, pulse)
            breathe_btn["root"].location = (0.0, 0.58, 0.0)
            plate_manual.location = (0.0, 0.0, 2.14)
            plate_manual.scale = (0.76, 0.76, 0.76)
            cf.set_face(alex, "alex_almost_wobbly.png")
            mash = max(0.0, math.sin(u * math.pi * 6.0))
            breathe_btn["cap"].location = (0.0, 0.0, 0.96 - 0.05 * mash)
            cf.pose_char(alex, torso_rot=(10.0, 0, 0), head_rot=(4.0, 0, math.sin(u * 20) * 5.0), arm_l=(88 + 20 * mash, -18, 12), arm_r=(88 + 20 * (1 - mash), 18, -12))
            kick = int(u * 14)
            sc.set_camera_look(cam_obj, (0.08, 1.72 - 0.24 * u, 1.50), (0.0, 0.12, 1.44), lens=26.0, kick_offset=(kick if kick < 7 else -1), kick_amp=0.04)

    bedroom_beats = ["b11_sleeping", "b12_auto_force", "b13_20k_times", "b15_manual_mode", "b16_good_luck"]

    if preview_only:
        for pid in ("b11_sleeping", "b13_20k_times", "b15_manual_mode", "b16_good_luck"):
            fa, fb = sc.beat_frame_range(beats_data, pid)
            fm = (fa + fb) // 2
            u = (fm - fa) / max(1, fb - fa)
            update_state(pid, u, fm)
            sc.render_frame(scene, fm, preview_tag=f"prev_{pid}")
        return

    for bid in bedroom_beats:
        fa, fb = sc.beat_frame_range(beats_data, bid)
        print(f"[scene_bedroom] Rendering {bid}: frames {fa}..{fb}")
        for f in range(fa, fb + 1):
            u = (f - fa) / max(1, fb - fa)
            update_state(bid, u, f)
            sc.render_frame(scene, f)


if __name__ == "__main__":
    main()
