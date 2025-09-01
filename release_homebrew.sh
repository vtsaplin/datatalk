#!/bin/bash

# Homebrew release script for Datatalk
# Usage: ./release_homebrew.sh <version>
# Example: ./release_homebrew.sh 0.1.0
#
# This script updates the Homebrew formula with the new version and SHA256

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 0.1.0"
    echo ""
    echo "This script updates the Homebrew formula for the given version."
    echo "Make sure the GitHub release already exists before running this."
    exit 1
fi

VERSION=$1
TAG="v$VERSION"
FORMULA_FILE="homebrew/datatalk.rb"

echo "Updating Homebrew formula for version $VERSION"

# Check if the formula file exists
if [ ! -f "$FORMULA_FILE" ]; then
    echo "ERROR: Formula file $FORMULA_FILE not found"
    exit 1
fi

# Download the release tarball and calculate SHA256
echo "Downloading release tarball to calculate SHA256..."
TARBALL_URL="https://github.com/vtsaplin/datatalk/archive/refs/tags/$TAG.tar.gz"
echo "URL: $TARBALL_URL"

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
echo "Changes made to $FORMULA_FILE:"
echo "- Version: $VERSION"
echo "- URL: $TARBALL_URL"
echo "- SHA256: $SHA256"
echo ""

# Show the diff
echo "Diff from previous version:"
diff "$FORMULA_FILE.backup" "$FORMULA_FILE" || true
echo ""

echo "Next steps:"
echo "1. Test the formula locally:"
echo "   brew install --build-from-source ./$FORMULA_FILE"
echo "2. If testing succeeds, commit the changes:"
echo "   git add $FORMULA_FILE"
echo "   git commit -m \"Update Homebrew formula to $VERSION\""
echo "   git push origin main"
echo "3. If you have a homebrew tap, update it as well"

# Offer to test the formula
read -p "Would you like to test the formula now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Testing formula..."
    brew install --build-from-source "./$FORMULA_FILE"
    echo ""
    echo "Testing installation..."
    datatalk --help
    echo ""
    echo "Formula test completed successfully!"
else
    echo "Skipping formula test. Remember to test before committing!"
fi
