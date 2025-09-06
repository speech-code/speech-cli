from logging.config import dictConfig

from speech_cli.config import LOGGING_CONFIG

dictConfig(LOGGING_CONFIG)

from .cli import SpeechCLI  # noqa: E402


def main():
    """Instantiate and run the speech cli app.

    Returns SpeechCLI class for textual run command in dev mode support.
    """
    SpeechCLI().run()


if __name__ == "__main__":
    main()
