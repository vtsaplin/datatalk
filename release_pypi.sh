#!/bin/bash

# PyPI release script for Datatalk
# Usage: ./release_pypi.sh <version> [--test]
# Example: ./release_pypi.sh 0.1.0
# Example: ./release_pypi.sh 0.1.0 --test  # Upload to TestPyPI first

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <version> [--test]"
    echo "Example: $0 0.1.0"
    echo "Example: $0 0.1.0 --test  # Upload to TestPyPI first"
    exit 1
fi

VERSION=$1
TEST_MODE=$2
TAG="v$VERSION"

echo "Preparing PyPI release $VERSION"

# Check if we have the necessary tools
if ! command -v uv &> /dev/null; then
    echo "ERROR: uv is required but not installed"
    exit 1
fi

# Update version in pyproject.toml
echo "Updating version in pyproject.toml..."
sed -i '' "s/version = \".*\"/version = \"$VERSION\"/" pyproject.toml

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

# Build the package
echo "Building package..."
uv build

# Check the built package
echo "Checking package..."
uv run twine check dist/*

if [ "$TEST_MODE" = "--test" ]; then
    echo "Uploading to TestPyPI..."
    echo "Make sure you have configured TestPyPI credentials:"
    echo "  uv run twine configure testpypi"
    echo ""
    read -p "Press Enter to continue or Ctrl+C to abort..."
    uv run twine upload --repository testpypi dist/*
    
    echo "Uploaded to TestPyPI successfully!"
    echo ""
    echo "Test the installation with:"
    echo "  pip install --index-url https://test.pypi.org/simple/ datatalk==$VERSION"
    echo ""
    echo "If everything works, run without --test flag to upload to PyPI:"
    echo "  ./release_pypi.sh $VERSION"
else
    echo "Uploading to PyPI..."
    echo "Make sure you have configured PyPI credentials:"
    echo "  uv run twine configure pypi"
    echo ""
    read -p "Press Enter to continue or Ctrl+C to abort..."
    uv run twine upload dist/*
    
    # Commit version change and create tag
    echo "Committing version change..."
    git add pyproject.toml
    git commit -m "Bump version to $VERSION for PyPI release"
    
    # Create and push tag
    echo "Creating and pushing tag $TAG..."
    git tag $TAG
    git push origin main
    git push origin $TAG
    
    echo "Released to PyPI successfully!"
    echo ""
    echo "Package is now available at: https://pypi.org/project/datatalk/"
    echo "Users can install with: pip install datatalk"
fi

echo ""
echo "Next steps:"
if [ "$TEST_MODE" = "--test" ]; then
    echo "1. Test the TestPyPI installation"
    echo "2. If all good, run: ./release_pypi.sh $VERSION"
else
    echo "1. Update Homebrew formula with new version and SHA256"
    echo "2. Test Homebrew installation"
    echo "3. Announce the release!"
fi
