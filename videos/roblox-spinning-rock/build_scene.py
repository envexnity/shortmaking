"""
build_scene.py — Full 9:16 Fada Theorem Roblox R6 Short ("In This World, Everyone Lives on a Giant Spinning Rock")
Blender 5.3.0 EEVEE, AgX - Punchy, 720x1280 -> 1080x1920, 30 fps.

- Art style inspired by @huss.hero (DgEkmPRjj__): bright vibrant suburban Roblox world,
  fluffy clouds, pastel gabled houses, crisp sidewalks/roads, dramatic sunset climax & cosmic space void.
- Preserves the exact 2 main R6 models (01_Alex_Protagonist & 02_Noob_BestFriend) verbatim,
  with classic Roblox faces & grounded IRL outfits on all 6 background R6 characters.

Usage:
  blender.exe --background --disable-autoexec --python build_scene.py -- --stills
  blender.exe --background --disable-autoexec --python build_scene.py -- --range 1 1014
  blender.exe --background --disable-autoexec --python build_scene.py
"""
import argparse
import math
import random
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

PROJ_DIR = Path(__file__).resolve().parent
ROOT = PROJ_DIR.parent.parent
sys.path.insert(0, str(PROJ_DIR))
sys.path.insert(0, str(ROOT / "90 Templates & Starter Kits" / "blender-cinema-kit"))

import blender_cinema_lib as bcl  # noqa: E402
import scene_common as sc  # noqa: E402


def make_box(name, loc, size, mat, col, rot=(0, 0, 0), bevel_w=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    sx, sy, sz = size
    for v in bm.verts:
        v.co.x *= sx
        v.co.y *= sy
        v.co.z *= sz
    me = bpy.data.meshes.new(f"{name}_Mesh")
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = loc
    obj.rotation_euler = rot
    col.objects.link(obj)
    obj.data.materials.append(mat)
    if bevel_w > 0:
        bev = obj.modifiers.new("Bevel", "BEVEL")
        bev.width = bevel_w
        bev.segments = 1
    return obj


def make_gable_roof(name, loc, width, depth, height, mat, col):
    """Build a proper triangular gable roof mesh (ridge running along X)."""
    bm = bmesh.new()
    hw, hd = width * 0.5, depth * 0.5
    v0 = bm.verts.new((-hw, -hd, 0.0))
    v1 = bm.verts.new(( hw, -hd, 0.0))
    v2 = bm.verts.new(( hw,  hd, 0.0))
    v3 = bm.verts.new((-hw,  hd, 0.0))
    r0 = bm.verts.new((-hw, 0.0, height))
    r1 = bm.verts.new(( hw, 0.0, height))
    bm.faces.new([v0, v1, v2, v3])
    bm.faces.new([v0, v1, r1, r0])
    bm.faces.new([v2, v3, r0, r1])
    bm.faces.new([v3, v0, r0])
    bm.faces.new([v1, v2, r1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(f"{name}_Mesh")
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = loc
    col.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def build_suburban_house(name, loc, facing_sign, wall_hex, roof_hex, trim_mat, win_mat, door_mat, col):
    """Build a crisp @huss.hero-inspired pastel suburban Roblox house with porch & white trim."""
    root = bpy.data.objects.new(name, None)
    root.location = loc
    col.objects.link(root)

    w_mat = sc.make_mat(f"Mat_House_{wall_hex}", wall_hex, rough=0.52)
    r_mat = sc.make_mat(f"Mat_Roof_{roof_hex}", roof_hex, rough=0.48)

    hw_x, hd_y, hh_z = 9.2, 7.6, 8.2
    body = make_box(f"{name}_Body", (0, 0, hh_z * 0.5), (hw_x, hd_y, hh_z), w_mat, col)
    body.parent = root

    # White corner trim pillars & top fascia
    for sx in (-1, 1):
        for sy in (-1, 1):
            c = make_box(f"{name}_Trim_{sx}_{sy}", (sx * (hw_x * 0.5 - 0.12), sy * (hd_y * 0.5 - 0.12), hh_z * 0.5), (0.36, 0.36, hh_z + 0.04), trim_mat, col)
            c.parent = root
    fascia = make_box(f"{name}_Fascia", (0, 0, hh_z + 0.12), (hw_x + 0.5, hd_y + 0.5, 0.28), trim_mat, col)
    fascia.parent = root

    # Gable roof
    roof = make_gable_roof(f"{name}_Roof", (0, 0, hh_z + 0.26), hw_x + 0.9, hd_y + 0.9, 3.8, r_mat, col)
    roof.parent = root

    # Front wall face coordinate (facing street = facing_sign * +Y)
    fy = facing_sign * (hd_y * 0.5)
    # Windows (2 upper, 1 side lower) with white frames
    for wx, wz in [(-2.5, 5.8), (2.5, 5.8), (2.5, 2.5)]:
        frm = make_box(f"{name}_WinF_{wx}_{wz}", (wx, fy + facing_sign * 0.06, wz), (2.3, 0.14, 2.1), trim_mat, col)
        pane = make_box(f"{name}_WinP_{wx}_{wz}", (wx, fy + facing_sign * 0.10, wz), (1.85, 0.12, 1.65), win_mat, col)
        frm.parent = root
        pane.parent = root

    # Front door + frame
    dfrm = make_box(f"{name}_DoorF", (-2.2, fy + facing_sign * 0.06, 2.1), (2.0, 0.14, 3.6), trim_mat, col)
    dp = make_box(f"{name}_Door", (-2.2, fy + facing_sign * 0.10, 2.05), (1.65, 0.12, 3.35), door_mat, col)
    dfrm.parent = root
    dp.parent = root

    # White front porch deck, awning, columns & chest-height railing
    py = fy + facing_sign * 1.45
    deck = make_box(f"{name}_Porch", (0, py, 0.22), (hw_x * 0.92, 2.8, 0.44), trim_mat, col)
    awning = make_box(f"{name}_Awning", (0, py, 3.85), (hw_x * 0.94, 2.9, 0.22), trim_mat, col)
    deck.parent = root
    awning.parent = root
    for cx in (-3.8, -0.4, 3.8):
        col_p = make_box(f"{name}_Pillar_{cx}", (cx, py + facing_sign * 1.15, 2.05), (0.28, 0.28, 3.3), trim_mat, col)
        col_p.parent = root
    # Porch rail only on right side (leaving left stairs open)
    rail = make_box(f"{name}_Rail", (1.8, py + facing_sign * 1.15, 1.15), (4.2, 0.14, 0.16), trim_mat, col)
    rail.parent = root

    return root


def build_lowpoly_tree(name, loc, col, scale=1.0):
    trunk_mat = sc.make_mat("Mat_TreeTrunk", "#7C4A26", rough=0.72)
    leaf_mat = sc.make_mat("Mat_TreeLeaf", "#28B84E", rough=0.58)
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.scale = (scale, scale, scale)
    col.objects.link(root)

    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.48, depth=3.8, location=(0, 0, 1.9))
    tr = sc._link_only(bpy.context.active_object, col)
    tr.name = f"{name}_Trunk"
    tr.data.materials.append(trunk_mat)
    tr.parent = root

    for idx, (ox, oy, oz, rad) in enumerate([(0, 0, 4.6, 2.0), (-1.0, 0.3, 3.9, 1.35), (1.0, -0.2, 4.1, 1.45)]):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=rad, location=(ox, oy, oz))
        lf = sc._link_only(bpy.context.active_object, col)
        lf.name = f"{name}_Leaf_{idx}"
        lf.data.materials.append(leaf_mat)
        lf.parent = root
    return root


def build_cloud(name, loc, col, scale=1.0):
    mat = sc.make_mat("Mat_CloudWhite", "#FFFFFF", rough=0.80, coat=0.0, emit_hex="#FFFFFF", emit_str=0.22)
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.scale = (scale, scale, scale)
    col.objects.link(root)
    for idx, (ox, oy, oz, r) in enumerate([(0, 0, 0, 1.8), (-1.5, 0.2, -0.3, 1.3), (1.6, -0.1, -0.2, 1.4), (0.4, 0.4, 0.6, 1.2)]):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=r, location=(ox, oy, oz))
        c = sc._link_only(bpy.context.active_object, col)
        c.name = f"{name}_Puff_{idx}"
        c.data.materials.append(mat)
        c.parent = root
    return root


def build_car(name, loc, color_hex, col, yaw_deg=0.0):
    """Chunky Roblox suburban sedan with tires planted cleanly at z = 0 relative to car origin."""
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.rotation_euler = (0, 0, math.radians(yaw_deg))
    col.objects.link(root)

    paint = sc.make_mat(f"Mat_Car_{color_hex}", color_hex, rough=0.26, coat=0.45)
    glass = sc.make_mat("Mat_CarGlass", "#93C5FD", rough=0.14, coat=0.50)
    tire = sc.make_mat("Mat_CarTire", "#1E222B", rough=0.75)
    rim = sc.make_mat("Mat_CarRim", "#CBD5E1", rough=0.35, metal=0.5)
    lamp = sc.make_mat("Mat_CarLamp", "#FEF08A", rough=0.2, emit_hex="#FEF08A", emit_str=2.2)

    body = make_box(f"{name}_Body", (0, 0, 1.05), (5.2, 2.5, 1.15), paint, col)
    cabin = make_box(f"{name}_Cabin", (-0.2, 0, 2.05), (2.9, 2.2, 1.0), paint, col)
    wind = make_box(f"{name}_Glass", (-0.2, 0, 2.05), (2.98, 2.02, 0.72), glass, col)
    for p in (body, cabin, wind):
        p.parent = root

    for wx in (-1.55, 1.55):
        for wy in (-1.28, 1.28):
            bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.55, depth=0.36, location=(wx, wy, 0.55), rotation=(math.radians(90), 0, 0))
            t = sc._link_only(bpy.context.active_object, col)
            t.data.materials.append(tire)
            t.parent = root
            bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.30, depth=0.39, location=(wx, wy, 0.55), rotation=(math.radians(90), 0, 0))
            rm = sc._link_only(bpy.context.active_object, col)
            rm.data.materials.append(rim)
            rm.parent = root
    for ly in (-0.82, 0.82):
        hl = make_box(f"{name}_HL_{ly}", (2.62, ly, 1.05), (0.08, 0.42, 0.30), lamp, col)
        hl.parent = root
    return root


