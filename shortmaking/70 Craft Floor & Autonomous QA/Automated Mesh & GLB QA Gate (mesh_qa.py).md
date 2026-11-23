---
title: Automated Mesh & GLB QA Gate (mesh_qa.py)
tags: [qa, gate, python, glb, stl, obj, validation]
updated: 2026-11-20
---

# Automated Mesh & GLB QA Gate (`mesh_qa.py`)

This vault ships a zero-dependency-fallback (plus enhanced `trimesh` support) automated mesh validator at **`80 Tools & MCPs/gate/mesh_qa.py`**.

Run it on EVERY exported `.glb`, `.gltf`, `.obj`, or `.stl` before passing to the visual critic!

---

## 1. Usage

```powershell
# Default web-hero profile
python "C:\Users\AFADAZIO\Obsidian\3D-Master-Vault\80 Tools & MCPs\gate\mesh_qa.py" model.glb

# Specific target profile
python "C:\Users\AFADAZIO\Obsidian\3D-Master-Vault\80 Tools & MCPs\gate\mesh_qa.py" ugc_hat.glb --profile roblox-ugc
python "C:\Users\AFADAZIO\Obsidian\3D-Master-Vault\80 Tools & MCPs\gate\mesh_qa.py" prop.glb --profile roblox-meshpart
python "C:\Users\AFADAZIO\Obsidian\3D-Master-Vault\80 Tools & MCPs\gate\mesh_qa.py" bracket.stl --profile 3d-print
python "C:\Users\AFADAZIO\Obsidian\3D-Master-Vault\80 Tools & MCPs\gate\mesh_qa.py" hero.glb --profile film-hero --json
```

---

## 2. Built-In Profiles & Thresholds

| Profile | Max Triangles | Max File Size | Max Texture Dim | Watertight Required | UV Required |
|---|---|---|---|---|---|
| `web-hero` | `50,000` | `8 MB` | `2048 px` | No | Yes |
| `web-prop` | `10,000` | `2 MB` | `1024 px` | No | Yes |
| `roblox-ugc` | `4,000` | `5 MB` | `1024 px` | No | Yes |
| `roblox-meshpart` | `10,000` | `10 MB` | `1024 px` | No | Yes |
| `game-hero` | `80,000` | `40 MB` | `4096 px` | No | Yes |
| `film-hero` | `2,000,000` | `500 MB` | `8192 px` | No | Yes |
| `3d-print` | `1,000,000` | `100 MB` | N/A | **Yes** | No |

---

## 3. What `mesh_qa.py` Audits Automatically
- Binary GLB header, JSON chunk integrity, mesh/primitive/material/texture counts
- Total triangle count & vertex count vs profile budget
- Embedded texture resolutions & file byte budget
- Real-world bounding box (`X × Y × Z` meters) + absurd-scale detection (`< 0.005 m` or `> 500 m`) + grounding check (`min_y` / `min_z` near `0`)
- UV coordinate presence (`TEXCOORD_0`) & normal attribute presence (`NORMAL`)
- Negative node scales (flipped-normal trap!)
- Watertightness / NaN vertex detection (when `trimesh` is available or direct binary inspection on `.stl` / `.obj`)

## Related Notes
- [[Craft Floor — Non-Negotiable 3D Quality Gates]]
- [[The Visual Critic & Cook Loop for 3D Assets]]
- [[glTF - GLB & USD Export Pipeline (Zero-Defect Rules)]]
