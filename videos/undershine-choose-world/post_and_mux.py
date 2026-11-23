"""
post_and_mux.py — Track 7 Undershine t3ssel8r post-processor, 4x nearest-neighbor upscale,
Orrery 5-4-3-2-1 countdown & world title cards, 8sb2R11FeVw subtitles, and -14 LUFS mux.
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
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
KIT_DIR = os.path.join(ROOT, "90 Templates & Starter Kits", "undershine-blender-pixel-kit")
sys.path.insert(0, KIT_DIR)

from pixel_postprocess import (
    hex_to_rgb01,
    process_pixel_frame,
    build_subtitle_chunks,
    draw_nextgen_subtitle_pill,
    find_bold_font,
)


def build_clean_chunks(words, max_words=3):
    """Group words into 1-3 word pills, flushing on any sentence end or gap > 0.28s."""
    chunks = []
    cur = []
    for i, w in enumerate(words):
        text = w["w"].strip()
        if not text:
            continue
        if cur and float(w["s"]) - cur[-1]["e"] > 0.28:
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


def mist_color_for_frame(frame_idx: int, shots_meta: dict):
    """Zone-aware Undershine atmospheric mist colors and mist weight."""
    c_space = hex_to_rgb01("#090b1a")
    c_w1 = hex_to_rgb01("#de9c68")
    c_w2 = hex_to_rgb01("#573873")
    c_w3_day = hex_to_rgb01("#e3a47b")
    c_w3_twilight = hex_to_rgb01("#232952")
    c_w4 = hex_to_rgb01("#592d38")

    for s in shots_meta.get("shots", []):
        if s["start_frame"] <= frame_idx <= s["end_frame"]:
            name = s["name"]
            if "Orrery" in name or "Globe" in name:
                return c_space, True
            if name.startswith("02_W1") or name.startswith("03_W1") or name.startswith("04_W1"):
                return c_w1, False
            if name.startswith("06_W2") or name.startswith("07_W2") or name.startswith("08_W2"):
                return c_w2, False
            if name.startswith("10_W3") or name.startswith("11_W3"):
                return c_w3_day, False
            if name.startswith("12_W3"):
                return c_w3_twilight, False
            if name.startswith("14_W4") or name.startswith("15_W4") or name.startswith("16_W4"):
                return c_w4, False
    return c_space, True


def draw_centered_text(draw, text: str, cx: int, cy: int, font, fill=(255, 255, 255, 255), shadow=(10, 10, 18, 220)):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = int(cx - tw * 0.5)
    y = int(cy - th * 0.5 - bbox[1])
    draw.text((x + 3, y + 4), text, font=font, fill=shadow)
    draw.text((x, y), text, font=font, fill=fill)


def apply_clean_world_overlays(
    hi_rgb: np.ndarray,
    frame_num: int,
    t_sec: float,
    shots_meta: dict,
    words_data: dict,
    fonts: dict,
) -> np.ndarray:
    """
    Minimalist high-contrast overlays ONLY on Intro Orrery & 1.0s World Planet cards,
    matching reference DfUSgKdxLrb while keeping >=90% of video pure 8sb2R11FeVw subtitles.
    """
    active_shot = None
    for s in shots_meta.get("shots", []):
        if s["start_frame"] <= frame_num <= s["end_frame"]:
            active_shot = s["name"]
            break
    if not active_shot:
        return hi_rgb

    is_orrery = "Orrery" in active_shot
    globe_titles = {
        "01_W1_Globe": ("WORLD 1", "The Sun Chaser", (255, 205, 110, 255)),
        "05_W2_Globe": ("WORLD 2", "The Lantern Canopy", (130, 238, 175, 255)),
        "09_W3_Globe": ("WORLD 3", "The Glass Harbour", (125, 225, 255, 255)),
        "13_W4_Globe": ("WORLD 4", "The Ember Vault", (255, 130, 95, 255)),
    }

    if not is_orrery and active_shot not in globe_titles:
        return hi_rgb

    H, W = hi_rgb.shape[:2]
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)

    if is_orrery:
        # Find countdown word timing ONLY after "here." (never match "one" in "one year here"!)
        words = words_data.get("words", [])
        digit_map = {"five": "5", "5": "5", "four": "4", "4": "4", "three": "3", "3": "3", "two": "2", "2": "2", "one": "1", "1": "1"}
        countdown_start = 3.25
        for w in words:
            if w["w"].strip(".,!?").lower() == "here":
                countdown_start = float(w["e"]) + 0.08
                break

        active_digit = None
        for w in words:
            if float(w["s"]) < countdown_start:
                continue
            tok = w["w"].strip(".,!?:;").lower()
            if tok in digit_map:
                if float(w["s"]) - 0.05 <= t_sec <= float(w["e"]) + 0.14:
                    active_digit = digit_map[tok]

        if active_digit is not None:
            draw_centered_text(od, active_digit, W // 2, 285, fonts["huge"], fill=(255, 255, 255, 255))
        elif t_sec < countdown_start:
            draw_centered_text(od, "Choose a World", W // 2, 240, fonts["title"], fill=(255, 255, 255, 255))
            draw_centered_text(od, "You Must Survive 1 Year Here", W // 2, 325, fonts["sub"], fill=(255, 230, 0, 255))

        # Subtle world index tags under each of the 4 globes
        labels = [("01", 320, 865), ("02", 760, 865), ("03", 320, 1285), ("04", 760, 1285)]
        for txt, lx, ly in labels:
            draw_centered_text(od, txt, lx, ly, fonts["tag"], fill=(215, 222, 245, 220))

    elif active_shot in globe_titles:
        w_num, w_sub, accent = globe_titles[active_shot]
        draw_centered_text(od, w_num, W // 2, 250, fonts["title"], fill=(255, 255, 255, 255))
        draw_centered_text(od, w_sub, W // 2, 330, fonts["sub"], fill=accent)

    ov_np = np.asarray(ov, dtype=np.float32)
    alpha = ov_np[:, :, 3:4] / 255.0
    blended = hi_rgb.astype(np.float32) * (1.0 - alpha) + ov_np[:, :, :3] * alpha
    return np.clip(blended, 0, 255).astype(np.uint8)


def load_pass_frame(passes_dir: str, num_str: str):
    img_p = os.path.join(passes_dir, f"img_{num_str}.png")
    img_rgb = cv2.cvtColor(cv2.imread(img_p, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
    H, W = img_rgb.shape[:2]

    depth_p = os.path.join(passes_dir, f"depth_{num_str}.png")
    if os.path.exists(depth_p):
        d_raw = cv2.imread(depth_p, cv2.IMREAD_UNCHANGED)
        d_ch = d_raw[:, :, 0] if d_raw.ndim == 3 else d_raw
        depth_norm = d_ch.astype(np.float32) / 65535.0
    else:
        depth_norm = np.ones((H, W), dtype=np.float32) * 0.5

    norm_p = os.path.join(passes_dir, f"norm_{num_str}.png")
    if os.path.exists(norm_p):
        n_raw = cv2.imread(norm_p, cv2.IMREAD_UNCHANGED)
        normal_xyz = n_raw[:, :, ::-1].astype(np.float32) / 65535.0
    else:
        normal_xyz = np.zeros((H, W, 3), dtype=np.float32)

    mist_p = os.path.join(passes_dir, f"mist_{num_str}.png")
    if os.path.exists(mist_p):
        m_raw = cv2.imread(mist_p, cv2.IMREAD_GRAYSCALE)
        mist_fac = m_raw.astype(np.float32) / 255.0
    else:
        mist_fac = np.zeros((H, W), dtype=np.float32)

    emit_p = os.path.join(passes_dir, f"emit_{num_str}.png")
    if os.path.exists(emit_p):
        emit_rgb = cv2.cvtColor(cv2.imread(emit_p, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
    else:
        emit_rgb = np.zeros((H, W, 3), dtype=np.uint8)

    return img_rgb, depth_norm, normal_xyz, mist_fac, emit_rgb


def load_fonts():
    return {
        "pill": find_bold_font(58),
        "title": find_bold_font(68),
        "sub": find_bold_font(44),
        "huge": find_bold_font(124),
        "tag": find_bold_font(30),
    }


def render_preview_sheet():
    passes_dir = os.path.join(BASE, "passes")
    prev_dir = os.path.join(BASE, "preview_stills")
    os.makedirs(prev_dir, exist_ok=True)

    shots_meta = json.load(open(os.path.join(BASE, "shots_meta.json"), encoding="utf-8"))
    words_data = json.load(open(os.path.join(BASE, "voice", "words.json"), encoding="utf-8"))
    chunks = build_clean_chunks(words_data["words"], max_words=3)
    fonts = load_fonts()
    ink_col = hex_to_rgb01("#181326")

    img_files = sorted(glob.glob(os.path.join(passes_dir, "img_*.png")))
    tiles = []
    for img_p in img_files:
        num_str = os.path.basename(img_p).replace("img_", "").replace(".png", "")
        frame_num = int(num_str)
        t_sec = (frame_num - 1) / float(shots_meta.get("fps", 30))

        img_rgb, depth_norm, normal_xyz, mist_fac, emit_rgb = load_pass_frame(passes_dir, num_str)
        mist_col, is_space = mist_color_for_frame(frame_num, shots_meta)
        if is_space:
            mist_fac = mist_fac * 0.0

        px_rgb = process_pixel_frame(img_rgb, depth_norm, normal_xyz, mist_fac, emit_rgb, mist_col, ink_col)
        hi_rgb = cv2.resize(px_rgb, (1080, 1920), interpolation=cv2.INTER_NEAREST)
        hi_rgb = apply_clean_world_overlays(hi_rgb, frame_num, t_sec, shots_meta, words_data, fonts)
        y_pill = 1540 if t_sec < words_data["sections"]["world1"]["start"] else 1360
        hi_rgb = draw_nextgen_subtitle_pill(hi_rgb, chunks, t_sec, fonts["pill"], y_center=y_pill)

        out_p = os.path.join(prev_dir, f"preview_{num_str}.jpg")
        cv2.imwrite(out_p, cv2.cvtColor(hi_rgb, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])
        tiles.append(cv2.resize(cv2.cvtColor(hi_rgb, cv2.COLOR_RGB2BGR), (270, 480), interpolation=cv2.INTER_AREA))

    if tiles:
        cols = 5
        rows = int(math.ceil(len(tiles) / cols))
        blank = np.zeros((480, 270, 3), dtype=np.uint8)
        while len(tiles) < cols * rows:
            tiles.append(blank)
        grid = np.vstack([np.hstack(tiles[r * cols : (r + 1) * cols]) for r in range(rows)])
        sheet_p = os.path.join(prev_dir, "all_angles_sheet.jpg")
        cv2.imwrite(sheet_p, grid, [cv2.IMWRITE_JPEG_QUALITY, 92])
        print(f"[OK] Saved {len(img_files)}-shot preview contact sheet -> {sheet_p}")


def render_full_video():
    passes_dir = os.path.join(BASE, "passes")
    out_video = os.path.join(BASE, "out", "undershine_choose_world.mp4")
    audio_path = os.path.join(BASE, "audio", "mix.wav")
    stills_dir = os.path.join(BASE, "out", "qa_stills")
    os.makedirs(os.path.dirname(out_video), exist_ok=True)
    os.makedirs(stills_dir, exist_ok=True)

    shots_meta = json.load(open(os.path.join(BASE, "shots_meta.json"), encoding="utf-8"))
    words_data = json.load(open(os.path.join(BASE, "voice", "words.json"), encoding="utf-8"))
    chunks = build_clean_chunks(words_data["words"], max_words=3)
    fonts = load_fonts()
    ink_col = hex_to_rgb01("#181326")
    fps = int(shots_meta.get("fps", 30))
    w1_start = float(words_data["sections"]["world1"]["start"])

    img_files = sorted(glob.glob(os.path.join(passes_dir, "img_*.png")))
    if not img_files:
        raise FileNotFoundError(f"No img_*.png files in {passes_dir}")

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
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", out_video]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    total = len(img_files)
    still_frames = {s["start_frame"] + (s["end_frame"] - s["start_frame"]) // 2 for s in shots_meta["shots"]}
    still_frames.add(1)

    for idx, img_p in enumerate(img_files):
        num_str = os.path.basename(img_p).replace("img_", "").replace(".png", "")
        frame_num = int(num_str)
        t_sec = idx / float(fps)

        img_rgb, depth_norm, normal_xyz, mist_fac, emit_rgb = load_pass_frame(passes_dir, num_str)
        mist_col, is_space = mist_color_for_frame(frame_num, shots_meta)
        if is_space:
            mist_fac = mist_fac * 0.0

        px_rgb = process_pixel_frame(img_rgb, depth_norm, normal_xyz, mist_fac, emit_rgb, mist_col, ink_col)
        hi_rgb = cv2.resize(px_rgb, (1080, 1920), interpolation=cv2.INTER_NEAREST)
        hi_rgb = apply_clean_world_overlays(hi_rgb, frame_num, t_sec, shots_meta, words_data, fonts)

        y_pill = 1540 if t_sec < w1_start else 1360
        # Skip redundant single-digit subtitle pill during the big 5..4..3..2..1 countdown
        if not (3.15 <= t_sec < w1_start):
            hi_rgb = draw_nextgen_subtitle_pill(hi_rgb, chunks, t_sec, fonts["pill"], y_center=y_pill)

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
