---
title: Color Psychology, Typography Pairing & Frame-0 Thumbnail Engineering
tags:
  - look-bible
  - color-theory
  - typography
  - graphic-design
  - thumbnails
  - frame-0
  - non-3d
  - ui-safe-zone
area: look-bible
style: all
status: evergreen
created: 2026-11-21
updated: 2026-11-21
summary: Complete non-3D visual design bible — 60-30-10 color value massing, 8 genre-locked production color palettes, mobile-first typography pairing & contrast rules, and 3-element Frame-0 / Browse-Shelf thumbnail engineering with the Squint Test.
---

# Color Psychology, Typography Pairing & Frame-0 Thumbnail Engineering

> [!IMPORTANT] Design for a `390 px` Phone Screen in Bright Sunlight
> `85%+` of short-form viewers watch on a phone held at arm's length while scrolling at 3 thumbs-per-second. Subtle pastel gradients, thin `300`-weight fonts, and cluttered 7-object compositions vanish instantly on mobile. **High value contrast, bold geometric hierarchy, and disciplined 3-color palettes win every time.**

---

## 1. The `60–30–10` Color & Value Massing Law

Never scatter 8 saturated rainbow colors across a frame—when everything shouts, nothing is heard:
- **`60%` Dominant Canvas (Low-to-Mid Saturation)**: The atmosphere/background (`sky`, `dark navy studio`, `warm parchment`, `CRT black`). Keeps eye fatigue low and makes characters pop.
- **`30%` Secondary Environment / Structure (Mid Value)**: Midground props, clothing bases, UI panels, maps, or framing silhouettes.
- **`10%` High-Chroma Focal Accent (Maximum Luminance/Saturation Contrast)**: **Reserved exclusively** for the hero subject, active subtitle highlight word (`#FFE600`), danger indicator (`#FF3344`), or key prop clue!

### The Grayscale Value Separation Rule (Squint Test)
Convert any still frame or thumbnail to **grayscale** (or squint until details blur):
- If the Hero Subject blends into the Background value (difference `< 25%` luminance), the shot fails readability—even if the hues are different (e.g., bright red on bright green looks identical in value!).
- Always pair **Light Hero on Dark Background** (glowing/cinematic/horror/sci-fi) OR **Dark-Outlined High-Contrast Hero on Warm Light Background** (2D toon/editorial/comic).

---

## 2. The 8 Genre-Locked Production Color Palettes

Copy these exact tested hex palettes so every video has cohesive art direction from Frame 0 to the final frame:

| Genre / Format | 60% Dominant BG | 30% Secondary / Mid | 10% Hero Accent | Ink / Text / Contrast | Emotional Signal |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Warm Toon History** *(Nutshell / Mr Omi)* | `#9ED4F0` Sky / `#DB9044` Sunset | `#8C7853` Stone / `#5B5173` Violet Shadow | `#E63946` Red Coat / `#FFE600` Gold | `#241726` Plum Ink *(never `#000`)* | Playful, hand-crafted, nostalgic |
| **2. Roblox Neon Storytime** *(Xenost / R6)* | `#0B1120` Deep Slate Studio | `#1E293B` Stud Deck / `#3B82F6` Roblox Blue | `#FACC15` Noob Yellow / `#38BDF8` Cyan Rim | `#FFFFFF` + `#08080A` Pill | Energetic, glossy, arcade-punchy |
| **3. Space & Science Explainer** *(Orbit / Kaz / Kurzgesagt)* | `#070B16` Deep Space | `#132342` Orbital Navy / `#2EC4B6` Teal | `#FF9F1C` Solar Amber / `#F72585` Magenta | `#F8FAFC` Crisp White | Awe, authority, cosmic scale |
| **4. Editorial Documentary** *(Vox / Johnny Harris)* | `#F4EFE4` Warm Newsprint | `#262A34` Charcoal Slate / `#C8BFA8` Kraft | `#FFE600` Highlighter / `#D62828` Red String | `#18191F` Editorial Ink | Investigative, smart, high-trust |
| **5. Dark Mystery / True Crime** *(Fern / Lemmino)* | `#090B10` Obsidian | `#1C2230` Cold Fog / `#3A465C` Steel | `#E07A5F` Warm Lamp / `#DC2626` Evidence Red | `#E2E8F0` Soft Bone | Suspenseful, journalistic, eerie |
| **6. Analog / ASCII Horror** *(Local 58 / CCTV)* | `#050806` CRT Void | `#112217` Phosphor Dim / `#1B2420` Static | `#33FF66` Terminal Green / `#FF2A2A` Alert | `#D8E4E0` Monospace | Uncanny dread, found-footage |
| **7. Cozy / Emotional 2D Story** *(Hachiko / Kacaurus)* | `#FFF7EA` Cream Paper | `#D9B89C` Warm Wood / `#7C90A0` Soft Slate | `#E76F51` Terracotta / `#F4A261` Amber | `#2A2128` Soft Charcoal | Intimate, heartfelt, bittersweet |
| **8. 8-Bit Retro Pixel Canvas** *(NES / Pico-8)* | `#1D2B53` Midnight Indigo | `#29ADFF` Sky / `#008751` Emerald | `#FFEC27` Coin Gold / `#FF004D` Laser Red | `#FFF1E8` Pixel Cream | Nostalgic, crisp, hyper-legible |

---

## 3. Typography Pairing & Mobile Legibility Rules

