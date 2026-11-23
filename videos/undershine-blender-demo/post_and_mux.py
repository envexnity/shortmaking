"""
post_and_mux.py — Runs Undershine t3ssel8r post-processing, 4x nearest-neighbor upscale,
8sb2R11FeVw subtitles, and explicit -14 LUFS audio mux.
"""
import os
import sys
import glob
import json
import argparse
import numpy as np
import cv2

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
KIT_DIR = os.path.join(ROOT, "90 Templates & Starter Kits", "undershine-blender-pixel-kit")
sys.path.insert(0, KIT_DIR)

from pixel_postprocess import (
    hex_to_rgb01,
    process_pixel_frame,
    run_postprocess,
    build_subtitle_chunks,
    draw_nextgen_subtitle_pill,
    find_bold_font,
)


def mist_schedule(u: float) -> np.ndarray:
    """Golden-hour peach haze -> burnt sunset mauve -> deep twilight indigo mist."""
    c0 = hex_to_rgb01("#e8a97e")  # Warm golden hour
    c1 = hex_to_rgb01("#c77b70")  # Sunset coral-rose
    c2 = hex_to_rgb01("#4c4675")  # Dusk violet
    c3 = hex_to_rgb01("#1b2142")  # Deep twilight indigo
    if u < 0.35:
        t = u / 0.35
        return c0 * (1 - t) + c1 * t
    elif u < 0.72:
        t = (u - 0.35) / 0.37
        return c1 * (1 - t) + c2 * t
    else:
        t = (u - 0.72) / 0.28
        return c2 * (1 - t) + c3 * t


def render_preview_sheet():
    passes_dir = os.path.join(BASE, "passes")
    prev_dir = os.path.join(BASE, "preview_stills")
    os.makedirs(prev_dir, exist_ok=True)

    words_p = os.path.join(BASE, "voice", "words.json")
    words = json.load(open(words_p, encoding="utf-8"))["words"]
    chunks = build_subtitle_chunks(words, max_words=3)
    font = find_bold_font(58)
    ink_col = hex_to_rgb01("#181326")

    img_files = sorted(glob.glob(os.path.join(passes_dir, "img_*.png")))
    tiles = []
    for img_p in img_files:
        base = os.path.basename(img_p)
        num_str = base.replace("img_", "").replace(".png", "")
        frame_num = int(num_str)
        u = (frame_num - 1) / 633.0

        img_rgb = cv2.cvtColor(cv2.imread(img_p, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
        d_raw = cv2.imread(os.path.join(passes_dir, f"depth_{num_str}.png"), cv2.IMREAD_UNCHANGED)
        depth_norm = (d_raw[:, :, 0] if d_raw.ndim == 3 else d_raw).astype(np.float32) / 65535.0
        n_raw = cv2.imread(os.path.join(passes_dir, f"norm_{num_str}.png"), cv2.IMREAD_UNCHANGED)
        normal_xyz = n_raw[:, :, ::-1].astype(np.float32) / 65535.0
        m_raw = cv2.imread(os.path.join(passes_dir, f"mist_{num_str}.png"), cv2.IMREAD_GRAYSCALE)
        mist_fac = m_raw.astype(np.float32) / 255.0
        e_rgb = cv2.cvtColor(cv2.imread(os.path.join(passes_dir, f"emit_{num_str}.png"), cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)

        px_rgb = process_pixel_frame(img_rgb, depth_norm, normal_xyz, mist_fac, e_rgb, mist_schedule(u), ink_col)
        hi_rgb = cv2.resize(px_rgb, (1080, 1920), interpolation=cv2.INTER_NEAREST)
        hi_rgb = draw_nextgen_subtitle_pill(hi_rgb, chunks, (frame_num - 1) / 30.0, font)

        out_p = os.path.join(prev_dir, f"preview_{num_str}.jpg")
        cv2.imwrite(out_p, cv2.cvtColor(hi_rgb, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])
        tiles.append(cv2.resize(cv2.cvtColor(hi_rgb, cv2.COLOR_RGB2BGR), (360, 640), interpolation=cv2.INTER_AREA))

    if len(tiles) >= 8:
        row1 = np.hstack(tiles[:4])
        row2 = np.hstack(tiles[4:8])
        sheet = np.vstack([row1, row2])
        sheet_p = os.path.join(prev_dir, "all_8_angles_sheet.jpg")
        cv2.imwrite(sheet_p, sheet, [cv2.IMWRITE_JPEG_QUALITY, 92])
        print(f"[OK] Saved 8-angle preview contact sheet -> {sheet_p}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    args = ap.parse_args()
    if args.preview:
        render_preview_sheet()
    else:
        run_postprocess(
            passes_dir=os.path.join(BASE, "passes"),
            out_video=os.path.join(BASE, "out", "undershine_blender_demo.mp4"),
            fps=30,
            target_w=1080,
            target_h=1920,
            words_json=os.path.join(BASE, "voice", "words.json"),
            audio_path=os.path.join(BASE, "audio", "mix.wav"),
            mist_schedule=mist_schedule,
            stills_dir=os.path.join(BASE, "out", "qa_stills"),
        )


if __name__ == "__main__":
    main()
