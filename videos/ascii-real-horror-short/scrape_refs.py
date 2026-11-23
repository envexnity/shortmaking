"""Step 2: Real-Human Reference Video Scraper & Trimmer for ascii-real-horror-short.
Reads beats.json, searches YouTube for real human reference clips matching each beat's action,
downloads clean <=720p MP4s, auto-selects high-motion/high-contrast non-black segments via OpenCV,
trims each clip to the beat duration, and builds refs/refs_verify_sheet.jpg for visual inspection.
"""
import json
import os
import subprocess
import sys
import cv2
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REFS_DIR = os.path.join(HERE, "refs")
RAW_DIR = os.path.join(REFS_DIR, "raw")
CLIPS_DIR = os.path.join(REFS_DIR, "clips")

BAD_WORDS = (
    "cartoon", "animated", "animation", "minecraft", "roblox", "gameplay",
    "game", "trailer", "reaction", "tutorial", "how to", "lyrics", "music video",
    "3d", "blender", "unreal", "godot", "ai ", "midjourney", "meme",
    "envato", "pond5", "videohive", "shutterstock", "istock", "getty", "alamy", "storyblocks",
)
GOOD_WORDS = ("free stock", "no copyright", "copyright free", "creative commons", "pexels", "pixabay", "close up", "closeup")

BEAT_QUERIES = {
    0: ["man walking to light in dark tunnel stock footage"],
    1: ["a person opening a door to go outside free stock footage"],
    2: ["old and abandoned house free stock footage"],
    3: ["Free HD Stock Footage of Men walk down dark hallway", "man walking away dark hallway pexels free stock"],
    4: ["ghost hand on window horror royalty free stock footage"],
    5: ["dark brown eye opening macro stock video"],
    6: ["door lock hand key free stock footage no copyright"],
    7: ["creepy man standing dark doorway free stock footage"],
    8: ["silhouette person doorway light pexels free stock", "man walking shadow daylight pexels free stock"],
    9: ["man smiling dark close up face pexels free stock", "creepy smile dark lighting pixabay free stock"],
    10: ["person running stairs night pexels free stock", "man running dark hallway pixabay free stock"],
    11: ["security operator talks using walkie-talkie"],
    12: ["close up man face dark pexels free stock", "person talking close up dark pixabay free stock"],
    13: ["no copyright man depressed sitting chair window free stock"],
}

# Pin exact verified IDs when known clean from manifest
PINNED_IDS = {
    3: "1TUKB2Mt5OI",
    4: "Fn3XS10hdOA",
    5: "N_XcW6jmbIA",
    8: "Is2Pcs_r2Po",
    9: "dF_vXRCrt1c",
    10: "ErBb2wH07VQ",
    11: "M0B8fx7mBP8",
    12: "8-NqmgfsQdE",
}


def search_candidates(queries: list[str], max_per_q: int = 6):
    seen = set()
    cands = []
    for q in queries:
        try:
            out = subprocess.check_output(
                ["yt-dlp", "--dump-json", "--flat-playlist", f"ytsearch{max_per_q}:{q}"],
                text=True,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            continue
        for line in out.splitlines():
            if not line.strip():
                continue
            d = json.loads(line)
            vid = d.get("id")
            if not vid or vid in seen:
                continue
            seen.add(vid)
            dur = d.get("duration") or 0
            title = (d.get("title") or "").strip()
            tl = title.lower()
            if dur < 3 or dur > 120:
                continue
            if any(bw in tl for bw in BAD_WORDS):
                continue
            score = sum(2 for gw in GOOD_WORDS if gw in tl)
            if 5 <= dur <= 35:
                score += 2
            cands.append({"id": vid, "title": title, "dur": dur, "score": score, "url": f"https://www.youtube.com/watch?v={vid}"})
    cands.sort(key=lambda x: x["score"], reverse=True)
    return cands


def download_video(url: str, out_path: str) -> bool:
    if os.path.exists(out_path) and os.path.getsize(out_path) > 10_000:
        return True
    cmd = [
        "yt-dlp", "-q", "--no-warnings",
        "-f", "bv*[height<=720][ext=mp4]/b[height<=720][ext=mp4]/bv*[height<=720]/b",
        "--merge-output-format", "mp4",
        "-o", out_path,
        url,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode == 0 and os.path.exists(out_path) and os.path.getsize(out_path) > 10_000


def pick_best_window(video_path: str, need_dur: float) -> tuple[float, float]:
    """Scan up to first 25s sequentially at ~2 fps to pick a clean, non-black, active segment."""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    if fps <= 1 or fps > 120:
        fps = 30.0
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    total_s = min(30.0, n_frames / fps) if n_frames > 0 else 10.0
    if total_s <= need_dur + 0.4:
        cap.release()
        return 0.0, max(0.5, total_s)

    step = max(1, int(fps * 0.5))
    max_scan_frames = int(min(n_frames if n_frames > 0 else fps * 25, fps * 25))
    samples = []
    prev = None
    idx = 0
    while idx < max_scan_frames:
        ok = cap.grab()
        if not ok:
            break
        if idx % step == 0:
            ok2, frame = cap.retrieve()
            if not ok2 or frame is None:
                break
            gray = cv2.cvtColor(cv2.resize(frame, (128, 128)), cv2.COLOR_BGR2GRAY).astype(np.float32)
            luma = float(gray.mean())
            contrast = float(gray.std())
            motion = float(np.abs(gray - prev).mean()) if prev is not None else 0.0
            prev = gray
            samples.append((idx / fps, luma, contrast, motion))
        idx += 1
    cap.release()

    if not samples:
        return 0.0, need_dur

    best_t = 0.0
    best_score = -1e9
    max_t = samples[-1][0]
    for t0, luma, contrast, motion in samples:
        if t0 + need_dur > max_t + 0.3 and t0 > 0.5:
            continue
        if luma < 12 or luma > 240 or contrast < 14:
            sc = -100.0
        else:
            sc = contrast * 0.6 + motion * 1.4 + (10.0 if 0.5 <= t0 <= max(1.0, max_t * 0.6) else 0.0)
        if sc > best_score:
            best_score = sc
            best_t = t0
    return round(best_t, 2), round(need_dur, 2)


def trim_clip(src: str, t0: float, dur: float, dst: str):
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-ss", f"{t0:.2f}", "-i", src,
        "-t", f"{dur + 0.4:.2f}",
        "-r", "30", "-an",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
        dst,
    ], check=True)


