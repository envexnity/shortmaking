"""
download_marketplace_assets.py
Downloads real Roblox Marketplace assets (Accessories, Hair, Hats, Glasses, Backpacks,
Faces, Classic Shirts, Classic Pants) from Roblox AssetDelivery API, parses XML & binary RBXM
metadata via rbxm_reader, converts Roblox .mesh files to .obj via mesh_reader, and saves a
verified manifest.json.
"""
import gzip
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking\assets\roblox-r6-characters")
SCRIPTS_DIR = ROOT / "scripts"
CACHE_DIR = ROOT / "marketplace_assets"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(SCRIPTS_DIR))
from readers import mesh_reader, rbxm_reader


def fetch_raw(asset_id: int) -> bytes:
    url = f"https://assetdelivery.roblox.com/v1/asset/?id={asset_id}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Roblox/WinInet",
            "Accept-Encoding": "gzip, deflate",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = resp.read()
    if data[:2] == b"\x1f\x8b":
        data = gzip.decompress(data)
    return data


def extract_id(val) -> int | None:
    if not val:
        return None
    if isinstance(val, dict):
        for k in ("uri", "url", "value", "id"):
            if k in val and val[k]:
                r = extract_id(val[k])
                if r:
                    return r
        return None
    s = str(val)
    m = re.search(r"(\d{5,})", s)
    return int(m.group(1)) if m else None


def to_vec3(v):
    if v is None:
        return None
    if isinstance(v, (list, tuple)) and len(v) >= 3:
        return [float(v[0]), float(v[1]), float(v[2])]
    if isinstance(v, dict) and all(k in v for k in ("x", "y", "z")):
        return [float(v["x"]), float(v["y"]), float(v["z"])]
    if hasattr(v, "x"):
        return [float(v.x), float(v.y), float(v.z)]
    return None


def to_cframe(cf):
    if cf is None:
        return None
    if isinstance(cf, dict):
        pos = to_vec3(cf.get("position") or cf.get("pos"))
        rot = cf.get("rotation") or cf.get("rot")
        if rot and len(rot) == 9:
            rot = [list(map(float, rot[0:3])), list(map(float, rot[3:6])), list(map(float, rot[6:9]))]
        elif rot and len(rot) == 3 and isinstance(rot[0], (list, tuple)):
            rot = [list(map(float, r)) for r in rot]
        else:
            rot = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        if pos:
            return {"pos": pos, "rot": rot}
    if hasattr(cf, "position"):
        pos = to_vec3(cf.position)
        r = getattr(cf, "rotation", None)
        if r and len(r) == 9:
            rot = [list(map(float, r[0:3])), list(map(float, r[3:6])), list(map(float, r[6:9]))]
        elif r and len(r) == 3 and isinstance(r[0], (list, tuple)):
            rot = [list(map(float, row)) for row in r]
        else:
            rot = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        return {"pos": pos, "rot": rot}
    if isinstance(cf, (list, tuple)):
        if len(cf) == 12:
            return {
                "pos": [float(cf[0]), float(cf[1]), float(cf[2])],
                "rot": [
                    [float(cf[3]), float(cf[4]), float(cf[5])],
                    [float(cf[6]), float(cf[7]), float(cf[8])],
                    [float(cf[9]), float(cf[10]), float(cf[11])],
                ],
            }
        elif len(cf) == 2 and isinstance(cf[0], (list, tuple)):
            pos = to_vec3(cf[0])
            r = cf[1]
            if len(r) == 9:
                rot = [list(map(float, r[0:3])), list(map(float, r[3:6])), list(map(float, r[6:9]))]
            else:
                rot = [list(map(float, row)) for row in r]
            return {"pos": pos, "rot": rot}
    return None


