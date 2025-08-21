import logging

from langchain_core.messages import SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import MessagesState

from speech_cli.core.base_agent import BaseAgent
from speech_cli.core.decorators import add_human_in_the_loop
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

from .system_messages import system_messages

logger = logging.getLogger(__name__)


class Translator(BaseAgent):
    """Agent for translating hlc code to high level languages."""

    overall_state = MessagesState

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

    config = {"recursion_limit": 500, "configurable": {"thread_id": "translator_2"}}

    checkpointer = InMemorySaver()

    system_message = [SystemMessage(content=system_messages.translator)]
