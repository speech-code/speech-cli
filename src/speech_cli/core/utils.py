import os
import platform
from typing import Any

from langchain_core.prompt_values import PromptValue
from langchain_core.prompts import ChatPromptTemplate


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
