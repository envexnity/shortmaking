"""Voice & word-level timing generator for cb-20261123-1 (5 Billionaires Build SI)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "scripts", "pixel_short_kit")))
import voice_gen

# Register distinct voices for all 6 speakers (Host + 5 AI Billionaires)
voice_gen.DEFAULT_VOICES.update({
    "host": {
        "voice_id": "TX3LPaxmHKxFdv7VOQHJ",  # Liam
        "edge_voice": "en-AU-WilliamNeural",
        "edge_rate": "+8%",
        "edge_pitch": "+2Hz",
        "speed": 1.15,
        "stability": 0.40,
        "similarity": 0.80,
        "style": 0.25,
        "gap_after": 0.12,
    },
    "sam": {
        "voice_id": "bIHbv24MWmeRgasZH58o",  # Will
        "edge_voice": "en-US-GuyNeural",
        "edge_rate": "+10%",
        "edge_pitch": "+4Hz",
        "speed": 1.15,
        "stability": 0.36,
        "similarity": 0.80,
        "style": 0.30,
        "gap_after": 0.10,
    },
    "jensen": {
        "voice_id": "pNInz6obpgDQGcFmaJgB",  # Adam
        "edge_voice": "en-US-ChristopherNeural",
        "edge_rate": "+6%",
        "edge_pitch": "-4Hz",
        "speed": 1.14,
        "stability": 0.45,
        "similarity": 0.80,
        "style": 0.24,
        "gap_after": 0.10,
    },
    "elon": {
        "voice_id": "N2lVS1w4EtoT3dr4eOWO",  # Callum
        "edge_voice": "en-US-EricNeural",
        "edge_rate": "+9%",
        "edge_pitch": "-2Hz",
        "speed": 1.15,
        "stability": 0.40,
        "similarity": 0.80,
        "style": 0.28,
        "gap_after": 0.10,
    },
    "zuck": {
        "voice_id": "IKne3meq5aSn9XLyUdCD",  # Charlie
        "edge_voice": "en-US-AndrewNeural",
        "edge_rate": "+12%",
        "edge_pitch": "+6Hz",
        "speed": 1.16,
        "stability": 0.38,
        "similarity": 0.80,
        "style": 0.26,
        "gap_after": 0.10,
    },
    "dario": {
        "voice_id": "pqHfZKP75CvOlQylNhV4",  # Bill
        "edge_voice": "en-GB-ThomasNeural",
        "edge_rate": "+8%",
        "edge_pitch": "0Hz",
        "speed": 1.14,
        "stability": 0.42,
        "similarity": 0.80,
        "style": 0.22,
        "gap_after": 0.10,
    },
})

SPEAKER_MAP = {k: k for k in ("host", "sam", "jensen", "elon", "zuck", "dario")}

CUSTOM_GAPS = {
    0: 0.12,
    1: 0.08,
    2: 0.12,
    3: 0.08,
    4: 0.14,
    5: 0.08,
    6: 0.14,
    7: 0.12,
    8: 0.08,
    9: 0.14,
    10: 0.12,
    11: 0.14,
    12: 0.05,
}

if __name__ == "__main__":
    voice_gen.generate_project_voice(HERE, SPEAKER_MAP, CUSTOM_GAPS)
