# Technical Workshop: Observability Without Oversharing: Privacy‑Conscious Telemetry for LLMs

This repo supports the hands‑on workshop delivered at AI_dev EU 2025 (Amsterdam).

- Talk page: https://sched.co/25TuD

In this 1-hour workshop, participants will have the opportunity to learn how to achieve robust observability for Large Language Models (LLMs) while safeguarding sensitive data. As LLMs become integral to production systems, monitoring their performance, usage, and costs is essential, and so is protecting user privacy! This session addresses these challenges using open-source tools such as OpenTelemetry + OpenLIT, and Prometheus + Grafana.

Through guided, hands-on exercises, participants will come away with practical skills in ethical AI monitoring. This workshop is designed for developers, data scientists, and AI practitioners who want to leverage open-source solutions to tackle privacy challenges in LLM deployments. Join us to gain hands-on experience and contribute to the future of responsible AI observability!

## Quick start (GitHub Codespaces)
1) Create a Codespace

Open this repo on GitHub, click the green Code button, choose the Codespaces tab, and “Create codespace on main”.

2) Wait for the dev container to finish initializing

Docker and Docker Compose are preinstalled inside the Codespace.

3) Create your env file

```bash
cp .env.example .env
```

4) Build and start the stack

```bash
make docker-up
```

5) Chat via the CLI

```bash
make docker-cli
```

Notes for providers in Codespaces:
- Ollama is already installed and running in this Codespace at http://localhost:11434. No extra setup needed. Containers access it via http://host.docker.internal:11434 (preconfigured in `docker-compose.override.yml`).
- Azure is cloud‑hosted and works great from Codespaces. See “Optional: Azure OpenAI” below.

## What you’ll use
- Ollama or Azure OpenAI backend (switch via `.env`)
- Session-based chat with rolling history
- Docker Compose stack: API, CLI (on demand), OpenTelemetry Collector, Prometheus, Tempo, Grafana
- Makefile for all common actions

## Alternative: Local Dev Container (VS Code + Docker)

Prefer running locally? You can use VS Code Dev Containers:

1) Requirements: VS Code, Docker Desktop, and the “Dev Containers” extension
2) Clone this repo and open the folder in VS Code
3) Reopen in container: View Command Palette → “Dev Containers: Reopen in Container”
4) In the dev container terminal, copy env and start the stack:

```bash
cp .env.example .env
make docker-up
make docker-cli
```

Notes for local dev:
- Ensure Ollama is running on your host (e.g., `ollama serve`) and the model (e.g., `phi3`) is available. The default `.env` uses `http://localhost:11434`; containers reach it via `host.docker.internal:11434` (preconfigured).
- If using Azure instead of Ollama, set the values in `.env` as shown below.

## Start the stack

Build and start all services in the background:

```bash
make docker-up
```

What this does:
- Builds images for the API and CLI based on `pyproject.toml`
- Starts the API (`llm-workshop-api`) on port 8000
- Starts the observability stack: OpenTelemetry Collector (4317/4318), Prometheus (9090), Tempo (3200), Grafana (3000)
- Keeps containers running in the background so you can attach logs or run the CLI when ready

Open these URLs (Codespaces will prompt to open forwarded ports):
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/healthz
- Grafana: http://localhost:3000 (anonymous admin is enabled; a default dashboard is preloaded)


## Use the terminal CLI

Once the stack is up and running, you can load the interactive chat CLI:

```bash
make docker-cli
```

This will exec into an existing CLI container if present, or run a fresh ephemeral one. Type your messages to chat with the model. Press Ctrl+C to exit.

## Configuration

Edit `.env` to choose a provider and model:

```env
# LLM Provider Selection (ollama | azure)
LLM_PROVIDER=ollama

# Ollama
OLLAMA_MODEL=phi3
OLLAMA_BASE_URL=http://localhost:11434
```

Tip for Codespaces with Ollama: the default `.env` (`OLLAMA_BASE_URL=http://localhost:11434`) is correct here, and containers are auto-wired to reach it via `host.docker.internal`.

### Optional: Azure OpenAI
Only needed if you don’t want to use Ollama. Set these in `.env`:

```env
LLM_PROVIDER=azure
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_MODEL=gpt-4o-mini
# AZURE_OPENAI_API_VERSION=2024-02-15-preview  # default
```

## Project structure

```text
.
├── apps/
│   ├── api/                  # FastAPI app
│   │   ├── main.py
│   │   ├── Dockerfile
│   │   ├── config/system_prompt.txt
│   │   ├── routers/inference.py
│   │   ├── schemas/{request.py,response.py}
│   │   ├── services/llm_client.py
│   │   └── utils/env.py
│   ├── cli/                  # Terminal chat client
│   │   ├── main.py
│   │   └── Dockerfile
│   ├── otel_col/             # OpenTelemetry Collector
│   │   ├── Dockerfile
│   │   └── otel_config.yaml
│   ├── grafana/              # Grafana config & dashboards
│   │   ├── grafana.ini
│   │   └── dashboards/llm_observability.json
│   ├── grafana_tempo/        # Tempo config
│   │   └── tempo.yaml
│   └── prometheus/           # Prometheus config
│       └── prometheus.yml
├── docker-compose.yml
├── docker-compose.override.yml
├── Makefile
├── .env.example
├── pyproject.toml
└── README.md
```

## Makefile commands

- `make help` — List available commands and descriptions
- `make docker-up` — Build (if needed) and start all services
- `make docker-logs` — Tail logs from all services
- `make docker-cli` — Start/exec the interactive CLI container
- `make docker-ps` — List services and status
- `make docker-down` — Stop and remove services
- `make docker-reset` — Stop and remove services, networks, and volumes
- `make docker-api-sh` — Open a shell inside the API container
- `make docker-logs-{api|prometheus|grafana|tempo|otelcol}` — Service‑specific logs
- `make docker-rebuild-nocache` — Rebuild images without cache

## Endpoints

- GET / — Root info
- GET /healthz — Health status (provider, model)
- POST /v1/chat — Chat endpoint (used by the CLI)

## Environment variables reference

The most relevant settings from `.env`:

- `LLM_PROVIDER` = `ollama` | `azure` (default: `ollama`)
- `OLLAMA_MODEL` (default: `phi3`)
- `OLLAMA_BASE_URL` (default: `http://localhost:11434`)
- `AZURE_OPENAI_MODEL` (example: `gpt-4o-mini`)
- `AZURE_OPENAI_ENDPOINT` (e.g., `https://your-resource.openai.azure.com/`)
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_API_VERSION` (default: `2024-02-15-preview`)
- `LOG_LEVEL` (default: `INFO`)

## Troubleshooting

- Health shows degraded: check `.env` provider settings and that the chosen backend is reachable. Then restart with `make docker-down && make docker-up`.
- Ollama in Codespaces: it should already be running at http://localhost:11434. If the first chat is slow or errors with a missing model, ensure the model (e.g., `phi3`) is available; the first use may trigger a download.
- Ports not opening: ensure Codespaces forwarded ports 8000 (API) and 3000 (Grafana). Open via the Ports tab if needed.
- Stuck containers or config changes not picked up: run `make docker-reset` to start fresh (removes volumes).
