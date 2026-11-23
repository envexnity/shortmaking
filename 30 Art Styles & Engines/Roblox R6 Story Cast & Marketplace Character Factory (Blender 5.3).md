---
title: Roblox R6 Story Cast & Marketplace Character Factory (Blender 5.3)
tags:
  - engine
  - roblox
  - r6
  - blender
  - characters
  - rigging
  - marketplace
  - storytime
area: engines
style: roblox
status: evergreen
created: 2026-11-21
updated: 2026-11-21
summary: Production-ready library of 8 fully rigged Roblox R6 storytime characters (Aeresei IK+FK Rig V2.22 + 50 real Roblox Marketplace assets) with packed Blender 5.3 .blend files, master cast stage, and automated Marketplace-to-Blender character factory pipeline.
---

# Roblox R6 Story Cast & Marketplace Character Factory (`Blender 5.3`)

> [!IMPORTANT] Production Cast Location
> - **Master 8-Character Stage**: `assets/roblox-r6-characters/Roblox_R6_Story_Cast.blend`
> - **Individual Rest-Pose `.blend` Files**: `assets/roblox-r6-characters/characters/01_*.blend` → `08_*.blend`
> - **Verified Base Rig**: `assets/roblox-r6-characters/source_rig/Blender_R6_Rig_v222.blend` (*Aeresei R6 IK + FK Blender Rig V2.22*, SHA-256 verified)
> - **50 Cached Real Roblox Marketplace Assets**: `assets/roblox-r6-characters/marketplace_assets/`
> - **Reproducible Factory Scripts**: `assets/roblox-r6-characters/scripts/`

![[cast_lineup_all8.png]]

![[cast_contact_sheet.png]]

---

## 1. The 8-Character Storytime Cast Roster

Every character is built on **Aeresei's verified R6 IK + FK Rig V2.22**, cleaned of legacy Blender 4.x `pose.bones[...].hide` driver warnings for **Blender 5.3.0**, upgraded with Cinema PBR shading (`AgX - Punchy`, procedural roughness breakup, subtle clearcoat, micro-bump — per **Rule 32**), and packed with crisp **`2048×1024` HD UV atlases** plus **real 3D Roblox Marketplace accessories** locked to `InternalArmature` (`Head` / `Torso`) via `CHILD_OF` constraints.

| # | Collection / `.blend` File | Story Role | Body Type | Active Real Roblox Marketplace Assets | Swappable Extras (`*_Extra_Swaps`) |
| :- | :--- | :--- | :--- | :--- | :--- |
| **1** | `01_Alex_Protagonist.blend` | Main Hero / Story Narrator | `MBlocky` | Pal Hair (`63690008`), Denim Jacket w/ White Hoodie (`398633584`), Black Jeans w/ White Shoes (`398633812`), Check It (`7074786`) | Red Roblox Cap (`1028606`) |
| **2** | `02_Noob_BestFriend.blend` | Classic Goofy Best Friend / Comic Relief | `MBlocky` | Iconic Noob BrickColors (`#F5CD30` / `#0D69AC` / `#A4BD47`), Red Roblox Cap (`1028606`), Silly Fun (`15432080`) | Angel Halo & Wings (`15967743`) |
| **3** | `03_RichKid_Dominus.blend` | Billionaire Flexer / Rival | `MBlocky` | Dominus Empyreus (`21070012`), Clockwork Shades (`11748356`), Gold-Trim Royal Tuxedo (`585×559`), Black Slacks (`129459077`), Chill (`7074764`) | Domino Crown (`1031429`) |
| **4** | `04_Maya_BestFriend.blend` | Cool Girl / Smart Best Friend / Sister | `FBlocky` | Beautiful Hair for Beautiful People (`16630147`), Rose Colored Glasses (`25931812`), Pastel Starburst Jacket (`398634295`), Beautiful You Jeans (`398634487`), Super Super Happy Face (`494291269`) | ROBLOX Girl Hair (`48474294`), Chestnut Bun (`62724852`) |
| **5** | `05_Dad_Principal.blend` | Strict Dad / Teacher / Principal | `MBlocky` | Classic ROBLOX Fedora (`1029025`), Nerd Glasses (`11884330`), Blue Plaid Shirt (`398635081`), Black Slacks (`129459077`), Man Face (`86487700`) | Shaggy (`20573078`) |
| **6** | `06_Hacker_Glitch.blend` | Chaos Hacker / Prankster Villain | `MBlocky` | The Void Star (`1125510`, subtle emission glow), Midnight Shades (`30331986`), Bandit Mask (`20642008`), Guitar Black Jacket (`4047884046`), Ripped Skater Pants (`398635338`), Err (`209994875`) | Domino Crown (`1031429`) |
| **7** | `07_Admin_Boss.blend` | Roblox Admin / Judge / Final Boss | `MBlocky` | Valkyrie Helm (`1365767`), Classic Swordpack (`19398258`, Back), Blue & Black Motorcycle Shirt (`144076358`), Black Jeans w/ Sneakers (`382538503`), Skeptic (`26424808`) | Clockwork Shades (`11748356`) |
| **8** | `08_Chloe_Rival.blend` | Popular Rival / Sassy Classmate / Karen | `FBlocky` | Lavender Updo (`451220849`), Stylish Aviators (`376526673`), Purple & Teal Top (`4047886060`), Jean Shorts w/ White Shoes (`382537950`), Woman Face (`86487766`) | Blonde Spiked Hair (`376524487`) |

---

## 2. How to Use in Track 5 Roblox Story Shorts

### A. Appending Characters into Any Story Scene
1. In Blender 5.3 (or via Python `bpy.data.libraries.load`), append the character's named collection:
   - `File → Append → assets/roblox-r6-characters/characters/01_Alex_Protagonist.blend → Collection → 01_Alex_Protagonist`
