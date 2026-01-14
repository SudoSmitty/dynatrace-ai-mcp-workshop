"""
Dynatrace AI Workshop - Secrets Server
Azure Function for securely distributing workshop credentials

This function validates a workshop token and returns Azure OpenAI credentials.
Instructors configure the token and credentials as Azure Function App Settings.
The workshop token can be rotated via the /api/rotate-token endpoint.
"""

import azure.functions as func
import json
import logging
import os
import hashlib
import time
from azure.storage.blob import BlobServiceClient

app = func.FunctionApp()

# Blob storage configuration
CONTAINER_NAME = "workshop-config"
TOKEN_BLOB_NAME = "workshop-token.txt"


def get_blob_client():
    """Get Azure Blob client for token storage."""
    connection_string = os.environ.get("AzureWebJobsStorage")
    if not connection_string:
        return None
    blob_service = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service.get_container_client(CONTAINER_NAME)
    
    # Create container if it doesn't exist
    try:
        container_client.create_container()
    except Exception:
        pass  # Container already exists
    
    return container_client.get_blob_client(TOKEN_BLOB_NAME)


def get_workshop_token() -> str:
    """
    Get the workshop token from blob storage.
    Returns empty string if not set.
    """
    try:
        blob_client = get_blob_client()
        if blob_client and blob_client.exists():
            token = blob_client.download_blob().readall().decode("utf-8").strip()
            if token:
                return token
    except Exception as e:
        logging.warning(f"Could not read token from blob storage: {e}")
    
    return ""


def set_workshop_token(token: str) -> bool:
    """
    Store the workshop token in blob storage.
    """
    try:
        blob_client = get_blob_client()
        if blob_client:
            blob_client.upload_blob(token.encode("utf-8"), overwrite=True)
            return True
    except Exception as e:
        logging.error(f"Could not write token to blob storage: {e}")
    return False


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
    
    # Get workshop token from blob storage
    valid_token = get_workshop_token()
    
    # Get Azure OpenAI configuration from App Settings (strip whitespace to handle copy/paste issues)
    azure_openai_endpoint = (os.environ.get("AZURE_OPENAI_ENDPOINT") or "").strip()
    azure_openai_api_key = (os.environ.get("AZURE_OPENAI_API_KEY") or "").strip().replace("\n", "").replace("\r", "")
    azure_openai_chat_deployment = (os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT") or "gpt-4o-mini").strip()
    azure_openai_embedding_deployment = (os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT") or "text-embedding-ada-002").strip()
    azure_openai_api_version = (os.environ.get("AZURE_OPENAI_API_VERSION") or "2024-08-01-preview").strip()
    
    # Validate configuration
    if not valid_token:
        logging.error("Workshop token not set. Use /api/rotate-token to set one.")
        return func.HttpResponse(
            json.dumps({"error": "Workshop token not configured. Instructor needs to run the 'Rotate Workshop Token' GitHub Action."}),
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


@app.route(route="rotate-token", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def rotate_token(req: func.HttpRequest) -> func.HttpResponse:
    """
    Rotate the workshop token. Requires admin secret for authentication.
    
    Request body:
    {
        "admin_secret": "the-admin-secret",
        "new_token": "the-new-workshop-token"
    }
    
    Response (success):
    {
        "success": true,
        "message": "Workshop token updated successfully"
    }
    """
    logging.info("Token rotation request received")
    
    # Get admin secret from environment
    admin_secret = (os.environ.get("ADMIN_SECRET") or "").strip()
    
    if not admin_secret:
        logging.error("ADMIN_SECRET not configured in App Settings")
        return func.HttpResponse(
            json.dumps({"error": "Server configuration error. ADMIN_SECRET not set."}),
            status_code=500,
            mimetype="application/json"
        )
    
    # Parse request
    try:
        req_body = req.get_json()
        provided_secret = req_body.get("admin_secret", "")
        new_token = req_body.get("new_token", "").strip()
    except (ValueError, AttributeError):
        return func.HttpResponse(
            json.dumps({"error": "Invalid request body. Expected JSON with 'admin_secret' and 'new_token'."}),
            status_code=400,
            mimetype="application/json"
        )
    
    # Validate admin secret
    if not provided_secret or not constant_time_compare(provided_secret, admin_secret):
        logging.warning("Invalid admin secret attempt for token rotation")
        time.sleep(1)  # Delay to prevent brute force
        return func.HttpResponse(
            json.dumps({"error": "Unauthorized"}),
            status_code=401,
            mimetype="application/json"
        )
    
    # Validate new token
    if not new_token or len(new_token) < 4:
        return func.HttpResponse(
            json.dumps({"error": "New token must be at least 4 characters"}),
            status_code=400,
            mimetype="application/json"
        )
    
    # Store the new token
    if set_workshop_token(new_token):
        logging.info("Workshop token rotated successfully")
        return func.HttpResponse(
            json.dumps({
                "success": True,
                "message": "Workshop token updated successfully"
            }),
            status_code=200,
            mimetype="application/json"
        )
    else:
        return func.HttpResponse(
            json.dumps({"error": "Failed to store new token. Check storage configuration."}),
            status_code=500,
            mimetype="application/json"
        )


@app.route(route="get-token", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def get_current_token(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get the current workshop token. Requires admin secret for authentication.
    Useful for instructors to check/share the current token.
    
    Request body:
    {
        "admin_secret": "the-admin-secret"
    }
    """
    logging.info("Get token request received")
    
    admin_secret = (os.environ.get("ADMIN_SECRET") or "").strip()
    
    if not admin_secret:
        return func.HttpResponse(
            json.dumps({"error": "ADMIN_SECRET not configured"}),
            status_code=500,
            mimetype="application/json"
        )
    
    try:
        req_body = req.get_json()
        provided_secret = req_body.get("admin_secret", "")
    except (ValueError, AttributeError):
        return func.HttpResponse(
            json.dumps({"error": "Invalid request body"}),
            status_code=400,
            mimetype="application/json"
        )
    
    if not provided_secret or not constant_time_compare(provided_secret, admin_secret):
        time.sleep(1)
        return func.HttpResponse(
            json.dumps({"error": "Unauthorized"}),
            status_code=401,
            mimetype="application/json"
        )
    
    current_token = get_workshop_token()
    return func.HttpResponse(
        json.dumps({"token": current_token}),
        status_code=200,
        mimetype="application/json"
    )
