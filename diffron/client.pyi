"""
Main Diffron client - unified interface for all Diffron functionality.
"""

from typing import Optional
from .lemonade import LemonadeClient
from .commit_gen import generate_commit_message
from .pr_gen import generate_pr_description, PRDescription


class DiffronClient:
    """Unified client for Diffron Git automation."""

    _lemonade_client: Optional[LemonadeClient]
    _model: Optional[str]
    _host: Optional[str]
    _port: Optional[int]

    def __init__(
        self,
        model: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """Initialize Diffron client."""
        ...

    @property
    def lemonade_client(self) -> LemonadeClient:
        """Get or create Lemonade client."""
        ...

    def detect_lemonade_port(self) -> Optional[int]:
        """Detect the port where Lemonade is running."""
        ...

    def generate_commit_message(
        self,
        diff: Optional[str] = None,
        max_chars: Optional[int] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """Generate a commit message from a git diff."""
        ...

    def generate_pr_description(
        self,
        branch: Optional[str] = None,
        base: Optional[str] = None,
        max_chars: Optional[int] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> PRDescription:
        """Generate a PR title and description from branch changes."""
        ...

    def install_hooks(
        self,
        repo_path: str = ".",
        global_install: bool = False,
    ) -> bool:
        """Install Diffron Git hooks."""
        ...

    def uninstall_hooks(
        self,
        repo_path: str = ".",
        global_install: bool = False,
    ) -> bool:
        """Remove Diffron Git hooks."""
        ...

    def is_hooks_installed(
        self,
        repo_path: str = ".",
        check_global: bool = False,
    ) -> bool:
        """Check if Diffron hooks are installed."""
        ...
