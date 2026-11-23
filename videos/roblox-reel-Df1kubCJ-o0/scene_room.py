"""
scene_room.py — Set 2: Alex's Bedroom Training Studio (with Live Window Party Crowd,
Top-Down POV Wrap Table, Breakfast Plate, Neighbor's Cat, Noob at Window/Door,
Hyper-Speed Blur Hands, and Sizzling Grill + 200-Patty Tower).

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

PROJ_DIR = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking\videos\roblox-reel-Df1kubCJ-o0")
sys.path.insert(0, str(PROJ_DIR))
import scene_common as sc
import blender_cinema_lib as bcl


def set_hidden_tree(obj, hide: bool):
    obj.hide_viewport = hide
    obj.hide_render = hide
    for ch in obj.children:
        set_hidden_tree(ch, hide)


def build_room_set(scene):
    col = bpy.data.collections.new("Set_AlexRoom")
    scene.collection.children.link(col)

    def box(name, loc, scale, hex_col, rough=0.50, metal=0.0, coat=0.10, emit_hex=None, emit_str=0.0, parent=None):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
        o = sc._link_only(bpy.context.active_object, col)
        o.name = name
        o.scale = scale
        o.data.materials.append(sc.make_mat(f"Mat_R_{name[:10]}_{hex_col}", hex_col, rough=rough, metal=metal, coat=coat, emit_hex=emit_hex, emit_str=emit_str))
        if parent:
            o.parent = parent
        return o

    # Warm wooden floor & cream bedroom walls
    box("Floor",    (0,  0.0, -0.25), (20, 18, 0.5), "#9A6238", rough=0.45, coat=0.18)
    box("Wall_L",   (-8, 0.0,  5.0),  (0.5, 18, 11), "#FDE8CD", rough=0.65)
    box("Wall_R",   ( 8, 0.0,  5.0),  (0.5, 18, 11), "#FDE8CD", rough=0.65)
    box("Ceiling",  (0,  0.0, 10.5),  (20, 18, 0.5), "#FFF7ED", rough=0.70)

    # Back Wall (-Y = -4.0) with LARGE OPEN WINDOW framing the partying crowd outside!
    box("BackWall_Bot", (0, -4.0, 1.4),  (16.5, 0.4, 2.8), "#38BDF8", rough=0.55)  # Blue wainscot below window
    box("BackWall_Top", (0, -4.0, 8.8),  (16.5, 0.4, 3.0), "#FDE8CD", rough=0.65)
    box("BackWall_L",   (-6.0, -4.0, 5.0), (4.5, 0.4, 6.0), "#FDE8CD", rough=0.65)
    box("BackWall_R",   ( 6.0, -4.0, 5.0), (4.5, 0.4, 6.0), "#FDE8CD", rough=0.65)
    # White window frame & center mullion
    box("WinSill",  (0, -3.82, 2.82), (8.4, 0.55, 0.22), "#F8FAFC", rough=0.35)
    box("WinTop",   (0, -3.85, 7.30), (8.4, 0.45, 0.22), "#F8FAFC", rough=0.35)
    box("WinBarV",  (0, -3.95, 5.05), (0.18, 0.25, 4.5), "#F8FAFC", rough=0.35)
    # Warm Orange Curtains flanking window
    box("Curtain_L", (-3.85, -3.60, 5.15), (0.95, 0.42, 4.8), "#F97316", rough=0.72)
    box("Curtain_R", ( 3.85, -3.60, 5.15), (0.95, 0.42, 4.8), "#F97316", rough=0.72)

    # Bedroom Doorway on Left Wall (-X = -5.5, Y = -2.0) for Noob ("Come out, he says!")
    box("DoorFrame", (-7.65, 1.5, 3.3), (0.35, 3.6, 6.6), "#F8FAFC", rough=0.45)
    box("DoorOpen",  (-7.95, 1.5, 3.3), (0.20, 3.1, 6.2), "#1E1B4B", rough=0.65)  # Dark party hallway behind Noob!

    # Outside Party Backdrop behind the window (-Y = -7 to -14)
    box("Out_Ground", (0, -10.5, -0.25), (28, 14, 0.5), "#334155", rough=0.75)
    # Colorful party string lights + night fireworks outside window
    pcols = ["#EF4444", "#FACC15", "#38BDF8", "#EC4899", "#A855F7", "#22C55E"]
    for i in range(10):
        lx = -5.5 + i * 1.25
        c_hex = pcols[i % len(pcols)]
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=0.22, location=(lx, -6.5, 6.5 - 0.5 * math.sin(i * 0.4)))
        b = sc._link_only(bpy.context.active_object, col)
        b.data.materials.append(sc.make_mat(f"Mat_OutBulb_{c_hex}", c_hex, emit_hex=c_hex, emit_str=6.0))
    # Fireworks stars visible through window
    for fx, fz, fcol in [(-2.6, 6.4, "#F472B6"), (0.2, 6.8, "#FACC15"), (2.8, 6.3, "#38BDF8")]:
        for k in range(8):
            ang = k * (math.pi / 4.0)
            bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.14, location=(fx + math.cos(ang)*0.75, -10.5, fz + math.sin(ang)*0.75))
            sp = sc._link_only(bpy.context.active_object, col)
            sp.data.materials.append(sc.make_mat(f"Mat_WinFW_{fcol}", fcol, emit_hex=fcol, emit_str=10.0))

    # ==================== TRAINING TABLE (Y = +1.8, Top at Z = 2.0) ====================
    box("TableTop",   (0.0, 1.85, 1.92), (6.4, 2.3, 0.16), "#7C4A22", rough=0.42, coat=0.15)
    for lx in (-2.9, 2.9):
        for ly in (0.95, 2.75):
            box(f"TLeg_{lx}_{ly}", (lx, ly, 0.95), (0.14, 0.14, 1.90), "#64748B", rough=0.35, metal=0.6)

    # Yellow wrapping paper sheet in center of table (with red stripe!)
    wrap_sheet = bpy.data.objects.new("Prop_WrapSheet", None)
    wrap_sheet.location = (0.0, 1.75, 2.02)
    col.objects.link(wrap_sheet)
    box("Sheet_Base",   (0, 0, 0.01), (1.75, 1.55, 0.025), "#FDE047", rough=0.55, parent=wrap_sheet)
    box("Sheet_Stripe", (0, 0, 0.025), (1.76, 0.18, 0.015), "#E11D48", rough=0.50, parent=wrap_sheet)

    # Center active unwrapped burger + center wrapped burger (for instant swap during wrap!)
    center_burger = sc.build_burger("CenterBurger", (0.0, 1.75, 2.03), col, scale=0.95)
    center_wrapped = sc.build_wrapped_burger("CenterWrapped", (0.0, 1.75, 2.03), col, scale=0.98)

    # Left stack of unwrapped burgers ready to wrap
    for i in range(4):
        sc.build_burger(f"LeftStackB_{i}", (2.45, 1.80, 2.01 + i * 0.48), col, scale=0.88)

    # Right growing GIANT TOWERS of yellow-wrapped burgers (24 wrapped burgers across 3 columns!)
    wrapped_towers = []
    tower_coords = [(-1.45, 1.60), (-2.25, 1.60), (-1.85, 2.25)]
    for tier in range(8):
        for cx, cy in tower_coords:
            wb = sc.build_wrapped_burger(f"TowerWB_{tier}_{cx:.1f}", (cx, cy, 2.01 + tier * 0.43), col, scale=0.90)
            wrapped_towers.append((tier, wb))

    # Alarm Clock (5:00 AM) + Stopwatch
    alarm_clock = sc.build_clock("AlarmClock_5AM", (1.65, 2.35, 2.01), col, scale=1.05, color_hex="#14B8A6")
    stopwatch = sc.build_clock("Stopwatch_Red", (-1.15, 2.35, 2.01), col, scale=0.95, color_hex="#EF4444")

    # Breakfast Plate (Fried Egg + 2 Bacon Strips!)
    breakfast = bpy.data.objects.new("Prop_Breakfast", None)
    breakfast.location = (0.0, 1.75, 2.04)
    col.objects.link(breakfast)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.62, depth=0.06, location=(0, 0, 0.03))
    pl = sc._link_only(bpy.context.active_object, col)
    pl.data.materials.append(sc.make_mat("Mat_PlateWhite", "#F8FAFC", rough=0.22, coat=0.35))
    pl.parent = breakfast
    bpy.ops.mesh.primitive_cylinder_add(vertices=18, radius=0.30, depth=0.04, location=(-0.12, 0.05, 0.07))
    ew = sc._link_only(bpy.context.active_object, col)
    ew.data.materials.append(sc.make_mat("Mat_EggWhite", "#FFFBEB", rough=0.35))
    ew.parent = breakfast
    bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=10, radius=0.14, location=(-0.12, 0.05, 0.09))
    ey = sc._link_only(bpy.context.active_object, col)
    ey.scale = (1.0, 1.0, 0.55)
    ey.data.materials.append(sc.make_mat("Mat_EggYolk", "#F59E0B", rough=0.20, coat=0.4))
    ey.parent = breakfast
    for bx in (0.20, 0.34):
        box(f"Bacon_{bx}", (bx, 0.0, 0.08), (0.10, 0.65, 0.03), "#B91C1C", rough=0.35, parent=breakfast)

    # Blue Plate prop (b18 "I wrap the plate")
    blue_plate = bpy.data.objects.new("Prop_BluePlate", None)
    blue_plate.location = (0.0, 1.75, 2.04)
    col.objects.link(blue_plate)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.62, depth=0.07, location=(0, 0, 0.035))
    bp = sc._link_only(bpy.context.active_object, col)
    bp.data.materials.append(sc.make_mat("Mat_PlateBlue", "#2563EB", rough=0.22, coat=0.35))
    bp.parent = blue_plate

    # Neighbor's Cozy Wrapped Cat (b19 "I wrap my neighbor's cat. The cat is fine. The cat is warm.")
    cat_prop = sc.build_cat("Prop_NeighborCat", (0.0, 1.85, 2.01), col, wrapped=True)

    # Black Flat-Top Griddle + Sizzling Raw Patty + Towering Cooked Patty Stack + Spatula!
    grill_root = bpy.data.objects.new("Prop_GrillSetup", None)
    grill_root.location = (0.0, 1.75, 2.02)
    col.objects.link(grill_root)
    box("GriddleBase", (0.0, 0.0, 0.08), (2.4, 1.55, 0.16), "#1E293B", rough=0.30, metal=0.65, parent=grill_root)
    box("GriddleHot",  (0.0, 0.0, 0.17), (2.15, 1.32, 0.03), "#0F172A", rough=0.22, metal=0.80, parent=grill_root)
    bpy.ops.mesh.primitive_cylinder_add(vertices=18, radius=0.40, depth=0.14, location=(0.0, 0.0, 0.25))
    patty_active = sc._link_only(bpy.context.active_object, col)
    patty_active.name = "Grill_FlipPatty"
    patty_active.data.materials.append(sc.make_mat("Mat_GrillPatty", "#5C2C16", rough=0.45))
    patty_active.parent = grill_root

    # Towering 200-Patty cooked stack on right of griddle!
    patty_tower = []
    for pi in range(22):
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.40, depth=0.14, location=(-1.65, 1.75, 2.08 + pi * 0.145))
        pt = sc._link_only(bpy.context.active_object, col)
        pt.data.materials.append(sc.make_mat("Mat_GrillPatty", "#5C2C16", rough=0.45))
        patty_tower.append(pt)

    # Speed-blur streaks around Alex's hands for b25 ("I stopped being able to see my own hands")!
    blur_arcs = bpy.data.objects.new("Prop_SpeedBlurArcs", None)
    blur_arcs.location = (0.0, 1.35, 2.85)
    col.objects.link(blur_arcs)
    for bi in range(6):
        bpy.ops.mesh.primitive_torus_add(major_radius=1.1 + bi * 0.14, minor_radius=0.045, location=(0, 0, (bi - 2.5) * 0.18), rotation=(math.radians(78), 0, bi * 0.35))
        arc = sc._link_only(bpy.context.active_object, col)
        arc.data.materials.append(sc.make_mat("Mat_SpeedWhite", "#F8FAFC", emit_hex="#E0F2FE", emit_str=3.5))
        arc.parent = blur_arcs

    # Party Cup prop for Noob neighbor
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.22, depth=0.55, location=(-6.2, 1.8, 2.4))
    party_cup = sc._link_only(bpy.context.active_object, col)
    party_cup.name = "Prop_PartyCup"
    party_cup.data.materials.append(sc.make_mat("Mat_PartyCupCyan", "#06B6D4", rough=0.25, coat=0.35))

    # Warm Bedroom Key Lighting + Night Party Spill through Window!
    sc.setup_bright_sky_world(scene, is_night=True)
    def add_area(name, loc, target, energy, sz, col_hex):
        ld = bpy.data.lights.new(name, type="AREA")
        ld.energy = energy
        ld.size = sz
        ld.color = bcl.hex_to_linear(col_hex)[:3]
        lo = bpy.data.objects.new(name, ld)
        col.objects.link(lo)
        lo.location = loc
        lo.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        return lo

    add_area("Room_CeilingWarm", ( 0.0,  3.5, 8.2), (0, 1.0, 2.4),  680, 6.0, "#FFF3DC")
    add_area("Room_FrontFill",   ( 2.0,  6.5, 4.8), (0, 0.5, 3.0),  280, 4.5, "#FFFFFF")
    add_area("Window_PartyGlow", ( 0.0, -7.5, 5.5), (0,-2.0, 3.5), 1150, 5.5, "#EC4899")
    add_area("Door_Light",       (-4.0,  4.0, 5.5), (-6.8, 1.5, 3.0), 580, 3.5, "#FFF7ED")

    return {
        "wrap_sheet": wrap_sheet,
        "center_burger": center_burger,
        "center_wrapped": center_wrapped,
        "wrapped_towers": wrapped_towers,
        "alarm_clock": alarm_clock,
        "stopwatch": stopwatch,
        "breakfast": breakfast,
        "blue_plate": blue_plate,
        "cat": cat_prop,
        "grill": grill_root,
        "flip_patty": patty_active,
        "patty_tower": patty_tower,
        "blur_arcs": blur_arcs,
        "party_cup": party_cup,
    }


def main():
    preview_only = "--preview" in sys.argv
    bcl.clear_scene()
    scene = bpy.context.scene
    sc.configure_fast_eevee(scene, res_x=720, res_y=1280, samples=10, raytracing=False)

    beats_data = sc.load_beats()
    props = build_room_set(scene)

    cast_col = bpy.data.collections.new("Room_Cast")
    scene.collection.children.link(cast_col)

    # Append Alex (with Pal Hair + Red Roblox Cap!)
    alex = sc.append_character("01_Alex_Protagonist", "Alex", cast_col, enable_extra_acc=["red_roblox_cap"])
    sc.set_char_transform(alex, 0.0, 0.2, 0.0, 0.0)

    # Append Neighbor Noob + Window Party Crowd outside!
    noob = sc.append_character("02_Noob_BestFriend", "Noob_Neighbor", cast_col, add_party_hat=True, party_hat_color="#06B6D4")
    maya = sc.append_character("04_Maya_BestFriend", "Maya_Out", cast_col, add_party_hat=True, party_hat_color="#EC4899")
    chloe = sc.append_character("08_Chloe_Rival", "Chloe_Out", cast_col, add_party_hat=True, party_hat_color="#FACC15")
    admin = sc.append_character("07_Admin_Boss", "Admin_Out", cast_col, add_party_hat=True, party_hat_color="#A855F7")

    sc.set_char_transform(maya,  -2.4, -6.2, 0.4,  8)
    sc.set_char_transform(chloe,  2.4, -6.2, 0.4, -8)
    sc.set_char_transform(admin,  0.0, -7.8, 0.4,  0)

    cam_d = bpy.data.cameras.new("Cam_Room")
    cam = bpy.data.objects.new("Cam_Room", cam_d)
    scene.collection.objects.link(cam)
    scene.camera = cam

    bcl.setup_cinema_compositor(
        scene, glare_threshold=1.5, glare_strength=0.16, dispersion=0.001,
        lift_rgb=(0.99, 0.99, 1.0), gamma_rgb=(1.0, 1.0, 1.0), gain_rgb=(1.02, 1.02, 1.01),
        vignette=0.12,
    )

    room_beats = [
        "b02_except_me", "b03_huss_1", "b08_preparing", "b09_huss_2",
        "b11_so_i_train", "b12_5am_wrist", "b13_200_wraps", "b14_no_breakfast",
        "b15_fold_tuck", "b16_four_sec", "b17_huss_3", "b18_wrap_items",
        "b19_wrap_cat", "b20_neighbor", "b21_come_out", "b22_exactly",
        "b23_huss_4", "b24_fold_fast", "b25_blur_hands", "b34_only_wrap",
        "b39_learning_cook", "b40_5am_200", "b41_huss_cook",
    ]

    # Map progressive tower heights across training arc!
    tower_tier_by_beat = {
        "b02_except_me": 1, "b03_huss_1": 1, "b08_preparing": 2, "b09_huss_2": 3,
        "b11_so_i_train": 4, "b12_5am_wrist": 3, "b13_200_wraps": 6, "b14_no_breakfast": 5,
        "b15_fold_tuck": 5, "b16_four_sec": 6, "b17_huss_3": 6, "b18_wrap_items": 6,
        "b19_wrap_cat": 5, "b20_neighbor": 5, "b21_come_out": 5, "b22_exactly": 7,
        "b23_huss_4": 8, "b24_fold_fast": 8, "b25_blur_hands": 8,
        "b34_only_wrap": 0, "b39_learning_cook": 0, "b40_5am_200": 0, "b41_huss_cook": 0,
    }

    for bid in room_beats:
        f0, f1 = sc.beat_frame_range(beats_data, bid)
        is_grill = bid in ("b34_only_wrap", "b39_learning_cook", "b40_5am_200", "b41_huss_cook")
        max_tier = tower_tier_by_beat.get(bid, 3)

        # Toggle towers
        for tier, wb in props["wrapped_towers"]:
            set_hidden_tree(wb, tier >= max_tier)

        # Toggle special props
        set_hidden_tree(props["wrap_sheet"], is_grill and bid != "b34_only_wrap")
        set_hidden_tree(props["breakfast"], bid != "b14_no_breakfast")
        set_hidden_tree(props["blue_plate"], bid != "b18_wrap_items")
        set_hidden_tree(props["cat"], bid != "b19_wrap_cat")
        set_hidden_tree(props["grill"], not is_grill)
        set_hidden_tree(props["alarm_clock"], bid not in ("b12_5am_wrist", "b39_learning_cook", "b40_5am_200"))
        set_hidden_tree(props["stopwatch"], bid not in ("b02_except_me", "b08_preparing", "b16_four_sec", "b24_fold_fast"))
        set_hidden_tree(props["blur_arcs"], bid != "b25_blur_hands")
        props["party_cup"].hide_viewport = bid not in ("b20_neighbor", "b21_come_out")
        props["party_cup"].hide_render = bid not in ("b20_neighbor", "b21_come_out")

        for pi, pt in enumerate(props["patty_tower"]):
            pt.hide_viewport = True
            pt.hide_render = True

        # Place Noob outside window by default, or in doorway for b21_come_out
        if bid == "b20_neighbor":
            sc.set_char_transform(noob, 0.0, -4.8, 0.85, 0.0)
            props["party_cup"].location = (-1.15, -3.7, 3.85)
        elif bid == "b21_come_out":
            sc.set_char_transform(noob, -6.4, 1.5, 0.0, -90.0)
            props["party_cup"].location = (-5.7, 0.4, 2.75)
        else:
            sc.set_char_transform(noob, 4.6, -6.8, 0.4, -18.0)

        frames_to_render = [(f0 + f1) // 2] if preview_only else list(range(f0, f1 + 1))
        for f in frames_to_render:
            u = (f - f0) / max(1, (f1 - f0))
            t = f / 30.0

            # Keep window party crowd dancing enthusiastically outside!
            sc.animate_party_dance(maya,  t, phase=0.2, energy=1.1)
            sc.animate_party_dance(chloe, t, phase=1.4, energy=1.1)
            sc.animate_party_dance(admin, t, phase=2.6, energy=1.0)
            if bid not in ("b20_neighbor", "b21_come_out"):
                sc.animate_party_dance(noob, t, phase=0.8, energy=1.2)

            # Default Alex table stance (hide Alex when POV looking at Neighbor Noob!)
            hide_alex = bid in ("b20_neighbor", "b21_come_out")
            alex["col"].hide_viewport = hide_alex
            alex["col"].hide_render = hide_alex
            sc.set_char_transform(alex, 0.0, 0.15, 0.0, 0.0)
            sc.swap_expression(alex, "alex_determined_atlas.png")

            # Default center burger visibility
            is_pov_huss = bid in ("b03_huss_1", "b09_huss_2", "b17_huss_3", "b23_huss_4")
            show_unwrapped = (not is_grill) and bid not in ("b14_no_breakfast", "b18_wrap_items", "b19_wrap_cat", "b12_5am_wrist")
            show_wrapped = False

            if is_pov_huss:
                # Iconic HUSS! montage: first 60% top-down POV wrapping hands, last 40% intense front close-up with kicks!
                cyc = (t * 6.5) % 1.0
                show_unwrapped = cyc < 0.52
                show_wrapped = cyc >= 0.52
                arm_in = math.sin(cyc * math.pi)
                sc.set_char_pose(
                    alex,
                    torso_loc=(0, 0, -0.10 * arm_in),
                    torso_rot=(18, 0, 0),
                    head_rot=(14, 0, 0),
                    rarm_rot=(-76 - 20 * arm_in, -18 * arm_in, 22 * arm_in),
                    larm_rot=(-76 - 20 * arm_in,  18 * arm_in, -22 * arm_in),
                )
                kick = (1.0 - (cyc * 2 % 1.0)) * 0.12 * (1 if int(f) % 2 == 0 else -1)
                if u < 0.62:
                    # Top-down POV camera straight over yellow wrapper & Alex's two arms!
                    sc.set_camera_look(cam, (0.0, 1.55, 6.05 + kick), (0.0, 1.72, 2.02), lens=32.0, roll_deg=180.0 + kick * 12)
                else:
                    sc.set_camera_look(cam, (0.0, 6.2 - 0.5 * u, 4.1 + kick), (0.0, 1.0, 3.1), lens=38.0, roll_deg=kick * 15)

            elif bid in ("b02_except_me", "b08_preparing", "b11_so_i_train", "b13_200_wraps", "b22_exactly"):
                # Intense Alex wrapping at table with colorful party crowd behind window & growing burger towers!
                w = math.sin(t * 18.0)
                sc.set_char_pose(
                    alex,
                    torso_rot=(14, 0, 4 * w),
                    head_rot=(10, 0, -4 * w),
                    rarm_rot=(-68 + 18 * w, -22, 26),
                    larm_rot=(-68 - 18 * w,  22, -26),
                )
                zoom_d = 8.4 - 1.0 * u if bid != "b22_exactly" else 7.6 - 0.9 * u
                sc.set_camera_look(cam, (0.3 - 0.6 * u, zoom_d, 4.35), (-0.25, 0.6, 3.25), lens=32.0)

            elif bid == "b12_5am_wrist":
                # 5 AM Wrist stretches next to Alarm Clock!
                w = math.sin(t * 14.0)
                sc.set_char_pose(
                    alex,
                    head_rot=(0, 0, 4 * w),
                    rarm_rot=(-90, 20 * w, -15 * w),
                    larm_rot=(-90, -20 * w, 15 * w),
                )
                sc.set_camera_look(cam, (0.8, 6.6 - 0.6 * u, 3.5), (0.2, 0.6, 3.1), lens=38.0)

            elif bid == "b14_no_breakfast":
                # Top-down POV wrapping the egg & bacon breakfast plate!
                fold = min(1.0, max(0.0, (u - 0.35) / 0.65))
                set_hidden_tree(props["breakfast"], fold > 0.68)
                show_wrapped = fold > 0.68
                sc.set_char_pose(
                    alex,
                    torso_rot=(18, 0, 0),
                    rarm_rot=(-76 - 18 * fold, -22 * fold, 24 * fold),
                    larm_rot=(-76 - 18 * fold,  22 * fold, -24 * fold),
                )
                sc.set_camera_look(cam, (0.0, 1.60, 6.10 - 0.35 * u), (0.0, 1.75, 2.04), lens=32.0, roll_deg=180.0)

            elif bid == "b15_fold_tuck":
                # Top-down rhythmic Fold, Fold, Tuck, Roll!
                phase = u * 4.0
                show_unwrapped = u < 0.72
                show_wrapped = u >= 0.72
                sc.set_char_pose(
                    alex,
                    torso_rot=(18, 0, 0),
                    rarm_rot=(-74 - 22 * abs(math.sin(phase * math.pi)), -24 * u, 28 * u),
                    larm_rot=(-74 - 22 * abs(math.cos(phase * math.pi)),  24 * u, -28 * u),
                )
                sc.set_camera_look(cam, (0.0, 1.55, 5.95 - 0.3 * u), (0.0, 1.75, 2.04), lens=33.0, roll_deg=180.0)

            elif bid == "b16_four_sec":
                # Glaring at the red stopwatch ("Four seconds. Too slow.")
                sc.set_char_pose(
                    alex,
                    torso_rot=(12, 0, -10),
                    head_rot=(16, 0, -16),
                    rarm_rot=(-55, -14, 18),
                    larm_rot=(-48, 12, -16),
                )
                sc.set_camera_look(cam, (-1.1, 6.4 - 0.9 * u, 3.9), (-0.3, 1.0, 3.0), lens=40.0)

            elif bid == "b18_wrap_items":
                # Wrapping the burger & blue plate!
                show_unwrapped = u < 0.45
                set_hidden_tree(props["blue_plate"], u < 0.45)
                sc.set_char_pose(
                    alex,
                    torso_rot=(14, 0, 0),
                    rarm_rot=(-72 + 14 * math.sin(t * 20), -18, 22),
                    larm_rot=(-72 - 14 * math.sin(t * 20),  18, -22),
                )
                sc.set_camera_look(cam, (0.5, 6.8 - 0.7 * u, 4.1), (0.0, 1.1, 2.9), lens=36.0)

            elif bid == "b19_wrap_cat":
                # Deadpan Alex behind the cozy wrapped orange cat ("The cat is fine. The cat is warm.")
                sc.swap_expression(alex, "alex_deadpan_atlas.png")
                sc.set_char_pose(
                    alex,
                    torso_rot=(0, 0, 0),
                    head_rot=(4, 0, 0),
                    rarm_rot=(-18, 8, -12),
                    larm_rot=(-18, -8, 12),
                )
                sc.set_camera_look(cam, (0.0, 6.5 - 0.8 * u, 3.6), (0.0, 1.2, 3.0), lens=38.0)

            elif bid == "b20_neighbor":
                # Neighbor Noob popping up outside Alex's window throwing a party!
                sc.animate_party_dance(noob, t, phase=0.0, energy=1.2)
                sc.set_camera_look(cam, (0.0, 1.4 - 0.8 * u, 4.4), (0.0, -4.8, 4.2), lens=32.0)

            elif bid == "b21_come_out":
                # Neighbor Noob leaning in Alex's doorway ("Come out, he says. You only live once.")
                sc.set_char_transform(noob, -6.2, 1.5, 0.0, -90.0)
                sc.set_char_pose(
                    noob,
                    torso_loc=(0, 0, 0.08 * abs(math.sin(t * 6))),
                    head_rot=(-4, 0, 8 * math.sin(t * 5)),
                    rarm_rot=(-125 + 14 * math.sin(t * 8), 16, -20),
                    larm_rot=(-60, -10, 12),
                )
                # Place camera cleanly in front of table/towers looking into open doorway!
                sc.set_camera_look(cam, (-1.2 - 0.8 * u, 4.4, 3.65), (-6.2, 1.5, 3.05), lens=34.0)

            elif bid == "b24_fold_fast":
                # Ultra-fast wrapping next to Stopwatch ("Fold, fold, tuck, roll. Two seconds. One second.")
                w = math.sin(t * 36.0)
                sc.set_char_pose(
                    alex,
                    torso_rot=(16, 0, 6 * w),
                    head_rot=(8, 0, -4 * w),
                    rarm_rot=(-72 + 28 * w, -24, 30),
                    larm_rot=(-72 - 28 * w,  24, -30),
                )
                sc.set_camera_look(cam, (0.0, 6.2 - 1.0 * u, 3.8), (0.0, 1.0, 3.1), lens=40.0)

            elif bid == "b25_blur_hands":
                # Shocked :O Alex with glowing white motion-blur arcs whipping around his hands!
                sc.swap_expression(alex, "alex_shocked_atlas.png")
                w = math.sin(t * 48.0)
                sc.set_char_pose(
                    alex,
                    torso_rot=(12, 0, 8 * w),
                    head_rot=(-4, 0, 5 * w),
                    rarm_rot=(-82 + 34 * w, -26, 32),
                    larm_rot=(-82 - 34 * w,  26, -32),
                )
                props["blur_arcs"].rotation_euler = (0, 0, t * 22.0)
                sc.set_camera_look(cam, (0.0, 5.8 - 0.7 * u, 3.7), (0.0, 0.8, 3.3), lens=40.0)

            elif bid == "b34_only_wrap":
                # Top-down gag: trying to wrap a raw burger patty directly on the black grill ("I only wrap.")
                w = math.sin(t * 16.0)
                props["wrap_sheet"].location = (0.0, 1.75, 2.22)
                sc.set_char_pose(
                    alex,
                    torso_rot=(18, 0, 0),
                    rarm_rot=(-76 - 16 * abs(w), -20, 22),
                    larm_rot=(-76 - 16 * abs(w),  20, -22),
                )
                sc.set_camera_look(cam, (0.0, 1.55, 6.0), (0.0, 1.75, 2.2), lens=34.0, roll_deg=180.0)

            elif bid in ("b39_learning_cook", "b40_5am_200", "b41_huss_cook"):
                # Alex back in his room learning to cook! Flipping patties into a towering 200-patty stack!
                props["wrap_sheet"].location = (0.0, 1.75, 2.02)
                w = math.sin(t * (22.0 if bid == "b41_huss_cook" else 12.0))
                flip_h = max(0.0, math.sin(t * 12.0)) * 1.45
                props["flip_patty"].location = (0.0, 0.0, 0.25 + flip_h)
                props["flip_patty"].rotation_euler = (flip_h * 4.5, 0.0, 0.0)
                # Grow cooked patty tower progressively!
                n_show = 4 if bid == "b39_learning_cook" else (int(6 + 16 * u) if bid == "b40_5am_200" else 22)
                for pi, pt in enumerate(props["patty_tower"]):
                    hide = pi >= n_show
                    pt.hide_viewport = hide
                    pt.hide_render = hide
                sc.set_char_pose(
                    alex,
                    torso_rot=(14, 0, 4 * w),
                    head_rot=(10, 0, -4 * w),
                    rarm_rot=(-78 - 22 * max(0, w), -10, 10),
                    larm_rot=(-68 + 14 * w, 12, -12),
                )
                kick = (0.10 * (1 if int(f) % 2 == 0 else -1)) if bid == "b41_huss_cook" else 0.0
                sc.set_camera_look(cam, (0.4 - 0.8 * u, 6.9 - 1.0 * u, 4.1 + kick), (-0.2, 0.8, 3.2), lens=36.0)

            set_hidden_tree(props["center_burger"], not show_unwrapped)
            set_hidden_tree(props["center_wrapped"], not show_wrapped)

            bpy.context.view_layer.update()
            sc.render_frame(scene, f, preview_tag=f"room_{bid}" if preview_only else None)

    print("scene_room.py COMPLETE!")


if __name__ == "__main__":
    main()
