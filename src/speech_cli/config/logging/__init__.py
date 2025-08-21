from speech_cli.config import app_config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": """{asctime} | {levelname} | '{message}'. Line no: {lineno:d} in
            {pathname}""",
            "style": "{",
        },
        "simple": {
            "format": """{asctime} | {levelname} | '{message}'""",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_true": {
            "()": "speech_cli.config.logging.filters.RequireDebugTrue",
        },
        "require_debug_false": {
            "()": "speech_cli.config.logging.filters.RequireDebugFalse",
        },
        "allow_only_debug_logs": {
            "()": "speech_cli.config.logging.filters.AllowOnlyDebugLogs",
        },
    },
}

if app_config.debug:
    LOGGING_CONFIG["handlers"] = {
        "debug_log_file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filters": ["require_debug_true", "allow_only_debug_logs"],
            "formatter": "verbose",
            # Creates a file with name speech.log in the base directory
            "filename": ".speech/debug.log",
        },
        "warning_log_file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filters": ["require_debug_true"],
            "formatter": "verbose",
            # Creates a file with name speech.log in the base directory
            "filename": ".speech/warning.log",
        },
    }
    LOGGING_CONFIG["loggers"] = {
        "speech_cli": {
            "handlers": [
                "debug_log_file",
                "warning_log_file",
            ],
            "level": "DEBUG",
        },
    }
else:
    LOGGING_CONFIG["handlers"] = {
        "prod_log_file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filters": ["require_debug_false"],
            "formatter": "simple",
            # Creates a file with name speech.log in the base directory
            "filename": ".speech/speech.log",
        },
    }
    LOGGING_CONFIG["loggers"] = {
        "": {
            "handlers": [
                "prod_log_file",
            ],
            "level": "ERROR",
        },
    }
