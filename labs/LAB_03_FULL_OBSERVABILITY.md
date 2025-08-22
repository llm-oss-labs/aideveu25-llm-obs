# Lab 3: Full Observability Stack 📈
**Duration**: 45 minutes  
**Difficulty**: Intermediate  

## 🎯 Objective
Transform your telemetry pipeline into a production-ready observability stack by adding Grafana, Prometheus, and Tempo. You'll create visualizations, analyze performance trends, and explore distributed tracing capabilities.

## 🎓 What You'll Learn
- Complete observability pipeline architecture
- Grafana dashboard creation and customization
- Prometheus metrics collection and querying
- Tempo distributed tracing analysis
- LLM-specific performance monitoring
- Time-series data analysis and alerting

## 📋 Prerequisites
- Completed Lab 2 (basic observability with OpenLIT)
- Understanding of telemetry data structure from debug output

## 🧪 Lab Steps

### Step 1: Apply the Full Observability Patch (5 minutes)

```bash
# Stop current services
make docker-down

# Apply the patch to add visualization stack
git apply labs/patches/lab3-add-full-observability-stack.patch
```

**🔍 What This Patch Adds:**
- **Grafana**: Visualization and dashboards
- **Prometheus**: Metrics storage and querying
- **Tempo**: Distributed trace storage
- **Updated OTel Collector**: Routes data to storage backends
- **Pre-built Dashboard**: LLM-specific visualizations

### Step 2: Examine the New Architecture (10 minutes)

#### Updated OTel Collector Configuration
```bash
# Check the enhanced collector config
cat apps/otel_col/otel_config.yaml
```

**Key Changes:**
- **New Exporters**: 
  - `otlp/tempo`: Sends traces to Tempo
  - `prometheus`: Exposes metrics for Prometheus scraping
- **Updated Pipelines**: Route traces to Tempo, metrics to Prometheus
- **Debug Exporter**: Still available for troubleshooting

#### Grafana Configuration
```bash
# Examine Grafana setup
ls -la apps/grafana/
cat apps/grafana/grafana.ini
```

**Features:**
- Anonymous admin access (workshop convenience)
- Auto-provisioned data sources
- Pre-built LLM observability dashboard
- Default home dashboard configuration

#### Data Source Configuration
```bash
# Check auto-provisioned data sources
cat apps/grafana/provisioning/datasources/datasources.yaml
```

**Data Sources:**
- **Prometheus**: `http://prometheus:9090` (metrics)
- **Tempo**: `http://tempo:3200` (traces)

#### Pre-built Dashboard
```bash
# Check the dashboard configuration
ls -la apps/grafana/dashboards/
wc -l apps/grafana/dashboards/llm_observability.json
```

**Dashboard Features:**
- Request rate and volume metrics
- Token usage and cost tracking
- Performance analysis (TTFT, throughput)
- Error rates and success metrics
- Detailed trace exploration

### Step 3: Start the Complete Stack (10 minutes)

```bash
# Start all services including visualization stack
make docker-up
```

**🔍 Monitor Startup:**
```bash
# Watch all services come online
make docker-logs | grep -E "(Started|ready|listening)"
```

**Services Starting:**
1. **Tempo**: Trace storage backend
2. **Prometheus**: Metrics collection  
3. **OTel Collector**: Enhanced with new exporters
4. **Grafana**: Dashboard interface
5. **API**: LLM application with telemetry

**Port Mapping:**
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090  
- API: http://localhost:8000

### Step 4: Generate Comprehensive Telemetry (5 minutes)

Create diverse telemetry data for analysis:

```bash
# Start multiple chat sessions
make docker-cli
```

**Conversation Scenarios:**
1. **Simple Questions**: "What is AI?"
2. **Complex Requests**: "Explain machine learning algorithms with examples"
3. **Follow-up Context**: Continue conversations in same session
4. **Different Sessions**: Start new sessions for variety

```bash
# In parallel, use API directly
for i in {1..5}; do
  curl -X POST "http://localhost:8000/v1/chat" \
    -H "Content-Type: application/json" \
    -d "{
      \"session_id\": \"load-test-$i\",
      \"user_message\": \"Explain topic $i in detail\"
    }"
  sleep 2
done
```

### Step 5: Explore Grafana Dashboard (15 minutes)

#### Access the Dashboard
Open your browser to: **http://localhost:3000**

