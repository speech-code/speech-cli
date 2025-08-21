import asyncio
import logging

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from speech_cli.config import api_config

logger = logging.getLogger(__name__)


class LLM[Agent]:
    """LLM class to manage llm invocation and model switching."""

    available_models: list[BaseChatModel | None] = []

    def __get__(self, obj: Agent, _objtype=None):
        """Initialize all configured models by user."""
        if len(self.available_models) == 0:
            for provider, config in api_config.configured().items():
                logger.debug("The available tools for agent, %r", obj.tools)
                model, api_key = config
                llm: BaseChatModel = init_chat_model(
                    model=model,
                    model_provider=provider,
                    api_key=api_key,
                )
                llm = llm.bind_tools(obj.tools) if obj.tools else llm
                self.available_models.append(llm)

        logger.debug("The built LLM, %r", self)
        return self

    async def invoke(self, messages, timeout=20.0):
        """Asynchronously invoke all available models, until a response.

        Else raise the raise the error from the last model call.
        """
        for llm in self.available_models:
            try:
                # ainvoke is async, so we can wrap it directly
                response = await asyncio.wait_for(
                    llm.ainvoke(messages),
                    timeout=timeout,  # hard cap regardless of SDK defaults
                )
                return response
            except TimeoutError as err:
                raise ConnectionError(
                    f"LLM call timed out after {timeout} seconds."
                ) from err
            except Exception as err:
                unknown_err = err
                pass

        raise unknown_err

    def __repr__(self) -> str:
        """LLM object representation."""
        attrs = {
            k: v for k, v in self.__class__.__dict__.items() if not k.startswith("__")
        }
        return f"{self.__class__.__name__}({attrs=})"
