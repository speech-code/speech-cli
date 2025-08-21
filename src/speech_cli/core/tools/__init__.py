import logging
from typing import Literal

from speech_cli.core.tool_call import ToolCall

from ._change_directory import change_directory
from ._delete_file_content import delete_file_content
from ._get_current_directory import get_current_directory
from ._insert_file_content import insert_file_content
from ._list_directory import list_directory
from ._read_file import read_file
from ._run_javascript_test import run_javascript_test
from ._run_python_test import run_python_test
from ._terminal import get_command_history, terminal_use
from ._update_file_content import update_file_content
from ._write_file import write_file

logger = logging.getLogger(__name__)


def generator_write_file(content: str) -> tuple[bool, str]:
    """Create and write content to a file.

    Args:
        content: Content to write to the file

    Returns:
        tuple[bool, str]: (success, message)

    """
    tool_call = ToolCall(
        name="generator_write_file",
        action_in_progress="Writing to HLC.json",
        action_success="Successfully wrote to HLC.json",
        action_failed="Couldn't write to HLC.json",
        message=content,
    )
    tool_call.stream()
    return write_file("HLC.json", content)


def translator_write_file(
    path: str, content: str, mode: Literal["overwrite", "append"] = "overwrite"
) -> tuple[bool, str]:
    """Write content to a file, with options to overwrite or append.

    This function can handle both string and JSON object content. It ensures
    the target directory exists before writing.

    Args:
        path (str): The path to the file.
        content (str): The content to write. Can be a string or a JSON
                       serializable object.
        mode (str, optional): The write mode, either 'overwrite' or 'append'.
                              Defaults to 'overwrite'.

    Returns:
        tuple[bool, str]: A tuple indicating success or failure and a
                          corresponding message.

    """
    tool_call = ToolCall(
        name="translator_write_file",
        action_in_progress=f"Writing to {path} in {mode} mode",
        action_success=f"Successfully wrote to {path} in {mode} mode",
        action_failed=f"Couldn't write to {path} in {mode} mode",
        message=content,
    )
    tool_call.stream()
    return write_file(path, content, mode=mode)


__all__ = [
    "change_directory",
    "delete_file_content",
    "get_current_directory",
    "insert_file_content",
    "list_directory",
    "read_file",
    "run_javascript_test",
    "run_python_test",
    "get_command_history",
    "terminal_use",
    "update_file_content",
    "write_file",
    "write_file",
]
