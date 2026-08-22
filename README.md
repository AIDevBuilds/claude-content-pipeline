# Content Pipeline for Claude Code

A set of Claude Code **agents** and **skills** that take a technical blog post or
YouTube video from "I need a topic" to "here is the draft, the diagrams, the SEO
package, and the thumbnail."

Everything is configuration-driven: point `config.json` at your own blog, channel
and brand colours and the whole pipeline writes in your voice, to your platforms.

---

## What's in here

| Component | Type | Does |
|---|---|---|
| `topic-scout` | agent | Finds gaps in your published archive, proposes topics, then researches and validates the one you pick |
| `blog-writer` | skill | Outline → draft → per-platform SEO and social copy |
| `blog-images` | skill | Hand-writes SVG diagrams from your palette, rasterizes to PNG |
| `video-scout` | agent | Cross-references your posts against your published videos to find video gaps, then produces a concept deep-dive |
| `video-scriptwriter` | skill | Full script, coding prompts to record, YouTube SEO, Shorts cut, post-publish sharing posts |
| `video-thumbnail` | skill | Renders a real 1280×720 thumbnail PNG from a branded HTML template |

**Agents** handle research. They run in an isolated context so fifteen web searches
don't bury your actual draft. **Skills** handle writing, and run in your main
conversation where your accumulated context lives.

Neither image generator is an AI image model. Both are deterministic template
renderers, because generated images drift in style between runs and a blog's
diagrams need to look like a set.

---

## Setup

```bash
git clone <your-fork> && cd <repo>
./setup.sh
```

`setup.sh` creates one shared `.venv`, installs dependencies, fetches Chromium for
Playwright, and seeds `config.json` from the example.

Diagram rendering also needs the native **cairo** library, which pip can't provide:

```bash
brew install cairo            # macOS
sudo apt-get install libcairo2   # Debian/Ubuntu
```

Then edit **`config.json`** — brand name, author, channel URLs, series, colours.
That file is gitignored, so your values stay yours.
`config.example.json` documents every field.

### Optional: point it at a career goal

`config.json` has a `positioning` block that turns the pipeline from "suggest good
topics" into "suggest topics that build evidence for the role I want next":

```jsonc
"positioning": {
  "targetRole": "Solution Architect with credible AI systems depth",
  "audienceSeniority": "senior engineers, tech leads, and architects",
  "altitude":       { "write": [...], "avoid": ["step-by-step build tutorials"] },
  "provenStrengths": [ "things you have genuinely done" ],
  "evidenceGaps":    [ { "skill": "LLM evaluation", "priority": "highest" } ],
  "honestFraming":   { "useThis": "...", "neverClaim": [...] }
}
```

With it set, the scouts reject topics matching `altitude.avoid` however well they'd
perform, weight suggestions toward your `evidenceGaps`, and label each candidate with
which gap it closes. The writing skills hold that altitude and use `honestFraming`
wording for any claim about you, so nothing gets published that you can't defend in
an interview.

Delete the block for goal-agnostic topic suggestions.

---

## Using it

Open Claude Code in the repo and talk to it.

**Blog:**
```
Use topic-scout to suggest my next blog post
Use topic-scout to research and validate: <the one you picked>
Using the blog-writer skill, turn this research brief into an outline
The outline looks good, write the full draft
This draft is final, give me the SEO and publish details
```

**Video:**
```
Use video-scout to suggest my next video
Use video-scout to research and validate: <the one you picked>
Using the video-scriptwriter skill, write the full script
Give me the coding prompts for this
Give me the YouTube SEO and thumbnail details
Also generate the Shorts package from this
Give me the sharing posts, here's the link: https://youtu.be/...
```

Full step-by-step walkthroughs: [WORKFLOW.md](WORKFLOW.md) and
[VIDEO_WORKFLOW.md](VIDEO_WORKFLOW.md).

Output lands in `blog-data/` and `video-data/`, both gitignored — this is a tooling
repo, your content stays local.

---

## Security

Two independent layers stop an agent reading credentials, both in
`.claude/settings.json`:

1. **`permissions.deny`** blocks the Read tool from `.env`, SSH keys, cloud
   credentials, `.npmrc`/`.pypirc`, `secrets/`, and certificate files.
2. **A `PreToolUse` hook** (`.claude/hooks/guard_secrets.py`) inspects every shell
   command and refuses anything touching those paths, closing the `cat .env` gap
   that permission rules alone leave open.

The `*.example` placeholders stay readable, so the agent can still see what shape a
config takes without ever seeing a real value.

Nothing here needs an API key to work. `YOUTUBE_API_KEY` is optional and only adds
view-count-informed topic suggestions; without it `video-scout` uses `yt-dlp`.

---

## Using a skill outside this repo

Each skill folder is self-contained. To use one globally:

```bash
cp -r .claude/skills/blog-writer ~/.claude/skills/
```

Scripts prefer this repo's `.venv` and fall back to system `python3`. Skills that
read `config.json` expect it at the repo root, so a copied skill needs one nearby.

---

## License

MIT. Adapt it, rebrand it, ship it.
