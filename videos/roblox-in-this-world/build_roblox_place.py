"""
build_roblox_place.py — Generates a complete, self-contained native Roblox Studio Place file
(`JumpTaxStorytime.rbxlx`) for Track 5: "In This World, Every Jump You Make Costs 100 Robux" (< 45s).

Populates inside native Roblox XML (`version="4"`):
  1. `Workspace` with 5 complete Roblox 3D sets (classic Studded parts, Neon lava kill-bricks, R6 character Models
     with SpecialMesh heads + `rbxasset://textures/face.png`, overhead `BillboardGui` Robux counters, Dominus crowns,
     Gravity Coil, Tax Bot drone, and Admin Ban Hammer).
  2. `Lighting` with `BloomEffect`, `ColorCorrectionEffect`, `Atmosphere`, and dramatic Roblox lighting.
  3. `StarterGui.JumpTaxHudGui` built to the Golden Laws of Roblox UI (`UDim2.fromScale`, `UIAspectRatioConstraint`,
     `AnchorPoint = 0.5, 0.5`, `UICorner`, `UIStroke`).
  4. `StarterPlayer.StarterPlayerScripts.StorytimeDirector` (`LocalScript`) that disables default CoreGui, locks
     `workspace.CurrentCamera.CameraType = Enum.CameraType.Scriptable`, and drives all 12 camera cuts, R6 limb
     animations, Gravity Coil launch, Tax Bot laser scan, Admin Ban Hammer slam, Zero-G float, and ForgeGUI HUD
     in real time inside Roblox Studio!
"""

import os
import json
import math
import html

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_RBXLX = os.path.join(BASE, "JumpTaxStorytime.rbxlx")

_ref_counter = 0


def next_ref() -> str:
    global _ref_counter
    _ref_counter += 1
    return f"RBX{_ref_counter:05d}"


def hex_to_rgb01(h: str):
    h = h.lstrip("#")
    return (int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0)


def cframe_xml(x, y, z, rx_deg=0.0, ry_deg=0.0, rz_deg=0.0, name="CFrame") -> str:
    rx, ry, rz = math.radians(rx_deg), math.radians(ry_deg), math.radians(rz_deg)
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    # Rz * Ry * Rx
    r00 = cz * cy
    r01 = cz * sy * sx - sz * cx
    r02 = cz * sy * cx + sz * sx
    r10 = sz * cy
    r11 = sz * sy * sx + cz * cx
    r12 = sz * sy * cx - cz * sx
    r20 = -sy
    r21 = cy * sx
    r22 = cy * cx
    return f"""<CoordinateFrame name="{name}">
        <X>{x:.4f}</X><Y>{y:.4f}</Y><Z>{z:.4f}</Z>
        <R00>{r00:.6f}</R00><R01>{r01:.6f}</R01><R02>{r02:.6f}</R02>
        <R10>{r10:.6f}</R10><R11>{r11:.6f}</R11><R12>{r12:.6f}</R12>
        <R20>{r20:.6f}</R20><R21>{r21:.6f}</R21><R22>{r22:.6f}</R22>
      </CoordinateFrame>"""


def part_xml(
    name: str,
    pos,
    size,
    color_hex: str,
    rot=(0.0, 0.0, 0.0),
    material_token: int = 256,  # 256=Plastic (shows studs!), 272=SmoothPlastic, 288=Neon
    top_studs: bool = True,
    shape_token: int = 1,       # 1=Block, 0=Ball, 2=Cylinder
    transparency: float = 0.0,
    children_xml: str = "",
) -> str:
    r, g, b = hex_to_rgb01(color_hex)
    top_surf = 1 if top_studs else 0  # 1 = Studs, 0 = Smooth
    return f"""<Item class="Part" referent="{next_ref()}">
      <Properties>
        <string name="Name">{html.escape(name)}</string>
        <bool name="Anchored">true</bool>
        <bool name="CanCollide">true</bool>
        <bool name="Locked">false</bool>
        <token name="shape">{shape_token}</token>
        <token name="Material">{material_token}</token>
        <token name="TopSurface">{top_surf}</token>
        <token name="BottomSurface">0</token>
        <token name="FrontSurface">0</token>
        <token name="BackSurface">0</token>
        <token name="LeftSurface">0</token>
        <token name="RightSurface">0</token>
        <float name="Transparency">{transparency:.3f}</float>
        <Color3 name="Color"><R>{r:.5f}</R><G>{g:.5f}</G><B>{b:.5f}</B></Color3>
        <Vector3 name="size"><X>{size[0]:.4f}</X><Y>{size[1]:.4f}</Y><Z>{size[2]:.4f}</Z></Vector3>
        {cframe_xml(pos[0], pos[1], pos[2], rot[0], rot[1], rot[2])}
      </Properties>
      {children_xml}
    </Item>"""


def point_light_xml(color_hex: str, brightness: float = 2.5, range_studs: float = 28.0) -> str:
    r, g, b = hex_to_rgb01(color_hex)
    return f"""<Item class="PointLight" referent="{next_ref()}">
      <Properties>
        <string name="Name">PointLight</string>
        <bool name="Enabled">true</bool>
        <bool name="Shadows">true</bool>
        <float name="Brightness">{brightness:.3f}</float>
        <float name="Range">{range_studs:.3f}</float>
        <Color3 name="Color"><R>{r:.5f}</R><G>{g:.5f}</G><B>{b:.5f}</B></Color3>
      </Properties>
    </Item>"""


