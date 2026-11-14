#!/usr/bin/env python3
"""Render a branded vertical Short from a voiceover and a spec.

    .venv/bin/python .claude/skills/video-shorts/scripts/render_short.py video-data/shorts/<slug>.json

Spec (JSON):
    eyebrow       series name shown in the top band, e.g. "What AI Gets Wrong"
    title         first title line
    title_accent  second title line, drawn in the accent colour
    audio         voiceover mp3, path relative to the repo root
    text          the exact text the voiceover speaks
    out           output mp4, relative to the repo root (default video-data/shorts/<slug>.mp4)
    timings       optional: JSON list of {"text","start","end"} word timings from a
                  transcription; without it, timings are estimated from the text

Brand colours come from brand.diagram.light in config.json, the brand name from
identity.brandName and the URL from channels.blog.url, so re-branding never touches
the template.

Nothing is written inside the skill folder. Render scratch (a copy of the voiceover,
the fonts, the props file) goes to <output.videoDir>/.cache/shorts/, which is safe to
delete; Remotion reads it through --public-dir.
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
REPO = SKILL.parents[2]
MAX_WORDS = 4          # words per caption card
PAUSE_COMMA = 0.18     # seconds of silence assumed after , ; :
PAUSE_STOP = 0.38      # after . ! ?
LEAD_IN = 0.08


def duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def playwright_shell() -> str | None:
    """Prefer the Chromium headless shell that ./setup.sh installs for Playwright.

    Remotion's own downloaded shell crashed on launch on macOS (icudtl.dat lookup)
    when run from a sandboxed shell; Playwright's build renders the same output.
    Falls back to Remotion's browser when Playwright's is not installed.
    """
    caches = [Path.home() / "Library/Caches/ms-playwright", Path.home() / ".cache/ms-playwright"]
    for cache in caches:
        hits = sorted(cache.glob("chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell"))
        if hits:
            return str(hits[-1])
    return None


def estimate_words(text: str, total: float) -> list[dict]:
    """Spread words across the audio by character weight, with pauses at punctuation."""
    words = text.split()
    pauses = [PAUSE_STOP if re.search(r"[.!?]$", w) else PAUSE_COMMA if re.search(r"[,;:]$", w) else 0
              for w in words]
    weights = [len(re.sub(r"\W", "", w)) + 2 for w in words]
    speak_time = total - LEAD_IN - sum(pauses[:-1])
    per_unit = speak_time / sum(weights)
    t, out = LEAD_IN, []
    for w, wt, p in zip(words, weights, pauses):
        end = t + wt * per_unit
        out.append({"text": w, "start": round(t, 3), "end": round(end, 3)})
        t = end + p
    return out


# Words a caption card should never end on: articles, prepositions, auxiliaries.
WEAK_END = {"a", "an", "the", "of", "to", "from", "in", "on", "at", "for", "with", "and",
            "or", "but", "it", "its", "is", "are", "was", "were", "can", "can't", "that",
            "this", "by", "as", "if", "so", "your", "my", "our", "their", "they", "we", "you"}


def bare(word: str) -> str:
    return re.sub(r"[^\w']", "", word).lower()


def to_phrases(words: list[dict]) -> list[dict]:
    """Chunk into 2-4 word cards at natural breaks.

    A card closes at punctuation, or at MAX_WORDS, or at a pause in the audio of
    more than 0.25s; it is pushed one word further when it would end on a weak word.
    """
    phrases, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        gap = (nxt["start"] - w["end"]) if nxt else 1
        punct = re.search(r"[.!?,;:]$", w["text"])
        full = len(cur) >= MAX_WORDS
        weak = bare(w["text"]) in WEAK_END
        if nxt is None or punct or gap > 0.25 or (full and not weak) or len(cur) >= MAX_WORDS + 1:
            phrases.append(cur)
            cur = []
    merged = []
    for p in phrases:  # fold one-word fragments into the previous card
        if merged and len(p) == 1 and len(merged[-1]) < MAX_WORDS and not re.search(r"[.!?]$", merged[-1][-1]["text"]):
            merged[-1].extend(p)
        else:
            merged.append(p)
    return [{"start": p[0]["start"], "end": p[-1]["end"], "words": p} for p in merged]


def align(text: str, timed: list[dict]) -> list[dict]:
    """Keep the script's exact words, take the timings from the transcription."""
    words = text.split()
    if len(words) != len(timed):
        sys.exit(f"timings have {len(timed)} words, text has {len(words)}; fix the spec text")
    return [{"text": w, "start": t["start"], "end": t["end"]} for w, t in zip(words, timed)]


