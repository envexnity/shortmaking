"""
post_and_mux.py — VFX, Theo Stat Card, Countdown Pop, Manga Impact Frames, White-Light Transition,
Rule-27 Subtitle Pill Compositor & BT.709 FFmpeg Muxer for videos/roblox-theo-631.
"""
import json
import math
import re
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

PROJ_DIR = Path(r"c:\Users\AFADAZIO\OneDrive\Desktop\shortmaking\videos\roblox-theo-631")
FRAMES_DIR = PROJ_DIR / "frames"
OUT_DIR = PROJ_DIR / "out"
OUT_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1920
FPS = 30

ALERT_WORDS = {"DEADLIEST", "GONE", "COOKED", "BLONDE", "HAIR"}
WIN_WORDS = {"WON", "GO", "BORN"}


def load_font(sz: int):
    for p in ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/impact.ttf"]:
        try:
            return ImageFont.truetype(p, sz)
        except Exception:
            continue
    return ImageFont.load_default()


def ease_out_back(u: float) -> float:
    u = max(0.0, min(1.0, u))
    c1 = 1.70158
    c3 = c1 + 1.0
    return 1.0 + c3 * ((u - 1.0) ** 3) + c1 * ((u - 1.0) ** 2)


def zoom_crop_rgb(im: Image.Image, scale: float) -> Image.Image:
    if scale <= 1.001:
        return im
    cw = max(16, int(round(W / scale)))
    ch = max(16, int(round(H / scale)))
    x0 = (W - cw) // 2
    y0 = (H - ch) // 2
    return im.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.Resampling.BICUBIC)


def build_caption_groups(words: list):
    groups = []
    cur = []
    for w in words:
        tok = w["word"].strip()
        if not tok:
            continue
        if tok == "HUSS!" or tok in ("3...", "2...", "1...", "GO!"):
            if cur:
                groups.append({"start": cur[0]["start"], "end": max(cur[-1]["end"], cur[0]["start"] + 0.14), "words": cur})
                cur = []
            groups.append({"start": w["start"], "end": max(w["end"], w["start"] + 0.14), "words": [w]})
            continue
        if cur and (w["start"] - cur[-1]["end"] > 0.22):
            groups.append({"start": cur[0]["start"], "end": max(cur[-1]["end"], cur[0]["start"] + 0.14), "words": cur})
            cur = []
        cur.append(w)
        char_len = sum(len(x["word"]) for x in cur)
        ends_sent = tok[-1] in ".!?"
        ends_clause = tok[-1] in ",;:"
        if len(cur) >= 3 or char_len >= 17 or ends_sent or (ends_clause and len(cur) >= 2):
            groups.append({"start": cur[0]["start"], "end": max(cur[-1]["end"], cur[0]["start"] + 0.14), "words": cur})
            cur = []
    if cur:
        groups.append({"start": cur[0]["start"], "end": max(cur[-1]["end"], cur[0]["start"] + 0.14), "words": cur})
    return groups


def make_speedline_mask() -> np.ndarray:
    im = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, int(H * 0.44)
    n_rays = 36
    for i in range(n_rays):
        a0 = (i / n_rays) * 2.0 * math.pi
        a1 = ((i + 0.36) / n_rays) * 2.0 * math.pi
        r_in = 220 if (i % 2 == 0) else 320
        r_out = 1600
        pts = [
            (cx + math.cos(a0) * r_in, cy + math.sin(a0) * r_in),
            (cx + math.cos(a0) * r_out, cy + math.sin(a0) * r_out),
            (cx + math.cos(a1) * r_out, cy + math.sin(a1) * r_out),
            (cx + math.cos(a1) * r_in, cy + math.sin(a1) * r_in),
        ]
        d.polygon(pts, fill=255 if (i % 2 == 0) else 90)
    return np.asarray(im, dtype=np.float32) / 255.0


def apply_impact_frame(arr: np.ndarray, speed_mask: np.ndarray, invert: bool = False) -> np.ndarray:
    gray = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
    thr = np.percentile(gray, 55)
    bw = np.where(gray >= thr, 235.0, 22.0)
    if invert:
        bw = 255.0 - bw
    bw = np.clip(bw * (1.0 - 0.45 * speed_mask) + speed_mask * (40.0 if not invert else 220.0), 18.0, 238.0)
    # Keep mean luma safely in [0.35..0.62]
    m = float(bw.mean() / 255.0)
    if m < 0.30:
        bw = np.clip(bw + 45.0, 18.0, 238.0)
    elif m > 0.68:
        bw = np.clip(bw - 45.0, 18.0, 238.0)
    return np.stack([bw, bw, bw], axis=2).astype(np.uint8)


