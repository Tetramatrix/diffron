"""
Lemonade integration for Diffron.

Provides automatic port detection and API client for Lemonade LLM server.
"""

import os
from typing import Optional, List
from openai import OpenAI

from .utils import scan_ports, is_port_open


DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8020  # Default Lemonade port
DEFAULT_PORTS = [8020, 8000, 8001, 8080, 8081, 5000, 5001]
LEMONADE_API_KEY = "lemonade"  # Default API key for Lemonade
DEFAULT_MODEL = "qwen2.5-it-3b-FLM"  # Default Lemonade model


def detect_lemonade_port(
    host: Optional[str] = None,
    ports: Optional[List[int]] = None
) -> Optional[int]:
    """
    Auto-detect the port where Lemonade is running.

    Checks LEMONADE_SERVER_URL environment variable first, then scans common ports.

    Args:
        host: Host to check. Defaults to DIFFRON_LEMONADE_HOST or localhost.
        ports: List of ports to scan. Defaults to common Lemonade ports.

    Returns:
        Port number if found, None otherwise.
    """
    # Check LEMONADE_SERVER_URL environment variable first (standard Lemonade env)
    server_url = os.environ.get("LEMONADE_SERVER_URL")
    if server_url:
        try:
            # Parse URL like "http://localhost:8020"
            from urllib.parse import urlparse
            parsed = urlparse(server_url)
            if parsed.port:
                port = parsed.port
                if is_port_open(parsed.hostname or DEFAULT_HOST, port):
                    return port
        except Exception:
            pass

    # Check DIFFRON_LEMONADE_PORT (Diffron-specific)
    env_port = os.environ.get("DIFFRON_LEMONADE_PORT")
    if env_port:
        try:
            port = int(env_port)
            if is_port_open(host or DEFAULT_HOST, port):
                return port
        except ValueError:
            pass

    # Scan common ports
    host = host or os.environ.get("DIFFRON_LEMONADE_HOST", DEFAULT_HOST)
    ports_to_scan = ports or DEFAULT_PORTS

    open_ports = scan_ports(ports_to_scan, host)

    if open_ports:
        return open_ports[0]  # Return first open port

    return None


def get_lemonade_url() -> str:
    """
    Get the Lemonade server URL from environment or default.

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
    """
    Check if Lemonade is running.

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
    """
    Client for interacting with Lemonade LLM server.

    Automatically detects the running Lemonade instance and provides
    a convenient interface for chat completions.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """
        Initialize the Lemonade client.

        Args:
            base_url: Lemonade server URL. Auto-detects from LEMONADE_SERVER_URL or defaults to http://localhost:8020.
            api_key: API key. Defaults to "lemonade".
            model: Model name to use. Defaults to qwen2.5-it-3b-FLM.
        """
        # Get base URL from parameter, environment, or default
        if base_url:
            self.base_url = base_url.rstrip("/")
        else:
            self.base_url = get_lemonade_url()

        # Parse host and port from base_url
        from urllib.parse import urlparse
        parsed = urlparse(self.base_url)
        self.host = parsed.hostname or DEFAULT_HOST
        self.port = parsed.port or DEFAULT_PORT

        self.api_key = api_key or LEMONADE_API_KEY

        # Model: parameter > environment > default
        self.model = model or os.environ.get("DIFFRON_MODEL") or DEFAULT_MODEL

        self.client = OpenAI(
            base_url=f"{self.base_url}/api/v1",
            api_key=self.api_key,
        )

    def chat_completion(
        self,
        messages: List[dict],
        max_tokens: int = 100,
        temperature: float = 0.2,
        **kwargs
    ) -> str:
        """
        Generate a chat completion.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.
            **kwargs: Additional arguments to pass to the API.

        Returns:
            Generated response content.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )
        return response.choices[0].message.content

    def __repr__(self) -> str:
        return f"LemonadeClient(base_url='{self.base_url}', model='{self.model}')"
