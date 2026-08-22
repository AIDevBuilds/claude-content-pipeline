# AIDevBuilds Video Workflow

## Setup

```bash
./setup.sh
```

That installs everything into the repo's shared `.venv` (never globally), including
`yt-dlp`, which fetches your published video list without needing an API key. Then
fill in `config.json` with your channel URL, handle and brand colours.

To use these outside this repo, copy the pieces into your home `.claude/` folder:
```bash
mkdir -p ~/.claude/agents ~/.claude/skills
cp .claude/agents/video-scout.md ~/.claude/agents/
cp -r .claude/skills/video-scriptwriter .claude/skills/video-thumbnail ~/.claude/skills/
```
Note that both read `config.json` from the repo root, so a copied skill needs one
nearby.

## The workflow

**1. Get a video topic suggestion**
```
Use video-scout to suggest my next video
```
→ Scans Hashnode, Medium, and your YouTube channel (via yt-dlp), then proposes 3-5 candidates — flagging which are "from an existing blog post" (less research needed) vs. "new topic."

**2. Validate the topic**
```
Use video-scout to research and validate: [topic you picked]
```
→ If it's from a blog post: pulls the post's argument + finds a live-codeable demo angle.
→ If it's new: produces `video-data/concept-deepdive.md` — read this yourself first. It exists so you understand the material deeply enough to talk about it off-the-cuff on camera, not just read a script.

**3. Generate the script**
```
Using the video-scriptwriter skill, write the full script
```
→ Produces `video-data/script.md` — voiceover + on-screen notes per beat, structured around the AI Autopsy format.

**4. Get the coding prompts** (if the video has a live build)
```
Give me the coding prompts for this
```
→ Produces `video-data/coding-prompts.md` — exact prompts to type into Claude Code/Cursor/Copilot while recording, matched to each script beat.

**5. Record the video** (outside Claude — this is you, on camera)

**6. Finalize — SEO package**
```
Give me the YouTube SEO and thumbnail details
```
→ Produces `video-data/youtube-seo.md` — 5 title options, thumbnail text + visual direction, full description, 15-20 tags. It then invokes the `video-thumbnail` skill to render the actual PNG at `video-data/images/thumbnail-<n>.png`, 1280×720, using the colours in `brand.thumbnail`.

**7. Get the Shorts version**
```
Also generate the Shorts package from this
```
→ Produces `video-data/shorts-package.md` — a cut-down script, its own title/description/tags/thumbnail text, built from the single strongest moment in the full video.

**8. Once it's uploaded and live, get your sharing kit**
```
Give me the sharing posts, here's the link: https://youtu.be/...
```
→ Produces `video-data/sharing-posts.md` — ready-to-paste posts (and a first comment where relevant) for **X, WhatsApp, and Reddit**, the plain `youtu.be` link with no UTM tagging or shortening, and 1-2 subreddits picked per-video based on that video's actual topic. See "Where the audience-source tracking went" below for why UTM/shorteners were dropped.

All of this workflow's output files live under `video-data/` in the project root, keeping them out of the way of the agent/skill config in `.claude/`.

**Where the audience-source tracking went:** this used to be a separate `utm_gen.py` script that tagged links with UTM params, shortened them via TinyURL, and called an external LLM for per-channel post copy. That's retired — `video-scriptwriter` (Step 5 above) now generates the post copy directly, using only facts already established in `script.md`/`youtube-seo.md`. The UTM tagging and shortening went with it: YouTube Studio's own **Analytics → Reach → Traffic Sources → External** report already buckets clicks by referrer domain automatically, UTM query params aren't parsed by YouTube's analytics at all, and shortened links get flagged by Reddit's spam filters more than plain ones. If you ever want click attribution *within* one platform (e.g. telling two different Reddit posts apart), that needs a real link tracker — worth revisiting later, not solved by UTM on a `youtu.be` link.

**Thumbnail image generation:** handled by the `video-thumbnail` skill, which renders `template.html` in headless Chromium at 2x and downsamples to exactly 1280×720. Colours and the channel tag come from `config.json`, so re-branding means editing that file, not the template. Layout changes belong in `.claude/skills/video-thumbnail/template.html`.

## Why it's split this way
Same principle as the blog workflow: research (video-scout) is noisy and benefits from isolation so it doesn't clutter your main conversation with search results and RSS/API output. Scripting and SEO (video-scriptwriter) need your ongoing context — the actual conversation where you're refining the script — so that stays in the main thread as a skill, not delegated away.
