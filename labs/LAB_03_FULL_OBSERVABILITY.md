# Lab 3: Full Observability Stack 📈
**Duration**: 15 minutes  

## 🎯 Objective
Transform your telemetry pipeline into a production-ready observability stack by adding Grafana, Prometheus, and Tempo. You'll create visualizations, analyze performance trends, and explore distributed tracing capabilities.

## 🎓 What You'll Learn
- Complete observability pipeline architecture
- Prometheus metrics collection and querying
- Tempo distributed tracing analysis
- Grafana dashboard visualization
- LLM-specific performance monitoring

## 📋 Prerequisites
- Completed Lab 2 (Basic Observability with OpenLIT)
- Understanding of telemetry data structure from debug output

## 🧪 Lab Steps

### Step 1: Apply the Full Observability Patch

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
- **Updated OTel Collector**: Routes data to storage backends (Prometheus & Tempo)
- **Pre-built Dashboard**: LLM-specific visualizations

### Step 2: Examine the New Architecture

#### Updated OTel Collector Configuration
```bash
# Check the enhanced collector config
code apps/otel_col/otel_config.yaml
```

**Key Changes:**
- **New Exporters**: 
  - `otlp/tempo`: Sends traces to Tempo
  - `prometheus`: Exposes metrics for Prometheus scraping
- **Updated Pipelines**: Route traces to Tempo, metrics to Prometheus
- **Debug Exporter**: Still available for troubleshooting but no longer enabled

#### Grafana Configuration

**Features:**
- Anonymous admin access (workshop convenience)
- Auto-provisioned data sources
- Pre-built LLM observability dashboard
- Default home dashboard configuration

#### Data Source Configuration
```bash
# Check auto-provisioned data sources
code apps/grafana/provisioning/datasources/datasources.yaml
```

**Data Sources:**
- **Prometheus**: `http://prometheus:9090` (metrics)
- **Tempo**: `http://tempo:3200` (traces)


### Step 3: Start the Complete Stack

```bash
# Start all services including visualization stack
make docker-up
```

**🔍 Monitor Startup:**
```bash
# Watch all services come online
make docker-logs | grep -E "(Started|ready|listening)"
```

**Port Mapping:**
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090  
- API: http://localhost:8000

> **💡 Codespaces Users**: These ports are automatically forwarded and accessible through your Codespaces environment. You can access them via the forwarded URLs shown in the Ports panel, or VS Code will prompt you with links when the services start.

### Step 4: Generate Comprehensive Telemetry

Create diverse telemetry data for analysis:

```bash
# Start multiple chat sessions
make docker-cli
```

**Conversation Scenarios:**
1. **Simple Questions**: "What is AI?"
2. **Leak Personal Information**: "My name is Bob and my e-mail is bob@hotmail.com"

### Step 5: Explore Grafana Dashboard

#### Access the Dashboard
Open your browser to: **http://localhost:3000**


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


## 🎯 Success Criteria
- [ ] All services start successfully
- [ ] Grafana loads the LLM Observability dashboard  
- [ ] Real-time metrics update as you use the application

## 📚 Key Takeaways
1. **Complete Pipeline**: Telemetry → Storage → Visualization
2. **Real-time Monitoring**: Live dashboards for operational awareness
3. **Historical Analysis**: Trend identification and capacity planning
4. **Correlation Power**: Connect high-level metrics to detailed traces

## 🚀 Next Steps
You now have a comprehensive observability stack that provides complete visibility into your LLM application's performance, usage, and costs. However, there's one critical aspect missing: **privacy protection**.

**Current Privacy Concerns:**
- ❌ User prompts captured in our flow
- ❌ Responses stored in telemetry  
- ❌ PII potentially exposed
- ❌ Compliance risks (GDPR, HIPAA, etc.)

In **Lab 4**, we'll implement privacy-conscious observability using PII detection and masking to maintain telemetry value while protecting user privacy.

---

**Ready for privacy protection?** → [Lab 4: Privacy-Conscious Observability](LAB_04_PRIVACY_OBSERVABILITY.md)