#!/bin/bash
set -e

echo "🚀 Setting up Dynatrace AI Observability Workshop Environment..."

# ═══════════════════════════════════════════════════════════════════════════
# Secrets Server Configuration
# ═══════════════════════════════════════════════════════════════════════════
SECRETS_SERVER_URL="${SECRETS_SERVER_URL:-https://workshop-secrets-server.azurewebsites.net/api}"

# ═══════════════════════════════════════════════════════════════════════════
# Function to fetch secrets from the workshop secrets server
# ═══════════════════════════════════════════════════════════════════════════
fetch_workshop_secrets() {
    local token="$1"
    local env_file="$2"
    
    echo "🔐 Fetching Azure OpenAI credentials from secrets server..."
    
    # Make request to secrets server
    response=$(curl -s -w "\n%{http_code}" -X POST "${SECRETS_SERVER_URL}/get-credentials" \
        -H "Content-Type: application/json" \
        -d "{\"workshop_token\": \"${token}\"}" 2>/dev/null)
    
    # Extract HTTP status code (last line) and body (everything else)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        # Parse JSON response and write to .env file
        azure_openai_endpoint=$(echo "$body" | grep -o '"azure_openai_endpoint":"[^"]*"' | cut -d'"' -f4)
        azure_openai_api_key=$(echo "$body" | grep -o '"azure_openai_api_key":"[^"]*"' | cut -d'"' -f4)
        azure_openai_chat_deployment=$(echo "$body" | grep -o '"azure_openai_chat_deployment":"[^"]*"' | cut -d'"' -f4)
        azure_openai_embedding_deployment=$(echo "$body" | grep -o '"azure_openai_embedding_deployment":"[^"]*"' | cut -d'"' -f4)
        azure_openai_api_version=$(echo "$body" | grep -o '"azure_openai_api_version":"[^"]*"' | cut -d'"' -f4)
        
        # Update .env file with Azure OpenAI credentials
        if [ -n "$azure_openai_endpoint" ] && [ -n "$azure_openai_api_key" ]; then
            # Remove any existing Azure OpenAI entries
            sed -i '/^AZURE_OPENAI_ENDPOINT=/d' "$env_file" 2>/dev/null || true
            sed -i '/^AZURE_OPENAI_API_KEY=/d' "$env_file" 2>/dev/null || true
            sed -i '/^AZURE_OPENAI_CHAT_DEPLOYMENT=/d' "$env_file" 2>/dev/null || true
            sed -i '/^AZURE_OPENAI_EMBEDDING_DEPLOYMENT=/d' "$env_file" 2>/dev/null || true
            sed -i '/^AZURE_OPENAI_API_VERSION=/d' "$env_file" 2>/dev/null || true
            
            # Append credentials
            echo "" >> "$env_file"
            echo "# Azure OpenAI Configuration (fetched from secrets server)" >> "$env_file"
            echo "AZURE_OPENAI_ENDPOINT=${azure_openai_endpoint}" >> "$env_file"
            echo "AZURE_OPENAI_API_KEY=${azure_openai_api_key}" >> "$env_file"
            echo "AZURE_OPENAI_CHAT_DEPLOYMENT=${azure_openai_chat_deployment}" >> "$env_file"
            echo "AZURE_OPENAI_EMBEDDING_DEPLOYMENT=${azure_openai_embedding_deployment}" >> "$env_file"
            echo "AZURE_OPENAI_API_VERSION=${azure_openai_api_version}" >> "$env_file"
            
            echo "✅ Azure OpenAI credentials configured successfully!"
            return 0
        else
            echo "❌ Failed to parse credentials from response"
            return 1
        fi
    elif [ "$http_code" = "401" ]; then
        echo "❌ Invalid workshop token. Please check with your instructor."
        return 1
    else
        echo "❌ Failed to fetch credentials (HTTP $http_code)"
        echo "   Response: $body"
        return 1
    fi
}

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r /workspaces/dynatrace-ai-mcp-workshop/app/requirements.txt

# Create attendee configuration if it doesn't exist
ENV_FILE="/workspaces/dynatrace-ai-mcp-workshop/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "📝 Creating environment configuration template..."
    cp /workspaces/dynatrace-ai-mcp-workshop/app/.env.template "$ENV_FILE"
    
    # Generate a unique attendee ID if not set
    if [ -z "$ATTENDEE_ID" ]; then
        RANDOM_ID=$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 4 | head -n 1)
        sed -i "s/ATTENDEE_ID=your-initials-here/ATTENDEE_ID=attendee-${RANDOM_ID}/" "$ENV_FILE"
        echo "✨ Generated unique attendee ID: attendee-${RANDOM_ID}"
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════
# Fetch secrets using workshop token
# ═══════════════════════════════════════════════════════════════════════════
# Check if we already have Azure OpenAI credentials
if grep -q "^AZURE_OPENAI_API_KEY=.\+" "$ENV_FILE" 2>/dev/null; then
    echo "✅ Azure OpenAI credentials already configured"
else
    # WORKSHOP_TOKEN is provided via Codespaces recommended secret prompt
    if [ -n "$WORKSHOP_TOKEN" ]; then
        echo "🔐 Fetching Azure OpenAI credentials using workshop token..."
        fetch_workshop_secrets "$WORKSHOP_TOKEN" "$ENV_FILE"
    else
        echo ""
        echo "⚠️  No workshop token found."
        echo "   If you skipped the token prompt, run: bash .devcontainer/fetch-secrets.sh"
        echo ""
    fi
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║     🎯 Dynatrace AI Observability Workshop Environment Ready!    ║"
echo "╠══════════════════════════════════════════════════════════════════╣"
echo "║                                                                  ║"
echo "║  📚 Open the workshop guide:                                     ║"
echo "║     https://sudosmitty.github.io/dynatrace-ai-mcp-workshop       ║"
echo "║                                                                  ║"
echo "║  🔧 Next Steps:                                                  ║"
echo "║     1. Verify your .env file has all credentials                 ║"
echo "║     2. Follow the workshop labs                                  ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
