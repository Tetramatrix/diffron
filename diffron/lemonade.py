"""Lemonade integration for Diffron.

Provides automatic port detection and API client for Lemonade LLM server.
"""

import os
import typing
from typing import Optional, List
from urllib.parse import urlparse

import openai
from openai import OpenAI

from .utils import is_port_open

# Import lemonade-python-sdk for verification
try:
    from lemonade_sdk.port_scanner import verify_lemonade_server
    from lemonade_sdk.port_scanner import find_available_lemonade_port
    HAS_LEMONADE_SDK = True
except ImportError:
    HAS_LEMONADE_SDK = False

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8020  # Default Lemonade port
DEFAULT_PORTS = [8020, 8000, 8001, 8080, 8081, 5000, 5001]
LEMONADE_API_KEY = "lemonade"  # Default API key for Lemonade
DEFAULT_MODEL = "qwen2.5-it-3b-FLM"  # Default Lemonade model


def detect_lemonade_port(
    host: Optional[str] = None,
    ports: Optional[List[int]] = None
) -> Optional[int]:
    """Auto-detect port for running Lemonade server.

    Uses lemonade-python-sdk's verify_lemonade_server to distinguish
    Lemonade from other services (e.g., Axo Biomarker on port 8000).

    Args:
        host: Host to check. Defaults to DIFFRON_LEMONADE_HOST or localhost.
        ports: List of ports to scan. Defaults to common Lemonade ports.

    Returns:
        Port number if found, None otherwise.
    """
    # Check LEMONADE_SERVER_URL environment variable first (standard Lemonade env)
    server_url = os.environ.get("LEMONADE_SERVER_URL")
    if server_url:
        from urllib.parse import urlparse
        parsed = urlparse(server_url)
        port = parsed.port
        hostname = parsed.hostname or DEFAULT_HOST
        # Verify it's actually Lemonade
        if HAS_LEMONADE_SDK and verify_lemonade_server(port, hostname):
            return port
        elif is_port_open(hostname, port):
            return port

    # Check DIFFRON_LEMONADE_PORT (Diffron-specific)
    env_port = os.environ.get("DIFFRON_LEMONADE_PORT")
    if env_port:
        try:
            port = int(env_port)
            hostname = host or DEFAULT_HOST
            if HAS_LEMONADE_SDK and verify_lemonade_server(port, hostname):
                return port
            elif is_port_open(hostname, port):
                return port
        except ValueError:
            pass

    # Use lemonade-python-sdk's find_available_lemonade_port
    if HAS_LEMONADE_SDK:
        hostname = host or os.environ.get("DIFFRON_LEMONADE_HOST", DEFAULT_HOST)
        scan_ports = ports or DEFAULT_PORTS
        found = find_available_lemonade_port(hostname, scan_ports)
        if found:
            return found

    # Fallback: manual scan verification
    hostname = host or os.environ.get("DIFFRON_LEMONADE_HOST", DEFAULT_HOST)
    ports_to_scan = ports or DEFAULT_PORTS
    for port in ports_to_scan:
        if is_port_open(hostname, port):
            if HAS_LEMONADE_SDK and verify_lemonade_server(port, hostname):
                return port
    # Without SDK, return first open port (legacy behavior)
    return None


def get_lemonade_url() -> str:
    """Get Lemonade server URL from environment or default.

    Returns:
        Lemonade server URL.
    """
    # Check LEMONADE_SERVER_URL first (standard)
    server_url = os.environ.get("LEMONADE_SERVER_URL")
    if server_url:
        return server_url.strip().rstrip("/")

    # Build URL from host/port
    host = os.environ.get("DIFFRON_LEMONADE_HOST", DEFAULT_HOST)
    port = detect_lemonade_port(host)
    if port:
        return f"http://{host}:{port}"

    # Fallback to default
    return f"http://{DEFAULT_HOST}:{DEFAULT_PORT}"


def is_lemonade_running(
    host: Optional[str] = None,
    port: Optional[int] = None
) -> bool:
    """Check if Lemonade is running.

    Args:
        host: Host to check. Defaults to DIFFRON_LEMONADE_HOST or localhost.
        port: Port to check. Auto-detects if not provided.

    Returns:
        True if Lemonade is running, False otherwise.
    """
    if port is None:
        port = detect_lemonade_port(host)
    if port is None:
        return False

    host = host or os.environ.get("DIFFRON_LEMONADE_HOST", DEFAULT_HOST)
    return is_port_open(host, port)


class LemonadeClient:
    """Client for interacting with Lemonade LLM server.

    Detects running Lemonade instance and provides a convenient
    interface for chat completions.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> None:
        """Initialize Lemonade client.

        Args:
            base_url: Lemonade server URL. Auto-detects from
                      LEMONADE_SERVER_URL, defaults to http://localhost:8020.
            api_key: API key. Defaults to "lemonade".
            model: Model name. Defaults to qwen2.5-it-3b-FLM.
        """
        # Get base URL from parameter or environment default
        self.base_url = (base_url or get_lemonade_url()).rstrip("/")
        # Parse host and port from base_url
        parsed = urlparse(self.base_url)
        self.host = parsed.hostname or DEFAULT_HOST
        self.port = parsed.port or DEFAULT_PORT
        self.api_key = api_key or LEMONADE_API_KEY
        # Model: parameter > environment > default
        self.model = model or os.environ.get("DIFFRON_MODEL") or DEFAULT_MODEL
        self._port = self.port  # Track current port for reload
        self.client = OpenAI(
            base_url=f"{self.base_url}/api/v1",
            api_key=self.api_key
        )

    def chat_completion(
        self,
        messages: List[dict],
        max_tokens: int = 100,
        temperature: float = 0.2,
        **kwargs
    ) -> str:
        """Generate chat completion.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.
            **kwargs: Additional arguments to pass to the API.

        Returns:
            Generated response content.

        Raises:
            RuntimeError: If model fails after retry attempts.
        """
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs
                )
                # Handle None response (model unresponsive)
                if response is None or not response.choices:
                    if attempt < max_retries:
                        self._reload_model()
                        continue
                    raise RuntimeError("Lemonade model returned no response")
                return response.choices[0].message.content
            except Exception as e:
                if attempt < max_retries:
                    self._reload_model()
                    continue
                raise RuntimeError(
                    f"Lemonade model failed after {max_retries} attempts: {e}"
                )

    def _reload_model(self) -> None:
        """Unload and reload the Lemonade model when unresponsive.

        Uses lemonade-python-sdk to detect and reconnect to the
        Lemonade server, which triggers a model reload.
        """
        try:
            if HAS_LEMONADE_SDK:
                # Find available port (triggers unload/reload via SDK)
                new_port = find_available_lemonade_port(
                    hostname=self.host or DEFAULT_HOST,
                    ports=DEFAULT_PORTS
                )
                if new_port and new_port != self._port:
                    self._port = new_port
                    self.port = new_port  # Update the port attribute
                    # Rebuild the base_url with the new port and the same host
                    self.base_url = f"http://{self.host}:{new_port}"
                    # Reinitialize client with new base_url
                    self._init_client()
        except Exception:
            # Silently continue on reload failure
            pass

    def _init_client(self) -> None:
        """Reinitialize the OpenAI client with current configuration."""
        self.client = OpenAI(
            base_url=f"{self.base_url}/api/v1",
            api_key=self.api_key
        )

    def __repr__(self) -> str:
        return f"LemonadeClient(base_url='{self.base_url}', model='{self.model}')"
