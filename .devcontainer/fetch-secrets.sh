#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# Fetch Workshop Secrets
# Run this script if you need to re-fetch Azure OpenAI credentials
# ═══════════════════════════════════════════════════════════════════════════

SECRETS_SERVER_URL="${SECRETS_SERVER_URL:-https://workshop-secrets-server.azurewebsites.net/api}"
ENV_FILE="/workspaces/dynatrace-ai-mcp-workshop/.env"

echo "🔐 Fetching Azure OpenAI credentials..."
echo ""

read -p "Enter your workshop token: " WORKSHOP_TOKEN

if [ -z "$WORKSHOP_TOKEN" ]; then
    echo "❌ No token provided. Exiting."
    exit 1
fi

# Make request to secrets server
response=$(curl -s -w "\n%{http_code}" -X POST "${SECRETS_SERVER_URL}/get-credentials" \
    -H "Content-Type: application/json" \
    -d "{\"workshop_token\": \"${WORKSHOP_TOKEN}\"}" 2>/dev/null)

# Extract HTTP status code (last line) and body (everything else)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "200" ]; then
    # Parse JSON response
    azure_openai_endpoint=$(echo "$body" | grep -o '"azure_openai_endpoint":"[^"]*"' | cut -d'"' -f4)
    azure_openai_api_key=$(echo "$body" | grep -o '"azure_openai_api_key":"[^"]*"' | cut -d'"' -f4)
    azure_openai_chat_deployment=$(echo "$body" | grep -o '"azure_openai_chat_deployment":"[^"]*"' | cut -d'"' -f4)
    azure_openai_embedding_deployment=$(echo "$body" | grep -o '"azure_openai_embedding_deployment":"[^"]*"' | cut -d'"' -f4)
    azure_openai_api_version=$(echo "$body" | grep -o '"azure_openai_api_version":"[^"]*"' | cut -d'"' -f4)
    
    if [ -n "$azure_openai_endpoint" ] && [ -n "$azure_openai_api_key" ]; then
        # Remove any existing Azure OpenAI entries
        sed -i '/^AZURE_OPENAI_ENDPOINT=/d' "$ENV_FILE" 2>/dev/null || true
        sed -i '/^AZURE_OPENAI_API_KEY=/d' "$ENV_FILE" 2>/dev/null || true
        sed -i '/^AZURE_OPENAI_CHAT_DEPLOYMENT=/d' "$ENV_FILE" 2>/dev/null || true
        sed -i '/^AZURE_OPENAI_EMBEDDING_DEPLOYMENT=/d' "$ENV_FILE" 2>/dev/null || true
        sed -i '/^AZURE_OPENAI_API_VERSION=/d' "$ENV_FILE" 2>/dev/null || true
        
        # Append credentials
        echo "" >> "$ENV_FILE"
        echo "# Azure OpenAI Configuration (fetched from secrets server)" >> "$ENV_FILE"
        echo "AZURE_OPENAI_ENDPOINT=${azure_openai_endpoint}" >> "$ENV_FILE"
        echo "AZURE_OPENAI_API_KEY=${azure_openai_api_key}" >> "$ENV_FILE"
        echo "AZURE_OPENAI_CHAT_DEPLOYMENT=${azure_openai_chat_deployment}" >> "$ENV_FILE"
        echo "AZURE_OPENAI_EMBEDDING_DEPLOYMENT=${azure_openai_embedding_deployment}" >> "$ENV_FILE"
        echo "AZURE_OPENAI_API_VERSION=${azure_openai_api_version}" >> "$ENV_FILE"
        
        echo ""
        echo "✅ Azure OpenAI credentials configured successfully!"
        echo ""
        echo "Your .env file has been updated with:"
        echo "   • AZURE_OPENAI_ENDPOINT"
        echo "   • AZURE_OPENAI_API_KEY"
        echo "   • AZURE_OPENAI_CHAT_DEPLOYMENT"
        echo "   • AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
        echo "   • AZURE_OPENAI_API_VERSION"
    else
        echo "❌ Failed to parse credentials from response"
        exit 1
    fi
elif [ "$http_code" = "401" ]; then
    echo "❌ Invalid workshop token. Please check with your instructor."
    exit 1
else
    echo "❌ Failed to fetch credentials (HTTP $http_code)"
    echo "   Response: $body"
    exit 1
fi
