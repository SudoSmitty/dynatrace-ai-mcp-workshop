---
layout: default
title: Lab 3 - Dynatrace MCP
nav_order: 5
---

# 🤖 Lab 3: Using Dynatrace MCP for Agentic AI

**Duration:** ~30 minutes

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

<div class="why-dynatrace" markdown="1">

## 🏆 Why Dynatrace MCP is Different

Other tools let you *see* traces. Dynatrace MCP lets you:

| Capability | Basic AI Assistants | Dynatrace MCP |
|------------|---------------------|---------------|
| Query observability data | ❌ No access | ✅ Natural language queries |
| Correlate AI + infrastructure | ❌ Separate tools | ✅ Unified view via Davis AI |
| Root cause analysis | ❌ You investigate | ✅ Davis AI explains issues |
| Take action | ❌ Copy/paste to other tools | ✅ Trigger workflows from IDE |
| Business context | ❌ Technical data only | ✅ Link tokens to user impact |

**The difference:** Ask "Why is my AI service slow?" and get answers that connect LLM latency to Azure region issues to user experience — all in one response.

</div>

---

## Step 1: Configure the Dynatrace MCP Server

The Dynatrace MCP server is already pre-configured in this workshop! You just need to add your Dynatrace environment URL (provided by your instructor).

### 1.1 Open the MCP Configuration

The MCP configuration file is located at `.vscode/mcp.json` in your workspace. Open it:

1. In the Explorer panel, expand the `.vscode` folder
2. Click on `mcp.json` to open it

You'll see the following configuration:

```json
{
  "servers": {
    "npx-dynatrace-mcp-server": {
      "command": "npx",
      "args": ["-y", "@dynatrace-oss/dynatrace-mcp-server@latest"],
      "env": {
        "DT_ENVIRONMENT": ""
      }
    }
  }
}
```

### 1.2 Add Your Dynatrace Environment URL

Update the `DT_ENVIRONMENT` value with your Dynatrace environment URL (provided by your instructor):

```json
{
  "servers": {
    "npx-dynatrace-mcp-server": {
      "command": "npx",
      "args": ["-y", "@dynatrace-oss/dynatrace-mcp-server@latest"],
      "env": {
        "DT_ENVIRONMENT": "https://abc12345.apps.dynatrace.com"
      }
    }
  }
}
```

| Placeholder | Replace With | Example |
|-------------|--------------|---------|
| `DT_ENVIRONMENT` | Your Dynatrace environment URL | `https://abc12345.apps.dynatrace.com` |

> **Tip:** Your environment URL is the same base URL you used to access Dynatrace in your browser from the previous lab exercises (without any path after the domain).

### 1.3 Save and Reload

1. Save/Close the `mcp.json` file (auto-saved if in Codespaces VS Code)
2. Open the Command Palette (`Cmd+Shift+P` or `Ctrl+Shift+P`)
3. Type **"Developer: Reload Window"**
4. Press Enter

---

## Step 2: Verify MCP Connection

### 2.1 Open GitHub Copilot Chat

1. Click on the Copilot icon on the top bar
2. Or use keyboard shortcut: `Cmd+Shift+I` (Mac) / `Ctrl+Shift+I` (Windows)

### 2.2 Test the Connection

In the Copilot chat, type:

```
@dynatrace What services are available in my environment?
```

If configured correctly, Copilot will query Dynatrace and return a list of services!

---

## 🎭 Your Mission (Choose Your Persona)

From this point forward, you'll focus on different use cases depending on your role.

<div class="persona-box developer" markdown="1">

### 💻 Developer: "I want to debug without leaving my IDE"

**Your story:** You're deep in code, fixing a bug in your RAG pipeline. Every time you need performance data, you have to context-switch to Dynatrace. What if you could just *ask*?

**Your goal:** Set up MCP so you can query Dynatrace directly from VS Code. Debug while you code!

**Focus on:** Steps 3 and 4 (marked with 💻)

</div>

