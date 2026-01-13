"""
Dynatrace AI Observability Workshop - SOLUTION FILE
=====================================================
This is the fully instrumented version of main.py for instructor reference.
DO NOT share this file with attendees until after the lab is complete.
"""

import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  ✅ SOLUTION: Dynatrace OpenLLMetry Instrumentation                      ║
# ╚══════════════════════════════════════════════════════════════════════════╝

from traceloop.sdk import Traceloop
from opentelemetry.sdk.metrics.export import AggregationTemporality

# Get Dynatrace configuration from environment
ATTENDEE_ID = os.getenv("ATTENDEE_ID", "workshop-attendee")
DT_ENDPOINT = os.getenv("DT_ENDPOINT")
DT_API_TOKEN = os.getenv("DT_API_TOKEN")

# Dynatrace requires Delta temporality for metrics
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

# ════════════════════════════════════════════════════════════════════════════

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import chromadb
from chromadb.config import Settings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", 8000))

# Initialize FastAPI app with attendee-specific naming
app = FastAPI(
    title=f"AI Chat Service - {ATTENDEE_ID}",
    description="A RAG-powered AI assistant for the Dynatrace AI Observability Workshop",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for UI
import os as os_path
STATIC_DIR = os_path.join(os_path.dirname(__file__), "..", "app", "static")
if os_path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ... (rest of the application code is identical to main.py)
