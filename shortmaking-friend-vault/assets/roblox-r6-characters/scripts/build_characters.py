"""
build_characters.py — Blender 5.3.0 Roblox R6 Story Cast Factory.
Builds 8 self-contained, rigged, packed Roblox R6 character .blend files from:
  - Aeresei's verified R6 IK + FK Blender Rig V2.22 (source_rig/Blender_R6_Rig_v222.blend)
  - 48 real Roblox Marketplace assets (3D .obj accessories, textures, shirts, pants, faces)
  - 2048x1024 HD baked character texture atlases (textures/<id>_atlas.png)
  - Blender 5.3 Cinema PBR shaders, Kelvin 3-point + rim studio lighting, AgX - Punchy

Run via:
  "C:\Program Files\Blender Foundation\Blender 5.3\blender.exe" --background --disable-autoexec --python build_characters.py
"""
import json
import math
import os
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Euler, Matrix, Vector

# Add blender-cinema-kit to path for Blender 5.3 helpers
SHORTMAKING_ROOT = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking")
sys.path.insert(0, str(SHORTMAKING_ROOT / "90 Templates & Starter Kits" / "blender-cinema-kit"))
import blender_cinema_lib as bcl

ROOT = SHORTMAKING_ROOT / "assets" / "roblox-r6-characters"
SOURCE_RIG = ROOT / "source_rig" / "Blender_R6_Rig_v222.blend"
MARKET_MANIFEST = json.loads((ROOT / "marketplace_assets" / "manifest.json").read_text(encoding="utf-8"))
CHAR_MANIFEST = json.loads((ROOT / "characters_manifest.json").read_text(encoding="utf-8"))

CHARS_DIR = ROOT / "characters"
RENDERS_DIR = ROOT / "renders"
CHARS_DIR.mkdir(parents=True, exist_ok=True)
RENDERS_DIR.mkdir(parents=True, exist_ok=True)

# Standard R6 Rig Attachment positions in Roblox coordinates (studs, origin at feet, Y-up, -Z forward)
# Verified against Blender_R6_Rig_v222.blend: Head center=(0,4.5,0) size 1.2, Torso center=(0,3.0,0) size (2,2,1)
RBX_PART_ATTACHMENTS = {
    "HatAttachment":        ("Head",  Vector((0.0, 4.5 + 0.6, 0.0))),
    "HairAttachment":       ("Head",  Vector((0.0, 4.5 + 0.6, 0.0))),
    "FaceFrontAttachment":  ("Head",  Vector((0.0, 4.5, -0.6))),
    "FaceCenterAttachment": ("Head",  Vector((0.0, 4.5, 0.0))),
    "NeckAttachment":       ("Torso", Vector((0.0, 4.0, 0.0))),
    "BodyBackAttachment":   ("Torso", Vector((0.0, 3.0, +0.5))),
    "BodyFrontAttachment":  ("Torso", Vector((0.0, 3.0, -0.5))),
    "WaistBackAttachment":  ("Torso", Vector((0.0, 2.0, +0.5))),
    "WaistFrontAttachment": ("Torso", Vector((0.0, 2.0, -0.5))),
    "WaistCenterAttachment":("Torso", Vector((0.0, 2.0, 0.0))),
}

