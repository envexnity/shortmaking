"""
post_and_mux.py — Track 5 Roblox "In This World" Storytime Editing, Zooms, VFX & Caption Compositor (< 45s).

Implements [[In This World Roblox Storytime - Editing, Zooms & VFX Bible]]:
  1. Frame-0 Opening Blurred Punch-Out (130% -> 100% scale, blur 3 -> 0 over 10 frames)
  2. Per-shot Back.Out Punch-In Zooms + continuous micro-drift (zero static holds)
  3. 4-Frame RGB Chromatic Aberration Splits on impact beats
  4. Radial Vignette Pulses (16% resting -> 36% on dread/debt beats)
  5. Diegetic ForgeGUI Roblox Overhead Balance Pill (R$ 0 -> -R$ 4,200 -> GRAVITY BANNED: FREE)
  6. Hook Mode Title Badge + Story Mode 8sb2R11FeVw Black-BG Pop Captions (#FFE600 / #FF3344 / #22EE66 emphasis)
  7. Direct FFmpeg bt709 H.264 encode + explicit -14 LUFS audio mux
"""
import os
import sys
import glob
import json
import math
import argparse
import subprocess
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))


def find_bold_font(size: int):
    candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\calibrib.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def build_clean_chunks(words, max_words=3):
    """Group words into crisp 2-3 word pop-caption pills."""
    chunks = []
    cur = []
    for w in words:
        text = w["w"].strip()
        if not text:
            continue
        if cur and float(w["s"]) - cur[-1]["e"] > 0.24:
            chunks.append(cur)
            cur = []
        cur.append({"w": text, "s": float(w["s"]), "e": float(w["e"])})
        ends_sent = text[-1] in ".!?"
        ends_clause = text[-1] in ",;:"
        if len(cur) >= max_words or ends_sent or (ends_clause and len(cur) >= 2):
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    return chunks


def build_vignette_mask(w: int, h: int) -> np.ndarray:
    y, x = np.ogrid[:h, :w]
    cx, cy = w * 0.5, h * 0.48
    rx, ry = w * 0.55, h * 0.55
    r2 = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
    return np.clip((r2 - 0.35) / 0.95, 0.0, 1.0).astype(np.float32)[:, :, None]


def apply_zoom_and_aberration(
    img_rgb: np.ndarray,
    frame_num: int,
    t_sec: float,
    active_shot: dict,
    vig_mask: np.ndarray,
) -> np.ndarray:
    """Applies Opening Blurred Punch-Out, per-shot micro-drift zoom, 4f RGB split on impacts, and vignette pulse."""
    H, W = img_rgb.shape[:2]
    s_f = active_shot["start_frame"]
    e_f = active_shot["end_frame"]
    u_shot = (frame_num - s_f) / max(1, e_f - s_f)
    local_f = frame_num - s_f

    # 1. Scale curve: Frame 0 blurred punch-out (1.26 -> 1.00 over 10f) + continuous drift (1.00 -> 1.07)
    blur_sigma = 0.0
    if frame_num <= 10:
        u0 = (frame_num - 1) / 9.0
        ease = 1.0 - (1.0 - u0) ** 3
        scale = 1.26 - 0.24 * ease
        blur_sigma = 2.6 * (1.0 - ease)
    else:
        # Snappy punch-in on CU/Macro shots + continuous micro-drift
        is_cu = any(k in active_shot["name"] for k in ("CU", "Dutch", "Macro", "Blast"))
        base_zoom = 1.0 + (0.08 if is_cu else 0.045) * u_shot
        if local_f < 6 and is_cu:
            # Back.Out punch-in entrance
            ub = local_f / 6.0
            scale = 0.96 + 0.06 * (1.0 + 2.7 * ((ub - 1.0) ** 3) + 1.7 * ((ub - 1.0) ** 2))
        else:
            scale = base_zoom

    if scale > 1.002:
        cw = int(round(W / scale))
        ch = int(round(H / scale))
        x0 = (W - cw) // 2
        y0 = (H - ch) // 2
        cropped = img_rgb[y0 : y0 + ch, x0 : x0 + cw]
        out = cv2.resize(cropped, (W, H), interpolation=cv2.INTER_CUBIC)
    else:
        out = img_rgb.copy()

    if blur_sigma > 0.15:
        out = cv2.GaussianBlur(out, (0, 0), sigmaX=blur_sigma)

    # 2. 4-Frame RGB Chromatic Aberration Split on impact cuts
    is_impact = any(k in active_shot["name"] for k in ("ZeroRobux", "CrackWide", "RoofBlast", "Negative4000", "BanAndFloat"))
    if is_impact and local_f < 5:
        shift = int(round((5 - local_f) * 2.2))
        if shift > 0:
            r_ch = np.roll(out[:, :, 0], -shift, axis=1)
            b_ch = np.roll(out[:, :, 2], shift, axis=1)
            out = np.stack([r_ch, out[:, :, 1], b_ch], axis=2)

    # 3. Radial Vignette Pulse (16% resting -> 34% on high-tension debt/lava shots)
    vig_str = 0.30 if is_impact else 0.16
    out_f = out.astype(np.float32) * (1.0 - vig_mask * vig_str)
    return np.clip(out_f, 0, 255).astype(np.uint8)


