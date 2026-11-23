"""
build_scene.py — Track 7 Undershine 3D Pixel Art Demo Scene in Blender 4.2 EEVEE Next.

Builds a lush, non-arcady 3D pixel-art valley (terraced cliffs, cascading waterfall,
winding shadow-receiving river, arched stone bridge with swinging warm lantern,
fluffy Ghibli-normal trees, swaying grass, glowing mushrooms, hooded traveler walking
on twos, ancient rune shrine, and igniting cliffside campfire with rising fireflies)
and renders 8 DISTINCT CINEMATIC CAMERA ANGLES automatically via Timeline Markers.
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
KIT_DIR = os.path.join(ROOT, "90 Templates & Starter Kits", "undershine-blender-pixel-kit")
sys.path.insert(0, KIT_DIR)

from blender_pixel_lib import (
    clear_scene,
    configure_undershine_eevee,
    setup_sky_world,
    hex_to_linear,
    make_hue_shifted_toon_mat,
    make_emissive_mat,
    make_water_mat,
    make_foliage_tree,
    add_multi_angle_shot,
    setup_passes_compositor,
)

FPS = 30
TOTAL_FRAMES = 634  # 21.13s (matches voiceover + 0.85s twilight payoff)


def river_center_x(y: float) -> float:
    return 1.35 * math.sin(y * 0.16)


def terrain_height(x: float, y: float) -> float:
    """Sculpted terraced Undershine valley terrain with river channel, bridge banks, and cliff ledges."""
    rx = river_center_x(y)
    dist_r = abs(x - rx)

    # River bed dip
    if dist_r < 2.05:
        t = dist_r / 2.05
        base_z = -0.65 + 0.65 * (t ** 2.4)
    else:
        bank = dist_r - 2.05
        # Smooth rise from riverbank, plateau near bridge/shrine, terraced hills further out
        base_z = 0.35 + 0.30 * min(bank, 3.0) + 0.18 * max(0.0, bank - 3.0) ** 1.15

    # Gentle organic rolling hills
    hills = 0.35 * math.sin(x * 0.28 + 0.5) * math.cos(y * 0.24 - 0.3)

    # Flatten bridge approaches around y = 0, x in [-5..-2] and [2..5.5]
    bridge_zone = math.exp(-((y / 3.2) ** 2)) * math.exp(-(((dist_r - 3.4) / 2.6) ** 2))
    # Flatten shrine & campfire clearing around (5.8, 6.2)
    shrine_dist = math.hypot(x - 5.8, y - 6.0)
    shrine_flat = math.exp(-((shrine_dist / 3.6) ** 2))

    # Waterfall cliff wall at north (y > 14.2)
    north_cliff = 0.0
    if y > 13.5:
        u = min(1.0, (y - 13.5) / 2.2)
        north_cliff = 7.4 * (u * u * (3 - 2 * u))

    # Dramatic east overhanging cliff behind shrine (x > 9.0)
    east_cliff = 0.0
    if x > 8.6:
        u = min(1.0, (x - 8.6) / 3.2)
        east_cliff = 6.8 * (u * u * (3 - 2 * u))

    # West background ridge (x < -8.5)
    west_ridge = 0.0
    if x < -8.2:
        u = min(1.0, (-8.2 - x) / 4.2)
        west_ridge = 5.5 * (u * u * (3 - 2 * u))

    z = base_z + hills + north_cliff + east_cliff + west_ridge
    # Smoothly flatten clearing & bridge pads
    z = z * (1.0 - 0.72 * bridge_zone) + 0.78 * (0.72 * bridge_zone)
    z = z * (1.0 - 0.85 * shrine_flat) + 1.05 * (0.85 * shrine_flat)

    # Subtle Undershine cliff terracing on steeper elevations (z > 2.2)
    if z > 2.2 and dist_r > 2.4:
        step = 0.75
        q = round(z / step) * step
        z = z * 0.45 + q * 0.55
    return z


def build_terrain_mesh(mat_grass, mat_cliff, mat_dirt):
    bm = bmesh.new()
    nx, ny = 84, 88
    xmin, xmax = -18.0, 18.0
    ymin, ymax = -16.0, 22.0

    grid = []
    for iy in range(ny):
        y = ymin + (ymax - ymin) * iy / (ny - 1)
        row = []
        for ix in range(nx):
            x = xmin + (xmax - xmin) * ix / (nx - 1)
            z = terrain_height(x, y)
            row.append(bm.verts.new((x, y, z)))
        grid.append(row)

    bm.verts.ensure_lookup_table()
    for iy in range(ny - 1):
        for ix in range(nx - 1):
            v00 = grid[iy][ix]
            v10 = grid[iy][ix + 1]
            v11 = grid[iy + 1][ix + 1]
            v01 = grid[iy + 1][ix]
            f = bm.faces.new((v00, v10, v11, v01))
            f.smooth = False  # Crisp low-poly pixel facets on cliffs/banks

            cx = (v00.co.x + v10.co.x + v11.co.x + v01.co.x) * 0.25
            cy = (v00.co.y + v10.co.y + v11.co.y + v01.co.y) * 0.25
            cz = (v00.co.z + v10.co.z + v11.co.z + v01.co.z) * 0.25
            dz = max(v00.co.z, v10.co.z, v11.co.z, v01.co.z) - min(v00.co.z, v10.co.z, v11.co.z, v01.co.z)

            # Assign cliff rock on steep faces / river bed, dirt path along trail, grass on meadows
            rx = river_center_x(cy)
            on_path = (
                (abs(cy) < 1.15 and abs(cx) < 5.2 and abs(cx - rx) > 2.2)
                or (cx > 2.8 and cx < 6.4 and cy > -0.6 and cy < 6.4 and abs((cx - 3.2) - (cy * 0.45)) < 1.1)
            )
            if dz > 0.34 or cz < 0.12:
                f.material_index = 1  # Cliff/stone
            elif on_path:
                f.material_index = 2  # Warm dirt trail
            else:
                f.material_index = 0  # Meadow grass

    mesh = bpy.data.meshes.new("ValleyTerrainMesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("ValleyTerrain", mesh)
    obj.data.materials.append(mat_grass)
    obj.data.materials.append(mat_cliff)
    obj.data.materials.append(mat_dirt)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def build_river_and_waterfall(mat_water, mat_waterfall, mat_foam):
    # River surface plane
    bm = bmesh.new()
    ny, nx = 60, 14
    rows = []
    for iy in range(ny):
        y = -16.0 + 31.6 * iy / (ny - 1)
        rx = river_center_x(y)
        row = []
        for ix in range(nx):
            x = rx - 2.6 + 5.2 * ix / (nx - 1)
            row.append(bm.verts.new((x, y, 0.02)))
        rows.append(row)
    for iy in range(ny - 1):
        for ix in range(nx - 1):
            bm.faces.new((rows[iy][ix], rows[iy][ix + 1], rows[iy + 1][ix + 1], rows[iy + 1][ix]))
    mesh = bpy.data.meshes.new("RiverMesh")
    bm.to_mesh(mesh)
    bm.free()
    river = bpy.data.objects.new("RiverSurface", mesh)
    river.data.materials.append(mat_water)
    bpy.context.scene.collection.objects.link(river)

    # Cascading waterfall sheet at y = 14.8, x = river_center_x(15.0)
    wx = river_center_x(15.0)
    bm_w = bmesh.new()
    for iz in range(12):
        z = 7.6 * iz / 11.0
        y_off = 14.75 + 0.55 * (1.0 - (z / 7.6) ** 1.5)
        for ix in range(6):
            x = wx - 1.35 + 2.70 * ix / 5.0
            bm_w.verts.new((x, y_off, z))
    bm_w.verts.ensure_lookup_table()
    for iz in range(11):
        for ix in range(5):
            i0 = iz * 6 + ix
            bm_w.faces.new((bm_w.verts[i0], bm_w.verts[i0 + 1], bm_w.verts[i0 + 7], bm_w.verts[i0 + 6]))
    m_wf = bpy.data.meshes.new("WaterfallMesh")
    bm_w.to_mesh(m_wf)
    bm_w.free()
    wf = bpy.data.objects.new("Waterfall", m_wf)
    wf.data.materials.append(mat_waterfall)
    bpy.context.scene.collection.objects.link(wf)

    # Animated mist/foam puffs at waterfall base
    for i in range(9):
        ang = i * 0.72
        px = wx - 1.4 + 2.8 * (i / 8.0)
        py = 14.2 + 0.35 * math.sin(ang)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.45 + 0.15 * (i % 3), location=(px, py, 0.22))
        puff = bpy.context.active_object
        puff.name = f"WaterfallFoam_{i}"
        puff.data.materials.append(mat_foam)
        d = puff.driver_add("scale", 2).driver
        d.expression = f"0.65 + 0.25 * sin(frame * 0.14 + {i * 0.9:.2f})"
        d2 = puff.driver_add("location", 2).driver
        d2.expression = f"0.22 + 0.14 * abs(sin(frame * 0.11 + {i * 1.1:.2f}))"


def build_stone_bridge(mat_stone, mat_stone_dark, mat_wood, mat_lantern_glow):
    """Arched weathered stone bridge spanning x=-3.6..+3.6 at y=0, with chest-height parapets & warm hanging lantern."""
    parent = bpy.data.objects.new("StoneBridge", None)
    bpy.context.scene.collection.objects.link(parent)

    def bridge_z(x: float) -> float:
        u = max(-1.0, min(1.0, x / 3.6))
        return 0.72 + 0.96 * (1.0 - u * u)

    # Main stone deck & arch voussoir blocks
    n_seg = 15
    for i in range(n_seg):
        x0 = -3.6 + 7.2 * i / n_seg
        x1 = -3.6 + 7.2 * (i + 1) / n_seg
        xm = 0.5 * (x0 + x1)
        zm = bridge_z(xm)
        slope = math.atan2(bridge_z(x1) - bridge_z(x0), x1 - x0)

        # Deck slab
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(xm, 0.0, zm - 0.22))
        blk = bpy.context.active_object
        blk.scale = ((x1 - x0) * 1.04, 1.95, 0.44)
        blk.rotation_euler = (0.0, -slope, 0.0)
        blk.data.materials.append(mat_stone if i % 2 == 0 else mat_stone_dark)
        blk.parent = parent

        # Low chest-height stone parapet blocks (z_top <= deck + 0.52 so traveler stays 100% readable!)
        for side_y in (-0.88, 0.88):
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(xm, side_y, zm + 0.24))
            par = bpy.context.active_object
            par.scale = ((x1 - x0) * 0.92, 0.24, 0.48 + (0.06 if i % 3 == 0 else 0.0))
            par.rotation_euler = (0.0, -slope, 0.0)
            par.data.materials.append(mat_stone_dark if i % 2 == 0 else mat_stone)
            par.parent = parent

    # Bridge stone piers anchored into riverbank
    for px in (-2.75, 2.75):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, 0.0, 0.15))
        pier = bpy.context.active_object
        pier.scale = (0.85, 2.25, 1.85)
        pier.data.materials.append(mat_stone_dark)
        pier.parent = parent

    # Center Arch Timber Lantern Post & Swinging Glowing Lantern!
    post_x, post_y, post_z = 0.0, 0.92, bridge_z(0.0)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(post_x, post_y, post_z + 1.15))
    post = bpy.context.active_object
    post.scale = (0.14, 0.14, 2.30)
    post.data.materials.append(mat_wood)
    post.parent = parent

    # Crossbeam overhanging bridge deck
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(post_x, post_y - 0.36, post_z + 2.22))
    arm = bpy.context.active_object
    arm.scale = (0.12, 0.86, 0.12)
    arm.data.materials.append(mat_wood)
    arm.parent = parent

    # Swinging pivot at top of lantern chain (obeying Law #18: pivot at top attachment point!)
    pivot = bpy.data.objects.new("LanternSwingPivot", None)
    pivot.location = (post_x, post_y - 0.68, post_z + 2.16)
    pivot.parent = parent
    bpy.context.scene.collection.objects.link(pivot)
    drv = pivot.driver_add("rotation_euler", 1).driver
    drv.expression = "0.09 * sin(frame * 0.085)"

    # Chain + metal cap + glowing lantern core
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.34, location=(0, 0, -0.17))
    chain = bpy.context.active_object
    chain.data.materials.append(mat_stone_dark)
    chain.parent = pivot

    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.22, radius2=0.06, depth=0.14, location=(0, 0, -0.36))
    cap = bpy.context.active_object
    cap.data.materials.append(mat_stone_dark)
    cap.parent = pivot

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, -0.54))
    glass = bpy.context.active_object
    glass.scale = (0.24, 0.24, 0.30)
    glass.data.materials.append(mat_lantern_glow)
    glass.parent = pivot

    # Warm flickering point light inside the bridge lantern
    ldata = bpy.data.lights.new("BridgeLanternLight", type="POINT")
    ldata.color = (1.0, 0.68, 0.28)
    ldata.energy = 110.0
    ldata.shadow_soft_size = 0.08
    lobj = bpy.data.objects.new("BridgeLanternLight", ldata)
    lobj.location = (0.0, 0.0, -0.55)
    lobj.parent = pivot
    bpy.context.scene.collection.objects.link(lobj)

    # Animate lantern intensity rising as twilight deepens + gentle flicker
    ldrv = ldata.driver_add("energy").driver
    ldrv.expression = "(90.0 + 160.0 * min(1.0, max(0.0, (frame - 220) / 260.0))) * (0.92 + 0.08 * sin(frame * 0.43))"

    return parent, bridge_z


def build_shrine_and_campfire(mat_stone, mat_stone_dark, mat_wood, mat_rune, mat_fire_outer, mat_fire_core):
    """Ancient stone shrine arch, glowing rune monolith, and igniting cliffside campfire."""
    parent = bpy.data.objects.new("AncientShrine", None)
    parent.location = (6.0, 6.6, 1.05)
    parent.rotation_euler = (0.0, 0.0, math.radians(-26.0))
    bpy.context.scene.collection.objects.link(parent)

    # Stepped circular stone dais
    for i, (r, h, z) in enumerate([(2.6, 0.24, 0.12), (2.0, 0.22, 0.34)]):
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=r, depth=h, location=(0, 0.4, z))
        dais = bpy.context.active_object
        dais.data.materials.append(mat_stone_dark if i == 0 else mat_stone)
        dais.parent = parent

    # Twin weathered stone shrine pillars + lintel arch
    for px in (-1.35, 1.35):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, 0.9, 1.85))
        pil = bpy.context.active_object
        pil.scale = (0.52, 0.52, 2.90)
        pil.data.materials.append(mat_stone)
        pil.parent = parent

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, 0.9, 3.35))
        cap = bpy.context.active_object
        cap.scale = (0.68, 0.68, 0.24)
        cap.data.materials.append(mat_stone_dark)
        cap.parent = parent

    # Carved lintel top beam
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.9, 3.65))
    lintel = bpy.context.active_object
    lintel.scale = (3.65, 0.64, 0.42)
    lintel.data.materials.append(mat_stone)
    lintel.parent = parent

    # Central Ancient Rune Monolith
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.95, 1.65))
    mono = bpy.context.active_object
    mono.scale = (0.76, 0.42, 2.45)
    mono.data.materials.append(mat_stone_dark)
    mono.parent = parent

    # Glowing turquoise rune bars embedded on monolith front face
    for rz, rw in [(2.25, 0.38), (1.85, 0.26), (1.45, 0.42), (1.05, 0.22)]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.72, rz))
        rb = bpy.context.active_object
        rb.scale = (rw, 0.08, 0.12)
        rb.data.materials.append(mat_rune)
        rb.parent = parent

    # Animate rune emission strength: quiet glow early -> vivid flare at twilight & ignition!
    em_node = next(n for n in mat_rune.node_tree.nodes if n.type == "EMISSION")
    r_drv = em_node.inputs["Strength"].driver_add("default_value").driver
    r_drv.expression = "1.2 + 5.5 * min(1.0, max(0.0, (frame - 360) / 140.0)) + (3.2 * min(1.0, max(0.0, (frame - 525) / 18.0))) * (0.85 + 0.15 * sin(frame * 0.35))"

    # Cyan rune point light (balanced so stone stays rich indigo-cyan, never clipped white!)
    rdata = bpy.data.lights.new("ShrineRuneLight", type="POINT")
    rdata.color = (0.24, 0.92, 0.90)
    rdata.shadow_soft_size = 0.02
    robj = bpy.data.objects.new("ShrineRuneLight", rdata)
    robj.location = (0.0, 0.25, 1.85)
    robj.parent = parent
    bpy.context.scene.collection.objects.link(robj)
    rl_drv = rdata.driver_add("energy").driver
    rl_drv.expression = "12.0 + 48.0 * min(1.0, max(0.0, (frame - 380) / 150.0)) + 45.0 * min(1.0, max(0.0, (frame - 525) / 16.0))"

    # --- Cliffside Campfire in front of the shrine ---
    cf_parent = bpy.data.objects.new("Campfire", None)
    cf_parent.location = (0.0, -1.15, 0.10)
    cf_parent.parent = parent
    bpy.context.scene.collection.objects.link(cf_parent)

    # Ring of river stones
    for i in range(9):
        a = i * math.tau / 9.0
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.18, location=(0.62 * math.cos(a), 0.62 * math.sin(a), 0.10))
        st = bpy.context.active_object
        st.scale = (1.1, 0.9, 0.65)
        st.data.materials.append(mat_stone_dark)
        st.parent = cf_parent

    # Crossed timber logs + glowing coal bed
    for a in (0.3, 1.35, 2.4):
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.09, depth=0.92, location=(0, 0, 0.14))
        lg = bpy.context.active_object
        lg.rotation_euler = (math.radians(82), 0.0, a)
        lg.data.materials.append(mat_wood)
        lg.parent = cf_parent

    # Stylized layered pixel flame tongues (rich deep orange outer + warm gold inner core)
    flame_specs = [
        (0.0, 0.0, 0.34, 0.30, 0.78, mat_fire_outer, 0.0, 0.0),
        (0.18, 0.08, 0.26, 0.20, 0.52, mat_fire_outer, 1.3, 0.18),
        (-0.16, 0.10, 0.24, 0.19, 0.48, mat_fire_outer, 2.6, -0.15),
        (0.04, -0.14, 0.22, 0.16, 0.42, mat_fire_outer, 3.8, 0.12),
        (0.0, 0.0, 0.25, 0.14, 0.40, mat_fire_core, 0.7, 0.0),
    ]
    for idx, (fx, fy, fz, fr, fh, fmat, ph, tilt) in enumerate(flame_specs):
        bpy.ops.mesh.primitive_cone_add(vertices=5, radius1=fr, radius2=0.02, depth=fh, location=(fx, fy, fz))
        fl = bpy.context.active_object
        fl.name = f"Flame_{idx}"
        fl.rotation_euler = (tilt, -tilt * 0.7, ph)
        fl.data.materials.append(fmat)
        fl.parent = cf_parent
        for axis in (0, 1, 2):
            fd = fl.driver_add("scale", axis).driver
            boost = "1.18" if axis == 2 else "0.95"
            fd.expression = f"(0.20 + 0.90 * min(1.0, max(0.0, (frame - 524) / 14.0))) * {boost} * (0.86 + 0.18 * sin(frame * 0.55 + {ph:.2f}))"

    # Warm flickering Campfire Point Light (rich amber glow, never clipping stone white!)
    fdata = bpy.data.lights.new("CampfireLight", type="POINT")
    fdata.color = (1.0, 0.40, 0.10)
    fdata.shadow_soft_size = 0.02
    fobj = bpy.data.objects.new("CampfireLight", fdata)
    fobj.location = (0.0, 0.0, 0.72)
    fobj.parent = cf_parent
    bpy.context.scene.collection.objects.link(fobj)
    f_drv = fdata.driver_add("energy").driver
    f_drv.expression = "(12.0 + 110.0 * min(1.0, max(0.0, (frame - 524) / 14.0))) * (0.85 + 0.15 * sin(frame * 0.68) + 0.07 * cos(frame * 1.13))"

    # Rising glowing embers from campfire
    for i in range(10):
        bpy.ops.mesh.primitive_cube_add(size=0.07, location=(0, 0, 0))
        emb = bpy.context.active_object
        emb.name = f"CampfireEmber_{i}"
        emb.data.materials.append(mat_fire_core)
        emb.parent = cf_parent
        phase = i * 11
        dx = emb.driver_add("location", 0).driver
        dx.expression = f"0.35 * sin((frame + {phase}) * 0.13 + {i})"
        dy = emb.driver_add("location", 1).driver
        dy.expression = f"0.35 * cos((frame + {phase}) * 0.11 + {i})"
        dz = emb.driver_add("location", 2).driver
        dz.expression = f"0.25 + (((frame * 0.07 + {i * 0.45:.2f}) % 2.8)) * (0.25 + 0.95 * min(1.0, max(0.0, (frame - 524) / 14.0)))"

    # Stone stepping path from bridge east end (+3.6, 0) to shrine (+5.4, +4.4)
    steps = [
        (3.9, 0.3), (4.3, 1.1), (4.7, 2.0), (5.0, 2.9), (5.3, 3.8), (5.5, 4.6)
    ]
    for i, (sx, sy) in enumerate(steps):
        sz = terrain_height(sx, sy)
        bpy.ops.mesh.primitive_cylinder_add(vertices=7, radius=0.42, depth=0.14, location=(sx, sy, sz + 0.04))
        stp = bpy.context.active_object
        stp.scale = (1.1, 0.85, 1.0)
        stp.data.materials.append(mat_stone if i % 2 == 0 else mat_stone_dark)

    return parent


def build_traveler_rig(mat_cloak, mat_skin, mat_wood, mat_stone_dark, mat_lantern_glow, bridge_z_fn):
    """
    Chunky stylized 3D pixel-RPG hooded traveler with backpack, staff & lantern,
    animated ON TWOS (15fps stepped stride) walking across the bridge toward the shrine!
    """
    rig = bpy.data.objects.new("TravelerRig", None)
    bpy.context.scene.collection.objects.link(rig)

    # Legs (stepped alternating walk!)
    legs = []
    for side, ly in [("L", -0.13), ("R", 0.13)]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, ly, 0.28))
        leg = bpy.context.active_object
        leg.name = f"TravelerLeg_{side}"
        leg.scale = (0.16, 0.14, 0.56)
        leg.data.materials.append(mat_stone_dark)
        leg.parent = rig
        legs.append(leg)

    # Cloak / Torso cone (bold readable crimson silhouette!)
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.40, radius2=0.22, depth=0.92, location=(0.0, 0.0, 0.82))
    cloak = bpy.context.active_object
    cloak.name = "TravelerCloak"
    cloak.data.materials.append(mat_cloak)
    cloak.parent = rig

    # Backpack
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.28, 0.0, 0.92))
    pack = bpy.context.active_object
    pack.scale = (0.26, 0.38, 0.44)
    pack.data.materials.append(mat_wood)
    pack.parent = rig

    # Head + Pointed Cozy RPG Hood
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.23, location=(0.04, 0.0, 1.40))
    head = bpy.context.active_object
    head.data.materials.append(mat_skin)
    head.parent = rig

    bpy.ops.mesh.primitive_cone_add(vertices=7, radius1=0.32, radius2=0.06, depth=0.48, location=(-0.03, 0.0, 1.56))
    hood = bpy.context.active_object
    hood.rotation_euler = (0.0, math.radians(-16), 0.0)
    hood.data.materials.append(mat_cloak)
    hood.parent = rig

    # Wooden walking staff with tiny warm tip crystal
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.035, depth=1.75, location=(0.24, -0.34, 0.92))
    staff = bpy.context.active_object
    staff.rotation_euler = (0.0, math.radians(10), 0.0)
    staff.data.materials.append(mat_wood)
    staff.parent = rig

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.09, location=(0.39, -0.34, 1.76))
    orb = bpy.context.active_object
    orb.data.materials.append(mat_lantern_glow)
    orb.parent = rig

    # Path waypoints: starts west side of bridge -> crosses center arch -> walks toward shrine clearing
    waypoints = [
        (1, -2.8, 0.0),
        (180, -0.9, 0.0),
        (285, 0.85, 0.0),
        (375, 3.25, 0.25),
        (465, 4.45, 2.35),
        (540, 4.95, 3.65),
        (634, 5.10, 3.95),
    ]

    def sample_path(f):
        for i in range(len(waypoints) - 1):
            f0, x0, y0 = waypoints[i]
            f1, x1, y1 = waypoints[i + 1]
            if f0 <= f <= f1:
                u = (f - f0) / max(1, f1 - f0)
                return x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
        return waypoints[-1][1], waypoints[-1][2]

    # Keyframe traveler movement stepped ON TWOS (every 2 frames -> crisp 15fps RPG stride!)
    for f in range(1, TOTAL_FRAMES + 1, 2):
        x, y = sample_path(f)
        xn, yn = sample_path(min(TOTAL_FRAMES, f + 4))
        yaw = math.atan2(yn - y, xn - x) if math.hypot(xn - x, yn - y) > 0.01 else math.radians(65)

        if abs(x) <= 3.55 and abs(y) < 0.8:
            z = bridge_z_fn(x)
        else:
            z = terrain_height(x, y)

        moving = f < 550
        bob = abs(math.sin(f * 0.26)) * 0.09 if moving else 0.0
        rig.location = (x, y, z + bob)
        rig.rotation_euler = (0.0, 0.0, yaw)
        rig.keyframe_insert(data_path="location", frame=f)
        rig.keyframe_insert(data_path="rotation_euler", frame=f)

        stride = math.sin(f * 0.26) * 0.45 if moving else 0.0
        legs[0].rotation_euler = (0.0, stride, 0.0)
        legs[1].rotation_euler = (0.0, -stride, 0.0)
        legs[0].keyframe_insert(data_path="rotation_euler", frame=f)
        legs[1].keyframe_insert(data_path="rotation_euler", frame=f)

    # Set CONSTANT interpolation on traveler & leg F-curves for authentic "on twos" pixel stride!
    for obj in [rig, legs[0], legs[1]]:
        if obj.animation_data and obj.animation_data.action:
            for fc in obj.animation_data.action.fcurves:
                for kp in fc.keyframe_points:
                    kp.interpolation = "CONSTANT"

    return rig


def populate_nature_and_fireflies(mat_canopy_oak, mat_canopy_pine, mat_trunk, mat_grass_tuft, mat_stone_dark, mat_mush_glow, mat_firefly):
    """Populates fluffy Ghibli trees, swaying grass tufts, river boulders, glowing mushrooms & twilight fireflies."""
    # Hand-curated tree layout framing EVERY camera without blocking sightlines!
    tree_specs = [
        # West hillside forest (casts dramatic long sunset shadows across river!)
        (-5.6, 2.2, 1.15, False, 1),
        (-7.4, -1.8, 1.30, True, 2),
        (-5.2, -3.4, 0.95, False, 3),
        (-8.6, 5.2, 1.35, True, 4),
        (-6.2, 8.8, 1.18, False, 5),
        (-4.8, 12.2, 1.10, True, 6),
        (-9.4, -5.8, 1.25, False, 7),
        # East bank & shrine backdrop forest
        (5.4, -3.5, 1.15, False, 8),
        (7.8, -1.6, 1.25, True, 9),
        (8.4, 2.8, 1.12, False, 10),
        (3.4, 10.6, 1.22, False, 11),
        (6.8, 11.4, 1.32, True, 12),
        (9.6, 9.2, 1.40, True, 13),
        # High cliff-top canopy near waterfall
        (-2.6, 16.5, 1.25, True, 14),
        (4.2, 16.2, 1.30, False, 15),
        (0.5, 18.2, 1.15, True, 16),
        # Foreground parallax framing pines south of bridge (for Shot 4 lateral track!)
        (-1.4, -5.8, 0.92, True, 17),
        (2.8, -5.6, 0.98, True, 18),
    ]
    for idx, (tx, ty, sc, is_pine, seed) in enumerate(tree_specs):
        tz = terrain_height(tx, ty) - 0.15
        make_foliage_tree(
            f"Tree_{idx:02d}",
            (tx, ty, tz),
            sc,
            mat_canopy_pine if is_pine else mat_canopy_oak,
            mat_trunk,
            seed=seed,
            pine=is_pine,
        )

    # River boulders & meadow rocks
    rng = random.Random(101)
    rock_coords = [
        (-2.5, -1.8, 0.55), (-2.3, 2.1, 0.48), (2.6, -2.2, 0.62), (2.7, 2.8, 0.52),
        (-1.8, 6.2, 0.65), (2.5, 7.8, 0.72), (-2.4, 11.2, 0.80), (3.1, 13.0, 0.88),
        (4.4, 6.4, 0.42), (7.6, 5.2, 0.58), (-4.2, 0.9, 0.45), (3.6, -0.9, 0.40),
        # Foreground framing boulders for Shot 6 waterline peek
        (-1.7, -4.6, 0.50), (1.8, -4.3, 0.52),
    ]
    for idx, (rx, ry, rad) in enumerate(rock_coords):
        rz = terrain_height(rx, ry) + rad * 0.25
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=rad, location=(rx, ry, rz))
        rk = bpy.context.active_object
        rk.name = f"Rock_{idx:02d}"
        rk.scale = (rng.uniform(0.9, 1.35), rng.uniform(0.85, 1.25), rng.uniform(0.55, 0.85))
        rk.rotation_euler = (0, 0, rng.uniform(0, math.tau))
        rk.data.materials.append(mat_stone_dark)

    # Stylized swaying 3D grass tufts (no shadow casting so grass doesn't create noisy black floor!)
    tuft_bm = bmesh.new()
    for blade in range(4):
        ang = blade * math.tau / 4.0 + 0.3
        bx, by = 0.08 * math.cos(ang), 0.08 * math.sin(ang)
        v0 = tuft_bm.verts.new((bx - 0.04, by, 0.0))
        v1 = tuft_bm.verts.new((bx + 0.04, by, 0.0))
        v2 = tuft_bm.verts.new((bx * 2.2, by * 2.2, 0.34))
        tuft_bm.faces.new((v0, v1, v2))
    tuft_mesh = bpy.data.meshes.new("GrassTuftMesh")
    tuft_bm.to_mesh(tuft_mesh)
    tuft_bm.free()
    tuft_mesh.materials.append(mat_grass_tuft)

    for i in range(65):
        gx = rng.uniform(-7.5, 8.2)
        gy = rng.uniform(-5.5, 11.5)
        if abs(gx - river_center_x(gy)) < 2.35:
            continue
        gz = terrain_height(gx, gy)
        if gz > 3.2:
            continue
        gobj = bpy.data.objects.new(f"Grass_{i:02d}", tuft_mesh)
        gobj.location = (gx, gy, gz - 0.04)
        sc = rng.uniform(0.8, 1.55)
        gobj.scale = (sc, sc, sc)
        gobj.rotation_euler = (0.0, 0.0, rng.uniform(0, math.tau))
        gobj.visible_shadow = False  # Clean non-noisy terrain shadows!
        bpy.context.scene.collection.objects.link(gobj)
        d = gobj.driver_add("rotation_euler", 0).driver
        d.expression = f"0.14 * sin(frame * 0.11 + {gx * 0.7 + gy * 0.5:.2f})"

    # Glowing cozy forest mushrooms near Worm's-Eye foreground (x=-3.2..-1.8, y=-2.8..-1.2) and shrine
    mush_spots = [
        (-2.8, -2.3), (-2.4, -2.6), (-3.1, -1.9), (3.8, 4.4), (4.2, 5.2), (7.1, 4.8), (5.2, 3.3)
    ]
    for idx, (mx, my) in enumerate(mush_spots):
        mz = terrain_height(mx, my)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=0.18, location=(mx, my, mz + 0.09))
        st = bpy.context.active_object
        st.data.materials.append(mat_trunk)
        bpy.ops.mesh.primitive_cone_add(vertices=7, radius1=0.15, radius2=0.04, depth=0.10, location=(mx, my, mz + 0.21))
        cp = bpy.context.active_object
        cp.data.materials.append(mat_mush_glow)

    # 28 Drifting Golden Twilight Fireflies across the river & valley!
    for i in range(28):
        fx = rng.uniform(-5.5, 8.0)
        fy = rng.uniform(-4.0, 12.5)
        fz = max(0.5, terrain_height(fx, fy)) + rng.uniform(0.55, 2.8)
        bpy.ops.mesh.primitive_cube_add(size=0.09, location=(fx, fy, fz))
        ff = bpy.context.active_object
        ff.name = f"Firefly_{i:02d}"
        ff.data.materials.append(mat_firefly)
        ff.visible_shadow = False
        # Drift smoothly & fade in as twilight arrives
        dx = ff.driver_add("location", 0).driver
        dx.expression = f"{fx:.2f} + 0.55 * sin(frame * 0.045 + {i * 1.1:.2f})"
        dz = ff.driver_add("location", 2).driver
        dz.expression = f"{fz:.2f} + 0.45 * cos(frame * 0.06 + {i * 0.8:.2f}) + 0.5 * min(1.0, max(0.0, (frame - 480) / 150.0))"
        for ax in (0, 1, 2):
            ds = ff.driver_add("scale", ax).driver
            ds.expression = f"(0.15 + 1.05 * min(1.0, max(0.0, (frame - 340) / 180.0))) * (0.55 + 0.45 * sin(frame * 0.18 + {i * 1.7:.2f}))"


def setup_dynamic_sun_and_sky(scene):
    """Golden Hour -> Sunset -> Deep Twilight sky & razor-crisp directional shadows."""
    bg, sky_ramp = setup_sky_world(
        scene,
        horizon_hex="#eba675",
        zenith_hex="#3c528c",
        ground_hex="#201d36",
        strength=0.60,
    )

    # Animate sky gradient transitioning Golden Hour (f1) -> Deep Sunset (f360) -> Indigo Twilight (f634)
    key_sky = [
        (1,   "#eba675", "#3c528c", 0.62),
        (280, "#e37e58", "#2d356b", 0.50),
        (480, "#634b7a", "#1c2045", 0.36),
        (634, "#2d2c54", "#10142e", 0.28),
    ]
    e_hor = sky_ramp.color_ramp.elements[1]
    e_zen = sky_ramp.color_ramp.elements[2]
    for f, h_hex, z_hex, st in key_sky:
        e_hor.color = hex_to_linear(h_hex)
        e_hor.keyframe_insert(data_path="color", frame=f)
        e_zen.color = hex_to_linear(z_hex)
        e_zen.keyframe_insert(data_path="color", frame=f)
        bg.inputs["Strength"].default_value = st
        bg.inputs["Strength"].keyframe_insert(data_path="default_value", frame=f)

    # Primary Sun Lamp: razor-sharp angle (0.004 rad) casting crisp zero-dither pixel shadows!
    sdata = bpy.data.lights.new("UndershineSun", type="SUN")
    sdata.angle = 0.004
    sdata.use_shadow = True
    sobj = bpy.data.objects.new("UndershineSun", sdata)
    scene.collection.objects.link(sobj)

    sun_keys = [
        # (frame, elevation_deg, azimuth_deg, energy, rgb)
        (1,   28.0, -52.0, 3.8, (1.0, 0.84, 0.62)),
        (196, 19.0, -64.0, 3.4, (1.0, 0.72, 0.45)),  # Low golden sunset -> LONG shadows across river!
        (370, 11.0, -76.0, 2.3, (0.98, 0.56, 0.38)),
        (510,  7.0, -84.0, 1.05, (0.55, 0.58, 0.92)), # Cool twilight moonlight transition
        (634, 16.0, -40.0, 0.85, (0.45, 0.58, 0.96)), # Crisp cool moonlit rim
    ]
    for f, el, az, en, rgb in sun_keys:
        # Sun points along local -Z; elevation el -> pitch = 90 - el
        sobj.rotation_euler = (math.radians(90.0 - el), 0.0, math.radians(az))
        sobj.keyframe_insert(data_path="rotation_euler", frame=f)
        sdata.energy = en
        sdata.keyframe_insert(data_path="energy", frame=f)
        sdata.color = rgb
        sdata.keyframe_insert(data_path="color", frame=f)

    # Cool indigo sky fill light (no shadow) so shadow sides stay rich cool blue/plum, never black!
    fdata = bpy.data.lights.new("SkyFillCool", type="SUN")
    fdata.energy = 0.45
    fdata.color = (0.38, 0.48, 0.88)
    fdata.use_shadow = False
    fobj = bpy.data.objects.new("SkyFillCool", fdata)
    fobj.rotation_euler = (math.radians(48), 0.0, math.radians(125))
    scene.collection.objects.link(fobj)


def setup_eight_camera_angles(scene):
    """
    8 COMPLETELY DISTINCT CAMERA ANGLES bound to Timeline Markers!
    Every single cut shifts at least 2 of (Azimuth, Elevation, Lens) and has continuous motion.
    """
    scene.timeline_markers.clear()

    shots = [
        # Shot 1 (0.00-3.33s): 3/4 Isometric Diorama Establishing (Undershine Hero! Bridge + River + Shrine + Trees!)
        {
            "name": "Cam01_IsoDiorama",
            "start": 1, "end": 100,
            "lens": 66.0,
            "pos_start": (-13.0, -13.5, 13.6),
            "pos_end":   (-10.5, -11.2, 11.4),
            "tgt_start": (0.8, 1.8, 1.3),
            "tgt_end":   (1.2, 2.6, 1.4),
            "roll": 0.0, "orbit": 4.0,
        },
        # Shot 2 (3.33-6.53s): High Bird's-Eye Top-Down (Long golden shadows stretching across river!)
        {
            "name": "Cam02_BirdsEye",
            "start": 101, "end": 196,
            "lens": 44.0,
            "pos_start": (-1.2, -3.6, 17.5),
            "pos_end":   (0.8, -2.4, 14.2),
            "tgt_start": (0.0, 0.5, 0.4),
            "tgt_end":   (0.5, 1.0, 0.4),
            "roll": 0.0, "orbit": -10.0,
        },
        # Shot 3 (6.53-9.50s): Low-Angle Worm's-Eye Hero (Up from glowing mushrooms & grass at arch & lantern!)
        {
            "name": "Cam03_LowWormsEye",
            "start": 197, "end": 285,
            "lens": 27.0,
            "pos_start": (-3.6, -4.4, 1.15),
            "pos_end":   (-2.5, -3.4, 1.35),
            "tgt_start": (0.1, 0.2, 2.35),
            "tgt_end":   (0.3, 0.4, 2.65),
            "roll": 0.0, "orbit": 0.0,
        },
        # Shot 4 (9.50-12.33s): Side-Profile Parallax Track (Gliding laterally behind silhouetted foreground pines!)
        {
            "name": "Cam04_SideParallax",
            "start": 286, "end": 370,
            "lens": 48.0,
            "pos_start": (-2.4, -7.8, 2.35),
            "pos_end":   (4.2, -7.2, 2.55),
            "tgt_start": (0.6, 0.0, 1.65),
            "tgt_end":   (3.4, 0.8, 1.55),
            "roll": 0.0, "orbit": 0.0,
        },
        # Shot 5 (12.33-14.80s): Over-the-Shoulder (OTS) Follow behind traveler toward twilight shrine!
        {
            "name": "Cam05_OTS_Follow",
            "start": 371, "end": 444,
            "lens": 34.0,
            "pos_start": (1.8, -1.6, 2.65),
            "pos_end":   (3.2, 0.6, 2.75),
            "tgt_start": (5.5, 5.8, 2.2),
            "tgt_end":   (6.0, 6.6, 2.3),
            "roll": 0.0, "orbit": 0.0,
        },
        # Shot 6 (14.80-17.33s): Unobstructed Waterline Skim NORTH of bridge looking across river toward glowing shrine & waterfall!
        {
            "name": "Cam06_WaterlinePeek",
            "start": 445, "end": 520,
            "lens": 38.0,
            "pos_start": (-1.3, 1.9, 1.05),
            "pos_end":   (-0.4, 3.8, 1.25),
            "tgt_start": (4.8, 6.8, 2.15),
            "tgt_end":   (5.8, 6.7, 2.20),
            "roll": 0.0, "orbit": 0.0,
        },
        # Shot 7 (17.33-18.93s): Tight Dutch-Angle Macro Close-Up of Campfire Ignition, Stone Ring & Glowing Rune Monolith!
        {
            "name": "Cam07_DutchMacro",
            "start": 521, "end": 568,
            "lens": 42.0,
            "pos_start": (2.3, 1.9, 2.35),
            "pos_end":   (3.1, 2.8, 2.20),
            "tgt_start": (5.8, 6.1, 2.05),
            "tgt_end":   (5.9, 6.2, 2.10),
            "roll": 6.5, "orbit": 0.0,
            "kick_frame": 528, "kick_amp": 0.12,
        },
        # Shot 8 (18.93-21.13s): Dramatic High Crane Orbit Reveal across the whole glowing twilight valley!
        {
            "name": "Cam08_CraneOrbit",
            "start": 569, "end": TOTAL_FRAMES,
            "lens": 32.0,
            "pos_start": (1.5, -6.5, 4.8),
            "pos_end":   (-4.5, -10.5, 11.2),
            "tgt_start": (4.8, 5.2, 2.0),
            "tgt_end":   (2.8, 4.2, 1.8),
            "roll": 0.0, "orbit": 16.0,
        },
    ]

    meta_shots = []
    for s in shots:
        add_multi_angle_shot(
            scene,
            name=s["name"],
            start_frame=s["start"],
            end_frame=s["end"],
            pos_start=s["pos_start"],
            pos_end=s["pos_end"],
            target_start=s["tgt_start"],
            target_end=s["tgt_end"],
            lens=s["lens"],
            roll_deg=s["roll"],
            orbit_deg=s["orbit"],
            kick_frame=s.get("kick_frame"),
            kick_amp=s.get("kick_amp", 0.12),
        )
        meta_shots.append({
            "name": s["name"],
            "start_frame": s["start"],
            "end_frame": s["end"],
            "start_sec": round((s["start"] - 1) / float(FPS), 3),
            "end_sec": round(s["end"] / float(FPS), 3),
        })

    with open(os.path.join(BASE, "shots_meta.json"), "w", encoding="utf-8") as f:
        json.dump({"fps": FPS, "total_frames": TOTAL_FRAMES, "shots": meta_shots}, f, indent=2)


def main():
    clear_scene()
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = TOTAL_FRAMES

    # 270x480 native pixel grid -> 4x integer scale = 1080x1920!
    configure_undershine_eevee(
        scene,
        res_x=270,
        res_y=480,
        fps=FPS,
        samples=16,
        mist_start=24.0,
        mist_depth=52.0,
    )
    if hasattr(scene.eevee, "shadow_ray_count"):
        scene.eevee.shadow_ray_count = 1
    if hasattr(scene.eevee, "shadow_step_count"):
        scene.eevee.shadow_step_count = 6

    # --- Hue-Shifted Atmospheric Materials (Zero Flat Arcady Colors!) ---
    mat_grass = make_hue_shifted_toon_mat(
        "Mat_Grass",
        deep_shadow_hex="#182633",
        shadow_hex="#243e45",
        mid_hex="#4d7a4f",
        lit_hex="#9ab858",
        grain_scale=3.8, grain_amt=0.16, snap_step=0.18,
    )
    mat_grass_tuft = make_hue_shifted_toon_mat(
        "Mat_GrassTuft",
        deep_shadow_hex="#1c303a",
        shadow_hex="#2c4e48",
        mid_hex="#5d8c52",
        lit_hex="#b5cf65",
        grain_scale=6.0, grain_amt=0.10, snap_step=0.12,
    )
    mat_cliff = make_hue_shifted_toon_mat(
        "Mat_Cliff",
        deep_shadow_hex="#1b1a30",
        shadow_hex="#2f2e4a",
        mid_hex="#5d596e",
        lit_hex="#a39386",
        grain_scale=2.8, grain_amt=0.18, snap_step=0.22,
    )
    mat_dirt = make_hue_shifted_toon_mat(
        "Mat_Dirt",
        deep_shadow_hex="#241929",
        shadow_hex="#422c38",
        mid_hex="#7c5644",
        lit_hex="#c28e63",
        grain_scale=5.2, grain_amt=0.16, snap_step=0.14,
    )
    mat_stone = make_hue_shifted_toon_mat(
        "Mat_Stone",
        deep_shadow_hex="#201e36",
        shadow_hex="#3a3854",
        mid_hex="#736f82",
        lit_hex="#bfb1a0",
        grain_scale=4.5, grain_amt=0.15, snap_step=0.15,
    )
    mat_stone_dark = make_hue_shifted_toon_mat(
        "Mat_StoneDark",
        deep_shadow_hex="#161529",
        shadow_hex="#2b2a42",
        mid_hex="#525066",
        lit_hex="#8c838a",
        grain_scale=4.2, grain_amt=0.15, snap_step=0.16,
    )
    mat_canopy_oak = make_hue_shifted_toon_mat(
        "Mat_CanopyOak",
        deep_shadow_hex="#152636",
        shadow_hex="#214247",
        mid_hex="#42754d",
        lit_hex="#8eb354",
        grain_scale=4.2, grain_amt=0.14, snap_step=0.16,
    )
    mat_canopy_pine = make_hue_shifted_toon_mat(
        "Mat_CanopyPine",
        deep_shadow_hex="#122133",
        shadow_hex="#1b3642",
        mid_hex="#2e594c",
        lit_hex="#618c58",
        grain_scale=4.6, grain_amt=0.14, snap_step=0.16,
    )
    mat_trunk = make_hue_shifted_toon_mat(
        "Mat_Trunk",
        deep_shadow_hex="#1f1424",
        shadow_hex="#3b2533",
        mid_hex="#664238",
        lit_hex="#9c6c52",
        grain_scale=6.0, grain_amt=0.15, snap_step=0.12,
    )
    mat_cloak = make_hue_shifted_toon_mat(
        "Mat_Cloak",
        deep_shadow_hex="#2b132b",
        shadow_hex="#591f36",
        mid_hex="#a63740",
        lit_hex="#e37254",
        grain_scale=6.0, grain_amt=0.08, snap_step=0.10,
    )
    mat_skin = make_hue_shifted_toon_mat(
        "Mat_Skin",
        deep_shadow_hex="#5c3540",
        shadow_hex="#9e655a",
        mid_hex="#d9a482",
        lit_hex="#f7d5b5",
        grain_scale=5.0, grain_amt=0.05, snap_step=0.10,
    )

    mat_water = make_water_mat("Mat_Water")
    mat_waterfall = make_water_mat(
        "Mat_Waterfall",
        deep_hex="#2d6c87",
        mid_hex="#55a8ba",
        lit_hex="#8cd9d6",
        foam_hex="#e6fcf9",
        snap_step=0.14,
    )
    mat_foam = make_hue_shifted_toon_mat(
        "Mat_Foam",
        deep_shadow_hex="#3f6580",
        shadow_hex="#6aa1b5",
        mid_hex="#b5e3de",
        lit_hex="#eefcfa",
        grain_scale=4.0, grain_amt=0.10, snap_step=0.14,
    )
    mat_lantern_glow = make_emissive_mat("Mat_LanternGlow", "#ffc966", strength=3.4)
    mat_rune = make_emissive_mat("Mat_RuneGlow", "#3de8de", strength=2.4)
    mat_fire_outer = make_emissive_mat("Mat_FireOuter", "#f25818", strength=2.6)
    mat_fire_core = make_emissive_mat("Mat_FireCore", "#ffe078", strength=3.6)
    mat_mush_glow = make_emissive_mat("Mat_MushGlow", "#4ce0cf", strength=2.4)
    mat_firefly = make_emissive_mat("Mat_Firefly", "#ffe47a", strength=4.2)

    # --- Build 3D World ---
    build_terrain_mesh(mat_grass, mat_cliff, mat_dirt)
    build_river_and_waterfall(mat_water, mat_waterfall, mat_foam)
    _, bridge_z_fn = build_stone_bridge(mat_stone, mat_stone_dark, mat_trunk, mat_lantern_glow)
    build_shrine_and_campfire(mat_stone, mat_stone_dark, mat_trunk, mat_rune, mat_fire_outer, mat_fire_core)
    build_traveler_rig(mat_cloak, mat_skin, mat_trunk, mat_stone_dark, mat_lantern_glow, bridge_z_fn)
    populate_nature_and_fireflies(
        mat_canopy_oak, mat_canopy_pine, mat_trunk, mat_grass_tuft, mat_stone_dark, mat_mush_glow, mat_firefly
    )

    # --- Lighting & 8-Angle Cameras ---
    setup_dynamic_sun_and_sky(scene)
    setup_eight_camera_angles(scene)

    passes_dir = os.path.join(BASE, "passes")
    setup_passes_compositor(scene, passes_dir, depth_max=48.0)

    # Save .blend file so user can also open/tweak it directly in Blender!
    blend_path = os.path.join(BASE, "undershine_valley.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[OK] Saved Blender scene -> {blend_path}")

    # Check mode: --preview renders 1 midpoint frame per camera for instant visual QA!
    if "--preview" in sys.argv:
        preview_frames = [45, 145, 240, 330, 410, 485, 545, 610]
        for f in preview_frames:
            scene.frame_set(f)
            scene.render.filepath = os.path.join(passes_dir, f"_dummy_{f:04d}.png")
            bpy.ops.render.render(write_still=False)
        print(f"[OK] Rendered {len(preview_frames)} preview frames across all 8 angles!")
    else:
        scene.render.filepath = os.path.join(passes_dir, "_dummy_")
        bpy.ops.render.render(animation=True)
        print(f"[OK] Rendered full {TOTAL_FRAMES}-frame multi-angle sequence -> {passes_dir}")


if __name__ == "__main__":
    main()