<div class="persona-box sre" markdown="1">

### 🔧 SRE/Platform: "I need faster incident response"

**Your story:** It's 2 AM and you get paged. Instead of fumbling through dashboards half-asleep, what if you could just ask about the issue?

**Your goal:** Learn to use MCP for rapid incident triage. Get answers in seconds, not minutes.

**Focus on:** Steps 5 and 6 (marked with 🔧)

</div>

---

<div class="persona-box developer" markdown="1">

## 💻 Step 3: Query Your AI Service (Developer)

Use MCP to analyze your instrumented AI service while coding.

### 3.1 Find Your Service

```
@dynatrace Tell me about the service called ai-chat-service-{YOUR_ATTENDEE_ID}
```

### 3.2 Analyze Token Usage

```
@dynatrace What is the total input and output token usage for spans in regards to the ai-chat-service-{YOUR_ATTENDEE_ID}
```

### 3.3 Debug While You Code

Use MCP alongside your code to understand your application's behavior:

```
I'm looking at main.py where I call Azure OpenAI.
@dynatrace What's the average latency for Azure OpenAI calls from my ai-chat-service-{YOUR_ATTENDEE_ID} service?
```

No context switching — debug while you code!

---

## 💻 Step 4: Agentic Debugging Workflows (Developer)

MCP enables powerful agentic workflows where AI assistants can take action based on observability data.

### 4.1 Find the Bottleneck

```
I'm seeing slow responses in my RAG pipeline. 
@dynatrace Analyze the trace data and tell me which step is the bottleneck for my ai-chat-service-{YOUR_ATTENDEE_ID} service.
Is it embeddings, vector search, or the LLM call?
```

### 4.2 Proactive Analysis

```
@dynatrace Analyze my ai-chat-service-{YOUR_ATTENDEE_ID} service and suggest optimizations to reduce token usage while maintaining response quality
```

### 4.3 Debugging Assistance

```
@dynatrace Help me understand why some of my RAG queries might be slow. Look at the trace data for patterns.
```

</div>

---

<div class="persona-box sre" markdown="1">

## 🔧 Step 5: Query Your AI Service (SRE)

Use MCP for quick incident triage without leaving your terminal.

### 5.1 Find Your Service

```
@dynatrace Tell me about the service called ai-chat-service-{YOUR_ATTENDEE_ID}
```

### 5.2 Check for Anomalies

```
@dynatrace Are there any anomalies in the last hour for ai-chat-service-{YOUR_ATTENDEE_ID}?
What's the current error rate and how does it compare to the baseline?
```

Get Davis AI insights without opening the Dynatrace UI!

### 5.3 Analyze Token Usage

```
@dynatrace What is the total input and output token usage for spans in regards to the ai-chat-service-{YOUR_ATTENDEE_ID}
```

---

## 🔧 Step 6: Agentic Incident Response (SRE)

MCP enables powerful agentic workflows for incident response directly from your IDE.

### 6.1 Incident Response

```
@dynatrace Are there any open problems affecting my ai-chat-service-{YOUR_ATTENDEE_ID} service?
If so, what's the root cause and which services are impacted?
Draft a Slack message summarizing the incident.
```

### 6.2 Service Architecture

```
@dynatrace Generate a summary of my ai-chat-service-{YOUR_ATTENDEE_ID} service's architecture based on the service flow data
```

### 6.3 Capacity Planning

```
@dynatrace Analyze my ai-chat-service-{YOUR_ATTENDEE_ID} service and suggest optimizations to reduce token usage while maintaining response quality
```

</div>

---

## Step 7: MCP Best Practices

### 7.1 Effective Prompting

**Good prompts are specific:**

✅ Good: `@dynatrace Show me the P95 response time for ai-chat-service-{YOUR_ATTENDEE_ID} over the last 4 hours`

❌ Vague: `@dynatrace How is my service doing?`

### 7.2 Iterative Queries

Start broad, then drill down:

