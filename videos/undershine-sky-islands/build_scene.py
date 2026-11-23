"""
build_scene.py — Track 7 Undershine 2.5D HD-2D Hybrid in Blender 5.3.0 (`BLENDER_EEVEE`, < 45s):
  - ONLY Background, Sky, 3D Terraced Terrain, Cliff Walls & 3D Water are 3D meshes
  - ALL Trees, Houses, Windmills, Rotors, Steam Train, Sanctuary Pagoda Tower, Pavilions,
    Iron Chains, Crystal Clusters, Bushes, Wildflowers, Lanterns & Characters are detailed
    2D Pixel-Art Sprites (`Closest` texture filter, alpha-clipped, casting real 3D shadows!)
  - ALL Planets in Zone 0 (Orrery & 4 Solo Planet Cards) are FULL SPHERICAL UV BALLS
    (`64x32` smooth spheres wrapped in detailed equirectangular pixel-art planet textures!)
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
SPRITES_DIR = os.path.join(BASE, "sprites")
sys.path.insert(0, KIT_DIR)

from blender_pixel_lib import (
    clear_scene,
    configure_undershine_eevee,
    setup_sky_world,
    hex_to_linear,
    make_hue_shifted_toon_mat,
    make_emissive_mat,
    make_water_mat,
    add_multi_angle_shot,
    apply_stepped_on_twos,
    set_action_interpolation,
    setup_passes_compositor,
)

FPS = 30
_SPRITE_MAT_CACHE = {}


def load_timing():
    words_p = os.path.join(BASE, "voice", "words.json")
    data = json.load(open(words_p, encoding="utf-8"))
    dur = float(data["duration"])
    secs = data["sections"]
    total_frames = int(round((dur + 0.55) * FPS))

    def sec_frames(key, is_last=False):
        s_f = max(1, int(round(secs[key]["start"] * FPS)) + 1)
        e_f = total_frames if is_last else max(s_f + 24, int(round(secs[key]["end"] * FPS)))
        return s_f, e_f

    i0, i1 = sec_frames("intro")
    w1_0, w1_1 = sec_frames("island1")
    w2_0, w2_1 = sec_frames("island2")
    w3_0, w3_1 = sec_frames("island3")
    w4_0, w4_1 = sec_frames("island4", is_last=True)

    w1_0 = i1 + 1
    w2_0 = w1_1 + 1
    w3_0 = w2_1 + 1
    w4_0 = w3_1 + 1
    return total_frames, {
        "intro": (1, i1),
        "island1": (w1_0, w1_1),
        "island2": (w2_0, w2_1),
        "island3": (w3_0, w3_1),
        "island4": (w4_0, w4_1),
    }


# =============================================================================
# 1. FULL SPHERICAL PLANET BALLS (Smooth 64x32 UV Spheres + Pixel Planet Map)
# =============================================================================
def make_spherical_planet_mat(name: str, tex_filename: str, atmo_hex: str):
    """
    Wraps a 512x256 equirectangular pixel-art planetary texture (`Closest` filter) onto a full
    smooth 3D sphere with 4-band spherical toon shading + atmospheric Fresnel rim glow!
    """
    mat = bpy.data.materials.new(name=name)
    if bpy.app.version < (5, 0, 0):
        mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    img_path = os.path.join(SPRITES_DIR, tex_filename)
    img = bpy.data.images.load(img_path, check_existing=True)
    img.colorspace_settings.name = "sRGB"

    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Closest"

    # Spherical lighting ramp
    diff = nt.nodes.new("ShaderNodeBsdfDiffuse")
    diff.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    s2rgb = nt.nodes.new("ShaderNodeShaderToRGB")
    rgb2bw = nt.nodes.new("ShaderNodeRGBToBW")

    shade_ramp = nt.nodes.new("ShaderNodeValToRGB")
    shade_ramp.color_ramp.interpolation = "CONSTANT"
    shade_ramp.color_ramp.elements[0].position = 0.0
    shade_ramp.color_ramp.elements[0].color = (0.16, 0.14, 0.28, 1.0)  # Deep cool night side
    shade_ramp.color_ramp.elements[1].position = 0.16
    shade_ramp.color_ramp.elements[1].color = (0.45, 0.42, 0.58, 1.0)  # Terminator twilight band
    e2 = shade_ramp.color_ramp.elements.new(0.38)
    e2.color = (0.86, 0.84, 0.88, 1.0)                                 # Mid day band
    e3 = shade_ramp.color_ramp.elements.new(0.68)
    e3.color = (1.12, 1.06, 0.96, 1.0)                                 # Sunlit peak band

    mul = nt.nodes.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs["Factor"].default_value = 1.0

    # Atmospheric Fresnel rim glow around the full spherical ball
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.32
    rim_ramp = nt.nodes.new("ShaderNodeValToRGB")
    rim_ramp.color_ramp.interpolation = "CONSTANT"
    rim_ramp.color_ramp.elements[0].position = 0.0
    rim_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    rim_ramp.color_ramp.elements[1].position = 0.66
    rim_ramp.color_ramp.elements[1].color = hex_to_linear(atmo_hex)

    add_rim = nt.nodes.new("ShaderNodeMix")
    add_rim.data_type = "RGBA"
    add_rim.blend_type = "ADD"
    add_rim.inputs["Factor"].default_value = 0.55

    nt.links.new(diff.outputs["BSDF"], s2rgb.inputs["Shader"])
    nt.links.new(s2rgb.outputs["Color"], rgb2bw.inputs["Color"])
    nt.links.new(rgb2bw.outputs["Val"], shade_ramp.inputs["Fac"])

    nt.links.new(tex.outputs["Color"], mul.inputs[6])
    nt.links.new(shade_ramp.outputs["Color"], mul.inputs[7])

    nt.links.new(lw.outputs["Facing"], rim_ramp.inputs["Fac"])
    nt.links.new(mul.outputs[2], add_rim.inputs[6])
    nt.links.new(rim_ramp.outputs["Color"], add_rim.inputs[7])
    nt.links.new(add_rim.outputs[2], out.inputs["Surface"])
    return mat


def make_full_planet_ball(name: str, loc, radius: float, tex_file: str, atmo_hex: str, spin_speed: float = 0.032):
    """Creates a true full spherical Planet Ball (64x32 smooth UV sphere) with pixel-art surface & atmosphere."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=radius, location=loc)
    ball = bpy.context.active_object
    ball.name = name
    for poly in ball.data.polygons:
        poly.use_smooth = True

    mat = make_spherical_planet_mat(f"Mat_{name}", tex_file, atmo_hex)
    ball.data.materials.append(mat)

    ball.rotation_euler = (math.radians(16), math.radians(-10), 0.0)
    drv = ball.driver_add("rotation_euler", 2).driver
    drv.expression = f"frame * {spin_speed:.4f}"
    return ball


