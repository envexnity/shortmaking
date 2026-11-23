"""
build_master_lineup.py — Assembles all 8 rigged Roblox R6 characters into one master
Blender 5.3.0 showcase & staging file (Roblox_R6_Story_Cast.blend), renders a 2560x1080
hero group poster (renders/cast_lineup_all8.png), and builds a labeled 4x2 contact sheet
(renders/cast_contact_sheet.png).

Run via:
  "C:\Program Files\Blender Foundation\Blender 5.3\blender.exe" --background --disable-autoexec --python build_master_lineup.py
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

SHORTMAKING_ROOT = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking")
sys.path.insert(0, str(SHORTMAKING_ROOT / "90 Templates & Starter Kits" / "blender-cinema-kit"))
sys.path.insert(0, str(SHORTMAKING_ROOT / "assets" / "roblox-r6-characters" / "scripts"))
import blender_cinema_lib as bcl
from build_characters import apply_personality_pose

ROOT = SHORTMAKING_ROOT / "assets" / "roblox-r6-characters"
CHAR_MANIFEST = json.loads((ROOT / "characters_manifest.json").read_text(encoding="utf-8"))
CHARS_DIR = ROOT / "characters"
RENDERS_DIR = ROOT / "renders"

# Curved hero lineup positions: (world_x, world_y, world_z, yaw_deg_around_world_Z)
# Camera sits at +Y looking toward -Y, so +X is viewer's LEFT and -X is viewer's RIGHT.
# Ordered naturally left-to-right: 01 Alex -> 02 Noob -> 03 Rich Kid -> 04 Maya -> 05 Dad -> 06 Hacker -> 07 Admin -> 08 Chloe
LINEUP_SLOTS = [
    ( 14.5, -1.6, 0.0,  18.0),  # 01 Alex (Hero)
    ( 10.4, -0.4, 0.0,  12.0),  # 02 Noob
    (  6.2,  0.3, 0.0,   7.0),  # 03 Rich Kid (Dominus)
    (  2.1,  0.7, 0.0,   3.0),  # 04 Maya
    ( -2.1,  0.7, 0.0,  -3.0),  # 05 Dad / Principal
    ( -6.2,  0.3, 0.0,  -7.0),  # 06 Hacker (Glitch)
    (-10.4, -0.4, 0.0, -12.0),  # 07 Admin (Boss)
    (-14.5, -1.6, 0.0, -18.0),  # 08 Chloe (Rival)
]


def place_rig_master_control(arm_obj, world_pos: Vector, yaw_deg: float):
    """Exact world-space placement & world-Z yaw using MasterControl's rest basis."""
    pb = arm_obj.pose.bones["MasterControl"]
    rest_3x3 = arm_obj.data.bones["MasterControl"].matrix_local.to_3x3()
    inv_3x3 = rest_3x3.inverted()

    pb.location = inv_3x3 @ world_pos
    pb.rotation_mode = "XYZ"
    world_rot = Matrix.Rotation(math.radians(yaw_deg), 3, "Z")
    local_rot = inv_3x3 @ world_rot @ rest_3x3
    pb.rotation_euler = local_rot.to_euler("XYZ")


