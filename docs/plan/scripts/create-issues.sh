#!/usr/bin/env bash
# Create one GitHub Issue per plan step, with labels, milestones and
# "blocked by" links between issues.
#
# Usage:  docs/plan/scripts/create-issues.sh OWNER/REPO [--dry-run]
#
# Needs the GitHub CLI (gh), logged in with write access to the repo's issues.
# Works with the bash that ships with macOS (3.2).
# Safe to re-run: labels are updated, and existing milestones and issues
# (matched by title) are reused instead of duplicated.
# The issue bodies link to the briefs on the default branch, assumed to be main.
set -euo pipefail

REPO="${1:-}"
MODE="${2:-}"
if [[ "$REPO" != */* || ( -n "$MODE" && "$MODE" != "--dry-run" ) ]]; then
  echo "Usage: $0 OWNER/REPO [--dry-run]" >&2
  exit 2
fi
DRY=false
if [[ "$MODE" == "--dry-run" ]]; then DRY=true; fi

STEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../steps" && pwd)"
BRIEF_URL="https://github.com/$REPO/blob/main/docs/plan/steps"

milestone_title() {
  case "$1" in
    M0) echo "M0 · Foundations" ;;
    M1) echo "M1 · Walking skeleton" ;;
    M2) echo "M2 · Intake and fast path" ;;
    M3) echo "M3 · Full path" ;;
    M4) echo "M4 · Publish by tier" ;;
    M5) echo "M5 · Day two and pilot" ;;
    *) echo "Unknown milestone: $1" >&2; return 1 ;;
  esac
}

# Print the command in dry-run mode, run it otherwise.
run() {
  if $DRY; then
    echo "[dry-run] $*"
  else
    "$@"
  fi
}

# Fields of a step brief. Line 1: "# NN · Title". Line 3: the metadata line.
step_meta()  { sed -n 3p "$1"; }
step_ms()    { step_meta "$1" | grep -oE 'Milestone:\*\* M[0-9]' | grep -oE 'M[0-9]$'; }
step_size()  { step_meta "$1" | grep -oE 'Size:\*\* [SML]' | grep -oE '[SML]$'; }
step_tag()   { step_meta "$1" | sed -E 's/.*\*\*Tag:\*\* (.*) · \*\*Size.*/\1/'; }
step_deps()  {  # hard blockers only, not "Needs later"
  step_meta "$1" | sed -E 's/.*\*\*Blocked by:\*\* //; s/ · \*\*Needs later.*//' | grep -oE '[0-9]{2}' || true
}

if ! command -v gh >/dev/null; then
  echo "The GitHub CLI (gh) is required: https://cli.github.com" >&2
  exit 1
fi
if ! $DRY; then gh auth status >/dev/null; fi

shopt -s nullglob
STEP_FILES=("$STEPS_DIR"/[0-9][0-9]-*.md)
if [[ ${#STEP_FILES[@]} -eq 0 ]]; then
  echo "No step briefs found in $STEPS_DIR" >&2
  exit 1
fi

echo "== Labels"
label() { run gh label create "$1" --repo "$REPO" --color "$2" --description "$3" --force; }
label plan-step       5319E7 "A step of docs/plan"
label ready-for-agent 0E8A16 "A code assistant can build this"
label ready-for-human D93F0B "A person must do this"
label needs-person    FBCA04 "A person applies, signs off or decides"
label needs-triage    EDEDED "Needs evaluating before work starts"
label needs-info      C2E0C6 "Waiting for more information"
label wontfix         FFFFFF "Will not be done"
label size:S          C5DEF5 "Small"
label size:M          90CAF9 "Medium"
label size:L          1E88E5 "Large: split into tickets first"

echo "== Milestones"
existing_ms=""
if ! $DRY; then
  existing_ms="$(gh api "repos/$REPO/milestones?state=all&per_page=100" --jq '.[].title')"
fi
for key in M0 M1 M2 M3 M4 M5; do
  title="$(milestone_title "$key")"
  if grep -qxF "$title" <<<"$existing_ms"; then
    echo "exists: $title"
  else
    run gh api "repos/$REPO/milestones" -f title="$title" --silent
  fi
done

echo "== Issues"
ISSUE=()  # index: step number, value: issue number
existing_issues=""
if ! $DRY; then
  existing_issues="$(gh issue list --repo "$REPO" --state all --limit 1000 \
    --json number,title --jq '.[] | "\(.number)\t\(.title)"')"
fi
for f in "${STEP_FILES[@]}"; do
  file="$(basename "$f")"
  step=$((10#${file:0:2}))
  title="$(head -n 1 "$f" | sed 's/^# //')"
  ms="$(milestone_title "$(step_ms "$f")")"
  tag="$(step_tag "$f")"
  labels="plan-step,size:$(step_size "$f")"
  case "$tag" in
    ready-for-human*) labels+=",ready-for-human" ;;
    *"·"*)            labels+=",ready-for-agent,needs-person" ;;
    *)                labels+=",ready-for-agent" ;;
  esac

  found="$(awk -F'\t' -v t="$title" '$2 == t { print $1; exit }' <<<"$existing_issues")"
  if [[ -n "$found" ]]; then
    ISSUE[step]="$found"
    echo "exists: #$found $title"
    continue
  fi
  if $DRY; then
    ISSUE[step]="$step"
    echo "[dry-run] create \"$title\" · milestone \"$ms\" · labels $labels"
    continue
  fi
  body="$(printf 'Brief: [docs/plan/steps/%s](%s/%s)\n\n%s\n' "$file" "$BRIEF_URL" "$file" "$(cat "$f")")"
  url="$(gh issue create --repo "$REPO" --title "$title" --body "$body" \
    --label "$labels" --milestone "$ms")"
  ISSUE[step]="${url##*/}"
  echo "created: #${ISSUE[$step]} $title"
  sleep 1  # stay clear of GitHub's secondary rate limits
done

echo "== Blocked-by links"
for f in "${STEP_FILES[@]}"; do
  file="$(basename "$f")"
  step=$((10#${file:0:2}))
  for dep in $(step_deps "$f"); do
    d=$((10#$dep))
    if [[ -z "${ISSUE[$d]:-}" ]]; then
      echo "warning: step $file is blocked by step $dep, which has no issue" >&2
      continue
    fi
    if $DRY; then
      echo "[dry-run] link: step ${file:0:2} blocked by step $dep"
      continue
    fi
    blocker_id="$(gh api "repos/$REPO/issues/${ISSUE[$d]}" --jq .id)"
    if gh api --method POST "repos/$REPO/issues/${ISSUE[$step]}/dependencies/blocked_by" \
        -F issue_id="$blocker_id" --silent 2>/dev/null; then
      echo "linked: #${ISSUE[$step]} blocked by #${ISSUE[$d]}"
    else
      echo "skipped: #${ISSUE[$step]} blocked by #${ISSUE[$d]} (already linked, or not available)"
    fi
  done
done

echo "Done."