# =============================================================================
# 2. 2D PIXEL-ART SPRITE CARD BUILDER (Closest Filter + 3D Cast Shadows!)
# =============================================================================
def get_2d_sprite_mat(sprite_filename: str, emissive_boost: float = 0.0):
    key = (sprite_filename, round(emissive_boost, 2))
    if key in _SPRITE_MAT_CACHE:
        return _SPRITE_MAT_CACHE[key]

    img_path = os.path.join(SPRITES_DIR, sprite_filename)
    img = bpy.data.images.load(img_path, check_existing=True)
    img.colorspace_settings.name = "sRGB"

    mat = bpy.data.materials.new(name=f"SprMat_{sprite_filename}")
    if bpy.app.version < (5, 0, 0):
        mat.use_nodes = True
    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = "DITHERED"
    elif hasattr(mat, "blend_method"):
        mat.blend_method = "CLIP"

    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Closest"
    tex.extension = "CLIP"

    transp = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix_sh = nt.nodes.new("ShaderNodeMixShader")

    # Crisp alpha threshold at 0.5 -> razor-sharp pixel silhouette & exact 3D cast shadow!
    a_gt = nt.nodes.new("ShaderNodeMath")
    a_gt.operation = "GREATER_THAN"
    a_gt.inputs[1].default_value = 0.5

    # Receive real 3D world lighting (sunlight + shadow + warm lantern point lights) while preserving hand-pixeled colors
    diff = nt.nodes.new("ShaderNodeBsdfDiffuse")
    diff.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    s2rgb = nt.nodes.new("ShaderNodeShaderToRGB")
    rgb2bw = nt.nodes.new("ShaderNodeRGBToBW")

    lit_map = nt.nodes.new("ShaderNodeMapRange")
    lit_map.clamp = True
    lit_map.inputs["From Min"].default_value = 0.0
    lit_map.inputs["From Max"].default_value = 0.85
    lit_map.inputs["To Min"].default_value = 0.72 + min(0.25, emissive_boost * 0.1)
    lit_map.inputs["To Max"].default_value = 1.10 + emissive_boost * 0.25

    col_mul = nt.nodes.new("ShaderNodeVectorMath")
    col_mul.operation = "SCALE"

    # Warm point-light tint bounce
    clamp_rgb = nt.nodes.new("ShaderNodeVectorMath")
    clamp_rgb.operation = "MINIMUM"
    clamp_rgb.inputs[1].default_value = (0.55, 0.55, 0.55)

    mix_warm = nt.nodes.new("ShaderNodeMix")
    mix_warm.data_type = "RGBA"
    mix_warm.blend_type = "ADD"
    mix_warm.inputs["Factor"].default_value = 0.14

    nt.links.new(diff.outputs["BSDF"], s2rgb.inputs["Shader"])
    nt.links.new(s2rgb.outputs["Color"], rgb2bw.inputs["Color"])
    nt.links.new(rgb2bw.outputs["Val"], lit_map.inputs["Value"])

    nt.links.new(tex.outputs["Color"], col_mul.inputs[0])
    nt.links.new(lit_map.outputs["Result"], col_mul.inputs["Scale"])

    nt.links.new(s2rgb.outputs["Color"], clamp_rgb.inputs[0])
    nt.links.new(col_mul.outputs["Vector"], mix_warm.inputs[6])
    nt.links.new(clamp_rgb.outputs["Vector"], mix_warm.inputs[7])

    nt.links.new(tex.outputs["Alpha"], a_gt.inputs[0])
    nt.links.new(a_gt.outputs["Value"], mix_sh.inputs["Fac"])
    nt.links.new(transp.outputs["BSDF"], mix_sh.inputs[1])
    nt.links.new(mix_warm.outputs[2], mix_sh.inputs[2])
    nt.links.new(mix_sh.outputs["Shader"], out.inputs["Surface"])

    _SPRITE_MAT_CACHE[key] = (mat, img.size[0], img.size[1])
    return _SPRITE_MAT_CACHE[key]


