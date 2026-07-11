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
from .agent_detect import (
    is_ai_agent_commit,
    is_well_formed_commit,
    list_known_agents,
    list_agent_names,
    get_agents_by_type,
)
from .models import (
    ModelConfig,
    list_available_models,
    get_default_model,
    get_model_config,
)

__version__ = "0.1.9"
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
    "is_ai_agent_commit",
    "is_well_formed_commit",
    "list_known_agents",
    "list_agent_names",
    "get_agents_by_type",
    "ModelConfig",
    "list_available_models",
    "get_default_model",
    "get_model_config",
]
