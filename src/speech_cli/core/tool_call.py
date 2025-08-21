from dataclasses import dataclass


@dataclass
class ToolCall:
    """An object for writing tool calls to graph stream."""

    name: str
    """Name of the tool."""

    action_in_progress: str
    """The action being carried out by the tool."""

    action_success: str
    """The action carried out by the tool."""

    action_failed: str
    """The action carried out by the tool."""

    message: str
    """Message to display in a collapsible."""

    def stream(self):
        """Stream this tool call."""
        from langgraph.config import get_stream_writer

        writer = get_stream_writer()

        if writer:
            writer((self,))
