"""
Commit message generation for Diffron.

Generates Conventional Commits format messages from git diffs.
"""

import re
import os
from typing import Optional

from .lemonade import LemonadeClient
from .utils import get_staged_diff


# Conventional Commits types
COMMIT_TYPES = [
    "feat",     # New feature
    "fix",      # Bug fix
    "docs",     # Documentation changes
    "style",    # Code style changes (formatting, etc.)
    "refactor", # Code refactoring
    "perf",     # Performance improvements
    "test",     # Test additions/modifications
    "build",    # Build system/external dependencies
    "ci",       # CI configuration
    "chore",    # Other changes
    "revert",   # Revert previous commit
]

DEFAULT_MAX_CHARS = 4000
DEFAULT_MAX_TOKENS = 100
DEFAULT_TEMPERATURE = 0.2


def generate_commit_message(
    diff: Optional[str] = None,
    max_chars: Optional[int] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    client: Optional[LemonadeClient] = None,
) -> str:
    """
    Generate a commit message from a git diff.

    Args:
        diff: Git diff string. If None, gets staged diff automatically.
        max_chars: Maximum characters of diff to send. Defaults to 4000.
        max_tokens: Maximum tokens to generate. Defaults to 100.
        temperature: Sampling temperature. Defaults to 0.2.
        client: LemonadeClient instance. Creates new one if not provided.

    Returns:
        Generated commit message in Conventional Commits format.

    Raises:
        ValueError: If diff is empty.
        ConnectionError: If Lemonade is not running.
    """
    max_chars = max_chars or int(os.environ.get("DIFFRON_MAX_DIFF_CHARS", DEFAULT_MAX_CHARS))
    max_tokens = max_tokens or DEFAULT_MAX_TOKENS
    temperature = temperature if temperature is not None else DEFAULT_TEMPERATURE

    # Get diff if not provided
    if diff is None:
        diff = get_staged_diff(max_chars=max_chars)

    if not diff.strip():
        raise ValueError("No staged changes to generate commit message from.")

    # Create client if not provided
    if client is None:
        client = LemonadeClient()

    # Build prompt
    commit_types = ", ".join(COMMIT_TYPES)
    prompt = (
        f"Write a concise Git commit message in Conventional Commits format. "
        f"Use one of these types: {commit_types}. "
        f"Format: 'type: description' (e.g., 'feat: add user authentication'). "
        f"Output ONLY the commit message, nothing else. No quotes, no explanations.\n\n"
        f"Diff:\n{diff}"
    )

    messages = [{"role": "user", "content": prompt}]

    # Generate completion
    response = client.chat_completion(
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    # Clean up response
    commit_message = response.strip()

    # Strip thinking/reasoning tags (e.g. from thinking models)
    commit_message = re.sub(r"<think>.*?</think>", "", commit_message, flags=re.DOTALL)
    commit_message = commit_message.replace("<think>", "").replace("</think>", "").strip()

    # Remove any surrounding quotes
    if commit_message.startswith('"') and commit_message.endswith('"'):
        commit_message = commit_message[1:-1]
    if commit_message.startswith("'") and commit_message.endswith("'"):
        commit_message = commit_message[1:-1]

    # Remove markdown code blocks if present
    if commit_message.startswith("```"):
        lines = commit_message.split("\n")
        commit_message = "\n".join(
            line for line in lines
            if not line.startswith("```")
        ).strip()

    return commit_message


def validate_commit_type(message: str) -> bool:
    """
    Validate that a commit message starts with a valid Conventional Commits type.

    Args:
        message: Commit message to validate.

    Returns:
        True if valid, False otherwise.
    """
    for commit_type in COMMIT_TYPES:
        if message.lower().startswith(f"{commit_type}:"):
            return True
        if message.lower().startswith(f"{commit_type}("):  # With scope
            return True
    return False


def format_commit_message(
    commit_type: str,
    description: str,
    scope: Optional[str] = None,
    breaking: bool = False,
) -> str:
    """
    Format a commit message with proper Conventional Commits structure.

    Args:
        commit_type: Type of commit (feat, fix, etc.).
        description: Short description of the change.
        scope: Optional scope (e.g., 'api', 'ui').
        breaking: Whether this is a breaking change.

    Returns:
        Formatted commit message.
    """
    scope_part = f"({scope})" if scope else ""
    breaking_part = "!" if breaking else ""

    return f"{commit_type}{scope_part}{breaking_part}: {description}"
