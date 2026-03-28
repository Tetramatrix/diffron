"""
PR description generation for Diffron.

Generates PR titles and descriptions from branch diffs.
"""

import os
from dataclasses import dataclass
from typing import Optional, Tuple

from .lemonade import LemonadeClient
from .utils import get_branch_diff, get_commit_log, get_current_branch, find_default_branch


DEFAULT_MAX_CHARS = 5000
DEFAULT_MAX_TOKENS = 300
DEFAULT_TEMPERATURE = 0.3


@dataclass
class PRDescription:
    """Represents a generated PR title and description."""

    title: str
    description: str

    def format_output(self) -> str:
        """
        Format as TITLE + DESCRIPTION output.

        Returns:
            Formatted string with TITLE and DESCRIPTION sections.
        """
        return f"TITLE: {self.title}\n\nDESCRIPTION:\n{self.description}"

    def to_github_cli(self) -> Tuple[str, str]:
        """
        Get title and body for GitHub CLI.

        Returns:
            Tuple of (title, body).
        """
        return self.title, self.description


def generate_pr_description(
    branch: Optional[str] = None,
    base: Optional[str] = None,
    max_chars: Optional[int] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    client: Optional[LemonadeClient] = None,
) -> PRDescription:
    """
    Generate a PR title and description from branch changes.

    Args:
        branch: Branch name to analyze. Defaults to current branch.
        base: Base branch to compare against. Defaults to main/master.
        max_chars: Maximum characters of diff to send. Defaults to 5000.
        max_tokens: Maximum tokens to generate. Defaults to 300.
        temperature: Sampling temperature. Defaults to 0.3.
        client: LemonadeClient instance. Creates new one if not provided.

    Returns:
        PRDescription with generated title and description.

    Raises:
        ValueError: If no differences found between branches.
        ConnectionError: If Lemonade is not running.
    """
    max_chars = max_chars or int(os.environ.get("DIFFRON_MAX_DIFF_CHARS", DEFAULT_MAX_CHARS))
    max_tokens = max_tokens or DEFAULT_MAX_TOKENS
    temperature = temperature if temperature is not None else DEFAULT_TEMPERATURE

    # Get branch name if not provided
    if branch is None:
        branch = get_current_branch()
        if branch is None:
            raise ValueError("Not in a git repository or no current branch.")

    # Get base branch if not provided
    if base is None:
        base = find_default_branch()

    # Get commit log and diff
    commit_log = get_commit_log(branch, base)
    diff = get_branch_diff(branch, base, max_chars=max_chars)

    if not diff.strip() and not commit_log.strip():
        raise ValueError(f"No differences found between {base} and {branch}.")

    # Create client if not provided
    if client is None:
        client = LemonadeClient()

    # Build prompt
    prompt = (
        "Generate a GitHub PR title and description based on these changes.\n"
        "Format strictly as:\n"
        "TITLE: <concise, descriptive title>\n"
        "DESCRIPTION: <detailed description with bullet points>\n\n"
        "Requirements:\n"
        "- TITLE should be under 80 characters\n"
        "- DESCRIPTION should summarize the main changes\n"
        "- Use bullet points for key changes\n"
        "- Mention any breaking changes if applicable\n\n"
    )

    if commit_log:
        prompt += f"Commits:\n{commit_log}\n\n"

    if diff:
        prompt += f"Diff:\n{diff}"

    messages = [{"role": "user", "content": prompt}]

    # Generate completion
    response = client.chat_completion(
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    # Parse response
    title, description = _parse_pr_response(response)

    return PRDescription(title=title, description=description)


def _parse_pr_response(response: str) -> Tuple[str, str]:
    """
    Parse PR response into title and description.

    Args:
        response: Raw response from LLM.

    Returns:
        Tuple of (title, description).
    """
    lines = response.strip().split("\n")

    title = ""
    description_lines = []
    in_description = False

    for line in lines:
        if line.startswith("TITLE:"):
            title = line.replace("TITLE:", "").strip()
        elif line.startswith("DESCRIPTION:"):
            in_description = True
            desc_part = line.replace("DESCRIPTION:", "").strip()
            if desc_part:
                description_lines.append(desc_part)
        elif in_description:
            description_lines.append(line)

    # Fallback: if no TITLE found, use first line
    if not title and lines:
        title = lines[0].strip()
        description_lines = lines[1:]

    # Fallback: if no DESCRIPTION found, use remaining lines
    if not description_lines and len(lines) > 1:
        description_lines = lines[1:]

    description = "\n".join(description_lines).strip()

    # Clean up markdown code blocks
    if description.startswith("```"):
        lines = description.split("\n")
        description = "\n".join(
            line for line in lines
            if not line.startswith("```")
        ).strip()

    return title, description


def create_github_pr(
    branch: Optional[str] = None,
    base: Optional[str] = None,
    auto_submit: bool = False,
) -> PRDescription:
    """
    Generate PR and optionally create it via GitHub CLI.

    Args:
        branch: Branch name. Defaults to current branch.
        base: Base branch. Defaults to main/master.
        auto_submit: If True, creates PR via gh CLI automatically.

    Returns:
        Generated PRDescription.

    Raises:
        RuntimeError: If gh CLI is not available when auto_submit=True.
    """
    import subprocess

    # Generate PR description
    pr = generate_pr_description(branch=branch, base=base)

    if auto_submit:
        # Check if gh CLI is available
        try:
            result = subprocess.run(
                ["gh", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                raise RuntimeError("GitHub CLI (gh) is not installed or not in PATH.")
        except FileNotFoundError:
            raise RuntimeError("GitHub CLI (gh) is not installed or not in PATH.")

        # Create PR
        subprocess.run(
            ["gh", "pr", "create", "--title", pr.title, "--body", pr.description],
            timeout=60,
        )

    return pr
