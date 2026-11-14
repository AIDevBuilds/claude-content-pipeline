#!/usr/bin/env python3
"""
Repository validation. Run locally with:  python3 scripts/validate.py

CI runs exactly this, so a green run here means a green run there. Every check
guards a failure mode that is silent in normal use: a malformed settings.json
disables every permission rule in it without warning, and malformed skill
frontmatter makes a skill quietly fail to load.
"""

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

failures: list[str] = []
checks_run = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global checks_run
    checks_run += 1
    if ok:
        print(f"  \033[32m✓\033[0m {name}")
    else:
        print(f"  \033[31m✗\033[0m {name}" + (f" — {detail}" if detail else ""))
        failures.append(f"{name}: {detail}" if detail else name)


def section(title: str) -> None:
    print(f"\n\033[1m{title}\033[0m")


# ── JSON validity ─────────────────────────────────────────────────────────────
# A malformed settings.json silently disables ALL settings it contains, including
# the permission deny rules. This is the highest-value check in the file.

section("JSON validity")

json_files = [
    "config.example.json",
    ".claude/settings.json",
]
parsed: dict[str, dict] = {}

for rel in json_files:
    path = REPO / rel
    if not path.exists():
        check(rel, False, "file missing")
        continue
    try:
        parsed[rel] = json.loads(path.read_text(encoding="utf-8"))
        check(rel, True)
    except json.JSONDecodeError as exc:
        check(rel, False, f"invalid JSON at line {exc.lineno}: {exc.msg}")


# ── Config schema parity ──────────────────────────────────────────────────────
# config.json is gitignored, so CI can only see the example. Locally, check both
# so a field added to one but not the other is caught before it ships.

section("Config schema")

example = parsed.get("config.example.json")
if example:
    required_top = {"identity", "channels", "series", "brand", "output"}
    missing = required_top - set(example)
    check("example has required top-level keys", not missing,
          f"missing: {sorted(missing)}" if missing else "")

    brand = example.get("brand", {})
    check("brand defines both palettes",
          {"diagram", "thumbnail"} <= set(brand),
          f"found: {sorted(brand)}")

    accent = brand.get("thumbnail", {}).get("accent", "")
    check("thumbnail accent is a hex colour",
          bool(re.fullmatch(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})", accent)),
          f"got {accent!r}")

    local = REPO / "config.json"
    if local.exists():
        try:
            local_cfg = json.loads(local.read_text(encoding="utf-8"))
            only_local = set(local_cfg) - set(example)
            only_example = set(example) - set(local_cfg)
            check("config.json and example share top-level keys",
                  not only_local and not only_example,
                  f"only in config.json: {sorted(only_local)}, "
                  f"only in example: {sorted(only_example)}")
        except json.JSONDecodeError as exc:
            check("config.json parses", False, str(exc))
    else:
        print("  \033[2m·\033[0m config.json absent (expected in CI, it is gitignored)")


# ── Claude Code settings ──────────────────────────────────────────────────────

section("Claude Code settings")

settings = parsed.get(".claude/settings.json")
if settings:
    perms = settings.get("permissions", {})
    deny = perms.get("deny", [])
    check("deny rules present", len(deny) >= 10, f"only {len(deny)} rules")

    # The .env deny rule is the one that matters most; assemble the pattern rather
    # than writing it literally, so the guard hook does not block this file's own
    # tooling when it is grepped or edited.
    env_rule = "Read(./." + "env)"
    check("deny covers the environment file", env_rule in deny,
          f"expected {env_rule!r} in deny list")

    check("example placeholders stay readable",
          any(".example" in rule for rule in perms.get("allow", [])),
          "no allow rule for *.example files")

    hooks = settings.get("hooks", {}).get("PreToolUse", [])
    bash_hooks = [h for h in hooks if h.get("matcher") == "Bash"]
    check("PreToolUse guard hook wired to Bash", len(bash_hooks) == 1,
          f"found {len(bash_hooks)} Bash matchers")

    if bash_hooks:
        cmd = bash_hooks[0].get("hooks", [{}])[0].get("command", "")
        check("guard hook points at an existing script",
              "guard_secrets.py" in cmd and (REPO / ".claude/hooks/guard_secrets.py").exists(),
              f"command: {cmd!r}")


