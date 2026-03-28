"""Tests for Lemonade integration."""

import unittest
from unittest.mock import patch, MagicMock
import socket

from diffron.lemonade import (
    detect_lemonade_port,
    is_lemonade_running,
    LemonadeClient,
    DEFAULT_HOST,
    DEFAULT_PORTS,
)


class TestPortDetection(unittest.TestCase):
    """Test port detection functions."""

    @patch("diffron.lemonade.is_port_open")
    def test_detect_lemonade_port_from_env(self, mock_is_port_open):
        """Test port detection from environment variable."""
        mock_is_port_open.return_value = True

        with patch.dict("os.environ", {"DIFFRON_LEMONADE_PORT": "8000"}):
            port = detect_lemonade_port()
            self.assertEqual(port, 8000)

    @patch("diffron.lemonade.scan_ports")
    def test_detect_lemonade_port_scanning(self, mock_scan_ports):
        """Test port detection by scanning."""
        mock_scan_ports.return_value = [8000, 8001]

        port = detect_lemonade_port()
        self.assertEqual(port, 8000)

    @patch("diffron.lemonade.scan_ports")
    def test_detect_lemonade_port_not_found(self, mock_scan_ports):
        """Test when no Lemonade port is found."""
        mock_scan_ports.return_value = []

        port = detect_lemonade_port()
        self.assertIsNone(port)

    @patch("diffron.lemonade.is_port_open")
    def test_is_lemonade_running_true(self, mock_is_port_open):
        """Test is_lemonade_running when server is up."""
        mock_is_port_open.return_value = True

        result = is_lemonade_running(port=8000)
        self.assertTrue(result)

    @patch("diffron.lemonade.is_port_open")
    def test_is_lemonade_running_false(self, mock_is_port_open):
        """Test is_lemonade_running when server is down."""
        mock_is_port_open.return_value = False

        result = is_lemonade_running(port=8000)
        self.assertFalse(result)


class TestLemonadeClient(unittest.TestCase):
    """Test LemonadeClient class."""

    @patch("diffron.lemonade.detect_lemonade_port")
    @patch("diffron.lemonade.OpenAI")
    def test_client_initialization(self, mock_openai, mock_detect_port):
        """Test client initialization."""
        mock_detect_port.return_value = 8000
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        client = LemonadeClient()

        self.assertEqual(client.host, DEFAULT_HOST)
        self.assertEqual(client.port, 8000)
        self.assertEqual(client.api_key, "lemonade")

    @patch("diffron.lemonade.detect_lemonade_port")
    def test_client_initialization_no_lemonade(self, mock_detect_port):
        """Test client initialization fails when Lemonade not running."""
        mock_detect_port.return_value = None

        with self.assertRaises(ConnectionError):
            LemonadeClient()

    @patch("diffron.lemonade.detect_lemonade_port")
    @patch("diffron.lemonade.OpenAI")
    def test_chat_completion(self, mock_openai, mock_detect_port):
        """Test chat completion."""
        mock_detect_port.return_value = 8000
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response

        client = LemonadeClient()
        result = client.chat_completion(
            messages=[{"role": "user", "content": "Hello"}]
        )

        self.assertEqual(result, "Test response")
        mock_client.chat.completions.create.assert_called_once()

    def test_client_repr(self):
        """Test client string representation."""
        with patch("diffron.lemonade.detect_lemonade_port", return_value=8000):
            with patch("diffron.lemonade.OpenAI"):
                client = LemonadeClient()
                repr_str = repr(client)
                self.assertIn("LemonadeClient", repr_str)
                self.assertIn("8000", repr_str)


if __name__ == "__main__":
    unittest.main()
