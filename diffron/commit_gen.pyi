"""
Commit message generation for Diffron.

Generates Conventional Commits format messages from git diffs.
"""

from typing import Optional
from .lemonade import LemonadeClient


COMMIT_TYPES: list[str]

DEFAULT_MAX_CHARS: int
DEFAULT_MAX_TOKENS: int
DEFAULT_TEMPERATURE: float


def generate_commit_message(
    diff: Optional[str] = None,
    max_chars: Optional[int] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    client: Optional[LemonadeClient] = None,
) -> str:
    """Generate a commit message from a git diff."""
    ...


def validate_commit_type(message: str) -> bool:
    """Validate that a commit message starts with a valid Conventional Commits type."""
    ...


def format_commit_message(
    commit_type: str,
    description: str,
    scope: Optional[str] = None,
    breaking: bool = False,
) -> str:
    """Format a commit message with proper Conventional Commits structure."""
    ...