def make_2d_sprite_card(
    name: str,
    sprite_filename: str,
    loc,
    height_m: float,
    yaw_deg: float = 0.0,
    anchor_bottom: bool = True,
    emissive_boost: float = 0.0,
    sway_seed: float = None,
    cross_shadow: bool = True,
):
    """
    Places a 2D Pixel-Art Sprite Card in 3D space (standing upright on the 3D terrain).
    If `cross_shadow=True`, adds an invisible-to-camera perpendicular shadow caster so the 2D sprite
    throws full-width 3D cast shadows across the terrain even when the sun is at a steep cross-angle!
    """
    mat, pw, ph = get_2d_sprite_mat(sprite_filename, emissive_boost=emissive_boost)
    aspect = float(pw) / max(1.0, float(ph))
    width_m = height_m * aspect

    bm = bmesh.new()
    z0 = 0.0 if anchor_bottom else -height_m * 0.5
    z1 = height_m if anchor_bottom else height_m * 0.5
    hw = width_m * 0.5

    v0 = bm.verts.new((-hw, 0.0, z0))
    v1 = bm.verts.new(( hw, 0.0, z0))
    v2 = bm.verts.new(( hw, 0.0, z1))
    v3 = bm.verts.new((-hw, 0.0, z1))
    face = bm.faces.new((v0, v1, v2, v3))

    uv_layer = bm.loops.layers.uv.new("UVMap")
    uvs = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    for loop, uv in zip(face.loops, uvs):
        loop[uv_layer].uv = uv

    # Give normals an upward hemisphere tilt so 3D sunlight shades the 2D sprite card evenly!
    mesh = bpy.data.meshes.new(f"{name}_SprMesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.rotation_euler = (0.0, 0.0, math.radians(yaw_deg))
    obj.data.materials.append(mat)
    bpy.context.scene.collection.objects.link(obj)

    if cross_shadow:
        # Perpendicular shadow-only twin card (invisible to camera, visible to Sun shadows!)
        sh_obj = bpy.data.objects.new(f"{name}_ShadowCaster", mesh)
        sh_obj.location = (0.0, 0.0, 0.0)
        sh_obj.rotation_euler = (0.0, 0.0, math.radians(78.0))
        sh_obj.visible_camera = False
        sh_obj.parent = obj
        bpy.context.scene.collection.objects.link(sh_obj)

    if sway_seed is not None:
        drv = obj.driver_add("rotation_euler", 1).driver
        drv.expression = f"0.022 * sin(frame * 0.075 + {sway_seed:.2f})"
    return obj


# =============================================================================
# 3. ZONE 0: FULL SPHERICAL PLANET BALL ORRERY & 4 SOLO PLANET BALLS
# =============================================================================
def populate_starfield(center_loc, count=90, span_x=14.0, y_min=4.0, y_max=22.0, z_min=-10.0, z_max=10.0, mat_star=None, seed=1):
    rng = random.Random(seed)
    cx, cy, cz = center_loc
    for i in range(count):
        sx = cx + rng.uniform(-span_x, span_x)
        sy = cy + rng.uniform(y_min, y_max)
        sz = cz + rng.uniform(z_min, z_max)
        sz_cube = rng.uniform(0.05, 0.11)
        bpy.ops.mesh.primitive_cube_add(size=sz_cube, location=(sx, sy, sz))
        st = bpy.context.active_object
        st.data.materials.append(mat_star)
        st.visible_shadow = False
        for ax in (0, 1, 2):
            d = st.driver_add("scale", ax).driver
            d.expression = f"0.55 + 0.45 * sin(frame * 0.14 + {i * 0.9:.2f})"


def build_zone0_full_planet_balls(mats):
    """Zone 0: 4 Full Spherical Planet Balls (2x2 Orrery at 0,0,0 + 4 Solo Planet Balls along -Y)."""
    orrery_specs = [
        ("Orrery_Ball_W1", (-1.85, 0.0,  1.35), 1.18, "planet_ball_w1.png", "#a8f085"),
        ("Orrery_Ball_W2", ( 1.85, 0.0,  1.35), 1.18, "planet_ball_w2.png", "#82b8ff"),
        ("Orrery_Ball_W3", (-1.85, 0.0, -2.05), 1.18, "planet_ball_w3.png", "#52fff0"),
        ("Orrery_Ball_W4", ( 1.85, 0.0, -2.05), 1.18, "planet_ball_w4.png", "#ff6b38"),
    ]
    for nm, loc, r, tex, atmo in orrery_specs:
        make_full_planet_ball(nm, loc, r, tex, atmo, spin_speed=0.028)
    populate_starfield((0, 0, 0), count=95, mat_star=mats["star"], seed=19)

    solo_specs = [
        ("Solo_Ball_W1", (0, -140, 0), 1.82, "planet_ball_w1.png", "#a8f085"),
        ("Solo_Ball_W2", (0, -280, 0), 1.82, "planet_ball_w2.png", "#82b8ff"),
        ("Solo_Ball_W3", (0, -420, 0), 1.82, "planet_ball_w3.png", "#52fff0"),
        ("Solo_Ball_W4", (0, -560, 0), 1.82, "planet_ball_w4.png", "#ff6b38"),
    ]
    for nm, loc, r, tex, atmo in solo_specs:
        make_full_planet_ball(nm, loc, r, tex, atmo, spin_speed=0.036)
        populate_starfield(loc, count=70, mat_star=mats["star"], seed=hash(nm) & 0xFF)


# =============================================================================
# 4. ZONE 1 (X=200): WORLD 1 — THE WINDMILL STEPPE (3D Terrain + 2D Sprites!)
# =============================================================================
def i1_terrain_z(lx: float, ly: float) -> float:
    river_x = 0.85 * math.sin(ly * 0.22)
    dist = abs(lx - river_x)
    if dist < 2.2:
        return -0.55 + 0.55 * (dist / 2.2) ** 2.2
    step_raw = 0.22 + 0.24 * min(dist - 2.2, 6.5) + 0.38 * max(0.0, (ly - 3.5) * 0.26)
    step = 0.65
    terraced = step_raw * 0.40 + (round(step_raw / step) * step) * 0.60
    return terraced + 0.14 * math.sin(lx * 0.45) * math.cos(ly * 0.40)


def build_zone1_windmill_steppe(mats, i1_start, i1_end):
    """3D Terraced Meadow, River & Waterfall + Detailed 2D Pixel-Art Windmills, Cottages, Trees, Bushes, Flowers & Baker."""
    ox, oy, oz = 200.0, 0.0, 0.0
    bm = bmesh.new()
    nx, ny = 76, 68  # Higher-detail 3D terrain mesh with crisp terraced ledges
    grid = []
    for iy in range(ny):
        ly = -14.0 + 30.0 * iy / (ny - 1)
        row = []
        for ix in range(nx):
            lx = -18.0 + 36.0 * ix / (nx - 1)
            lz = i1_terrain_z(lx, ly)
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
            cx = (v00.co.x + v10.co.x + v11.co.x + v01.co.x) * 0.25 - ox
            cy = (v00.co.y + v10.co.y + v11.co.y + v01.co.y) * 0.25 - oy
            if dz > 0.22 or cz < 0.06:
                f.material_index = 1  # Terraced cliff stone
            elif abs(cy + 1.5) < 1.1 and abs(cx) < 7.5:
                f.material_index = 2  # Cobblestone/dirt path leading across meadow
            else:
                f.material_index = 0  # Lush pixel-art meadow grass
    mesh = bpy.data.meshes.new("I1_SteppeMesh")
    bm.to_mesh(mesh)
    bm.free()
    terr = bpy.data.objects.new("I1_Steppe3DTerrain", mesh)
    terr.data.materials.append(mats["i1_grass"])
    terr.data.materials.append(mats["stone"])
    terr.data.materials.append(mats["dirt_path"])
    bpy.context.scene.collection.objects.link(terr)

    # 3D River & Waterfall plane + 3D stone bridge deck (so water & bridge have real 3D ground depth)
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(ox, oy + 1.5, oz + 0.02))
    river = bpy.context.active_object
    river.scale = (4.8, 26.0, 1.0)
    river.data.materials.append(mats["water"])

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox - 0.5, oy - 11.4, oz - 3.6))
    wfall = bpy.context.active_object
    wfall.scale = (3.4, 0.40, 7.2)
    wfall.data.materials.append(mats["water"])

    for i in range(9):
        u = -1.0 + 2.0 * (i + 0.5) / 9.0
        bx = ox + u * 2.9
        bz = oz + 0.45 + 0.55 * (1.0 - u * u)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bx, oy - 1.5, bz - 0.14))
        blk = bpy.context.active_object
        blk.scale = (0.72, 1.55, 0.28)
        blk.data.materials.append(mats["stone"] if i % 2 == 0 else mats["stone_dark"])

    # --- 2D PIXEL-ART SPRITES IN WORLD 1 ---
    # 1. Three Giant 2D Pixel-Art Windmill Towers + Spinning 2D Sail Rotors!
    windmills = [
        ("I1_Windmill_Hero", (3.6, 2.6), 5.6, 22.0, 0.062, 0.2),
        ("I1_Windmill_West", (-5.0, 5.4), 5.0, -14.0, 0.055, 1.4),
        ("I1_Windmill_Far",  (0.3, 9.8),  4.6, 8.0, 0.058, 2.6),
    ]
    for wname, (wx, wy), wh, wyaw, wspd, wphase in windmills:
        wz = oz + i1_terrain_z(wx, wy) - 0.05
        tw = make_2d_sprite_card(wname, "windmill_tower.png", (ox + wx, oy + wy, wz), height_m=wh, yaw_deg=wyaw, anchor_bottom=True)
        # Spinning 2D Pixel-Art Rotor Sprite placed slightly in front (-Y local) of the upper tower
        rad_y = math.radians(wyaw)
        fx, fy = math.sin(rad_y) * 0.28, -math.cos(rad_y) * 0.28
        rotor = make_2d_sprite_card(
            f"{wname}_Rotor",
            "windmill_rotor.png",
            (ox + wx + fx, oy + wy + fy, wz + wh * 0.72),
            height_m=wh * 0.92,
            yaw_deg=wyaw,
            anchor_bottom=False,
            cross_shadow=False,
        )
        drv = rotor.driver_add("rotation_euler", 1).driver
        drv.expression = f"frame * {wspd:.4f} + {wphase:.2f}"

    # 2. Detailed 2D Pixel-Art Half-Timbered Baker's Cottages + Warm Point Light
    for idx, (cx, cy, ch, cyaw) in enumerate([(-4.0, -0.6, 3.8, -18.0), (5.8, -3.2, 3.3, 24.0)]):
        cz = oz + i1_terrain_z(cx, cy) - 0.05
        make_2d_sprite_card(f"I1_Cottage_{idx}", "cottage_house.png", (ox + cx, oy + cy, cz), height_m=ch, yaw_deg=cyaw, emissive_boost=0.45)

    ov_light = bpy.data.lights.new("I1_CottageLight", type="POINT")
    ov_light.color = (1.0, 0.72, 0.28)
    ov_light.energy = 155.0
    ov_lobj = bpy.data.objects.new("I1_CottageLight", ov_light)
    ov_lobj.location = (ox - 3.2, oy - 1.5, oz + 2.2)
    bpy.context.scene.collection.objects.link(ov_lobj)

    # 3. 2D Pixel-Art Hanging Bridge Lantern
    make_2d_sprite_card("I1_BridgeLantern", "hanging_lantern_sprite.png", (ox - 1.8, oy - 2.1, oz + 1.35), height_m=1.15, yaw_deg=-10.0, emissive_boost=0.85, sway_seed=1.2)

    # 4. Animated 2D Pixel-Art Baker Character Sprite walking across the stone bridge (stepped ON TWOS!)
    baker = make_2d_sprite_card("I1_BakerSprite", "char_baker.png", (ox - 2.0, oy - 1.5, oz + 0.65), height_m=1.55, yaw_deg=0.0, emissive_boost=0.25)
    for f in range(i1_start, i1_end + 1):
        u = (f - i1_start) / max(1, i1_end - i1_start)
        bx = ox - 2.1 + 2.6 * u
        bz = oz + 0.50 + 0.50 * (1.0 - ((bx - ox) / 2.9) ** 2) + abs(math.sin(f * 0.28)) * 0.07
        baker.location = (bx, oy - 1.5, bz)
        baker.keyframe_insert(data_path="location", frame=f)
    apply_stepped_on_twos(baker, step=2)

    # 5. Dense Layered 2D Pixel-Art Trees, Berry Bushes & Wildflower Patches across the 3D terrain!
    tree_placements = [
        (-7.4,  1.4, 4.4, "tree_oak_a.png", -12.0, 101),
        (-6.5, -4.8, 4.0, "tree_pine_a.png", -8.0, 102),
        ( 7.2, -0.8, 4.3, "tree_oak_b.png",  18.0, 103),
        ( 6.8,  5.8, 4.6, "tree_oak_a.png",  15.0, 104),
        (-2.8,  8.6, 4.5, "tree_oak_b.png",  -5.0, 105),
        ( 3.2,  8.8, 4.2, "tree_pine_a.png", 10.0, 106),
        (-8.2,  6.2, 4.4, "tree_pine_a.png", -15.0, 107),
        ( 8.4,  2.6, 4.1, "tree_pine_a.png", 20.0, 108),
        (-4.8, -7.2, 3.8, "tree_oak_a.png", -10.0, 109),
        ( 4.6, -6.8, 3.9, "tree_oak_b.png",  14.0, 110),
    ]
    for idx, (tx, ty, th, tfile, tyaw, tseed) in enumerate(tree_placements):
        tz = oz + i1_terrain_z(tx, ty) - 0.06
        make_2d_sprite_card(f"I1_SprTree_{idx}", tfile, (ox + tx, oy + ty, tz), height_m=th, yaw_deg=tyaw, sway_seed=float(tseed))

    detail_foliage = [
        (-2.6, -2.5, 1.15, "bush_cluster.png", 0.0),
        ( 2.4, -2.4, 1.10, "bush_cluster.png", 12.0),
        (-5.4,  0.8, 1.25, "bush_cluster.png", -15.0),
        ( 2.2,  1.4, 1.20, "bush_cluster.png", 18.0),
        (-1.8,  3.6, 1.15, "bush_cluster.png", -8.0),
        ( 4.8,  0.8, 1.20, "bush_cluster.png", 14.0),
        (-3.2, -3.2, 0.85, "flower_patch.png", 5.0),
        (-1.2, -3.0, 0.80, "flower_patch.png", -6.0),
        ( 1.6, -3.1, 0.85, "flower_patch.png", 10.0),
        ( 3.0,  0.2, 0.90, "flower_patch.png", 15.0),
        (-2.5,  1.2, 0.85, "flower_patch.png", -12.0),
        ( 0.8,  4.2, 0.88, "flower_patch.png", 8.0),
    ]
    for idx, (fx, fy, fh, ffile, fyaw) in enumerate(detail_foliage):
        fz = oz + i1_terrain_z(fx, fy) - 0.04
        make_2d_sprite_card(f"I1_DetailSpr_{idx}", ffile, (ox + fx, oy + fy, fz), height_m=fh, yaw_deg=fyaw, sway_seed=float(idx + 200))


