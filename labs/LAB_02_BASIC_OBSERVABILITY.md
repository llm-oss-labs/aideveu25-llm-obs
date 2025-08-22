# Lab 2: Basic Observability with OpenLIT 📊
**Duration**: 45 minutes  
**Difficulty**: Intermediate  

## 🎯 Objective
Add telemetry collection to your LLM application using OpenLIT SDK and OpenTelemetry Collector. You'll learn to capture, export, and examine LLM-specific telemetry data in a debug mode before setting up visualization tools.

## 🎓 What You'll Learn
- OpenTelemetry fundamentals and architecture
- Automatic LLM instrumentation with OpenLIT
- Trace vs metric data concepts
- OTLP (OpenTelemetry Protocol) basics
- Telemetry data structure and semantics
- Debug-mode telemetry inspection

## 📋 Prerequisites
- Completed Lab 1 (baseline application running)
- Understanding of the baseline architecture

## 🧪 Lab Steps

### Step 1: Apply the OpenLIT Observability Patch (5 minutes)

```bash
# Stop the current services
make docker-down

# Apply the patch to add basic observability
git apply labs/patches/lab2-add-basic-observability.patch
```

**🔍 What This Patch Adds:**
- OpenLIT SDK to `pyproject.toml`
- OpenLIT instrumentation in `apps/api/main.py`
- OpenTelemetry Collector service with debug configuration
- Basic OTEL environment variables

### Step 2: Examine the Changes (10 minutes)

#### OpenLIT Integration
```bash
# Check the API changes
diff -u apps/api/main.py.orig apps/api/main.py || true
```

**Key Addition:**
```python
import openlit
openlit.init(capture_message_content=True)
```

**🔍 Analysis:**
- `capture_message_content=True` enables full prompt/response capture
- Automatic instrumentation of OpenAI client calls
- Zero manual instrumentation required

#### OpenTelemetry Collector Configuration
```bash
# Examine the OTel Collector setup
cat apps/otel_col/otel_config.yaml
```

**Key Components:**
- **Receivers**: Accept OTLP data on ports 4317 (gRPC) and 4318 (HTTP)
- **Processors**: Batch processing and memory management
- **Exporters**: Debug exporter for human-readable output
- **Pipelines**: Separate processing for traces and metrics

#### Docker Services
```bash
# Check the new service definition
grep -A 15 "otelcol:" docker-compose.yml
```

**Service Details:**
- Built from custom Dockerfile
- Memory-limited for workshop efficiency
- Exposes OTLP receiver ports
- Volume mounts configuration

### Step 3: Build and Start with Observability (5 minutes)

```bash
# Build the new services (OTel Collector)
make docker-up
```

**🔍 Watch the Startup:**
```bash
# Monitor logs to see OTel Collector initialization
make docker-logs
```

Look for:
- OpenLIT initialization in the API logs
- OTel Collector startup messages
- OTLP receivers starting on ports 4317/4318

### Step 4: Generate Telemetry Data (10 minutes)

#### Start a Chat Session
```bash
# Open the CLI
make docker-cli
```

**Have Several Conversations:**
1. "What is OpenTelemetry?"
2. "Explain the difference between traces and metrics"
3. "What are the benefits of observability?"
4. "How does automatic instrumentation work?"

#### Use the API Directly
```bash
# In another terminal, make API calls
curl -X POST "http://localhost:8000/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "api-test-session",
    "user_message": "What is the purpose of telemetry data?"
  }'
```

### Step 5: Examine Telemetry Output (15 minutes)

#### View Debug Telemetry
```bash
# Filter for telemetry data in OTel Collector logs
docker logs otelcol | grep -A 50 "ResourceSpans"
```

**🔍 Trace Data Structure:**
```
ResourceSpans #0
Resource SchemaURL: 
Resource attributes:
     -> service.name: Str(fastapi-chatbot)
     -> telemetry.sdk.name: Str(openlit)
     -> telemetry.sdk.version: Str(1.35.x)
ScopeSpans #0
...
```

#### Analyze a Complete Trace
Look for these key attributes in the trace output:

**LLM-Specific Attributes:**
```
-> gen_ai.request.model: Str(phi3)
-> gen_ai.prompt: Str(user's question)
-> gen_ai.completion: Str(assistant's response)
-> gen_ai.usage.input_tokens: Int(142)
-> gen_ai.usage.output_tokens: Int(89)
-> gen_ai.usage.cost: Float(0.000023)
```

**Standard Attributes:**
```
-> http.method: Str(POST)
-> http.status_code: Int(200)
-> span.kind: Str(client)
-> operation.name: Str(chat_completion)
```

#### Check Metrics Output
```bash
# Look for metrics data
docker logs otelcol | grep -A 20 "ResourceMetrics"
```

**Key Metrics:**
- `gen_ai_requests_total` - Request counter
- `gen_ai_client_token_usage` - Token consumption
- `gen_ai_usage_cost_USD` - Cost tracking
- `gen_ai_client_operation_duration` - Response time

### Step 6: Understanding Telemetry Concepts (10 minutes)

#### Traces vs Metrics
**Traces** (What happened):
```bash
# Trace example shows request flow
echo "Trace = Individual request journey with timing and context"
echo "- Start: User sends message"
echo "- Span 1: FastAPI receives request"  
echo "- Span 2: LLM client processes"
echo "- Span 3: Ollama/Azure generates response"
echo "- End: Response returned to user"
```

