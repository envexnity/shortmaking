"""
build_scene.py — Track 7 Undershine 3D Pixel Art: "Choose a World. You Must Survive One Year Here."

Builds 5 distinct, non-overlapping Undershine 3D pixel-art worlds/zones inside one coherent
Blender 4.2 EEVEE Next scene:
  - Zone 0 (X=0):   Astral Orrery (4 rotating 3D pixel globes + 4 Solo Planet Title Cards along -Y)
  - Zone 1 (X=200): World 1 — The Sun Chaser (walking lantern lighthouse fortress + creeping frost wall)
  - Zone 2 (X=400): World 2 — The Lantern Canopy (giant Ghibli trees, rope bridges, glider, moths, purple fog)
  - Zone 3 (X=600): World 3 — The Glass Harbour (mirror sapphire lake, bridge, cozy flat & Syndicate Spire)
  - Zone 4 (X=800): World 4 — The Ember Vault (obsidian crater, furnace array, ash, masked miner, supply beam)

Automatically reads voice/words.json so all 17 camera cuts and sky/sun transitions lock to narration.
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


def load_timing():
    words_p = os.path.join(BASE, "voice", "words.json")
    data = json.load(open(words_p, encoding="utf-8"))
    dur = float(data["duration"])
    secs = data["sections"]
    total_frames = int(round((dur + 0.85) * FPS))

    def sec_frames(key, is_last=False):
        s_f = max(1, int(round(secs[key]["start"] * FPS)) + 1)
        e_f = total_frames if is_last else max(s_f + 30, int(round(secs[key]["end"] * FPS)))
        return s_f, e_f

    i0, i1 = sec_frames("intro")
    w1_0, w1_1 = sec_frames("world1")
    w2_0, w2_1 = sec_frames("world2")
    w3_0, w3_1 = sec_frames("world3")
    w4_0, w4_1 = sec_frames("world4", is_last=True)

    # Ensure seamless contiguous frames with zero gaps
    w1_0 = i1 + 1
    w2_0 = w1_1 + 1
    w3_0 = w2_1 + 1
    w4_0 = w3_1 + 1
    return total_frames, {
        "intro": (1, i1),
        "world1": (w1_0, w1_1),
        "world2": (w2_0, w2_1),
        "world3": (w3_0, w3_1),
        "world4": (w4_0, w4_1),
    }


def make_planet_globe(name: str, loc, radius: float, base_mat, accent_mat, glow_mat, kind: str, spin_speed: float = 0.032):
    """Creates a detailed stylized 3D pixel diorama planet with orbiting landmarks."""
    parent = bpy.data.objects.new(name, None)
    parent.location = loc
    bpy.context.scene.collection.objects.link(parent)

    # Core chunky icosphere
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=radius, location=(0, 0, 0))
    core = bpy.context.active_object
    core.name = f"{name}_Core"
    core.data.materials.append(base_mat)
    core.parent = parent

    # Slight organic terrain relief on icosphere verts
    rng = random.Random(hash(name) & 0xFFFF)
    for v in core.data.vertices:
        bump = 1.0 + rng.uniform(-0.07, 0.09)
        v.co *= bump

    if kind == "w1":
        # Mini Sun-Chaser lighthouse silhouette sticking out of upper rim + dusk ring
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, radius + 0.25))
        hull = bpy.context.active_object
        hull.scale = (0.48, 0.28, 0.26)
        hull.data.materials.append(accent_mat)
        hull.parent = parent

        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.12, depth=0.45, location=(0.0, 0.0, radius + 0.55))
        tw = bpy.context.active_object
        tw.data.materials.append(accent_mat)
        tw.parent = parent

        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.14, location=(0.0, 0.0, radius + 0.80))
        bc = bpy.context.active_object
        bc.data.materials.append(glow_mat)
        bc.parent = parent

        # Frost ice belt on south pole
        bpy.ops.mesh.primitive_cone_add(vertices=7, radius1=radius * 0.52, radius2=0.1, depth=radius * 0.45, location=(0, 0, -radius * 0.85))
        ice = bpy.context.active_object
        ice.rotation_euler = (math.pi, 0, 0)
        ice.data.materials.append(accent_mat)
        ice.parent = parent

    elif kind == "w2":
        # Fluffy emerald canopy mounds + glowing amber sap lanterns orbiting equator
        for i in range(6):
            ang = i * math.tau / 6.0
            lat = 0.28 * math.sin(i * 1.9)
            r = radius * 0.96
            px = r * math.cos(lat) * math.cos(ang)
            py = r * math.cos(lat) * math.sin(ang)
            pz = r * math.sin(lat)
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=radius * 0.34, location=(px, py, pz))
            puff = bpy.context.active_object
            puff.data.materials.append(accent_mat)
            puff.parent = parent
        for i in range(4):
            ang = i * math.tau / 4.0 + 0.4
            bpy.ops.mesh.primitive_cube_add(size=radius * 0.14, location=((radius + 0.30) * math.cos(ang), (radius + 0.30) * math.sin(ang), 0.12 * math.sin(ang * 2)))
            lt = bpy.context.active_object
            lt.data.materials.append(glow_mat)
            lt.parent = parent

    elif kind == "w3":
        # Continental terrace island + gleaming Syndicate Spire + cyan ring
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=radius * 0.48, location=(radius * 0.55, 0.2 * radius, 0.35 * radius))
        isl = bpy.context.active_object
        isl.scale = (1.1, 1.3, 0.6)
        isl.data.materials.append(accent_mat)
        isl.parent = parent

        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.18, radius2=0.05, depth=radius * 0.78, location=(0.0, 0.0, radius + 0.28))
        spire = bpy.context.active_object
        spire.data.materials.append(accent_mat)
        spire.parent = parent

        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.14, location=(0.0, 0.0, radius + 0.68))
        orb = bpy.context.active_object
        orb.data.materials.append(glow_mat)
        orb.parent = parent

    elif kind == "w4":
        # Glowing lava core ridges & orbital ash ring
        for i in range(5):
            ang = i * math.tau / 5.0
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(radius * 0.75 * math.cos(ang), radius * 0.75 * math.sin(ang), 0.25 * math.sin(ang)))
            mag = bpy.context.active_object
            mag.scale = (radius * 0.32, radius * 0.18, radius * 0.32)
            mag.rotation_euler = (0.3 * i, 0.2 * i, ang)
            mag.data.materials.append(glow_mat)
            mag.parent = parent
        # Ash halo cubes
        for i in range(8):
            ang = i * math.tau / 8.0
            bpy.ops.mesh.primitive_cube_add(size=radius * 0.12, location=((radius + 0.36) * math.cos(ang), (radius + 0.36) * math.sin(ang), 0.18 * math.cos(ang)))
            rk = bpy.context.active_object
            rk.data.materials.append(accent_mat)
            rk.parent = parent

    drv = parent.driver_add("rotation_euler", 2).driver
    drv.expression = f"frame * {spin_speed:.4f}"
    parent.rotation_euler = (math.radians(14), math.radians(-10), 0.0)
    return parent


def populate_starfield(center_loc, count=85, span_x=14.0, y_min=4.0, y_max=22.0, z_min=-10.0, z_max=10.0, mat_star=None, seed=1):
    rng = random.Random(seed)
    cx, cy, cz = center_loc
    for i in range(count):
        sx = cx + rng.uniform(-span_x, span_x)
        sy = cy + rng.uniform(y_min, y_max)
        sz = cz + rng.uniform(z_min, z_max)
        sz_cube = rng.uniform(0.05, 0.12)
        bpy.ops.mesh.primitive_cube_add(size=sz_cube, location=(sx, sy, sz))
        st = bpy.context.active_object
        st.data.materials.append(mat_star)
        st.visible_shadow = False
        for ax in (0, 1, 2):
            d = st.driver_add("scale", ax).driver
            d.expression = f"0.55 + 0.45 * sin(frame * 0.14 + {i * 0.9:.2f})"


def build_zone0_space(mats):
    """Astral Orrery (2x2 showcase at 0,0,0) + 4 Solo Planet Title Cards along -Y."""
    # Orrery 2x2 grid framed cleanly in 9:16 vertical camera at (0, -11.5, 0)
    globe_specs = [
        ("Orrery_W1", (-1.85, 0.0, 1.35), 1.15, mats["w1_sand"], mats["stone"], mats["amber"], "w1"),
        ("Orrery_W2", ( 1.85, 0.0, 1.35), 1.15, mats["w2_moss"], mats["w2_oak"], mats["amber"], "w2"),
        ("Orrery_W3", (-1.85, 0.0, -2.05), 1.15, mats["water"], mats["w3_stone"], mats["cyan"], "w3"),
        ("Orrery_W4", ( 1.85, 0.0, -2.05), 1.15, mats["w4_obs"], mats["w4_iron"], mats["lava"], "w4"),
    ]
    for nm, loc, r, bm, am, gm, kd in globe_specs:
        make_planet_globe(nm, loc, r, bm, am, gm, kd, spin_speed=0.035)
    populate_starfield((0, 0, 0), count=90, mat_star=mats["star"], seed=11)

    # 4 Solo Planet Title Cards separated by 140m along -Y so zero cross-visibility
    solo_specs = [
        ("Solo_W1", (0, -140, 0), mats["w1_sand"], mats["stone"], mats["amber"], "w1"),
        ("Solo_W2", (0, -280, 0), mats["w2_moss"], mats["w2_oak"], mats["amber"], "w2"),
        ("Solo_W3", (0, -420, 0), mats["water"], mats["w3_stone"], mats["cyan"], "w3"),
        ("Solo_W4", (0, -560, 0), mats["w4_obs"], mats["w4_iron"], mats["lava"], "w4"),
    ]
    for nm, loc, bm, am, gm, kd in solo_specs:
        make_planet_globe(nm, loc, 1.75, bm, am, gm, kd, spin_speed=0.042)
        populate_starfield(loc, count=65, mat_star=mats["star"], seed=hash(nm) & 0xFF)


def w1_terrain_z(lx: float, ly: float) -> float:
    """Stepped golden ochre canyon floor & flanking mesa cliffs around local (0,0)."""
    canyon = max(0.0, (abs(ly) - 3.8) * 0.55)
    step = 0.85
    if canyon > 0.6:
        canyon = canyon * 0.45 + (round(canyon / step) * step) * 0.55
    ripples = 0.24 * math.sin(lx * 0.35) * math.cos(ly * 0.30)
    return canyon + ripples


def build_zone1_sunchaser(mats, w1_start, w1_end):
    """World 1: The Sun Chaser (X=200) — Walking Lighthouse Fortress & Creeping Frost Line."""
    ox, oy, oz = 200.0, 0.0, 0.0
    bm = bmesh.new()
    nx, ny = 58, 52
    grid = []
    for iy in range(ny):
        ly = -18.0 + 36.0 * iy / (ny - 1)
        row = []
        for ix in range(nx):
            lx = -22.0 + 44.0 * ix / (nx - 1)
            lz = w1_terrain_z(lx, ly)
            row.append(bm.verts.new((ox + lx, oy + ly, oz + lz)))
        grid.append(row)
    bm.verts.ensure_lookup_table()
    for iy in range(ny - 1):
        for ix in range(nx - 1):
            v00, v10, v11, v01 = grid[iy][ix], grid[iy][ix + 1], grid[iy + 1][ix + 1], grid[iy + 1][ix]
            f = bm.faces.new((v00, v10, v11, v01))
            f.smooth = False
            dz = max(v00.co.z, v10.co.z, v11.co.z, v01.co.z) - min(v00.co.z, v10.co.z, v11.co.z, v01.co.z)
            cx = (v00.co.x + v10.co.x + v11.co.x + v01.co.x) * 0.25 - ox
            if cx < -8.0:
                f.material_index = 2  # Frosty indigo edge!
            elif dz > 0.30:
                f.material_index = 1  # Canyon cliff
            else:
                f.material_index = 0  # Sunlit desert floor
    mesh = bpy.data.meshes.new("W1_CanyonMesh")
    bm.to_mesh(mesh); bm.free()
    terr = bpy.data.objects.new("W1_Canyon", mesh)
    terr.data.materials.append(mats["w1_sand"])
    terr.data.materials.append(mats["w1_cliff"])
    terr.data.materials.append(mats["w1_frost"])
    bpy.context.scene.collection.objects.link(terr)

    # Jagged indigo ice crystal spires along western frost line (x = 186..191)
    rng = random.Random(201)
    for i in range(18):
        ix = ox - rng.uniform(7.5, 13.5)
        iy = oy + rng.uniform(-11.0, 11.0)
        iz = w1_terrain_z(ix - ox, iy - oy)
        h = rng.uniform(2.0, 4.8)
        bpy.ops.mesh.primitive_cone_add(vertices=5, radius1=rng.uniform(0.5, 1.0), radius2=0.06, depth=h, location=(ix, iy, iz + h * 0.45))
        sp = bpy.context.active_object
        sp.rotation_euler = (rng.uniform(-0.18, 0.18), rng.uniform(0.10, 0.32), rng.uniform(0, 3.14))
        sp.data.materials.append(mats["w1_frost"])

    # --- Walking Sun-Chaser Lighthouse Rig ---
    rig = bpy.data.objects.new("W1_WalkingLighthouse", None)
    bpy.context.scene.collection.objects.link(rig)

    # Main citadel armored hull
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 2.35))
    hull = bpy.context.active_object
    hull.scale = (5.4, 3.0, 2.1)
    hull.data.materials.append(mats["stone"])
    hull.parent = rig

    # Upper deck chest-high parapet walls (Law #19)
    for sy in (-1.42, 1.42):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, sy, 3.65))
        par = bpy.context.active_object
        par.scale = (5.3, 0.18, 0.52)
        par.data.materials.append(mats["stone_dark"])
        par.parent = rig
    for sx in (-2.6, 2.6):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, 0.0, 3.65))
        par = bpy.context.active_object
        par.scale = (0.18, 3.0, 0.52)
        par.data.materials.append(mats["stone_dark"])
        par.parent = rig

    # Glowing warm bunk porthole windows along hull sides
    for side_y in (-1.53, 1.53):
        for wx in (-1.8, -0.9, 0.0, 0.9, 1.8):
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(wx, side_y, 2.45))
            win = bpy.context.active_object
            win.scale = (0.42, 0.08, 0.48)
            win.data.materials.append(mats["amber"])
            win.parent = rig

    # Tall front stone lighthouse spire + rotating beacon crown
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1.05, depth=3.8, location=(1.1, 0.0, 5.25))
    spire = bpy.context.active_object
    spire.data.materials.append(mats["stone"])
    spire.parent = rig

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.72, depth=0.95, location=(1.1, 0.0, 7.55))
    lamp_core = bpy.context.active_object
    lamp_core.data.materials.append(mats["amber"])
    lamp_core.parent = rig

    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=1.22, radius2=0.14, depth=0.85, location=(1.1, 0.0, 8.35))
    roof = bpy.context.active_object
    roof.data.materials.append(mats["stone_dark"])
    roof.parent = rig

    # Beacon Point Light
    b_light = bpy.data.lights.new("W1_BeaconLight", type="POINT")
    b_light.color = (1.0, 0.72, 0.28)
    b_light.energy = 260.0
    b_obj = bpy.data.objects.new("W1_BeaconLight", b_light)
    b_obj.location = (1.1, 0.0, 7.6)
    b_obj.parent = rig
    bpy.context.scene.collection.objects.link(b_obj)

    # Rear chimney smokestack + rising steam cubes
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.30, depth=1.6, location=(-1.6, 0.65, 4.15))
    chim = bpy.context.active_object
    chim.data.materials.append(mats["stone_dark"])
    chim.parent = rig
    for i in range(6):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.28, location=(-1.6, 0.65, 5.2))
        sm = bpy.context.active_object
        sm.data.materials.append(mats["foam"])
        sm.parent = rig
        dz = sm.driver_add("location", 2).driver
        dz.expression = f"5.0 + ((frame * 0.09 + {i * 0.55:.2f}) % 3.2)"
        dx = sm.driver_add("location", 0).driver
        dx.expression = f"-1.6 - ((frame * 0.09 + {i * 0.55:.2f}) % 3.2) * 0.5"

    # Cozy deck tea brazier + 2 tiny hooded crew watchers on roof deck
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.32, depth=0.35, location=(-0.55, -0.45, 3.58))
    braz = bpy.context.active_object
    braz.data.materials.append(mats["stone_dark"])
    braz.parent = rig
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.20, location=(-0.55, -0.45, 3.82))
    coal = bpy.context.active_object
    coal.data.materials.append(mats["amber"])
    coal.parent = rig

    for wx, wy in [(-0.95, -0.45), (-0.15, 0.55)]:
        bpy.ops.mesh.primitive_cone_add(vertices=7, radius1=0.28, radius2=0.12, depth=0.72, location=(wx, wy, 3.76))
        cr = bpy.context.active_object
        cr.data.materials.append(mats["cloak"])
        cr.parent = rig
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.16, location=(wx, wy, 4.20))
        hd = bpy.context.active_object
        hd.data.materials.append(mats["skin"])
        hd.parent = rig

    # 6 Articulated Walking Legs stepped ON TWOS
    legs = []
    for idx, (lx, ly) in enumerate([(-1.8, -1.35), (0.0, -1.35), (1.8, -1.35), (-1.8, 1.35), (0.0, 1.35), (1.8, 1.35)]):
        piv = bpy.data.objects.new(f"W1_LegPivot_{idx}", None)
        piv.location = (lx, ly, 1.55)
        piv.parent = rig
        bpy.context.scene.collection.objects.link(piv)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, -0.82))
        lg = bpy.context.active_object
        lg.scale = (0.42, 0.36, 1.65)
        lg.data.materials.append(mats["stone_dark"])
        lg.parent = piv
        legs.append((idx, piv))

    # Animate walking lighthouse striding east across the canyon (ON TWOS!)
    for f in range(w1_start, w1_end + 1, 2):
        u = (f - w1_start) / max(1, w1_end - w1_start)
        cx = ox - 1.8 + 4.8 * u
        bob = abs(math.sin(f * 0.22)) * 0.10
        rig.location = (cx, oy, oz + bob + 0.15)
        rig.keyframe_insert(data_path="location", frame=f)
        for idx, piv in legs:
            phase = 0.0 if (idx % 2 == 0) else math.pi
            piv.rotation_euler = (0.0, 0.28 * math.sin(f * 0.22 + phase), 0.0)
            piv.keyframe_insert(data_path="rotation_euler", frame=f)
    for obj in [rig] + [p for _, p in legs]:
        if obj.animation_data and obj.animation_data.action:
            for fc in obj.animation_data.action.fcurves:
                for kp in fc.keyframe_points:
                    kp.interpolation = "CONSTANT"


def build_zone2_canopy(mats, w2_start, w2_end):
    """World 2: The Lantern Canopy (X=400) — Ghibli Tree Canopy, Rope Bridges, Winged Glider, Moths & Purple Fog."""
    ox, oy, oz = 400.0, 0.0, 0.0

    # Deep violet glowing poison valley fog sea below (z = -4.2)
    bpy.ops.mesh.primitive_plane_add(size=46.0, location=(ox, oy, oz - 4.2))
    fog = bpy.context.active_object
    fog.data.materials.append(mats["w2_poison"])
    fog.visible_shadow = False

    # Colossal trunk pillars & fluffy Ghibli canopies framing a misty gorge (clear center sightline!)
    tree_nodes = [
        (-6.8, 2.6, 2.1, False, 21),
        ( 6.8, 2.6, 2.2, False, 22),
        (-7.4, -6.2, 1.75, True, 23),
        ( 7.6, -6.0, 1.85, False, 24),
        (-1.0, 9.2, 2.35, False, 25),
        (-9.0, -1.0, 2.0, True, 26),
        ( 9.0, -0.8, 2.1, True, 27),
        ( 1.5, 13.5, 2.5, False, 28),
    ]
    for idx, (lx, ly, sc, is_pine, sd) in enumerate(tree_nodes):
        make_foliage_tree(
            f"W2_Tree_{idx}",
            (ox + lx, oy + ly, oz - 4.5),
            sc * 1.35,
            mats["w2_pine"] if is_pine else mats["w2_oak"],
            mats["trunk"],
            seed=sd,
            pine=is_pine,
        )

    # Suspended wooden canopy platforms on East & West giant trunks (z = 2.6)
    for px, py, pr in [(-6.4, 2.4, 2.2), (6.4, 2.4, 2.2), (-1.0, 9.0, 2.4)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=pr, depth=0.35, location=(ox + px, oy + py, oz + 2.4))
        plat = bpy.context.active_object
        plat.data.materials.append(mats["trunk"])
        # Cute little timber canopy hut on each platform
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox + px, oy + py + 0.35, oz + 3.15))
        hut = bpy.context.active_object
        hut.scale = (1.3, 1.1, 1.1)
        hut.data.materials.append(mats["stone"])
        bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=1.15, radius2=0.1, depth=0.85, location=(ox + px, oy + py + 0.35, oz + 4.10))
        hrf = bpy.context.active_object
        hrf.rotation_euler = (0, 0, math.radians(45))
        hrf.data.materials.append(mats["w2_oak"])

    # Hanging Rope Bridge spanning (-4.6, 2.2) to (+4.6, 2.4) at z = 2.45
    for i in range(16):
        u = i / 15.0
        bx = ox - 4.5 + 9.0 * u
        by = oy + 2.2 + 0.15 * u
        sag = -0.55 * math.sin(u * math.pi)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bx, by, oz + 2.42 + sag))
        plank = bpy.context.active_object
        plank.scale = (0.48, 1.10, 0.12)
        plank.data.materials.append(mats["trunk"])

    # Timber lantern post + crossbeam anchored to bridge west pier (-1.5, 1.6) in clear air!
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox - 2.2, oy + 1.85, oz + 3.1))
    lpost = bpy.context.active_object
    lpost.scale = (0.18, 0.18, 2.75)
    lpost.data.materials.append(mats["trunk"])
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox - 1.85, oy + 1.55, oz + 4.38))
    larm = bpy.context.active_object
    larm.scale = (0.85, 0.72, 0.16)
    larm.data.materials.append(mats["trunk"])

    # Hero Swaying Amber Sap Lantern hung from crossbeam tip (Law #18 top pivot!)
    piv = bpy.data.objects.new("W2_SapLanternPivot", None)
    piv.location = (ox - 1.55, oy + 1.35, oz + 4.32)
    bpy.context.scene.collection.objects.link(piv)
    drv = piv.driver_add("rotation_euler", 1).driver
    drv.expression = "0.10 * sin(frame * 0.09)"

    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=0.75, location=(0, 0, -0.37))
    rope = bpy.context.active_object
    rope.data.materials.append(mats["trunk"])
    rope.parent = piv

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, -0.92))
    sap_glow = bpy.context.active_object
    sap_glow.scale = (0.38, 0.38, 0.48)
    sap_glow.data.materials.append(mats["amber"])
    sap_glow.parent = piv

    s_light = bpy.data.lights.new("W2_SapLight", type="POINT")
    s_light.color = (1.0, 0.72, 0.25)
    s_light.energy = 140.0
    s_lobj = bpy.data.objects.new("W2_SapLight", s_light)
    s_lobj.location = (0, 0, -0.95)
    s_lobj.parent = piv
    bpy.context.scene.collection.objects.link(s_lobj)

    # Swooping Winged Canopy Glider!
    glider = bpy.data.objects.new("W2_Glider", None)
    bpy.context.scene.collection.objects.link(glider)
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.22, radius2=0.06, depth=0.9, location=(0, 0, 0))
    body = bpy.context.active_object
    body.rotation_euler = (math.radians(90), 0, 0)
    body.data.materials.append(mats["cloak"])
    body.parent = glider
    for side in (-1, 1):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 0.65, -0.08, 0.05))
        wg = bpy.context.active_object
        wg.scale = (1.2, 0.42, 0.05)
        wg.rotation_euler = (0.0, side * -0.14, side * -0.22)
        wg.data.materials.append(mats["amber"])
        wg.parent = glider

    for f in range(w2_start, w2_end + 1):
        u = (f - w2_start) / max(1, w2_end - w2_start)
        gx = ox - 4.2 + 9.2 * math.sin(u * math.pi * 1.1)
        gy = oy - 2.2 + 5.5 * u
        gz = oz + 3.4 + 0.85 * math.cos(u * math.tau)
        glider.location = (gx, gy, gz)
        glider.rotation_euler = (0.12, -0.24 * math.cos(u * math.pi), math.radians(-35 + 65 * u))
        glider.keyframe_insert(data_path="location", frame=f)
        glider.keyframe_insert(data_path="rotation_euler", frame=f)

    # 18 Glowing Canopy Moths orbiting lantern & bridge ropes!
    rng = random.Random(303)
    for i in range(18):
        mx = ox - 1.55 + rng.uniform(-1.3, 1.6)
        my = oy + 1.45 + rng.uniform(-0.9, 1.1)
        mz = oz + 2.7 + rng.uniform(-0.3, 1.4)
        bpy.ops.mesh.primitive_cube_add(size=0.11, location=(mx, my, mz))
        moth = bpy.context.active_object
        moth.data.materials.append(mats["cyan"] if i % 2 == 0 else mats["amber"])
        moth.visible_shadow = False
        dx = moth.driver_add("location", 0).driver
        dx.expression = f"{mx:.2f} + 0.48 * sin(frame * 0.16 + {i * 1.3:.2f})"
        dz = moth.driver_add("location", 2).driver
        dz.expression = f"{mz:.2f} + 0.35 * cos(frame * 0.21 + {i * 0.9:.2f})"


def build_zone3_harbour(mats):
    """World 3: The Glass Harbour (X=600) — Mirror Sapphire Lake, Bridge, Cozy Flat & Syndicate Spire."""
    ox, oy, oz = 600.0, 0.0, 0.0

    # Terraced grassy harbour shoreline & lake bed
    bm = bmesh.new()
    nx, ny = 60, 60
    grid = []
    for iy in range(ny):
        ly = -16.0 + 34.0 * iy / (ny - 1)
        row = []
        for ix in range(nx):
            lx = -18.0 + 36.0 * ix / (nx - 1)
            rx = 1.1 * math.sin(ly * 0.18)
            dist = abs(lx - rx)
            if dist < 3.6:
                lz = -0.55 + 0.55 * (dist / 3.6) ** 2.4
            else:
                lz = 0.42 + 0.25 * min(dist - 3.6, 4.0) + 0.18 * max(0.0, dist - 7.6)
            if ly > 12.0:
                lz += 3.8 * min(1.0, (ly - 12.0) / 4.0)
            row.append(bm.verts.new((ox + lx, oy + ly, oz + lz)))
        grid.append(row)
    bm.verts.ensure_lookup_table()
    for iy in range(ny - 1):
        for ix in range(nx - 1):
            v00, v10, v11, v01 = grid[iy][ix], grid[iy][ix + 1], grid[iy + 1][ix + 1], grid[iy + 1][ix]
            f = bm.faces.new((v00, v10, v11, v01))
            f.smooth = False
            dz = max(v00.co.z, v10.co.z, v11.co.z, v01.co.z) - min(v00.co.z, v10.co.z, v11.co.z, v01.co.z)
            cz = (v00.co.z + v10.co.z + v11.co.z + v01.co.z) * 0.25
            f.material_index = 1 if (dz > 0.28 or cz < 0.12) else 0
    mesh = bpy.data.meshes.new("W3_HarbourMesh")
    bm.to_mesh(mesh); bm.free()
    terr = bpy.data.objects.new("W3_HarbourTerrain", mesh)
    terr.data.materials.append(mats["w3_grass"])
    terr.data.materials.append(mats["w3_stone"])
    bpy.context.scene.collection.objects.link(terr)

    # Shimmering animated sapphire lake sheet
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(ox, oy + 0.5, oz + 0.04))
    lake = bpy.context.active_object
    lake.scale = (9.5, 32.0, 1.0)
    lake.data.materials.append(mats["water"])

    # Arched limestone footbridge spanning across the harbour channel at y = 0
    for i in range(13):
        u = -1.0 + 2.0 * (i + 0.5) / 13.0
        bx = ox + u * 4.2
        bz = oz + 0.65 + 0.95 * (1.0 - u * u)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bx, oy, bz - 0.18))
        blk = bpy.context.active_object
        blk.scale = (0.70, 1.85, 0.36)
        blk.data.materials.append(mats["w3_stone"] if i % 2 == 0 else mats["stone_dark"])
        for sy in (-0.82, 0.82):
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bx, oy + sy, bz + 0.22))
            par = bpy.context.active_object
            par.scale = (0.62, 0.20, 0.44)
            par.data.materials.append(mats["w3_stone"])

    # Cozy lakeside flat with glowing warm terrace window & quiet desk/chair on balcony (west bank -5.2, -1.6)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox - 5.4, oy - 1.4, oz + 1.75))
    flat = bpy.context.active_object
    flat.scale = (2.6, 2.8, 2.2)
    flat.data.materials.append(mats["w3_stone"])
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox - 4.05, oy - 1.4, oz + 1.85))
    fwin = bpy.context.active_object
    fwin.scale = (0.12, 1.35, 0.95)
    fwin.data.materials.append(mats["amber"])
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=2.1, radius2=0.25, depth=1.1, location=(ox - 5.4, oy - 1.4, oz + 3.4))
    froof = bpy.context.active_object
    froof.rotation_euler = (0, 0, math.radians(45))
    froof.data.materials.append(mats["cloak"])

    # Seated lakeside watcher on terrace stone bench overlooking the Spire
    bpy.ops.mesh.primitive_cone_add(vertices=7, radius1=0.30, radius2=0.14, depth=0.72, location=(ox - 3.6, oy - 0.8, oz + 1.15))
    wk = bpy.context.active_object
    wk.data.materials.append(mats["cloak"])
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.17, location=(ox - 3.6, oy - 0.8, oz + 1.62))
    wh = bpy.context.active_object
    wh.data.materials.append(mats["skin"])

    # Tall Gleaming Glass Harbour Syndicate Spire on east promontory (ox + 4.8, oy + 5.8)
    sx, sy = ox + 4.8, oy + 5.8
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=2.3, depth=0.5, location=(sx, sy, oz + 0.55))
    dais = bpy.context.active_object
    dais.data.materials.append(mats["w3_stone"])

    for tier_z, tier_r, tier_h in [(2.4, 1.45, 3.4), (5.3, 1.05, 2.8), (7.7, 0.68, 2.4)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=tier_r, depth=tier_h, location=(sx, sy, oz + tier_z))
        st = bpy.context.active_object
        st.data.materials.append(mats["w3_stone"])

    # Glowing Cyan Arcane Rings + Skyward Cargo Telemetry Beam on Spire!
    for rz, rr in [(3.9, 1.56), (6.5, 1.14), (8.9, 0.78)]:
        bpy.ops.mesh.primitive_torus_add(major_radius=rr, minor_radius=0.09, major_segments=16, minor_segments=6, location=(sx, sy, oz + rz))
        ring = bpy.context.active_object
        ring.data.materials.append(mats["cyan"])

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.16, depth=14.0, location=(sx, sy, oz + 15.8))
    beam = bpy.context.active_object
    beam.data.materials.append(mats["cyan"])
    beam.visible_shadow = False

    sp_light = bpy.data.lights.new("W3_SpireLight", type="POINT")
    sp_light.color = (0.30, 0.90, 1.0)
    sp_light.energy = 160.0
    sp_lobj = bpy.data.objects.new("W3_SpireLight", sp_light)
    sp_lobj.location = (sx - 0.5, sy - 0.8, oz + 6.5)
    bpy.context.scene.collection.objects.link(sp_lobj)

    # Lush Ghibli trees around Glass Harbour
    for idx, (lx, ly, sc, ip, sd) in enumerate([
        (-5.8, 3.8, 1.25, False, 31), (-7.2, -4.4, 1.15, True, 32),
        (5.6, -2.8, 1.20, False, 33), (8.2, 2.5, 1.35, True, 34),
        (-3.2, 9.6, 1.30, False, 35), (1.8, 10.4, 1.20, True, 36),
    ]):
        make_foliage_tree(f"W3_Tree_{idx}", (ox + lx, oy + ly, oz + 0.55), sc, mats["w2_pine"] if ip else mats["w2_oak"], mats["trunk"], seed=sd, pine=ip)


def build_zone4_embervault(mats):
    """World 4: The Ember Vault (X=800) — Obsidian Crater, 16 Glowing Furnace Thrusters, Ash, Miner & Supply Beam."""
    ox, oy, oz = 800.0, 0.0, 0.0

    # Stepped Obsidian Volcanic Caldera Bowl
    bm = bmesh.new()
    nx, ny = 56, 56
    grid = []
    for iy in range(ny):
        ly = -16.0 + 32.0 * iy / (ny - 1)
        row = []
        for ix in range(nx):
            lx = -16.0 + 32.0 * ix / (nx - 1)
            r = math.hypot(lx, ly)
            if r < 4.5:
                lz = -1.6
            else:
                wall = (r - 4.5) * 0.65
                step = 0.90
                lz = -1.5 + wall * 0.45 + (round(wall / step) * step) * 0.55
            row.append(bm.verts.new((ox + lx, oy + ly, oz + lz)))
        grid.append(row)
    bm.verts.ensure_lookup_table()
    for iy in range(ny - 1):
        for ix in range(nx - 1):
            f = bm.faces.new((grid[iy][ix], grid[iy][ix + 1], grid[iy + 1][ix + 1], grid[iy + 1][ix]))
            f.smooth = False
            f.material_index = 0
    mesh = bpy.data.meshes.new("W4_CraterMesh")
    bm.to_mesh(mesh); bm.free()
    terr = bpy.data.objects.new("W4_Crater", mesh)
    terr.data.materials.append(mats["w4_obs"])
    bpy.context.scene.collection.objects.link(terr)

    # Glowing molten lava pool at bottom of pit
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=4.8, depth=0.3, location=(ox, oy, oz - 1.35))
    lava = bpy.context.active_object
    lava.data.materials.append(mats["lava"])
    lava.visible_shadow = False

    # Suspended Iron Gantry Bridge across pit at z = 1.65
    for i in range(13):
        bx = ox - 4.8 + 9.6 * i / 12.0
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bx, oy - 0.5, oz + 1.55))
        cat = bpy.context.active_object
        cat.scale = (0.76, 1.65, 0.26)
        cat.data.materials.append(mats["w4_iron"])
    for px in (-4.4, 4.4):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox + px, oy - 0.5, oz + 0.2))
        pier = bpy.context.active_object
        pier.scale = (0.75, 1.75, 3.0)
        pier.data.materials.append(mats["w4_iron"])

    # Towering Furnace Bank + 12 Glowing Orange Reactor Thruster Vents on North Wall (y = 6.2)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox, oy + 6.4, oz + 4.4))
    fwall = bpy.context.active_object
    fwall.scale = (10.5, 2.2, 6.2)
    fwall.data.materials.append(mats["w4_iron"])

    for row_z in (2.6, 4.2, 5.8):
        for col_x in (-3.6, -1.2, 1.2, 3.6):
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.58, depth=0.6, location=(ox + col_x, oy + 5.2, oz + row_z), rotation=(math.radians(90), 0, 0))
            vent = bpy.context.active_object
            vent.data.materials.append(mats["lava"] if (int(col_x + row_z) % 2 == 0) else mats["amber"])

    # 3 Tall Industrial Smokestacks belching dark ash & glowing ember puffs
    for sx in (-3.4, 0.0, 3.4):
        bpy.ops.mesh.primitive_cylinder_add(vertices=7, radius=0.55, depth=4.4, location=(ox + sx, oy + 6.4, oz + 9.4))
        stk = bpy.context.active_object
        stk.data.materials.append(mats["w4_iron"])

    # Warm orange furnace point light + cyan Glass Harbour Cargo Supply Beam rising from center crane!
    fl = bpy.data.lights.new("W4_FurnaceLight", type="POINT")
    fl.color = (1.0, 0.42, 0.14)
    fl.energy = 280.0
    fobj = bpy.data.objects.new("W4_FurnaceLight", fl)
    fobj.location = (ox, oy + 2.5, oz + 2.8)
    bpy.context.scene.collection.objects.link(fobj)

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.22, depth=18.0, location=(ox + 1.8, oy - 0.5, oz + 9.8))
    sbeam = bpy.context.active_object
    sbeam.data.materials.append(mats["cyan"])
    sbeam.visible_shadow = False

    # Hooded Miner standing on bridge with glowing Cyan Respirator Mask!
    bpy.ops.mesh.primitive_cone_add(vertices=7, radius1=0.34, radius2=0.16, depth=0.92, location=(ox - 0.4, oy - 0.5, oz + 2.15))
    miner = bpy.context.active_object
    miner.data.materials.append(mats["w4_iron"])
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.20, location=(ox - 0.4, oy - 0.5, oz + 2.74))
    mhead = bpy.context.active_object
    mhead.data.materials.append(mats["stone"])
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox - 0.35, oy - 0.68, oz + 2.70))
    mask = bpy.context.active_object
    mask.scale = (0.20, 0.14, 0.14)
    mask.data.materials.append(mats["cyan"])

    # Rising glowing ember cubes from pit (keep clear of Cam 16 west gantry pullback path)
    rng = random.Random(404)
    for i in range(24):
        ex = ox + rng.uniform(-4.5, 5.0)
        ey = oy + rng.uniform(-4.2, 4.2)
        ez = oz - 0.5 + rng.uniform(0.0, 4.0)
        if ex < ox - 1.2 and ey < 0.6:
            ex = ox + abs(ex - ox)
        bpy.ops.mesh.primitive_cube_add(size=0.12, location=(ex, ey, ez))
        em = bpy.context.active_object
        em.data.materials.append(mats["amber"] if i % 2 == 0 else mats["lava"])
        em.visible_shadow = False
        dz = em.driver_add("location", 2).driver
        dz.expression = f"-0.6 + ((frame * 0.08 + {i * 0.45:.2f}) % 7.5)"


def setup_world_lighting_and_sky(scene, spans):
    """Per-zone instant CONSTANT sky & sun shifts + smooth twilight drift inside World 3."""
    bg, sky_ramp = setup_sky_world(scene, horizon_hex="#131630", zenith_hex="#090b1a", ground_hex="#080914", strength=0.30)

    sdata = bpy.data.lights.new("UndershineSun", type="SUN")
    sdata.angle = 0.005
    sdata.use_shadow = True
    sobj = bpy.data.objects.new("UndershineSun", sdata)
    scene.collection.objects.link(sobj)

    fdata = bpy.data.lights.new("SkyFillCool", type="SUN")
    fdata.energy = 0.52
    fdata.color = (0.40, 0.50, 0.90)
    fdata.use_shadow = False
    fobj = bpy.data.objects.new("SkyFillCool", fdata)
    fobj.rotation_euler = (math.radians(48), 0.0, math.radians(130))
    scene.collection.objects.link(fobj)

    i0, i1 = spans["intro"]
    w1_0, w1_1 = spans["world1"]
    w2_0, w2_1 = spans["world2"]
    w3_0, w3_1 = spans["world3"]
    w4_0, w4_1 = spans["world4"]

    w1_g_end = w1_0 + 27
    w2_g_end = w2_0 + 27
    w3_g_end = w3_0 + 27
    w4_g_end = w4_0 + 27
    w3_b = w3_g_end + int((w3_1 - w3_g_end) * 0.68)

    # (frame, hor_hex, zen_hex, bg_str, sun_el, sun_az, sun_en, sun_rgb, constant)
    sky_sun_keys = [
        (1,       "#161936", "#090b1a", 0.34, 28.0, -45.0, 2.8, (0.95, 0.92, 1.0), True),
        (w1_0,    "#161936", "#090b1a", 0.34, 24.0, -42.0, 3.0, (1.0, 0.88, 0.72), True),
        (w1_g_end + 1, "#ebb378", "#2d3d73", 0.60, 21.0, -56.0, 3.8, (1.0, 0.80, 0.54), True),
        (w2_0,    "#161936", "#090b1a", 0.34, 26.0, -40.0, 2.8, (0.85, 1.0, 0.88), True),
        (w2_g_end + 1, "#d99e68", "#22384c", 0.54, 24.0, -50.0, 3.4, (1.0, 0.84, 0.60), True),
        (w3_0,    "#161936", "#090b1a", 0.34, 28.0, -44.0, 3.0, (0.86, 0.95, 1.0), True),
        (w3_g_end + 1, "#eba97c", "#394d88", 0.62, 23.0, -58.0, 3.7, (1.0, 0.82, 0.58), True),
        (w3_b + 1, "#1e1f45", "#0c0f26", 0.24, 15.0, -72.0, 0.65, (0.42, 0.54, 0.96), True),
        (w4_0,    "#161936", "#090b1a", 0.34, 24.0, -38.0, 3.0, (1.0, 0.72, 0.52), True),
        (w4_g_end + 1, "#6e363c", "#17162e", 0.40, 22.0, -52.0, 2.2, (1.0, 0.64, 0.42), True),
    ]

    e_hor = sky_ramp.color_ramp.elements[1]
    e_zen = sky_ramp.color_ramp.elements[2]
    for f, hh, zh, bs, el, az, en, rgb, const in sky_sun_keys:
        e_hor.color = hex_to_linear(hh)
        e_hor.keyframe_insert(data_path="color", frame=f)
        e_zen.color = hex_to_linear(zh)
        e_zen.keyframe_insert(data_path="color", frame=f)
        bg.inputs["Strength"].default_value = bs
        bg.inputs["Strength"].keyframe_insert(data_path="default_value", frame=f)

        sobj.rotation_euler = (math.radians(90.0 - el), 0.0, math.radians(az))
        sobj.keyframe_insert(data_path="rotation_euler", frame=f)
        sdata.energy = en
        sdata.keyframe_insert(data_path="energy", frame=f)
        sdata.color = rgb
        sdata.keyframe_insert(data_path="color", frame=f)

    # Set CONSTANT interpolation everywhere so every zone cut & twilight reveal snaps crisply
    for holder in (scene.world.node_tree, sobj, sdata):
        if holder.animation_data and holder.animation_data.action:
            for fc in holder.animation_data.action.fcurves:
                for kp in fc.keyframe_points:
                    kp.interpolation = "CONSTANT"


def setup_17_cameras(scene, spans):
    scene.timeline_markers.clear()

    def world_splits(s_f, e_f):
        g_end = s_f + 27  # ~0.93s globe card
        rem = e_f - g_end
        c1 = g_end + int(rem * 0.34)
        c2 = g_end + int(rem * 0.68)
        return g_end, c1, c2

    i0, i1 = spans["intro"]
    w1_0, w1_1 = spans["world1"]
    w2_0, w2_1 = spans["world2"]
    w3_0, w3_1 = spans["world3"]
    w4_0, w4_1 = spans["world4"]

    w1g, w1a, w1b = world_splits(w1_0, w1_1)
    w2g, w2a, w2b = world_splits(w2_0, w2_1)
    w3g, w3a, w3b = world_splits(w3_0, w3_1)
    w4g, w4a, w4b = world_splits(w4_0, w4_1)

    shots = [
        # Intro 2x2 Orrery
        {"name": "00_Orrery_Countdown", "start": i0, "end": i1, "lens": 38.0,
         "pos_start": (0.0, -14.6, -0.30), "pos_end": (0.0, -12.2, -0.25),
         "tgt_start": (0.0, 0.0, -0.20), "tgt_end": (0.0, 0.0, -0.20), "roll": 0.0, "orbit": 0.0},

        # World 1 — Sun Chaser (X=200)
        {"name": "01_W1_Globe", "start": w1_0, "end": w1g, "lens": 36.0,
         "pos_start": (0.0, -149.8, 0.6), "pos_end": (0.0, -148.2, 0.4),
         "tgt_start": (0.0, -140.0, 0.30), "tgt_end": (0.0, -140.0, 0.30), "roll": 0.0, "orbit": 8.0},
        {"name": "02_W1_LowLighthouse", "start": w1g + 1, "end": w1a, "lens": 25.0,
         "pos_start": (205.4, -3.5, 1.25), "pos_end": (206.4, -3.2, 1.45),
         "tgt_start": (199.2, 0.0, 3.9), "tgt_end": (200.2, 0.0, 4.2), "roll": 0.0, "orbit": 0.0},
        {"name": "03_W1_IsoShadow", "start": w1a + 1, "end": w1b, "lens": 54.0,
         "pos_start": (214.5, -16.5, 13.0), "pos_end": (216.0, -15.0, 11.8),
         "tgt_start": (200.0, 0.0, 2.4), "tgt_end": (201.0, 0.0, 2.5), "roll": 0.0, "orbit": 5.0},
        {"name": "04_W1_DeckWatch", "start": w1b + 1, "end": w1_1, "lens": 30.0,
         "pos_start": (203.4, -2.7, 5.25), "pos_end": (204.0, -2.4, 5.05),
         "tgt_start": (195.0, 0.0, 2.9), "tgt_end": (192.8, 0.2, 2.6), "roll": 0.0, "orbit": 0.0},

        # World 2 — Lantern Canopy (X=400)
        {"name": "05_W2_Globe", "start": w2_0, "end": w2g, "lens": 36.0,
         "pos_start": (0.0, -289.8, 0.6), "pos_end": (0.0, -288.2, 0.4),
         "tgt_start": (0.0, -280.0, 0.30), "tgt_end": (0.0, -280.0, 0.30), "roll": 0.0, "orbit": -8.0},
        {"name": "06_W2_BirdsEye", "start": w2g + 1, "end": w2a, "lens": 44.0,
         "pos_start": (399.0, -3.5, 15.8), "pos_end": (401.0, -2.0, 13.6),
         "tgt_start": (400.0, 1.8, 1.5), "tgt_end": (400.2, 2.2, 1.5), "roll": 0.0, "orbit": -10.0},
        {"name": "07_W2_SideParallax", "start": w2a + 1, "end": w2b, "lens": 42.0,
         "pos_start": (394.8, -9.2, 3.7), "pos_end": (404.5, -8.8, 4.0),
         "tgt_start": (399.0, 2.0, 2.8), "tgt_end": (401.5, 2.2, 3.0), "roll": 0.0, "orbit": 0.0},
        {"name": "08_W2_DutchMacro", "start": w2b + 1, "end": w2_1, "lens": 46.0,
         "pos_start": (401.6, -2.2, 3.2), "pos_end": (400.9, -1.4, 3.35),
         "tgt_start": (398.4, 1.4, 3.3), "tgt_end": (398.5, 1.4, 3.35), "roll": 6.5, "orbit": 0.0},

        # World 3 — Glass Harbour (X=600)
        {"name": "09_W3_Globe", "start": w3_0, "end": w3g, "lens": 36.0,
         "pos_start": (0.0, -429.8, 0.6), "pos_end": (0.0, -428.2, 0.4),
         "tgt_start": (0.0, -420.0, 0.30), "tgt_end": (0.0, -420.0, 0.30), "roll": 0.0, "orbit": 8.0},
        {"name": "10_W3_IsoHarbour", "start": w3g + 1, "end": w3a, "lens": 48.0,
         "pos_start": (586.5, -13.5, 11.8), "pos_end": (588.5, -11.8, 10.4),
         "tgt_start": (600.2, 2.0, 2.5), "tgt_end": (600.8, 2.5, 2.7), "roll": 0.0, "orbit": 5.0},
        {"name": "11_W3_PeekBalcony", "start": w3a + 1, "end": w3b, "lens": 35.0,
         "pos_start": (598.6, -5.6, 2.2), "pos_end": (599.6, -4.0, 2.4),
         "tgt_start": (595.5, -1.0, 2.0), "tgt_end": (598.2, 1.5, 2.6), "roll": 0.0, "orbit": 0.0},
        {"name": "12_W3_SpireTwilight", "start": w3b + 1, "end": w3_1, "lens": 27.0,
         "pos_start": (600.2, 2.0, 1.4), "pos_end": (601.4, 3.0, 1.8),
         "tgt_start": (604.8, 5.8, 4.6), "tgt_end": (604.8, 5.8, 5.3), "roll": 0.0, "orbit": 0.0},

        # World 4 — Ember Vault (X=800)
        {"name": "13_W4_Globe", "start": w4_0, "end": w4g, "lens": 36.0,
         "pos_start": (0.0, -569.8, 0.6), "pos_end": (0.0, -568.2, 0.4),
         "tgt_start": (0.0, -560.0, 0.30), "tgt_end": (0.0, -560.0, 0.30), "roll": 0.0, "orbit": -8.0},
        {"name": "14_W4_CraneCrater", "start": w4g + 1, "end": w4a, "lens": 30.0,
         "pos_start": (809.4, -6.5, 9.8), "pos_end": (806.2, -9.8, 11.4),
         "tgt_start": (799.8, 1.2, 2.0), "tgt_end": (799.8, 1.5, 2.4), "roll": 0.0, "orbit": 10.0},
        {"name": "15_W4_LowFurnace", "start": w4a + 1, "end": w4b, "lens": 26.0,
         "pos_start": (795.6, -5.0, 1.0), "pos_end": (797.2, -3.5, 1.3),
         "tgt_start": (800.2, 5.2, 4.4), "tgt_end": (800.4, 5.4, 4.8), "roll": -5.0, "orbit": 0.0},
        {"name": "16_W4_PullbackReveal", "start": w4b + 1, "end": w4_1, "lens": 36.0,
         "pos_start": (795.8, -0.8, 3.0), "pos_end": (790.5, -5.6, 6.2),
         "tgt_start": (800.4, -0.4, 2.5), "tgt_end": (801.0, 0.8, 4.2), "roll": 0.0, "orbit": 6.0},
    ]

    meta_shots = []
    for s in shots:
        cam = add_multi_angle_shot(
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
        )
        cam.data.clip_end = 110.0  # Isolates zones cleanly (zones are >=140m apart!)
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

    configure_undershine_eevee(
        scene,
        res_x=270,
        res_y=480,
        fps=FPS,
        samples=12,
        mist_start=26.0,
        mist_depth=55.0,
    )
    if hasattr(scene.eevee, "shadow_ray_count"):
        scene.eevee.shadow_ray_count = 1
    if hasattr(scene.eevee, "shadow_step_count"):
        scene.eevee.shadow_step_count = 6

    mats = {
        "w1_sand": make_hue_shifted_toon_mat("Mat_W1_Sand", "#3b2333", "#a86848", "#e8b06d", deep_shadow_hex="#1f1426", grain_scale=3.8, grain_amt=0.16, snap_step=0.18),
        "w1_cliff": make_hue_shifted_toon_mat("Mat_W1_Cliff", "#2a1b30", "#6e4244", "#c27a57", deep_shadow_hex="#181226", grain_scale=2.8, grain_amt=0.18, snap_step=0.22),
        "w1_frost": make_hue_shifted_toon_mat("Mat_W1_Frost", "#162040", "#3a5b8c", "#9fd5f0", deep_shadow_hex="#0f142e", grain_scale=4.5, grain_amt=0.12, snap_step=0.16),
        "w2_moss": make_hue_shifted_toon_mat("Mat_W2_Moss", "#1a3038", "#3d6e4c", "#89b359", deep_shadow_hex="#121e2b", grain_scale=4.2, grain_amt=0.15, snap_step=0.16),
        "w2_oak": make_hue_shifted_toon_mat("Mat_W2_Oak", "#162938", "#3e704c", "#8db557", deep_shadow_hex="#111d2b", grain_scale=4.2, grain_amt=0.14, snap_step=0.16),
        "w2_pine": make_hue_shifted_toon_mat("Mat_W2_Pine", "#132133", "#2b5448", "#5f8c56", deep_shadow_hex="#0d1726", grain_scale=4.5, grain_amt=0.14, snap_step=0.16),
        "w2_poison": make_emissive_mat("Mat_W2_Poison", "#5c3378", strength=1.4),
        "w3_grass": make_hue_shifted_toon_mat("Mat_W3_Grass", "#1f3842", "#4b7d53", "#9ec261", deep_shadow_hex="#142330", grain_scale=4.0, grain_amt=0.15, snap_step=0.18),
        "w3_stone": make_hue_shifted_toon_mat("Mat_W3_Stone", "#2b2b45", "#7a778f", "#d4c8b8", deep_shadow_hex="#1a1a30", grain_scale=4.5, grain_amt=0.14, snap_step=0.15),
        "w4_obs": make_hue_shifted_toon_mat("Mat_W4_Obsidian", "#151424", "#2e2a40", "#594b5e", deep_shadow_hex="#0e0d1a", grain_scale=3.2, grain_amt=0.18, snap_step=0.20),
        "w4_iron": make_hue_shifted_toon_mat("Mat_W4_Iron", "#191829", "#3c394d", "#786970", deep_shadow_hex="#10101f", grain_scale=4.0, grain_amt=0.14, snap_step=0.16),
        "stone": make_hue_shifted_toon_mat("Mat_Stone", "#211f38", "#736f82", "#bfb1a0", deep_shadow_hex="#161529", grain_scale=4.5, grain_amt=0.15, snap_step=0.15),
        "stone_dark": make_hue_shifted_toon_mat("Mat_StoneDark", "#161529", "#4f4c63", "#8a7f87", deep_shadow_hex="#0f0e1f", grain_scale=4.2, grain_amt=0.15, snap_step=0.16),
        "trunk": make_hue_shifted_toon_mat("Mat_Trunk", "#1f1424", "#664238", "#9c6c52", deep_shadow_hex="#140d1a", grain_scale=5.8, grain_amt=0.15, snap_step=0.13),
        "cloak": make_hue_shifted_toon_mat("Mat_Cloak", "#2b132b", "#a63740", "#e37254", deep_shadow_hex="#1d0d21", grain_scale=6.0, grain_amt=0.08, snap_step=0.10),
        "skin": make_hue_shifted_toon_mat("Mat_Skin", "#5c3540", "#d9a482", "#f7d5b5", grain_scale=5.0, grain_amt=0.05, snap_step=0.10),
        "foam": make_hue_shifted_toon_mat("Mat_Foam", "#3a4563", "#9ea9bf", "#e8edf5", deep_shadow_hex="#232942", grain_scale=4.0, grain_amt=0.10, snap_step=0.14),
        "water": make_water_mat("Mat_Water"),
        "amber": make_emissive_mat("Mat_Amber", "#ffbd4a", strength=3.6),
        "cyan": make_emissive_mat("Mat_Cyan", "#45f0e5", strength=3.2),
        "lava": make_emissive_mat("Mat_Lava", "#ff521c", strength=3.8),
        "star": make_emissive_mat("Mat_Star", "#dce6ff", strength=2.6),
    }

    build_zone0_space(mats)
    build_zone1_sunchaser(mats, spans["world1"][0], spans["world1"][1])
    build_zone2_canopy(mats, spans["world2"][0], spans["world2"][1])
    build_zone3_harbour(mats)
    build_zone4_embervault(mats)

    setup_world_lighting_and_sky(scene, spans)
    meta_shots = setup_17_cameras(scene, spans)

    passes_dir = os.path.join(BASE, "passes")
    setup_passes_compositor(scene, passes_dir, depth_max=60.0)

    blend_path = os.path.join(BASE, "choose_world.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[OK] Saved Blender scene -> {blend_path} ({total_frames} frames)")

    if "--preview" in sys.argv:
        # Render midpoint frame for every one of the 17 shots for instant multi-angle visual QA!
        mids = [s["start_frame"] + (s["end_frame"] - s["start_frame"]) // 2 for s in meta_shots]
        for f in mids:
            scene.frame_set(f)
            scene.render.filepath = os.path.join(passes_dir, f"_dummy_{f:04d}.png")
            bpy.ops.render.render(write_still=False)
        print(f"[OK] Rendered {len(mids)} preview stills across all 17 shots!")
    elif "--range" in sys.argv:
        idx = sys.argv.index("--range")
        scene.frame_start = int(sys.argv[idx + 1])
        scene.frame_end = int(sys.argv[idx + 2])
        scene.render.filepath = os.path.join(passes_dir, "_dummy_")
        bpy.ops.render.render(animation=True)
        print(f"[OK] Re-rendered frames {scene.frame_start}..{scene.frame_end}!")
    else:
        scene.render.filepath = os.path.join(passes_dir, "_dummy_")
        bpy.ops.render.render(animation=True)
        print(f"[OK] Rendered full {total_frames}-frame multi-angle sequence!")


if __name__ == "__main__":
    main()
