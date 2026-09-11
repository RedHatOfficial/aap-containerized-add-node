#!/usr/bin/env bash
# Open (or reuse) a changelog PR into devel. Auto-merge when branch protection allows.
# Usage: bash .github/scripts/open_release_pr.sh 1.2.3
set -euo pipefail

VERSION="${1:?Usage: open_release_pr.sh MAJOR.MINOR.PATCH}"
BRANCH="release/${VERSION}"
TITLE="[RELEASE] Update changelog ${VERSION}"
BODY="Automated changelog, fragment consumption, and galaxy.yml bump for ${VERSION}."

if gh pr view "${BRANCH}" --json number --jq .number >/dev/null 2>&1; then
  echo "PR for ${BRANCH} already exists."
else
  gh pr create --base devel --head "${BRANCH}" --title "${TITLE}" --body "${BODY}"
fi

if gh pr merge "${BRANCH}" --squash --auto; then
  echo "Enabled auto-merge (squash) for ${BRANCH}."
else
  echo "::notice::Could not enable auto-merge. Leave the PR open for review (devel is protected)."
fi
