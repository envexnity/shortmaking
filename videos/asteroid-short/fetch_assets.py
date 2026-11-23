"""Fetch real NASA Asteroid / Impact / Crater imagery into videos/asteroid-short/assets/."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.abspath(os.path.join(HERE, "..", "..", "90 Templates & Starter Kits", "orbit-2d-space-kit"))
sys.path.insert(0, KIT)

from fetch_nasa import search_and_download  # noqa: E402

QUERIES = [
    {
        "key": "bennu_rubble",
        "q": "PIA23555",
        "prefer": ["PIA23555", "Bennu"],
        "exclude": ["logo", "portrait"],
    },
    {
        "key": "dart_impact",
        "q": "PIA02122",
        "prefer": ["PIA02122", "Hubble"],
        "exclude": ["logo", "portrait"],
    },
    {
        "key": "asteroid_crater",
        "q": "PIA03490",
        "prefer": ["PIA03490", "Meteor Crater"],
        "exclude": ["logo", "portrait"],
    },
]

if __name__ == "__main__":
    search_and_download(QUERIES, os.path.join(HERE, "assets"))
