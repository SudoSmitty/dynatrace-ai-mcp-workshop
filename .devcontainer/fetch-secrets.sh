#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# Fetch Workshop Secrets
# Run this script if you need to re-fetch Azure OpenAI credentials
# Secrets are stored directly in ~/.bashrc (no separate file)
# ═══════════════════════════════════════════════════════════════════════════

SECRETS_SERVER_URL="${SECRETS_SERVER_URL:-https://workshop-secrets-server.azurewebsites.net/api}"
BASHRC_FILE="$HOME/.bashrc"

# Function to add a secret to bashrc (avoiding duplicates)
add_secret_to_bashrc() {
    local var_name="$1"
    local var_value="$2"
    
    # Remove any existing entry for this variable
    sed -i "/^export ${var_name}=/d" "$BASHRC_FILE" 2>/dev/null || true
    
    # Append the new value
    echo "export ${var_name}=\"${var_value}\"" >> "$BASHRC_FILE"
}

echo "🔐 Workshop Credentials Setup"
echo ""

# Prompt for attendee ID
current_attendee="${ATTENDEE_ID:-}"
read -p "Enter your attendee ID (e.g., your initials) [${current_attendee:-press enter to generate}]: " input_attendee

if [ -n "$input_attendee" ]; then
    ATTENDEE_ID="$input_attendee"
elif [ -z "$current_attendee" ]; then
    RANDOM_ID=$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 4 | head -n 1)
    ATTENDEE_ID="attendee-${RANDOM_ID}"
else
    ATTENDEE_ID="$current_attendee"
fi

# Set attendee ID
export ATTENDEE_ID
add_secret_to_bashrc "ATTENDEE_ID" "$ATTENDEE_ID"
echo "✅ Attendee ID: $ATTENDEE_ID"
echo ""

# Prompt for workshop token
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
        # Export to current shell
        export AZURE_OPENAI_ENDPOINT="${azure_openai_endpoint}"
        export AZURE_OPENAI_API_KEY="${azure_openai_api_key}"
        export AZURE_OPENAI_CHAT_DEPLOYMENT="${azure_openai_chat_deployment}"
        export AZURE_OPENAI_EMBEDDING_DEPLOYMENT="${azure_openai_embedding_deployment}"
        export AZURE_OPENAI_API_VERSION="${azure_openai_api_version}"
        
        # Add to bashrc for new terminals
        add_secret_to_bashrc "AZURE_OPENAI_ENDPOINT" "${azure_openai_endpoint}"
        add_secret_to_bashrc "AZURE_OPENAI_API_KEY" "${azure_openai_api_key}"
        add_secret_to_bashrc "AZURE_OPENAI_CHAT_DEPLOYMENT" "${azure_openai_chat_deployment}"
        add_secret_to_bashrc "AZURE_OPENAI_EMBEDDING_DEPLOYMENT" "${azure_openai_embedding_deployment}"
        add_secret_to_bashrc "AZURE_OPENAI_API_VERSION" "${azure_openai_api_version}"
        
        echo ""
        echo "✅ Azure OpenAI credentials configured!"
        echo ""
        echo "The following environment variables are now set:"
        echo "   • AZURE_OPENAI_ENDPOINT"
        echo "   • AZURE_OPENAI_API_KEY"
        echo "   • AZURE_OPENAI_CHAT_DEPLOYMENT"
        echo "   • AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
        echo "   • AZURE_OPENAI_API_VERSION"
        echo ""
        echo "🔄 Open a new terminal or run: source ~/.bashrc"
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
