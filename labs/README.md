# 🕵️‍♂️ LLM Observability Workshop Labs

## 🎯 Workshop Overview
This hands-on workshop teaches you how to implement comprehensive observability for Large Language Models (LLMs) while maintaining user privacy. You'll progressively build from a basic chat application to a full observability stack with privacy-conscious telemetry.

### 🎓 Learning Objectives
By the end of this workshop, you will:
- ✅ Understand the fundamentals of LLM application architecture
- ✅ Implement OpenTelemetry instrumentation for LLM applications
- ✅ Set up a complete observability stack (OpenLIT, Grafana, Prometheus, Tempo)
- ✅ Create informative dashboards for LLM metrics and traces
- ✅ Implement PII detection and masking for privacy-conscious telemetry
- ✅ Apply best practices for ethical AI monitoring

### 📋 Prerequisites
- Basic knowledge of Python and Docker
- Familiarity with REST APIs and FastAPI (helpful but not required)
- Understanding of containerization concepts
- GitHub Codespaces account OR local Docker environment

## 📚 Lab Structure

### Progressive Learning Path
| Lab | Title | Duration | Configuration | Key Learning |
|-----|-------|----------|---------------|--------------|
| [Lab 1](LAB_01_BASELINE.md) | Baseline Setup | 10 min | `make lab1` | LLM app fundamentals |
| [Lab 2](LAB_02_BASIC_OBSERVABILITY.md) | Basic Observability with OpenLIT | 15 min | `make lab2` | OpenLIT + OpenTelemetry |
| [Lab 3](LAB_03_FULL_OBSERVABILITY.md) | Full Observability Stack | 15 min | `make lab3` | Grafana + Prometheus + Tempo |
| [Lab 4](LAB_04_PRIVACY_OBSERVABILITY.md) | Privacy-Conscious Observability | 10 min | `make lab4` | PII masking with Presidio |

**Total Duration**: ~60 minutes

### How Lab Management Works

The workshop uses a **template-based system** to manage different configurations:

- **`make lab1`**: Resets to baseline application (no observability)
- **`make lab2`**: Switches to Lab 2 configuration (adds OpenLIT + OTEL Collector)  
- **`make lab3`**: Switches to Lab 3 configuration (adds Grafana, Prometheus, Tempo)
- **`make lab4`**: Switches to Lab 4 configuration (adds PII masking with Presidio)

Each `make labX` command:
1. **Builds incrementally** from the previous lab (lab1→lab2, lab2→lab3, lab3→lab4)
2. **Copies template files** from `labs/templates/labX/` to override/add to current configuration
3. **Updates configuration files** (`main.py`, `pyproject.toml`, `docker-compose.yml`, etc.)
4. **Creates necessary directories** and configurations for that lab's specific features

> **📝 Lab Progression**: 
> - `make lab1` runs `clean` first, then sets up baseline
> - `make lab2` runs `lab1` first, then adds observability components
> - `make lab3` runs `lab2` first, then adds visualization stack
> - `make lab4` runs `lab3` first, then adds PII masking
>
> This ensures each lab includes all previous features plus new ones.

**Key Files Managed:**
- `apps/api/main.py` - Application entry point (OpenLIT integration)
- `apps/api/routers/inference.py` - Chat endpoint (PII masking)
- `pyproject.toml` - Python dependencies
- `docker-compose.yml` - Service configuration
- `apps/otel_col/` - OpenTelemetry Collector configuration
- `apps/grafana/` - Grafana dashboards and provisioning
- `apps/api/utils/pii_masker.py` - PII masking utility

**Check your current status** anytime with: `make status`

> **💡 Behind the Scenes**: The lab configurations are stored as complete template files in `labs/templates/lab1/`, `labs/templates/lab2/`, etc. When you run `make lab2`, it copies these pre-configured templates to your working directory, ensuring a consistent and predictable setup for each lab.


