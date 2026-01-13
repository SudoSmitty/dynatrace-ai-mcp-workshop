---
layout: default
title: Resources
nav_order: 6
---

# 📚 Workshop Resources

Quick reference links and additional learning materials for Dynatrace AI Observability.

---

## 🔗 Official Documentation

### Dynatrace

| Resource | Link |
|----------|------|
| Dynatrace Documentation | [docs.dynatrace.com](https://docs.dynatrace.com) |
| OpenTelemetry Integration | [OTLP Ingest](https://docs.dynatrace.com/docs/extend-dynatrace/opentelemetry) |
| Grail & DQL | [DQL Documentation](https://docs.dynatrace.com/docs/platform/grail/dynatrace-query-language) |
| Dynatrace MCP | [MCP Server Documentation](https://docs.dynatrace.com/docs/platform/davis-ai/mcp) |

### OpenLLMetry / Traceloop

| Resource | Link |
|----------|------|
| OpenLLMetry GitHub | [traceloop/openllmetry](https://github.com/traceloop/openllmetry) |
| Traceloop SDK Docs | [docs.traceloop.com](https://docs.traceloop.com) |
| Supported Libraries | [Integrations List](https://docs.traceloop.com/integrations) |

### OpenTelemetry

| Resource | Link |
|----------|------|
| OpenTelemetry Python | [opentelemetry.io/docs/instrumentation/python](https://opentelemetry.io/docs/instrumentation/python/) |
| OTLP Specification | [OTLP Spec](https://opentelemetry.io/docs/specs/otlp/) |
| Semantic Conventions | [GenAI Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) |

---

## 🛠️ Workshop Code Reference

### Dynatrace Instrumentation Template

```python
import os
from traceloop.sdk import Traceloop

# REQUIRED: Set Delta temporality for Dynatrace
os.environ["OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE"] = "delta"

# Initialize Traceloop for Dynatrace
headers = {"Authorization": f"Api-Token {os.getenv('DT_API_TOKEN')}"}
Traceloop.init(
    app_name="your-service-name",
    api_endpoint=os.getenv("DT_ENDPOINT"),  # https://xxx.live.dynatrace.com/api/v2/otlp
    headers=headers
)
```

### Required Environment Variables

```bash
# Dynatrace Configuration
DT_ENDPOINT=https://YOUR_ENV.live.dynatrace.com/api/v2/otlp
DT_API_TOKEN=dt0c01.XXXXXXXXXX.YYYYYYYYYYYY

# Application Configuration
ATTENDEE_ID=your-unique-id
```

### Python Dependencies

```
traceloop-sdk>=0.15.0
opentelemetry-exporter-otlp>=1.22.0
```

---

## 📊 Useful DQL Queries

### LLM Token Usage

```sql
fetch spans
| filter service.name == "ai-chat-service-*"
| filter isNotNull(llm.usage.total_tokens)
| summarize 
    total_tokens = sum(llm.usage.total_tokens),
    prompt_tokens = sum(llm.usage.prompt_tokens),
    completion_tokens = sum(llm.usage.completion_tokens)
  by bin(timestamp, 1h)
```

### LLM Latency Analysis

```sql
fetch spans
| filter span.name matches "openai.*"
| summarize 
    avg_latency = avg(duration),
    p50_latency = percentile(duration, 50),
    p95_latency = percentile(duration, 95),
    p99_latency = percentile(duration, 99)
  by span.name
```

### Request Distribution by Model

```sql
fetch spans
| filter isNotNull(llm.model)
| summarize count = count() by llm.model
| sort count desc
```

### Error Rate for AI Requests

```sql
fetch spans
| filter service.name == "ai-chat-service-*"
| summarize 
    total = count(),
    errors = countIf(otel.status_code == "ERROR")
| fieldsAdd error_rate = errors * 100.0 / total
```

---

## 🔐 API Token Permissions

For this workshop, your Dynatrace API token needs these scopes:

| Permission | Purpose |
|------------|---------|
| `openTelemetryTrace.ingest` | Ingest trace data via OTLP |
| `metrics.ingest` | Ingest metrics via OTLP |
| `entities.read` | Read entity information (for MCP) |
| `problems.read` | Read problem data (for MCP) |
| `logs.read` | Read log data (for MCP) |
| `DataExport` | Export data via DQL (for MCP) |

---

## 🎓 Further Learning

### Dynatrace University

- [Dynatrace Fundamentals](https://university.dynatrace.com)
- [OpenTelemetry with Dynatrace](https://university.dynatrace.com/ondemand/course/41840)
- [Davis AI Fundamentals](https://university.dynatrace.com/ondemand/course/41839)

### AI/ML Observability

- [Monitoring LLM Applications](https://www.dynatrace.com/news/blog/monitoring-llm-applications/)
- [OpenTelemetry GenAI Working Group](https://github.com/open-telemetry/community/tree/main/projects/genai)

### GitHub Resources

- [This Workshop Repository](https://github.com/YOUR_ORG/dynatrace-ai-mcp-workshop)
- [Dynatrace GitHub](https://github.com/Dynatrace)
- [OpenLLMetry](https://github.com/traceloop/openllmetry)

---

## 🆘 Getting Help

### During the Workshop

- Raise your hand for instructor assistance
- Use the workshop chat/Slack channel

### After the Workshop

- [Dynatrace Community](https://community.dynatrace.com/)
- [Dynatrace Support](https://support.dynatrace.com/)
- [Stack Overflow - dynatrace tag](https://stackoverflow.com/questions/tagged/dynatrace)

---

## 📝 Feedback

We'd love to hear your feedback on this workshop! Please share your thoughts with your instructor or via the feedback form provided.

---

[← Back to Workshop Home](index.md){: .btn .btn-primary }
