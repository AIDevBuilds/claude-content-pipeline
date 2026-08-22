---
name: blog-writer
description: Use when outlining, drafting, or finalizing a blog post/newsletter issue. Applies brand voice rules, series conventions, and generates platform-specific SEO metadata plus ready-to-paste social copy (Hashnode, Dev.to, Medium, X, LinkedIn). Do not use for topic research, that's handled by the topic-scout agent.
---

# Blog Writer

## Read the config first
Before writing anything, read `config.json` at the repo root. It supplies the brand
name, the author's name and bio, every channel URL and handle, and the list of
content series. **Never hardcode any of those into a draft or into this file** —
if a value you need is missing from config, say so rather than inventing one.

Fields this skill uses: `identity.brandName`, `identity.author`, `channels.*`,
`series[]`, `positioning`, `output.blogDir`.

## Positioning, when configured
If config has a `positioning` block, the author is writing to build evidence for a
career target. Three consequences, all binding:

1. **Hold the altitude.** `positioning.altitude.write` and `.avoid` define what the
   post may be. If the approved outline has drifted into a tutorial, say so before
   drafting rather than writing it well at the wrong level.
2. **Write for `audienceSeniority`.** Assume that reader's knowledge. Explaining what
   a REST API is to an audience of architects reads as miscalibration, and the
   miscalibration is what gets noticed, not the explanation.
3. **Use `honestFraming` verbatim for any claim about the author.** In the bio, the
   intro, and anywhere the post says "I built" or "I led", the wording comes from
   `honestFraming.useThis`. Never write anything in `honestFraming.neverClaim`, even
   if the research brief implies it and even if it would strengthen the hook. A claim
   that collapses under questioning is worse than a weaker true one. When the post
   needs a credibility anchor, reach for `honestFraming.leadWith` first.

## Output location
Every file this skill produces goes under the directory named by `output.blogDir`
in config (`blog-data/` by default), not the repo root: `blog-data/outline.md`,
`blog-data/draft.md`, `blog-data/seo-and-publish.md`. Images generated via the
`blog-images` skill live alongside them at `blog-data/images/`. Wherever the steps
below say "produce `outline.md`", write it to that path.

## Who's writing
The author named in `identity.author` (name, role, and one-line bio). Voice is
direct, first-person, technical-peer-to-technical-peer. NOT marketing-speak, NOT
hype.

Avoid: exclamation points for hype, "game-changing," "unlock," "supercharge," "in today's fast-paced world," AI-generated-sounding transitions ("In this post, we will explore..."), tidy 3-point listicle structure unless the content genuinely is a list, **em-dashes anywhere** (use a comma, period, colon, semicolon, or parentheses instead; em-dashes are one of the most obvious AI tells and should never appear in outline, draft, or SEO text).

Sentences vary in length: some short, some longer with a real subordinate clause. Every technical claim should sound like it came from someone who built the thing, not someone who read about it.

## The series
Read `series[]` from config: each entry has a `name` and a `description` defining
what belongs in it and what separates it from its neighbours. Tag every post with
exactly one series, and honour the description's guidance on opening style — some
series call for a narrative scenario, others for a direct claim, and forcing the
wrong one reads as constructed rather than earned.

If a proposed post doesn't fit any configured series, say so rather than stretching
one to fit.

## Workflow

### Step 1: Outline (from a research brief)
Given a research brief (from topic-scout, or pasted in directly), produce `blog-data/outline.md`:
- Working title (a few alternatives if the topic is punchy enough to warrant it)
- Series tag
- 3-5 section headers with a one-line summary of what each covers
- Which concrete example anchors the piece
- Estimated read time

Stop after the outline. Wait for approval or edits before drafting.

### Step 2: Detailed Draft
Once the outline is approved, write `blog-data/draft.md`, full article, following the voice rules above. Structure:
- Hook opening (a specific scenario or claim, not a generic definition)
- Body sections per the approved outline
- A concrete example (code, diagram description, or real scenario), never purely abstract
- A closing "takeaway": sharp, quotable, one or two sentences