def billboard_tag_xml(text: str, text_hex: str = "#FFE600", bg_hex: str = "#10121C", offset_y: float = 3.2) -> str:
    tr, tg, tb = hex_to_rgb01(text_hex)
    br, bg, bb = hex_to_rgb01(bg_hex)
    return f"""<Item class="BillboardGui" referent="{next_ref()}">
      <Properties>
        <string name="Name">OverheadTag</string>
        <bool name="Active">true</bool>
        <bool name="AlwaysOnTop">true</bool>
        <bool name="Enabled">true</bool>
        <UDim2 name="Size"><XS>0</XS><XO>220</XO><YS>0</YS><YO>46</YO></UDim2>
        <Vector3 name="StudsOffset"><X>0</X><Y>{offset_y:.2f}</Y><Z>0</Z></Vector3>
      </Properties>
      <Item class="Frame" referent="{next_ref()}">
        <Properties>
          <string name="Name">Pill</string>
          <UDim2 name="Size"><XS>1</XS><XO>0</XO><YS>1</YS><YO>0</YO></UDim2>
          <Color3 name="BackgroundColor3"><R>{br:.4f}</R><G>{bg:.4f}</G><B>{bb:.4f}</B></Color3>
          <float name="BackgroundTransparency">0.12</float>
          <int name="BorderSizePixel">0</int>
        </Properties>
        <Item class="UICorner" referent="{next_ref()}">
          <Properties><UDim name="CornerRadius"><S>0</S><O>12</O></UDim></Properties>
        </Item>
        <Item class="UIStroke" referent="{next_ref()}">
          <Properties>
            <Color3 name="Color"><R>{tr:.4f}</R><G>{tg:.4f}</G><B>{tb:.4f}</B></Color3>
            <float name="Thickness">2.5</float>
          </Properties>
        </Item>
        <Item class="TextLabel" referent="{next_ref()}">
          <Properties>
            <string name="Name">Label</string>
            <UDim2 name="Size"><XS>1</XS><XO>-12</XO><YS>1</YS><YO>-6</YO></UDim2>
            <UDim2 name="Position"><XS>0</XS><XO>6</XO><YS>0</YS><YO>3</YO></UDim2>
            <float name="BackgroundTransparency">1</float>
            <string name="Text">{html.escape(text)}</string>
            <Color3 name="TextColor3"><R>{tr:.4f}</R><G>{tg:.4f}</G><B>{tb:.4f}</B></Color3>
            <bool name="TextScaled">true</bool>
            <token name="Font">19</token>
          </Properties>
        </Item>
      </Item>
    </Item>"""


def r6_avatar_xml(
    name: str,
    root_pos,
    rot_y_deg: float,
    torso_hex: str,
    legs_hex: str,
    arms_hex: str,
    head_hex: str = "#F5CD30",
    role: str = "hero",
    overhead_text: str = None,
    overhead_col: str = "#FFE600",
) -> str:
    """
    Builds an authentic Roblox R6 Character Model in Roblox Studio coordinates (Y is up, 1 stud = 1 unit, R6 height = 5 studs):
      - Left Leg:  (-0.5, 1.0, 0), size (1, 2, 1)
      - Right Leg: ( 0.5, 1.0, 0), size (1, 2, 1)
      - Torso:     ( 0.0, 3.0, 0), size (2, 2, 1)
      - Left Arm:  (-1.5, 3.0, 0), size (1, 2, 1)
      - Right Arm: ( 1.5, 3.0, 0), size (1, 2, 1)
      - Head:      ( 0.0, 4.5, 0), size (2, 1, 1) + SpecialMesh Head (Scale 1.25, 1.25, 1.25) + face Decal
    """
    ox, oy, oz = root_pos
    rad = math.radians(rot_y_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)

    def world_pt(lx, ly, lz):
        wx = ox + lx * cos_a + lz * sin_a
        wy = oy + ly
        wz = oz - lx * sin_a + lz * cos_a
        return (wx, wy, wz)

    head_children = f"""
      <Item class="SpecialMesh" referent="{next_ref()}">
        <Properties>
          <string name="Name">Mesh</string>
          <token name="MeshType">0</token>
          <Vector3 name="Scale"><X>1.25</X><Y>1.25</Y><Z>1.25</Z></Vector3>
        </Properties>
      </Item>
      <Item class="Decal" referent="{next_ref()}">
        <Properties>
          <string name="Name">face</string>
          <token name="Face">5</token>
          <Content name="Texture"><url>rbxasset://textures/face.png</url></Content>
        </Properties>
      </Item>
    """
    if overhead_text:
        head_children += billboard_tag_xml(overhead_text, text_hex=overhead_col, offset_y=2.8)

    extras = ""
    if role == "hero":
        # Spiky brown hair block on top of head
        extras += part_xml("Hair", world_pt(0.0, 5.15, 0.0), (1.35, 0.45, 1.35), "#4A2E1E", rot=(0, rot_y_deg, 0), material_token=272, top_studs=False)
    elif role == "dominus":
        # Golden Dominus Hood + Glowing Neon Gold Winged Horns
        extras += part_xml("DominusHood", world_pt(0.0, 4.65, 0.05), (1.55, 1.45, 1.45), "#E8B938", rot=(0, rot_y_deg, 0), material_token=272, top_studs=False)
        extras += part_xml("HornL", world_pt(-0.85, 5.25, 0.0), (0.35, 0.95, 0.35), "#FFD838", rot=(0, rot_y_deg, 28), material_token=288, top_studs=False)
        extras += part_xml("HornR", world_pt( 0.85, 5.25, 0.0), (0.35, 0.95, 0.35), "#FFD838", rot=(0, rot_y_deg, -28), material_token=288, top_studs=False)
    elif role == "noob":
        # Glowing Neon Cyan Gravity Coil attached to Right Arm
        for c_i in range(4):
            extras += part_xml(
                f"GravityCoil_{c_i}",
                world_pt(1.5, 2.3 + c_i * 0.35, -0.55),
                (0.75, 0.22, 0.75),
                "#28F0FF",
                rot=(15, rot_y_deg, 0),
                material_token=288,
                top_studs=False,
                children_xml=point_light_xml("#28F0FF", 2.0, 14.0) if c_i == 1 else "",
            )
    elif role == "admin":
        # Glowing Admin Crown + Giant Red/Gold Ban Hammer
        extras += part_xml("AdminCrown", world_pt(0.0, 5.3, 0.0), (1.4, 0.5, 1.4), "#FFD838", rot=(0, rot_y_deg, 0), material_token=288, top_studs=False)
        extras += part_xml("BanHammerShaft", world_pt(1.6, 3.2, -1.2), (0.35, 3.6, 0.35), "#1A1C24", rot=(55, rot_y_deg, 0), material_token=272, top_studs=False)
        extras += part_xml(
            "BanHammerHead",
            world_pt(1.6, 4.4, -2.3),
            (1.8, 1.1, 1.1),
            "#FF2A2A",
            rot=(55, rot_y_deg, 0),
            material_token=288,
            top_studs=False,
            children_xml=point_light_xml("#FF2A2A", 3.0, 18.0),
        )

    parts = [
        part_xml("Torso", world_pt(0.0, 3.0, 0.0), (2.0, 2.0, 1.0), torso_hex, rot=(0, rot_y_deg, 0), material_token=272, top_studs=False),
        part_xml("Left Leg", world_pt(-0.5, 1.0, 0.0), (1.0, 2.0, 1.0), legs_hex, rot=(0, rot_y_deg, 0), material_token=272, top_studs=False),
        part_xml("Right Leg", world_pt(0.5, 1.0, 0.0), (1.0, 2.0, 1.0), legs_hex, rot=(0, rot_y_deg, 0), material_token=272, top_studs=False),
        part_xml("Left Arm", world_pt(-1.5, 3.0, 0.0), (1.0, 2.0, 1.0), arms_hex, rot=(0, rot_y_deg, 0), material_token=272, top_studs=False),
        part_xml("Right Arm", world_pt(1.5, 3.0, 0.0), (1.0, 2.0, 1.0), arms_hex, rot=(0, rot_y_deg, 0), material_token=272, top_studs=False),
        part_xml("Head", world_pt(0.0, 4.5, 0.0), (2.0, 1.0, 1.0), head_hex, rot=(0, rot_y_deg, 0), material_token=272, top_studs=False, children_xml=head_children),
        extras,
    ]
    return f"""<Item class="Model" referent="{next_ref()}">
      <Properties><string name="Name">{html.escape(name)}</string></Properties>
      {''.join(parts)}
    </Item>"""