### What You'll Build
```
Lab 1: LLM Chat App                    Lab 2: + Telemetry Collection
┌─────────────────┐                   ┌─────────────────┐
│ 💬 CLI Client   │                   │ 💬 CLI Client   │
│ 🚀 FastAPI      │                   │ 🚀 FastAPI      │ ──┐
│ 🤖 LLM Provider │                   │ 🤖 LLM Provider │   │
└─────────────────┘                   └─────────────────┘   │
                                                            │
Lab 3: + Visualization Stack          Lab 4: + Privacy Protection
┌─────────────────┐                   ┌─────────────────┐   │
│ 💬 CLI Client   │                   │ 💬 CLI Client   │   │
│ 🚀 FastAPI      │ ──┐               │ 🚀 FastAPI      │ ──┼──┐
│ 🤖 LLM Provider │   │               │ 🔒 PII Masker   │   │  │
│ 📊 Grafana      │   │               │ 🤖 LLM Provider │   │  │
│ 📈 Prometheus   │   │               │ 📊 Grafana      │   │  │
│ 📦 Tempo        │ ──┼─── Dashboards │ 📈 Prometheus   │   │  │
└─────────────────┘   │               │ 📦 Tempo        │ ──┼──┼─ Privacy-Safe
                      │               └─────────────────┘   │    Dashboards
                      │                                     │  
                      └── Raw Telemetry ───────────────────┘  
                                                              
                          
```

## 🚀 Quick Start

### Setup (GitHub Codespaces - Recommended)
1. Open this repository in GitHub
2. Click "Code" → "Codespaces" → "Create codespace on main"
3. Wait for environment initialization

### Setup (Local)
1. Clone repository and open in VS Code
2. Click "Reopen in Container" when prompted
3. Wait for container build completion

### Begin Workshop
```bash
# Copy environment configuration
cp .env.example .env

# Start with Lab 1
cd labs
code LAB_01_BASELINE.md
```

## 🔧 Essential Commands

### Docker Management
```bash
# Start all services
make docker-up

# Stop all services  
make docker-down

# Complete reset (removes volumes)
make docker-reset

# View logs
make docker-logs

# Open CLI chat
make docker-cli
```

### Service Access
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/healthz
- **Grafana Dashboard**: http://localhost:3000
- **Prometheus**: http://localhost:9090
- **Tempo**: http://localhost:3200

## 📊 Monitoring Dashboard

### Key Metrics to Watch
- **Request Rate**: Requests per second
- **Token Usage**: Input/output consumption  
- **Response Time**: Time to first token (TTFT)
- **Cost Tracking**: Estimated spending
- **Error Rates**: Success vs failure ratio
- **PII Detection**: Privacy protection effectiveness

### Grafana Dashboard Features
- Real-time LLM request monitoring
- Token usage and cost analysis
- Performance metrics (TTFT, throughput)
- Distributed trace exploration
- Error tracking and alerting

## ❌ Troubleshooting

### Common Issues

**Services won't start**:
```bash
# Check port conflicts
sudo lsof -i :8000,:3000,:9090
make docker-reset && make docker-up
```

**No telemetry data**:
```bash
# Verify OpenLIT initialization (compose-managed service)
docker compose logs llm-workshop-api | grep -i openlit
# Check OTel Collector
docker logs otelcol | grep -i error
```

**Dashboard shows no data**:
```bash
# Check time range (default: last 15 minutes)
# Generate fresh data
make docker-cli
```


## 🎯 Success Criteria

### Lab 1 Complete ✅
- [ ] LLM application runs successfully
- [ ] CLI chat works with basic questions
- [ ] Health check returns "healthy" status
- [ ] Understand session-based architecture

### Lab 2 Complete ✅
- [ ] OpenLIT SDK initializes correctly
- [ ] Telemetry data appears in OTel Collector logs
- [ ] Traces show LLM-specific attributes
- [ ] Understand traces vs metrics

### Lab 3 Complete ✅
- [ ] Grafana loads LLM dashboard
- [ ] Real-time metrics update during usage
- [ ] Prometheus shows LLM metrics
- [ ] Tempo displays detailed traces

### Lab 4 Complete ✅
- [ ] PII masking processes sensitive data
- [ ] Telemetry shows masked values
- [ ] Application functionality remains intact
- [ ] Understand privacy trade-offs

---

## 🏆 Workshop Completion

**Congratulations!** 🎉 By completing all labs, you've built a production-ready, privacy-conscious LLM observability stack and gained expertise in:

✅ **LLM Application Development**  
✅ **OpenTelemetry Instrumentation**  
✅ **Production Monitoring Stack**  
✅ **Privacy-Conscious Telemetry**  
✅ **Ethical AI Monitoring**  

**Next Steps**: Apply these concepts to your production LLM applications and contribute to responsible AI observability practices!

*Share your achievement:* `#AIdevEU2025 #OpenTelemetry #LLMObservability #PrivacyAI`