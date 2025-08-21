import logging
import subprocess
from datetime import datetime
from pathlib import Path

from speech_cli.core.tool_call import ToolCall

logger = logging.getLogger(__name__)
# List to store command history
command_history = []

# Maximum history size
MAX_HISTORY_SIZE = 50


def terminal_use(command: str) -> tuple[bool, str]:
    """Execute a command in the terminal and returns the output.

    This tool is designed to run shell-safe commands, providing a secure way to
    interact with the system's terminal. It captures and returns the standard
    output and standard error, allowing for robust error handling and output
    processing. The command history is recorded, which can be useful for
    debugging and auditing purposes.

    Args:
        command (str): The command to be executed in the terminal.

    Returns:
        tuple[bool, str]: A tuple where the first element is a boolean
                          indicating if the command was successful (True) or not
                          (False), and the second element is a string
                          containing the standard output if successful, or an
                          error message if not.

    """
    tool_call = ToolCall(
        name="terminal_use",
        action_in_progress="Executing command",
        action_success="Executed command",
        action_failed="Couldn't execute command",
        message=command,
    )
    tool_call.stream()

    try:
        working_dir = Path.cwd()
        if not working_dir.exists():
            return False, f"Directory does not exist: {working_dir}"

        result = subprocess.run(
            command,
            check=False,
            shell=True,
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutes timeout
        )

        success = result.returncode == 0
        output = result.stdout if success else result.stderr

        # Add to command history
        command_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "command": command,
                "success": success,
            }
        )
        if len(command_history) > MAX_HISTORY_SIZE:
            command_history.pop(0)

        return success, output

    except subprocess.TimeoutExpired:
        return False, "Command timed out after 10 minutes"
    except Exception as e:
        return False, f"Error executing command: {e}"


def get_command_history(count: int = 10) -> tuple[bool, str]:
    """Retrieve the recent command execution history.

    This function provides a log of the most recently executed commands, which is
    useful for reviewing past actions. Each history entry includes a timestamp,
    the command that was run, and its success status.

    Args:
        count (int, optional): The number of recent commands to retrieve.
                               Defaults to 10.

    Returns:
        tuple[bool, str]: A tuple where the first element is always True, and
                          the second element is a formatted string of the
                          command history. If no history is available, it
                          returns a message indicating that.

    """
    tool_call = ToolCall(
        name="get_command_history",
        action_in_progress="Retrieving command history",
        action_success="Retrieved command history",
        action_failed="Couldn't retrieve command history",
        message=f"Retrieved the last {count} executed commands.",
    )
    tool_call.stream()
    if len(command_history) == 0:
        return True, "No command execution history."

    count = min(count, len(command_history))
    recent_commands = command_history[-count:]

    output = f"Recent {count} command history:\n\n"
    for i, cmd in enumerate(recent_commands):
        status = "✓" if cmd["success"] else "✗"
        output += f"{i + 1}. [{status}] {cmd['timestamp']}: {cmd['command']}\n"

    return True, output