def build_workspace_sets_xml() -> str:
    items = []

    # =========================================================================
    # SET 0 (X = 0): LAVA OBBY SPAWN ROOM ("In this world, 1 jump = 100 Robux")
    # =========================================================================
    s0 = []
    s0.append(part_xml("ObbyFloor", (0, -0.5, 0), (36, 1, 36), "#232733", top_studs=True))
    s0.append(part_xml("BackWall", (0, 10, -16), (36, 22, 1), "#182238", top_studs=False))
    for ix in range(-3, 4):
        for iz in range(-3, 3):
            if ix == 0 and iz == 0:
                continue
            col = "#FF2A2A" if (ix + iz) % 2 == 0 else "#FF7B1A"
            light = point_light_xml(col, 1.8, 14.0) if (abs(ix) <= 1 and abs(iz) <= 1) else ""
            s0.append(part_xml(f"LavaKillBrick_{ix}_{iz}", (ix * 4.5, 0.2, iz * 4.5), (3.9, 0.6, 3.9), col, material_token=288, top_studs=True, children_xml=light))

    s0.append(part_xml("SafeSpawnBlock", (0, 0.5, 0), (3.8, 1.0, 3.8), "#787F8C", top_studs=True))
    for idx, (gx, gy, gz) in enumerate([(-6.5, 2.5, -9.0), (0.0, 4.0, -11.0), (6.5, 2.5, -9.0)]):
        s0.append(part_xml(f"ObbyGoal_{idx}", (gx, gy, gz), (4.5, 1.0, 4.5), "#28B458", top_studs=True))

    s0.append(r6_avatar_xml("Hero_Obby", (0, 1.0, 0), 0.0, "#1E66D0", "#232733", "#F5CD30", role="hero", overhead_text="BALANCE: R$ 0 (1 JUMP = -R$ 100)", overhead_col="#FF3344"))
    items.append(f'<Item class="Model" referent="{next_ref()}"><Properties><string name="Name">Set0_LavaObby</string></Properties>{"".join(s0)}</Item>')

    # =========================================================================
    # SET 1 (X = 200): ROBLOX HIGH HALLWAY (Dominus Kids Bunny-Hopping)
    # =========================================================================
    ox = 200.0
    s1 = []
    s1.append(part_xml("HallFloor", (ox, -0.5, 0), (42, 1, 28), "#787F8C", top_studs=True))
    s1.append(part_xml("HallWall", (ox, 9, -10), (42, 20, 1), "#182238", top_studs=False))
    for i, lx in enumerate(range(-15, 16, 3)):
        lcol = "#1E66D0" if i % 2 == 0 else "#E8B938"
        s1.append(part_xml(f"Locker_{i}", (ox + lx, 3.5, -8.5), (2.6, 7.0, 1.8), lcol, material_token=272, top_studs=False))

    s1.append(r6_avatar_xml("Hero_Hall", (ox - 5.5, 0.0, 1.5), -25.0, "#1E66D0", "#232733", "#F5CD30", role="hero", overhead_text="R$ 0 (WALKING SLOWLY)", overhead_col="#FFE600"))
    s1.append(r6_avatar_xml("Noob_Hall", (ox - 9.0, 0.0, -0.5), -20.0, "#0D69AC", "#4B974B", "#F5CD30", role="noob"))
    s1.append(r6_avatar_xml("Dominus_Rich1", (ox + 1.5, 2.2, -1.0), 15.0, "#E8B938", "#1A1C24", "#E8B938", head_hex="#1A1C24", role="dominus", overhead_text="R$ 999,999 (-R$ 100/HOP)", overhead_col="#22EE66"))
    s1.append(r6_avatar_xml("Dominus_Rich2", (ox + 6.0, 1.4, -2.5), -15.0, "#1A1C24", "#E8B938", "#E8B938", head_hex="#1A1C24", role="dominus"))
    items.append(f'<Item class="Model" referent="{next_ref()}"><Properties><string name="Name">Set1_SchoolHallway</string></Properties>{"".join(s1)}</Item>')

    # =========================================================================
    # SET 2 (X = 400): CLASSROOM FLOOR IS LAVA & GRAVITY COIL LAUNCH
    # =========================================================================
    ox = 400.0
    s2 = []
    s2.append(part_xml("LavaBase", (ox, -0.5, 0), (38, 1, 30), "#FF2A2A", material_token=288, top_studs=True))
    for ix in range(-2, 3):
        for iz in range(-2, 2):
            col = "#FF7B1A" if (ix + iz) % 2 == 0 else "#232733"
            mat = 288 if (ix + iz) % 2 == 0 else 256
            s2.append(part_xml(f"CrackTile_{ix}_{iz}", (ox + ix * 5.2, 0.1, iz * 4.8), (4.2, 0.6, 4.0), col, material_token=mat, top_studs=True))

    s2.append(part_xml("SafeGreenPlatform", (ox + 6.5, 1.8, -3.5), (7.5, 3.6, 6.5), "#28B458", top_studs=True))
    s2.append(r6_avatar_xml("Teacher_Platform", (ox + 6.5, 3.6, -3.5), 22.0, "#4A2E1E", "#232733", "#F5CD30", role="teacher", overhead_text="TEACHER: JUMP TO SAFETY!", overhead_col="#FFE600"))

    s2.append(part_xml("HeroDeskIsland", (ox - 2.5, 0.8, 1.0), (8.2, 1.6, 5.2), "#787F8C", top_studs=True))
    s2.append(r6_avatar_xml("Noob_CoilFriend", (ox - 4.8, 1.6, 1.0), -28.0, "#0D69AC", "#4B974B", "#F5CD30", role="noob", overhead_text="FREE GRAVITY COIL!", overhead_col="#28F0FF"))
    s2.append(r6_avatar_xml("Hero_CoilLaunch", (ox - 0.8, 1.6, 1.0), 10.0, "#1E66D0", "#232733", "#F5CD30", role="hero", overhead_text="COIL LAUNCH: 42x JUMPS!", overhead_col="#FF3344"))

    s2.append(part_xml("ShatteredRoofL", (ox - 7.0, 12.5, 0.0), (8.5, 1.2, 10.0), "#232733", top_studs=True))
    s2.append(part_xml("ShatteredRoofR", (ox + 6.2, 12.5, 0.0), (8.5, 1.2, 10.0), "#232733", top_studs=True))
    items.append(f'<Item class="Model" referent="{next_ref()}"><Properties><string name="Name">Set2_ClassroomCoil</string></Properties>{"".join(s2)}</Item>')

    # =========================================================================
    # SET 3 (X = 600): SKY AIRTIME TAXI-METER & ROBLOX TAX BOT
    # =========================================================================
    ox = 600.0
    s3 = []
    s3.append(part_xml("StudRulerTower", (ox + 5.0, 9.0, -2.5), (2.2, 28.0, 2.2), "#232733", top_studs=False))
    for t_i in range(10):
        tcol = "#FF2A2A" if t_i % 2 == 0 else "#FFD838"
        s3.append(part_xml(f"StudTick_{t_i}", (ox + 3.5, -1.5 + t_i * 2.4, -2.5), (1.5, 0.5, 0.8), tcol, material_token=288, top_studs=False))

    s3.append(r6_avatar_xml("Hero_Airborne", (ox - 1.2, 4.0, 0.0), 8.0, "#1E66D0", "#232733", "#F5CD30", role="hero", overhead_text="DEBT: -R$ 4,200 (42 JUMPS)", overhead_col="#FF3344"))
    s3.append(part_xml("TaxBotCore", (ox + 2.6, 7.2, 0.5), (2.4, 2.4, 2.4), "#1A1C24", shape_token=0, material_token=272, top_studs=False))
    s3.append(part_xml("TaxBotRing", (ox + 2.6, 7.2, 0.5), (3.4, 0.45, 3.4), "#FFD838", material_token=288, top_studs=False, children_xml=point_light_xml("#FFD838", 2.5, 18.0)))
    s3.append(part_xml("TaxBotLaser", (ox + 0.6, 7.0, 0.2), (3.8, 0.28, 0.28), "#FF2A2A", material_token=288, top_studs=False, children_xml=point_light_xml("#FF2A2A", 3.0, 16.0)))
    items.append(f'<Item class="Model" referent="{next_ref()}"><Properties><string name="Name">Set3_SkyTaxBot</string></Properties>{"".join(s3)}</Item>')

    # =========================================================================
    # SET 4 (X = 800): ADMIN GRAVITY BAN & ZERO-G FREE FLOAT
    # =========================================================================
    ox = 800.0
    s4 = []
    s4.append(part_xml("AdminFloor", (ox, -0.5, 0), (42, 1, 28), "#787F8C", top_studs=True))
    s4.append(part_xml("AdminWall", (ox, 9, -10), (42, 20, 1), "#182238", top_studs=False))
    s4.append(part_xml("BanAnvilPedestal", (ox - 2.8, 1.2, -1.0), (3.2, 2.4, 2.6), "#FFD838", material_token=288, top_studs=True, children_xml=point_light_xml("#FFD838", 2.5, 16.0)))
    s4.append(r6_avatar_xml("Admin_Character", (ox - 2.8, 0.0, -3.2), 0.0, "#1A1C24", "#232733", "#E8B938", role="admin", overhead_text="ADMIN: GRAVITY BANNED!", overhead_col="#FFD838"))
    s4.append(r6_avatar_xml("Dominus_Stunned", (ox + 5.8, 0.0, -2.5), 25.0, "#E8B938", "#1A1C24", "#E8B938", head_hex="#1A1C24", role="dominus"))
    s4.append(r6_avatar_xml("Hero_ZeroGFloat", (ox + 1.0, 2.6, 0.5), 0.0, "#1E66D0", "#232733", "#F5CD30", role="hero", overhead_text="FLOAT TO CLASS: R$ 0 (FREE!)", overhead_col="#22EE66"))
    s4.append(part_xml("ZeroGRingL", (ox + 0.5, 2.5, 0.5), (1.5, 0.25, 1.5), "#28F0FF", material_token=288, top_studs=False, children_xml=point_light_xml("#28F0FF", 2.5, 15.0)))
    s4.append(part_xml("ZeroGRingR", (ox + 1.5, 2.5, 0.5), (1.5, 0.25, 1.5), "#28F0FF", material_token=288, top_studs=False))
    items.append(f'<Item class="Model" referent="{next_ref()}"><Properties><string name="Name">Set4_AdminFloat</string></Properties>{"".join(s4)}</Item>')

    return "\n".join(items)


