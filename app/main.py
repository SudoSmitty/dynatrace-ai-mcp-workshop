"""
Dynatrace AI Observability Workshop
====================================
Sample RAG (Retrieval Augmented Generation) Service

This is a simple AI-powered Q&A service that uses:
- OpenAI for LLM capabilities
- ChromaDB for vector storage
- LangChain for orchestration

🎯 WORKSHOP OBJECTIVE:
    Attendees will add OpenLLMetry/Traceloop instrumentation to this
    service to send traces to Dynatrace.
"""

import os
import warnings
from pathlib import Path
from dotenv import load_dotenv

# Suppress OpenTelemetry warnings about None attribute values (from tracing libraries)
warnings.filterwarnings("ignore", message="Invalid type NoneType for attribute")

# Load environment variables from .env file in project root
# (handles both running from app/ directory and from project root)
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    
    load_dotenv(env_path)
else:
    load_dotenv()  # Fall back to default behavior

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  🔬 LAB 1: INSTRUMENTATION SECTION                                        ║
# ║                                                                           ║
# ║  TODO: Add Dynatrace OpenLLMetry instrumentation here                    ║
# ║  Follow the instructions in the workshop guide to add the                 ║
# ║  Traceloop initialization code below this comment block.                  ║
# ║                                                                           ║
# ╚══════════════════════════════════════════════════════════════════════════╝

# ---> ADD YOUR INSTRUMENTATION CODE HERE <---




# ════════════════════════════════════════════════════════════════════════════

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import chromadb
from chromadb.config import Settings
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Get configuration from environment
ATTENDEE_ID = os.getenv("ATTENDEE_ID", "workshop-attendee")
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", 8000))

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_CHAT_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o-mini")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

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
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ═══════════════════════════════════════════════════════════════════════════
# Pydantic Models
# ═══════════════════════════════════════════════════════════════════════════

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str
    use_rag: bool = True

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str
    attendee_id: str
    sources: Optional[List[str]] = None

class DocumentRequest(BaseModel):
    """Request model for adding documents"""
    content: str
    metadata: Optional[dict] = None

class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    attendee_id: str
    service_name: str

# ═══════════════════════════════════════════════════════════════════════════
# Knowledge Base - Sample Documents about Dynatrace
# ═══════════════════════════════════════════════════════════════════════════

SAMPLE_DOCUMENTS = [
    """
    Dynatrace is an AI-powered, full-stack observability platform that provides 
    automatic and intelligent monitoring for cloud-native and enterprise environments. 
    It uses Davis AI to automatically detect anomalies, identify root causes, and 
    provide precise answers about application performance issues.
    """,
    """
    Dynatrace OneAgent is a single agent that automatically discovers and monitors 
    all processes, services, and infrastructure in your environment. It requires 
    no manual configuration and provides full-stack visibility from the application 
    layer down to the infrastructure.
    """,
    """
    OpenTelemetry is an open-source observability framework that provides APIs, 
    libraries, and tools for collecting telemetry data. Dynatrace fully supports 
    OpenTelemetry and can ingest traces, metrics, and logs via the OTLP protocol.
    """,
    """
    Grail is Dynatrace's next-generation data lakehouse that provides unified 
    storage and analysis of all observability data. It enables powerful analytics, 
    custom dashboards, and AI-powered insights across logs, traces, metrics, 
    and business events.
    """,
    """
    Dynatrace Application Security provides runtime vulnerability detection and 
    protection. It automatically identifies vulnerabilities in your running 
    applications without requiring code changes or additional agents.
    """,
    """
    OpenLLMetry is an open-source project built on OpenTelemetry for monitoring 
    LLM applications. It provides automatic instrumentation for popular AI/ML 
    frameworks like OpenAI, LangChain, and more, enabling observability into 
    AI workloads.
    """,
    """
    The Dynatrace MCP (Model Context Protocol) server enables AI assistants to 
    interact with Dynatrace environments. It allows querying Dynatrace data, 
    analyzing problems, and getting insights directly from your IDE using 
    tools like GitHub Copilot.
    """
]

# ═══════════════════════════════════════════════════════════════════════════
# RAG Components Initialization
# ═══════════════════════════════════════════════════════════════════════════

