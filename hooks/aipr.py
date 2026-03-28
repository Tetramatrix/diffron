#!/usr/bin/env python
"""
Diffron PR Description Generator (aipr).

Generates GitHub PR title and description from branch changes.
Run this script manually when ready to create a PR.

Usage:
    python aipr.py [branch] [base]

    branch: Branch to analyze (default: current branch)
    base: Base branch to compare against (default: main/master)

Example:
    python aipr.py feature/my-feature main
"""

import sys
import os
import subprocess

# Add parent directory to path to import diffron
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from diffron.pr_gen import generate_pr_description, create_github_pr
from diffron.lemonade import is_lemonade_running


def check_gh_cli() -> bool:
    """Check if GitHub CLI is available."""
    try:
        result = subprocess.run(
            ["gh", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def main():
    """Main entry point."""
    # Parse arguments
    branch = sys.argv[1] if len(sys.argv) > 1 else None
    base = sys.argv[2] if len(sys.argv) > 2 else None

    # Check if Lemonade is running
    if not is_lemonade_running():
        print(
            "Error: Lemonade server is not running.",
            file=sys.stderr
        )
        print(
            "Please start Lemonade first (e.g., 'lemonade serve').",
            file=sys.stderr
        )
        sys.exit(1)

    try:
        # Generate PR description
        print("Analyzing branch changes...")
        pr = generate_pr_description(branch=branch, base=base)

        # Output result
        print("\n" + "=" * 60)
        print(pr.format_output())
        print("=" * 60 + "\n")

        # Check if gh CLI is available
        if check_gh_cli():
            response = input("Create PR on GitHub now? (y/n): ").strip().lower()
            if response in ("y", "yes"):
                print("Creating PR...")
                create_github_pr(branch=branch, base=base, auto_submit=True)
                print("PR created successfully!")
        else:
            print(
                "Tip: Install GitHub CLI (gh) to auto-create PRs: "
                "https://cli.github.com/"
            )

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ConnectionError as e:
        print(f"Connection error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)


if __name__ == "__main__":
    main()
