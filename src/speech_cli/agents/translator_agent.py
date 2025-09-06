from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from langchain_core.messages import SystemMessage
from langgraph.graph import START
from langgraph.prebuilt import ToolNode, tools_condition

from speech_cli.core.decorators import add_human_in_the_loop
from speech_cli.core.system_messages import system_messages
from speech_cli.core.tools import (
    change_directory,
    delete_file_content,
    get_command_history,
    get_current_directory,
    insert_file_content,
    list_directory,
    read_file,
    run_javascript_test,
    run_python_test,
    terminal_use,
    translator_write_file,
    update_file_content,
)
from speech_cli.core.utils import read_hlc_file

from .base import AgentsGraphState, BaseAgent, BaseState

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

logger = logging.getLogger(__name__)


class TranslatorOverallState(BaseState):
    """Translator overall state."""

    pass


class Translator(BaseAgent, end_node=True, private_state=True):
    """Agent for translating hlc code to high level languages."""

    overall_state = TranslatorOverallState
    tools = [
        add_human_in_the_loop(
            terminal_use,
            interrupt_config={
                "allow_accept": True,
                "allow_ignore": True,
            },
        ),
        add_human_in_the_loop(
            delete_file_content,
            interrupt_config={
                "allow_accept": True,
                "allow_ignore": True,
            },
        ),
        add_human_in_the_loop(
            run_python_test,
            interrupt_config={
                "allow_accept": True,
                "allow_ignore": True,
            },
        ),
        add_human_in_the_loop(
            run_javascript_test,
            interrupt_config={
                "allow_accept": True,
                "allow_ignore": True,
            },
        ),
        change_directory,
        get_command_history,
        get_current_directory,
        insert_file_content,
        list_directory,
        read_file,
        update_file_content,
        translator_write_file,
    ]

    _system_message = [SystemMessage(content=system_messages.translator)]

    @classmethod
    async def llm_node(cls, state: TranslatorOverallState) -> TranslatorOverallState:
        """Graph reasoning (llm) node."""
        logger.debug("Translator state: %r", state)
        messages = cls._system_message + state.messages

        response = await cls.llm_invoke(messages)

        return {"messages": [response]}

    @classmethod
    async def call_translator(cls, _state: AgentsGraphState):
        """Isolation unit for the translator agent."""
        await cls.graph.ainvoke({"messages": read_hlc_file()})

    @classmethod
    def nodes(cls) -> list[tuple[str, Callable]]:
        """Class method for retrieving agent nodes."""
        return [("translator", cls.llm_node), ("tools", ToolNode(cls.tools))]

    @classmethod
    def static_edges(cls) -> list[tuple[str | list[str], str]]:
        """Class method for retrieving agent static edges."""
        return [(START, "translator"), ("tools", "translator")]

    @classmethod
    def conditional_edges(cls) -> list[tuple[str, Any]]:
        """Class method for retrieving agent conditional edges."""
        return [("translator", tools_condition)]
