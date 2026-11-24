"""
post_and_mux.py — Step 5 1080x1920 Lanczos Upscaler, Rule-27 Black-Pill Subtitle Compositor & BT.709 Muxer
for videos/roblox-spinning-rock.

Reads Blender 5.3 720x1280 frames (frames/f_%04d.png), upscales cleanly to 1080x1920,
overlays crisp 2-4 word black-pill captions (8sb2R11FeVw style) synced to voice/words.json,
adds subtle 4f chromatic/impact pulse on brake/launch beats, and pipes to FFmpeg with
explicit -map 0:v:0 -map 1:a:0 and bt709 tags -> out/final.mp4.
"""
import argparse
import json
import math
import re
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJ_DIR = Path(__file__).resolve().parent
FRAMES_DIR = PROJ_DIR / "frames"
PREVIEWS_DIR = PROJ_DIR / "previews"
OUT_DIR = PROJ_DIR / "out"
OUT_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1920
FPS = 30

ALERT_WORDS = {
    "GIANT", "ROCK", "SPINNING", "THOUSAND", "GUARDRAILS", "FLYING",
    "BURNING", "SIXTYSEVEN", "VOID", "PITCHBLACK", "STRETCHING",
    "BRAKES", "LAUNCHED", "SIDEWAYS", "SPACE",
}

_PILL_CACHE = {}


def load_font(sz: int):
    for p in ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/impact.ttf"]:
        try:
            return ImageFont.truetype(p, sz)
        except Exception:
            continue
    return ImageFont.load_default()


def build_caption_groups(words: list, max_words: int = 3):
    """Group aligned words into punchy 2-4 word pills respecting punctuation & gaps."""
    groups = []
    cur = []
    for w in words:
        txt = w["word"].strip()
        if not txt:
            continue
        if cur and (float(w["start"]) - float(cur[-1]["end"]) > 0.25):
            groups.append({"start": cur[0]["start"], "end": max(cur[-1]["end"], cur[0]["start"] + 0.16), "words": cur})
            cur = []
        cur.append(w)
        ends_sent = txt[-1] in ".!?"
        ends_clause = txt[-1] in ",;—"
        if len(cur) >= max_words or ends_sent or (ends_clause and len(cur) >= 2):
            groups.append({"start": cur[0]["start"], "end": max(cur[-1]["end"], cur[0]["start"] + 0.16), "words": cur})
            cur = []
    if cur:
        groups.append({"start": cur[0]["start"], "end": max(cur[-1]["end"], cur[0]["start"] + 0.16), "words": cur})
    return groups


def render_pill_sprite(words_chunk: list, active_idx: int, pop_scale: float, font) -> Image.Image:
    q_scale = round(pop_scale, 2) if abs(pop_scale - 1.0) > 0.005 else 1.0
    key = (tuple(w["word"] for w in words_chunk), active_idx, q_scale)
    cached = _PILL_CACHE.get(key)
    if cached is not None:
        return cached

    pieces = [w["word"] + (" " if i < len(words_chunk) - 1 else "") for i, w in enumerate(words_chunk)]
    dummy = Image.new("RGBA", (10, 10))
    dd = ImageDraw.Draw(dummy)
    widths = [dd.textlength(p, font=font) for p in pieces]
    text_w = int(math.ceil(sum(widths)))
    bbox = dd.textbbox((0, 0), "Ag", font=font)
    text_h = bbox[3] - bbox[1]

    pad_x, pad_y = 38, 22
    box_w, box_h = text_w + pad_x * 2, text_h + pad_y * 2
    ov_w, ov_h = box_w + 40, box_h + 40
    ov = Image.new("RGBA", (ov_w, ov_h), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)

    x0, y0 = 20, 20
    # Drop shadow + tight near-opaque black rounded pill (8sb2R11FeVw style)
    od.rounded_rectangle([x0 + 2, y0 + 6, x0 + box_w + 2, y0 + box_h + 6], radius=16, fill=(0, 0, 0, 115))
    od.rounded_rectangle([x0, y0, x0 + box_w, y0 + box_h], radius=16, fill=(8, 8, 10, 232))

    cur_x = x0 + pad_x
    text_y = y0 + pad_y - bbox[1]
    for i, p in enumerate(pieces):
        clean_u = re.sub(r"[^A-Za-z]", "", p).upper()
        if i == active_idx:
            col = (255, 68, 82, 255) if clean_u in ALERT_WORDS else (255, 230, 0, 255)
        else:
            col = (255, 255, 255, 255)
        od.text((cur_x, text_y), p, font=font, fill=col)
        cur_x += widths[i]

    if q_scale != 1.0:
        nw, nh = max(4, int(round(ov_w * q_scale))), max(4, int(round(ov_h * q_scale)))
        ov = ov.resize((nw, nh), Image.Resampling.BILINEAR)

    if len(_PILL_CACHE) < 1024:
        _PILL_CACHE[key] = ov
    return ov


