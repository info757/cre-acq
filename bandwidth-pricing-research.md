# AI Voice Agent Pricing Strategy: Market Research & Frameworks
*Compiled Feb 2026 | Will Holt*

---

## Opening Note

This document is a collection of market research and pricing frameworks compiled after our conversation. It is meant as a thinking tool, not a prescription. Bandwidth has far more context on its reseller network, cost structure, and customer behavior than any outside analysis can capture. My hope is that some of these frameworks might be useful as you finalize the GTM approach, or at minimum surface questions worth examining.

---

## 1. The Core Strategic Question: What Budget Does This Live In?

One of the more interesting questions for a product like this is where it lives in the buyer's mental model, and whose budget it gets approved from.

Traditional SaaS tends to be evaluated against the IT budget. Operations and headcount decisions live in a separate, typically much larger budget. An AI voice agent that handles inbound calls and books appointments sits somewhere at the boundary of both, and how it is framed at the point of sale may significantly influence both adoption and willingness to pay.

**A potential framing worth testing:**

> Software tends to be budgeted in IT. Labor tends to be budgeted in operations.

If resellers frame the AI as an operations decision, positioning it as a "digital worker" rather than a software feature, the relevant comparison shifts from software spend to labor spend. Whether that framing resonates with Bandwidth's specific reseller network and their SMB clients is an open empirical question, and one the anchor partner program could help answer.

**The scale of the opportunity:**
- US labor compensation: ~$15 trillion/year
- US SMB workforce: ~60 million employees
- US Virtual Receptionist Service market (2025): $5.26 billion, CAGR 9.8%

---

## 2. Infrastructure Cost Context

Understanding the competitive COGS landscape is useful context for thinking about where Bandwidth's pricing can realistically land and what margin structure is sustainable for the reseller channel.

**Estimated fully loaded costs at 10,000 minutes/month** (orchestration + STT + LLM + TTS + telephony):

| Platform | Monthly Cost | Effective $/min | Notes |
|---|---|---|---|
| **Retell AI** | ~$700 | ~$0.07 | Low latency (~600ms), bundled efficiencies |
| **Bland AI** | ~$900 to $1,200 | ~$0.09 to $0.12 | Strong outbound, ~800ms latency |
| **Air AI** | License-heavy | ~$0.11 | Pre-built agents, high upfront |
| **Vapi** | ~$1,400 to $1,600 | ~$0.14 to $0.16 | Highest dev flexibility, third-party API cost dependencies |

One observation worth noting: Bandwidth's carrier edge architecture, running AI on its own SIP infrastructure rather than public internet routing, represents a potential COGS and latency advantage relative to these infrastructure comparisons. Whether and how that translates into pricing power is a product and market question.

---

## 3. The Labor Value Context: What SMBs Currently Pay

To calibrate the pricing conversation, it is helpful to understand what SMBs are already paying for the human alternative, both in-house and through BPO services.

**In-house receptionist, Greensboro, NC (representative mid-market benchmark):**

| Component | Annual |
|---|---|
| Base salary (front office, mid-level) | $35,000 to $45,000 |
| Payroll taxes (FICA, FUTA, NC SUTA) | +$4,000 to $6,000 |
| Benefits (conservative 20 to 30%) | +$7,000 to $13,500 |
| **Fully loaded annual cost** | **$46,000 to $64,500** |
| **Fully loaded monthly cost** | **$3,833 to $5,375** |

Constraints: 40 hrs/week, single-call concurrency, sick leave, turnover, training.

**Premium live virtual receptionist services, what SMBs pay today:**

| Service | Base/mo | Overage | Coverage |
|---|---|---|---|
| Smith.ai | $285 to $300 | $8.50 to $11.50/call ($1.44 to $1.75/min) | Business hours |
| Ruby Receptionists | $219+ | $3.39 to $4.90/min | Business hours |
| AnswerConnect | $350 (200 min incl.) | Steep overage | 24/7 optional |

These services time-share human labor across clients. Their pricing reflects what SMBs are psychologically prepared to pay for answered calls, and suggests there may be significant runway above the developer-tier per-minute rates.

**The revenue leakage angle:**
- 72 to 80% of callers hang up without leaving a voicemail when calls go unanswered
- For high-value service businesses, a missed call can represent hundreds to thousands in lost revenue
- 24/7 AI coverage may capture revenue that currently leaks entirely, not just reduce cost

---

## 4. Retail Pricing Models Worth Considering

There are several distinct approaches the reseller channel could use to price this at the SMB level. Each has different implications for adoption, margin, and the buyer's psychology. I will outline four that seem relevant, with the caveat that Bandwidth's anchor partner data will likely reveal things no external analysis can predict.

### Model A: Consumption-Based (Per-Minute)

