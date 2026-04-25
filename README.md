# Diffron

Git commit message and PR description generator using AMD Lemonade via lemonade-python-sdk.

**Diffron is a production-ready reference implementation of the lemonade-python-sdk — submitted to the AMD Lemonade Developer Challenge 2026.**

![Version](https://img.shields.io/badge/version-0.1.5-blue)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)

---

## Features

- 🤖 **Auto Commit Messages** - Generates Conventional Commits format messages from your staged changes
- 📝 **PR Descriptions** - Creates detailed PR titles and descriptions from branch diffs
- 🔌 **Lemonade Integration** - Works with your local Lemonade LLM server (no cloud required)
- 🪟 **Windows Ready** - Fully compatible with GitHub Desktop 3.5.5+ hooks support
- ⚡ **Auto-Detection** - Automatically finds your running Lemonade instance
- 🎯 **Curated Models** - Easy model selection with recommended models for different tasks

---

## Quick Start

### 1. Install AMD Lemonade Server

**Lemonade is AMD's local LLM server for Ryzen AI PCs.**

1. Download the installer from [AMD Lemonade Releases](https://github.com/AMD-AI-Software/lemonade/releases)
2. Run `Lemonade_Server_Installer.exe`
3. Launch Lemonade Server from the desktop shortcut
4. Download a model via the Lemonade UI (e.g., `qwen3.5-0.8b-gguf` - the new default!)

📚 **Documentation:** [AMD Ryzen AI - Lemonade Setup](https://ryzenai.docs.amd.com/en/latest/llm/server_interface.html)

### 2. Install lemonade-python-sdk

**Our Python SDK for AMD Lemonade API:**

```bash
pip install lemonade-sdk
```

🔗 **Source:** [github.com/Tetramatrix/lemonade-python-sdk](https://github.com/Tetramatrix/lemonade-python-sdk)

### 3. Configure Environment

**Set Lemonade Server URL (Permanent):**
1. System Properties → Environment Variables
2. New User Variable:
   - Name: `LEMONADE_SERVER_URL`
   - Value: `http://localhost:8020`

**Or Temporary (current session):**
```cmd
set LEMONADE_SERVER_URL=http://localhost:8020
```

### 4. Install Diffron

```bash
pip install diffron
```

### 5. Setup Model (Important!)

**Diffron comes with curated models. The default model works out of the box.**

**Default model:** `qwen2.5-it-3b-FLM` (included with Lemonade)

**To use a different model:**

```bash
# List all curated models
diffron-setup-model --list

# Set a specific model (sets DIFFRON_MODEL env var permanently)
diffron-setup-model --model qwen3.5-0.8b-gguf

# Reset to default
diffron-setup-model
```

**Or via Python API:**

```python
from diffron import list_available_models, get_default_model

# List all curated models
models = list_available_models()
for model in models:
    print(f"{model.name}: {model.description}")

# Get default model
default = get_default_model()
print(f"Default: {default.name}")
```

**Or manually via environment variable:**

```cmd
# Temporary (current session)
set DIFFRON_MODEL=qwen3.5-0.8b-gguf

# Permanent (System Properties → Environment Variables)
# Name: DIFFRON_MODEL
# Value: qwen3.5-0.8b-gguf
```

### 5. Install Git Hooks

```bash
python -c "from diffron.git_hooks import install_hooks; install_hooks(global_install=True)"
```

### 6. Test It

```bash
# Make a change
echo "test" > test.txt
git add test.txt

# Commit - hooks generate the message automatically!
git commit -m "anything"
```

Expected output:
```
[master abc123] feat: add test.txt file
 1 file changed, 1 insertion(+)
```

---

## Installation

### Requirements

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.9+ | Runtime |
| Git | 2.0+ | Version control |
| GitHub Desktop | 3.5.5+ | Git GUI (Windows) |
| lemonade-sdk | Latest | AMD Lemonade API client |
| Lemonade | Latest | Local LLM server |

### Full Installation Guide

See [docs/SETUP.md](docs/SETUP.md) for detailed Windows-specific instructions.

---

## Usage

### CLI Commands

```bash
# Install hooks globally
python -c "from diffron.git_hooks import install_hooks; install_hooks(global_install=True)"

# Generate PR description
python -c "from diffron import generate_pr_description; pr = generate_pr_description(); print(pr.format_output())"

# Check status
python -c "from diffron import is_lemonade_running, is_hooks_installed; print('Lemonade:', is_lemonade_running()); print('Hooks:', is_hooks_installed(check_global=True))"
```

### Python API

```python
from diffron import DiffronClient

# Create client
client = DiffronClient()

# Generate commit message
msg = client.generate_commit_message()
print(msg)  # "feat: add user authentication"

# Generate PR description
pr = client.generate_pr_description(branch="feature/my-feature")
print(f"TITLE: {pr.title}")
print(f"DESCRIPTION: {pr.description}")

# Install hooks
client.install_hooks(global_install=True)
```

### GitHub Desktop Workflow

1. Make changes to your files
2. Open GitHub Desktop
3. Enter any commit message (e.g., "auto")
4. Click "Commit to main"
5. **Diffron replaces** your message with AI-generated message

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LEMONADE_SERVER_URL` | `http://localhost:8020` | Lemonade server URL |
| `DIFFRON_MODEL` | `qwen2.5-it-3b-FLM` | Model name to use |
| `DIFFRON_MAX_DIFF_CHARS` | `4000` | Max diff characters |

### Curated Models

Diffron comes with a collection of curated models optimized for different use cases:

| Model ID | Description | Parameters | Best For |
|----------|-------------|------------|----------|
| **qwen2.5-it-3b-FLM** ⭐ | Qwen 2.5 IT — Default, reliable | 3B | Commit messages, PR descriptions |
| qwen3.5-0.8b-gguf | Qwen 3.5 — Lightweight & fast | 0.8B | Quick commits, low-resource PCs |
| qwen2.5-7b-gguf | Qwen 2.5 — Larger model | 7B | Complex analysis, code review |
| llama-3.2-3b-gguf | Llama 3.2 — Alternative | 3B | General purpose |

### Change Model

```bash
# Set a curated model
diffron-setup-model --model qwen3.5-0.8b-gguf

# List available models
diffron-setup-model --list

# Or manually (system-wide)
setx DIFFRON_MODEL "qwen3.5-0.8b-gguf"
```

### Python API

```python
from diffron import DiffronClient

# Use a curated model by name
client = DiffronClient(model="qwen2.5-7b-gguf")

# Get model configuration
from diffron import get_model_config
config = get_model_config("qwen3.5-0.8b-gguf")
if config:
    print(f"Best for: {config.best_for}")
    print(f"Parameters: {config.parameters}")
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [SETUP.md](docs/SETUP.md) | Complete installation guide for Windows |
| [HOOKS.md](docs/HOOKS.md) | Git hooks architecture and internals |
| [USAGE.md](docs/USAGE.md) | Detailed usage examples |

---

## Related Projects

### Tetramatrix Projects

| Project | Description |
|---------|-------------|
| [**lemonade-python-sdk**](https://github.com/Tetramatrix/lemonade-python-sdk) | 🍋 **AMD Lemonade Challenge Submission** - Python SDK for AMD Lemonade API |
| [**Diffron**](https://pypi.org/project/diffron/) | Production-ready reference implementation using lemonade-python-sdk (this repo) |
| [**Aicono**](https://tetramatrix.github.io/Aicono/) | AI Assistant (Desktop App) |
| [**TabNeuron**](https://tetramatrix.github.io/TabNeuron/) | Browser Connector / Memory |
| [**Sorana**](https://tetramatrix.github.io/Sorana/) | Advanced AI Interface |
| [**RyzenZPilot**](https://tetramatrix.github.io/RyzenZPilot/) | Hardware Optimization |

**Note:** Lemonade is AMD's local LLM server for Ryzen AI PCs. Diffron uses `lemonade-python-sdk` to communicate with Lemonade's API.

🏆 **AMD Lemonade Developer Challenge 2026:** This project demonstrates the capabilities of lemonade-python-sdk as a real-world application built on AMD Lemonade.

---

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│ 1. User makes changes and runs: git commit              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 2. Git hook executes prepare-commit-msg                 │
│    - Location: C:/Users/Name/.diffron-hooks/            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 3. Hook reads staged diff: git diff --cached            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 4. Hook calls Lemonade API                              │
│    - URL: http://localhost:8020/api/v1                  │
│    - Model: qwen3.5-0.8b-gguf (default)                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 5. AI generates Conventional Commit message             │
│    - "feat: add user authentication module"             │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 6. Git opens editor with generated message              │
│    - User can review/modify before saving               │
└─────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

### Lemonade Not Detected

```bash
# Start Lemonade
lemonade serve qwen3.5-0.8b-gguf

# Verify URL
echo %LEMONADE_SERVER_URL%
```

### Hooks Not Working

```bash
# Check GitHub Desktop version (must be 3.5.5+)
# Help → About

# Verify hooks path
git config --global core.hooksPath

# Reinstall hooks
python -c "from diffron.git_hooks import install_hooks; install_hooks(global_install=True)"
```

### Model Not Found (404)

```bash
# Download model
lemonade pull qwen3.5-0.8b-gguf

# Verify model name
diffron-setup-model --list
```

### Wrong Model Being Used

**Symptom:** Logs show old model name despite installation.

**Cause:** `DIFFRON_MODEL` environment variable overrides the default.

**Solution:**
```bash
# Check current value
echo %DIFFRON_MODEL%

# Reset to recommended
diffron-setup-model --model qwen3.5-0.8b-gguf

# Or remove override (uses default from curated models)
diffron-setup-model
```

See [docs/SETUP.md](docs/SETUP.md) for complete troubleshooting guide.

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Contributing

Contributions welcome! This is an open source project.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

### Development Setup

```bash
git clone https://github.com/diffron/diffron.git
cd diffron
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/
```

---

## Acknowledgments

- **Lemonade** - Local LLM server by the Lemonade team
- **GitHub Desktop** - Git GUI with hooks support (3.5.5+)
- **Conventional Commits** - Commit message format specification

---

*Version: 0.1.0 | Last updated: 2026-03-28*
