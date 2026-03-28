"""Tests for utility functions."""

import unittest
from unittest.mock import patch, MagicMock
import socket
import subprocess

from diffron.utils import (
    scan_ports,
    is_port_open,
    get_staged_diff,
    get_branch_diff,
    get_commit_log,
    get_current_branch,
    is_git_repo,
    get_git_dir,
    find_default_branch,
    COMMON_PORTS,
)


class TestPortScanning(unittest.TestCase):
    """Test port scanning functions."""

    @patch("diffron.utils.is_port_open")
    def test_scan_ports(self, mock_is_port_open):
        """Test scanning multiple ports."""
        mock_is_port_open.side_effect = [True, False, True]

        ports = [8000, 8001, 8080]
        result = scan_ports(ports=ports)

        self.assertEqual(result, [8000, 8080])

    @patch("diffron.utils.is_port_open")
    def test_scan_ports_default(self, mock_is_port_open):
        """Test scanning with default ports."""
        mock_is_port_open.return_value = False

        result = scan_ports()

        self.assertEqual(result, [])
        self.assertEqual(len(mock_is_port_open.call_args_list), len(COMMON_PORTS))

    @patch("socket.create_connection")
    def test_is_port_open_true(self, mock_create_connection):
        """Test port open detection when port is open."""
        mock_create_connection.return_value = MagicMock()

        result = is_port_open("localhost", 8000)

        self.assertTrue(result)
        mock_create_connection.assert_called_once_with(("localhost", 8000), timeout=1.0)

    @patch("socket.create_connection")
    def test_is_port_open_false(self, mock_create_connection):
        """Test port open detection when port is closed."""
        mock_create_connection.side_effect = ConnectionRefusedError()

        result = is_port_open("localhost", 8000)

        self.assertFalse(result)

    @patch("socket.create_connection")
    def test_is_port_open_timeout(self, mock_create_connection):
        """Test port open detection with timeout."""
        mock_create_connection.side_effect = socket.timeout()

        result = is_port_open("localhost", 8000)

        self.assertFalse(result)


class TestGitOperations(unittest.TestCase):
    """Test Git operation functions."""

    @patch("subprocess.run")
    def test_get_staged_diff(self, mock_run):
        """Test getting staged diff."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="diff --git a/file.py b/file.py\n+new code"
        )

        result = get_staged_diff()

        self.assertIn("diff --git", result)
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_get_staged_diff_truncated(self, mock_run):
        """Test that diff is truncated to max_chars."""
        long_diff = "x" * 5000
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=long_diff
        )

        result = get_staged_diff(max_chars=1000)

        self.assertEqual(len(result), 1000)

    @patch("subprocess.run")
    def test_get_staged_diff_error(self, mock_run):
        """Test getting staged diff on error."""
        mock_run.side_effect = subprocess.SubprocessError()

        result = get_staged_diff()

        self.assertEqual(result, "")

    @patch("subprocess.run")
    def test_get_branch_diff(self, mock_run):
        """Test getting branch diff."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="diff content"
        )

        result = get_branch_diff("feature", "main")

        self.assertEqual(result, "diff content")
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_get_commit_log(self, mock_run):
        """Test getting commit log."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="abc123 Commit message\n"
        )

        result = get_commit_log("feature", "main")

        self.assertIn("abc123", result)

    @patch("subprocess.run")
    def test_get_current_branch(self, mock_run):
        """Test getting current branch."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="feature/test\n"
        )

        result = get_current_branch()

        self.assertEqual(result, "feature/test")

    @patch("subprocess.run")
    def test_get_current_branch_not_repo(self, mock_run):
        """Test getting current branch when not in repo."""
        mock_run.side_effect = FileNotFoundError()

        result = get_current_branch()

        self.assertIsNone(result)

    @patch("subprocess.run")
    def test_is_git_repo_true(self, mock_run):
        """Test git repo detection when is repo."""
        mock_run.return_value = MagicMock(returncode=0)

        result = is_git_repo()

        self.assertTrue(result)

    @patch("subprocess.run")
    def test_is_git_repo_false(self, mock_run):
        """Test git repo detection when not repo."""
        mock_run.return_value = MagicMock(returncode=128)

        result = is_git_repo()

        self.assertFalse(result)

    @patch("subprocess.run")
    def test_get_git_dir(self, mock_run):
        """Test getting git directory."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=".git\n"
        )

        with patch("os.path.isabs", return_value=False):
            with patch("os.path.abspath", return_value="/abs/path/.git"):
                result = get_git_dir()

                self.assertEqual(result, "/abs/path/.git")

    @patch("subprocess.run")
    def test_find_default_branch_main(self, mock_run):
        """Test finding default branch (main)."""
        mock_run.return_value = MagicMock(returncode=0)

        result = find_default_branch()

        self.assertEqual(result, "main")

    @patch("subprocess.run")
    def test_find_default_branch_master(self, mock_run):
        """Test finding default branch (master)."""
        # main doesn't exist, master does
        mock_run.side_effect = [
            MagicMock(returncode=128),  # main
            MagicMock(returncode=0),     # master
        ]

        result = find_default_branch()

        self.assertEqual(result, "master")

    @patch("subprocess.run")
    def test_find_default_branch_fallback(self, mock_run):
        """Test default branch fallback to main."""
        mock_run.side_effect = subprocess.SubprocessError()

        result = find_default_branch()

        self.assertEqual(result, "main")


if __name__ == "__main__":
    unittest.main()