# Material look-dev presets for Roblox accessories
ACCESSORY_PBR_PRESETS = {
    "beautiful_hair":      {"rough": 0.38, "metal": 0.0,  "coat": 0.14, "emit": 0.0},
    "roblox_girl_hair":    {"rough": 0.40, "metal": 0.0,  "coat": 0.12, "emit": 0.0},
    "pal_hair":            {"rough": 0.44, "metal": 0.0,  "coat": 0.08, "emit": 0.0},
    "blonde_spiked_hair":  {"rough": 0.42, "metal": 0.0,  "coat": 0.10, "emit": 0.0},
    "brown_charmer_hair":  {"rough": 0.42, "metal": 0.0,  "coat": 0.10, "emit": 0.0},
    "lavender_updo":       {"rough": 0.40, "metal": 0.0,  "coat": 0.12, "emit": 0.0},
    "chestnut_bun":        {"rough": 0.42, "metal": 0.0,  "coat": 0.10, "emit": 0.0},
    "shaggy":              {"rough": 0.46, "metal": 0.0,  "coat": 0.06, "emit": 0.0},
    "red_roblox_cap":      {"rough": 0.50, "metal": 0.0,  "coat": 0.08, "emit": 0.0},
    "propeller_beanie":    {"rough": 0.32, "metal": 0.10, "coat": 0.25, "emit": 0.0},
    "dominus_empyreus":    {"rough": 0.34, "metal": 0.22, "coat": 0.20, "emit": 0.0},
    "valkyrie_helm":       {"rough": 0.22, "metal": 0.65, "coat": 0.35, "emit": 0.0},
    "domino_crown":        {"rough": 0.24, "metal": 0.55, "coat": 0.30, "emit": 0.0},
    "classic_fedora":      {"rough": 0.58, "metal": 0.0,  "coat": 0.05, "emit": 0.0},
    "void_star":           {"rough": 0.20, "metal": 0.45, "coat": 0.40, "emit": 0.45},
    "nerd_glasses":        {"rough": 0.15, "metal": 0.10, "coat": 0.50, "emit": 0.0},
    "stylish_aviators":    {"rough": 0.12, "metal": 0.55, "coat": 0.60, "emit": 0.0},
    "midnight_shades":     {"rough": 0.12, "metal": 0.25, "coat": 0.65, "emit": 0.0},
    "clockwork_shades":    {"rough": 0.14, "metal": 0.65, "coat": 0.55, "emit": 0.0},
    "rose_glasses":        {"rough": 0.14, "metal": 0.30, "coat": 0.55, "emit": 0.0},
    "bandit_mask":         {"rough": 0.62, "metal": 0.0,  "coat": 0.04, "emit": 0.0},
    "swordpack":           {"rough": 0.24, "metal": 0.70, "coat": 0.30, "emit": 0.0},
}


def clean_invalid_drivers():
    """Remove Blender 4.x invalid pose.bones[...].hide drivers so Blender 5.3 loads with 0 warnings."""
    for obj in bpy.data.objects:
        if obj.animation_data and obj.animation_data.drivers:
            to_remove = []
            for fc in obj.animation_data.drivers:
                if fc.data_path.endswith(".hide"):
                    to_remove.append(fc)
            for fc in to_remove:
                obj.animation_data.drivers.remove(fc)


