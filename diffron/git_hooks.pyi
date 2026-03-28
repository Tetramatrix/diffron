"""
Git hooks installation and management for Diffron.

Provides functions to install, uninstall, and verify Diffron Git hooks.
"""

from pathlib import Path
from typing import Optional


WRAPPER_NAME: str
PYTHON_HOOK_NAME: str
HOOKS_TEMPLATE_DIR: Path


def install_hooks(
    repo_path: str = ".",
    global_install: bool = False,
) -> bool:
    """Install Diffron Git hooks to a repository."""
    ...


def _install_global_hooks() -> bool:
    """Install hooks globally using git config core.hooksPath."""
    ...


def uninstall_hooks(
    repo_path: str = ".",
    global_install: bool = False,
) -> bool:
    """Remove Diffron Git hooks from a repository."""
    ...


def is_hooks_installed(
    repo_path: str = ".",
    check_global: bool = False,
) -> bool:
    """Check if Diffron hooks are installed."""
    ...


def _make_executable(path: Path) -> None:
    """Make a file executable."""
    ...


def get_hooks_status(repo_path: str = ".") -> dict:
    """Get detailed status of hooks installation."""
    ...
