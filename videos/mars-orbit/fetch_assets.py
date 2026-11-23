"""Fetch 5 real public-domain NASA/JPL Mars photos for videos/mars-orbit/assets/."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.abspath(os.path.join(HERE, "..", "..", "90 Templates & Starter Kits", "orbit-2d-space-kit"))
sys.path.insert(0, KIT)

from fetch_nasa import search_and_download

QUERIES = [
    {
        "key": "phoenix_scoop",
        "q": "PIA10745",
        "prefer": ["PIA10745", "Martian Soil Inside"],
        "exclude": ["artist", "illustration", "diagram", "selfie", "map"],
    },
    {
        "key": "opportunity_rover",
        "q": "Opportunity solar panels dust",
        "prefer": ["PIA15114", "PIA20329", "Self-Portrait", "Solar Panel"],
        "exclude": ["Stereo", "Anaglyph", "artist", "illustration", "cartoon"],
    },
    {
        "key": "alba_mons",
        "q": "Alba Mons",
        "prefer": ["PIA23933", "PIA23294", "Tectonics", "Alba"],
        "exclude": ["artist", "illustration", "cartoon"],
    },
    {
        "key": "cerberus_fossae",
        "q": "Cerberus Fossae",
        "prefer": ["PIA11323", "PIA04751", "Cerberus"],
        "exclude": ["artist", "illustration", "cartoon"],
    },
    {
        "key": "mars_globe",
        "q": "Mars Valles Marineris",
        "prefer": ["PIA02005", "Tharsis", "Valles"],
        "exclude": ["artist", "illustration", "rosette"],
    },
]

if __name__ == "__main__":
    assets_dir = os.path.join(HERE, "assets")
    manifest = search_and_download(QUERIES, assets_dir)
    print(f"\nSaved {len(manifest)} NASA photos to {assets_dir}")