### A. Approved Short-Form Font Pairings
Never mix more than **2 font families** in a single video (1 Display/Subtitle + 1 Supporting Data/Mono):

| Video Style | Primary Headline / Subtitle Font | Secondary HUD / Label Font | Character & Weight Rules |
| :--- | :--- | :--- | :--- |
| **Viral Storytelling / Roblox / Next-Gen Pill** | **Montserrat Black** / **Metropolis ExtraBold** / **Burbank Big Condensed** | **Inter SemiBold** | `56–64 px` at `1080×1920`, tight tracking `-0.02em`, `ALL CAPS` for 1–3 word hooks, Title Case or Upper for `2–4` word pills |
| **Editorial Documentary / History** | **Playfair Display Bold** / **Instrument Serif** (italic for quotes) | **Space Grotesk Bold** / **Inter** | Use crisp serif for narration emphasis + clean geometric sans for dates/maps |
| **Tech / Space / Data / UI Stories** | **Plus Jakarta Sans ExtraBold** / **Satoshi Black** | **JetBrains Mono Bold** (`tabular-nums`) | **Always set `font-variant-numeric: tabular-nums`** on ticking counters so numbers never jitter left/right! |
| **ASCII Horror / Retro 8-Bit** | **JetBrains Mono Bold** / **Press Start 2P** / **VT323** | Same monospace family | Lock pixel fonts to exact integer multiples (`16 px`, `24 px`, `32 px`, `48 px`) so strokes stay razor-sharp |

### B. Non-Negotiable Mobile Readability Laws
1. **Minimum Legible Font Size at `1080×1920`**:
   - Primary Subtitles / Hook Title: **`56–84 px`** (never smaller than `48 px`).
   - Secondary HUD / Date / Label: **`28–36 px`** (never smaller than `24 px`—anything under `22 px` turns to mush on a `390 px` phone!).
2. **Contrast Ratio Floor**: Always exceed **`7:1` WCAG AAA contrast** for text over moving video by placing subtitles inside the **`8sb2R11FeVw` black rounded pill** (`rgba(8, 8, 10, 0.90)`, `border-radius: 16px`, `padding: 22px 38px`) OR pairing thick `6–8 px` dark stroke + soft drop shadow.
3. **Color-Coded Semantic Highlighting** (max 1 highlight color per caption pill):
   - **`#FFFFFF`** = Base spoken words
   - **`#FFE600`** (Yellow) = Hero nouns, quantities, time limits, rule words (`$100`, `1880`, `SECRET`)
   - **`#FF3344`** (Red) = Danger, failure, debt, villains, bans (`DEBT`, `ZERO`, `COLLAPSED`)
   - **`#22EE66`** (Green) = Wins, survival, `"Luckily..."` beats (`FREE`, `SAVED`, `RICH`)

---

## 4. Frame-0 & Browse-Shelf Thumbnail Engineering

On YouTube Shorts, **`15–25%` of total views** arrive via Home/Subscription/Search shelves where viewers judge a **static thumbnail frame**—and on the Shorts/TikTok/Reels feed, **Frame 0** is your live visual billboard for the first `0.4 seconds` before the viewer's brain even processes Word 2.

### The 3-Element Thumbnail & Frame-0 Law
Every high-CTR Frame 0 / Thumbnail contains **at most 3 visual elements** (if there are 4+, cut one):
1. **1 Unmistakable Subject** (Expressive character close-up with `'wide'`/`'o'` reaction OR single dramatic hero object like a snapping bridge / glowing planet / giant debt counter).
2. **1 Visual Conflict / Paradox Clue** (Red arrow, crack, lava floor, `"-$10,000"` overhead badge, or dramatic size contrast—*tiny human vs. giant object*).
3. **1 Short Hook Text Lockup (`2–4` words MAX)** — Must **complement**, never repeat, the video title! (e.g., Title: *"The Bridge That Collapsed From a Song"* → Frame-0 Visual Text: **`TOO POLITE TO STOP`**).

### The 5-Point Frame-0 / Thumbnail Pre-Ship Audit
- [ ] **200 px Shrink Test**: Shrink the frame down to `200 px` tall—can you read the facial expression, the paradox, and the `2–4` word text in **`< 0.5 seconds`**?
- [ ] **9:16 Safe-Zone Check**: Are all faces, props, and hook text completely outside the Top (`0–220 px`), Bottom (`1460–1920 px`), and Right Rail (`920–1080 px`) platform UI dead zones?
- [ ] **Focal Triangle**: Do eyes/arrows/lighting naturally pull the viewer's gaze in a tight triangle (`Face → Paradox Prop → Hook Text`)?
- [ ] **Zero Duplicate Clutter**: No redundant HUD boxes, watermarks, or tiny corner URLs competing with the focal point.
- [ ] **Instant Motion on Frame 0→10**: In the actual video, Frame 0 opens mid-motion (`130%→100%` punch-out or active camera creep)—never a static title card!

## Related Vault Guides
- [[04 Next-Generation Retention, Subtitles & Audio Spec]]
- [[Non-3D Visual Styles Encyclopedia (2D Vector, Storytime Animatics, Documentary Collage, 8-Bit & ASCII Horror)]]
- [[Bonus Track - Kinetic Typography & Motion Graphics (Remotion + EffectCraft + GSAP)]]
- [[Deep Research - Animation Layout, Staging & Visual Composition]]
- [[Readability Traps & Anti-Slop Rules]]
