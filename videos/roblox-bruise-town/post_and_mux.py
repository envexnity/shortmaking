"""
post_and_mux.py — Step 5 @Arseluz27 Pixel Post-Processor, Subtitle Pill Compositor & BT.709 Muxer
for videos/roblox-bruise-town.

Reads Blender 5.3 270x480 multi-pass frames (15 fps) -> applies 1px dark silhouette outlines,
convex highlights, zone-aware atmospheric mist & golden bloom, Bayer dither, 4x nearest-neighbor
upscale to 1080x1920, Rule-27 synced black-pill captions, and stepped-on-twos 30fps mux with audio/mix.wav.

Usage:
  python post_and_mux.py --stills-only
  python post_and_mux.py
"""
import argparse
import glob
import json
import math
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
KIT_DIR = ROOT / "90 Templates & Starter Kits" / "undershine-blender-pixel-kit"
sys.path.insert(0, str(KIT_DIR))

from pixel_postprocess import (  # noqa: E402
    find_bold_font,
    hex_to_rgb01,
    process_pixel_frame,
)

W, H = 1080, 1920
IN_FPS = 15
OUT_FPS = 30

ALERT_WORDS = {"CRUELTY", "BRUISE", "BRUISED", "UNRECOGNIZABLE", "SWOLLEN", "WELTS", "ENEMIES", "GRUDGES", "BROKEN"}
_PILL_CACHE = {}


def build_clean_chunks(words: list, outro_start: float, outro_dur: float, max_words: int = 3):
    chunks = []
    cur = []
    for w in words:
        text = w["w"].strip()
        if not text:
            continue
        if cur and float(w["s"]) - cur[-1]["e"] > 0.25:
            chunks.append(cur)
            cur = []
        cur.append({"w": text, "s": float(w["s"]), "e": float(w["e"])})
        ends_sent = text[-1] in ".!?"
        ends_clause = text[-1] in ",;:—\""
        if len(cur) >= max_words or ends_sent or (ends_clause and len(cur) >= 2):
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)

    # Outro Thorfinn quote synced to thorfinn_outro.mp4 audio
    chunks.append([
        {"w": "I", "s": outro_start + 0.08, "e": outro_start + 0.55},
        {"w": "have", "s": outro_start + 0.55, "e": outro_start + 0.85},
        {"w": "no", "s": outro_start + 0.85, "e": outro_start + 1.15},
        {"w": "enemies.", "s": outro_start + 1.15, "e": outro_start + 1.90},
    ])
    chunks.append([
        {"w": "I", "s": outro_start + 2.10, "e": outro_start + 2.55},
        {"w": "have", "s": outro_start + 2.55, "e": outro_start + 2.85},
        {"w": "no", "s": outro_start + 2.85, "e": outro_start + 3.15},
        {"w": "grudges", "s": outro_start + 3.15, "e": outro_start + 3.85},
        {"w": "against", "s": outro_start + 3.85, "e": outro_start + 4.18},
        {"w": "you.", "s": outro_start + 4.18, "e": outro_start + 4.85},
    ])
    chunks.append([
        {"w": "I", "s": outro_start + 5.10, "e": outro_start + 6.00},
        {"w": "HAVE", "s": outro_start + 6.00, "e": outro_start + 6.80},
        {"w": "NO", "s": outro_start + 6.80, "e": outro_start + 7.60},
        {"w": "ENEMIES.", "s": outro_start + 7.60, "e": outro_start + outro_dur - 0.15},
    ])
    return chunks


