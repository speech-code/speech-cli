import logging
import traceback
from collections.abc import Coroutine, Iterable
from logging.config import dictConfig
from pathlib import Path

from langchain_core.messages import AIMessageChunk, ToolMessage
from langgraph.types import Interrupt
from textual import work
from textual.app import App, ComposeResult, SystemCommand
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Static
from textual_autocomplete import AutoComplete

from speech_cli.agents import Generator, Translator
from speech_cli.config import LOGGING_CONFIG, api_config
from speech_cli.core.tool_call import ToolCall

from .screens import APIConfigModal, SettingsScreen
from .widgets import AgentResponse, ShowGraphInterrupt

logger = logging.getLogger(__name__)


class SpeechCLI(App):
    """Speech CLI tool."""

    SCREENS = {"settings": SettingsScreen, "api_config_modal": APIConfigModal}
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    CSS_PATH = "styles.tcss"

    _models = [
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    ]

    _generator = Generator()
    _translator = Translator()
    _currently_running_agent: Coroutine | None = None
    _current_agent_response_widget: AgentResponse | None = None

    def generate_prd(self):
        """Generate PRD file from HLC."""
        pass

    def _get_hlc(self) -> str:
        """Get the HLC.json file in the working directory."""
        file = Path.cwd() / "HLC.json"

        if file.exists():
            with file.open(encoding="utf-8") as f:
                content = f.read()

            return content

    def update_agent_response_widget(
        self,
        agent_response: AIMessageChunk | ToolMessage | Interrupt | ToolCall,
    ) -> bool:
        """Update the widget with the content."""
        _continue = True

        logger.debug("The agent response: %r", agent_response)
        if isinstance(agent_response, AIMessageChunk):
            if self._current_agent_response_widget.create_new_ai_message_widget:
                # Reseting the ai message to an empty string.
                self._current_agent_response_widget.ai_message = ""

            self._current_agent_response_widget.ai_message += agent_response.content
        elif isinstance(agent_response, ToolMessage | ToolCall):
            self._current_agent_response_widget.tool_call_message = agent_response
        elif isinstance(agent_response, Interrupt):
            self._current_agent_response_widget.graph_interrupt = agent_response

            _continue = False

        self.chat_area.scroll_end()

        return _continue

    async def run_translator(self, user_input: str | dict) -> bool:
        """Execute translator agent."""
        self._currently_running_agent = self.run_translator
        async for agent_response in self._translator.run(initial_state=user_input):
            close_execution = self.update_agent_response_widget(agent_response)

        return close_execution

    async def run_generator(self, user_input: str | dict) -> bool:
        """Execute generator agent.

        Returns True if the generator agent responded, False otherwise.

        Args:
            user_input (str): The user input.
            agent_response_widget (AgentResponse): The widget to update.

        Returns:
            bool: Whether the widget was updated or not, i.e. the agent responded

        """
        self._currently_running_agent = self.run_generator
        async for agent_response in self._generator.run(initial_state=user_input):
            continue_execution = self.update_agent_response_widget(agent_response)

        if continue_execution:
            if hlc_file := self._get_hlc():
                return await self.run_translator(hlc_file)

            self.chat_box.enable_messages(Input.Submitted)
            self._current_agent_response_widget = None
            return False

        return continue_execution

    @work(exclusive=True)
    async def agents_executor(self, user_input: str):
        """Execute translator and generator agents asynchronously as a worker.

        Serves as the bridge between the agents and ui.
        """
        if not self._current_agent_response_widget:
            self.chat_box.value = ""
            self.chat_box.disable_messages(Input.Submitted)
            user_message = Horizontal(
                Static(content=user_input, classes="userMessage"),
                classes="userMessageContainer",
            )
            await self.chat_area.mount(user_message)
            self.chat_area.scroll_end()

            if user_input == "/prd":
                return self.generate_prd()

            self._current_agent_response_widget = AgentResponse()
            await self.chat_area.mount(self._current_agent_response_widget)
            self.chat_area.scroll_end()

        try:
            if self._currently_running_agent:
                close_execution = await self._currently_running_agent(user_input)
            else:
                close_execution = await self.run_generator(user_input)
        except ConnectionError as e:
            self._current_agent_response_widget.error_message = (
                "Connection error, make sure you are connected to the internet!"
            )
            logger.error("Connection Error: %s\n%s", e, traceback.format_exc())
            self._current_agent_response_widget = None
            self.chat_box.enable_messages(Input.Submitted)
        except Exception as e:
            self._current_agent_response_widget.error_message = (
                "Unknown error encountered, please try again!"
            )
            logger.error("Unknown Exception: %s\n%s", e, traceback.format_exc())
            self._current_agent_response_widget = None
            self.chat_box.enable_messages(Input.Submitted)
        else:
            if close_execution:
                self._currently_running_agent = None
                self._current_agent_response_widget = None
                self.chat_box.enable_messages(Input.Submitted)

        self.chat_area.scroll_end()

    async def on_show_graph_interrupt_response(
        self, event: ShowGraphInterrupt.Response
    ):
        """Continue agent execution after human response."""
        self.agents_executor([event.human_response])

    async def on_mount(self) -> None:
        """Display app title and sub-title on app mount."""
        self.title = "Speech CLI"
        self.sub_title = "From Natural Language to Code"

        if not api_config.configured():
            await self.push_screen("api_config_modal")

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

    def on_input_submitted(self, event: Input.Submitted):
        """Initiate agent execution on input submission."""
        if event.value.isspace() or len(event.value) == 0:
            return

        self.agents_executor(event.value)

    def run(self):
        """Configure logging before running app."""
        dictConfig(LOGGING_CONFIG)

        return super().run()
