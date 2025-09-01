#!/bin/bash

# Release script for Datatalk (GitHub only)
# Usage: ./release_github.sh <version>
# Example: ./release_github.sh 0.1.0
# 
# For PyPI releases, use: ./release_pypi.sh <version>

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 0.1.0"
    echo ""
    echo "This script creates GitHub releases only."
    echo "For PyPI releases, use: ./release_pypi.sh <version>"
    exit 1
fi

VERSION=$1
TAG="v$VERSION"

echo "Preparing release $TAG"

# Update version in pyproject.toml
echo "Updating version in pyproject.toml..."
sed -i '' "s/version = \".*\"/version = \"$VERSION\"/" pyproject.toml

# Commit version change
echo "Committing version change..."
git add pyproject.toml
git commit -m "Bump version to $VERSION"

# Create and push tag
echo "Creating and pushing tag $TAG..."
git tag $TAG
git push origin main
git push origin $TAG

echo "Release $TAG created successfully!"
echo ""
echo "Next steps:"
echo "1. Go to GitHub and create a release from tag $TAG"
echo "2. For Homebrew: Run ./release_homebrew.sh $VERSION"
echo "   (or manually update homebrew/datatalk.rb with new version and SHA256)"
echo "3. For PyPI: Run ./release_pypi.sh $VERSION"
echo ""
echo "Or use the unified script: ./release_all.sh $VERSION"
