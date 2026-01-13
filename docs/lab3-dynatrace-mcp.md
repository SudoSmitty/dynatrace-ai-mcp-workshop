---
layout: default
title: Lab 3 - Dynatrace MCP
nav_order: 5
---

# 🤖 Lab 3: Using Dynatrace MCP for Agentic AI

**Duration:** ~45 minutes

In this lab, you'll configure and use the Dynatrace MCP (Model Context Protocol) server to interact with Dynatrace directly from your IDE using AI assistants like GitHub Copilot.

---

## 🎯 Learning Objectives

- Understand what MCP is and how it enables agentic AI
- Install and configure the Dynatrace MCP server
- Use natural language to query Dynatrace from VS Code
- Analyze problems and traces using AI assistance
- Explore real-world use cases for observability-driven AI

---

## What is MCP?

**Model Context Protocol (MCP)** is an open standard that allows AI assistants to interact with external tools and data sources. With Dynatrace MCP, you can:

- Query Dynatrace using natural language
- Analyze problems and incidents
- Retrieve metrics, traces, and logs
- Get AI-powered insights about your applications

Think of it as giving your AI assistant **direct access to Dynatrace**!

---

## Step 1: Install Dynatrace MCP Server

The Dynatrace MCP server runs locally and connects your AI assistant to Dynatrace.

### 1.1 Install via NPM

In your Codespace terminal, run:

```bash
npm install -g @dynatrace/mcp-server
```

### 1.2 Verify Installation

```bash
dynatrace-mcp --version
```

You should see the version number printed.

---

## Step 2: Configure MCP for VS Code

### 2.1 Create MCP Configuration

Create the VS Code MCP settings file:

```bash
mkdir -p ~/.vscode-server/data/User/globalStorage/github.copilot
```

Create the configuration file at `~/.vscode-server/data/User/globalStorage/github.copilot/mcp.json`:

```json
{
  "mcpServers": {
    "dynatrace": {
      "command": "dynatrace-mcp",
      "args": [],
      "env": {
        "DT_ENDPOINT": "https://YOUR_ENV.live.dynatrace.com",
        "DT_API_TOKEN": "YOUR_API_TOKEN"
      }
    }
  }
}
```

### 2.2 Update with Your Credentials

Replace the placeholders with your actual Dynatrace credentials (same ones from Lab 0):

```json
{
  "mcpServers": {
    "dynatrace": {
      "command": "dynatrace-mcp",
      "args": [],
      "env": {
        "DT_ENDPOINT": "https://abc12345.live.dynatrace.com",
        "DT_API_TOKEN": "dt0c01.XXXXXXXXXX.YYYYYYYYYYYYYYYY"
      }
    }
  }
}
```

> **Tip:** You can copy the values from your `.env` file

### 2.3 Restart VS Code

For the MCP configuration to take effect:

1. Open the Command Palette (`Cmd+Shift+P` or `Ctrl+Shift+P`)
2. Type **"Developer: Reload Window"**
3. Press Enter

---

## Step 3: Verify MCP Connection

### 3.1 Open GitHub Copilot Chat

1. Click on the Copilot icon in the left sidebar
2. Or use keyboard shortcut: `Cmd+Shift+I` (Mac) / `Ctrl+Shift+I` (Windows)

### 3.2 Test the Connection

In the Copilot chat, type:

```
@dynatrace What services are available in my environment?
```

If configured correctly, Copilot will query Dynatrace and return a list of services!

---

## Step 4: Query Your AI Service

Let's use MCP to analyze your instrumented AI service.

### 4.1 Find Your Service

```
@dynatrace Tell me about the service called ai-chat-service-{YOUR_ATTENDEE_ID}
```

Replace `{YOUR_ATTENDEE_ID}` with your actual attendee ID.

### 4.2 Get Service Metrics

```
@dynatrace What is the average response time for ai-chat-service-jsmith in the last hour?
```

### 4.3 Analyze Token Usage

```
@dynatrace Show me the token usage for my AI service
```

---

## Step 5: Explore Traces with MCP

### 5.1 Get Recent Traces

```
@dynatrace Show me the last 5 traces for ai-chat-service-{YOUR_ATTENDEE_ID}
```

### 5.2 Analyze Slow Requests

```
@dynatrace Are there any slow requests in my AI service? What's causing them?
```

### 5.3 Trace Details

```
@dynatrace Explain the trace flow for a typical chat request in my AI service
```

---

## Step 6: Problem Analysis

### 6.1 Check for Problems

```
@dynatrace Are there any open problems in the environment?
```

### 6.2 Analyze a Problem (if any exist)

