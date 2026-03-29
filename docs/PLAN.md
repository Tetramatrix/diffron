# Diffron Project Plan

## Overview

**Diffron** generates Git commit messages and PR descriptions using Lemonade via lemonade-python-sdk.

**Name Etymology:** `diff` + `-ron` (echoing TabNeuron) — Technical, concise.

---

## Project Structure

```
diffron/
├── diffron/
│   ├── __init__.py
│   ├── __init__.pyi
│   ├── py.typed
│   ├── client.py          # Main DiffronClient class
│   ├── client.pyi
│   ├── lemonade.py        # Lemonade SDK integration & port detection
│   ├── lemonade.pyi
│   ├── git_hooks.py       # Git hook installation & management
│   ├── git_hooks.pyi
│   ├── commit_gen.py      # Commit message generation logic
│   ├── commit_gen.pyi
│   ├── pr_gen.py          # PR description generation logic
│   ├── pr_gen.pyi
│   └── utils.py           # Shared utilities
│   └── utils.pyi
├── tests/
│   ├── __init__.py
│   ├── test_lemonade.py
│   ├── test_git_hooks.py
│   ├── test_commit_gen.py
│   └── test_pr_gen.py
├── hooks/
│   ├── prepare-commit-msg     # Shell wrapper (no extension)
│   ├── prepare-commit-msg.py  # Python hook script
│   └── aipr.py                # PR description generator (manual run)
├── docs/
│   ├── PLAN.md            # This file
│   ├── SETUP.md           # Installation & configuration guide
│   ├── USAGE.md           # User documentation
│   └── API.md             # API reference
├── .gitignore
├── pyproject.toml
├── setup.py
├── setup.pyi
├── README.md
├── LICENSE
└── requirements.txt
```

---

## Core Features

### 1. Lemonade Auto-Detection
- **Port Discovery:** Automatically detect running Lemonade instance
- **Fallback Ports:** Try common ports (8000, 8001, 8080, etc.)
- **Connection Validation:** Verify Lemonade is responsive before use

### 2. Git Hook Automation
- **prepare-commit-msg Hook:** Auto-generates commit messages on `git commit`
- **Windows-Compatible:** Uses shell wrapper + Python script pattern
- **GitHub Desktop Ready:** Works with GitHub Desktop 3.5.5+ hooks support
- **Skip Logic:** Intelligently skips merges, rebases, and empty commits

### 3. Commit Message Generation
- **Conventional Commits:** Enforces `feat:`, `fix:`, `chore:`, etc. format
- **Context-Aware:** Analyzes staged diff (up to 4000 chars)
- **Concise Output:** Max 100 tokens, temperature 0.2 for consistency

### 4. PR Description Generator (`aipr.py`)
- **Manual Trigger:** Run `diffron-pr` or `python -m diffron.aipr`
- **Branch Analysis:** Compares branch to main/master
- **Dual Output:** Generates TITLE + DESCRIPTION format
- **GitHub CLI Integration:** Auto-creates PR via `gh pr create` if available

---

## Technical Architecture

### Module Dependencies

```
diffron/
├── client.py (Main Entry Point)
│   └── Uses: lemonade.py, git_hooks.py, commit_gen.py, pr_gen.py
│
├── lemonade.py (Lemonade Integration)
│   └── Uses: utils.py (for port scanning)
│   └── External: openai package (Lemonade API client)
│
├── git_hooks.py (Hook Management)
│   └── Uses: utils.py (for path resolution)
│   └── Installs: hooks/prepare-commit-msg, hooks/prepare-commit-msg.py
│
├── commit_gen.py (Commit Generation)
│   └── Uses: lemonade.py, utils.py (for diff extraction)
│
└── pr_gen.py (PR Generation)
    └── Uses: lemonade.py, utils.py (for branch/log extraction)
```

