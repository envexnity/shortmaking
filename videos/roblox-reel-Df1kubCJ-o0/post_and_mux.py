"""
post_and_mux.py — Fast Python/Pillow + FFmpeg Post-Compositor & Final Mux for Df1kubCJ-o0 Remake.
Reads rendered 1080x1920 frames (frames/f_%04d.png), overlays:
  1. Crisp word-synced bold geometric captions inside a clean black rounded pill (Rule 27, 9:16 safe zone y=1320px),
     with active-word yellow #FFE600 pop + pop-bounce spring scale!
  2. Animated Bun Town overhead digital counter (`BURGERS: 001 -> 400`) during b48_400_burgers ("400 burgers. One minute.").
  3. Subtle speed-lines vignette pulse during b25_blur_hands ("I stopped being able to see my own hands.") & HUSS! beats.
Pipes directly into FFmpeg with explicit audio map (-map 0:v:0 -map 1:a:0) and bt709 color tags -> out/final.mp4!
"""
import json
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJ_DIR = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking\videos\roblox-reel-Df1kubCJ-o0")
FRAMES_DIR = PROJ_DIR / "frames"
OUT_DIR = PROJ_DIR / "out"
OUT_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1920
FPS = 30


def load_font(sz: int):
    for p in ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/impact.ttf"]:
        try:
            return ImageFont.truetype(p, sz)
        except Exception:
            continue
    return ImageFont.load_default()


def build_caption_groups(words: list, max_words=2):
    """Group aligned words into punchy 1-2 word pills (HUSS! always standalone 1-word pop!)."""
    groups = []
    i = 0
    while i < len(words):
        w = words[i]
        txt = w["word"].strip()
        if not txt:
            i += 1
            continue
        if txt.upper() == "HUSS!" or txt.endswith((".", "!", "?", ",")) or i + 1 >= len(words):
            groups.append({"start": w["start"], "end": max(w["end"], w["start"] + 0.14), "words": [w]})
            i += 1
        else:
            w2 = words[i + 1]
            # Keep 2 short words together if close in time (<0.35s gap) and not HUSS!
            if w2["word"].strip().upper() != "HUSS!" and (w2["start"] - w["end"]) < 0.25 and (len(txt) + len(w2["word"])) <= 14:
                groups.append({"start": w["start"], "end": max(w2["end"], w2["start"] + 0.14), "words": [w, w2]})
                i += 2
            else:
                groups.append({"start": w["start"], "end": max(w["end"], w["start"] + 0.14), "words": [w]})
                i += 1
    return groups


