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

echo "📦 Preparing release $VERSION"

# --- Check if tag already exists ---
if git rev-parse "$TAG" >/dev/null 2>&1; then
    echo "❌ Error: Tag $TAG already exists"
    echo "   To create a new release, update the version in pyproject.toml first"
    exit 1
fi

# --- Check for uncommitted changes ---
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  Warning: You have uncommitted changes"
    echo ""
    git status --short
    echo ""
    read -p "Commit these changes before releasing? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add -A
        git commit -m "chore: bump version to $VERSION"
    else
        echo "❌ Release cancelled. Please commit or stash your changes."
        exit 1
    fi
fi

# --- Update README install instructions (optional) ---
# Use sed to replace the version tag in the git install URL
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS version (BSD sed)
    sed -i '' "s/git+https:\/\/github\.com\/vtsaplin\/datatalk\.git@v[0-9]*\.[0-9]*\.[0-9]*/git+https:\/\/github.com\/vtsaplin\/datatalk.git@$TAG/g" README.md
else
    # Linux version (GNU sed)
    sed -i "s/git+https:\/\/github\.com\/vtsaplin\/datatalk\.git@v[0-9]*\.[0-9]*\.[0-9]*/git+https:\/\/github.com\/vtsaplin\/datatalk.git@$TAG/g" README.md
fi

# Check if README was actually changed
if ! git diff-index --quiet HEAD -- README.md 2>/dev/null; then
    git add README.md
    git commit -m "docs: update install instructions for $VERSION"
    echo "✅ README updated"
fi

# --- Push changes to main ---
git push origin main
echo "✅ Changes pushed to main"

# --- Create and push tag ---
git tag "$TAG"
git push origin "$TAG"
echo "✅ Tag $TAG pushed"

# --- Done ---
echo ""
echo "🎉 Release $VERSION completed!"
echo ""
echo "Next steps:"
echo "  1. GitHub Actions will automatically:"
echo "     - Create a GitHub Release with notes"
echo "     - Build and publish to PyPI"
echo "  2. Check progress at: https://github.com/vtsaplin/datatalk/actions"
echo ""
echo "Install with:"
echo "  pip install datatalk-cli==$VERSION"
