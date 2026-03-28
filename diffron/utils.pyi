"""
Shared utilities for Diffron.

Provides common functions for port scanning, Git operations, and file handling.
"""

from typing import List, Optional


COMMON_PORTS: List[int]


def scan_ports(
    ports: Optional[List[int]] = None,
    host: str = "localhost"
) -> List[int]:
    """Scan for open ports on the given host."""
    ...


def is_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    """Check if a port is open on the given host."""
    ...


def get_staged_diff(max_chars: int = 4000) -> str:
    """Get the staged git diff."""
    ...


def get_branch_diff(branch: str, base: str = "main", max_chars: int = 5000) -> str:
    """Get the diff between a branch and its base."""
    ...


def get_commit_log(branch: str, base: str = "main") -> str:
    """Get the commit log between a branch and its base."""
    ...


def get_current_branch() -> Optional[str]:
    """Get the current git branch name."""
    ...


def is_git_repo(path: str = ".") -> bool:
    """Check if the given path is inside a git repository."""
    ...


def get_git_dir(path: str = ".") -> Optional[str]:
    """Get the .git directory path."""
    ...


def find_default_branch() -> str:
    """Find the default branch (main or master)."""
    ...
