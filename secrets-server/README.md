# Workshop Secrets Server

An Azure Function that securely distributes Azure OpenAI credentials to workshop attendees using a rotating workshop token.

## How It Works

1. Instructor deploys this Azure Function and configures secrets as App Settings
2. Instructor generates a workshop token for each session
3. Attendees enter the workshop token when starting their Codespace
4. The Codespace setup script fetches credentials from this function
5. Credentials are stored locally in the attendee's `.env` file

## Deployment

### Prerequisites

- Azure CLI installed and logged in
- Azure Functions Core Tools (optional, for local testing)

### Quick Deploy

```bash
# Login to Azure
az login

# Create resource group (if needed)
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

### Configure App Settings

After deployment, configure the secrets in Azure Portal or via CLI:

```bash
az functionapp config appsettings set \
  --name workshop-secrets-server \
  --resource-group rg-workshop-secrets \
  --settings \
    WORKSHOP_TOKEN="your-unique-workshop-token" \
    ADMIN_SECRET="your-secure-admin-secret" \
    AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com" \
    AZURE_OPENAI_API_KEY="your-azure-openai-api-key" \
    AZURE_OPENAI_CHAT_DEPLOYMENT="gpt-4o-mini" \
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT="text-embedding-ada-002" \
    AZURE_OPENAI_API_VERSION="2024-08-01-preview"
```

> **Note:** The `ADMIN_SECRET` is used to authenticate token rotation requests from GitHub Actions. Generate a strong random string.

## Rotating Workshop Tokens

### Option A: GitHub Actions (Recommended)

Use the **"Rotate Workshop Token"** workflow in the repository:

1. Go to **Actions** → **Rotate Workshop Token**
2. Click **Run workflow**
3. Enter a custom token (e.g., `dynatrace2026`) or leave empty to auto-generate
4. View the summary to get the new token

**Required Setup (one-time):**

Add these to repository Settings → Secrets and variables → Actions:

| Type | Name | Description |
|------|------|-------------|
| Secret | `ADMIN_SECRET` | Must match the `ADMIN_SECRET` in Azure Function App Settings |
| Variable | `AZURE_FUNCTION_APP_NAME` | e.g., `workshop-secrets-server` |

> **How it works:** The GitHub Actions workflow calls the `/api/rotate-token` endpoint on the Azure Function, which stores the new token in Azure Blob Storage. No Azure RBAC or service principal required!

### Option B: Direct API Call

You can rotate the token by calling the API directly:

```bash
curl -X POST https://workshop-secrets-server.azurewebsites.net/api/rotate-token \
  -H "Content-Type: application/json" \
  -d '{
    "admin_secret": "your-admin-secret",
    "new_token": "dynatrace2026"
  }'
```

### Option C: Azure CLI (Initial Setup Only)

For the initial token before the rotate endpoint is available:

```bash
# Use a simple, memorable word
NEW_TOKEN="dynatrace2026"

az functionapp config appsettings set \
  --name workshop-secrets-server \
  --resource-group rg-workshop-secrets \
  --settings WORKSHOP_TOKEN="$NEW_TOKEN"
```

> **Note:** Once deployed, the function reads tokens from blob storage first, falling back to the environment variable. Use the API or GitHub Actions for rotation.

## Local Development

1. Install Azure Functions Core Tools
2. Update `local.settings.json` with your test values
3. Run locally:
   ```bash
   func start
   ```
4. Test the endpoint:
   ```bash
   curl -X POST http://localhost:7071/api/get-credentials \
     -H "Content-Type: application/json" \
     -d '{"workshop_token": "your-test-token"}'
   ```

## API Endpoints

### POST /api/get-credentials

Request credentials with a workshop token.

**Request:**
```json
{
  "workshop_token": "instructor-provided-token"
}
```

**Success Response (200):**
```json
{
  "azure_openai_endpoint": "https://...",
  "azure_openai_api_key": "...",
  "azure_openai_chat_deployment": "gpt-4o",
  "azure_openai_embedding_deployment": "dynatrace-ai-agent",
  "azure_openai_api_version": "2024-11-20"
}
```

**Error Response (401):**
```json
{
  "error": "Invalid workshop token. Please check with your instructor."
}
```

### GET /api/health

Health check endpoint.

**Response (200):**
```json
{
  "status": "healthy",
  "service": "workshop-secrets-server"
}
```

### POST /api/rotate-token

Rotate the workshop token. Requires admin authentication.

**Request:**
```json
{
  "admin_secret": "your-admin-secret",
  "new_token": "new-workshop-token"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Workshop token updated successfully"
}
```

**Error Response (401):**
```json
{
  "error": "Unauthorized"
}
```

### POST /api/get-token

Get the current workshop token. Requires admin authentication. Useful for instructors to check/share the current token.

**Request:**
```json
{
  "admin_secret": "your-admin-secret"
}
```

**Success Response (200):**
```json
{
  "token": "current-workshop-token"
}
```

## Security Considerations

- Tokens are compared using constant-time comparison to prevent timing attacks
- A small delay is added on failed attempts to slow brute-force attacks
- All credentials are stored in Azure Function App Settings (encrypted at rest)
- Workshop tokens are stored in Azure Blob Storage (using the function's built-in storage)
- The `ADMIN_SECRET` protects the token rotation endpoint
- Rotate the WORKSHOP_TOKEN after each workshop session
- Consider adding rate limiting via Azure API Management for production use
