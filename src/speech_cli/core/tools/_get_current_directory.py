import logging
from pathlib import Path

from speech_cli.core.tool_call import ToolCall

logger = logging.getLogger(__name__)


def get_current_directory() -> tuple[bool, str]:
    """Get the current working directory.

    This function returns the absolute path of the directory from which the
    script is currently running.

    Returns:
        tuple[bool, str]: A tuple where the first element is always True, and
                          the second element is the path of the current
                          working directory.

    """
    tool_call = ToolCall(
        name="get_current_directory",
        action_in_progress="Retrieving current directory",
        action_success="Retrieved current directory",
        action_failed="Couldn't retrieve current directory",
        message=f"The current directory: {Path.cwd()}",
    )
    tool_call.stream()
    return True, str(Path.cwd())
