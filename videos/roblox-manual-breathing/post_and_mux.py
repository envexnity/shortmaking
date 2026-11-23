"""
post_and_mux.py — Kinetic Rule-27 Caption Compositor & BT.709 FFmpeg Muxer for roblox-manual-breathing.
- Upscales frames/f_%04d.png cleanly to 1080x1920 (Lanczos)
- Adds subtle Rule 1.1 Opening Blurred Punch-Out on frames 1..8
- Burns punchy 1-2 word synced black-pill captions with #FFE600 active-word pop (and #FF3344 on danger/manual words)
- Muxes with audio/mix.wav via explicit -map 0:v:0 -map 1:a:0.
"""
import json
import re
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROJ_DIR = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking\videos\roblox-manual-breathing")
FRAMES_DIR = PROJ_DIR / "frames"
OUT_DIR = PROJ_DIR / "out"
OUT_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1920
FPS = 30

ALERT_WORDS = {"BLACK", "LOG", "OUT", "NO", "PAUSE", "OFF", "MANUALLY", "LUCK", "STOP", "UNCONSCIOUS"}


def load_font(sz: int):
    for p in ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/impact.ttf"]:
        try:
            return ImageFont.truetype(p, sz)
        except Exception:
            continue
    return ImageFont.load_default()


def build_caption_groups(words: list):
    groups = []
    i = 0
    while i < len(words):
        w = words[i]
        txt = w["word"].strip()
        if not txt:
            i += 1
            continue
        if txt.endswith((".", "!", "?", ",", "—")) or i + 1 >= len(words):
            groups.append({"start": w["start"], "end": max(w["end"], w["start"] + 0.14), "words": [w]})
            i += 1
        else:
            w2 = words[i + 1]
            if (w2["start"] - w["end"]) < 0.25 and (len(txt) + len(w2["word"])) <= 13:
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

    f_cap = load_font(64)
    f_big = load_font(74)

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

        # Rule 1.1 Opening Blurred Punch-Out (frames 1..8)
        if f <= 8:
            u = (f - 1) / 7.0
            ease = 1.0 - (1.0 - u) ** 3
            scale = 1.18 - 0.18 * ease
            blur_r = 2.2 * (1.0 - ease)
            if scale > 1.005:
                cw, ch = int(W / scale), int(H / scale)
                x0 = (W - cw) // 2
                y0 = (H - ch) // 2
                im = im.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.Resampling.LANCZOS)
            if blur_r > 0.25:
                im = im.filter(ImageFilter.GaussianBlur(radius=blur_r))

        t = (f - 1) / FPS
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)

        while g_idx < len(groups) and groups[g_idx]["end"] < t - 0.04:
            g_idx += 1
        active_g = None
        if g_idx < len(groups) and groups[g_idx]["start"] - 0.04 <= t <= groups[g_idx]["end"] + 0.08:
            active_g = groups[g_idx]

        if active_g is not None:
            ws = active_g["words"]
            tokens = [w["word"].strip() for w in ws]
            clean_up = [re.sub(r"[^A-Z0-9]", "", tok.upper()) for tok in tokens]
            is_big = any(cu in ("20000", "MANUALLY", "OFF", "LUCK") for cu in clean_up)
            font_use = f_big if is_big else f_cap

            full_str = " ".join(tokens)
            bb = d.textbbox((0, 0), full_str, font=font_use)
            tw, th = bb[2] - bb[0], bb[3] - bb[1]

            dt_g = max(0.0, t - active_g["start"])
            pop_y = int(max(0.0, (0.10 - dt_g) / 0.10) * 12)

            pad_x, pad_y = (38, 22)
            cy = 1340 + pop_y
            x0 = W // 2 - tw // 2 - pad_x
            y0 = cy - th // 2 - pad_y
            x1 = W // 2 + tw // 2 + pad_x
            y1 = cy + th // 2 + pad_y
            d.rounded_rectangle([x0, y0, x1, y1], radius=16, fill=(8, 8, 10, 234))

            cur_x = W // 2 - tw // 2 - bb[0]
            text_y = cy - th // 2 - bb[1]
            sp_w = d.textbbox((0, 0), " ", font=font_use)[2]
            for wi, w in enumerate(ws):
                tok = w["word"].strip()
                cu = clean_up[wi]
                is_cur = (w["start"] - 0.04 <= t <= w["end"] + 0.06)
                if is_cur:
                    col = (255, 58, 72, 255) if cu in ALERT_WORDS else (255, 230, 0, 255)
                else:
                    col = (255, 255, 255, 255)
                d.text((cur_x, text_y), tok, fill=col, font=font_use)
                wbb = d.textbbox((0, 0), tok, font=font_use)
                cur_x += (wbb[2] - wbb[0]) + sp_w

        comp = Image.alpha_composite(im, overlay).convert("RGB")
        proc.stdin.write(comp.tobytes())

    proc.stdin.close()
    rc = proc.wait()
    assert rc == 0, f"FFmpeg exited with {rc}"
    print(f"Muxed final 1080x1920 video -> {out_mp4} ({total_frames} frames)")


if __name__ == "__main__":
    main()
