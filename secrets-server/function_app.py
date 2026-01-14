"""
Dynatrace AI Workshop - Secrets Server
Azure Function for securely distributing workshop credentials

This function validates a workshop token and returns Azure OpenAI credentials.
Instructors configure the token and credentials as Azure Function App Settings.
"""

import azure.functions as func
import json
import logging
import os
import hashlib
import time

app = func.FunctionApp()


def constant_time_compare(val1: str, val2: str) -> bool:
    """
    Compare two strings in constant time to prevent timing attacks.
    """
    if len(val1) != len(val2):
        return False
    result = 0
    for x, y in zip(val1.encode(), val2.encode()):
        result |= x ^ y
    return result == 0


@app.route(route="get-credentials", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def get_credentials(req: func.HttpRequest) -> func.HttpResponse:
    """
    Validate workshop token and return Azure OpenAI credentials.
    
    Request body:
    {
        "workshop_token": "the-token-from-instructor"
    }
    
    Response (success):
    {
        "azure_openai_endpoint": "https://...",
        "azure_openai_api_key": "...",
        "azure_openai_chat_deployment": "gpt-4o-mini",
        "azure_openai_embedding_deployment": "text-embedding-ada-002",
        "azure_openai_api_version": "2024-08-01-preview"
    }
    
    Response (error):
    {
        "error": "Invalid workshop token"
    }
    """
    logging.info("Secrets request received")
    
    # Get configuration from App Settings (strip whitespace to handle copy/paste issues)
    valid_token = (os.environ.get("WORKSHOP_TOKEN") or "").strip()
    azure_openai_endpoint = (os.environ.get("AZURE_OPENAI_ENDPOINT") or "").strip()
    azure_openai_api_key = (os.environ.get("AZURE_OPENAI_API_KEY") or "").strip().replace("\n", "").replace("\r", "")
    azure_openai_chat_deployment = (os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT") or "gpt-4o-mini").strip()
    azure_openai_embedding_deployment = (os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT") or "text-embedding-ada-002").strip()
    azure_openai_api_version = (os.environ.get("AZURE_OPENAI_API_VERSION") or "2024-08-01-preview").strip()
    
    # Validate configuration
    if not valid_token:
        logging.error("WORKSHOP_TOKEN not configured in App Settings")
        return func.HttpResponse(
            json.dumps({"error": "Server configuration error. Contact instructor."}),
            status_code=500,
            mimetype="application/json"
        )
    
    if not azure_openai_endpoint or not azure_openai_api_key:
        logging.error("Azure OpenAI credentials not configured in App Settings")
        return func.HttpResponse(
            json.dumps({"error": "Server configuration error. Contact instructor."}),
            status_code=500,
            mimetype="application/json"
        )
    
    # Parse request
    try:
        req_body = req.get_json()
        provided_token = req_body.get("workshop_token", "")
    except (ValueError, AttributeError):
        return func.HttpResponse(
            json.dumps({"error": "Invalid request body. Expected JSON with 'workshop_token'."}),
            status_code=400,
            mimetype="application/json"
        )
    
    # Validate token (constant-time comparison to prevent timing attacks)
    if not provided_token or not constant_time_compare(provided_token, valid_token):
        logging.warning(f"Invalid token attempt")
        # Add small delay to prevent brute force
        time.sleep(0.5)
        return func.HttpResponse(
            json.dumps({"error": "Invalid workshop token. Please check with your instructor."}),
            status_code=401,
            mimetype="application/json"
        )
    
    # Success - return credentials
    logging.info("Valid token - returning credentials")
    credentials = {
        "azure_openai_endpoint": azure_openai_endpoint,
        "azure_openai_api_key": azure_openai_api_key,
        "azure_openai_chat_deployment": azure_openai_chat_deployment,
        "azure_openai_embedding_deployment": azure_openai_embedding_deployment,
        "azure_openai_api_version": azure_openai_api_version
    }
    
    return func.HttpResponse(
        json.dumps(credentials),
        status_code=200,
        mimetype="application/json"
    )


@app.route(route="health", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """
    Health check endpoint to verify the function is running.
    """
    return func.HttpResponse(
        json.dumps({"status": "healthy", "service": "workshop-secrets-server"}),
        status_code=200,
        mimetype="application/json"
    )
