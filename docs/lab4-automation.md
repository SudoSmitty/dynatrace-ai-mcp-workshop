---
layout: default
title: Lab 4 - Workflow Automation
nav_order: 6
---

# ⚡ Lab 4: Workflow Automation - Become the AI Cost Guardian

**Duration:** ~30 minutes

In this lab, you'll create automated workflows that transform you from someone who *monitors* AI costs to someone who *controls* them. This is your "hero moment" — building automation you can take back to your team.

---

## 🎯 Learning Objectives

- Create a Dynatrace Workflow for AI observability
- Set up automated token usage monitoring
- Configure alerts that matter (not noise)
- Build a daily AI cost summary automation
- Understand the Dynatrace automation advantage

---

<div class="why-dynatrace">

## 🏆 Why Dynatrace? The Automation Advantage

| Capability | Other Tools | Dynatrace |
|------------|-------------|-----------|
| Trace collection | ✅ Manual thresholds | ✅ Davis AI anomaly detection |
| Alert configuration | ❌ You define every threshold | ✅ Auto-baselines, smart alerts |
| Root cause | ❌ You investigate | ✅ Davis AI automatic RCA |
| Remediation | ❌ External tools (PagerDuty, etc.) | ✅ Built-in Workflows + integrations |
| Context | Token counts only | ✅ Tokens + infrastructure + user impact |

**The difference:** Other tools tell you *something is wrong*. Dynatrace tells you *what's wrong, why, and can fix it automatically*.

</div>

---

## Step 1: Navigate to Workflows

### 1.1 Access the Workflows App

1. In Dynatrace, click on the **Workflows** app in the left navigation (or search for it)
2. Click **+ Workflow** to create a new workflow

### 1.2 Name Your Workflow

Name it: `AI Cost Guardian - {YOUR_ATTENDEE_ID}`

---

## Step 2: Create a Token Usage Alert Workflow

This workflow will alert you when token usage exceeds a threshold — perfect for catching runaway AI costs.

### 2.1 Set the Trigger

1. Click on the trigger block (the starting point)
2. Select **Schedule trigger**:
   - Set to run every **15 minutes** for testing

### 2.2 Add a DQL Query Action

1. Click **+ Add action**
2. Select **Run DQL query**
3. Enter this query:

```sql
fetch spans
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| filter isNotNull(gen_ai.usage.input_tokens)
| summarize 
    total_input_tokens = sum(gen_ai.usage.input_tokens),
    total_output_tokens = sum(gen_ai.usage.output_tokens),
    request_count = count()
| fieldsAdd total_tokens = total_input_tokens + total_output_tokens
| fieldsAdd estimated_cost_usd = (total_input_tokens * 2.50 + total_output_tokens * 10.00) / 1000000
```

4. Name this action: `Get Token Usage`

### 2.3 Add a Condition

1. Click **+ Add action** 
2. Select **Condition**
3. Set the condition:
   ```
   result.records[0].total_tokens > 10000
   ```
   (Adjust threshold based on your expected usage)

### 2.4 Add a Notification Action

1. In the **True** branch, click **+ Add action**
2. Select **Send notification** (Slack, Teams, Email, etc.)
3. Configure your message:

```
🚨 AI Token Alert - {YOUR_ATTENDEE_ID}

Token usage exceeded threshold!

📊 Stats:
• Total Tokens: {{ result.records[0].total_tokens }}
• Input Tokens: {{ result.records[0].total_input_tokens }}
• Output Tokens: {{ result.records[0].total_output_tokens }}
• Estimated Cost: ${{ result.records[0].estimated_cost_usd | round(4) }}
• Request Count: {{ result.records[0].request_count }}

```

### 2.5 Save and Activate

1. Click **Save**
2. Toggle the workflow to **Enabled**

---

## Step 3: Daily AI Cost Summary Workflow

Create a workflow that sends you a daily summary — no more surprise bills!

### 3.1 Create a New Workflow

1. Click **+ Workflow**
2. Name it: `Daily AI Summary - {YOUR_ATTENDEE_ID}`

### 3.2 Set Schedule Trigger

1. Select **Schedule trigger**
2. Configure: **Daily at 9:00 AM** (or your preferred time)

### 3.3 Add Comprehensive DQL Query

Add a **Run DQL query** action with:

```sql
fetch spans
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| filter isNotNull(gen_ai.usage.input_tokens)
| summarize 
    total_input = sum(gen_ai.usage.input_tokens),
    total_output = sum(gen_ai.usage.output_tokens),
    avg_input = avg(gen_ai.usage.input_tokens),
    avg_output = avg(gen_ai.usage.output_tokens),
    max_input = max(gen_ai.usage.input_tokens),
    request_count = count(),
  by: {span.name}
| sort total_input + total_output desc
| limit 10
```

### 3.4 Add Summary Query

Add another **Run DQL query** action:

```sql
fetch spans
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| filter isNotNull(gen_ai.usage.input_tokens)
| summarize 
    total_input = sum(gen_ai.usage.input_tokens),
    total_output = sum(gen_ai.usage.output_tokens),
    total_requests = count(),
    avg_latency_ms = avg(duration) / 1000000
| fieldsAdd estimated_daily_cost = (total_input * 2.50 + total_output * 10.00) / 1000000
| fieldsAdd projected_monthly_cost = estimated_daily_cost * 30
```

