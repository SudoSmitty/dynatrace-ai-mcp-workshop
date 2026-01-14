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

## Step 2: Configure Workshop Credentials

After the Codespace starts, you'll see a message asking you to configure your credentials.

### 2.1 Run the Setup Script

Open a terminal in VS Code (`Ctrl+`` ` or `Cmd+`` `) and run:

```bash
bash .devcontainer/fetch-secrets.sh
```

### 2.2 Enter Your Credentials

You'll be prompted for:
1. **Attendee ID** - Enter your initials (e.g., `jsmith`) or press Enter to auto-generate
2. **Workshop Token** - Your instructor will provide this

```
🔐 Workshop Credentials Setup

Enter your attendee ID (e.g., your name or initials, no spaces) [press enter to generate]: jsmith
✅ Attendee ID: jsmith

Enter your workshop token: dynatrace2026
✅ Azure OpenAI credentials configured!
```

---

## Step 3: Configure Dynatrace Credentials

Your Attendee ID and Azure OpenAI credentials are now configured as environment variables. You just need to add your Dynatrace credentials.

### 3.1 Open the Environment File

1. In the VS Code Explorer, locate and open the `.env` file in the root directory

2. You'll see it only contains placeholders for Dynatrace credentials

### 3.2 Add Dynatrace Credentials

Your instructor will provide the following values. Enter them in your `.env` file:

```bash
# Dynatrace Configuration - Get these from your instructor
DT_ENDPOINT=https://YOUR_ENV.live.dynatrace.com/api/v2/otlp
DT_API_TOKEN=dt0c01.XXXXXXXXXX.YYYYYYYYYYYYYYYY
```

### 3.3 Verify Configuration

Your complete `.env` file should look like this:

```bash
# Dynatrace Configuration
DT_ENDPOINT=https://abc12345.live.dynatrace.com/api/v2/otlp
DT_API_TOKEN=dt0c01.EXAMPLE_TOKEN_HERE
```

> **ℹ️ Note:** Azure OpenAI credentials and your Attendee ID are stored as environment variables (not in the `.env` file) for security.

To verify your environment variables are set, run in the terminal:

```bash
echo "Attendee: $ATTENDEE_ID"
echo "Azure OpenAI: ${AZURE_OPENAI_ENDPOINT:+configured}"
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

2. You should see the **AI Chat Interface** - a beautiful web UI for chatting with the AI assistant!

3. Try sending a message like:
   > "What is Dynatrace?"

4. You should receive an AI-generated response in the chat!

> **💡 Tip:** If you miss the popup, click the **Ports** tab in VS Code, find port 8000, and click the 🌐 globe icon.

### 3.4 Stop the Application

Press `Ctrl+C` in the terminal to stop the application.

---

## ✅ Checkpoint

Before proceeding to Lab 1, verify:

- [ ] Your Codespace is running
- [ ] The `.env` file has your `ATTENDEE_ID` (set via Codespace prompt)
- [ ] The `.env` file has `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY` (fetched via workshop token)
- [ ] The `.env` file has the `DT_ENDPOINT` and `DT_API_TOKEN` from your instructor
- [ ] The sample application starts without errors
- [ ] You can access the application in your browser
- [ ] The chat endpoint responds with AI-generated text

---

## 🆘 Troubleshooting

### "Azure OpenAI credentials not found"

If you skipped entering the workshop token during Codespace creation:
1. Get the workshop token from your instructor
2. Run: `bash .devcontainer/fetch-secrets.sh`
3. Enter the workshop token when prompted
4. Verify your `.env` file now has the Azure OpenAI credentials

### "Invalid workshop token"

1. Double-check you've entered the token correctly
2. Make sure there are no extra spaces
3. Ask your instructor to verify the token is correct

### Missing or wrong ATTENDEE_ID

If you skipped the Attendee ID prompt or want to change it:
1. Open the `.env` file
2. Update the `ATTENDEE_ID=` line with your initials

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
