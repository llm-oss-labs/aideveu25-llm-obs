#!/usr/bin/env bash

# Fail fast and show commands
set -euxo pipefail

# Use an in-project virtual environment at .venv/
# This aligns with VS Code setting python.defaultInterpreterPath
poetry config virtualenvs.in-project true

# Install Python dependencies from pyproject.toml/poetry.lock
# --no-interaction avoids prompts during automated prebuilds
poetry install --no-interaction

# Install Ollama system-wide inside the container
# - curl downloads the installer; sudo -E preserves env (e.g., proxy)
# - "|| true" prevents the whole setup from failing if Ollama install has transient issues
curl -fsSL https://ollama.com/install.sh | sudo -E sh || true

# Prune Poetry/pip caches to keep the image/container smaller
rm -rf ~/.cache/pip ~/.cache/pypoetry || true
