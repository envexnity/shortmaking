"""
scene_exterior.py — Set 3: Bun Town Restaurant Exterior (Daytime) + Rejection Letter Close-Up.
Renders beats: b10_bun_town, b35_no_job, b36_letter, b37_almost.
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


def build_exterior_set(scene):
    col = bpy.data.collections.new("Set_BunTownExt")
    scene.collection.children.link(col)
    props_dir = PROJ_DIR / "props"

    def box(name, loc, scale, hex_col, rough=0.45):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
        o = sc._link_only(bpy.context.active_object, col)
        o.name = name
        o.scale = scale
        o.data.materials.append(sc.make_mat(f"Mat_E_{name[:10]}_{hex_col}", hex_col, rough=rough))
        return o

    # Street, crosswalk, and clean tiled sidewalk
    box("Road",     (0,  4.0, -0.25), (50, 10, 0.5), "#334155", rough=0.72)
    box("Sidewalk", (0, -2.2, -0.15), (50,  4.5, 0.5), "#E2E8F0", rough=0.60)
    for ix in range(-14, 15, 3):
        box(f"Cross_{ix}", (ix, 2.2, 0.02), (1.3, 3.2, 0.04), "#F8FAFC", rough=0.6)

    # Iconic white-and-teal BUN TOWN building (-Y = behind Alex)
    box("BT_MainWall",  (0, -10.0, 5.2), (18.0, 10.0, 10.4), "#F8FAFC", rough=0.42)
    box("BT_TealStripe",(0,  -4.95, 7.6), (18.2, 0.35, 1.2),  "#0D9488", rough=0.35)
    box("BT_RedTrim",   (0,  -4.92, 8.3), (18.2, 0.40, 0.35), "#EF4444", rough=0.35)
    box("BT_Roof",      (0, -10.0, 10.7), (19.0, 11.0, 0.7), "#0F766E", rough=0.40)

    # Glass storefront windows & doors
    for wx in (-5.5, 0.0, 5.5):
        box(f"Glass_{wx}", (wx, -4.94, 3.2), (4.2, 0.16, 4.6), "#BAE6FD", rough=0.12)
        box(f"Frame_{wx}", (wx, -4.90, 5.55), (4.5, 0.25, 0.25), "#0D9488", rough=0.35)

    # Giant BUN TOWN Roof Marquee Sign (clear in front of roof overhang, right-reading facing +Y!)
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0.0, -4.32, 10.45), rotation=(math.radians(90), 0, math.radians(180)))
    sign = sc._link_only(bpy.context.active_object, col)
    sign.name = "Sign_BunTown"
    sign.scale = (9.6, 2.56, 1.0)
    sign.data.materials.append(sc.make_image_mat("Mat_SignBunTown", props_dir / "sign_buntown.png", rough=0.35, emit=0.15))

    # Giant 3D Burger Mascot perched on top of the BUN TOWN roof!
    sc.build_burger("RoofBurger", (0.0, -5.0, 11.75), col, scale=3.4)

    # "NOW HIRING: BURGER WRAPPER" sign outside left of Alex (upright, clean backing behind it!)
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(2.4, -1.96, 2.05), rotation=(math.radians(90), 0, math.radians(180)))
    hire = sc._link_only(bpy.context.active_object, col)
    hire.name = "Sign_NowHiring"
    hire.scale = (2.1, 2.6, 1.0)
    hire.data.materials.append(sc.make_image_mat("Mat_SignHiring", props_dir / "sign_now_hiring.png", rough=0.40, emit=0.05))
    # Backing board cleanly behind the front face
    box("HireBack", (2.4, -2.14, 2.05), (2.2, 0.16, 2.7), "#0F766E", rough=0.45)

    # Potted plants flanking entrance
    for px in (-4.4, 4.4):
        bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.65, depth=1.1, location=(px, -3.5, 0.55))
        pot = sc._link_only(bpy.context.active_object, col)
        pot.data.materials.append(sc.make_mat("Mat_Pot", "#C2410C", rough=0.6))
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=10, radius=0.95, location=(px, -3.5, 1.65))
        bush = sc._link_only(bpy.context.active_object, col)
        bush.data.materials.append(sc.make_mat("Mat_Bush", "#22C55E", rough=0.6))

    # Official Bun Town Rejection Letter ("Thank you for wrapping my tie.") — right-reading facing +Y!
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(-1.45, 0.95, 2.95), rotation=(math.radians(90), 0, math.radians(180)))
    letter = sc._link_only(bpy.context.active_object, col)
    letter.name = "Prop_RejectionLetter"
    letter.scale = (1.65, 2.08, 1.0)
    letter.data.materials.append(sc.make_image_mat("Mat_LetterTie", props_dir / "letter_tie.png", rough=0.45, emit=0.10))

    # Bright Sunny Sky & Warm Sun Light
    sc.setup_bright_sky_world(scene, is_night=False)
    sun_d = bpy.data.lights.new("Sun_Ext", type="SUN")
    sun_d.energy = 3.4
    sun = bpy.data.objects.new("Sun_Ext", sun_d)
    col.objects.link(sun)
    sun.rotation_euler = (math.radians(45), math.radians(-18), math.radians(22))

    # Soft front fill so Alex's face & letter read super brightly
    fill_d = bpy.data.lights.new("Fill_Ext", type="AREA")
    fill_d.energy = 600
    fill_d.size = 6.0
    fill = bpy.data.objects.new("Fill_Ext", fill_d)
    col.objects.link(fill)
    fill.location = (0, 9.5, 5.5)
    fill.rotation_euler = (Vector((0, -1, 2.8)) - fill.location).to_track_quat("-Z", "Y").to_euler()

    return {"col": col, "letter": letter}


def main():
    preview_only = "--preview" in sys.argv
    bcl.clear_scene()
    scene = bpy.context.scene
    sc.configure_fast_eevee(scene, res_x=720, res_y=1280, samples=10, raytracing=False)

    beats_data = sc.load_beats()
    props = build_exterior_set(scene)

    # Append our protagonist Alex (with Pal Hair + Red Roblox Cap!)
    alex = sc.append_character("01_Alex_Protagonist", "Alex", enable_extra_acc=["red_roblox_cap"])
    sc.set_char_transform(alex, -1.2, -1.2, 0.0, 0.0)

    cam_d = bpy.data.cameras.new("Cam_Ext")
    cam = bpy.data.objects.new("Cam_Ext", cam_d)
    scene.collection.objects.link(cam)
    scene.camera = cam

    bcl.setup_cinema_compositor(
        scene, glare_threshold=1.6, glare_strength=0.12, dispersion=0.0008,
        lift_rgb=(0.995, 0.995, 1.0), gamma_rgb=(1.0, 1.0, 1.0), gain_rgb=(1.02, 1.02, 1.0),
        vignette=0.10,
    )

    ext_beats = ["b10_bun_town", "b35_no_job", "b36_letter", "b37_almost"]

    for bid in ext_beats:
        f0, f1 = sc.beat_frame_range(beats_data, bid)
        show_letter = bid in ("b35_no_job", "b36_letter", "b37_almost")
        props["letter"].hide_viewport = not show_letter
        props["letter"].hide_render = not show_letter

        frames_to_render = [(f0 + f1) // 2] if preview_only else list(range(f0, f1 + 1))
        for f in frames_to_render:
            u = (f - f0) / max(1, (f1 - f0))
            t = f / 30.0

            if bid == "b10_bun_town":
                # Alex standing proudly outside BUN TOWN pointing toward NOW HIRING!
                sc.set_char_transform(alex, -1.5, -1.0, 0.0, 10.0)
                sc.swap_expression(alex, "alex_determined_atlas.png")
                sc.set_char_pose(
                    alex,
                    torso_loc=(0, 0, 0.04 * math.sin(t * 5)),
                    head_rot=(-4, 0, -8),
                    larm_rot=(-75, -20, 28),
                    rarm_rot=(12, 8, -10),
                )
                sc.set_camera_look(cam, (0.2, 10.5 - 1.2 * u, 3.8), (0.3, -3.5, 4.4), lens=28.0)

            elif bid == "b35_no_job":
                # Alex holding the rejection letter looking totally defeated
                sc.set_char_transform(alex, 0.0, -0.5, 0.0, 0.0)
                sc.swap_expression(alex, "alex_deadpan_atlas.png")
                sc.set_char_pose(
                    alex,
                    head_rot=(6, 0, 0),
                    larm_rot=(-75, 8, -12),
                    rarm_rot=(8, 4, -6),
                )
                props["letter"].location = (-1.35, 0.55, 2.75)
                props["letter"].scale = (1.35, 1.70, 1.0)
                sc.set_camera_look(cam, (0.0, 8.2 - 0.8 * u, 3.2), (-0.2, -0.3, 3.0), lens=36.0)

            elif bid == "b36_letter":
                # Crisp close-up zoom onto "Thank you for wrapping my tie."!
                sc.set_char_transform(alex, 0.0, -0.5, 0.0, 0.0)
                props["letter"].location = (-1.35, 0.85, 2.90)
                props["letter"].scale = (1.65, 2.08, 1.0)
                sc.set_camera_look(cam, (-1.35, 4.45 - 0.45 * u, 2.90), (-1.35, 0.85, 2.90), lens=44.0)

            elif bid == "b37_almost":
                # Alex trying to smile through the pain ("Almost. Almost.") — rapid face twitch!
                sc.set_char_transform(alex, 0.0, -0.5, 0.0, 0.0)
                expr = "alex_smug_atlas.png" if (0.35 <= u <= 0.62) else "alex_sad_almost_atlas.png"
                sc.swap_expression(alex, expr)
                sc.set_char_pose(
                    alex,
                    head_rot=(4 * math.sin(u * 12), 0, 3 * math.sin(u * 16)),
                    larm_rot=(-70, 8, -10),
                    rarm_rot=(6, 4, -6),
                )
                props["letter"].location = (-1.35, 0.55, 2.65)
                props["letter"].scale = (1.28, 1.62, 1.0)
                sc.set_camera_look(cam, (0.0, 7.6 - 0.6 * u, 3.35), (-0.1, -0.4, 3.35), lens=40.0)

            bpy.context.view_layer.update()
            sc.render_frame(scene, f, preview_tag=f"ext_{bid}" if preview_only else None)

    print("scene_exterior.py COMPLETE!")


if __name__ == "__main__":
    main()
