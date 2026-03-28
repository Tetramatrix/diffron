"""
Diffron - AI-powered Git automation with Lemonade.

Automatically generates commit messages and PR descriptions using
your local Lemonade LLM server.
"""

from typing import Optional
from .client import DiffronClient
from .lemonade import LemonadeClient
from .commit_gen import generate_commit_message
from .pr_gen import generate_pr_description, PRDescription
from .git_hooks import install_hooks, uninstall_hooks, is_hooks_installed

__version__: str
__author__: str

__all__ = [
    "DiffronClient",
    "LemonadeClient",
    "detect_lemonade_port",
    "generate_commit_message",
    "generate_pr_description",
    "PRDescription",
    "install_hooks",
    "uninstall_hooks",
    "is_hooks_installed",
]