def build_dog(name, loc, col, yaw_deg=0.0):
    """Cute blocky Roblox Golden Retriever dog standing cleanly at z = 0."""
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.rotation_euler = (0, 0, math.radians(yaw_deg))
    col.objects.link(root)

    fur = sc.make_mat("Mat_DogFur", "#E8A94B", rough=0.55)
    ear = sc.make_mat("Mat_DogEar", "#B87528", rough=0.58)
    collar = sc.make_mat("Mat_DogCollar", "#EF4444", rough=0.35)
    blk = sc.make_mat("Mat_DogBlk", "#18181B", rough=0.3)

    parts = [
        ("Body",   (0.0,  0.0,  0.95), (1.35, 0.72, 0.68), fur),
        ("Head",   (0.72, 0.0,  1.45), (0.68, 0.66, 0.64), fur),
        ("Snout",  (1.10, 0.0,  1.34), (0.28, 0.34, 0.26), fur),
        ("Nose",   (1.25, 0.0,  1.42), (0.08, 0.14, 0.10), blk),
        ("EyeL",   (1.07, 0.16, 1.56), (0.04, 0.09, 0.11), blk),
        ("EyeR",   (1.07,-0.16, 1.56), (0.04, 0.09, 0.11), blk),
        ("EarL",   (0.66, 0.36, 1.50), (0.20, 0.10, 0.34), ear),
        ("EarR",   (0.66,-0.36, 1.50), (0.20, 0.10, 0.34), ear),
        ("Collar", (0.55, 0.0,  1.18), (0.24, 0.72, 0.56), collar),
        ("Tail",   (-0.78,0.0,  1.22), (0.45, 0.16, 0.16), fur),
    ]
    for pname, ploc, psize, pmat in parts:
        o = make_box(f"{name}_{pname}", ploc, psize, pmat, col)
        if pname == "Tail":
            o.rotation_euler = (0, math.radians(-35), 0)
        o.parent = root

    legs = []
    for lx in (-0.42, 0.42):
        for ly in (-0.22, 0.22):
            leg = make_box(f"{name}_Leg_{lx}_{ly}", (lx, ly, 0.34), (0.24, 0.24, 0.68), fur, col)
            leg.parent = root
            legs.append(leg)
    return {"root": root, "legs": legs}


def build_gravity_arrows(col):
    """Glowing cyan downward magnetic force arrows around Alex's shoes for b03_glue_force."""
    root = bpy.data.objects.new("Prop_GravityArrows", None)
    root.location = (0, 0, 0)
    col.objects.link(root)

    mat = sc.make_mat("Mat_GravCyan", "#38BDF8", rough=0.25, emit_hex="#38BDF8", emit_str=3.5)
    arrows = []
    for i, ang in enumerate([0, 72, 144, 216, 288]):
        rad = math.radians(ang)
        ax, ay = math.cos(rad) * 1.45, math.sin(rad) * 1.45
        ar = bpy.data.objects.new(f"GravArrow_{i}", None)
        ar.location = (ax, ay, 1.35)
        col.objects.link(ar)
        ar.parent = root
        shaft = make_box(f"GravShaft_{i}", (0, 0, 0.55), (0.16, 0.16, 1.0), mat, col)
        shaft.parent = ar
        bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.34, radius2=0.02, depth=0.55, location=(0, 0, -0.20), rotation=(math.radians(180), 0, 0))
        tip = sc._link_only(bpy.context.active_object, col)
        tip.data.materials.append(mat)
        tip.parent = ar
        arrows.append(ar)
    return {"root": root, "arrows": arrows}