def parse_model_file(path: Path) -> dict:
    info = {
        "class": None,
        "name": "",
        "mesh_id": None,
        "texture_id": None,
        "scale": [1.0, 1.0, 1.0],
        "offset": [0.0, 0.0, 0.0],
        "vertex_color": [1.0, 1.0, 1.0],
        "attachment_name": "HatAttachment",
        "attachment_pos": [0.0, 0.0, 0.0],
        "attachment_right": [1.0, 0.0, 0.0],
        "attachment_up": [0.0, 1.0, 0.0],
        "attachment_forward": [0.0, 0.0, -1.0],
        "attachment_cframe": None,
        "handle_size": [1.0, 1.0, 1.0],
        "template_id": None,
        "meshes": [],
    }
    model = rbxm_reader.parse(str(path))

    def walk(inst):
        cls = getattr(inst, "class_name", "")
        props = getattr(inst, "properties", {}) or {}
        if cls in ("Accessory", "Hat", "Shirt", "Pants", "Decal"):
            if info["class"] is None:
                info["class"] = cls
            if not info["name"] and "Name" in props:
                info["name"] = str(props["Name"])
            for k in ("ShirtTemplate", "PantsTemplate", "Texture"):
                if k in props:
                    aid = extract_id(props[k])
                    if aid:
                        info["template_id"] = aid
            for k, field in [
                ("AttachmentPos", "attachment_pos"),
                ("AttachmentRight", "attachment_right"),
                ("AttachmentUp", "attachment_up"),
                ("AttachmentForward", "attachment_forward"),
            ]:
                if k in props:
                    v3 = to_vec3(props[k])
                    if v3:
                        info[field] = v3

        elif cls in ("SpecialMesh", "FileMesh", "MeshPart"):
            mid = None
            tid = None
            for k in ("MeshId", "MeshID"):
                if k in props:
                    mid = extract_id(props[k]) or mid
            for k in ("TextureId", "TextureID"):
                if k in props:
                    tid = extract_id(props[k]) or tid
            sc = to_vec3(props.get("Scale")) or [1.0, 1.0, 1.0]
            off = to_vec3(props.get("Offset")) or [0.0, 0.0, 0.0]
            vc = to_vec3(props.get("VertexColor")) or [1.0, 1.0, 1.0]
            if mid and info["mesh_id"] is None:
                info["mesh_id"] = mid
                info["texture_id"] = tid
                info["scale"] = sc
                info["offset"] = off
                info["vertex_color"] = vc
            if mid:
                info["meshes"].append({
                    "mesh_id": mid,
                    "texture_id": tid,
                    "scale": sc,
                    "offset": off,
                    "vertex_color": vc,
                })

        elif cls == "Part":
            sz = to_vec3(props.get("size") or props.get("Size"))
            if sz:
                info["handle_size"] = sz

        elif cls == "Attachment":
            aname = str(props.get("Name", "")).strip()
            if aname:
                info["attachment_name"] = aname
            cf = to_cframe(props.get("CFrame"))
            if cf:
                info["attachment_cframe"] = cf

        for ch in getattr(inst, "children", []) or []:
            walk(ch)

    for r in getattr(model, "roots", []) or []:
        walk(r)
    return info