# Initialize embeddings and vector store
embeddings = None
vectorstore = None
qa_chain = None
retriever = None
llm = None

def format_docs(docs):
    """Format retrieved documents into a single string"""
    return "\n\n".join(doc.page_content for doc in docs)

# ═══════════════════════════════════════════════════════════════════════════
# RAG Pipeline Functions (Each creates distinct trace spans)
# ═══════════════════════════════════════════════════════════════════════════

# Import Traceloop decorators for creating trace hierarchies
try:
    from traceloop.sdk.decorators import workflow, task
    TRACELOOP_AVAILABLE = True
except ImportError:
    TRACELOOP_AVAILABLE = False
    # Define no-op decorators if Traceloop not available
    def workflow(name): return lambda f: f
    def task(name): return lambda f: f

@task(name="retrieve_documents")
def retrieve_documents(query: str) -> list:
    """
    Step 1: Retrieve relevant documents from vector store
    This generates embedding + vector search spans
    """
    if not retriever:
        return []
    docs = retriever.invoke(query)
    return docs

@task(name="generate_context")
def generate_context(docs: list) -> str:
    """
    Step 2: Format retrieved documents into context string
    """
    if not docs:
        return "No relevant context found."
    return format_docs(docs)

@task(name="generate_response")
def generate_response(question: str, context: str) -> str:
    """
    Step 3: Generate LLM response with context
    This generates the main LLM completion span
    """
    if not llm:
        raise ValueError("LLM not initialized")
    
    # Use chat messages format for cleaner trace capture
    from langchain_core.messages import SystemMessage, HumanMessage
    
    system_prompt = f"""You are a helpful AI assistant for the Dynatrace AI Observability Workshop.
Use the following context to answer the question. If you don't know the answer based on the 
context, say so and provide a general helpful response.

Context: {context}"""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=question)
    ]
    
    response = llm.invoke(messages)
    return response.content

def summarize_sources(docs: list) -> list:
    """
    Step 4: Extract and summarize source snippets
    """
    if not docs:
        return []
    return [doc.page_content[:100] + "..." for doc in docs]

@task(name="analyze_query_intent")
def analyze_query_intent(query: str) -> dict:
    """
    Step 5: Quick LLM call to classify query intent
    This adds an additional LLM span for richer traces
    """
    if not llm:
        return {"intent": "unknown", "confidence": 0}
    
    # Use messages format for consistent trace capture
    from langchain_core.messages import HumanMessage
    
    classification_prompt = f"""Classify the following query into one of these categories: 
    'technical', 'conceptual', 'troubleshooting', 'general'. 
    Respond with just the category name.
    
    Query: {query}"""
    
    result = llm.invoke([HumanMessage(content=classification_prompt)])
    return {"intent": result.content.strip().lower(), "query": query}

def initialize_rag():
    """Initialize the RAG components with sample documents"""
    global embeddings, vectorstore, qa_chain, retriever, llm
    
    try:
        # Initialize Azure OpenAI embeddings
        embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            azure_deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
            api_version=AZURE_OPENAI_API_VERSION
        )
        
        # Create text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        
        # Split documents
        docs = text_splitter.create_documents(SAMPLE_DOCUMENTS)
        
        # Create vector store
        vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            collection_name=f"workshop_{ATTENDEE_ID}"
        )
        
        # Create retriever
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        
        # Initialize Azure OpenAI LLM (stored globally for reuse)
        llm = AzureChatOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            azure_deployment=AZURE_OPENAI_CHAT_DEPLOYMENT,
            api_version=AZURE_OPENAI_API_VERSION,
            temperature=0.7
        )
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_template(
            """You are a helpful AI assistant for the Dynatrace AI Observability Workshop.
            Use the following context to answer the question. If you don't know the answer based on the 
            context, say so and provide a general helpful response.
            
            Context: {context}
            
            Question: {question}
            
            Answer:"""
        )
        
        # Create RAG chain using LCEL
        qa_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        print(f"✅ RAG initialized successfully for attendee: {ATTENDEE_ID}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize RAG: {e}")
        return False

