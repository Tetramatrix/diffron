"""
Git hooks installation and management for Diffron.

Provides functions to install, uninstall, and verify Diffron Git hooks.
"""

import os
import shutil
import stat
from pathlib import Path
from typing import Optional

from .utils import get_git_dir, is_git_repo


# Hook file names
WRAPPER_NAME = "prepare-commit-msg"
PYTHON_HOOK_NAME = "prepare-commit-msg.py"

# Get the hooks directory (where the template hooks are stored)
DIFFRON_PACKAGE_DIR = Path(__file__).parent
HOOKS_TEMPLATE_DIR = DIFFRON_PACKAGE_DIR / "hooks"


def install_hooks(
    repo_path: str = ".",
    global_install: bool = False,
) -> bool:
    """
    Install Diffron Git hooks to a repository.

    Args:
        repo_path: Path to the git repository. Defaults to current directory.
        global_install: If True, install hooks globally for all repositories.

    Returns:
        True if installation was successful, False otherwise.
    """
    if global_install:
        return _install_global_hooks()

    if not is_git_repo(repo_path):
        raise ValueError(f"Not a git repository: {repo_path}")

    git_dir = get_git_dir(repo_path)
    if git_dir is None:
        raise ValueError(f"Could not find .git directory in: {repo_path}")

    hooks_dir = Path(git_dir) / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)

    # Copy wrapper script
    wrapper_src = HOOKS_TEMPLATE_DIR / WRAPPER_NAME
    wrapper_dst = hooks_dir / WRAPPER_NAME

    if wrapper_src.exists():
        shutil.copy2(wrapper_src, wrapper_dst)
        _make_executable(wrapper_dst)

    # Copy Python hook script
    python_hook_src = HOOKS_TEMPLATE_DIR / PYTHON_HOOK_NAME
    python_hook_dst = hooks_dir / PYTHON_HOOK_NAME

    if python_hook_src.exists():
        shutil.copy2(python_hook_src, python_hook_dst)
        _make_executable(python_hook_dst)

    return True


