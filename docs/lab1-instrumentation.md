---
layout: default
title: Lab 1 - AI Instrumentation
nav_order: 3
---

# 🔬 Lab 1: AI Instrumentation with OpenLLMetry

**Duration:** ~30 minutes

In this lab, you'll add OpenLLMetry instrumentation to the sample RAG application to send traces to Dynatrace.

---

## 🎯 Learning Objectives

- Understand how OpenLLMetry works with OpenTelemetry
- Add Traceloop instrumentation to a Python AI application
- Configure the exporter for Dynatrace OTLP ingestion
- Verify traces are being sent to Dynatrace

---

## Step 1: Install OpenLLMetry Dependencies

First, we need to add the traceloop SDK and OpenTelemetry exporter packages.

### 1.1 Update requirements.txt

Open `app/requirements.txt` and **uncomment** the following lines (remove the `#`):

```python
# Before (commented out):
# traceloop-sdk==0.15.11
# opentelemetry-exporter-otlp==1.22.0

# After (uncommented):
traceloop-sdk==0.15.11
opentelemetry-exporter-otlp==1.22.0
```

### 1.2 Install the Dependencies

In the terminal, run:

```bash
pip install traceloop-sdk opentelemetry-exporter-otlp
```

Expected output:
```
Successfully installed traceloop-sdk-0.15.11 opentelemetry-exporter-otlp-1.22.0 ...
```

---

## Step 2: Add Dynatrace Instrumentation

Now we'll add the instrumentation code to our application.

### 2.1 Open the Main Application File

Open `app/main.py` in VS Code.

### 2.2 Locate the Instrumentation Section

Find this comment block near the top of the file:

```python
# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  🔬 LAB 1: INSTRUMENTATION SECTION                                        ║
# ║                                                                           ║
# ║  TODO: Add Dynatrace OpenLLMetry instrumentation here                    ║
# ║  Follow the instructions in the workshop guide to add the                 ║
# ║  Traceloop initialization code below this comment block.                  ║
# ║                                                                           ║
# ╚══════════════════════════════════════════════════════════════════════════╝

# ---> ADD YOUR INSTRUMENTATION CODE HERE <---
```

### 2.3 Add the Instrumentation Code

Replace `# ---> ADD YOUR INSTRUMENTATION CODE HERE <---` with the following code:

```python
from traceloop.sdk import Traceloop

# Get Dynatrace configuration from environment
ATTENDEE_ID = os.getenv("ATTENDEE_ID", "workshop-attendee")
DT_ENDPOINT = os.getenv("DT_ENDPOINT")
DT_API_TOKEN = os.getenv("DT_API_TOKEN")

# ⚠️ IMPORTANT: Dynatrace requires Delta temporality for metrics
# This MUST be set before Traceloop.init()
os.environ["OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE"] = "delta"

# Initialize Traceloop with Dynatrace endpoint
if DT_ENDPOINT and DT_API_TOKEN:
    headers = {"Authorization": f"Api-Token {DT_API_TOKEN}"}
    Traceloop.init(
        app_name=f"ai-chat-service-{ATTENDEE_ID}",
        api_endpoint=DT_ENDPOINT,
        headers=headers
    )
    print(f"✅ Traceloop initialized - sending traces to Dynatrace")
    print(f"   Service Name: ai-chat-service-{ATTENDEE_ID}")
    print(f"   Endpoint: {DT_ENDPOINT}")
else:
    print("⚠️  Dynatrace configuration not found. Traceloop not initialized.")
    print("   Please set DT_ENDPOINT and DT_API_TOKEN in your .env file")
```

---

## Step 3: Understanding the Code

Let's break down what each part does:

### 3.1 Import Statement

```python
from traceloop.sdk import Traceloop
```

The Traceloop SDK provides automatic instrumentation for LLM frameworks like OpenAI, LangChain, and more.

### 3.2 Delta Temporality Setting

```python
os.environ["OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE"] = "delta"
```

> **⚠️ Critical for Dynatrace:** Dynatrace expects metrics with **Delta temporality**, not Cumulative. This environment variable must be set before initializing Traceloop.

### 3.3 Traceloop Initialization

```python
Traceloop.init(
    app_name=f"ai-chat-service-{ATTENDEE_ID}",  # Your unique service name
    api_endpoint=DT_ENDPOINT,                     # Dynatrace OTLP endpoint
    headers=headers                               # API Token authentication
)
```

| Parameter | Description |
|-----------|-------------|
| `app_name` | Service name that appears in Dynatrace (includes your attendee ID) |
| `api_endpoint` | The Dynatrace OTLP ingestion endpoint |
| `headers` | Authentication header with your API token |

---

## Step 4: Restart the Application

