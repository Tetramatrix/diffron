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
DEFAULT_MAX_TOKENS = 500
DEFAULT_TEMPERATURE = 0.4


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
        max_tokens: Maximum tokens to generate. Defaults to 500.
        temperature: Sampling temperature. Defaults to 0.4.
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
        f"Write a Git commit message following the Conventional Commits specification.\n\n"
        f"Format:\n"
        f"  type(scope): short summary\n"
        f"\n"
        f"  Optional body explaining what changed and why.\n"
        f"  Use bullet points for multiple changes.\n"
        f"  Wrap lines at 72 characters.\n\n"
        f"Rules:\n"
        f"- Use one of: {commit_types}\n"
        f"- Scope is optional — use it when the change affects a specific module/component\n"
        f"- The summary line should be imperative mood (\"add\" not \"added\"), max 72 chars\n"
        f"- The body lists WHAT changed per file/area and WHY, not a diff walkthrough\n"
        f"- Separate title from body with a blank line\n"
        f"- If the change is trivial (single file, <10 lines), a title-only message is fine\n\n"
        f"Examples:\n"
        f"  feat(auth): add JWT token refresh logic\n"
        f"\n"
        f"  Implement automatic token refresh when the access token expires.\n"
        f"  Uses a background thread to refresh 30 seconds before expiry,\n"
        f"  preventing interrupted user sessions.\n"
        f"\n"
        f"  refactor(api): extract route handlers into separate modules\n"
        f"\n"
        f"  router.py:\n"
        f"  - Move auth routes to auth_router.py\n"
        f"  - Move user routes to user_router.py\n"
        f"\n"
        f"  Reduces router.py from 800 to 120 lines for easier maintenance.\n"
        f"\n"
        f"  fix(parser): handle empty input gracefully\n"
        f"\n"
        f"Output ONLY the commit message, nothing else.\n\n"
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

    # Remove markdown code blocks if present
    if commit_message.startswith("```"):
        lines = commit_message.split("\n")
        # Find opening and closing ``` and strip them
        start = 0
        end = len(lines)
        for i, line in enumerate(lines):
            if line.strip().startswith("```") and i == 0:
                start = 1
            elif line.strip() == "```" and i > 0:
                end = i
                break
        commit_message = "\n".join(lines[start:end]).strip()

    # Remove surrounding quotes (only if entire message is wrapped)
    if (commit_message.startswith('"') and commit_message.endswith('"')) or \
       (commit_message.startswith("'") and commit_message.endswith("'")):
        commit_message = commit_message[1:-1].strip()

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
