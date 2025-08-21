import contextlib
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class AppConfig:
    """Configuration management class for Speech CLI.

    This class provides a unified interface for managing configuration settings
    by loading from both config.json and .env files. It supports both local
    project-specific configuration and global user configuration.

    Configuration Loading Priority:
    1. Local project configuration (.speech/ in current working directory)
    2. Global user configuration (~/.speech/ in user home directory)
    3. Default configuration values

    File Types Supported:
    - config.json: JSON format for structured configuration data

    Local vs Global Configuration:
    - Local: Located in .speech/ directory within your project
    - Global: Located in ~/.speech/ directory in user home
    - Local configuration takes precedence over global configuration

    """

    _default_config: dict[str, Any] = {
        "debug": False,
    }
    _config_file_name = "config.json"

    def __init__(self):
        self._project_speech_dir = Path.cwd() / ".speech"
        self._user_speech_dir = Path.home() / ".speech"
        self._project_speech_dir.mkdir(parents=True, exist_ok=True)

        self._config_data: dict[str, Any] = self._default_config | self._load_config()

        if not (self._user_speech_dir / self._config_file_name).exists():
            self.save(self._default_config, user=True)

    @property
    def all(self) -> dict[str, Any]:
        """Get all the configurations for a project."""
        return self._config_data.copy()

    def _read_config(self, config_file: Path):
        """Return json file if it exists."""
        if config_file.exists():
            with (
                contextlib.suppress(json.JSONDecodeError, OSError),
                config_file.open(encoding="utf-8") as f,
            ):
                return json.load(f)
        return {}

    def _load_config(self) -> dict[str, Any]:
        """Load user and project configuration file."""
        project_config_file = self._project_speech_dir / self._config_file_name
        user_config_file = self._user_speech_dir / self._config_file_name

        return self._read_config(user_config_file) | self._read_config(
            project_config_file
        )

    def save(self, config: dict[str, Any], user: bool = False) -> None:
        """Save current configuration to config.json file.

        Creates the .speech directory if it doesn't exist and writes
        the current configuration data to config.json in a formatted,
        human-readable JSON structure.

        Note: This method is automatically called by set() and update()
        methods, so manual calling is usually not necessary.
        """
        for key, value in config.items():
            setattr(self, key, value)

        speech_dir = self._project_speech_dir if not user else self._user_speech_dir
        speech_dir.mkdir(parents=True, exist_ok=True)
        file: Path = speech_dir / self._config_file_name

        with contextlib.suppress(OSError):
            existing_data = {}
            if file.exists():
                with (
                    file.open("r", encoding="utf-8") as f,
                    contextlib.suppress(json.JSONDecodeError),
                ):
                    existing_data = json.load(f)

            config_data = existing_data | config
            with file.open("w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

    def __getattr__(self, name: str) -> Any:
        """Allow attribute-style access to config variables."""
        if name.startswith("_"):
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            )

        if name in self._config_data:
            return self._config_data[name]

        raise AttributeError(f"Configuration '{name}' not found")

    def __setattr__(self, name: str, value: Any) -> None:
        """Allow attribute-style setting of config variables."""
        if name.startswith("_"):
            super().__setattr__(name, value)
            return

        if hasattr(self, "_config_data"):
            self._config_data[name] = value
        else:
            super().__setattr__(name, value)

    def __repr__(self) -> str:
        """Create string representation of a config instance."""
        return f"Config({self._config_data})"


app_config = AppConfig()
