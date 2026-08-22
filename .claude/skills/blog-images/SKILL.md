---
name: blog-images
description: Generates on-brand technical diagrams and hero images for blog posts, written as hand-crafted SVG and rasterized to PNG via a local script — not an AI image generator. Called by blog-writer during drafting/finalizing whenever a post has a structural concept (a stack, a comparison, a flow, a decision) that a diagram would make clearer than prose alone. Can also be invoked standalone: "generate images for this post."
---

# Blog Images

## Why code, not an AI image generator
AI image generators drift stylistically from post to post — different palettes,
different linework, a different "vibe" each time, because nothing enforces
consistency between generations. Diagrams built as SVG from a fixed palette and a
fixed set of layout rules don't drift: the same input rules produce the same visual
language every time. That consistency is the entire point of this skill. Do not
fall back to an AI image generator even if one becomes available — hand-written SVG
is the method, not a workaround.

## Setup (once per machine)
```bash
./setup.sh          # from the repo root
```
This creates the shared `.venv` and checks that `cairosvg` can actually load the
native cairo library. If it reports cairo missing, install it (`brew install cairo`
on macOS, `apt-get install libcairo2` on Debian/Ubuntu) and re-run. `render_svg.sh`
prints the same guidance if it hits the problem later.

## Workflow

**1. Identify image opportunities from the draft/outline.**
Don't force a diagram where prose already does the job. Look specifically for:
- A concept that's inherently structural (a stack, a layered model, a pipeline).
- A comparison or contrast between exactly 2 things (a before/after, two primitives).
- A decision flow (if X, use Y; if not, use Z).

Typical output: one hero image (the post's core concept rendered visually) plus 0-2
inline diagrams for genuinely structural sections. More than that usually means the
post has too many ideas, not too few pictures.

**2. Write the SVG by hand.** Read `brand.diagram` in `config.json` at the repo root
for every colour — never invent a hex value inline, and never hardcode one that
should come from config. [references/palette.md](references/palette.md) explains
what each token is for and the layout rules that go with it. Target canvases:
- Hero image: 1600×840 (roughly matches common social-card proportions)
- Inline diagram: 1200×675, or taller if the content is a vertical stack

**3. Render to PNG:**
```bash
.claude/skills/blog-images/render_svg.sh \
    blog-data/images/<slug>.svg \
    blog-data/images/<slug>.png \
    1600
```
Save both the `.svg` source and the rendered `.png` under `blog-data/images/`
(the script creates the directory). Keep the SVG source — it is what makes the
diagram editable later instead of a dead asset.

**4. Wire it into the draft.** Add `![alt text](images/<slug>.png)` at the right spot
in `blog-data/draft.md`. The path stays relative to the draft's own folder, so it is
`images/<slug>.png` and not `blog-data/images/<slug>.png`. Alt text should describe
the diagram's content for a reader who can't see it (accessibility, and it's free
SEO) — not a generic caption like "diagram".

**5. Check it at reading size.** Read the PNG back and judge it at roughly 700px
wide, which is how it will appear inline. Text that is legible at 1600px can turn to
mush at inline width.

**6. Report back** a short list of every image generated: filename, intended
placement (hero / after which section), and the alt text used, so the user can
review before publishing.

## Style notes beyond the palette
- No emoji or icon fonts. If a diagram needs a symbol, draw it as a simple geometric
  shape (arrow, dot, bracket) consistent with the rest of the linework.
- Label things directly on the diagram rather than relying on a separate legend — if
  a legend feels necessary, the diagram is trying to show too much.
- Text should hold up scaled down, not just at full canvas size.
