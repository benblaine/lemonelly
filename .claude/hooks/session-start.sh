#!/bin/bash
# SessionStart hook — guards against building from a stale checkout.
#
# Why this exists: a session once started from a branch cut before the draft
# system landed on main, hand-rolled five draft pages on a retired design, and
# shipped them. This hook fetches origin/main, tells the session exactly how
# far behind its checkout is, and confirms the draft-system files are present.
# Its stdout is injected into the session's context.
set -uo pipefail

# Web sessions only — local checkouts manage their own git state.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0

if ! git fetch origin main --quiet 2>/dev/null; then
  echo "WARNING: could not fetch origin/main — network or remote issue. Before"
  echo "changing anything, verify this checkout is current (git fetch origin main)."
else
  behind=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo "?")
  if [ "$behind" != "0" ] && [ "$behind" != "?" ]; then
    echo "WARNING: this checkout is $behind commit(s) BEHIND origin/main."
    echo "Do not build on it as-is. Start from current main first:"
    echo "  git checkout -B <your-branch> origin/main"
    echo "(Keep any unmerged commits by rebasing them onto origin/main instead.)"
  fi
fi

# Sanity markers: if these are missing, the checkout predates the draft system.
missing=""
[ -f template/draft.template.html ] || missing="$missing template/draft.template.html"
[ -f .claude/skills/draft/SKILL.md ] || missing="$missing .claude/skills/draft/SKILL.md"
[ -f reference/DRAFTS.md ] || missing="$missing reference/DRAFTS.md"
if [ -n "$missing" ]; then
  echo "WARNING: draft-system files missing from this checkout:$missing"
  echo "This checkout predates the current draft system. Fetch origin/main and"
  echo "rebase before doing ANY draft work — never hand-roll a draft page."
fi

echo "Repo guide: CLAUDE.md. Client draft pages are built ONLY via the /draft"
echo "skill (.claude/skills/draft/SKILL.md) from template/draft.template.html."
exit 0
