#!/usr/bin/env bash
# One-time setup for the content pipeline.
#
# Creates a single shared venv at the repo root that every skill uses, so there
# is exactly one Python environment to reason about rather than one per skill.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$REPO_ROOT/.venv"
PY="$VENV/bin/python"

step() { printf '\n\033[1m▸ %s\033[0m\n' "$1"; }
warn() { printf '\033[33m  ! %s\033[0m\n' "$1"; }
ok()   { printf '\033[32m  ✓ %s\033[0m\n' "$1"; }

# ── 1. Shared venv ────────────────────────────────────────────────────────────
step "Creating shared venv at .venv"
if [ -d "$VENV" ]; then
  ok "already exists, reusing"
else
  python3 -m venv "$VENV"
  ok "created"
fi

step "Installing Python dependencies"
"$PY" -m pip install --quiet --upgrade pip
"$PY" -m pip install --quiet -r "$REPO_ROOT/requirements.txt"
ok "installed"

# ── 2. Native cairo (blog-images) ─────────────────────────────────────────────
# cairosvg wraps the native cairo library; there is no pure-Python fallback.
# The only check that means anything is whether cairosvg actually imports, so
# test that directly rather than trusting ctypes.util.find_library — on macOS it
# does not search Homebrew's lib dir and reports a false negative.
step "Checking native cairo"
if [ "$(uname -s)" = "Darwin" ] && command -v brew >/dev/null 2>&1; then
  export DYLD_FALLBACK_LIBRARY_PATH="$(brew --prefix)/lib:${DYLD_FALLBACK_LIBRARY_PATH:-}"
fi
if "$PY" -c "import cairosvg" 2>/dev/null; then
  ok "cairo found, cairosvg imports cleanly"
else
  warn "cairosvg cannot load cairo. Diagram rendering (blog-images) will fail."
  case "$(uname -s)" in
    Darwin) warn "  macOS:  brew install cairo" ;;
    Linux)  warn "  Debian/Ubuntu:  sudo apt-get install libcairo2"
            warn "  Fedora:         sudo dnf install cairo" ;;
    *)      warn "  Install the cairo shared library for your platform." ;;
  esac
  warn "Continuing — the thumbnail skill does not need cairo."
fi

# ── 3. Chromium for Playwright (video-thumbnail) ──────────────────────────────
step "Installing Chromium for Playwright"
"$PY" -m playwright install chromium
ok "installed"

# ── 4. Local config ───────────────────────────────────────────────────────────
step "Checking local config"
if [ -f "$REPO_ROOT/config.json" ]; then
  ok "config.json exists"
else
  cp "$REPO_ROOT/config.example.json" "$REPO_ROOT/config.json"
  ok "created config.json from the example — edit it with your own brand and URLs"
fi

if [ ! -f "$REPO_ROOT/.env" ] && [ -f "$REPO_ROOT/.env.example" ]; then
  cp "$REPO_ROOT/.env.example" "$REPO_ROOT/.env"
  ok "created .env from the example (every value in it is optional)"
fi

printf '\n\033[32m\033[1mSetup complete.\033[0m Next: edit config.json, then open Claude Code here.\n\n'
