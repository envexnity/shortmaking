"""Custom 8-bit Chiptune Score & SFX for dino-time-8bit-short."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "scripts", "pixel_short_kit")))
from audio_mix import (
    mix_and_master, place, synth_segmented_bgm,
    synth_chip_pop, synth_impact_zap, synth_roar_rumble, synth_shimmer, synth_coin_clink,
)

SEGMENTS = [
    {"start_beat": 0, "end_beat": 3, "melody": [72, 76, 79, 76, 74, 77, 81, 77], "bass": [48, 48, 55, 48, 53, 53, 48, 53], "duty": 0.25},
    {"start_beat": 4, "end_beat": 8, "melody": [65, 69, 72, 69, 64, 67, 71, 67], "bass": [41, 41, 48, 41, 40, 40, 47, 40], "duty": 0.50},
    {"start_beat": 9, "end_beat": 12, "melody": [67, 71, 74, 79, 69, 72, 76, 81], "bass": [43, 43, 50, 43, 45, 45, 52, 45], "duty": 0.25},
    {"start_beat": 13, "end_beat": 15, "melody": [64, 0, 60, 0, 62, 0, 59, 0], "bass": [45, 0, 41, 0, 43, 0, 40, 0], "duty": 0.25, "hat": False},
]

def bgm_fn(total_sec, beats):
    return synth_segmented_bgm(total_sec, beats, SEGMENTS, bpm=144.0, seed=33)

def sfx_fn(sfx, beats, libs):
    place(sfx, synth_chip_pop(780, 1560, 0.14), beats[3]["start"], 0.65)
    place(sfx, synth_impact_zap(920, 110, 0.30), beats[4]["start"] + 0.10, 0.80)
    place(sfx, synth_roar_rumble(0.65), beats[5]["start"], 0.90)
    place(sfx, synth_shimmer((880, 1108, 1318)), beats[9]["start"] + 0.10, 0.65)
    place(sfx, libs["riser_hit"][-42000:], beats[12]["start"] - 0.18, 0.60)
    place(sfx, synth_chip_pop(620, 1400, 0.14), beats[12]["start"], 0.75)
    place(sfx, synth_coin_clink(), beats[15]["speechEnd"] - 0.25, 0.85)

if __name__ == "__main__":
    mix_and_master(HERE, bgm_fn, sfx_fn)
