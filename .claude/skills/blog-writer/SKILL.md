---
name: blog-writer
description: Use when outlining, drafting, or finalizing a blog post/newsletter issue. Applies brand voice rules, series conventions, and generates platform-specific SEO metadata plus ready-to-paste social copy (Hashnode, Dev.to, Medium, X launch + two-week drip, LinkedIn, Reddit/Hacker News). Do not use for topic research, that's handled by the topic-scout agent.
model: opus
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
If config has a `positioning` block, the author is writing to show expertise at
the level in `positioning.targetLevel`. Three consequences, all binding:

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

## Content limits
Read every file in `contentLimits.files` (config) before outlining; they outrank
everything above. In every case:
- No material from the author's job: code, designs, diagrams, metrics, incidents,
  project, client or employer names. Not anonymised, not "inspired by".
- Nothing that names or implies the employer or its clients, and nothing negative
  about them.
- Examples, scenarios and code are written from scratch for the post, or come from
  public sources. Label a hypothetical scenario as one.
- Anything else the limits files forbid (for example monetisation or certain
  contacts).
- If unsure whether something is allowed, leave it out and ask.

## Output location
Every file this skill produces goes under the directory named by `output.blogDir`
in config (`blog-data/` by default), not the repo root: `blog-data/outline.md`,
`blog-data/draft.md`, `blog-data/seo-and-publish.md`. Images generated via the
`blog-images` skill live alongside them at `blog-data/images/`. Wherever the steps
below say "produce `outline.md`", write it to that path.

`blog-data/images/` holds only the article currently being written. Once an article
is published, archive everything that belongs to it in
`blog-data/archive/<YYYY-MM-DD>-<slug>/` (publish date, short slug):

```
archive/<date>-<slug>/
  outline.md  draft.md  research-brief.md  seo-and-publish.md  medium.html
  images/             inline diagrams the article itself uses (draft paths stay images/<file>)
  images/x/           images made for X posts about the article (launch, drip)
  images/linkedin/    images made for LinkedIn posts about the article
  images/newsletter/  images made for a newsletter issue about the article
  images/social/      an image used on more than one platform
  images/specs/       the JSON specs the card-grid images were rendered from
```

Images made later for posts about an already-archived article go straight into
that article's platform folder, not into `blog-data/images/`. After any move,
update every path that points at the moved files: any schedule or tracker that
links to them, newsletter block files and `seo-and-publish.md`. Brand
images that belong to no article (banners, profile and publication social images)
live in `blog-data/channel-updates/`, next to that platform's settings note.

## Who's writing
The author named in `identity.author` (name, role, and one-line bio). Voice is
direct, first-person, technical-peer-to-technical-peer. NOT marketing-speak, NOT
hype.

Avoid: exclamation points for hype, "game-changing," "unlock," "supercharge," "in today's fast-paced world," AI-generated-sounding transitions ("In this post, we will explore..."), tidy 3-point listicle structure unless the content genuinely is a list, **em-dashes anywhere** (use a comma, period, colon, semicolon, or parentheses instead; em-dashes are one of the most obvious AI tells and should never appear in outline, draft, or SEO text).

Sentences vary in length: some short, some longer with a real subordinate clause. Every technical claim should sound like it came from someone who has reasoned it through and could defend it, not someone who skimmed a summary. Concreteness comes from worked examples built for the post, never from the author's job.

## The series
Read `series[]` from config: each entry has a `name` and a `description` defining
what belongs in it and what separates it from its neighbours. Tag every post with
exactly one series, and honour the description's guidance on opening style — some
series call for a narrative scenario, others for a direct claim, and forcing the
wrong one reads as constructed rather than earned.

If a proposed post doesn't fit any configured series, say so rather than stretching
one to fit.

## Hooks and packaging
A cold reader decides in the title, the first line of a social post, or the subject
line. Hooks are written as their own deliverable, never lifted from the middle of
the draft, and every hook (title, opening, launch post, each drip and follow-up
post, newsletter subject) is checked against the rubric below. (Added 31 Oct 2026
after an independent audit; mirrors the video-scriptwriter rubric.)

