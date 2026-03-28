# Diffron

Git commit message and PR description generator using Lemonade.

![Version](https://img.shields.io/badge/version-0.1.0-blue)
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
- 🎯 **Model Flexible** - Use any Lemonade-compatible model (default: qwen2.5-it-3b-FLM)

---

## Quick Start

### 1. Install Lemonade

```bash
pip install lemonade-sdk
lemonade pull qwen2.5-it-3b-FLM
lemonade serve qwen2.5-it-3b-FLM
```

### 2. Set Environment Variable

**Permanent (recommended):**
1. System Properties → Environment Variables
2. New User Variable:
   - Name: `LEMONADE_SERVER_URL`
   - Value: `http://localhost:8020`

**Temporary (current session):**
```cmd
set LEMONADE_SERVER_URL=http://localhost:8020
```

### 3. Install Diffron

```bash
pip install diffron
```

### 4. Install Git Hooks

```bash
python -c "from diffron.git_hooks import install_hooks; install_hooks(global_install=True)"
```

### 5. Test It

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

### Change Model

```cmd
# System-wide
setx DIFFRON_MODEL "qwen2.5-coder-7b"

# Current session
set DIFFRON_MODEL=qwen2.5-coder-7b
```

### Python API

```python
from diffron import DiffronClient

# Use different model
client = DiffronClient(model="your-model-name")
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

| Project | Description |
|---------|-------------|
| **Aicono** | AI Assistant (Desktop App) |
| **TabNeuron** | Browser Connector / Memory |
| **Sorana** | Advanced AI Interface |
| **RyzenPilot** | Hardware Optimization |
| **lemonade-python-sdk** | Python SDK for AMD Lemonade API |

**Note:** Lemonade is AMD's local LLM server. Diffron uses the `lemonade-python-sdk` to communicate with Lemonade's API.

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
│    - Model: qwen2.5-it-3b-FLM                           │
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
lemonade serve qwen2.5-it-3b-FLM

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
lemonade pull qwen2.5-it-3b-FLM

# Verify model name
set DIFFRON_MODEL=qwen2.5-it-3b-FLM
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
