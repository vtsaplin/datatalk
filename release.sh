#!/bin/bash
# Cross-platform release script for DataTalk CLI
# Works on macOS, Linux, Windows (Git Bash/WSL)
# Usage: ./release.sh

set -e

# --- Ensure we're on main branch ---
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "❌ Error: Must be on main branch to release"
    echo "   Current branch: $CURRENT_BRANCH"
    exit 1
fi

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

# --- Update README install instructions ---
# Use sed to replace the version tag in the git install URL
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS version (BSD sed)
    sed -i '' "s/git+https:\/\/github\.com\/vtsaplin\/datatalk\.git@v[0-9]*\.[0-9]*\.[0-9]*/git+https:\/\/github.com\/vtsaplin\/datatalk.git@$TAG/g" README.md
else
    # Linux version (GNU sed)
    sed -i "s/git+https:\/\/github\.com\/vtsaplin\/datatalk\.git@v[0-9]*\.[0-9]*\.[0-9]*/git+https:\/\/github.com\/vtsaplin\/datatalk.git@$TAG/g" README.md
fi

git add README.md
git commit -m "Update README for $VERSION" || echo "ℹ️ README already up to date"
git push origin main

# --- Done ---
echo ""
echo "🎉 Release $VERSION completed"
echo "Install with:"
echo "  pip install git+https://github.com/vtsaplin/datatalk.git@$TAG"
