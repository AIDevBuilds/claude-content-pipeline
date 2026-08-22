# Blog Workflow

## Setup
```bash
./setup.sh
```
Then fill in `config.json` (brand name, author, blog and Medium URLs, series,
diagram palette) and open Claude Code in this directory.

To use these outside this repo, copy `.claude/agents/topic-scout.md` and the
`.claude/skills/blog-writer/` and `.claude/skills/blog-images/` folders into
`~/.claude/`. Both read `config.json` from the repo root, so a copied skill needs
one nearby.

## The actual workflow, matching what you asked for

**1. Get a topic suggestion**
```
Use topic-scout to suggest my next blog post
```
→ Returns 2-3 candidates with reasoning. You pick one, reject all, or ask for a different angle.

**2. Research & validate**
```
Use topic-scout to research and validate: [chosen topic]
```
→ Returns `blog-data/research-brief.md` — sourced, validated, with a concrete example identified.

**3. Generate outline**
```
Using the blog-writer skill, turn this research brief into an outline
```
→ Returns `blog-data/outline.md`. Review it, request changes if needed.

**4. Generate detailed draft**
```
The outline looks good, write the full draft
```
→ Returns `blog-data/draft.md`, written in your voice, with `[NEEDS: ...]` markers anywhere it's missing something only you know. Any diagrams the blog-images skill generates along the way land in `blog-data/images/`.

**5. You edit the draft manually**
Fill in the `[NEEDS:]` markers, adjust anything that doesn't sound like you, add real specifics.

**6. Finalize**
```
This draft is final, give me the SEO and publish details
```
→ Returns `blog-data/seo-and-publish.md` with per-platform titles, descriptions, tags, and a cross-post checklist.

All of this workflow's output files live under `blog-data/` in the project root, keeping them out of the way of the agent/skill config in `.claude/`.

## Why it's split this way
- Research is noisy (search results, source-checking) — keeping it in an isolated subagent means your main conversation stays clean and you're not scrolling past 15 search queries to find your draft.
- Writing needs your accumulated context (past articles, ongoing edits, your voice) — that stays in the main conversation with the skill loaded, not delegated away.
