# AI-Augmented Fast Track: A Proposal for CRE Analyst

**Prepared by:** Will Holt
**Date:** March 2026

---

## Executive Summary

Fast Track already delivers the most rigorous CRE fundamentals training available. This proposal adds one thing: an AI layer that eliminates manual grunt work so students spend more time thinking like investors and less time fighting Excel.

The goal is not to replace the curriculum. It is to future-proof it.

CRE professionals who cannot use AI to accelerate financial analysis, document review, and model building will be at a structural disadvantage within 2-3 years. Fast Track is uniquely positioned to address that gap — before anyone else does.

This module introduces AI workflows as a parallel track woven into each of the 8 Fast Track phases. Students learn the same fundamentals they always have, and they also learn how to work 10x faster using tools that are already reshaping how deals get done.

---

## The Problem

Fast Track teaches students to build Excel models, read deal documents, and think through capital structures. That will always matter.

But today, a significant portion of the work required to get to insight is still manual:

- Extracting financial data from OMs, rent rolls, and loan term sheets
- Populating pro forma templates line by line
- Building comparison tables from scratch
- Abstracting leases by hand
- Writing market memos from raw data

These tasks are not where analysis happens. They are the work that precedes analysis. AI can automate most of them — accurately, auditably, and fast.

The professionals entering CRE today are competing against peers who are already using AI to do in 10 minutes what used to take 3 hours. Fast Track students deserve to know how.

---

## The Solution: An AI Layer Across All 8 Phases

Each Fast Track phase gets a 30–60 minute AI workflow session that maps directly to the skills students are already learning. The sessions are hands-on. Students replicate every workflow themselves.

The AI does not replace the model. It builds the inputs for the model — extracted from real documents, validated for accuracy, and reviewed by the student before anything hits a cell.

---

## The Three Superpowers

### Superpower 1: Document → Model

**What it does:**
Upload a deal document — an OM, rent roll, loan term sheet, or lease — and AI extracts the key financial data and auto-populates the relevant fields in the Excel model.

**Why it matters:**
This is the most time-consuming step in most analysts' workflows. It is also the most error-prone. Manual transcription introduces mistakes. AI extraction with validation catches them.

**Example:**
Student uploads a 40-page OM. Within seconds, the system has extracted NOI, in-place cap rate, occupancy, rent/SF, lease expirations, and loan terms — and flagged two figures it could not confirm with high confidence for human review. Student approves. Excel model populates.

---

### Superpower 2: Text → Model

**What it does:**
Student types deal assumptions in plain language. AI interprets them and builds the pro forma structure in Excel.

**Why it matters:**
This teaches students to think in assumptions first — which is the right instinct — before they ever open a spreadsheet. It also dramatically accelerates scenario analysis.

**Example:**
"200-unit multifamily, average 950 SF, $2.50/SF monthly rent, 5% vacancy, 65% LTV, 6.5% interest rate, 5.5% exit cap, 5-year hold."
AI builds the pro forma. Student reviews, adjusts, refines.

---

### Superpower 3: Voice → Model

**What it does:**
Student dictates deal assumptions out loud. Speech-to-text transcribes it. AI structures the output. Excel gets built.

**Why it matters:**
This is the future of field work. Walking a property, touring a market, sitting in a meeting — the ability to capture assumptions in real time and convert them directly to a working model is a genuine competitive edge.

**Example:**
Analyst records a 90-second voice memo after a site tour. By the time they get back to the office, a draft pro forma is waiting.

---

## Module-by-Module Breakdown

### Phase 1: Valuation
**AI Workflow:** Deal document extraction → DCF model population
Students upload an OM or broker package. AI extracts NOI, cap rate, rent roll summary, lease term data, and operating expense assumptions. Validated output populates the valuation model inputs.

---

### Phase 2: Debt and Leverage
**AI Workflow:** Natural language → loan comparison table
Students describe a deal and financing scenario in plain text. AI generates a structured loan comparison table across multiple scenarios (different LTVs, rates, amortization schedules) in Excel.

---

### Phase 3: Development
**AI Workflow:** Voice or text → development pro forma
Students dictate or type a development scenario — unit count, avg SF, rent assumptions, construction cost, stabilized cap rate. AI builds a development pro forma including construction budget, equity/debt stack, and stabilized yield.

---

### Phase 4: Joint Ventures
**AI Workflow:** JV agreement → waterfall explanation + model mapping
Students upload a JV agreement excerpt. AI identifies the waterfall structure, explains each tier in plain language, and maps the promote logic to the appropriate cells in a waterfall model.

---

### Phase 5: Capital Markets
**AI Workflow:** Market data → investment memo draft
Students provide a set of comp transactions or market data points. AI synthesizes them into a structured market summary memo — supply/demand dynamics, cap rate trends, buyer profiles — that can anchor a client presentation.

---

### Phase 6: CRE System
**AI Workflow:** Natural language → deal tracking dashboard
Students describe what they want to track (deal name, asset type, stage, NOI, yield, contact). AI generates the Excel or Notion database structure and writes the formulas. Students learn to use AI as a formula engine, not just an analysis tool.

---

### Phase 7: Sales and Due Diligence
**AI Workflow:** Due diligence documents → checklist population + issue flagging
Students upload a set of due diligence documents. AI reviews them against a standard DD checklist, marks completed items, summarizes key findings, and flags items that require further attention or are missing entirely.

---

### Phase 8: Leasing
**AI Workflow:** Lease document → abstraction table
Students upload a lease. AI extracts base rent, escalations, TI allowance, lease term, options, co-tenancy clauses, and exclusivity provisions — and populates a standard lease abstraction template. Multiple leases can be compared side by side.

