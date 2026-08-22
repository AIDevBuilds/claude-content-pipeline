# Repository guide

A content pipeline for a technical blog and YouTube channel, built as Claude Code
agents and skills. There is no application to run: the deliverables are markdown
files and images under `blog-data/` and `video-data/`.

## Hard rules

**Never read credentials.** Do not open `.env`, SSH keys, cloud credential files,
`.npmrc`/`.pypirc`, or anything under a `secrets/` directory — not with Read, not
with `cat`/`head`/`grep`, not through a Python one-liner, not to "just check the
format". This is enforced by `permissions.deny` and a `PreToolUse` hook in
`.claude/settings.json`, but treat it as a rule you follow rather than a fence you
test. If you need to know whether a variable is set, check the environment without
opening the file: `[ -n "$YOUTUBE_API_KEY" ] && echo set`. The committed
`.env.example` is readable and documents the expected shape.

**Never hardcode identity.** Brand name, author details, channel URLs, handles,
series names, and brand colours all live in `config.json` at the repo root. Read
them from there. If a value is missing, say so rather than inventing one — a
plausible-looking invented URL is worse than an explicit gap. This repo is public
and other people run it with their own `config.json`.

**Never invent facts for published content.** Drafts and scripts use `[NEEDS: ...]`
markers for anything only the author would know (a real metric, an internal
example, a version number). Leave the marker; do not fill it with a guess.

**Respect `positioning.honestFraming`.** When config carries a `positioning` block,
any claim about the author's experience uses `honestFraming.useThis` wording, and
nothing in `honestFraming.neverClaim` gets written — not in a draft, a bio, a video
description, or a social post, and not even when it would make a stronger hook. This
content is career evidence; a claim that collapses under interview questioning costs
more than a weaker true one gains.

**Hold the altitude.** `positioning.altitude` says what level the content must work
at. Content pitched below the author's target role signals the level below it. If an
approved outline has drifted into a tutorial, say so before drafting rather than
writing it well at the wrong level.

## Layout

```
.claude/
  agents/           topic-scout, video-scout — research, run isolated
  skills/           blog-writer, blog-images, video-scriptwriter, video-thumbnail
  hooks/            guard_secrets.py — blocks shell access to credentials
  settings.json     committed: permission rules + the hook
config.json         local identity and brand values (gitignored)
config.example.json committed template
blog-data/          generated posts and diagrams (gitignored)
video-data/         generated scripts, SEO and thumbnails (gitignored)
.venv/              one shared venv for every skill
```

Skill folders are self-contained: each bundles its own script and assets so it can
be copied into `~/.claude/skills/` and still work. Scripts prefer the repo's
`.venv` and fall back to system `python3`.

## Setup

```bash
./setup.sh
```
Creates `.venv`, installs `requirements.txt`, fetches Chromium for Playwright, and
seeds `config.json` from the example. Diagram rendering additionally needs the
native cairo library (`brew install cairo`, or `apt-get install libcairo2`); setup
checks and tells you if it is missing.

## Conventions

- Python is only ever installed into `.venv`, never globally.
- Both image generators are deterministic template renderers, not AI image models.
  That is deliberate: generated images drift in style between runs, and a blog's
  diagrams and a channel's thumbnails have to look like a set. Do not swap in an
  image model.
- `blog-data/` and `video-data/` are gitignored. Do not commit generated content.
- No em-dashes in any generated blog or video copy. The voice rules in
  `blog-writer/SKILL.md` are specific and worth reading before writing prose.
