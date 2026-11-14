---
name: video-shorts
description: Renders a branded vertical YouTube Short (1080x1920 MP4) from an ElevenLabs voiceover and a small JSON spec, using a fixed Remotion template in the light framed style with word-by-word captions. Not an AI video generator. Use after video-scriptwriter has produced the Short's script and the voiceover exists, or standalone: "render the Short for <article>".
---

# Video Shorts

## Why a template
Same reason as `blog-images` and `video-thumbnail`: a channel's Shorts have to look
like a set. The layout lives in `src/Short.tsx`; colours, brand name and URL come from
`config.json` (`brand.diagram.light`, `identity.brandName`, `channels.blog.url`).
Re-branding means editing `config.json`, never the template.

## Setup (once per machine)
```bash
cd .claude/skills/video-shorts && npm install     # local node_modules, never npm -g
```
Rendering uses Playwright's Chromium from `./setup.sh` when present (Remotion's own
browser crashed on launch here), and `ffprobe` for the audio length.

## Folder layout
`scripts/render_short.py` (the renderer), `src/` (the Remotion template),
`assets/fonts/` and `assets/icons/` (approved Lucide icons, ISC licence),
`examples/example.json` (a generic spec). Nothing is written inside the skill while
rendering: the voiceover copy, fonts and props go to `<output.videoDir>/.cache/shorts/`,
which is safe to delete.

## Workflow
1. **Script first.** The voiceover text comes from `video-scriptwriter` (or an
   already published post, word for word). Never write new claims here. Content
   limits and honest framing apply exactly as for posts.
2. **Voiceover.** Generate with the ElevenLabs connector, using the voice and model in
   `config.json` `video.voice` (`name`, `model`). If that is not set, list the
   account's voices and pick a clear general-purpose one. Save the chosen take as an mp3 under
   `video-data/`.
3. **Spec** at `video-data/shorts/<slug>.json`. Each Short is ONE diagram that
   evolves with the voiceover (YouTube demonetizes look-alike template output, so
   every Short gets its own diagram). The worked example is
   `.claude/skills/video-shorts/examples/example.json`. Fields:
   - `eyebrow` (series name), `audio`, `text` (exact spoken words), `timings`
     (word timings from an ElevenLabs transcription, matched word for word to `text`)
   - `chunks`: caption chunks, 2-4 words, one line each, covering `text` exactly
   - `emphasis`: 1-2 key words drawn in orange
   - `headers`: `[{at, title, accent?, accentAt?}]`, max two lines, frame 0 is the hook
   - `nodes`: `{id: {icon, label, sub?, tone?, mono?}}` with approved Lucide icons
   - `states`: keyframes `{at, edges, nodes: {id: {x, y, w, h?, row?, tone?, label?, sub?, opacity?, glow?}}}`;
     nodes move between states, new nodes pop in, missing ones fade out
   - `packets`, `chips`, `badges`, `meters`, `notes`: timed overlays
   - `dividers`: `[{at, until?, x, y1, y2}]`, a dashed vertical boundary line
   - edge styles: an edge may carry a third element, `[a, b, {tone?, glow?, width?}]`;
     `tone: "b"` draws it in the problem colour with a matching arrowhead
   - chips: `between: [a, b]` centres the chip in the gap between two nodes and follows
     them as they move (use it instead of swapping chips mid-video); `toneAt` turns it
     to the problem colour at that time
   Anything timed at 0 is drawn complete on frame 0.
   Pacing: a visual change every 2-3s, a bigger change every 5-7s, hook drawn at
   frame 0. Keep content in x 72-920, y 290-1440.
   **Frame 0 is the hook,** fully drawn (headline plus the first diagram state), and
   the headline says the same thing as the first spoken line. No title card, logo
   or empty build-up before it.
   **Vary the shape.** The template is fixed, so vary what goes in it: compare the
   new spec with the last few in `video-data/shorts/` and change the diagram shape
   (flow, comparison, stack, before/after, single node under pressure), the headline
   pattern and the overlay types. A spec that reuses an earlier Short's nodes and
   states with new labels is the "template with little to no variation" YouTube's
   inauthentic-content rule describes; redesign it.
4. **Render:**
   ```bash
   .venv/bin/python .claude/skills/video-shorts/scripts/render_short.py video-data/shorts/<slug>.json
   ```
   Output: `video-data/shorts/<slug>.mp4`.
5. **Independent review** (never the writer): export frames and send them to a fresh
   reviewer agent with the spec, the voiceover timings and frame 0 of the last three
   Shorts; it checks the hook frame, pacing, accuracy, safe zones and that this Short
   doesn't look like a re-labelled copy of an earlier one. Fix what it flags, up to 3
   rounds, stop at PASS.
6. **Check** the MP4 before upload: captions in sync, nothing important in the
   bottom ~20% or right edge (YouTube's UI covers them), no em-dashes on screen.
   The top ~260px is covered too: on a Samsung S25 YouTube's back and search icons sit
   over the dark band, and on an iPhone 18 Pro the status bar does, with the icons
   down to about y 255 (checked 6 Nov 2026). So the band carries no text; the series
   label sits at y 262, just above the header. Keep every card's right edge at or
   left of x 920, including glows and badges, or it runs into the like button.
7. **Upload:** tick YouTube's "Altered or synthetic content" box for any
   ElevenLabs voice. Description ends with `identity.disclaimer`. Set the related
   video and pinned comment from the Shorts package, pick the hook frame as the
   thumbnail, and publish on the scheduled day (never batch-publish, never delete
   and re-upload an underperformer). Log it in `video-data/shorts-log.md`.
