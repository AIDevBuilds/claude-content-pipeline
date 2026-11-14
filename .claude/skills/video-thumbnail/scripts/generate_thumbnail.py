#!/usr/bin/env python3
"""
Thumbnail generator — renders template.html in headless Chromium at 2x, then
downsamples to exactly 1280x720.

Brand colours and the channel tag come from config.json at the repo root; nothing
about the brand is hardcoded here. See config.example.json for the shape.

Setup:
    ./setup.sh          (from the repo root — creates .venv and fetches Chromium)

Usage:
    .venv/bin/python .claude/skills/video-thumbnail/scripts/generate_thumbnail.py \
        --video 01 \
        --tag "SYSTEM DESIGN" \
        --prefix "// when the cache lies" \
        --title "STALE\\nREADS" \
        --highlight "STALE" \
        --subtitle "Cache-aside · TTLs · invalidation" \
        --tools "Redis,PostgreSQL,Python" \
        --active-tool "Redis" \
        --badge-number "2" \
        --badge-label "fixes\\nshown" \
        --code "def get(key):\\n  v = cache.get(key)\\n  return v" \
        --bugline "cache.get(key)"

Output -> video-data/images/thumbnail-01.png (1280x720)
"""

import argparse
import base64
import html as html_mod
import io
import json
import re
import sys
import textwrap
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

SKILL_DIR = Path(__file__).resolve().parents[1]
# .claude/skills/video-thumbnail -> repo root
REPO_ROOT = SKILL_DIR.parents[2]
TEMPLATE_PATH = SKILL_DIR / "assets" / "template.html"
FONT_PATH = SKILL_DIR / "assets" / "fonts" / "Inter-latin.woff2"


# ── Config ────────────────────────────────────────────────────────────────────

def load_config() -> dict:
    """
    Read config.json from the repo root, falling back to config.example.json so a
    fresh clone renders something sane instead of crashing.

    Only non-secret presentation values are read here: brand colours and the
    display name. Credentials are never loaded by this script.
    """
    for name in ("config.json", "config.example.json"):
        path = REPO_ROOT / name
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                sys.exit(f"ERROR: {path} is not valid JSON — {exc}")
    sys.exit(f"ERROR: no config.json or config.example.json found in {REPO_ROOT}")


def hex_to_rgb_triplet(value: str) -> str:
    """'#00ff88' -> '0,255,136', so the hex can be reused inside rgba()."""
    h = value.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"expected a 3- or 6-digit hex colour, got {value!r}")
    return ",".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))


def build_theme_css(cfg: dict) -> str:
    """Override the template's :root defaults with the configured palette."""
    theme = cfg.get("brand", {}).get("thumbnail", {})
    accent = theme.get("accent", "#F59E0B")
    try:
        accent_rgb = hex_to_rgb_triplet(accent)
    except ValueError as exc:
        sys.exit(f"ERROR: brand.thumbnail.accent — {exc}")
    return (
        "\n  <style>\n"
        "    :root {\n"
        f"      --bg: {theme.get('background', '#0B1020')};\n"
        f"      --bg-alt: {theme.get('backgroundAlt', '#111833')};\n"
        f"      --accent: {accent};\n"
        f"      --accent-rgb: {accent_rgb};\n"
        f"      --text: {theme.get('textPrimary', '#ffffff')};\n"
        "    }\n"
        "  </style>"
    )


# ── Template assembly ─────────────────────────────────────────────────────────

def load_template() -> str:
    if not TEMPLATE_PATH.exists():
        sys.exit(f"ERROR: template.html not found at {TEMPLATE_PATH}")
    return TEMPLATE_PATH.read_text(encoding="utf-8")


def build_font_face() -> str:
    """
    Base64-embed the Inter woff2 so the headless browser renders it reliably.
    set_content() has no base URL, so external/relative font paths won't load —
    embedding is the only robust way to use a non-system font here.
    """
    if not FONT_PATH.exists():
        print(f"WARNING: {FONT_PATH.name} not found — headline falls back to Arial Black.")
        return ""
    data = base64.b64encode(FONT_PATH.read_bytes()).decode("utf-8")
    return f"""
  <style>
    @font-face {{
      font-family: 'Inter';
      font-style: normal;
      font-weight: 100 900;
      font-display: block;
      src: url(data:font/woff2;base64,{data}) format('woff2');
    }}
  </style>"""


def encode_image(image_path: str) -> str:
    path = Path(image_path)
    if not path.exists():
        print(f"WARNING: screenshot not found at {image_path} — using code visual instead.")
        return ""
    ext = path.suffix.lower().lstrip(".")
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp"}.get(ext, "png")
    data = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:image/{mime};base64,{data}"


def build_tool_badges(tools: list, active: str) -> str:
    badges = []
    for tool in tools:
        cls = "tool-badge active" if tool.strip() == active.strip() else "tool-badge"
        badges.append(f'<div class="{cls}">{html_mod.escape(tool.strip())}</div>')
    return "\n    ".join(badges)


