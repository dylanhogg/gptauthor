#!/usr/bin/env bash

set -euo pipefail

MAIN_BRANCH="${1:-main}"

echo "Before removals:"
git worktree list

git worktree list --porcelain |
awk -v main_branch="$MAIN_BRANCH" '
  /^worktree / {
    worktree_path = substr($0, length("worktree ") + 1)
    keep = 0
  }

  $0 == "branch refs/heads/" main_branch {
    keep = 1
  }

  /^$/ {
    if (!keep && worktree_path != "") {
      print worktree_path
    }

    worktree_path = ""
    keep = 0
  }

  END {
    if (!keep && worktree_path != "") {
      print worktree_path
    }
  }
' |
while IFS= read -r worktree_path; do
  echo "Removing worktree: $worktree_path"
  git worktree remove "$worktree_path"
done

git worktree prune

echo "After removals:"
git worktree list
