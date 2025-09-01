#!/bin/bash

# Simplified release script for Datatalk (GitHub + Homebrew)
# Usage: ./release.sh
# Reads version from pyproject.toml and creates a release

set -e

# Function to get current version from pyproject.toml
get_current_version() {
    grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'
}

# Parse arguments
for arg in "$@"; do
    case $arg in
        --help|-h)
            echo "Usage: $0"
            echo ""
            echo "This script reads the version from pyproject.toml and creates a release."
            echo "Make sure to update the version in pyproject.toml before running this script."
            exit 0
            ;;
        *)
            echo "ERROR: Unknown argument: $arg"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Get version from pyproject.toml
VERSION=$(get_current_version)

if [ -z "$VERSION" ]; then
    echo "ERROR: Could not read version from pyproject.toml"
    exit 1
fi

echo "Using version from pyproject.toml: $VERSION"

TAG="v$VERSION"
FORMULA_FILE="homebrew/datatalk-cli.rb"

echo "Starting release process for version $VERSION"
echo ""

# Step 1: Create and push tag
echo "Step 1: Creating and pushing tag $TAG..."
git tag $TAG
git push origin main
git push origin $TAG

echo ""
echo "GitHub release completed!"
echo ""

# Step 2: Update Homebrew formula
echo "Step 2: Updating Homebrew formula..."

# Check if the formula file exists
if [ ! -f "$FORMULA_FILE" ]; then
    echo "ERROR: Formula file $FORMULA_FILE not found"
    exit 1
fi

# Download the release tarball and calculate SHA256
echo "Downloading release tarball to calculate SHA256..."
TARBALL_URL="https://github.com/vtsaplin/datatalk/archive/refs/tags/$TAG.tar.gz"
echo "URL: $TARBALL_URL"

# Wait a moment for GitHub to make the release available
echo "Waiting for GitHub release to become available..."
sleep 5

# Download and calculate SHA256
SHA256=$(curl -sL "$TARBALL_URL" | shasum -a 256 | cut -d' ' -f1)

if [ -z "$SHA256" ]; then
    echo "ERROR: Failed to download tarball or calculate SHA256"
    echo "Make sure the GitHub release $TAG exists"
    exit 1
fi

echo "Calculated SHA256: $SHA256"

# Create a backup of the formula
cp "$FORMULA_FILE" "$FORMULA_FILE.backup"
echo "Created backup: $FORMULA_FILE.backup"

# Update the formula with new version and SHA256
echo "Updating formula..."
sed -i '' "s|url \".*\"|url \"$TARBALL_URL\"|" "$FORMULA_FILE"
sed -i '' "s/sha256 \".*\"/sha256 \"$SHA256\"/" "$FORMULA_FILE"

echo "Formula updated successfully!"
echo ""

# Commit the formula update
echo "Committing Homebrew formula update..."
git add "$FORMULA_FILE"
git commit -m "Update Homebrew formula to $VERSION"
git push origin main

echo ""
echo "Release completed successfully!"
echo ""
echo "Summary:"
echo "- Version: $VERSION"
echo "- GitHub: Tag $TAG created and pushed"
echo "- Homebrew: Formula updated with new SHA256"
echo ""
echo "Next steps:"
echo "1. Go to GitHub and create a release from tag $TAG if needed"
echo "2. Test the Homebrew formula:"
echo "   brew install --build-from-source ./$FORMULA_FILE"
echo "3. Test the installation:"
echo "   datatalk-cli --help"
echo ""
echo "Package available at:"
echo "- GitHub: https://github.com/vtsaplin/datatalk/releases/tag/$TAG"
