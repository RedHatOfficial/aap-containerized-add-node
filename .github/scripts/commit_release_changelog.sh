#!/usr/bin/env bash
# Generate antsibull changelog, commit, and push release/<version>.
# Usage: bash .github/scripts/commit_release_changelog.sh 1.2.3
set -euo pipefail

VERSION="${1:?Usage: commit_release_changelog.sh MAJOR.MINOR.PATCH}"
BRANCH="release/${VERSION}"

git checkout -B "${BRANCH}"
python3 .github/scripts/calculate_release_version.py --set-galaxy "${VERSION}"
antsibull-changelog lint
antsibull-changelog release --verbose --version "${VERSION}"

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add CHANGELOG.rst changelogs/changelog.yaml changelogs/fragments galaxy.yml

if git diff --cached --quiet; then
  echo "::error::No changelog changes to commit for ${VERSION}."
  exit 1
fi

git commit -m "$(cat <<EOF
docs(changelog): release ${VERSION}

Signed-off-by: github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>
EOF
)"

git push --force-with-lease origin "${BRANCH}"
echo "Pushed ${BRANCH}"