def _install_global_hooks() -> bool:
    """
    Install hooks globally using git config core.hooksPath.

    Returns:
        True if installation was successful, False otherwise.
    """
    import subprocess

    # Create global hooks directory in user's home
    home_dir = Path.home()
    global_hooks_dir = home_dir / ".diffron-hooks"
    global_hooks_dir.mkdir(parents=True, exist_ok=True)

    # Copy hook files
    wrapper_src = HOOKS_TEMPLATE_DIR / WRAPPER_NAME

    # For global install, use the simplified hook that imports from installed package
    python_hook_src = HOOKS_TEMPLATE_DIR / "prepare-commit-msg-global.py"
    if not python_hook_src.exists():
        # Fallback to regular hook if global version doesn't exist
        python_hook_src = HOOKS_TEMPLATE_DIR / PYTHON_HOOK_NAME

    wrapper_dst = global_hooks_dir / WRAPPER_NAME
    python_hook_dst = global_hooks_dir / PYTHON_HOOK_NAME

    if wrapper_src.exists():
        shutil.copy2(wrapper_src, wrapper_dst)
        _make_executable(wrapper_dst)

    if python_hook_src.exists():
        shutil.copy2(python_hook_src, python_hook_dst)
        _make_executable(python_hook_dst)

    # Configure git to use global hooks path
    hooks_path_str = str(global_hooks_dir).replace("\\", "/")
    try:
        subprocess.run(
            ["git", "config", "--global", "core.hooksPath", hooks_path_str],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return True
    except subprocess.SubprocessError:
        return False


def uninstall_hooks(
    repo_path: str = ".",
    global_install: bool = False,
) -> bool:
    """
    Remove Diffron Git hooks from a repository.

    Args:
        repo_path: Path to the git repository. Defaults to current directory.
        global_install: If True, remove global hooks configuration.

    Returns:
        True if uninstallation was successful, False otherwise.
    """
    import subprocess

    if global_install:
        # Remove global hooks configuration
        try:
            subprocess.run(
                ["git", "config", "--global", "--unset", "core.hooksPath"],
                check=True,
                capture_output=True,
                text=True,
                timeout=10,
            )
        except subprocess.SubprocessError:
            pass  # Config might not be set

        # Remove global hooks directory
        home_dir = Path.home()
        global_hooks_dir = home_dir / ".diffron-hooks"
        if global_hooks_dir.exists():
            try:
                shutil.rmtree(global_hooks_dir)
            except Exception:
                pass
        return True

    if not is_git_repo(repo_path):
        raise ValueError(f"Not a git repository: {repo_path}")

    git_dir = get_git_dir(repo_path)
    if git_dir is None:
        raise ValueError(f"Could not find .git directory in: {repo_path}")

    hooks_dir = Path(git_dir) / "hooks"

    # Remove hook files
    wrapper_path = hooks_dir / WRAPPER_NAME
    python_hook_path = hooks_dir / PYTHON_HOOK_NAME

    removed = False

    if wrapper_path.exists():
        wrapper_path.unlink()
        removed = True

    if python_hook_path.exists():
        python_hook_path.unlink()
        removed = True

    return removed


def is_hooks_installed(
    repo_path: str = ".",
    check_global: bool = False,
) -> bool:
    """
    Check if Diffron hooks are installed.

    Args:
        repo_path: Path to the git repository. Defaults to current directory.
        check_global: If True, check for global hooks configuration.

    Returns:
        True if hooks are installed, False otherwise.
    """
    import subprocess

    if check_global:
        # Check global hooks configuration
        try:
            result = subprocess.run(
                ["git", "config", "--global", "core.hooksPath"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                hooks_path = result.stdout.strip()
                # Check if it's the diffron hooks directory
                if ".diffron-hooks" in hooks_path:
                    return True
        except subprocess.SubprocessError:
            pass
        return False

    if not is_git_repo(repo_path):
        return False

    git_dir = get_git_dir(repo_path)
    if git_dir is None:
        return False

    hooks_dir = Path(git_dir) / "hooks"

    # Check if both hook files exist
    wrapper_path = hooks_dir / WRAPPER_NAME
    python_hook_path = hooks_dir / PYTHON_HOOK_NAME

    return wrapper_path.exists() and python_hook_path.exists()


def _make_executable(path: Path) -> None:
    """
    Make a file executable.

    Args:
        path: Path to the file.
    """
    if os.name == "nt":
        # Windows doesn't use Unix permissions, but we can still set the flag
        pass
    else:
        # Unix-like systems
        current_mode = path.stat().st_mode
        path.chmod(current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def get_hooks_status(repo_path: str = ".") -> dict:
    """
    Get detailed status of hooks installation.

    Args:
        repo_path: Path to the git repository.

    Returns:
        Dict with status information.
    """
    status = {
        "is_git_repo": is_git_repo(repo_path),
        "local_hooks_installed": False,
        "global_hooks_configured": False,
        "wrapper_exists": False,
        "python_hook_exists": False,
        "git_dir": None,
        "hooks_dir": None,
    }

    if status["is_git_repo"]:
        git_dir = get_git_dir(repo_path)
        status["git_dir"] = str(git_dir) if git_dir else None

        if git_dir:
            hooks_dir = Path(git_dir) / "hooks"
            status["hooks_dir"] = str(hooks_dir)

            wrapper_path = hooks_dir / WRAPPER_NAME
            python_hook_path = hooks_dir / PYTHON_HOOK_NAME

            status["wrapper_exists"] = wrapper_path.exists()
            status["python_hook_exists"] = python_hook_path.exists()
            status["local_hooks_installed"] = (
                status["wrapper_exists"] and status["python_hook_exists"]
            )

    status["global_hooks_configured"] = is_hooks_installed(
        repo_path, check_global=True
    )

    return status
