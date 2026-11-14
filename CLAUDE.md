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

**Respect content limits.** `contentLimits.files` in config lists the author's own
rule files (kept in a gitignored folder). Read every listed file before any topic
suggestion, outline, draft, script, social copy, reply or config change, and follow
it. They outrank `positioning`: a stronger post never justifies using material the
author is not free to share. Whether or not any file is listed: no detail from the
author's job (code, designs, diagrams, metrics, incidents, project, client or
employer names), not even anonymised or "inspired by"; never ask the author for an
internal example; never read employer documents such as policies or contracts, ask
for the author's own summary instead; and flag any novel technique or code for the
author to clear before publishing, since work contracts often claim inventions. Add
`identity.disclaimer` from config as a footer on every post and video description.

**Never invent facts for published content.** Drafts and scripts use `[NEEDS: ...]`
markers for anything only the author would know (a personal opinion, a public
source to cite, a version number). Leave the marker; do not fill it with a guess.

**Respect `positioning.honestFraming`.** When config carries a `positioning` block,
any claim about the author's experience uses `honestFraming.useThis` wording, and
nothing in `honestFraming.neverClaim` gets written — not in a draft, a bio, a video
description, or a social post, and not even when it would make a stronger hook. Readers who
know the subject will test these claims; one that collapses under a follow-up
question costs more than a weaker true one gains.

**Hold the altitude.** `positioning.altitude` says what level the content must work
at. Content pitched below `positioning.targetLevel` signals the level below it. If an
approved outline has drifted into a tutorial, say so before drafting rather than
writing it well at the wrong level.

## Layout

```
.claude/
  agents/           topic-scout, video-scout (research, run isolated), copy-reviewer
  skills/           blog-writer, blog-images, video-scriptwriter, video-thumbnail,
                    video-shorts (Remotion)
  hooks/            guard_secrets.py — blocks shell commands that name credential files
  settings.json     committed: permission rules + the hook
docs/               workflow guides (blog, video, Shorts, models)
evals/              eval cases for the copy-reviewer judge
config.json         local identity and brand values (gitignored)
config.example.json committed template
blog-data/          generated posts and diagrams (gitignored)
video-data/         generated scripts, SEO, thumbnails, Shorts; .cache/ = scratch (gitignored)
private/            your rule files, analytics, notes (gitignored)
scripts/            validate.py (CI checks), setup-github.sh
.venv/              one shared venv for every skill
```

Skill folders are self-contained: each bundles its own code and assets so it can
be copied into `~/.claude/skills/` and still work. Inside a skill: `SKILL.md`,
`scripts/` (code that runs), `references/` (docs loaded on demand), `assets/` (fonts,
icons, templates used in output), `examples/` (generic samples). Nothing is written
into a skill folder at runtime: generated output and render scratch go under
`blog-data/` or `video-data/` (scratch in `video-data/.cache/`, safe to delete), and
personal files go in `private/`. Scripts prefer the repo's `.venv` and fall back to
system `python3`.

## Setup

```bash
./setup.sh
```
Creates `.venv`, installs `requirements.txt`, fetches Chromium for Playwright, and
seeds `config.json` from the example. Diagram rendering additionally needs the
native cairo library (`brew install cairo`, or `apt-get install libcairo2`); setup
checks and tells you if it is missing.

## Conventions

- When a request is covered by a skill or agent, use it rather than drafting
  directly: posts through `blog-writer`; videos through `video-scriptwriter`;
  topic ideas through the scouts. The skills carry the
  review loop, the logging and the content-limit checks; writing freehand skips them.

- To make a Short (from a link, pasted text or a screenshot): `docs/HOW_TO_MAKE_A_SHORT.md`. Which model each skill and agent uses: `docs/MODELS.md`.
- After changing `copy-reviewer`, the review loops that call it, or its model, run
  the evals in `evals/copy-reviewer/` (see its README) and report the result. Zero
  false PASS is required.
- Commits go through `scripts/pre-commit` (install: `ln -sf ../../scripts/pre-commit
  .git/hooks/pre-commit`). It blocks private paths and personal terms. Never bypass
  it with `--no-verify` without the author's explicit go-ahead.
- Python is only ever installed into `.venv`, never globally; run scripts with
  `.venv/bin/python`. Node packages (the `video-shorts` Remotion project) install
  into that skill's own `node_modules` with a plain `npm install`, never `npm -g`.
  Browsers come from Playwright's cache, which `./setup.sh` fills.
- Both image generators are deterministic template renderers, not AI image models.
  That is deliberate: generated images drift in style between runs, and a blog's
  diagrams and a channel's thumbnails have to look like a set. Do not swap in an
  image model.
- `blog-data/` and `video-data/` are gitignored. Do not commit generated content.
- No em-dashes in any generated blog or video copy. The voice rules in
  `blog-writer/SKILL.md` are specific and worth reading before writing prose.
