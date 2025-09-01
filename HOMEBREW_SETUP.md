# Homebrew Installation Guide for Datatalk

This guide explains how to make Datatalk installable via Homebrew.

## Prerequisites

1. **GitHub Repository**: Your project needs to be hosted on GitHub
2. **Releases**: You need to create GitHub releases with version tags
3. **Homebrew Tap**: You can either submit to the main Homebrew repository or create your own tap

## Steps to Make Datatalk Installable via Homebrew

### 1. Set up GitHub Repository

First, create a GitHub repository and push your code:

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit"

# Add your GitHub repository as origin
git remote add origin https://github.com/YOUR_USERNAME/datatalk.git
git branch -M main
git push -u origin main
```

### 2. Create a GitHub Release

Create a release with a version tag:

```bash
# Tag the current commit
git tag v0.1.0
git push origin v0.1.0
```

Or create the release through GitHub's web interface, or use the provided script:

```bash
./release_github.sh 0.1.0
```

### 3. Update the Homebrew Formula

After creating the release, you need to update the formula with the new version and SHA256 hash.

#### Option A: Automated (Recommended)

Use the provided Homebrew release script:

```bash
./release_homebrew.sh 0.1.0
```

This script will:
- Download the release tarball and calculate the SHA256 hash
- Update the formula file automatically
- Show you the changes made
- Optionally test the formula

#### Option B: Manual

1. Download the release tarball to get its SHA256 hash:
   ```bash
   curl -L https://github.com/tsaplin/datatalk/archive/refs/tags/v0.1.0.tar.gz | shasum -a 256
   ```

2. Update the `homebrew/datatalk.rb` file:
   - Replace the version number in the URL
   - Replace `SHA256_HASH_HERE` with the actual SHA256 hash from step 1

### 4. Option A: Create Your Own Homebrew Tap

Create your own Homebrew tap (recommended for easier maintenance):

```bash
# Create a new repository for your tap
# Name it: homebrew-datatalk
# Structure:
# homebrew-datatalk/
#   Formula/
#     datatalk.rb

# Users can then install with:
# brew tap YOUR_USERNAME/datatalk
# brew install datatalk
```

### 5. Option B: Submit to Official Homebrew

For official Homebrew inclusion:

1. Fork the [Homebrew/homebrew-core](https://github.com/Homebrew/homebrew-core) repository
2. Add your formula to `Formula/datatalk.rb`
3. Submit a pull request

### 6. Test the Installation

Test your formula locally:

```bash
# Install from local formula
brew install --build-from-source ./homebrew/datatalk.rb

# Or if using a tap:
brew tap YOUR_USERNAME/datatalk
brew install datatalk
```

## Formula Explanation

The `datatalk.rb` formula:

- **desc**: Short description of the tool
- **homepage**: Project homepage (GitHub repository)
- **url**: Download URL for the source code
- **sha256**: SHA256 hash of the source tarball
- **license**: Software license
- **depends_on**: System dependencies (Python 3.11)
- **install**: Installation method using `virtualenv_install_with_resources`
- **test**: Basic test to verify installation

## Updating Versions

For each new release:

1. Create a new git tag and GitHub release
2. Update the version number and SHA256 hash in the formula
3. Commit and push the updated formula

## Example Usage After Installation

Once installed via Homebrew, users can run:

```bash
datatalk --help
datatalk sample_data.csv --prompt "Show me the top 10 entries"
```

## Notes

- The formula uses `virtualenv_install_with_resources` which automatically handles Python dependencies
- Homebrew will create an isolated Python virtual environment for Datatalk
- Users don't need to worry about Python dependency conflicts
