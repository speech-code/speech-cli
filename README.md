<p align="center">
 <img src="assets/logo-light.svg#gh-light-mode-only" style="width:200px">
  <img src="assets/logo-dark.svg#gh-dark-mode-only" style="width:200px">
</p>
<p align="center">
    <em>Speech CLI, build any software instantly in natural language, directly on your local device.</em>
</p>

---

Speech CLI is a command-line application that lets you build software instantly using natural language, running directly on your local device. Describe what you want to build in plain English and Speech CLI scaffolds, generates, and automates the code and project tasks locally — no cloud dependency required.

## Related projects & important links

- Sample projects built with Speech CLI: <https://github.com/speech-code/projects>
- Speech YouTube channel: <https://www.youtube.com/@speechdotdev>

## Quick start

### Prerequisites

- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/) package manager

### Setup

Install the CLI tool directly using uv:

```bash
uv tool install git+https://github.com/speech-code/speech-cli
```

Once installed, you can run the tool from anywhere:

```bash
speech
```

#### Installing uv (if not already installed)

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

#### For Windows Users

For the best experience, use Windows Terminal instead of the legacy Command Prompt. You can install it via:

```bash
winget install --id Microsoft.WindowsTerminal -e
```

Or download it from the [Microsoft Store](https://www.microsoft.com/store/productId/9N0DX20HK701).

## Contributing

Contributions are welcome. Please read the repository's CONTRIBUTING.md at the project root for guidelines on reporting issues, proposing changes, and submitting pull requests.