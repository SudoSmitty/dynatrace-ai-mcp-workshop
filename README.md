# 🎯 Dynatrace AI Observability & MCP Workshop

A hands-on workshop for learning AI/LLM observability with Dynatrace and the Model Context Protocol (MCP).

---

> ## 🚀 **Workshop Attendees: Start Here!**
> 
> ### [![📖 Open Workshop Guide](https://img.shields.io/badge/📖_Open_Workshop_Guide-Click_Here_to_Start-blue?style=for-the-badge&logoColor=white)](https://sudosmitty.github.io/dynatrace-ai-mcp-workshop)
>
> The guide walks you through launching your Codespace, configuring your environment, and completing all labs with detailed instructions, code snippets, and screenshots.

---

## 📋 Workshop Overview

| **Duration** | 2 - 2.5 hours |
|--------------|---------------|
| **Level** | Intermediate |
| **Format** | Hands-on Labs |
| **Platform** | GitHub Codespaces |

### What You'll Learn

- ✅ Instrument AI/LLM applications with OpenLLMetry
- ✅ Send traces to Dynatrace via OTLP
- ✅ Analyze LLM performance, token usage, and costs
- ✅ Use Dynatrace MCP for agentic AI workflows

---

## 📚 Workshop Labs

| Lab | Duration | Description |
|-----|----------|-------------|
| [Lab 0: Setup](https://sudosmitty.github.io/dynatrace-ai-mcp-workshop/lab0-setup.html) | 15 min | Environment configuration |
| [Lab 1: Instrumentation](https://sudosmitty.github.io/dynatrace-ai-mcp-workshop/lab1-instrumentation.html) | 30 min | Add OpenLLMetry to the sample app |
| [Lab 2: Explore Traces](https://sudosmitty.github.io/dynatrace-ai-mcp-workshop/lab2-explore-traces.html) | 45 min | Analyze AI traces in Dynatrace |
| [Lab 3: Dynatrace MCP](https://sudosmitty.github.io/dynatrace-ai-mcp-workshop/lab3-dynatrace-mcp.html) | 45 min | Use MCP for agentic AI |

---

## 👨‍🏫 Instructor Setup

### Prerequisites

1. **GitHub Account** with Codespaces enabled
2. **Dynatrace Environment** (playground/demo tenant)
3. **Access to this repository** (for GitHub Actions)

### How It Works

> **Attendees share the same repository**—they don't fork it. Each attendee launches their own isolated Codespace, and all their code modifications stay private to that Codespace session.

The workshop uses a pre-deployed **Azure Function secrets server** to securely distribute Azure OpenAI credentials. Attendees enter a workshop token—they never see the actual API keys.

### Setup Steps (Before Each Workshop)

#### 1. Rotate the Workshop Token

Use the **"Rotate Workshop Token"** GitHub Action:

1. Go to **Actions** → **Rotate Workshop Token**
2. Click **Run workflow**
3. Enter a memorable token (e.g., `perform2026`, `acepaces`, `dynatraceai`)
4. The summary will confirm the new token

> 💡 **Tip:** Rotate the token before and after each workshop session for security.

#### 2. Create Dynatrace API Token

Create an API token in your Dynatrace tenant with these permissions:
- `openTelemetryTrace.ingest`
- `metrics.ingest`
- `entities.read`
- `problems.read`
- `logs.read`
- `DataExport`

#### 3. Prepare Attendee Credentials

Create a shared document or slide with:

| Credential | Value | Notes |
|------------|-------|-------|
| `WORKSHOP_TOKEN` | The token you set in Step 1 | For Azure OpenAI access |
| `DT_ENDPOINT` | `https://YOUR_ENV.live.dynatrace.com/api/v2/otlp` | Include `/api/v2/otlp` suffix! |
| `DT_API_TOKEN` | Your Dynatrace API token | From Step 2 |

---

### 🔧 Secrets Server Administration

The Azure Function secrets server is already deployed at `workshop-secrets-server.azurewebsites.net`. 

For maintenance, configuration changes, or troubleshooting, see [secrets-server/README.md](secrets-server/README.md).

---

## 🔧 The Sample Application

### Overview

A RAG (Retrieval Augmented Generation) service built with:
- **FastAPI** - Web framework
- **Azure OpenAI** - LLM provider
- **LangChain** - Orchestration
- **ChromaDB** - Vector store

### Key Features

- 🎨 **Beautiful Chat UI** - Interactive web interface for conversations
- 📚 Pre-loaded with Dynatrace-related knowledge
- 🏷️ Unique service naming per attendee (`ai-chat-service-{ATTENDEE_ID}`)
- 🔬 Ready for OpenLLMetry instrumentation

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Chat UI (web interface) |
| `/chat` | POST | Chat API endpoint |
| `/info` | GET | Service information |
| `/health` | GET | Health check |
| `/documents` | POST | Add documents to knowledge base |

---

## 📊 What Gets Traced

After instrumentation, Dynatrace captures:

| Span Type | Data Captured |
|-----------|---------------|
| HTTP Requests | Endpoint, status, duration |
| Embeddings | Model, token count, latency |
| Vector Search | Query count, results |
| LLM Completion | Model, tokens, prompt/response |

---

## 🔐 Security Notes

- Azure OpenAI credentials are distributed via a secure secrets server with rotating workshop tokens
- Attendees never see the raw Azure OpenAI API key—it's fetched automatically
- Workshop tokens should be rotated after each workshop session
- Dynatrace tokens should be rotated after workshops
- Consider using a dedicated playground tenant

---

## 📝 License

This workshop is provided for educational purposes. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [OpenLLMetry / Traceloop](https://github.com/traceloop/openllmetry)
- [Dynatrace](https://www.dynatrace.com)
- [OpenTelemetry](https://opentelemetry.io)
