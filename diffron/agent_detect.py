"""
AI agent detection for Diffron.

Detects when an AI coding agent is making a commit so Diffron can skip
message generation — the agent already produces good messages.

Maintains a categorized registry of known AI agents (CLI and GUI) and
supports user-configured custom patterns.
"""

import os
import subprocess
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Predefined AI agent registry
# ---------------------------------------------------------------------------
# Each entry: { "name": ..., "env_vars": [...], "git_names": [...], "git_emails": [...] }
# env_vars: substrings that may appear in ANY environment variable name (upper-cased)
# git_names: substrings that may appear in git config user.name
# git_emails: substrings that may appear in git config user.email

AI_AGENTS: List[Dict[str, object]] = [
    # ── CLI-based coding agents ──────────────────────────────────────────
    {
        "name": "Claude Code (Anthropic)",
        "type": "cli",
        "env_vars": ["CLAUDE", "ANTHROPIC"],
        "git_names": ["claude", "anthropic"],
        "git_emails": ["claude", "anthropic", "ai@anthropic"],
    },
    {
        "name": "GitHub Copilot CLI",
        "type": "cli",
        "env_vars": ["COPILOT", "GITHUB_COPILOT"],
        "git_names": ["copilot", "github-copilot"],
        "git_emails": ["copilot", "github-copilot"],
    },
    {
        "name": "Aider",
        "type": "cli",
        "env_vars": ["AIDER"],
        "git_names": ["aider"],
        "git_emails": ["aider"],
    },
    {
        "name": "OpenAI Codex CLI",
        "type": "cli",
        "env_vars": ["CODEX", "OPENAI"],
        "git_names": ["codex", "openai"],
        "git_emails": ["codex", "openai", "ai@openai"],
    },
    {
        "name": "Amazon Q Developer (CodeWhisperer)",
        "type": "cli",
        "env_vars": ["CODEWHISPERER", "AMAZON_Q", "AWS_Q"],
        "git_names": ["codewhisperer", "amazon-q", "aws-q"],
        "git_emails": ["codewhisperer", "amazon-q"],
    },
    {
        "name": "Cline (Roo Code)",
        "type": "cli",
        "env_vars": ["CLINE", "ROO_CODE", "ROO"],
        "git_names": ["cline", "roo"],
        "git_emails": ["cline", "roo"],
    },
    {
        "name": "Windsurf (Codeium)",
        "type": "cli",
        "env_vars": ["WINDSURF", "CODEIUM"],
        "git_names": ["windsurf", "codeium"],
        "git_emails": ["windsurf", "codeium"],
    },
    {
        "name": "Continue.dev",
        "type": "cli",
        "env_vars": ["CONTINUE"],
        "git_names": ["continue"],
        "git_emails": ["continue"],
    },
    {
        "name": "Tabnine",
        "type": "cli",
        "env_vars": ["TABNINE"],
        "git_names": ["tabnine"],
        "git_emails": ["tabnine"],
    },
    {
        "name": "Sourcegraph Cody",
        "type": "cli",
        "env_vars": ["CODY", "SOURCEGRAPH"],
        "git_names": ["cody", "sourcegraph"],
        "git_emails": ["cody", "sourcegraph"],
    },
    {
        "name": "Augment Code",
        "type": "cli",
        "env_vars": ["AUGMENT"],
        "git_names": ["augment"],
        "git_emails": ["augment"],
    },
    {
        "name": "MarsCode (ByteDance)",
        "type": "cli",
        "env_vars": ["MARSCODE"],
        "git_names": ["marscode"],
        "git_emails": ["marscode"],
    },
    {
        "name": "PearAI",
        "type": "cli",
        "env_vars": ["PEARAI"],
        "git_names": ["pearai"],
        "git_emails": ["pearai"],
    },
    {
        "name": "Void",
        "type": "cli",
        "env_vars": ["VOID"],
        "git_names": ["void"],
        "git_emails": ["void"],
    },
    {
        "name": "Supermaven",
        "type": "cli",
        "env_vars": ["SUPERMAVEN"],
        "git_names": ["supermaven"],
        "git_emails": ["supermaven"],
    },
    {
        "name": "Command Code",
        "type": "cli",
        "env_vars": ["COMMANDCODE", "COMMAND_CODE"],
        "git_names": ["command code", "commandcode"],
        "git_emails": ["commandcode"],
    },

    # ── GUI-based AI coding agents / IDEs ────────────────────────────────
    {
        "name": "Cursor",
        "type": "gui",
        "env_vars": ["CURSOR"],
        "git_names": ["cursor"],
        "git_emails": ["cursor"],
    },
    {
        "name": "Windsurf IDE",
        "type": "gui",
        "env_vars": ["WINDSURF", "CODEIUM"],
        "git_names": ["windsurf", "codeium"],
        "git_emails": ["windsurf", "codeium"],
    },
    {
        "name": "GitHub Copilot (VS Code)",
        "type": "gui",
        "env_vars": ["COPILOT", "GITHUB_COPILOT"],
        "git_names": ["copilot"],
        "git_emails": ["copilot"],
    },
    {
        "name": "Cline (VS Code)",
        "type": "gui",
        "env_vars": ["CLINE", "ROO_CODE"],
        "git_names": ["cline", "roo"],
        "git_emails": ["cline", "roo"],
    },
    {
        "name": "Continue.dev (VS Code)",
        "type": "gui",
        "env_vars": ["CONTINUE"],
        "git_names": ["continue"],
        "git_emails": ["continue"],
    },
    {
        "name": "Tabnine (IDE Plugin)",
        "type": "gui",
        "env_vars": ["TABNINE"],
        "git_names": ["tabnine"],
        "git_emails": ["tabnine"],
    },
    {
        "name": "Amazon Q (VS Code)",
        "type": "gui",
        "env_vars": ["CODEWHISPERER", "AMAZON_Q", "AWS_Q"],
        "git_names": ["codewhisperer", "amazon-q"],
        "git_emails": ["codewhisperer", "amazon-q"],
    },
    {
        "name": "Sourcegraph Cody (VS Code)",
        "type": "gui",
        "env_vars": ["CODY", "SOURCEGRAPH"],
        "git_names": ["cody", "sourcegraph"],
        "git_emails": ["cody", "sourcegraph"],
    },
    {
        "name": "MarsCode (VS Code)",
        "type": "gui",
        "env_vars": ["MARSCODE"],
        "git_names": ["marscode"],
        "git_emails": ["marscode"],
    },
    {
        "name": "JetBrains AI Assistant",
        "type": "gui",
        "env_vars": ["JETBRAINS", "IDEA"],
        "git_names": ["jetbrains", "ai assistant"],
        "git_emails": ["jetbrains"],
    },

    # ── Cloud / remote environments ──────────────────────────────────────
    {
        "name": "GitHub Codespaces",
        "type": "cloud",
        "env_vars": ["GITHUB_CODESPACES", "CODESPACE"],
        "git_names": ["codespace"],
        "git_emails": ["codespace", "github.dev"],
    },
    {
        "name": "GitPod",
        "type": "cloud",
        "env_vars": ["GITPOD"],
        "git_names": ["gitpod"],
        "git_emails": ["gitpod"],
    },
    {
        "name": "Replit",
        "type": "cloud",
        "env_vars": ["REPL", "REPLIT"],
        "git_names": ["replit", "repl"],
        "git_emails": ["replit"],
    },

    # ── Agent frameworks / orchestration ─────────────────────────────────
    {
        "name": "Devin (Cognition)",
        "type": "agent",
        "env_vars": ["DEVIN"],
        "git_names": ["devin", "cognition"],
        "git_emails": ["devin", "cognition"],
    },
    {
        "name": "SWE-agent",
        "type": "agent",
        "env_vars": ["SWE_AGENT", "SWEAGENT"],
        "git_names": ["swe-agent", "sweagent"],
        "git_emails": ["swe-agent", "sweagent"],
    },
    {
        "name": "OpenHands (OpenDevin)",
        "type": "agent",
        "env_vars": ["OPENHANDS", "OPENDEVIN"],
        "git_names": ["openhands", "opendevin"],
        "git_emails": ["openhands", "opendevin"],
    },
    {
        "name": "AutoCodeRover",
        "type": "agent",
        "env_vars": ["AUTOCODEROVER"],
        "git_names": ["autocoderover"],
        "git_emails": ["autocoderover"],
    },
    {
        "name": "Mintlify",
        "type": "agent",
        "env_vars": ["MINTLIFY"],
        "git_names": ["mintlify"],
        "git_emails": ["mintlify"],
    },

    # ── Tetramatrix ecosystem ────────────────────────────────────────────
    {
        "name": "MiMo Code",
        "type": "cli",
        "env_vars": ["MIMO", "MIMOCODE"],
        "git_names": ["mimo", "mimocode"],
        "git_emails": ["mimo"],
    },
    {
        "name": "Qwen Coder",
        "type": "cli",
        "env_vars": ["QWEN"],
        "git_names": ["qwen"],
        "git_emails": ["qwen"],
    },
    {
        "name": "Kilo Code",
        "type": "cli",
        "env_vars": ["KILO", "KILOCODE"],
        "git_names": ["kilo", "kilocode"],
        "git_emails": ["kilo"],
    },
    {
        "name": "Hermes",
        "type": "cli",
        "env_vars": ["HERMES"],
        "git_names": ["hermes"],
        "git_emails": ["hermes"],
    },
    {
        "name": "FreeBuff",
        "type": "cli",
        "env_vars": ["FREEBUFF"],
        "git_names": ["freebuff"],
        "git_emails": ["freebuff"],
    },
    {
        "name": "OpenCode",
        "type": "cli",
        "env_vars": ["OPENCODE"],
        "git_names": ["opencode"],
        "git_emails": ["opencode"],
    },
    {
        "name": "TabNeuron",
        "type": "gui",
        "env_vars": ["TABNEURON"],
        "git_names": ["tabneuron"],
        "git_emails": ["tabneuron"],
    },
    {
        "name": "Sorana",
        "type": "gui",
        "env_vars": ["SORANA"],
        "git_names": ["sorana"],
        "git_emails": ["sorana"],
    },
    {
        "name": "Aicono",
        "type": "gui",
        "env_vars": ["AICONO"],
        "git_names": ["aicono"],
        "git_emails": ["aicono"],
    },
    {
        "name": "DevBrowser",
        "type": "gui",
        "env_vars": ["DEVBROWSER"],
        "git_names": ["devbrowser"],
        "git_emails": ["devbrowser"],
    },
]


