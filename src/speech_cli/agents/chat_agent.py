from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from langchain_core.messages import SystemMessage
from langgraph.graph import START
from langgraph.prebuilt import ToolNode, tools_condition

from speech_cli.core.system_messages import system_messages
from speech_cli.core.tools import transfer_to_generator

from .base import BaseAgent, BaseState

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any


logger = logging.getLogger(__name__)


class ChatOverallState(BaseState):
    """Chat overall state."""

    pass


class Chat(BaseAgent, start_node=True):
    """Chat agent."""

    overall_state = ChatOverallState
    tools = [transfer_to_generator]

    _system_message = [SystemMessage(content=system_messages.chat)]

    @classmethod
    async def llm_node(cls, state: ChatOverallState) -> ChatOverallState:
        """Graph reasoning (llm) node."""
        messages = cls._system_message + state.messages

        response = await cls.llm_invoke(messages)

        logger.debug("The llm response: %r", response)

        return {"messages": response}

    @classmethod
    def nodes(cls) -> list[tuple[str, Callable]]:
        """Class method for retrieving agent nodes."""
        return [("chat", cls.llm_node), ("tools", ToolNode(cls.tools))]

    @classmethod
    def static_edges(cls) -> list[tuple[str | list[str], str]]:
        """Class method for retrieving agent static edges."""
        return [(START, "chat")]

    @classmethod
    def conditional_edges(cls) -> list[tuple[str, Any]]:
        """Class method for retrieving agent conditional edges."""
        return [("chat", tools_condition)]
