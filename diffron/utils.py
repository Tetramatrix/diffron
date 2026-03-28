"""
Shared utilities for Diffron.

Provides common functions for port scanning, Git operations, and file handling.
"""

import subprocess
import socket
from typing import List, Optional
import psutil


COMMON_PORTS = [8000, 8001, 8080, 8081, 5000, 5001]


def scan_ports(ports: Optional[List[int]] = None, host: str = "localhost") -> List[int]:
    """
    Scan for open ports on the given host.

    Args:
        ports: List of ports to scan. Defaults to COMMON_PORTS.
        host: Host to scan. Defaults to localhost.

    Returns:
        List of open ports.
    """
    if ports is None:
        ports = COMMON_PORTS

    open_ports = []
    for port in ports:
        if is_port_open(host, port):
            open_ports.append(port)

    return open_ports


def is_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    """
    Check if a port is open on the given host.

    Args:
        host: Host to check.
        port: Port number to check.
        timeout: Connection timeout in seconds.

    Returns:
        True if port is open, False otherwise.
    """
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def get_staged_diff(max_chars: int = 4000) -> str:
    """
    Get the staged git diff.

    Args:
        max_chars: Maximum number of characters to return.

    Returns:
        Staged diff as string, truncated to max_chars.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True,
            text=True,
            errors="ignore",
            timeout=30,
        )
        diff = result.stdout[:max_chars]
        return diff
    except (subprocess.SubprocessError, FileNotFoundError):
        return ""


def get_branch_diff(branch: str, base: str = "main", max_chars: int = 5000) -> str:
    """
    Get the diff between a branch and its base.

    Args:
        branch: Branch name to compare.
        base: Base branch to compare against.
        max_chars: Maximum number of characters to return.

    Returns:
        Diff as string, truncated to max_chars.
    """
    try:
        result = subprocess.run(
            ["git", "diff", f"{base}..{branch}"],
            capture_output=True,
            text=True,
            errors="ignore",
            timeout=30,
        )
        diff = result.stdout[:max_chars]
        return diff
    except (subprocess.SubprocessError, FileNotFoundError):
        return ""


def get_commit_log(branch: str, base: str = "main") -> str:
    """
    Get the commit log between a branch and its base.

    Args:
        branch: Branch name.
        base: Base branch.

    Returns:
        Commit log as string (oneline format).
    """
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", f"{base}..{branch}"],
            capture_output=True,
            text=True,
            errors="ignore",
            timeout=30,
        )
        return result.stdout
    except (subprocess.SubprocessError, FileNotFoundError):
        return ""


def get_current_branch() -> Optional[str]:
    """
    Get the current git branch name.

    Returns:
        Branch name or None if not in a git repo.
    """
    try:
        result = subprocess.run(
            ["git", "symbolic-ref", "--short", "HEAD"],
            capture_output=True,
            text=True,
            errors="ignore",
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return None


def is_git_repo(path: str = ".") -> bool:
    """
    Check if the given path is inside a git repository.

    Args:
        path: Path to check.

    Returns:
        True if inside a git repo, False otherwise.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
            cwd=path,
            timeout=10,
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def get_git_dir(path: str = ".") -> Optional[str]:
    """
    Get the .git directory path.

    Args:
        path: Path to check.

    Returns:
        Absolute path to .git directory or None.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
            cwd=path,
            timeout=10,
        )
        if result.returncode == 0:
            git_dir = result.stdout.strip()
            # Convert to absolute path
            import os
            if not os.path.isabs(git_dir):
                git_dir = os.path.abspath(os.path.join(path, git_dir))
            return git_dir
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return None


def find_default_branch() -> str:
    """
    Find the default branch (main or master).

    Returns:
        Default branch name.
    """
    try:
        # Try main first (modern default)
        result = subprocess.run(
            ["git", "rev-parse", "--verify", "main"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return "main"

        # Fall back to master
        result = subprocess.run(
            ["git", "rev-parse", "--verify", "master"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return "master"
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    return "main"  # Default to main
