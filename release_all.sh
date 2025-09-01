#!/bin/bash

# Unified release script for Datatalk
# Usage: ./release_all.sh [version] [--test-pypi] [--skip-homebrew]
# Example: ./release_all.sh                    # Auto-increment patch version
# Example: ./release_all.sh 0.2.0             # Use specific version
# Example: ./release_all.sh --test-pypi        # Auto-increment + test on TestPyPI
# Example: ./release_all.sh 0.1.5 --skip-homebrew

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

# Parse arguments to determine version
VERSION=""
TEST_MODE=""
SKIP_HOMEBREW=""

for arg in "$@"; do
    case $arg in
        --test-pypi)
            TEST_MODE="--test-pypi"
            ;;
        --skip-homebrew)
            SKIP_HOMEBREW="true"
            ;;
        --help|-h)
            echo "Usage: $0 [version] [--test-pypi] [--skip-homebrew]"
            echo ""
            echo "Arguments:"
            echo "  version         Specific version to release (optional - will auto-increment if not provided)"
            echo "  --test-pypi     Test on TestPyPI first"
            echo "  --skip-homebrew Skip Homebrew update"
            echo ""
            echo "Examples:"
            echo "  $0                    # Auto-increment patch version"
            echo "  $0 0.2.0             # Use specific version"
            echo "  $0 --test-pypi       # Auto-increment + test mode"
            echo "  $0 0.1.5 --skip-homebrew"
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
