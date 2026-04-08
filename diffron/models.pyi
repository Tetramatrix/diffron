"""Type stubs for curated models module."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ModelConfig:
    name: str
    description: str
    parameters: str
    best_for: str
    is_default: bool = False


AVAILABLE_MODELS: List[ModelConfig]
DEFAULT_MODEL_NAME: str


def list_available_models() -> List[ModelConfig]: ...
def get_default_model() -> ModelConfig: ...
def get_model_config(model_name: str) -> Optional[ModelConfig]: ...
def setup_model_cli() -> None: ...
