"""
Command-line interface for Diffron.

Provides CLI entry points for installing hooks, generating PRs, and checking status.
"""

import argparse
import sys
from typing import Optional


def install_hooks_cli():
    """CLI entry point for installing Git hooks."""
    parser = argparse.ArgumentParser(
        description="Install Diffron Git hooks to a repository."
    )
    parser.add_argument(
        "--global",
        dest="global_install",
        action="store_true",
        help="Install hooks globally for all repositories.",
    )
    parser.add_argument(
        "--repo",
        "-r",
        type=str,
        default=".",
        help="Path to the git repository (default: current directory).",
    )

    args = parser.parse_args()

    from .git_hooks import install_hooks

    try:
        success = install_hooks(
            repo_path=args.repo,
            global_install=args.global_install,
        )
        if success:
            if args.global_install:
                print("Diffron hooks installed globally for all repositories.")
            else:
                print(f"Diffron hooks installed to: {args.repo}")
            sys.exit(0)
        else:
            print("Failed to install hooks.", file=sys.stderr)
            sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def uninstall_hooks_cli():
    """CLI entry point for uninstalling Git hooks."""
    parser = argparse.ArgumentParser(
        description="Remove Diffron Git hooks from a repository."
    )
    parser.add_argument(
        "--global",
        dest="global_install",
        action="store_true",
        help="Remove global hooks configuration.",
    )
    parser.add_argument(
        "--repo",
        "-r",
        type=str,
        default=".",
        help="Path to the git repository (default: current directory).",
    )

    args = parser.parse_args()

    from .git_hooks import uninstall_hooks

    try:
        success = uninstall_hooks(
            repo_path=args.repo,
            global_install=args.global_install,
        )
        if success:
            if args.global_install:
                print("Diffron global hooks configuration removed.")
            else:
                print(f"Diffron hooks removed from: {args.repo}")
            sys.exit(0)
        else:
            print("No hooks found to remove.", file=sys.stderr)
            sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def pr_description_cli():
    """CLI entry point for generating PR descriptions."""
    parser = argparse.ArgumentParser(
        description="Generate GitHub PR title and description."
    )
    parser.add_argument(
        "--branch",
        "-b",
        type=str,
        default=None,
        help="Branch to analyze (default: current branch).",
    )
    parser.add_argument(
        "--base",
        type=str,
        default=None,
        help="Base branch to compare against (default: main/master).",
    )
    parser.add_argument(
        "--create",
        "-c",
        action="store_true",
        help="Automatically create PR on GitHub (requires gh CLI).",
    )

    args = parser.parse_args()

    from .pr_gen import generate_pr_description, create_github_pr
    from .lemonade import is_lemonade_running

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
        if args.create:
            pr = create_github_pr(
                branch=args.branch,
                base=args.base,
                auto_submit=True,
            )
            print("PR created successfully!")
        else:
            pr = generate_pr_description(
                branch=args.branch,
                base=args.base,
            )
            print(pr.format_output())
        sys.exit(0)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ConnectionError as e:
        print(f"Connection error: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nCancelled.", file=sys.stderr)
        sys.exit(130)


def status_cli():
    """CLI entry point for checking Lemonade and hooks status."""
    parser = argparse.ArgumentParser(
        description="Check Diffron status (Lemonade connection, hooks installation)."
    )
    parser.add_argument(
        "--repo",
        "-r",
        type=str,
        default=".",
        help="Path to the git repository (default: current directory).",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed status information.",
    )

    args = parser.parse_args()

    from .lemonade import detect_lemonade_port, is_lemonade_running
    from .git_hooks import get_hooks_status, is_hooks_installed

    # Check Lemonade status
    print("Lemonade Server:")
    if is_lemonade_running():
        port = detect_lemonade_port()
        print(f"  ✓ Running on port {port}")
    else:
        print("  ✗ Not running")
        print("    Start with: lemonade serve")

    # Check hooks status
    print("\nGit Hooks:")

    if args.verbose:
        status = get_hooks_status(args.repo)
        print(f"  Is git repo: {status['is_git_repo']}")
        if status['git_dir']:
            print(f"  Git directory: {status['git_dir']}")
        if status['hooks_dir']:
            print(f"  Hooks directory: {status['hooks_dir']}")
        print(f"  Wrapper exists: {status['wrapper_exists']}")
        print(f"  Python hook exists: {status['python_hook_exists']}")
        print(f"  Local hooks installed: {status['local_hooks_installed']}")
        print(f"  Global hooks configured: {status['global_hooks_configured']}")
    else:
        local_installed = is_hooks_installed(args.repo, check_global=False)
        global_configured = is_hooks_installed(args.repo, check_global=True)

        if local_installed:
            print(f"  ✓ Installed locally ({args.repo})")
        elif global_configured:
            print("  ✓ Installed globally")
        else:
            print("  ✗ Not installed")
            print("    Install with: diffron-install-hooks")

    sys.exit(0)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Diffron - AI-powered Git automation with Lemonade",
        prog="diffron",
    )
    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version="%(prog)s 0.1.3",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Install hooks command
    install_parser = subparsers.add_parser(
        "install-hooks",
        help="Install Git hooks to a repository",
    )
    install_parser.add_argument(
        "--global",
        dest="global_install",
        action="store_true",
        help="Install hooks globally for all repositories.",
    )
    install_parser.add_argument(
        "--repo",
        "-r",
        type=str,
        default=".",
        help="Path to the git repository (default: current directory).",
    )

    # Uninstall hooks command
    uninstall_parser = subparsers.add_parser(
        "uninstall-hooks",
        help="Remove Git hooks from a repository",
    )
    uninstall_parser.add_argument(
        "--global",
        dest="global_install",
        action="store_true",
        help="Remove global hooks configuration.",
    )
    uninstall_parser.add_argument(
        "--repo",
        "-r",
        type=str,
        default=".",
        help="Path to the git repository (default: current directory).",
    )

    # PR command
    pr_parser = subparsers.add_parser(
        "pr",
        help="Generate PR title and description",
    )
    pr_parser.add_argument(
        "--branch",
        "-b",
        type=str,
        default=None,
        help="Branch to analyze (default: current branch).",
    )
    pr_parser.add_argument(
        "--base",
        type=str,
        default=None,
        help="Base branch to compare against (default: main/master).",
    )
    pr_parser.add_argument(
        "--create",
        "-c",
        action="store_true",
        help="Automatically create PR on GitHub (requires gh CLI).",
    )

    # Status command
    status_parser = subparsers.add_parser(
        "status",
        help="Check Diffron status",
    )
    status_parser.add_argument(
        "--repo",
        "-r",
        type=str,
        default=".",
        help="Path to the git repository (default: current directory).",
    )
    status_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed status information.",
    )

    args = parser.parse_args()

    if args.command == "install-hooks":
        install_hooks_cli()
    elif args.command == "uninstall-hooks":
        uninstall_hooks_cli()
    elif args.command == "pr":
        pr_description_cli()
    elif args.command == "status":
        status_cli()
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
