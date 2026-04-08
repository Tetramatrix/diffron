# Changelog

All notable changes to Diffron will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Pre-commit hook for linting suggestions
- Custom model selection per repository
- Multi-language commit message support
- Integration with GitHub CLI for auto PR creation

---

## [0.1.3] - 2026-04-08

### Added
- **Curated Models System** — Pre-configured model collection with easy selection
  - `list_available_models()` — List all curated models with metadata
  - `get_default_model()` — Get the recommended default model
  - `get_model_config(name)` — Get configuration for a specific model by name
  - `diffron-setup-model` CLI — Interactive model selection and configuration
    - `diffron-setup-model` — Set default model
    - `diffron-setup-model --list` — Show all available models
    - `diffron-setup-model --model NAME` — Set specific model
  - `ModelConfig` dataclass — Structured model metadata (name, description, parameters, best_for)

### Changed
- Updated metadata and documentation for public PyPI release
- Moved private files (docs, tests, scripts, notes) to `homelab/` folder
- Improved sync script exclusion patterns

---

## [0.1.0] - 2026-03-28

### Added

#### Core Features
- **Lemonade Integration**
  - Auto-detection of Lemonade server via `LEMONADE_SERVER_URL` environment variable
  - Fallback port scanning (8020, 8000, 8001, 8080, etc.)
  - Support for custom model configuration via `DIFFRON_MODEL`
  - Default model: `qwen2.5-it-3b-FLM`
  - Uses `lemonade-python-sdk` for API communication

- **Git Hooks**
  - `prepare-commit-msg` hook for automatic commit message generation
  - Global installation (`~/.diffron-hooks`)
  - Per-repository installation (`.git/hooks/`)
  - Windows-compatible shell wrapper for GitHub Desktop 3.5.5+
  - Smart skip logic for merges, rebases, and amend commits
  - Silent failure when Lemonade is unavailable (doesn't block commits)

- **Commit Message Generation**
  - Conventional Commits format enforcement
  - Configurable diff size limit (default: 4000 characters)
  - Temperature control for response creativity
  - Automatic cleanup of quotes and markdown in responses

- **PR Description Generation**
  - Branch diff analysis
  - Commit log summarization
  - TITLE + DESCRIPTION format output
  - GitHub CLI integration for auto PR creation

- **Python API**
  - `DiffronClient` class for unified interface
  - `LemonadeClient` for direct Lemonade API access
  - `generate_commit_message()` function
  - `generate_pr_description()` function
  - `install_hooks()` / `uninstall_hooks()` functions
  - `is_hooks_installed()` verification

- **CLI Commands**
  - `diffron-install-hooks` - Install Git hooks
  - `diffron-uninstall-hooks` - Remove Git hooks
  - `diffron-pr` - Generate PR description
  - `diffron-status` - Check Lemonade and hooks status

#### Documentation
- `README.md` - Project overview and quick start
- `docs/SETUP.md` - Complete Windows installation guide
- `docs/HOOKS.md` - Git hooks architecture documentation
- `docs/USAGE.md` - Detailed usage examples
- `docs/PLAN.md` - Project roadmap and architecture
- `docs/PYPI_RELEASE.md` - PyPI release checklist

#### Testing
- Unit tests for `lemonade.py`
- Unit tests for `commit_gen.py`
- Unit tests for `pr_gen.py`
- Unit tests for `git_hooks.py`
- Unit tests for `utils.py`

#### Developer Experience
- Type hints throughout codebase (`.pyi` stub files)
- `pyproject.toml` configuration
- `pytest` test suite
- `black` and `isort` configuration
- `mypy` type checking configuration

### Technical Details

#### Dependencies
- `openai>=1.0.0` - Lemonade API client
- `psutil>=5.9.0` - Port scanning

#### Supported Platforms
- Windows 10/11 (primary target)
- GitHub Desktop 3.5.5+ (hooks support)
- Python 3.9, 3.10, 3.11, 3.12

#### Architecture
- Modular package structure
- Separation of concerns (lemonade, hooks, commit_gen, pr_gen)
- Environment variable configuration
- Graceful error handling

### Known Issues
- Model auto-detection via API not supported by Lemonade (uses default)
- Requires `LEMONADE_SERVER_URL` environment variable for reliable detection
- Global hooks require Git configuration (`core.hooksPath`)

---

## Version History

| Version | Date | Status |
|---------|------|--------|
| 0.1.0 | 2026-03-28 | Initial Release |

---

*Last updated: 2026-03-28*
