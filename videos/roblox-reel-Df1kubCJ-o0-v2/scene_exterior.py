"""
scene_exterior.py — Set 3: Iconic Bun Town Diner Facade (Daytime) & Rejection Letter Close-Up.
Renders beats: b10_bun_town, b35_no_job, b36_letter, b37_almost.
"""
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

PROJ_DIR = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking\videos\roblox-reel-Df1kubCJ-o0-v2")
sys.path.insert(0, str(PROJ_DIR))
import scene_common as sc
import char_factory as cf
import props_factory as pf
import blender_cinema_lib as bcl


def _make_uv_plane(name: str, loc, w: float, h: float, mat, col):
    """Pure-bmesh right-reading upright plane facing +Y camera."""
    bm = bmesh.new()
    v0 = bm.verts.new(( w * 0.5, 0.0, -h * 0.5))
    v1 = bm.verts.new((-w * 0.5, 0.0, -h * 0.5))
    v2 = bm.verts.new((-w * 0.5, 0.0,  h * 0.5))
    v3 = bm.verts.new(( w * 0.5, 0.0,  h * 0.5))
    f = bm.faces.new((v0, v1, v2, v3))
    uv = bm.loops.layers.uv.new("UVMap")
    uvs = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    for lp, uvc in zip(f.loops, uvs):
        lp[uv].uv = uvc
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    o = bpy.data.objects.new(name, mesh)
    o.location = loc
    col.objects.link(o)
    o.data.materials.append(mat)
    return o


