# Roblox R6 Story Cast — Rigged Blender 5.3 Character Library

Built on **Aeresei's official R6 IK + FK Blender Rig V2.22** (SHA-256 verified) and dressed with **50 real Roblox Marketplace assets** (official 3D `.mesh` accessories, classic shirts, classic pants, and classic faces). All textures are packed into every `.blend` file so each character can be opened standalone or appended (`File → Append → Collection`) straight into any story scene.

## Files & Folders

- `Roblox_R6_Story_Cast.blend` — Master Blender 5.3.0 scene with all **8 fully rigged R6 characters** arranged on a glossy Roblox Stud Stage with Kelvin 3-point + rim studio lighting.
- `characters/` — **8 individual, self-contained, rest-pose rigged `.blend` files** ready for animation:
  1. `01_Alex_Protagonist.blend` — **Alex (Main Hero / Narrator)** (`MBlocky`) · *Pal Hair (`63690008`), Denim Jacket w/ White Hoodie (`398633584`), Black Jeans w/ White Shoes (`398633812`), Check It (`7074786`)* · Extra swap: *Red Roblox Cap (`1028606`)*
  2. `02_Noob_BestFriend.blend` — **Noob (Classic Goofy Best Friend)** (`MBlocky`) · *Classic Noob BrickColors, Red Roblox Cap (`1028606`), Silly Fun (`15432080`)* · Extra swap: *Angel Halo & Wings (`15967743`)*
  3. `03_RichKid_Dominus.blend` — **Rich Kid (Billionaire Flexer / Rival)** (`MBlocky`) · *Dominus Empyreus (`21070012`), Clockwork Shades (`11748356`), Gold-Trim Royal Tuxedo, Black Slacks (`129459077`), Chill (`7074764`)* · Extra swap: *Domino Crown (`1031429`)*
  4. `04_Maya_BestFriend.blend` — **Maya (Cool Girl / Smart Best Friend / Sister)** (`FBlocky`) · *Beautiful Hair for Beautiful People (`16630147`), Rose Colored Glasses (`25931812`), Pastel Starburst Top w/ Gray Jacket (`398634295`), Beautiful You Jeans (`398634487`), Super Super Happy Face (`494291269`)* · Extra swaps: *ROBLOX Girl Hair (`48474294`), Chestnut Bun (`62724852`)*
  5. `05_Dad_Principal.blend` — **Dad / Teacher / Principal** (`MBlocky`) · *Classic ROBLOX Fedora (`1029025`), Nerd Glasses (`11884330`), Blue Plaid Shirt (`398635081`), Black Slacks (`129459077`), Man Face (`86487700`)* · Extra swap: *Shaggy (`20573078`)*
  6. `06_Hacker_Glitch.blend` — **Hacker (Chaos Villain / Prankster)** (`MBlocky`) · *The Void Star (`1125510`), Midnight Shades (`30331986`), Bandit Mask (`20642008`), Guitar Tee w/ Black Jacket (`4047884046`), Ripped Skater Pants (`398635338`), Err (`209994875`)* · Extra swap: *Domino Crown (`1031429`)*
  7. `07_Admin_Boss.blend` — **Admin (Roblox Admin / Judge / Boss)** (`MBlocky`) · *Valkyrie Helm (`1365767`), Classic Swordpack (`19398258`), Blue & Black Motorcycle Shirt (`144076358`), Black Jeans w/ Sneakers (`382538503`), Skeptic (`26424808`)* · Extra swap: *Clockwork Shades (`11748356`)*
  8. `08_Chloe_Rival.blend` — **Chloe (Popular Rival / Sassy Classmate / Karen)** (`FBlocky`) · *Lavender Updo (`451220849`), Stylish Aviators (`376526673`), Purple & Teal Top (`4047886060`), Jean Shorts w/ White Shoes (`382537950`), Woman Face (`86487766`)* · Extra swap: *Blonde Spiked Hair (`376524487`)*
- `renders/` — High-resolution Blender 5.3 renders (`cast_lineup_all8.png`, `cast_contact_sheet.png`, and `01_*.png`–`08_*.png`).
- `source_rig/Blender_R6_Rig_v222.blend` — Original SHA-256 verified Aeresei R6 IK + FK Blender Rig V2.22.
- `marketplace_assets/` — Cached raw `.rbxm`/`.rbxmx`, `.mesh`, converted `.obj`, and `.png` textures for all 50 real Roblox Marketplace assets.
- `scripts/` — Reproducible automation pipeline (`download_marketplace_assets.py`, `bake_textures.py`, `build_characters.py`, `build_master_lineup.py`) so you can add more Roblox characters from any Marketplace Asset IDs in seconds.

## Quick Animation Guide (Blender 5.3)

1. **Append a Character**: `File → Append → characters/01_Alex_Protagonist.blend → Collection → 01_Alex_Protagonist`.
2. **Animate Controls**: Select `__PrimaryArmature` (or `<char_id>_Rig` in the master cast file) and enter **Pose Mode**:
   - **`MasterControl`**: Move & rotate the whole character (body + all Marketplace accessories move together).
   - **`LowerTorso-FK` / `Torso_FK`**: Hip bob, lean, and torso twist.
   - **`Head`**: Head turns, nods, and comedy reactions (hats, hair, and glasses follow automatically).
   - **`RightArm_FK` / `LeftArm_FK`** (or switch `Right Arm` / `Left Arm` empty property `IK/FK` to `1.0` to use `RightArm-IK` / `LeftArm-IK`).
   - **`RightLeg-IK` / `LeftLeg-IK`**: Planted IK feet for walks, jumps, and dramatic stances.
3. **Swap Accessories**: Expand `<char_id>_Extra_Swaps` in the Outliner and toggle viewport/render visibility on alternate hats or hairs.
