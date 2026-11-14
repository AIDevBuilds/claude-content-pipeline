# Changelog

Notable changes to the pipeline: agents, skills, hooks, templates and docs.
Generated content (`blog-data/`, `video-data/`) is gitignored and not tracked here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.2.0] - 2026-11-14

### Added
- `copy-reviewer` agent: an independent reviewer that reads a post, article or script cold and returns PASS or a numbered list of fixes. Used in a write-review loop (fresh agent per round, at most 5 rounds) by `blog-writer` and `video-scriptwriter`. A calling skill can send extra checks.
- `video-shorts` skill: renders a branded vertical Short (1080x1920 MP4) from a voiceover and a small JSON spec with a fixed Remotion template and word-by-word captions.
- `blog-images` card-grid template (`render_cardgrid.py`, `references/cardgrid.md`): portrait and landscape infographics for 4 to 8 parallel items, with Lucide line icons (`assets/icons/`, ISC licence) picked by `pick_icon.py`.
- `docs/HOW_TO_MAKE_A_SHORT.md` and `docs/MODELS.md` (which model each skill and agent uses).
- `identity.disclaimer` in `config.example.json`: an optional footer added to every post and video description.
- `brand.diagram.light.accentB` in `config.example.json` (second accent for the light palette).
- `openpyxl` in `requirements.txt` for reading analytics exports.
- `CHANGELOG.md`.
- `contentLimits.files` in `config.example.json`: a list of the author's own rule files (kept in a gitignored folder). Every skill and agent reads them before writing; without them a generic baseline still applies.
- `scripts/pre-commit`: refuses a commit that stages a private path or a personal term (values from `config.json`, plus `private/public-denylist.txt`), or whose author email contains one, and runs `scripts/validate.py`. Extra local-only paths go in `private/local-only-paths.txt`.
- `evals/copy-reviewer/`: an eval set for the `copy-reviewer` judge (four generic example cases, the case format, how to run it, and the pass bar: zero false PASS), rerun whenever the reviewer's prompt, model or calling review loops change.
- `video.voice` in `config.example.json`: the ElevenLabs voice and model for Shorts.
- `video-shorts/examples/example.json`: a generic worked example spec.

### Changed
- `copy-reviewer`: explicit verdict rule. REVISE only for a blocking finding (accuracy, framing, limits, clear generated tells, a failed caller check, platform limits, or text the reader cannot follow); taste goes in optional notes after a PASS. Calibrated against the eval set after the baseline flagged too much already-approved copy.
- `scripts/validate.py` checks every public file (tracked or addable), not only `.claude/**/*.md`, with generic patterns only: no private paths, no real channel URLs, no home-folder paths, no personal email addresses, placeholders only in `config.example.json`, no runtime output inside skills, and (locally) none of your `config.json` values. The hardcoded brand pattern is gone.
- Skill folders follow one layout: `SKILL.md`, `scripts/` (code), `references/`, `assets/` (fonts, icons, templates), `examples/`. Moved `blog-images` scripts to `scripts/`; `video-thumbnail` script to `scripts/`, template and fonts to `assets/`, sample to `examples/`; `video-shorts` renderer to `scripts/`, fonts and icons from `public/` to `assets/`.
- `video-shorts` no longer writes inside the skill: the voiceover copy, fonts and props go to `<output.videoDir>/.cache/shorts/` and Remotion reads them via `--public-dir`. `.gitignore` covers `**/.cache/`.
- `video-shorts` template: anything timed at 0 (header, nodes, chips, notes, meters) is fully drawn on frame 0, so the hook frame is never blank. New spec options: `dividers` (dashed vertical boundary lines), edge styles as an optional third element of an edge (`tone`, `glow`, `width`), and chip `between` (centred between two nodes, follows them) and `toneAt` (turns to the problem colour).
- `video-shorts` template: the top band no longer carries text, because YouTube's controls cover it on Android and iOS. The series label moved to y 262, above the header, and the header moved down 12px. Safe-zone notes updated in `SKILL.md`.
- `blog-images` card grid: concept-explainer cards put the public source in the footer instead of a takeaway.
- `blog-writer` and `blog-images`: a published article's files and images are archived together in `blog-data/archive/<date>-<slug>/`, with social images sorted into `images/x/`, `images/linkedin/`, `images/newsletter/` (or `images/social/`) and specs in `images/specs/`; `blog-data/images/` holds only the article in progress; brand images live in `blog-data/channel-updates/`.
- Moved the workflow guides (`WORKFLOW.md`, `VIDEO_WORKFLOW.md`, `HOW_TO_MAKE_A_SHORT.md`, `MODELS.md`) into `docs/`. `README.md`, `CLAUDE.md` and `CHANGELOG.md` stay at the root.
- `blog-images` now uses the light palette by default; the dark palette is used only on request.
- `render_svg.sh` passes cairo the first named font family instead of a CSS fallback list, so bold and italic render correctly.
- `blog-writer`: review loop on the draft and on every piece of social copy, a ~3,000-word length budget with a suggested split, a two-week X drip package, LinkedIn follow-up posts, a Medium AI-disclosure note, a newsletter CTA and disclaimer footer, newsletter issues written in the template's block format, and a content-limit check before handing over a draft.
- `video-scriptwriter`: content limits section and an independent review of every script.
- `topic-scout` and `video-scout`: `model: opus`; `provenStrengths` used only to judge credibility, never as material; examples from public sources.
- `guard_secrets.py`: docstring now states exactly what the hook does and does not catch (interpreters that open a secret file are blocked; commands that never name the file are not), and points to the sandbox for OS-level enforcement.
- `CLAUDE.md`: hard rules for content limits, honest framing, altitude, `[NEEDS: ...]` markers; skill and agent conventions.
- `.gitignore`: `private/` (author notes that must never be committed).
- `blog-writer`: a "Hooks and packaging" rubric for titles, openings, X launch and drip posts, LinkedIn launch and follow-ups, and newsletter subjects (3 to 4 options in different patterns, 7 pass/fail rules, one promise across the package, LinkedIn first line under about 140 characters, a hook record in `seo-and-publish.md`), from an independent audit.
- `video-scriptwriter` and `video-shorts`: hook rules (4 options in different patterns, frame 0 and first line agree, no warm-up, a payoff the video delivers, altitude and honest framing), packaging for full videos (title, thumbnail and cold open as one promise, re-hooks), series-shaped script structure instead of one fixed format, an originality check against the last five Shorts for YouTube's inauthentic-content rule, related video and pinned comment for every Short, and a `video-data/shorts-log.md` performance log.
- `positioning.contentMix` in `config.example.json` (optional ratio between two content tracks, e.g. 2 architecture : 1 AI); `topic-scout` proposes from the under-served track and `blog-writer` interleaves drips to keep the feed near it.

## [0.1.0] - 2026-08-22

### Added
- Initial pipeline: `topic-scout` and `video-scout` agents; `blog-writer`, `blog-images`, `video-scriptwriter` and `video-thumbnail` skills; the `guard_secrets.py` PreToolUse hook and its tests; `config.example.json`; `setup.sh`; CI workflow.
