import logging

from speech_cli.config import app_config


class RequireDebugTrue(logging.Filter):
    """Filter to allow logs during development."""

    def filter(self, _):
        """Filter method to return the debug config value."""
        return app_config.debug


class RequireDebugFalse(logging.Filter):
    """Filter to allow logs during production."""

    def filter(self, _):
        """Filter method to return the negated debug config value."""
        return not app_config.debug


class AllowOnlyDebugLogs(logging.Filter):
    """Custom filter to allow only debug level logs."""

    def filter(self, record):
        """Filter method to check if the log level is DEBUG."""
        return record.levelno == logging.DEBUG