# =============================================================================
# 5. ZONE 2 (X=400): WORLD 2 — THE MIDNIGHT RAIL (3D Cliffs + 2D Sprites!)
# =============================================================================
def build_zone2_midnight_rail(mats, i2_start, i2_end):
    """3D Cliff Gorge, 3D Cloud Sea & 3D Viaduct Deck + 2D Pixel-Art Brass Train, Track Crew, Lanterns & Pines."""
    ox, oy, oz = 400.0, 0.0, 0.0

    # 3D Freezing Cloud Sea plane & 3D jagged cliff gorge walls
    bpy.ops.mesh.primitive_plane_add(size=48.0, location=(ox, oy, oz - 4.5))
    csea = bpy.context.active_object
    csea.data.materials.append(mats["i2_cloudsea"])
    csea.visible_shadow = False

    for lx, ly, sx, sy, sz in [
        (-12.5, 2.5, 5.5, 16.0, 8.5),
        ( 12.5, 2.5, 5.5, 16.0, 8.5),
        (-4.5, 11.5, 7.0,  4.5, 9.8),
        ( 4.5, 11.5, 7.0,  4.5, 9.2),
    ]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox + lx, oy + ly, oz + sz * 0.35 - 3.0))
        cl = bpy.context.active_object
        cl.scale = (sx, sy, sz)
        cl.data.materials.append(mats["i2_cliff"])

    # 3D Stone Viaduct Bridge Deck & Piers (ground surface for the 2D Train & Track-Laying Crew!)
    for px in range(-10, 12, 4):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox + px, oy + 2.0, oz - 1.2))
        pier = bpy.context.active_object
        pier.scale = (1.25, 1.75, 6.6)
        pier.data.materials.append(mats["stone"])
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox + px + 2.0, oy + 2.0, oz + 1.65))
        arch = bpy.context.active_object
        arch.scale = (2.8, 1.65, 0.85)
        arch.data.materials.append(mats["stone_dark"])

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox, oy + 2.0, oz + 2.22))
    deck = bpy.context.active_object
    deck.scale = (22.0, 2.1, 0.36)
    deck.data.materials.append(mats["stone"])

    # --- 2D PIXEL-ART SPRITES IN WORLD 2 ---
    # 1. Animated 2D Pixel-Art Heated Brass Steam Train & Dining Carriage Sprite!
    train_rig = bpy.data.objects.new("I2_TrainRig", None)
    bpy.context.scene.collection.objects.link(train_rig)

    train_spr = make_2d_sprite_card(
        "I2_BrassTrainSprite",
        "brass_train_sprite.png",
        (0.0, 0.0, 0.0),
        height_m=2.75,
        yaw_deg=0.0,
        anchor_bottom=True,
        emissive_boost=0.55,
    )
    train_spr.parent = train_rig

    t_light = bpy.data.lights.new("I2_TrainHeadlamp", type="POINT")
    t_light.color = (1.0, 0.76, 0.32)
    t_light.energy = 240.0
    t_lobj = bpy.data.objects.new("I2_TrainHeadlamp", t_light)
    t_lobj.location = (3.4, -0.6, 1.35)
    t_lobj.parent = train_rig
    bpy.context.scene.collection.objects.link(t_lobj)

    # 2. Animated 2D Pixel-Art Front Track-Laying Crew Sprites right in front of the cowcatcher (stepped ON TWOS!)
    for idx, (wx_off, wy_off, phase) in enumerate([(3.75, -0.35, 0.0), (4.45, 0.25, math.pi)]):
        worker = make_2d_sprite_card(
            f"I2_RailWorkerSpr_{idx}",
            "char_railworker.png",
            (wx_off, wy_off, 0.0),
            height_m=1.55,
            yaw_deg=-15.0,
            anchor_bottom=True,
            emissive_boost=0.35,
        )
        worker.parent = train_rig
        for f in range(i2_start, i2_end + 1):
            worker.rotation_euler = (0.0, 0.24 * math.sin(f * 0.45 + phase), math.radians(-15.0))
            worker.keyframe_insert(data_path="rotation_euler", frame=f)
        apply_stepped_on_twos(worker, step=2)

    for f in range(i2_start, i2_end + 1):
        u = (f - i2_start) / max(1, i2_end - i2_start)
        tx = ox - 3.6 + 4.8 * u
        tz = oz + 2.38 + 0.02 * math.sin(f * 0.9)
        train_rig.location = (tx, oy + 1.9, tz)
        train_rig.keyframe_insert(data_path="location", frame=f)

    # 3. Swaying 2D Pixel-Art Signal Lanterns along Viaduct
    for idx, lx in enumerate([-4.2, 0.4, 4.8]):
        make_2d_sprite_card(
            f"I2_SignalLantern_{idx}",
            "hanging_lantern_sprite.png",
            (ox + lx, oy + 1.15, oz + 4.15),
            height_m=1.25,
            yaw_deg=0.0,
            anchor_bottom=False,
            emissive_boost=0.95,
            sway_seed=float(idx * 1.7 + 3.0),
        )

    # 4. Detailed 2D Pixel-Art Pines, Bushes & Glowing Frost Crystals framing the Viaduct
    pine_nodes = [
        (-6.2, -3.5, -1.2, 4.4, "tree_pine_a.png", 5.0),
        ( 6.4, -3.4, -1.2, 4.3, "tree_pine_a.png", -8.0),
        (-9.4,  4.8,  1.2, 4.6, "tree_pine_a.png", 12.0),
        ( 9.5,  4.6,  1.2, 4.5, "tree_pine_a.png", -12.0),
        (-3.2,  8.8,  1.8, 4.2, "tree_pine_a.png", 0.0),
        ( 3.5,  8.8,  1.8, 4.2, "tree_pine_a.png", 4.0),
    ]
    for idx, (px_x, px_y, px_z, ph, pfile, pyaw) in enumerate(pine_nodes):
        make_2d_sprite_card(f"I2_SprPine_{idx}", pfile, (ox + px_x, oy + px_y, oz + px_z), height_m=ph, yaw_deg=pyaw, sway_seed=float(idx + 300))


