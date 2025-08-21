import logging
import subprocess

from speech_cli.core.tool_call import ToolCall

logger = logging.getLogger(__name__)


def run_python_test(file_path: str) -> dict:
    """Run a python test file and returns the result.

    Args:
        file_path: The path to the python test file.

    Returns:
        A dictionary with the test result.

    """
    tool_call = ToolCall(
        name="run_python_test",
        action_in_progress="Running python test",
        action_success="Python test passed",
        action_failed="Python test failed",
        message=file_path,
    )
    tool_call.stream()
    command = ["python", "-m", "unittest", file_path]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr
