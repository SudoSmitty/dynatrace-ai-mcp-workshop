# AGENTS.md

This file provides guidance to AI coding agents like Claude Code (claude.ai/code), Cursor AI, Codex, Gemini CLI, GitHub Copilot, and other AI coding assistants when working with code in this repository.

## Project Summary

Hands-on workshop teaching AI/LLM observability with Dynatrace. Attendees run a RAG chatbot in GitHub Codespaces, add OpenLLMetry instrumentation, and analyze traces.

## Commands

```bash
# Run the sample app (from project root)
cd app && python main.py          # Serves on http://localhost:8000

# Test chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Dynatrace?", "use_rag": true}'

# Install dependencies
pip install -r app/requirements.txt

# Build docs locally
cd docs && bundle install && bundle exec jekyll serve
```

## Architecture

```
app/main.py          # FastAPI + LangChain RAG app (MAIN FILE attendees modify)
app/static/          # Chat UI (marked.js for markdown, highlight.js for code)
secrets-server/      # Azure Function - distributes Azure OpenAI creds via token
docs/                # Jekyll GitHub Pages - lab guides (lab0-lab4)
solutions/           # Reference instrumented app (instructor use)
.devcontainer/       # Codespace config (Python 3.11, Node 20)
```

### RAG Pipeline Flow (`app/main.py`)

```
@workflow: process_rag_chat()
  ├── @task: analyze_query_intent()   → LLM classifies query type
  ├── @task: retrieve_documents()     → ChromaDB vector search
  ├── @task: generate_context()       → Format docs into context string
  └── @task: generate_response()      → LLM generates final answer
```

## Critical Configuration

| Variable | Required Value | Notes |
|----------|----------------|-------|
| `AZURE_OPENAI_API_VERSION` | `2024-08-01-preview` | Other versions may return 404 |
| `DT_ENDPOINT` | Must end with `/api/v2/otlp` | Common mistake to omit suffix |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | `dynatraceRAG` | Uses `text-embedding-3-large` |

## Code Patterns

### Traceloop Decorators
```python
from traceloop.sdk.decorators import workflow, task

@workflow(name="rag_chat_pipeline")
def process_rag_chat(message: str):
    ...

@task(name="retrieve_documents")  
def retrieve_documents(query: str):
    ...
```

### FastAPI Lifespan (Modern Pattern)
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_rag()  # Startup
    yield
    # Shutdown

app = FastAPI(lifespan=lifespan)
```

### Instrumentation Location
Attendees add code at this marker in `app/main.py`:
```python
# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  🔬 LAB 1: INSTRUMENTATION SECTION                                        ║
# ╚══════════════════════════════════════════════════════════════════════════╝
# ---> ADD YOUR INSTRUMENTATION CODE HERE <---
```

## Workshop Labs Overview

| Lab | Focus | Persona Value |
|-----|-------|---------------|
| Lab 0 | Environment Setup | All |
| Lab 1 | Add Instrumentation | Developer: See your code in traces |
| Lab 2 | Explore Traces & Token Economics | Developer: Debug RAG pipeline; SRE: Cost analysis |
| Lab 3 | Dynatrace MCP + Error Investigation | Developer: Debug errors from IDE; SRE: Incident triage with MCP |
| Lab 4 | Workflow Automation | SRE: Automate cost alerts, daily summaries ("Hero Moment") |

## Error Simulation Feature

The UI has a **🐛 Simulate Errors** toggle that generates realistic RAG/LLM errors for workshop demos:

| Error Code | Exception | Simulates |
|------------|-----------|-----------|
| `EMB_NULL_VECTOR` | EmbeddingServiceError | Null vectors from embedding model |
| `CHROMA_COLLECTION_ERR` | VectorStoreConnectionError | ChromaDB connection failure |
| `LLM_MALFORMED_RESPONSE` | LLMResponseError | Invalid JSON from Azure OpenAI |
| `CTX_WINDOW_EXCEEDED` | ContextWindowExceededError | Token limit exceeded |
| `DOC_NO_MATCHES` | DocumentRetrievalError | No relevant documents found |
| `RAG_CHAIN_TIMEOUT` | RAGPipelineError | LangChain execution timeout |
| `CONTENT_FILTER_BLOCK` | LLMResponseError | Content policy violation |

Used in Lab 3 for practicing error investigation with Dynatrace MCP.

## Known Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Chat returns "Failed to send message" on long responses | Default fetch timeout | UI has 2-min AbortController timeout |
| 404 from Azure OpenAI | Wrong API version | Use `2025-07-01-preview` |
| Prompt caching not working | System prompt < 1024 tokens | `RAG_SYSTEM_PROMPT` is 1,200+ tokens |
| Deprecation warning on startup | `@app.on_event("startup")` | Use `lifespan` context manager |
| `GenAICustomOperationName` import error on startup | `opentelemetry-instrumentation-langchain>=0.53.0` references a missing class | Pin `traceloop-sdk==0.50.1` and `opentelemetry-exporter-otlp==1.39.1` |

## Protected Files

Do not modify without good reason:
- `.devcontainer/` — Tested Codespace config
- `secrets-server/` — Production Azure Function
- `solutions/` — Instructor reference implementation

## Key URLs

- Workshop Guide: https://sudosmitty.github.io/dynatrace-ai-mcp-workshop
- Secrets Server: https://workshop-secrets-server.azurewebsites.net
- Codespace: https://codespaces.new/sudosmitty/dynatrace-ai-mcp-workshop?quickstart=1