# =============================================================================
# 6. ZONE 3 (X=600): WORLD 3 — THE CLOCKWORK SANCTUARY (3D Terraces + 2D Sprites!)
# =============================================================================
def build_zone3_sanctuary(mats):
    """3D Marble Terraces & 3D Turquoise Hot-Spring Pool + 2D Pixel-Art Golden Pagoda Spire, Pavilions, Trees & Scholars."""
    ox, oy, oz = 600.0, 0.0, 0.0

    bm = bmesh.new()
    nx, ny = 72, 72
    grid = []
    for iy in range(ny):
        ly = -16.0 + 34.0 * iy / (ny - 1)
        row = []
        for ix in range(nx):
            lx = -18.0 + 36.0 * ix / (nx - 1)
            rx = 1.0 * math.sin(ly * 0.18)
            dist = abs(lx - rx)
            if dist < 3.5:
                lz = -0.50 + 0.50 * (dist / 3.5) ** 2.3
            else:
                raw = 0.42 + 0.24 * min(dist - 3.5, 4.5) + 0.20 * max(0.0, dist - 8.0)
                step = 0.60
                lz = raw * 0.38 + (round(raw / step) * step) * 0.62
            if ly > 11.5:
                lz += 3.5 * min(1.0, (ly - 11.5) / 4.5)
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
            f.material_index = 1 if (dz > 0.24 or cz < 0.15) else 0
    mesh = bpy.data.meshes.new("I3_SanctuaryMesh")
    bm.to_mesh(mesh)
    bm.free()
    terr = bpy.data.objects.new("I3_Sanctuary3DTerrain", mesh)
    terr.data.materials.append(mats["i3_grass"])
    terr.data.materials.append(mats["i3_marble"])
    bpy.context.scene.collection.objects.link(terr)

    # 3D Turquoise Hot-Spring Mirror Pool & 3D Marble Bridge Deck
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(ox, oy + 0.5, oz + 0.04))
    pool = bpy.context.active_object
    pool.scale = (9.2, 30.0, 1.0)
    pool.data.materials.append(mats["water"])

    for i in range(11):
        u = -1.0 + 2.0 * (i + 0.5) / 11.0
        bx = ox + u * 4.0
        bz = oz + 0.60 + 0.80 * (1.0 - u * u)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bx, oy, bz - 0.15))
        blk = bpy.context.active_object
        blk.scale = (0.72, 1.70, 0.30)
        blk.data.materials.append(mats["i3_marble"] if i % 2 == 0 else mats["i3_gold"])

    # --- 2D PIXEL-ART SPRITES IN WORLD 3 ---
    # 1. Colossal 2D Pixel-Art Clockwork Sanctuary Golden Pagoda Spire (`sanctuary_tower_sprite.png`)
    sx, sy = ox + 4.4, oy + 5.2
    make_2d_sprite_card(
        "I3_SanctuaryTowerSprite",
        "sanctuary_tower_sprite.png",
        (sx, sy, oz + 0.55),
        height_m=9.2,
        yaw_deg=-22.0,
        anchor_bottom=True,
        emissive_boost=0.55,
    )
    # 3 Glowing Cyan Gravity-Tether Beams rising cleanly from the Clockwork Tower spire tip!
    for b_idx, (ang_x, ang_y) in enumerate([(0.0, 0.0), (-0.18, 0.10), (0.16, -0.12)]):
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.14 if b_idx == 0 else 0.09, depth=12.0, location=(sx, sy + 0.35, oz + 14.8))
        beam = bpy.context.active_object
        beam.rotation_euler = (ang_x, ang_y, 0.0)
        beam.data.materials.append(mats["cyan"])
        beam.visible_shadow = False

    sp_light = bpy.data.lights.new("I3_TowerLight", type="POINT")
    sp_light.color = (0.32, 0.92, 1.0)
    sp_light.energy = 185.0
    sp_lobj = bpy.data.objects.new("I3_TowerLight", sp_light)
    sp_lobj.location = (sx - 0.8, sy - 1.0, oz + 5.5)
    bpy.context.scene.collection.objects.link(sp_lobj)

    # 2. Detailed 2D Pixel-Art Marble Garden Pavilions (`marble_pavilion_sprite.png`)
    make_2d_sprite_card("I3_MarblePavilion_W", "marble_pavilion_sprite.png", (ox - 5.2, oy - 1.2, oz + 0.65), height_m=4.0, yaw_deg=24.0, emissive_boost=0.40)
    make_2d_sprite_card("I3_MarblePavilion_N", "marble_pavilion_sprite.png", (ox - 2.4, oy + 7.2, oz + 0.85), height_m=3.6, yaw_deg=8.0, emissive_boost=0.40)

    # 3. 2D Pixel-Art Sanctuary Scholar Character Sprites (`char_scholar.png`)
    make_2d_sprite_card("I3_Scholar_1", "char_scholar.png", (ox - 2.8, oy - 0.6, oz + 0.72), height_m=1.60, yaw_deg=18.0, emissive_boost=0.35, sway_seed=4.1)
    make_2d_sprite_card("I3_Scholar_2", "char_scholar.png", (ox + 0.4, oy + 0.0, oz + 1.38), height_m=1.55, yaw_deg=-12.0, emissive_boost=0.35, sway_seed=5.4)

    # 4. Dense 2D Pixel-Art Golden & Emerald Ghibli Trees, Bushes & Flower Patches
    sanc_trees = [
        (-5.8,  3.6, 4.3, "tree_gold_a.png",  16.0, 301),
        (-7.0, -4.2, 4.1, "tree_pine_a.png",  20.0, 302),
        ( 5.6, -2.6, 4.2, "tree_gold_a.png", -18.0, 303),
        ( 8.2,  2.4, 4.5, "tree_oak_a.png",  -24.0, 304),
        (-3.2,  9.6, 4.4, "tree_gold_a.png",   6.0, 305),
        ( 1.6, 10.2, 4.2, "tree_pine_a.png",  -8.0, 306),
        (-8.4,  0.5, 4.3, "tree_oak_b.png",   22.0, 307),
        ( 7.4,  7.6, 4.4, "tree_gold_a.png", -16.0, 308),
    ]
    for idx, (tx, ty, th, tfile, tyaw, tseed) in enumerate(sanc_trees):
        make_2d_sprite_card(f"I3_SprTree_{idx}", tfile, (ox + tx, oy + ty, oz + 0.60), height_m=th, yaw_deg=tyaw, sway_seed=float(tseed))

    sanc_foliage = [
        (-3.6,  1.5, 1.20, "bush_cluster.png", 15.0),
        ( 3.4,  1.6, 1.15, "bush_cluster.png", -15.0),
        (-4.2, -3.2, 0.90, "flower_patch.png", 12.0),
        ( 3.8, -1.8, 0.90, "flower_patch.png", -12.0),
        (-1.8,  4.2, 0.88, "flower_patch.png", 6.0),
        ( 2.2,  3.2, 0.92, "flower_patch.png", -10.0),
    ]
    for idx, (fx, fy, fh, ffile, fyaw) in enumerate(sanc_foliage):
        make_2d_sprite_card(f"I3_DetailSpr_{idx}", ffile, (ox + fx, oy + fy, oz + 0.55), height_m=fh, yaw_deg=fyaw, sway_seed=float(idx + 350))


