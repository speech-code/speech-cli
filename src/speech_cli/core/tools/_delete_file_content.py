# ruff: noqa: PLR0912 PLR0911

import logging
from pathlib import Path

from speech_cli.core.tool_call import ToolCall

logger = logging.getLogger(__name__)


def delete_file_content(
    path: str,
    row: int | None = None,
    rows: list[int] | None = None,
    substring: str | None = None,
) -> tuple[bool, str]:
    """Delete content from a file.

    This function can delete content by row, a list of rows, or by a
    substring within the specified rows.

    Args:
        path (str): The path to the file.
        row (int, optional): The row number to delete.
        rows (list, optional): A list of row numbers to delete.
        substring (str, optional): A substring to delete within the
                                   specified rows.

    Returns:
        tuple[bool, str]: Success or failure and a corresponding message.

    """
    action_in_progress = f"Deleting from {path} file"
    action_success = f"Deleted from {path} file"
    action_failed = f"Couldn't delete from {path} file"
    if substring:
        action_in_progress = f"Deleting {substring} from {path} file"
        action_success = f"Deleted {substring} from {path} file"
        action_failed = f"Couldn't delete {substring} from {path} file"

    tool_call = ToolCall(
        name="delete_file_content",
        action_in_progress=action_in_progress,
        action_success=action_success,
        action_failed=action_failed,
        message=substring,
    )
    tool_call.stream()
    try:
        p = Path(path)
        if not p.is_file():
            return False, f"Error: File '{path}' does not exist."

        lines = p.read_text(encoding="utf-8").splitlines(True)
        total_lines = len(lines)

        if substring is not None:
            target_rows = range(total_lines)
            if rows is not None:
                target_rows = rows
            elif row is not None:
                target_rows = [row]

            modified_rows = []
            for r in target_rows:
                if r < total_lines and substring in lines[r]:
                    lines[r] = lines[r].replace(substring, "")
                    modified_rows.append(r)

            if not modified_rows:
                return True, f"No occurrences of '{substring}' found to delete."

            p.write_text("".join(lines), encoding="utf-8")
            return (
                True,
                "Successfully removed "
                f"'{substring}' from rows {modified_rows} in '{path}'.",
            )

        elif rows is not None:
            rows_to_delete = sorted({r for r in rows if r < total_lines}, reverse=True)
            if not rows_to_delete:
                return True, "No rows were within range to delete."
            for r in rows_to_delete:
                del lines[r]
            p.write_text("".join(lines), encoding="utf-8")
            return True, f"Successfully deleted rows {rows_to_delete} from '{path}'."

        elif row is not None:
            if row >= total_lines:
                return False, f"Error: Row {row} is out of range."
            del lines[row]
            p.write_text("".join(lines), encoding="utf-8")
            return True, f"Successfully deleted row {row} from '{path}'."

        else:
            p.write_text("")
            return True, f"Successfully cleared all content from '{path}'."

    except PermissionError:
        return False, f"Error: No permission to modify file '{path}'."
    except Exception as e:
        return False, f"Error deleting content: {e}"
