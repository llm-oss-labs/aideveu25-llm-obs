.PHONY: docker-api-sh docker-build docker-cli docker-down docker-logs docker-logs-api docker-logs-grafana docker-logs-otelcol docker-logs-prometheus docker-logs-tempo docker-ps docker-pull docker-rebuild-nocache docker-restart docker-reset docker-up help test-api

DOCKER ?= docker
DC ?= docker compose

# Default target
help: ## List available commands and descriptions
	@echo "LLM Workshop API - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Docker
docker-up: ## Build (if needed) and start all services in the background
	$(DC) down && $(DC) up --build -d

docker-build: ## Build all Docker images defined in docker-compose
	$(DC) build

docker-pull: ## Pull service images from registries (no build)
	$(DC) pull

docker-down: ## Stop and remove services, network, and anonymous volumes
	$(DC) down

docker-logs: ## Tail logs from all services (press Ctrl+C to stop)
	$(DC) logs -f

docker-cli: ## Start or exec into the interactive CLI (compose-managed)
	@if [ -n "$$($(DC) ps -q llm-workshop-cli)" ]; then \
		echo "Running CLI inside existing llm-workshop-cli container..."; \
		$(DC) exec -it llm-workshop-cli python main.py; \
	else \
		echo "🚀 Starting llm-workshop-cli..."; \
		$(DC) run --rm llm-workshop-cli; \
	fi

# Convenience & debugging
docker-ps: ## List compose services and status
	$(DC) ps

docker-restart: ## Restart all services in place (no rebuild)
	$(DC) restart

docker-reset: ## Stop and remove services, networks, and volumes (fresh start)
	$(DC) down -v

docker-rebuild-nocache: ## Rebuild images without cache
	$(DC) build --no-cache

docker-api-sh: ## Open a shell inside the API container
	$(DC) exec -it llm-workshop-api /bin/bash

# Service-specific logs
docker-logs-api: ## Tail API logs
	$(DC) logs -f llm-workshop-api

docker-logs-prometheus: ## Tail Prometheus logs
	$(DC) logs -f prometheus

docker-logs-grafana: ## Tail Grafana logs
	$(DC) logs -f grafana

docker-logs-tempo: ## Tail Tempo logs
	$(DC) logs -f tempo

docker-logs-otelcol: ## Tail OpenTelemetry Collector logs
	$(DC) logs -f otelcol

# Testing
test-api: ## Smoke-test the chat API endpoint with a sample request
	@echo "\n🧪 Testing chat endpoint..."
	@curl -s -X POST "http://localhost:8000/v1/chat" \
		-H "Content-Type: application/json" \
		-d '{"session_id": "test-session", "user_message": "Hello, how are you?"}' | python -m json.tool