### External Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `openai` | >=1.0 | Lemonade API client (compatible with Lemonade's OpenAI-compatible API) |
| `gitpython` | >=3.1 | Git operations (optional, fallback to subprocess) |
| `psutil` | >=5.9 | Port scanning for Lemonade detection |

### Lemonade SDK Integration

Since Diffron is part of the same ecosystem as `lemonade-python-sdk`, it should:

1. **Import Directly:** `from lemonade_sdk import LemonadeClient`
2. **Auto-Configure:** Use SDK's built-in port detection
3. **Fallback:** If SDK not installed, use direct OpenAI client with auto-discovery

---

## Implementation Phases

### Phase 1: Core Infrastructure
- [ ] Create project skeleton (this plan)
- [ ] Implement `lemonade.py` with port detection
- [ ] Implement `commit_gen.py` with basic diff analysis
- [ ] Create shell wrapper + Python hook scripts
- [ ] Write `git_hooks.py` for installation logic

### Phase 2: PR Generation
- [ ] Implement `pr_gen.py` for branch analysis
- [ ] Create `aipr.py` standalone script
- [ ] Add GitHub CLI integration
- [ ] Format output as TITLE + DESCRIPTION

### Phase 3: Polish & Packaging
- [ ] Write comprehensive tests
- [ ] Create documentation (SETUP.md, USAGE.md, API.md)
- [ ] Build PyPI package
- [ ] Add CLI entry points (`diffron-install-hooks`, `diffron-pr`)

### Phase 4: Advanced Features (Future)
- [ ] Global hooks installation (`--global` flag)
- [ ] Custom model selection
- [ ] Commit message templates
- [ ] Multi-language support
- [ ] Pre-commit hook for linting suggestions

---

## Windows-Specific Considerations

### Git Hooks on Windows

**GitHub Desktop 3.5.5+** officially supports Git hooks. The setup requires:

1. **Shell Wrapper** (`.git/hooks/prepare-commit-msg`):
   ```sh
   #!/C:/Program Files/Git/usr/bin/sh.exe
   python ".git/hooks/prepare-commit-msg.py" "$1" "$2"
   exit 0
   ```

2. **Python Script** (`.git/hooks/prepare-commit-msg.py`):
   - Full logic for commit generation
   - Handles encoding (UTF-8)
   - Graceful error handling

### PATH Issues (Resolved in Desktop 3.5.5)
- No need for global hooks path workaround
- Git for Windows bundles proper shell interpreter
- Python must be in system PATH (user responsibility)

### Encoding
- All file I/O must use `encoding="utf-8"`
- Git diff output may contain non-ASCII characters
- Use `errors="ignore"` for subprocess output

---

## API Design

### DiffronClient

```python
from diffron import DiffronClient

client = DiffronClient()

# Auto-detect Lemonade
port = client.detect_lemonade_port()  # Returns 8000 or None

# Generate commit message
commit_msg = client.generate_commit_message(diff=diff_text)

# Generate PR description
pr = client.generate_pr_description(branch="feature/my-branch")
print(f"TITLE: {pr.title}")
print(f"DESCRIPTION: {pr.description}")

# Install hooks
client.install_hooks(repo_path=".")
```

### CLI Entry Points

```bash
# Install hooks to current repo
diffron-install-hooks

# Install hooks globally
diffron-install-hooks --global

# Generate PR description manually
diffron-pr

# Check Lemonade status
diffron-status
```

---

## Hook Script Specifications

### prepare-commit-msg (Shell Wrapper)

**Location:** `.git/hooks/prepare-commit-msg` (no extension)

**Purpose:** Git calls this file; it delegates to Python script.

**Content:**
```sh
#!/C:/Program Files/Git/usr/bin/sh.exe
python ".git/hooks/prepare-commit-msg.py" "$1" "$2"
exit 0
```

### prepare-commit-msg.py (Python Hook)

**Location:** `.git/hooks/prepare-commit-msg.py`

**Purpose:** Generates commit message from staged diff.