def configure_body_type(feminine: bool):
    """
    Keep only the active R6 Blocky body type (MBlocky or FBlocky), strip hide drivers on the
    6 active body meshes so they stay cleanly visible regardless of autoexec, and remove unused
    body-type meshes so each character .blend is lightweight and clean.
    """
    active_col_name = "FBlocky" if feminine else "MBlocky"
    unused_cols = ["F2012", "F2016", "M2012", "M2016", "MBlocky" if feminine else "FBlocky"]

    # Update Body settings empty
    if "Body" in bpy.data.objects:
        bpy.data.objects["Body"]["BodyType"] = 1
        bpy.data.objects["Body"]["Feminine"] = bool(feminine)

    # Remove unused body collections and their mesh objects
    for cname in unused_cols:
        col = bpy.data.collections.get(cname)
        if col:
            for obj in list(col.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(col)

    # Also remove empty Feminine/Masculine wrapper collections if unused
    for cname in ("Feminine", "Masculine"):
        col = bpy.data.collections.get(cname)
        if col and len(col.objects) == 0 and len(col.children) == 0:
            bpy.data.collections.remove(col)

    # Remove hide_viewport/hide_render drivers on active 6 parts and force visible
    active_col = bpy.data.collections.get(active_col_name)
    active_parts = {}
    if active_col:
        for obj in active_col.objects:
            if obj.animation_data and obj.animation_data.drivers:
                for fc in list(obj.animation_data.drivers):
                    if fc.data_path in ("hide_viewport", "hide_render"):
                        obj.animation_data.drivers.remove(fc)
            obj.hide_viewport = False
            obj.hide_render = False
            # Classify by Roblox part name
            for pname in ("Head", "Torso", "Left Arm", "Right Arm", "Left Leg", "Right Leg"):
                if obj.name.startswith(pname):
                    active_parts[pname] = obj
                    break
    return active_parts


def build_body_material(char_id: str, atlas_path: str):
    """Upgrade PrimaryMaterial to Blender 5.3 Cinema Roblox PBR (procedural roughness + coat + micro-bump)."""
    mat = bpy.data.materials.get("PrimaryMaterial")
    if mat is None:
        mat = bpy.data.materials.new(f"Mat_{char_id}_Body")
    else:
        mat.name = f"Mat_{char_id}_Body"

    if bpy.app.version < (5, 0, 0):
        mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (600, 0)

    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (260, 0)
    bsdf.inputs["IOR"].default_value = 1.48
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.45
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 0.16
    if "Coat Roughness" in bsdf.inputs:
        bsdf.inputs["Coat Roughness"].default_value = 0.18
    if "Diffuse Roughness" in bsdf.inputs:
        bsdf.inputs["Diffuse Roughness"].default_value = 0.25

    # Load crisp 2048x1024 baked atlas image and pack it
    img = bpy.data.images.load(atlas_path, check_existing=False)
    img.name = f"{char_id}_atlas.png"
    img.colorspace_settings.name = "sRGB"
    img.pack()

    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.location = (-220, 220)
    tex.image = img
    tex.interpolation = "Linear"
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])

    # Procedural roughness breakup & tactile micro-bump (Zero Plastic Viewport CGI law!)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-680, -140)

    noise_r = nt.nodes.new("ShaderNodeTexNoise")
    noise_r.location = (-440, -60)
    noise_r.inputs["Scale"].default_value = 26.0
    noise_r.inputs["Detail"].default_value = 5.0
    noise_r.inputs["Roughness"].default_value = 0.55
    nt.links.new(tc.outputs["Object"], noise_r.inputs["Vector"])

    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.location = (-180, -60)
    mr.inputs["From Min"].default_value = 0.25
    mr.inputs["From Max"].default_value = 0.75
    mr.inputs["To Min"].default_value = 0.26
    mr.inputs["To Max"].default_value = 0.40
    nt.links.new(noise_r.outputs["Fac"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], bsdf.inputs["Roughness"])

    noise_b = nt.nodes.new("ShaderNodeTexNoise")
    noise_b.location = (-440, -280)
    noise_b.inputs["Scale"].default_value = 90.0
    noise_b.inputs["Detail"].default_value = 4.0
    nt.links.new(tc.outputs["Object"], noise_b.inputs["Vector"])

    bump = nt.nodes.new("ShaderNodeBump")
    bump.location = (-40, -260)
    bump.inputs["Strength"].default_value = 0.014
    bump.inputs["Distance"].default_value = 0.004
    nt.links.new(noise_b.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    # Remove old packed R6rig1_diff.png image if unused
    old_img = bpy.data.images.get("R6rig1_diff.png")
    if old_img and old_img.users == 0:
        bpy.data.images.remove(old_img)

    return mat


def load_obj_to_blender_mesh(obj_path: str, mesh_name: str, transform_fn):
    """
    Pure-Python OBJ parser directly into bpy.data.meshes with exact vertex transform and UV mapping.
    Zero importer axis ambiguity.
    """
    verts = []
    uvs = []
    faces = []
    face_uvs = []

    with open(obj_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("v "):
                parts = line.split()
                vx, vy, vz = float(parts[1]), float(parts[2]), float(parts[3])
                p = transform_fn(Vector((vx, vy, vz)))
                verts.append((p.x, p.y, p.z))
            elif line.startswith("vt "):
                parts = line.split()
                uvs.append((float(parts[1]), float(parts[2])))
            elif line.startswith("f "):
                parts = line.split()[1:]
                f_v = []
                f_vt = []
                for tok in parts:
                    comps = tok.split("/")
                    vi = int(comps[0])
                    vi = vi - 1 if vi > 0 else len(verts) + vi
                    f_v.append(vi)
                    if len(comps) >= 2 and comps[1]:
                        ti = int(comps[1])
                        ti = ti - 1 if ti > 0 else len(uvs) + ti
                        f_vt.append(ti)
                    else:
                        f_vt.append(-1)
                if len(f_v) >= 3:
                    # Ensure valid distinct indices
                    if len(set(f_v)) == len(f_v):
                        faces.append(tuple(f_v))
                        face_uvs.append(tuple(f_vt))

    me = bpy.data.meshes.new(mesh_name)
    me.from_pydata(verts, [], faces)

    # Assign UV layer
    if uvs:
        uv_layer = me.uv_layers.new(name="UVMap")
        for poly, f_vt in zip(me.polygons, face_uvs):
            for li, ti in zip(poly.loop_indices, f_vt):
                if 0 <= ti < len(uvs):
                    uv_layer.data[li].uv = uvs[ti]

    # Merge Roblox v1.00 split-triangle duplicate vertices (preserving per-loop UVs!) for silky smooth shading
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()

    # Smooth shading with sharp-edge preservation via EdgeSplit modifier added on object
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    me.update()
    return me


def build_accessory_material(char_id: str, acc_key: str, acc_entry: dict):
    mat = bpy.data.materials.new(f"Mat_{char_id}_{acc_key}")
    if bpy.app.version < (5, 0, 0):
        mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    preset = ACCESSORY_PBR_PRESETS.get(acc_key, {"rough": 0.38, "metal": 0.05, "coat": 0.15, "emit": 0.0})

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (620, 0)

    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (280, 0)
    bsdf.inputs["Metallic"].default_value = preset["metal"]
    bsdf.inputs["Roughness"].default_value = preset["rough"]
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = preset["coat"]
    if "Coat Roughness" in bsdf.inputs:
        bsdf.inputs["Coat Roughness"].default_value = 0.16

    tex_path = acc_entry["files"].get("texture")
    vc = acc_entry["parsed"].get("vertex_color", [1.0, 1.0, 1.0])
    if tex_path and os.path.exists(tex_path):
        img = bpy.data.images.load(tex_path, check_existing=False)
        img.name = f"{char_id}_{acc_key}_tex.png"
        img.colorspace_settings.name = "sRGB"
        img.pack()
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.location = (-280, 220)
        tex.image = img

        if any(abs(c - 1.0) > 0.02 for c in vc):
            mix = nt.nodes.new("ShaderNodeMix")
            mix.data_type = "RGBA"
            mix.blend_type = "MULTIPLY"
            mix.inputs["Factor"].default_value = 1.0
            mix.inputs["B"].default_value = (vc[0], vc[1], vc[2], 1.0)
            mix.location = (20, 200)
            nt.links.new(tex.outputs["Color"], mix.inputs["A"])
            nt.links.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
        else:
            nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])

        if preset["emit"] > 0.0:
            nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
            bsdf.inputs["Emission Strength"].default_value = preset["emit"]
    else:
        bsdf.inputs["Base Color"].default_value = (vc[0], vc[1], vc[2], 1.0)

    # Subtle roughness breakup so accessories never look flat
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-560, -140)
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.location = (-340, -140)
    noise.inputs["Scale"].default_value = 24.0
    noise.inputs["Detail"].default_value = 4.0
    nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])

    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.location = (-80, -140)
    mr.inputs["From Min"].default_value = 0.2
    mr.inputs["From Max"].default_value = 0.8
    mr.inputs["To Min"].default_value = max(0.08, preset["rough"] - 0.07)
    mr.inputs["To Max"].default_value = min(0.85, preset["rough"] + 0.08)
    nt.links.new(noise.outputs["Fac"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], bsdf.inputs["Roughness"])

    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def attach_marketplace_accessory(
    char_id: str,
    acc_key: str,
    active_parts: dict,
    target_collection,
    hidden: bool = False,
):
    """
    Load a real Roblox Marketplace 3D accessory (.obj + .png), compute exact Roblox Studio
    Attachment weld transform into Blender R6 coordinates, and lock it to InternalArmature
    via CHILD_OF constraint matching Head_MBlocky / Torso_MBlocky.
    """
    entry = MARKET_MANIFEST[acc_key]
    parsed = entry["parsed"]
    obj_path = entry["files"]["obj"]

    att_name = parsed.get("attachment_name") or "HatAttachment"
    part_name, part_att_pos_rbx = RBX_PART_ATTACHMENTS.get(
        att_name, ("Head", Vector((0.0, 4.5 + 0.6, 0.0)))
    )

    # Build M_part_att in Roblox world coords
    m_part_att = Matrix.Translation(part_att_pos_rbx)

    # Build M_acc_att in Handle local coords (Roblox space)
    cf = parsed.get("attachment_cframe")
    if cf and cf.get("pos"):
        p = cf["pos"]
        r = cf.get("rot") or [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        m_acc_att = Matrix((
            (r[0][0], r[0][1], r[0][2], p[0]),
            (r[1][0], r[1][1], r[1][2], p[1]),
            (r[2][0], r[2][1], r[2][2], p[2]),
            (0.0,     0.0,     0.0,     1.0),
        ))
    else:
        ap = parsed.get("attachment_pos", [0.0, 0.0, 0.0])
        ar = parsed.get("attachment_right", [1.0, 0.0, 0.0])
        au = parsed.get("attachment_up", [0.0, 1.0, 0.0])
        af = parsed.get("attachment_forward", [0.0, 0.0, -1.0])
        # Roblox CFrame columns are (Right, Up, -Forward)
        m_acc_att = Matrix((
            (ar[0], au[0], -af[0], ap[0]),
            (ar[1], au[1], -af[1], ap[1]),
            (ar[2], au[2], -af[2], ap[2]),
            (0.0,   0.0,   0.0,    1.0),
        ))

    # SpecialMesh scale & offset
    sc = parsed.get("scale", [1.0, 1.0, 1.0])
    off = parsed.get("offset", [0.0, 0.0, 0.0])
    m_weld_rbx = m_part_att @ m_acc_att.inverted()

    # Exact Roblox -> Blender_R6_Rig_v222 rotation: (x, y, z) -> (x, -z, +y)
    m_rbx_to_bl = Matrix.Rotation(math.radians(90.0), 4, "X")

    # Fine-tuned per-accessory Z lift (studs) when needed so eyes/face read clearly
    z_lift = 0.10 if acc_key == "valkyrie_helm" else 0.0

    def xform(v: Vector) -> Vector:
        vh = Vector((v.x * sc[0] + off[0], v.y * sc[1] + off[1], v.z * sc[2] + off[2]))
        vr = m_weld_rbx @ vh
        vb = m_rbx_to_bl @ vr
        return Vector((vb.x, vb.y, vb.z + z_lift))

    me = load_obj_to_blender_mesh(obj_path, f"Mesh_{char_id}_{acc_key}", xform)
    acc_obj = bpy.data.objects.new(f"Acc_{acc_key}", me)
    target_collection.objects.link(acc_obj)

    # Crisp auto-smooth edge split (45 deg) so curved hoods/lenses/hair are smooth while hard corners stay crisp
    es = acc_obj.modifiers.new("EdgeSplit", "EDGE_SPLIT")
    es.split_angle = math.radians(45.0)
    es.use_edge_angle = True

    mat = build_accessory_material(char_id, acc_key, entry)
    acc_obj.data.materials.append(mat)

    # Lock to InternalArmature bone with the exact same CHILD_OF inverse matrix as Head/Torso!
    ref_part = active_parts.get(part_name)
    internal_arm = bpy.data.objects.get("InternalArmature")
    if internal_arm and ref_part:
        c = acc_obj.constraints.new("CHILD_OF")
        c.target = internal_arm
        c.subtarget = part_name
        # Copy exact inverse matrix from the rig's own Head/Torso part so zero drift occurs!
        for rc in ref_part.constraints:
            if rc.type == "CHILD_OF" and rc.target == internal_arm and rc.subtarget == part_name:
                c.inverse_matrix = rc.inverse_matrix.copy()
                break

    acc_obj.hide_viewport = hidden
    acc_obj.hide_render = hidden
    return acc_obj


def apply_personality_pose(arm_obj, pose_name: str):
    """
    Pose the verified Aeresei R6 IK + FK Rig (__PrimaryArmature) into expressive storytime poses!
    Note: Arms default to FK (RightArm_FK, LeftArm_FK), Legs default to IK (RightLeg-IK, LeftLeg-IK),
    Torso via LowerTorso-FK / Torso_FK, Head via Head bone.
    """
    pbs = arm_obj.pose.bones

    def set_rot(bone_name, rx, ry, rz):
        if bone_name in pbs:
            pb = pbs[bone_name]
            pb.rotation_mode = "XYZ"
            pb.rotation_euler = (math.radians(rx), math.radians(ry), math.radians(rz))

    def set_loc(bone_name, lx, ly, lz):
        if bone_name in pbs:
            pbs[bone_name].location = (lx, ly, lz)

    # Reset all pose bones first
    for pb in pbs:
        pb.location = (0.0, 0.0, 0.0)
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = (0.0, 0.0, 0.0)

    if pose_name == "hero_wave":
        # Friendly protagonist waving right hand up, subtle confident lean
        set_rot("LowerTorso-FK", 3, 0, -8)
        set_rot("Head", -5, -4, 12)
        set_rot("RightArm_FK", -135, 18, -22)
        set_rot("LeftArm_FK", 14, -8, -16)
        set_loc("RightLeg-IK", 0.12, 0.18, 0.0)
        set_loc("LeftLeg-IK", -0.10, -0.14, 0.0)

    elif pose_name == "noob_excited":
        # Classic Noob super excited mid-cheer!
        set_loc("LowerTorso-FK", 0.0, 0.0, 0.14)
        set_rot("LowerTorso-FK", -6, 0, 5)
        set_rot("Head", -10, 8, -8)
        set_rot("RightArm_FK", -148, 22, -26)
        set_rot("LeftArm_FK", -138, -24, 24)
        set_loc("RightLeg-IK", 0.18, 0.22, 0.18)
        set_loc("LeftLeg-IK", -0.18, -0.10, 0.0)

    elif pose_name == "rich_flex":
        # Rich Kid flexing with chin tilted up, one hand on hip, one forward smugly
        set_rot("LowerTorso-FK", -6, 0, 14)
        set_rot("Head", -8, -5, -16)
        set_rot("RightArm_FK", -36, -24, 28)
        set_rot("LeftArm_FK", 22, 16, 26)
        set_loc("RightLeg-IK", 0.16, 0.22, 0.0)
        set_loc("LeftLeg-IK", -0.14, -0.16, 0.0)

    elif pose_name == "maya_cheer":
        # Cheerful confident wave & friendly head tilt
        set_rot("LowerTorso-FK", 4, 0, 10)
        set_rot("Head", -4, 9, -12)
        set_rot("LeftArm_FK", -125, -20, 22)
        set_rot("RightArm_FK", 18, 12, -18)
        set_loc("LeftLeg-IK", -0.12, 0.20, 0.0)
        set_loc("RightLeg-IK", 0.10, -0.12, 0.0)

    elif pose_name == "dad_lecture":
        # Stern Dad / Principal leaning forward lecturing with raised pointing arm!
        set_rot("LowerTorso-FK", 8, 0, -10)
        set_rot("Head", 6, -3, 12)
        set_rot("RightArm_FK", -82, 8, -10)
        set_rot("LeftArm_FK", 18, -14, -22)
        set_loc("RightLeg-IK", 0.12, 0.20, 0.0)
        set_loc("LeftLeg-IK", -0.12, -0.16, 0.0)

    elif pose_name == "hacker_scheme":
        # Sneaky hunched chaos hacker scheming!
        set_loc("LowerTorso-FK", 0.0, 0.0, -0.16)
        set_rot("LowerTorso-FK", 14, 0, 12)
        set_rot("Head", -12, -6, -15)
        set_rot("RightArm_FK", -58, -28, 22)
        set_rot("LeftArm_FK", -54, 28, -22)
        set_loc("RightLeg-IK", 0.18, 0.24, 0.0)
        set_loc("LeftLeg-IK", -0.22, -0.18, 0.0)

    elif pose_name == "admin_power":
        # Commanding Admin power stance, wide feet, broad confident posture
        set_rot("LowerTorso-FK", -5, 0, -8)
        set_rot("Head", -4, 4, 10)
        set_rot("RightArm_FK", -24, 22, -26)
        set_rot("LeftArm_FK", -22, -20, 24)
        set_loc("RightLeg-IK", 0.26, 0.16, 0.0)
        set_loc("LeftLeg-IK", -0.26, -0.14, 0.0)

    elif pose_name == "chloe_sass":
        # Popular rival sassy attitude pose
        set_rot("LowerTorso-FK", -5, 0, -14)
        set_rot("Head", -4, -8, 16)
        set_rot("RightArm_FK", 22, -22, -28)
        set_rot("LeftArm_FK", -48, 24, -18)
        set_loc("RightLeg-IK", 0.16, 0.20, 0.0)
        set_loc("LeftLeg-IK", -0.10, -0.14, 0.0)

    bpy.context.view_layer.update()


def setup_portrait_studio(scene, accent_hex="#38BDF8"):
    """Set up Blender 5.3 EEVEE raytracing studio with Kelvin 3-point + rim lighting & stud pedestal."""
    bcl.configure_eevee_cinema(
        scene, res_x=900, res_y=1200, fps=30, samples=32,
        raytracing=True, fast_gi=True, view_transform="AgX", look="AgX - Punchy",
        motion_blur=False,
    )
    bcl.setup_dark_studio_world(scene, hex_col="#0B1120", strength=0.35)

    # Studio collection (removed before saving clean character .blend!)
    st_col = bpy.data.collections.new("_TempPortraitStudio")
    scene.collection.children.link(st_col)

    # Seamless dark slate studio floor + Roblox stud pedestal
    bpy.ops.mesh.primitive_plane_add(size=40.0, location=(0, 0, 0.0))
    floor = bpy.context.active_object
    floor.name = "_StudioFloor"
    for c in list(floor.users_collection):
        c.objects.unlink(floor)
    st_col.objects.link(floor)
    f_mat = bcl.make_pbr_material("_MatStudioFloor", "#131B2E", roughness_min=0.32, roughness_max=0.46, metallic=0.05, coat_weight=0.25, bump_strength=0.02)
    floor.data.materials.append(f_mat)

    # Curved cyclorama backdrop
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=14.0, depth=18.0, location=(0, 0, 8.0))
    cyc = bpy.context.active_object
    cyc.name = "_StudioCyc"
    for c in list(cyc.users_collection):
        c.objects.unlink(cyc)
    st_col.objects.link(cyc)
    cyc_mat = bcl.make_pbr_material("_MatStudioCyc", "#0D1528", roughness_min=0.82, roughness_max=0.92, bump_strength=0.0)
    cyc.data.materials.append(cyc_mat)

    # Roblox-style glowing accent baseplate disk under character
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=2.6, depth=0.14, location=(0, 0, -0.07))
    ped = bpy.context.active_object
    ped.name = "_Pedestal"
    for c in list(ped.users_collection):
        c.objects.unlink(ped)
    st_col.objects.link(ped)
    ped_mat = bcl.make_pbr_material("_MatPedestal", "#1E293B", roughness_min=0.24, roughness_max=0.36, metallic=0.15, coat_weight=0.35)
    ped.data.materials.append(ped_mat)

    # Glowing rim ring around pedestal
    bpy.ops.mesh.primitive_torus_add(major_radius=2.62, minor_radius=0.045, location=(0, 0, 0.01))
    ring = bpy.context.active_object
    ring.name = "_PedestalRing"
    for c in list(ring.users_collection):
        c.objects.unlink(ring)
    st_col.objects.link(ring)
    ring_mat = bcl.make_pbr_material("_MatRing", accent_hex, roughness_min=0.18, roughness_max=0.25, emission_hex=accent_hex, emission_strength=4.5)
    ring.data.materials.append(ring_mat)

    # Kelvin 3-Point + Rim Lighting (Character faces +Y!)
    def add_area(name, loc, target, energy, size, kelvin=None, color_hex=None, spread_deg=65.0):
        ld = bpy.data.lights.new(name, type="AREA")
        ld.energy = energy
        ld.size = size
        ld.spread = math.radians(spread_deg)
        if color_hex:
            ld.color = bcl.hex_to_linear(color_hex)[:3]
        elif kelvin:
            ld.use_temperature = True
            ld.temperature = kelvin
        lo = bpy.data.objects.new(name, ld)
        st_col.objects.link(lo)
        lo.location = loc
        direction = Vector(target) - Vector(loc)
        lo.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        return lo

    target = (0.0, 0.0, 3.0)
    # Key light front-right (+X, +Y, +Z) warm-neutral daylight
    add_area("_KeyLight",  (5.5, 6.5, 7.2),  target, energy=680.0, size=3.8, kelvin=5400.0, spread_deg=60.0)
    # Soft cool fill front-left (-X, +Y, +Z)
    add_area("_FillLight", (-6.0, 5.5, 4.5), target, energy=260.0, size=5.2, kelvin=7200.0, spread_deg=85.0)
    # Crisp colored rim backlight (-Y, +Z) separating silhouette cleanly!
    add_area("_RimLight",  (-3.5, -5.8, 6.2), (0, 0, 3.4), energy=750.0, size=2.8, color_hex=accent_hex, spread_deg=50.0)
    add_area("_RimLight2", (4.0, -5.2, 5.5),  (0, 0, 3.2), energy=420.0, size=2.6, kelvin=8200.0, spread_deg=55.0)

    # Portrait Camera (character faces +Y, so camera sits at +Y looking at -Y!)
    cam_d = bpy.data.cameras.new("_PortraitCam")
    cam_d.lens = 48.0
    cam_o = bpy.data.objects.new("_PortraitCam", cam_d)
    st_col.objects.link(cam_o)
    cam_o.location = (1.65, 9.8, 3.35)
    aim = Vector((0.0, 0.0, 2.85)) - cam_o.location
    cam_o.rotation_euler = aim.to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam_o

    # Blender 5.3 Compositor polish
    bcl.setup_cinema_compositor(
        scene, glare_threshold=1.35, glare_strength=0.25, dispersion=0.002,
        lift_rgb=(0.985, 0.99, 1.01), gamma_rgb=(1.0, 1.0, 1.0), gain_rgb=(1.03, 1.02, 1.0),
        vignette=0.18,
    )
    return st_col