**🔍 You Should See:**
- Automatic login (anonymous admin)
- LLM Observability dashboard as home page
- Real-time metrics updating

#### Dashboard Sections

**1. Overview Metrics** (Top Row):
- **LLM Request Rate**: Requests per second
- **Total Usage Cost**: Estimated spending
- **Successful Requests**: Total count
- **Models in Use**: Distribution pie chart

**2. Performance Analysis**:
- **Time to First Token (TTFT)**: Latency metric
- **Token Generation Rate**: Throughput (tokens/sec)
- **Request Volume Over Time**: Trend analysis

**3. Detailed Analysis**:
- **Token Consumption vs Cost**: Relationship visualization
- **Request Duration Distribution**: Performance histogram

**4. Detailed Traces**:
- **Trace Table**: Individual request analysis

#### Interactive Exploration
```bash
# Generate varied load while watching dashboard
echo "Watch the dashboard update in real-time as you:"
echo "1. Send simple questions (low token usage)"
echo "2. Send complex requests (high token usage)"  
echo "3. Create errors (stop/start services)"
echo "4. Vary request frequency"
```

### Step 6: Prometheus Metrics Analysis (10 minutes)

#### Access Prometheus UI
Open: **http://localhost:9090**

#### Key Queries to Try

**Request Rate:**
```promql
rate(gen_ai_requests_total[5m])
```

**Average Token Usage:**
```promql
avg(gen_ai_client_token_usage_sum) / avg(gen_ai_client_token_usage_count)
```

**Cost Per Request:**
```promql
avg(gen_ai_usage_cost_USD_sum) / avg(gen_ai_requests_total)
```

**Response Time Percentiles:**
```promql
histogram_quantile(0.95, rate(gen_ai_client_operation_duration_seconds_bucket[5m]))
```

#### Understanding Metrics Types
```bash
# Counter metrics (always increasing)
echo "gen_ai_requests_total - Total requests made"

# Gauge metrics (current value)  
echo "gen_ai_active_sessions - Current active sessions"

# Histogram metrics (distribution)
echo "gen_ai_client_operation_duration_seconds - Response time distribution"

# Summary metrics (percentiles)
echo "gen_ai_usage_cost_USD - Cost distribution and totals"
```

### Step 7: Tempo Trace Analysis (10 minutes)

