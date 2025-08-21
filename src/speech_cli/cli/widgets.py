import logging

from langchain_core.messages import ToolMessage
from langgraph.prebuilt.interrupt import HumanResponse
from langgraph.types import Interrupt
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import (
    Button,
    Collapsible,
    Input,
    Label,
    LoadingIndicator,
    Markdown,
    Select,
    Static,
)

from speech_cli.config import api_config
from speech_cli.core.tool_call import ToolCall

logger = logging.getLogger(__name__)


class ShowToolCall(Vertical):
    """Widget to show tool call, and result."""

    def __init__(self, tool_call: ToolCall) -> None:
        self.tool_call = tool_call

        super().__init__()

    def compose(self) -> ComposeResult:
        """Create child widgets for this widget."""
        self.collapsible = Collapsible(
            Static(f"[d]{self.tool_call.message}[/d]"),
            title=self.tool_call.action_in_progress,
        )
        yield self.collapsible

        self.tool_running_indicator = LoadingIndicator()
        yield self.tool_running_indicator

    async def update_tool_call(self, tool_message: ToolMessage):
        """Update tool call with tool message.

        Args:
            tool_message (ToolMessage): The tool final message.

        """
        if tool_message.name == self.tool_call.name:
            if tool_message.content[0]:
                self.collapsible.title = self.tool_call.action_success
                self.add_class("success")
            else:
                self.collapsible.title = self.tool_call.action_failed
                self.add_class("error")

        await self.tool_running_indicator.remove()


class _ToolArgs(Vertical):
    """Widget for displaying tool args."""

    def __init__(self, tool_args: Interrupt) -> None:
        self.tool_args: dict = tool_args

        super().__init__()

    def compose(self) -> ComposeResult:
        """Create child widgets for this widget."""
        for arg, value in self.tool_args.items():
            yield Static(f"[d][i]arg:[/i] {arg}[/d]")
            yield Static(f"[d][i]value:[/i] {value}[/d]")


class ShowGraphInterrupt(Vertical):
    """Graph interrupt widget.

    For accepting, editing, directly responding or rejecting tool execution.
    """

    class Response(Message):
        """Event sent when graph interrupt `Button` is pressed."""

        def __init__(self, human_response: HumanResponse) -> None:
            self.human_response: HumanResponse = human_response
            """The human response as a `dict`."""
            super().__init__()

    def __init__(self, graph_interrupt: Interrupt) -> None:
        self.graph_interrupt = graph_interrupt

        super().__init__()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        interrupt = self.graph_interrupt.value[0]

        yield Collapsible(
            _ToolArgs(interrupt["action_request"]["args"]),
            title=interrupt["description"],
        )
        with Horizontal(classes="graphInterruptBtns"):
            for action in interrupt["config"]:
                name = action.split("_")[1]
                yield Button(
                    label=name.capitalize(),
                    classes=name,
                    name=name,
                )

    def get_tool_args(self):
        """Retrieve the args for a tool."""
        # TODO(@Collins): Implement this to allow edit and response interrupts.
        return {}

    def on_button_pressed(self, event: Button.Pressed):
        """Create and post user response."""
        for button in self.query("Horizontal Button"):
            button.disabled = True

        human_response = HumanResponse(
            type=event.button.name, args=self.get_tool_args()
        )
        self.post_message(ShowGraphInterrupt.Response(human_response))


class AgentResponse(Vertical):
    """An agent response widget for displaying all possible agent responses."""

    ai_message: str = reactive("", init=False, layout=True)
    ai_message_widget: Markdown | None = None
    create_new_ai_message_widget: bool = True

    tool_call_message: ToolMessage | ToolCall | None = reactive(
        None, init=False, layout=True
    )
    show_tool_call_widget: ShowToolCall | None = None

    graph_interrupt: Interrupt | None = reactive(None, init=False, layout=True)

    error_message: str = reactive("", init=False, layout=True)

    def on_mount(self) -> None:
        """Display the loading indicator on mount."""
        self.loading = True

    def _ensure_widget_ready(self, create_new_ai_message_widget=False):
        """Remove loading indicator & ensure the ai message goes to the right widget."""
        if self.loading:
            self.loading = False

        self.create_new_ai_message_widget = create_new_ai_message_widget

    async def watch_ai_message(self, ai_message: str) -> None:
        """Update UI with AI message.

        Args:
            ai_message (str): The AI message.

        """
        if len(ai_message) == 0:
            return

        if self.create_new_ai_message_widget:
            self.ai_message_widget = Markdown(markdown=ai_message, classes="aiMessage")
            self._ensure_widget_ready()
            await self.mount(self.ai_message_widget)
        else:
            await self.ai_message_widget.update(ai_message)

    async def watch_tool_call_message(
        self, tool_call_message: ToolMessage | ToolCall
    ) -> None:
        """Update UI with tool call message.

        Args:
            tool_call_message (ToolMessage | ToolCall): The tool call or message.

        """
        self._ensure_widget_ready(True)

        if isinstance(tool_call_message, ToolCall):
            self.show_tool_call_widget = ShowToolCall(tool_call_message).add_class(
                "graphProcesses"
            )
            await self.mount(self.show_tool_call_widget)

        elif isinstance(tool_call_message, ToolMessage):
            if self.show_tool_call_widget:
                await self.show_tool_call_widget.update_tool_call(tool_call_message)

    async def watch_graph_interrupt(self, graph_interrupt: Interrupt) -> None:
        """Update UI with the graph interrupt.

        Args:
            graph_interrupt (Interrupt): The graph interrupt.

        """
        self._ensure_widget_ready(True)
        await self.mount(
            ShowGraphInterrupt(graph_interrupt).add_class("graphProcesses")
        )

    async def watch_error_message(self, error_message: str) -> None:
        """Update UI with connection error message.

        Args:
            error_message (str): The error message.

        """
        self._ensure_widget_ready()

        await self.mount(Label(error_message, classes="exception error"))


class ConfigureProvider(Horizontal):
    """A widget for configuring a model provider."""

    def compose(self) -> ComposeResult:
        """Composing  the widgets for this container."""
        self.provider_select = Select(
            [(provider, provider) for provider in api_config.not_configured()],
            prompt="Select provider",
            name="provider",
        )
        yield self.provider_select

        self.model_select = Select([], prompt="Select model", name="model")
        yield self.model_select

        self.api_input = Input(placeholder="Enter API Key", password=True)
        yield self.api_input

    def on_select_changed(self, event: Select.Changed) -> None:
        """Populate the available models for the selected provider."""
        if event.select.name == "provider":
            self.model_select.set_options(
                [(model, model) for model in api_config.not_configured()[event.value]],
            )

    def get_values(self) -> tuple[str, str, str]:
        """Return the given api config."""
        return self.provider_select.value, self.model_select.value, self.api_input.value