```
@dynatrace Tell me about the most recent problem and its root cause
```

### 6.3 Get Recommendations

```
@dynatrace Based on my AI service performance, what improvements would you recommend?
```

---

## Step 7: Advanced Queries

### 7.1 DQL Queries via MCP

You can ask MCP to run DQL queries:

```
@dynatrace Run this query: fetch spans | filter service.name == "ai-chat-service-jsmith" | summarize count() by span.name
```

### 7.2 Compare Performance

```
@dynatrace Compare the performance of embedding calls vs LLM completion calls in my service
```

### 7.3 Cost Analysis

```
@dynatrace Estimate the OpenAI API costs based on token usage for my service today
```

---

## Step 8: Agentic Workflows

MCP enables powerful agentic workflows where AI assistants can take action based on observability data.

### 8.1 Proactive Analysis

```
@dynatrace Analyze my AI service and suggest optimizations to reduce token usage while maintaining response quality
```

### 8.2 Debugging Assistance

```
@dynatrace Help me understand why some of my RAG queries might be slow. Look at the trace data for patterns.
```

### 8.3 Documentation Generation

```
@dynatrace Generate a summary of my AI service's architecture based on the service flow data
```

---

## 🔬 Hands-On Exercises

### Exercise 1: Service Health Report

Use MCP to generate a health report for your service:

```
@dynatrace Create a health report for ai-chat-service-{YOUR_ATTENDEE_ID} including:
- Request rate
- Error rate
- Average response time
- Token usage summary
```

### Exercise 2: Custom Analysis

Ask MCP to analyze a specific aspect of your AI service:

```
@dynatrace Analyze the relationship between prompt length and response time in my AI service
```

### Exercise 3: Incident Response Simulation

Practice using MCP for incident response:

```
@dynatrace If my AI service suddenly had a 50% increase in response time, what steps would you recommend to diagnose the issue?
```

---

## Step 9: MCP Best Practices

### 9.1 Effective Prompting

**Good prompts are specific:**

✅ Good: `@dynatrace Show me the P95 response time for ai-chat-service-jsmith over the last 4 hours`

❌ Vague: `@dynatrace How is my service doing?`

### 9.2 Iterative Queries

Start broad, then drill down:

1. `@dynatrace Show me an overview of my AI service`
2. `@dynatrace What are the slowest endpoints?`
3. `@dynatrace Why is /chat endpoint slow?`
4. `@dynatrace Show me slow traces for /chat`

### 9.3 Combining with Code

You can use MCP alongside your code:

```
I'm looking at main.py line 150 where I call OpenAI. 
@dynatrace What's the average latency for OpenAI calls from my service?
```

---

## ✅ Checkpoint

Before completing the workshop, verify:

- [ ] Dynatrace MCP server is installed
- [ ] MCP is configured in VS Code
- [ ] You can query Dynatrace using `@dynatrace` in Copilot Chat
- [ ] You've successfully retrieved information about your AI service
- [ ] You understand how to use MCP for problem analysis
- [ ] You've explored agentic workflow capabilities

---

## 🆘 Troubleshooting

### "MCP server not found"

1. Verify installation: `which dynatrace-mcp`
2. Reinstall: `npm install -g @dynatrace/mcp-server`

### "@dynatrace not recognized"

1. Check the mcp.json configuration file exists
2. Verify the JSON syntax is valid
3. Reload VS Code window

### "Authentication failed"

1. Verify your API token in the mcp.json file
2. Ensure the token has appropriate permissions:
   - `Read entities`
   - `Read problems`
   - `Read metrics`
   - `Read logs`
   - `Read traces`

### "No data returned"

1. Verify the Dynatrace endpoint URL is correct
2. Check that your service is sending data
3. Try a simpler query first: `@dynatrace List all services`

---

## 🎓 What You've Learned

Congratulations! In this lab, you've learned how to:

1. ✅ Install and configure Dynatrace MCP server
2. ✅ Connect your IDE to Dynatrace via MCP
3. ✅ Query observability data using natural language
4. ✅ Analyze traces and performance from your IDE
5. ✅ Use agentic AI for observability workflows

---

## 🚀 Next Steps

Now that you've completed the workshop, consider:

- Exploring more MCP capabilities with your own applications
- Creating custom dashboards for AI service monitoring
- Setting up alerts for LLM token usage and latency
- Integrating MCP into your daily development workflow

---

## 🎉 Workshop Complete!

You've successfully completed the Dynatrace AI Observability Workshop! 

<div class="lab-nav">
  <a href="lab2-explore-traces">← Lab 2: Explore Traces</a>
  <a href="resources">View Resources →</a>
</div>