def main():
    beats_data = json.loads((PROJ_DIR / "voice" / "beats.json").read_text(encoding="utf-8"))
    words = json.loads((PROJ_DIR / "voice" / "words.json").read_text(encoding="utf-8"))
    groups = build_caption_groups(words)

    total_frames = int(round(beats_data["total_duration"] * FPS))
    mix_wav = PROJ_DIR / "audio" / "mix.wav"
    out_mp4 = OUT_DIR / "final.mp4"

    # Find b48_400_burgers frame range for the digital 001 -> 400 counter overlay
    b48_range = None
    b25_range = None
    for b in beats_data["beats"]:
        if b["id"] == "b48_400_burgers":
            b48_range = (b["start"], b["end"])
        elif b["id"] == "b25_blur_hands":
            b25_range = (b["start"], b["end"])

    f_cap = load_font(66)
    f_huss = load_font(78)
    f_cnt = load_font(58)

    # Start FFmpeg rawvideo pipe -> H.264 High + AAC 192k + explicit audio map + bt709 tags!
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0",
        "-i", str(mix_wav),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p",
        "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart", "-shortest",
        str(out_mp4),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    last_valid_img = None
    g_idx = 0

    for f in range(1, total_frames + 1):
        fp = FRAMES_DIR / f"f_{f:04d}.png"
        if fp.exists():
            im = Image.open(fp).convert("RGBA")
            if im.size != (W, H):
                im = im.resize((W, H), Image.Resampling.LANCZOS)
            last_valid_img = im
        elif last_valid_img is not None:
            im = last_valid_img.copy()
        else:
            im = Image.new("RGBA", (W, H), (16, 24, 42, 255))

        t = (f - 1) / FPS
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)

        # 1. Animated digital counter during b48_400_burgers ("400 burgers. One minute.")
        if b48_range and b48_range[0] <= t <= b48_range[1] + 0.15:
            u = min(1.0, max(0.0, (t - b48_range[0]) / max(0.1, b48_range[1] - b48_range[0])))
            cnt_val = int(round(1 + 399 * (u ** 0.85)))
            box_w, box_h = 440, 108
            bx0, by0 = (W - box_w) // 2, 240
            d.rounded_rectangle([bx0, by0, bx0 + box_w, by0 + box_h], radius=20, fill=(10, 14, 22, 232), outline=(250, 204, 21, 255), width=5)
            txt_c = f"BURGERS: {cnt_val:03d}"
            bb = d.textbbox((0, 0), txt_c, font=f_cnt)
            tw, th = bb[2] - bb[0], bb[3] - bb[1]
            d.text((W // 2 - tw // 2, by0 + (box_h - th) // 2 - 4), txt_c, fill=(255, 230, 0, 255), font=f_cnt)

        # 2. Subtle radial anime speed lines during b25_blur_hands!
        if b25_range and b25_range[0] <= t <= b25_range[1]:
            cx, cy = W // 2, H // 2 - 80
            for k in range(28):
                ang = (k / 28.0) * 2 * math.pi + (f % 3) * 0.08
                r0 = 420 + (k % 3) * 45
                r1 = 1150
                d.line(
                    [(cx + math.cos(ang) * r0, cy + math.sin(ang) * r0),
                     (cx + math.cos(ang) * r1, cy + math.sin(ang) * r1)],
                    fill=(255, 255, 255, 72), width=5,
                )

        # 3. Active Kinetic Caption Pill (Rule 27: black rounded pill, y = 1320px safe zone, active word yellow!)
        while g_idx < len(groups) and groups[g_idx]["end"] < t - 0.04:
            g_idx += 1
        active_g = None
        if g_idx < len(groups) and groups[g_idx]["start"] - 0.04 <= t <= groups[g_idx]["end"] + 0.08:
            active_g = groups[g_idx]

        if active_g is not None:
            ws = active_g["words"]
            is_huss = len(ws) == 1 and ws[0]["word"].strip().upper() == "HUSS!"
            font_use = f_huss if is_huss else f_cap

            # Measure total pill width
            tokens = [w["word"].strip() for w in ws]
            full_str = " ".join(tokens)
            bb = d.textbbox((0, 0), full_str, font=font_use)
            tw, th = bb[2] - bb[0], bb[3] - bb[1]

            # Subtle pop-bounce vertical offset on first 4 frames of each pill
            dt_g = max(0.0, t - active_g["start"])
            pop_y = int(max(0.0, (0.10 - dt_g) / 0.10) * 14)

            pad_x, pad_y = 38, 22
            px0 = (W - tw) // 2 - pad_x
            py0 = 1325 - th // 2 - pad_y + pop_y
            px1 = px0 + tw + 2 * pad_x
            py1 = py0 + th + 2 * pad_y

            d.rounded_rectangle([px0, py0, px1, py1], radius=18, fill=(8, 8, 12, 232))

            # Render words with active-word #FFE600 yellow highlight!
            cur_x = px0 + pad_x
            ty = py0 + pad_y - bb[1]
            for wi, wobj in enumerate(ws):
                wtxt = wobj["word"].strip() + (" " if wi < len(ws) - 1 else "")
                is_active_w = is_huss or (wobj["start"] - 0.04 <= t <= wobj["end"] + 0.06)
                col = (255, 230, 0, 255) if is_active_w else (255, 255, 255, 255)
                d.text((cur_x, ty), wtxt, fill=col, font=font_use)
                cur_x += d.textlength(wtxt, font=font_use)

        comp = Image.alpha_composite(im, overlay).convert("RGB")
        proc.stdin.write(comp.tobytes())
        if f % 300 == 0 or f == total_frames:
            print(f"  [MUX] Composited frame {f}/{total_frames}")

    proc.stdin.close()
    rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"FFmpeg mux failed with code {rc}")
    print(f"FINISHED FINAL VIDEO -> {out_mp4}")


if __name__ == "__main__":
    main()