def build_headline_main(title_raw: str, highlight: str) -> str:
    title_raw = title_raw.replace("\\n", "\n")
    result = []
    for line in title_raw.split("\n"):
        line_html = html_mod.escape(line)
        if highlight:
            pattern = re.compile(re.escape(html_mod.escape(highlight)), re.IGNORECASE)
            line_html = pattern.sub(
                lambda m: f'<span class="highlight">{m.group(0)}</span>', line_html
            )
        result.append(line_html)
    return "<br>".join(result)


def build_code_visual(code_snippet: str, bug_line: str, theme: dict) -> str:
    """Build a styled code block for the right panel."""
    accent_rgb = hex_to_rgb_triplet(theme.get("accent", "#F59E0B"))
    bug_colour = theme.get("bug", "#F43F5E")
    bug_rgb = hex_to_rgb_triplet(bug_colour)

    lines = code_snippet.replace("\\n", "\n").split("\n")[:10]
    html_lines = []
    for line in lines:
        escaped = html_mod.escape(line)
        is_bug = bug_line and bug_line.lower() in line.lower()
        if line.strip().startswith("#"):
            html_lines.append(f'<div class="code-line c-comment">{escaped}</div>')
        elif is_bug:
            html_lines.append(f'<span class="code-line c-bug">{escaped}</span>')
        else:
            html_lines.append(f'<div class="code-line c-normal">{escaped}</div>')
    lines_html = "\n      ".join(html_lines)

    return f"""
  <style>
    .face-area {{
      background: {theme.get('background', '#0B1020')};
      border: 1px solid rgba({accent_rgb},0.25);
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: flex-start;   /* flush-left like a real code editor */
      text-align: left;
      padding: 28px 28px;
      gap: 0;
      overflow: hidden;
    }}
    .face-area-icon, .face-area-label {{ display: none; }}
    .code-line {{
      font-family: 'Courier New', monospace;
      font-size: 22px;
      font-weight: 700;
      line-height: 1.85;
      white-space: pre;
      letter-spacing: 0.3px;
      display: block;
    }}
    .c-comment {{ color: {theme.get('codeComment', f'rgba({accent_rgb},0.62)')}; }}
    .c-normal  {{ color: {theme.get('codeNormal', 'rgba(255,255,255,0.88)')}; }}
    .c-bug     {{
      color: {bug_colour};
      font-weight: 700;
      background: rgba({bug_rgb},0.15);
      display: block;
      padding: 0 4px;
      border-left: 3px solid {bug_colour};
      margin-left: -4px;
    }}
  </style>
  <script>
    document.addEventListener('DOMContentLoaded', function() {{
      document.querySelector('.face-area').innerHTML = `
        {lines_html}
      `;
    }});
  </script>
"""


def build_screenshot_html(encoded: str, code_snippet: str, bug_line: str, theme: dict) -> str:
    if not encoded:
        return build_code_visual(code_snippet, bug_line, theme)
    accent_rgb = hex_to_rgb_triplet(theme.get("accent", "#F59E0B"))
    return f"""
    <style>
      .face-area {{
        background-image: url("{encoded}");
        background-size: cover;
        background-position: center;
        border: 2px solid rgba({accent_rgb},0.4);
      }}
      .face-area-icon, .face-area-label {{ display: none; }}
    </style>
    """


def _replace_div(html: str, css_class: str, inner: str) -> str:
    """Swap the contents of the first <div class="css-class">…</div>."""
    return re.sub(
        rf'(<div class="{css_class}">).*?(</div>)',
        lambda m: m.group(1) + inner + m.group(2),
        html,
        count=1,
        flags=re.DOTALL,
    )


def inject(html: str, **v) -> str:
    html = _replace_div(html, "channel-tag", v["brand_name"])
    html = _replace_div(html, "ep-tag", v["tag"])
    html = _replace_div(html, "headline-top", v["prefix"])
    html = _replace_div(html, "headline-main", f'\n      {v["headline_main"]}\n    ')
    html = _replace_div(html, "headline-sub", v["subtitle"])
    html = _replace_div(html, "big-text", v["badge_number"])
    html = _replace_div(html, "small-text", v["badge_label"])

    html = re.sub(
        r'(<div class="bottom-bar">).*?(</div>\s*<!-- Result)',
        lambda m: m.group(1) + f'\n    {v["tool_badges"]}\n  </div>\n\n  <!-- Result',
        html,
        count=1,
        flags=re.DOTALL,
    )

    if v.get("screenshot_html"):
        html = html.replace("</head>", v["screenshot_html"] + "\n</head>")
    return html


# ── Render ────────────────────────────────────────────────────────────────────

