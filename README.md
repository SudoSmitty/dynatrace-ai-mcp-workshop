# 🎯 Dynatrace AI Observability & MCP Workshop

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/sudosmitty/dynatrace-ai-mcp-workshop?quickstart=1)

A hands-on workshop for learning AI/LLM observability with Dynatrace and the Model Context Protocol (MCP).

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

## 🚀 Quick Start for Attendees

> **Note:** Each attendee gets their own **isolated Codespace environment**. You don't need to fork or clone this repository—just launch a Codespace and your changes stay private to your session.

### Step 1: Launch Codespace

Click the button above or use:
```
https://codespaces.new/sudosmitty/dynatrace-ai-mcp-workshop?quickstart=1
```

### Step 2: Configure Environment

Edit the `.env` file with:
- Your unique `ATTENDEE_ID` (your initials or name)
- `DT_ENDPOINT` and `DT_API_TOKEN` (provided by instructor)

### Step 3: Follow the Labs

Open the workshop guide: [Workshop Labs](https://sudosmitty.github.io/dynatrace-ai-mcp-workshop)

---

## 📚 Workshop Labs

| Lab | Duration | Description |
|-----|----------|-------------|
| [Lab 0: Setup](https://sudosmitty.github.io/dynatrace-ai-mcp-workshop/lab0-setup.html) | 15 min | Environment configuration |
| [Lab 1: Instrumentation](https://sudosmitty.github.io/dynatrace-ai-mcp-workshop/lab1-instrumentation.html) | 30 min | Add OpenLLMetry to the sample app |
| [Lab 2: Explore Traces](https://sudosmitty.github.io/dynatrace-ai-mcp-workshop/lab2-explore-traces.html) | 45 min | Analyze AI traces in Dynatrace |
| [Lab 3: Dynatrace MCP](https://sudosmitty.github.io/dynatrace-ai-mcp-workshop/lab3-dynatrace-mcp.html) | 45 min | Use MCP for agentic AI |

---

## 🏗️ Repository Structure

```
├── .devcontainer/          # GitHub Codespaces configuration
│   ├── devcontainer.json   # Container settings and extensions
│   └── setup.sh            # Post-create setup script
├── .github/                # GitHub configuration
├── app/                    # Sample RAG/LLM application
│   ├── main.py            # Main application (to be instrumented)
│   ├── requirements.txt   # Python dependencies
│   └── .env.template      # Environment template
├── docs/                   # GitHub Pages workshop guide
│   ├── index.md           # Workshop home
│   ├── lab0-setup.md      # Lab 0: Environment setup
│   ├── lab1-instrumentation.md  # Lab 1: Add instrumentation
│   ├── lab2-explore-traces.md   # Lab 2: Analyze in Dynatrace
│   ├── lab3-dynatrace-mcp.md    # Lab 3: Use MCP
│   └── resources.md       # Reference links
├── solutions/              # Solution files (instructor only)
└── README.md              # This file
```

---

## 👨‍🏫 Instructor Setup

### Prerequisites

1. **GitHub Account** with Codespaces enabled
2. **Dynatrace Environment** (playground/demo tenant)
3. **OpenAI API Key** with sufficient quota

### How It Works

> **Attendees share the same repository**—they don't fork it. Each attendee launches their own isolated Codespace, and all their code modifications stay private to that Codespace session.

### Setup Steps

#### 1. Clone Repository (for customization)

```bash
git clone https://github.com/sudosmitty/dynatrace-ai-mcp-workshop.git
```

#### 2. Configure GitHub Secrets

Add these secrets to the repository (Settings → Secrets → Codespaces):

| Secret | Description |
|--------|-------------|
| `OPENAI_API_KEY` | OpenAI API key for all attendees |

#### 3. Create Dynatrace API Token

Create an API token in your Dynatrace tenant with these permissions:
- `openTelemetryTrace.ingest`
- `metrics.ingest`
- `entities.read`
- `problems.read`
- `logs.read`
- `DataExport`

#### 4. Enable GitHub Pages

1. Go to Settings → Pages
2. Source: Deploy from a branch
3. Branch: `main`, folder: `/docs`

#### 5. Prepare Attendee Credentials

Create a shared document or slide with:
- `DT_ENDPOINT`: `https://YOUR_ENV.live.dynatrace.com/api/v2/otlp`
- `DT_API_TOKEN`: The token created above

---

## 🔧 The Sample Application

### Overview

A RAG (Retrieval Augmented Generation) service built with:
- **FastAPI** - Web framework
- **OpenAI** - LLM provider
- **LangChain** - Orchestration
- **ChromaDB** - Vector store

### Key Features

- Pre-loaded with Dynatrace-related knowledge
- Unique service naming per attendee (`ai-chat-service-{ATTENDEE_ID}`)
- Ready for OpenLLMetry instrumentation

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/health` | GET | Health check |
| `/chat` | POST | Chat with AI (RAG-enabled) |
| `/documents` | POST | Add documents to knowledge base |
| `/info` | GET | Service information |

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

- OpenAI API key is stored in GitHub Secrets (not exposed to attendees)
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