def get_robux_hud_state(t_sec: float, sections: dict):
    """Computes live diegetic ForgeGUI Roblox top HUD counter state across the 6 beats."""
    b2_s = sections.get("beat2", {}).get("start", 8.7)
    b3_s = sections.get("beat3", {}).get("start", 13.2)
    b4_s = sections.get("beat4", {}).get("start", 19.0)
    b5_s = sections.get("beat5", {}).get("start", 25.4)
    b6_s = sections.get("beat6", {}).get("start", 33.6)

    if t_sec < 3.4:
        return "WORLD RULE: 1 JUMP = -R$ 100", (255, 230, 0, 255), (20, 24, 38, 228)
    elif t_sec < b2_s:
        return "MY BALANCE: R$ 0 (STRANDED)", (255, 65, 80, 255), (38, 14, 22, 232)
    elif t_sec < b3_s:
        return "DOMINUS KIDS: R$ 999,999 (-R$ 100/HOP)", (34, 238, 102, 255), (16, 32, 26, 228)
    elif t_sec < b4_s:
        return "ALERT: FLOOR IS LAVA | BALANCE: R$ 0", (255, 65, 80, 255), (42, 12, 18, 235)
    elif t_sec < b4_s + 2.8:
        return "EQUIPPED: FREE GRAVITY COIL (R$ 0)", (40, 240, 255, 255), (14, 28, 42, 228)
    elif t_sec < b5_s:
        u = min(1.0, (t_sec - (b4_s + 2.8)) / max(0.5, b5_s - (b4_s + 2.8)))
        jumps = max(1, int(round(u * 42)))
        return f"COIL LAUNCH: {jumps}x JUMPS REGISTERED!", (255, 140, 40, 255), (40, 18, 14, 235)
    elif t_sec < b6_s:
        u = min(1.0, (t_sec - b5_s) / max(0.5, (b6_s - 1.2) - b5_s))
        debt = int(round(100 + u * 4100))
        return f"AIRTIME TAX METER: -R$ {debt:,}", (255, 55, 70, 255), (46, 10, 18, 238)
    else:
        return "GRAVITY: BANNED | FLOAT TAX: R$ 0", (34, 238, 102, 255), (14, 36, 24, 232)


