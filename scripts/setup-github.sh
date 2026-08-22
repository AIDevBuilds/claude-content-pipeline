#!/usr/bin/env bash
# One-time: publish this repo to GitHub and apply branch protection.
#
# Run once, from the repo root:  ./scripts/setup-github.sh
#
# Safe to re-run: each step checks whether it has already been done.
set -euo pipefail

REPO_NAME="claude-content-pipeline"
DESCRIPTION="Claude Code agents and skills that take a technical blog post or YouTube video from topic research to draft, diagrams, SEO and thumbnail. Configuration-driven."

step() { printf '\n\033[1m▸ %s\033[0m\n' "$1"; }
ok()   { printf '\033[32m  ✓ %s\033[0m\n' "$1"; }
warn() { printf '\033[33m  ! %s\033[0m\n' "$1"; }

cd "$(dirname "${BASH_SOURCE[0]}")/.."

# ── 0. Preflight ──────────────────────────────────────────────────────────────
step "Preflight"
command -v gh >/dev/null || { echo "gh CLI not installed"; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "gh not authenticated. Run: gh auth login"; exit 1; }
OWNER="$(gh api user --jq .login)"
ok "authenticated as $OWNER"

python3 scripts/validate.py >/dev/null || { echo "validate.py failed, fix before publishing"; exit 1; }
python3 .claude/hooks/test_guard_secrets.py >/dev/null || { echo "guard tests failed"; exit 1; }
ok "local checks pass"

# Refuse to publish if anything secret would be committed.
if git status --porcelain --untracked-files=all | grep -qE '(^|/)\.env$|credentials\.json|\.pem$|id_rsa'; then
  echo "ERROR: a credential file is not being ignored. Fix .gitignore before publishing."
  exit 1
fi
ok "no credential files would be committed"

# ── 1. Commit ─────────────────────────────────────────────────────────────────
step "Committing"
git init -q 2>/dev/null || true
git add -A
if git diff --cached --quiet 2>/dev/null && git rev-parse HEAD >/dev/null 2>&1; then
  ok "nothing new to commit"
else
  git commit -q -m "Content pipeline: Claude Code agents and skills for blog and video

Agents (topic-scout, video-scout) handle research in isolated context.
Skills (blog-writer, blog-images, video-scriptwriter, video-thumbnail)
handle writing and rendering in the main conversation.

All identity and brand values live in config.json so the pipeline can be
forked and repointed. Both image generators are deterministic template
renderers rather than image models, so output stays visually consistent.

Credentials are protected by permission deny rules plus a PreToolUse hook
that blocks shell access to secret paths."
  ok "committed"
fi

git branch -M main

# ── 2. Create the remote ──────────────────────────────────────────────────────
step "Creating GitHub repository"
if gh repo view "$OWNER/$REPO_NAME" >/dev/null 2>&1; then
  ok "$OWNER/$REPO_NAME already exists"
  git remote get-url origin >/dev/null 2>&1 || \
    git remote add origin "git@github.com:$OWNER/$REPO_NAME.git"
else
  gh repo create "$REPO_NAME" --public --source=. --remote=origin --description "$DESCRIPTION"
  ok "created $OWNER/$REPO_NAME"
fi

step "Pushing main"
git push -u origin main
ok "pushed"

# ── 3. Wait for CI, so required checks exist before we require them ───────────
# Requiring a status check that has never reported will block every merge.
step "Waiting for the first CI run"
sleep 10
if gh run list --limit 1 --json databaseId --jq '.[0].databaseId' >/dev/null 2>&1; then
  gh run watch "$(gh run list --limit 1 --json databaseId --jq '.[0].databaseId')" --exit-status \
    && ok "CI green" || warn "CI did not pass; protection still applies, fix the run before merging PRs"
else
  warn "no CI run detected yet; check the Actions tab"
fi

# ── 4. Branch protection ──────────────────────────────────────────────────────
# Deliberately: required_approving_review_count is 0.
#
# Outside contributors already cannot merge, they have no write access, so their
# PRs need you to merge them regardless. Requiring an approval would only affect
# YOU, and GitHub does not let a PR author approve their own PR, so on a solo
# repo it means nothing can ever merge. Raise this to 1 the day you add a
# collaborator, not before.
#
# enforce_admins is false so a bad rule cannot lock you out of your own repo.
step "Applying branch protection to main"
gh api -X PUT "repos/$OWNER/$REPO_NAME/branches/main/protection" \
  -H "Accept: application/vnd.github+json" --input - >/dev/null <<'JSON'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["Validate repository", "Scan for committed secrets"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 0,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_linear_history": true,
  "required_conversation_resolution": true
}
JSON
ok "main now requires a pull request and passing CI"

# ── 5. Repo hygiene ───────────────────────────────────────────────────────────
step "Repository settings"
gh api -X PATCH "repos/$OWNER/$REPO_NAME" \
  -f delete_branch_on_merge=true \
  -F has_wiki=false \
  -F has_projects=false >/dev/null
ok "squash-friendly defaults set"

gh api -X PUT "repos/$OWNER/$REPO_NAME/topics" \
  -H "Accept: application/vnd.github+json" \
  -f 'names[]=claude-code' -f 'names[]=claude' -f 'names[]=ai-agents' \
  -f 'names[]=content-creation' -f 'names[]=technical-writing' >/dev/null
ok "topics added for discoverability"

printf '\n\033[32m\033[1mDone.\033[0m  https://github.com/%s/%s\n\n' "$OWNER" "$REPO_NAME"
echo "From now on, main is protected. To make a change:"
echo "  git checkout -b my-change"
echo "  # edit, then:"
echo "  git commit -am 'what changed' && git push -u origin my-change"
echo "  gh pr create --fill && gh pr merge --squash --auto"
echo
