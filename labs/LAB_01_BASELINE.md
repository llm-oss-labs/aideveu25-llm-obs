# Lab 1: Baseline Setup 🏗️
**Duration**: 30 minutes  
**Difficulty**: Beginner  

## 🎯 Objective
Set up and run a basic LLM chat application without observability. This establishes our baseline and helps you understand the core application architecture before adding telemetry.

## 🎓 What You'll Learn
- LLM application fundamentals and architecture
- FastAPI backend structure and API endpoints
- Docker Compose service orchestration
- LLM provider configuration (Ollama vs Azure OpenAI)
- Session-based chat functionality

## 📋 Prerequisites
- Completed workshop setup (GitHub Codespaces or local Dev Container)
- Basic understanding of Docker and APIs

## 🧪 Lab Steps

### Step 1: Reset to Baseline (5 minutes)
First, we'll apply the reset patch to remove all observability components and start with a clean baseline.

```bash
# Apply the reset patch to remove observability
git apply labs/patches/lab1-reset-to-baseline.patch
```

**🔍 What This Does:**
- Removes OpenLIT SDK instrumentation
- Removes OpenTelemetry Collector configuration
- Removes Grafana, Prometheus, and Tempo services
- Removes PII masking functionality
- Strips the application down to its core: API + CLI

### Step 2: Examine the Clean Architecture (10 minutes)

Let's explore what remains after the reset:

```bash
# Check the simplified Docker Compose
cat docker-compose.yml
```

**🔍 Analysis Questions:**
1. How many services are now defined?
2. What ports are exposed by each service?
3. Which service depends on which?

```bash
# Examine the API structure
tree apps/api/
```

**Key Components:**
- `main.py` - FastAPI application setup and lifespan management
- `routers/inference.py` - Chat endpoint implementation
- `services/llm_client.py` - Unified LLM provider client
- `schemas/` - Request/response models
- `utils/env.py` - Configuration management

```bash
# Look at the simplified API main file
cat apps/api/main.py
```

**🔍 Notice What's Missing:**
- No `import openlit` 
- No `openlit.init()` call
- Simplified error handling

### Step 3: Configure Your LLM Provider (5 minutes)

You can choose between Ollama (local) or Azure OpenAI (cloud).

#### Option A: Ollama (Recommended for Workshop)
```bash
# Copy the example environment file
cp .env.example .env

# The default configuration uses Ollama
cat .env | grep -E "(LLM_PROVIDER|OLLAMA)"
```

**Configuration:**
```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=phi3
OLLAMA_BASE_URL=http://localhost:11434
```

#### Option B: Azure OpenAI (If You Have Access)
```bash
# Edit the .env file
nano .env

# Update these values:
LLM_PROVIDER=azure
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_MODEL=gpt-4o-mini
```

### Step 4: Build and Start the Services (5 minutes)

```bash
# Build and start the API and CLI services
make docker-up
```

**🔍 Watch the Logs:**
```bash
# In a separate terminal, monitor the startup
make docker-logs
```

You should see:
- API service starting on port 8000
- LLM client initialization
- Provider connection success/failure

### Step 5: Test the Application (5 minutes)

#### Health Check
```bash
# Check API health
curl http://localhost:8000/healthz
```

**Expected Response:**
```json
{
  "status": "healthy",
  "provider": "ollama",
  "model": "phi3",
  "pii_masking_enabled": false,
  "timestamp": "2025-01-XX..."
}
```

#### Interactive Chat
```bash
# Start the CLI chat interface
make docker-cli
```

**Try These Interactions:**
1. Simple greeting: "Hello, how are you?"
2. Technical question: "Explain what Docker is"
3. Follow-up question: "What about Kubernetes?"
4. Exit with `Ctrl+C`

#### API Documentation
Open your browser to: http://localhost:8000/docs

**🔍 Explore:**
- Available endpoints
- Request/response schemas
- Try the interactive API test

## 🔍 Understanding the Architecture

### Session Management
The application uses in-memory session storage to maintain conversation context:

```bash
# Look at the session implementation
grep -A 10 "SESSION_STORE" apps/api/services/llm_client.py
```

### LLM Provider Abstraction
```bash
# Examine how providers are abstracted
grep -A 20 "def _initialize_client" apps/api/services/llm_client.py
```

**Key Insights:**
- Unified interface for different providers
- OpenAI-compatible API for consistent integration
- Provider-specific error handling

### Request Flow
1. User input → CLI client
2. CLI → FastAPI `/v1/chat` endpoint
3. FastAPI → LLM client service
4. LLM client → Provider (Ollama/Azure)
5. Response flows back through the chain

## 🧪 Experiments to Try

### 1. Multiple Sessions
Start multiple CLI instances and chat in different "sessions":
```bash
# Terminal 1
make docker-cli

# Terminal 2 (different session)
make docker-cli
```

### 2. API Testing
Use curl to test the API directly:
```bash
curl -X POST "http://localhost:8000/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session",
    "user_message": "What is machine learning?"
  }'
```

### 3. Provider Switching
If you have Azure access, try switching providers:
```bash
# Stop services
make docker-down

# Edit .env to change LLM_PROVIDER
# Restart
make docker-up
```

## ❌ Troubleshooting

### Issue: Ollama Connection Failed
```bash
# Check if Ollama is running (in Codespaces, it should be)
curl http://localhost:11434/api/version
```

**Solution**: In Codespaces, Ollama is pre-installed. For local environments, install Ollama or use Azure OpenAI.

### Issue: Port Already in Use
```bash
# Check what's using the port
sudo lsof -i :8000

# Stop any existing containers
make docker-reset
```

### Issue: Health Check Shows Degraded
Check the logs for specific error messages:
```bash
make docker-logs | grep -i error
```

## 🎯 Success Criteria
- [ ] Application builds and starts without errors
- [ ] Health check returns "healthy" status
- [ ] CLI chat works with basic questions
- [ ] API documentation is accessible
- [ ] You understand the session-based architecture

## 📚 Key Takeaways
1. **Clean Architecture**: The baseline app is simple but functional
2. **Provider Abstraction**: Same interface works with different LLM providers
3. **Session Management**: Conversations maintain context
4. **No Observability**: We have zero visibility into performance, usage, or costs
5. **Privacy**: No PII protection mechanisms in place

## 🚀 Next Steps
You now have a working LLM application! But we have no insight into:
- How many requests are being made
- How long responses take
- How many tokens are consumed
- What errors occur
- Any performance bottlenecks

In **Lab 2**, we'll add basic observability with OpenLIT and OpenTelemetry to start gathering this crucial operational data.

---

**Ready for observability?** → [Lab 2: Basic Observability](LAB_02_BASIC_OBSERVABILITY.md)