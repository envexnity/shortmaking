"""
scene_room.py — Set 2: Alex's Textured Bedroom Training Studio (True SI Scale 1 BU = 1m).
Includes: honey-oak wood planks, teal-blue brick wainscot, casement window looking onto LIVE night
town street + dancing crowd + fireworks, espresso folding table, 4-flap animated wrap sheet,
sculpted hero burgers/cat/clocks/egg-bacon/griddle/blur-arms, and Neighbor doorway party reveal.

Renders beats:
  b02_except_me, b03_huss_1, b08_preparing, b09_huss_2, b11_so_i_train, b12_5am_wrist,
  b13_200_wraps, b14_no_breakfast, b15_fold_tuck, b16_four_sec, b17_huss_3, b18_wrap_items,
  b19_wrap_cat, b20_neighbor, b21_come_out, b22_exactly, b23_huss_4, b24_fold_fast,
  b25_blur_hands, b34_only_wrap, b39_learning_cook, b40_5am_200, b41_huss_cook.
"""
import math
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


def build_room_set(scene):
    col = bpy.data.collections.new("Set_AlexRoom")
    scene.collection.children.link(col)

    m_floor = sc.make_textured_pbr("Mat_RoomFloor", sc.TEX_ENV / "wood_planks_honey.png", sc.TEX_ENV / "wood_planks_honey_bump.png", uv_scale=(0.65, 0.65, 0.65), rough_min=0.45, rough_max=0.62, coat=0.04)
    m_table = sc.make_textured_pbr("Mat_RoomTable", sc.TEX_ENV / "wood_table_espresso.png", sc.TEX_ENV / "wood_table_espresso_bump.png", uv_scale=(1.15, 1.15, 1.15), rough_min=0.42, rough_max=0.58, coat=0.05)
    m_brick = sc.make_textured_pbr("Mat_RoomBrick", sc.TEX_ENV / "brick_blue_wainscot.png", sc.TEX_ENV / "brick_blue_wainscot_bump.png", uv_scale=(1.05, 1.05, 1.05), rough_min=0.65, rough_max=0.82, coat=0.0)
    m_cream = sc.make_stylized_pbr("Mat_RoomCream", "#F5E2C8", rough=0.75, coat=0.0, bump_str=0.025)
    m_trim = sc.make_stylized_pbr("Mat_RoomTrimWht", "#F8FAFC", rough=0.42, coat=0.04)
    m_curt = sc.make_stylized_pbr("Mat_RoomCurtain", "#EA6A20", rough=0.70, coat=0.0, sheen=0.45)
    m_steel = sc.make_stylized_pbr("Mat_RoomSteel", "#94A3B8", rough=0.28, metal=0.80)
    m_beam = sc.make_stylized_pbr("Mat_RoomBeam", "#6E4224", rough=0.62, coat=0.0)

    # Bedroom shell (floor z=0, back wall w/ window at y=-1.45, left wall w/ doorway at x=-2.75)
    pf.make_bevel_box("Floor", (0, 1.2, -0.10), (7.0, 8.4, 0.20), m_floor, col, bevel_w=0.01)
    # Soft circular bedroom rug
    pf.make_smooth_cyl("Rug_Base", (0.0, 0.65, 0.008), 1.45, 0.014, sc.make_stylized_pbr("Mat_Rug", "#9CA3AF", rough=0.82, sheen=0.4), col, segs=40, bevel_w=0.004)
    pf.make_smooth_cyl("Rug_Inner", (0.0, 0.65, 0.011), 1.15, 0.014, sc.make_stylized_pbr("Mat_RugIn", "#E2D6C3", rough=0.82, sheen=0.4), col, segs=40, bevel_w=0.004)

    # Right & Ceiling & Back Wall framing big window (window opening: x in [-1.45..+1.45], z in [1.10..2.65])
    pf.make_bevel_box("Wall_R", (2.8, 0.4, 1.8), (0.20, 6.4, 3.8), m_cream, col, bevel_w=0.02)
    pf.make_bevel_box("Wall_R_Brick", (2.69, 0.4, 0.55), (0.06, 6.3, 1.10), m_brick, col, bevel_w=0.01)
    pf.make_bevel_box("Ceiling", (0, 0.4, 3.55), (7.0, 6.4, 0.20), sc.make_stylized_pbr("Mat_Ceil", "#FFF7ED", rough=0.72), col, bevel_w=0.02)
    for bx in (-1.6, 0.0, 1.6):
        pf.make_bevel_box(f"Beam_{bx}", (bx, 0.4, 3.40), (0.22, 6.2, 0.16), m_beam, col, bevel_w=0.015)

    # Back Wall (-Y = -1.45): blue brick lower wainscot + cream upper piers + white chair rail + window frame
    pf.make_bevel_box("Back_Brick", (0, -1.45, 0.55), (5.8, 0.18, 1.10), m_brick, col, bevel_w=0.01)
    pf.make_bevel_box("Back_Rail", (0, -1.35, 1.12), (5.8, 0.10, 0.07), m_trim, col, bevel_w=0.01)
    pf.make_bevel_box("Back_Top", (0, -1.45, 3.10), (5.8, 0.18, 0.90), m_cream, col, bevel_w=0.015)
    pf.make_bevel_box("Back_PierL", (-2.15, -1.45, 1.90), (1.40, 0.18, 1.60), m_cream, col, bevel_w=0.015)
    pf.make_bevel_box("Back_PierR", ( 2.15, -1.45, 1.90), (1.40, 0.18, 1.60), m_cream, col, bevel_w=0.015)
    # White multi-pane window frame & mullions
    pf.make_bevel_box("Win_Sill", (0, -1.36, 1.11), (3.05, 0.26, 0.07), m_trim, col, bevel_w=0.01)
    pf.make_bevel_box("Win_Head", (0, -1.38, 2.66), (3.05, 0.22, 0.08), m_trim, col, bevel_w=0.01)
    pf.make_bevel_box("Win_MullV", (0, -1.43, 1.88), (0.06, 0.10, 1.52), m_trim, col, bevel_w=0.006)
    pf.make_bevel_box("Win_MullH", (0, -1.43, 1.90), (2.92, 0.08, 0.05), m_trim, col, bevel_w=0.006)
    # Fluted Orange Tied-Back Curtains + Rod + Cute Potted Cactus on Sill!
    pf.make_smooth_cyl("CurtRod", (0, -1.24, 2.74), 0.022, 3.5, m_beam, col, rot=(0, math.radians(90), 0), bevel_w=0.004)
    for sx in (-1.38, 1.38):
        for fi in range(3):
            pf.make_smooth_cyl(f"Curt_{sx}_{fi}", (sx + (fi - 1) * 0.09, -1.27, 1.90), 0.075, 1.62, m_curt, col, segs=18, bevel_w=0.01)
    # Potted cactus on right windowsill
    pf.make_smooth_cyl("CactPot", (1.18, -1.34, 1.19), 0.07, 0.10, sc.make_stylized_pbr("Mat_Terra", "#C2410C", rough=0.65), col, segs=18, bevel_w=0.008)
    pf.make_smooth_cyl("CactBody", (1.18, -1.34, 1.29), 0.045, 0.15, sc.make_stylized_pbr("Mat_Cact", "#22C55E", rough=0.55), col, segs=16, bevel_w=0.02)

    # Left Wall (-X = -2.45) with Open Framed Doorway (y in [-0.75..+0.45], z in [0..2.15]) for Neighbor!
    pf.make_bevel_box("Wall_L_BrickF", (-2.45, 1.75, 0.55), (0.18, 2.6, 1.10), m_brick, col, bevel_w=0.01)
    pf.make_bevel_box("Wall_L_TopF",   (-2.45, 1.75, 2.28), (0.18, 2.6, 2.38), m_cream, col, bevel_w=0.01)
    pf.make_bevel_box("Wall_L_Back",   (-2.45, -1.20, 1.80), (0.18, 0.90, 3.60), m_cream, col, bevel_w=0.01)
    pf.make_bevel_box("Wall_L_Header", (-2.45, -0.15, 2.85), (0.18, 1.30, 1.40), m_cream, col, bevel_w=0.01)
    pf.make_bevel_box("DoorFrame_N", (-2.42, -0.76, 1.08), (0.24, 0.08, 2.16), m_trim, col, bevel_w=0.01)
    pf.make_bevel_box("DoorFrame_S", (-2.42,  0.46, 1.08), (0.24, 0.08, 2.16), m_trim, col, bevel_w=0.01)
    pf.make_bevel_box("DoorFrame_T", (-2.42, -0.15, 2.16), (0.24, 1.32, 0.08), m_trim, col, bevel_w=0.01)
    # Dark moody party hallway box behind door
    m_hall = sc.make_stylized_pbr("Mat_HallDark", "#1E163E", rough=0.75)
    pf.make_bevel_box("Hall_Back", (-3.95, -0.15, 1.6), (0.20, 3.2, 3.4), m_hall, col, bevel_w=0.01)
    pf.make_bevel_box("Hall_Floor", (-3.25, -0.15, -0.05), (1.8, 3.2, 0.12), m_floor, col, bevel_w=0.01)

    # Hanging Warm Pendant Lamp Dome at top of room
    pf.make_smooth_cyl("LampCord", (0, 0.55, 3.10), 0.012, 0.85, sc.make_stylized_pbr("Mat_Cord", "#1E293B"), col, segs=12, bevel_w=0)
    pf.make_smooth_sphere("LampShade", (0, 0.55, 2.66), (0.26, 0.26, 0.14), sc.make_stylized_pbr("Mat_LampShade", "#F59E0B", rough=0.30, emit_hex="#FEF08A", emit_str=1.8), col, segs=24)

    # ==================== OUTSIDE PARTY STREET VISIBLE THROUGH WINDOW (-Y = -2.8 .. -8.0) ====================
    pf.make_bevel_box("Out_Street", (0, -4.5, -0.10), (14, 5.0, 0.20), sc.make_textured_pbr("Mat_OutAsph", sc.TEX_ENV / "asphalt_speckled.png", uv_scale=(0.5, 0.5, 0.5)), col)
    pf.build_townhouse("Out_HouseL", (-2.8, -6.8, 0.0), col, 2.6, 2.2, 3.4, "#93C5FD", "#DC2626", is_night=True)
    pf.build_townhouse("Out_HouseR", ( 2.8, -6.8, 0.0), col, 2.6, 2.2, 3.6, "#C4B5FD", "#0F766E", is_night=True)
    pcols = ["#EF4444", "#FACC15", "#38BDF8", "#EC4899", "#A855F7", "#22C55E"]
    for i in range(10):
        lx = -2.2 + i * 0.48
        lz = 2.45 - 0.22 * math.sin((i / 9.0) * math.pi)
        c_hex = pcols[i % len(pcols)]
        pf.make_smooth_sphere(f"WinBulb_{i}", (lx, -2.55, lz), (0.075, 0.075, 0.075), sc.make_stylized_pbr(f"Mat_WB_{c_hex}", c_hex, emit_hex=c_hex, emit_str=6.5), col, segs=12)
    for fi, (fx, fy, fz, fcol) in enumerate([(-1.2, -6.5, 2.45, "#F472B6"), (0.0, -6.8, 2.55, "#FACC15"), (1.1, -6.5, 2.40, "#38BDF8")]):
        m_fw = sc.make_stylized_pbr(f"Mat_WinFW_{fcol}", fcol, emit_hex=fcol, emit_str=11.0)
        for ray in range(8):
            ang = ray * (math.pi / 4.0)
            pf.make_smooth_sphere(f"WinFW_{fi}_{ray}", (fx + math.cos(ang) * 0.34, fy, fz + math.sin(ang) * 0.34), (0.055, 0.055, 0.055), m_fw, col, segs=8)

    # ==================== TRAINING FOLDING TABLE (y=0.60, top at z=0.72m) ====================
    pf.make_bevel_box("TableTop", (0.0, 0.60, 0.695), (2.25, 0.84, 0.05), m_table, col, bevel_w=0.012, segs=3)
    for lx in (-0.98, 0.98):
        for ly in (0.28, 0.92):
            pf.make_smooth_cyl(f"TLeg_{lx}_{ly}", (lx, ly, 0.34), 0.022, 0.68, m_steel, col, segs=16, bevel_w=0.003)

    # Animated 4-Flap Wrapping Paper Sheet at center of table (0.0, 0.56, 0.722)
    wrap_sheet = pf.build_animated_wrap_sheet("Prop_WrapSheet", (0.0, 0.56, 0.722), col, scale=1.05)

    # Center Gourmet Hero Burger & Wrapped Burger (on table top z=0.726)
    center_burger = pf.build_hero_burger("CenterBurger", (0.0, 0.56, 0.732), col, scale=0.92)
    center_wrapped = pf.build_wrapped_burger("CenterWrapped", (0.0, 0.56, 0.732), col, scale=0.95)

    # Left Stack of Unwrapped Burgers (viewer right +X = Alex's left, matching OG!)
    for i in range(4):
        pf.build_hero_burger(f"UnwrapStack_{i}", (0.82, 0.58, 0.72 + i * 0.18), col, scale=0.84)

    # Right Towering Stacks of Wrapped Burgers (viewer left -X = Alex's right, rising up!)
    wrapped_towers = []
    for tier in range(8):
        for cx, cy in [(-0.56, 0.48), (-0.86, 0.48), (-0.70, 0.74)]:
            wb = pf.build_wrapped_burger(f"TowerWB_{tier}_{cx:.2f}", (cx, cy, 0.72 + tier * 0.140), col, scale=0.86)
            wrapped_towers.append((tier, wb))

    # Hero Clocks (5AM Teal Alarm Clock + Red Stopwatch)
    alarm_clock = pf.build_hero_clock("Alarm_5AM", (0.56, 0.76, 0.72), col, is_alarm=True, scale=0.95)
    stopwatch = pf.build_hero_clock("Stopwatch_Red", (-0.38, 0.76, 0.72), col, is_alarm=False, scale=0.95)

    # Breakfast Plate, Blue Plate, Sculpted Cozy Cat, Cast-Iron Griddle + Cooked Tower, Speed-Blur Ghost Arms
    breakfast = pf.build_hero_breakfast("Prop_Breakfast", (0.0, 0.56, 0.732), col)
    blue_plate = pf.make_smooth_cyl("Prop_BluePlate", (0.0, 0.56, 0.742), 0.21, 0.022, sc.make_stylized_pbr("Mat_PlateBlue", "#2563EB", rough=0.16, coat=0.55), col, segs=40, bevel_w=0.008)
    cat_prop = pf.build_hero_cat("Prop_NeighborCat", (0.0, 0.58, 0.722), col, scale=1.05)

    griddle_info = pf.build_hero_griddle("Prop_Griddle", (0.0, 0.56, 0.722), col)
    m_patty = sc.make_stylized_pbr("Mat_HB_Patty", "#592A16", rough=0.58, bump_str=0.06)
    patty_tower = []
    for pi in range(20):
        pt = pf.make_smooth_cyl(f"CookedPatty_{pi}", (-0.54, 0.58, 0.74 + pi * 0.044), 0.13, 0.042, m_patty, col, segs=28, bevel_w=0.012)
        patty_tower.append(pt)

    blur_fx = pf.build_blur_hands_fx("Prop_BlurHands", (0.0, 0.42, 0.94), col)

    return {
        "wrap_sheet": wrap_sheet,
        "center_burger": center_burger,
        "center_wrapped": center_wrapped,
        "wrapped_towers": wrapped_towers,
        "alarm_clock": alarm_clock,
        "stopwatch": stopwatch,
        "breakfast": breakfast,
        "blue_plate": blue_plate,
        "cat_prop": cat_prop,
        "griddle": griddle_info,
        "patty_tower": patty_tower,
        "blur_fx": blur_fx,
    }


