from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Label

from speech_cli.config import api_config

from .widgets import ConfigureProvider


class APIConfigModal(ModalScreen):
    """Screen for user notification."""

    def compose(self) -> ComposeResult:
        """Adding child widgets to the model config screen."""
        yield Label("Configure an API to continue..")
        self.configure_provider = ConfigureProvider()
        yield self.configure_provider

        with Horizontal(id="apiConfigBtn"):
            if api_config.configured():
                yield Button("Cancel", variant="warning")

            yield Button("Save", variant="primary", name="save")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Save API configuration."""
        if event.button.name == "save":
            api_config.set_api_key(*self.configure_provider.get_values())
            await self.run_action("app.dismiss_api_config_modal")


class SettingsScreen(Screen):
    """Settings screen for allowing users to configure speech cli."""

    def compose(self) -> ComposeResult:
        """Adding child widgets to the settings screen."""
        yield ConfigureProvider()
