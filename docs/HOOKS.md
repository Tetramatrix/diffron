# Diffron Git Hooks Architecture

Detailed technical documentation on how Diffron Git hooks work on Windows.

---

## Table of Contents

1. [Overview](#overview)
2. [Hook Types](#hook-types)
3. [Installation Methods](#installation-methods)
4. [Hook Execution Flow](#hook-execution-flow)
5. [File Structure](#file-structure)
6. [Windows-Specific Implementation](#windows-specific-implementation)
7. [Security Considerations](#security-considerations)
8. [Customization](#customization)

---

## Overview

Diffron uses Git's `prepare-commit-msg` hook to automatically generate commit messages using AI. The hook runs **before** the commit message editor opens, allowing it to pre-populate the message.

### Key Features

- **Automatic:** Runs on every `git commit`
- **Non-blocking:** Commits still work if Lemonade is unavailable
- **Smart:** Skips merges, rebases, and amends
- **Windows-native:** Designed for GitHub Desktop 3.5.5+

---

## Hook Types

### prepare-commit-msg Hook

**When it runs:** After Git prepares the default commit message, but before the editor starts.

**Purpose:** Modify or replace the default commit message.

**Arguments:**
1. `$1` - Path to file containing the commit message
2. `$2` - Source of the commit message (`message`, `template`, `merge`, `squash`, `commit`)
3. `$3` - (Optional) Commit object name (for `commit` source)

**Diffron behavior:**
- Reads staged diff
- Calls Lemonade API
- Writes generated message to file
- Git opens editor with generated message

---

## Installation Methods

### Global Installation

**Location:** `C:\Users\YourName\.diffron-hooks\`

**Git config:**
```bash
git config --global core.hooksPath "C:/Users/YourName/.diffron-hooks"
```

**Applies to:** All repositories on the system.

**Pros:**
- Install once, works everywhere
- Consistent behavior across projects

**Cons:**
- Affects all repositories
- Requires global Git configuration

### Per-Repository Installation

**Location:** `.git\hooks\`

**Git config:** None required (Git checks `.git/hooks` by default)

**Applies to:** Single repository only.

**Pros:**
- Repository-specific configuration
- No global changes

**Cons:**
- Must install for each repository
- Easy to forget when cloning

---

## Hook Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER ACTION                               │
│              git commit -m "anything" (or GitHub Desktop)        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GIT PREPARES COMMIT                           │
│         - Validates staged changes                               │
│         - Creates .git/COMMIT_EDITMSG with default message       │
│         - Determines commit source (message/template/merge)      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│              GIT EXECUTES prepare-commit-msg HOOK                │
│         - Calls: .diffron-hooks/prepare-commit-msg               │
│         - Passes: COMMIT_EDITMSG path, commit source             │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SHELL WRAPPER (prepare-commit-msg)            │
│         #!/C:/Program Files/Git/usr/bin/sh.exe                  │
│         HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"               │
│         python "$HOOK_DIR/prepare-commit-msg.py" "$1" "$2"      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                  PYTHON HOOK (prepare-commit-msg.py)             │
│         1. Parse arguments (msg_file, commit_source)             │
│         2. Check if should skip (merge/squash/amend)             │
│         3. Check if Lemonade is running                          │
│         4. Get staged diff (git diff --cached)                   │
│         5. Call Lemonade API for message generation              │
│         6. Write generated message to msg_file                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      GIT OPENS EDITOR                            │
│         - Opens COMMIT_EDITMSG with generated content            │
│         - User can review/modify before saving                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      COMMIT COMPLETED                            │
│         - Git creates commit with final message                  │
│         - Hook execution complete                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## File Structure

### Global Hooks Directory

```
C:\Users\YourName\.diffron-hooks\
├── prepare-commit-msg       # Shell wrapper (no extension)
└── prepare-commit-msg.py    # Python hook script
```

### File Contents

#### prepare-commit-msg (Shell Wrapper)

```bash
#!/C:/Program Files/Git/usr/bin/sh.exe
# Diffron prepare-commit-msg hook wrapper

# Get the directory where this wrapper script is located
HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
python "$HOOK_DIR/prepare-commit-msg.py" "$1" "$2"
exit 0
```

**Purpose:** Git for Windows executes this shell script, which delegates to Python.

**Why a wrapper?**
- Git for Windows uses bundled Git Bash
- Python may not be in Git Bash PATH
- Wrapper ensures correct Python interpreter is used

#### prepare-commit-msg.py (Python Hook)

```python
#!/usr/bin/env python
"""Diffron prepare-commit-msg Git hook."""

import sys
import os
from diffron.commit_gen import generate_commit_message
from diffron.lemonade import is_lemonade_running


def main():
    # Parse arguments
    if len(sys.argv) < 2:
        sys.exit(1)

    commit_msg_file = sys.argv[1]
    commit_source = sys.argv[2] if len(sys.argv) > 2 else ""

    # Skip for merges, rebases, amends
    skip_sources = {"merge", "squash", "commit"}
    if commit_source in skip_sources:
        sys.exit(0)

    # Check if Lemonade is running
    if not is_lemonade_running():
        sys.exit(0)  # Silent skip

    try:
        # Generate commit message
        commit_message = generate_commit_message()

        if commit_message:
            # Write to commit message file
            with open(commit_msg_file, "w", encoding="utf-8") as f:
                f.write(commit_message)
    except Exception as e:
        # Log error but don't block commit
        error_msg = f"# Diffron error: {e}\n"
        try:
            with open(commit_msg_file, "a", encoding="utf-8") as f:
                f.write(error_msg)
        except Exception:
            pass

    sys.exit(0)


if __name__ == "__main__":
    main()
```

---

## Windows-Specific Implementation

### GitHub Desktop 3.5.5+ Hooks Support

Before version 3.5.5, GitHub Desktop on Windows had issues with Git hooks:

| Issue | Status in 3.5.5+ |
|-------|------------------|
| PATH not inherited | ✅ Fixed |
| Shell interpreter missing | ✅ Fixed |
| Hooks path ignored | ✅ Fixed |

### Why This Implementation Works

1. **Shell Wrapper:** Uses Git Bash's `sh.exe` interpreter
   - Path: `C:/Program Files/Git/usr/bin/sh.exe`
   - Bundled with Git for Windows

2. **Python Path:** Wrapper finds Python from system PATH
   - No hardcoded Python path
   - Works with any Python installation

3. **Absolute Paths:** Hook directory resolved dynamically
   ```bash
   HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
   ```

4. **UTF-8 Encoding:** All file I/O uses UTF-8
   - Windows default is often CP1252
   - Explicit encoding prevents issues

### Git Configuration

**Check current hooks path:**
```bash
git config --global core.hooksPath
```

**Set hooks path manually:**
```bash
git config --global core.hooksPath "C:/Users/YourName/.diffron-hooks"
```

**Verify Git can find hooks:**
```bash
git config core.hooksPath
dir "%USERPROFILE%\.diffron-hooks"
```

---

## Security Considerations

### Hook Permissions

On Windows, file permissions are less restrictive than Unix. However:

- Hooks should only be writable by the user
- Avoid running Git as Administrator
- Keep `.diffron-hooks` in user directory

### Code Execution

Git hooks execute arbitrary code. Security measures:

1. **Diffron hooks are open source** - code is auditable
2. **No network calls except to localhost** - Lemonade runs locally
3. **No sensitive data transmitted** - only code diffs

### Supply Chain

When installing from PyPI:

```bash
pip install diffron
```

The package is verified by PyPI's security measures. For maximum security, install from source:

```bash
git clone https://github.com/diffron/diffron.git
cd diffron
pip install -e .
```

---

## Customization

### Modify Hook Behavior

Edit `.diffron-hooks/prepare-commit-msg.py`:

```python
# Change max diff size
from diffron.commit_gen import generate_commit_message
msg = generate_commit_message(max_chars=8000)  # Default: 4000

# Change temperature (creativity)
from diffron.lemonade import LemonadeClient
client = LemonadeClient()
msg = client.generate_commit_message(temperature=0.5)  # Default: 0.2
```

### Add Custom Logic

```python
# Add timestamp comment
with open(commit_msg_file, "a", encoding="utf-8") as f:
    f.write(f"\n# Generated by Diffron at {datetime.now()}")
```

### Disable for Specific Repositories

```bash
# In specific repository
cd path/to/repo
git config --unset core.hooksPath
```

### Use Different Model Per Repository

```bash
# In specific repository
cd path/to/repo
git config diffron.model "your-model-name"
```

Then modify hook to read this config:

```python
import subprocess
result = subprocess.run(
    ["git", "config", "diffron.model"],
    capture_output=True,
    text=True
)
model = result.stdout.strip() or "qwen2.5-it-3b-FLM"
```

---

## Debugging Hooks

### Enable Verbose Output

Add to `prepare-commit-msg.py`:

```python
import sys

# Log to file for debugging
with open("C:/temp/diffron-hook.log", "a", encoding="utf-8") as log:
    log.write(f"Arguments: {sys.argv}\n")
    log.write(f"Commit source: {commit_source}\n")
```

### Test Hook Manually

```bash
# Create test commit message file
echo "test message" > C:\temp\test-commit-msg.txt

# Run hook manually
python C:\Users\YourName\.diffron-hooks\prepare-commit-msg.py C:\temp\test-commit-msg.txt message

# Check result
type C:\temp\test-commit-msg.txt
```

### Check Git Hook Execution

```bash
# Enable Git trace
export GIT_TRACE=1
git commit -m "test"

# Look for hook execution in output
```

---

## Hook Lifecycle

### Installation
1. User runs `install_hooks(global_install=True)`
2. Files copied to `.diffron-hooks`
3. Git config set to hooks path

### Execution (per commit)
1. Git detects `prepare-commit-msg` hook
2. Shell wrapper executes
3. Python script runs
4. Message generated and written
5. Git opens editor

### Uninstallation
1. User runs `uninstall_hooks(global_install=True)`
2. Git config unset
3. `.diffron-hooks` directory removed

---

*Last updated: 2026-03-28*
*Version: 0.1.0*