def apply_chromatic_aberration(arr: np.ndarray, shift_px: int = 6) -> np.ndarray:
    out = arr.copy()
    out[:, shift_px:, 0] = arr[:, :-shift_px, 0]
    out[:, :-shift_px, 2] = arr[:, shift_px:, 2]
    return out


def draw_theo_stat_card(overlay: Image.Image, t: float, t_start: float, t_end: float,
                        f_title, f_label, f_val):
    if not (t_start <= t <= t_end):
        return
    u_in = min(1.0, (t - t_start) / 0.22)
    u_out = min(1.0, max(0.0, (t_end - t) / 0.18))
    sc = ease_out_back(u_in) * u_out
    if sc < 0.05:
        return

    cw, ch = 880, 226
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([0, 0, cw - 1, ch - 1], radius=24, fill=(12, 16, 28, 232), outline=(239, 68, 68, 255), width=6)
    cd.rounded_rectangle([24, 18, 280, 64], radius=12, fill=(239, 68, 68, 255))
    cd.text((152, 41), "RACER #631", fill=(255, 255, 255, 255), font=f_title, anchor="mm")
    cd.text((310, 41), "BIOLOGICAL TUNNEL", fill=(148, 163, 184, 255), font=f_title, anchor="lm")

    cd.text((36, 98), "NAME:", fill=(148, 163, 184, 255), font=f_label)
    cd.text((178, 92), "THEO", fill=(255, 255, 255, 255), font=f_val)
    cd.text((440, 98), "RANK:", fill=(148, 163, 184, 255), font=f_label)
    cd.text((578, 92), "#631", fill=(255, 230, 0, 255), font=f_val)

    cd.text((36, 164), "ODDS:", fill=(148, 163, 184, 255), font=f_label)
    cd.text((178, 158), "1 IN 250,000,000", fill=(56, 189, 248, 255), font=f_val)

    nw, nh = max(8, int(round(cw * sc))), max(8, int(round(ch * sc)))
    card_rs = card.resize((nw, nh), Image.Resampling.BICUBIC)
    px = (W - nw) // 2
    py = 385 - nh // 2
    overlay.alpha_composite(card_rs, (px, py))


