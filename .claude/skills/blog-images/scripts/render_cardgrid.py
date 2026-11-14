#!/usr/bin/env python3
"""
Card-grid infographic: a JSON spec in, an on-brand SVG out.

    render_cardgrid.py spec.json out.svg

The layout is fixed (title band, numbered cards in a grid, footer) and every
colour comes from `brand.diagram` in config.json, so every infographic made with
it looks like part of the same set. That is the same reason the skill writes SVG
by hand rather than using an image model: nothing here can drift between runs.

Spec shape (see references/cardgrid.md for the rules on content):

    {
      "title": "8 kinds of AI guardrail",
      "subtitle": "and which family carries the weight",
      "size": "portrait",                 # portrait 1080x1350 | landscape 1600x900
      "columns": 2,                       # optional; default 2 portrait, 4 landscape
      "cards": [
        {"heading": "Input",
         "lines": ["Detector: injection classifier", "Control: length cap"],
         "tag": "Detector carries it", "tone": "b"}   # tone: a | b | muted
      ],
      "labels": {"Control": "a", "Detector": "b"},  # optional: colour "Label:" prefixes
      "lead": true,                       # optional: first line of each card in its accent
      "footer": "If the model's output can influence the decision, it's a detector.",
      "theme": "light",                   # optional: use brand.diagram.light
      "frame": true,                      # optional: dark top/bottom bands
      "eyebrow_left": "Terms & Tools", "eyebrow_right": "AI guardrails",
      "title_accent": "second headline line in the accent colour",
      "icons": true                       # optional: per-card "icon": "<lucide name>"
    }

Only the standard library is used, so this runs on any python3.
"""

import json
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

SIZES = {"portrait": (1080, 1350), "landscape": (1600, 900)}
MARGIN = 48
GAP = 20
RADIUS = 8
STROKE_W = 1.5
# Bold and italic work once render_font() hands cairo a single family name.
BOLD = 700


def find_config(start: Path) -> dict:
    for folder in [start, *start.parents]:
        candidate = folder / "config.json"
        if candidate.is_file():
            return json.loads(candidate.read_text())
    sys.exit("ERROR: config.json not found above " + str(start))