---

## Architecture: Why This Is Compliant and Accurate

This is the section that matters for any firm evaluating whether to trust AI-assisted workflows in a professional environment.

### The Core Principle

AI is one step in a deterministic pipeline — not the final word. Accuracy is enforced at the system level, not hoped for at the prompt level.

### The Pipeline

```
Deal Document (PDF / email attachment)
        ↓
[Step 1: Document Parser]       — extracts raw text, preserves structure
        ↓
[Step 2: AI Extraction]         — structured JSON output only, no free-form text
                                  temperature = 0, source citation required
        ↓
[Step 3: Validation Layer]      — math checks, range checks, anomaly flagging
                                  non-AI logic: does NOI ÷ Cap Rate = Value?
        ↓
[Step 4: Human Review]          — student or analyst approves extracted data
                                  nothing hits the model without confirmation
        ↓
[Step 5: Model Population]      — validated data writes to Excel
        ↓
[Step 6: Audit Log]             — source doc, timestamp, extracted values, approver
```

### Why Each Step Matters

**Structured output enforcement:** The AI is instructed to return only a predefined JSON schema. There is no narrative, no approximation, no rounding without flagging. This eliminates hallucinated numbers.

**Source citation requirement:** The AI must quote the exact text from the source document where it found each figure. If it cannot find a citation, it flags the field as unconfirmed. Auditors can verify every extracted value back to its source.

**Validation layer:** Before anything reaches the analyst, automated logic checks that the numbers are internally consistent and within expected ranges for the asset class. Outliers are flagged, not silently passed through.

**Human checkpoint:** The analyst reviews and approves extracted data before it populates any model. AI surfaces the data; the human owns the decision to use it.

**Audit log:** Every extraction is logged. This is the compliance requirement most AI tools fail to address. Every workflow here leaves a full paper trail.

### Data Security

The workflow is designed so that sensitive deal data stays in a controlled environment:

- **Self-hosted n8n** — the orchestration layer runs on infrastructure the firm controls. Data does not flow through third-party automation platforms.
- **Document data stays internal** — the pipeline can be configured so document text never leaves the firm's environment. If cloud AI models are used, documents can be anonymized before submission.
- **Local model option** — for firms with strict data policies, the AI extraction step can run on a locally hosted model (Llama, Mistral via Ollama) with zero external API calls.

---

## Tool Stack

### For Students (No Coding Required)

| Tool | Role | Cost |
|---|---|---|
| n8n | Workflow orchestration — the pipeline | Free (self-hosted) |
| Claude or ChatGPT | AI extraction and generation | ~$20/month |
| Whisper | Speech-to-text for voice workflows | Free (local) |
| Excel / Google Sheets | Output target | Existing |

### For Students Who Want to Go Deeper

- **Python + openpyxl / xlwings** — programmatic Excel control
- **LlamaIndex / LangChain** — advanced document parsing and RAG workflows
- **Ollama** — run local AI models with zero API costs and full data privacy

### Why n8n Over Alternatives

- **vs. Zapier:** n8n is more powerful, more flexible for AI workflows, and self-hostable. Zapier costs more and keeps your data in their cloud.
- **vs. Make:** Similar capabilities, but n8n has better AI node support and is open source.
- **vs. Python scripts:** More accessible for non-developers, visual by design, easier to teach and debug in a classroom setting.

The key pedagogical advantage of n8n is that the workflow is *visible*. Students can see every step on a canvas — document in, AI extraction, validation, human review, Excel output. That transparency builds understanding and trust.

---

## Proposed Delivery Format

### Option A: AI Add-On (Recommended for Initial Rollout)
Each Fast Track session ends with a 30–45 minute AI workflow module that maps directly to the phase covered that week. Students replicate the workflow in real time. Total addition: ~4–6 hours across the 8-week cohort.

**Pros:** Minimal disruption to existing curriculum. AI reinforces what was just taught. Easier to pilot and refine.

### Option B: Standalone AI Track
A parallel 4-session AI cohort available to Fast Track graduates or as an add-on enrollment. Covers the 3 Superpowers in depth with hands-on build sessions.

**Pros:** Deeper coverage. Can be priced separately. Attracts working professionals who want AI skills without repeating the full Fast Track.

### Option C: Full Integration
AI workflows are embedded directly into each phase from day one. Excel and AI are taught side by side from the start.

**Pros:** Most cohesive experience. Best long-term positioning.

---

## Why This Works for CRE Analyst

- It deepens the value of a curriculum that is already best-in-class
- It creates a new revenue stream (AI module add-on or standalone track)
- It positions CRE Analyst as the first CRE training program to take AI seriously at the workflow level — not just mentioning it, but teaching it hands-on
- It gives graduates a skill set that is immediately deployable in their first job
- The compliance-first architecture addresses the objection that kills most AI proposals in institutional settings

---

## About Will Holt

Will is a Fast Track and Valuation alum who has spent the past several years at the intersection of commercial real estate and technology. He is currently building AI workflow systems for CRE applications — including document extraction pipelines, automated financial modeling, and voice-to-model tools of the type described in this proposal.

He is not pitching a concept. He is pitching what he has already built.

His background in CRE fundamentals combined with hands-on AI implementation experience makes him uniquely suited to bridge the gap between what the Fast Track curriculum teaches and where the industry is heading.

---

*This proposal is intended as a starting point for a conversation. The specific module design, delivery format, and tool choices can be adapted to fit CRE Analyst's curriculum structure, student base, and institutional requirements.*
