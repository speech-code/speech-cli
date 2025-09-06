from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from langchain.chat_models import init_chat_model

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel
    from langchain_core.language_models.base import LanguageModelInput
    from langchain_core.messages import BaseMessage
    from langchain_core.runnables import Runnable

    from speech_cli.agents.base import BaseAgent

logger = logging.getLogger(__name__)


class LLM:
    """Maintain a single shared BaseChatModel and return per-agent configured LLMs.

    LLM holds one BaseChatModel instance as the application's current model. When an
    agent requests its LLM, the shared model is returned with that agent's tools
    bound to it so the agent receives a ready-to-use chat model. The stored model
    reference can be updated at runtime by the `APIConfig` class so changes to the
    user's model selection take effect immediately for subsequent agent requests.
    """

    _COMPULSORY_ARGS = ("model", "api_key", "model_provider")
    _OPTIONAL_ARGS = ("base_url",)

    llm: BaseChatModel | None = None

    def __get__(
        self, _agent: BaseAgent, agent_type: type[BaseAgent]
    ) -> Runnable[LanguageModelInput, BaseMessage]:
        """Return the right llm for each agent at runtime."""
        return self.llm.bind_tools(agent_type.tools) if agent_type.tools else self.llm

    @classmethod
    def create_model(cls, config: dict[str, str]):
        """Create and store llm."""
        if not isinstance(config, dict):
            raise TypeError(f"Expected api config to be a dict, not {type(config)}.")

        verified_args = {}

        for arg in cls._COMPULSORY_ARGS:
            if arg not in config:
                raise ValueError("Config dict missing a compulsory arg, {arg}")

            verified_args[arg] = config[arg]

        for arg in cls._OPTIONAL_ARGS:
            if arg in config:
                verified_args[arg] = config[arg]

        cls.llm = init_chat_model(**verified_args, timeout=600)
