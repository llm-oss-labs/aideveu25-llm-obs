.PHONY: lab1 lab2 lab3 lab4 status clean help docker-up docker-build docker-pull docker-down docker-logs docker-cli docker-ps docker-restart docker-reset docker-rebuild-nocache docker-api-sh docker-logs-api docker-logs-prometheus docker-logs-grafana docker-logs-tempo docker-logs-otelcol test-api

LAB_TEMPLATES = labs/templates
DOCKER ?= docker
DC ?= docker compose

# Default target
help: ## List available commands and descriptions
	@echo "🧪 LLM Observability Workshop - Lab Management"
	@echo ""
	@echo "📚 Lab Commands:"
	@echo "  make lab1      - Switch to Lab 1 (Baseline - No observability)"
	@echo "  make lab2      - Switch to Lab 2 (Basic observability with OpenLIT)"
	@echo "  make lab3      - Switch to Lab 3 (Full observability stack)"
	@echo "  make lab4      - Switch to Lab 4 (Privacy protection with PII masking)"
	@echo "  make status    - Show current lab configuration"
	@echo "  make clean     - Clean up observability components"
	@echo ""
	@echo "🐳 Docker Commands:"
	@echo "  make docker-up       - Build and start all services"
	@echo "  make docker-down     - Stop all services"
	@echo "  make docker-build    - Build all images"
	@echo "  make docker-pull     - Pull service images"
	@echo "  make docker-logs     - View all logs"
	@echo "  make docker-cli      - Interactive CLI"
	@echo "  make docker-ps       - List services status"
	@echo "  make docker-restart  - Restart services"
	@echo "  make docker-reset    - Full reset (remove volumes)"
	@echo "  make docker-rebuild-nocache - Rebuild without cache"
	@echo "  make docker-api-sh   - Shell into API container"
	@echo "  make docker-logs-*   - Individual service logs"
	@echo "  make test-api        - Test the API endpoint"
	@echo ""
	@echo "📖 For detailed instructions, see labs/README.md"

# Lab Management Commands
lab1: clean ## Switch to Lab 1: Baseline (no observability, no PII masking)
	@echo "🔄 Switching to Lab 1: Baseline..."
	@rm -f apps/api/utils/pii_masker.py
	@cp $(LAB_TEMPLATES)/lab1/main.py apps/api/main.py
	@cp $(LAB_TEMPLATES)/lab1/inference.py apps/api/routers/inference.py
	@cp $(LAB_TEMPLATES)/lab1/pyproject.toml pyproject.toml
	@cp $(LAB_TEMPLATES)/lab1/docker-compose.yml docker-compose.yml
	@cp $(LAB_TEMPLATES)/lab1/Dockerfile apps/api/Dockerfile
	@echo "   📄 Updated main.py (removed OpenLIT)"
	@echo "   📄 Updated inference.py (removed PII masking)"
	@echo "   📄 Updated pyproject.toml (removed OpenLIT and PII dependencies)"
	@echo "   📄 Updated docker-compose.yml (basic services only)"
	@echo "   📄 Updated Dockerfile (no PII dependencies)"
	@echo "✅ Lab 1: Baseline state - Ready for basic LLM integration!"

lab2: lab1 ## Switch to Lab 2: Basic Observability (OpenLIT + OTEL Collector)
	@echo "🔄 Switching to Lab 2: Basic Observability..."
	@cp $(LAB_TEMPLATES)/lab2/main.py apps/api/main.py
	@cp $(LAB_TEMPLATES)/lab2/pyproject.toml pyproject.toml
	@cp $(LAB_TEMPLATES)/lab2/docker-compose.yml docker-compose.yml
	@mkdir -p apps/otel_col
	@cp $(LAB_TEMPLATES)/lab2/otel_config.yaml apps/otel_col/otel_config.yaml
	@cp $(LAB_TEMPLATES)/lab2/otel_Dockerfile apps/otel_col/Dockerfile
	@echo "   📄 Updated main.py (added OpenLIT integration)"
	@echo "   📄 Updated pyproject.toml (added OpenLIT dependency)"
	@echo "   📄 Updated docker-compose.yml (added OTEL Collector)"
	@echo "   📁 Created apps/otel_col/ with configuration"
	@echo "✅ Lab 2: Basic observability with OpenLIT + OTEL Collector!"

