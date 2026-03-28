# Diffron Usage Guide

This guide provides detailed usage examples for Diffron's CLI and Python API.

---

## Table of Contents

1. [CLI Commands](#cli-commands)
2. [Python API](#python-api)
3. [Git Hooks Workflow](#git-hooks-workflow)
4. [PR Workflow](#pr-workflow)
5. [Advanced Usage](#advanced-usage)

---

## CLI Commands

### `diffron-install-hooks`

Install Git hooks to automatically generate commit messages.

```bash
# Install to current repository
diffron-install-hooks

# Install to specific repository
diffron-install-hooks --repo /path/to/repo

# Install globally (all repositories)
diffron-install-hooks --global
```

### `diffron-uninstall-hooks`

Remove Git hooks from a repository.

```bash
# Uninstall from current repository
diffron-uninstall-hooks

# Uninstall from specific repository
diffron-uninstall-hooks --repo /path/to/repo

# Uninstall global hooks
diffron-uninstall-hooks --global
```

### `diffron-pr`

Generate PR title and description.

```bash
# Generate for current branch
diffron-pr

# Generate for specific branch
diffron-pr --branch feature/my-feature

# Specify base branch
diffron-pr --base develop

# Generate and create PR on GitHub (requires gh CLI)
diffron-pr --create
```

### `diffron-status`

Check Diffron status (Lemonade connection, hooks installation).

```bash
# Quick status
diffron-status

# Detailed status
diffron-status --verbose

# Check specific repository
diffron-status --repo /path/to/repo
```

---

## Python API

### Basic Usage

```python
from diffron import DiffronClient

# Create client (auto-detects Lemonade)
client = DiffronClient()

# Generate commit message from staged diff
commit_msg = client.generate_commit_message()
print(commit_msg)  # "feat: add user authentication"

# Generate PR description
pr = client.generate_pr_description(branch="feature/my-feature")
print(f"TITLE: {pr.title}")
print(f"DESCRIPTION: {pr.description}")

# Install hooks
client.install_hooks(repo_path=".")
```

### Lemonade Client

```python
from diffron import LemonadeClient, detect_lemonade_port

# Detect Lemonade port
port = detect_lemonade_port()
print(f"Lemonade running on port: {port}")  # 8000

# Create client with specific settings
client = LemonadeClient(
    host="localhost",
    port=8000,
    model="your-model-name",
)

# Generate chat completion
response = client.chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    max_tokens=50,
    temperature=0.5,
)
print(response)
```

### Commit Message Generation

```python
from diffron import generate_commit_message

# Generate from staged diff (automatic)
msg = generate_commit_message()

# Generate from custom diff
custom_diff = """
diff --git a/src/main.py b/src/main.py
+def hello():
+    print("Hello, World!")
"""
msg = generate_commit_message(diff=custom_diff)

# With custom parameters
msg = generate_commit_message(
    diff=custom_diff,
    max_chars=2000,      # Limit diff size
    max_tokens=50,       # Limit response length
    temperature=0.1,     # More deterministic
)
```

### PR Description Generation

```python
from diffron import generate_pr_description, PRDescription

# Generate for current branch
pr = generate_pr_description()

# Generate for specific branch
pr = generate_pr_description(
    branch="feature/my-feature",
    base="main",
)

# Access properties
print(f"Title: {pr.title}")
print(f"Description: {pr.description}")

# Format output
print(pr.format_output())

# Get GitHub CLI format
title, body = pr.to_github_cli()
```

### Git Hooks Management

```python
from diffron import install_hooks, uninstall_hooks, is_hooks_installed

# Install hooks
install_hooks(repo_path=".")
install_hooks(repo_path="/path/to/repo")
install_hooks(global_install=True)  # Global installation

# Check if installed
if is_hooks_installed():
    print("Hooks are installed!")

# Uninstall hooks
uninstall_hooks(repo_path=".")
uninstall_hooks(global_install=True)  # Remove global hooks

# Get detailed status
from diffron import get_hooks_status
status = get_hooks_status()
print(status)
# {
#     'is_git_repo': True,
#     'local_hooks_installed': True,
#     'global_hooks_configured': False,
#     ...
# }
```

---

## Git Hooks Workflow

### Automatic Commit Messages

Once hooks are installed, commit messages are generated automatically:

```bash
# Make changes
echo "new feature" >> feature.py
git add feature.py

# Commit - hooks generate the message
git commit

# Result: "feat: add new feature" (auto-generated)
```

### Skip Auto-Generation

Hooks automatically skip:
- Merge commits
- Rebase operations
- Amend commits (`git commit --amend`)
- Empty commits

To manually write a commit message when hooks are installed:

```bash
# Use -m flag to provide message directly
git commit -m "chore: manual commit message"

# Or edit the generated message
git commit  # Opens editor with generated message
```

### Hook Behavior

The `prepare-commit-msg` hook:

1. **Checks Lemonade:** Silently exits if Lemonade is not running
2. **Analyzes Diff:** Gets staged changes (max 4000 chars)
3. **Generates Message:** Calls Lemonade API
4. **Writes Message:** Populates commit message file
5. **Opens Editor:** Git opens editor with generated message (default behavior)

To skip the editor and commit directly:

```bash
git commit -m "auto"  # Hook replaces "auto" with generated message
```

---

## PR Workflow

### Standard Workflow

1. **Create feature branch:**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make commits:**
   ```bash
   # Diffron auto-generates commit messages
   git add .
   git commit
   ```

3. **Generate PR description:**
   ```bash
   diffron-pr
   ```

4. **Copy output and create PR:**
   - Copy TITLE and DESCRIPTION
   - Go to GitHub
   - Create PR with copied content

### Automated Workflow (with GitHub CLI)

1. **Install GitHub CLI:**
   ```bash
   # Windows (winget)
   winget install GitHub.cli

   # Or download from https://cli.github.com/
   ```

2. **Authenticate:**
   ```bash
   gh auth login
   ```

3. **Generate and create PR:**
   ```bash
   diffron-pr --create
   ```

### Manual PR Script

Use the standalone `aipr.py` script:

```bash
# From hooks directory
python hooks/aipr.py

# With branch arguments
python hooks/aipr.py feature/my-feature main
```

---

## Advanced Usage

### Custom Commit Types

Diffron uses Conventional Commits by default. To customize:

```python
from diffron.commit_gen import COMMIT_TYPES, format_commit_message

# View available types
print(COMMIT_TYPES)
# ['feat', 'fix', 'docs', 'style', 'refactor', 'perf', 'test', 'build', 'ci', 'chore', 'revert']

# Format with scope and breaking change
msg = format_commit_message(
    commit_type="feat",
    description="change API structure",
    scope="api",
    breaking=True,
)
print(msg)  # "feat(api)!: change API structure"
```

### Batch Operations

```python
from diffron import DiffronClient

client = DiffronClient()

# Process multiple repositories
repos = ["/path/to/repo1", "/path/to/repo2"]

for repo in repos:
    print(f"Processing {repo}...")
    client.install_hooks(repo_path=repo)
```

### Integration with CI/CD

Use Diffron in CI pipelines:

```yaml
# GitHub Actions example
name: PR Description
on:
  pull_request:
    types: [opened]

jobs:
  generate-pr:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install Diffron
        run: pip install diffron
      - name: Generate PR description
        run: diffron-pr
        env:
          DIFFRON_LEMONADE_HOST: ${{ secrets.LEMONADE_HOST }}
```

### Custom Prompts

Modify the prompt for commit generation:

```python
from diffron.lemonade import LemonadeClient

client = LemonadeClient()

custom_prompt = """
Analyze this git diff and write a commit message.
Focus on the user-facing changes.
Format: type(scope): description

Diff:
""" + diff

response = client.chat_completion(
    messages=[{"role": "user", "content": custom_prompt}],
    max_tokens=100,
    temperature=0.2,
)
```

---

## Tips and Best Practices

### 1. Review Generated Messages

Always review auto-generated commit messages before committing:

```bash
git commit  # Opens editor with generated message
# Review and save, or modify as needed
```

### 2. Use Scopes for Large Projects

For projects with multiple components:

```bash
# Generated: "feat(api): add user endpoint"
# Generated: "fix(ui): resolve button alignment"
```

### 3. Keep Changes Focused

Smaller, focused commits generate better messages:

```bash
# Good: Single feature
git add src/auth.py
git commit  # "feat: add authentication"

# Better than: Multiple unrelated changes
git add .
git commit  # Generic message
```

### 4. Combine with Pre-commit Hooks

Use Diffron alongside pre-commit hooks:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
  # Diffron handles commit messages separately
```

---

## Examples

### Example 1: Feature Development

```bash
# Start feature branch
git checkout -b feat/user-auth

# Make changes and commit (auto-generated messages)
git add src/auth.py
git commit  # "feat: add user authentication"

git add tests/test_auth.py
git commit  # "test: add authentication tests"

# Generate PR description
diffron-pr --create
```

### Example 2: Bug Fix

```bash
# Create fix branch
git checkout -b fix/login-bug

# Fix the bug
git add src/login.py
git commit  # "fix: resolve login redirect issue"

# Generate PR
diffron-pr --base main
```

### Example 3: Documentation Update

```bash
# Update docs
git add docs/*.md
git commit  # "docs: update installation guide"

# No PR needed for docs-only changes
git push origin main
```

---

*Last updated: 2026-03-28*