def build_director_localscript_xml(words_data: dict) -> str:
    """
    Client Cutscene Director LocalScript:
    - Disables Roblox CoreGui clutter
    - Builds the ForgeGUI Top HUD Pill + Storytime 8sb2R11FeVw Bottom Pop-Caption Pill
    - Drives `workspace.CurrentCamera` smoothly through all 12 shots across Sets 0..4
    - Animates R6 avatars (panic arms, Dominus bunny-hops, Gravity Coil launch, Airborne Tax Bot scan, Zero-G float)
    """
    words_json_str = json.dumps(words_data["words"])
    secs_json_str = json.dumps(words_data["sections"])

    luau_code = f"""-- StorytimeDirector.client.lua — Full Roblox Studio Cutscene, Camera, Animation & ForgeGUI Caption Engine (< 45s)
local RunService = game:GetService("RunService")
local StarterGui = game:GetService("StarterGui")
local TweenService = game:GetService("TweenService")
local Players = game:GetService("Players")
local HttpService = game:GetService("HttpService")
local UserInputService = game:GetService("UserInputService")
local CoreGui = game:GetService("CoreGui")

pcall(function()
    StarterGui:SetCoreGuiEnabled(Enum.CoreGuiType.All, false)
end)

local WORDS = HttpService:JSONDecode([=[{words_json_str}]=])
local SECTIONS = HttpService:JSONDecode([=[{secs_json_str}]=])

-- Build Chunks (2-3 words per 8sb2R11FeVw black-bg pill)
local CHUNKS = {{}}
do
    local cur = {{}}
    for _, w in ipairs(WORDS) do
        if #cur > 0 and (w.s - cur[#cur].e) > 0.24 then
            table.insert(CHUNKS, cur)
            cur = {{}}
        end
        table.insert(cur, w)
        local lastChar = string.sub(w.w, -1)
        if #cur >= 3 or lastChar == "." or lastChar == "!" or lastChar == "?" or (lastChar == "," and #cur >= 2) then
            table.insert(CHUNKS, cur)
            cur = {{}}
        end
    end
    if #cur > 0 then
        table.insert(CHUNKS, cur)
    end
end

-- Mount ScreenGui in CoreGui (for Studio Edit-Mode Plugin) or PlayerGui (for Playtest)
local guiParent = CoreGui
pcall(function()
    if Players.LocalPlayer and Players.LocalPlayer:FindFirstChild("PlayerGui") then
        guiParent = Players.LocalPlayer.PlayerGui
    end
end)
local oldGui = guiParent:FindFirstChild("JumpTaxHudGui")
if oldGui then oldGui:Destroy() end

local sgui = Instance.new("ScreenGui")
sgui.Name = "JumpTaxHudGui"
sgui.IgnoreGuiInset = true
sgui.ResetOnSpawn = false
sgui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
sgui.DisplayOrder = 100
sgui.Parent = guiParent

-- Top ForgeGUI Live Robux Balance / World Rule Pill
local topPill = Instance.new("Frame")
topPill.Name = "TopHudPill"
topPill.AnchorPoint = Vector2.new(0.5, 0.5)
topPill.Position = UDim2.fromScale(0.5, 0.12)
topPill.Size = UDim2.fromScale(0.76, 0.065)
topPill.BackgroundColor3 = Color3.fromRGB(16, 18, 28)
topPill.BackgroundTransparency = 0.08
topPill.BorderSizePixel = 0
topPill.Parent = sgui

local topCorner = Instance.new("UICorner")
topCorner.CornerRadius = UDim.new(0, 16)
topCorner.Parent = topPill

local topStroke = Instance.new("UIStroke")
topStroke.Thickness = 3
topStroke.Color = Color3.fromRGB(255, 230, 0)
topStroke.Parent = topPill

local topLabel = Instance.new("TextLabel")
topLabel.Name = "HudText"
topLabel.AnchorPoint = Vector2.new(0.5, 0.5)
topLabel.Position = UDim2.fromScale(0.5, 0.5)
topLabel.Size = UDim2.fromScale(0.92, 0.76)
topLabel.BackgroundTransparency = 1
topLabel.Font = Enum.Font.GothamBlack
topLabel.TextScaled = true
topLabel.TextColor3 = Color3.fromRGB(255, 230, 0)
topLabel.Text = "WORLD RULE: 1 JUMP = -R$ 100"
topLabel.Parent = topPill

-- Bottom 8sb2R11FeVw Black-BG Pop-Caption Pill
local capPill = Instance.new("Frame")
capPill.Name = "SubtitlePill"
capPill.AnchorPoint = Vector2.new(0.5, 0.5)
capPill.Position = UDim2.fromScale(0.5, 0.72)
capPill.Size = UDim2.fromScale(0.68, 0.085)
capPill.BackgroundColor3 = Color3.fromRGB(8, 8, 10)
capPill.BackgroundTransparency = 0.08
capPill.BorderSizePixel = 0
capPill.Parent = sgui

local capCorner = Instance.new("UICorner")
capCorner.CornerRadius = UDim.new(0, 16)
capCorner.Parent = capPill

local capLabel = Instance.new("TextLabel")
capLabel.Name = "CapText"
capLabel.AnchorPoint = Vector2.new(0.5, 0.5)
capLabel.Position = UDim2.fromScale(0.5, 0.5)
capLabel.Size = UDim2.fromScale(0.92, 0.78)
capLabel.BackgroundTransparency = 1
capLabel.Font = Enum.Font.GothamBlack
capLabel.RichText = true
capLabel.TextScaled = true
capLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
capLabel.Text = ""
capLabel.Parent = capPill

-- 12 Multi-Angle Storytime Camera Shots across Sets 0..4
local b1_s, b1_e = SECTIONS.beat1.start, SECTIONS.beat1["end"]
local b2_s, b2_e = SECTIONS.beat2.start, SECTIONS.beat2["end"]
local b3_s, b3_e = SECTIONS.beat3.start, SECTIONS.beat3["end"]
local b4_s, b4_e = SECTIONS.beat4.start, SECTIONS.beat4["end"]
local b5_s, b5_e = SECTIONS.beat5.start, SECTIONS.beat5["end"]
local b6_s, b6_e = SECTIONS.beat6.start, SECTIONS.beat6["end"] + 0.45

local SHOTS = {{
    {{ s = 0.0, e = b1_s + (b1_e - b1_s)*0.32, p0 = Vector3.new(0, 6.8, 13.5), p1 = Vector3.new(0, 6.2, 11.2), t0 = Vector3.new(0, 4.0, 0), t1 = Vector3.new(0, 4.2, 0), fov = 55, roll = 0 }},
    {{ s = b1_s + (b1_e - b1_s)*0.32, e = b1_s + (b1_e - b1_s)*0.62, p0 = Vector3.new(1.0, 5.8, 7.5), p1 = Vector3.new(-0.5, 5.9, 6.4), t0 = Vector3.new(0, 5.3, 0), t1 = Vector3.new(0, 5.4, 0), fov = 42, roll = 4.5 }},
    {{ s = b1_s + (b1_e - b1_s)*0.62, e = b1_e, p0 = Vector3.new(-6.0, 7.2, 10.8), p1 = Vector3.new(5.2, 6.2, 9.6), t0 = Vector3.new(0, 3.8, -0.3), t1 = Vector3.new(0, 4.0, -0.5), fov = 58, roll = -7.0 }},

    {{ s = b2_s, e = b2_s + (b2_e - b2_s)*0.54, p0 = Vector3.new(193.5, 5.6, 13.8), p1 = Vector3.new(198.5, 5.8, 12.5), t0 = Vector3.new(198.5, 4.4, -0.8), t1 = Vector3.new(201.5, 4.6, -1.2), fov = 52, roll = 0 }},
    {{ s = b2_s + (b2_e - b2_s)*0.54, e = b2_e, p0 = Vector3.new(203.8, 2.8, 9.2), p1 = Vector3.new(201.0, 3.2, 8.2), t0 = Vector3.new(202.0, 5.4, -1.5), t1 = Vector3.new(202.5, 5.8, -1.5), fov = 62, roll = 5.0 }},

    {{ s = b3_s, e = b3_s + (b3_e - b3_s)*0.55, p0 = Vector3.new(394.0, 7.0, 13.5), p1 = Vector3.new(398.0, 6.4, 11.8), t0 = Vector3.new(401.0, 4.4, -1.0), t1 = Vector3.new(402.0, 4.8, -1.6), fov = 58, roll = -5.5 }},
    {{ s = b3_s + (b3_e - b3_s)*0.55, e = b3_e, p0 = Vector3.new(397.5, 6.8, 8.8), p1 = Vector3.new(399.2, 6.9, 7.5), t0 = Vector3.new(399.2, 6.2, 0.8), t1 = Vector3.new(399.2, 6.3, 0.8), fov = 44, roll = 6.5 }},

    {{ s = b4_s, e = b4_s + (b4_e - b4_s)*0.46, p0 = Vector3.new(393.5, 6.1, 10.2), p1 = Vector3.new(396.0, 6.3, 9.0), t0 = Vector3.new(397.2, 5.5, 0.8), t1 = Vector3.new(398.2, 5.7, 0.8), fov = 52, roll = 0 }},
    {{ s = b4_s + (b4_e - b4_s)*0.46, e = b4_e, p0 = Vector3.new(399.2, 5.6, 13.2), p1 = Vector3.new(399.2, 13.8, 14.8), t0 = Vector3.new(399.2, 6.1, 0.8), t1 = Vector3.new(399.2, 16.5, 0.8), fov = 64, roll = -8.0 }},

    {{ s = b5_s, e = b5_s + (b5_e - b5_s)*0.50, p0 = Vector3.new(599.6, 7.4, 13.2), p1 = Vector3.new(600.4, 10.6, 12.4), t0 = Vector3.new(600.6, 7.0, -0.4), t1 = Vector3.new(600.8, 10.2, -0.4), fov = 56, roll = 0 }},
    {{ s = b5_s + (b5_e - b5_s)*0.50, e = b5_e, p0 = Vector3.new(597.0, 11.2, 10.2), p1 = Vector3.new(598.4, 13.8, 9.0), t0 = Vector3.new(599.6, 10.6, 0.0), t1 = Vector3.new(599.8, 13.2, 0.0), fov = 46, roll = 8.5 }},

    {{ s = b6_s, e = b6_s + (b6_e - b6_s)*0.45, p0 = Vector3.new(794.0, 5.5, 12.4), p1 = Vector3.new(796.5, 5.7, 10.8), t0 = Vector3.new(797.5, 4.4, -1.6), t1 = Vector3.new(798.8, 4.6, -1.2), fov = 56, roll = -4.0 }},
    {{ s = b6_s + (b6_e - b6_s)*0.45, e = b6_e, p0 = Vector3.new(797.5, 5.5, 13.2), p1 = Vector3.new(802.5, 5.7, 12.0), t0 = Vector3.new(799.2, 4.4, -0.4), t1 = Vector3.new(803.2, 4.6, -0.6), fov = 56, roll = 0 }},
}}

local function smootherstep(u)
    u = math.clamp(u, 0, 1)
    return u * u * u * (u * (u * 6 - 15) + 10)
end

local t0 = os.clock()
local DURATION = b6_e

UserInputService.InputBegan:Connect(function(inp)
    if inp.KeyCode == Enum.KeyCode.F8 or inp.KeyCode == Enum.KeyCode.R then
        t0 = os.clock()
    end
end)

-- Cache base CFrames of animated parts in Workspace for smooth 60fps in-Studio R6 acting!
local BASE_CF = {{}}
local function getBaseCF(inst)
    if not inst then return nil end
    if not BASE_CF[inst] then
        BASE_CF[inst] = inst.CFrame
    end
    return BASE_CF[inst]
end

local function animateR6Model(model, t, mode)
    if not model then return end
    local torso = model:FindFirstChild("Torso")
    local head = model:FindFirstChild("Head")
    local la = model:FindFirstChild("Left Arm")
    local ra = model:FindFirstChild("Right Arm")
    local ll = model:FindFirstChild("Left Leg")
    local rl = model:FindFirstChild("Right Leg")
    if not torso then return end

    local baseT = getBaseCF(torso)
    local dy = 0
    local dz = 0
    local tiltZ = 0
    local s = math.sin(t * 8.0)

    if mode == "panic" then
        dy = math.abs(math.sin(t * 9.0)) * 0.25
        s = math.sin(t * 14.0)
    elseif mode == "hop" then
        dy = math.abs(math.sin(t * 7.5)) * 3.2
        dz = -math.sin(t * 1.8) * 2.5
    elseif mode == "walk" then
        dy = math.abs(math.sin(t * 6.0)) * 0.15
        dz = -math.sin(t * 1.5) * 1.8
    elseif mode == "coil_launch" then
        local mid4 = b4_s + (b4_e - b4_s) * 0.45
        if t > mid4 then
            local u = math.clamp((t - mid4) / math.max(0.1, b4_e - mid4), 0, 1)
            dy = (u ^ 1.5) * 18.0
            tiltZ = u * 0.35
        else
            dy = math.abs(math.sin(t * 8.0)) * 0.2
        end
    elseif mode == "airborne" then
        local u = math.clamp((t - b5_s) / math.max(0.1, b5_e - b5_s), 0, 1)
        dy = u * 8.5
        tiltZ = 0.18 * math.sin(t * 5.0)
        s = math.sin(t * 15.0)
    elseif mode == "zerog" then
        local u = math.clamp((t - b6_s) / math.max(0.1, b6_e - b6_s), 0, 1)
        dy = 1.4 + 0.55 * math.sin(t * 4.0)
        dz = (u - 0.5) * 5.0
        tiltZ = 0.22 * math.sin(t * 3.0)
    end

    local offsetCF = CFrame.new(0, dy, dz) * CFrame.Angles(0, 0, tiltZ)
    torso.CFrame = baseT * offsetCF

    for _, child in ipairs(model:GetChildren()) do
        if child:IsA("BasePart") and child ~= torso then
            local bcf = getBaseCF(child)
            local rel = baseT:ToObjectSpace(bcf)
            if child == la then
                local ang = (mode == "panic" or mode == "coil_launch" or mode == "airborne") and math.rad(145 + 25*s) or (0.65 * s)
                child.CFrame = torso.CFrame * rel * CFrame.Angles(ang, 0, 0)
            elseif child == ra then
                local ang = (mode == "panic" or mode == "coil_launch" or mode == "airborne") and math.rad(145 - 25*s) or (-0.65 * s)
                child.CFrame = torso.CFrame * rel * CFrame.Angles(ang, 0, 0)
            elseif child == ll then
                child.CFrame = torso.CFrame * rel * CFrame.Angles(-0.55 * s, 0, 0)
            elseif child == rl then
                child.CFrame = torso.CFrame * rel * CFrame.Angles(0.55 * s, 0, 0)
            else
                child.CFrame = torso.CFrame * rel
            end
        end
    end
end

RunService.RenderStepped:Connect(function()
    if not workspace:FindFirstChild("Set0_LavaObby") then
        sgui.Enabled = false
        return
    end
    sgui.Enabled = true
    local cam = workspace.CurrentCamera
    if not cam then return end
    cam.CameraType = Enum.CameraType.Scriptable

    local t = (os.clock() - t0) % DURATION

    -- Animate R6 characters across all 5 sets inside Roblox Studio!
    local s0 = workspace:FindFirstChild("Set0_LavaObby")
    if s0 then animateR6Model(s0:FindFirstChild("Hero_Obby"), t, "panic") end

    local s1 = workspace:FindFirstChild("Set1_SchoolHallway")
    if s1 then
        animateR6Model(s1:FindFirstChild("Hero_Hall"), t, "walk")
        animateR6Model(s1:FindFirstChild("Noob_Hall"), t + 0.4, "walk")
        animateR6Model(s1:FindFirstChild("Dominus_Rich1"), t, "hop")
        animateR6Model(s1:FindFirstChild("Dominus_Rich2"), t + 0.35, "hop")
    end

    local s2 = workspace:FindFirstChild("Set2_ClassroomCoil")
    if s2 then
        animateR6Model(s2:FindFirstChild("Teacher_Platform"), t, "panic")
        animateR6Model(s2:FindFirstChild("Noob_CoilFriend"), t, "walk")
        animateR6Model(s2:FindFirstChild("Hero_CoilLaunch"), t, "coil_launch")
    end

    local s3 = workspace:FindFirstChild("Set3_SkyTaxBot")
    if s3 then
        animateR6Model(s3:FindFirstChild("Hero_Airborne"), t, "airborne")
        local botCore = s3:FindFirstChild("TaxBotCore")
        local botRing = s3:FindFirstChild("TaxBotRing")
        local botLaser = s3:FindFirstChild("TaxBotLaser")
        local u5 = math.clamp((t - b5_s) / math.max(0.1, b5_e - b5_s), 0, 1)
        local by = u5 * 8.5 + 0.4 * math.sin(t * 6.0)
        if botCore then botCore.CFrame = getBaseCF(botCore) + Vector3.new(0, by, 0) end
        if botRing then botRing.CFrame = (getBaseCF(botRing) + Vector3.new(0, by, 0)) * CFrame.Angles(0, t * 3.0, 0) end
        if botLaser then botLaser.CFrame = getBaseCF(botLaser) + Vector3.new(0, by, 0) end
    end

    local s4 = workspace:FindFirstChild("Set4_AdminFloat")
    if s4 then
        animateR6Model(s4:FindFirstChild("Admin_Character"), t, "panic")
        animateR6Model(s4:FindFirstChild("Dominus_Stunned"), t, "panic")
        animateR6Model(s4:FindFirstChild("Hero_ZeroGFloat"), t, "zerog")
    end

    -- 1. Camera Cut & Smootherstep Motion
    local activeShot = SHOTS[#SHOTS]
    for _, sh in ipairs(SHOTS) do
        if t >= sh.s and t <= sh.e then
            activeShot = sh
            break
        end
    end
    local u = smootherstep((t - activeShot.s) / math.max(0.01, activeShot.e - activeShot.s))
    local pos = activeShot.p0:Lerp(activeShot.p1, u)
    local tgt = activeShot.t0:Lerp(activeShot.t1, u)
    cam.FieldOfView = activeShot.fov
    cam.CFrame = CFrame.lookAt(pos, tgt) * CFrame.Angles(0, 0, math.rad(activeShot.roll))

    -- 2. Update Top ForgeGUI HUD State
    if t < 3.4 then
        topLabel.Text = "WORLD RULE: 1 JUMP = -R$ 100"
        topLabel.TextColor3 = Color3.fromRGB(255, 230, 0)
        topStroke.Color = Color3.fromRGB(255, 230, 0)
    elseif t < b2_s then
        topLabel.Text = "MY BALANCE: R$ 0 (STRANDED)"
        topLabel.TextColor3 = Color3.fromRGB(255, 65, 80)
        topStroke.Color = Color3.fromRGB(255, 65, 80)
    elseif t < b3_s then
        topLabel.Text = "DOMINUS KIDS: R$ 999,999 (-R$ 100/HOP)"
        topLabel.TextColor3 = Color3.fromRGB(34, 238, 102)
        topStroke.Color = Color3.fromRGB(34, 238, 102)
    elseif t < b4_s then
        topLabel.Text = "ALERT: FLOOR IS LAVA | BALANCE: R$ 0"
        topLabel.TextColor3 = Color3.fromRGB(255, 65, 80)
        topStroke.Color = Color3.fromRGB(255, 65, 80)
    elseif t < b4_s + 2.8 then
        topLabel.Text = "EQUIPPED: FREE GRAVITY COIL (R$ 0)"
        topLabel.TextColor3 = Color3.fromRGB(40, 240, 255)
        topStroke.Color = Color3.fromRGB(40, 240, 255)
    elseif t < b5_s then
        local jumps = math.clamp(math.floor(((t - (b4_s + 2.8)) / math.max(0.5, b5_s - (b4_s + 2.8))) * 42), 1, 42)
        topLabel.Text = string.format("COIL LAUNCH: %dx JUMPS REGISTERED!", jumps)
        topLabel.TextColor3 = Color3.fromRGB(255, 140, 40)
        topStroke.Color = Color3.fromRGB(255, 140, 40)
    elseif t < b6_s then
        local debt = math.clamp(math.floor(100 + ((t - b5_s) / math.max(0.5, (b6_s - 1.2) - b5_s)) * 4100), 100, 4200)
        topLabel.Text = string.format("AIRTIME TAX METER: -R$ %d", debt)
        topLabel.TextColor3 = Color3.fromRGB(255, 55, 70)
        topStroke.Color = Color3.fromRGB(255, 55, 70)
    else
        topLabel.Text = "GRAVITY: BANNED | FLOAT TAX: R$ 0"
        topLabel.TextColor3 = Color3.fromRGB(34, 238, 102)
        topStroke.Color = Color3.fromRGB(34, 238, 102)
    end

    -- 3. Update Bottom 8sb2R11FeVw Subtitle Pill
    local activeChunk = nil
    for _, ch in ipairs(CHUNKS) do
        if t >= (ch[1].s - 0.04) and t <= (ch[#ch].e + 0.12) then
            activeChunk = ch
            break
        end
    end
    if activeChunk then
        capPill.Visible = true
        local activeIdx = 1
        for i, w in ipairs(activeChunk) do
            if t >= (w.s - 0.02) then activeIdx = i end
        end
        local parts = {{}}
        for i, w in ipairs(activeChunk) do
            if i == activeIdx then
                table.insert(parts, '<font color="#FFE600">' .. w.w .. '</font>')
            else
                table.insert(parts, '<font color="#FFFFFF">' .. w.w .. '</font>')
            end
        end
        capLabel.Text = table.concat(parts, " ")
    else
        capPill.Visible = false
    end
end)
"""
    return f"""<Item class="LocalScript" referent="{next_ref()}">
      <Properties>
        <string name="Name">StorytimeDirector</string>
        <ProtectedString name="Source"><![CDATA[{luau_code}]]></ProtectedString>
      </Properties>
    </Item>"""


