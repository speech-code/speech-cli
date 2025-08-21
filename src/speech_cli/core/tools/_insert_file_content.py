import json
import logging
from pathlib import Path

from speech_cli.core.tool_call import ToolCall

logger = logging.getLogger(__name__)


def insert_file_content(
    path: str, content: str, row: int = None, rows: list[int] = None
) -> tuple[bool, str]:
    """Insert content at specific row(s) in a file.

    This function can insert content at a single row, multiple rows, or append
    to the end of the file.

    Args:
        path (str): The path to the file.
        content (str): The content to insert.
        row (int, optional): The row number to insert at (0-based).
        rows (list, optional): A list of row numbers to insert at.

    Returns:
        tuple[bool, str]: A tuple indicating success or failure and a
                          corresponding message.

    """
    tool_call = ToolCall(
        name="insert_file_content",
        action_in_progress=f"Inserting to {path} file",
        action_success=f"Inserted to {path} file",
        action_failed=f"Couldn't insert to {path} file",
        message=content,
    )
    tool_call.stream()
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        if not p.exists():
            p.touch()

        if not isinstance(content, str):
            try:
                content = json.dumps(content, indent=4, default=str)
            except Exception as e:
                return False, f"Error: Unable to convert content to JSON string: {e}"

        if content and not content.endswith("\n"):
            content += "\n"

        lines = p.read_text(encoding="utf-8").splitlines(True)
        content_lines = content.splitlines(True)

        if rows is not None:
            rows = sorted(set(rows), reverse=True)
            for r in rows:
                if r > len(lines):
                    lines.extend(["\n"] * (r - len(lines)))
                lines[r:r] = content_lines
            p.write_text("".join(lines), encoding="utf-8")
            return True, f"Successfully inserted content at rows {rows} in '{path}'."

        elif row is not None:
            if row > len(lines):
                lines.extend(["\n"] * (row - len(lines)))
            lines[row:row] = content_lines
            p.write_text("".join(lines), encoding="utf-8")
            return True, f"Successfully inserted content at row {row} in '{path}'."

        else:
            with p.open("a", encoding="utf-8") as file:
                file.write(content)
            return True, f"Successfully appended content to '{path}'."

    except PermissionError:
        return False, f"Error: No permission to modify file '{path}'."
    except Exception as e:
        return False, f"Error inserting content: {e}"