def build_set1_town(scene):
    """Set 1: @huss.hero-inspired Bright Suburban Roblox Street at (0, 0, 0)."""
    col = bpy.data.collections.new("Set1_TownStreet")
    scene.collection.children.link(col)

    m_road = sc.make_mat("Mat_Road", "#2D323E", rough=0.72)
    m_stripe = sc.make_mat("Mat_RoadStripe", "#F8FAFC", rough=0.55)
    m_sidewalk = sc.make_mat("Mat_Sidewalk", "#D8DEE6", rough=0.62)
    m_grass = sc.make_mat("Mat_Grass", "#4CC459", rough=0.72)
    m_trim = sc.make_mat("Mat_HouseTrim", "#F8FAFC", rough=0.45)
    m_win = sc.make_mat("Mat_HouseWindow", "#A5DCFF", rough=0.18, coat=0.35, emit_hex="#FEF08A", emit_str=0.0)
    m_door = sc.make_mat("Mat_HouseDoor", "#5C3A28", rough=0.55)
    m_pole = sc.make_mat("Mat_StreetPole", "#282C36", rough=0.40, metal=0.45)
    m_lamp = sc.make_mat("Mat_StreetLamp", "#FEF08A", rough=0.20, emit_hex="#FEF08A", emit_str=0.4)

    # Road top at z=-0.06, sidewalk top at z=0.0, grass top at z=-0.02
    make_box("Road", (0, 0, -0.31), (110, 10.0, 0.50), m_road, col)
    make_box("Sidewalk_N", (0, -7.2, -0.25), (110, 4.4, 0.50), m_sidewalk, col)
    make_box("Sidewalk_S", (0,  7.2, -0.25), (110, 4.4, 0.50), m_sidewalk, col)
    make_box("Lawn_N", (0, -22.0, -0.27), (120, 26.0, 0.50), m_grass, col)
    make_box("Lawn_S", (0,  22.0, -0.27), (120, 26.0, 0.50), m_grass, col)
    # Far green hills
    make_box("Hill_N", (0, -48.0, 2.5), (140, 24.0, 6.0), m_grass, col)
    make_box("Hill_S", (0,  48.0, 2.5), (140, 24.0, 6.0), m_grass, col)

    # Crisp white dashed center line & solid edge lines (offset >= 0.015m above road top)
    for ix in range(-44, 48, 5):
        make_box(f"Dash_{ix}", (ix, 0.0, -0.045), (2.4, 0.28, 0.03), m_stripe, col)
    make_box("EdgeLine_N", (0, -4.65, -0.045), (108, 0.22, 0.03), m_stripe, col)
    make_box("EdgeLine_S", (0,  4.65, -0.045), (108, 0.22, 0.03), m_stripe, col)

    # Pastel @huss.hero suburban houses along both sides (push South row back to y=20.5 so camera corridor stays 100% open)
    house_palette = [
        ("#F5D04C", "#334155"),  # Sunny yellow + charcoal roof
        ("#F2A2C8", "#7C2D12"),  # Soft pink + warm brown roof
        ("#DE6B58", "#1E293B"),  # Coral brick + slate roof
        ("#8ABDF7", "#1D4ED8"),  # Sky blue + royal blue roof
        ("#78C784", "#365314"),  # Sage green + forest roof
    ]
    for i, hx in enumerate([-24, -12, 0, 12, 24]):
        wc, rc = house_palette[i % len(house_palette)]
        build_suburban_house(f"HouseN_{i}", (hx, -15.5, 0.0), +1, wc, rc, m_trim, m_win, m_door, col)
        wc2, rc2 = house_palette[(i + 2) % len(house_palette)]
        build_suburban_house(f"HouseS_{i}", (hx + 4, 21.0, 0.0), -1, wc2, rc2, m_trim, m_win, m_door, col)

    # Trees along lawns (clear of camera viewlines on road/sidewalks)
    for i, tx in enumerate([-18, -6, 6, 18, 30]):
        build_lowpoly_tree(f"TreeN_{i}", (tx, -10.5, 0.0), col, scale=0.92 + (i % 2) * 0.14)
        build_lowpoly_tree(f"TreeS_{i}", (tx - 3, 16.5, 0.0), col, scale=0.95)

    # Streetlights (clear of center x=0 hero sightline!) & fire hydrant
    for sx in (-16, -7.5, 8.5, 18):
        make_box(f"LampPoleN_{sx}", (sx, -5.3, 3.6), (0.24, 0.24, 7.2), m_pole, col)
        make_box(f"LampArmN_{sx}", (sx, -4.6, 7.1), (0.22, 1.5, 0.20), m_pole, col)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.42, location=(sx, -4.0, 6.85))
        b = sc._link_only(bpy.context.active_object, col)
        b.data.materials.append(m_lamp)
    # Red fire hydrant
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.28, depth=1.1, location=(5.6, -5.35, 0.55))
    hyd = sc._link_only(bpy.context.active_object, col)
    hyd.data.materials.append(sc.make_mat("Mat_Hydrant", "#DC2626", rough=0.35))

    # Fluffy white clouds in sky
    for i, (cx, cy, cz, cs) in enumerate([
        (-16, -24, 18, 1.5), (4, -28, 20, 1.8), (22, -22, 17, 1.4), (-8, 24, 19, 1.6), (16, 26, 20, 1.5)
    ]):
        build_cloud(f"Cloud_{i}", (cx, cy, cz), col, scale=cs)

    # Two cars (parked safely away during intro, positioned for b10b_arguing_traffic & b12 launch!)
    car_red = build_car("Car_Red", (9.2, -2.0, -0.06), "#DC2626", col, yaw_deg=0.0)
    car_blue = build_car("Car_Blue", (15.4, -2.0, -0.06), "#2563EB", col, yaw_deg=180.0)

    # Dog + Gravity Arrows
    dog = build_dog("Prop_Dog", (-5.2, -6.2, 0.0), col, yaw_deg=180.0)
    grav = build_gravity_arrows(col)

    # Cast in Set 1: Main 2 R6 (Alex & Noob preserved verbatim) + 6 Grounded IRL Background R6
    cast_col = bpy.data.collections.new("Set1_Cast")
    col.children.link(cast_col)

    alex = sc.append_r6_character("01_Alex_Protagonist", "Alex", cast_col)
    noob = sc.append_r6_character("02_Noob_BestFriend", "Noob", cast_col)

    bg_dogwalker = sc.append_r6_character(
        "01_Alex_Protagonist", "BG_DogWalker", cast_col,
        atlas_filename="bg_dogwalker_atlas.png", strip_all_default_acc=True, keep_acc=("pal_hair",), hair_tint_hex="#3E281B",
    )
    bg_woman_pink = sc.append_r6_character(
        "04_Maya_BestFriend", "BG_WomanPink", cast_col,
        atlas_filename="bg_woman_pink_atlas.png", strip_all_default_acc=True, keep_acc=("roblox_girl_hair",),
    )
    bg_dad_plaid = sc.append_r6_character(
        "05_Dad_Principal", "BG_DadPlaid", cast_col,
        atlas_filename="bg_dad_plaid_atlas.png", strip_all_default_acc=True, keep_acc=("shaggy",),
    )
    bg_neighbor_green = sc.append_r6_character(
        "01_Alex_Protagonist", "BG_NeighborGreen", cast_col,
        atlas_filename="bg_neighbor_green_atlas.png", strip_all_default_acc=True, keep_acc=("pal_hair",), hair_tint_hex="#1C1917",
    )
    bg_friend_coral = sc.append_r6_character(
        "02_Noob_BestFriend", "BG_FriendCoral", cast_col,
        atlas_filename="bg_friend_coral_atlas.png", strip_all_default_acc=True, extra_acc_key="brown_charmer_hair", hair_tint_hex="#261A14",
    )
    bg_woman_jacket = sc.append_r6_character(
        "04_Maya_BestFriend", "BG_WomanJacket", cast_col,
        atlas_filename="bg_woman_jacket_atlas.png", strip_all_default_acc=True, keep_acc=("chestnut_bun",),
    )

    # Attach white Tax Envelope cleanly via CHILD_OF to BG_DadPlaid's Right Arm (never floating!)
    tax_env = make_box("Prop_TaxEnvelope", (0.0, 0.0, 0.0), (0.95, 0.08, 0.65), sc.make_mat("Mat_TaxEnv", "#F8FAFC", rough=0.5), col)
    tax_stripe = make_box("Prop_TaxRed", (0.0, 0.045, 0.0), (0.68, 0.02, 0.16), sc.make_mat("Mat_TaxRed", "#EF4444", rough=0.45), col)
    tax_stripe.parent = tax_env
    # Position in rig space at Right Arm bottom/hand area (-1.5, 0.55, 2.2) before CHILD_OF
    tax_env.location = (-1.52, 0.62, 2.25)
    tax_env.rotation_euler = (math.radians(20), 0.0, math.radians(-10))
    c_tax = tax_env.constraints.new("CHILD_OF")
    c_tax.target = bg_dad_plaid["internal_arm"]
    c_tax.subtarget = "Right Arm"
    rarm_mesh = next(o for o in bg_dad_plaid["objects"] if o.type == "MESH" and o.name.startswith("Right Arm"))
    for rc in rarm_mesh.constraints:
        if rc.type == "CHILD_OF" and rc.target == bg_dad_plaid["internal_arm"] and rc.subtarget == "Right Arm":
            c_tax.inverse_matrix = rc.inverse_matrix.copy()
            break

    # Dog leash attached via CHILD_OF to BG_DogWalker's Right Arm hand tip (-1.5, 0, 2.0 in rig coords)
    leash = make_box("Prop_Leash", (-1.1, 1.05, 1.55), (0.05, 2.2, 0.05), sc.make_mat("Mat_Leash", "#78350F", rough=0.6), col, rot=(math.radians(-22), 0, math.radians(-18)))
    c_lsh = leash.constraints.new("CHILD_OF")
    c_lsh.target = bg_dogwalker["internal_arm"]
    c_lsh.subtarget = "Right Arm"
    dw_rarm = next(o for o in bg_dogwalker["objects"] if o.type == "MESH" and o.name.startswith("Right Arm"))
    for rc in dw_rarm.constraints:
        if rc.type == "CHILD_OF" and rc.target == bg_dogwalker["internal_arm"] and rc.subtarget == "Right Arm":
            c_lsh.inverse_matrix = rc.inverse_matrix.copy()
            break

    # Lighting for Set 1 (Crisp @huss.hero Sun + Soft Front Fill)
    lcol = bpy.data.collections.new("Set1_Lights")
    col.children.link(lcol)
    sun_d = bpy.data.lights.new("Sun_Town", type="SUN")
    sun_d.energy = 3.2
    sun_d.angle = math.radians(1.6)
    sun = bpy.data.objects.new("Sun_Town", sun_d)
    lcol.objects.link(sun)
    sun.rotation_euler = (math.radians(44), math.radians(-16), math.radians(26))

    fill_d = bpy.data.lights.new("Fill_Town", type="AREA")
    fill_d.energy = 680
    fill_d.size = 10.0
    fill_d.color = bcl.hex_to_linear("#F8FBFF")[:3]
    fill = bpy.data.objects.new("Fill_Town", fill_d)
    lcol.objects.link(fill)
    fill.location = (0, 14.0, 9.0)
    fill.rotation_euler = (Vector((0, 0, 2.8)) - fill.location).to_track_quat("-Z", "Y").to_euler()

    return {
        "col": col, "win_mat": m_win, "lamp_mat": m_lamp, "sun": sun, "fill": fill,
        "car_red": car_red, "car_blue": car_blue, "dog": dog, "grav": grav,
        "tax_env": tax_env, "leash": leash,
        "alex": alex, "noob": noob,
        "bg": [bg_dogwalker, bg_woman_pink, bg_dad_plaid, bg_neighbor_green, bg_friend_coral, bg_woman_jacket],
        "bg_dogwalker": bg_dogwalker, "bg_woman_pink": bg_woman_pink, "bg_dad_plaid": bg_dad_plaid,
        "bg_neighbor_green": bg_neighbor_green, "bg_friend_coral": bg_friend_coral, "bg_woman_jacket": bg_woman_jacket,
    }