def build_roblox_stud_stage(scene):
    stage_col = bpy.data.collections.new("Stage_Studio")
    scene.collection.children.link(stage_col)

    # Dark studio glossy floor
    bpy.ops.mesh.primitive_plane_add(size=120.0, location=(0, 0, -0.30))
    floor = bpy.context.active_object
    floor.name = "Stage_Floor"
    for c in list(floor.users_collection):
        c.objects.unlink(floor)
    stage_col.objects.link(floor)
    floor.data.materials.append(
        bcl.make_pbr_material("Mat_StageFloor", "#0C1222", roughness_min=0.25, roughness_max=0.38, metallic=0.10, coat_weight=0.35, bump_strength=0.015)
    )

    # Curved Roblox-themed platform deck (0.30 studs thick, top at z=0.0)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -0.4, -0.15))
    deck = bpy.context.active_object
    deck.name = "Stage_RobloxDeck"
    deck.scale = (36.0, 9.0, 0.30)
    bpy.ops.object.transform_apply(scale=True)
    for c in list(deck.users_collection):
        c.objects.unlink(deck)
    stage_col.objects.link(deck)
    bcl.add_cinema_bevel(deck, width=0.06, segments=2)
    deck.data.materials.append(
        bcl.make_pbr_material("Mat_StageDeck", "#172033", roughness_min=0.28, roughness_max=0.40, metallic=0.12, coat_weight=0.30, bump_strength=0.015)
    )

    # Raised Roblox Studs along the front edge of the stage deck (iconic Roblox look!)
    stud_mat = bcl.make_pbr_material("Mat_StageStud", "#24324D", roughness_min=0.22, roughness_max=0.34, metallic=0.15, coat_weight=0.40)
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.30, depth=0.12, location=(0, 0, 0))
    stud_proto = bpy.context.active_object
    stud_mesh = stud_proto.data
    stud_mesh.materials.append(stud_mat)
    bpy.data.objects.remove(stud_proto, do_unlink=True)

    for ix in range(-16, 17, 2):
        for iy in (3.1, -3.9):
            so = bpy.data.objects.new(f"Stud_{ix}_{iy:.0f}", stud_mesh)
            so.location = (float(ix), iy, 0.06)
            stage_col.objects.link(so)

    # Neon cyan front trim bar + gold rear trim bar
    for name, y_pos, col_hex in [
        ("Stage_FrontNeon", 4.12, "#38BDF8"),
        ("Stage_RearNeon", -4.92, "#A855F7"),
    ]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, y_pos, -0.04))
        bar = bpy.context.active_object
        bar.name = name
        bar.scale = (36.1, 0.12, 0.08)
        bpy.ops.object.transform_apply(scale=True)
        for c in list(bar.users_collection):
            c.objects.unlink(bar)
        stage_col.objects.link(bar)
        bar.data.materials.append(
            bcl.make_pbr_material(f"Mat_{name}", col_hex, roughness_min=0.15, roughness_max=0.2, emission_hex=col_hex, emission_strength=4.5)
        )

    # Backdrop curved wall behind cast
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=42.0, depth=34.0, location=(0.0, 2.0, 14.0))
    cyc = bpy.context.active_object
    cyc.name = "Stage_Backdrop"
    for c in list(cyc.users_collection):
        c.objects.unlink(cyc)
    stage_col.objects.link(cyc)
    cyc.data.materials.append(
        bcl.make_pbr_material("Mat_StageBackdrop", "#0A1020", roughness_min=0.85, roughness_max=0.95, bump_strength=0.0)
    )

    # Kelvin 3-Point + Wide Studio Rim Lighting across all 8 characters
    def add_area(name, loc, target, energy, sx, sy, kelvin=None, color_hex=None, spread_deg=65.0):
        ld = bpy.data.lights.new(name, type="AREA")
        ld.shape = "RECTANGLE"
        ld.size = sx
        ld.size_y = sy
        ld.energy = energy
        ld.spread = math.radians(spread_deg)
        if color_hex:
            ld.color = bcl.hex_to_linear(color_hex)[:3]
        elif kelvin:
            ld.use_temperature = True
            ld.temperature = kelvin
        lo = bpy.data.objects.new(name, ld)
        stage_col.objects.link(lo)
        lo.location = loc
        lo.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        return lo

    # Wide soft warm-daylight key across entire 8-character stage
    add_area("Key_Left",   (-10.0, 14.0, 11.5), (-7.0, 0.0, 2.8), energy=2600.0, sx=14.0, sy=5.0, kelvin=5400.0, spread_deg=68.0)
    add_area("Key_Right",  ( 10.0, 14.0, 11.5), ( 7.0, 0.0, 2.8), energy=2600.0, sx=14.0, sy=5.0, kelvin=5400.0, spread_deg=68.0)
    # Soft front cool fill
    add_area("Fill_Front", (  0.0, 18.0,  6.0), ( 0.0, 0.0, 2.5), energy=1200.0, sx=24.0, sy=6.0, kelvin=7000.0, spread_deg=90.0)
    # Dramatic colored rim backlights separating every character silhouette!
    add_area("Rim_Cyan",   (-12.0, -9.5,  8.5), (-8.0, 0.0, 3.5), energy=3200.0, sx=12.0, sy=3.5, color_hex="#38BDF8", spread_deg=55.0)
    add_area("Rim_Gold",   (  0.0, -9.5,  9.0), ( 0.0, 0.0, 3.5), energy=2800.0, sx=12.0, sy=3.5, color_hex="#FACC15", spread_deg=55.0)
    add_area("Rim_Violet", ( 12.0, -9.5,  8.5), ( 8.0, 0.0, 3.5), energy=3200.0, sx=12.0, sy=3.5, color_hex="#C084FC", spread_deg=55.0)

    # Hero Wide Lineup Camera (frames all 8 characters left-to-right with clean headroom)
    cam_d = bpy.data.cameras.new("Cam_CastLineup")
    cam_d.lens = 36.0
    cam_o = bpy.data.objects.new("Cam_CastLineup", cam_d)
    stage_col.objects.link(cam_o)
    cam_o.location = (0.0, 35.5, 4.8)
    cam_o.rotation_euler = (Vector((0.0, 0.0, 2.85)) - cam_o.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam_o


def append_all_characters(scene):
    """Append all 8 self-contained rigged R6 character collections and pose them on stage."""
    cast_root = bpy.data.collections.new("Roblox_R6_Cast")
    scene.collection.children.link(cast_root)

    for idx, spec in enumerate(CHAR_MANIFEST):
        cid = spec["id"]
        blend_path = CHARS_DIR / f"{cid}.blend"

        # Append the character's top-level collection (e.g. '01_Alex_Protagonist')
        before_cols = set(bpy.data.collections)
        before_objs = set(bpy.data.objects)
        with bpy.data.libraries.load(str(blend_path), link=False) as (data_from, data_to):
            data_to.collections = [cid]

        new_cols = [c for c in bpy.data.collections if c not in before_cols]
        new_objs = [o for o in bpy.data.objects if o not in before_objs]

        # Link top-level appended collection into cast_root
        top_col = bpy.data.collections.get(cid)
        if top_col is None and new_cols:
            top_col = new_cols[0]
        if top_col:
            cast_root.children.link(top_col)

        # Find this character's __PrimaryArmature among newly appended objects
        primary_arm = None
        for o in new_objs:
            if o.type == "ARMATURE" and o.name.startswith("__PrimaryArmature"):
                primary_arm = o
                o.name = f"{cid}_Rig"
            elif o.type == "ARMATURE" and o.name.startswith("InternalArmature"):
                o.name = f"{cid}_InternalArmature"

        if primary_arm:
            # Clear any leftover default rest action from source rig so stage placement & poses persist!
            if primary_arm.animation_data:
                primary_arm.animation_data.action = None
            apply_personality_pose(primary_arm, spec["pose"])
            wx, wy, wz, yaw = LINEUP_SLOTS[idx]
            place_rig_master_control(primary_arm, Vector((wx, wy, wz)), yaw)
            print(f"[PLACED] {cid:22s} at ({wx:+.1f}, {wy:+.1f}, {wz:+.1f}) yaw={yaw:+.0f} deg")
        else:
            print(f"[WARN] Could not locate __PrimaryArmature for {cid}")

    bpy.context.view_layer.update()


def build_contact_sheet():
    """Assemble a crisp 4x2 labeled showcase sheet of all 8 character renders using Pillow."""
    from PIL import Image, ImageDraw, ImageFont

    cols, rows = 4, 2
    tile_w, tile_h = 540, 720
    pad = 24
    header_h = 96
    label_h = 74

    sheet_w = pad + cols * (tile_w + pad)
    sheet_h = header_h + pad + rows * (tile_h + label_h + pad)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 15, 28))
    draw = ImageDraw.Draw(sheet)

    def load_font(size, bold=True):
        candidates = (
            ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"]
            if bold else
            ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"]
        )
        for p in candidates:
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
        return ImageFont.load_default()

    f_title = load_font(40, bold=True)
    f_sub = load_font(20, bold=False)
    f_name = load_font(24, bold=True)
    f_role = load_font(16, bold=False)

    draw.text((pad, 20), "ROBLOX R6 STORY CAST — 8 RIGGED CHARACTERS (AERESEI IK+FK V2.22 + MARKETPLACE)", fill=(240, 248, 255), font=f_title)
    draw.text((pad, 68), "Blender 5.3.0  •  50 Real Roblox Marketplace Assets  •  Individual .blend Files + Master Cast Scene Ready to Animate", fill=(148, 163, 184), font=f_sub)

    for idx, spec in enumerate(CHAR_MANIFEST):
        r, c = divmod(idx, cols)
        x = pad + c * (tile_w + pad)
        y = header_h + pad + r * (tile_h + label_h + pad)

        img_p = RENDERS_DIR / f"{spec['id']}.png"
        if img_p.exists():
            im = Image.open(img_p).convert("RGB").resize((tile_w, tile_h), Image.Resampling.LANCZOS)
            sheet.paste(im, (x, y))

        # Card footer bar
        draw.rectangle([x, y + tile_h, x + tile_w, y + tile_h + label_h], fill=(20, 29, 48))
        draw.rectangle([x, y, x + tile_w, y + tile_h + label_h], outline=(56, 75, 110), width=2)

        body_tag = "FBlocky" if spec["feminine"] else "MBlocky"
        draw.text((x + 14, y + tile_h + 10), f"{idx+1}. {spec['display_name']}", fill=(255, 255, 255), font=f_name)
        draw.text((x + 14, y + tile_h + 42), f"{spec['role']}  [{body_tag}]", fill=(148, 197, 255), font=f_role)

    out_sheet = RENDERS_DIR / "cast_contact_sheet.png"
    sheet.save(out_sheet)
    print(f"[SAVED] Contact sheet -> {out_sheet}")