# =============================================================================
# 7. ZONE 4 (X=800): WORLD 4 — THE BALLAST QUARRY (3D Crater + 2D Sprites!)
# =============================================================================
def build_zone4_ballast_quarry(mats, i4_start, i4_end):
    """3D Stepped Obsidian Quarry Pit + 2D Pixel-Art Riveted Iron Chains, Glowing Sky-Stone Crystals & Miners."""
    ox, oy, oz = 800.0, 0.0, 0.0

    bm = bmesh.new()
    nx, ny = 68, 68
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
                step = 0.80
                lz = -1.5 + wall * 0.40 + (round(wall / step) * step) * 0.60
            row.append(bm.verts.new((ox + lx, oy + ly, oz + lz)))
        grid.append(row)
    bm.verts.ensure_lookup_table()
    for iy in range(ny - 1):
        for ix in range(nx - 1):
            f = bm.faces.new((grid[iy][ix], grid[iy][ix + 1], grid[iy + 1][ix + 1], grid[iy + 1][ix]))
            f.smooth = False
            f.material_index = 0
    mesh = bpy.data.meshes.new("I4_QuarryMesh")
    bm.to_mesh(mesh)
    bm.free()
    terr = bpy.data.objects.new("I4_Quarry3DTerrain", mesh)
    terr.data.materials.append(mats["i4_obs"])
    bpy.context.scene.collection.objects.link(terr)

    # 3D Glowing Molten Sky-Stone Pool & 3D Iron Gantry Deck
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=4.6, depth=0.3, location=(ox, oy, oz - 1.35))
    cbed = bpy.context.active_object
    cbed.data.materials.append(mats["lava"])
    cbed.visible_shadow = False

    for i in range(13):
        bx = ox - 4.8 + 9.6 * i / 12.0
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bx, oy - 0.5, oz + 1.55))
        cat = bpy.context.active_object
        cat.scale = (0.76, 1.55, 0.24)
        cat.data.materials.append(mats["i4_iron"])

    # Vertical Sky-Crane Gravity Beam positioned behind gantry on north crystal mooring (unobstructed miner!)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.18, depth=18.0, location=(ox + 2.4, oy + 3.2, oz + 9.2))
    sbeam = bpy.context.active_object
    sbeam.data.materials.append(mats["cyan"])
    sbeam.visible_shadow = False

    fl = bpy.data.lights.new("I4_QuarryLight", type="POINT")
    fl.color = (1.0, 0.44, 0.16)
    fl.energy = 280.0
    fobj = bpy.data.objects.new("I4_QuarryLight", fl)
    fobj.location = (ox, oy + 2.4, oz + 2.8)
    bpy.context.scene.collection.objects.link(fobj)

    # --- 2D PIXEL-ART SPRITES IN WORLD 4 ---
    # 1. Six Colossal 2D Pixel-Art Riveted Iron Anchor Chain Columns (`iron_chain_sprite.png`) stretching into the storm!
    chain_spots = [
        (-3.6, 4.8, 0.8, 7.2, 8.0),
        ( 0.0, 5.2, 0.8, 7.6, 0.0),
        ( 3.6, 4.8, 0.8, 7.2, -8.0),
        ( 1.8, -0.5, 1.5, 6.8, 12.0),
        (-5.2, 2.2, 1.4, 6.8, 16.0),
        ( 5.2, 2.2, 1.4, 6.8, -16.0),
    ]
    for idx, (cx, cy, cz, ch, cyaw) in enumerate(chain_spots):
        make_2d_sprite_card(
            f"I4_SprChain_{idx}",
            "iron_chain_sprite.png",
            (ox + cx, oy + cy, oz + cz),
            height_m=ch,
            yaw_deg=cyaw,
            anchor_bottom=True,
            emissive_boost=0.45,
        )
        # Stack a second tier up to z = +14m so chains reach all the way into the clouds!
        make_2d_sprite_card(
            f"I4_SprChainTop_{idx}",
            "iron_chain_sprite.png",
            (ox + cx, oy + cy, oz + cz + ch * 0.94),
            height_m=ch,
            yaw_deg=cyaw,
            anchor_bottom=True,
            emissive_boost=0.45,
        )

    # 2. Multifaceted 2D Pixel-Art Glowing Sky-Stone Crystal Clusters (`crystal_cyan.png`, `crystal_amber.png`)
    rng = random.Random(409)
    for i in range(14):
        ang = i * math.tau / 14.0
        cr_r = rng.uniform(2.8, 5.8)
        cx = cr_r * math.cos(ang)
        cy = cr_r * math.sin(ang)
        cfile = "crystal_cyan.png" if i % 2 == 0 else "crystal_amber.png"
        make_2d_sprite_card(
            f"I4_SprCrystal_{i}",
            cfile,
            (ox + cx, oy + cy, oz - 0.9),
            height_m=rng.uniform(1.8, 2.8),
            yaw_deg=rng.uniform(-22.0, 22.0),
            anchor_bottom=True,
            emissive_boost=0.85,
        )

    # 3. Animated 2D Pixel-Art Quarry Miner Character Sprites (`char_miner.png`, stepped ON TWOS!)
    miner = make_2d_sprite_card(
        "I4_MinerSprite",
        "char_miner.png",
        (ox - 0.5, oy - 0.5, oz + 1.68),
        height_m=1.62,
        yaw_deg=14.0,
        anchor_bottom=True,
        emissive_boost=0.45,
    )
    for f in range(i4_start, i4_end + 1):
        u = (f - i4_start) / max(1, i4_end - i4_start)
        miner.location = (ox - 0.6 + 1.1 * u, oy - 0.5, oz + 1.68 + abs(math.sin(f * 0.26)) * 0.06)
        miner.keyframe_insert(data_path="location", frame=f)
    apply_stepped_on_twos(miner, step=2)

    make_2d_sprite_card(
        "I4_MinerSprite_2",
        "char_miner.png",
        (ox + 2.4, oy - 0.5, oz + 1.68),
        height_m=1.55,
        yaw_deg=-18.0,
        anchor_bottom=True,
        emissive_boost=0.45,
        sway_seed=7.2,
    )