**Metrics** (How much/how often):
```bash
# Metrics aggregate data over time
echo "Metrics = Aggregated measurements over time"
echo "- Request rate: 5 requests/minute"
echo "- Average tokens: 150 input + 75 output"
echo "- Total cost: $0.002 in last hour"
```

#### OpenLIT Instrumentation Magic
```bash
# See what OpenLIT automatically captures
cat << EOF
OpenLIT automatically instruments:
📊 Request/Response metadata
🕐 Timing information  
💰 Cost calculation (estimated)
🔢 Token usage counting
🏷️  Model and provider identification
🚫 Error detection and classification
📍 Distributed tracing context
EOF
```

## 🧪 Experiments to Try

### 1. Compare Different Prompts
Test how prompt complexity affects metrics:

```bash
# Simple prompt
curl -X POST "http://localhost:8000/v1/chat" \
  -d '{"session_id": "test1", "user_message": "Hi"}'

# Complex prompt  
curl -X POST "http://localhost:8000/v1/chat" \
  -d '{"session_id": "test2", "user_message": "Explain quantum computing in detail with examples and applications"}'

# Check logs for token differences
docker logs otelcol | grep "gen_ai.usage" | tail -4
```

### 2. Session Context Impact
See how conversation history affects token usage:

```bash
# Start new session
curl -X POST "http://localhost:8000/v1/chat" \
  -d '{"session_id": "context-test", "user_message": "What is Docker?"}'

# Continue conversation (includes history)
curl -X POST "http://localhost:8000/v1/chat" \
  -d '{"session_id": "context-test", "user_message": "How is it different from VMs?"}'
```

### 3. Error Telemetry
Trigger an error to see how it's captured:

```bash
# Temporarily break the service
make docker-down

# Try to make a request (will fail)
curl -X POST "http://localhost:8000/v1/chat" \
  -d '{"session_id": "error-test", "user_message": "This will fail"}'

# Restart and check error telemetry
make docker-up
```

## 🔍 Deep Dive: Telemetry Data Analysis

### Trace Anatomy
Each trace contains:

```
🔗 Trace ID: Unique identifier for the entire request
├── 📊 Root Span: FastAPI HTTP request
│   ├── ⏱️  Duration: Total request time
│   ├── 🏷️  Tags: HTTP method, status, etc.
│   └── 📝 Events: Request start/end
└── 🤖 Child Span: LLM operation
    ├── 💬 Prompt: User input (if capture enabled)
    ├── 🤖 Response: LLM output (if capture enabled)  
    ├── 🔢 Tokens: Input/output counts
    ├── 💰 Cost: Estimated price
    └── ⚡ Performance: TTFT, tokens/sec
```

### Metric Types
```bash
# Counter: Ever-increasing values
echo "gen_ai_requests_total: 42 (total requests)"

# Gauge: Point-in-time values  
echo "gen_ai_active_sessions: 3 (current sessions)"

# Histogram: Distribution of values
echo "gen_ai_request_duration: [0.5s, 1.2s, 0.8s, ...]"

# Summary: Percentiles and counts
echo "gen_ai_token_usage: p50=150, p95=500, count=100"
```

## ❌ Troubleshooting

### Issue: No Telemetry Data Appearing
```bash
# Check if OpenLIT initialized
docker logs llm-workshop-api | grep -i openlit

# Verify OTel Collector is receiving data
docker logs otelcol | grep "OTLP receiver"

# Ensure environment variables are set
docker exec llm-workshop-api env | grep OTEL
```

### Issue: OTel Collector Startup Fails
```bash
# Check configuration syntax
docker logs otelcol | grep -i error

# Verify config file
cat apps/otel_col/otel_config.yaml | yaml_lint || echo "Check YAML syntax"
```

### Issue: Missing Trace/Metric Data
```bash
# Confirm capture_message_content setting
grep -n "capture_message_content" apps/api/main.py

# Check exporter configuration
grep -A 5 "exporters:" apps/otel_col/otel_config.yaml
```

## 🎯 Success Criteria
- [ ] OpenLIT SDK successfully initializes in API logs
- [ ] OTel Collector starts and receives data
- [ ] Trace data appears with LLM-specific attributes
- [ ] Metrics show request counts and token usage
- [ ] Debug output shows structured telemetry data
- [ ] You understand traces vs metrics concepts

## 📚 Key Takeaways
1. **Automatic Instrumentation**: OpenLIT requires minimal code changes
2. **Rich Context**: LLM operations generate detailed telemetry
3. **Cost Tracking**: Token usage translates to estimated costs
4. **Performance Visibility**: Response times and throughput are captured
5. **Debug Mode**: Raw telemetry helps understand data structure
6. **Standards**: OpenTelemetry provides vendor-neutral telemetry

## 🚀 Next Steps
You now have telemetry data flowing, but it's only visible in debug logs. While this gives you the raw data, it's not practical for monitoring production systems. 

In **Lab 3**, we'll add a complete visualization stack (Grafana, Prometheus, Tempo) to turn this raw telemetry into actionable dashboards and alerts.

**Current Limitations:**
- ❌ No historical data storage
- ❌ No visual dashboards  
- ❌ No alerting capabilities
- ❌ Difficult to analyze trends
- ❌ Not suitable for production monitoring

---

**Ready for visualization?** → [Lab 3: Full Observability Stack](LAB_03_FULL_OBSERVABILITY.md)