def main():
    bcl.clear_scene()
    scene = bpy.context.scene
    bcl.configure_eevee_cinema(
        scene, res_x=2560, res_y=1080, fps=30, samples=48,
        raytracing=True, fast_gi=True, view_transform="AgX", look="AgX - Punchy",
        motion_blur=False,
    )
    bcl.setup_dark_studio_world(scene, hex_col="#090F1E", strength=0.35)

    build_roblox_stud_stage(scene)
    append_all_characters(scene)

    bcl.setup_cinema_compositor(
        scene, glare_threshold=1.35, glare_strength=0.22, dispersion=0.0018,
        lift_rgb=(0.985, 0.99, 1.01), gamma_rgb=(1.0, 1.0, 1.0), gain_rgb=(1.03, 1.02, 1.0),
        vignette=0.16,
    )

    bpy.ops.file.pack_all()
    master_blend = ROOT / "Roblox_R6_Story_Cast.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(master_blend))
    print(f"[SAVED] Master 8-character rigged Blender scene -> {master_blend}")

    poster_path = RENDERS_DIR / "cast_lineup_all8.png"
    scene.render.filepath = str(poster_path)
    scene.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    print(f"[RENDERED] Master cast lineup poster -> {poster_path}")


if __name__ == "__main__":
    main()
