#!/bin/bash

# Simplified release script for Datatalk (GitHub + Homebrew)
# Usage: ./release.sh [version]
# Example: ./release.sh        # Auto-increment patch version
# Example: ./release.sh 0.2.0  # Use specific version

set -e

# Function to get current version from pyproject.toml
get_current_version() {
    grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'
}

# Function to increment patch version
increment_patch_version() {
    local version=$1
    local major=$(echo $version | cut -d. -f1)
    local minor=$(echo $version | cut -d. -f2)
    local patch=$(echo $version | cut -d. -f3)
    echo "$major.$minor.$((patch + 1))"
}

# Parse arguments
VERSION=""

for arg in "$@"; do
    case $arg in
        --help|-h)
            echo "Usage: $0 [version]"
            echo ""
            echo "Arguments:"
            echo "  version    Specific version to release (optional - will auto-increment if not provided)"
            echo ""
            echo "Examples:"
            echo "  $0          # Auto-increment patch version"
            echo "  $0 0.2.0    # Use specific version"
            exit 0
            ;;
        *)
            # If it's not a flag and VERSION is empty, assume it's a version number
            if [[ ! $arg =~ ^-- ]] && [ -z "$VERSION" ]; then
                VERSION=$arg
            fi
            ;;
    esac
done

# Auto-detect version if not provided
if [ -z "$VERSION" ]; then
    CURRENT_VERSION=$(get_current_version)
    VERSION=$(increment_patch_version $CURRENT_VERSION)
    echo "Auto-incrementing version: $CURRENT_VERSION → $VERSION"
else
    echo "Using specified version: $VERSION"
fi

TAG="v$VERSION"
FORMULA_FILE="homebrew/datatalk-cli.rb"

echo "Starting release process for version $VERSION"
echo ""

# Step 1: Update version in pyproject.toml
echo "Step 1: Updating version in pyproject.toml..."
sed -i '' "s/version = \".*\"/version = \"$VERSION\"/" pyproject.toml

# Step 2: Commit version change
echo "Step 2: Committing version change..."
git add pyproject.toml
git commit -m "Bump version to $VERSION"

# Step 3: Create and push tag
echo "Step 3: Creating and pushing tag $TAG..."
git tag $TAG
git push origin main
git push origin $TAG

echo ""
echo "GitHub release completed!"
echo ""

# Step 4: Update Homebrew formula
echo "Step 4: Updating Homebrew formula..."

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
