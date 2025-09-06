from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from langchain_core.messages import SystemMessage
from langgraph.graph import START
from langgraph.prebuilt import ToolNode, tools_condition

from speech_cli.core.system_messages import system_messages
from speech_cli.core.tools import generator_write_file as write_file

from .base import AgentsGraphState, BaseAgent, BaseState

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

    from langchain_core.messages import AIMessage


logger = logging.getLogger(__name__)


class GeneratorOverallState(BaseState):
    """Generator overall state."""

    pass


class Generator(BaseAgent, next_node="Translator", private_state=True):
    """Agent for generating hlc code from natural language."""

    overall_state = GeneratorOverallState
    tools = [write_file]

    _system_message = [SystemMessage(content=system_messages.generator)]

    @classmethod
    async def llm_node(cls, state: GeneratorOverallState) -> GeneratorOverallState:
        """Graph reasoning (llm) node."""
        logger.debug("Entering the Generator agent...")

        messages = cls._system_message + state.messages

        response: AIMessage = await cls.llm_invoke(messages)

        return {"messages": [response]}

    @classmethod
    async def call_generator(cls, state: AgentsGraphState):
        """Isolation unit for the generator agent."""
        await cls.graph.ainvoke({"messages": state.summary})

    @classmethod
    def nodes(cls) -> list[tuple[str, Callable]]:
        """Class method for retrieving agent nodes."""
        return [("generator", cls.llm_node), ("tools", ToolNode(cls.tools))]

    @classmethod
    def static_edges(cls) -> list[tuple[str | list[str], str]]:
        """Class method for retrieving agent static edges."""
        return [(START, "generator")]

    @classmethod
    def conditional_edges(cls) -> list[tuple[str, Any]]:
        """Class method for retrieving agent conditional edges."""
        return [("generator", tools_condition)]
