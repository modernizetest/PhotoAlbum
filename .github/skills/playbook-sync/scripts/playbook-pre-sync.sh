#!/usr/bin/env bash
#
# playbook-pre-sync.sh — Prepare a remote repository for playbook sync.
#
# Clones (or updates) the target repo, sets up the branch, and outputs
# the playbook output path on the last line of stdout.
#
# Usage:  ./scripts/playbook-pre-sync.sh <github-repo-url>
# Output: The absolute path to the playbook/ directory (last line of stdout)
#
# Exit codes:
#   0 — success
#   1 — clone/pull failed
#   2 — authentication failed
#   3 — branch setup failed
#
# Requires: git, gh (GitHub CLI)

set -euo pipefail

REPO_URL="${1:?Usage: playbook-pre-sync.sh <github-repo-url>}"
BRANCH="modernize/playbook-sync"

# Ensure GITHUB_TOKEN is set for gh CLI (needed when running in agent terminals)
if [ -z "${GITHUB_TOKEN:-}" ] && command -v gh &>/dev/null; then
    GITHUB_TOKEN=$(gh auth token 2>/dev/null) && export GITHUB_TOKEN || true
fi

# --- Derive temp path ---
repo_name=$(echo "$REPO_URL" | sed -E 's|.*/([^/]+?)(.git)?/?$|\1|')
TEMP_DIR="${TMPDIR:-${TEMP:-/tmp}}"
REPO_DIR="$TEMP_DIR/modernize-playbook-sync/$repo_name"

# --- Clone or update ---
if [ -d "$REPO_DIR/.git" ]; then
    echo "Updating existing clone at $REPO_DIR..." >&2
    cd "$REPO_DIR"
    # Reset to default branch before pulling to avoid conflicts
    default_branch=$(git remote show origin 2>/dev/null | grep 'HEAD branch' | awk '{print $NF}')
    if [ -n "$default_branch" ]; then
        git checkout "$default_branch" 2>/dev/null || true
    fi
    git pull --ff-only 2>&1 >&2 || {
        echo "ERROR: Failed to update repository. Retrying with fresh clone..." >&2
        cd /
        rm -rf "$REPO_DIR"
    }
fi

if [ ! -d "$REPO_DIR/.git" ]; then
    echo "Cloning $REPO_URL to $REPO_DIR..." >&2
    mkdir -p "$(dirname "$REPO_DIR")"
    if ! gh repo clone "$REPO_URL" "$REPO_DIR" 2>&1 >&2; then
        echo "ERROR: Failed to clone repository. Verify the URL is correct and accessible: $REPO_URL" >&2
        exit 1
    fi
fi

cd "$REPO_DIR"

# --- Branch strategy ---
# Check for existing open PR for modernize/playbook-sync
existing_pr=$(gh pr list --repo "$REPO_URL" --head "$BRANCH" --state open --json url --limit 1 2>/dev/null || echo "[]")

if echo "$existing_pr" | grep -q '"url"'; then
    # Open PR exists — checkout existing branch and pull latest
    pr_url=$(echo "$existing_pr" | sed -n 's/.*"url"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
    echo "Found existing open PR: $pr_url" >&2
    echo "Checking out branch $BRANCH..." >&2

    git fetch origin "$BRANCH" 2>&1 >&2 || {
        echo "ERROR: Failed to fetch branch $BRANCH." >&2
        exit 3
    }
    git checkout "$BRANCH" 2>&1 >&2 || {
        echo "ERROR: Failed to checkout branch $BRANCH." >&2
        exit 3
    }
    git pull 2>&1 >&2 || true
    echo "Checked out existing branch $BRANCH" >&2
else
    # No open PR — create new branch from default branch
    echo "No existing open PR. Creating new branch $BRANCH..." >&2

    # Delete local branch if it exists (leftover from a previous merged PR)
    git branch -D "$BRANCH" 2>/dev/null || true
    # Delete remote tracking branch if it exists
    git push origin --delete "$BRANCH" 2>/dev/null || true

    if ! git checkout -b "$BRANCH" 2>&1 >&2; then
        echo "ERROR: Failed to create branch $BRANCH. Verify you have push access to this repository." >&2
        exit 3
    fi
    echo "Created branch $BRANCH" >&2
fi

# --- Ensure playbook directory exists ---
PLAYBOOK_DIR="$REPO_DIR/playbook"
mkdir -p "$PLAYBOOK_DIR"

# --- Output the playbook path (last line, read by SKILL.md) ---
echo "$PLAYBOOK_DIR"
