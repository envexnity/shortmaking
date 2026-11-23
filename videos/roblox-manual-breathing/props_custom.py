"""
props_custom.py — Custom 3D Storytelling Props & Glowing UI Sign Plates for roblox-manual-breathing.
Pure bmesh + PIL graphic plates so timers, lungs, air wisps, No-Pause button, Disconnect alert,
20,000 counter, and Manual Breathe button read instantly at 1080x1920.
"""
import math
import sys
from pathlib import Path

try:
    import bmesh
    import bpy
    from mathutils import Euler, Vector
except ImportError:
    bmesh = bpy = Euler = Vector = None

SHORTMAKING_ROOT = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking")
V2_DIR = SHORTMAKING_ROOT / "videos" / "roblox-reel-Df1kubCJ-o0-v2"
PROJ_DIR = SHORTMAKING_ROOT / "videos" / "roblox-manual-breathing"
UI_DIR = PROJ_DIR / "textures" / "ui_plates"
UI_DIR.mkdir(parents=True, exist_ok=True)

if bpy is not None:
    sys.path.insert(0, str(V2_DIR))
    import scene_common as sc
    import props_factory as pf


def generate_ui_plates():
    """Generate crisp glowing 3D signage textures for timers, disconnect, no-pause, 20k, and manual button."""
    from PIL import Image, ImageDraw, ImageFont

    def _load_font(sz: int):
        for p in ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/impact.ttf"]:
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                continue
        return ImageFont.load_default()
    specs = [
        ("plate_auto_on.png",   (12, 34, 28),  (34, 238, 120),  "AUTO MODE: ON",    "#22EE78"),
        ("plate_manual.png",    (48, 10, 14),  (255, 51, 68),   "MANUAL MODE!",     "#FF3344"),
        ("plate_breathe.png",   (180, 20, 32), (255, 220, 220), "BREATHE",          "#FFFFFF"),
        ("plate_no_pause.png",  (40, 12, 16),  (255, 68, 68),   "NO PAUSE",         "#FF4444"),
        ("plate_logout.png",    (32, 12, 16),  (255, 51, 68),   "DISCONNECTED",     "#FF4455"),
        ("plate_20k.png",       (12, 24, 48),  (56, 189, 248),  "20,000 / DAY",     "#38BDF8"),
        ("plate_timer_ok.png",  (10, 32, 36),  (56, 238, 180),  "00:03.8",          "#38EEB4"),
        ("plate_timer_low.png", (48, 12, 14),  (255, 51, 68),   "00:00.0",          "#FF3344"),
        ("plate_zzz.png",       (18, 22, 54),  (165, 180, 252), "Z z z . . .",      "#C7D2FE"),
    ]
    font = _load_font(64)
    for fname, bg, border, text, fg_hex in specs:
        p = UI_DIR / fname
        if p.exists():
            continue
        im = Image.new("RGBA", (640, 220), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([8, 8, 632, 212], radius=32, fill=bg + (242,), outline=border + (255,), width=10)
        bb = d.textbbox((0, 0), text, font=font)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        d.text(((640 - tw) // 2 - bb[0], (220 - th) // 2 - bb[1]), text, fill=fg_hex, font=font)
        im.save(p)


def make_emissive_plate_obj(name: str, png_name: str, loc, width_m: float, height_m: float, col, rot=(math.radians(90), 0, 0), emit_str: float = 2.6, parent=None):
    """Create a double-sided crisp UV-mapped 3D UI sign slab."""
    p = UI_DIR / png_name
    mat_name = f"Mat_UI_{png_name}"
    m = bpy.data.materials.get(mat_name)
    if m is None:
        m = bpy.data.materials.new(mat_name)
        nt = m.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Roughness"].default_value = 0.35
        bsdf.inputs["Emission Strength"].default_value = emit_str
        tex = nt.nodes.new("ShaderNodeTexImage")
        img = bpy.data.images.load(str(p), check_existing=True)
        img.colorspace_settings.name = "sRGB"
        tex.image = img
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
        nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
        if hasattr(m, "surface_render_method"):
            m.surface_render_method = "BLENDED"

    bm = bmesh.new()
    hw, hh = width_m * 0.5, height_m * 0.5
    v0 = bm.verts.new((-hw, -hh, 0.0))
    v1 = bm.verts.new(( hw, -hh, 0.0))
    v2 = bm.verts.new(( hw,  hh, 0.0))
    v3 = bm.verts.new((-hw,  hh, 0.0))
    f = bm.faces.new((v0, v1, v2, v3))
    uv = bm.loops.layers.uv.new("UVMap")
    # Viewed from +Y (camera looking -Y), +X is screen-left and -X is screen-right:
    # map u=0 to +hw (v1, v2) and u=1 to -hw (v0, v3) so text reads left-to-right!
    uvs = [(1.0, 0.0), (0.0, 0.0), (0.0, 1.0), (1.0, 1.0)]
    for lp, uvc in zip(f.loops, uvs):
        lp[uv].uv = uvc

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.rotation_euler = rot
    col.objects.link(obj)
    obj.data.materials.append(m)
    if parent:
        obj.parent = parent
    return obj


def build_air_wisps(name: str, col, count: int = 10):
    """Build small glowing cyan air-stream spheres that animate into/out of a character's mouth/nose without blocking eyes."""
    m_air = sc.make_stylized_pbr("Mat_AirWisp", "#38BDF8", rough=0.18, emit_hex="#7DD3FC", emit_str=3.5, alpha=0.80)
    wisps = []
    for i in range(count):
        s = pf.make_smooth_sphere(f"{name}_{i}", (0, 0, -10), (0.022, 0.022, 0.022), m_air, col, segs=12)
        wisps.append(s)
    return wisps


def animate_air_wisps(wisps: list, head_pos: tuple, t: float, speed: float = 1.8, exhale: bool = False):
    hx, hy, hz = head_pos
    n = len(wisps)
    for i, w in enumerate(wisps):
        u = ((t * speed) + i / n) % 1.0
        if exhale:
            u = 1.0 - u
        # Stream from front-lower air curving into mouth/nose (hz - 0.08) so eyes remain 100% clear
        dist = 0.78 * (1.0 - u) + 0.19
        ang = (i * 1.15) + u * 4.2
        spread = (1.0 - u) * 0.22 + 0.03
        w.location = (hx + math.cos(ang) * spread, hy + dist, (hz - 0.08) + math.sin(ang) * spread * 0.45)
        sc_sz = 0.50 + 0.60 * math.sin(u * math.pi)
        w.scale = (sc_sz, sc_sz, sc_sz)


def build_xray_lungs(name: str, col):
    """Build two stylized glowing lung pouches + bronchi in front of torso for crisp X-ray readability."""
    root = bpy.data.objects.new(name, None)
    col.objects.link(root)
    m_lung = sc.make_stylized_pbr("Mat_LungGlow", "#FB7185", rough=0.25, sss=0.25, emit_hex="#F43F5E", emit_str=2.6)
    m_tube = sc.make_stylized_pbr("Mat_Trachea", "#38BDF8", rough=0.25, emit_hex="#7DD3FC", emit_str=2.4)
    pf.make_smooth_cyl(f"{name}_Trachea", (0.0, 0.185, 1.24), 0.026, 0.22, m_tube, col, segs=16, parent=root)
    pf.make_smooth_cyl(f"{name}_BronchL", (-0.06, 0.185, 1.12), 0.018, 0.14, m_tube, col, segs=12, rot=(0, math.radians(65), 0), parent=root)
    pf.make_smooth_cyl(f"{name}_BronchR", ( 0.06, 0.185, 1.12), 0.018, 0.14, m_tube, col, segs=12, rot=(0, math.radians(-65), 0), parent=root)
    lung_l = pf.make_smooth_sphere(f"{name}_LungL", (-0.118, 0.190, 1.01), (0.102, 0.042, 0.165), m_lung, col, segs=18, parent=root)
    lung_r = pf.make_smooth_sphere(f"{name}_LungR", ( 0.118, 0.190, 1.01), (0.102, 0.042, 0.165), m_lung, col, segs=18, parent=root)
    return {"root": root, "l": lung_l, "r": lung_r}


def build_arcade_button(name: str, loc, col, cap_hex: str = "#EF4444", emit_hex: str = "#FF3344", plate_png: str = "plate_breathe.png"):
    """Build a chunky tactile Roblox arcade button on a dark metallic pedestal."""
    root = bpy.data.objects.new(name, None)
    root.location = loc
    col.objects.link(root)
    m_base = sc.make_stylized_pbr(f"Mat_{name}_Base", "#1E293B", rough=0.34, metal=0.65)
    m_ped = sc.make_stylized_pbr(f"Mat_{name}_Ped", "#334155", rough=0.42, metal=0.40)
    m_cap = sc.make_stylized_pbr(f"Mat_{name}_Cap", cap_hex, rough=0.22, coat=0.45, emit_hex=emit_hex, emit_str=1.6)
    pf.make_bevel_box(f"{name}_Pedestal", (0, 0, 0.42), (0.68, 0.68, 0.84), m_ped, col, bevel_w=0.02, parent=root)
    pf.make_bevel_box(f"{name}_Housing", (0, 0, 0.88), (0.56, 0.56, 0.10), m_base, col, bevel_w=0.015, parent=root)
    cap = pf.make_smooth_cyl(f"{name}_Cap", (0, 0, 0.96), 0.21, 0.11, m_cap, col, segs=28, bevel_w=0.018, parent=root)
    sign = make_emissive_plate_obj(f"{name}_Sign", plate_png, (0, 0.345, 0.56), 0.56, 0.20, col, rot=(math.radians(90), 0, 0), emit_str=2.8, parent=root)
    return {"root": root, "cap": cap, "sign": sign}


def build_bed(name: str, loc, col):
    """Build a cozy Roblox Studio wooden bed with mattress, pillow, and teal blanket."""
    root = bpy.data.objects.new(name, None)
    root.location = loc
    col.objects.link(root)
    m_wood = sc.make_textured_pbr("Mat_BedWood", sc.TEX_ENV / "wood_table_espresso.png", sc.TEX_ENV / "wood_table_espresso_bump.png", uv_scale=(0.8, 0.8, 0.8), rough_min=0.42, rough_max=0.58)
    m_mat = sc.make_stylized_pbr("Mat_BedMat", "#F8FAFC", rough=0.72, sheen=0.4)
    m_blnk = sc.make_stylized_pbr("Mat_BedBlanket", "#0EA5E9", rough=0.68, sheen=0.45)
    m_pil = sc.make_stylized_pbr("Mat_BedPillow", "#FFFFFF", rough=0.75, sheen=0.5)

    pf.make_bevel_box(f"{name}_Frame", (0, 0, 0.22), (1.28, 2.15, 0.18), m_wood, col, bevel_w=0.02, parent=root)
    pf.make_bevel_box(f"{name}_Headboard", (0, -1.04, 0.62), (1.32, 0.10, 0.96), m_wood, col, bevel_w=0.02, parent=root)
    pf.make_bevel_box(f"{name}_Mattress", (0, 0.02, 0.40), (1.18, 2.00, 0.22), m_mat, col, bevel_w=0.04, parent=root)
    pf.make_bevel_box(f"{name}_Blanket", (0, 0.28, 0.45), (1.22, 1.46, 0.20), m_blnk, col, bevel_w=0.045, parent=root)
    pf.make_bevel_box(f"{name}_Pillow", (0, -0.76, 0.56), (0.82, 0.36, 0.14), m_pil, col, bevel_w=0.05, parent=root)
    return root


if __name__ == "__main__":
    generate_ui_plates()
    print(f"Generated {len(list(UI_DIR.glob('*.png')))} UI plate textures in {UI_DIR}")
