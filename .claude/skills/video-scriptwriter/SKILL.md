---
name: video-scriptwriter
description: Use when scripting, finalizing, or generating SEO/thumbnail/Shorts material for a YouTube video. Takes a validated topic or concept deep-dive (from the video-scout agent) and produces a full voiceover + on-screen script, coding prompts to record, and a complete YouTube SEO package for both the main video and a Shorts cut. Do not use for topic research — that's video-scout's job.
---

# Video Scriptwriter

## Read the config first
Before writing anything, read `config.json` at the repo root for the channel
identity, author bio, channel URLs and handles, and the sharing configuration.
**Never hardcode any of those** — if a value you need is missing, say so rather than
inventing one. Fields used here: `identity.*`, `channels.*`, `sharing.*`,
`positioning`, `output.videoDir`.

## Positioning, when configured
If config has a `positioning` block, the creator is building evidence for a career
target. Three consequences, all binding:

1. **Hold the altitude.** `positioning.altitude.write` and `.avoid` define what the
   video may be. This bites harder on video than on the blog, because tutorial
   framing is what performs and also what miscasts the creator's level. Flag the
   conflict rather than quietly writing the higher-performing version.
2. **Write for `audienceSeniority`.** Pitch the explanation at that viewer. Over-
   explaining basics to a senior audience is the fastest way to read as junior.
3. **Use `honestFraming` verbatim for any claim about the creator** — in the script,
   the video description, and the sharing posts. Never write anything listed in
   `honestFraming.neverClaim`. On camera this matters more than in text: a viewer
   hears the difference between someone describing what they built and someone
   describing what they read. When the script needs a credibility beat, use
   `honestFraming.leadWith`.

## Output location
Every file this skill produces goes under the directory named by `output.videoDir`
in config (`video-data/` by default), not the repo root: `video-data/script.md`,
`video-data/coding-prompts.md`, `video-data/youtube-seo.md`,
`video-data/shorts-package.md`, `video-data/sharing-posts.md`. Wherever the steps
below say "produce `script.md`", write it to that path.

## Channel identity (the SEO/tone reference)
Build it from `identity.brandName`, `identity.tagline`, and `identity.author.bio`
in config.

If the channel has a recurring episode format, the creator will have described it
(in a concept deep-dive, a previous script, or directly). Use their exact framing
for it. Do not invent a format name or attribute a format the creator has not
actually established.

Voice rules (same as the blog-writer skill): direct, first-person,
technical-peer-to-technical-peer. No hype words, no "in this video we're going to
explore," no fake enthusiasm. Sentences vary in length. Every claim sounds like it
came from someone who actually built the thing.

## Workflow

### Step 0: Confirm understanding
If working from a `concept-deepdive.md` (a genuinely new topic, not from an existing blog post), confirm the creator has actually read it before proceeding. That doc exists specifically to prevent a shallow, definition-level video — if they haven't read it, tell them to read it first and stop.

### Step 1: Full Script
Produce `video-data/script.md`:

```markdown
# [Working Title]

**Format:** Full video | Short | Both
**Est. runtime:** [x] min

## HOOK (0:00–0:15)
[VOICEOVER]: ...
[ON SCREEN]: ...

## SETUP
[VOICEOVER]: ...
[ON SCREEN]: ...

## THE BUILD
[VOICEOVER]: ...
[ON SCREEN]: (live coding — see coding-prompts.md)

## THE AUTOPSY
[VOICEOVER]: ...
[ON SCREEN]: ...

## THE FIX
[VOICEOVER]: ...
[ON SCREEN]: ...

## TAKEAWAY / CTA
[VOICEOVER]: ...
[ON SCREEN]: subscribe end card, newsletter link
```

Leave `[NEEDS: ...]` markers for anything only the creator would know — a specific number, a personal opinion, an internal detail. Do not invent specifics to fill gaps.

### Step 2: Coding Prompts (only if the video includes a live build)
Produce `video-data/coding-prompts.md` — the exact sequence of prompts to type into Claude Code / Cursor / Copilot while recording, in the order they appear in the script, each one labeled with which script beat it belongs to. Write these as realistic prompts a person would actually type, not artificially polished ones — the video's credibility depends on this looking like real usage.

### Step 3: Finalize — YouTube SEO & Thumbnail
Produce `video-data/youtube-seo.md`:

**Titles** — 5 options, hook-driven, honest (no overpromising), most under 60 characters so they don't truncate in search/suggested results.

**Thumbnail**
- Overlay text: 3-6 words max, high-contrast, punchy
- Visual direction: describe the composition and what curiosity/emotion it creates
- Then actually render it: invoke the `video-thumbnail` skill, which builds a real
  1280x720 PNG from the brand template using the colours in `brand.thumbnail`. Pass
  it the overlay text decided here so the thumbnail and title do different jobs
  rather than repeating each other. Do not describe the thumbnail and stop — the
  deliverable is the image file.

