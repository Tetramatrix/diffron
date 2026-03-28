"""
PR description generation for Diffron.

Generates PR titles and descriptions from branch diffs.
"""

from dataclasses import dataclass
from typing import Optional, Tuple
from .lemonade import LemonadeClient


DEFAULT_MAX_CHARS: int
DEFAULT_MAX_TOKENS: int
DEFAULT_TEMPERATURE: float


@dataclass
class PRDescription:
    """Represents a generated PR title and description."""

    title: str
    description: str

    def format_output(self) -> str:
        """Format as TITLE + DESCRIPTION output."""
        ...

    def to_github_cli(self) -> Tuple[str, str]:
        """Get title and body for GitHub CLI."""
        ...


def generate_pr_description(
    branch: Optional[str] = None,
    base: Optional[str] = None,
    max_chars: Optional[int] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    client: Optional[LemonadeClient] = None,
) -> PRDescription:
    """Generate a PR title and description from branch changes."""
    ...


def _parse_pr_response(response: str) -> Tuple[str, str]:
    """Parse PR response into title and description."""
    ...


def create_github_pr(
    branch: Optional[str] = None,
    base: Optional[str] = None,
    auto_submit: bool = False,
) -> PRDescription:
    """Generate PR and optionally create it via GitHub CLI."""
    ...