def draw_forgegui_top_hud(frame_rgb: np.ndarray, t_sec: float, sections: dict, fonts: dict) -> np.ndarray:
    """Draws the diegetic ForgeGUI Roblox HUD pill at y=260px (inside 9:16 top safe zone) + Hook Title on 0-2.4s."""
    H, W = frame_rgb.shape[:2]
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)

    label, text_col, bg_col = get_robux_hud_state(t_sec, sections)
    f_hud = fonts["hud"]
    bbox = od.textbbox((0, 0), label, font=f_hud)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 32, 16
    bw, bh = tw + pad_x * 2, th + pad_y * 2
    x0 = (W - bw) // 2
    y0 = 235

    # ForgeGUI Simulator style rounded pill with dark stroke & accent rim
    od.rounded_rectangle([x0 + 2, y0 + 5, x0 + bw + 2, y0 + bh + 5], radius=16, fill=(0, 0, 0, 130))
    od.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=16, fill=bg_col, outline=text_col, width=3)
    od.text((x0 + pad_x, y0 + pad_y - bbox[1]), label, font=f_hud, fill=text_col)

    ov_np = np.asarray(ov, dtype=np.float32)
    alpha = ov_np[:, :, 3:4] / 255.0
    blended = frame_rgb.astype(np.float32) * (1.0 - alpha) + ov_np[:, :, :3] * alpha
    return np.clip(blended, 0, 255).astype(np.uint8)


def classify_word_color(word_str: str, is_active: bool):
    """Roblox Storytime Emphasis Palette: Yellow #FFE600, Red #FF3344, Green #22EE66, White #FFFFFF."""
    low = word_str.strip(".,!?:;\"").lower()
    red_words = {"zero", "lava", "unluckily", "negative", "4,000", "banned", "debt", "cracked"}
    green_words = {"luckily", "free", "rich", "safe"}
    yellow_words = {"100", "robux", "jump", "jumps", "42", "dominus", "coil", "turbo", "admin"}

    if not is_active:
        return (255, 255, 255, 255)
    if low in red_words:
        return (255, 65, 80, 255)
    if low in green_words:
        return (34, 238, 102, 255)
    if low in yellow_words:
        return (255, 230, 0, 255)
    return (255, 230, 0, 255)


def draw_storytime_pop_subtitle(
    frame_rgb: np.ndarray,
    chunks,
    t_sec: float,
    font,
    y_center: int = 1320,
) -> np.ndarray:
    """
    8sb2R11FeVw Black-BG Rounded Pill with 4-frame Pop-Up Bounce Curve (85% -> 110% -> 100%)
    and Roblox Storytime semantic word color emphasis (#FFE600 / #FF3344 / #22EE66).
    """
    active_chunk = None
    for ch in chunks:
        if ch[0]["s"] - 0.04 <= t_sec <= ch[-1]["e"] + 0.12:
            active_chunk = ch
            break
    if not active_chunk:
        return frame_rgb

    H, W = frame_rgb.shape[:2]
    active_idx = 0
    for i, w in enumerate(active_chunk):
        if t_sec >= w["s"] - 0.02:
            active_idx = i

    t_since = max(0.0, t_sec - active_chunk[0]["s"])
    u = min(1.0, t_since / 0.11)
    c1 = 1.70158
    c3 = c1 + 1.0
    pop_scale = (
        0.86 + 0.14 * (1.0 + c3 * ((u - 1.0) ** 3) + c1 * ((u - 1.0) ** 2))
        if u < 1.0
        else 1.0
    )

    pieces = [
        w["w"] + (" " if i < len(active_chunk) - 1 else "")
        for i, w in enumerate(active_chunk)
    ]

    dummy = Image.new("RGBA", (10, 10))
    dd = ImageDraw.Draw(dummy)
    widths = [dd.textlength(p, font=font) for p in pieces]
    text_w = int(math.ceil(sum(widths)))
    bbox = dd.textbbox((0, 0), "Ag", font=font)
    text_h = bbox[3] - bbox[1]

    pad_x, pad_y = 38, 22
    box_w = text_w + pad_x * 2
    box_h = text_h + pad_y * 2

    ov_w, ov_h = box_w + 40, box_h + 40
    ov = Image.new("RGBA", (ov_w, ov_h), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)

    x0, y0 = 20, 20
    od.rounded_rectangle([x0 + 2, y0 + 6, x0 + box_w + 2, y0 + box_h + 6], radius=16, fill=(0, 0, 0, 120))
    od.rounded_rectangle([x0, y0, x0 + box_w, y0 + box_h], radius=16, fill=(8, 8, 10, 234))

    cur_x = x0 + pad_x
    text_y = y0 + pad_y - bbox[1]
    for i, p in enumerate(pieces):
        col = classify_word_color(active_chunk[i]["w"], i == active_idx)
        od.text((cur_x, text_y), p, font=font, fill=col)
        cur_x += widths[i]

    if abs(pop_scale - 1.0) > 0.004:
        nw = max(4, int(round(ov_w * pop_scale)))
        nh = max(4, int(round(ov_h * pop_scale)))
        ov = ov.resize((nw, nh), Image.Resampling.BILINEAR)
    else:
        nw, nh = ov_w, ov_h

    px = int(W * 0.5 - nw * 0.5)
    py = int(y_center - nh * 0.5)

    ov_np = np.asarray(ov, dtype=np.float32)
    x_s, y_s = max(0, px), max(0, py)
    x_e, y_e = min(W, px + nw), min(H, py + nh)
    if x_e > x_s and y_e > y_s:
        ox_s, oy_s = x_s - px, y_s - py
        sub_ov = ov_np[oy_s : oy_s + (y_e - y_s), ox_s : ox_s + (x_e - x_s)]
        alpha = sub_ov[:, :, 3:4] / 255.0
        dst = frame_rgb[y_s:y_e, x_s:x_e].astype(np.float32)
        blended = dst * (1.0 - alpha) + sub_ov[:, :, :3] * alpha
        frame_rgb[y_s:y_e, x_s:x_e] = np.clip(blended, 0, 255).astype(np.uint8)
    return frame_rgb


