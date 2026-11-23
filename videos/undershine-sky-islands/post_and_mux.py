"""
post_and_mux.py — High-Speed 8-Thread Track 7 Undershine t3ssel8r post-processor, 4x nearest-neighbor upscale,
cached Orrery 5-4-3-2-1 countdown & sky-island title cards, cached 8sb2R11FeVw subtitles, and -14 LUFS bt709 mux.
"""
import os
import sys
import glob
import json
import math
import time
import argparse
import subprocess
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import cv2
from PIL import Image, ImageDraw

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
KIT_DIR = os.path.join(ROOT, "90 Templates & Starter Kits", "undershine-blender-pixel-kit")
sys.path.insert(0, KIT_DIR)

from pixel_postprocess import (
    hex_to_rgb01,
    process_pixel_frame,
    draw_nextgen_subtitle_pill,
    find_bold_font,
)

_OVERLAY_CACHE = {}


def build_clean_chunks(words, max_words=3):
    """Group words into 1-3 word pills, flushing on any sentence end or gap > 0.28s."""
    chunks = []
    cur = []
    for w in words:
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
    c_i1 = hex_to_rgb01("#de9c68")
    c_i2 = hex_to_rgb01("#3f4e82")
    c_i3_day = hex_to_rgb01("#e3a47b")
    c_i3_twilight = hex_to_rgb01("#232952")
    c_i4 = hex_to_rgb01("#592d38")

    for s in shots_meta.get("shots", []):
        if s["start_frame"] <= frame_idx <= s["end_frame"]:
            name = s["name"]
            if "Orrery" in name or "Globe" in name:
                return c_space, True
            if name.startswith("02_I1") or name.startswith("03_I1") or name.startswith("04_I1"):
                return c_i1, False
            if name.startswith("06_I2") or name.startswith("07_I2") or name.startswith("08_I2"):
                return c_i2, False
            if name.startswith("10_I3") or name.startswith("11_I3"):
                return c_i3_day, False
            if name.startswith("12_I3"):
                return c_i3_twilight, False
            if name.startswith("14_I4") or name.startswith("15_I4") or name.startswith("16_I4"):
                return c_i4, False
    return c_space, True


def draw_centered_text(draw, text: str, cx: int, cy: int, font, fill=(255, 255, 255, 255), shadow=(10, 10, 18, 220)):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = int(cx - tw * 0.5)
    y = int(cy - th * 0.5 - bbox[1])
    draw.text((x + 3, y + 4), text, font=font, fill=shadow)
    draw.text((x, y), text, font=font, fill=fill)


def _get_cached_overlay(key, W: int, H: int, builder_fn):
    cached = _OVERLAY_CACHE.get(key)
    if cached is not None:
        return cached
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    builder_fn(od, W, H)
    ov_np = np.asarray(ov, dtype=np.float32)
    ys, xs = np.where(ov_np[:, :, 3] > 0)
    if len(ys) == 0:
        res = None
    else:
        y0, y1 = int(ys.min()), int(ys.max()) + 1
        x0, x1 = int(xs.min()), int(xs.max()) + 1
        sub = ov_np[y0:y1, x0:x1]
        alpha = sub[:, :, 3:4] * (1.0 / 255.0)
        res = (y0, y1, x0, x1, sub[:, :, :3] * alpha, 1.0 - alpha)
    _OVERLAY_CACHE[key] = res
    return res