def build_exterior_set(scene):
    col = bpy.data.collections.new("Set_BunTownExt")
    scene.collection.children.link(col)

    m_asph = sc.make_textured_pbr("Mat_ExtAsph", sc.TEX_ENV / "asphalt_speckled.png", sc.TEX_ENV / "asphalt_speckled_bump.png", uv_scale=(0.80, 0.80, 0.80), rough_min=0.72, rough_max=0.90, coat=0.0)
    m_pave = sc.make_textured_pbr("Mat_ExtPave", sc.TEX_ENV / "sidewalk_pavers.png", sc.TEX_ENV / "sidewalk_pavers_bump.png", uv_scale=(0.85, 0.85, 0.85), rough_min=0.66, rough_max=0.86, coat=0.0)
    m_curb = sc.make_stylized_pbr("Mat_ExtCurb", "#CBD5E1", rough=0.72, coat=0.0)
    m_cream = sc.make_stylized_pbr("Mat_BTCream", "#FBF5EA", rough=0.65, coat=0.0, bump_str=0.02)
    m_teal = sc.make_stylized_pbr("Mat_BTTeal", "#0D9488", rough=0.45, coat=0.08)
    m_red = sc.make_stylized_pbr("Mat_BTRed", "#DC2626", rough=0.45, coat=0.06)
    m_wht = sc.make_stylized_pbr("Mat_BTWht", "#F8FAFC", rough=0.52, coat=0.0)
    m_glass = sc.make_stylized_pbr("Mat_BTGlass", "#BAE6FD", rough=0.08, coat=0.45, alpha=0.26)
    m_tile_in = sc.make_textured_pbr("Mat_BTInTile", sc.TEX_ENV / "tile_cream_diner.png", uv_scale=(0.80, 0.80, 0.80), coat=0.06)

    # Street, crosswalk, curb, paver sidewalk
    pf.make_bevel_box("Road", (0, 2.2, -0.15), (26, 4.6, 0.30), m_asph, col, bevel_w=0.02)
    pf.make_bevel_box("Curb", (0, -0.05, -0.04), (26, 0.22, 0.14), m_curb, col, bevel_w=0.015)
    pf.make_bevel_box("Sidewalk", (0, -1.35, -0.05), (26, 2.6, 0.20), m_pave, col, bevel_w=0.02)
    for ix in range(-6, 7, 1):
        if ix % 2 == 0:
            pf.make_bevel_box(f"Cross_{ix}", (ix * 0.68, 1.35, 0.008), (0.36, 1.45, 0.016), m_wht, col, bevel_w=0.004)

    # BUN TOWN Building Shell (Main facade at y = -2.65, interior depth behind glass!)
    pf.make_bevel_box("BT_WallL", (-3.35, -2.65, 1.65), (1.9, 0.32, 3.3), m_cream, col, bevel_w=0.02)
    pf.make_bevel_box("BT_WallR", ( 3.35, -2.65, 1.65), (1.9, 0.32, 3.3), m_cream, col, bevel_w=0.02)
    pf.make_bevel_box("BT_WallTop", (0.0, -2.65, 3.15), (8.6, 0.36, 0.90), m_cream, col, bevel_w=0.02)
    pf.make_bevel_box("BT_WainL", (-3.35, -2.52, 0.45), (1.92, 0.12, 0.90), m_teal, col, bevel_w=0.015)
    pf.make_bevel_box("BT_WainR", ( 3.35, -2.52, 0.45), (1.92, 0.12, 0.90), m_teal, col, bevel_w=0.015)
    pf.make_bevel_box("BT_RoofTeal", (0.0, -2.65, 3.68), (8.8, 1.6, 0.28), m_teal, col, bevel_w=0.02)
    # Interior counter & wrapped burger shelf visible behind transparent glass doors!
    pf.make_bevel_box("BT_InFloor", (0, -4.6, -0.05), (8.4, 3.8, 0.12), m_tile_in, col)
    pf.make_bevel_box("BT_InBack",  (0, -6.4, 1.8), (8.6, 0.2, 3.8), m_cream, col)
    pf.make_bevel_box("BT_InCount", (0, -4.4, 0.48), (4.6, 0.7, 0.96), m_teal, col, bevel_w=0.02)
    pf.make_bevel_box("BT_InCountTop", (0, -4.4, 0.98), (4.7, 0.76, 0.08), m_cream, col, bevel_w=0.01)
    for bx in (-1.2, 0.0, 1.2):
        pf.build_wrapped_burger(f"BT_InWB_{bx}", (bx, -4.4, 1.02), col, scale=0.85)

    # Glass Doors + Large Display Windows
    pf.make_bevel_box("BT_GlassCenter", (0, -2.65, 1.35), (4.8, 0.04, 2.6), m_glass, col, bevel_w=0.005)
    for mx in (-2.4, -0.8, 0.8, 2.4):
        pf.make_bevel_box(f"BT_Mullion_{mx}", (mx, -2.62, 1.35), (0.09, 0.14, 2.65), m_teal, col, bevel_w=0.01)
    pf.make_bevel_box("BT_DoorTransom", (0, -2.60, 2.66), (4.9, 0.16, 0.12), m_teal, col, bevel_w=0.01)

    # Slanted Striped Red-and-Cream Awning Roof!
    for si in range(16):
        ax = -3.8 + si * 0.506
        mat_s = m_red if (si % 2 == 0) else m_wht
        pf.make_bevel_box(f"Awning_{si}", (ax, -2.05, 2.90), (0.50, 1.15, 0.10), mat_s, col, bevel_w=0.01, rot=(math.radians(16), 0, 0))

    # Giant BUN TOWN Roof Marquee Sign + Giant 3D Smiling Burger Mascot on Roof (cleanly IN FRONT of BT_RoofTeal!)
    m_marquee = sc.make_textured_pbr("Mat_Marquee", sc.TEX_PROPS / "sign_buntown_marquee.png", proj="UV", rough_min=0.38, rough_max=0.48, coat=0.0, emit_str=0.04, ao_str=0.04)
    pf.make_bevel_box("MarqueeBack", (0, -1.86, 4.18), (4.65, 0.14, 1.26), m_teal, col, bevel_w=0.02)
    _make_uv_plane("Sign_BunTown", (0.0, -1.78, 4.18), 4.5, 1.20, m_marquee, col)
    pf.build_hero_burger("RoofMascotBurger", (0.0, -1.85, 4.82), col, scale=3.0)

    # Crisp "NOW HIRING: BURGER WRAPPER" Poster in right storefront window (viewer's right = -X)!
    m_hire = sc.make_textured_pbr("Mat_NowHiring", sc.TEX_PROPS / "sign_now_hiring.png", proj="UV", rough_min=0.42, rough_max=0.52, coat=0.0, emit_str=0.02, ao_str=0.04)
    _make_uv_plane("Sign_NowHiring", (-1.55, -2.48, 1.38), 0.98, 1.18, m_hire, col)
    pf.make_bevel_box("HireBack", (-1.55, -2.53, 1.38), (1.02, 0.05, 1.22), m_wht, col, bevel_w=0.008)

    # Terracotta Potted Shrubs flanking door + Red Sidewalk Fire Hydrant + Neighboring Townhouses & Trees!
    m_pot = sc.make_stylized_pbr("Mat_ExtPot", "#C2410C", rough=0.68, coat=0.0)
    m_bush = sc.make_stylized_pbr("Mat_ExtBush", "#22C55E", rough=0.68, coat=0.0, sss=0.08, bump_str=0.05)
    for px in (-2.55, 2.55):
        pf.make_smooth_cyl(f"Pot_{px}", (px, -2.05, 0.24), 0.26, 0.48, m_pot, col, segs=22, bevel_w=0.015)
        pf.make_smooth_sphere(f"Bush_{px}", (px, -2.05, 0.62), (0.34, 0.34, 0.30), m_bush, col, segs=20)
    pf.make_smooth_cyl("Hydrant_Body", (-2.6, -0.35, 0.28), 0.11, 0.52, m_red, col, segs=18, bevel_w=0.015)
    pf.make_smooth_sphere("Hydrant_Cap", (-2.6, -0.35, 0.56), (0.12, 0.12, 0.09), m_red, col, segs=16)

    # Distant background houses, trees & clouds so background is rich & never flat!
    pf.build_townhouse("SideHouse_L", (7.2, -4.5, 0.0), col, 4.2, 3.8, 5.4, "#93C5FD", "#EA580C", is_night=False)
    pf.build_townhouse("SideHouse_R", (-7.2, -4.5, 0.0), col, 4.2, 3.8, 5.0, "#FDE68A", "#2563EB", is_night=False)
    pf.build_bumpy_tree("ExtTree_L", (4.8, -3.5, 0.0), col, scale=1.15)
    pf.build_bumpy_tree("ExtTree_R", (-4.8, -3.5, 0.0), col, scale=1.08)
    m_cloud = sc.make_stylized_pbr("Mat_ExtCloud", "#FFFFFF", rough=0.72, coat=0.0, sss=0.08)
    for ci, (cx, cy, cz) in enumerate([(-4.5, -9.0, 6.2), (3.8, -10.0, 6.8)]):
        for ox, oy, oz, sc_c in [(0, 0, 0, (1.5, 0.7, 0.7)), (-0.9, 0, -0.1, (1.0, 0.6, 0.55)), (0.9, 0, -0.1, (1.0, 0.6, 0.55))]:
            pf.make_smooth_sphere(f"ExtCloud_{ci}_{ox}", (cx + ox, cy + oy, cz + oz), sc_c, m_cloud, col, segs=16)

    # Rejection Letter Card ("Thank you for wrapping my tie.") — crisp rounded card with soft slate backing!
    m_let = sc.make_textured_pbr("Mat_ExtLetter", sc.TEX_PROPS / "letter_tie.png", proj="UV", rough_min=0.45, rough_max=0.55, coat=0.0, emit_str=0.0, ao_str=0.02, alpha_clip=True)
    letter_root = bpy.data.objects.new("Prop_RejectionLetter", None)
    letter_root.location = (0.38, -0.05, 1.05)
    col.objects.link(letter_root)
    pf.make_bevel_box("Letter_Backing", (0, -0.012, 0), (0.49, 0.015, 0.61), sc.make_stylized_pbr("Mat_LetBack", "#94A3B8", rough=0.55, coat=0.0), col, bevel_w=0.008, segs=2, parent=letter_root)
    lp_plane = _make_uv_plane("Letter_Face", (0, 0.0, 0), 0.48, 0.60, m_let, col)
    lp_plane.parent = letter_root

    # Crisp Pixar Blue Daytime Sky & Balanced Stylized Lighting (zero milky haze!)
    sc.setup_stylized_sky_world(scene, "day", strength=0.68)
    sun_d = bpy.data.lights.new("Sun_Ext", type="SUN")
    sun_d.energy = 2.5
    sun_d.angle = math.radians(1.5)
    sun = bpy.data.objects.new("Sun_Ext", sun_d)
    col.objects.link(sun)
    sun.rotation_euler = (math.radians(42), math.radians(-20), math.radians(24))

    for nm, loc, tgt, en, sz, temp, spr in [
        ("Ext_FrontFill", (0.8, 4.5, 2.6), (0.0, -1.0, 1.2), 110.0, 4.0, 5400, 95),
        ("Ext_Rim",       (-1.5, -4.5, 4.5), (0.0, 0.0, 1.2), 260.0, 3.0, 7400, 70),
    ]:
        ld = bpy.data.lights.new(nm, type="AREA")
        ld.energy = en
        ld.size = sz
        ld.spread = math.radians(spr)
        ld.use_temperature = True
        ld.temperature = temp
        lo = bpy.data.objects.new(nm, ld)
        col.objects.link(lo)
        lo.location = loc
        lo.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()

    return {"col": col, "letter": letter_root}


