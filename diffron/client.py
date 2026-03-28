"""
Main Diffron client - unified interface for all Diffron functionality.
"""

from typing import Optional

from .lemonade import LemonadeClient, detect_lemonade_port
from .commit_gen import generate_commit_message
from .pr_gen import generate_pr_description, PRDescription
from .git_hooks import install_hooks, uninstall_hooks, is_hooks_installed


class DiffronClient:
    """
    Unified client for Diffron Git automation.

    Provides a single interface for commit message generation,
    PR description generation, and Git hooks management.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """
        Initialize Diffron client.

        Args:
            model: Model name to use. Auto-detects if not provided.
            host: Lemonade server host. Auto-detects if not provided.
            port: Lemonade server port. Auto-detects if not provided.
        """
        self._lemonade_client: Optional[LemonadeClient] = None
        self._model = model
        self._host = host
        self._port = port

    @property
    def lemonade_client(self) -> LemonadeClient:
        """Get or create Lemonade client."""
        if self._lemonade_client is None:
            self._lemonade_client = LemonadeClient(
                host=self._host,
                port=self._port,
                model=self._model,
            )
        return self._lemonade_client

    def detect_lemonade_port(self) -> Optional[int]:
        """
        Detect the port where Lemonade is running.

        Returns:
            Port number if found, None otherwise.
        """
        return detect_lemonade_port(host=self._host)

    def generate_commit_message(
        self,
        diff: Optional[str] = None,
        max_chars: Optional[int] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate a commit message from a git diff.

        Args:
            diff: Git diff string. If None, gets staged diff automatically.
            max_chars: Maximum characters of diff to send.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.

        Returns:
            Generated commit message in Conventional Commits format.
        """
        return generate_commit_message(
            diff=diff,
            max_chars=max_chars,
            max_tokens=max_tokens,
            temperature=temperature,
            client=self.lemonade_client,
        )

    def generate_pr_description(
        self,
        branch: Optional[str] = None,
        base: Optional[str] = None,
        max_chars: Optional[int] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> PRDescription:
        """
        Generate a PR title and description from branch changes.

        Args:
            branch: Branch name to analyze. Defaults to current branch.
            base: Base branch to compare against. Defaults to main/master.
            max_chars: Maximum characters of diff to send.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.

        Returns:
            PRDescription with generated title and description.
        """
        return generate_pr_description(
            branch=branch,
            base=base,
            max_chars=max_chars,
            max_tokens=max_tokens,
            temperature=temperature,
            client=self.lemonade_client,
        )

    def install_hooks(
        self,
        repo_path: str = ".",
        global_install: bool = False,
    ) -> bool:
        """
        Install Diffron Git hooks.

        Args:
            repo_path: Path to the git repository.
            global_install: If True, install globally for all repositories.

        Returns:
            True if installation was successful.
        """
        return install_hooks(
            repo_path=repo_path,
            global_install=global_install,
        )

    def uninstall_hooks(
        self,
        repo_path: str = ".",
        global_install: bool = False,
    ) -> bool:
        """
        Remove Diffron Git hooks.

        Args:
            repo_path: Path to the git repository.
            global_install: If True, remove global hooks configuration.

        Returns:
            True if uninstallation was successful.
        """
        return uninstall_hooks(
            repo_path=repo_path,
            global_install=global_install,
        )

    def is_hooks_installed(
        self,
        repo_path: str = ".",
        check_global: bool = False,
    ) -> bool:
        """
        Check if Diffron hooks are installed.

        Args:
            repo_path: Path to the git repository.
            check_global: If True, check for global hooks configuration.

        Returns:
            True if hooks are installed.
        """
        return is_hooks_installed(
            repo_path=repo_path,
            check_global=check_global,
        )
