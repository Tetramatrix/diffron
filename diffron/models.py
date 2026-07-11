"""
Curated models for Diffron.

Provides a collection of pre-configured models optimized for different use cases
with the AMD Lemonade LLM server.
"""

from dataclasses import dataclass
from typing import List, Optional

__all__ = [
    "ModelConfig",
    "list_available_models",
    "get_default_model",
    "get_model_config",
    "setup_model_cli",
]


@dataclass
class ModelConfig:
    """Configuration for a curated model."""

    name: str
    description: str
    parameters: str
    best_for: str
    is_default: bool = False

    def __repr__(self) -> str:
        marker = " (default)" if self.is_default else ""
        return f"ModelConfig({self.name}{marker})"


# Curated model collection
AVAILABLE_MODELS: List[ModelConfig] = [
    ModelConfig(
        name="qwen2.5-it-3b-FLM",
        description="Qwen 2.5 Instruct — balanced performance and quality",
        parameters="3B",
        best_for="Commit messages, PR descriptions, general tasks",
        is_default=True,
    ),
    ModelConfig(
        name="Qwen3.5-0.8B-GGUF",
        description="Qwen 3.5 — lightweight and fast, low resource usage",
        parameters="0.8B",
        best_for="Quick commits, low-resource PCs, fast iteration",
    ),
    ModelConfig(
        name="qwen2.5-7b-gguf",
        description="Qwen 2.5 — larger model with better reasoning",
        parameters="7B",
        best_for="Complex code analysis, detailed PR descriptions",
    ),
    ModelConfig(
        name="llama-3.2-3b-gguf",
        description="Llama 3.2 — alternative architecture",
        parameters="3B",
        best_for="General purpose, different perspective on code",
    ),
]

DEFAULT_MODEL_NAME = "Qwen3.5-0.8B-GGUF"


def list_available_models() -> List[ModelConfig]:
    """
    List all curated models available for use with Diffron.

    Returns:
        List of ModelConfig objects sorted by relevance (default first).
    """
    # Put default model first, then others
    models = sorted(AVAILABLE_MODELS, key=lambda m: not m.is_default)
    return models


def get_default_model() -> ModelConfig:
    """
    Get the default curated model configuration.

    Returns:
        ModelConfig for the default model.
    """
    for model in AVAILABLE_MODELS:
        if model.is_default:
            return model
    # Fallback
    return AVAILABLE_MODELS[0]


def get_model_config(model_name: str) -> Optional[ModelConfig]:
    """
    Get configuration for a specific model by name.

    Args:
        model_name: Model name (e.g., 'Qwen3.5-0.8B-GGUF').

    Returns:
        ModelConfig if found, None otherwise.
    """
    # Exact match first
    for model in AVAILABLE_MODELS:
        if model.name == model_name:
            return model
    # Case-insensitive fallback
    for model in AVAILABLE_MODELS:
        if model.name.lower() == model_name.lower():
            return model
    return None


def setup_model_cli():
    """
    CLI entry point for setting up the model.

    Handles:
    - `diffron-setup-model` — set default model
    - `diffron-setup-model --list` — list available models
    - `diffron-setup-model --model NAME` — set specific model
    """
    import argparse
    import sys
    import os

    parser = argparse.ArgumentParser(
        description="Set up Diffron model selection.",
        prog="diffron-setup-model",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available curated models.",
    )
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        default=None,
        help="Set a specific model by name.",
    )

    args = parser.parse_args()

    if args.list:
        print("Available curated models:\n")
        models = list_available_models()
        for i, model in enumerate(models, 1):
            marker = " ⭐ DEFAULT" if model.is_default else ""
            print(f"  {i}. {model.name}{marker}")
            print(f"     Parameters: {model.parameters}")
            print(f"     Best for:   {model.best_for}")
            print(f"     {model.description}")
            print()
        sys.exit(0)

    if args.model:
        # Validate model name (case-insensitive)
        config = get_model_config(args.model)
        if config is None:
            available = ", ".join(m.name for m in AVAILABLE_MODELS)
            print(f"Error: Unknown model '{args.model}'", file=sys.stderr)
            print(f"Available models: {available}", file=sys.stderr)
            sys.exit(1)

        # Use the canonical name from config (not user input)
        os.environ["DIFFRON_MODEL"] = config.name

        success = _set_env_permanently("DIFFRON_MODEL", config.name)
        print(f"Model set to: {config.name} ⭐")
        print(f"  {config.description}")
        print(f"  Best for: {config.best_for}")
        print()
        if success:
            print("Note: Restart your terminal for the change to take effect.")
        else:
            print("Set for current session only.")

        sys.exit(0)

    # No arguments: set default model
    default = get_default_model()
    os.environ["DIFFRON_MODEL"] = default.name

    success = _set_env_permanently("DIFFRON_MODEL", default.name)
    print(f"Default model set to: {default.name} ⭐")
    print(f"  {default.description}")
    print(f"  Best for: {default.best_for}")
    print()
    if success:
        print("Note: Restart your terminal for the change to take effect.")
    else:
        print("Set for current session only.")

    sys.exit(0)


def _set_env_permanently(name: str, value: str) -> bool:
    """Set an environment variable permanently (cross-platform).

    Windows: uses setx command.
    Linux/macOS: writes to shell profile (~/.bashrc, ~/.zshrc, etc.).

    Returns:
        True if successful, False otherwise.
    """
    import subprocess
    import sys
    import os

    if os.name == "nt":
        # Windows: use setx
        try:
            subprocess.run(
                ["setx", name, value],
                check=True,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    else:
        # Linux/macOS: write to shell profile
        home = os.path.expanduser("~")
        export_line = f'export {name}="{value}"\n'

        # Determine which shell profile to use
        shell = os.environ.get("SHELL", "")
        if "zsh" in shell:
            profile = os.path.join(home, ".zshrc")
        elif "fish" in shell:
            profile = os.path.join(home, ".config", "fish", "config.fish")
        else:
            profile = os.path.join(home, ".bashrc")

        try:
            # Check if already set in profile
            if os.path.exists(profile):
                with open(profile, "r", encoding="utf-8") as f:
                    if f"export {name}=" in f.read():
                        # Update existing line
                        lines = f.readlines() if False else []  # noqa: dummy
                        _update_profile_var(profile, name, value)
                        return True

            # Append to profile
            with open(profile, "a", encoding="utf-8") as f:
                f.write(f"\n# Diffron - set by diffron-setup-model\n")
                f.write(export_line)
            return True
        except OSError:
            return False


def _update_profile_var(profile: str, name: str, value: str) -> None:
    """Update an existing env var in a shell profile file."""
    import re

    with open(profile, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace existing export line
    pattern = rf'^export {re.escape(name)}=.*$'
    replacement = f'export {name}="{value}"'
    new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    if new_content == content:
        # No existing line found, append
        with open(profile, "a", encoding="utf-8") as f:
            f.write(f'\nexport {name}="{value}"\n')
    else:
        with open(profile, "w", encoding="utf-8") as f:
            f.write(new_content)
