r"""Step 3: Real-Human-Footage -> Sobel-Edge ASCII Cinema Renderer (1080x1920 @ 30fps).
Reads beats.json + refs/clips/beat_XX.mp4, extracts real human motion/silhouettes via CLAHE +
2x Sobel edge glyphs (/ \ | _) + luminance ramp + CRT phosphor bloom + 8sb2R11FeVw subtitles,
and streams directly into FFmpeg H.264 bt709 + muxes audio/mix.wav.

Usage:
  python ascii_video_render.py --stills out/stills
  python ascii_video_render.py --audio audio/mix.wav --out out/ascii_real_horror.mp4
"""
import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import time
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
FPS = 30
COLS, ROWS = 72, 80
CELL_W, CELL_H = 15, 24  # 72*15 = 1080, 80*24 = 1920
FW, FH = COLS * 2, ROWS * 2  # 144 x 160 2x field for Sobel

RAMP = " .,:;-=+*#%@"
EXTRA = "/\\|_0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ*!?"
ALL_CHARS = list(dict.fromkeys(RAMP + EXTRA))
CHAR_TO_IDX = {ch: idx for idx, ch in enumerate(ALL_CHARS)}

# Beat palette table: (bg_rgb, dark_rgb, mid_rgb, hi_rgb, mode)
PALETTES = {
    "green_cam":  ((5, 13, 9),   (12, 48, 28),  (28, 195, 102), (185, 255, 215)),
    "amber_hall": ((14, 10, 4),  (58, 42, 14),  (228, 178, 64), (255, 244, 195)),
    "red_terror": ((18, 4, 6),   (68, 12, 18),  (242, 62, 72),  (255, 208, 208)),
    "blue_bolt":  ((6, 11, 20),  (18, 46, 86),  (78, 175, 248), (215, 242, 255)),
    "day_cyan":   ((6, 14, 18),  (18, 62, 78),  (68, 208, 232), (220, 252, 255)),
    "amber_warn": ((16, 8, 4),   (64, 32, 10),  (248, 155, 42), (255, 235, 185)),
}

BEAT_STYLE = {
    0: ("green_cam",  0.00, 1.07, 0.00),
    1: ("green_cam",  0.02, 1.12, -0.02),
    2: ("amber_hall", -0.02, 1.10, 0.00),
    3: ("green_cam",  0.00, 1.09, 0.02),
    4: ("red_terror", 0.04, 1.14, -0.03),
    5: ("red_terror", -0.05, 1.18, 0.02),
    6: ("blue_bolt",  0.00, 1.10, 0.00),
    7: ("red_terror", 0.05, 1.15, -0.03),
    8: ("day_cyan",   0.00, 1.08, 0.01),
    9: ("red_terror", -0.04, 1.16, 0.00),
    10: ("red_terror", 0.06, 1.18, -0.04),
    11: ("amber_warn", 0.02, 1.11, 0.02),
    12: ("red_terror", -0.06, 1.22, 0.00),
    13: ("green_cam",  0.03, 1.13, -0.02),
}


def find_font(candidates: list[str], size: int):
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def build_glyph_atlas() -> np.ndarray:
    """Returns float32 array shape (num_chars, CELL_H, CELL_W) in [0, 1]."""
    font = find_font([
        r"C:\Windows\Fonts\consolab.ttf",
        r"C:\Windows\Fonts\CascadiaMono.ttf",
        r"C:\Windows\Fonts\courbd.ttf",
        r"C:\Windows\Fonts\lucon.ttf",
    ], 21)
    atlas = np.zeros((len(ALL_CHARS), CELL_H, CELL_W), dtype=np.float32)
    for idx, ch in enumerate(ALL_CHARS):
        if ch == " ":
            continue
        im = Image.new("L", (CELL_W, CELL_H), 0)
        dr = ImageDraw.Draw(im)
        dr.text((CELL_W * 0.5, CELL_H * 0.52), ch, fill=255, font=font, anchor="mm")
        arr = np.asarray(im, dtype=np.float32) / 255.0
        # Slight stroke boost for clean mobile visibility
        atlas[idx] = np.clip(arr * 1.15, 0.0, 1.0)
    return atlas


