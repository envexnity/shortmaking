"""Fetch real NASA / JPL / Spitzer / Chandra Black Hole imagery into videos/black-hole-short/assets/."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.abspath(os.path.join(HERE, "..", "..", "90 Templates & Starter Kits", "orbit-2d-space-kit"))
sys.path.insert(0, KIT)

from fetch_nasa import search_and_download  # noqa: E402

QUERIES = [
    {
        "key": "m87_eht",
        "q": "PIA23122",
        "prefer": ["PIA23122", "Messier 87"],
        "exclude": ["logo", "portrait"],
    },
    {
        "key": "m87_jet",
        "q": "PIA20865",
        "prefer": ["PIA20865", "Black Hole"],
        "exclude": ["logo", "portrait"],
    },
    {
        "key": "sgra_center",
        "q": "PIA25440",
        "prefer": ["PIA25440", "Black Hole"],
        "exclude": ["logo", "portrait"],
    },
]

if __name__ == "__main__":
    search_and_download(QUERIES, os.path.join(HERE, "assets"))