def wrap(text: str, max_chars: int) -> list:
    """Greedy word wrap. Width is estimated from character count, which holds for
    the system sans-serif stack at these sizes; check the PNG anyway."""
    words, lines, current = text.split(), [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= max_chars or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


ICON_DIR = Path(__file__).resolve().parents[1] / "assets" / "icons" / "lucide"


def render_font(stack: str) -> str:
    """cairosvg passes font-family straight to cairo, which cannot read a CSS
    fallback list: given one it silently uses a default face with no bold or
    italic. Use the first named family from the config stack instead."""
    skip = {"-apple-system", "blinkmacsystemfont", "system-ui", "sans-serif", "serif"}
    for part in stack.split(","):
        name = part.strip().strip('"').strip("'")
        if name and name.lower() not in skip:
            return name
    return "sans-serif"


def icon_el(name, x, y, size, color):
    """A Lucide icon (24x24 line art) at (x, y), scaled to size, stroked in color."""
    src = ICON_DIR / f"{name}.svg"
    if not src.is_file():
        sys.exit(f"ERROR: icon '{name}' not found in {ICON_DIR}")
    body = re.findall(r"<(?:path|line|polyline|polygon|circle|ellipse|rect)\b[^>]*/>", src.read_text())
    s = size / 24
    return (f'<g transform="translate({x:.1f},{y:.1f}) scale({s:.3f})" fill="none" '
            f'stroke="{color}" stroke-width="2" stroke-linecap="round" '
            f'stroke-linejoin="round">{"".join(body)}</g>')


def text_el(x, y, content, size, fill, font, weight=400, anchor="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family={quoteattr(font)} '
            f'font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}">{escape(content)}</text>')


def build(spec: dict, palette: dict, brand_line: str, site: str = "") -> str:
    width, height = SIZES[spec.get("size", "portrait")]
    portrait = width < height
    font = render_font(palette["fontStack"])
    tones = {"a": palette["accentA"], "b": palette["accentB"],
             "muted": palette["textMuted"]}
    used_accents = {c.get("tone", "a") for c in spec["cards"]} - {"muted"}
    if len(used_accents) > 2:
        sys.exit("ERROR: more than two accents; split the infographic.")

    cards = spec["cards"]
    labels = spec.get("labels", {})          # e.g. {"Control": "a", "Detector": "b"}
    cols = spec.get("columns", 2 if portrait else 4)
    rows = -(-len(cards) // cols)

    s = 1.0 if portrait else 1.05          # type scale
    title_size, sub_size = round(54 * s), round(26 * s)
    head_size, body_size, tag_size = round(28 * s), round(21 * s), round(18 * s)
    footer_size = round(22 * s)

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
           f'height="{height}" viewBox="0 0 {width} {height}">',
           f'<rect width="{width}" height="{height}" fill="{palette["canvas"]}"/>']

    # Framed layout: a dark band top and bottom, the same on every image, so
    # the series reads as a set (eyebrow labels top, brand and site bottom).
    frame = spec.get("frame", False)
    band = 64 if frame else 0
    if frame:
        title_size = round(title_size * 0.85)   # the bands take room; keep the grid readable
    band_fill, band_text = palette["textPrimary"], palette["canvas"]
    if frame:
        out.append(f'<rect width="{width}" height="{band}" fill="{band_fill}"/>')
        for txt, x, anchor in ((spec.get("eyebrow_left", ""), MARGIN, "start"),
                               (spec.get("eyebrow_right", ""), width - MARGIN, "end")):
            if txt:
                out.append(f'<text x="{x}" y="{band / 2 + 6:.1f}" font-family={quoteattr(font)} '
                           f'font-size="17" font-weight="{BOLD}" letter-spacing="2" '
                           f'fill="{band_text}" text-anchor="{anchor}">{escape(txt.upper())}</text>')

    # Title block: headline, optional accent second line, subtitle
    y = band + MARGIN + title_size
    for line in wrap(spec["title"], int((width - 2 * MARGIN) / (title_size * 0.5))):
        out.append(text_el(MARGIN, y, line, title_size, palette["textPrimary"], font, BOLD))
        y += title_size * 1.15
    if spec.get("title_accent"):
        for line in wrap(spec["title_accent"], int((width - 2 * MARGIN) / (title_size * 0.5))):
            out.append(text_el(MARGIN, y, line, title_size, palette["accentA"], font, BOLD))
            y += title_size * 1.15
    if spec.get("subtitle"):
        out.append(text_el(MARGIN, y + 4, spec["subtitle"], sub_size, palette["textMuted"], font))
        y += sub_size + 8
    if frame:
        y += 18
        out.append(f'<line x1="{MARGIN}" y1="{y:.1f}" x2="{width - MARGIN}" y2="{y:.1f}" '
                   f'stroke="{palette["stroke"]}" stroke-width="{STROKE_W}"/>')
    grid_top = y + 28

    # Takeaway: as large as fits on one line (down to 20px), then wrap; the
    # grid gets whatever height is left.
    footer_size = round(footer_size * 1.3)
    fchars = lambda size: int((width - 2 * MARGIN) / (size * 0.55))
    while footer_size > 20 and len(wrap(spec.get("footer", ""), fchars(footer_size))) > 1:
        footer_size -= 1
    footer_lines = wrap(spec.get("footer", ""), fchars(footer_size))
    footer_h = 22 + len(footer_lines) * footer_size * 1.25 + (14 if frame else 30)
    footer_top = height - (band + 8 if frame else MARGIN) - footer_h
    grid_bottom = footer_top - 24

    card_w = (width - 2 * MARGIN - (cols - 1) * GAP) / cols
    card_h = (grid_bottom - grid_top - (rows - 1) * GAP) / rows

    # Fit the type to the busiest card: shrink in steps rather than let a tag
    # overlap text. If it still doesn't fit at 80%, the card says too much.
    rad = 18

    def needed(card, head, body):
        head_lines = wrap(card["heading"], int((card_w - 48 - 2 * rad - 14) / (head * 0.55)))
        chars = int((card_w - 48) / (body * 0.52))
        h = 24 + 36 + 22 + (len(head_lines) - 1) * head * 1.15
        for line in card.get("lines", []):
            h += len(wrap(line, chars)) * body * 1.3 + body * 0.35
        side_tag = cols == 1 and not spec.get("icons")
        return h + (52 if card.get("tag") and not side_tag else 20)

    # Scale goes up as well as down: a two-card layout should fill its cards
    # rather than leave half of each one empty at phone size.
    base_head, base_body, base_tag = head_size, body_size, tag_size
    for step in range(26):
        f = round(2.0 - 0.05 * step, 2)
        head_size, body_size = round(base_head * f), round(base_body * f)
        tag_size = round(base_tag * min(max(1.0, f), 1.4))
        worst = max(range(len(cards)), key=lambda n: needed(cards[n], head_size, body_size))
        room = card_h * 0.9 if f > 1 else card_h   # leave air when scaling up
        if needed(cards[worst], head_size, body_size) <= room:
            break
    else:
        sys.exit(f"ERROR: card {worst + 1} ({cards[worst]['heading']}) has too much text "
                 "to fit; shorten its lines or use fewer cards.")
    max_chars = int((card_w - 48) / (body_size * 0.52))

    for i, card in enumerate(cards):
        r, c = divmod(i, cols)
        x = MARGIN + c * (card_w + GAP)
        top = grid_top + r * (card_h + GAP)
        tone = tones[card.get("tone", "a")]
        out.append(f'<rect x="{x:.1f}" y="{top:.1f}" width="{card_w:.1f}" '
                   f'height="{card_h:.1f}" rx="{RADIUS}" fill="{palette["surface"]}" '
                   f'stroke="{palette["stroke"]}" stroke-width="{STROKE_W}"/>')
        # Numbered badge, sized with the heading it sits beside
        br = max(rad, round(head_size * 0.6))
        cx, cy = x + 24 + br, top + 24 + rad
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{br}" fill="{tone}"/>')
        nsz = round(br * 1.1)
        out.append(text_el(cx, cy + nsz * 0.36, str(i + 1), nsz, palette["canvas"], font, BOLD, "middle"))
        icon_room = 0
        if spec.get("icons") and card.get("icon"):
            isz = round(head_size * 1.5)
            out.append(icon_el(card["icon"], x + card_w - 24 - isz, top + 20, isz, tone))
            icon_room = isz + 12
        head_chars = int((card_w - 48 - 2 * rad - 14 - icon_room) / (head_size * 0.55))
        head_lines = wrap(card["heading"], head_chars)
        for k, part in enumerate(head_lines):
            out.append(text_el(cx + br + 14, cy + head_size * 0.36 + k * head_size * 1.15,
                               part, head_size, palette["textPrimary"], font, BOLD))
        # Body lines
        ly = top + 24 + 36 + 22 + body_size + (len(head_lines) - 1) * head_size * 1.15
        for n, line in enumerate(card.get("lines", [])):
            if n == 0 and spec.get("lead"):
                # The first line is the card's key question, in the card's accent.
                for part in wrap(line, max_chars):
                    out.append(text_el(x + 24, ly, part, body_size, tone, font, BOLD))
                    ly += body_size * 1.3
                ly += body_size * 0.35
                continue
            label, _, rest = line.partition(": ")
            label_tone = labels.get(label) if rest else None
            for k, part in enumerate(wrap(line, max_chars)):
                if k == 0 and label_tone:
                    body = part[len(label) + 2:]
                    out.append(
                        f'<text x="{x + 24:.1f}" y="{ly:.1f}" font-family={quoteattr(font)} '
                        f'font-size="{body_size}" fill="{palette["textPrimary"]}">'
                        f'<tspan fill="{tones[label_tone]}" font-weight="{BOLD}">'
                        f'{escape(label)}:</tspan> {escape(body)}</text>')
                else:
                    out.append(text_el(x + 24, ly, part, body_size, palette["textPrimary"], font))
                ly += body_size * 1.3
            ly += body_size * 0.35
        # Tag: on the heading row for wide single-column cards, otherwise
        # pinned to the card's bottom edge
        if card.get("tag") and cols == 1 and not spec.get("icons"):
            # wide single-column card without an icon: the tag fits on the heading row
            out.append(text_el(x + card_w - 24, cy + tag_size * 0.36, card["tag"],
                               tag_size, tone, font, BOLD, "end"))
        elif card.get("tag"):
            ty = top + card_h - 22
            out.append(f'<rect x="{x + 24:.1f}" y="{ty - tag_size * 0.38:.1f}" width="28" height="4" '
                       f'rx="2" fill="{tone}"/>')
            out.append(text_el(x + 24 + 38, ty, card["tag"], tag_size, tone, font, BOLD))

    # Footer: the takeaway, then the brand line
    out.append(f'<line x1="{MARGIN}" y1="{footer_top:.1f}" x2="{width - MARGIN}" '
               f'y2="{footer_top:.1f}" stroke="{palette["stroke"]}" stroke-width="{STROKE_W}"/>')
    fy = footer_top + 22 + footer_size
    for line in footer_lines:
        out.append(text_el(MARGIN, fy, line, footer_size, palette["textPrimary"], font, BOLD))
        fy += footer_size * 1.25
    if frame:
        out.append(f'<rect y="{height - band}" width="{width}" height="{band}" fill="{band_fill}"/>')
        for txt, x, anchor in ((brand_line, MARGIN, "start"), (site, width - MARGIN, "end")):
            if txt:
                out.append(f'<text x="{x}" y="{height - band / 2 + 7:.1f}" '
                           f'font-family={quoteattr(font)} font-size="20" font-style="italic" '
                           f'fill="{band_text}" text-anchor="{anchor}">{escape(txt)}</text>')
    else:
        out.append(text_el(width - MARGIN, height - MARGIN + 4, brand_line, base_tag,
                           palette["textMuted"], font, 400, "end"))
    out.append("</svg>")
    return "\n".join(out)


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: render_cardgrid.py spec.json out.svg", file=sys.stderr)
        return 64
    spec_path, out_path = Path(sys.argv[1]), Path(sys.argv[2])
    spec = json.loads(spec_path.read_text())
    config = find_config(Path(__file__).resolve().parent)
    palette = dict(config["brand"]["diagram"])
    if spec.get("theme") == "light":
        palette.update(palette.get("light", {}))   # light overrides; missing keys fall back
    blog_url = config.get("channels", {}).get("blog", {}).get("url", "")
    site = blog_url.split("://", 1)[-1].rstrip("/")
    identity = config.get("identity", {})
    handle = config.get("channels", {}).get("x", {}).get("handle", "")
    brand_line = " · ".join(v for v in [identity.get("brandName", ""), handle] if v)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(build(spec, palette, brand_line, site))
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
