#!/bin/bash
set -e

echo "🚀 Setting up Dynatrace AI Observability Workshop Environment..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r /workspaces/dynatrace-ai-mcp-workshop/app/requirements.txt

# Create attendee configuration if it doesn't exist
if [ ! -f /workspaces/dynatrace-ai-mcp-workshop/.env ]; then
    echo "📝 Creating environment configuration template..."
    cp /workspaces/dynatrace-ai-mcp-workshop/app/.env.template /workspaces/dynatrace-ai-mcp-workshop/.env
    
    # Generate a unique attendee ID if not set
    if [ -z "$ATTENDEE_ID" ]; then
        RANDOM_ID=$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 4 | head -n 1)
        echo "ATTENDEE_ID=attendee-${RANDOM_ID}" >> /workspaces/dynatrace-ai-mcp-workshop/.env
        echo "✨ Generated unique attendee ID: attendee-${RANDOM_ID}"
    fi
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║     🎯 Dynatrace AI Observability Workshop Environment Ready!    ║"
echo "╠══════════════════════════════════════════════════════════════════╣"
echo "║                                                                  ║"
echo "║  📚 Open the workshop guide:                                     ║"
echo "║     https://YOUR_GITHUB_USERNAME.github.io/dynatrace-ai-mcp-workshop  ║"
echo "║                                                                  ║"
echo "║  🔧 Next Steps:                                                  ║"
echo "║     1. Edit the .env file with your details                      ║"
echo "║     2. Follow the workshop labs                                  ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
