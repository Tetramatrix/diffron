# Diffron Setup Guide for Windows

Complete installation guide for Diffron on Windows with AMD Lemonade and GitHub Desktop.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step 1: Install Lemonade](#step-1-install-lemonade)
3. [Step 2: Install Diffron](#step-2-install-diffron)
4. [Step 3: Configure Environment](#step-3-configure-environment)
5. [Step 4: Install Git Hooks](#step-4-install-git-hooks)
6. [Step 5: Verify Installation](#step-5-verify-installation)
7. [Changing the Model](#changing-the-model)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.9+ | Runtime environment |
| Git | 2.0+ | Version control |
| GitHub Desktop | 3.5.5+ | Git GUI with hooks support |

### Verify Prerequisites

```bash
# Check Python
python --version

# Check Git
git --version

# Check GitHub Desktop version
# Open GitHub Desktop → Help → About
```

---

## Step 1: Install Lemonade

AMD Lemonade is a local LLM server that Diffron uses for AI-powered commit messages.

### 1.1 Install lemonade-python-sdk

Our Python SDK for AMD Lemonade:

```bash
pip install lemonade-sdk
```

### 1.2 Download Model

Diffron uses `qwen2.5-it-3b-FLM` by default. Download it via Lemonade:

```bash
# Using Lemonade CLI
lemonade pull qwen2.5-it-3b-FLM

# Or via Python
python -c "from lemonade_sdk import pull; pull('qwen2.5-it-3b-FLM')"
```

### 1.3 Start Lemonade Server

```bash
# Start Lemonade with the model
lemonade serve qwen2.5-it-3b-FLM
```

**Default Configuration:**
- **URL:** `http://localhost:8020`
- **Port:** `8020`
- **Model:** `qwen2.5-it-3b-FLM`

### 1.4 Verify Lemonade is Running

```bash
# Test connection
curl http://localhost:8020/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "{\"model\": \"qwen2.5-it-3b-FLM\", \"messages\": [{\"role\": \"user\", \"content\": \"Hello\"}]}"
```

---

## Step 2: Install Diffron

### Option A: From PyPI (Recommended)

```bash
pip install diffron
```

### Option B: From Source (Development)

```bash
# Clone repository
git clone https://github.com/diffron/diffron.git
cd diffron

# Install in development mode
pip install -e .
```

### Verify Installation

```bash
python -c "import diffron; print(f'Diffron v{diffron.__version__}')"
```

---

## Step 3: Configure Environment

### 3.1 Set Lemonade Server URL (System-Wide)

**Method 1: Windows Environment Variables (Permanent)**

1. Press `Win + X` → System
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "User variables" or "System variables", click "New"
5. Add:
   - **Variable name:** `LEMONADE_SERVER_URL`
   - **Variable value:** `http://localhost:8020`
6. Click OK

**Method 2: Command Line (Current Session)**

```cmd
set LEMONADE_SERVER_URL=http://localhost:8020
```

**Method 3: PowerShell (Current Session)**

```powershell
$env:LEMONADE_SERVER_URL="http://localhost:8020"
```

### 3.2 Optional: Set Custom Model

```cmd
# System-wide (permanent)
setx DIFFRON_MODEL "qwen2.5-it-3b-FLM"

# Current session only
set DIFFRON_MODEL=qwen2.5-it-3b-FLM
```

### 3.3 Verify Environment Variables

```bash
# Check LEMONADE_SERVER_URL
echo %LEMONADE_SERVER_URL%

# Check DIFFRON_MODEL
echo %DIFFRON_MODEL%
```

---

## Step 4: Install Git Hooks

Git hooks enable automatic commit message generation.

### 4.1 Global Installation (All Repositories)

**Recommended for most users.**

```bash
python -c "from diffron.git_hooks import install_hooks; install_hooks(global_install=True)"
```

This installs hooks to `C:\Users\YourName\.diffron-hooks` and configures Git globally.

### 4.2 Per-Repository Installation

For specific repositories only:

```bash
cd path\to\your\repository
python -c "from diffron.git_hooks import install_hooks; install_hooks(repo_path='.')"
```

### 4.3 Verify Hooks Installation

```bash
# Check global hooks path
git config --global core.hooksPath

# Should output: C:/Users/YourName/.diffron-hooks
```

---

## Step 5: Verify Installation

### 5.1 Run Status Check

```bash
python -c "from diffron import is_lemonade_running, is_hooks_installed; print('Lemonade:', is_lemonade_running()); print('Hooks:', is_hooks_installed(check_global=True))"
```

Expected output:
```
Lemonade: True
Hooks: True
```

### 5.2 Test Commit Message Generation

```bash
# Create a test repository
mkdir test-diffron
cd test-diffron
git init

# Create a test file
echo "Hello World" > test.txt
git add test.txt

# Commit (hooks will generate message)
git commit -m "test"
```

Expected output:
```
[master abc123] feat: add test.txt file
 1 file changed, 1 insertion(+)
 create mode 100644 test.txt
```

---

## Changing the Model

### Option 1: Environment Variable (Recommended)

**System-wide:**
```cmd
setx DIFFRON_MODEL "your-model-name"
```

**Current session:**
```cmd
set DIFFRON_MODEL=your-model-name
```

### Option 2: Python API

```python
from diffron import DiffronClient

# Specify model directly
client = DiffronClient(model="your-model-name")

# Generate commit message
msg = client.generate_commit_message()
```

### Option 3: Modify Default in Source

Edit `diffron/lemonade.py`:

```python
DEFAULT_MODEL = "your-model-name"  # Change this line
```

### Available Models

Common models compatible with Lemonade:

| Model | Size | Use Case |
|-------|------|----------|
| `qwen2.5-it-3b-FLM` | 3B | Default, balanced |
| `qwen2.5-coder-7b` | 7B | Code-focused |
| `llama-3.2-3b` | 3B | General purpose |
| `mistral-7b` | 7B | High quality |

---

## How Git Hooks Work

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│ 1. User clicks "Commit" in GitHub Desktop               │
│    - Or runs: git commit -m "anything"                  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 2. Git executes prepare-commit-msg hook                 │
│    - Location: C:/Users/Name/.diffron-hooks/            │
│    - Wrapper: prepare-commit-msg (shell script)         │
│    - Python: prepare-commit-msg.py                      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 3. Hook reads staged diff                               │
│    - Runs: git diff --cached                            │
│    - Limits to 4000 characters                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 4. Hook calls Lemonade API                              │
│    - URL: http://localhost:8020/api/v1                  │
│    - Model: qwen2.5-it-3b-FLM                           │
│    - Prompt: "Write a Conventional Commit message..."   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 5. Hook writes generated message                        │
│    - Replaces commit message in .git/COMMIT_EDITMSG     │
│    - Git opens editor with generated message            │
└─────────────────────────────────────────────────────────┘
```

### Hook Files

**Global hooks location:** `C:\Users\YourName\.diffron-hooks\`

| File | Purpose |
|------|---------|
| `prepare-commit-msg` | Shell wrapper (calls Python script) |
| `prepare-commit-msg.py` | Python hook logic |

### Hook Behavior

| Scenario | Behavior |
|----------|----------|
| Lemonade running | Generates commit message |
| Lemonade not running | Silently skips, allows manual commit |
| Merge commit | Skips (doesn't interfere) |
| Rebase | Skips (doesn't interfere) |
| `git commit --amend` | Skips (doesn't interfere) |
| Empty commit | Skips (no diff to analyze) |

### Disable Hooks Temporarily

```bash
# Bypass hooks for single commit
git commit -m "manual message" --no-verify

# Or uninstall hooks
python -c "from diffron.git_hooks import uninstall_hooks; uninstall_hooks(global_install=True)"
```

---

## GitHub Desktop Integration

### Requirements

- **GitHub Desktop 3.5.5+** (required for hooks support on Windows)
- Hooks installed globally or per-repository

### Workflow

1. **Make changes** in your repository
2. **Open GitHub Desktop** - changes appear automatically
3. **Enter any commit message** (e.g., "auto")
4. **Click "Commit to main"**
5. **Diffron replaces** your message with AI-generated message

### Example

```
Before commit: "test"
After commit:  "feat: add user authentication module"
```

### Troubleshooting GitHub Desktop

**Problem:** Hooks don't execute

**Solutions:**

1. **Update GitHub Desktop:**
   - Help → Check for Updates
   - Must be version 3.5.5 or later

2. **Verify hooks path:**
   ```bash
   git config --global core.hooksPath
   ```

3. **Restart GitHub Desktop** after installing hooks

---

## VS Code Integration

### Using Git in VS Code

1. Make changes
2. Open Source Control panel (Ctrl+Shift+G)
3. Enter any message in commit input
4. Click commit button (or Ctrl+Enter)
5. Diffron generates the message

### Using Terminal in VS Code

```bash
# Standard commit (hooks run automatically)
git add .
git commit -m "auto"
```

---

## Troubleshooting

### Lemonade Not Detected

**Error:** `ConnectionError: Could not detect Lemonade server`

**Solutions:**

1. **Start Lemonade:**
   ```bash
   lemonade serve qwen2.5-it-3b-FLM
   ```

2. **Check URL:**
   ```bash
   echo %LEMONADE_SERVER_URL%
   # Should be: http://localhost:8020
   ```

3. **Test connection:**
   ```bash
   curl http://localhost:8020/api/v1/chat/completions ^
     -H "Content-Type: application/json" ^
     -d "{\"model\": \"qwen2.5-it-3b-FLM\", \"messages\": [{\"role\": \"user\", \"content\": \"Hi\"}]}"
   ```

### Hooks Not Executing

**Error:** Commit message not generated

**Solutions:**

1. **Check hooks path:**
   ```bash
   git config --global core.hooksPath
   ```

2. **Verify hook files exist:**
   ```bash
   dir %USERPROFILE%\.diffron-hooks
   ```

3. **Reinstall hooks:**
   ```bash
   python -c "from diffron.git_hooks import install_hooks; install_hooks(global_install=True)"
   ```

### Model Not Found (404 Error)

**Error:** `NotFoundError: Error code: 404`

**Solutions:**

1. **Verify model is downloaded:**
   ```bash
   lemonade list
   ```

2. **Download model if missing:**
   ```bash
   lemonade pull qwen2.5-it-3b-FLM
   ```

3. **Set correct model name:**
   ```cmd
   setx DIFFRON_MODEL "qwen2.5-it-3b-FLM"
   ```

### Python Not Found

**Error:** `'python' is not recognized`

**Solutions:**

1. **Add Python to PATH:**
   - System Properties → Environment Variables
   - Edit "Path" variable
   - Add: `C:\Users\YourName\AppData\Local\Programs\Python\Python314\`
   - Add: `C:\Users\YourName\AppData\Local\Programs\Python\Python314\Scripts\`

2. **Use full path:**
   ```bash
   C:\Python314\python.exe -c "from diffron.git_hooks import install_hooks; install_hooks(global_install=True)"
   ```

---

## Uninstall

### Remove Hooks

```bash
# Remove global hooks
python -c "from diffron.git_hooks import uninstall_hooks; uninstall_hooks(global_install=True)"
```

### Remove Environment Variables

1. System Properties → Environment Variables
2. Delete `LEMONADE_SERVER_URL` and `DIFFRON_MODEL`

### Uninstall Package

```bash
pip uninstall diffron
```

---

*Last updated: 2026-03-28*
*Version: 0.1.0*