def build_set2_space(scene):
    """Set 2: Cosmic Roblox Planet Earth + Giant Burning Sun + Expanding Infinite Void at X = 160."""
    col = bpy.data.collections.new("Set2_SpaceOrbit")
    scene.collection.children.link(col)
    OX = 160.0

    # Earth Root at (160, 0, 0)
    earth_root = bpy.data.objects.new("EarthRoot", None)
    earth_root.location = (OX, 0.0, 0.0)
    col.objects.link(earth_root)

    m_ocean = sc.make_mat("Mat_EarthOcean", "#2563EB", rough=0.30, coat=0.25)
    m_land = sc.make_mat("Mat_EarthLand", "#22C55E", rough=0.55)
    m_ice = sc.make_mat("Mat_EarthIce", "#F8FAFC", rough=0.45)
    m_cloud = sc.make_mat("Mat_SpaceCloud", "#FFFFFF", rough=0.75, emit_hex="#FFFFFF", emit_str=0.25)

    R_EARTH = 6.4
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=R_EARTH, location=(0, 0, 0))
    ocean = sc._link_only(bpy.context.active_object, col)
    ocean.name = "Earth_Ocean"
    ocean.data.materials.append(m_ocean)
    ocean.parent = earth_root

    # Raised blocky green continents & polar ice caps
    rng = random.Random(77)
    land_patches = [
        (0, 0, 2.2), (20, 12, 1.8), (-24, 15, 2.0), (55, -18, 2.4), (115, 22, 2.1),
        (165, -8, 2.5), (-110, 10, 2.3), (-155, -20, 1.9), (75, 32, 1.7), (-60, -30, 2.0),
    ]
    for i, (lon_d, lat_d, rad) in enumerate(land_patches):
        lon, lat = math.radians(lon_d), math.radians(lat_d)
        px = R_EARTH * math.cos(lat) * math.cos(lon)
        py = R_EARTH * math.cos(lat) * math.sin(lon)
        pz = R_EARTH * math.sin(lat)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=rad, location=(px * 0.94, py * 0.94, pz * 0.94))
        lp = sc._link_only(bpy.context.active_object, col)
        lp.name = f"Earth_Land_{i}"
        lp.scale = (1.0, 1.0, 0.55)
        lp.rotation_euler = Vector((px, py, pz)).to_track_quat("Z", "Y").to_euler()
        lp.data.materials.append(m_land)
        lp.parent = earth_root

    for pole_z in (R_EARTH * 0.92, -R_EARTH * 0.92):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=2.1, location=(0, 0, pole_z))
        ic = sc._link_only(bpy.context.active_object, col)
        ic.scale = (1.1, 1.1, 0.48)
        ic.data.materials.append(m_ice)
        ic.parent = earth_root

    # Tiny suburban houses & trees seated squarely on North Pole cap (top ~6.85)
    for idx, (lx, ly, lz, hcol) in enumerate([(-1.05, -0.45, 6.72, "#F5D04C"), (1.15, -0.35, 6.68, "#F2A2C8"), (0.10, -1.25, 6.65, "#8ABDF7")]):
        hm = sc.make_mat(f"Mat_TinyH_{idx}", hcol, rough=0.5)
        hb = make_box(f"TinyHouse_{idx}", (lx, ly, lz), (0.65, 0.65, 0.65), hm, col)
        hb.rotation_euler = Vector((lx, ly, lz)).to_track_quat("Z", "Y").to_euler()
        hb.parent = earth_root

    # Equatorial white spin streaks around Earth
    streak_mat = sc.make_mat("Mat_SpinStreak", "#E0F2FE", rough=0.3, emit_hex="#BAE6FD", emit_str=2.2)
    spin_rings = bpy.data.objects.new("Earth_SpinStreaks", None)
    spin_rings.location = (OX, 0, 0)
    col.objects.link(spin_rings)
    for idx in range(5):
        bpy.ops.mesh.primitive_torus_add(major_radius=7.4 + idx * 0.45, minor_radius=0.06, major_segments=48, minor_segments=6, location=(0, 0, -1.6 + idx * 0.8))
        sr = sc._link_only(bpy.context.active_object, col)
        sr.scale = (1.0, 1.0, 0.35)
        sr.data.materials.append(streak_mat)
        sr.parent = spin_rings

    # Giant Burning Sun Rock at (OX - 44, -36, 4)
    SUN_POS = Vector((OX - 44.0, -36.0, 4.0))
    sun_root = bpy.data.objects.new("SunRoot", None)
    sun_root.location = SUN_POS
    col.objects.link(sun_root)
    m_sun = sc.make_mat("Mat_SunCore", "#FACC15", rough=0.3, emit_hex="#FB923C", emit_str=3.8)
    m_sun_crust = sc.make_mat("Mat_SunCrust", "#EA580C", rough=0.4, emit_hex="#F97316", emit_str=2.4)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=12.5, location=(0, 0, 0))
    sun_core = sc._link_only(bpy.context.active_object, col)
    sun_core.data.materials.append(m_sun)
    sun_core.parent = sun_root
    for i in range(8):
        ang = i * math.pi * 0.25
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=3.6, location=(math.cos(ang) * 10.2, math.sin(ang) * 10.2, (i % 3 - 1) * 3.8))
        sc_p = sc._link_only(bpy.context.active_object, col)
        sc_p.data.materials.append(m_sun_crust)
        sc_p.parent = sun_root

    # Glowing 67,000 MPH Orbit Arc Ring centered on Sun passing through Earth
    R_ORBIT = (Vector((OX, 0, 0)) - SUN_POS).length
    bpy.ops.mesh.primitive_torus_add(major_radius=R_ORBIT, minor_radius=0.22, major_segments=96, minor_segments=8, location=SUN_POS)
    orbit_ring = sc._link_only(bpy.context.active_object, col)
    orbit_ring.name = "OrbitArc"
    orbit_ring.rotation_euler = (math.radians(-4), math.radians(3), 0)
    orbit_ring.data.materials.append(sc.make_mat("Mat_OrbitRing", "#38BDF8", emit_hex="#38BDF8", emit_str=2.6))

    # Infinitely expanding void concentric boundary rings
    void_rings = []
    m_void = sc.make_mat("Mat_VoidGrid", "#60A5FA", emit_hex="#93C5FD", emit_str=1.9)
    for i in range(8):
        bpy.ops.mesh.primitive_torus_add(major_radius=24.0 + i * 11.0, minor_radius=0.14, major_segments=64, minor_segments=6, location=(OX - 16, -12, 0))
        vr = sc._link_only(bpy.context.active_object, col)
        vr.rotation_euler = (math.radians(72), math.radians(14), 0)
        vr.data.materials.append(m_void)
        void_rings.append(vr)

    # 300 Crisp White/Blue Starfield Dots surrounding Set 2
    m_star = sc.make_mat("Mat_StarDot", "#FFFFFF", emit_hex="#FFFFFF", emit_str=3.2)
    for i in range(280):
        th = rng.uniform(0, 2 * math.pi)
        ph = math.acos(rng.uniform(-1, 1))
        rad = rng.uniform(42, 95)
        sx = OX + rad * math.sin(ph) * math.cos(th)
        sy = rad * math.sin(ph) * math.sin(th)
        sz = rad * math.cos(ph)
        make_box(f"Star_{i}", (sx, sy, sz), (0.28, 0.28, 0.28), m_star, col)

    # Tiny Alex & Noob standing on top of spinning Earth
    cast2 = bpy.data.collections.new("Set2_TinyCast")
    col.children.link(cast2)
    alex_tiny = sc.append_r6_character("01_Alex_Protagonist", "Alex_Tiny", cast2)
    noob_tiny = sc.append_r6_character("02_Noob_BestFriend", "Noob_Tiny", cast2)

    # Space lighting (Warm solar key + bright front cosmic fill + cool rim so Earth & riders pop brightly!)
    lcol = bpy.data.collections.new("Set2_Lights")
    col.children.link(lcol)
    sol_d = bpy.data.lights.new("Sun_SpaceKey", type="POINT")
    sol_d.energy = 140000.0
    sol_d.color = bcl.hex_to_linear("#FFE6B3")[:3]
    sol_l = bpy.data.objects.new("Sun_SpaceKey", sol_d)
    sol_l.location = (OX - 26, -22, 8)
    lcol.objects.link(sol_l)

    sfill_d = bpy.data.lights.new("Space_FrontFill", type="AREA")
    sfill_d.energy = 8500.0
    sfill_d.size = 24.0
    sfill_d.color = bcl.hex_to_linear("#E0F2FE")[:3]
    sfill_l = bpy.data.objects.new("Space_FrontFill", sfill_d)
    sfill_l.location = (OX + 4, 24, 12)
    sfill_l.rotation_euler = (Vector((OX, 0, 2)) - sfill_l.location).to_track_quat("-Z", "Y").to_euler()
    lcol.objects.link(sfill_l)

    rim_d = bpy.data.lights.new("Space_Rim", type="AREA")
    rim_d.energy = 2800.0
    rim_d.size = 18.0
    rim_d.color = bcl.hex_to_linear("#93C5FD")[:3]
    rim_l = bpy.data.objects.new("Space_Rim", rim_d)
    rim_l.location = (OX + 20, 18, 16)
    rim_l.rotation_euler = (Vector((OX, 0, 4)) - rim_l.location).to_track_quat("-Z", "Y").to_euler()
    lcol.objects.link(rim_l)

    return {
        "col": col, "ox": OX, "r_earth": R_EARTH, "earth_root": earth_root,
        "spin_rings": spin_rings, "sun_root": sun_root, "sun_pos": SUN_POS,
        "orbit_ring": orbit_ring, "void_rings": void_rings,
        "alex_tiny": alex_tiny, "noob_tiny": noob_tiny,
    }


def coaster_track_pos(y_val: float, ox: float = -160.0) -> tuple[Vector, float]:
    """Smooth banked rollercoaster spline along +Y."""
    x = ox + 3.2 * math.sin(y_val * 0.08)
    z = 2.0 + 1.2 * math.sin(y_val * 0.11)
    dx_dy = 3.2 * 0.08 * math.cos(y_val * 0.08)
    yaw = math.degrees(math.atan2(-dx_dy, 1.0))
    return Vector((x, y_val, z)), yaw


