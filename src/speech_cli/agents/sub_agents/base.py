from speech_cli.agents.base import BaseAgent


class BaseSubAgent(BaseAgent):
    """Base class for all sub agents."""

    def __init_subclass__(cls):
        """Build the sub agent for every sub class."""
        super().__init_subclass__(sub_agent=True)
