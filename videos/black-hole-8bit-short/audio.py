"""Custom 8-bit Chiptune Score & SFX for black-hole-8bit-short."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "scripts", "pixel_short_kit")))
from audio_mix import (
    mix_and_master, place, synth_segmented_bgm,
    synth_chip_pop, synth_impact_zap, synth_shimmer, synth_overdrive_riser, synth_coin_clink,
)

SEGMENTS = [
    {"start_beat": 0, "end_beat": 3, "melody": [72, 76, 79, 76, 74, 77, 81, 77], "bass": [48, 48, 55, 48, 53, 53, 48, 53], "duty": 0.25},
    {"start_beat": 4, "end_beat": 8, "melody": [69, 72, 75, 72, 68, 71, 74, 71], "bass": [45, 45, 52, 45, 44, 44, 51, 44], "duty": 0.125},
    {"start_beat": 9, "end_beat": 12, "melody": [74, 77, 81, 84, 76, 79, 83, 86], "bass": [50, 50, 57, 50, 52, 52, 59, 52], "bell": True},
    {"start_beat": 13, "end_beat": 15, "melody": [64, 0, 60, 0, 62, 0, 59, 0], "bass": [45, 0, 41, 0, 43, 0, 40, 0], "duty": 0.25, "hat": False},
]

def bgm_fn(total_sec, beats):
    return synth_segmented_bgm(total_sec, beats, SEGMENTS, bpm=140.0, seed=11)

def sfx_fn(sfx, beats, libs):
    place(sfx, synth_chip_pop(780, 1560, 0.14), beats[3]["start"], 0.65)
    place(sfx, synth_impact_zap(920, 65, 0.32), beats[4]["start"] + 0.15, 0.85)
    place(sfx, synth_shimmer(), beats[7]["start"], 0.75)
    place(sfx, synth_shimmer((880, 1174, 1568)), beats[9]["start"] + 0.10, 0.70)
    place(sfx, synth_overdrive_riser(0.75), beats[11]["start"] + 0.15, 0.75)
    place(sfx, libs["riser_hit"][-48000:], beats[12]["start"] - 0.20, 0.55)
    place(sfx, synth_impact_zap(640, 90, 0.26), beats[13]["start"] - 0.06, 0.80)
    place(sfx, synth_coin_clink(), beats[15]["speechEnd"] - 0.25, 0.90)

if __name__ == "__main__":
    mix_and_master(HERE, bgm_fn, sfx_fn)