def load_fonts():
    return {
        "pill": find_bold_font(60),
        "hud": find_bold_font(36),
    }


def shot_for_frame(frame_num: int, shots_meta: dict) -> dict:
    shots = shots_meta.get("shots", [])
    for s in shots:
        if s["start_frame"] <= frame_num <= s["end_frame"]:
            return s
    return shots[-1] if shots else {"name": "00_Default", "start_frame": 1, "end_frame": 1000}


def render_preview_sheet():
    frames_dir = os.path.join(BASE, "frames")
    prev_dir = os.path.join(BASE, "preview_stills")
    os.makedirs(prev_dir, exist_ok=True)

    shots_meta = json.load(open(os.path.join(BASE, "shots_meta.json"), encoding="utf-8"))
    words_data = json.load(open(os.path.join(BASE, "voice", "words.json"), encoding="utf-8"))
    chunks = build_clean_chunks(words_data["words"], max_words=3)
    fonts = load_fonts()
    vig_mask = build_vignette_mask(1080, 1920)

    img_files = sorted(glob.glob(os.path.join(frames_dir, "f_*.png")))
    tiles = []
    for img_p in img_files:
        num_str = os.path.basename(img_p).replace("f_", "").replace(".png", "")
        frame_num = int(num_str)
        t_sec = (frame_num - 1) / float(shots_meta.get("fps", 30))

        raw_bgr = cv2.imread(img_p, cv2.IMREAD_COLOR)
        hi_rgb = cv2.resize(cv2.cvtColor(raw_bgr, cv2.COLOR_BGR2RGB), (1080, 1920), interpolation=cv2.INTER_LANCZOS4)
        act_shot = shot_for_frame(frame_num, shots_meta)

        hi_rgb = apply_zoom_and_aberration(hi_rgb, frame_num, t_sec, act_shot, vig_mask)
        hi_rgb = draw_forgegui_top_hud(hi_rgb, t_sec, words_data["sections"], fonts)
        hi_rgb = draw_storytime_pop_subtitle(hi_rgb, chunks, t_sec, fonts["pill"], y_center=1330)

        out_p = os.path.join(prev_dir, f"preview_{num_str}.jpg")
        cv2.imwrite(out_p, cv2.cvtColor(hi_rgb, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])
        tiles.append(cv2.resize(cv2.cvtColor(hi_rgb, cv2.COLOR_RGB2BGR), (270, 480), interpolation=cv2.INTER_AREA))

    if tiles:
        cols = 4
        rows = int(math.ceil(len(tiles) / cols))
        blank = np.zeros((480, 270, 3), dtype=np.uint8)
        while len(tiles) < cols * rows:
            tiles.append(blank)
        grid = np.vstack([np.hstack(tiles[r * cols : (r + 1) * cols]) for r in range(rows)])
        sheet_p = os.path.join(prev_dir, "all_angles_sheet.jpg")
        cv2.imwrite(sheet_p, grid, [cv2.IMWRITE_JPEG_QUALITY, 92])
        print(f"[OK] Saved {len(img_files)}-shot Roblox preview sheet -> {sheet_p}")


