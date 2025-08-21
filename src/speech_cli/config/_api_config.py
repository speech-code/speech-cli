from pathlib import Path

from dotenv import dotenv_values, set_key


class APIConfig:
    """ENV class for multiple model api configuration."""

    _default_api_config = {
        "OPENAI": ("gpt-4", "gpt-5"),
        "ANTHROPIC": ("claude-4",),
        "GOOGLE_GENAI": ("gemini-2.5-flash", "gemini-2.5-pro"),
    }

    def __init__(self):
        self._speech_dir = Path.home() / ".speech"
        self._env_file = self._speech_dir / ".env"

        self._ensure_files_exist()

        self._envs = self._load_env()

    def _ensure_files_exist(self):
        """Ensure the .speech directory and .env file exist."""
        self._speech_dir.mkdir(parents=True, exist_ok=True)
        self._env_file.touch(exist_ok=True)

    def _load_env(self):
        """Load configuration from .env file."""
        model_envs = {}
        for provider, model_config in dotenv_values(self._env_file).items():
            model_envs[provider.lower()] = model_config.split(", ")
        return model_envs

    def set_api_key(self, provider: str, model: str, api_key: str):
        """Set the API key for a given provider in the .env file.

        Provider should be one of the supported providers.
        """
        provider_upper = provider.upper()
        if provider_upper not in self._default_api_config:
            raise ValueError(f"Provider '{provider}' is not supported.")

        set_key(self._env_file, provider_upper, f"{model}, {api_key}")
        self._envs = self._load_env()

    def configured(self):
        """Get all available model configurations."""
        return self._envs

    def not_configured(self) -> dict[str, tuple[str]]:
        """Get all un-configured model configurations."""
        not_configured = {}

        for provider in self._default_api_config:
            if provider.lower() not in self._envs:
                not_configured[provider] = self._default_api_config[provider]

        return not_configured


api_config = APIConfig()