def build_set3_analogy(scene):
    """Set 3: Merry-Go-Round Strapped to a Rollercoaster in an Infinite Pitch-Black Lobby at X = -160."""
    col = bpy.data.collections.new("Set3_AnalogyLobby")
    scene.collection.children.link(col)
    OX = -160.0

    m_rail = sc.make_mat("Mat_CoasterRail", "#CBD5E1", rough=0.25, metal=0.65)
    m_tie = sc.make_mat("Mat_CoasterTie", "#EF4444", rough=0.35)
    m_cart_y = sc.make_mat("Mat_CartYellow", "#FACC15", rough=0.32, coat=0.35)
    m_cart_b = sc.make_mat("Mat_CartBlue", "#2563EB", rough=0.32, coat=0.35)
    m_mgr_red = sc.make_mat("Mat_MgrRed", "#EF4444", rough=0.35, coat=0.30)
    m_mgr_blu = sc.make_mat("Mat_MgrBlue", "#3B82F6", rough=0.35, coat=0.30)
    m_arch = sc.make_mat("Mat_LobbyArch", "#E0F2FE", emit_hex="#BAE6FD", emit_str=2.6)

    # Track beams & ties from y=-35 to y=+65
    for y_step in range(-32, 64, 2):
        p0, yaw0 = coaster_track_pos(float(y_step), OX)
        p1, _ = coaster_track_pos(float(y_step + 2), OX)
        mid = (p0 + p1) * 0.5
        seg_len = (p1 - p0).length
        ang_z = math.atan2(p1.y - p0.y, p1.x - p0.x) - math.pi * 0.5
        ang_x = math.atan2(p1.z - p0.z, math.hypot(p1.x - p0.x, p1.y - p0.y))
        tie = make_box(f"Tie_{y_step}", (mid.x, mid.y, mid.z - 0.15), (2.4, 0.32, 0.18), m_tie, col, rot=(ang_x, 0, ang_z))
        for rx in (-0.95, 0.95):
            rpos = mid + Vector((math.cos(ang_z) * rx, math.sin(ang_z) * rx, 0.05))
            make_box(f"Rail_{y_step}_{rx}", rpos, (0.20, seg_len + 0.15, 0.22), m_rail, col, rot=(ang_x, 0, ang_z))
        if y_step % 6 == 0:
            make_box(f"Pylon_{y_step}", (mid.x, mid.y, mid.z * 0.5 - 3.0), (0.35, 0.35, mid.z + 6.0), m_tie, col)

    # Stretching infinite lobby neon frame arches along track
    arches = []
    for i in range(16):
        ay = -18.0 + i * 5.8
        ar = bpy.data.objects.new(f"LobbyArch_{i}", None)
        ar.location = (OX, ay, 4.5)
        col.objects.link(ar)
        aw, ah = 14.0, 12.0
        make_box(f"ArchT_{i}", (0, 0,  ah * 0.5), (aw, 0.24, 0.24), m_arch, col).parent = ar
        make_box(f"ArchB_{i}", (0, 0, -ah * 0.5), (aw, 0.24, 0.24), m_arch, col).parent = ar
        make_box(f"ArchL_{i}", (-aw * 0.5, 0, 0), (0.24, 0.24, ah), m_arch, col).parent = ar
        make_box(f"ArchR_{i}", ( aw * 0.5, 0, 0), (0.24, 0.24, ah), m_arch, col).parent = ar
        arches.append(ar)

    # Rollercoaster Cart + Spinning Playground Merry-Go-Round bolted on top!
    cart_root = bpy.data.objects.new("CoasterCart", None)
    cart_root.location = (OX, 0.0, 2.0)
    col.objects.link(cart_root)
    make_box("CartBase", (0, 0, 0.55), (2.8, 3.6, 0.85), m_cart_y, col).parent = cart_root
    make_box("CartNose", (0, 1.95, 0.50), (2.5, 0.8, 0.72), m_cart_b, col).parent = cart_root

    mgr_deck = bpy.data.objects.new("MgrDeck", None)
    mgr_deck.location = (0, 0, 1.12)
    col.objects.link(mgr_deck)
    mgr_deck.parent = cart_root

    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=2.45, depth=0.22, location=(0, 0, 0.0))
    disc = sc._link_only(bpy.context.active_object, col)
    disc.data.materials.append(m_mgr_red)
    disc.parent = mgr_deck
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.18, depth=2.1, location=(0, 0, 1.05))
    pole = sc._link_only(bpy.context.active_object, col)
    pole.data.materials.append(m_rail)
    pole.parent = mgr_deck
    # Waist/chest grab ring & spokes (clear of character faces!)
    bpy.ops.mesh.primitive_torus_add(major_radius=1.85, minor_radius=0.07, major_segments=32, minor_segments=8, location=(0, 0, 1.95))
    ring = sc._link_only(bpy.context.active_object, col)
    ring.data.materials.append(m_mgr_blu)
    ring.parent = mgr_deck
    for k in range(4):
        ang = k * math.pi * 0.5
        hx, hy = math.cos(ang) * 0.92, math.sin(ang) * 0.92
        make_box(f"MgrBarH_{k}", (hx, hy, 1.95), (1.85, 0.12, 0.12), m_mgr_blu, col, rot=(0, 0, ang)).parent = mgr_deck
        make_box(f"MgrBarV_{k}", (math.cos(ang) * 1.85, math.sin(ang) * 1.85, 1.0), (0.12, 0.12, 1.95), m_rail, col).parent = mgr_deck

    # Alex & Noob riding on the Merry-Go-Round
    cast3 = bpy.data.collections.new("Set3_RideCast")
    col.children.link(cast3)
    alex_ride = sc.append_r6_character("01_Alex_Protagonist", "Alex_Ride", cast3)
    noob_ride = sc.append_r6_character("02_Noob_BestFriend", "Noob_Ride", cast3)

    # Set 3 lighting (bright key + cool rim so riders pop cleanly against the stretching black void!)
    lcol = bpy.data.collections.new("Set3_Lights")
    col.children.link(lcol)
    kl_d = bpy.data.lights.new("Ride_Key", type="AREA")
    kl_d.energy = 4200
    kl_d.size = 10.0
    kl = bpy.data.objects.new("Ride_Key", kl_d)
    kl.location = (OX + 7, 10, 12)
    kl.rotation_euler = (Vector((OX, 12, 4)) - kl.location).to_track_quat("-Z", "Y").to_euler()
    lcol.objects.link(kl)

    rl_d = bpy.data.lights.new("Ride_Rim", type="AREA")
    rl_d.energy = 3200
    rl_d.size = 10.0
    rl_d.color = bcl.hex_to_linear("#7DD3FC")[:3]
    rl = bpy.data.objects.new("Ride_Rim", rl_d)
    rl.location = (OX - 8, 22, 10)
    rl.rotation_euler = (Vector((OX, 12, 4)) - rl.location).to_track_quat("-Z", "Y").to_euler()
    lcol.objects.link(rl)

    return {
        "col": col, "ox": OX, "cart_root": cart_root, "mgr_deck": mgr_deck,
        "arches": arches, "key_light": kl, "rim_light": rl,
        "alex_ride": alex_ride, "noob_ride": noob_ride,
    }


def set_town_day_or_sunset(s1: dict, world_info: dict, sunset: bool):
    sc.set_world_mode(world_info, "sunset" if sunset else "day")
    if sunset:
        s1["sun"].data.energy = 2.0
        s1["sun"].data.color = bcl.hex_to_linear("#FF9A5C")[:3]
        s1["fill"].data.energy = 1050.0
        s1["fill"].data.color = bcl.hex_to_linear("#FFD4B8")[:3]
        for n in s1["win_mat"].node_tree.nodes:
            if n.type == "BSDF_PRINCIPLED":
                n.inputs["Emission Strength"].default_value = 2.6
        for n in s1["lamp_mat"].node_tree.nodes:
            if n.type == "BSDF_PRINCIPLED":
                n.inputs["Emission Strength"].default_value = 4.0
    else:
        s1["sun"].data.energy = 3.2
        s1["sun"].data.color = bcl.hex_to_linear("#FFFDF5")[:3]
        s1["fill"].data.energy = 780.0
        s1["fill"].data.color = bcl.hex_to_linear("#F8FBFF")[:3]
        for n in s1["win_mat"].node_tree.nodes:
            if n.type == "BSDF_PRINCIPLED":
                n.inputs["Emission Strength"].default_value = 0.0
        for n in s1["lamp_mat"].node_tree.nodes:
            if n.type == "BSDF_PRINCIPLED":
                n.inputs["Emission Strength"].default_value = 0.4


