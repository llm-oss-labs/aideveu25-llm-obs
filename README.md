# LLM Observability Workshop API

A minimal, workshop-ready Python API built with FastAPI that integrates with both Ollama (local) and Azure OpenAI models. Perfect for demonstrating LLM integration patterns and observability concepts.

## 🚀 Features

- **Dual LLM Provider Support**: Seamlessly switch between Ollama and Azure OpenAI via environment variables
- **Session Management**: In-memory conversation history tracking
- **Type Safety**: Full Pydantic validation for requests and responses
- **Docker Ready**: Multi-stage build with health checks
- **Developer Friendly**: Auto-reload, API docs, and comprehensive error handling
- **Workshop Optimized**: No authentication or rate limiting for easy demos

## 📋 Prerequisites

- Python 3.11+
- Poetry (for dependency management)
- Docker (optional, for containerization)
- Ollama (if using local models)
- Azure OpenAI credentials (if using Azure)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd llm-observability-workshop
```

### 2. Install Poetry

```bash
# macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -

# Or using Homebrew (macOS)
brew install poetry
```

### 3. Install Dependencies

```bash
# Install all dependencies
poetry install

# Install only production dependencies
poetry install --only main
```

### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# For Ollama:
LLM_PROVIDER=ollama
OLLAMA_MODEL=phi3

# For Azure OpenAI:
LLM_PROVIDER=azure
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_MODEL=gpt-4o-mini
```

## 🏃‍♂️ Running the Application

### Using Poetry

```bash
# Run with auto-reload (development)
poetry run uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000

# Or use the Makefile
make run
```

### Using Docker

```bash
# Build the image
docker build -t llm-workshop-api .

# Run the container
docker run --rm -p 8000:8000 --env-file .env llm-workshop-api

# Or use docker-compose
docker-compose up --build
```

## 🧪 Testing the API

### Health Check

```bash
curl http://localhost:8000/healthz
```

### Chat Endpoint

```bash
# Send a message
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-123",
    "user_message": "Hello! What is FastAPI?"
  }'

# Continue the conversation
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-123",
    "user_message": "Can you give me an example?"
  }'
```

### Interactive API Documentation

Visit http://localhost:8000/docs for the interactive Swagger UI.

## 📁 Project Structure

```
llm-observability-workshop/
├── apps/api/
│   ├── main.py                 # FastAPI application entry point
│   ├── routers/
│   │   └── inference.py        # Chat endpoint logic
│   ├── services/
│   │   └── llm_client.py       # LLM provider abstraction
│   ├── config/
│   │   └── system_prompt.txt   # Default system prompt
│   ├── schemas/
│   │   ├── request.py          # Request models
│   │   └── response.py         # Response models
│   └── utils/
│       └── env.py              # Environment configuration
├── pyproject.toml              # Poetry configuration
├── poetry.lock                 # Locked dependencies
├── Dockerfile                  # Multi-stage Docker build
├── docker-compose.yml          # Docker compose configuration
├── .env.example                # Environment template
└── Makefile                    # Development commands
```

## 🔧 API Reference

### Endpoints

#### `GET /` - Root endpoint
Returns basic API information.

#### `GET /healthz` - Health check
Returns current status and configuration.

**Response:**
```json
{
  "status": "healthy",
  "provider": "ollama",
  "model": "phi3"
}
```

#### `POST /v1/chat` - Chat with LLM
Send a message and receive a response from the configured LLM.

**Request:**
```json
{
  "session_id": "unique-session-id",
  "user_message": "Your message here"
}
```

**Response:**
```json
{
  "session_id": "unique-session-id",
  "reply": "LLM response here"
}
```

## 🐳 Docker Support

### Building the Image

```bash
docker build -t llm-workshop-api .
```

### Running with Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🛠️ Development

### Available Make Commands

```bash
make help          # Show all available commands
make install       # Install dependencies with Poetry
make setup         # Setup environment and copy .env.example
make run           # Run the FastAPI server with auto-reload
make test          # Run tests
make lint          # Run code linting
make format        # Format code with black and isort
make clean         # Clean cache and temporary files
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=apps --cov-report=html
```

### Code Quality

```bash
# Format code
make format

# Check linting
make lint
```

## 🔍 Ollama Setup

If using Ollama as your LLM provider:

1. **Install Ollama**: Visit [ollama.com](https://ollama.com)

2. **Start Ollama service**:
   ```bash
   ollama serve
   ```

3. **Pull the Phi3 model**:
   ```bash
   ollama pull phi3
   ```

4. **Configure environment**:
   ```bash
   LLM_PROVIDER=ollama
   OLLAMA_MODEL=phi3
   ```

## 🌐 Azure OpenAI Setup

If using Azure OpenAI:

1. **Set environment variables**:
   ```bash
   LLM_PROVIDER=azure
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-api-key
   AZURE_OPENAI_MODEL=gpt-4o-mini
   ```

## 🤝 Contributing

This is a workshop project designed for learning. Feel free to:
- Add new LLM providers
- Implement observability features
- Enhance error handling
- Add authentication/authorization
- Implement persistent storage

## 📝 License

This project is for educational purposes as part of the LLM Observability Workshop.

## 🆘 Troubleshooting

### Poetry Issues

```bash
# If Poetry is not found
export PATH="$HOME/.local/bin:$PATH"

# Clear Poetry cache
poetry cache clear --all pypi

# Reinstall dependencies
rm -rf poetry.lock
poetry install
```

### Ollama Connection Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Use a different port
poetry run uvicorn apps.api.main:app --port 8001
```
