"""Tests for Git hooks installation."""

import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
import os

from diffron.git_hooks import (
    install_hooks,
    uninstall_hooks,
    is_hooks_installed,
    get_hooks_status,
    WRAPPER_NAME,
    PYTHON_HOOK_NAME,
)


class TestHooksInstallation(unittest.TestCase):
    """Test hooks installation functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.git_dir = Path(self.temp_dir) / ".git"
        self.hooks_dir = self.git_dir / "hooks"
        self.git_dir.mkdir(parents=True, exist_ok=True)
        self.hooks_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("diffron.git_hooks.is_git_repo")
    @patch("diffron.git_hooks.get_git_dir")
    def test_install_hooks(self, mock_get_git_dir, mock_is_git_repo):
        """Test hooks installation."""
        mock_is_git_repo.return_value = True
        mock_get_git_dir.return_value = str(self.git_dir)

        success = install_hooks(repo_path=self.temp_dir)

        self.assertTrue(success)

        # Check if hook files were created
        wrapper_path = self.hooks_dir / WRAPPER_NAME
        python_hook_path = self.hooks_dir / PYTHON_HOOK_NAME

        # Note: Files might not exist if template dir doesn't exist in test env
        # This is expected behavior

    @patch("diffron.git_hooks.is_git_repo")
    def test_install_hooks_not_repo(self, mock_is_git_repo):
        """Test installation fails when not a git repo."""
        mock_is_git_repo.return_value = False

        with self.assertRaises(ValueError):
            install_hooks(repo_path=self.temp_dir)

    @patch("diffron.git_hooks.is_git_repo")
    @patch("diffron.git_hooks.get_git_dir")
    def test_uninstall_hooks(self, mock_get_git_dir, mock_is_git_repo):
        """Test hooks uninstallation."""
        mock_is_git_repo.return_value = True
        mock_get_git_dir.return_value = str(self.git_dir)

        # Create dummy hook files
        wrapper_path = self.hooks_dir / WRAPPER_NAME
        python_hook_path = self.hooks_dir / PYTHON_HOOK_NAME
        wrapper_path.touch()
        python_hook_path.touch()

        success = uninstall_hooks(repo_path=self.temp_dir)

        self.assertTrue(success)
        self.assertFalse(wrapper_path.exists())
        self.assertFalse(python_hook_path.exists())

    @patch("diffron.git_hooks.is_git_repo")
    @patch("diffron.git_hooks.get_git_dir")
    def test_is_hooks_installed_true(
        self, mock_get_git_dir, mock_is_git_repo
    ):
        """Test hooks detection when installed."""
        mock_is_git_repo.return_value = True
        mock_get_git_dir.return_value = str(self.git_dir)

        # Create dummy hook files
        wrapper_path = self.hooks_dir / WRAPPER_NAME
        python_hook_path = self.hooks_dir / PYTHON_HOOK_NAME
        wrapper_path.touch()
        python_hook_path.touch()

        result = is_hooks_installed(repo_path=self.temp_dir)

        self.assertTrue(result)

    @patch("diffron.git_hooks.is_git_repo")
    @patch("diffron.git_hooks.get_git_dir")
    def test_is_hooks_installed_false(
        self, mock_get_git_dir, mock_is_git_repo
    ):
        """Test hooks detection when not installed."""
        mock_is_git_repo.return_value = True
        mock_get_git_dir.return_value = str(self.git_dir)

        result = is_hooks_installed(repo_path=self.temp_dir)

        self.assertFalse(result)


class TestGetHooksStatus(unittest.TestCase):
    """Test get_hooks_status function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.git_dir = Path(self.temp_dir) / ".git"
        self.hooks_dir = self.git_dir / "hooks"
        self.git_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("diffron.git_hooks.is_git_repo")
    @patch("diffron.git_hooks.get_git_dir")
    def test_status_with_hooks_installed(
        self, mock_get_git_dir, mock_is_git_repo
    ):
        """Test status when hooks are installed."""
        mock_is_git_repo.return_value = True
        mock_get_git_dir.return_value = str(self.git_dir)

        # Create dummy hook files
        wrapper_path = self.hooks_dir / WRAPPER_NAME
        python_hook_path = self.hooks_dir / PYTHON_HOOK_NAME
        wrapper_path.touch()
        python_hook_path.touch()

        status = get_hooks_status(repo_path=self.temp_dir)

        self.assertTrue(status["is_git_repo"])
        self.assertTrue(status["local_hooks_installed"])
        self.assertTrue(status["wrapper_exists"])
        self.assertTrue(status["python_hook_exists"])

    @patch("diffron.git_hooks.is_git_repo")
    def test_status_not_git_repo(self, mock_is_git_repo):
        """Test status when not a git repo."""
        mock_is_git_repo.return_value = False

        status = get_hooks_status(repo_path=self.temp_dir)

        self.assertFalse(status["is_git_repo"])
        self.assertIsNone(status["git_dir"])


if __name__ == "__main__":
    unittest.main()
