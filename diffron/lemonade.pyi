"""
Lemonade integration for Diffron.

Provides automatic port detection and API client for Lemonade LLM server.
"""

from typing import Optional, List


DEFAULT_HOST: str
DEFAULT_PORTS: List[int]
LEMONADE_API_KEY: str


def detect_lemonade_port(
    host: Optional[str] = None,
    ports: Optional[List[int]] = None
) -> Optional[int]:
    """Auto-detect the port where Lemonade is running."""
    ...


def is_lemonade_running(
    host: Optional[str] = None,
    port: Optional[int] = None
) -> bool:
    """Check if Lemonade is running."""
    ...


class LemonadeClient:
    """Client for interacting with Lemonade LLM server."""

    host: str
    port: int
    api_key: str
    model: str
    base_url: str
    client: OpenAI

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """Initialize the Lemonade client."""
        ...

    def _detect_model(self) -> str:
        """Auto-detect available models from Lemonade."""
        ...

    def chat_completion(
        self,
        messages: List[dict],
        max_tokens: int = 100,
        temperature: float = 0.2,
        **kwargs
    ) -> str:
        """Generate a chat completion."""
        ...

    def __repr__(self) -> str:
        ...
def get_lemonade_url(
    host: Optional[str] = None,
    port: Optional[int] = None,
) -> str:
    """Get the Lemonade server URL."""