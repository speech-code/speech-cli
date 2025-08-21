import logging
import subprocess

from speech_cli.core.tool_call import ToolCall

logger = logging.getLogger(__name__)


def run_javascript_test(file_path: str) -> dict:
    """Run a javascript test file and returns the result.

    Args:
        file_path: The path to the javascript test file.

    Returns:
        A dictionary with the test result.

    """
    tool_call = ToolCall(
        name="run_javascript_test",
        action_in_progress="Running javascript test",
        action_success="Javascript test passed",
        action_failed="Javascript test failed",
        message=file_path,
    )
    tool_call.stream()
    command = ["jest", file_path]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr
