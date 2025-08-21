speech-dev:
	uv pip install -e . 

speech:
	python -m speech_cli.cli

dev:
	textual run --dev speech_cli.cli:SpeechCLI

console:
	textual console