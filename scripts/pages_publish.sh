#!/usr/bin/env bash
# Publish the built single-file site to the gh-pages branch using plain git (no third-party actions).
#
#   pages_publish.sh main            put the site at the root, keeping any pr-preview/ folders
#   pages_publish.sh preview <PR>    put the site at pr-preview/pr-<PR>/
#   pages_publish.sh remove <PR>     delete pr-preview/pr-<PR>/
#
# Environment:
#   SITE_DIR   folder containing index.html (default: site)
#   REPO_URL   remote to publish to (default: this repository, authenticated with GITHUB_TOKEN)
set -euo pipefail

mode=${1:?usage: pages_publish.sh main|preview|remove [PR_NUMBER]}
pr=${2:-}
if [[ $mode != main && ! $pr =~ ^[0-9]+$ ]]; then
  echo "a numeric PR number is required for '$mode'" >&2
  exit 2
fi

site=$(cd "${SITE_DIR:-site}" 2>/dev/null && pwd || true)
if [[ $mode != remove && ! -f $site/index.html ]]; then
  echo "no index.html in ${SITE_DIR:-site}" >&2
  exit 2
fi
repo_url=${REPO_URL:-"https://x-access-token:${GITHUB_TOKEN:?GITHUB_TOKEN is required}@github.com/${GITHUB_REPOSITORY:?}.git"}

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
if git ls-remote --exit-code --heads "$repo_url" gh-pages >/dev/null 2>&1; then
  git clone --quiet --branch gh-pages --depth 1 "$repo_url" "$work"
elif [[ $mode == remove ]]; then
  echo "no gh-pages branch yet, nothing to remove"
  exit 0
else
  git init --quiet "$work"
  git -C "$work" checkout --quiet --orphan gh-pages
  git -C "$work" remote add origin "$repo_url"
fi

cd "$work"
git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

case $mode in
  main)
    find . -mindepth 1 -maxdepth 1 ! -name .git ! -name pr-preview -exec rm -rf {} +
    cp "$site/index.html" index.html
    touch .nojekyll
    message="Deploy main"
    ;;
  preview)
    rm -rf "pr-preview/pr-$pr"
    mkdir -p "pr-preview/pr-$pr"
    cp "$site/index.html" "pr-preview/pr-$pr/index.html"
    touch .nojekyll
    message="Deploy preview for PR #$pr"
    ;;
  remove)
    rm -rf "pr-preview/pr-$pr"
    message="Remove preview for PR #$pr"
    ;;
  *)
    echo "unknown mode '$mode'" >&2
    exit 2
    ;;
esac

git add -A
if git diff --cached --quiet; then
  echo "nothing to publish"
  exit 0
fi
git commit --quiet -m "$message"

# The workflows serialize publishes, but retry once or twice if another push slipped in.
for attempt in 1 2 3; do
  if git push --quiet origin HEAD:gh-pages; then
    echo "$message: published"
    exit 0
  fi
  git pull --quiet --rebase origin gh-pages || true
done
echo "could not push to gh-pages" >&2
exit 1