def place_background_crowd_default(s1: dict, t: float):
    """Place the 6 grounded IRL background characters cleanly on sidewalks with zero clipping."""
    # Move heroes safely aside by default so they never photobomb background-only cuts!
    sc.set_char_transform(s1["alex"], -28.0, 0.0, -0.06, 0.0)
    sc.set_char_transform(s1["noob"], -31.0, 0.0, -0.06, 0.0)

    # Dog walker + dog strolling along north sidewalk
    walk_x = -6.0 + (t % 8.0) * 0.45
    sc.set_char_transform(s1["bg_dogwalker"], walk_x, -6.4, 0.0, -90.0)
    sc.animate_walk(s1["bg_dogwalker"], t, phase=0.2, speed=4.8)
    s1["dog"]["root"].location = (walk_x + 1.8, -6.1, 0.0)
    s1["dog"]["root"].rotation_euler = (0, 0, math.radians(0.0))
    for i, lg in enumerate(s1["dog"]["legs"]):
        lg.rotation_euler = (0, math.sin(t * 7.0 + i * math.pi * 0.5) * 0.35, 0)

    sc.set_char_transform(s1["bg_woman_pink"], 6.2, -6.6, 0.0, 25.0)
    sc.animate_walk(s1["bg_woman_pink"], t, phase=1.4, speed=4.4)

    sc.set_char_transform(s1["bg_dad_plaid"], -10.5, -6.8, 0.0, 0.0)
    sc.animate_idle(s1["bg_dad_plaid"], t, phase=0.8)

    sc.set_char_transform(s1["bg_neighbor_green"], 11.2, -6.3, 0.0, -45.0)
    sc.animate_idle(s1["bg_neighbor_green"], t, phase=2.1)

    sc.set_char_transform(s1["bg_friend_coral"], 13.6, -6.3, 0.0, 45.0)
    sc.animate_idle(s1["bg_friend_coral"], t, phase=2.7)

    sc.set_char_transform(s1["bg_woman_jacket"], -13.5, 6.6, 0.0, 180.0)
    sc.animate_walk(s1["bg_woman_jacket"], t, phase=3.1, speed=4.2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stills", action="store_true", help="Render Gate-1 representative stills across all 17 cuts")
    parser.add_argument("--range", nargs=2, type=int, metavar=("START", "END"), help="Render specific frame range")
    args, _ = parser.parse_known_args(sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else [])

    bcl.clear_scene()
    scene = bpy.context.scene
    sc.configure_eevee(scene, res_x=720, res_y=1280, samples=10)
    world_info = sc.build_switchable_world(scene)

    beats_data = sc.load_beats()
    total_frames = int(math.ceil(beats_data["total_duration"] * sc.FPS))
    beats = beats_data["beats"]

    s1 = build_set1_town(scene)
    s2 = build_set2_space(scene)
    s3 = build_set3_analogy(scene)

    cam_d = bpy.data.cameras.new("Cam_Main")
    cam = bpy.data.objects.new("Cam_Main", cam_d)
    scene.collection.objects.link(cam)
    scene.camera = cam

    bcl.setup_cinema_compositor(
        scene,
        glare_threshold=1.55,
        glare_strength=0.16,
        dispersion=0.0008,
        distortion=0.0,
        lift_rgb=(0.995, 0.995, 1.0),
        gamma_rgb=(1.0, 1.0, 1.0),
        gain_rgb=(1.02, 1.02, 1.01),
        vignette=0.10,
    )

    # Map every frame 1..total_frames to its beat info
    beat_ranges = []
    for i, b in enumerate(beats):
        f0 = 1 if i == 0 else int(round(b["start"] * sc.FPS)) + 1
        f1 = total_frames if i + 1 == len(beats) else max(f0, int(round(beats[i + 1]["start"] * sc.FPS)))
        beat_ranges.append((b, f0, f1))

    # Build representative stills list if --stills
    still_targets = {}
    if args.stills:
        for b, f0, f1 in beat_ranges:
            bid = b["id"]
            if bid in ("b03_glue_force", "b05_orbit_sun", "b11_hit_brakes"):
                still_targets[f0 + int((f1 - f0) * 0.25)] = f"{bid}_a"
                still_targets[f0 + int((f1 - f0) * 0.78)] = f"{bid}_b"
            else:
                still_targets[(f0 + f1) // 2] = bid
        still_targets[1] = "frame_0001_hook"

    f_min = args.range[0] if args.range else 1
    f_max = args.range[1] if args.range else total_frames

    for b, f0, f1 in beat_ranges:
        bid = b["id"]
        frames_to_do = [f for f in range(f0, f1 + 1) if f_min <= f <= f_max]
        if args.stills:
            frames_to_do = [f for f in frames_to_do if f in still_targets]
        if not frames_to_do:
            continue

        # Configure set visibility & world sky once per beat
        is_set1 = b["shot"].startswith("set1")
        is_set2 = b["shot"] == "set2_space"
        is_set3 = b["shot"] == "set3_analogy"
        is_sunset = b["shot"] in ("set1_sunset", "set1_launch")

        s1["col"].hide_render = not is_set1
        s1["col"].hide_viewport = not is_set1
        s2["col"].hide_render = not is_set2
        s2["col"].hide_viewport = not is_set2
        s3["col"].hide_render = not is_set3
        s3["col"].hide_viewport = not is_set3

        if is_set1:
            set_town_day_or_sunset(s1, world_info, sunset=is_sunset)
        else:
            sc.set_world_mode(world_info, "space")

        for f in frames_to_do:
            u = (f - f0) / max(1, (f1 - f0))
            t = (f - 1) / float(sc.FPS)

            if is_set1:
                # Reset props visibility
                sc.set_hidden_tree(s1["grav"]["root"], bid != "b03_glue_force")
                sc.set_hidden_tree(s1["tax_env"], bid != "b10a_paying_taxes")
                sc.set_hidden_tree(s1["leash"], bid == "b12_launched_space")
                s1["car_red"].location = (8.2, -1.6, -0.06)
                s1["car_red"].rotation_euler = (0, 0, 0)
                s1["car_blue"].location = (14.4, -1.6, -0.06)
                s1["car_blue"].rotation_euler = (0, 0, math.radians(180))
                sc.swap_atlas(s1["alex"], "01_Alex_Protagonist_atlas.png")
                sc.swap_atlas(s1["noob"], "02_Noob_BestFriend_atlas.png")
                place_background_crowd_default(s1, t)

            if bid == "b01a_town_rock":
                # Frame 0 @huss.hero-inspired elevated suburban street with Alex & Noob waving (3.3m apart, zero arm overlap!)
                sc.set_char_transform(s1["alex"], -1.70, 0.2, -0.06, 8.0)
                sc.set_char_transform(s1["noob"],  1.70, 0.2, -0.06, -8.0)
                sc.set_char_pose(
                    s1["alex"],
                    torso_loc=(0, 0, 0.06 * abs(math.sin(t * 5))),
                    head_rot=(-6, 0, math.sin(t * 3) * 6),
                    rarm_rot=(-125 + math.sin(t * 8) * 16, 8, -10),
                    larm_rot=(10, -4, 8),
                )
                sc.set_char_pose(
                    s1["noob"],
                    torso_loc=(0, 0, 0.09 * abs(math.sin(t * 6 + 0.5))),
                    head_rot=(-8, 0, math.cos(t * 4) * 8),
                    rarm_rot=(-130 - math.sin(t * 9) * 18, 10, -10),
                    larm_rot=(-130 + math.sin(t * 9) * 18, -10, 10),
                )
                sc.set_camera_look(
                    cam,
                    (-0.6 + 0.7 * u, 11.4 - 2.4 * u, 6.2 - 2.5 * u),
                    (0.0, -0.5, 3.0 - 0.2 * u),
                    lens=30.0 + 3.5 * u,
                    roll_deg=-2.2 * (1.0 - u),
                )

            elif bid == "b01b_spin_1000":
                # Spinning Roblox Earth rock at 1,000 mph with tiny Alex & Noob planted cleanly on North Pole ice cap!
                sc.set_hidden_tree(s2["spin_rings"], False)
                sc.set_hidden_tree(s2["orbit_ring"], True)
                for vr in s2["void_rings"]:
                    sc.set_hidden_tree(vr, True)
                spin_yaw = u * 210.0
                tilt = Matrix.Rotation(math.radians(16.0), 4, "Y")
                spin = Matrix.Rotation(math.radians(spin_yaw), 4, "Z")
                earth_m = Matrix.Translation((s2["ox"], 0.0, 0.0)) @ tilt @ spin
                s2["earth_root"].matrix_world = earth_m
                s2["spin_rings"].rotation_euler = (0.0, math.radians(16.0), math.radians(-spin_yaw * 1.4))

                for ch, local_off, lyaw in [
                    (s2["alex_tiny"], Vector((-0.65, 0.85, 6.72)), 10.0),
                    (s2["noob_tiny"], Vector(( 0.65, 0.85, 6.72)), -10.0),
                ]:
                    wpos = earth_m @ local_off
                    sc.set_char_transform(ch, wpos.x, wpos.y, wpos.z, spin_yaw + lyaw, pitch_deg=10.0, roll_deg=-8.0, scale=0.28)
                    sc.set_char_pose(ch, rarm_rot=(-135, 10, -12), larm_rot=(-135, -10, 12))
                sc.set_camera_look(
                    cam,
                    (s2["ox"] - 2.2 + 4.4 * u, 19.5 - 2.0 * u, 10.2 - 0.8 * u),
                    (s2["ox"], 0.0, 2.8),
                    lens=30.0,
                    roll_deg=3.0 * math.sin(u * math.pi),
                )

            elif bid == "b02_no_guardrails":
                # Noob leans precariously over sidewalk edge checking for missing guardrails!
                sc.set_char_transform(s1["alex"], -1.6, -5.2, 0.0, 12.0)
                sc.set_char_transform(s1["noob"],  1.1, -5.0, 0.0, -6.0)
                sc.swap_atlas(s1["alex"], "alex_deadpan_atlas.png")
                sc.animate_idle(s1["alex"], t, head_yaw=-14.0)
                lean = 26.0 + 10.0 * math.sin(u * math.pi)
                sc.set_char_pose(
                    s1["noob"],
                    torso_loc=(0.0, 0.25, 0.0),
                    torso_rot=(lean, 0.0, 8.0 * math.sin(t * 5)),
                    head_rot=(18.0, 0.0, math.sin(t * 7) * 22.0),
                    rarm_rot=(-45.0, 18.0, -34.0),
                    larm_rot=(-45.0, -18.0, 34.0),
                )
                sc.set_camera_look(
                    cam,
                    (-0.4 + 1.4 * u, 2.4 - 1.2 * u, 2.7 + 0.4 * u),
                    (-0.1, -5.0, 2.9),
                    lens=30.0 + 3.0 * u,
                )

            elif bid == "b03_glue_force":
                # Split into 2 dynamic sub-cuts at u=0.55 ("gluing your shoes to the dirt")
                sc.set_char_transform(s1["alex"], -0.8, 0.0, -0.06, 6.0)
                sc.set_char_transform(s1["noob"],  1.5, -0.5, -0.06, -12.0)
                if u < 0.55:
                    sub_u = u / 0.55
                    sc.set_hidden_tree(s1["grav"]["root"], True)
                    hop_z = max(0.0, math.sin(sub_u * math.pi) * 0.62)
                    sc.set_char_transform(s1["alex"], -0.8, 0.0, -0.06 + hop_z, 6.0)
                    sc.set_char_pose(
                        s1["alex"],
                        torso_rot=(-6.0 * math.sin(sub_u * math.pi), 0, 0),
                        head_rot=(-8.0, 0, 0),
                        rarm_rot=(-105.0, 12, -22),
                        larm_rot=(-105.0, -12, 22),
                        rleg_loc=(0, 0, 0.30 * math.sin(sub_u * math.pi)),
                        lleg_loc=(0, 0, 0.22 * math.sin(sub_u * math.pi)),
                    )
                    sc.animate_idle(s1["noob"], t, head_yaw=14.0)
                    sc.set_camera_look(
                        cam,
                        (0.2 - 1.0 * sub_u, 10.2 - 1.4 * sub_u, 2.9 + 0.4 * sub_u),
                        (0.1, -0.2, 2.8),
                        lens=30.0,
                    )
                else:
                    sub_u = (u - 0.55) / 0.45
                    sc.set_hidden_tree(s1["grav"]["root"], False)
                    s1["grav"]["root"].location = (-0.8, 0.0, -0.06)
                    for idx, ar in enumerate(s1["grav"]["arrows"]):
                        ar.location.z = 1.6 - ((sub_u * 1.8 + idx * 0.2) % 1.0) * 1.1
                    sc.set_char_pose(
                        s1["alex"],
                        torso_loc=(0, 0, -0.18 * (1.0 - min(1.0, sub_u * 2.5))),
                        torso_rot=(8.0, 0, 0),
                        head_rot=(12.0, 0, 0),
                        rarm_rot=(20, 10, -18),
                        larm_rot=(20, -10, 18),
                    )
                    k_sh = int((u - 0.55) * (f1 - f0))
                    sc.set_camera_look(
                        cam,
                        (-2.4 + 0.8 * sub_u, 4.8 - 0.8 * sub_u, 0.9 + 0.3 * sub_u),
                        (-0.8, 0.0, 1.35),
                        lens=28.0,
                        shake_k=k_sh if k_sh < 7 else None,
                        shake_amp=0.10,
                    )

            elif bid == "b04_not_parked":
                # Tight Earth profile as glowing cyan orbit ring & speed streaks ignite!
                sc.set_hidden_tree(s2["spin_rings"], False)
                sc.set_hidden_tree(s2["orbit_ring"], False)
                for vr in s2["void_rings"]:
                    sc.set_hidden_tree(vr, True)
                spin_yaw = 210.0 + u * 160.0
                earth_m = Matrix.Translation((s2["ox"], 0.0, 0.0)) @ Matrix.Rotation(math.radians(16.0), 4, "Y") @ Matrix.Rotation(math.radians(spin_yaw), 4, "Z")
                s2["earth_root"].matrix_world = earth_m
                for ch, local_off in [(s2["alex_tiny"], Vector((-0.65, 0.85, 6.72)),), (s2["noob_tiny"], Vector((0.65, 0.85, 6.72)),)]:
                    wpos = earth_m @ local_off
                    sc.set_char_transform(ch, wpos.x, wpos.y, wpos.z, spin_yaw, scale=0.28)
                sc.set_camera_look(
                    cam,
                    (s2["ox"] + 15.0 - 2.5 * u, 11.5 - 1.5 * u, 5.2 + 0.8 * u),
                    (s2["ox"], 0.0, 0.4),
                    lens=32.0,
                    roll_deg=-5.0,
                )

            elif bid == "b05_orbit_sun":
                # Earth whipping along giant orbit ring around blazing Sun rock! (2 sub-cuts at u=0.50)
                sc.set_hidden_tree(s2["spin_rings"], True)
                sc.set_hidden_tree(s2["orbit_ring"], False)
                for vr in s2["void_rings"]:
                    sc.set_hidden_tree(vr, True)

                sun_c = s2["sun_pos"]
                r_vec = Vector((s2["ox"], 0.0, 0.0)) - sun_c
                ang_orb = -0.35 + u * 0.95
                rot_orb = Matrix.Rotation(ang_orb, 4, "Z")
                epos = sun_c + (rot_orb @ r_vec)
                earth_m = Matrix.Translation(epos) @ Matrix.Rotation(math.radians(t * 240.0), 4, "Z")
                s2["earth_root"].matrix_world = earth_m
                s2["sun_root"].rotation_euler = (0, 0, t * 0.4)
                for ch, off in [(s2["alex_tiny"], Vector((-0.65, 0.85, 6.72))), (s2["noob_tiny"], Vector((0.65, 0.85, 6.72)))]:
                    wpos = earth_m @ off
                    sc.set_char_transform(ch, wpos.x, wpos.y, wpos.z, t * 240.0, scale=0.28)

                if u < 0.50:
                    sub_u = u / 0.50
                    sc.set_camera_look(
                        cam,
                        (epos.x + 14.0, epos.y + 22.0 - 6.0 * sub_u, 14.0 - 2.0 * sub_u),
                        ((epos.x + sun_c.x) * 0.5, (epos.y + sun_c.y) * 0.5, 2.0),
                        lens=26.0,
                        roll_deg=-4.0,
                    )
                else:
                    sub_u = (u - 0.50) / 0.50
                    sc.set_camera_look(
                        cam,
                        (epos.x - 10.0 + 2.0 * sub_u, epos.y + 22.0 - 3.0 * sub_u, 11.5 - 1.5 * sub_u),
                        (sun_c.x * 0.30 + epos.x * 0.70, sun_c.y * 0.30 + epos.y * 0.70, 2.0),
                        lens=23.0 + 2.0 * sub_u,
                        roll_deg=5.0,
                    )

            elif bid == "b06_expanding_void":
                # Dramatic pull-back revealing solar system inside expanding concentric space rings!
                sc.set_hidden_tree(s2["spin_rings"], True)
                sc.set_hidden_tree(s2["orbit_ring"], False)
                for idx, vr in enumerate(s2["void_rings"]):
                    sc.set_hidden_tree(vr, False)
                    sc_val = 1.0 + u * (0.45 + idx * 0.08)
                    vr.scale = (sc_val, sc_val, sc_val)
                sun_c = s2["sun_pos"]
                s2["earth_root"].matrix_world = Matrix.Translation((s2["ox"], 0, 0)) @ Matrix.Rotation(math.radians(t * 240.0), 4, "Z")
                sc.set_char_transform(s2["alex_tiny"], s2["ox"] - 0.65, 0.85, 6.72, 0, scale=0.28)
                sc.set_char_transform(s2["noob_tiny"], s2["ox"] + 0.65, 0.85, 6.72, 0, scale=0.28)
                sc.set_camera_look(
                    cam,
                    (s2["ox"] - 6.0 - 18.0 * u, 28.0 + 36.0 * u, 18.0 + 22.0 * u),
                    ((s2["ox"] + sun_c.x) * 0.5, (sun_c.y) * 0.5, 2.0),
                    lens=24.0 - 3.0 * u,
                )

            elif bid == "b07_merry_go_round":
                # Alex & Noob standing at lx=+-1.72 leaning outward slightly with clear headroom!
                cart_y = -6.0 + u * 26.0
                cpos, cyaw = coaster_track_pos(cart_y, s3["ox"])
                s3["cart_root"].location = cpos
                s3["cart_root"].rotation_euler = (0, 0, math.radians(cyaw))
                spin_rad = 0.6 + u * 3.8
                s3["mgr_deck"].rotation_euler = (0, 0, spin_rad)

                deck_m = Matrix.Translation(cpos) @ Matrix.Rotation(math.radians(cyaw), 4, "Z") @ Matrix.Translation((0, 0, 1.23)) @ Matrix.Rotation(spin_rad, 4, "Z")
                for ch, lx, ly, lyaw in [(s3["alex_ride"], 1.72, 0.0, 90.0), (s3["noob_ride"], -1.72, 0.0, -90.0)]:
                    wpos = deck_m @ Vector((lx, ly, 0.0))
                    sc.set_char_transform(ch, wpos.x, wpos.y, wpos.z, cyaw + math.degrees(spin_rad) + lyaw)
                    sc.set_char_pose(
                        ch,
                        torso_rot=(8.0, 0.0, 0.0),
                        head_rot=(-4.0, 0.0, math.sin(t * 7.0) * 10.0),
                        rarm_rot=(-56.0, 8.0, -8.0),
                        larm_rot=(-56.0, -8.0, 8.0),
                    )
                s3["key_light"].location = (cpos.x + 6, cpos.y + 8, 12)
                sc.set_camera_look(
                    cam,
                    (cpos.x + 6.4 - 1.6 * u, cpos.y + 9.2, cpos.z + 4.4 - 0.5 * u),
                    (cpos.x, cpos.y, cpos.z + 3.2),
                    lens=28.0,
                    roll_deg=5.0 * math.sin(u * math.pi),
                )

            elif bid == "b08_stretching_lobby":
                cart_y = 20.0 + u * 26.0
                cpos, cyaw = coaster_track_pos(cart_y, s3["ox"])
                s3["cart_root"].location = cpos
                s3["cart_root"].rotation_euler = (0, 0, math.radians(cyaw))
                spin_rad = 4.4 + u * 4.2
                s3["mgr_deck"].rotation_euler = (0, 0, spin_rad)
                for idx, ar in enumerate(s3["arches"]):
                    stretch = 1.0 + u * (0.40 + idx * 0.06)
                    ar.scale = (stretch, 1.0, stretch)

                deck_m = Matrix.Translation(cpos) @ Matrix.Rotation(math.radians(cyaw), 4, "Z") @ Matrix.Translation((0, 0, 1.23)) @ Matrix.Rotation(spin_rad, 4, "Z")
                for ch, lx, ly, lyaw in [(s3["alex_ride"], 1.72, 0.0, 90.0), (s3["noob_ride"], -1.72, 0.0, -90.0)]:
                    wpos = deck_m @ Vector((lx, ly, 0.0))
                    sc.set_char_transform(ch, wpos.x, wpos.y, wpos.z, cyaw + math.degrees(spin_rad) + lyaw)
                    sc.set_char_pose(ch, torso_rot=(8, 0, 0), rarm_rot=(-58, 8, -8), larm_rot=(-58, -8, 8))
                sc.set_camera_look(
                    cam,
                    (cpos.x - 2.2, cpos.y - 13.0 - 3.0 * u, cpos.z + 5.8 + 1.2 * u),
                    (s3["ox"] + 0.5, cpos.y + 16.0, 4.4),
                    lens=24.0,
                    roll_deg=-5.0,
                )

            elif bid == "b09_casual_dog":
                # Sunny @huss.hero street: IRL dog walker 3/4 toward camera walking blocky golden dog!
                dx = -4.2 + u * 2.2
                sc.set_char_transform(s1["bg_dogwalker"], dx, -6.4, 0.0, -38.0)
                sc.animate_walk(s1["bg_dogwalker"], t, speed=4.6)
                # Override right arm slightly forward to hold leash
                sc.set_char_pose(s1["bg_dogwalker"], rarm_rot=(-34.0, 6.0, -10.0))
                s1["dog"]["root"].location = (dx + 2.0, -5.6, 0.0)
                s1["dog"]["root"].rotation_euler = (0, 0, math.radians(15.0))
                for i, lg in enumerate(s1["dog"]["legs"]):
                    lg.rotation_euler = (0, math.sin(t * 7.5 + i * 1.57) * 0.35, 0)
                # Keep Noob cleanly clear of frame edge
                sc.set_char_transform(s1["noob"], -18.0, -6.8, 0.0, 0.0)
                sc.set_camera_look(
                    cam,
                    (dx + 0.8, 2.8 - 1.4 * u, 2.8),
                    (dx + 0.9, -6.0, 2.2),
                    lens=32.0,
                )

            elif bid == "b10a_paying_taxes":
                sc.set_char_transform(s1["bg_dad_plaid"], -10.5, -6.8, 0.0, 6.0)
                sc.set_char_pose(
                    s1["bg_dad_plaid"],
                    torso_loc=(0, 0, 0.03 * math.sin(t * 4)),
                    head_rot=(10.0, 0, math.sin(t * 6) * 5.0),
                    rarm_rot=(-78.0, -10.0, 26.0),
                    larm_rot=(8.0, -6.0, 8.0),
                )
                sc.set_camera_look(
                    cam,
                    (-10.1 + 0.4 * u, 0.8 - 1.2 * u, 3.0),
                    (-10.5, -6.8, 2.9),
                    lens=32.0 + 3.0 * u,
                )

            elif bid == "b10b_arguing_traffic":
                # Two IRL neighbors arguing FACE-TO-FACE in front of the red & blue cars!
                sc.set_char_transform(s1["bg_neighbor_green"], 10.1, 1.4, -0.06,  68.0)
                sc.set_char_transform(s1["bg_friend_coral"],   12.5, 1.4, -0.06, -68.0)
                sc.animate_argue(s1["bg_neighbor_green"], t, phase=0.0)
                sc.animate_argue(s1["bg_friend_coral"],   t, phase=1.8)
                sc.set_camera_look(
                    cam,
                    (11.3, 9.2 - 1.4 * u, 3.3),
                    (11.3, -0.4, 2.4),
                    lens=30.0,
                )

            elif bid == "b11_hit_brakes":
                # Dramatic @huss.hero Sunset-Red shift! Separate Alex & Noob to +-1.65 (zero arm overlap!)
                sc.set_char_transform(s1["alex"], -1.65, 0.0, -0.06, 6.0)
                sc.set_char_transform(s1["noob"],  1.65, 0.0, -0.06, -6.0)
                if u < 0.45:
                    sub_u = u / 0.45
                    sc.swap_atlas(s1["alex"], "alex_determined_atlas.png")
                    sc.set_char_pose(s1["alex"], torso_rot=(-5, 0, 0), head_rot=(-4, 0, -6), rarm_rot=(-25, 10, -16))
                    sc.set_char_pose(s1["noob"], torso_rot=(-5, 0, 0), head_rot=(-6, 0, 8), larm_rot=(-25, -10, 16))
                    sc.set_camera_look(
                        cam,
                        (0.0, 9.8 - 2.0 * sub_u, 3.1),
                        (0.0, 0.0, 3.2),
                        lens=30.0 + 3.0 * sub_u,
                        roll_deg=-6.0,
                    )
                else:
                    sub_u = (u - 0.45) / 0.55
                    sc.swap_atlas(s1["alex"], "alex_shocked_atlas.png")
                    sc.swap_atlas(s1["noob"], "02_Noob_Shocked_atlas.png")
                    sc.set_char_pose(s1["alex"], torso_rot=(-10, 0, 0), head_rot=(-12, 0, 0), rarm_rot=(-115, 12, -16), larm_rot=(-115, -12, 16))
                    sc.set_char_pose(s1["noob"], torso_rot=(-10, 0, 0), head_rot=(-12, 0, 0), rarm_rot=(-120, 12, -16), larm_rot=(-120, -12, 16))
                    k_sh = int((u - 0.45) * (f1 - f0))
                    sc.set_camera_look(
                        cam,
                        (0.0, 9.2 - 1.4 * sub_u, 3.3),
                        (0.0, 0.0, 3.4),
                        lens=30.0 + 3.0 * sub_u,
                        roll_deg=6.5,
                        shake_k=k_sh if k_sh < 7 else None,
                        shake_amp=0.14,
                    )

            elif bid == "b12_launched_space":
                # PAYOFF: Widely spread clean silhouettes launching sideways into the sunset-to-space sky!
                sc.swap_atlas(s1["alex"], "alex_shocked_atlas.png")
                sc.swap_atlas(s1["noob"], "02_Noob_Shocked_atlas.png")
                launch_d = (u ** 1.2) * 14.0
                sc.set_char_transform(s1["alex"], -2.2 + launch_d * 0.72, 0.5, 1.2 + launch_d * 0.55, 18.0 + u * 210, pitch_deg=u * 130, roll_deg=-u * 80)
                sc.set_char_transform(s1["noob"],  2.6 + launch_d * 0.90, -0.5, 2.0 + launch_d * 0.72, -20.0 - u * 240, pitch_deg=-u * 150, roll_deg=u * 100)
                for ch in (s1["alex"], s1["noob"]):
                    sc.set_char_pose(ch, rarm_rot=(-155, 22, -32), larm_rot=(-155, -22, 32), rleg_loc=(0, 0.35, 0.35), lleg_loc=(0, -0.35, 0.25))

                bg_offsets = [(-9.5, -5.0, 0.6), (-5.5, -6.5, 2.2), (6.0, -5.8, 1.2), (10.5, -6.5, 2.8), (-1.5, -7.2, 3.6), (14.5, -5.2, 0.8)]
                for idx, ch in enumerate(s1["bg"]):
                    bx0, by0, bz0 = bg_offsets[idx]
                    ld = (u ** 1.2) * (10.0 + idx * 1.4)
                    sc.set_char_transform(ch, bx0 + ld * 0.82, by0, bz0 + ld * 0.58, idx * 45 + u * 180, pitch_deg=u * 120, roll_deg=u * 80)
                    sc.set_char_pose(ch, rarm_rot=(-145, 20, -25), larm_rot=(-145, -20, 25))
                s1["car_red"].location = (9.5 + launch_d * 0.95, -2.2, 1.2 + launch_d * 0.62)
                s1["car_red"].rotation_euler = (math.radians(-u * 55), math.radians(-u * 40), math.radians(u * 90))
                s1["dog"]["root"].location = (-6.5 + launch_d * 0.78, -3.5, 1.4 + launch_d * 0.68)
                s1["dog"]["root"].rotation_euler = (math.radians(u * 110), math.radians(-u * 75), 0)

                k_sh = f - f0
                sc.set_camera_look(
                    cam,
                    (0.5 + 2.5 * u, 11.4 + 1.8 * u, 2.2),
                    (2.0 + 6.5 * u, -1.5, 4.4 + 6.5 * u),
                    lens=24.0,
                    roll_deg=-7.5 * (1.0 - u),
                    shake_k=k_sh if k_sh < 7 else None,
                    shake_amp=0.20,
                )

            bpy.context.view_layer.update()
            tag = still_targets.get(f) if args.stills else None
            sc.render_frame(scene, f, preview_tag=tag)

    print("build_scene.py COMPLETE!")


if __name__ == "__main__":
    main()
