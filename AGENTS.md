# AGENTS.md - AI Coding Agent Context

This file provides context for AI coding agents (GitHub Copilot, Claude, Cursor, etc.) working with this codebase.

## Project Overview

This is the **Dynatrace AI Observability & MCP Workshop** — a hands-on training environment that teaches attendees how to instrument AI/LLM applications with OpenLLMetry and analyze traces in Dynatrace.

**Key Characteristics:**
- Runs entirely in GitHub Codespaces (no local setup required)
- Attendees share the same repo but get isolated Codespace environments
- Uses a token-based secrets server to distribute Azure OpenAI credentials securely
- Workshop duration: 2-2.5 hours with 4 labs

## Repository Structure

```
├── app/                      # Sample RAG chatbot application
│   ├── main.py              # FastAPI app with LangChain + ChromaDB
│   ├── static/index.html    # Chat UI with markdown rendering
│   └── requirements.txt     # Python dependencies
├── docs/                     # Jekyll-based GitHub Pages workshop guide
│   ├── index.md             # Workshop landing page
│   ├── lab0-setup.md        # Environment setup lab
│   ├── lab1-instrumentation.md  # Add OpenLLMetry instrumentation
│   ├── lab2-explore-traces.md   # Analyze traces in Dynatrace
│   └── lab3-dynatrace-mcp.md    # Model Context Protocol lab
├── secrets-server/           # Azure Function for credential distribution
│   └── function_app.py      # Token validation + credential API
├── solutions/                # Completed instrumented app (reference)
├── .devcontainer/            # Codespace configuration
│   ├── devcontainer.json    # Container settings, extensions, ports
│   ├── setup.sh             # Post-create setup script
│   └── fetch-secrets.sh     # Credential fetching script for attendees
├── .github/workflows/        # GitHub Actions (token rotation, etc.)
└── .mcp/                     # MCP configuration for Lab 3
```

## Technology Stack

### Sample Application (`app/`)
- **Framework:** FastAPI with uvicorn
- **LLM Provider:** Azure OpenAI (GPT-4o, text-embedding-3-large)
- **Orchestration:** LangChain (LCEL chains, ChatPromptTemplate)
- **Vector Store:** ChromaDB (in-memory)
- **Observability:** OpenLLMetry/Traceloop SDK with `@workflow` and `@task` decorators

### Secrets Server (`secrets-server/`)
- **Platform:** Azure Functions (Python v2 model)
- **Storage:** Azure Blob Storage for token persistence
- **Endpoints:** `/api/get-credentials`, `/api/rotate-token`, `/api/get-token`

### Documentation (`docs/`)
- **Generator:** Jekyll with GitHub Pages
- **Theme:** Custom layout in `_layouts/default.html`
- **Assets:** CSS in `assets/css/style.css`

## Important Conventions

### Environment Variables
The app expects these environment variables (set via `.env` file):

```bash
# Azure OpenAI (fetched from secrets server)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=dynatraceRAG
AZURE_OPENAI_API_VERSION=2025-07-01-preview

# Dynatrace (provided by instructor)
DT_ENDPOINT=https://your-env.live.dynatrace.com/api/v2/otlp
DT_API_TOKEN=your-dt-token

# Workshop
ATTENDEE_ID=your-unique-id
```

### Instrumentation Pattern
The app uses Traceloop decorators for trace hierarchy:

```python
from traceloop.sdk.decorators import workflow, task

@workflow(name="rag_chat_pipeline")
def process_rag_chat(message: str):
    # Parent span for the entire RAG flow
    ...

@task(name="retrieve_documents")
def retrieve_documents(query: str):
    # Child span for document retrieval
    ...
```

### Azure OpenAI API Version
Use `2025-07-01-preview` — newer versions return 404 errors.

### Prompt Caching
The `RAG_SYSTEM_PROMPT` in `main.py` is intentionally 1,200+ tokens to enable Azure OpenAI prompt caching (requires 1,024+ token prefix).

## Common Tasks

### Running the Sample App
```bash
cd app
python main.py
# Opens on http://localhost:8000
```

### Testing the Chat Endpoint
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Dynatrace?", "use_rag": true}'
```

### Rotating Workshop Token (Instructor)
Use the GitHub Action: Actions → Rotate Workshop Token → Run workflow

### Building Docs Locally
```bash
cd docs
bundle install
bundle exec jekyll serve
```

## Files Attendees Modify

During the workshop, attendees only modify:
1. `app/main.py` — Add instrumentation code in the marked section
2. `.env` — Set environment variables

The instrumentation section is clearly marked:
```python
# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  🔬 LAB 1: INSTRUMENTATION SECTION                                        ║
# ╚══════════════════════════════════════════════════════════════════════════╝

# ---> ADD YOUR INSTRUMENTATION CODE HERE <---
```

## Key URLs

- **Workshop Guide:** https://sudosmitty.github.io/dynatrace-ai-mcp-workshop
- **Secrets Server:** https://workshop-secrets-server.azurewebsites.net
- **Launch Codespace:** https://codespaces.new/sudosmitty/dynatrace-ai-mcp-workshop?quickstart=1

## Azure Resources

| Resource | Name | Purpose |
|----------|------|---------|
| Function App | `workshop-secrets-server` | Credential distribution |
| Resource Group | `rg-workshop-secrets` | Contains all resources |
| OpenAI Resource | `cj-ai-workshop` | LLM and embedding models |
| Storage Account | Used by Function App | Token persistence |

## Troubleshooting Notes

- **Chat UI timeout:** Fetch has 2-minute timeout for long LLM responses
- **DT_ENDPOINT suffix:** Must include `/api/v2/otlp` at the end
- **Embedding model:** The `dynatraceRAG` deployment uses `text-embedding-3-large`
- **FastAPI lifespan:** Uses modern `lifespan` context manager (not deprecated `@app.on_event`)

## Do Not Modify

- `.devcontainer/` — Tested configuration for Codespaces
- `secrets-server/` — Production Azure Function
- `solutions/` — Reference implementation for instructors
