#!/bin/bash
# verify.sh — machine-enforce the invariants CLAUDE.md and the /draft skill care
# about most. Mirrors the SKILL.md §6 QA checklist so CI and the documented
# workflow stay in lockstep. Runnable locally before pushing:  bash scripts/verify.sh
#
# Hard failures (exit 1): checks 1–5. Check 6 is advisory (warning only).
set -uo pipefail

cd "$(dirname "$0")/.." || exit 1
fail=0

echo "== 1. Generated files are in sync with the template =="
python3 scripts/build.py >/dev/null || { echo "  FAIL: scripts/build.py errored"; exit 1; }
generated="index.html za/index.html us/index.html uk/index.html eu/index.html sitemap.xml"
if ! git diff --quiet -- $generated; then
  echo "  FAIL: generated files differ from a fresh build. Did you hand-edit a"
  echo "        generated page, or forget to run scripts/build.py and commit it?"
  git diff --stat -- $generated | sed 's/^/        /'
  fail=1
else
  echo "  ok"
fi

echo "== 2. Every draft carries noindex, nofollow =="
missing_noindex=""
for f in draft/*/index.html; do
  [ -e "$f" ] || continue
  grep -q 'noindex, nofollow' "$f" || missing_noindex="$missing_noindex $f"
done
if [ -n "$missing_noindex" ]; then
  echo "  FAIL: missing noindex meta:$missing_noindex"
  fail=1
else
  echo "  ok"
fi

echo "== 3. Drafts make zero external requests (lemonelly.com only) =="
# Any absolute http(s) or protocol-relative URL whose host is not lemonelly.com.
# Matches src=/href=/content= attributes; lemonelly.com og:image/canonical are allowed.
external=$(grep -rhoiE '(src|href|content)="(https?:)?//[^"]*"' draft/ 2>/dev/null \
  | sed -E 's#.*"(https?:)?//([^/"]+).*#\2#' \
  | grep -viE '^(www\.)?lemonelly\.com$' | sort -u)
if [ -n "$external" ]; then
  echo "  FAIL: draft pages reference external hosts:"
  echo "$external" | sed 's/^/        /'
  fail=1
else
  echo "  ok"
fi

echo "== 4. No draft leaks into sitemap.xml =="
if grep -qi draft sitemap.xml; then
  echo "  FAIL: sitemap.xml references a draft path — drafts must never be indexed."
  fail=1
else
  echo "  ok"
fi

echo "== 5. robots.txt keeps Disallow: /draft/ =="
if grep -qE '^\s*Disallow:\s*/draft/\s*$' robots.txt; then
  echo "  ok"
else
  echo "  FAIL: robots.txt is missing 'Disallow: /draft/'."
  fail=1
fi

echo "== 6. (advisory) fabricated-proof heuristic =="
suspects=$(grep -riE 'starting at|4\.9|5-star|[0-9],[0-9]{3}\+|BBB|GAF' draft/ 2>/dev/null)
if [ -n "$suspects" ]; then
  echo "  WARNING: possible fabricated proof — verify each is a real, sourced"
  echo "  figure from the fact sheet (SKILL.md §5 HARD RULE). Not failing CI:"
  echo "$suspects" | sed 's/^/        /'
else
  echo "  ok"
fi

echo
if [ "$fail" -ne 0 ]; then
  echo "verify.sh: FAILED — fix the hard failures above before pushing."
  exit 1
fi
echo "verify.sh: all invariant checks passed."
