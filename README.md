# LLM Observability Workshop

A minimal FastAPI + LangChain and terminal CLI for LLM integration demos. Supports Ollama (local) and Azure OpenAI, with session-based chat, and Docker/Poetry dev flows.

## Features
- Ollama or Azure OpenAI backend (switch via `.env`)
- Session-based chat with rolling history
- Terminal chat CLI (local or Docker)
- Docker Compose for API, CLI, and observability
- Makefile for common dev/test/build tasks

## Quickstart

### 1. Clone & Install

```bash
git clone https://github.com/joaquinrz/llm-observability-workshop.git
cd llm-observability-workshop
poetry install
cp .env.example .env  # then edit .env for your provider
```

### 2. Run API (dev mode)

```bash
make run
# or
poetry run uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Run CLI (local)

```bash
make cli
# or
poetry run python apps/cli/main.py
```

### 4. Run with Docker Compose (Recommended)

```bash
docker compose up --build -d
# or
make docker-up
```

API: http://localhost:8000  
CLI: `docker compose run --rm llm-workshop-cli`

## API Endpoints

- `GET /` — Root info
- `GET /healthz` — Health check (status, provider, model)
- `POST /v1/chat` — Chat (JSON: `session_id`, `user_message`)

### Example: Health Check

```bash
curl -s http://localhost:8000/healthz | python -m json.tool
```

### Example: Chat

```bash
curl -s -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-session", "user_message": "Hello!"}' | python -m json.tool
```

## Project Structure

```text
llm-observability-workshop/
├── apps/api/           # FastAPI app (main.py, routers, services, schemas, config)
│   └── Dockerfile      # API Docker build
├── apps/cli/           # Terminal chat client (main.py, Dockerfile)
├── apps/otel_col/      # OpenTelemetry collector config
├── pyproject.toml      # Poetry config (shared)
├── docker-compose.yml  # Compose for API, CLI, otel
├── Makefile            # Dev/build/test helpers
├── .env.example        # Env template
└── ...
```

## Makefile Highlights

- `make run` — Start API (dev, reload)
- `make cli` — Run CLI locally
- `make docker-up` — Start all services (API, CLI, otel)
- `make docker-cli` — Run CLI in Docker
- `make test-api` — Smoke test root & chat endpoints
- `make format` / `make lint` — Code quality
- `make clean` — Remove Python cache

## Provider Setup

### Ollama (local)
1. [Install Ollama](https://ollama.com)
2. Start the server:

   ```bash
   ollama serve
   ```

3. Pull the model:

   ```bash
   ollama pull phi3
   ```

4. Set in `.env`:

   ```text
   LLM_PROVIDER=ollama
   OLLAMA_MODEL=phi3
   ```

### Azure OpenAI
1. Set in `.env`:

   ```text
   LLM_PROVIDER=azure
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-api-key
   AZURE_OPENAI_MODEL=gpt-4o-mini
   ```

## Troubleshooting

- **Health check fails:** Check `.env` and provider status, then restart API.
- **Ollama not running:** `ollama serve` and `ollama pull phi3`.
- **Port in use:** Change port in `.env` and Makefile.
- **Poetry issues:**

  ```bash
  export PATH="$HOME/.local/bin:$PATH"
  poetry cache clear --all pypi
  rm poetry.lock && poetry install
  ```

## License

Educational use for LLM Observability Workshop.