**Description**
- First 2-3 lines must hook AND include primary keywords — this is the only part visible before "Show more"
- Full description: what they'll learn, relevant links (newsletter, blog post if applicable, GitHub repo)
- Timestamps: `[NEEDS: exact timestamps after editing]`

**Tags** — 15-20, mixing broad (software architecture, AI coding tools) and specific (bounded context, FastAPI, Claude Code) terms.

### Step 4: Shorts Package (if applicable)
Identify the single most compelling ~30-45 second moment from the full script — usually the reveal beat or a sharp takeaway line. Produce `video-data/shorts-package.md`:
- Short script (voiceover + on-screen text overlay cues — Shorts rely heavily on captions since many are watched muted)
- Its own hook title (shorter and punchier than the main video's)
- Its own description (1-2 lines + link to the full video)
- Its own tags
- Thumbnail text (2-3 words — Shorts thumbnails matter less but still worth having)

### Step 5: Post-Publish Sharing Kit (once the video is live)
Trigger: the creator has uploaded the video and gives you the live URL (`youtu.be/...` or `youtube.com/watch?v=...`), asking for the links/posts to share it. Produce `video-data/sharing-posts.md` with ready-to-paste posts for exactly the channels listed in `sharing.enabledChannels` in config (X, WhatsApp and Reddit by default) — no others. Blog cross-posting (Medium, Dev.to, and the primary blog) is deliberately not handled here; the `blog-writer` skill already covers it per-post when a video ties to an article.

Use only facts already established in `script.md` and `youtube-seo.md` (the hook, the specific autopsy finding, the tools/versions named) — never invent a number, feature, or claim that isn't already in those files. Apply the same voice rules as the rest of this skill: direct, no hype, no "check out my new video."

**Link format — follow `sharing.linkFormat` in config, which defaults to `plain`: the live URL, nothing appended.** Do not generate UTM parameters and do not run it through a link shortener:
- YouTube Studio's own **Analytics → Reach → Traffic Sources → External** report already buckets incoming clicks by referrer domain (`t.co`, `reddit.com`, etc.) automatically, with no tagging required — UTM query strings aren't parsed by YouTube's analytics at all, so appending them to a `youtu.be` link gains nothing there.
- Shortened links (TinyURL, bit.ly, etc.) get caught by Reddit's spam filters more often than a plain `youtu.be` link — actively worse for the platform where trust matters most.
- If the creator later wants to know which *specific post* drove a click within one platform (e.g. distinguishing two different Reddit posts, which YouTube's own report can't do either way), that needs a real self-hosted or paid link tracker — note it as a future option, don't build it now.

**X (Twitter)**
- Single post, ≤220 characters excluding the link — measure the actual string, don't estimate (same discipline as the `blog-writer` skill's X character counts; a URL counts as 23 characters toward X's own limit regardless of true length, but the 220-char budget here is exclusive of the link).
- Hook on line one, no preamble. Link on its own line.
- First comment: tag the relevant account from `sharing.toolAccountsToTag` in config, picking whichever fits the tool actually used in this video, with one sentence on what it built and what broke. Factual, not promotional. Skip the tag entirely if none of the configured accounts genuinely apply.
- At most 2 hashtags, last line only: the brand tag (`identity.brandName` as one word) plus one topical tag.

**WhatsApp**
- 2-3 sentences, written like a text to a specific person, not a broadcast blast. No hashtags, no hype adjectives.
- Sentence 1 names what the video is and why it's worth watching, specifically — not a generic "check this out."
- Close with the link and nothing after it.
- Note in the output: send individually to people it's actually relevant to, not as a group forward.

**Reddit**
- Pick 1-2 subreddits that fit *this specific video's* topic and tools — don't default to the same subs every time. Ground the pick in what the video actually covers (a FastAPI build fits r/Python or r/FastAPI; a Claude Code build fits r/ClaudeAI; a general architecture failure mode fits r/ExperiencedDevs or r/softwarearchitecture). State which subs you picked and why.
- CRITICAL: no self-promo language. No "I made a video," no "subscribe," no channel branding in the post body — Reddit's filters and its users both punish this hard. Lead with the technical problem or finding as a genuine discussion post or question; the video is supporting evidence, not the pitch.
- 2-3 sentences. Mention the link naturally near the end ("full walkthrough here" or similar wording), not as a call to action.
- Flag for the creator: check each subreddit's self-promotion rules and your account's karma/age against them before posting — several subs require an established posting history first, and a fresh account posting a link reads as spam regardless of content quality.

**Report back**: list every post generated with its channel, character count where relevant (X), the subreddits picked and why (Reddit), and the flags above, so the creator can sanity-check before pasting anywhere.

## Copyright/citation rule
If a concept deep-dive includes quotes or close paraphrases from sources, rewrite fully in original words for the script — no lifted phrasing, even short.
