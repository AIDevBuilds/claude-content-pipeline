# How to make a Short

A vertical YouTube Short (1080x1920, about 30 to 45 seconds) made from one idea: an article of yours, a post of yours, or text you paste. Claude writes the script, you approve it, Claude makes the voiceover and the animated diagram, and independent reviewers check each stage. About 50 minutes of your time per Short, most of it waiting.

## 1. How to ask

You don't need a long prompt or a slash command. Say what you want and give the source, in any of these ways.

**A link**
> Make a Short from this article: https://your-blog.example/...

**Text pasted in the chat**
> Make a Short from this post: <paste the text>

**A screenshot** (drop it into `blog-data/inbox/` and say so)
> Make a Short from the screenshot in the inbox.

**Just a topic from your own blog**
> Make a Short from the caching article, the part about stale reads.

Optional extras you can add to the same message:
- **A focus:** "only the refund example", "the test at the end".
- **A length:** "30 seconds" (default is 30 to 45).
- **A series label:** one of the `series` names in `config.json`.

Claude picks the right skill itself. If you want to be explicit, `/video-scriptwriter` writes the script and `/video-shorts` renders it.

## 2. What counts as a good source

| Source | Works? | Notes |
|---|---|---|
| Your own article (link or text) | Yes, best | Scripts stay inside what the article already claims. |
| Your own LinkedIn or X post | Yes | Paste the text. Links to posts often need a login, so I may not be able to open them; if I can't, I'll say so and ask for the text or a screenshot. |
| A public article or docs page by someone else | Yes, with care | Your own angle only, credited by name in the description. No copied sentences or images. I'd read it and ask what your point is. |
| Someone else's social post | Only as a starting point | Same rule: your own point, credited, never a retelling. |
| Anything from your job | **No** | Not even anonymised. Your content limits apply to Shorts exactly as to posts. |
| An idea with no source | Ask me first | I need a source or your own reasoning to draw from. I won't invent claims. |

## 3. What happens, step by step

| # | Step | Who | Check | You |
|---|---|---|---|---|
| 1 | Read the source, find the single idea and your own angle, write 4 hook options and a script (about 90 to 100 words for 40 s) | `video-scriptwriter` | **Script gate:** an independent reviewer checks the hook rubric and that it isn't a near-copy of the last five Shorts, up to 3 rounds | Pick the hook, approve the script |
| 2 | Voiceover with ElevenLabs, then a transcript for caption timing | me | **Voice gate:** an independent reviewer compares the take with the script, up to 2 rounds | Listen to the take |
| 3 | Diagram spec (nodes, arrows, caption chunks) and render | `video-shorts` | **Visual gate:** an independent reviewer looks at frames, up to 3 rounds | Watch the video |
| 4 | Upload text: title, description with the disclaimer, tags | me | Quick copy review | Paste into YouTube Studio |

The reviewers are separate agents that read the work cold. Every Short gets its own purpose-built diagram, never a swapped-text template, because YouTube demonetises mass-produced look-alike content.

**Hooks.** The first line and frame 0 are the hook: no greeting, no channel name, the same message spoken and on screen, and a payoff the Short actually delivers. The rules and hook patterns are in `video-scriptwriter` ("Hooks and packaging").

**Why not a Short every day.** YouTube's own Shorts team says upload frequency on its own doesn't boost performance; each Short is judged by whether its test audience keeps watching. Its inauthentic-content rule (July 2025) targets templated, repetitive, mass-produced Shorts with AI voices, which is what a daily script-generated Short would look like. So cadence comes from your publishing schedule, and every Short needs its own angle and a visibly different diagram.

## 4. What I will ask you

- **Which source**, if you didn't give one.
- **Your OK on the script** before I spend voice credits.
- **Any fact only you know**, as a marker in the script. I won't guess.
- **A final look** at the video.

## 5. Where the files land

| File | Where |
|---|---|
| Script | `video-data/script.md` |
| Voiceover takes | `video-data/voice-tests/` |
| Word timings | `video-data/shorts/<slug>.words.json` |
| Diagram spec | `video-data/shorts/<slug>.json` |
| **Finished video** | `video-data/shorts/<slug>.mp4` |

A worked example: `.claude/skills/video-shorts/examples/example.json`.

## 6. Upload checklist (YouTube Studio)

- [ ] Tick **"Altered or synthetic content"** when the voice is ElevenLabs.
- [ ] Description ends with your `identity.disclaimer` from `config.json` (if set).
- [ ] Add the newsletter link to the description (never promise a schedule).
- [ ] Credit any source that isn't yours.
- [ ] Add it to the **Shorts** playlist and to its series playlist.
- [ ] Set the **related video** and post the **pinned comment** from the Shorts package.
- [ ] Pick the hook frame (full headline visible) as the thumbnail.
- [ ] Publish on the day your schedule says. Never delete and re-upload a Short that underperforms.
- [ ] After 7 days, send Claude the viewed vs swiped away, average % viewed and subscribers for the log (`video-data/shorts-log.md`).

## 7. Costs and limits

- **ElevenLabs credits** (Starter plan: 30,000 a month): about 170 per 10 seconds of voice per take, so roughly 700 for a 40-second Short; one take by default. Transcription for caption timing is about 60 for 10 seconds. A Short costs roughly 800 to 1,500 credits, so you can make well over a dozen a month.
- **Time:** about 50 minutes of your attention per Short; plan it into your week.
- **Voice:** set in `config.json` under `video.voice` (name and model). Without it, Claude lists your ElevenLabs voices and picks a clear general-purpose one.
- **If the voice reviewer finds a wrong or dropped word,** I regenerate only that take (one at a time) to save credits.

## 8. Common slips

- **"Just make a Short" with no source.** Give me a link, text or a topic.
- **Pasting something from work.** I'll stop and ask for something public instead.
- **Skipping the script approval.** It's the cheapest point to fix anything; a re-recorded voice costs credits.
- **Posting before the "synthetic content" box is ticked.**
