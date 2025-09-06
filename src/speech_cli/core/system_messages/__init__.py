from pathlib import Path

from speech_cli.core.utils import get_system_info


class _SystemMessages:
    """Retrieve the system message.

    Make sure the system message is stored in .txt file.
    And that the attribute name matches the file name.

    Example:
        >>> SystemMessages.translator  # returns TRANSLATOR.md

    """

    current_dir = Path(__file__).parent

    def _load_file(self, file: Path):
        """Extract system message from a markdown file.

        Args:
            file: Path to the markdown file

        Returns:
            str: Markdown content.

        """
        with file.open(encoding="utf-8") as f:
            content = f.read()

        return content

    def __getattr__(self, name: str):
        file = self.current_dir / f"{name.upper()}.md"

        if not file.exists():
            raise FileNotFoundError(
                f"No file named {name.upper()}.md found in the system messages"
                " directory."
            )

        if name == "translator":
            return self._load_file(file) % get_system_info()

        return self._load_file(file)


system_messages = _SystemMessages()
