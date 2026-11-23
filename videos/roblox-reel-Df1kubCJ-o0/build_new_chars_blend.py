"""
build_new_chars_blend.py
Builds 09_BunTown_Manager.blend and 10_Town_Mayor.blend in assets/roblox-r6-characters/characters/
using our verified Aeresei R6 IK+FK Blender Rig V2.22 + Blender 5.3 Cinema PBR!
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

SHORTMAKING_ROOT = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking")
CAST_ROOT = SHORTMAKING_ROOT / "assets" / "roblox-r6-characters"
PROJ_DIR = SHORTMAKING_ROOT / "videos" / "roblox-reel-Df1kubCJ-o0"
EXPR_DIR = PROJ_DIR / "expressions"

sys.path.insert(0, str(SHORTMAKING_ROOT / "90 Templates & Starter Kits" / "blender-cinema-kit"))
sys.path.insert(0, str(CAST_ROOT / "scripts"))
import blender_cinema_lib as bcl
import build_characters as bc


def lock_to_head(obj, active_parts):
    internal_arm = bpy.data.objects.get("InternalArmature")
    ref_head = active_parts.get("Head")
    if internal_arm and ref_head:
        c = obj.constraints.new("CHILD_OF")
        c.target = internal_arm
        c.subtarget = "Head"
        for rc in ref_head.constraints:
            if rc.type == "CHILD_OF" and rc.target == internal_arm and rc.subtarget == "Head":
                c.inverse_matrix = rc.inverse_matrix.copy()
                break


def add_mayor_tophat(col, active_parts):
    """Build a crisp 3D Mayor Black Top Hat with Gold Band + mini Party Hat on top."""
    # Brim
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.92, depth=0.10, location=(0.0, 0.0, 5.10))
    brim = bpy.context.active_object
    brim.name = "Acc_MayorTopHat_Brim"
    # Crown
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.62, depth=0.95, location=(0.0, 0.0, 5.58))
    crown = bpy.context.active_object
    crown.name = "Acc_MayorTopHat_Crown"
    # Gold band
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.645, depth=0.16, location=(0.0, 0.0, 5.24))
    band = bpy.context.active_object
    band.name = "Acc_MayorTopHat_Band"
    # Gray hair puffs on sides of head
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.34, location=(0.56, -0.05, 4.92))
    hair_r = bpy.context.active_object
    hair_r.name = "Acc_MayorHair_R"
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.34, location=(-0.56, -0.05, 4.92))
    hair_l = bpy.context.active_object
    hair_l.name = "Acc_MayorHair_L"

    mat_hat = bcl.make_pbr_material("Mat_MayorTopHat", "#14161D", roughness_min=0.32, roughness_max=0.44, coat_weight=0.18)
    mat_gold = bcl.make_pbr_material("Mat_MayorBand", "#EAB308", roughness_min=0.20, roughness_max=0.30, metallic=0.75, coat_weight=0.35)
    mat_gray = bcl.make_pbr_material("Mat_MayorHair", "#9CA3AF", roughness_min=0.45, roughness_max=0.58)

    for o, m in [(brim, mat_hat), (crown, mat_hat), (band, mat_gold), (hair_r, mat_gray), (hair_l, mat_gray)]:
        o.data.materials.append(m)
        for c in list(o.users_collection):
            c.objects.unlink(o)
        col.objects.link(o)
        lock_to_head(o, active_parts)


def build_extra(cid: str, atlas_path: Path, accessories: list, is_mayor: bool = False):
    bpy.ops.wm.open_mainfile(filepath=str(bc.SOURCE_RIG))
    bc.clean_invalid_drivers()
    active_parts = bc.configure_body_type(feminine=False)
    body_mat = bc.build_body_material(cid, str(atlas_path))
    for pobj in active_parts.values():
        if pobj.data.materials:
            pobj.data.materials[0] = body_mat
        else:
            pobj.data.materials.append(body_mat)

    rig_col = bpy.data.collections.get("Rig1") or bpy.context.scene.collection
    rig_col.name = cid
    acc_col = bpy.data.collections.new(f"{cid}_Accessories")
    rig_col.children.link(acc_col)

    for acc_key in accessories:
        bc.attach_marketplace_accessory(cid, acc_key, active_parts, acc_col, hidden=False)

    if is_mayor:
        add_mayor_tophat(acc_col, active_parts)

    for o in bpy.data.objects:
        if o.name.startswith("_Shape_") or o.name == "POVCamera":
            o.hide_render = True

    bpy.ops.file.pack_all()
    out_blend = bc.CHARS_DIR / f"{cid}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(out_blend))
    print(f"[SAVED NEW RIGGED CHAR] {out_blend.name}")


def main():
    build_extra("09_BunTown_Manager", EXPR_DIR / "manager_happy_atlas.png", ["brown_charmer_hair"], is_mayor=False)
    build_extra("10_Town_Mayor", EXPR_DIR / "mayor_happy_atlas.png", [], is_mayor=True)


if __name__ == "__main__":
    main()
