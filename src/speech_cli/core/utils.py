from __future__ import annotations

import logging
import os
import platform
from pathlib import Path
from typing import TYPE_CHECKING, Any

import requests
from langchain_core.prompts import ChatPromptTemplate

if TYPE_CHECKING:
    from typing import Any

    from langchain_core.prompt_values import PromptValue

logger = logging.getLogger(__name__)


def create_prompt(system_message: str, *args: str, **kwargs: Any) -> PromptValue:
    """Create a formatted prompt.

    Pass in the system message and a series of messages, you would want to include in
    the user message, all as raw strings. And specify the formatters via kwargs.

    Args:
        system_message (str): The system message for the model.
        *args (str): Messages that will form the user message.
        **kwargs (Any): The formatters.

    Returns:
        PromptValue: The formatted prompt.

    """
    prompt_template = ChatPromptTemplate.from_messages(
        [("system", system_message), ("human", args.join("\n"))]
    )

    return prompt_template.invoke(kwargs)


def get_system_info():
    """Retrieve OS and system platform information as a Markdown formatted string."""
    info = {
        "os": platform.system(),
        "os_version": platform.version(),
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
    }
    markdown = """**System Information:**

    - OS: {os}
    - OS Version: {os_version}
    - Platform: {platform}
    - Architecture: {architecture}
    - Processor: {processor}
    - CPU Count: {cpu_count}
    """.format(**info)

    return markdown


def read_hlc_file():
    """Read the HLC.json file."""
    file = Path.cwd() / "HLC.json"

    if file.exists():
        with file.open(encoding="utf-8") as f:
            content = f.read()

        return content


def connected_to_internet() -> bool:
    """Check if user has internet connectivity."""
    url = "https://google.com"
    status_code = 200

    try:
        response = requests.get(url, timeout=15)
        logger.debug("The response: %r", response)
        return response.status_code == status_code
    except Exception as _err:
        logger.debug("The response: %r", _err)
        return False
