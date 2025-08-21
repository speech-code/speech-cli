import logging
from pathlib import Path

from speech_cli.core.tool_call import ToolCall

logger = logging.getLogger(__name__)


def change_directory(path: str) -> tuple[bool, str]:
    """Change the current working directory.

    This function allows for navigating the file system by changing the current
    directory to the specified path.

    Args:
        path (str): The path of the directory to switch to.

    Returns:
        tuple[bool, str]: A tuple where the first element is a boolean
                          indicating success (True) or failure (False), and the
                          second element is a message indicating the result of
                          the operation.

    """
    tool_call = ToolCall(
        name="change_directory",
        action_in_progress="Changing directory",
        action_success="Changed directory",
        action_failed="Couldn't change directory",
        message=path,
    )
    tool_call.stream()
    try:
        p = Path(path)
        p.resolve(strict=True)
        # Cannot use os.chdir with pathlib, so we keep it for now,
        # but the check is with pathlib
        import os

        os.chdir(p)
        return True, f"Switched to directory: {Path.cwd()}"
    except FileNotFoundError:
        return False, f"Error: Directory '{path}' does not exist."
    except PermissionError:
        return False, f"Error: No permission to access directory '{path}'."
    except Exception as e:
        return False, f"Error changing directory: {e}"
