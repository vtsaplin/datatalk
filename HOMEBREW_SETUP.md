# Homebrew Setup Guide for DataTalk CLI

This guide explains how to set up Homebrew installation for DataTalk CLI using our automated release process.

## Overview

DataTalk CLI uses an automated release process that maintains a Homebrew formula in the repository. The formula is automatically updated by our release scripts to use GitHub release tarballs as the source.

## Current Homebrew Configuration

### Formula Details
- **Package Name**: `datatalk-cli` 
- **Command Name**: `datatalk-cli`
- **Formula File**: `homebrew/datatalk-cli.rb`
- **Class Name**: `DatatalkCli`
- **Source**: GitHub release tarballs
- **Python Version**: 3.11

### Current Formula Structure
```ruby
class DatatalkCli < Formula
  include Language::Python::Virtualenv

  desc "Query CSV and Parquet data with natural language"
  homepage "https://github.com/vtsaplin/datatalk"
  url "https://github.com/vtsaplin/datatalk/archive/refs/tags/vX.X.X.tar.gz"
  sha256 "CALCULATED_AUTOMATICALLY"
  license "MIT"
  head "https://github.com/vtsaplin/datatalk.git", branch: "main"

  depends_on "python@3.11"

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/datatalk-cli", "--help"
  end
end
```
## Automated Release Process

### Using Release Scripts

Our release process automatically manages the Homebrew formula. The recommended approach is:

**Complete Release (All Platforms):**
```bash
./release_all.sh 0.1.2
```

**Homebrew Only:**
```bash
./release_homebrew.sh 0.1.2
```

### What the Release Script Does

The `release_homebrew.sh` script:

1. Downloads the GitHub release tarball for the specified version
2. Calculates the SHA256 hash automatically
3. Updates `homebrew/datatalk-cli.rb` with:
   - New version number in URL
   - Correct SHA256 hash
4. Creates a backup of the previous formula
5. Shows a diff of the changes
6. Commits the updated formula

### Manual Process (Not Recommended)

If you need to update manually for some reason:

1. Create GitHub release first:
   ```bash
   git tag v0.1.2
   git push origin v0.1.2
   gh release create v0.1.2 --generate-notes
   ```

2. Calculate SHA256 hash:
   ```bash
   curl -sL https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.2.tar.gz | shasum -a 256
   ```

3. Update `homebrew/datatalk-cli.rb` manually with new URL and SHA256

## Distribution Options

### Option 1: Local Formula (Current Setup)

Users can install directly from the repository:
```bash
# Clone the repository
git clone https://github.com/vtsaplin/datatalk.git
cd datatalk

# Install from local formula
brew install --build-from-source ./homebrew/datatalk-cli.rb

# Test installation
datatalk-cli --help
```

### Option 2: Create a Homebrew Tap (Future)

Create your own tap for easier distribution:

1. Create a new repository: `homebrew-tools`
2. Copy the formula to `Formula/datatalk-cli.rb`
3. Users install with:
   ```bash
   brew tap vtsaplin/tools
   brew install datatalk-cli
   ```

### Option 3: Submit to Official Homebrew (Future)

For maximum reach, submit to Homebrew core:
1. Fork [Homebrew/homebrew-core](https://github.com/Homebrew/homebrew-core)
2. Add formula to `Formula/datatalk-cli.rb`  
3. Submit pull request

## Testing the Formula

After any update, test locally:

```bash
# Test the current formula
brew install --build-from-source ./homebrew/datatalk-cli.rb

# Verify installation
datatalk-cli --version
datatalk-cli --help

# Test with sample data
datatalk-cli sample_data/employees.csv "Show me the data structure"

# Uninstall for clean testing
brew uninstall datatalk-cli
```

## Important Notes

### Consistent Naming
- **Package**: `datatalk-cli` (what you install)
- **Command**: `datatalk-cli` (what you run)
- **Formula**: `DatatalkCli` (Ruby class name)
- **File**: `datatalk-cli.rb` (formula filename)

### Source Strategy
- Uses GitHub release tarballs (not PyPI)
- Ensures consistency with git tags
- Allows users to install without PyPI dependency
- Automatically calculated SHA256 hashes

### Python Environment
- Creates isolated virtual environment
- Uses Python 3.11 as dependency
- Installs all Python dependencies automatically
- No conflicts with system Python packages

## Release Script Integration

The Homebrew setup is fully integrated with our release scripts:

- `release_all.sh` - Includes Homebrew update
- `release_homebrew.sh` - Dedicated Homebrew updates  
- `release_github.sh` - Creates necessary GitHub releases
- All scripts maintain version consistency across platforms