def _get_pill_sprite(active_chunk, active_idx: int, pop_scale: float, font):
    q_scale = round(pop_scale, 2) if abs(pop_scale - 1.0) > 0.005 else 1.0
    key = (tuple(w["w"] for w in active_chunk), active_idx, q_scale)
    cached = _PILL_CACHE.get(key)
    if cached is not None:
        return cached

    pieces = [w["w"] + (" " if i < len(active_chunk) - 1 else "") for i, w in enumerate(active_chunk)]
    dummy = Image.new("RGBA", (10, 10))
    dd = ImageDraw.Draw(dummy)
    widths = [dd.textlength(p, font=font) for p in pieces]
    text_w = int(math.ceil(sum(widths)))
    bbox = dd.textbbox((0, 0), "Ag", font=font)
    text_h = bbox[3] - bbox[1]

    pad_x, pad_y = 36, 20
    box_w, box_h = text_w + pad_x * 2, text_h + pad_y * 2
    ov_w, ov_h = box_w + 40, box_h + 40
    ov = Image.new("RGBA", (ov_w, ov_h), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)

    x0, y0 = 20, 20
    od.rounded_rectangle([x0 + 2, y0 + 6, x0 + box_w + 2, y0 + box_h + 6], radius=16, fill=(0, 0, 0, 115))
    od.rounded_rectangle([x0, y0, x0 + box_w, y0 + box_h], radius=16, fill=(8, 8, 10, 232))

    cur_x = x0 + pad_x
    text_y = y0 + pad_y - bbox[1]
    for i, p in enumerate(pieces):
        clean_u = re.sub(r"[^A-Za-z]", "", p).upper()
        if i == active_idx:
            col = (255, 72, 88, 255) if clean_u in ALERT_WORDS else (255, 230, 0, 255)
        else:
            col = (255, 255, 255, 255)
        od.text((cur_x, text_y), p, font=font, fill=col)
        cur_x += widths[i]

    if q_scale != 1.0:
        nw, nh = max(4, int(round(ov_w * q_scale))), max(4, int(round(ov_h * q_scale)))
        ov = ov.resize((nw, nh), Image.Resampling.BILINEAR)
    else:
        nw, nh = ov_w, ov_h

    ov_np = np.asarray(ov, dtype=np.float32)
    alpha = ov_np[:, :, 3:4] / 255.0
    res = (ov_np[:, :, :3] * alpha, 1.0 - alpha, nw, nh)
    if len(_PILL_CACHE) < 1024:
        _PILL_CACHE[key] = res
    return res


def draw_subtitle_pill(frame_rgb: np.ndarray, chunks, t_sec: float, font, y_center: int = 1360):
    active_chunk = None
    for ch in chunks:
        if ch[0]["s"] - 0.04 <= t_sec <= ch[-1]["e"] + 0.14:
            active_chunk = ch
            break
    if not active_chunk:
        return frame_rgb

    active_idx = 0
    for i, w in enumerate(active_chunk):
        if t_sec >= w["s"] - 0.02:
            active_idx = i

    t_since = max(0.0, t_sec - active_chunk[0]["s"])
    u = min(1.0, t_since / 0.10)
    if u < 1.0:
        c1 = 1.70158
        c3 = c1 + 1.0
        pop_scale = 0.88 + 0.12 * (1.0 + c3 * ((u - 1.0) ** 3) + c1 * ((u - 1.0) ** 2))
    else:
        pop_scale = 1.0

    rgb_premul, inv_alpha, nw, nh = _get_pill_sprite(active_chunk, active_idx, pop_scale, font)
    px = int(W * 0.5 - nw * 0.5)
    py = int(y_center - nh * 0.5)
    x_s, y_s = max(0, px), max(0, py)
    x_e, y_e = min(W, px + nw), min(H, py + nh)
    if x_e > x_s and y_e > y_s:
        ox_s, oy_s = x_s - px, y_s - py
        hs, ws = y_e - y_s, x_e - x_s
        dst = frame_rgb[y_s:y_e, x_s:x_e].astype(np.float32)
        frame_rgb[y_s:y_e, x_s:x_e] = np.clip(
            dst * inv_alpha[oy_s:oy_s + hs, ox_s:ox_s + ws] + rgb_premul[oy_s:oy_s + hs, ox_s:ox_s + ws],
            0, 255
        ).astype(np.uint8)
    return frame_rgb


def mist_color_for_time(t_sec: float, beats: dict, outro_start: float):
    if t_sec >= outro_start:
        return hex_to_rgb01("#e8964e"), 0.88  # Golden sunset bloom for Thorfinn outro!
    if t_sec >= beats["b15_tuesday"]["start"]:
        return hex_to_rgb01("#75829c"), 0.65  # Moody Tuesday apartment
    if beats["b13_mom_sick"]["start"] <= t_sec < beats["b14_night_shifts"]["start"]:
        return hex_to_rgb01("#b4d0e6"), 0.65  # Crisp hospital blue
    if (beats["b07_sam_work"]["start"] <= t_sec < beats["b08_bleachers"]["start"]) or (
        beats["b14_night_shifts"]["start"] <= t_sec < beats["b15_tuesday"]["start"]
    ):
        return hex_to_rgb01("#c99d74"), 0.72  # Warm shop / kitchen light
    return hex_to_rgb01("#9fb8dc"), 0.55      # Clear afternoon town sky


