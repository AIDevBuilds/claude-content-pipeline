#!/usr/bin/env python3
"""
Find Lucide icons for a concept, and record the ones chosen.

    pick_icon.py search "rate limit"        candidates, best match first
    pick_icon.py approve "rate limiting" gauge "throughput dial; limits = how fast"

Icons are picked against icon-map.json first: a concept that already has an
approved icon always gets the same one, so a series reads consistently. Only a
new concept goes to search, and its choice is recorded with the reason.
"""
import json
import sys
import urllib.request
from pathlib import Path

ICONS = Path(__file__).resolve().parents[1] / "assets" / "icons"
LUCIDE = ICONS / "lucide"
MAP = ICONS / "icon-map.json"
VERSION = "0.460.0"


def load_map() -> dict:
    return json.loads(MAP.read_text()) if MAP.is_file() else {}


def search(query: str) -> None:
    approved = load_map()
    q = query.lower()
    for concept, entry in approved.items():
        if q in concept or concept in q:
            print(f"APPROVED  {concept} -> {entry['icon']}  ({entry['why']})")
    tags = json.loads((LUCIDE / "tags.json").read_text())
    words = q.split()
    scored = []
    for name, kw in tags.items():
        name_words = set(name.split("-"))
        tag_words = set(" ".join(kw).replace("-", " ").split())
        score = sum(3 if w in name_words else 1 for w in words if w in name_words | tag_words)
        if score:
            scored.append((score, name, kw))
    for score, name, kw in sorted(scored, key=lambda s: -s[0])[:12]:
        have = "local" if (LUCIDE / f"{name}.svg").is_file() else "fetch"
        print(f"{score:>2}  {name:<28} [{have}]  {', '.join(kw[:6])}")


def approve(concept: str, icon: str, why: str) -> None:
    path = LUCIDE / f"{icon}.svg"
    if not path.is_file():
        url = f"https://unpkg.com/lucide-static@{VERSION}/icons/{icon}.svg"
        data = urllib.request.urlopen(url, timeout=20).read().decode()
        if "<script" in data or "href" in data:
            sys.exit(f"ERROR: {icon}.svg contains script or links; not saved")
        path.write_text(data)
    m = load_map()
    m[concept.lower()] = {"icon": icon, "why": why}
    MAP.write_text(json.dumps(dict(sorted(m.items())), indent=2) + "\n")
    print(f"approved {concept} -> {icon}")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "search":
        search(" ".join(sys.argv[2:]))
    elif len(sys.argv) == 5 and sys.argv[1] == "approve":
        approve(*sys.argv[2:])
    else:
        print(__doc__)
        sys.exit(64)
