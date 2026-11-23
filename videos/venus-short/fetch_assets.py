"""Fetch real Venus NASA/JPL imagery into videos/venus-short/assets/."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.abspath(os.path.join(HERE, "..", "..", "90 Templates & Starter Kits", "orbit-2d-space-kit"))
sys.path.insert(0, KIT)

from fetch_nasa import search_and_download  # noqa: E402

QUERIES = [
    {
        "key": "venus_magellan",
        "q": "Magellan Venus",
        "prefer": ["PIA00104", "Magellan", "mosaic", "radar", "globe"],
        "exclude": ["illustration", "artist", "concept"],
    },
    {
        "key": "venus_clouds",
        "q": "PIA00072",
        "prefer": ["PIA00072", "Mariner", "clouds"],
        "exclude": ["illustration", "artist", "concept"],
    },
    {
        "key": "venus_volcano",
        "q": "Venus radar volcano",
        "prefer": ["Magellan", "Maat", "radar", "PIA"],
        "exclude": ["illustration", "artist", "concept"],
    },
]

if __name__ == "__main__":
    search_and_download(QUERIES, os.path.join(HERE, "assets"))