Now let's restart the application with instrumentation enabled.

### 4.1 Start the Application

If the application is still running, stop it with `Ctrl+C`, then start it again:

```bash
cd app
python main.py
```

### 4.2 Verify Instrumentation

You should see the new instrumentation messages:

```
✅ Traceloop initialized - sending traces to Dynatrace
   Service Name: ai-chat-service-jsmith
   Endpoint: https://abc12345.live.dynatrace.com/api/v2/otlp

╔══════════════════════════════════════════════════════════════════════╗
║         🚀 AI Chat Service Starting...                               ║
║                                                                      ║
║         Attendee ID: jsmith                                          ║
║         Service: ai-chat-service-jsmith                              ║
╚══════════════════════════════════════════════════════════════════════╝

✅ RAG initialized successfully for attendee: jsmith
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## Step 5: Generate Test Traffic

Let's create some traces by using the chat endpoint.

### 5.1 Send Chat Requests

Open a new terminal and send several requests:

```bash
# Request 1: Ask about Dynatrace
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Dynatrace and what does it do?"}'

# Request 2: Ask about OpenTelemetry
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How does OpenTelemetry work with Dynatrace?"}'

# Request 3: Ask about observability
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain observability for AI applications"}'

# Request 4: Direct LLM call (no RAG)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Write a haiku about monitoring", "use_rag": false}'
```

### 5.2 What Gets Traced?

Each request generates traces for:
- **HTTP Request** - The incoming FastAPI request
- **Embedding Generation** - OpenAI embeddings for vector search
- **Vector Store Query** - ChromaDB retrieval
- **LLM Completion** - OpenAI chat completion
- **Token Usage** - Input/output token counts

---

## Step 6: Verify in Terminal Logs

As traces are sent, you may see OpenTelemetry log messages in the terminal indicating successful exports.

---

## ✅ Checkpoint

Before proceeding to Lab 2, verify:

- [ ] The `traceloop-sdk` and `opentelemetry-exporter-otlp` packages are installed
- [ ] The instrumentation code is added to `main.py`
- [ ] The application starts with "✅ Traceloop initialized" message
- [ ] You've sent at least 3-4 chat requests
- [ ] No errors appear in the terminal

---

## 🔍 Code Review: Your Updated main.py

The top of your `main.py` should now look like this:

```python
"""
Dynatrace AI Observability Workshop
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  🔬 LAB 1: INSTRUMENTATION SECTION                                        ║
# ╚══════════════════════════════════════════════════════════════════════════╝

from traceloop.sdk import Traceloop

# Get Dynatrace configuration from environment
ATTENDEE_ID = os.getenv("ATTENDEE_ID", "workshop-attendee")
DT_ENDPOINT = os.getenv("DT_ENDPOINT")
DT_API_TOKEN = os.getenv("DT_API_TOKEN")

# ⚠️ IMPORTANT: Dynatrace requires Delta temporality for metrics
os.environ["OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE"] = "delta"

# Initialize Traceloop with Dynatrace endpoint
if DT_ENDPOINT and DT_API_TOKEN:
    headers = {"Authorization": f"Api-Token {DT_API_TOKEN}"}
    Traceloop.init(
        app_name=f"ai-chat-service-{ATTENDEE_ID}",
        api_endpoint=DT_ENDPOINT,
        headers=headers
    )
    print(f"✅ Traceloop initialized - sending traces to Dynatrace")
    # ... rest of init logging
else:
    print("⚠️  Dynatrace configuration not found.")

# ════════════════════════════════════════════════════════════════════════════

from fastapi import FastAPI, HTTPException
# ... rest of imports and application code
```

---

## 🆘 Troubleshooting

### "Module traceloop not found"

Run the pip install command again:
```bash
pip install traceloop-sdk opentelemetry-exporter-otlp
```

### "401 Unauthorized" in logs

Your API token may be incorrect. Double-check:
1. The token in your `.env` file
2. That it has `openTelemetryTrace.ingest` permission
3. No extra spaces or quotes around the token

### "Traceloop not initialized" message

Check your `.env` file has both:
- `DT_ENDPOINT` set correctly
- `DT_API_TOKEN` set correctly

### Application crashes after adding instrumentation

1. Check for syntax errors in your code
2. Ensure imports are at the top of the file
3. Verify the `load_dotenv()` is called before accessing environment variables

---

## 🎉 Excellent Work!

You've successfully instrumented an AI application for Dynatrace! Now let's explore the traces in the Dynatrace UI.

<div class="lab-nav">
  <a href="lab0-setup">← Lab 0: Setup</a>
  <a href="lab2-explore-traces">Lab 2: Explore Traces →</a>
</div>
