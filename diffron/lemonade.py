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
    from lemonade_sdk.client import LemonadeClient as _LemonadeSDKClient
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
    """Detect port for running Lemonade server.

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
        parsed = urlparse(server_url)
        port = parsed.port
        if port and is_port_open(parsed.hostname or "localhost", port):
            return port

    # Use SDK for verification
    h = host or os.environ.get("DIFFRON_LEMONADE_HOST") or DEFAULT_HOST
    p = ports or DEFAULT_PORTS
    return verify_lemonade_server(hostname=h, ports=p)


class LemonadeClient:
    """Lemonade LLM API client with automatic port detection.

    Wraps the OpenAI-compatible API of the Lemonade server,
    handling connection setup and model inference.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        api_key: str = LEMONADE_API_KEY,
        model: str = DEFAULT_MODEL,
    ) -> None:
        """Initialize Lemonade client.

        Args:
            host: Host of the Lemonade server. Defaults to env or localhost.
            port: Port of the Lemonade server. Auto-detects if None.
            api_key: API key for the server.
            model: Model name to use for inference.
        """
        self.host = host or os.environ.get("DIFFRON_LEMONADE_HOST") or DEFAULT_HOST
        self.api_key = api_key
        self.model = model

        # Auto-detect port if not provided
        if port:
            self._port = port
            self.port = port
        else:
            detected = detect_lemonade_port(host=self.host)
            if detected:
                self._port = detected
                self.port = detected
            else:
                # Fallback to default port
                self._port = DEFAULT_PORT
                self.port = DEFAULT_PORT

        self.base_url = f"http://{self.host}:{self._port}"
        self._init_client()

    def _init_client(self) -> None:
        """Reinitialize OpenAI client with current configuration."""
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
        """Generate chat completion.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.
            **kwargs: Additional arguments to pass to API.

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
                    **kwargs,
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
        """Unload and reload Lemonade model when unresponsive.

        Uses lemonade-python-sdk's unload_model() and load_model() methods
        to properly force a server-side model restart.
        """
        try:
            # Use SDK's LemonadeClient for server operations
            sdk_client = _LemonadeSDKClient(
                base_url=f"http://{self.host}:{self._port}"
            )

            # Unload current model from server
            sdk_client.unload_model()

            # Small delay to allow server to complete unload
            import time
            time.sleep(0.5)

            # Load the model back on server
            sdk_client.load_model(model_name=self.model)

            # Reinitialize our client (same port, model should be fresh)
            self._init_client()

        except Exception:
            pass  # Continue even if reload fails

    def __repr__(self) -> str:
        return f"LemonadeClient(base_url={self.base_url}, model={self.model})"
