#!/usr/bin/env bash
set -euo pipefail

REPO_URL=${1:-https://github.com/luci-digital/lucia_tooling_omzsh.git}
DEST_DIR=${2:-third_party/lucia_tooling_omzsh}

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [ -d "$DEST_DIR" ]; then
  echo "Target path '$DEST_DIR' already exists. Aborting."
  exit 0
fi

if ! command -v git >/dev/null 2>&1; then
  echo "git not found. Attempting to install..."
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update && sudo apt-get install -y git
  elif command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y git
  elif command -v pacman >/dev/null 2>&1; then
    sudo pacman -S --noconfirm git
  elif command -v yum >/dev/null 2>&1; then
    sudo yum install -y git
  else
    echo "No package manager detected. Please install git manually: https://git-scm.com/downloads" >&2
    exit 1
  fi
fi

# If this repo is a git working tree, add as submodule
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Adding as git submodule: $REPO_URL -> $DEST_DIR"
  git submodule add "$REPO_URL" "$DEST_DIR"
  git submodule update --init --recursive "$DEST_DIR"
else
  echo "Cloning repository into $DEST_DIR"
  git clone "$REPO_URL" "$DEST_DIR"
fi

echo "Clone complete: $DEST_DIR"
