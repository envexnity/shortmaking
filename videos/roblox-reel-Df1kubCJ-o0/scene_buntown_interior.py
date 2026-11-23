"""
scene_buntown_interior.py — Set 4: Bun Town Interior (Interview w/ Manager + Wrapped Burger/Clipboard/Tie
+ Midnight 400-Person Party Rush + Flying Wrapped Burgers + Stunned Mayor + Final Wall of Burgers & HUSS!).

Renders beats:
  b26_interview, b27_one_burger, b28_whenever, b29_already_wrap, b30_clipboard_tie,
  b31_impressed, b32_one_question, b33_never_cooked, b42_hired, b43_already_start,
  b45_midnight_rush, b46_one_of_me, b47_huss_climax, b48_400_burgers,
  b49_mayor_stared, b50_final_callback, b51_final_huss.
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


def set_hidden_tree(obj, hide: bool):
    obj.hide_viewport = hide
    obj.hide_render = hide
    for ch in obj.children:
        set_hidden_tree(ch, hide)


def build_interior_set(scene):
    col = bpy.data.collections.new("Set_BunTownInt")
    scene.collection.children.link(col)
    props_dir = PROJ_DIR / "props"

    def box(name, loc, scale, hex_col, rough=0.42, metal=0.0, coat=0.15, parent=None):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
        o = sc._link_only(bpy.context.active_object, col)
        o.name = name
        o.scale = scale
        o.data.materials.append(sc.make_mat(f"Mat_I_{name[:10]}_{hex_col}", hex_col, rough=rough, metal=metal, coat=coat))
        if parent:
            o.parent = parent
        return o

    # Clean cream fast-food tiled floor & walls
    box("Floor",   (0,  0.0, -0.25), (34, 34, 0.5), "#F5EFE6", rough=0.35, coat=0.25)
    box("Wall_N",  (0, -10.0, 6.0),  (34, 0.5, 13), "#FFF8EC", rough=0.55)
    box("Wall_S",  (0,  16.0, 6.0),  (34, 0.5, 13), "#FFF8EC", rough=0.55)
    box("Wall_W",  (-14, 2.0, 6.0),  (0.5, 34, 13), "#FFF8EC", rough=0.55)
    box("Wall_E",  ( 14, 2.0, 6.0),  (0.5, 34, 13), "#FFF8EC", rough=0.55)
    box("Ceiling", (0,  2.0, 12.2),  (34, 34, 0.5), "#F8FAFC", rough=0.60)

    # Teal stripe along interior walls
    box("TealTrim_N", (0, -9.70, 7.2), (33.5, 0.12, 0.65), "#0D9488", rough=0.35)
    box("TealTrim_S", (0, 15.70, 7.2), (33.5, 0.12, 0.65), "#0D9488", rough=0.35)

    # Colorful ceiling triangle party bunting flags!
    bunt_cols = ["#0D9488", "#FACC15", "#EF4444", "#38BDF8"]
    for bi in range(14):
        bx = -10.5 + bi * 1.6
        bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.45, radius2=0.02, depth=0.85, location=(bx, 2.0, 8.2), rotation=(math.radians(180), 0, 0))
        fl = sc._link_only(bpy.context.active_object, col)
        fl.data.materials.append(sc.make_mat(f"Mat_Bunt_{bunt_cols[bi % 4]}", bunt_cols[bi % 4], rough=0.5))

    # ==================== ICONIC BUN TOWN COUNTER (Y = 0.0, Top at Z = 2.15) ====================
    box("Counter_Base", (0.0, 0.0, 1.00), (16.0, 2.4, 2.00), "#0D9488", rough=0.35, coat=0.22)
    box("Counter_Top",  (0.0, 0.0, 2.08), (16.4, 2.75, 0.22), "#FAF5EB", rough=0.25, coat=0.30)
    box("Counter_Trim", (0.0, 1.24, 1.65), (16.1, 0.08, 0.22), "#F8FAFC", rough=0.30)

    # Cute Circular Bun Town Burger Logo Emblem on front of counter!
    bpy.ops.mesh.primitive_cylinder_add(vertices=28, radius=0.82, depth=0.10, location=(-1.4, 1.26, 1.05), rotation=(math.radians(90), 0, 0))
    emblem = sc._link_only(bpy.context.active_object, col)
    emblem.data.materials.append(sc.make_image_mat("Mat_BTLogo", props_dir / "buntown_logo_circle.png", rough=0.30, emit=0.08))

    # Ketchup & Mustard squeeze bottles on counter
    for bx, col_h in [(2.1, "#DC2626"), (2.65, "#FACC15")]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.16, depth=0.62, location=(bx, 0.75, 2.50))
        bt = sc._link_only(bpy.context.active_object, col)
        bt.data.materials.append(sc.make_mat(f"Mat_Cond_{col_h}", col_h, rough=0.28, coat=0.35))
        bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.14, radius2=0.03, depth=0.22, location=(bx, 0.75, 2.92))
        cap = sc._link_only(bpy.context.active_object, col)
        cap.data.materials.append(sc.make_mat(f"Mat_Cond_{col_h}", col_h, rough=0.28, coat=0.35))

    # Stainless Kitchen Shelves behind counter (-Y = -4.2) stocked with golden wrapped burgers!
    box("Shelf_Back", (0, -4.5, 4.4), (13.0, 1.2, 0.16), "#CBD5E1", rough=0.25, metal=0.75)
    for sx in range(-5, 6, 2):
        sc.build_wrapped_burger(f"ShelfWB_{sx}", (float(sx), -4.4, 4.50), col, scale=0.90)

    # Counter Interview Props: Unwrapped Burger, Wrapped Burger, Unwrapped Clipboard, Wrapped Clipboard, Wrapped Tie!
    c_burger = sc.build_burger("Counter_Burger", (0.55, 0.45, 2.20), col, scale=1.05)
    c_wrapped = sc.build_wrapped_burger("Counter_WrappedBurger", (0.55, 0.45, 2.20), col, scale=1.08)

    # Clipboard (normal brown wood + white paper) vs Wrapped Clipboard (yellow burger wrapper!)
    clip_normal = bpy.data.objects.new("Prop_ClipboardNormal", None)
    clip_normal.location = (-1.15, 0.35, 2.22)
    col.objects.link(clip_normal)
    box("ClipBoard", (0, 0, 0.04), (0.85, 1.15, 0.08), "#92400E", rough=0.55, parent=clip_normal)
    box("ClipPaper", (0, 0, 0.09), (0.72, 0.96, 0.02), "#F8FAFC", rough=0.50, parent=clip_normal)

    clip_wrapped = bpy.data.objects.new("Prop_ClipboardWrapped", None)
    clip_wrapped.location = (-1.15, 0.35, 2.22)
    col.objects.link(clip_wrapped)
    box("ClipWrapY", (0, 0, 0.06), (0.94, 1.24, 0.12), "#FCD34D", rough=0.50, parent=clip_wrapped)
    box("ClipWrapR", (0, 0, 0.07), (0.96, 0.16, 0.13), "#E11D48", rough=0.48, parent=clip_wrapped)

    # Wrapped Tie (sits right over Manager's chest when "So was his tie." lands!!)
    tie_wrapped = bpy.data.objects.new("Prop_TieWrapped", None)
    tie_wrapped.location = (0.0, -1.08, 3.12)
    col.objects.link(tie_wrapped)
    box("TieWrapY", (0, 0, 0), (0.58, 0.24, 1.18), "#FCD34D", rough=0.48, parent=tie_wrapped)
    box("TieWrapR", (0, 0.01, 0), (0.60, 0.25, 0.18), "#E11D48", rough=0.48, parent=tie_wrapped)

    # Yellow wrapping paper sheet on counter for Alex's climax POV wrap!
    pov_sheet = bpy.data.objects.new("Prop_CounterSheet", None)
    pov_sheet.location = (0.0, 0.25, 2.20)
    col.objects.link(pov_sheet)
    box("CSheet_Y", (0, 0, 0.01), (1.75, 1.55, 0.025), "#FDE047", rough=0.55, parent=pov_sheet)
    box("CSheet_R", (0, 0, 0.025), (1.76, 0.18, 0.015), "#E11D48", rough=0.50, parent=pov_sheet)

    # Giant Golden Wall of Wrapped Burgers on counter for b50_final_callback!
    wall_burgers = []
    for col_x in (-1.9, -2.85, -3.8):
        for row_z in range(10):
            wb = sc.build_wrapped_burger(f"FinalWall_{col_x:.1f}_{row_z}", (col_x, 0.25, 2.20 + row_z * 0.43), col, scale=0.92)
            wall_burgers.append(wb)

    # 24 Flying Wrapped Burgers for b48_400_burgers ("400 burgers. One minute.")!!
    flying_burgers = []
    rng = random.Random(77)
    for fi in range(24):
        wb = sc.build_wrapped_burger(f"FlyWB_{fi}", (0, 0, 3.0), col, scale=0.95)
        flying_burgers.append((
            wb,
            rng.uniform(-7.5, 7.5),   # target X over crowd
            rng.uniform(3.2, 11.5),   # target Y over crowd
            rng.uniform(2.5, 5.2),    # arc peak height
            rng.uniform(0.0, 1.0),    # phase offset
        ))

    # Bright Balanced Fast-Food Interior Lighting (zero washout under AgX!)
    sc.setup_bright_sky_world(scene, is_night=False)
    for nm, loc, tgt, en, sz in [
        ("Int_Overhead1", ( 0.0,  2.5, 10.2), (0,  0.0, 2.5), 1150, 9.0),
        ("Int_Overhead2", ( 0.0,  9.5, 10.2), (0,  7.5, 2.5), 1050, 9.0),
        ("Int_FrontFill", ( 2.5,  6.5,  5.2), (0, -1.0, 3.2),  420, 5.0),
        ("Int_Kitchen",   ( 0.0, -4.5,  8.5), (0, -2.5, 3.0),  680, 6.0),
    ]:
        ld = bpy.data.lights.new(nm, type="AREA")
        ld.energy = en
        ld.size = sz
        ld.color = bcl.hex_to_linear("#FFFDF7")[:3]
        lo = bpy.data.objects.new(nm, ld)
        col.objects.link(lo)
        lo.location = loc
        lo.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()

    return {
        "c_burger": c_burger,
        "c_wrapped": c_wrapped,
        "clip_normal": clip_normal,
        "clip_wrapped": clip_wrapped,
        "tie_wrapped": tie_wrapped,
        "pov_sheet": pov_sheet,
        "wall_burgers": wall_burgers,
        "flying_burgers": flying_burgers,
    }


def main():
    preview_only = "--preview" in sys.argv
    bcl.clear_scene()
    scene = bpy.context.scene
    sc.configure_fast_eevee(scene, res_x=720, res_y=1280, samples=10, raytracing=False)

    beats_data = sc.load_beats()
    props = build_interior_set(scene)

    cast_col = bpy.data.collections.new("Int_Cast")
    scene.collection.children.link(cast_col)

    # Main 3 Characters
    alex = sc.append_character("01_Alex_Protagonist", "Alex", cast_col, enable_extra_acc=["red_roblox_cap"])
    manager = sc.append_character("09_BunTown_Manager", "Manager", cast_col)
    mayor = sc.append_character("10_Town_Mayor", "Mayor", cast_col, add_party_hat=True, party_hat_color="#38BDF8")

    # Midnight Rush Party Crowd (all our cast in party hats packed inside Bun Town!)
    crowd_defs = [
        ("02_Noob_BestFriend", "Crowd_Noob1",   "#FACC15", (-3.8, 4.2, 0, 170)),
        ("04_Maya_BestFriend", "Crowd_Maya1",   "#EC4899", ( 3.6, 4.4, 0, 190)),
        ("08_Chloe_Rival",     "Crowd_Chloe1",  "#A855F7", (-1.5, 5.8, 0, 175)),
        ("05_Dad_Principal",   "Crowd_Dad1",    "#22C55E", ( 1.8, 5.6, 0, 185)),
        ("06_Hacker_Glitch",   "Crowd_Hacker1", "#EF4444", (-5.8, 6.2, 0, 165)),
        ("07_Admin_Boss",      "Crowd_Admin1",  "#38BDF8", ( 5.6, 6.2, 0, 195)),
        ("03_RichKid_Dominus", "Crowd_Rich1",   "#F59E0B", (-3.5, 8.2, 0, 175)),
        ("02_Noob_BestFriend", "Crowd_Noob2",   "#EC4899", ( 0.0, 8.4, 0, 180)),
        ("04_Maya_BestFriend", "Crowd_Maya2",   "#FACC15", ( 3.5, 8.0, 0, 185)),
        ("08_Chloe_Rival",     "Crowd_Chloe2",  "#38BDF8", (-6.2, 9.2, 0, 170)),
        ("05_Dad_Principal",   "Crowd_Dad2",    "#A855F7", ( 6.2, 9.0, 0, 190)),
    ]
    crowd = []
    for cid, nm, phc, pos in crowd_defs:
        ch = sc.append_character(cid, nm, cast_col, add_party_hat=True, party_hat_color=phc)
        crowd.append((ch, pos))

    cam_d = bpy.data.cameras.new("Cam_Int")
    cam = bpy.data.objects.new("Cam_Int", cam_d)
    scene.collection.objects.link(cam)
    scene.camera = cam

    bcl.setup_cinema_compositor(
        scene, glare_threshold=1.6, glare_strength=0.14, dispersion=0.0008,
        lift_rgb=(0.995, 0.995, 1.0), gamma_rgb=(1.0, 1.0, 1.0), gain_rgb=(1.02, 1.02, 1.0),
        vignette=0.10,
    )

    int_beats = [
        "b26_interview", "b27_one_burger", "b28_whenever", "b29_already_wrap",
        "b30_clipboard_tie", "b31_impressed", "b32_one_question", "b33_never_cooked",
        "b42_hired", "b43_already_start", "b45_midnight_rush", "b46_one_of_me",
        "b47_huss_climax", "b48_400_burgers", "b49_mayor_stared",
        "b50_final_callback", "b51_final_huss",
    ]

    for bid in int_beats:
        f0, f1 = sc.beat_frame_range(beats_data, bid)
        is_rush = bid in ("b45_midnight_rush", "b48_400_burgers", "b49_mayor_stared")
        show_wall = bid in ("b50_final_callback", "b51_final_huss")

        # Hide/show crowd & mayor cleanly
        for ch, (cx, cy, cz, cyaw) in crowd:
            ch["col"].hide_viewport = not is_rush
            ch["col"].hide_render = not is_rush
            sc.set_char_transform(ch, cx, cy, cz, cyaw)
        mayor["col"].hide_viewport = not is_rush
        mayor["col"].hide_render = not is_rush

        # Hide/show final wall & flying burgers
        for wb in props["wall_burgers"]:
            set_hidden_tree(wb, not show_wall)
        for wb, *_ in props["flying_burgers"]:
            set_hidden_tree(wb, bid != "b48_400_burgers")

        set_hidden_tree(props["pov_sheet"], bid not in ("b43_already_start", "b46_one_of_me", "b47_huss_climax", "b50_final_callback", "b51_final_huss"))

        frames_to_render = [(f0 + f1) // 2] if preview_only else list(range(f0, f1 + 1))
        for f in frames_to_render:
            u = (f - f0) / max(1, (f1 - f0))
            t = f / 30.0

            # Defaults — hide Alex on Manager-focused shots so Alex never overlaps Manager!
            is_mgr_shot = bid in ("b27_one_burger", "b28_whenever", "b29_already_wrap", "b30_clipboard_tie", "b31_impressed", "b32_one_question", "b42_hired")
            manager["col"].hide_viewport = not is_mgr_shot
            manager["col"].hide_render = not is_mgr_shot
            alex["col"].hide_viewport = is_mgr_shot
            alex["col"].hide_render = is_mgr_shot
            set_hidden_tree(props["c_burger"], True)
            set_hidden_tree(props["c_wrapped"], True)
            set_hidden_tree(props["clip_normal"], True)
            set_hidden_tree(props["clip_wrapped"], True)
            set_hidden_tree(props["tie_wrapped"], True)

            if bid == "b26_interview":
                # Alex marches confidently into Bun Town!
                sc.swap_expression(alex, "alex_determined_atlas.png")
                sc.set_char_transform(alex, 0.0, 9.0 - 4.0 * u, 0.0, 180.0)
                w = math.sin(t * 10.0)
                sc.set_char_pose(alex, torso_loc=(0, 0, abs(w)*0.12), rarm_rot=(25*w, 0, 0), larm_rot=(-25*w, 0, 0))
                sc.set_camera_look(cam, (0.0, 1.5, 3.4), (0.0, 7.5 - 3.5 * u, 3.0), lens=34.0)

            elif bid == "b27_one_burger":
                # Dramatic close-up on ONE unwrapped burger placed on the counter!
                manager["col"].hide_viewport = False
                manager["col"].hide_render = False
                sc.set_char_transform(manager, 0.0, -1.65, 0.0, 0.0)
                set_hidden_tree(props["c_burger"], False)
                props["c_burger"].location = (0.55, 0.45, 2.20 + max(0.0, (0.25 - u) * 2.5))
                sc.set_camera_look(cam, (0.55, 3.2 - 0.5 * u, 3.55), (0.55, 0.45, 2.45), lens=46.0)

            elif bid == "b28_whenever":
                # Manager smiling politely behind counter with burger & clipboard ("Whenever you are ready")
                manager["col"].hide_viewport = False
                manager["col"].hide_render = False
                sc.set_char_transform(manager, 0.0, -1.65, 0.0, 0.0)
                sc.swap_expression(manager, "manager_happy_atlas.png")
                sc.set_char_pose(manager, head_rot=(-4, 0, 6 * math.sin(t * 4)), rarm_rot=(-42, 18, -18), larm_rot=(-38, -14, 14))
                set_hidden_tree(props["c_burger"], False)
                props["c_burger"].location = (0.55, 0.45, 2.20)
                set_hidden_tree(props["clip_normal"], False)
                sc.set_camera_look(cam, (0.0, 5.8 - 0.6 * u, 3.7), (0.0, -0.8, 3.2), lens=38.0)

            elif bid == "b29_already_wrap":
                # BOOM! Burger is ALREADY wrapped in yellow paper — Manager's jaw drops!
                manager["col"].hide_viewport = False
                manager["col"].hide_render = False
                sc.set_char_transform(manager, 0.0, -1.65, 0.0, 0.0)
                sc.swap_expression(manager, "manager_shocked_atlas.png")
                sc.set_char_pose(manager, head_rot=(12, 0, 0), rarm_rot=(-65, 24, -22), larm_rot=(-65, -24, 22))
                set_hidden_tree(props["c_wrapped"], False)
                set_hidden_tree(props["clip_normal"], False)
                sc.set_camera_look(cam, (0.0, 5.2 - 0.5 * u, 3.7), (0.0, -0.8, 3.1), lens=42.0)

            elif bid == "b30_clipboard_tie":
                # First half: Clipboard is wrapped! Second half: Manager looks down — HIS TIE IS WRAPPED!!
                manager["col"].hide_viewport = False
                manager["col"].hide_render = False
                sc.set_char_transform(manager, 0.0, -1.65, 0.0, 0.0)
                sc.swap_expression(manager, "manager_shocked_atlas.png")
                set_hidden_tree(props["c_wrapped"], False)
                set_hidden_tree(props["clip_wrapped"], False)
                if u >= 0.45:
                    set_hidden_tree(props["tie_wrapped"], False)
                    sc.set_char_pose(manager, head_rot=(32, 0, 0), rarm_rot=(-50, 20, -20), larm_rot=(-50, -20, 20))
                    sc.set_camera_look(cam, (0.0, 4.4 - 0.6 * (u - 0.45), 3.65), (0.0, -1.2, 3.25), lens=46.0)
                else:
                    sc.set_char_pose(manager, head_rot=(10, 0, -18), rarm_rot=(-55, 18, -18), larm_rot=(-55, -18, 18))
                    sc.set_camera_look(cam, (-0.3, 5.0, 3.65), (-0.4, -0.5, 3.0), lens=42.0)

            elif bid == "b31_impressed":
                # Manager staring straight ahead with wrapped tie ("He was impressed. I could tell.")
                manager["col"].hide_viewport = False
                manager["col"].hide_render = False
                sc.set_char_transform(manager, 0.0, -1.65, 0.0, 0.0)
                sc.swap_expression(manager, "manager_stern_atlas.png")
                sc.set_char_pose(manager, head_rot=(0, 0, 0), rarm_rot=(-22, 8, -10), larm_rot=(-22, -8, 10))
                set_hidden_tree(props["c_wrapped"], False)
                set_hidden_tree(props["clip_wrapped"], False)
                set_hidden_tree(props["tie_wrapped"], False)
                sc.set_camera_look(cam, (0.0, 5.2 - 0.5 * u, 3.65), (0.0, -1.0, 3.25), lens=40.0)

            elif bid == "b32_one_question":
                # Manager raises finger seriously: "Then he asked me one question. Can you cook a burger?"
                manager["col"].hide_viewport = False
                manager["col"].hide_render = False
                sc.set_char_transform(manager, 0.0, -1.65, 0.0, 0.0)
                sc.swap_expression(manager, "manager_stern_atlas.png")
                sc.set_char_pose(manager, torso_rot=(8, 0, 0), head_rot=(4, 0, 0), larm_rot=(-122, -10, 14), rarm_rot=(-30, 8, -8))
                set_hidden_tree(props["c_wrapped"], False)
                set_hidden_tree(props["tie_wrapped"], False)
                sc.set_camera_look(cam, (0.2, 4.9 - 0.6 * u, 3.65), (0.0, -1.1, 3.35), lens=42.0)

            elif bid == "b33_never_cooked":
                # Alex on customer side shrugging deadpan behind ketchup & mustard bottles!
                sc.set_char_transform(alex, 0.0, 2.2, 0.0, 180.0)
                sc.swap_expression(alex, "alex_deadpan_atlas.png")
                shrug = math.sin(u * math.pi)
                sc.set_char_pose(alex, head_rot=(0, 8 * shrug, 0), rarm_rot=(-32 * shrug, 28 * shrug, -32 * shrug), larm_rot=(-32 * shrug, -28 * shrug, 32 * shrug))
                set_hidden_tree(props["c_wrapped"], False)
                sc.set_camera_look(cam, (0.8, -3.2 + 0.5 * u, 3.7), (0.2, 1.8, 3.2), lens=38.0)

            elif bid == "b42_hired":
                # Manager thrilled behind counter ("You're hired! When can you start?")
                manager["col"].hide_viewport = False
                manager["col"].hide_render = False
                sc.set_char_transform(manager, 0.0, -1.65, 0.0, 0.0)
                sc.swap_expression(manager, "manager_thrilled_atlas.png")
                sc.set_char_pose(manager, head_rot=(-4, 0, 6 * math.sin(t * 7)), rarm_rot=(-55, 16, -16), larm_rot=(-55, -16, 16))
                set_hidden_tree(props["c_burger"], False)
                props["c_burger"].location = (0.55, 0.45, 2.20)
                set_hidden_tree(props["clip_normal"], False)
                sc.set_camera_look(cam, (0.0, 5.4 - 0.7 * u, 3.65), (0.0, -1.0, 3.25), lens=40.0)

            elif bid in ("b43_already_start", "b46_one_of_me"):
                # Alex ALREADY behind the Bun Town counter locked in wrapping!
                sc.set_char_transform(alex, 0.0, -1.65, 0.0, 0.0)
                sc.swap_expression(alex, "alex_determined_atlas.png")
                w = math.sin(t * 22.0)
                sc.set_char_pose(alex, torso_rot=(15, 0, 4 * w), head_rot=(10, 0, 0), rarm_rot=(-70 + 18 * w, -20, 24), larm_rot=(-70 - 18 * w, 20, -24))
                set_hidden_tree(props["c_burger"], False)
                props["c_burger"].location = (0.0, 0.25, 2.22)
                sc.set_camera_look(cam, (0.3, 5.4 - 0.9 * u, 4.1), (0.0, -0.8, 3.1), lens=38.0)

            elif bid == "b45_midnight_rush":
                # High-angle wide shot of the HUGE party-hat crowd rushing into Bun Town at midnight!
                sc.set_char_transform(alex, 0.0, -1.65, 0.0, 0.0)
                sc.set_char_transform(mayor, 0.0, 3.8, 0.0, 180.0)
                sc.animate_party_dance(mayor, t, phase=0.0, energy=1.0)
                for idx, (ch, _) in enumerate(crowd):
                    sc.animate_party_dance(ch, t, phase=idx * 0.7, energy=1.15)
                sc.set_camera_look(cam, (-3.5 + 7.0 * u, -2.5, 9.2 - 1.0 * u), (0.0, 6.2, 2.6), lens=26.0)

            elif bid in ("b47_huss_climax", "b51_final_huss"):
                # Ferocious climax HUSS! POV wrap + intense counter front!
                sc.set_char_transform(alex, 0.0, -1.65, 0.0, 0.0)
                sc.swap_expression(alex, "alex_determined_atlas.png")
                cyc = (t * 7.5) % 1.0
                arm_in = math.sin(cyc * math.pi)
                set_hidden_tree(props["c_burger"], cyc >= 0.50)
                set_hidden_tree(props["c_wrapped"], cyc < 0.50)
                props["c_burger"].location = (0.0, 0.25, 2.22)
                props["c_wrapped"].location = (0.0, 0.25, 2.22)
                sc.set_char_pose(
                    alex,
                    torso_loc=(0, 0, -0.10 * arm_in),
                    torso_rot=(18, 0, 0),
                    head_rot=(12, 0, 0),
                    rarm_rot=(-78 - 20 * arm_in, -20 * arm_in, 24 * arm_in),
                    larm_rot=(-78 - 20 * arm_in,  20 * arm_in, -24 * arm_in),
                )
                kick = (1.0 - (cyc * 2 % 1.0)) * 0.14 * (1 if int(f) % 2 == 0 else -1)
                if (bid == "b47_huss_climax" and u < 0.60) or (bid == "b51_final_huss" and u >= 0.45):
                    sc.set_camera_look(cam, (0.0, 0.10, 6.20 + kick), (0.0, 0.25, 2.20), lens=32.0, roll_deg=180.0 + kick * 14)
                else:
                    sc.set_camera_look(cam, (0.0, 4.6 - 0.6 * u, 4.0 + kick), (0.0, -0.9, 3.2), lens=40.0, roll_deg=kick * 16)

            elif bid == "b48_400_burgers":
                # 400 BURGERS FLYING IN ARCS OVER THE PACKED CROWD!!
                sc.set_char_transform(alex, 0.0, -1.65, 0.0, 0.0)
                sc.set_char_transform(mayor, 0.0, 3.8, 0.0, 180.0)
                for idx, (ch, _) in enumerate(crowd):
                    sc.animate_party_dance(ch, t, phase=idx * 0.7, energy=1.3)
                for wb, tx, ty, pk, ph in props["flying_burgers"]:
                    fu = (u * 2.2 + ph) % 1.0
                    bx = tx * fu
                    by = -0.5 + (ty + 0.5) * fu
                    bz = 2.6 + 4.0 * pk * fu * (1.0 - fu)
                    wb.location = (bx, by, bz)
                    wb.rotation_euler = (fu * 10.0, fu * 6.0, 0.0)
                sc.set_camera_look(cam, (-5.5 + 3.5 * u, 13.0 - 1.8 * u, 9.2), (0.0, 3.0, 3.0), lens=26.0)

            elif bid == "b49_mayor_stared":
                # Close-up of the Mayor jaw-dropped staring in disbelief ("How did you do that?")!
                sc.set_char_transform(mayor, 0.0, 4.2, 0.0, 180.0)
                sc.swap_expression(mayor, "mayor_shocked_atlas.png" if u < 0.55 else "mayor_confused_atlas.png")
                sc.set_char_pose(mayor, head_rot=(0, 4 * math.sin(u * 8), 0), rarm_rot=(-15, 8, -12), larm_rot=(-15, -8, 12))
                sc.set_camera_look(cam, (0.0, -0.8 + 0.6 * u, 3.85), (0.0, 4.2, 3.75), lens=44.0)

            elif bid == "b50_final_callback":
                # Smug Alex behind a MASSIVE GOLDEN WALL of wrapped burgers! ("While you were out partying, I said. By the way...")
                sc.set_char_transform(alex, 0.0, -1.65, 0.0, 0.0)
                sc.swap_expression(alex, "alex_smug_atlas.png")
                w = math.sin(t * 20.0)
                sc.set_char_pose(alex, torso_rot=(10, 0, 4 * w), head_rot=(-2, 0, -4 * w), rarm_rot=(-68 + 16 * w, -18, 22), larm_rot=(-68 - 16 * w, 18, -22))
                set_hidden_tree(props["c_burger"], False)
                props["c_burger"].location = (0.0, 0.25, 2.22)
                sc.set_camera_look(cam, (0.6 - 0.6 * u, 5.8 - 1.1 * u, 4.0), (-0.4, -0.6, 3.3), lens=38.0)

            bpy.context.view_layer.update()
            sc.render_frame(scene, f, preview_tag=f"int_{bid}" if preview_only else None)

    print("scene_buntown_interior.py COMPLETE!")


if __name__ == "__main__":
    main()