def list_known_agents() -> List[Dict[str, object]]:
    """Return the full registry of known AI agents.

    Returns:
        List of agent dicts with keys: name, type, env_vars, git_names, git_emails.
    """
    return list(AI_AGENTS)


def list_agent_names() -> List[str]:
    """Return just the names of all known AI agents."""
    return [a["name"] for a in AI_AGENTS]


def get_agents_by_type(agent_type: str) -> List[Dict[str, object]]:
    """Return agents filtered by type (cli, gui, cloud, agent).

    Args:
        agent_type: One of 'cli', 'gui', 'cloud', 'agent'.

    Returns:
        List of matching agent dicts.
    """
    return [a for a in AI_AGENTS if a.get("type") == agent_type]


# ---------------------------------------------------------------------------
# Conventional Commits types for message quality detection
# ---------------------------------------------------------------------------
CONVENTIONAL_COMMIT_TYPES = [
    "feat", "fix", "docs", "style", "refactor",
    "perf", "test", "build", "ci", "chore", "revert",
]


# ---------------------------------------------------------------------------
# Detection functions
# ---------------------------------------------------------------------------

def is_ai_agent_commit() -> bool:
    """Main entry point — returns True if an AI agent is detected.

    Combines three detection layers:
    1. Environment variable scanning against the AI agent registry
    2. Git config identity check against the AI agent registry
    3. User-configured custom patterns (DIFFRON_SKIP_PATTERNS / git config)
    """
    if _check_env_vars():
        return True
    if _check_git_config():
        return True
    if _check_custom_patterns():
        return True
    return False


