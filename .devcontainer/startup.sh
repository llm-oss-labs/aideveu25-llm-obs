#!/usr/bin/env bash
set -euo pipefail

log() { echo "[startup] $*"; }

# If Ollama is not installed yet (e.g., postCreate failed), don't fail container start
if ! command -v ollama >/dev/null 2>&1; then
	log "ollama not found; skipping startup. Ensure postCreateCommand installed it."
	exit 0
fi

export OLLAMA_HOST="0.0.0.0:11434"

# Start Ollama service in the background if not already running
if ! pgrep -x "ollama" >/dev/null 2>&1; then
	log "Starting Ollama daemon..."
	nohup ollama serve >/tmp/ollama.log 2>&1 &
fi

# Wait for Ollama API to be reachable (default port 11434)
log "Waiting for Ollama to become ready..."
tries=0
until curl -fsS http://localhost:11434/api/tags >/dev/null 2>&1; do
	tries=$((tries+1))
	if [ $tries -gt 60 ]; then
		log "Ollama did not become healthy in time. See /tmp/ollama.log" >&2
		exit 1
	fi
	sleep 1
done

log "Ollama is ready."

# Optionally warm up a lightweight model if it exists or can be pulled quickly
MODEL="phi3:latest"

if ! ollama list | awk 'NR>1{print $1}' | grep -q "^${MODEL}$"; then
	log "Pulling ${MODEL} (one-time)..."
	ollama pull "${MODEL}" || true
fi

log "Warming up ${MODEL} (one-time, non-blocking)..."
# Run a tiny prompt to ensure the model is loaded once; ignore output
( ollama run "${MODEL}" "Hello" >/dev/null 2>&1 || true ) &

log "Startup script completed."
