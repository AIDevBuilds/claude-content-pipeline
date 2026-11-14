# Evals for copy-reviewer

`copy-reviewer` is an LLM judge: every draft, script and piece of launch copy passes
through it before you see it. A judge that is never measured is a guess, so this
folder measures it. It answers four questions you should ask of any LLM judge:

| Question | Answer in this repo |
|---|---|
| Who defines "good"? | The checks written in `.claude/agents/copy-reviewer.md`. |
| Who labels the validation set? | You. Each case carries the verdict *you* would give. |
| Who pays for the correction sample? | You, monthly: compare 5 recent verdicts with your own judgement; every disagreement becomes a new case. |
| What triggers a re-check? | Any change to the reviewer's prompt, its model, or the review loops that call it. |

The four cases in `cases/` are generic examples that show the format. Replace and
extend them with cases from your own drafts: text you rejected, text you published,
and anything the reviewer got wrong. Keep cases that quote real people or replies in
a gitignored folder (for example `private/evals/`), not here.

## Case format

One markdown file per case: expected verdict (`PASS` or `REVISE`), expected
category (`accuracy`, `framing`, `limits`, `generated`, `quality`, `platform`), why,
platform, any context the reviewer needs, and the text in a code block.

## Running it

In Claude Code, say: **"run the copy-reviewer evals in evals/copy-reviewer"**. For each
case, Claude spawns a fresh `copy-reviewer` agent with the text, platform and context
(never the expected verdict), records the verdict and finding categories, and writes
`results/<date>.md`.

## Reading the result

| Number | Meaning | Bar |
|---|---|---|
| False PASS | a case that should fail passed: bad copy would be published | 0 |
| False REVISE | a case that should pass was flagged: noise that costs review rounds | low |
| Category match | a REVISE case was flagged for the expected reason | most cases |

A false PASS blocks the change that caused it. When the reviewer disagrees with a
label, look at the case: if the reviewer is right, fix the label; never fix a label
just to make a run pass.