1. `@dynatrace Show me an overview of my AI service`
2. `@dynatrace What are the slowest endpoints?`
3. `@dynatrace Why is /chat endpoint slow?`
4. `@dynatrace Show me slow traces for /chat`

### 7.3 Combining with Code

You can use MCP alongside your code:

```
I'm looking at main.py where I call Azure OpenAI. 
@dynatrace What's the average latency for Azure OpenAI calls from my service?
```

---

## ✅ Checkpoint

Before completing the workshop, verify:

- [ ] You've added your `DT_ENVIRONMENT` URL to `.vscode/mcp.json`
- [ ] You've reloaded VS Code after saving the configuration
- [ ] You can query Dynatrace using `@dynatrace` in Copilot Chat
- [ ] You've successfully retrieved information about your AI service
- [ ] You understand how to use MCP for problem analysis
- [ ] You've explored agentic workflow capabilities

---

## 🆘 Troubleshooting

### "MCP server not found"

1. Verify Node.js is installed: `node --version`
2. Ensure the `.vscode/mcp.json` file exists in your workspace
3. Test MCP server access: `npx @dynatrace-oss/dynatrace-mcp-server@latest --version`
4. Clear NPM cache if needed: `npm cache clean --force`

### "@dynatrace not recognized"

1. Check that `.vscode/mcp.json` contains the correct configuration
2. Verify the JSON syntax is valid (no trailing commas, proper quotes)
3. Reload VS Code window (`Developer: Reload Window`)
4. Make sure `DT_ENVIRONMENT` is set to your Dynatrace URL

### "Authentication failed" or "401 Unauthorized"

1. Verify `DT_ENVIRONMENT` in `.vscode/mcp.json` is correct
2. Ensure the URL format is `https://YOUR_ENV_ID.apps.dynatrace.com`
3. Check that your Dynatrace environment allows API access
4. Check that your token has appropriate permissions:
   - `Read entities`
   - `Read problems`
   - `Read metrics`
   - `Read logs`
   - `Read traces`

### "No data returned"

1. Verify `DT_ENVIRONMENT` in `.vscode/mcp.json` is correct
2. Check that your service is sending data to Dynatrace
3. Try a simpler query first: `@dynatrace List all services`

### "Connection refused" or "Network error"

1. If in a Codespace, ensure outbound connections are allowed
2. Check if your organization has firewall rules blocking the connection
3. Verify the URL format is `https://YOUR_ENV_ID.apps.dynatrace.com`

---

## 🎓 What You've Learned

<div class="persona-box developer" markdown="1">

### 💻 Developer Takeaways

You can now debug without leaving your IDE:

1. ✅ Configure Dynatrace MCP in VS Code
2. ✅ Query your service performance using natural language
3. ✅ Find bottlenecks in your RAG pipeline from the IDE
4. ✅ Get optimization suggestions while you code
5. ✅ Combine code context with observability data

**Your new workflow:** See a slow response? Just ask `@dynatrace` what's happening instead of context-switching to dashboards.

</div>

<div class="persona-box sre" markdown="1">

### 🔧 SRE/Platform Takeaways

You can now respond to incidents faster:

1. ✅ Configure Dynatrace MCP for terminal/IDE access
2. ✅ Check for anomalies and error rates instantly
3. ✅ Get Davis AI root cause analysis via natural language
4. ✅ Draft incident communications directly from MCP
5. ✅ Query service architecture and capacity data

**Your 2 AM incident response:** Ask `@dynatrace` for the root cause and draft a Slack message — all without opening a browser.

</div>

---

## 🚀 Next Steps

Now that you've completed this lab, continue to Lab 4 to learn how to automate your AI observability workflows!

---

## 🎉 Great Progress!

You've learned how to use Dynatrace MCP for agentic AI workflows. Now let's put it all together with automated workflows!

<div class="lab-nav">
  <a href="lab2-explore-traces">← Lab 2: Explore Traces</a>
  <a href="lab4-automation">Lab 4: Automation →</a>
</div>