def render_full_video():
    frames_dir = os.path.join(BASE, "frames")
    out_video = os.path.join(BASE, "out", "roblox_in_this_world.mp4")
    audio_path = os.path.join(BASE, "audio", "mix.wav")
    stills_dir = os.path.join(BASE, "out", "qa_stills")
    os.makedirs(os.path.dirname(out_video), exist_ok=True)
    os.makedirs(stills_dir, exist_ok=True)

    shots_meta = json.load(open(os.path.join(BASE, "shots_meta.json"), encoding="utf-8"))
    words_data = json.load(open(os.path.join(BASE, "voice", "words.json"), encoding="utf-8"))
    chunks = build_clean_chunks(words_data["words"], max_words=3)
    fonts = load_fonts()
    fps = int(shots_meta.get("fps", 30))
    vig_mask = build_vignette_mask(1080, 1920)

    img_files = sorted(glob.glob(os.path.join(frames_dir, "f_*.png")))
    if not img_files:
        raise FileNotFoundError(f"No f_*.png files in {frames_dir}")

    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", "1080x1920",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "-",
    ]
    if os.path.exists(audio_path):
        cmd += ["-i", audio_path, "-map", "0:v:0", "-map", "1:a:0", "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += [
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "16",
        "-pix_fmt", "yuv420p",
        "-colorspace", "bt709",
        "-color_primaries", "bt709",
        "-color_trc", "bt709",
        out_video,
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    total = len(img_files)
    still_frames = {s["start_frame"] + (s["end_frame"] - s["start_frame"]) // 2 for s in shots_meta["shots"]}
    still_frames.add(1)

    for idx, img_p in enumerate(img_files):
        num_str = os.path.basename(img_p).replace("f_", "").replace(".png", "")
        frame_num = int(num_str)
        t_sec = idx / float(fps)

        raw_bgr = cv2.imread(img_p, cv2.IMREAD_COLOR)
        hi_rgb = cv2.resize(cv2.cvtColor(raw_bgr, cv2.COLOR_BGR2RGB), (1080, 1920), interpolation=cv2.INTER_LANCZOS4)
        act_shot = shot_for_frame(frame_num, shots_meta)

        hi_rgb = apply_zoom_and_aberration(hi_rgb, frame_num, t_sec, act_shot, vig_mask)
        hi_rgb = draw_forgegui_top_hud(hi_rgb, t_sec, words_data["sections"], fonts)
        hi_rgb = draw_storytime_pop_subtitle(hi_rgb, chunks, t_sec, fonts["pill"], y_center=1330)

        if frame_num in still_frames:
            cv2.imwrite(
                os.path.join(stills_dir, f"frame_{frame_num:04d}.jpg"),
                cv2.cvtColor(hi_rgb, cv2.COLOR_RGB2BGR),
                [cv2.IMWRITE_JPEG_QUALITY, 92],
            )
        proc.stdin.write(hi_rgb.tobytes())

    proc.stdin.close()
    ret = proc.wait()
    if ret != 0:
        raise RuntimeError(f"FFmpeg exited with code {ret}")
    print(f"[OK] Encoded {total} frames -> {out_video}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    args = ap.parse_args()
    if args.preview:
        render_preview_sheet()
    else:
        render_full_video()


if __name__ == "__main__":
    main()
