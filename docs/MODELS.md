# Which model does what

Main session runs on **Sonnet**. Work where one wrong claim costs credibility runs on
**Opus**, pinned with `model: opus` in the agent or skill frontmatter, so it applies
whatever the main session uses. Change a pin by editing that one line.

## Opus (pinned)

| Where | Type | Why Opus |
|---|---|---|
| `copy-reviewer` | agent | The independent gate for every post, article and script. Catches wrong technical claims, honest-framing slips and content-limit problems. |
| `topic-scout` | agent | Topic research and validation; has to judge sources and depth. |
| `video-scout` | agent | Concept deep-dives that the script is built on. |
| `blog-writer` | skill | Articles and social copy; voice, accuracy and altitude. |
| `video-scriptwriter` | skill | Video and Short scripts. |

## Opus, launched per task (no file to pin)

| Task | How |
|---|---|
| Voice review (take vs approved script, max 2 rounds) | fresh agent launched with model Opus |
| Visual review of a Short (frames, max 3 rounds) | fresh agent launched with model Opus |
| Trend research for formats (e.g. what works in Shorts now) | fresh agent launched with model Opus |

## Sonnet (main session, no pin)

| Where | Type | Why Sonnet is enough |
|---|---|---|
| `blog-images` | skill | Deterministic SVG templates; layout work, not judgment. |
| `video-thumbnail` | skill | Fixed HTML template render. |
| `video-shorts` | skill | Writing the diagram spec and rendering; quality is checked by the Opus visual reviewer. |
| Daily plan, ticking, collapsing days | session | Bookkeeping. |
| Weekly results table from screenshots | session | Reading numbers into a table. |
| Settings packs (YouTube, beehiiv) | session | Mechanical; copy inside them still goes to `copy-reviewer` (Opus). |

## When to switch the main session to Opus yourself (`/model`)

- A long drafting session where you go back and forth on one article or script.
- Anything touching the content limits that is not covered by a skill.
- Debugging something subtle in the pipeline code.

## Changing a pin

Changing `copy-reviewer`'s model changes the judge every draft passes through. Run
the evals in [`evals/copy-reviewer/`](../evals/copy-reviewer/README.md) before and
after, and keep the change only if no case that should fail gets through.

Last updated 14 Nov 2026.
