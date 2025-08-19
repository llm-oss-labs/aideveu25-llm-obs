#!/usr/bin/env bash
set -euo pipefail

log() { echo "[postStart] $*"; }

# If Ollama is not installed yet (e.g., onCreate failed), don't fail container start
if ! command -v ollama >/dev/null 2>&1; then
	log "ollama not found; skipping startup. Ensure onCreateCommand installed it."
	exit 0
fi

# Allow override via containerEnv; default to bind-all for dev convenience
export OLLAMA_HOST="${OLLAMA_HOST:-0.0.0.0:11434}"
MODEL="${OLLAMA_MODEL:-phi3:latest}"
PORT="${OLLAMA_HOST##*:}"

# Start Ollama service in the background if not already running
if ! pgrep -x "ollama" >/dev/null 2>&1; then
	log "Starting Ollama daemon..."
	nohup ollama serve >/tmp/ollama.log 2>&1 &
fi

# Non-blocking health check in background, then pull/warmup
(
	log "Waiting for Ollama to become ready (non-blocking)..."
	tries=0
	until curl -fsS "http://localhost:${PORT}/api/tags" >/dev/null 2>&1; do
		tries=$((tries+1))
		if [ $tries -gt 60 ]; then
			log "Ollama did not become healthy in time. See /tmp/ollama.log" >&2
			exit 0
		fi
		sleep 1
	done
	log "Ollama is ready."

	# Optionally warm up a lightweight model if it exists or can be pulled quickly
	if ! ollama list | awk 'NR>1{print $1}' | grep -q "^${MODEL}$"; then
		log "Pulling ${MODEL} (one-time)..."
		ollama pull "${MODEL}" || true
	fi

	log "Warming up ${MODEL} (non-blocking)..."
	( ollama run "${MODEL}" "Hello" >/dev/null 2>&1 || true ) &
) &

log "Post-start script completed."