def _check_env_vars() -> bool:
    """Scan ALL environment variable names against the AI agent registry.

    Case-insensitive substring match. On Windows os.environ is already
    case-insensitive; on Linux/macOS we normalize to uppercase for matching.
    """
    # Build a flat set of all env_var patterns from the registry
    all_patterns: set = set()
    for agent in AI_AGENTS:
        for pattern in agent.get("env_vars", []):
            all_patterns.add(pattern.upper())

    for key in os.environ:
        key_upper = key.upper()
        for pattern in all_patterns:
            if pattern in key_upper:
                return True
    return False


def _check_git_config() -> bool:
    """Check git user.name and user.email against the AI agent registry."""
    user_name = _get_git_config("user.name")
    if user_name:
        name_lower = user_name.lower()
        for agent in AI_AGENTS:
            for pattern in agent.get("git_names", []):
                if pattern in name_lower:
                    return True

    user_email = _get_git_config("user.email")
    if user_email:
        email_lower = user_email.lower()
        for agent in AI_AGENTS:
            for pattern in agent.get("git_emails", []):
                if pattern in email_lower:
                    return True

    return False


def _check_custom_patterns() -> bool:
    """Check user-configured patterns from DIFFRON_SKIP_PATTERNS / git config."""
    custom_names = _get_custom_env_names()
    for name in custom_names:
        if name in os.environ:
            return True
    return False


def _get_custom_env_names() -> list:
    """Get custom env var names from DIFFRON_SKIP_PATTERNS env var or git config."""
    names = []

    env_val = os.environ.get("DIFFRON_SKIP_PATTERNS", "")
    if env_val:
        names.extend(n.strip() for n in env_val.split(",") if n.strip())

    git_val = _get_git_config("diffron.skip-patterns")
    if git_val:
        names.extend(n.strip() for n in git_val.split(",") if n.strip())

    return names


def _get_git_config(key: str) -> Optional[str]:
    """Get a git config value. Returns None on failure."""
    try:
        result = subprocess.run(
            ["git", "config", key],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return None


def is_well_formed_commit(message: str) -> bool:
    """Check if commit message already follows Conventional Commits format.

    Matches: 'feat: description', 'feat(scope): description', etc.
    Skips comment lines and leading blank lines.
    """
    if not message or not message.strip():
        return False

    lines = message.split("\n")
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        for commit_type in CONVENTIONAL_COMMIT_TYPES:
            if stripped.startswith(f"{commit_type}:") or stripped.startswith(f"{commit_type}("):
                return True
        return False

    return False