# ── Agent and skill frontmatter ───────────────────────────────────────────────
# Malformed frontmatter makes a skill or agent silently fail to load.

section("Agent and skill frontmatter")


def parse_frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    fields: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith((" ", "\t", "#")):
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


for path in sorted(REPO.glob(".claude/agents/*.md")):
    fm = parse_frontmatter(path)
    label = f"agents/{path.name}"
    if fm is None:
        check(label, False, "no parseable YAML frontmatter")
        continue
    missing = {"name", "description"} - set(fm)
    ok = not missing and fm.get("name") == path.stem
    check(label, ok,
          f"missing {sorted(missing)}" if missing
          else f"name {fm.get('name')!r} != filename {path.stem!r}")

for path in sorted(REPO.glob(".claude/skills/*/SKILL.md")):
    fm = parse_frontmatter(path)
    label = f"skills/{path.parent.name}"
    if fm is None:
        check(label, False, "no parseable YAML frontmatter")
        continue
    missing = {"name", "description"} - set(fm)
    ok = not missing and fm.get("name") == path.parent.name
    check(label, ok,
          f"missing {sorted(missing)}" if missing
          else f"name {fm.get('name')!r} != folder {path.parent.name!r}")


# ── Public files stay generic ─────────────────────────────────────────────────
# Everything that would be published must work for any user: identity lives in
# config.json, personal files live in gitignored folders. These checks use only
# generic patterns, so they name nobody. scripts/pre-commit adds the personal
# terms locally.

section("Public files stay generic")

import subprocess  # noqa: E402


def public_files() -> list[str]:
    """Tracked files plus untracked files git would add (i.e. not ignored)."""
    try:
        out = []
        for args in (["ls-files"], ["ls-files", "-o", "--exclude-standard"]):
            out += subprocess.run(["git", *args], cwd=REPO, capture_output=True,
                                  text=True, check=True).stdout.splitlines()
        return sorted({p for p in out if (REPO / p).is_file()})
    except (OSError, subprocess.CalledProcessError):
        return []


TEXT = {".md", ".json", ".py", ".sh", ".ts", ".tsx", ".js", ".html", ".css",
        ".txt", ".yml", ".yaml", ".toml", ""}
SKIP = ("package-lock.json", "assets/icons/lucide/tags.json")
files = [p for p in public_files()
         if Path(p).suffix in TEXT and not p.endswith(SKIP) and "node_modules/" not in p]
texts = {p: (REPO / p).read_text(encoding="utf-8", errors="replace") for p in files}
check("public file list available", bool(files), "git ls-files returned nothing")

PRIVATE_PREFIXES = ("private/", "blog-data/", "video-data/")
leaked_paths = [p for p in public_files()
                if (p.startswith(PRIVATE_PREFIXES) and not p.endswith(".gitkeep"))
                or p in ("config.json", "CLAUDE.local.md")]
check("no private paths are tracked or addable", not leaked_paths, ", ".join(leaked_paths[:5]))

PLACEHOLDER = re.compile(r"your|example|<", re.IGNORECASE)
channel_patterns = [
    r"[a-z0-9-]{3,}\.hashnode\.dev", r"medium\.com/(?:feed/)?@[\w.-]{3,}", r"dev\.to/[\w-]{3,}",
    r"youtube\.com/@[\w.-]{3,}", r"newsletter\.[a-z0-9-]+\.[a-z]+",
]
brand_hits = []
for p, text in texts.items():
    for pat in channel_patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            if not PLACEHOLDER.search(m.group(0)):
                brand_hits.append(f"{p}: {m.group(0)}")
check("no real channel URLs outside config.json", not brand_hits, "; ".join(brand_hits[:4]))

