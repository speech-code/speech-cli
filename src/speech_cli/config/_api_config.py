import json
import logging
from pathlib import Path

from speech_cli.core.llm import LLM

logger = logging.getLogger(__name__)

_SUPPORTED_PROVIDERS = {
    # "Open AI": {
    #     # These will be provided in addition to the model and api key
    #     # configuration, during model creation.
    #     "model_provider": "openai",
    # },
    "Google Gemini": {"model_provider": "google_genai"},
    # "Anthropic": {"model_provider": "anthropic"},
    "Open Router": {
        "model_provider": "openai",
        "base_url": "https://openrouter.ai/api/v1",
    },
}


class _GetAvailableModels:
    """Retrieves available models for selected provided, and api key."""

    def __init__(self, provider: str, api_key: str):
        self.api_key = api_key

        _method_name = provider.lower().replace(" ", "_")
        try:
            self.models = getattr(self, _method_name)() or []
        except Exception as err:
            logger.warning("Error occurred while trying to retrieve models: %s", err)
            self.models = []
        logger.debug("""The available models: %s""", self.models)

    def open_router(self):
        """Retrieve available models from open router."""
        import requests

        url = "https://openrouter.ai/api/v1/models"
        response = requests.get(url)

        status_code = 200
        if response.status_code == status_code:
            return [model["id"] for model in response.json()["data"]]

    def google_gemini(self):
        """Retrieve available models from google gemini."""
        from google import genai

        client = genai.Client(api_key=self.api_key)
        available_models = client.models.list()

        logger.debug("Google gemini models: %s", available_models)

        return [model.name.split("/")[1] for model in available_models]

    # TODO@chideracollins: Add support for the remaining providers
    def open_ai(self):
        """Retrieve available models from open ai."""
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)

        _available_models = client.models.list()

    def anthropic(self):
        """Retrieve available models from anthropic."""
        import anthropic

        client = anthropic.Anthropic(api_key=self.api_key)

        _available_models = client.models.list(limit=20)


class APIConfig:
    """Api configuration class."""

    def __init__(self):
        self._speech_dir = Path.home() / ".speech"
        self._config_file = self._speech_dir / "api_config.json"

        self._speech_dir.mkdir(parents=True, exist_ok=True)
        self._config_file.touch(exist_ok=True)

        try:
            with self._config_file.open(encoding="utf-8") as f:
                self.config: dict = json.load(f)
        except json.JSONDecodeError:
            self.config = None

        logger.debug("The retrieved config: %s", self.config)

        if self.config:
            LLM.create_model(self.config)

    @property
    def supported_providers(self) -> list[str]:
        """Get a list of all the supported model providers."""
        return sorted(_SUPPORTED_PROVIDERS.keys())

    def get_models(self, provider: str, api_key: str) -> list[str]:
        """Look up online for the available models given the provider and api key.

        Args:
            provider (str): Selected provider.
            api_key (str): The api key.

        Returns:
            list[str]: Available models.

        """
        return sorted(_GetAvailableModels(provider, api_key).models)

    async def configure(self, provider: str, model: str, api_key: str):
        """Store the api configuration in the api_config.json file."""
        if provider not in _SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported provider {provider}, provided.")
        self.config = {
            "verbose_name": provider,
            "model": model,
            "api_key": api_key,
        }

        self.config.update(_SUPPORTED_PROVIDERS[provider])

        with self._config_file.open("w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)

        LLM.create_model(self.config)

    @property
    def configured(self) -> bool:
        """Check if api has been configured."""
        return bool(LLM.llm)


api_config = APIConfig()
