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

<div class="why-dynatrace" markdown="1">

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

---

## 🎭 Choose Your Persona

From here, focus on the workflows most relevant to your role. Complete at least one workflow.

<div class="persona-box developer" markdown="1">

### 💻 Developer Path

**Your goal:** Create workflows that alert you before users complain. Sleep better knowing automation has your back.

**Must-do:** Step 2 (Token Usage Alert)

</div>

<div class="persona-box sre" markdown="1">

### 🔧 SRE/Platform Path

**Your goal:** Build the automation that makes you the AI Cost Guardian. This is your "hero moment"!

**Must-do:** Step 3 (Daily Summary)

</div>

---

<div class="persona-box developer" markdown="1">

## 💻 Step 2: Create a Token Usage Alert Workflow

This workflow will alert you when token usage exceeds a threshold — perfect for catching runaway AI costs.

### 2.1 Create a New Workflow

1. Click **+ Workflow**
2. Name it: `Token Usage Alert - {YOUR_ATTENDEE_ID}`

### 2.2 Set the Trigger

1. Click on the trigger block (the starting point)
2. Select **Time Interval trigger**:
   - Set to run every **15 minutes** for testing

### 2.3 Add a DQL Query Action

1. Click **+ Add task**
2. Select **Execute DQL query**
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

4. Name this task: `get_token_usage`

### 2.4 Add a Notification Action

1. Add an **Email** -> **Send email** task
3. Configure your message:

{% raw %}
```
🚨 AI Token Alert - sudosmitty

Token usage exceeded threshold!

📊 Stats:
• Total Tokens: {{ result("get_token_usage").records[0].total_tokens }}
• Input Tokens: {{ result("get_token_usage").records[0].total_input_tokens }}
• Output Tokens: {{ result("get_token_usage").records[0].total_output_tokens }}
• Estimated Cost: ${{ result("get_token_usage").records[0].estimated_cost_usd | round(4) }}
• Request Count: {{ result("get_token_usage").records[0].request_count }}

```
{% endraw %}

### 2.4 Add a Condition

1. Select **Condition**
2. Set the condition:
{% raw %}
   ```
   {{ result("get_token_usage").records[0].total_tokens > 1000 }}
   ```
{% endraw %}
   (Adjust threshold based on your expected usage)

### 2.6 Save and Deploy

1. Click **Deploy**
2. Click **Save and Deploy** on the pop-up
2. Click **Run**

</div>

---

<div class="persona-box sre" markdown="1">

## 🔧 Step 3: Daily AI Cost Summary Workflow

Create a workflow that sends you a daily summary — no more surprise bills!

### 3.1 Create a New Workflow

1. Click **+ Workflow**
2. Name it: `Daily AI Summary - {YOUR_ATTENDEE_ID}`

### 3.2 Set Schedule Trigger

1. Select **Fix Time trigger**
2. Configure: **Daily at 9:00 AM** (or your preferred time)

### 3.3 Add Comprehensive DQL Query

Add a **Execute DQL query** task named `usage` with:

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

Add another **Execute DQL query** task named `cost` with:

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

1. Add an **Email** -> **Send email** task
3. Configure your message:

{% raw %}
```
📊 Daily AI Service Report - {YOUR_ATTENDEE_ID}

═══════════════════════════════════════
💰 COST SUMMARY
═══════════════════════════════════════
• Today's Estimated Cost: ${{ result("cost").records[0].estimated_daily_cost | round(4) }}
• Projected Monthly Cost: ${{ result("cost").records[0].projected_monthly_cost | round(2) }}

═══════════════════════════════════════
📈 USAGE METRICS
═══════════════════════════════════════
• Total Requests: {{ result("usage").records | map(attribute="request_count") | map("int") | sum }}
• Total Input Tokens: {{ result("usage").records | map(attribute="total_input") | map("int") | sum }}
• Total Output Tokens: {{ result("usage").records | map(attribute="total_output") | map("int") | sum }}
• Avg Response Time: {{ result("cost").records[0].avg_latency_ms }}ms

```
{% endraw %}
</div>

---

## ✅ Checkpoint

Before completing this lab, verify:

- [ ] Created a workflow
- [ ] Set up notification
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

<div class="persona-box developer" markdown="1">

### 💻 Developer Takeaways

You've built automation that watches your AI service:

1. ✅ Create scheduled workflows that run DQL queries
2. ✅ Set up token usage alerts with thresholds
3. ✅ Configure notifications (Slack, Teams, Email)
4. ✅ Add conditions to avoid alert noise

**Sleep better:** Your workflow will alert you if token usage spikes — before users complain or the bill arrives.

</div>

<div class="persona-box sre" markdown="1">

### 🔧 SRE/Platform Takeaways

You're now the AI Cost Guardian:

1. ✅ Build daily cost summary workflows
2. ✅ Calculate projected monthly costs automatically
3. ✅ Identify top token consumers by operation
4. ✅ Trigger workflows from Davis AI problems

**Take back to your team:** These workflows are production-ready. Customize the thresholds and notification channels for your environment.

</div>

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
