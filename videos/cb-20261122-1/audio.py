"""Custom 8-bit Chiptune Score & SFX for cb-20261122-1 (Lightning Bolt)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "scripts", "pixel_short_kit")))
from audio_mix import (
    mix_and_master, place, synth_segmented_bgm,
    synth_chip_pop, synth_impact_zap, synth_shimmer, synth_overdrive_riser, synth_coin_clink, synth_roar_rumble,
)

SEGMENTS = [
    {"start_beat": 0, "end_beat": 3, "melody": [69, 72, 76, 72, 71, 74, 77, 74], "bass": [45, 45, 52, 45, 50, 50, 45, 50], "duty": 0.25},
    {"start_beat": 4, "end_beat": 8, "melody": [72, 75, 79, 84, 82, 79, 75, 72], "bass": [48, 48, 55, 48, 48, 48, 55, 48], "duty": 0.50},
    {"start_beat": 9, "end_beat": 12, "melody": [74, 77, 81, 86, 84, 81, 77, 74], "bass": [50, 50, 57, 50, 50, 50, 57, 50], "bell": True},
    {"start_beat": 13, "end_beat": 15, "melody": [64, 0, 60, 0, 59, 0, 57, 0], "bass": [45, 0, 41, 0, 43, 0, 40, 0], "duty": 0.25, "hat": False},
]

def bgm_fn(total_sec, beats):
    return synth_segmented_bgm(total_sec, beats, SEGMENTS, bpm=148.0, seed=101)

def sfx_fn(sfx, beats, libs):
    place(sfx, synth_chip_pop(740, 1520, 0.14), beats[3]["start"], 0.65)
    place(sfx, synth_overdrive_riser(0.50), beats[4]["start"] + 0.08, 0.65)
    place(sfx, synth_impact_zap(1300, 95, 0.30), beats[7]["start"], 0.90)
    place(sfx, synth_roar_rumble(0.45), beats[8]["start"] + 0.55, 0.70)
    place(sfx, synth_shimmer((1046, 1318, 1760)), beats[9]["start"] + 0.08, 0.68)
    place(sfx, libs["ui_click"], beats[12]["start"] - 0.10, 0.95)
    place(sfx, synth_impact_zap(1500, 65, 0.34), beats[12]["start"], 0.95)
    place(sfx, synth_coin_clink(), beats[15]["speechEnd"] - 0.25, 0.90)

if __name__ == "__main__":
    mix_and_master(HERE, bgm_fn, sfx_fn)