Leave inline `[NEEDS: ...]` markers anywhere you're missing a detail only the user would know (a real metric, an internal example, a specific tool version).

If the post walks through several terms or concepts side by side (a glossary-style section, a comparison table), give **each one** its own concrete example inline, not just an abstract definition. A reader should never hit a defined term with nothing to anchor it to.

Before treating a strong or superlative claim from the research brief as settled ("the most commonly confused pair," "the standard approach," anything with "most"/"always"/"never"), spot-check it against the brief's cited sources or a fresh search rather than repeating it on faith. If the source doesn't fully back the claim, soften the language instead of asserting it flatly.

**Images:** once the draft has real content, check it for structural concepts a diagram would clarify: a stack/layered model, a two-thing comparison, a decision flow. If one exists, invoke the `blog-images` skill to generate it (hero image and/or inline diagrams); it handles style, palette, and rendering. Don't invoke it for posts that are purely narrative with nothing structural to draw.

**Newsletter CTA:** append a block at the end of every draft, after the closing takeaway, using `channels.newsletter.name` and `channels.newsletter.subscribeUrl` from config:

> **Enjoyed this breakdown?** I write about decisions like this one in my newsletter, **{channels.newsletter.name}**.
>
> [Subscribe here →]({channels.newsletter.subscribeUrl})