# ═══════════════════════════════════════════════════════════════════════════
# API Endpoints
# ═══════════════════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup_event():
    """Initialize RAG on startup"""
    print(f"""
    ╔══════════════════════════════════════════════════════════════════════╗
    ║         🚀 AI Chat Service Starting...                               ║
    ║                                                                      ║
    ║         Attendee ID: {ATTENDEE_ID:<43}║
    ║         Service: ai-chat-service-{ATTENDEE_ID:<28}║
    ╚══════════════════════════════════════════════════════════════════════╝
    """)
    initialize_rag()

@app.get("/", response_class=FileResponse)
async def root():
    """Serve the chat UI"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/api/health", response_model=HealthResponse)
async def api_health():
    """API Health check with service information"""
    return HealthResponse(
        status="healthy",
        attendee_id=ATTENDEE_ID,
        service_name=f"ai-chat-service-{ATTENDEE_ID}"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        attendee_id=ATTENDEE_ID,
        service_name=f"ai-chat-service-{ATTENDEE_ID}"
    )

@workflow(name="rag_chat_pipeline")
def process_rag_chat(message: str) -> tuple:
    """
    RAG Chat Pipeline - Groups all LLM calls under a single parent trace
    """
    # Step 1: Analyze query intent (generates LLM span)
    intent_info = analyze_query_intent(message)
    
    # Step 2: Retrieve relevant documents (generates embedding + search spans)
    retrieved_docs = retrieve_documents(message)
    
    # Step 3: Generate context from documents
    context = generate_context(retrieved_docs)
    
    # Step 4: Generate response with context (generates LLM span)
    response_text = generate_response(message, context)
    
    # Step 5: Summarize sources for response
    sources = summarize_sources(retrieved_docs)
    
    return response_text, sources


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint - Process a message using RAG or direct LLM
    
    This endpoint generates multiple trace spans:
    1. Query intent analysis (LLM call)
    2. Document retrieval (embedding + vector search)
    3. Context generation
    4. Response generation (LLM call)
    5. Source summarization
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Add user's original question as a trace attribute for better visibility in Dynatrace
    # This captures the actual user input separately from the full RAG prompt
    try:
        from traceloop.sdk import Traceloop
        Traceloop.set_association_properties({
            "user.question": request.message,
            "use_rag": str(request.use_rag)
        })
    except Exception:
        pass  # Traceloop not initialized, skip
    
    try:
        if request.use_rag and retriever and llm:
            # Use the workflow-decorated function to group all operations
            response_text, sources = process_rag_chat(request.message)
        else:
            # Direct LLM call (single LLM span)
            direct_llm = AzureChatOpenAI(
                azure_endpoint=AZURE_OPENAI_ENDPOINT,
                api_key=AZURE_OPENAI_API_KEY,
                azure_deployment=AZURE_OPENAI_CHAT_DEPLOYMENT,
                api_version=AZURE_OPENAI_API_VERSION,
                temperature=0.7
            )
            response = direct_llm.invoke(request.message)
            response_text = response.content
            sources = None
        
        return ChatResponse(
            response=response_text,
            attendee_id=ATTENDEE_ID,
            sources=sources
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/documents")
async def add_document(request: DocumentRequest):
    """Add a document to the knowledge base"""
    if not vectorstore:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        docs = text_splitter.create_documents([request.content])
        vectorstore.add_documents(docs)
        
        return {"status": "success", "message": "Document added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding document: {str(e)}")

@app.get("/info")
async def get_info():
    """Get detailed service information"""
    return {
        "service_name": f"ai-chat-service-{ATTENDEE_ID}",
        "attendee_id": ATTENDEE_ID,
        "rag_initialized": qa_chain is not None,
        "documents_loaded": len(SAMPLE_DOCUMENTS),
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Service info"},
            {"path": "/health", "method": "GET", "description": "Health check"},
            {"path": "/chat", "method": "POST", "description": "Chat with AI"},
            {"path": "/documents", "method": "POST", "description": "Add documents"},
        ]
    }

# ═══════════════════════════════════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    print(f"Starting AI Chat Service for attendee: {ATTENDEE_ID}")
    uvicorn.run(
        "main:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=True
    )