**Write options, pick one, show the rest.** Titles and launch hooks get 3 to 4
options in different patterns:
- **Counter-intuitive claim:** something the target reader believes, contradicted by
  the article ("Most AI guardrails can't authorize anything.").
- **Stakes in one line:** a specific consequence from the article, labelled as an
  example where it is one ("Your guardrail approved a $509 refund.").
- **The distinction:** two things readers treat as one, named ("Consistent is not
  valid.").
- **The decision question:** a question the reader can't answer yet and the article
  answers ("Where does the human label enter your eval?").

**Every hook must pass all of these:**
1. **First words carry it.** No warm-up, no "In this post", no context sentence
   before the hook. Front-load the claim: feeds, inboxes and search results cut
   from the right.
2. **Specific, not complete.** Name the object (a refund, a judge, a queue), not
   "this one mistake". Give the claim, hold back the mechanism; a hook that resolves
   everything has no click left in it.
3. **The article pays it off, early.** The opening's first example proves the
   title's claim, and the thesis is stated within the first ~150 words. A hook the
   article doesn't pay off is clickbait, and with this audience it costs credibility.
4. **Backed, with its qualifier.** Any "most", "never", "can't" or number in a hook
   is supported by the article in the same strength. If the article says "most",
   the hook does not say "all".
5. **Altitude holds.** Pitched at `audienceSeniority`. No "How to", "A beginner's
   guide", "X explained" or "What is" framings; those signal the level below.
6. **Honest framing holds.** No implied experience beyond `honestFraming.useThis`,
   nothing from `neverClaim`, nothing from the author's job.
7. **One promise across the package.** Title, hero or card-grid title, LinkedIn first
   line, X Post 1 and newsletter subject make the same promise in different words.

Send the chosen hook and the alternatives to `copy-reviewer` with this rubric, so it
judges the hook against it rather than in general.

## Workflow

### Step 1: Outline (from a research brief)
Given a research brief (from topic-scout, or pasted in directly), produce `blog-data/outline.md`:
- Working title: 3 to 4 options in different patterns from "Hooks and packaging",
  each with one line on what the article must deliver to pay it off. Recommend one.
- Series tag
- 3-5 section headers with a one-line summary of what each covers
- Which concrete example anchors the piece
- Estimated read time

**Length budget: about 3,000 words (roughly 12 minutes) per post.** A new author's
readers are cold, and few will commit 20+ minutes to someone they don't know yet. If the outline would run longer, say so and propose a split into
two posts (name the split point and what each half's standalone claim is) rather
than outlining one long piece. Two posts at the right length also mean two
publishing moments instead of one.

Stop after the outline. Wait for approval or edits before drafting.

### Step 2: Detailed Draft
Once the outline is approved, write `blog-data/draft.md`, full article, following the voice rules above. Structure:
- Hook opening: a specific scenario or claim, not a generic definition. The first
  sentence is part of the hook, the first example proves the title's claim (not a
  neighbouring one), and the thesis is stated by about word 150.
- Body sections per the approved outline
- A concrete example (code, diagram description, or a scenario built for the post or taken from a public source), never purely abstract
- A closing "takeaway": sharp, quotable, one or two sentences

Leave inline `[NEEDS: ...]` markers anywhere you're missing a detail only the user would know (a personal opinion, a public source to cite, a specific tool version, a detail from their personal projects). Never ask for an internal or work example, metric or incident.

After writing, count the draft's words (excluding the references list). If it exceeds the ~3,000-word budget from Step 1, say so with the count and suggest the cleanest split point, instead of silently delivering a long draft.

If the post walks through several terms or concepts side by side (a glossary-style section, a comparison table), give **each one** its own concrete example inline, not just an abstract definition. A reader should never hit a defined term with nothing to anchor it to.

Before treating a strong or superlative claim from the research brief as settled ("the most commonly confused pair," "the standard approach," anything with "most"/"always"/"never"), spot-check it against the brief's cited sources or a fresh search rather than repeating it on faith. If the source doesn't fully back the claim, soften the language instead of asserting it flatly.

**Images:** once the draft has real content, check it for structural concepts a diagram would clarify: a stack/layered model, a two-thing comparison, a decision flow. If one exists, invoke the `blog-images` skill to generate it (hero image and/or inline diagrams); it handles style, palette, and rendering. Don't invoke it for posts that are purely narrative with nothing structural to draw.

**Newsletter CTA:** append a block at the end of every draft, after the closing takeaway, using `channels.newsletter.name` and `channels.newsletter.subscribeUrl` from config:

> **Enjoyed this breakdown?** I write about decisions like this one in my newsletter, **{channels.newsletter.name}**.
>
> [Subscribe here →]({channels.newsletter.subscribeUrl})

The URL comes from config and must never be dropped, altered, or replaced with a guess. The surrounding text should be reworded per post (naming that post's specific topic instead of the generic phrasing above), as long as the link survives intact. If `channels.newsletter.subscribeUrl` is empty in config, skip the block entirely rather than inventing a URL.

**Disclaimer footer:** if `identity.disclaimer` is set in config, add it verbatim as the last line of every draft, after the newsletter CTA, in italics.

**Content-limit check:** before showing the user a finished draft, check it against the "Content limits" section above and every file in `contentLimits.files`. Under the draft, list anything close to the line, plus any technique, tool or code in the post that might be novel rather than publicly known, so the author can clear it before publishing. Say "nothing flagged" if that is the result.

### Review loop (draft and every piece of social copy)
Before showing the user a finished draft, and again before handing over
`seo-and-publish.md`, run the write-review loop with the `copy-reviewer` agent:

1. Send the agent the text, the platform, and the round number. Spawn it fresh each
   round, so it reads the text cold and never sees your reasoning.
2. On `VERDICT: REVISE`, fix only what it flagged. Keep the sentences, rhythm and
   best phrases it did not flag; a fix that reads worse than the original is not a fix.
   If you disagree with a finding, keep the text and note why.
3. Repeat until `VERDICT: PASS`, **at most 5 rounds**. If round 5 still says REVISE,
   stop and show the user the remaining findings instead of looping further.
4. `needs-author` findings are never fixed by inventing detail. They become
   `[NEEDS: ...]` markers or a question to the user.

For an article, review it section by section rather than in one pass, so findings
stay specific. For social copy, review each piece (launch post, each drip post, the
LinkedIn post, each Reddit body) separately.

Under the final text, add a short loop record: rounds run, and the findings fixed or
declined.

**What the loop is not.** It makes the writing better and more accurate. It does not
change who wrote it. Where a platform bans AI-written posts or requires disclosure
(see `blog-data/reddit-rules.md`: r/softwarearchitecture bans AI-generated posts,
r/ExperiencedDevs requires disclosure, r/LLMDevs asks for attribution), give the
user notes and a structure to write from, and run the loop on *their* draft. Never
present a Claude-written body as ready to post on those platforms. Medium allows
AI-assisted articles but requires a disclosure (see the Medium section of Step 3).

### Newsletter issues are written in the template's block format
For any newsletter issue, write the content in the order and shape of the newsletter's template, so every piece pastes straight into its block. Follow `blog-data/newsletter/TEMPLATE.md`: one fenced block per piece of text, a block-by-block paste file named `blog-data/newsletter/issue-NN-blocks.md` (subject options, preview text, send date, image paths with alt text, links, a before-you-send checklist). Render any card images as landscape, light, framed via `blog-images`. The copy-reviewer loop applies to the content and again to anything added when laying it out. Never promise a schedule beyond "once a month".

Subject options (3) follow the hooks rubric: a claim or a decision question, never a
contents label ("Two articles on..."), front-loaded. Preview text extends the subject
with the stakes or the withheld gap, never restates it or lists the issue's contents.
Open rates are inflated by Apple Mail Privacy Protection, so judge subject lines by
clicks, not opens.

### Step 3: Finalize
Before producing SEO details, confirm two things and flag rather than silently finalizing if either is missing:
- Every image the post needs has been generated (via `blog-images`) and is referenced in `blog-data/draft.md`.
- The newsletter CTA block is present at the end of `blog-data/draft.md` with the subscribe link intact, followed by the disclaimer footer if `identity.disclaimer` is set.

When the user says the draft is ready (after their own edits), produce `blog-data/seo-and-publish.md` containing:

**Primary blog** (the platform named in `channels.blog.platform`, published at `channels.blog.url`)
- Display Title (≤60 chars recommended, 140 max)
- Article Slug (URL-safe: lowercase, hyphenated, no stop words unless needed for clarity)
- SEO Title (≤60 chars, the meta title tag; can match Display Title or be tightened further for search)
- SEO Description (≤150 chars, the meta description tag)
- Tags (lowercase)
- Hook record: the hook pattern used for the title, X Post 1 and the LinkedIn first
  line, so a weekly review can compare patterns against clicks over time.

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
- **AI disclosure (Medium policy, checked Oct 2026):** a story that includes
  AI-generated or AI-assisted text must say so, or Medium limits it to the author's
  own followers. Drafts from this skill count as AI-assisted. Put one plain sentence
  in the first two paragraphs of the Medium copy, worded by the author, for example
  "I wrote this with help from an AI writing assistant; the decisions, examples and
  edits are mine." Grammar checks, outlining and fact-checking need no disclosure.
  Do not put a mostly AI-generated story behind the Partner Program paywall. Check
  the target publication's own AI rules before submitting.

**X** (the account at `channels.x.handle`)

Write ready-to-paste post text, not a description of what to post. Match the account's established voice, drawn from what already performs there:
- Open with a flat, contrarian claim on its own line. No preamble, no "I wrote about...". Examples of the register: "Your architecture diagram is lying to you." / "It built a gorgeous architecture. Then it quietly sabotaged its own database."
- Contrarian does not mean absolute. Keep the article's qualifier ("probably",
  "most") in the hook; an overstated hook is the first thing a senior reader rebuts.
- Setup, then reveal. Short lines, hard line breaks between beats. White space does the pacing.
- Technical and blunt. No hype adjectives, no "🚀 Excited to share".
- Hashtags: at most 2, at the end. The brand tag (`identity.brandName` as one word, e.g. `#YourBrand`) plus one topical tag (e.g. `#ClaudeCode`, `#MCP`). Never mid-sentence.
- Emoji: sparing and functional only. 🧵 to mark a thread is established and fine; decorative emoji are not.

**Why one post per article is not enough.** A small account's posts reach almost nobody, and X deprioritizes posts carrying an external link. A single launch post (or thread) per article is one lottery ticket every few weeks. So the X output is a two-week package: one launch, then a drip of standalone posts that each carry one idea from the article natively, with no link.

**1. Launch (day 0).** Decide the format from the content and say which you chose and why:
- **Post + reply** (the default): the hook stands alone as the post; the link goes in the first reply. Label these "Post 1" and "Reply to Post 1".
- **Thread** when the post has a natural enumeration (e.g. five terms, four failure modes). Number the posts, write each one out in full, and mark the opener with 🧵. The final post carries no link; the link goes in a reply to the final post.

**2. Drip (days 1 to 14): 8 to 10 standalone posts.** Each one:
- Carries exactly one idea from the article (a distinction, a test, a failure mode, a number, a code contrast) and makes complete sense to someone who never saw the launch.
- Opens with its own hook line that passes the rubric in "Hooks and packaging", and
  never reuses the launch hook or another drip post's first line.
- Invites a substantive reply where it fits (a decision the reader has faced), never
  engagement bait.
- Has no link and no "from my latest post". If a reader wants more, the pinned post and bio do that job.
- Uses a varied shape across the set, so the feed doesn't read as one post repeated: a flat claim, a before/after, a short "A vs B" contrast, a question the article answers, a code snippet of 5 lines or fewer, a diagram post.
- Names an image from `blog-data/images/` when one fits (diagram posts do well); at least two posts in the set should use one. Never reference an image that doesn't exist.
- Is labelled with a suggested day (`Day 1`, `Day 2`, `Day 4`, ...), spaced so there is roughly one per day with a couple of gaps.

**Track balance across drips.** A drip fills two weeks of X posts with one article's
track. If config sets `positioning.contentMix` and two articles of the same track
would run back to back, interleave: put a few standalone posts from the other track
(from an earlier article in that track) into the drip days, so the feed stays near
the ratio. Say in the package which track each post counts toward.

The same voice rules apply to every drip post. Hashtags: the drip posts carry at most one topical tag, or none; the brand tag goes on the launch only.

Keep every individual post under 280 characters and state the character count next to each one so it can be verified at a glance. X counts any URL as 23 characters regardless of its real length, so measure with that substitution rather than counting the placeholder. Verify the counts by actually measuring the strings, never by estimating.

**LinkedIn**

Longer and more context-setting than X, but the same anti-hype voice. Ready-to-paste text.
- Hook in the first line, under about 140 characters: the fold sits near 200
  characters on desktop but only 2 to 3 lines on mobile (estimates, not a LinkedIn
  spec). State the first line's character count, measured.
- The line after the hook starts paying it off. LinkedIn's ranking penalises posts
  people scroll past quickly and rewards reading time, so a teaser that makes readers
  scroll past costs reach; the post must reward the reader for stopping.
- Short paragraphs, one to three lines each, with blank lines between them. Dense blocks get skipped.
- Frame around the reader's problem, not the article's existence. "Here's a distinction that costs teams real time" beats "I published a new post".
- Close with a genuine question to invite comments, then the link last so the final call to action is the click.
- 3 to 5 hashtags at the very end.
- No engagement bait ("Agree? 👇", "Thoughts??"), no emoji bullets.
- Name the image to attach: the hero diagram from `blog-data/images/` if one exists. A text post with only a link preview card is the weakest LinkedIn format.

After the launch post, write **two native follow-up posts** for the following week, with no link at all. Each takes one idea from the article (ideally the diagram plus a short explanation of it) and stands completely on its own. Label them "LinkedIn follow-up 1 (suggested day N)" and "LinkedIn follow-up 2 (suggested day N)". Each follow-up gets its own first-line hook under the same rubric, in a different pattern from the launch post.

**Audience constraint: coworkers and managers are connected on LinkedIn.** Never write an anecdote that describes the user's team, a colleague's mistake, or an incident at their workplace, even anonymised ("a teammate spent an afternoon...", "our changelog", "someone on my team"). It reads as publicly critiquing a colleague's work in front of their management chain. Frame the same point as a general industry pattern or in second person instead: "You can spend an afternoon building an MCP server for a problem a 40-line Skill would have closed." This keeps the concrete stakes without implicating anyone. The same caution applies to the article itself and to X, since colleagues can find published work; LinkedIn is simply where the exposure is guaranteed.

**Link placement on LinkedIn specifically (as of 2026): put the link in the post body, not the first comment.** The first-comment workaround has been patched; LinkedIn detects "bridge behavior" (a post engineered to funnel readers into a comment) and applies the same reach penalty, with comment-link visibility reportedly cut by up to 80%. Burying the link now costs the same reach and adds friction. This does not apply to X, where link-in-reply remains a valid format choice.

The body-link penalty itself is genuinely contested (reported anywhere from an 18.8% median reduction in a 1.3M-post study to ~60%, with at least one large analysis finding no penalty at all), so don't over-optimize placement. What every source agrees on: a self-sufficient post that delivers real value on its own outperforms a teaser. Optimize for that, then make the link visible. Reach is not the goal; article reads are, and a visible link seen by fewer people beats a buried link seen by more.

**Hooks on both platforms must earn the click, not just the scroll.** The social copy will often give away the post's core idea, which is correct (self-sufficient posts travel further). So the click has to be earned by something the social copy deliberately does not resolve: a decision procedure, a test, a specific worked example, the tradeoff. Name that gap explicitly in the CTA ("the one question that tells you which you need" beats "full breakdown"). Never end on a bare "read more" or "link below".

**Social image: one card-grid infographic per article**

When the article contains a list of 4 to 8 parallel items (kinds, failure modes,
checks, layers), produce one card-grid image for the social posts with the
`blog-images` skill's template (`references/cardgrid.md`), portrait 1080×1350.
Inline diagrams stay as they are; the card version is for the feed, not the article.
If the article has no such list, say so and skip it rather than forcing one.

- **The title is a claim, not a label.** "Most AI guardrails can't authorize
  anything" stops the scroll; "8 kinds of AI guardrail" describes the picture. Put the
  descriptive version in the subtitle.
- **Hold something back for the click.** The image shows the *what* (the items and
  the verdict on each). The *how* (the worked example, the code, the decision
  procedure) stays in the article, and the post's CTA names that gap.
- **Every card's text comes from the article**, under the same no-invented-facts
  rule. Quote the article's own qualifiers rather than simplifying them away.
- **Say where it goes:** which post carries it (the LinkedIn launch, or one named X
  drip post), and write alt text for it: what the image says, for screen readers and
  for platforms that can't read text inside images.
- **Frequency:** at most about one card-grid post a week across the accounts, mixed
  with other formats (two-panel comparison, code before/after, flow diagram), so the
  format doesn't stop registering. A weekly review of results decides whether to use it more.
- Use the framed light layout and, where every card has a clear match, icons picked by
  the rules in `cardgrid.md` (approved map first, card -> icon -> reason shown to the author).
- List the image in `seo-and-publish.md` with its spec path, PNG path, title, target
  post and alt text.

**Community distribution**

Platform feeds won't send readers to an account with no audience yet; communities will, when the post is written for them. Produce one ready-to-paste entry per community below, and only where the post genuinely fits:

- **Reddit:** pick at most two subreddits whose audience matches the post's topic and `positioning.audienceSeniority` (for architecture and AI-systems posts, communities such as r/softwarearchitecture, r/ExperiencedDevs, r/LLMDevs, or r/ClaudeAI for Claude Code topics). For each: a plain, non-clickbait title, and a native text body of 150 to 300 words that delivers the core idea on its own, ending with the canonical link as "longer write-up, with the worked example: <url>". Add a line reminding the user to read that subreddit's self-promotion rules before posting; some ban links to your own blog outright, and a removed post costs more than a skipped one. Where the subreddit bans AI-written posts or requires disclosure (`blog-data/reddit-rules.md`), give the title, the core point and the supporting facts as notes for the user to write from, not a finished body.
- **Hacker News:** only if the post makes a substantive, non-obvious technical argument. Give the submission title (the plain descriptive title, no clickbait, no "I"), and say "skip" with a reason when it doesn't fit. One submission per post, never resubmitted.
- **Medium publication:** remind the user that distribution on Medium comes mostly from publications, not from an author profile with no followers. Suggest searching Medium for publications that ran similar topics in the last few months and submitting there. Do not name a specific publication as accepting submissions unless you've verified it.

Never invent community names, submission URLs or rules. If you are not sure a community exists or allows this kind of post, say so.

**Cross-post checklist**
- [ ] Canonical URL set on Dev.to
- [ ] Canonical URL set on Medium
- [ ] Medium story submitted to a publication (or a note on why not)
- [ ] CTA block added linking to newsletter
- [ ] Disclaimer footer present on every platform's copy of the article
- [ ] Content-limit flags cleared by the author
- [ ] X launch post published, link in the reply
- [ ] X drip posts scheduled (days 1 to 14)
- [ ] LinkedIn post published with the hero image attached
- [ ] Card-grid image attached to its target post, with alt text (or noted as skipped)
- [ ] LinkedIn follow-ups scheduled
- [ ] Reddit / Hacker News posts made where they fit, rules checked first
- [ ] Images re-uploaded on platforms that don't pull them from the canonical (Medium, Dev.to)

## Copyright/citation rule
If the research brief includes quotes or close paraphrases from sources, rewrite fully in original words for the draft, no lifted phrasing, even short. This applies doubly to any compressed, quotable summary line (especially a closing takeaway): these tend to converge on phrasing that's already common across whatever comparison genre the post is writing about. Before finalizing a line like that, search for the distinctive phrase; if it lands close to an existing source's actual wording, rewrite it further rather than assume independent convergence is safe to publish.
