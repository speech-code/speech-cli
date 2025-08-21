# ruff: noqa: PLR0911 PLR0912
import json
import logging
from pathlib import Path

from speech_cli.core.tool_call import ToolCall

logger = logging.getLogger(__name__)


def update_file_content(
    path: str,
    content: str,
    row: int = None,
    rows: list[int] = None,
    substring: str = None,
) -> tuple[bool, str]:
    """Update content in a file.

    This function can replace entire rows or specific substrings within rows
    with new content.

    Args:
        path (str): The path to the file.
        content (str): The new content.
        row (int, optional): The row number to update.
        rows (list, optional): A list of row numbers to update.
        substring (str, optional): The substring to replace with the new
                                   content.

    Returns:
        tuple[bool, str]: A tuple indicating success or failure and a
                          corresponding message.

    """
    tool_call = ToolCall(
        name="update_file_content",
        action_in_progress=f"Updating {path} file",
        action_success=f"Updated {path} file",
        action_failed=f"Couldn't update {path} file",
        message=substring,
    )
    tool_call.stream()
    try:
        p = Path(path)
        if not p.is_file():
            return False, f"Error: File '{path}' does not exist."

        lines = p.read_text(encoding="utf-8").splitlines(True)
        total_lines = len(lines)

        if not isinstance(content, str):
            try:
                content = json.dumps(content, indent=4, default=str)
            except Exception as e:
                return (
                    False,
                    f"Error: Unable to convert content to a writable string: {e}",
                )

        if substring is None and content and not content.endswith("\n"):
            content += "\n"

        target_rows = range(total_lines)
        if rows is not None:
            target_rows = rows
        elif row is not None:
            target_rows = [row]

        updated_rows = []
        for r in target_rows:
            if r < total_lines:
                if substring:
                    if substring in lines[r]:
                        lines[r] = lines[r].replace(substring, content)
                        updated_rows.append(r)
                else:
                    lines[r] = content
                    updated_rows.append(r)

        if not updated_rows:
            return True, "No content was updated."

        p.write_text("".join(lines), encoding="utf-8")
        if substring:
            return (
                True,
                f"Successfully updated substring in rows {updated_rows} in '{path}'.",
            )
        return True, f"Successfully updated rows {updated_rows} in '{path}'."

    except PermissionError:
        return False, f"Error: No permission to modify file '{path}'."
    except Exception as e:
        return False, f"Error updating content: {e}"
