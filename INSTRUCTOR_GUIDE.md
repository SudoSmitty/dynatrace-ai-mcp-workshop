# Dynatrace AI Observability Workshop - Instructor Guide

This document provides guidance for instructors running the workshop.

## Pre-Workshop Checklist

### 1 Week Before

- [ ] Verify Dynatrace playground tenant access
- [ ] Create API token with required permissions
- [ ] Verify Azure OpenAI resource is provisioned and accessible
- [ ] Verify the secrets server Azure Function is accessible (already deployed at `workshop-secrets-server.azurewebsites.net`)
- [ ] Test Codespace creation end-to-end
- [ ] Prepare attendee credential sharing document

> **Important:** Attendees share the same repository—they don't fork it. Each attendee launches their own isolated Codespace environment where all code modifications stay private to their session.

### Day Before

- [ ] Verify Dynatrace tenant is accessible
- [ ] Test API token is working
- [ ] Verify Azure OpenAI deployments are responding
- [ ] Generate a new workshop token and update the secrets server
- [ ] Test the full flow: Codespace → workshop token → app runs
- [ ] Prepare backup credentials if needed
- [ ] Send reminder to attendees with GitHub account requirements

### Day Of

- [ ] Verify all systems operational
- [ ] Have backup plans ready
- [ ] Prepare screen sharing for demos
- [ ] Have troubleshooting guide handy

---

## Secrets Server Setup

The workshop uses an Azure Function to securely distribute Azure OpenAI credentials to attendees. This avoids sharing raw API keys and allows token rotation per workshop.

> **Note:** The secrets server is already deployed at `https://workshop-secrets-server.azurewebsites.net`. You typically do **not** need to redeploy it. The sections below are provided for reference in case you need to set up a new instance or troubleshoot the existing one.

### Initial Deployment (Reference Only - Already Deployed)

```bash
# Login to Azure
az login

# Create resource group
az group create --name rg-workshop-secrets --location eastus

# Create storage account (required for Azure Functions)
az storage account create \
  --name stworkshopsecrets \
  --resource-group rg-workshop-secrets \
  --location eastus \
  --sku Standard_LRS

# Create Function App
az functionapp create \
  --name workshop-secrets-server \
  --resource-group rg-workshop-secrets \
  --storage-account stworkshopsecrets \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --os-type linux

# Deploy the function
cd secrets-server
func azure functionapp publish workshop-secrets-server
```

### Configure Azure OpenAI Credentials (Reference Only)

> **Current Configuration:** The secrets server is already configured with the correct Azure OpenAI credentials. Only update these if credentials have changed.

```bash
az functionapp config appsettings set \
  --name workshop-secrets-server \
  --resource-group rg-workshop-secrets \
  --settings \
    AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com" \
    AZURE_OPENAI_API_KEY="your-azure-openai-api-key" \
    AZURE_OPENAI_CHAT_DEPLOYMENT="gpt-4o" \
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT="dynatraceRAG" \
    AZURE_OPENAI_API_VERSION="2025-07-01-preview"
```

> **Critical:** The API version must be `2025-07-01-preview` - newer versions return 404 errors. The embedding deployment uses `text-embedding-3-large` under the name `dynatraceRAG`.

### Generate Workshop Token (Per Workshop)

You can rotate the workshop token using the GitHub Actions workflow or manually via Azure CLI.

#### Option A: GitHub Actions (Recommended)

1. Go to the repository's **Actions** tab
2. Select **"Rotate Workshop Token"** workflow
3. Click **"Run workflow"**
4. Enter a custom token (e.g., `dynatrace2026`)
5. Click **"Run workflow"**
6. View the workflow summary to see the new token

#### Option B: Azure CLI (Manual)

```bash
# Use a simple word or phrase - easy to share verbally!
# Examples: dynatrace2026, aiworkshop, observability
NEW_TOKEN="dynatrace2026"

# Update the function app setting
az functionapp config appsettings set \
  --name workshop-secrets-server \
  --resource-group rg-workshop-secrets \
  --settings WORKSHOP_TOKEN="$NEW_TOKEN"

echo "Workshop Token: $NEW_TOKEN"
```