def draw_countdown_pop(overlay: Image.Image, t: float, ticks: list[dict], f_cd):
    for tk in ticks:
        if tk["start"] <= t <= tk["end"]:
            u = min(1.0, (t - tk["start"]) / 0.10)
            sc = 0.85 + 0.25 * ease_out_back(u)
            lbl = tk["label"].replace(".", "")
            col = (34, 238, 102, 255) if "GO" in lbl else (255, 230, 0, 255)
            d = ImageDraw.Draw(overlay)
            # Crisp thick stroke centered at y=430
            d.text((W // 2, 430), lbl, fill=col, font=f_cd, anchor="mm", stroke_width=14, stroke_fill=(12, 12, 18, 255))
            break


def main():
    beats_data = json.loads((PROJ_DIR / "voice" / "beats.json").read_text(encoding="utf-8"))
    words = json.loads((PROJ_DIR / "voice" / "words.json").read_text(encoding="utf-8"))
    shots = json.loads((PROJ_DIR / "voice" / "shots.json").read_text(encoding="utf-8"))
    beats = {b["id"]: b for b in beats_data["beats"]}

    groups = build_caption_groups(words)
    total_frames = int(round(beats_data["total_duration"] * FPS))
    mix_wav = PROJ_DIR / "audio" / "mix.wav"
    out_mp4 = OUT_DIR / "final.mp4"

    f_cap = load_font(60)
    f_huss = load_font(74)
    f_card_t = load_font(28)
    f_card_l = load_font(34)
    f_card_v = load_font(44)
    f_cd = load_font(170)

    speed_mask = make_speedline_mask()
    impact_set = set()
    for ifr in shots.get("impact_frames", []):
        impact_set.add(ifr)
        impact_set.add(ifr + 1)
    egg_hit = int(shots.get("egg_hit_frame", -999))
    flash_c = int(shots.get("flash_center_frame", -999))
    ca_set = set()
    for sfr in shots.get("shake_frames", []):
        for k in range(4):
            ca_set.add(sfr + k)

    b04s, b04e = beats["b04_theo_intro"]["start"], beats["b04_theo_intro"]["end"]
    b10s = beats["b10_dad_twist"]["start"]
    cd_ticks = beats["b05_countdown_go"].get("countdown_ticks", [])

    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0",
        "-i", str(mix_wav),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
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
            im = Image.open(fp).convert("RGB")
            if im.size != (W, H):
                im = im.resize((W, H), Image.Resampling.LANCZOS)
            last_valid_img = im
        elif last_valid_img is not None:
            im = last_valid_img.copy()
        else:
            im = Image.new("RGB", (W, H), (24, 34, 54))

        t = (f - 1) / float(FPS)

        # Frame-0 kinetic snap (118% -> 100%) + b04 subtle push + b10 horror punch-in
        if f <= 9:
            u0 = 1.0 - (f - 1) / 8.0
            im = zoom_crop_rgb(im, 1.0 + 0.18 * (u0 ** 2))
        elif b04s <= t <= b04e:
            u4 = (t - b04s) / max(0.1, b04e - b04s)
            im = zoom_crop_rgb(im, 1.0 + 0.06 * u4)
        elif t >= b10s:
            u10 = (t - b10s) / max(0.1, beats_data["total_duration"] - b10s)
            im = zoom_crop_rgb(im, 1.0 + 0.14 * min(1.0, u10 * 1.2))

        arr = np.asarray(im, dtype=np.uint8)

        # Manga B&W impact frames & RGB split chromatic aberration
        if f in impact_set:
            arr = apply_impact_frame(arr, speed_mask, invert=(f == egg_hit + 1))
        elif f in ca_set:
            arr = apply_chromatic_aberration(arr, shift_px=7)

        # Warm-white flash transition across b08 -> b09
        if abs(f - flash_c) <= 5:
            alpha_w = max(0.0, 1.0 - abs(f - flash_c) / 5.5) * 0.88
            white_col = np.array([232.0, 230.0, 222.0], dtype=np.float32)
            arr = np.clip(arr.astype(np.float32) * (1.0 - alpha_w) + white_col * alpha_w, 0, 255).astype(np.uint8)

        im_rgba = Image.fromarray(arr, mode="RGB").convert("RGBA")
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)

        # Theo Stat Card & Race Countdown
        draw_theo_stat_card(overlay, t, b04s + 0.15, b04e - 0.10, f_card_t, f_card_l, f_card_v)
        draw_countdown_pop(overlay, t, cd_ticks, f_cd)

        # Rule-27 Next-Gen Black-Pill Subtitles
        while g_idx < len(groups) and groups[g_idx]["end"] < t - 0.04:
            g_idx += 1
        active_g = None
        if g_idx < len(groups) and groups[g_idx]["start"] - 0.04 <= t <= groups[g_idx]["end"] + 0.10:
            active_g = groups[g_idx]

        if active_g is not None:
            ws = active_g["words"]
            tokens = [w["word"].strip() for w in ws]
            is_huss = (len(tokens) == 1 and tokens[0] == "HUSS!")
            font_use = f_huss if is_huss else f_cap
            full_str = " ".join(tokens)
            bb = d.textbbox((0, 0), full_str, font=font_use)
            tw, th = bb[2] - bb[0], bb[3] - bb[1]

            dt_g = max(0.0, t - active_g["start"])
            pop_y = int(max(0.0, (0.10 - dt_g) / 0.10) * 12)
            pad_x, pad_y = (42, 24) if is_huss else (38, 22)
            cy = 1345 + pop_y
            x0 = W // 2 - tw // 2 - pad_x
            y0 = cy - th // 2 - pad_y
            x1 = W // 2 + tw // 2 + pad_x
            y1 = cy + th // 2 + pad_y
            d.rounded_rectangle([x0, y0, x1, y1], radius=16, fill=(8, 8, 10, 232))

            cur_x = W // 2 - tw // 2 - bb[0]
            text_y = cy - th // 2 - bb[1]
            sp_w = d.textbbox((0, 0), " ", font=font_use)[2]
            for w in ws:
                tok = w["word"].strip()
                clean_u = re.sub(r"[^A-Za-z0-9]", "", tok).upper()
                is_cur = (w["start"] - 0.04 <= t <= w["end"] + 0.06)
                if is_huss:
                    col = (255, 230, 0, 255)
                elif is_cur:
                    if clean_u in ALERT_WORDS:
                        col = (255, 64, 78, 255)
                    elif clean_u in WIN_WORDS:
                        col = (34, 238, 102, 255)
                    else:
                        col = (255, 230, 0, 255)
                else:
                    col = (255, 255, 255, 255)
                d.text((cur_x, text_y), tok, fill=col, font=font_use)
                wbb = d.textbbox((0, 0), tok, font=font_use)
                cur_x += (wbb[2] - wbb[0]) + sp_w

        comp = Image.alpha_composite(im_rgba, overlay).convert("RGB")
        proc.stdin.write(comp.tobytes())

    proc.stdin.close()
    rc = proc.wait()
    assert rc == 0, f"FFmpeg exited with {rc}"
    print(f"STEP 5 MUX COMPLETE -> {out_mp4} ({total_frames} frames)")


if __name__ == "__main__":
    main()
