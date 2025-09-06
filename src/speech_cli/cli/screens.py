from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Label
from textual.worker import WorkerState

from speech_cli.config import api_config

from .widgets import APIConfig

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.worker import Worker


class APIConfigModal(ModalScreen):
    """First time api configuration screen."""

    def compose(self) -> ComposeResult:
        """Adding child widgets to the model config screen."""
        yield Label("Configure an API to continue..")

        self.configure_provider = APIConfig()
        yield self.configure_provider

        with Horizontal(id="apiConfigBtn"):
            yield Button("Save", variant="primary", name="save")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Save API configuration."""
        if (
            event.button.name == "save"
            and self.configure_provider.all_widgets_has_a_value
        ):
            self.run_worker(
                api_config.configure(*self.configure_provider.get_values()),
                exclusive=True,
            )

    async def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Dismiss screen if, api configure worker is successful."""
        if event.state == WorkerState.SUCCESS:
            await self.run_action("app.pop_screen")


class SettingsScreen(Screen):
    """Settings screen for allowing users to configure speech cli."""

    def compose(self) -> ComposeResult:
        """Adding child widgets to the settings screen."""
        yield APIConfig()
