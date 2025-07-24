.PHONY: help install run test docker-build docker-run clean

# Default target
help: ## Show this help message
	@echo "LLM Workshop API - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Setup and Installation
install: ## Install dependencies with Poetry
	poetry install --only main

install-dev: ## Install with dev dependencies
	poetry install

setup: install ## Setup environment from .env.example
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env file from .env.example"; \
		echo "📝 Please edit .env with your configuration"; \
	else \
		echo "✅ .env file already exists"; \
	fi

# Running the application
run: ## Run the API server (development mode)
	poetry run uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000

# Testing
test-api: ## Test API endpoints with curl
	@echo "🧪 Testing health endpoint..."
	@curl -s "http://localhost:8000/healthz" | python -m json.tool
	@echo "\n🧪 Testing chat endpoint..."
	@curl -s -X POST "http://localhost:8000/v1/chat" \
		-H "Content-Type: application/json" \
		-d '{"session_id": "test-session", "user_message": "Hello, how are you?"}' | python -m json.tool

# Docker
docker-build: ## Build Docker image
	docker build -t llm-workshop-api .

docker-run: ## Run Docker container
	docker run --rm -p 8000:8000 --env-file .env llm-workshop-api

docker-up: ## Start with docker-compose
	docker-compose up --build

docker-down: ## Stop docker-compose
	docker-compose down

# Ollama helpers
ollama-setup: ## Setup Ollama (pull phi3 model)
	ollama pull phi3
	@echo "✅ Phi3 model ready. Make sure 'ollama serve' is running!"

# Cleanup
clean: ## Clean cache and temporary files
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	@echo "✅ Cleaned Python cache files"

# Quick start commands
quickstart: setup ollama-setup ## Complete setup for workshop
	@echo "\n✅ Setup complete!"
	@echo "📝 Next steps:"
	@echo "  1. Edit .env file with your configuration"
	@echo "  2. Run 'ollama serve' in another terminal"
	@echo "  3. Run 'make run' to start the API"

demo: run ## Alias for 'make run' - start the demo