lab3: lab2 ## Switch to Lab 3: Full Observability (Grafana + Prometheus + Tempo)
	@echo "🔄 Switching to Lab 3: Full Observability Stack..."
	@cp $(LAB_TEMPLATES)/lab3/docker-compose.yml docker-compose.yml
	@cp $(LAB_TEMPLATES)/lab3/otel_config.yaml apps/otel_col/otel_config.yaml
	@mkdir -p apps/grafana/dashboards apps/grafana/provisioning/{dashboards,datasources,org}
	@mkdir -p apps/grafana_tempo apps/prometheus
	@cp -r $(LAB_TEMPLATES)/lab3/grafana/* apps/grafana/
	@cp $(LAB_TEMPLATES)/lab3/tempo.yaml apps/grafana_tempo/tempo.yaml
	@cp $(LAB_TEMPLATES)/lab3/prometheus.yml apps/prometheus/prometheus.yml
	@echo "   📄 Updated docker-compose.yml (added Grafana, Prometheus, Tempo)"
	@echo "   📄 Updated OTEL config (exports to Tempo and Prometheus)"
	@echo "   📁 Created apps/grafana/ with dashboards and provisioning"
	@echo "   📁 Created apps/grafana_tempo/ with Tempo configuration"
	@echo "   📁 Created apps/prometheus/ with Prometheus configuration"
	@echo "✅ Lab 3: Full observability stack ready!"
	@echo "   🌐 Grafana will be available at http://localhost:3000"
	@echo "   📊 Prometheus at http://localhost:9090"

lab4: lab3 ## Switch to Lab 4: Privacy Protection (PII masking + full observability)
	@echo "� Switching to Lab 4: Privacy Protection..."
	@cp $(LAB_TEMPLATES)/lab4/inference.py apps/api/routers/inference.py
	@cp $(LAB_TEMPLATES)/lab4/pyproject.toml pyproject.toml
	@cp $(LAB_TEMPLATES)/lab4/Dockerfile apps/api/Dockerfile
	@mkdir -p apps/api/utils
	@cp $(LAB_TEMPLATES)/lab4/pii_masker.py apps/api/utils/pii_masker.py
	@echo "   📄 Updated inference.py (added PII masking)"
	@echo "   📄 Updated pyproject.toml (added PII dependencies)"
	@echo "   📄 Updated Dockerfile (added spaCy model download)"
	@echo "   📁 Created apps/api/utils/pii_masker.py"
	@echo "✅ Lab 4: Privacy protection with PII masking enabled!"

# Utility Commands
clean: ## Clean up observability components
	@echo "🧹 Cleaning up observability components..."
	@rm -rf apps/otel_col apps/grafana apps/grafana_tempo apps/prometheus 2>/dev/null || true
	@echo "✅ Cleaned up"

status: ## Show current lab configuration
	@echo "📊 Current Lab Configuration:"
	@echo ""
	@echo -n "OpenLIT Integration: "
	@if grep -q "import openlit" apps/api/main.py 2>/dev/null; then echo "✅ Enabled"; else echo "❌ Disabled"; fi
	@echo -n "PII Masking:         "
	@if test -f apps/api/utils/pii_masker.py; then echo "✅ Enabled"; else echo "❌ Disabled"; fi
	@echo -n "OTEL Collector:      "
	@if test -d apps/otel_col; then echo "✅ Configured"; else echo "❌ Not configured"; fi
	@echo -n "Observability Stack: "
	@if test -d apps/grafana; then echo "✅ Full Stack (Grafana + Prometheus + Tempo)"; \
	elif test -d apps/otel_col; then echo "🔶 Basic (OTEL Collector only)"; \
	else echo "❌ None"; fi
	@echo ""
	@echo "Detected Lab State:"
	@if test -f apps/api/utils/pii_masker.py && test -d apps/grafana; then echo "🎯 Lab 4: Privacy Protection"; \
	elif test -d apps/grafana; then echo "🎯 Lab 3: Full Observability"; \
	elif test -d apps/otel_col; then echo "🎯 Lab 2: Basic Observability"; \
	else echo "🎯 Lab 1: Baseline"; fi

# Docker Commands
docker-up: ## Build (if needed) and start all services in the background
	$(DC) down && $(DC) up --build -d
	@echo ""
	@echo "🚀 Services started! Available endpoints:"
	@echo "   📱 API: http://localhost:8000"
	@echo "   📚 API Docs: http://localhost:8000/docs"
	@if test -d apps/grafana; then echo "   📊 Grafana: http://localhost:3000"; fi
	@if test -d apps/prometheus; then echo "   📈 Prometheus: http://localhost:9090"; fi

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