def load_clip_frames(clip_path: str) -> list[np.ndarray]:
    cap = cv2.VideoCapture(clip_path)
    frames = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frames.append(frame)
    cap.release()
    if not frames:
        raise RuntimeError(f"Empty clip: {clip_path}")
    return frames


def crop_and_motion(frame: np.ndarray, zoom: float, pan_x: float, pan_y: float, rot_rad: float) -> np.ndarray:
    """Center-crop real video to 9:16 + apply zoom creep, handheld sway, and Dutch tilt."""
    fh, fw = frame.shape[:2]
    target_ar = 9.0 / 16.0
    if fw / fh > target_ar:
        cw = fh * target_ar
        ch = fh
    else:
        cw = fw
        ch = fw / target_ar

    # Apply zoom & pan safely inside source bounds
    zw = max(32.0, cw / zoom)
    zh = max(32.0, ch / zoom)
    cx = fw * 0.5 + pan_x * (fw - zw) * 0.25
    cy = fh * 0.5 + pan_y * (fh - zh) * 0.25
    x0 = int(max(0, min(fw - zw, cx - zw * 0.5)))
    y0 = int(max(0, min(fh - zh, cy - zh * 0.5)))
    crop = frame[y0 : int(y0 + zh), x0 : int(x0 + zw)]
    if crop.size == 0:
        crop = frame
    small = cv2.resize(crop, (FW, FH), interpolation=cv2.INTER_AREA)
    if abs(rot_rad) > 1e-4:
        M = cv2.getRotationMatrix2D((FW * 0.5, FH * 0.5), math.degrees(rot_rad), 1.04)
        small = cv2.warpAffine(small, M, (FW, FH), borderMode=cv2.BORDER_REFLECT)
    return small


def condition_human_luma(bgr_small: np.ndarray) -> np.ndarray:
    """Enhance real human silhouettes, facial features, hands, and contours cleanly."""
    gray = cv2.cvtColor(bgr_small, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.2, tileGridSize=(6, 6))
    eq = clahe.apply(gray).astype(np.float32)
    # Percentile stretch (3%..97%) so dimly lit horror clips stay vivid in ASCII
    lo, hi = np.percentile(eq, [3, 97])
    norm = np.clip((eq - lo) / max(18.0, hi - lo), 0.0, 1.0)
    # Subtle unsharp detail boost
    blur = cv2.GaussianBlur(norm, (0, 0), 1.1)
    sharp = np.clip(norm + 0.55 * (norm - blur), 0.0, 1.0)
    # Power curve lifts midtones slightly without blowing highlights
    return np.power(sharp, 0.85).astype(np.float32)


def kick_offset(t: float, t_impact: float, amp_px: float = 24.0):
    f = int(round((t - t_impact) * FPS))
    if f < 0 or f >= 7:
        return 0.0, 0.0, 0.0, False
    decay = 1.0 - f / 7.0
    sign = 1.0 if (f % 2 == 0) else -1.0
    return sign * amp_px * 0.5 * decay, sign * amp_px * decay, sign * 0.028 * decay, True


def build_subtitle_chunks(beats: list[dict]) -> list[dict]:
    chunks = []
    for b in beats:
        ws = b.get("words", [])
        cur = []
        for i, w in enumerate(ws):
            cur.append(w)
            txt = " ".join(x["w"] for x in cur)
            ends = bool(re.search(r"[.?!,—:]$", w["w"])) if False else (w["w"][-1:] in ".?!,—:")
            if len(cur) >= 3 or (len(cur) >= 2 and (len(txt) > 15 or ends)) or i == len(ws) - 1:
                chunks.append({
                    "start": cur[0]["start"],
                    "end": cur[-1]["end"] + 0.08,
                    "words": cur,
                    "speaker": b["speaker"],
                    "beatIdx": b["i"],
                })
                cur = []
    return chunks


