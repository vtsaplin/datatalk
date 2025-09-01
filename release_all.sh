#!/bin/bash

# Unified release script for Datatalk
# Usage: ./release_all.sh <version> [--test-pypi] [--skip-homebrew]
# Example: ./release_all.sh 0.1.0
# Example: ./release_all.sh 0.1.0 --test-pypi
# Example: ./release_all.sh 0.1.0 --skip-homebrew

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <version> [--test-pypi] [--skip-homebrew]"
    echo "Example: $0 0.1.0"
    echo "Example: $0 0.1.0 --test-pypi  # Test on TestPyPI first"
    echo "Example: $0 0.1.0 --skip-homebrew  # Skip Homebrew update"
    echo ""
    echo "This script handles GitHub, PyPI, and Homebrew releases in the correct order."
    exit 1
fi

VERSION=$1
TEST_MODE=""
SKIP_HOMEBREW=""

# Parse arguments
for arg in "$@"; do
    case $arg in
        --test-pypi)
            TEST_MODE="--test-pypi"
            ;;
        --skip-homebrew)
            SKIP_HOMEBREW="true"
            ;;
    esac
done

TAG="v$VERSION"

echo "Starting unified release process for version $VERSION"
echo ""

# Step 1: GitHub Release
echo "Step 1: Creating GitHub release..."
./release_github.sh $VERSION

echo ""
echo "GitHub release completed!"
echo ""

# Step 2: PyPI Release
if [ "$TEST_MODE" = "--test-pypi" ]; then
    echo "Step 2: Creating TestPyPI release..."
    ./release_pypi.sh $VERSION --test
else
    echo "Step 2: Creating PyPI release..."
    echo "WARNING: This will publish to production PyPI!"
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ./release_pypi.sh $VERSION
    else
        echo "ERROR: PyPI release cancelled"
        echo "You can run it manually later with: ./release_pypi.sh $VERSION"
        exit 0
    fi
fi

echo ""
echo "PyPI release completed!"
echo ""

# Step 3: Homebrew Release
if [ "$SKIP_HOMEBREW" != "true" ] && [ "$TEST_MODE" != "--test-pypi" ]; then
    echo "Step 3: Updating Homebrew formula..."
    read -p "Update Homebrew formula? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        echo "Skipping Homebrew update"
    else
        ./release_homebrew.sh $VERSION
        echo ""
        echo "Homebrew formula updated!"
    fi
elif [ "$TEST_MODE" = "--test-pypi" ]; then
    echo "Step 3: Skipping Homebrew (TestPyPI mode)"
else
    echo "Step 3: Skipping Homebrew (--skip-homebrew flag)"
fi

echo ""
echo "All releases completed successfully!"
echo ""
echo "Summary:"
echo "- GitHub: Tag $TAG created and pushed"
if [ "$TEST_MODE" = "--test-pypi" ]; then
    echo "- TestPyPI: Package uploaded for testing"
    echo "- Homebrew: Skipped (TestPyPI mode)"
    echo ""
    echo "Next steps:"
    echo "1. Test TestPyPI installation:"
    echo "   pip install --index-url https://test.pypi.org/simple/ datatalk==$VERSION"
    echo "2. If all good, run production release:"
    echo "   ./release_pypi.sh $VERSION"
    echo "3. Then update Homebrew:"
    echo "   ./release_homebrew.sh $VERSION"
else
    echo "- PyPI: Package published to production"
    if [ "$SKIP_HOMEBREW" != "true" ]; then
        echo "- Homebrew: Formula updated"
    else
        echo "- Homebrew: Skipped"
    fi
    echo ""
    echo "Next steps:"
    echo "1. Test all installation methods"
    echo "2. Announce the release!"
fi

echo ""
echo "Package available at:"
echo "- GitHub: https://github.com/vtsaplin/datatalk/releases/tag/$TAG"
if [ "$TEST_MODE" != "--test-pypi" ]; then
    echo "- PyPI: https://pypi.org/project/datatalk/"
fi