The URL comes from config and must never be dropped, altered, or replaced with a guess. The surrounding text should be reworded per post (naming that post's specific topic instead of the generic phrasing above), as long as the link survives intact. If `channels.newsletter.subscribeUrl` is empty in config, skip the block entirely rather than inventing a URL.

### Step 3: Finalize
Before producing SEO details, confirm two things and flag rather than silently finalizing if either is missing:
- Every image the post needs has been generated (via `blog-images`) and is referenced in `blog-data/draft.md`.
- The newsletter CTA block is present at the end of `blog-data/draft.md` with the subscribe link intact.

When the user says the draft is ready (after their own edits), produce `blog-data/seo-and-publish.md` containing:

**Primary blog** (the platform named in `channels.blog.platform`, published at `channels.blog.url`)
- Display Title (≤60 chars recommended, 140 max)
- Article Slug (URL-safe: lowercase, hyphenated, no stop words unless needed for clarity)
- SEO Title (≤60 chars, the meta title tag; can match Display Title or be tightened further for search)
- SEO Description (≤150 chars, the meta description tag)
- Tags (lowercase)

This is the canonical home of the post. Every cross-post below points back to it.

**Dev.to** (skip this section if `channels.devto.profileUrl` is empty)
- Title (can match the primary)
- Tags (max 4, lowercase, no spaces: e.g. `softwarearchitecture` not `software architecture`)
- Canonical URL reminder: point back to the primary blog original

**Medium** (skip this section if `channels.medium.profileUrl` is empty)
- Title
- Subtitle (Medium's version of a dek/description)
- Tags (up to 5)
- Canonical URL reminder: point back to the primary blog original

**X** (the account at `channels.x.handle`)

Write ready-to-paste post text, not a description of what to post. Match the account's established voice, drawn from what already performs there:
- Open with a flat, contrarian claim on its own line. No preamble, no "I wrote about...". Examples of the register: "Your architecture diagram is lying to you." / "It built a gorgeous architecture. Then it quietly sabotaged its own database."
- Setup, then reveal. Short lines, hard line breaks between beats. White space does the pacing.
- Technical and blunt. No hype adjectives, no "🚀 Excited to share".
- Hashtags: at most 2, at the end. The brand tag (`identity.brandName` as one word, e.g. `#YourBrand`) plus one topical tag (e.g. `#ClaudeCode`, `#MCP`). Never mid-sentence.
- Emoji: sparing and functional only. 🧵 to mark a thread is established and fine; decorative emoji are not.

Decide the format from the content and say which you chose and why:
- **Single post** when the whole idea lands in one hook plus the link.
- **Thread** when the post has a natural enumeration (e.g. five terms, four failure modes). Number the posts, write each one out in full, and mark the opener with 🧵. Put the article link in the final post, not the first, so the thread isn't cut short by the algorithm.
- **Post + reply** when there is one strong hook and the link would dilute it. Hook stands alone as the post; the link goes in the first reply. Label these clearly as "Post 1" and "Reply to Post 1".

Keep every individual post under 280 characters and state the character count next to each one so it can be verified at a glance. X counts any URL as 23 characters regardless of its real length, so measure with that substitution rather than counting the placeholder. Verify the counts by actually measuring the strings, never by estimating.

**LinkedIn**

Longer and more context-setting than X, but the same anti-hype voice. Ready-to-paste text.
- Hook in the first two lines: LinkedIn truncates after roughly 200 characters behind a "see more", so the payoff has to be above that fold.
- Short paragraphs, one to three lines each, with blank lines between them. Dense blocks get skipped.
- Frame around the reader's problem, not the article's existence. "Here's a distinction that costs teams real time" beats "I published a new post".
- Close with a genuine question to invite comments, then the link last so the final call to action is the click.
- 3 to 5 hashtags at the very end.
- No engagement bait ("Agree? 👇", "Thoughts??"), no emoji bullets.

**Audience constraint: coworkers and managers are connected on LinkedIn.** Never write an anecdote that describes the user's team, a colleague's mistake, or an incident at their workplace, even anonymised ("a teammate spent an afternoon...", "our changelog", "someone on my team"). It reads as publicly critiquing a colleague's work in front of their management chain. Frame the same point as a general industry pattern or in second person instead: "You can spend an afternoon building an MCP server for a problem a 40-line Skill would have closed." This keeps the concrete stakes without implicating anyone. The same caution applies to the article itself and to X, since colleagues can find published work; LinkedIn is simply where the exposure is guaranteed.

**Link placement on LinkedIn specifically (as of 2026): put the link in the post body, not the first comment.** The first-comment workaround has been patched; LinkedIn detects "bridge behavior" (a post engineered to funnel readers into a comment) and applies the same reach penalty, with comment-link visibility reportedly cut by up to 80%. Burying the link now costs the same reach and adds friction. This does not apply to X, where link-in-reply remains a valid format choice.

The body-link penalty itself is genuinely contested (reported anywhere from an 18.8% median reduction in a 1.3M-post study to ~60%, with at least one large analysis finding no penalty at all), so don't over-optimize placement. What every source agrees on: a self-sufficient post that delivers real value on its own outperforms a teaser. Optimize for that, then make the link visible. Reach is not the goal; article reads are, and a visible link seen by fewer people beats a buried link seen by more.

**Hooks on both platforms must earn the click, not just the scroll.** The social copy will often give away the post's core idea, which is correct (self-sufficient posts travel further). So the click has to be earned by something the social copy deliberately does not resolve: a decision procedure, a test, a specific worked example, the tradeoff. Name that gap explicitly in the CTA ("the one question that tells you which you need" beats "full breakdown"). Never end on a bare "read more" or "link below".

**Cross-post checklist**
- [ ] Canonical URL set on Dev.to
- [ ] Canonical URL set on Medium
- [ ] CTA block added linking to newsletter
- [ ] X post/thread published, article link included in the correct position
- [ ] LinkedIn post published
- [ ] Images re-uploaded on platforms that don't pull them from the canonical (Medium, Dev.to)

## Copyright/citation rule
If the research brief includes quotes or close paraphrases from sources, rewrite fully in original words for the draft, no lifted phrasing, even short. This applies doubly to any compressed, quotable summary line (especially a closing takeaway): these tend to converge on phrasing that's already common across whatever comparison genre the post is writing about. Before finalizing a line like that, search for the distinctive phrase; if it lands close to an existing source's actual wording, rewrite it further rather than assume independent convergence is safe to publish.
