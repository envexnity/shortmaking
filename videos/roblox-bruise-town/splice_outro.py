"""
splice_outro.py — Splices the EffectCraft-rendered Thorfinn outro (assets/outro_clips/thorfinn_outro.mp4)
onto the rendered story segment of out/final_v1_backup.mp4 (0 .. outro_start) and muxes with
the updated -14 LUFS audio/mix.wav (Aruarian Dance original + voice + SFX + Thorfinn outro audio).
Zero Blender re-rendering needed!
"""
import json
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent

beats_data = json.loads((BASE / "voice" / "beats.json").read_text(encoding="utf-8"))
story_end = float(beats_data["beats"][-1]["end"])

story_src = BASE / "out" / "final_v1_backup.mp4"
ec_outro = ROOT / "assets" / "outro_clips" / "thorfinn_outro.mp4"
mix_wav = BASE / "audio" / "mix.wav"
out_mp4 = BASE / "out" / "final.mp4"

filter_complex = (
    f"[0:v]trim=start=0:end={story_end:.3f},setpts=PTS-STARTPTS,fps=30,format=yuv420p[v0];"
    f"[1:v]fps=30,scale=1080:1920,setsar=1,format=yuv420p[v1];"
    f"[v0][v1]concat=n=2:v=1:a=0[v]"
)

cmd = [
    "ffmpeg", "-hide_banner", "-y",
    "-i", str(story_src),
    "-i", str(ec_outro),
    "-i", str(mix_wav),
    "-filter_complex", filter_complex,
    "-map", "[v]", "-map", "2:a:0",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p",
    "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
    "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
    "-movflags", "+faststart", "-shortest",
    str(out_mp4),
]
subprocess.run(cmd, check=True)
print(f"[OK] Spliced EffectCraft outro + Aruarian Dance mix -> {out_mp4}")
