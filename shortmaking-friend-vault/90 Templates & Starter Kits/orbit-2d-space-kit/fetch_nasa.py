"""Fetch real public-domain NASA/JPL images from images-api.nasa.gov with Windows SSL fallback."""
import json
import os
import re
import ssl
import sys
import urllib.parse
import urllib.request

UNVERIFIED_CTX = ssl._create_unverified_context()


def _get_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "OrbitSpaceVideoKit/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        with urllib.request.urlopen(req, timeout=20, context=UNVERIFIED_CTX) as resp:
            return json.loads(resp.read().decode("utf-8"))


def _download(url: str, dest: str):
    req = urllib.request.Request(url, headers={"User-Agent": "OrbitSpaceVideoKit/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
    except Exception:
        with urllib.request.urlopen(req, timeout=30, context=UNVERIFIED_CTX) as resp:
            data = resp.read()
    with open(dest, "wb") as f:
        f.write(data)


def search_and_download(queries: list[dict], out_dir: str) -> list[dict]:
    """
    queries: list of {"key": "phoenix_scoop", "q": "Phoenix lander scoop soil Mars", "prefer": ["PIA", "soil", "scoop"]}
    """
    os.makedirs(out_dir, exist_ok=True)
    manifest = []

    for spec in queries:
        key = spec["key"]
        q = spec["q"]
        url = f"https://images-api.nasa.gov/search?{urllib.parse.urlencode({'q': q, 'media_type': 'image'})}"
        data = _get_json(url)
        items = data.get("collection", {}).get("items", [])
        if not items:
            print(f"[WARN] No NASA API results for '{q}'", file=sys.stderr)
            continue

        # Score candidates so preferred keywords or clean PIA IDs rank first
        prefers = [p.lower() for p in spec.get("prefer", [])]
        excludes = [e.lower() for e in spec.get("exclude", ["artist", "illustration", "concept", "diagram"])]

        def score_item(it):
            d = (it.get("data") or [{}])[0]
            blob = " ".join([
                d.get("nasa_id", ""),
                d.get("title", ""),
                d.get("description", ""),
            ]).lower()
            s = 0
            for p in prefers:
                if p in blob:
                    s += 10
            for ex in excludes:
                if ex in blob:
                    s -= 25
            if d.get("nasa_id", "").startswith("PIA"):
                s += 3
            return s

        ranked = sorted(items[:25], key=score_item, reverse=True)
        chosen = None
        img_url = None

        for cand in ranked[:8]:
            href = None
            if cand.get("href"):
                try:
                    assets = _get_json(cand["href"])
                    for suffix in ("~large.jpg", "~medium.jpg", "~small.jpg", "~orig.jpg", ".jpg"):
                        href = next((a for a in assets if a.lower().endswith(suffix)), None)
                        if href:
                            break
                except Exception:
                    pass
            if not href:
                links = cand.get("links") or []
                href = next((l["href"] for l in links if l.get("render") == "image"), None)
            if href:
                chosen = cand
                img_url = href
                break

        if not chosen or not img_url:
            print(f"[WARN] No downloadable image URL for '{key}'", file=sys.stderr)
            continue

        meta = (chosen.get("data") or [{}])[0]
        dest = os.path.join(out_dir, f"{key}.jpg")
        try:
            _download(img_url, dest)
        except Exception:
            # Fallback to original href link
            fallback_href = next((l["href"] for l in (chosen.get("links") or []) if l.get("render") == "image"), img_url)
            _download(fallback_href, dest)
            img_url = fallback_href

        credit = meta.get("secondary_creator") or meta.get("photographer") or meta.get("center") or "NASA"
        if "NASA" not in credit.upper():
            center = meta.get("center", "JPL")
            credit = f"NASA/{center}/{credit}".strip("/")

        entry = {
            "key": key,
            "query": q,
            "nasa_id": meta.get("nasa_id", ""),
            "title": meta.get("title", ""),
            "date_created": (meta.get("date_created") or "")[:10],
            "center": meta.get("center", ""),
            "credit": credit,
            "source_url": f"https://images.nasa.gov/details/{meta.get('nasa_id', '')}",
            "image_url": img_url,
            "local_file": dest,
            "bytes": os.path.getsize(dest),
        }
        manifest.append(entry)
        print(f"[OK] {key}: {entry['nasa_id']} ({entry['bytes'] // 1024} KB) — {entry['credit']}")

    manifest_path = os.path.join(out_dir, "nasa_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    return manifest


if __name__ == "__main__":
    # CLI smoke test: python fetch_nasa.py out_dir "Mars Phoenix soil" "Mars Opportunity rover"
    if len(sys.argv) < 3:
        print("Usage: python fetch_nasa.py <out_dir> <query1> [<query2> ...]")
        sys.exit(1)
    out = sys.argv[1]
    qs = [{"key": f"img_{i}", "q": q} for i, q in enumerate(sys.argv[2:])]
    search_and_download(qs, out)
