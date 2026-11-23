"""Custom 8-bit Chiptune Score & SFX for ocean-bottom-8bit-short."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "scripts", "pixel_short_kit")))
from audio_mix import (
    mix_and_master, place, synth_segmented_bgm,
    synth_chip_pop, synth_bubble_bloop, synth_impact_zap, synth_shimmer, synth_coin_clink,
)

SEGMENTS = [
    {"start_beat": 0, "end_beat": 3, "melody": [72, 76, 79, 76, 74, 77, 81, 77], "bass": [48, 48, 55, 48, 53, 53, 48, 53], "duty": 0.25},
    {"start_beat": 4, "end_beat": 8, "melody": [69, 72, 76, 72, 67, 71, 74, 71], "bass": [45, 45, 52, 45, 43, 43, 50, 43], "bell": True},
    {"start_beat": 9, "end_beat": 12, "melody": [65, 69, 72, 76, 67, 71, 74, 79], "bass": [41, 41, 48, 41, 43, 43, 50, 43], "duty": 0.125},
    {"start_beat": 13, "end_beat": 15, "melody": [64, 0, 60, 0, 62, 0, 59, 0], "bass": [45, 0, 41, 0, 43, 0, 40, 0], "duty": 0.25, "hat": False},
]

def bgm_fn(total_sec, beats):
    return synth_segmented_bgm(total_sec, beats, SEGMENTS, bpm=138.0, seed=44)

def sfx_fn(sfx, beats, libs):
    place(sfx, synth_chip_pop(780, 1560, 0.14), beats[3]["start"], 0.65)
    place(sfx, synth_bubble_bloop(), beats[4]["start"] + 0.15, 0.80)
    place(sfx, synth_bubble_bloop(), beats[5]["start"], 0.75)
    place(sfx, synth_impact_zap(720, 90, 0.26), beats[7]["start"], 0.80)
    place(sfx, synth_shimmer((784, 987, 1174)), beats[9]["start"] + 0.10, 0.65)
    place(sfx, libs["ui_click"], beats[12]["start"] - 0.10, 0.95)
    place(sfx, libs["riser_hit"][-42000:], beats[12]["start"], 0.55)
    place(sfx, synth_coin_clink(), beats[15]["speechEnd"] - 0.25, 0.80)

if __name__ == "__main__":
    mix_and_master(HERE, bgm_fn, sfx_fn)
