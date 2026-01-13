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
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Get configuration from environment
ATTENDEE_ID = os.getenv("ATTENDEE_ID", "workshop-attendee")
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

def format_docs(docs):
    """Format retrieved documents into a single string"""
    return "\n\n".join(doc.page_content for doc in docs)

def initialize_rag():
    """Initialize the RAG components with sample documents"""
    global embeddings, vectorstore, qa_chain, retriever
    
    try:
        # Initialize OpenAI embeddings
        embeddings = OpenAIEmbeddings()
        
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
        
        # Initialize LLM
        llm = ChatOpenAI(
            model="gpt-4o-mini",
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

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint - Process a message using RAG or direct LLM
    
    This is the main endpoint that will generate traces showing:
    - LLM calls to OpenAI
    - Embedding generation
    - Vector store retrieval
    - Response generation
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        if request.use_rag and qa_chain:
            # Use RAG chain (LCEL returns string directly)
            response_text = qa_chain.invoke(request.message)
            # Get sources separately
            if retriever:
                source_docs = retriever.invoke(request.message)
                sources = [doc.page_content[:100] + "..." for doc in source_docs]
            else:
                sources = None
        else:
            # Direct LLM call
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
            response = llm.invoke(request.message)
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
