# Contributing to DataTalk

## Development Setup

```bash
git clone https://github.com/vtsaplin/datatalk-cli.git
cd datatalk-cli

# Install dependencies (first time setup)
uv sync

# Option 1: Run from source (recommended, no installation needed)
uv run python -m datatalk.main sample_data/sales_data.csv

# Option 2: Install in editable mode (changes reflected immediately)
uv pip install -e .
dtalk sample_data/sales_data.csv

# Uninstall editable install (if needed)
uv pip uninstall datatalk-cli

# Run tests
uv run python -m pytest

# Build package
python -m build
```

## Creating Demo

Generate animated GIF using [VHS](https://github.com/charmbracelet/vhs):

```bash
# Install VHS
brew install vhs  # macOS
# or download from https://github.com/charmbracelet/vhs/releases

# Generate demo.gif from demo.tape
vhs demo.tape
```

Edit `demo.tape` to change demo script. Result saved to `docs/demo.gif`.

## Making a Release

Release process is automated via `release.sh`:

```bash
# 1. Update version in pyproject.toml
# 2. Run release script
./release.sh
```

**What it does:**
- Runs tests
- Checks you're on `main` branch
- Creates and pushes git tag (e.g., `v0.2.1`)
- GitHub Actions automatically publishes to PyPI

**Requirements:**
- Clean working directory (or will prompt to commit)
- All tests passing
- On `main` branch

## Contributing Guidelines

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests (`uv run python -m pytest`)
4. Submit a PR

[Issue Tracker](https://github.com/vtsaplin/datatalk-cli/issues) | [Discussions](https://github.com/vtsaplin/datatalk-cli/discussions)

