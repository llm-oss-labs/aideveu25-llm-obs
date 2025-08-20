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

# Check if Ollama is already running
if pgrep -x "ollama" >/dev/null 2>&1; then
    log "Ollama is already running"
else
    log "Starting Ollama daemon..."
    # Start Ollama in a more persistent way
    nohup ollama serve >/tmp/ollama.log 2>&1 &
    OLLAMA_PID=$!
    
    # Give it a moment to start
    sleep 2
        
    log "Ollama daemon started with PID $OLLAMA_PID"
fi

# Wait for Ollama to become ready (with timeout)
log "Waiting for Ollama to become ready..."
tries=0
max_tries=30
until curl -fsS "http://localhost:${PORT}/api/tags" >/dev/null 2>&1; do
    tries=$((tries+1))
    if [ $tries -gt $max_tries ]; then
        log "Ollama did not become healthy in time. Check /tmp/ollama.log"
        cat /tmp/ollama.log
        exit 1
    fi
    log "Attempt $tries/$max_tries - waiting..."
    sleep 2
done

log "Ollama is ready!"

# Ensure the model is available
if ! ollama list | awk 'NR>1{print $1}' | grep -q "^${MODEL%:*}"; then
    log "Pulling ${MODEL} (this may take a while)..."
    ollama pull "${MODEL}" || {
        log "Failed to pull model ${MODEL}"
        exit 1
    }
fi

# Test the model
log "Testing ${MODEL}..."
echo "Hello, how are you?" | ollama run "${MODEL}" >/dev/null 2>&1 || {
    log "Model test failed, but continuing..."
}

log "Post-start script completed successfully."
