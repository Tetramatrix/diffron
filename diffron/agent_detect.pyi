"""
AI agent detection for Diffron.

Detects when an AI coding agent is making a commit so Diffron can skip
message generation — the agent already produces good messages.

Maintains a categorized registry of known AI agents (CLI and GUI) and
supports user-configured custom patterns.
"""

from typing import Dict, List

AI_AGENTS: List[Dict[str, object]]

def list_known_agents() -> List[Dict[str, object]]:
    """Return the full registry of known AI agents."""
    ...

def list_agent_names() -> List[str]:
    """Return just the names of all known AI agents."""
    ...

def get_agents_by_type(agent_type: str) -> List[Dict[str, object]]:
    """Return agents filtered by type (cli, gui, cloud, agent)."""
    ...

def is_ai_agent_commit() -> bool:
    """Main entry point — returns True if an AI agent is detected."""
    ...

def is_well_formed_commit(message: str) -> bool:
    """Check if commit message already follows Conventional Commits format."""
    ...
