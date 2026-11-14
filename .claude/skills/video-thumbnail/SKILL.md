---
name: video-thumbnail
description: Renders a branded 1280x720 YouTube thumbnail PNG from a fixed HTML template via headless Chromium — not an AI image generator. Called by video-scriptwriter once the thumbnail text and visual direction are decided, or standalone: "generate the thumbnail for this video."
---

# Video Thumbnail

## Why a template, not an AI image generator
Same reasoning as the `blog-images` skill: generated images drift in style between
runs, and a channel's thumbnails have to look like a set. A fixed HTML template
with configurable text slots produces the same visual language every time. Do not
substitute an AI image generator even if one is available.

## Setup (once per machine)
```bash
./setup.sh          # from the repo root — creates .venv and fetches Chromium
```
Everything else is already in the skill folder: `assets/template.html` and the
embedded Inter webfont under `assets/fonts/`. The script is `scripts/generate_thumbnail.py`;
`examples/example-output.png` shows what it produces.

## What is configurable, and where
Brand colours and the channel tag come from `brand.thumbnail` and
`identity.brandName` in `config.json` at the repo root. `assets/template.html` reads them
as CSS custom properties, so **re-branding means editing `config.json`, never the
template**. Layout changes (positions, sizes, which panels show) do belong in
`assets/template.html`.

## Workflow

**1. Get the text from the SEO package.** `video-scriptwriter` already decides the
overlay text and visual direction and writes them into `video-data/youtube-seo.md`.
Use those values rather than inventing new ones. If that file does not exist yet,
stop and generate it first — a thumbnail written independently of the title tends
to fight it.

**2. Choose the right panel.** Two options, and the choice matters:
- `--code` renders a syntax-styled code snippet, with `--bugline` highlighting the
  offending line in the bug colour. Use this when the video's payoff is a specific
  line of code. Keep it to 4-6 short lines; 10 is the hard cap and anything dense
  turns to mush at sidebar size.
- `--screenshot` drops in an image instead. Use for a face cam frame or a real
  editor screenshot.

**3. Render:**
```bash
.venv/bin/python .claude/skills/video-thumbnail/scripts/generate_thumbnail.py \
    --video 01 \
    --tag "SYSTEM DESIGN" \
    --prefix "// when the cache lies" \
    --title "STALE\nREADS" \
    --highlight "STALE" \
    --subtitle "Cache-aside · TTLs · invalidation" \
    --tools "Redis,PostgreSQL,Python" \
    --active-tool "Redis" \
    --badge-number "2" \
    --badge-label "fixes\nshown" \
    --code "def get(key):\n  v = cache.get(key)\n  if v is None:\n    v = db.read(key)\n    cache.set(key, v)\n  return v" \
    --bugline "cache.set(key, v)"
```
Output lands at `video-data/images/thumbnail-<video>.png` at exactly 1280x720.

**4. Check it at real size.** Read the PNG back and judge it scaled down to roughly
320px wide, which is how most viewers meet it. If the headline is unreadable there,
it is too long — cut words rather than shrinking the font.

**5. Report back**: the output path, the exact text used, and one line on whether
it holds up at sidebar size.

## Copy rules for the overlay text
- `--title`: 2-4 words per line, 2 lines max. It is a headline, not a sentence.
- `--highlight`: the single phrase carrying the tension. Highlighting everything
  highlights nothing.
- Never restate the video title verbatim. The thumbnail and title should do
  different work: title carries the search keywords, thumbnail carries the hook.
- No hype punctuation. No "!!!", no "SHOCKING". The channel's credibility is the
  product; a clickbait thumbnail spends it.
- `--badge-number` should be a real number from the video (bugs found, minutes
  taken). Never invent one to make the badge look better.

## Rendering notes worth preserving
These are deliberate and should survive future edits:
- Rendered at `device_scale_factor=2` then LANCZOS-downsampled to 1280x720, so
  YouTube skips its own softer downscaler and only applies JPEG compression.
- The background grid and glow layers are disabled on purpose. Fine lines and soft
  gradients waste YouTube's ~14KB grid-thumbnail JPEG budget and blur the headline.
- The headline carries a hard multi-directional text outline rather than a soft
  shadow, because soft shadows smear through recompression.
