#!/bin/bash
# Note: No 'set -e' - we want to continue even if some steps fail

echo "🚀 Setting up Dynatrace AI Observability Workshop Environment..."

# ═══════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════
SECRETS_SERVER_URL="${SECRETS_SERVER_URL:-https://workshop-secrets-server.azurewebsites.net/api}"
ENV_FILE="/workspaces/dynatrace-ai-mcp-workshop/.env"
BASHRC_FILE="$HOME/.bashrc"

# ═══════════════════════════════════════════════════════════════════════════
# Function to add a secret to bashrc (avoiding duplicates)
# ═══════════════════════════════════════════════════════════════════════════
add_secret_to_bashrc() {
    local var_name="$1"
    local var_value="$2"
    
    # Remove any existing entry for this variable
    sed -i "/^export ${var_name}=/d" "$BASHRC_FILE" 2>/dev/null || true
    
    # Append the new value
    echo "export ${var_name}=\"${var_value}\"" >> "$BASHRC_FILE"
}

# ═══════════════════════════════════════════════════════════════════════════
# Function to fetch secrets and store as environment variables (hidden)
# ═══════════════════════════════════════════════════════════════════════════
fetch_workshop_secrets() {
    local token="$1"
    
    echo "🔐 Fetching Azure OpenAI credentials from secrets server..."
    
    # Make request to secrets server
    response=$(curl -s -w "\n%{http_code}" -X POST "${SECRETS_SERVER_URL}/get-credentials" \
        -H "Content-Type: application/json" \
        -d "{\"workshop_token\": \"${token}\"}" 2>/dev/null)
    
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
            # Export to current shell
            export AZURE_OPENAI_ENDPOINT="${azure_openai_endpoint}"
            export AZURE_OPENAI_API_KEY="${azure_openai_api_key}"
            export AZURE_OPENAI_CHAT_DEPLOYMENT="${azure_openai_chat_deployment}"
            export AZURE_OPENAI_EMBEDDING_DEPLOYMENT="${azure_openai_embedding_deployment}"
            export AZURE_OPENAI_API_VERSION="${azure_openai_api_version}"
            
            # Add to bashrc for new terminals (hidden in shell config)
            add_secret_to_bashrc "AZURE_OPENAI_ENDPOINT" "${azure_openai_endpoint}"
            add_secret_to_bashrc "AZURE_OPENAI_API_KEY" "${azure_openai_api_key}"
            add_secret_to_bashrc "AZURE_OPENAI_CHAT_DEPLOYMENT" "${azure_openai_chat_deployment}"
            add_secret_to_bashrc "AZURE_OPENAI_EMBEDDING_DEPLOYMENT" "${azure_openai_embedding_deployment}"
            add_secret_to_bashrc "AZURE_OPENAI_API_VERSION" "${azure_openai_api_version}"
            
            echo "✅ Azure OpenAI credentials configured!"
            return 0
        else
            echo ""
            echo "❌ Failed to parse credentials from server response."
            echo "   Run 'bash .devcontainer/fetch-secrets.sh' to try again."
            echo ""
            return 0  # Don't fail Codespace setup
        fi
    elif [ "$http_code" = "401" ]; then
        echo ""
        echo "❌ Invalid workshop token - the token you entered was not recognized."
        echo "   Please verify the token with your instructor and run:"
        echo "   bash .devcontainer/fetch-secrets.sh"
        echo ""
        return 0  # Don't fail Codespace setup
    else
        echo ""
        echo "❌ Could not reach secrets server (HTTP $http_code)"
        echo "   Run 'bash .devcontainer/fetch-secrets.sh' to try again."
        echo ""
        return 0  # Don't fail Codespace setup
    fi
}

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r /workspaces/dynatrace-ai-mcp-workshop/app/requirements.txt

# ═══════════════════════════════════════════════════════════════════════════
# Set up hidden secrets file (sourced by shell, not visible in .env)
# ═══════════════════════════════════════════════════════════════════════════

# Set ATTENDEE_ID from environment or generate one
if [ -n "$ATTENDEE_ID" ]; then
    export ATTENDEE_ID="${ATTENDEE_ID}"
    add_secret_to_bashrc "ATTENDEE_ID" "${ATTENDEE_ID}"
    echo "✅ Using attendee ID: ${ATTENDEE_ID}"
else
    # Generate a random ID - attendee can change it later
    RANDOM_ID=$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 4 | head -n 1)
    export ATTENDEE_ID="attendee-${RANDOM_ID}"
    add_secret_to_bashrc "ATTENDEE_ID" "attendee-${RANDOM_ID}"
    echo "✨ Generated attendee ID: attendee-${RANDOM_ID}"
fi

# Check for workshop token - if not set, guide user to configure
if [ -n "$WORKSHOP_TOKEN" ]; then
    echo "🔑 Workshop token received (length: ${#WORKSHOP_TOKEN} chars)"
    fetch_workshop_secrets "$WORKSHOP_TOKEN" || true
else
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║  📋 ACTION REQUIRED: Configure Workshop Credentials              ║"
    echo "╠══════════════════════════════════════════════════════════════════╣"
    echo "║                                                                  ║"
    echo "║  Run this command to set up your Azure OpenAI credentials:      ║"
    echo "║                                                                  ║"
    echo "║    bash .devcontainer/fetch-secrets.sh                          ║"
    echo "║                                                                  ║"
    echo "║  Your instructor will provide the workshop token.               ║"
    echo "║                                                                  ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""
fi

# Secrets are now directly in bashrc - no separate file needed

# ═══════════════════════════════════════════════════════════════════════════
# Create Dynatrace credentials template (for attendee to fill in)
# ═══════════════════════════════════════════════════════════════════════════
if [ ! -f "$ENV_FILE" ]; then
    echo "📝 Creating Dynatrace configuration template..."
    cat > "$ENV_FILE" << 'EOF'
# ═══════════════════════════════════════════════════════════════════════════════
# Dynatrace AI Observability Workshop - Configuration
# ═══════════════════════════════════════════════════════════════════════════════
# 
# This file contains your Dynatrace credentials.
# The Azure OpenAI credentials are already configured in your environment.
#
# ═══════════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════════
# DYNATRACE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════
# Get these from your instructor or your Dynatrace environment
# Environment URL format: https://{your-environment-id}.live.dynatrace.com

DT_ENDPOINT=
DT_API_TOKEN=
EOF
    echo "✅ Created .env file - add your Dynatrace credentials"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║     🎯 Dynatrace AI Observability Workshop Environment Ready!    ║"
echo "╠══════════════════════════════════════════════════════════════════╣"
echo "║                                                                  ║"
echo "║  ✅ Azure OpenAI credentials: Configured (hidden)               ║"
echo "║  ✅ Attendee ID: Set in environment                             ║"
echo "║                                                                  ║"
echo "║  📝 ACTION REQUIRED:                                            ║"
echo "║     Edit .env file to add your Dynatrace credentials            ║"
echo "║                                                                  ║"
echo "║  📚 Workshop Guide:                                             ║"
echo "║     https://sudosmitty.github.io/dynatrace-ai-mcp-workshop       ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