def draw_subtitle_pill(pil_img: Image.Image, chunk: dict, t: float, font: ImageFont.FreeTypeFont):
    words = chunk["words"]
    if not words:
        return
    active_idx = len(words) - 1
    for i, w in enumerate(words):
        if t >= w["start"] - 0.04:
            active_idx = i

    pop_col = "#FF3344" if (chunk["speaker"] == "doppelganger" or chunk["beatIdx"] in (5, 7, 9, 12, 13)) else "#FFE600"
    pieces = [w["w"] + (" " if i < len(words) - 1 else "") for i, w in enumerate(words)]

    tmp_draw = ImageDraw.Draw(pil_img)
    widths = [tmp_draw.textlength(p, font=font) for p in pieces]
    text_w = sum(widths)
    font_h = 58
    pad_x, pad_y = 38, 22
    box_w = int(round(text_w + pad_x * 2))
    box_h = int(round(font_h + pad_y * 2))

    # 3-frame easeOutBack pop-in
    u = min(1.0, max(0.0, (t - chunk["start"]) / 0.10))
    c1, c3 = 1.70158, 2.70158
    scale = 0.88 + 0.12 * (1.0 + c3 * ((u - 1.0) ** 3) + c1 * ((u - 1.0) ** 2)) if u < 1.0 else 1.0

    sw = max(2, int(round(box_w * scale)))
    sh = max(2, int(round(box_h * scale)))
    x0 = W // 2 - sw // 2
    y0 = 1365 - sh // 2

    overlay = Image.new("RGBA", pil_img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle([x0, y0, x0 + sw, y0 + sh], radius=16, fill=(8, 8, 10, 234))
    pil_img.paste(Image.alpha_composite(pil_img.convert("RGBA"), overlay).convert("RGB"))

    dr = ImageDraw.Draw(pil_img)
    cx = W * 0.5 - (text_w * scale) * 0.5
    cy = 1365
    for i, p in enumerate(pieces):
        col = pop_col if i == active_idx else "#FFFFFF"
        dr.text((cx, cy), p, font=font, fill=col, anchor="lm")
        cx += widths[i] * scale


def render_ascii_frame(
    luma_2x: np.ndarray,
    pal: tuple,
    atlas: np.ndarray,
    scanline_mask: np.ndarray,
    vig_mask: np.ndarray,
    chroma_shift: int,
    glitch_amt: float,
    frame_idx: int,
    beat_idx: int,
    t: float,
) -> np.ndarray:
    bg_rgb, dark_rgb, mid_rgb, hi_rgb = pal

    # 2x Sobel edge detection on real human luma field
    gx = cv2.Sobel(luma_2x, cv2.CV_32F, 1, 0, ksize=3) * 0.25
    gy = cv2.Sobel(luma_2x, cv2.CV_32F, 0, 1, ksize=3) * 0.25
    mag_2x = np.hypot(gx, gy)

    # Downsample 2x2 blocks -> 80x72 cell grid
    lum_cell = luma_2x.reshape(ROWS, 2, COLS, 2).mean(axis=(1, 3))
    mag_cell = mag_2x.reshape(ROWS, 2, COLS, 2).mean(axis=(1, 3))
    gx_cell = gx.reshape(ROWS, 2, COLS, 2).mean(axis=(1, 3))
    gy_cell = gy.reshape(ROWS, 2, COLS, 2).mean(axis=(1, 3))

    # Luminance character index
    lum_idx = np.clip(np.round(lum_cell * (len(RAMP) - 1)), 0, len(RAMP) - 1).astype(np.int32)

    # Edge override: snap strong Sobel gradients to _, \, |, /
    edge_mask = mag_cell > 0.22
    ang = (np.degrees(np.arctan2(gy_cell, gx_cell) + math.pi * 0.5) % 180.0 + 180.0) % 180.0
    edge_char = np.where(
        (ang < 22.5) | (ang >= 157.5),
        CHAR_TO_IDX["_"],
        np.where(ang < 67.5, CHAR_TO_IDX["\\"], np.where(ang < 112.5, CHAR_TO_IDX["|"], CHAR_TO_IDX["/"])),
    )
    char_idx = np.where(edge_mask, edge_char, lum_idx)

    # Subtle ambient background dot grid so zero frames ever go dead pitch-black
    char_idx = np.where(char_idx == 0, 1, char_idx)
    lum_cell = np.maximum(lum_cell, 0.14)

    # Color ramp interpolation: dark -> mid -> hi
    u = np.clip(lum_cell, 0.0, 1.0)[..., None]
    c_dark = np.array(dark_rgb, dtype=np.float32)
    c_mid = np.array(mid_rgb, dtype=np.float32)
    c_hi = np.array(hi_rgb, dtype=np.float32)
    cell_rgb = np.where(
        u < 0.55,
        c_dark + (c_mid - c_dark) * (u / 0.55),
        c_mid + (c_hi - c_mid) * ((u - 0.55) / 0.45),
    )

    # Glitch corruption bands during scare kicks
    if glitch_amt > 0.01:
        rng = np.random.default_rng(frame_idx + 1999)
        for r in range(ROWS):
            if rng.random() < glitch_amt * 0.22:
                sh = int(rng.integers(-4, 5))
                if sh != 0:
                    char_idx[r] = np.roll(char_idx[r], sh)
                    cell_rgb[r] = np.roll(cell_rgb[r], sh, axis=0)
                    corrupt = rng.random(COLS) < 0.28
                    g_pool = np.array([CHAR_TO_IDX[c] for c in "#%*!?"], dtype=np.int32)
                    char_idx[r, corrupt] = rng.choice(g_pool, size=int(corrupt.sum()))

    # Diegetic security camera stamp on Beats 0 & 13 inside safe interior margins
    if beat_idx in (0, 13):
        stamp = "CAM-03"
        for i, ch in enumerate(stamp):
            char_idx[11, 10 + i] = CHAR_TO_IDX[ch]
            cell_rgb[11, 10 + i] = c_hi
        rec = "* REC" if (int(t * 2) % 2 == 0) else "  REC"
        for i, ch in enumerate(rec):
            char_idx[11, 56 + i] = CHAR_TO_IDX[ch]
            cell_rgb[11, 56 + i] = np.array([255, 68, 78], dtype=np.float32)

    # Vectorized glyph blitting: (ROWS, COLS, CELL_H, CELL_W) -> (H, W)
    alpha_grid = atlas[char_idx]  # (80, 72, 24, 15)
    alpha_full = alpha_grid.transpose(0, 2, 1, 3).reshape(H, W)

    # Expand per-cell RGB to pixel grid cleanly via np.repeat
    rgb_full = np.repeat(np.repeat(cell_rgb, CELL_H, axis=0), CELL_W, axis=1)  # (1920, 1080, 3)

    bg_arr = np.array(bg_rgb, dtype=np.float32).reshape(1, 1, 3)
    if chroma_shift > 0:
        a_r = np.roll(alpha_full, -chroma_shift, axis=1)
        a_g = alpha_full
        a_b = np.roll(alpha_full, chroma_shift, axis=1)
        a_rgb = np.stack([a_r, a_g, a_b], axis=-1)
        canvas = bg_arr * (1.0 - a_rgb) + rgb_full * a_rgb
    else:
        a1 = alpha_full[..., None]
        canvas = bg_arr * (1.0 - a1) + rgb_full * a1

    # CRT scanlines + GPU-style Gaussian phosphor bloom + vignette
    canvas *= scanline_mask
    glow_small = cv2.resize(canvas, (270, 480), interpolation=cv2.INTER_AREA)
    glow_small = cv2.GaussianBlur(glow_small, (0, 0), 3.2)
    glow_full = cv2.resize(glow_small, (W, H), interpolation=cv2.INTER_LINEAR)
    canvas = np.clip(canvas + glow_full * 0.38, 0.0, 255.0) * vig_mask
    return canvas.astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", default=None)
    ap.add_argument("--audio", default=None)
    ap.add_argument("--out", default=os.path.join(HERE, "out", "ascii_real_horror.mp4"))
    args = ap.parse_args()

    with open(os.path.join(HERE, "beats.json"), encoding="utf-8") as f:
        bd = json.load(f)
    with open(os.path.join(HERE, "refs", "refs_manifest.json"), encoding="utf-8") as f:
        rm = json.load(f)

    beats = bd["beats"]
    total_sec = bd["total"]
    total_frames = int(math.ceil(total_sec * FPS))
    sub_chunks = build_subtitle_chunks(beats)

    atlas = build_glyph_atlas()
    sub_font = find_font([
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\calibrib.ttf",
    ], 58)

    # Precompute CRT scanline mask & vignette mask
    scan_row = np.where((np.arange(H) % 4) == 0, 0.85, 1.0).astype(np.float32)[:, None, None]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rn = np.hypot((xx - W * 0.5) / (W * 0.55), (yy - H * 0.46) / (H * 0.55))
    vig = np.clip(1.0 - np.maximum(0.0, rn - 0.55) * 0.55, 0.48, 1.0)[..., None].astype(np.float32)

    print("Preloading real human reference clips into memory...")
    clips = {m["beat"]: load_clip_frames(m["clip"]) for m in rm}

    def frame_at_time(t: float, f_idx: int) -> Image.Image:
        # Locate active beat
        bi = 0
        for b in beats:
            if b["start"] <= t < b["end"]:
                bi = b["i"]
                break
            if t >= b["end"]:
                bi = b["i"]
        b = beats[bi]
        u = min(1.0, max(0.0, (t - b["start"]) / max(0.1, b["end"] - b["start"])))

        pal_name, tilt_base, z_end, pan_dir = BEAT_STYLE.get(bi, ("green_cam", 0.0, 1.10, 0.0))
        pal = PALETTES[pal_name]

        # Ping-pong / loop real clip smoothly
        cframes = clips[bi]
        cf_idx = int((t - b["start"]) * FPS)
        if len(cframes) > 1:
            period = 2 * (len(cframes) - 1)
            m = cf_idx % period
            cf_idx = m if m < len(cframes) else period - m
        else:
            cf_idx = 0
        src_bgr = cframes[cf_idx]

        # Continuous camera zoom + handheld sway + impact kicks
        zoom = 1.02 + u * (z_end - 1.0)
        pan_x = math.sin(t * 2.1) * 0.14 + pan_dir * u
        pan_y = math.cos(t * 1.6) * 0.12
        rot = tilt_base + math.sin(t * 1.3) * 0.008

        k_times = [4.75, 9.85, 16.50, 24.46, 29.36, 31.35]
        chroma = 0
        glitch = 0.0
        for kt in k_times:
            kx, ky, krot, act = kick_offset(t, kt, 0.25)
            if act:
                pan_x += kx
                pan_y += ky
                rot += krot
                chroma = 4
                glitch = 0.75

        bgr_2x = crop_and_motion(src_bgr, zoom, pan_x, pan_y, rot)
        luma_2x = condition_human_luma(bgr_2x)
        rgb_arr = render_ascii_frame(luma_2x, pal, atlas, scan_row, vig, chroma, glitch, f_idx, bi, t)

        pil_img = Image.fromarray(rgb_arr, mode="RGB")
        for ch in sub_chunks:
            if ch["start"] <= t <= ch["end"]:
                draw_subtitle_pill(pil_img, ch, t, sub_font)
                break
        return pil_img

    if args.stills:
        os.makedirs(args.stills, exist_ok=True)
        times = [0.03] + [round((b["start"] + b["end"]) * 0.5, 3) for b in beats]
        for idx, ts in enumerate(times):
            im = frame_at_time(ts, int(ts * FPS))
            im.save(os.path.join(args.stills, f"still_{idx:02d}.jpg"), quality=92)
        subprocess.run([
            "ffmpeg", "-y", "-v", "error",
            "-i", os.path.join(args.stills, "still_%02d.jpg"),
            "-vf", "scale=270:480,tile=5x3",
            os.path.join(args.stills, "sheet.jpg"),
        ], check=True)
        print(f"Saved {len(times)} ASCII stills + sheet.jpg in {args.stills}")
        return

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    silent_mp4 = args.out + ".silent.mp4" if args.audio else args.out
    ff = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p",
        "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
        "-movflags", "+faststart",
        silent_mp4,
    ], stdin=subprocess.PIPE)

    t0 = time.time()
    for f_idx in range(total_frames):
        im = frame_at_time(f_idx / FPS, f_idx)
        ff.stdin.write(np.asarray(im, dtype=np.uint8).tobytes())
        if (f_idx + 1) % 150 == 0 or f_idx == total_frames - 1:
            print(f"  [ascii-real-horror] Frame {f_idx + 1}/{total_frames} ({time.time() - t0:.1f}s)", flush=True)
    ff.stdin.close()
    ret = ff.wait()
    if ret != 0:
        raise RuntimeError(f"ffmpeg exited with {ret}")

    if args.audio and os.path.exists(args.audio):
        subprocess.run([
            "ffmpeg", "-y", "-v", "error",
            "-i", silent_mp4, "-i", os.path.abspath(args.audio),
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-map", "0:v:0", "-map", "1:a:0", "-shortest",
            args.out,
        ], check=True)
        os.remove(silent_mp4)
    print(f"Rendered {total_frames} frames -> {args.out} in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
