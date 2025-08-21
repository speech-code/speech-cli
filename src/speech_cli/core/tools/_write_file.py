import json
import logging
from pathlib import Path
from typing import Literal

logger = logging.getLogger(__name__)


def write_file(
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
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)

        if not isinstance(content, str):
            try:
                content = json.dumps(content, indent=4, default=str)
            except Exception as e:
                return (
                    False,
                    f"Error: Unable to convert content to a writable string: {e}",
                )

        if content and not content.endswith("\n"):
            content += "\n"

        file_mode = "w" if mode.lower() == "overwrite" else "a"
        with p.open(file_mode, encoding="utf-8") as file:
            file.write(content)

        if p.exists():
            return (
                True,
                f"Successfully wrote {p.stat().st_size} bytes to '{p}' in {mode} mode.",
            )
        else:
            return (
                False,
                "Write operation completed, "
                f"but unable to verify file exists at '{p}'.",
            )

    except PermissionError:
        return False, f"Error: No permission to write to file '{path}'."
    except Exception as e:
        return False, f"Error writing to file: {e}"