# Curated 100% Real Official Roblox Marketplace Catalog Assets for our 8-Character Story Cast
ASSET_CATALOG = {
    # --- HAIR ---
    "pal_hair":            {"id": 63690008,   "kind": "accessory", "label": "Pal Hair (Classic Bacon Hair)"},
    "blonde_spiked_hair":  {"id": 376524487,  "kind": "accessory", "label": "Blonde Spiked Hair"},
    "brown_charmer_hair":  {"id": 3814474927, "kind": "accessory", "label": "Brown Charmer Hair"},
    "lavender_updo":       {"id": 451220849,  "kind": "accessory", "label": "Lavender Updo"},
    "chestnut_bun":        {"id": 62724852,   "kind": "accessory", "label": "Chestnut Bun"},
    "shaggy":              {"id": 20573078,   "kind": "accessory", "label": "Shaggy"},
    "orange_beanie_hair":  {"id": 376548738,  "kind": "accessory", "label": "Orange Beanie with Black Hair"},
    # --- HATS / CROWNS / HELMETS ---
    "red_roblox_cap":      {"id": 1028606,    "kind": "accessory", "label": "Red Roblox Cap"},
    "propeller_beanie":    {"id": 15967743,   "kind": "accessory", "label": "Propeller Beanie"},
    "dominus_empyreus":    {"id": 21070012,   "kind": "accessory", "label": "Dominus Empyreus"},
    "valkyrie_helm":       {"id": 1365767,    "kind": "accessory", "label": "Valkyrie Helm"},
    "domino_crown":        {"id": 1031429,    "kind": "accessory", "label": "Domino Crown"},
    "classic_fedora":      {"id": 1029025,    "kind": "accessory", "label": "Classic ROBLOX Fedora"},
    "void_star":           {"id": 1125510,    "kind": "accessory", "label": "The Void Star"},
    # --- FACE ACCESSORIES (GLASSES / SHADES / MASKS) ---
    "nerd_glasses":        {"id": 11884330,   "kind": "accessory", "label": "Nerd Glasses"},
    "stylish_aviators":    {"id": 376526673,  "kind": "accessory", "label": "Stylish Aviators"},
    "midnight_shades":     {"id": 30331986,   "kind": "accessory", "label": "Midnight Shades"},
    "clockwork_shades":    {"id": 11748356,   "kind": "accessory", "label": "Clockwork Shades"},
    "rose_glasses":        {"id": 25931812,   "kind": "accessory", "label": "Rose Colored Glasses"},
    "bandit_mask":         {"id": 20642008,   "kind": "accessory", "label": "Bandit Mask"},
    # --- BACK ACCESSORIES ---
    "swordpack":           {"id": 19398258,   "kind": "accessory", "label": "Classic Swordpack"},
    # --- FACES (Decals) ---
    "face_smile":          {"id": 144075659,  "kind": "face", "label": "Smile"},
    "face_check_it":       {"id": 7074786,    "kind": "face", "label": "Check It"},
    "face_chill":          {"id": 7074764,    "kind": "face", "label": "Chill"},
    "face_silly_fun":      {"id": 15432080,   "kind": "face", "label": "Silly Fun"},
    "face_man":            {"id": 86487700,   "kind": "face", "label": "Man Face"},
    "face_woman":          {"id": 86487766,   "kind": "face", "label": "Woman Face"},
    "face_sshf":           {"id": 494291269,  "kind": "face", "label": "Super Super Happy Face"},
    "face_skeptic":        {"id": 26424808,   "kind": "face", "label": "Skeptic"},
    "face_err":            {"id": 209994875,  "kind": "face", "label": "Err / Grumpy"},
    "face_epic":           {"id": 7074893,    "kind": "face", "label": "Epic / Confident"},
    "face_shocked":        {"id": 277950647,  "kind": "face", "label": "Anguished / Shocked"},
    # --- CLASSIC SHIRTS ---
    "shirt_roblox_jacket": {"id": 607785314,  "kind": "shirt", "label": "ROBLOX Jacket"},
    "shirt_denim_hoodie":  {"id": 398633584,  "kind": "shirt", "label": "Denim Jacket with White Hoodie"},
    "shirt_blue_plaid":    {"id": 398635081,  "kind": "shirt", "label": "Blue Plaid Shirt"},
    "shirt_pastel_jacket": {"id": 398634295,  "kind": "shirt", "label": "Pastel Starburst Top with Gray Jacket"},
    "shirt_moto_blue":     {"id": 144076358,  "kind": "shirt", "label": "Blue and Black Motorcycle Shirt"},
    "shirt_guitar_black":  {"id": 4047884046, "kind": "shirt", "label": "Guitar Tee with Black Jacket"},
    "shirt_purple_teal":   {"id": 4047886060, "kind": "shirt", "label": "Purple and Teal Top"},
    "shirt_pizza":         {"id": 4047884939, "kind": "shirt", "label": "My Favorite Pizza Shirt"},
    "shirt_tuxedo":        {"id": 15466335,   "kind": "shirt", "label": "Classic Tuxedo Shirt"},
    "shirt_grey_denim":    {"id": 144076436,  "kind": "shirt", "label": "Grey Striped Shirt with Denim Jacket"},
    # --- CLASSIC PANTS ---
    "pants_black_white":   {"id": 398633812,  "kind": "pants", "label": "Black Jeans with White Shoes"},
    "pants_beautiful_you": {"id": 398634487,  "kind": "pants", "label": "Beautiful You Jeans"},
    "pants_ripped_skater": {"id": 398635338,  "kind": "pants", "label": "Ripped Skater Pants"},
    "pants_dark_green":    {"id": 144076760,  "kind": "pants", "label": "Dark Green Jeans"},
    "pants_jean_shorts":   {"id": 382537950,  "kind": "pants", "label": "Jean Shorts with White Shoes"},
    "pants_black_sneak":   {"id": 382538503,  "kind": "pants", "label": "Black Jeans with Sneakers"},
    "pants_black_slacks":  {"id": 129459077,  "kind": "pants", "label": "Black Slacks"},
}