def generate_thumbnail(
    cfg, tag, prefix, title, highlight, subtitle,
    tools, active_tool, badge_number, badge_label,
    screenshot_path, code_snippet, bug_line, output_path,
):
    theme = cfg.get("brand", {}).get("thumbnail", {})
    brand_name = cfg.get("identity", {}).get("brandName", "BRAND")

    html = load_template()
    # Theme first, then font — both appended into <head> before render.
    html = html.replace("</head>", build_theme_css(cfg) + "\n</head>")
    html = html.replace("</head>", build_font_face() + "\n</head>")

    screenshot_enc = encode_image(screenshot_path) if screenshot_path else ""

    final_html = inject(
        html,
        brand_name      = html_mod.escape(brand_name),
        tag             = html_mod.escape(tag),
        prefix          = html_mod.escape(prefix),
        headline_main   = build_headline_main(title, highlight),
        subtitle        = subtitle,  # allows intentional <br> from the caller
        tool_badges     = build_tool_badges(tools, active_tool),
        badge_number    = html_mod.escape(badge_number),
        badge_label     = html_mod.escape(badge_label).replace("\\n", "<br>").replace("\n", "<br>"),
        screenshot_html = build_screenshot_html(screenshot_enc, code_snippet, bug_line, theme),
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=2)
        page.set_content(final_html, wait_until="networkidle")
        page.evaluate("document.fonts.ready")  # ensure embedded Inter is loaded
        page.wait_for_timeout(400)
        # Capture the 2x supersampled frame in-memory (2560x1440), then LANCZOS
        # downscale to exactly 1280x720. Uploading at YouTube's native thumbnail
        # size lets it skip its own (softer) downscaler and only JPEG-compress.
        shot = page.screenshot(clip={"x": 0, "y": 0, "width": 1280, "height": 720})
        browser.close()

    img = Image.open(io.BytesIO(shot)).resize((1280, 720), Image.LANCZOS)
    img.save(output_path, "PNG", optimize=True)

    print(f"Thumbnail saved -> {output_path}  (1280x720, LANCZOS from 2x supersample)")


def main():
    parser = argparse.ArgumentParser(
        description="Render a branded 1280x720 YouTube thumbnail from template.html",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:

              # No screenshot — shows the code snippet in the right panel
              .venv/bin/python .claude/skills/video-thumbnail/scripts/generate_thumbnail.py \\
                --video 01 \\
                --tag "SYSTEM DESIGN" \\
                --prefix "// when the cache lies" \\
                --title "STALE\\nREADS" \\
                --highlight "STALE" \\
                --subtitle "Cache-aside · TTLs · invalidation" \\
                --tools "Redis,PostgreSQL,Python" \\
                --active-tool "Redis" \\
                --badge-number "2" \\
                --badge-label "fixes\\nshown" \\
                --code "def get(key):\\n  v = cache.get(key)\\n  return v" \\
                --bugline "cache.get(key)"

              # With a screenshot from the build session in the right panel
              ... --screenshot ./my_screenshot.png
        """)
    )
    parser.add_argument("--video",        required=True, help="Video number, e.g. 01 — used in the output filename")
    parser.add_argument("--tag",          default="AI vs CODE")
    parser.add_argument("--prefix",       default="// I built a")
    parser.add_argument("--title",        required=True, help=r"Headline; use \n for line breaks")
    parser.add_argument("--highlight",    required=True, help="Substring of --title to paint in the accent colour")
    parser.add_argument("--subtitle",     default="")
    parser.add_argument("--tools",        required=True, help="Comma-separated tool names")
    parser.add_argument("--active-tool",  required=True, help="Which of --tools to emphasise")
    parser.add_argument("--badge-number", required=True)
    parser.add_argument("--badge-label",  required=True)
    parser.add_argument("--code",         default="", help=r"Code snippet for the right panel; use \n for newlines")
    parser.add_argument("--bugline",      default="", help="Substring of --code to flag in the bug colour")
    parser.add_argument("--screenshot",   default=None, help="Image for the right panel instead of a code snippet")
    parser.add_argument("--output",       default=None, help="Override the output path")

    args = parser.parse_args()
    cfg = load_config()

    video_num = args.video.zfill(2)
    if args.output:
        output_path = Path(args.output)
    else:
        video_dir = cfg.get("output", {}).get("videoDir", "video-data")
        output_path = REPO_ROOT / video_dir / "images" / f"thumbnail-{video_num}.png"

    code = args.code or (
        f"# {cfg.get('identity', {}).get('brandName', 'BRAND')}\n"
        "# Real builds\n# Honest failures"
    )

    generate_thumbnail(
        cfg             = cfg,
        tag             = args.tag,
        prefix          = args.prefix,
        title           = args.title,
        highlight       = args.highlight,
        subtitle        = args.subtitle,
        tools           = [t.strip() for t in args.tools.split(",")],
        active_tool     = args.active_tool,
        badge_number    = args.badge_number,
        badge_label     = args.badge_label,
        screenshot_path = args.screenshot,
        code_snippet    = code,
        bug_line        = args.bugline,
        output_path     = output_path,
    )


if __name__ == "__main__":
    main()
