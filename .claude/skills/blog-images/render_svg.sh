#!/usr/bin/env bash
# Rasterize a hand-written SVG diagram to PNG.
#
#   render_svg.sh input.svg output.png [width_px]
#
# This stays a shell script rather than a Python entry point for one reason:
# cairosvg loads libcairo through the dynamic linker at import time, and on macOS
# Homebrew installs it somewhere the linker does not search by default. The
# DYLD_FALLBACK_LIBRARY_PATH fix has to be in the environment *before* the
# interpreter starts, so it cannot be set from inside the Python process itself.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# .claude/skills/blog-images -> repo root
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

if [ $# -lt 2 ]; then
  echo "usage: render_svg.sh input.svg output.png [width_px]" >&2
  exit 64
fi

SVG_IN="$1"
PNG_OUT="$2"
WIDTH="${3:-1600}"

if [ ! -f "$SVG_IN" ]; then
  echo "ERROR: no such SVG: $SVG_IN" >&2
  exit 66
fi

# Prefer the repo's shared venv; fall back to whatever python3 is on PATH so a
# skill folder copied into ~/.claude/skills/ still works outside the repo.
if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PY="$REPO_ROOT/.venv/bin/python"
else
  PY="$(command -v python3 || true)"
  [ -n "$PY" ] || { echo "ERROR: no python3 found." >&2; exit 69; }
fi

# macOS: point the dynamic linker at Homebrew's lib dir. `brew --prefix` resolves
# correctly on both Apple Silicon (/opt/homebrew) and Intel (/usr/local).
if [ "$(uname -s)" = "Darwin" ] && command -v brew >/dev/null 2>&1; then
  export DYLD_FALLBACK_LIBRARY_PATH="$(brew --prefix)/lib:${DYLD_FALLBACK_LIBRARY_PATH:-}"
fi

if ! "$PY" -c "import cairosvg" 2>/dev/null; then
  echo "ERROR: cairosvg could not load the native cairo library." >&2
  echo "  Run ./setup.sh from the repo root, and install cairo:" >&2
  case "$(uname -s)" in
    Darwin) echo "    brew install cairo" >&2 ;;
    Linux)  echo "    sudo apt-get install libcairo2   # or: sudo dnf install cairo" >&2 ;;
  esac
  exit 69
fi

mkdir -p "$(dirname "$PNG_OUT")"

"$PY" - "$SVG_IN" "$PNG_OUT" "$WIDTH" <<'PY'
import sys
import cairosvg

svg_in, png_out, width = sys.argv[1], sys.argv[2], int(sys.argv[3])
cairosvg.svg2png(url=svg_in, write_to=png_out, output_width=width)
PY

echo "Rendered $PNG_OUT (width ${WIDTH}px)"
