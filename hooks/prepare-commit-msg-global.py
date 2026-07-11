#!/usr/bin/env python
"""
Diffron prepare-commit-msg Git hook.

Automatically generates commit messages using Lemonade LLM.
Installed globally by Diffron.
"""

import sys
import os

# Import diffron from installed package (no path manipulation needed)
from diffron.commit_gen import generate_commit_message
from diffron.lemonade import is_lemonade_running


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

    # Skip if the existing message is already well-formed
    if commit_source == "message":
        try:
            from diffron.agent_detect import is_well_formed_commit
            with open(commit_msg_file, "r", encoding="utf-8") as f:
                existing_msg = f.read().strip()
            if existing_msg and is_well_formed_commit(existing_msg):
                sys.exit(0)
        except Exception:
            pass

    # Check if Lemonade is running
    if not is_lemonade_running():
        # Silently exit if Lemonade not running - let user commit manually
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