def setup_world_lighting_and_sky(scene, spans):
    bg, sky_ramp = setup_sky_world(scene, horizon_hex="#131630", zenith_hex="#090b1a", ground_hex="#080914", strength=0.30)

    sdata = bpy.data.lights.new("UndershineSun", type="SUN")
    sdata.angle = 0.008  # Razor-sharp graphic 3D shadows cast by our 2D pixel sprites!
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
    w1_0, w1_1 = spans["island1"]
    w2_0, w2_1 = spans["island2"]
    w3_0, w3_1 = spans["island3"]
    w4_0, w4_1 = spans["island4"]

    w1_g_end = w1_0 + 22
    w2_g_end = w2_0 + 22
    w3_g_end = w3_0 + 22
    w4_g_end = w4_0 + 22
    w3_b = w3_g_end + int((w3_1 - w3_g_end) * 0.68)

    sky_sun_keys = [
        (1,            "#161936", "#090b1a", 0.34, 28.0, -45.0, 2.8, (0.95, 0.92, 1.0)),
        (w1_0,         "#161936", "#090b1a", 0.34, 24.0, -42.0, 3.0, (1.0, 0.88, 0.72)),
        (w1_g_end + 1, "#ebb378", "#2d3d73", 0.62, 22.0, -54.0, 3.8, (1.0, 0.82, 0.56)),
        (w2_0,         "#161936", "#090b1a", 0.34, 26.0, -40.0, 2.8, (0.85, 0.95, 1.0)),
        (w2_g_end + 1, "#c98b68", "#1d2d4e", 0.50, 20.0, -50.0, 3.2, (1.0, 0.78, 0.55)),
        (w3_0,         "#161936", "#090b1a", 0.34, 28.0, -44.0, 3.0, (0.88, 0.95, 1.0)),
        (w3_g_end + 1, "#eba97c", "#394d88", 0.62, 24.0, -58.0, 3.7, (1.0, 0.82, 0.58)),
        (w3_b + 1,     "#1e1f45", "#0c0f26", 0.24, 15.0, -72.0, 0.65, (0.42, 0.54, 0.96)),
        (w4_0,         "#161936", "#090b1a", 0.34, 24.0, -38.0, 3.0, (1.0, 0.72, 0.52)),
        (w4_g_end + 1, "#6e363c", "#17162e", 0.40, 22.0, -52.0, 2.2, (1.0, 0.64, 0.42)),
    ]

    e_hor = sky_ramp.color_ramp.elements[1]
    e_zen = sky_ramp.color_ramp.elements[2]
    for f, hh, zh, bs, el, az, en, rgb in sky_sun_keys:
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

    for holder in (scene.world.node_tree, sobj, sdata):
        set_action_interpolation(holder, "CONSTANT")


