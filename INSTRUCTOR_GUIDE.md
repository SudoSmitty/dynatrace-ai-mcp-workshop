# Dynatrace AI Observability Workshop - Instructor Guide

This document provides guidance for instructors running the workshop.

## Pre-Workshop Checklist

### 1 Week Before

- [ ] Verify Dynatrace playground tenant access
- [ ] Create API token with required permissions
- [ ] Verify Azure OpenAI resource is provisioned and accessible
- [ ] Configure GitHub Secrets for the repository (AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY)
- [ ] Test Codespace creation end-to-end
- [ ] Prepare attendee credential sharing document

> **Important:** Attendees share the same repository—they don't fork it. Each attendee launches their own isolated Codespace environment where all code modifications stay private to their session.

### Day Before

- [ ] Verify Dynatrace tenant is accessible
- [ ] Test API token is working
- [ ] Verify Azure OpenAI deployments are responding (test endpoint + API key)
- [ ] Prepare backup credentials if needed
- [ ] Send reminder to attendees with GitHub account requirements

### Day Of

- [ ] Verify all systems operational
- [ ] Have backup plans ready
- [ ] Prepare screen sharing for demos
- [ ] Have troubleshooting guide handy

---

## Credential Distribution

Create a simple slide or document to share with attendees:

```
╔═══════════════════════════════════════════════════════════════╗
║          Dynatrace AI Workshop - Credentials                  ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  DT_ENDPOINT:                                                 ║
║  https://abc12345.live.dynatrace.com/api/v2/otlp             ║
║                                                               ║
║  DT_API_TOKEN:                                                ║
║  dt0c01.XXXXXXXXXX.YYYYYYYYYYYYYYYYYYYYYYYYYYYY              ║
║                                                               ║
║  Dynatrace UI:                                                ║
║  https://abc12345.live.dynatrace.com                          ║
║  Username: workshop@example.com                               ║
║  Password: [provided verbally]                                ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## Timing Guide

| Time | Activity | Notes |
|------|----------|-------|
| 0:00-0:15 | Introduction & Lab 0 | Welcome, objectives, environment setup |
| 0:15-0:45 | Lab 1 | Instrumentation - most hands-on coding |
| 0:45-1:30 | Lab 2 | Dynatrace exploration - lots of screen sharing |
| 1:30-2:15 | Lab 3 | MCP - interactive, exploratory |
| 2:15-2:30 | Wrap-up | Q&A, resources, feedback |

---

## Common Issues & Solutions

### Codespace Won't Start

**Symptom:** Codespace creation hangs or fails
**Solution:** 
1. Check GitHub status page
2. Try a different browser
3. Have attendee create from repo page directly

### Azure OpenAI Errors

**Symptom:** "API key invalid", "Resource not found", or rate limiting
**Solution:**
1. Verify AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY secrets are set correctly
2. Check Azure OpenAI resource quotas in Azure Portal
3. Verify deployment names match (gpt-4o-mini, text-embedding-ada-002)
4. Have backup credentials ready

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
