from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from langchain_core.messages import AIMessageChunk, ToolMessage
from langgraph.types import Interrupt
from textual import work
from textual.app import App, SystemCommand
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Static
from textual_autocomplete import AutoComplete

from speech_cli.agents import AgentsGraph
from speech_cli.config import api_config
from speech_cli.core.tool_call import ToolCall

from .screens import APIConfigModal, SettingsScreen
from .widgets import AgentResponse

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Any

    from textual.app import ComposeResult

    from .widgets import ShowGraphInterrupt


logger = logging.getLogger(__name__)


class SpeechCLI(App):
    """Speech CLI tool."""

    SCREENS = {"settings": SettingsScreen}
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    CSS_PATH = "styles.tcss"

    _current_agent_response_widget: AgentResponse | None = None

    async def on_mount(self) -> None:
        """Display app title and sub-title on app mount."""
        self.title = "Speech CLI"
        self.sub_title = "From Natural Language to Code"

        if not api_config.configured:
            await self.push_screen(APIConfigModal())

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()

        with Container():
            self.chat_area = VerticalScroll(id="chatArea")
            yield self.chat_area

            self.chat_box = Input(
                id="chatBox", placeholder="What are we building?", type="text"
            )
            yield self.chat_box

            yield AutoComplete(self.chat_box, candidates=["/code", "/prd", "/continue"])

        yield Footer()

    async def app_settings(self):
        """Push the settings screen."""
        await self.push_screen("settings")

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        """Adding a settings command."""
        yield from super().get_system_commands(screen)
        yield SystemCommand("Settings", "Manage Speech CLI settings", self.app_settings)

    def action_toggle_dark(self) -> None:
        """Toggle theme mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_quit(self) -> None:
        """Cancel all workers upon exit from user."""
        for worker in self.app.workers:
            worker.cancel()

        return super().action_quit()

    async def action_dismiss_api_config_modal(self):
        """Dismiss API config modal."""
        await self.pop_screen()

    def update_agent_response_widget(
        self,
        agent_response: AIMessageChunk | ToolMessage | Interrupt | ToolCall,
    ) -> None:
        """Update the widget with the content."""
        if isinstance(agent_response, AIMessageChunk):
            if self._current_agent_response_widget.create_new_ai_message_widget:
                # Resetting the ai message to an empty string.
                self._current_agent_response_widget.ai_message = ""

            self._current_agent_response_widget.ai_message += agent_response.content
        elif isinstance(agent_response, ToolMessage | ToolCall):
            self._current_agent_response_widget.tool_call_message = agent_response
        elif isinstance(agent_response, Interrupt):
            self._current_agent_response_widget.graph_interrupt = agent_response

    @work(exclusive=True)
    async def execute_agents(self, user_input: str | list[dict[str, Any]]):
        """Initiate the agent workflow, by calling the agents executor.

        Args:
            user_input (str | list[dict]): The input to the agents executor.

        """
        with AgentsGraph(user_input) as graph:
            async for agent_response in graph.run():
                self.update_agent_response_widget(agent_response)
                self.chat_area.scroll_end()

        if error := graph.error:
            self._current_agent_response_widget.error_message = error

        if not graph.interrupted:
            self._current_agent_response_widget = None
            self.chat_box.enable_messages(Input.Submitted)

        self.chat_area.scroll_end()

    def on_show_graph_interrupt_response(self, event: ShowGraphInterrupt.Response):
        """Continue agent execution after human response."""
        self.execute_agents([event.human_response])

    async def on_input_submitted(self, event: Input.Submitted):
        """Initiate agent execution on input submission."""
        user_input = event.value

        if user_input.isspace() or len(event.value) == 0:
            return

        self.chat_box.value = ""
        self.chat_box.disable_messages(Input.Submitted)

        await self.chat_area.mount(
            Horizontal(
                Static(content=user_input, classes="userMessage"),
                classes="userMessageContainer",
            )
        )

        self._current_agent_response_widget = AgentResponse()
        await self.chat_area.mount(self._current_agent_response_widget)
        self.chat_area.scroll_end()

        self.execute_agents(user_input)

    def run(self):
        """Configure logging before running app."""
        return super().run()
