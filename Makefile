.PHONY: install run pull-model setup

# The default lightweight model recommended for NekoBuddy
MODEL ?= gemma4:e2b

install:
	@echo "Installing dependencies using uv..."
	uv sync

pull-model:
	@echo "Pulling recommended Ollama model ($(MODEL))..."
	ollama pull $(MODEL)

setup: install pull-model
	@echo "========================================"
	@echo "Setup complete! NekoBuddy is ready."
	@echo "Type 'make run' to start the application."
	@echo "========================================"

run:
	uv run python src/main.py