def apply_clean_island_overlays(
    hi_rgb: np.ndarray,
    frame_num: int,
    t_sec: float,
    shots_meta: dict,
    words_data: dict,
    fonts: dict,
    countdown_start: float,
) -> np.ndarray:
    """Cached minimalist high-contrast overlays ONLY on Intro Orrery & 0.9s Sky-Island Title Cards."""
    active_shot = None
    for s in shots_meta.get("shots", []):
        if s["start_frame"] <= frame_num <= s["end_frame"]:
            active_shot = s["name"]
            break
    if not active_shot:
        return hi_rgb

    is_orrery = "Orrery" in active_shot
    globe_titles = {
        "01_I1_Globe": ("WORLD 1", "The Windmill Steppe", (165, 235, 130, 255)),
        "05_I2_Globe": ("WORLD 2", "The Midnight Rail", (255, 205, 110, 255)),
        "09_I3_Globe": ("WORLD 3", "The Clockwork Sanctuary", (125, 230, 255, 255)),
        "13_I4_Globe": ("WORLD 4", "The Ballast Quarry", (255, 125, 90, 255)),
    }

    if not is_orrery and active_shot not in globe_titles:
        return hi_rgb

    H, W = hi_rgb.shape[:2]

    if is_orrery:
        words = words_data.get("words", [])
        digit_map = {"five": "5", "5": "5", "four": "4", "4": "4", "three": "3", "3": "3", "two": "2", "2": "2", "one": "1", "1": "1"}
        active_digit = None
        for w in words:
            if float(w["s"]) < countdown_start:
                continue
            tok = w["w"].strip(".,!?:;").lower()
            if tok in digit_map and (float(w["s"]) - 0.05 <= t_sec <= float(w["e"]) + 0.14):
                active_digit = digit_map[tok]
        mode = f"digit_{active_digit}" if active_digit else ("title" if t_sec < countdown_start else "labels_only")
        key = ("orrery", mode)

        def build_fn(od, w_px, h_px):
            if active_digit is not None:
                draw_centered_text(od, active_digit, w_px // 2, 285, fonts["huge"], fill=(255, 255, 255, 255))
            elif t_sec < countdown_start:
                draw_centered_text(od, "Choose a World", w_px // 2, 240, fonts["title"], fill=(255, 255, 255, 255))
                draw_centered_text(od, "Every Year, 1 Falls Into the Storm", w_px // 2, 325, fonts["sub"], fill=(255, 230, 0, 255))
            for txt, lx, ly in [("01", 320, 895), ("02", 760, 895), ("03", 320, 1320), ("04", 760, 1320)]:
                draw_centered_text(od, txt, lx, ly, fonts["tag"], fill=(215, 222, 245, 220))

        ov_slice = _get_cached_overlay(key, W, H, build_fn)
    else:
        w_num, w_sub, accent = globe_titles[active_shot]
        key = ("globe", active_shot)

        def build_fn(od, w_px, h_px):
            draw_centered_text(od, w_num, w_px // 2, 250, fonts["title"], fill=(255, 255, 255, 255))
            draw_centered_text(od, w_sub, w_px // 2, 330, fonts["sub"], fill=accent)

        ov_slice = _get_cached_overlay(key, W, H, build_fn)

    if ov_slice is not None:
        y0, y1, x0, x1, premul, inv_a = ov_slice
        dst = hi_rgb[y0:y1, x0:x1].astype(np.float32)
        hi_rgb[y0:y1, x0:x1] = np.clip(dst * inv_a + premul, 0, 255).astype(np.uint8)
    return hi_rgb


def load_pass_frame(passes_dir: str, num_str: str):
    img_p = os.path.join(passes_dir, f"img_{num_str}.png")
    img_rgb = cv2.cvtColor(cv2.imread(img_p, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
    H, W = img_rgb.shape[:2]

    depth_p = os.path.join(passes_dir, f"depth_{num_str}.png")
    if os.path.exists(depth_p):
        d_raw = cv2.imread(depth_p, cv2.IMREAD_UNCHANGED)
        d_ch = d_raw[:, :, 0] if d_raw.ndim == 3 else d_raw
        depth_norm = d_ch.astype(np.float32) * (1.0 / 65535.0)
    else:
        depth_norm = np.ones((H, W), dtype=np.float32) * 0.5

    norm_p = os.path.join(passes_dir, f"norm_{num_str}.png")
    if os.path.exists(norm_p):
        n_raw = cv2.imread(norm_p, cv2.IMREAD_UNCHANGED)
        normal_xyz = n_raw[:, :, ::-1].astype(np.float32) * (1.0 / 65535.0)
    else:
        normal_xyz = np.zeros((H, W, 3), dtype=np.float32)

    mist_p = os.path.join(passes_dir, f"mist_{num_str}.png")
    if os.path.exists(mist_p):
        m_raw = cv2.imread(mist_p, cv2.IMREAD_GRAYSCALE)
        mist_fac = m_raw.astype(np.float32) * (1.0 / 255.0)
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
        "sub": find_bold_font(42),
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
    i1_start = float(words_data["sections"]["island1"]["start"])
    countdown_start = 3.60
    for w in words_data.get("words", []):
        if w["w"].strip(".,!?").lower() == "storm":
            countdown_start = float(w["e"]) + 0.08
            break

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
        hi_rgb = apply_clean_island_overlays(hi_rgb, frame_num, t_sec, shots_meta, words_data, fonts, countdown_start)
        y_pill = 1540 if t_sec < i1_start else 1360
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


def render_full_video(workers: int = 8):
    t0 = time.perf_counter()
    passes_dir = os.path.join(BASE, "passes")
    out_video = os.path.join(BASE, "out", "undershine_sky_islands.mp4")
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
    i1_start = float(words_data["sections"]["island1"]["start"])

    countdown_start = 3.60
    for w in words_data.get("words", []):
        if w["w"].strip(".,!?").lower() == "storm":
            countdown_start = float(w["e"]) + 0.08
            break

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
    cmd += [
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "16",
        "-pix_fmt", "yuv420p",
        "-colorspace", "bt709",
        "-color_primaries", "bt709",
        "-color_trc", "bt709",
        out_video,
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    total = len(img_files)
    still_frames = {s["start_frame"] + (s["end_frame"] - s["start_frame"]) // 2 for s in shots_meta["shots"]}
    still_frames.add(1)

    def _worker_fn(item):
        idx, img_p = item
        num_str = os.path.basename(img_p).replace("img_", "").replace(".png", "")
        frame_num = int(num_str)
        t_sec = idx / float(fps)

        img_rgb, depth_norm, normal_xyz, mist_fac, emit_rgb = load_pass_frame(passes_dir, num_str)
        mist_col, is_space = mist_color_for_frame(frame_num, shots_meta)
        if is_space:
            mist_fac = mist_fac * 0.0

        px_rgb = process_pixel_frame(img_rgb, depth_norm, normal_xyz, mist_fac, emit_rgb, mist_col, ink_col)
        hi_rgb = cv2.resize(px_rgb, (1080, 1920), interpolation=cv2.INTER_NEAREST)
        hi_rgb = apply_clean_island_overlays(hi_rgb, frame_num, t_sec, shots_meta, words_data, fonts, countdown_start)

        y_pill = 1540 if t_sec < i1_start else 1360
        if not (countdown_start - 0.05 <= t_sec < i1_start):
            hi_rgb = draw_nextgen_subtitle_pill(hi_rgb, chunks, t_sec, fonts["pill"], y_center=y_pill)
        return frame_num, hi_rgb

    with ThreadPoolExecutor(max_workers=workers) as pool:
        for frame_num, hi_rgb in pool.map(_worker_fn, enumerate(img_files), chunksize=8):
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
    dt = time.perf_counter() - t0
    print(f"[OK] Encoded {total} frames -> {out_video} in {dt:.2f}s ({total / max(0.01, dt):.1f} fps)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    if args.preview:
        render_preview_sheet()
    else:
        render_full_video(workers=args.workers)


if __name__ == "__main__":
    main()