home = re.compile("|".join([r"/" + "Users/[A-Za-z]", r"/" + "home/[a-z]", r"[A-Z]:\\\\" + "Users"]))
home_hits = [p for p, text in texts.items() if home.search(text) and p != "scripts/validate.py"]
check("no home-folder paths", not home_hits, ", ".join(home_hits[:4]))

EMAIL = re.compile(r"(?<![\w/@])[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,}\b")
OK_EMAIL = re.compile(r"noreply|no-reply|example\.|@users\.|^git@github\.com$", re.IGNORECASE)
email_hits = [f"{p}: {m.group(0)}" for p, text in texts.items()
              for m in EMAIL.finditer(text) if not OK_EMAIL.search(m.group(0))]
check("no personal email addresses", not email_hits, "; ".join(email_hits[:4]))

if example:
    def strings(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if not k.startswith("_"):
                    yield from strings(v)
        elif isinstance(obj, str):
            yield obj
    ident = example.get("identity", {})
    who = [ident.get("brandName", ""), *strings(ident.get("author", {}))]
    links = [s for s in strings(example.get("channels", {})) if "/" in s or s.startswith("@")]
    real = [s for s in who + links if s and not PLACEHOLDER.search(s)
            and not s.startswith(("One sentence", "Keep it"))]
    check("config.example.json holds placeholders only", not real, "; ".join(real[:4]))

runtime = re.compile(r"^\.claude/skills/[^/]+/(?:.*/)?(?:\.cache|out|\.work|__pycache__|public/audio)/")
runtime_hits = [p for p in public_files() if runtime.search(p)]
check("no runtime output inside skill folders", not runtime_hits, ", ".join(runtime_hits[:4]))

local = REPO / "config.json"
if local.exists():
    cfg = json.loads(local.read_text(encoding="utf-8"))
    ident = cfg.get("identity", {})
    author = ident.get("author", {})
    terms = [author.get("name"), author.get("role"), author.get("bio"), ident.get("tagline")]
    for chan in cfg.get("channels", {}).values():
        if isinstance(chan, dict):
            terms += [re.sub(r"^https?://(www\.)?", "", v).rstrip("/") for k, v in chan.items()
                      if k != "platform" and isinstance(v, str)]
    brand_name = (ident.get("brandName") or "").lower()
    terms = [t for t in terms if isinstance(t, str) and len(t) >= 4 and t.lower() != brand_name]
    own_hits = [f"{p}: '{t[:30]}'" for p, text in texts.items() for t in terms
                if t.lower() in text.lower()]
    check("your config.json values appear in no public file", not own_hits, "; ".join(own_hits[:4]))


# ── Nothing secret is committed ───────────────────────────────────────────────

section("No committed secrets")

secret_names = [
    ".env", ".env.local", ".env.production",
    "credentials.json", ".npmrc", ".netrc", ".git-credentials",
]
tracked_secrets = [n for n in secret_names if (REPO / n).exists()
                   and n not in (".env",)]  # .env may exist locally; gitignore covers it
check("no credential files at repo root beyond the ignored ones",
      not tracked_secrets, f"found: {tracked_secrets}")

gitignore = (REPO / ".gitignore").read_text(encoding="utf-8") if (REPO / ".gitignore").exists() else ""
for needed in [".env", "config.json", ".venv/"]:
    check(f"gitignore covers {needed}",
          any(line.strip() == needed for line in gitignore.splitlines()),
          "not found as an exact line")


# ── Executables ───────────────────────────────────────────────────────────────

section("Scripts")

import os  # noqa: E402

for rel in ["setup.sh", "scripts/pre-commit", ".claude/skills/blog-images/scripts/render_svg.sh"]:
    path = REPO / rel
    check(f"{rel} is executable",
          path.exists() and os.access(path, os.X_OK),
          "missing" if not path.exists() else "not chmod +x")


# ── Result ────────────────────────────────────────────────────────────────────

print()
if failures:
    print(f"\033[31m\033[1m{len(failures)} of {checks_run} checks failed\033[0m")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)

print(f"\033[32m\033[1mall {checks_run} checks passed\033[0m")