def setup_room_lights(scene):
    lcol = bpy.data.collections.new("Room_Lights")
    scene.collection.children.link(lcol)
    sc.setup_stylized_sky_world(scene, "night", strength=0.35)

    # Stylized Warm Indoor Cozy Key vs Cool Indigo Window Rim! (Balanced so shirt & face never bloom!)
    lights = [
        ("Room_PendantKey", (0.2, 1.35, 2.45), (0.0, 0.25, 1.15), 145.0, 2.2, 3800, 78),
        ("Room_FrontFill",  (-1.4, 2.45, 1.85), (0.0, 0.15, 1.25), 68.0, 2.8, 5200, 100),
        ("Room_WinRim",     (0.0, -3.20, 2.65), (0.0, 0.10, 1.45), 290.0, 2.5, 7600, 70),
        ("Room_PartyOut",   (0.0, -4.00, 2.40), (0.0, -3.5, 0.80), 220.0, 3.0, 3400, 105),
    ]
    for nm, loc, tgt, en, sz, temp, spr in lights:
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


def main():
    preview_only = "--preview" in sys.argv
    bcl.clear_scene()
    scene = bpy.context.scene
    res = (1080, 1920) if preview_only else (720, 1280)
    sc.configure_stylized_eevee(scene, res_x=res[0], res_y=res[1], samples=(16 if preview_only else 12), raytracing=True, fast_gi=True, motion_blur=False, exposure=-0.16)

    beats_data = sc.load_beats()
    props = build_room_set(scene)
    setup_room_lights(scene)

    cast_col = bpy.data.collections.new("Room_Cast")
    scene.collection.children.link(cast_col)

    alex = cf.create_character("alex", "Alex", cast_col)
    cf.set_char_transform(alex, 0.0, -0.05, 0.0, 0.0)

    neighbor = cf.create_character("neighbor", "Neighbor", cast_col)
    cf.set_char_transform(neighbor, -2.1, -0.15, 0.0, -90.0)

    # Live Dancing Party Crowd outside bedroom window!
    out_crowd = []
    for idx, (kind, hat, ox, oy) in enumerate([
        ("teal_friend", "#FACC15", -1.15, -3.4),
        ("mint_girl", "#38BDF8", -0.35, -3.6),
        ("purple_hoodie", "#EC4899", 0.45, -3.5),
        ("grandma", "#22C55E", 1.20, -3.7),
    ]):
        c = cf.create_character(kind, f"OutCrowd_{idx}", cast_col, party_hat=hat)
        cf.set_char_transform(c, ox, oy, 0.0, 0.0)
        out_crowd.append(c)

    cam_d = bpy.data.cameras.new("Cam_Room")
    cam = bpy.data.objects.new("Cam_Room", cam_d)
    scene.collection.objects.link(cam)
    scene.camera = cam

    bcl.setup_cinema_compositor(
        scene, glare_threshold=1.65, glare_strength=0.10, dispersion=0.0009,
        lift_rgb=(0.988, 0.992, 1.012), gamma_rgb=(1.0, 1.0, 1.0), gain_rgb=(1.01, 1.005, 0.99),
        vignette=0.14,
    )

    room_beats = [
        "b02_except_me", "b03_huss_1", "b08_preparing", "b09_huss_2",
        "b11_so_i_train", "b12_5am_wrist", "b13_200_wraps", "b14_no_breakfast",
        "b15_fold_tuck", "b16_four_sec", "b17_huss_3", "b18_wrap_items",
        "b19_wrap_cat", "b20_neighbor", "b21_come_out", "b22_exactly",
        "b23_huss_4", "b24_fold_fast", "b25_blur_hands", "b34_only_wrap",
        "b39_learning_cook", "b40_5am_200", "b41_huss_cook",
    ]
    preview_keep = {"b02_except_me", "b03_huss_1", "b14_no_breakfast", "b19_wrap_cat", "b21_come_out", "b25_blur_hands", "b40_5am_200"}

    for bid in room_beats:
        binfo = sc.beat_info(beats_data, bid)
        f0, f1 = sc.beat_frame_range(beats_data, bid)
        is_pov = bid in ("b03_huss_1", "b09_huss_2", "b14_no_breakfast", "b15_fold_tuck", "b17_huss_3", "b23_huss_4", "b34_only_wrap")
        is_cook = bid in ("b34_only_wrap", "b39_learning_cook", "b40_5am_200", "b41_huss_cook")
        is_huss = "huss" in bid
        cf.set_pov_arms_only(alex, is_pov)

        # Toggle props cleanly per beat
        sc.set_hidden_tree(props["wrap_sheet"]["root"], is_cook and bid != "b34_only_wrap")
        sc.set_hidden_tree(props["center_burger"], bid in ("b14_no_breakfast", "b19_wrap_cat", "b21_come_out", "b34_only_wrap", "b39_learning_cook", "b40_5am_200", "b41_huss_cook"))
        sc.set_hidden_tree(props["center_wrapped"], True)
        sc.set_hidden_tree(props["breakfast"], bid != "b14_no_breakfast")
        props["blue_plate"].hide_viewport = True
        props["blue_plate"].hide_render = True
        sc.set_hidden_tree(props["cat_prop"], bid != "b19_wrap_cat")
        sc.set_hidden_tree(props["alarm_clock"], bid not in ("b12_5am_wrist", "b13_200_wraps", "b40_5am_200"))
        sc.set_hidden_tree(props["stopwatch"], bid not in ("b02_except_me", "b08_preparing", "b11_so_i_train", "b15_fold_tuck", "b16_four_sec", "b18_wrap_items", "b22_exactly", "b24_fold_fast", "b25_blur_hands"))
        sc.set_hidden_tree(props["griddle"]["root"], not is_cook)
        for pt in props["patty_tower"]:
            pt.hide_viewport = (bid not in ("b40_5am_200", "b41_huss_cook"))
            pt.hide_render = (bid not in ("b40_5am_200", "b41_huss_cook"))
        sc.set_hidden_tree(props["blur_fx"], bid != "b25_blur_hands")
        sc.set_hidden_tree(neighbor["arm"], bid != "b21_come_out")

        # Progressive wrapped tower growth!
        bi_num = binfo["index"]
        max_tier = 1 if bi_num <= 8 else (3 if bi_num <= 13 else (5 if bi_num <= 18 else (8 if bi_num <= 25 else 0)))
        for tier, wb in props["wrapped_towers"]:
            hide_wb = (tier >= max_tier) or is_cook
            sc.set_hidden_tree(wb, hide_wb)

        # Hit frames for HUSS! sync
        huss_frames = [int(round(ht * 30.0)) + 1 for ht in binfo.get("huss_hit_times", [])]

        frames_to_render = [(f0 + f1) // 2] if preview_only else list(range(f0, f1 + 1))
        for f in frames_to_render:
            if preview_only and bid not in preview_keep:
                continue
            u = (f - f0) / max(1, (f1 - f0))
            t = f / 30.0

            # Animate outside window party crowd
            for oi, oc in enumerate(out_crowd):
                cf.animate_party_dance(oc, t, phase=oi * 1.1, energy=1.0)
            if bid == "b20_neighbor":
                cf.set_char_transform(neighbor, 0.35, -3.1, 0.0, 0.0)
                sc.set_hidden_tree(neighbor["arm"], False)
                cf.animate_party_dance(neighbor, t, phase=0.2, energy=1.15)
            elif bid == "b21_come_out":
                # Party Neighbor leaning into Alex's bedroom doorway!
                cf.set_char_transform(neighbor, -2.05, -0.10, 0.0, -72.0)
                cf.pose_char(
                    neighbor,
                    pelvis_z=0.04 * abs(math.sin(t * 7.0)),
                    torso_rot=(6, 0, -10),
                    head_rot=(-4, 0, 8 + 6 * math.sin(t * 6.0)),
                    arm_l=(125 + 22 * math.sin(t * 9.0), 0, -24),
                    forearm_l=(20, 0, 0),
                    arm_r=(55, 0, 15),
                    forearm_r=(45, 0, 0),
                )

            # Default Alex transform behind table
            cf.set_char_transform(alex, 0.0, -0.05, 0.0, 0.0)
            pf.set_wrap_fold(props["wrap_sheet"], 0.0, 0.0)

            kick_off = -1
            if is_huss and huss_frames:
                # Find closest past huss hit frame
                diffs = [f - hf for hf in huss_frames if f >= hf]
                if diffs:
                    kick_off = min(diffs)

            if bid in ("b02_except_me", "b08_preparing", "b11_so_i_train"):
                cf.set_face_with_blink(alex, "alex_determined", f, seed=1)
                slam = abs(math.sin(t * 10.0))
                cf.pose_char(
                    alex,
                    torso_rot=(8, 0, 0),
                    head_rot=(6, 0, 0),
                    arm_l=(52 + 12 * slam, -24, -10),
                    forearm_l=(32 + 10 * slam, -12, 0),
                    arm_r=(52 + 12 * slam, 24, 10),
                    forearm_r=(32 + 10 * slam, 12, 0),
                )
                sc.set_camera_look(cam, (0.0, 2.35 - 0.18 * u, 1.38), (0.0, 0.25, 1.12), lens=36.0, fstop=3.2)

            elif is_pov and is_huss:
                # Top-down POV rapid folding! Place Alex closer & lower, tilt blocky arms inward onto wrap sheet flaps!
                cf.set_char_transform(alex, 0.0, 0.12, -0.15, 0.0)
                pulse = 0.5 + 0.5 * math.sin(t * 28.0)
                cf.pose_char(
                    alex,
                    torso_rot=(0, 0, 0),
                    arm_l=(48 + 4 * pulse, -26 - 8 * pulse, 0),
                    forearm_l=(12 + 14 * pulse, -14, 0),
                    arm_r=(48 + 4 * pulse, 26 + 8 * pulse, 0),
                    forearm_r=(12 + 14 * pulse, 14, 0),
                )
                pf.set_wrap_fold(props["wrap_sheet"], 0.35 + 0.45 * pulse, 0.20 + 0.35 * (1.0 - pulse))
                if u > 0.65:
                    sc.set_hidden_tree(props["center_burger"], True)
                    sc.set_hidden_tree(props["center_wrapped"], False)
                sc.set_camera_look(cam, (0.0, 0.10, 1.54 - 0.05 * u), (0.0, 0.58, 0.74), lens=24.0, fstop=4.0, kick_offset=kick_off, kick_amp=0.025)

            elif bid == "b12_5am_wrist":
                cf.set_face_with_blink(alex, "alex_determined", f, seed=2)
                cf.pose_char(
                    alex,
                    torso_rot=(4, 0, 0),
                    head_rot=(4, 0, 0),
                    arm_l=(82, 0, -12),
                    forearm_l=(32 * math.sin(t * 14.0), 0, 24),
                    arm_r=(82, 0, 12),
                    forearm_r=(-32 * math.sin(t * 14.0), 0, -24),
                )
                sc.set_camera_look(cam, (0.28, 2.05 - 0.16 * u, 1.38), (0.10, 0.15, 1.24), lens=42.0, fstop=3.0)

            elif bid == "b13_200_wraps":
                cf.set_face_with_blink(alex, "alex_focus_squint", f, seed=3)
                wob = math.sin(t * 22.0)
                cf.pose_char(alex, torso_rot=(8, 0, 0), arm_l=(54 + 10 * wob, -24, -10), forearm_l=(34, -12, 0), arm_r=(54 - 10 * wob, 24, 10), forearm_r=(34, 12, 0))
                sc.set_camera_look(cam, (-0.35 + 0.15 * u, 2.35, 1.42), (-0.15, 0.25, 1.12), lens=35.0, fstop=3.2)

            elif bid == "b14_no_breakfast":
                cf.set_char_transform(alex, 0.0, 0.12, -0.15, 0.0)
                cf.pose_char(alex, torso_rot=(0, 0, 0), arm_l=(48, -26, 0), forearm_l=(12 + 12 * u, -14, 0), arm_r=(48, 26, 0), forearm_r=(12 + 12 * u, 14, 0))
                pf.set_wrap_fold(props["wrap_sheet"], max(0.0, (u - 0.45) * 1.4), 0.0)
                sc.set_camera_look(cam, (0.0, 0.10, 1.54 - 0.05 * u), (0.0, 0.58, 0.74), lens=24.0, fstop=4.0)

            elif bid == "b15_fold_tuck":
                cf.set_char_transform(alex, 0.0, 0.12, -0.15, 0.0)
                u_lr = min(1.0, u * 1.8)
                u_fb = max(0.0, min(1.0, (u - 0.45) * 1.9))
                pf.set_wrap_fold(props["wrap_sheet"], u_lr, u_fb)
                cf.pose_char(alex, torso_rot=(0, 0, 0), arm_l=(48, -26 - 8 * u, 0), forearm_l=(14 + 12 * u, -14, 0), arm_r=(48, 26 + 8 * u, 0), forearm_r=(14 + 12 * u, 14, 0))
                if u > 0.78:
                    sc.set_hidden_tree(props["center_burger"], True)
                    sc.set_hidden_tree(props["center_wrapped"], False)
                sc.set_camera_look(cam, (0.0, 0.10, 1.54 - 0.05 * u), (0.0, 0.58, 0.74), lens=24.0, fstop=4.0)

            elif bid == "b16_four_sec":
                cf.set_face_with_blink(alex, "alex_determined", f, seed=4)
                cf.pose_char(alex, torso_rot=(8, 0, 0), head_rot=(12, 0, -14), arm_l=(52, -22, -10), forearm_l=(36, -10, 0), arm_r=(52, 22, 10), forearm_r=(36, 10, 0))
                sc.set_camera_look(cam, (-0.38, 1.95 - 0.15 * u, 1.25), (-0.18, 0.25, 1.05), lens=38.0, fstop=2.8)

            elif bid == "b18_wrap_items":
                cf.set_face_with_blink(alex, "alex_deadpan", f, seed=5)
                is_plate = u > 0.50
                sc.set_hidden_tree(props["center_burger"], is_plate)
                props["blue_plate"].hide_viewport = not is_plate
                props["blue_plate"].hide_render = not is_plate
                cf.pose_char(alex, torso_rot=(6, 0, 0), arm_l=(54, -22, -10), forearm_l=(34, -10, 0), arm_r=(54, 22, 10), forearm_r=(34, 10, 0))
                sc.set_camera_look(cam, (0.18 - 0.18 * u, 2.25, 1.38), (0.0, 0.28, 1.06), lens=36.0, fstop=3.2)

            elif bid == "b19_wrap_cat":
                cf.set_face_with_blink(alex, "alex_deadpan", f, seed=6)
                cf.pose_char(alex, torso_rot=(2, 0, 0), head_rot=(6, 0, 0), arm_l=(44, -24, -8), forearm_l=(32, -8, 0), arm_r=(44, 24, 8), forearm_r=(32, 8, 0))
                sc.set_camera_look(cam, (0.0, 2.05 - 0.16 * u, 1.34), (0.0, 0.35, 1.15), lens=38.0, fstop=2.8)

            elif bid == "b20_neighbor":
                cf.set_face_with_blink(alex, "alex_deadpan", f, seed=7)
                cf.pose_char(alex, head_rot=(-4, 0, 18), arm_l=(44, -18, -8), forearm_l=(32, -8, 0), arm_r=(44, 18, 8), forearm_r=(32, 8, 0))
                sc.set_camera_look(cam, (0.55, 2.15, 1.46), (0.20, -1.6, 1.32), lens=38.0, fstop=3.5)

            elif bid == "b21_come_out":
                sc.set_camera_look(cam, (-0.25, 1.95 - 0.18 * u, 1.28), (-2.05, -0.10, 1.22), lens=36.0, fstop=3.0)

            elif bid == "b22_exactly":
                cf.set_face_with_blink(alex, "alex_determined", f, seed=8)
                cf.pose_char(alex, torso_rot=(6, 0, 0), head_rot=(4, 0, 0), arm_l=(56, -22, -10), forearm_l=(36, -12, 0), arm_r=(56, 22, 10), forearm_r=(36, 12, 0))
                sc.set_camera_look(cam, (0.0, 2.05 - 0.22 * u, 1.40), (0.0, 0.15, 1.32), lens=42.0, fstop=3.0)

            elif bid == "b24_fold_fast":
                cf.set_face_with_blink(alex, "alex_determined", f, seed=9)
                fl = math.sin(t * 36.0)
                cf.pose_char(alex, torso_rot=(8, 0, 0), arm_l=(58 + 16 * fl, -24, -10), forearm_l=(38, -12, 0), arm_r=(58 - 16 * fl, 24, 10), forearm_r=(38, 12, 0))
                sc.set_camera_look(cam, (0.0, 2.15 - 0.20 * u, 1.38), (0.0, 0.25, 1.12), lens=36.0, fstop=3.2)

            elif bid == "b25_blur_hands":
                # Expressive wide shocked eyes CLEARLY unobstructed while blocky forearms & ghost arms blur below!
                cf.set_face(alex, "alex_shocked_wide.png")
                fl = math.sin(t * 48.0)
                cf.pose_char(alex, torso_rot=(4, 0, 0), head_rot=(-4, 0, 0), arm_l=(62 + 16 * fl, -26, -10), forearm_l=(40, -14, 0), arm_r=(62 - 16 * fl, 26, 10), forearm_r=(40, 14, 0))
                props["blur_fx"].rotation_euler = (0, 0, math.sin(t * 42.0) * 0.22)
                sc.set_camera_look(cam, (0.0, 1.98 - 0.16 * u, 1.38), (0.0, 0.20, 1.24), lens=40.0, fstop=3.2)

            elif bid == "b34_only_wrap":
                cf.set_char_transform(alex, 0.0, 0.12, -0.15, 0.0)
                pf.set_wrap_fold(props["wrap_sheet"], min(0.85, u * 1.1), 0.0)
                cf.pose_char(alex, torso_rot=(0, 0, 0), arm_l=(48, -26 - 8 * u, 0), forearm_l=(14 + 12 * u, -14, 0), arm_r=(48, 26 + 8 * u, 0), forearm_r=(14 + 12 * u, 14, 0))
                sc.set_camera_look(cam, (0.0, 0.10, 1.54 - 0.05 * u), (0.0, 0.58, 0.74), lens=24.0, fstop=4.0)

            elif bid in ("b39_learning_cook", "b40_5am_200", "b41_huss_cook"):
                cf.set_face_with_blink(alex, "alex_determined", f, seed=11)
                flip_u = (t * 2.5) % 1.0
                props["griddle"]["patty"].location.z = 0.088 + 0.14 * max(0.0, math.sin(flip_u * math.pi))
                props["griddle"]["patty"].rotation_euler = (flip_u * math.pi * 2.0, 0, 0)
                props["griddle"]["spatula"].location = (-0.22, -0.02, 0.22 + 0.06 * math.sin(flip_u * math.pi))
                props["griddle"]["spatula"].rotation_euler = (0.0, math.radians(-12), math.radians(-18))
                for si, sp in enumerate(props["griddle"]["steam"]):
                    sp.location.z = 0.15 + ((t * 0.35 + si * 0.33) % 1.0) * 0.28
                cf.pose_char(alex, torso_rot=(8, 0, 0), head_rot=(8, 0, 0), arm_l=(54 + 14 * math.sin(t * 14.0), -20, -10), forearm_l=(36, -10, 0), arm_r=(52, 16, 10), forearm_r=(34, 10, 0))
                sc.set_camera_look(cam, (0.25 - 0.15 * u, 2.25 - 0.14 * u, 1.38), (0.0, 0.25, 1.08), lens=36.0, fstop=3.2, kick_offset=kick_off, kick_amp=0.03)

            if preview_only:
                sc.render_frame(scene, f, preview_tag=f"room_{bid}")
                break
            else:
                sc.render_frame(scene, f)


if __name__ == "__main__":
    main()