def generate_rbxlx():
    words_data = json.load(open(os.path.join(BASE, "voice", "words.json"), encoding="utf-8"))
    sets_xml = build_workspace_sets_xml()
    director_xml = build_director_localscript_xml(words_data)
    hud_rbxmx = open(os.path.join(BASE, "JumpTaxHudGui.rbxmx"), encoding="utf-8").read()
    # Extract inner <Item class="ScreenGui"...>...</Item> from JumpTaxHudGui.rbxmx
    s_idx = hud_rbxmx.find('<Item class="ScreenGui"')
    e_idx = hud_rbxmx.rfind("</Item>") + len("</Item>")
    screen_gui_xml = hud_rbxmx[s_idx:e_idx] if s_idx != -1 else ""

    rbxlx = f"""<roblox xmlns:xmime="http://www.w3.org/2005/05/xmlmime" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://www.roblox.com/roblox.xsd" version="4">
  <Meta name="ExplicitAutoJoints">true</Meta>
  <Item class="Workspace" referent="{next_ref()}">
    <Properties>
      <string name="Name">Workspace</string>
      <float name="Gravity">196.2</float>
    </Properties>
    <Item class="Camera" referent="{next_ref()}">
      <Properties>
        <string name="Name">Camera</string>
        <float name="FieldOfView">55</float>
        {cframe_xml(0.0, 6.5, 12.5, -14.0, 0.0, 0.0)}
        {cframe_xml(0.0, 4.0, 0.0, 0.0, 0.0, 0.0, name="Focus")}
      </Properties>
    </Item>
    {sets_xml}
  </Item>
  <Item class="Lighting" referent="{next_ref()}">
    <Properties>
      <string name="Name">Lighting</string>
      <Color3 name="Ambient"><R>0.18</R><G>0.20</G><B>0.28</B></Color3>
      <Color3 name="OutdoorAmbient"><R>0.28</R><G>0.32</G><B>0.42</B></Color3>
      <float name="Brightness">2.4</float>
      <float name="ClockTime">14.5</float>
      <float name="GeographicLatitude">35</float>
      <bool name="GlobalShadows">true</bool>
    </Properties>
    <Item class="BloomEffect" referent="{next_ref()}">
      <Properties>
        <string name="Name">Bloom</string>
        <bool name="Enabled">true</bool>
        <float name="Intensity">0.65</float>
        <float name="Size">24</float>
        <float name="Threshold">0.95</float>
      </Properties>
    </Item>
    <Item class="ColorCorrectionEffect" referent="{next_ref()}">
      <Properties>
        <string name="Name">ColorCorrection</string>
        <bool name="Enabled">true</bool>
        <float name="Contrast">0.12</float>
        <float name="Saturation">0.15</float>
      </Properties>
    </Item>
  </Item>
  <Item class="StarterGui" referent="{next_ref()}">
    <Properties><string name="Name">StarterGui</string></Properties>
    {screen_gui_xml}
  </Item>
  <Item class="StarterPlayer" referent="{next_ref()}">
    <Properties><string name="Name">StarterPlayer</string></Properties>
    <Item class="StarterPlayerScripts" referent="{next_ref()}">
      <Properties><string name="Name">StarterPlayerScripts</string></Properties>
      {director_xml}
    </Item>
  </Item>
</roblox>
"""
    with open(OUT_RBXLX, "w", encoding="utf-8") as f:
        f.write(rbxlx)
    print(f"[OK] Generated native Roblox Studio Place -> {OUT_RBXLX} ({len(rbxlx):,} bytes)")

    # Also write the auto-running Edit-Mode Studio Plugin to %LOCALAPPDATA%\Roblox\Plugins
    plugins_dir = os.path.join(os.environ["LOCALAPPDATA"], "Roblox", "Plugins")
    os.makedirs(plugins_dir, exist_ok=True)
    plugin_path = os.path.join(plugins_dir, "JumpTaxAutoDirector.lua")
    c_start = director_xml.find("<![CDATA[") + len("<![CDATA[")
    c_end = director_xml.rfind("]]>")
    plugin_luau = director_xml[c_start:c_end]
    with open(plugin_path, "w", encoding="utf-8") as pf:
        pf.write(plugin_luau)
    print(f"[OK] Installed Roblox Studio Edit-Mode Cutscene Plugin -> {plugin_path}")


if __name__ == "__main__":
    generate_rbxlx()
