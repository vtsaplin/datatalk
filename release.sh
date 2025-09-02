#!/bin/bash
set -e

# Get version from pyproject.toml
VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
TAG="v$VERSION"

echo "📦 Releasing $VERSION"

# Tagging
if git rev-parse "$TAG" >/dev/null 2>&1; then
    echo "⚠️ Tag $TAG already exists, skipping"
else
    git tag "$TAG"
    git push origin main
    git push origin "$TAG"
    echo "✅ GitHub tag $TAG pushed"
fi

# Update README install instructions
sed -i '' "s|pip install git+https://github.com/vtsaplin/datatalk.git@v[0-9.]\+|pip install git+https://github.com/vtsaplin/datatalk.git@$TAG|" README.md
sed -i '' "s|uv pip install git+https://github.com/vtsaplin/datatalk.git@v[0-9.]\+|uv pip install git+https://github.com/vtsaplin/datatalk.git@$TAG|" README.md

git add README.md
git commit -m "Update README for $VERSION" || echo "ℹ️ README already up to date"
git push origin main

echo "🎉 Release $VERSION completed"
echo "Install with:"
echo "  pip install git+https://github.com/vtsaplin/datatalk.git@$TAG"
