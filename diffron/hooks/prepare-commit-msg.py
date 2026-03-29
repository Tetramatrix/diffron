#!/usr/bin/env python
"""
Diffron prepare-commit-msg Git hook.

Automatically generates commit messages using Lemonade LLM.
Installed globally by Diffron.
"""

import sys
import os
import urllib.request
import urllib.error

# Import diffron from installed package (no path manipulation needed)
from diffron.commit_gen import generate_commit_message
from diffron.lemonade import get_lemonade_url


def is_lemonade_api_responsive(url: str, timeout: float = 10.0) -> bool:
    """
    Check if Lemonade API actually responds (not just port open).

    Args:
        url: Lemonade server URL.
        timeout: Request timeout in seconds (10s to allow for slow startup).

    Returns:
        True if API responds successfully.
    """
    try:
        # Try /api/v1/models endpoint
        models_url = f"{url}/api/v1/models"
        req = urllib.request.Request(models_url)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                return True
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        pass

    # Fallback: try root endpoint
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status == 200
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        pass

    return False


def main():
    """Main hook entry point."""
    # Parse arguments
    if len(sys.argv) < 2:
        print("Error: Missing commit message file argument", file=sys.stderr)
        sys.exit(1)

    commit_msg_file = sys.argv[1]
    commit_source = sys.argv[2] if len(sys.argv) > 2 else ""

    # Skip for merges, rebases, and amend commits
    skip_sources = {"merge", "squash", "commit"}
    if commit_source in skip_sources:
        sys.exit(0)

    # Change to the repository directory (where git commit was run)
    repo_dir = os.path.dirname(os.path.abspath(commit_msg_file))
    # Navigate up from .git/COMMIT_EDITMSG to repo root
    if os.path.basename(repo_dir) == ".git":
        repo_dir = os.path.dirname(repo_dir)
    os.chdir(repo_dir)

    # Get Lemonade URL and check if API is actually responsive
    lemonade_url = get_lemonade_url()
    if not is_lemonade_api_responsive(lemonade_url):
        # Silently exit if Lemonade not responding - let user commit manually
        sys.exit(0)

    try:
        # Generate commit message
        commit_message = generate_commit_message()

        if commit_message:
            # Write to commit message file
            with open(commit_msg_file, "w", encoding="utf-8") as f:
                f.write(commit_message)
    except Exception as e:
        # Log error but don't block commit
        error_msg = f"# Diffron error: {e}\n"
        try:
            with open(commit_msg_file, "a", encoding="utf-8") as f:
                f.write(error_msg)
        except Exception:
            pass
        sys.exit(0)  # Don't block commit on error

    sys.exit(0)


if __name__ == "__main__":
    main()
