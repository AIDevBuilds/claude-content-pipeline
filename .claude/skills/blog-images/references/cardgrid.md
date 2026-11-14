# Card-grid infographics

A fixed template for list-shaped ideas: numbered cards in a grid, a title band and a
one-line takeaway. Built for the LinkedIn and X feed, where a tall image that reads
at phone width earns more attention than a landscape diagram.

```bash
python3 .claude/skills/blog-images/scripts/render_cardgrid.py \
    blog-data/images/specs/<slug>.json blog-data/images/<slug>.svg
.claude/skills/blog-images/scripts/render_svg.sh \
    blog-data/images/<slug>.svg blog-data/images/<slug>.png 1080   # 1600 for landscape
```

Keep the JSON spec in `blog-data/images/specs/`; it is the editable source, the same
way the SVG is for hand-written diagrams. The spec format is documented at the top
of `scripts/render_cardgrid.py`.

## When to use it
- The idea is a list of 4 to 8 parallel items: kinds, failure modes, steps, checks.
- Each item can be said in a heading plus two short lines.
- Not for flows, stacks or two-way comparisons: those stay hand-written SVG.

## Sizes
- `portrait`, 1080×1350: LinkedIn and X posts. Default. 2 columns, up to 8 cards.
- `landscape`, 1600×900: blog inline or hero. 4 columns.

## Content rules
- The title is a claim (the post's hook); the descriptive label goes in the subtitle.
- Show the *what*, keep the *how* (worked example, code, procedure) for the article,
  so the image earns a click instead of replacing the read.
- Every card carries the same structure (same labels, same line count where possible),
  so the grid reads as one comparison.
- Lines stay under about 45 characters; the script wraps, but two wrapped lines per
  card is the limit before it reads as dense.
- Two accents maximum, as in palette.md. `tone` per card: `a`, `b`, or `muted` for a
  neutral case. `labels` colours a "Label:" prefix with the same tones, so the
  colour key lives on the cards themselves and no legend is needed.
- The footer is the post's one takeaway, in a single sentence. Exception (set 6 Nov
  2026): on a concept explainer (how something works inside, with claims taken from
  docs or a paper) the footer names the public source instead, for example
  "Sources: PostgreSQL docs (MVCC, vacuuming, hot standby)." The image travels
  without the post text, and a mechanism claim invites "says who?". Tradeoff and
  opinion cards keep the takeaway.
- Every fact on a card must come from the article or a verified source; the card
  is published content, under the same no-invented-facts rule as the draft.
- Icons are optional (`"icons": true` plus `"icon": "<name>"` per card). They are Lucide
  line icons (ISC licence) stored in `assets/icons/lucide/`, drawn in the card's tone.
  How to pick them:
  1. **Check `assets/icons/icon-map.json` first.** A concept that already has an approved
     icon always uses it, so "retrieval" looks the same in every post.
  2. **For a new concept, search:** `python3 .claude/skills/blog-images/scripts/pick_icon.py search "<words>"` lists Lucide
     icons whose name or tags match. Search only suggests; it does not decide.
  3. **Apply the fit test:** the icon must show the card's *mechanism or object* (a lock
     for access control, a wrench for tool calls), recognisable at 40px without the
     heading. Reject icons that only match a word ("rate" in "vibrate"), that are
     decorative (sparkles, rockets), or that could stand for several cards in the
     same image.
  4. **No icon is better than a wrong one.** If any card has no clear match, render
     the whole image without icons; a mix of icons and gaps looks unfinished.
  5. **Show the choices before rendering:** list card -> icon -> one-line reason for the
     author to approve, then record each new one with
     `python3 .claude/skills/blog-images/scripts/pick_icon.py approve "<concept>" <icon> "<reason>"` (downloads the icon
     from lucide-static 0.460.0 if it isn't local).

## Defaults for social posts (decided 24 Oct 2026)
Every social image uses `"theme": "light"`, `"frame": true` and `"icons": true`. Icons stay
on unless one card has no clear match, in which case the whole image goes without.

## Framed light layout
`"theme": "light", "frame": true` gives the house style: a dark top band
(`eyebrow_left` = series, `eyebrow_right` = topic), a two-tone headline (`title` plus
`title_accent`), a divider, the cards, a one-line takeaway, and a dark bottom band with
the brand line and blog URL from config in italics.
- The brand line (brand name and X handle) comes from config automatically.
