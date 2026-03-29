# PyPI Release Checklist

Complete guide for publishing Diffron to PyPI as an open source package.

---

## Table of Contents

1. [Pre-Release Preparation](#pre-release-preparation)
2. [Build Package](#build-package)
3. [TestPyPI Upload](#testpypi-upload)
4. [Final Verification](#final-verification)
5. [PyPI Upload](#pypi-upload)
6. [Post-Release](#post-release)
7. [GitHub Release](#github-release)

---

## Pre-Release Preparation

### 1. Update Version Number

**Files to update:**

- `diffron/__init__.py`
- `setup.py`
- `pyproject.toml`
- `docs/SETUP.md` (version badges)
- `README.md` (version badges)

**Version format:** `MAJOR.MINOR.PATCH` (e.g., `0.1.0`)

```python
# diffron/__init__.py
__version__ = "0.1.0"
```

### 2. Update CHANGELOG.md

Document all changes since last release:

```markdown
## [0.1.0] - 2026-03-28

### Added
- Initial release
- Lemonade integration with auto-detection
- Git hooks for automatic commit message generation
- PR description generator
- CLI commands
- Python API
- Windows support for GitHub Desktop 3.5.5+
```

### 3. Verify Requirements

**Check `requirements.txt`:**
```
openai>=1.0.0
psutil>=5.9.0
```

**Check `setup.py` classifiers:**
```python
classifiers=[
    "Development Status :: 3 - Alpha",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
```

### 4. Run Tests

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v --cov=diffron

# Check coverage (target: >80%)
pytest --cov-report=html
```

### 5. Code Quality Checks

```bash
# Type checking
mypy diffron/

# Code formatting
black diffron/ tests/

# Import sorting
isort diffron/ tests/

# Linting (if configured)
flake8 diffron/
```

### 6. Verify Documentation

- [ ] README.md is complete and accurate
- [ ] SETUP.md has working instructions
- [ ] HOOKS.md explains architecture
- [ ] USAGE.md has examples
- [ ] All links work
- [ ] Code examples are tested

### 7. Clean Build Artifacts

```bash
# Remove old builds
rmdir /s /q build
rmdir /s /q dist
rmdir /s /q *.egg-info

# Clean Python cache
del /s /q *.pyc
rmdir /s /q __pycache__
```

---

## Build Package

### Install Build Tools

```bash
pip install build twine
```

### Create Distribution Packages

```bash
# Build source distribution and wheel
python -m build

# Verify output
dir dist
# Should show:
# - diffron-0.1.0.tar.gz
# - diffron-0.1.0-py3-none-any.whl
```

### Inspect Package Metadata

```bash
# Check wheel contents
tar -tzf dist/diffron-0.1.0.tar.gz

# Verify metadata
twine check dist/*
```

Expected output:
```
Checking dist/diffron-0.1.0.tar.gz: PASSED
Checking dist/diffron-0.1.0-py3-none-any.whl: PASSED
```

---

## TestPyPI Upload

### Create TestPyPI Account

1. Go to https://test.pypi.org/account/register/
2. Create account
3. Verify email

### Generate API Token

1. Go to https://test.pypi.org/manage/account/token/
2. Create new API token
3. Copy token (starts with `pypi-`)

### Configure Twine

```bash
# Create/edit .pypirc in home directory
notepad %USERPROFILE%\.pypirc
```

**Content:**
```ini
[distutils]
index-servers =
    testpypi
    pypi

[testpypi]
  repository = https://test.pypi.org/legacy/
  username = __token__
  password = pypi-<YOUR_TESTPYPI_TOKEN>

[pypi]
  repository = https://upload.pypi.org/legacy/
  username = __token__
  password = pypi-<YOUR_PYPI_TOKEN>
```

### Upload to TestPyPI

```bash
twine upload --repository testpypi dist/*
```

Enter your token when prompted.

### Test Installation from TestPyPI

```bash
# Create fresh virtual environment
python -m venv test-env
test-env\Scripts\activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple diffron==0.1.0

# Verify installation
python -c "import diffron; print(diffron.__version__)"
```

### Test Functionality

```bash
# Test imports
python -c "from diffron import DiffronClient; print('OK')"

# Test Lemonade detection
python -c "from diffron import detect_lemonade_port; print(detect_lemonade_port())"

# Test hooks installation
python -c "from diffron.git_hooks import install_hooks; print('OK')"
```

---

## Final Verification

### Pre-Upload Checklist

- [ ] All tests pass
- [ ] Code quality checks pass
- [ ] Documentation is complete
- [ ] Version number is correct
- [ ] CHANGELOG.md is updated
- [ ] TestPyPI upload successful
- [ ] TestPyPI installation works
- [ ] All features tested

### Repository Cleanup

```bash
# Remove test artifacts
rmdir /s /q test-env

# Clean build directory (keep dist for PyPI upload)
rmdir /s /q build
```

---

## PyPI Upload

### Create PyPI Account

1. Go to https://pypi.org/account/register/
2. Create account
3. Verify email

### Generate API Token

1. Go to https://pypi.org/manage/account/token/
2. Create new API token
3. Copy token (starts with `pypi-`)

### Update .pypirc

Add your PyPI token to `%USERPROFILE%\.pypirc`:

```ini
[pypi]
  repository = https://upload.pypi.org/legacy/
  username = __token__
  password = pypi-<YOUR_PYPI_TOKEN>
```

### Upload to PyPI

```bash
twine upload dist/*
```

Enter your token when prompted.

### Verify Upload

1. Go to https://pypi.org/project/diffron/
2. Check package page
3. Verify version, description, links

---

## Post-Release

### Update GitHub Repository

1. **Push latest code:**
   ```bash
   git add .
   git commit -m "chore: release v0.1.0"
   git tag v0.1.0
   git push origin master --tags
   ```

2. **Update repository description:**
   - Add PyPI badge to README
   - Add installation instructions

### Announce Release

1. **GitHub Discussions:**
   - Create release announcement
   - Tag contributors

2. **Social Media:**
   - Twitter/X
   - LinkedIn
   - Relevant subreddits (r/Python, r/MachineLearning)

3. **Community:**
   - Python Discord
   - Lemonade community channels

### Monitor Package

- Watch PyPI download stats: https://pypistats.org/packages/diffron
- Monitor GitHub issues
- Respond to user feedback

---

## GitHub Release

### Create Release on GitHub

1. Go to https://github.com/diffron/diffron/releases
2. Click "Create a new release"
3. Tag version: `v0.1.0`
4. Release title: `Diffron v0.1.0`
5. Description: Copy from CHANGELOG.md
6. Click "Publish release"

### Release Template

```markdown
## Diffron v0.1.0

Initial release of Diffron - AI-powered Git automation with Lemonade.

### Features

- 🤖 Automatic commit message generation
- 📝 PR description generator
- 🔌 Lemonade integration (auto-detection)
- 🪟 Windows support (GitHub Desktop 3.5.5+)
- ⚡ Conventional Commits format

### Installation

```bash
pip install diffron
```

### Quick Start

```bash
# Install hooks
python -c "from diffron.git_hooks import install_hooks; install_hooks(global_install=True)"

# Commit with AI-generated messages
git commit -m "auto"
```

### Documentation

- [Setup Guide](https://github.com/diffron/diffron/blob/main/docs/SETUP.md)
- [Usage Guide](https://github.com/diffron/diffron/blob/main/docs/USAGE.md)
- [Hooks Architecture](https://github.com/diffron/diffron/blob/main/docs/HOOKS.md)

### Contributors

Thanks to all contributors!

### License

MIT License
```

---

## Future Releases

### Version Bumping

```bash
# Patch release (bug fixes)
0.1.0 → 0.1.1

# Minor release (new features, backward compatible)
0.1.0 → 0.2.0

# Major release (breaking changes)
0.1.0 → 1.0.0
```

### Release Workflow

For each release:

1. Update version in all files
2. Update CHANGELOG.md
3. Run tests
4. Build package
5. Upload to TestPyPI
6. Test installation
7. Upload to PyPI
8. Create GitHub release
9. Announce release

---

## Troubleshooting

### Upload Fails: "File already exists"

**Solution:** Bump version number and rebuild.

```bash
# Update version
# Edit __init__.py, setup.py, pyproject.toml

# Rebuild
rmdir /s /q build dist
python -m build

# Upload again
twine upload dist/*
```

### Metadata Validation Fails

**Solution:** Check `twine check` output for specific errors.

Common issues:
- Missing required fields in `setup.py`
- Invalid classifier values
- Malformed long_description

### Installation Test Fails

**Solution:** Ensure all dependencies are on PyPI.

```bash
# Check if dependencies are available
pip index versions <package-name>
```

---

## Resources

- [PyPI Documentation](https://packaging.python.org/)
- [TestPyPI](https://test.pypi.org/)
- [twine Documentation](https://twine.readthedocs.io/)
- [Semantic Versioning](https://semver.org/)

---

*Last updated: 2026-03-28*
*Version: 0.1.0*
