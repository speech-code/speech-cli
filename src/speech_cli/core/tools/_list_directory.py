import logging
from pathlib import Path

from speech_cli.core.tool_call import ToolCall

logger = logging.getLogger(__name__)


def list_directory(path: str | None = None) -> tuple[bool, str]:
    """List the files and subdirectories in a specified directory.

    This function provides a view of the contents of a directory,
    distinguishing between files and subdirectories. If no path is provided, it
    lists the contents of the current working directory.

    Args:
        path (str, optional): The path of the directory to list. Defaults to
                              the current directory.

    Returns:
        tuple[bool, str]: A tuple where the first element is a boolean
                          indicating success (True) or failure (False), and the
                          second element is a formatted string of the directory
                          contents or an error message.

    """
    tool_call = ToolCall(
        name="list_directory",
        action_in_progress="Viewing directory contents",
        action_success="Viewed directory contents",
        action_failed="Couldn't view directory contents",
        message=path,
    )
    tool_call.stream()
    try:
        target_path = Path(path) if path else Path.cwd()
        if not target_path.is_dir():
            return False, f"Error: '{target_path}' is not a valid directory."

        items = list(target_path.iterdir())
        dirs = sorted([f"📁 {item.name}/" for item in items if item.is_dir()])
        files = sorted([f"📄 {item.name}" for item in items if item.is_file()])

        if not dirs and not files:
            return True, f"Directory '{target_path}' is empty."

        output = f"Contents of directory '{target_path}':\n\n"
        if dirs:
            output += "Directories:\n" + "\n".join(dirs) + "\n\n"
        if files:
            output += "Files:\n" + "\n".join(files)

        return True, output.strip()

    except PermissionError:
        return False, f"Error: No permission to access directory '{path}'."
    except Exception as e:
        return False, f"Error listing directory contents: {e}"
