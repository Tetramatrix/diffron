"""
Diffron - AI-powered Git automation with Lemonade.

Automatically generates commit messages and PR descriptions using
your local Lemonade LLM server.
"""

from .client import DiffronClient
from .lemonade import LemonadeClient, detect_lemonade_port
from .commit_gen import generate_commit_message
from .pr_gen import generate_pr_description, PRDescription
from .git_hooks import install_hooks, uninstall_hooks, is_hooks_installed

__version__ = "0.1.0"
__author__ = "Diffron Contributors"
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
