# Release Process

## 🚀 Quick Release

```bash
# Complete release to all platforms
./release_all.sh 0.1.3

# Test first (recommended)
./release_pypi.sh 0.1.3 --test
./release_all.sh 0.1.3
```

## 🔧 One-Time Setup

### PyPI Token

Store your PyPI API token securely:

```bash
# Option 1: In keychain (recommended)
uv run python -c "
import keyring, getpass
token = getpass.getpass('PyPI token: ')
keyring.set_password('https://upload.pypi.org/legacy/', '__token__', token)
"

# Option 2: Environment variable
export TWINE_PASSWORD=pypi-AgEIcHl...  # Add to ~/.zshrc
```

### Verify Tools

```bash
gh auth status    # GitHub CLI authenticated
uv --version      # Package manager working
```

## � Release Steps

1. **Clean working directory**: `git status`
2. **Run release**: `./release_all.sh X.Y.Z`
3. **Follow prompts**: Enter PyPI token when asked
4. **Verify**: Check [PyPI](https://pypi.org/project/datatalk-cli/) and [GitHub](https://github.com/vtsaplin/datatalk/releases)

## 🛠️ Individual Scripts

```bash
./release_github.sh 0.1.3     # GitHub release only
./release_pypi.sh 0.1.3       # PyPI release only  
./release_homebrew.sh 0.1.3   # Homebrew formula only
```

## 🔍 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Authentication failed" | Check PyPI token is stored correctly |
| "Version already exists" | Use a new version number |
| "Package name conflicts" | Already using `datatalk-cli` |
| "Working directory not clean" | Commit or stash changes |

## 📦 What Gets Released

- **GitHub**: Tag + release at [GitHub Releases](https://github.com/vtsaplin/datatalk/releases)
- **PyPI**: Package at [PyPI Project](https://pypi.org/project/datatalk-cli/)
- **Homebrew**: Formula updated in `homebrew/datatalk-cli.rb`

Installation after release:

```bash
pip install datatalk-cli        # PyPI
brew install ./homebrew/datatalk-cli.rb  # Local Homebrew
```
