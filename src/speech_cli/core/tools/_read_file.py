# ruff: noqa: PLR0911 PLR0912
import json
import logging
from pathlib import Path

from speech_cli.core.tool_call import ToolCall

logger = logging.getLogger(__name__)


def read_file(
    path: str, start_row: int = None, end_row: int = None, as_json: bool = False
) -> tuple[bool, str]:
    """Read content from a file.

    This function can read an entire file or specific lines. It also includes
    a safeguard against reading very large files. It can optionally parse the
    file content as JSON.

    Args:
        path (str): The path to the file.
        start_row (int, optional): The starting row to read from (0-based).
        end_row (int, optional): The ending row to read to (inclusive).
        as_json (bool, optional): If True, attempts to parse the file content
                                  as JSON.

    Returns:
        tuple[bool, str]: A tuple indicating success or failure and the file
                          content or an error message.

    """
    tool_call = ToolCall(
        name="read_file",
        action_in_progress=f"Reading {path} file, line: {start_row} - {end_row}",
        action_success=f"Read {path} file, line nos: {start_row} - {end_row}",
        action_failed=f"Couldn't read {path} file, line: {start_row} - {end_row}",
        message=path,
    )
    tool_call.stream()
    try:
        p = Path(path)
        if not p.exists():
            return False, f"Error: File '{path}' does not exist."
        if not p.is_file():
            return False, f"Error: '{path}' is not a file."

        if p.stat().st_size > 10 * 1024 * 1024:  # 10 MB limit
            return (
                False,
                "Warning: File is very large "
                f"({p.stat().st_size / 1024 / 1024:.2f} MB).",
            )

        with p.open(encoding="utf-8", errors="replace") as file:
            lines = file.readlines()

        if start_row is not None:
            if start_row < 0:
                return False, "Error: start_row must be non-negative."
            if end_row is None:
                if start_row >= len(lines):
                    return False, f"Error: start_row {start_row} is out of range."
                content = f"Line {start_row}: {lines[start_row]}"
            else:
                if end_row < start_row:
                    return (
                        False,
                        "Error: end_row must be greater than or equal to start_row.",
                    )
                selected_lines = lines[start_row : end_row + 1]
                content = "".join(
                    f"Line {start_row + i}: {line}"
                    for i, line in enumerate(selected_lines)
                )
        else:
            content = "".join(lines)

        if as_json:
            if start_row is not None:
                return (
                    False,
                    "Error: Cannot parse as JSON when displaying line numbers.",
                )
            try:
                parsed_json = json.loads(content)
                return True, json.dumps(parsed_json, indent=4)
            except json.JSONDecodeError as e:
                return (
                    False,
                    "Error: File content is not valid JSON. "
                    f"{e}\n\nRaw content:\n{content}",
                )

        return True, content

    except PermissionError:
        return False, f"Error: No permission to read file '{path}'."
    except Exception as e:
        return False, f"Error reading file: {e}"