**Logic Flow:**
1. Parse arguments: `commit_msg_file`, `commit_source`
2. Skip if source is `merge`, `squash`, or `commit`
3. Get staged diff: `git diff --cached` (max 4000 chars)
4. Exit if diff is empty
5. Call Lemonade API with diff context
6. Write generated message to file

### aipr.py (PR Generator)

**Location:** Project root or installed to PATH

**Purpose:** Manually generate PR title + description.

**Logic Flow:**
1. Get current branch name
2. Get commit log: `git log --oneline main..HEAD`
3. Get diff: `git diff main..HEAD` (max 5000 chars)
4. Call Lemonade API with context
5. Parse TITLE + DESCRIPTION from response
6. Optionally create PR via `gh pr create`

---

## Testing Strategy

### Unit Tests
- `test_lemonade.py`: Port detection, API client
- `test_commit_gen.py`: Message generation logic
- `test_pr_gen.py`: PR description formatting
- `test_git_hooks.py`: Hook installation paths

### Integration Tests
- End-to-end commit message generation
- PR description with real Git repo
- Lemonade connection (mock or skip if unavailable)

### Test Fixtures
- Sample diffs (small, medium, large)
- Sample Git logs
- Mock Lemonade responses

---

## Documentation Plan

### SETUP.md
- Prerequisites (Python, Git, GitHub Desktop version)
- Lemonade installation & setup
- Diffron installation (`pip install diffron`)
- Hook installation (per-repo and global)
- Troubleshooting (common Windows issues)

### USAGE.md
- Basic workflow (commit, push, PR)
- CLI commands reference
- Customization options
- Examples with screenshots

### API.md
- `DiffronClient` class reference
- Method signatures & return types
- Error handling
- Extension points

---

## Success Criteria

1. **Functional:**
   - Hooks install successfully on Windows
   - Commit messages auto-generated on `git commit`
   - PR descriptions generated with `diffron-pr`
   - Lemonade auto-detection works reliably

2. **User Experience:**
   - Zero-config for users with Lemonade running
   - Clear error messages if Lemonade not found
   - Seamless GitHub Desktop integration

3. **Code Quality:**
   - Type hints throughout (`.pyi` stubs)
   - Test coverage >80%
   - PEP 8 compliant
   - Comprehensive docstrings

---

## Future Enhancements

- **Pre-commit Hook:** AI-powered linting suggestions
- **Review Assistant:** Auto-generate code review comments
- **Commit Summarizer:** Summarize multiple commits for squash
- **Multi-Model Support:** Let users choose model for generation
- **Offline Mode:** Cache responses for common patterns
- **Slack/Teams Integration:** Post commit summaries to channels

---

## Related Projects

```
┌─────────────────────────────────────────────────────┐
│  Aicono       │ AI Assistant (Desktop App)          │
│  TabNeuron    │ Browser Connector / Memory          │
│  Sorana       │ Advanced AI Interface               │
│  RyzenPilot   │ Hardware Optimization               │
│  lemonade-sdk │ Python SDK for AMD Lemonade API     │
│  Diffron      │ Git Commit/PR Generator             │
└─────────────────────────────────────────────────────┘
```

Note: Lemonade is AMD's local LLM server. Diffron uses lemonade-python-sdk to communicate with Lemonade's API.

---

## Next Steps

1. **Initialize Git Repo:** `git init` in project folder
2. **Create Package Skeleton:** Run `python -m diffron` scaffold
3. **Implement lemonade.py:** Port detection + API client
4. **Implement commit_gen.py:** Basic commit generation
5. **Create Hook Scripts:** Shell wrapper + Python script
6. **Test End-to-End:** Verify with real Git repo + Lemonade
7. **Write Docs:** SETUP.md, USAGE.md
8. **Publish to PyPI:** First release v0.1.0

---

*Document created: 2026-03-28*
*Project: Diffron v0.1.0 (Planning Phase)*