def process_one_frame(args_tuple):
    num_str, img_p, passes_dir, beats, outro_start, chunks, font = args_tuple
    frame_15 = int(num_str)
    t_sec = (frame_15 - 1) / float(IN_FPS)

    depth_p = passes_dir / f"depth_{num_str}.png"
    norm_p = passes_dir / f"norm_{num_str}.png"
    mist_p = passes_dir / f"mist_{num_str}.png"
    emit_p = passes_dir / f"emit_{num_str}.png"

    img_bgr = cv2.imread(str(img_p), cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    h, w = img_rgb.shape[:2]

    if depth_p.exists():
        d_raw = cv2.imread(str(depth_p), cv2.IMREAD_UNCHANGED)
        d_ch = d_raw[:, :, 0] if d_raw.ndim == 3 else d_raw
        depth_norm = d_ch.astype(np.float32) * (1.0 / 65535.0)
    else:
        depth_norm = np.ones((h, w), dtype=np.float32) * 0.5

    if norm_p.exists():
        n_raw = cv2.imread(str(norm_p), cv2.IMREAD_UNCHANGED)
        normal_xyz = n_raw[:, :, ::-1].astype(np.float32) * (1.0 / 65535.0)
    else:
        normal_xyz = np.zeros((h, w, 3), dtype=np.float32)

    if mist_p.exists():
        mist_fac = cv2.imread(str(mist_p), cv2.IMREAD_GRAYSCALE).astype(np.float32) * (1.0 / 255.0)
    else:
        mist_fac = np.zeros((h, w), dtype=np.float32)

    if emit_p.exists():
        emit_rgb = cv2.cvtColor(cv2.imread(str(emit_p), cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
    else:
        emit_rgb = np.zeros((h, w, 3), dtype=np.uint8)

    mist_col, bloom_str = mist_color_for_time(t_sec, beats, outro_start)
    ink_col = hex_to_rgb01("#12101c")

    px_rgb = process_pixel_frame(
        img_rgb, depth_norm, normal_xyz, mist_fac, emit_rgb,
        mist_col, ink_col,
        outline_strength=0.72,
        bevel_strength=0.14,
        bloom_strength=bloom_str,
        dither_levels=30.0,
    )
    hi_base = cv2.resize(px_rgb, (W, H), interpolation=cv2.INTER_NEAREST)

    # Render two stepped-on-twos 30fps frames (subtitles update crisply at 30fps on top of 15fps pixel art)
    f_a = draw_subtitle_pill(hi_base.copy(), chunks, t_sec, font)
    f_b = draw_subtitle_pill(hi_base.copy(), chunks, t_sec + (1.0 / OUT_FPS), font)
    return frame_15, f_a, f_b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills-only", action="store_true")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    beats_data = json.loads((BASE / "voice" / "beats.json").read_text(encoding="utf-8"))
    beats = {b["id"]: b for b in beats_data["beats"]}
    outro_start = float(beats_data["outro_start"])
    outro_dur = float(beats_data["outro_duration"])
    total_dur = float(beats_data["total_duration"])

    words = json.loads((BASE / "voice" / "words.json").read_text(encoding="utf-8"))
    chunks = build_clean_chunks(words, outro_start, outro_dur, max_words=3)
    font = find_bold_font(56)

    passes_dir = BASE / "passes"
    img_files = sorted(glob.glob(str(passes_dir / "img_*.png")))
    if not img_files:
        raise FileNotFoundError(f"No img_*.png files in {passes_dir}")

    tasks = []
    for p in img_files:
        ip = Path(p)
        num_str = ip.stem.replace("img_", "")
        tasks.append((num_str, ip, passes_dir, beats, outro_start, chunks, font))

    if args.stills_only:
        stills_dir = BASE / "preview_stills"
        stills_dir.mkdir(parents=True, exist_ok=True)
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            for frame_15, f_a, _ in pool.map(process_one_frame, tasks):
                out_p = stills_dir / f"still_{frame_15:04d}.png"
                cv2.imwrite(str(out_p), cv2.cvtColor(f_a, cv2.COLOR_RGB2BGR))
                print(f"[STILL] {out_p}")
        return

    out_dir = BASE / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_mp4 = out_dir / "final.mp4"
    mix_wav = BASE / "audio" / "mix.wav"

    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(OUT_FPS), "-i", "-",
        "-i", str(mix_wav),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p",
        "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart", "-shortest",
        str(out_mp4),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    t0 = time.perf_counter()
    target_out_frames = int(round(total_dur * OUT_FPS))
    written = 0

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for _, f_a, f_b in pool.map(process_one_frame, tasks, chunksize=6):
            if written < target_out_frames:
                proc.stdin.write(f_a.tobytes())
                written += 1
            if written < target_out_frames:
                proc.stdin.write(f_b.tobytes())
                written += 1

    proc.stdin.close()
    ret = proc.wait()
    if ret != 0:
        raise RuntimeError(f"FFmpeg exited with code {ret}")
    dt = time.perf_counter() - t0
    print(f"[OK] Encoded {written} frames ({OUT_FPS}fps) -> {out_mp4} in {dt:.2f}s")


if __name__ == "__main__":
    main()