def setup_17_cameras(scene, spans):
    scene.timeline_markers.clear()

    def island_splits(s_f, e_f):
        g_end = s_f + 22  # ~0.73s solo full planet ball card
        rem = e_f - g_end
        c1 = g_end + int(rem * 0.34)
        c2 = g_end + int(rem * 0.68)
        return g_end, c1, c2

    i0, i1 = spans["intro"]
    w1_0, w1_1 = spans["island1"]
    w2_0, w2_1 = spans["island2"]
    w3_0, w3_1 = spans["island3"]
    w4_0, w4_1 = spans["island4"]

    w1g, w1a, w1b = island_splits(w1_0, w1_1)
    w2g, w2a, w2b = island_splits(w2_0, w2_1)
    w3g, w3a, w3b = island_splits(w3_0, w3_1)
    w4g, w4a, w4b = island_splits(w4_0, w4_1)

    shots = [
        # Intro 2x2 Full Spherical Planet Ball Orrery
        {"name": "00_Orrery_Countdown", "start": i0, "end": i1, "lens": 38.0,
         "pos_start": (0.0, -14.6, -0.30), "pos_end": (0.0, -12.2, -0.25),
         "tgt_start": (0.0, 0.0, -0.20), "tgt_end": (0.0, 0.0, -0.20), "roll": 0.0, "orbit": 0.0},

        # World 1 — The Windmill Steppe (X=200)
        {"name": "01_I1_Globe", "start": w1_0, "end": w1g, "lens": 36.0,
         "pos_start": (0.0, -149.6, 0.5), "pos_end": (0.0, -148.0, 0.3),
         "tgt_start": (0.0, -140.0, 0.0), "tgt_end": (0.0, -140.0, 0.0), "roll": 0.0, "orbit": 8.0},
        {"name": "02_I1_IsoSteppe", "start": w1g + 1, "end": w1a, "lens": 50.0,
         "pos_start": (209.5, -15.5, 10.6), "pos_end": (211.0, -14.0, 9.6),
         "tgt_start": (199.8, 1.2, 2.2), "tgt_end": (200.4, 1.6, 2.4), "roll": 0.0, "orbit": 4.0},
        {"name": "03_I1_LowWindmill", "start": w1a + 1, "end": w1b, "lens": 28.0,
         "pos_start": (200.2, -5.2, 1.35), "pos_end": (201.4, -4.2, 1.55),
         "tgt_start": (203.2, 2.4, 3.8), "tgt_end": (203.5, 2.6, 4.1), "roll": 0.0, "orbit": 0.0},
        {"name": "04_I1_PeekCottage", "start": w1b + 1, "end": w1_1, "lens": 35.0,
         "pos_start": (199.8, -7.4, 2.2), "pos_end": (198.4, -6.0, 2.0),
         "tgt_start": (197.2, -1.0, 1.6), "tgt_end": (198.5, -1.0, 1.5), "roll": 0.0, "orbit": 0.0},

        # World 2 — The Midnight Rail (X=400)
        {"name": "05_I2_Globe", "start": w2_0, "end": w2g, "lens": 36.0,
         "pos_start": (0.0, -289.6, 0.5), "pos_end": (0.0, -288.0, 0.3),
         "tgt_start": (0.0, -280.0, 0.0), "tgt_end": (0.0, -280.0, 0.0), "roll": 0.0, "orbit": -8.0},
        {"name": "06_I2_SideTrackTrain", "start": w2g + 1, "end": w2a, "lens": 42.0,
         "pos_start": (395.5, -8.6, 3.8), "pos_end": (403.5, -8.2, 4.1),
         "tgt_start": (397.5, 1.9, 3.4), "tgt_end": (401.2, 1.9, 3.5), "roll": 0.0, "orbit": 0.0},
        {"name": "07_I2_BirdsEyeViaduct", "start": w2a + 1, "end": w2b, "lens": 44.0,
         "pos_start": (399.0, -6.5, 13.5), "pos_end": (401.2, -5.2, 11.8),
         "tgt_start": (399.5, 1.9, 2.8), "tgt_end": (400.8, 1.9, 2.8), "roll": 0.0, "orbit": -8.0},
        {"name": "08_I2_DutchFrontTrack", "start": w2b + 1, "end": w2_1, "lens": 38.0,
         "pos_start": (405.8, -4.6, 3.8), "pos_end": (404.8, -3.8, 3.6),
         "tgt_start": (403.0, 1.8, 3.3), "tgt_end": (403.8, 1.9, 3.3), "roll": 6.0, "orbit": 0.0},

        # World 3 — The Clockwork Sanctuary (X=600)
        {"name": "09_I3_Globe", "start": w3_0, "end": w3g, "lens": 36.0,
         "pos_start": (0.0, -429.6, 0.5), "pos_end": (0.0, -428.0, 0.3),
         "tgt_start": (0.0, -420.0, 0.0), "tgt_end": (0.0, -420.0, 0.0), "roll": 0.0, "orbit": 8.0},
        {"name": "10_I3_IsoSanctuary", "start": w3g + 1, "end": w3a, "lens": 48.0,
         "pos_start": (589.5, -13.5, 10.4), "pos_end": (591.5, -11.8, 9.2),
         "tgt_start": (600.2, 2.0, 2.6), "tgt_end": (600.8, 2.5, 2.8), "roll": 0.0, "orbit": 5.0},
        {"name": "11_I3_OTS_Garden", "start": w3a + 1, "end": w3b, "lens": 34.0,
         "pos_start": (598.2, -5.6, 2.25), "pos_end": (599.2, -4.2, 2.45),
         "tgt_start": (596.8, 0.2, 2.1), "tgt_end": (601.8, 3.2, 3.4), "roll": 0.0, "orbit": 0.0},
        {"name": "12_I3_TowerTwilight", "start": w3b + 1, "end": w3_1, "lens": 28.0,
         "pos_start": (600.2, -1.2, 1.5), "pos_end": (601.4, -0.2, 1.9),
         "tgt_start": (604.2, 5.2, 4.8), "tgt_end": (604.2, 5.2, 5.6), "roll": 0.0, "orbit": 0.0},

        # World 4 — The Ballast Quarry (X=800)
        {"name": "13_I4_Globe", "start": w4_0, "end": w4g, "lens": 36.0,
         "pos_start": (0.0, -569.6, 0.5), "pos_end": (0.0, -568.0, 0.3),
         "tgt_start": (0.0, -560.0, 0.0), "tgt_end": (0.0, -560.0, 0.0), "roll": 0.0, "orbit": -8.0},
        {"name": "14_I4_CraneQuarry", "start": w4g + 1, "end": w4a, "lens": 30.0,
         "pos_start": (808.2, -7.8, 8.8), "pos_end": (805.2, -10.2, 10.2),
         "tgt_start": (799.8, 1.2, 2.4), "tgt_end": (799.8, 1.5, 2.8), "roll": 0.0, "orbit": 8.0},
        {"name": "15_I4_LowChains", "start": w4a + 1, "end": w4b, "lens": 27.0,
         "pos_start": (796.2, -5.2, 1.15), "pos_end": (797.6, -3.8, 1.45),
         "tgt_start": (800.2, 4.5, 4.6), "tgt_end": (800.4, 4.8, 5.2), "roll": -5.5, "orbit": 0.0},
        {"name": "16_I4_PullbackSever", "start": w4b + 1, "end": w4_1, "lens": 35.0,
         "pos_start": (796.2, -3.2, 2.8), "pos_end": (791.5, -7.2, 5.6),
         "tgt_start": (800.2, 0.2, 2.8), "tgt_end": (800.6, 1.2, 4.2), "roll": 0.0, "orbit": 5.0,
         "kick_frame": max(w4b + 5, w4_1 - 30)},
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
            kick_frame=s.get("kick_frame"),
            kick_amp=0.22,
        )
        cam.data.clip_end = 110.0
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
        "i1_grass": make_hue_shifted_toon_mat("Mat_I1_Grass", "#1d363d", "#4a7c4e", "#9cc258", deep_shadow_hex="#13222b", grain_scale=6.2, grain_amt=0.18, snap_step=0.12),
        "dirt_path": make_hue_shifted_toon_mat("Mat_DirtPath", "#2b1d2e", "#785342", "#c49266", deep_shadow_hex="#1b1221", grain_scale=7.0, grain_amt=0.18, snap_step=0.11),
        "i2_cliff": make_hue_shifted_toon_mat("Mat_I2_Cliff", "#1c1c36", "#4f4c69", "#9e8e84", deep_shadow_hex="#121226", grain_scale=5.2, grain_amt=0.19, snap_step=0.14),
        "i2_cloudsea": make_emissive_mat("Mat_I2_CloudSea", "#344878", strength=1.2),
        "i3_grass": make_hue_shifted_toon_mat("Mat_I3_Grass", "#1f3842", "#4b7d53", "#9ec261", deep_shadow_hex="#142330", grain_scale=6.0, grain_amt=0.17, snap_step=0.12),
        "i3_marble": make_hue_shifted_toon_mat("Mat_I3_Marble", "#2d2d4a", "#85839c", "#e6dccf", deep_shadow_hex="#1b1b32", grain_scale=6.5, grain_amt=0.15, snap_step=0.12),
        "i3_gold": make_hue_shifted_toon_mat("Mat_I3_Gold", "#38222e", "#a87238", "#f5c862", deep_shadow_hex="#241520", grain_scale=6.5, grain_amt=0.15, snap_step=0.12),
        "i4_obs": make_hue_shifted_toon_mat("Mat_I4_Obsidian", "#151424", "#2e2a40", "#594b5e", deep_shadow_hex="#0e0d1a", grain_scale=5.2, grain_amt=0.20, snap_step=0.14),
        "i4_iron": make_hue_shifted_toon_mat("Mat_I4_Iron", "#191829", "#3c394d", "#786970", deep_shadow_hex="#10101f", grain_scale=5.8, grain_amt=0.16, snap_step=0.12),
        "stone": make_hue_shifted_toon_mat("Mat_Stone", "#211f38", "#736f82", "#bfb1a0", deep_shadow_hex="#161529", grain_scale=6.2, grain_amt=0.17, snap_step=0.12),
        "stone_dark": make_hue_shifted_toon_mat("Mat_StoneDark", "#161529", "#4f4c63", "#8a7f87", deep_shadow_hex="#0f0e1f", grain_scale=6.0, grain_amt=0.17, snap_step=0.12),
        "water": make_water_mat("Mat_Water"),
        "amber": make_emissive_mat("Mat_Amber", "#ffbd4a", strength=3.6),
        "cyan": make_emissive_mat("Mat_Cyan", "#45f0e5", strength=3.2),
        "lava": make_emissive_mat("Mat_Lava", "#ff521c", strength=3.8),
        "star": make_emissive_mat("Mat_Star", "#dce6ff", strength=2.6),
    }

    build_zone0_full_planet_balls(mats)
    build_zone1_windmill_steppe(mats, spans["island1"][0], spans["island1"][1])
    build_zone2_midnight_rail(mats, spans["island2"][0], spans["island2"][1])
    build_zone3_sanctuary(mats)
    build_zone4_ballast_quarry(mats, spans["island4"][0], spans["island4"][1])

    setup_world_lighting_and_sky(scene, spans)
    meta_shots = setup_17_cameras(scene, spans)

    passes_dir = os.path.join(BASE, "passes")
    setup_passes_compositor(scene, passes_dir, depth_max=60.0)

    blend_path = os.path.join(BASE, "sky_islands.blend")
    if "--range" not in sys.argv:
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        print(f"[OK] Saved 2.5D Hybrid Blender 5.3 scene -> {blend_path} ({total_frames} frames)")

    if "--preview" in sys.argv:
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
        print(f"[OK] Rendered frames {scene.frame_start}..{scene.frame_end}!")
    else:
        scene.render.filepath = os.path.join(passes_dir, "_dummy_")
        bpy.ops.render.render(animation=True)
        print(f"[OK] Rendered full {total_frames}-frame 2.5D Hybrid sequence!")


if __name__ == "__main__":
    main()
