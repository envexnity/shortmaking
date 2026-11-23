---
name: forge-gui
description: Design, generate, and inject production-grade Game UI for Roblox and game engines. Replicates ForgeGUI + Claude Pro with AI UI planning, 9-slice generation, responsive Luau code, interactive HTML previews, and live Studio integration.
---

# ForgeGUI Studio Skill

Use this skill whenever you need to build, generate, restyle, or integrate game UI assets and code for Roblox (or other game engines like UEFN / Unity).

## Core Capabilities

1. **AI UI Architecture & Design Tokens (`forge_plan_ui`)**
   - Automatically computes genre-specific color palettes (Simulator, Anime, Sci-Fi, RPG, Horror, Clean Glassmorphism).
   - Establishes scale bounds (`UISizeConstraint`), `UIAspectRatioConstraint`, and corner radii.
   - Plans the instance hierarchy (`ScreenGui`, `MainFrame`, `Header`, `ScrollingFrame`, `Grid`).

2. **Interactive HTML5 Responsive Previewer (`forge_preview_interactive`)**
   - Creates a standalone interactive web playground in the user's workspace.
   - Emulates mobile (iPhone), tablet (iPad), PC 1080p, and console viewports with live device switcher pills.
   - Built-in Web Audio synthesis provides real tactile clicks, bubbly pops, and purchase chimes without external assets.
   - Allows the user to test button bounce physics and responsive scaling before pushing into the game.

3. **Production Luau Code Generation (`forge_build_luau`)**
   - 100% scale-based coordinates (`UDim2.fromScale(x, y)`), eliminating device-specific layout bugs.
   - Integrated `TweenService` micro-interactions (bouncy hover, squash on press, spring release).
   - Audio feedback hooked up to Roblox `SoundService`.
   - Grid scrolling with `AutomaticCanvasSize = Enum.AutomaticSize.Y`.

4. **Roblox XML Model Export (`forge_export_rbxmx`)**
   - Generates `.rbxmx` XML files ready for instant drag-and-drop into Roblox Studio `StarterGui`.

5. **Live Studio Injection (`forge_push_studio` & Desktop Automation)**
   - When Ropilot is connected, runs Lua directly in Studio's edit context via `ropilot_edit_ctx_run_command`.
   - Can also generate Command Bar snippets or automate window focus via `windows-desktop`.

---

## Step-by-Step Workflow

### Step 1: Analyze & Plan the UI
Call `forge_plan_ui` with the target `genre` and `screen_type`:
```json
{
  "title": "Pet Hatching Shop",
  "genre": "simulator",
  "screen_type": "shop"
}
```

### Step 2: Generate Interactive Preview
Call `forge_preview_interactive` so the user can immediately open and interact with the UI:
```json
{
  "title": "Pet Hatching Shop",
  "genre": "simulator",
  "screen_type": "shop"
}
```
Provide the clickable `file:///` link to the generated HTML file in chat.

### Step 3: Build Production Luau Code
Call `forge_build_luau` with customized items, rarity badges, and pricing:
```json
{
  "screen_name": "PetShopGui",
  "genre": "simulator",
  "screen_type": "shop",
  "include_tweens": true,
  "include_sounds": true
}
```

### Step 4: Deliver to Studio
- If the user wants a model file: Call `forge_export_rbxmx`.
- If Studio is open and connected: Call `ropilot_edit_ctx_run_command` or `forge_push_studio`.
- If using desktop automation: Call `windows-desktop:focus_window` for Roblox Studio.
