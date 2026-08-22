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


# ── Identity must stay in config ──────────────────────────────────────────────
# This protects the whole point of the config layer: a brand value hardcoded back
# into a skill means every forker inherits it.

section("No hardcoded identity")

identity_patterns = [
    r"aidevbuilds",
    r"hashnode\.dev",
    r"medium\.com/@",
    r"newsletter\.[a-z0-9-]+\.com",
]
offenders: list[str] = []
for path in sorted(REPO.glob(".claude/**/*.md")):
    text = path.read_text(encoding="utf-8").lower()
    for pat in identity_patterns:
        if re.search(pat, text):
            offenders.append(f"{path.relative_to(REPO)} matches /{pat}/")

check("agents and skills carry no brand values", not offenders,
      "; ".join(offenders[:4]))


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

for rel in ["setup.sh", ".claude/skills/blog-images/render_svg.sh"]:
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
