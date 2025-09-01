# Release Process Documentation

This document provides a complete guide for releasing new versions of DataTalk CLI across all platforms: GitHub, PyPI, and Homebrew.

## 🚀 Quick Release Commands

```bash
# For a complete release to all platforms
./release_all.sh 0.1.2

# For individual platform releases
./release_github.sh 0.1.2    # GitHub only
./release_pypi.sh 0.1.2      # PyPI only  
./release_homebrew.sh 0.1.2  # Homebrew only

# For testing PyPI first
./release_pypi.sh 0.1.2 --test
```

## 📋 Release Scripts Overview

### 1. `release_all.sh` - Master Release Script
**Purpose**: Orchestrates complete release across all platforms
**Usage**: `./release_all.sh <version> [--test-pypi] [--skip-homebrew]`

**What it does**:
1. Runs `release_github.sh` to create GitHub release
2. Runs `release_pypi.sh` to publish to PyPI
3. Runs `release_homebrew.sh` to update Homebrew formula
4. Provides comprehensive status reporting

**Examples**:
```bash
./release_all.sh 0.1.2                    # Full production release
./release_all.sh 0.1.2 --test-pypi        # Test on TestPyPI first
./release_all.sh 0.1.2 --skip-homebrew    # Skip Homebrew update
```

### 2. `release_github.sh` - GitHub Release
**Purpose**: Creates GitHub tags and releases
**Usage**: `./release_github.sh <version>`

**What it does**:
1. Updates version in `pyproject.toml`
2. Commits version change
3. Creates and pushes git tag
4. Provides next steps for manual GitHub release creation

### 3. `release_pypi.sh` - PyPI Release  
**Purpose**: Publishes package to PyPI or TestPyPI
**Usage**: `./release_pypi.sh <version> [--test]`

**What it does**:
1. Updates version in `pyproject.toml`
2. Cleans previous builds
3. Builds source distribution and wheel
4. Uploads to PyPI or TestPyPI
5. Creates git tag and commits (production mode only)

**Examples**:
```bash
./release_pypi.sh 0.1.2          # Production PyPI release
./release_pypi.sh 0.1.2 --test   # TestPyPI release for testing
```

### 4. `release_homebrew.sh` - Homebrew Formula Update
**Purpose**: Updates Homebrew formula with new version and SHA256
**Usage**: `./release_homebrew.sh <version>`

**What it does**:
1. Downloads release tarball from GitHub
2. Calculates SHA256 hash
3. Updates `homebrew/datatalk-cli.rb` formula
4. Creates backup of previous formula
5. Offers to test the formula locally

## 🔧 Prerequisites Setup

### 1. PyPI Authentication

#### Option A: Store in Keychain (Recommended)
```bash
# Install keyring support
uv add keyring

# Store token in keychain (will prompt for token)
uv run python -c "
import keyring
import getpass
token = getpass.getpass('Enter your PyPI token: ')
keyring.set_password('https://upload.pypi.org/legacy/', '__token__', token)
print('Token stored in keychain!')
"
```

#### Option B: Environment Variables
```bash
# Add to your ~/.zshrc or ~/.bashrc
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-AgEIcHl...  # Your actual token

# Reload shell
source ~/.zshrc
```

#### Option C: Configuration File
```bash
# Create ~/.pypirc
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHl...  # Your actual token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHl...  # Your TestPyPI token
EOF

chmod 600 ~/.pypirc
```

### 2. GitHub Authentication
Ensure GitHub CLI is authenticated:
```bash
gh auth status
# If not authenticated:
gh auth login
```

### 3. Required Tools
```bash
# Verify required tools are installed
uv --version       # Package manager
git --version      # Version control
gh --version       # GitHub CLI
curl --version     # For downloading and SHA256 calculation
```

## 🏗️ Project Structure

```
datatalk/
├── release_all.sh         # Master release script
├── release_github.sh      # GitHub release automation
├── release_pypi.sh        # PyPI publishing
├── release_homebrew.sh    # Homebrew formula updates
├── homebrew/
│   └── datatalk-cli.rb    # Homebrew formula
├── pyproject.toml         # Package configuration
└── docs/
    ├── PYPI_SETUP.md      # Detailed PyPI setup
    └── HOMEBREW_SETUP.md  # Detailed Homebrew setup
```

## 📝 Step-by-Step Release Process

### For a New Release (e.g., v0.1.3):

1. **Ensure clean working directory**:
   ```bash
   git status  # Should show "working tree clean"
   ```

2. **Run complete release**:
   ```bash
   ./release_all.sh 0.1.3
   ```

3. **Follow prompts**:
   - Confirm PyPI upload when prompted
   - Enter API token if not stored in keychain
   - Confirm Homebrew formula update

4. **Verify release**:
   ```bash
   # Check GitHub release
   open https://github.com/vtsaplin/datatalk/releases
   
   # Check PyPI
   open https://pypi.org/project/datatalk-cli/
   
   # Test installation
   pip install datatalk-cli==0.1.3
   datatalk-cli --version
   ```

### For Testing Before Production:

1. **Test on TestPyPI first**:
   ```bash
   ./release_all.sh 0.1.3 --test-pypi
   ```

2. **Test installation from TestPyPI**:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ datatalk-cli==0.1.3
   ```

3. **If testing succeeds, do production release**:
   ```bash
   ./release_pypi.sh 0.1.3
   ./release_homebrew.sh 0.1.3
   ```

## 🔍 Troubleshooting

### Common Issues:

1. **"Package name already exists"**:
   - Choose a different package name in `pyproject.toml`
   - Current name: `datatalk-cli`

2. **"Authentication failed"**:
   - Verify PyPI token is correctly stored
   - Check token hasn't expired
   - Ensure token has correct permissions

3. **"Version already exists"**:
   - Use a new version number
   - Check what versions exist: `pip index versions datatalk-cli`

4. **"Homebrew formula test failed"**:
   - This is expected if you don't have a Homebrew tap
   - Formula is still valid for manual installation

5. **"Git working directory not clean"**:
   - Commit or stash any uncommitted changes
   - Use `git status` to check what needs to be committed

### Getting Help:

```bash
# Check script help
./release_all.sh --help
./release_pypi.sh --help
./release_homebrew.sh --help

# Test individual components
uv build                    # Test package building
uv run twine check dist/*   # Validate built packages
```

## 🎯 Release Checklist

- [ ] Version number updated in `pyproject.toml`
- [ ] All tests passing: `uv run pytest`
- [ ] Documentation updated if needed
- [ ] GitHub release created with tag
- [ ] PyPI package published
- [ ] Homebrew formula updated
- [ ] Installation tested from all sources
- [ ] Release notes written
- [ ] Social media/announcement (optional)

## 🔗 Useful Links

- **PyPI Project**: https://pypi.org/project/datatalk-cli/
- **GitHub Repository**: https://github.com/vtsaplin/datatalk
- **GitHub Releases**: https://github.com/vtsaplin/datatalk/releases
- **PyPI Account**: https://pypi.org/manage/account/
- **TestPyPI**: https://test.pypi.org/project/datatalk-cli/

## 📚 Additional Resources

- **PyPI Project**: https://pypi.org/project/datatalk-cli/
- **GitHub Repository**: https://github.com/vtsaplin/datatalk
- **GitHub Releases**: https://github.com/vtsaplin/datatalk/releases
- **PyPI Account Management**: https://pypi.org/manage/account/
- **TestPyPI**: https://test.pypi.org/project/datatalk-cli/
- **Main Project Documentation**: [README.md](./README.md)