def composite_caption(im: Image.Image, groups: list, t: float, font, y_center: int = 1350) -> Image.Image:
    active_grp = None
    for g in groups:
        if g["start"] - 0.04 <= t <= g["end"] + 0.14:
            active_grp = g
            break
    if active_grp is None:
        return im

    words_c = active_grp["words"]
    active_idx = 0
    for i, w in enumerate(words_c):
        if t >= float(w["start"]) - 0.02:
            active_idx = i

    t_since = max(0.0, t - float(active_grp["start"]))
    u = min(1.0, t_since / 0.10)
    if u < 1.0:
        c1 = 1.70158
        c3 = c1 + 1.0
        pop_scale = 0.88 + 0.12 * (1.0 + c3 * ((u - 1.0) ** 3) + c1 * ((u - 1.0) ** 2))
    else:
        pop_scale = 1.0

    sprite = render_pill_sprite(words_c, active_idx, pop_scale, font)
    px = int(W * 0.5 - sprite.width * 0.5)
    py = int(y_center - sprite.height * 0.5)
    im.alpha_composite(sprite, (px, py))
    return im


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stills-only", action="store_true")
    args = parser.parse_args()

    beats_data = json.loads((PROJ_DIR / "voice" / "beats.json").read_text(encoding="utf-8"))
    words = json.loads((PROJ_DIR / "voice" / "words.json").read_text(encoding="utf-8"))
    groups = build_caption_groups(words, max_words=3)
    font = load_font(58)

    if args.stills_only:
        out_p_dir = PREVIEWS_DIR / "captioned"
        out_p_dir.mkdir(parents=True, exist_ok=True)
        for p in sorted(PREVIEWS_DIR.glob("*.png")):
            im = Image.open(p).convert("RGBA").resize((W, H), Image.Resampling.LANCZOS)
            # Composite matching beat's midpoint caption
            stem = re.sub(r"_(a|b)$", "", p.stem)
            t_mid = 0.5
            for b in beats_data["beats"]:
                if b["id"] == stem:
                    t_mid = 0.5 * (b["start"] + b["end"])
                    break
            im = composite_caption(im, groups, t_mid, font)
            im.convert("RGB").save(out_p_dir / p.name)
        print(f"[OK] Captioned preview stills -> {out_p_dir}")
        return

    total_frames = int(math.ceil(beats_data["total_duration"] * FPS))
    mix_wav = PROJ_DIR / "audio" / "mix.wav"
    out_mp4 = OUT_DIR / "final.mp4"

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
            im = Image.new("RGBA", (W, H), (40, 120, 220, 255))

        t = (f - 1) / float(FPS)
        im = composite_caption(im, groups, t, font, y_center=1350)
        proc.stdin.write(im.convert("RGB").tobytes())

    proc.stdin.close()
    ret = proc.wait()
    if ret != 0:
        raise RuntimeError(f"FFmpeg mux failed with exit code {ret}")
    print(f"[OK] Final mastered MP4 -> {out_mp4} ({total_frames} frames @ {FPS}fps)")


if __name__ == "__main__":
    main()
