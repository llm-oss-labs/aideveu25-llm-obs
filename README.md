# 🕵️‍♂️ Observability Without Oversharing: Privacy-Conscious Telemetry for LLMs

Welcome to the hands-on workshop delivered at **AI_dev EU 2025** in Amsterdam! This repository contains everything you need to follow along.

- **Talk Page**: [https://sched.co/25TuD](https://sched.co/25TuD)

In this 1-hour workshop, you'll learn how to achieve robust observability for Large Language Models (LLMs) while safeguarding sensitive data. As LLMs become integral to production systems, monitoring their performance, usage, and costs is essential—but so is protecting user privacy! This session addresses these challenges using a powerful stack of open-source tools.

Join us to gain practical skills in ethical AI monitoring and contribute to the future of responsible AI observability!

## ✨ What You'll Use

This project provides a complete environment to explore LLM observability:

- **LLM Backend**: Switch between `Ollama` (local) or `Azure OpenAI` (cloud).
- **Chat Interface**: A session-based chat CLI with rolling history.
- **Observability Stack**:
  - **OpenTelemetry**: For generating and collecting telemetry data.
  - **Prometheus**: For metrics and alerting.
  - **Grafana Tempo**: For trace storage and retrieval.
  - **Grafana**: For beautiful, pre-configured dashboards.
- **Containerized Services**: The entire stack runs in Docker, managed with Docker Compose.
- **Simplified Workflow**: A `Makefile` provides simple commands for all common actions.

---

## 🚀 Quick Start (GitHub Codespaces)

The easiest way to get started is with GitHub Codespaces, which provides a pre-configured cloud-based development environment.

1.  **Create a Codespace**:
    - Open this repository on GitHub.
    - Click the green **< > Code** button.
    - Go to the **Codespaces** tab and click **Create codespace on main**.

2.  **Wait for Initialization**: The dev container will set up Docker and all necessary tools automatically.

3.  **Create Your Environment File**:
    ```bash
    cp .env.example .env
    ```

4.  **Build and Start the Stack**:
    ```bash
    make docker-up
    ```

5.  **Chat with the LLM**:
    ```bash
    make docker-cli
    ```

> **Note for Codespaces Users**: Ollama is pre-installed and running at `http://localhost:11434`. The containers are automatically configured to access it, so no extra setup is needed!

---

## 💻 Alternative: Local Dev Container

If you prefer to run this project locally, you can use VS Code Dev Containers. The initial setup may take longer as it builds the required Docker images on your machine.

**Requirements**:
- Visual Studio Code
- Docker Desktop
- The [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) for VS Code.

**Steps**:
1. Clone this repository and open the folder in VS Code.
2. When prompted, click **Reopen in Container**. (Or, open the Command Palette and select `Dev Containers: Reopen in Container`).
3. In the dev container's terminal, set up your environment and start the stack:
   ```bash
   cp .env.example .env
   make docker-up
   make docker-cli
   ```

> **Note for Local Dev Users**: Ensure Ollama is running on your host machine (e.g., by running `ollama serve`). The default `.env` configuration should work out-of-the-box.

---

## ▶️ How to Use the Stack

### Start All Services

This command builds the Docker images (if they don't exist) and starts all services in the background.

```bash
make docker-up
```

Once running, you can access the following services (Codespaces will prompt you to forward the ports):

- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Health Check**: [http://localhost:8000/healthz](http://localhost:8000/healthz)
- **Grafana Dashboard**: [http://localhost:3000](http://localhost:3000) (Anonymous admin is enabled, and a default dashboard is preloaded).

### Use the Terminal CLI

After the stack is running, open the interactive chat CLI:

```bash
make docker-cli
```

This command will either attach to an existing CLI container or create a new one. Type your messages to chat with the model, and press `Ctrl+C` to exit.

---

## ⚙️ Configuration

You can customize the application by editing the `.env` file.

### LLM Provider

Choose between `ollama` (default) and `azure`.

```env
# LLM Provider Selection (ollama | azure)
LLM_PROVIDER=ollama

# --- Ollama Settings ---
OLLAMA_MODEL=phi3
OLLAMA_BASE_URL=http://localhost:11434
```

### Optional: Azure OpenAI

If you want to use Azure, update your `.env` file with the following settings:

```env
LLM_PROVIDER=azure

# --- Azure OpenAI Settings ---
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_MODEL=gpt-4o-mini
# AZURE_OPENAI_API_VERSION=2024-02-15-preview  # (Default)
```

---

## 🔍 Project Details

<details>
<summary><strong>📂 Project Structure</strong></summary>

```
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
</details>

<details>
<summary><strong>📜 Makefile Commands</strong></summary>

- `make help`: List all available commands.
- `make docker-up`: Build and start all services.
- `make docker-logs`: Tail logs from all services.
- `make docker-cli`: Start the interactive CLI container.
- `make docker-ps`: List running services.
- `make docker-down`: Stop and remove all services.
- `make docker-reset`: Nuke the entire stack (services, networks, and volumes).
- `make docker-api-sh`: Open a shell inside the API container.
- `make docker-rebuild-nocache`: Rebuild images without using the cache.
</details>

<details>
<summary><strong>🌐 API Endpoints</strong></summary>

- `GET /`: Root info.
- `GET /healthz`: Health status (provider, model).
- `POST /v1/chat`: The main chat endpoint used by the CLI.
</details>

<details>
<summary><strong>🔑 Environment Variables</strong></summary>

The most relevant settings from `.env`:

- `LLM_PROVIDER`: `ollama` | `azure` (default: `ollama`)
- `OLLAMA_MODEL`: (default: `phi3`)
- `OLLAMA_BASE_URL`: (default: `http://localhost:11434`)
- `AZURE_OPENAI_MODEL`: (example: `gpt-4o-mini`)
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_API_VERSION`: (default: `2024-02-15-preview`)
- `LOG_LEVEL`: (default: `INFO`)
</details>

---

## 🛠️ Troubleshooting

- **Health Check Degraded**: Check your `.env` provider settings and ensure the chosen backend (Ollama or Azure) is reachable. Restart the stack with `make docker-down && make docker-up`.
- **Ollama in Codespaces**: The first chat may be slow if the model (`phi3`) needs to be downloaded.
- **Ports Not Opening**: If ports 8000 (API) or 3000 (Grafana) aren't forwarded in Codespaces, open them manually from the **Ports** tab.
- **Stuck Containers**: If something seems wrong, run `make docker-reset` to completely reset the environment.

---

## 📄 License

This project is licensed under the terms of the [LICENSE](LICENSE) file.
