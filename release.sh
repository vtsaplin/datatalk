#!/bin/bash
# Cross-platform release script for Datatalk
# Works on macOS, Linux, Windows (Git Bash/WSL)
# Usage: ./release.sh

set -e

# --- Get version from pyproject.toml ---
VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
TAG="v$VERSION"

echo "📦 Releasing $VERSION"

# --- Git tag ---
if git rev-parse "$TAG" >/dev/null 2>&1; then
    echo "⚠️ Tag $TAG already exists, skipping"
else
    git tag "$TAG"
    git push origin main
    git push origin "$TAG"
    echo "✅ GitHub tag $TAG pushed"
fi

# --- Detect sed flavour (GNU vs BSD) ---
if sed --version >/dev/null 2>&1; then
    # GNU sed (Linux, WSL, Git Bash)
    SED_CMD="sed -i"
else
    # BSD sed (macOS)
    SED_CMD="sed -i '' -E"
fi

# --- Update README install instructions ---
$SED_CMD "s|git\+https://github.com/vtsaplin/datatalk.git@v[0-9]+\.[0-9]+\.[0-9]+|git+https://github.com/vtsaplin/datatalk.git@$TAG|g" README.md

git add README.md
git commit -m "Update README for $VERSION" || echo "ℹ️ README already up to date"
git push origin main

# --- Done ---
echo ""
echo "🎉 Release $VERSION completed"
echo "Install with:"
echo "  pip install git+https://github.com/vtsaplin/datatalk.git@$TAG"
