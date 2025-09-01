# PyPI Release Guide for Datatalk

This guide explains how to publish Datatalk to PyPI (Python Package Index).

## Prerequisites

1. **PyPI Account**: Create accounts on both [PyPI](https://pypi.org/) and [TestPyPI](https://test.pypi.org/)
2. **API Tokens**: Generate API tokens for authentication
3. **Build Tools**: Ensure `uv` is installed (already required for this project)

## Setup PyPI Credentials

### 1. Install Twine (for uploading)

```bash
uv add --dev twine
```

### 2. Configure API Tokens

Create API tokens on PyPI and TestPyPI, then configure them:

```bash
# Configure PyPI credentials
uv run twine configure pypi

# Configure TestPyPI credentials (for testing)
uv run twine configure testpypi
```

This will create `~/.pypirc` with your credentials.

## Release Process

### 1. Test Release (Recommended First)

Always test on TestPyPI first:

```bash
./release_pypi.sh 0.1.0 --test
```

This will:
- Update version in `pyproject.toml`
- Build the package using `uv build`
- Check the package with `twine check`
- Upload to TestPyPI

### 2. Test the TestPyPI Installation

```bash
# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ datatalk==0.1.0

# Test it works
datatalk --help
```

### 3. Production Release

If TestPyPI works correctly, release to production PyPI:

```bash
./release_pypi.sh 0.1.0
```

This will:
- Build and upload to PyPI
- Commit version changes
- Create and push git tags
- Provide next steps

## Manual Release Process

If you prefer manual control:

```bash
# 1. Update version in pyproject.toml
# 2. Clean and build
rm -rf dist/ build/ *.egg-info/
uv build

# 3. Check the package
uv run twine check dist/*

# 4. Upload to TestPyPI first
uv run twine upload --repository testpypi dist/*

# 5. Test installation
pip install --index-url https://test.pypi.org/simple/ datatalk

# 6. Upload to PyPI
uv run twine upload dist/*
```

## Package Structure

The package structure is defined in `pyproject.toml`:

- **Entry Point**: `datatalk.main:main` creates the `datatalk` command
- **Dependencies**: All dependencies are automatically installed
- **Metadata**: Description, author, license, etc.

## Installation Methods for Users

Once published, users can install via:

### PyPI (pip)
```bash
pip install datatalk
```

### PyPI (uv)
```bash
uv add datatalk
```

### Homebrew
```bash
brew tap tsaplin/datatalk
brew install datatalk
```

## Version Management

- Update version only in `pyproject.toml`
- Follow [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`
- Create git tags for each release
- Both scripts automatically handle version updates

## Troubleshooting

### Common Issues

1. **Authentication Error**:
   - Ensure API tokens are correctly configured
   - Check `~/.pypirc` file

2. **Package Already Exists**:
   - You cannot overwrite existing versions
   - Increment version number

3. **Build Errors**:
   - Ensure all dependencies are correctly specified
   - Check `pyproject.toml` syntax

4. **Import Errors After Install**:
   - Verify package structure
   - Test locally with `uv run datatalk`

### Useful Commands

```bash
# Check package without uploading
uv run twine check dist/*

# List package contents
tar -tzf dist/datatalk-*.tar.gz

# Test local installation
pip install dist/datatalk-*.whl
```

## Best Practices

1. **Always test on TestPyPI first**
2. **Use meaningful version numbers**
3. **Update changelog/release notes**
4. **Test installation on clean environment**
5. **Keep PyPI and Homebrew versions synchronized**

## Release Checklist

- [ ] Code is tested and working
- [ ] Version updated in `pyproject.toml`
- [ ] README and documentation updated
- [ ] Test on TestPyPI
- [ ] Release to PyPI
- [ ] Create GitHub release
- [ ] Update Homebrew formula
- [ ] Announce release
