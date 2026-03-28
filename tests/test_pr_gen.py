"""Tests for PR description generation."""

import unittest
from unittest.mock import patch, MagicMock

from diffron.pr_gen import (
    generate_pr_description,
    PRDescription,
    _parse_pr_response,
)


class TestPRDescription(unittest.TestCase):
    """Test PRDescription dataclass."""

    def test_format_output(self):
        """Test format_output method."""
        pr = PRDescription(title="Test Title", description="Test description")
        output = pr.format_output()

        self.assertIn("TITLE: Test Title", output)
        self.assertIn("DESCRIPTION:\nTest description", output)

    def test_to_github_cli(self):
        """Test to_github_cli method."""
        pr = PRDescription(title="Test Title", description="Test description")
        title, body = pr.to_github_cli()

        self.assertEqual(title, "Test Title")
        self.assertEqual(body, "Test description")


class TestParsePRResponse(unittest.TestCase):
    """Test PR response parsing."""

    def test_parse_standard_format(self):
        """Test parsing standard TITLE/DESCRIPTION format."""
        response = """TITLE: Add new feature
DESCRIPTION:
This PR adds a new feature.

- Implemented feature X
- Added tests
- Updated docs"""

        title, description = _parse_pr_response(response)

        self.assertEqual(title, "Add new feature")
        self.assertIn("This PR adds a new feature", description)

    def test_parse_multiline_description(self):
        """Test parsing multiline description."""
        response = """TITLE: Fix bug
DESCRIPTION:
Line 1
Line 2
Line 3"""

        title, description = _parse_pr_response(response)

        self.assertEqual(title, "Fix bug")
        self.assertIn("Line 1", description)
        self.assertIn("Line 2", description)
        self.assertIn("Line 3", description)

    def test_parse_fallback_title(self):
        """Test fallback when TITLE prefix missing."""
        response = """First line as title
Second line as description"""

        title, description = _parse_pr_response(response)

        self.assertEqual(title, "First line as title")
        self.assertEqual(description, "Second line as description")

    def test_parse_removes_code_blocks(self):
        """Test that code blocks are removed."""
        response = """TITLE: Test
DESCRIPTION:
```
Some code block
```
More description"""

        title, description = _parse_pr_response(response)

        self.assertNotIn("```", description)


class TestGeneratePRDescription(unittest.TestCase):
    """Test PR description generation."""

    @patch("diffron.pr_gen.get_current_branch")
    @patch("diffron.pr_gen.find_default_branch")
    @patch("diffron.pr_gen.get_commit_log")
    @patch("diffron.pr_gen.get_branch_diff")
    @patch("diffron.pr_gen.LemonadeClient")
    def test_generate_pr_description(
        self, mock_client_class, mock_get_diff, mock_get_log,
        mock_find_branch, mock_get_branch
    ):
        """Test PR description generation."""
        mock_get_branch.return_value = "feature/test"
        mock_find_branch.return_value = "main"
        mock_get_log.return_value = "abc123 Add feature"
        mock_get_diff.return_value = "diff content"

        mock_client = MagicMock()
        mock_client.chat_completion.return_value = (
            "TITLE: Add feature\nDESCRIPTION: This adds a feature"
        )
        mock_client_class.return_value = mock_client

        pr = generate_pr_description()

        self.assertEqual(pr.title, "Add feature")
        self.assertEqual(pr.description, "This adds a feature")

    @patch("diffron.pr_gen.get_current_branch")
    @patch("diffron.pr_gen.find_default_branch")
    @patch("diffron.pr_gen.get_commit_log")
    @patch("diffron.pr_gen.get_branch_diff")
    def test_generate_pr_description_no_changes(
        self, mock_get_diff, mock_get_log, mock_find_branch, mock_get_branch
    ):
        """Test PR generation with no changes."""
        mock_get_branch.return_value = "feature/test"
        mock_find_branch.return_value = "main"
        mock_get_log.return_value = ""
        mock_get_diff.return_value = ""

        with self.assertRaises(ValueError):
            generate_pr_description()

    @patch("diffron.pr_gen.LemonadeClient")
    def test_generate_pr_description_custom_branches(
        self, mock_client_class
    ):
        """Test PR generation with custom branches."""
        mock_client = MagicMock()
        mock_client.chat_completion.return_value = (
            "TITLE: Custom PR\nDESCRIPTION: Custom description"
        )
        mock_client_class.return_value = mock_client

        pr = generate_pr_description(branch="develop", base="staging")

        self.assertEqual(pr.title, "Custom PR")


if __name__ == "__main__":
    unittest.main()