The most direct translation of infrastructure economics. Easy to implement, familiar to telecom resellers, and highly predictable for margin forecasting.

A potential tension worth examining: non-technical SMB buyers tend to struggle with usage-based billing for products where they do not intuitively understand the unit. Research from enterprise AI deployments suggests consumption pricing can suppress adoption as buyers self-limit usage to avoid billing surprises. Whether that dynamic holds for Bandwidth's specific reseller/SMB segment is worth testing.

### Model B: Digital Worker (Seat-Based)

Package the AI as a role rather than a usage metric. Instead of "AI Voice Minutes," the reseller sells a "24/7 Scheduling Coordinator" or "Inbound Triage Agent" at a flat monthly rate.

Potential advantages:
- Predictable monthly cost reduces buyer anxiety
- Framing as a "digital worker" may unlock headcount budgets
- Flat-rate model does not penalize longer, more successful conversations

Illustrative retail price ranges to potentially validate:

| Agent Role | Indicative Retail/mo | Included Minutes |
|---|---|---|
| Basic inbound triage | $197 | ~500 min |
| Scheduling + booking | $397 | ~800 min |
| CRM revival / lead reactivation | $697 to $997 | ~1,000 min |

These are starting hypotheses for validation, not recommendations.

### Model C: Workflow/Action-Based

Charge per successful task completion rather than time present. A nominal platform fee covers infrastructure, and micro-transactions trigger on defined outcomes (e.g., lead captured + CRM updated + SMS sent = $1.50 per completed workflow).

This model works well when the AI is visibly replacing specific administrative processes and the SMB can directly correlate cost to tasks completed. It requires more instrumentation to track reliably.

### Model D: Outcome-Based (Pay-Per-Performance)

Zero monthly retainer, with the SMB paying only when the AI delivers a measurable outcome, typically a booked appointment ($30 to $50) or qualified lead captured ($15 to $25).

This model removes perceived risk for the SMB buyer entirely and aligns vendor incentives with customer outcomes. Intercom has used a version of this ($0.99 per resolved support ticket) successfully in enterprise. The tradeoff is that the MSP absorbs variable compute costs against an uncertain conversion rate, which requires confidence in the AI's performance and a clear definition of what "outcome" means.

---

## 5. Wholesale Channel Considerations

A few structural questions that seem worth examining when designing the reseller pricing architecture:

**Reseller margin sustainability:** Telecom MSPs are accustomed to 50 to 75% margin on their core products. If the wholesale structure compresses margins significantly below that, the channel may be slow to prioritize selling it. Understanding what margin level motivates the specific reseller types in Bandwidth's network seems like a key input.

**Two-layer structure to consider:**
- A platform/access fee for the white-label environment and tooling (pure SaaS margin for Bandwidth)
- A separate wholesale compute component with a margin buffer between Bandwidth's COGS and the reseller's cost

This structure could allow Bandwidth to capture SaaS-style recurring revenue while giving MSPs flexibility to build their own retail packaging on top.

**Capability-tiered licensing:** An alternative to volume-based pricing is pricing on what the AI is permitted to do, for example basic FAQ routing, calendar booking, or full lead qualification. This approach may capture more value as the AI takes on higher-value tasks and creates a natural expansion path as SMBs see results.

---

## 6. Price Discovery Approaches

Given the novelty of the category, validated pricing data from real buyers will be more valuable than any external benchmark. A few methods that tend to surface useful signal:

**Van Westendorp:** Four questions to resellers and SMB pilots: at what price does this seem too cheap to trust? A bargain? Starting to feel expensive? Too expensive? The intersecting curves define the acceptable price range. Particularly useful when there is no established market comparable.

**Gabor-Granger:** Show a price, ask yes/no. Test a range across reseller cohorts. Builds a demand curve quickly.

**Jobs-to-Be-Done interviews:** Talk to resellers not about pricing but about what they are currently paying to solve the same problem. Understanding their existing margin structure and their SMB clients' current pain gives better pricing data than any survey.

**Founding Partner Program:** Offer an early cohort of 10 to 20 resellers a locked rate in exchange for deployment commitment, feedback calls, and case study rights. Creates real usage data, revenue momentum, and advocates before GA.

---

## 7. Reseller Discovery Questions

If the plan is to run structured interviews with anchor partners, these tend to surface the most useful signal:

1. *"Walk me through how your SMB clients currently handle inbound calls, and what are they paying today?"*
2. *"If a client's AI agent books 10 extra appointments this month, what's that worth to them?"*
3. *"What would you need to see to confidently bundle this with what you're already selling?"*
4. *"If I showed you this at $99/month wholesale, what would be your honest first reaction?"*
5. *"What's the one thing that would make this impossible to sell to your clients?"*

---

*Research compiled by Will Holt | Feb 2026*