ACCENT_COLORS = {
    "01_Alex_Protagonist": "#38BDF8",
    "02_Noob_BestFriend":  "#FACC15",
    "03_RichKid_Dominus":  "#F59E0B",
    "04_Maya_BestFriend":  "#F472B6",
    "05_Dad_Principal":    "#60A5FA",
    "06_Hacker_Glitch":    "#A855F7",
    "07_Admin_Boss":       "#22D3EE",
    "08_Chloe_Rival":      "#E879F9",
}


def build_single_character(spec: dict):
    cid = spec["id"]
    print(f"\n========== BUILDING {cid} ({spec['display_name']}) ==========")
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_RIG))

    clean_invalid_drivers()
    active_parts = configure_body_type(feminine=spec["feminine"])
    body_mat = build_body_material(cid, spec["atlas_path"])

    # Assign upgraded cinema material to all 6 active parts
    for pname, pobj in active_parts.items():
        if pobj.data.materials:
            pobj.data.materials[0] = body_mat
        else:
            pobj.data.materials.append(body_mat)

    # Create Accessories & Extra_Accessories collections under Rig1
    rig_col = bpy.data.collections.get("Rig1") or bpy.context.scene.collection
    rig_col.name = cid  # Clean collection name for easy File -> Append!

    acc_col = bpy.data.collections.new(f"{cid}_Accessories")
    rig_col.children.link(acc_col)

    for acc_key in spec.get("accessories", []):
        attach_marketplace_accessory(cid, acc_key, active_parts, acc_col, hidden=False)
        print(f"  + Attached Marketplace accessory: {acc_key}")

    if spec.get("extra_accessories"):
        extra_col = bpy.data.collections.new(f"{cid}_Extra_Swaps")
        rig_col.children.link(extra_col)
        for acc_key in spec["extra_accessories"]:
            attach_marketplace_accessory(cid, acc_key, active_parts, extra_col, hidden=True)
            print(f"  + Added swappable accessory (hidden): {acc_key}")

    # Hide POVCamera & RigShapes from render
    for o in bpy.data.objects:
        if o.name.startswith("_Shape_") or o.name == "POVCamera":
            o.hide_render = True

    # Ensure all textures packed and save CLEAN REST-POSE .blend for animation!
    bpy.ops.file.pack_all()
    blend_out = CHARS_DIR / f"{cid}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_out))
    print(f"  [SAVED] Rest-pose rigged .blend -> {blend_out.name}")

    # Now apply signature personality pose + render studio portrait to verify look & rigging!
    arm = bpy.data.objects["__PrimaryArmature"]
    apply_personality_pose(arm, spec["pose"])
    setup_portrait_studio(bpy.context.scene, accent_hex=ACCENT_COLORS.get(cid, "#38BDF8"))

    render_out = RENDERS_DIR / f"{cid}.png"
    bpy.context.scene.render.filepath = str(render_out)
    bpy.context.scene.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    print(f"  [RENDERED] Portrait -> {render_out.name}")


def main():
    for spec in CHAR_MANIFEST:
        build_single_character(spec)
    print("\nALL 8 RIGGED ROBLOX R6 CHARACTERS BUILT & RENDERED SUCCESSFULLY!")


if __name__ == "__main__":
    main()
