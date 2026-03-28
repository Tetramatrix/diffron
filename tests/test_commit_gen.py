"""Tests for commit message generation."""

import unittest
from unittest.mock import patch, MagicMock

from diffron.commit_gen import (
    generate_commit_message,
    validate_commit_type,
    format_commit_message,
    COMMIT_TYPES,
)


class TestCommitMessageGeneration(unittest.TestCase):
    """Test commit message generation."""

    @patch("diffron.commit_gen.get_staged_diff")
    @patch("diffron.commit_gen.LemonadeClient")
    def test_generate_commit_message(self, mock_client_class, mock_get_diff):
        """Test commit message generation."""
        mock_get_diff.return_value = "diff --git a/file.py b/file.py\n+new code"

        mock_client = MagicMock()
        mock_client.chat_completion.return_value = "feat: add new feature"
        mock_client_class.return_value = mock_client

        result = generate_commit_message()

        self.assertEqual(result, "feat: add new feature")
        mock_get_diff.assert_called_once()
        mock_client.chat_completion.assert_called_once()

    @patch("diffron.commit_gen.get_staged_diff")
    def test_generate_commit_message_empty_diff(self, mock_get_diff):
        """Test commit message generation with empty diff."""
        mock_get_diff.return_value = ""

        with self.assertRaises(ValueError):
            generate_commit_message()

    @patch("diffron.commit_gen.LemonadeClient")
    def test_generate_commit_message_with_custom_diff(self, mock_client_class):
        """Test commit message generation with custom diff."""
        mock_client = MagicMock()
        mock_client.chat_completion.return_value = "fix: resolve bug"
        mock_client_class.return_value = mock_client

        custom_diff = "custom diff content"
        result = generate_commit_message(diff=custom_diff)

        self.assertEqual(result, "fix: resolve bug")

    @patch("diffron.commit_gen.LemonadeClient")
    def test_generate_commit_message_cleans_quotes(self, mock_client_class):
        """Test that generated messages have quotes removed."""
        mock_client = MagicMock()
        mock_client.chat_completion.return_value = '"feat: add feature"'
        mock_client_class.return_value = mock_client

        result = generate_commit_message(diff="diff")

        self.assertEqual(result, "feat: add feature")

    @patch("diffron.commit_gen.LemonadeClient")
    def test_generate_commit_message_cleans_code_blocks(self, mock_client_class):
        """Test that generated messages have code blocks removed."""
        mock_client = MagicMock()
        mock_client.chat_completion.return_value = "```feat: add feature```"
        mock_client_class.return_value = mock_client

        result = generate_commit_message(diff="diff")

        self.assertNotIn("```", result)


class TestValidateCommitType(unittest.TestCase):
    """Test commit type validation."""

    def test_valid_commit_types(self):
        """Test validation of valid commit types."""
        valid_messages = [
            "feat: add new feature",
            "fix: resolve bug",
            "docs: update readme",
            "style: format code",
            "refactor: improve performance",
            "perf: optimize query",
            "test: add unit tests",
            "build: update dependencies",
            "ci: add workflow",
            "chore: clean up",
            "revert: undo last commit",
        ]

        for msg in valid_messages:
            self.assertTrue(validate_commit_type(msg), f"Failed for: {msg}")

    def test_valid_commit_types_with_scope(self):
        """Test validation with scope."""
        valid_messages = [
            "feat(api): add endpoint",
            "fix(ui): resolve layout issue",
            "docs(readme): update installation",
        ]

        for msg in valid_messages:
            self.assertTrue(validate_commit_type(msg), f"Failed for: {msg}")

    def test_invalid_commit_types(self):
        """Test validation of invalid commit types."""
        invalid_messages = [
            "add new feature",
            "bugfix: fix something",
            "update: change stuff",
            "",
        ]

        for msg in invalid_messages:
            self.assertFalse(validate_commit_type(msg), f"Failed for: {msg}")


class TestFormatCommitMessage(unittest.TestCase):
    """Test commit message formatting."""

    def test_format_basic(self):
        """Test basic formatting."""
        result = format_commit_message("feat", "add new feature")
        self.assertEqual(result, "feat: add new feature")

    def test_format_with_scope(self):
        """Test formatting with scope."""
        result = format_commit_message("feat", "add endpoint", scope="api")
        self.assertEqual(result, "feat(api): add endpoint")

    def test_format_breaking(self):
        """Test formatting with breaking change."""
        result = format_commit_message("feat", "change api", breaking=True)
        self.assertEqual(result, "feat!: change api")

    def test_format_with_scope_and_breaking(self):
        """Test formatting with scope and breaking change."""
        result = format_commit_message(
            "feat", "change api", scope="api", breaking=True
        )
        self.assertEqual(result, "feat(api)!: change api")

    def test_all_commit_types(self):
        """Test formatting all commit types."""
        for commit_type in COMMIT_TYPES:
            result = format_commit_message(commit_type, "test description")
            self.assertTrue(result.startswith(f"{commit_type}:"))


if __name__ == "__main__":
    unittest.main()