### 3.5 Send Daily Report

Add a notification action with a formatted report:

```
📊 Daily AI Service Report - {YOUR_ATTENDEE_ID}

═══════════════════════════════════════
💰 COST SUMMARY
═══════════════════════════════════════
• Today's Estimated Cost: ${{ summary.estimated_daily_cost | round(4) }}
• Projected Monthly Cost: ${{ summary.projected_monthly_cost | round(2) }}

═══════════════════════════════════════
📈 USAGE METRICS
═══════════════════════════════════════
• Total Requests: {{ summary.total_requests }}
• Total Input Tokens: {{ summary.total_input | round(0) }}
• Total Output Tokens: {{ summary.total_output | round(0) }}
• Avg Response Time: {{ summary.avg_latency_ms | round(2) }}ms

═══════════════════════════════════════
🔝 TOP TOKEN CONSUMERS
═══════════════════════════════════════
{% for op in operations %}
• {{ op.span_name }}: {{ op.total_input + op.total_output }} tokens
{% endfor %}

```

---

## Step 4: Anomaly-Based Alert (Davis AI)

<div class="persona-box sre">

### 🔧 SRE/Platform View

Instead of setting static thresholds, let Davis AI learn what's "normal" for your service and alert on anomalies. This eliminates alert fatigue and catches issues you didn't anticipate.

</div>

### 4.1 Create Davis-Powered Workflow

1. Create a new workflow: `AI Anomaly Response - {YOUR_ATTENDEE_ID}`
2. Set trigger: **Davis problem**
3. Filter for your service:
   - Problem category: `Slowdown` or `Error`
   - Affected entity: `ai-chat-service-{YOUR_ATTENDEE_ID}`

### 4.2 Add Diagnostic Query

When a problem occurs, automatically gather context:

```sql
fetch spans
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| filter timestamp >= now() - 30m
| summarize 
    avg_duration_ms = avg(duration) / 1000000,
    error_count = countIf(otel.status_code == "ERROR"),
    total_count = count(),
    p95_duration_ms = percentile(duration, 95) / 1000000,
  by: {span.name}
| sort avg_duration_ms desc
```

### 4.3 Enrich Problem with AI Context

Add the diagnostic results to the problem ticket for faster resolution.

---

## 🔬 Additional Hands-On Exercises (Time Permitting)

### Exercise 1: Prompt Length Alert

Create a workflow that alerts when average prompt length exceeds a threshold (indicating potential prompt injection or abuse):

```sql
fetch spans
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| filter isNotNull(gen_ai.usage.input_tokens)
| summarize avg_input = avg(gen_ai.usage.input_tokens)
| filter avg_input > 2000
```

### Exercise 2: Cache Efficiency Monitor

<div class="persona-box developer">

### 💻 Developer View

Monitor your prompt caching effectiveness. Low cache rates mean you're paying more than necessary!

</div>

```sql
fetch spans
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| filter isNotNull(gen_ai.usage.cache_read_input_tokens)
| summarize 
    cached = sum(gen_ai.usage.cache_read_input_tokens),
    total = sum(gen_ai.usage.input_tokens)
| fieldsAdd cache_rate = (cached / total) * 100
| filter cache_rate < 30
```

### Exercise 3: Error Rate Automation

Create a workflow that automatically creates an incident ticket when LLM error rate exceeds 5%.

---

## ✅ Checkpoint

Before completing this lab, verify:

- [ ] Created a token usage alert workflow
- [ ] Set up a daily summary workflow
- [ ] Tested workflow execution
- [ ] Understood how Davis AI can trigger workflows
- [ ] Know how to add conditions and notifications

---

## 🆘 Troubleshooting

### "Workflow not triggering"

1. Verify the workflow is set to **Enabled**
2. Check that your service is generating data
3. For scheduled triggers, wait for the next scheduled run
4. Use **Run** to test manually

### "DQL query returns no data"

1. Verify your service name matches exactly
2. Check the time range in your query
3. Ensure your application has processed requests recently

### "Notification not received"

1. Verify the notification channel configuration
2. Check for authentication/permission issues
3. Test the notification channel independently

---

## 🎓 What You've Learned

Congratulations! You've created automated workflows that:

1. ✅ Monitor AI token usage automatically
2. ✅ Send daily cost summaries
3. ✅ Alert on anomalies detected by Davis AI
4. ✅ Provide actionable context for troubleshooting

**You're now the AI Cost Guardian for your team!** 🦸

---

## 🚀 Take It Further

Ideas for production workflows:

| Workflow | Trigger | Action |
|----------|---------|--------|
| **Cost Circuit Breaker** | Token rate > limit | Disable endpoint temporarily |
| **Model Fallback** | GPT-4 latency spike | Switch to GPT-4o-mini |
| **Weekly Executive Report** | Schedule (Monday 8am) | Email summary to leadership |
| **Prompt Injection Alert** | Unusual input patterns | Security team notification |
| **SLA Violation** | P95 latency > 5s | Create incident + page on-call |

---

## 🎉 Lab Complete!

You've built automation that will save your team time and money. These workflows demonstrate the Dynatrace difference — not just observability, but **actionable automation**.

<div class="lab-nav">
  <a href="lab3-dynatrace-mcp">← Lab 3: Dynatrace MCP</a>
  <a href="resources">View Resources →</a>
</div>
