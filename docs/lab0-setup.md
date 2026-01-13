---
layout: default
title: Lab 0 - Environment Setup
nav_order: 2
---

# 🔧 Lab 0: Environment Setup

**Duration:** ~15 minutes

In this lab, you'll set up your workshop environment using GitHub Codespaces and configure the necessary credentials.

---

## 📋 Prerequisites

Before starting, ensure you have:
- ✅ A GitHub account
- ✅ Dynatrace credentials (provided by your instructor)
- ✅ Access to this workshop repository

---

## Step 1: Launch GitHub Codespace

1. Click the button below to launch your personal workshop environment:

   [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/sudosmitty/dynatrace-ai-mcp-workshop?quickstart=1)

2. Wait for the Codespace to build (this takes 2-3 minutes on first launch)

3. Once ready, you'll see VS Code in your browser with the workshop files

> **💡 Important:** Each attendee gets their own **isolated Codespace**. All your code changes stay within your Codespace and won't affect other workshop participants. No need to fork or create branches!

---

## Step 2: Configure Your Environment

### 2.1 Open the Environment File

1. In the VS Code Explorer, locate and open the `.env` file in the root directory

2. If no `.env` file exists, copy from the template:
   ```bash
   cp app/.env.template .env
   ```

### 2.2 Set Your Attendee ID

Replace the placeholder with your initials or a unique identifier:

```bash
# Example: Use your initials or name
ATTENDEE_ID=jsmith
```

> **Important:** This ID will be used to name your service, making it easy to find YOUR traces in the shared Dynatrace environment.

### 2.3 Configure Dynatrace Credentials

Your instructor will provide the following values. Enter them in your `.env` file:

```bash
# Dynatrace Configuration - Get these from your instructor
DT_ENDPOINT=https://YOUR_ENV.live.dynatrace.com/api/v2/otlp
DT_API_TOKEN=dt0c01.XXXXXXXXXX.YYYYYYYYYYYYYYYY
```

### 2.4 Verify Configuration

Your complete `.env` file should look like this:

```bash
# Attendee Configuration
ATTENDEE_ID=jsmith

# Dynatrace Configuration
DT_ENDPOINT=https://abc12345.live.dynatrace.com/api/v2/otlp
DT_API_TOKEN=dt0c01.EXAMPLE_TOKEN_HERE

# App Configuration (leave as default)
APP_HOST=0.0.0.0
APP_PORT=8000
```

---

## Step 3: Verify the Sample Application

Let's make sure everything is working before we add instrumentation.

### 3.1 Start the Application

Open a terminal in VS Code (`Ctrl+`` ` or `Cmd+`` `) and run:

```bash
cd app
python main.py
```

### 3.2 Expected Output

You should see output similar to:

```
╔══════════════════════════════════════════════════════════════════════╗
║         🚀 AI Chat Service Starting...                               ║
║                                                                      ║
║         Attendee ID: jsmith                                          ║
║         Service: ai-chat-service-jsmith                              ║
╚══════════════════════════════════════════════════════════════════════╝

✅ RAG initialized successfully for attendee: jsmith
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 3.3 Test the Application

1. When the application starts, VS Code will show a popup about port 8000. Click **"Open in Browser"**

2. You should see a JSON response:
   ```json
   {
     "status": "healthy",
     "attendee_id": "jsmith",
     "service_name": "ai-chat-service-jsmith"
   }
   ```

3. Test the chat endpoint using the terminal (open a new terminal with `+`):

   ```bash
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "What is Dynatrace?"}'
   ```

4. You should receive an AI-generated response!

### 3.4 Stop the Application

Press `Ctrl+C` in the terminal to stop the application.

---

## ✅ Checkpoint

Before proceeding to Lab 1, verify:

- [ ] Your Codespace is running
- [ ] The `.env` file is configured with your `ATTENDEE_ID`
- [ ] The `.env` file has the `DT_ENDPOINT` and `DT_API_TOKEN` from your instructor
- [ ] The sample application starts without errors
- [ ] You can access the application in your browser
- [ ] The chat endpoint responds with AI-generated text

---

## 🆘 Troubleshooting

### "OPENAI_API_KEY not set"

The OpenAI API key is provided via GitHub Secrets. If you see this error:
1. Make sure you're using the official workshop repository
2. Contact your instructor - they may need to add the secret

### "Connection refused" on port 8000

1. Make sure the application is running
2. Check that port 8000 is being forwarded (look in the Ports tab)

### Application crashes on startup

1. Check your `.env` file for typos
2. Ensure all dependencies are installed: `pip install -r app/requirements.txt`

---

## 🎉 Great Job!

Your environment is ready! Let's move on to adding AI observability instrumentation.

<div class="lab-nav">
  <a href="./">← Home</a>
  <a href="lab1-instrumentation">Lab 1: Instrumentation →</a>
</div>
