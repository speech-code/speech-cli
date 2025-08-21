import logging

from langchain_core.messages import SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import MessagesState

from speech_cli.core.base_agent import BaseAgent
from speech_cli.core.tools import generator_write_file

from .system_messages import system_messages

logger = logging.getLogger(__name__)


class Generator(BaseAgent):
    """Agent for generating hlc code from natural language."""

    config = {"recursion_limit": 500, "configurable": {"thread_id": "generator_1"}}

    checkpointer = InMemorySaver()

    overall_state = MessagesState

    tools = [generator_write_file]

    system_message = [SystemMessage(content=system_messages.generator)]