#### Access via Grafana
1. Go to Grafana (http://localhost:3000)
2. Navigate: **Explore** → **Tempo**
3. Use TraceQL or search interface

#### TraceQL Queries
```traceql
# Find all LLM traces
{span.telemetry.sdk.name="openlit"}

# High token usage traces  
{span.gen_ai.usage.input_tokens > 100}

# Slow responses
{span.gen_ai.client.operation.duration > 2s}

# Specific model usage
{span.gen_ai.request.model="phi3"}
```

#### Trace Analysis
**Click on Individual Traces to See:**
- Complete request timeline
- Span hierarchy and relationships
- LLM-specific attributes:
  - Original prompt
  - Generated response  
  - Token counts
  - Cost calculations
  - Performance metrics

## 🧪 Advanced Experiments

### 1. Performance Load Testing
```bash
# Create sustained load
for i in {1..20}; do
  (curl -X POST "http://localhost:8000/v1/chat" \
    -H "Content-Type: application/json" \
    -d "{\"session_id\": \"perf-test-$i\", \"user_message\": \"Generate a long response about technology\"}" &)
done

# Watch metrics spike in Grafana
echo "Monitor: Request rate, response times, token usage"
```

### 2. Cost Analysis
```bash
# Compare costs across different prompt types
cat << 'EOF' > cost_test.sh
#!/bin/bash
# Simple prompt
curl -s -X POST "http://localhost:8000/v1/chat" \
  -d '{"session_id": "cost1", "user_message": "Hi"}' > /dev/null

# Medium prompt  
curl -s -X POST "http://localhost:8000/v1/chat" \
  -d '{"session_id": "cost2", "user_message": "Explain machine learning"}' > /dev/null

# Complex prompt
curl -s -X POST "http://localhost:8000/v1/chat" \
  -d '{"session_id": "cost3", "user_message": "Write a detailed analysis of artificial intelligence, including history, current applications, future prospects, ethical considerations, and technical implementation details"}' > /dev/null

echo "Check Grafana for cost differences"
EOF

chmod +x cost_test.sh
./cost_test.sh
```

### 3. Custom Dashboard Creation
1. In Grafana, click **+** → **Dashboard**
2. Add panels for custom metrics:
   - Requests by session
   - Error rates over time
   - Token efficiency (output/input ratio)
   - Model comparison metrics

### 4. Alerting Setup (Optional)
```bash
# Example: Alert on high response times
echo "In Grafana:"
echo "1. Go to Alerting → Alert Rules"
echo "2. Create rule for: avg(gen_ai_client_operation_duration_seconds) > 5"
echo "3. Set notification channels"
```

## 🔍 Deep Dive: Dashboard Analysis

### Key Performance Indicators (KPIs)
```bash
cat << 'EOF'
📊 LLM Application KPIs:

🚀 Performance:
- Time to First Token (TTFT): < 1s (good), > 3s (poor)
- Token Generation Rate: > 10 tokens/sec (good)
- Request Success Rate: > 99%

💰 Cost Management:
- Cost per 1000 tokens: Track trends
- Daily/monthly spending: Budget tracking
- Cost per request: Efficiency metric

📈 Usage Patterns:
- Peak request times: Capacity planning
- Session duration: User engagement
- Token distribution: Prompt optimization

🔧 System Health:
- Error rates: < 1%
- Response time p95: < 5s  
- Queue depth: < 10 pending
EOF
```

### Correlation Analysis
```bash
echo "Look for correlations in your dashboard:"
echo "📈 High token usage ↔ Higher costs"
echo "⏱️  Complex prompts ↔ Longer response times"
echo "🔄 Longer sessions ↔ More context tokens"
echo "⚡ Simple questions ↔ Faster responses"
```

## ❌ Troubleshooting

### Issue: Grafana Dashboard Not Loading
```bash
# Check Grafana logs
docker logs grafana | grep -i error

# Verify data sources
curl http://localhost:3000/api/datasources

# Check dashboard provisioning
docker logs grafana | grep -i dashboard
```

### Issue: No Metrics in Prometheus
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Verify OTel Collector metrics endpoint
curl http://localhost:9464/metrics

# Check scrape configuration
docker logs prometheus | grep -i error
```

### Issue: Missing Traces in Tempo
```bash
# Verify Tempo is receiving data
docker logs tempo | grep -i received

# Check OTel Collector trace export
docker logs otelcol | grep -i tempo

# Test Tempo API
curl http://localhost:3200/api/search
```

### Issue: Dashboard Shows No Data
```bash
# Check time range (default: last 15 minutes)
echo "Adjust time range in Grafana if needed"

# Verify query syntax in panels
echo "Check Prometheus queries in panel edit mode"

# Generate fresh data
make docker-cli  # Create new requests
```

## 🎯 Success Criteria
- [ ] All services start successfully
- [ ] Grafana loads the LLM Observability dashboard  
- [ ] Real-time metrics update as you use the application
- [ ] Prometheus shows LLM-specific metrics
- [ ] Tempo displays detailed traces with LLM attributes
- [ ] You can correlate high-level metrics with detailed traces
- [ ] Dashboard provides actionable insights

## 📚 Key Takeaways
1. **Complete Pipeline**: Telemetry → Storage → Visualization
2. **Real-time Monitoring**: Live dashboards for operational awareness
3. **Historical Analysis**: Trend identification and capacity planning
4. **Correlation Power**: Connect high-level metrics to detailed traces
5. **Cost Visibility**: Track and optimize LLM spending
6. **Performance Insights**: Identify bottlenecks and optimization opportunities
7. **Production Ready**: Scalable, persistent, and alertable

## 🚀 Next Steps
You now have a comprehensive observability stack that provides complete visibility into your LLM application's performance, usage, and costs. However, there's one critical aspect missing: **privacy protection**.

**Current Privacy Concerns:**
- ❌ User prompts captured in traces
- ❌ Responses stored in telemetry  
- ❌ PII potentially exposed in logs
- ❌ Sensitive data in monitoring systems
- ❌ Compliance risks (GDPR, HIPAA, etc.)

In **Lab 4**, we'll implement privacy-conscious observability using PII detection and masking to maintain telemetry value while protecting user privacy.

---

**Ready for privacy protection?** → [Lab 4: Privacy-Conscious Observability](LAB_04_PRIVACY_OBSERVABILITY.md)