def main():
    manifest = {}
    for key, spec in ASSET_CATALOG.items():
        aid = spec["id"]
        kind = spec["kind"]
        label = spec["label"]
        item_dir = CACHE_DIR / kind / key
        item_dir.mkdir(parents=True, exist_ok=True)
        try:
            raw = fetch_raw(aid)
            if raw[:4] == b"\x89PNG":
                p = item_dir / f"{aid}.png"
                p.write_bytes(raw)
                parsed = {"class": "Image", "template_id": aid}
            else:
                ext = ".rbxm" if raw[:8] == b"<roblox!" else ".rbxmx"
                p = item_dir / f"{aid}{ext}"
                p.write_bytes(raw)
                parsed = parse_model_file(p)

            entry = {
                "key": key,
                "asset_id": aid,
                "kind": kind,
                "label": label,
                "parsed": parsed,
                "files": {},
            }

            if kind in ("face", "shirt", "pants"):
                tid = parsed.get("template_id")
                if tid and raw[:4] != b"\x89PNG":
                    tex_bytes = fetch_raw(tid)
                    tex_path = item_dir / f"tex_{tid}.png"
                    tex_path.write_bytes(tex_bytes)
                    entry["files"]["texture"] = str(tex_path)
                elif raw[:4] == b"\x89PNG":
                    entry["files"]["texture"] = str(p)

            elif kind == "accessory":
                mid = parsed.get("mesh_id")
                tid = parsed.get("texture_id")
                if mid:
                    m_bytes = fetch_raw(mid)
                    m_path = item_dir / f"mesh_{mid}.mesh"
                    m_path.write_bytes(m_bytes)
                    mesh_json = mesh_reader.parse(m_bytes)
                    obj_path = item_dir / f"{key}.obj"
                    mesh_reader.write_obj_from_mesh_json(mesh_json, str(obj_path), lod_index=0, object_name=key)
                    entry["files"]["mesh"] = str(m_path)
                    entry["files"]["obj"] = str(obj_path)
                    entry["mesh_stats"] = {
                        "version": mesh_json.get("version"),
                        "verts": len(mesh_json.get("vertices", [])),
                        "faces": len(mesh_json.get("faces", [])),
                    }
                if tid:
                    t_bytes = fetch_raw(tid)
                    t_path = item_dir / f"tex_{tid}.png"
                    t_path.write_bytes(t_bytes)
                    entry["files"]["texture"] = str(t_path)

            manifest[key] = entry
            if kind == "accessory" and "mesh_stats" in entry:
                ms = entry["mesh_stats"]
                att = parsed.get("attachment_name")
                cf = parsed.get("attachment_cframe")
                pos_str = f"cf={cf['pos']}" if cf else f"pos={parsed.get('attachment_pos')}"
                print(f"[OK] {kind:9s} | {key:20s} | v{ms['version']} ({ms['verts']:4d}v/{ms['faces']:4d}f) | {att} {pos_str}")
            else:
                tex_f = Path(entry["files"].get("texture", "")).name if entry["files"].get("texture") else "NONE"
                print(f"[OK] {kind:9s} | {key:20s} | tex={tex_f}")
        except Exception as e:
            print(f"[FAIL] {kind:9s} | {key:20s} | id={aid} | {e}")

    manifest_path = CACHE_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nSaved verified manifest ({len(manifest)}/{len(ASSET_CATALOG)} assets) -> {manifest_path}")


if __name__ == "__main__":
    main()