def icon_markup(spec: dict) -> dict:
    """Inline the inner SVG of every Lucide icon the diagram uses, so colour is styleable."""
    names = {n["icon"] for n in spec.get("nodes", {}).values()} | {b["icon"] for b in spec.get("badges", [])}
    out = {}
    for n in names:
        f = SKILL / "assets" / "icons" / f"{n}.svg"
        if not f.exists():
            sys.exit(f"icon {n} missing: approve it with blog-images/scripts/pick_icon.py and copy it to assets/icons/")
        out[n] = re.search(r"<svg[^>]*>(.*)</svg>", f.read_text(), re.S).group(1).strip()
    return out


def chunk_by_spec(words: list[dict], chunks: list[str]) -> list[dict]:
    """Use the author's caption chunks exactly; they must cover the text word for word."""
    out, i = [], 0
    for c in chunks:
        n = len(c.split())
        part = words[i:i + n]
        if [w["text"] for w in part] != c.split():
            sys.exit(f"caption chunk {c!r} does not match the text at word {i}")
        out.append({"start": part[0]["start"], "end": part[-1]["end"], "words": part})
        i += n
    if i != len(words):
        sys.exit("caption chunks do not cover the whole text")
    return out


def main() -> None:
    spec_path = Path(sys.argv[1]).resolve()
    spec = json.loads(spec_path.read_text())
    config = json.loads((REPO / "config.json").read_text())
    light = config["brand"]["diagram"]["light"]

    audio_src = REPO / spec["audio"]
    total = duration(audio_src)
    words = (align(spec["text"], json.loads((REPO / spec["timings"]).read_text())) if spec.get("timings")
             else estimate_words(spec["text"], total))

    video_dir = config.get("output", {}).get("videoDir", "video-data")
    cache = REPO / video_dir / ".cache" / "shorts"
    public = cache / "public"
    (public / "audio").mkdir(parents=True, exist_ok=True)
    shutil.copytree(SKILL / "assets" / "fonts", public / "fonts", dirs_exist_ok=True)
    audio_name = f"audio/{spec_path.stem}{audio_src.suffix}"
    shutil.copy(audio_src, public / audio_name)

    blog = config["channels"]["blog"]["url"]
    props = {
        "brand": {k: light[k] for k in
                  ("canvas", "surface", "stroke", "textPrimary", "textMuted", "accentA", "accentB")}
                 | {"brandName": config["identity"]["brandName"],
                    "url": re.sub(r"^https?://", "", blog)},
        "eyebrow": spec["eyebrow"],
        "audio": audio_name,
        "durationSec": total,
        "phrases": chunk_by_spec(words, spec["chunks"]) if spec.get("chunks") else to_phrases(words),
        "emphasis": [bare(w) for w in spec.get("emphasis", [])],
        "headers": spec["headers"],
        "nodes": spec["nodes"],
        "states": spec["states"],
        "packets": spec.get("packets", []),
        "chips": spec.get("chips", []),
        "badges": spec.get("badges", []),
        "meters": spec.get("meters", []),
        "notes": spec.get("notes", []),
        "dividers": spec.get("dividers", []),
        "icons": icon_markup(spec),
    }
    work = cache / "props"
    work.mkdir(parents=True, exist_ok=True)
    props_path = work / f"{spec_path.stem}.props.json"
    props_path.write_text(json.dumps(props, indent=1))

    out = REPO / spec.get("out", f"video-data/shorts/{spec_path.stem}.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["npx", "remotion", "render", "src/index.ts", "Short", str(out),
           f"--props={props_path}", f"--public-dir={public}", "--codec=h264", "--log=error"]
    browser = playwright_shell()
    if browser:
        cmd.append(f"--browser-executable={browser}")
    subprocess.run(cmd, cwd=SKILL, check=True)
    print(out)


if __name__ == "__main__":
    main()