def main():
    preview_only = "--preview" in sys.argv
    bcl.clear_scene()
    scene = bpy.context.scene
    res = (1080, 1920) if preview_only else (720, 1280)
    sc.configure_stylized_eevee(scene, res_x=res[0], res_y=res[1], samples=(16 if preview_only else 12), raytracing=True, fast_gi=True, motion_blur=False, exposure=-0.20)

    beats_data = sc.load_beats()
    props = build_exterior_set(scene)

    cast_col = bpy.data.collections.new("Ext_Cast")
    scene.collection.children.link(cast_col)
    alex = cf.create_character("alex", "Alex", cast_col)

    cam_d = bpy.data.cameras.new("Cam_Ext")
    cam = bpy.data.objects.new("Cam_Ext", cam_d)
    scene.collection.objects.link(cam)
    scene.camera = cam

    bcl.setup_cinema_compositor(
        scene, glare_threshold=1.65, glare_strength=0.10, dispersion=0.0008,
        lift_rgb=(0.995, 0.995, 1.005), gamma_rgb=(1.0, 1.0, 1.0), gain_rgb=(1.01, 1.01, 0.99),
        vignette=0.10,
    )

    ext_beats = ["b10_bun_town", "b35_no_job", "b36_letter", "b37_almost"]
    preview_keep = {"b10_bun_town", "b37_almost"}

    for bid in ext_beats:
        f0, f1 = sc.beat_frame_range(beats_data, bid)
        show_letter = bid in ("b35_no_job", "b36_letter", "b37_almost")
        sc.set_hidden_tree(props["letter"], not show_letter)

        frames_to_render = [(f0 + f1) // 2] if preview_only else list(range(f0, f1 + 1))
        for f in frames_to_render:
            if preview_only and bid not in preview_keep:
                continue
            u = (f - f0) / max(1, (f1 - f0))
            t = f / 30.0

            if bid == "b10_bun_town":
                cf.set_char_transform(alex, 0.78, -0.75, 0.0, -14.0)
                cf.set_face_with_blink(alex, "alex_determined", f, seed=21)
                cf.pose_char(
                    alex,
                    pelvis_z=0.015 * math.sin(t * 5.0),
                    head_rot=(-4, 0, 8),
                    arm_l=(8, 0, -5),
                    forearm_l=(8, 0, 0),
                    arm_r=(75, 0, 22),
                    forearm_r=(18, 0, 0),
                )
                sc.set_camera_look(cam, (0.0, 4.9 - 0.55 * u, 1.55), (-0.12, -1.8, 2.38), lens=25.0, fstop=4.0)

            elif bid == "b35_no_job":
                cf.set_char_transform(alex, 0.0, -0.65, 0.0, 0.0)
                cf.set_face_with_blink(alex, "alex_deadpan", f, seed=22)
                cf.pose_char(
                    alex,
                    head_rot=(4, 0, 0),
                    arm_l=(64, -10, -6),
                    forearm_l=(24, 0, 0),
                    arm_r=(4, 0, 5),
                    forearm_r=(6, 0, 0),
                )
                props["letter"].location = (0.36, -0.02, 1.05)
                props["letter"].scale = (1.0, 1.0, 1.0)
                sc.set_camera_look(cam, (0.08, 2.35 - 0.16 * u, 1.15), (0.08, -0.65, 1.05), lens=36.0, fstop=3.2)

            elif bid == "b36_letter":
                cf.set_char_transform(alex, 0.0, -0.65, 0.0, 0.0)
                cf.set_face(alex, "alex_deadpan.png")
                cf.pose_char(alex, arm_l=(68, -10, -6), forearm_l=(24, 0, 0), arm_r=(4, 0, 5), forearm_r=(6, 0, 0))
                props["letter"].location = (0.34, 0.02, 1.10)
                props["letter"].scale = (1.15, 1.15, 1.15)
                sc.set_camera_look(cam, (0.34, 1.12 - 0.16 * u, 1.10), (0.34, 0.02, 1.10), lens=48.0, fstop=3.2)

            elif bid == "b37_almost":
                cf.set_char_transform(alex, 0.0, -0.65, 0.0, 0.0)
                cf.set_face_with_blink(alex, "alex_almost_wobbly", f, seed=23)
                cf.pose_char(alex, head_rot=(4 + 2 * math.sin(t * 2.5), 0, 0), arm_l=(64, -10, -6), forearm_l=(24, 0, 0), arm_r=(4, 0, 5), forearm_r=(6, 0, 0))
                props["letter"].location = (0.33, -0.02, 1.04)
                props["letter"].scale = (0.86, 0.86, 0.86)
                sc.set_camera_look(cam, (0.04, 2.15 - 0.26 * u, 1.28), (0.04, -0.65, 1.15), lens=40.0, fstop=2.8)

            if preview_only:
                sc.render_frame(scene, f, preview_tag=f"ext_{bid}")
                break
            else:
                sc.render_frame(scene, f)


if __name__ == "__main__":
    main()