def build_verify_sheet(clips_meta: list[dict], out_jpg: str):
    tw, th = 270, 480
    cols = 7
    rows = int(np.ceil(len(clips_meta) / cols))
    sheet = Image.new("RGB", (tw * cols, th * rows), (10, 12, 16))
    draw = ImageDraw.Draw(sheet)

    for i, m in enumerate(clips_meta):
        c_idx, r_idx = i % cols, i // cols
        x0, y0 = c_idx * tw, r_idx * th
        clip_path = m["clip"]
        cap = cv2.VideoCapture(clip_path)
        nf = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 1)
        cap.set(cv2.CAP_PROP_POS_FRAMES, nf // 2)
        ok, frame = cap.read()
        cap.release()
        if ok:
            # Center-crop to 9:16 preview just like the ASCII shader will!
            h, w = frame.shape[:2]
            target_ar = 9.0 / 16.0
            if w / h > target_ar:
                nw = int(h * target_ar)
                sx = (w - nw) // 2
                frame = frame[:, sx : sx + nw]
            else:
                nh = int(w / target_ar)
                sy = (h - nh) // 2
                frame = frame[sy : sy + nh, :]
            rgb = cv2.cvtColor(cv2.resize(frame, (tw, th)), cv2.COLOR_BGR2RGB)
            sheet.paste(Image.fromarray(rgb), (x0, y0))
        draw.rectangle([x0, y0, x0 + tw, y0 + 28], fill=(0, 0, 0))
        draw.text((x0 + 6, y0 + 6), f"B{i:02d} {m['id']} ({m['dur']:.1f}s)", fill=(255, 230, 80))

    sheet.save(out_jpg, quality=90)


def main():
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(CLIPS_DIR, exist_ok=True)
    with open(os.path.join(HERE, "beats.json"), encoding="utf-8") as f:
        bd = json.load(f)
    beats = bd["beats"]

    # Optional CLI override: --only 3,4,5 and --pick 4:2
    picks = {}
    only_set = None
    args = sys.argv[1:]
    idx_a = 0
    while idx_a < len(args):
        arg = args[idx_a]
        if arg == "--only" and idx_a + 1 < len(args):
            only_set = {int(x) for x in args[idx_a + 1].split(",") if x.strip()}
            idx_a += 2
            continue
        if ":" in arg and not arg.startswith("--"):
            bi_s, ci_s = arg.split(":", 1)
            picks[int(bi_s)] = int(ci_s)
        idx_a += 1

    old_manifest_path = os.path.join(REFS_DIR, "refs_manifest.json")
    old_map = {}
    if os.path.exists(old_manifest_path):
        old_map = {m["beat"]: m for m in json.load(open(old_manifest_path, encoding="utf-8"))}

    manifest = []
    for b in beats:
        i = b["i"]
        if only_set is not None and i not in only_set and i in old_map:
            manifest.append(old_map[i])
            continue
        need_dur = max(1.6, float(b["end"]) - float(b["start"]))
        queries = BEAT_QUERIES.get(i, [b["text"]])
        cands = search_candidates(queries, max_per_q=6)
        if i in PINNED_IDS:
            pid = PINNED_IDS[i]
            cands = [{"id": pid, "title": f"Pinned {pid}", "dur": 15, "score": 99, "url": f"https://www.youtube.com/watch?v={pid}"}] + [c for c in cands if c["id"] != pid]
        if not cands:
            raise RuntimeError(f"No video candidates found for beat {i}: {queries}")

        pick_idx = min(picks.get(i, 0), len(cands) - 1)
        chosen = None
        raw_path = None
        for offset in range(len(cands)):
            cand = cands[(pick_idx + offset) % len(cands)]
            rp = os.path.join(RAW_DIR, f"beat_{i:02d}_{cand['id']}.mp4")
            if download_video(cand["url"], rp):
                chosen = cand
                raw_path = rp
                break

        if not chosen:
            raise RuntimeError(f"All downloads failed for beat {i}")

        t0, win_dur = pick_best_window(raw_path, need_dur)
        clip_path = os.path.join(CLIPS_DIR, f"beat_{i:02d}.mp4")
        trim_clip(raw_path, t0, win_dur, clip_path)

        entry = {
            "beat": i,
            "id": chosen["id"],
            "title": chosen["title"],
            "url": chosen["url"],
            "t0": t0,
            "dur": need_dur,
            "clip": clip_path,
            "candidates": [{"id": c["id"], "title": c["title"], "dur": c["dur"]} for c in cands[:5]],
        }
        manifest.append(entry)
        print(f"  [B{i:02d}] {chosen['id']} @ {t0:.2f}s | {chosen['title'][:55]}", flush=True)

    with open(os.path.join(REFS_DIR, "refs_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    sheet_path = os.path.join(REFS_DIR, "refs_verify_sheet.jpg")
    build_verify_sheet(manifest, sheet_path)
    print(f"Saved {len(manifest)} real reference clips + {sheet_path}")


if __name__ == "__main__":
    main()