2. Clear any leftover source action on `__PrimaryArmature` (`if arm.animation_data: arm.animation_data.action = None`) before positioning.
3. Move and rotate the entire character cleanly in world space via the **`MasterControl`** pose bone (both body meshes and all welded Marketplace accessories travel together).

### B. Rig Control Map (`__PrimaryArmature` in Pose Mode)
| Control Bone | Function | Default Mode |
| :--- | :--- | :--- |
| `MasterControl` | Root world position & yaw for the whole character + accessories | World Root |
| `LowerTorso-FK` / `Torso_FK` | Hip bounce, anticipation squash, comedic lean, torso twist | FK |
| `Head` | Head turns, nods, shock tilts (hair, hats, glasses follow automatically) | FK |
| `RightArm_FK` / `LeftArm_FK` | Snappy arm gestures, waves, pointing, flexing *(set `Right Arm`/`Left Arm` empty `IK/FK = 1.0` to use `RightArm-IK`/`LeftArm-IK`)* | FK (`0.0`) |
| `RightLeg-IK` / `LeftLeg-IK` | Planted IK feet for walk cycles, jumps, and wide power stances | IK (`1.0`) |

> [!TIP] Exact World Placement via Python (`MasterControl`)
> `MasterControl`'s rest bone axes differ from world Z-up, so always transform desired world `(wx, wy, wz)` and `yaw_deg` through its rest basis (see `place_rig_master_control()` in `assets/roblox-r6-characters/scripts/build_master_lineup.py`):
> ```python
> rest_3x3 = arm.data.bones["MasterControl"].matrix_local.to_3x3()
> inv_3x3 = rest_3x3.inverted()
> pb.location = inv_3x3 @ Vector((wx, wy, wz))
> pb.rotation_mode = "XYZ"
> pb.rotation_euler = (inv_3x3 @ Matrix.Rotation(math.radians(yaw_deg), 3, "Z") @ rest_3x3).to_euler("XYZ")
> ```

---

## 3. Technical Architecture (Marketplace-to-Blender Factory)

1. **Marketplace Asset Downloader (`scripts/download_marketplace_assets.py`)**:
   - Pulls official Roblox Marketplace items directly via `https://assetdelivery.roblox.com/v1/asset/?id=<ID>` (gzip-aware).
   - Parses both XML `.rbxmx` and binary `.rbxm` files using `scripts/readers/rbxm_reader.py` to extract `MeshId`, `TextureId`, `Scale`, `Offset`, `VertexColor`, and exact `Attachment` `CFrame`s (`HatAttachment`, `HairAttachment`, `FaceFrontAttachment`, `BodyBackAttachment`).
   - Decodes Roblox `.mesh` binaries (`v1.00–v5.00` + Draco) via `scripts/readers/mesh_reader.py` into clean `.obj` geometry.
2. **Exact R6 Coordinate & Attachment Weld (`scripts/build_characters.py`)**:
   - Applies Roblox `SpecialMesh.Scale` / `Offset` and Attachment weld `M_part_att @ M_acc_att.inverted()` in Roblox stud space (`1 Blender Unit = 1 Stud`, Head center `(0, 4.5, 0)`, Torso center `(0, 3.0, 0)`).
   - Rotates Roblox space `(X, Y_up, Z_back)` into `Blender_R6_Rig_v222` space `(X, -Z, +Y)` (`+90°` around X).
   - Merges Roblox v1.00 split-triangle vertices (`bmesh.ops.remove_doubles(..., dist=0.0005)`) while preserving UV loops + adds a `45°` `EDGE_SPLIT` modifier for silky-smooth hoods, shades, helmets, and hair.
   - Locks each accessory to `InternalArmature` (`Head` or `Torso`) using the exact same `CHILD_OF` `inverse_matrix` as the rig's native body parts.
3. **Pixel-Exact `2048×1024` HD UV Atlas Baker (`scripts/bake_textures.py`)**:
   - Composites base BrickColor skin tones → official `585×559` Classic Pants → official `585×559` Classic Shirts → Classic Face decals with `3px` bevel edge-bleed onto the exact measured `MBlocky`/`FBlocky` UV islands (`ROTATE_270` on vertical strips, `0°` on caps & upright head square at `X=[896..1024], Y=[0..128]`).

---

## 4. CLI Commands — Adding More Characters Anytime

```powershell
# 1. Fetch/update real Roblox Marketplace assets (edit ASSET_CATALOG in script to add any IDs)
python "assets/roblox-r6-characters/scripts/download_marketplace_assets.py"

# 2. Bake 2048x1024 HD texture atlases for all characters in CHARACTER_SPECS
python "assets/roblox-r6-characters/scripts/bake_textures.py"

# 3. Build all individual packed .blend characters + render 900x1200 studio portraits
& "C:\Program Files\Blender Foundation\Blender 5.3\blender.exe" --background --disable-autoexec --python "assets/roblox-r6-characters/scripts/build_characters.py"

# 4. Assemble master 8-character Roblox_R6_Story_Cast.blend & render 2560x1080 hero lineup poster
& "C:\Program Files\Blender Foundation\Blender 5.3\blender.exe" --background --disable-autoexec --python "assets/roblox-r6-characters/scripts/build_master_lineup.py"
```

---

## Related Vault Guides
- [[Style 5 - Roblox Animated Shorts (Ropilot + ForgeGUI + Blender R6-R15)]]
- [[In This World Roblox Storytime - Editing, Zooms & VFX Bible]]
- [[Blender 5.3 Cinematic Rendering & Animation Mastery Bible]]
- [[SFX Direction & The 2-4 Frame Lead-In Law]]
