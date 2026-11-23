"""Custom 8-bit Chiptune Score & SFX for cb-20261123-1 (5 Billionaires Build SI)."""
import os
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "scripts", "pixel_short_kit")))
from audio_mix import (
    SR, mix_and_master, place, pulse_wave, tri_wave, midi_hz,
    synth_chip_pop, synth_impact_zap, synth_shimmer, synth_overdrive_riser,
    synth_coin_clink, synth_bubble_bloop, synth_roar_rumble,
)

SEGMENTS = [
    {"start_beat": 0, "end_beat": 2, "melody": [69, 72, 76, 81, 76, 72, 74, 79], "bass": [45, 45, 52, 45, 48, 48, 43, 48], "duty": 0.25},
    {"start_beat": 3, "end_beat": 6, "melody": [71, 75, 78, 83, 78, 75, 76, 81], "bass": [47, 47, 54, 47, 50, 50, 45, 50], "duty": 0.50},
    {"start_beat": 7, "end_beat": 9, "melody": [72, 76, 79, 84, 79, 76, 77, 81], "bass": [48, 48, 55, 48, 53, 53, 48, 53], "bell": True},
    {"start_beat": 10, "end_beat": 12, "melody": [74, 77, 81, 86, 81, 77, 79, 84], "bass": [50, 50, 57, 50, 55, 55, 50, 55], "duty": 0.25},
]


def bgm_fn(total_sec, beats):
    """High-energy 150 BPM arcade synth without artificial beat-1 dropout."""
    n_total = int(total_sec * SR)
    bgm = np.zeros(n_total, np.float32)
    step_dur = 60.0 / 150.0 / 2.0
    steps = int(total_sec / step_dur) + 1
    rng = np.random.default_rng(777)

    for s in range(steps):
        ts = s * step_dur
        if ts >= total_sec:
            break
        seg = SEGMENTS[-1]
        for cand in SEGMENTS:
            t0 = beats[cand["start_beat"]]["start"] if cand["start_beat"] < len(beats) else total_sec
            t1 = beats[cand["end_beat"]]["end"] if cand["end_beat"] < len(beats) else total_sec + 1.0
            if t0 <= ts < t1:
                seg = cand
                break

        i0 = int(ts * SR)
        sn = min(int(step_dur * SR), n_total - i0)
        if sn <= 10:
            continue
        tt = np.arange(sn, dtype=np.float32) / SR
        env = np.exp(-tt * 7.8)
        m_note = seg["melody"][s % len(seg["melody"])]
        b_note = seg["bass"][s % len(seg["bass"])]

        if m_note > 0:
            if seg.get("bell"):
                lead = (
                    np.sin(2 * np.pi * midi_hz(m_note) * tt)
                    + 0.4 * np.sin(2 * np.pi * midi_hz(m_note + 12) * tt)
                ) * np.exp(-tt * 6.0) * 0.20
            else:
                lead = pulse_wave(np.full(sn, midi_hz(m_note), np.float32), seg.get("duty", 0.25)) * env * 0.22
            bgm[i0:i0 + sn] += lead
        if b_note > 0:
            bass = tri_wave(np.full(sn, midi_hz(b_note), np.float32)) * np.exp(-tt * 3.5) * 0.34
            bgm[i0:i0 + sn] += bass
        if s % 2 == 1:
            hat = rng.standard_normal(sn).astype(np.float32) * np.exp(-tt * 42.0) * 0.11
            bgm[i0:i0 + sn] += hat
    return bgm


def sfx_fn(sfx, beats, libs):
    # Pre-cut whooshes on major contestant switches (2-4 frames before cut)
    for bi in [1, 3, 5, 7, 8, 10, 11, 12]:
        if bi < len(beats):
            place(sfx, libs["whoosh"], beats[bi]["start"] - 0.08, 0.55)

    place(sfx, synth_coin_clink(), beats[0]["speechEnd"] - 0.35, 0.75)
    place(sfx, synth_chip_pop(700, 1500, 0.14), beats[1]["start"] + 0.05, 0.70)
    place(sfx, synth_bubble_bloop(0.24), beats[2]["start"] + 0.15, 0.80)
    place(sfx, synth_overdrive_riser(0.45), beats[3]["start"] + 0.10, 0.65)
    place(sfx, synth_roar_rumble(0.50), beats[4]["start"] + 0.10, 0.80)
    place(sfx, synth_overdrive_riser(0.50), beats[5]["start"] + 0.15, 0.70)
    place(sfx, synth_impact_zap(1100, 85, 0.32), beats[6]["speechEnd"] - 0.30, 0.95)
    place(sfx, synth_chip_pop(540, 1180, 0.12), beats[7]["start"] + 0.12, 0.75)
    place(sfx, synth_shimmer((1046, 1318, 1568, 2093)), beats[8]["start"] + 0.08, 0.75)
    place(sfx, libs["ui_click"], beats[9]["start"] + (beats[9]["end"] - beats[9]["start"]) * 0.48, 0.90)
    place(sfx, synth_bubble_bloop(0.26), beats[10]["speechEnd"] - 0.35, 0.85)
    place(sfx, libs["riser_hit"][-42000:], beats[12]["start"] - 0.15, 0.65)
    place(sfx, synth_coin_clink(), beats[12]["speechEnd"] - 0.25, 0.95)


if __name__ == "__main__":
    mix_and_master(HERE, bgm_fn, sfx_fn)