> **Tip:** Use simple, memorable words that are easy to share verbally and type correctly.

### Verify Setup

```bash
# Test the endpoint
curl -X POST https://workshop-secrets-server.azurewebsites.net/api/get-credentials \
  -H "Content-Type: application/json" \
  -d '{"workshop_token": "YOUR_TOKEN_HERE"}'
```

---

## How Secrets Work

The workshop uses a security-first approach to credential distribution:

### What Attendees See

1. **Codespace starts** - No prompts during creation (cleaner UX)
2. **Terminal shows prompt** - Asks them to run `fetch-secrets.sh`
3. **Interactive setup** - They enter attendee ID and workshop token (visible, not masked)
4. **In `.env` file:** Only Dynatrace credentials (which they need to enter manually)
5. **Azure OpenAI credentials:** Hidden in `~/.bashrc`

### How It Works Internally

1. When the Codespace starts, `setup.sh` runs
2. It generates a random attendee ID and shows a prompt to run `fetch-secrets.sh`
3. Attendee runs `fetch-secrets.sh` which prompts for ID and workshop token
4. Script fetches Azure OpenAI credentials from the secrets server
5. Credentials are exported directly to `~/.bashrc` as environment variables
6. No intermediate files are created - secrets exist only in memory and bashrc
7. Python's `os.getenv()` reads these environment variables seamlessly

### Why This Approach?

- **Security:** Attendees never see Azure OpenAI API keys (buried in bashrc, no obvious files)
- **Simplicity:** One token shared verbally; no credential files to distribute
- **Flexibility:** Token can be rotated per workshop without changing documentation
- **Isolation:** Each Codespace is independent with its own environment
- **No files to find:** No `.workshop-secrets` or similar files for curious attendees to discover

### Attendee Troubleshooting

If an attendee's Azure OpenAI credentials aren't working:

```bash
# Check if secrets are loaded
echo "Azure: ${AZURE_OPENAI_ENDPOINT:+configured}"
echo "Attendee: $ATTENDEE_ID"

# Re-fetch credentials (will prompt for workshop token)
bash .devcontainer/fetch-secrets.sh

# Then reload bashrc or open a new terminal
source ~/.bashrc
```

> **Note:** If an attendee asks where the secrets are stored, they're in `~/.bashrc`. This is intentionally obscure - most attendees won't think to look there.

---

## Credential Distribution

Create a simple slide or document to share with attendees:

```
╔═══════════════════════════════════════════════════════════════╗
║          Dynatrace AI Workshop - Credentials                  ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  After your Codespace starts, run this command:               ║
║                                                               ║
║    bash .devcontainer/fetch-secrets.sh                        ║
║                                                               ║
║  You'll be prompted for:                                      ║
║    • Attendee ID: (your initials, e.g., jsmith)              ║
║    • Workshop Token: dynatrace2026                            ║
║                                                               ║
║  ─────────────────────────────────────────────────────────────║
║                                                               ║
║  Then add to your .env file:                                  ║
║                                                               ║
║  DT_ENDPOINT:                                                 ║
║  https://abc12345.live.dynatrace.com/api/v2/otlp             ║
║                                                               ║
║  DT_API_TOKEN:                                                ║
║  dt0c01.XXXXXXXXXX.YYYYYYYYYYYYYYYYYYYYYYYYYYYY              ║
║                                                               ║
║  ─────────────────────────────────────────────────────────────║
║                                                               ║
║  Dynatrace UI:                                                ║
║  https://abc12345.live.dynatrace.com                          ║
║  Username: workshop@example.com                               ║
║  Password: [provided verbally]                                ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

> **Tip:** The workshop token is visible when attendees type it (not masked), making it easier to verify they entered it correctly.

---

## Timing Guide

| Time | Activity | Notes |
|------|----------|-------|
| 0:00-0:15 | Introduction & Lab 0 | Welcome, objectives, environment setup |
| 0:15-0:30 | Lab 1 | Instrumentation - most hands-on coding |
| 0:30-1:00 | Lab 2 | Dynatrace exploration - lots of screen sharing |
| 1:00-1:30 | Lab 3 | MCP - interactive, exploratory |
| 1:30-1:45 | Wrap-up | Q&A, resources, feedback |
---

## Common Issues & Solutions

### Codespace Won't Start

**Symptom:** Codespace creation hangs or fails
**Solution:** 
1. Check GitHub status page
2. Try a different browser
3. Have attendee create from repo page directly

### Azure OpenAI Errors

**Symptom:** "API key invalid", "Resource not found", 404 errors, or rate limiting
**Solution:**
1. Verify the secrets server is running: `curl https://workshop-secrets-server.azurewebsites.net/api/health`
2. Check the workshop token is correct in the secrets server app settings
3. Check Azure OpenAI resource quotas in Azure Portal
4. Verify deployment names match (`gpt-4o-mini` for chat, `dynatraceRAG` for embeddings)
5. Verify API version is `2025-07-01-preview` (newer versions return 404)
6. Have attendees re-run: `bash .devcontainer/fetch-secrets.sh`

### Invalid Workshop Token

**Symptom:** Attendee gets "Invalid workshop token" error
**Solution:**
1. Verify the workshop token on your slide matches the one configured in the secrets server
2. Check for copy/paste errors (extra spaces, missing characters)
3. Have attendee re-run: `bash .devcontainer/fetch-secrets.sh`

### No Traces in Dynatrace

**Symptom:** Application runs but no traces appear
**Solution:**
1. Verify DT_ENDPOINT format (must include /api/v2/otlp)
2. Check API token permissions
3. Wait 1-2 minutes for data to appear
4. Check for typos in .env file

### MCP Not Connecting

**Symptom:** @dynatrace commands not recognized
**Solution:**
1. Verify mcp.json configuration
2. Reload VS Code window
3. Check Node.js installation: `node --version`
4. Reinstall MCP: `npm install -g @dynatrace/mcp-server`

---

## Demo Script

### Lab 2 Demo Points

When showing Dynatrace UI:

1. **Service Discovery**
   - Show how service name includes attendee ID
   - Explain automatic service detection

2. **Trace Analysis**
   - Walk through a complete trace
   - Highlight LLM-specific attributes
   - Show token usage

3. **DQL Queries**
   - Demo live query execution
   - Show how to iterate on queries

### Lab 3 Demo Points

When showing MCP:

1. **Basic Queries**
   - Start with simple queries
   - Show natural language flexibility

2. **Problem Analysis**
   - If problems exist, demo analysis
   - Otherwise, explain the capability

3. **Agentic Workflows**
   - Show how MCP enables multi-step analysis
   - Demonstrate follow-up questions

---

## Backup Plans

### If Dynatrace Unavailable

- Use pre-recorded demo videos
- Focus on instrumentation concepts
- Show screenshots of expected results

### If Azure OpenAI Unavailable

- Have a backup Azure OpenAI resource in a different region
- Focus on instrumentation patterns
- Can still explain the concepts

### If Codespaces Unavailable

- Provide local setup instructions
- Use Docker alternative:
  ```bash
  docker pull python:3.11
  docker run -it -v $(pwd):/app python:3.11 bash
  ```

---

## Feedback Collection

At the end of the workshop, ask attendees:

1. What was the most valuable part?
2. What could be improved?
3. Would you use these tools in production?
4. Any additional topics you'd like covered?

---

## Post-Workshop

- [ ] Rotate API tokens
- [ ] Clean up Dynatrace data (optional)
- [ ] Collect and review feedback
- [ ] Update materials based on learnings
- [ ] Share resources with attendees
