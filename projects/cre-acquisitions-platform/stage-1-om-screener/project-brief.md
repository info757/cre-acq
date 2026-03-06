# Project Brief — CRE OM Screener
**BMAD Phase 1: Analysis**
_Status: DRAFT — awaiting Will's review and approval before moving to PRD_

---

## What We're Building

An AI agent that reads Offering Memorandums (PDFs) and produces a structured
screening verdict — so acquisitions professionals stop reading 80-page marketing
documents to find out one number doesn't work.

The agent extracts key metrics from the OM itself (not listing metadata), scores
them against configurable buy criteria, flags red flags the site search would miss,
and delivers a go/no-go verdict with supporting evidence in under 2 minutes.

---

## The Problem

CRE acquisitions professionals receive OMs from brokers, listing platforms, and
direct sources constantly. The site search (Crexi, LoopNet) filters against
broker-entered metadata — not OM content. The OM contains what the deal actually
is: actual NOI vs. pro-forma, real expense ratios, debt terms, lease expirations,
physical condition signals. All of that requires a human to open and read the PDF.

At volume (20–50 OMs/month), this is hours of work spent mostly eliminating
deals that should have been obvious nos.

---

## Why This Is Better Than Site Search

| Site Search | OM Screener |
|---|---|
| Filters on broker-entered metadata | Reads the actual OM content |
| Misses pro-forma vs. actual NOI gap | Catches the gap explicitly |
| Can't detect lease expiration concentration | Flags lease roll risk |
| Fixed platform filter schema | Fully configurable criteria |
| No red flag detection | Flags deferred maintenance signals, thin DSCR, etc. |

---

## Primary User

**CRE acquisitions professional** — anyone actively reviewing deal flow:
individual investors, small acquisitions teams, fund analysts. Not limited to
a single property type or market. Criteria must be fully reconfigurable on the
fly (multifamily one day, industrial the next).

Will Holt is also a direct user — this gets filmed as the demo.

---

## Knowledge Architecture (3 Layers)

**Layer 1 — Base CRE Knowledge (built in)**
Public-domain underwriting fundamentals: DSCR benchmarks, cap rate analysis,
occupancy standards, expense ratio norms, debt coverage logic, market tier
classifications. No IP issues. Grounds scoring in CRE-specific logic vs.
generic LLM reasoning.

**Layer 2 — Configurable Criteria (per session)**
User-defined schema that mirrors CRE listing platform filters but applied to
OM content: property type, market, price range, cap rate floor, occupancy
minimum, max LTV, DSCR threshold, vintage range, and any custom rules.
Changeable without touching code.

**Layer 3 — Client Historical Data (per engagement)**
When deployed for a paying client: their historical deal flow ingested and
used to calibrate scoring. The agent learns how that specific team thinks.
The longer they use it, the better it gets. This is the retainer story.

---

## MVP Scope (Demo-Ready)

- Single PDF input (drop or path)
- Property types: multifamily and industrial (most requested asset classes)
- Extracts: NOI, cap rate, occupancy, asking price, price/unit, debt terms
  (LTV/DSCR/rate/maturity), vintage, market, expense ratio, key lease info
- Scores against configurable criteria (JSON or simple form input)
- Flags: pro-forma vs. trailing NOI gap, thin DSCR, lease roll concentration,
  occupancy below threshold, expense ratio outliers
- Output: structured verdict (go / conditional / no-go) + extracted metrics
  table + red flags list + one-paragraph narrative summary
- Delivery: Telegram message + structured JSON file written to disk
- Human review gate: extracted metrics displayed before scoring fires

---

## What the Output Looks Like

```
VERDICT: CONDITIONAL ⚠️

Property: 142-Unit Multifamily | Charlotte, NC | Asking $18.2M
Cap Rate: 4.8% (listed 5.5% — pro-forma gap detected)
NOI: $873K trailing / $1.1M pro-forma (26% spread — FLAG)
Occupancy: 91% (threshold: 88% — PASS)
DSCR: 1.18 at 6.5% / 75% LTV (threshold: 1.20 — FAIL, marginal)
Expense Ratio: 48% (market norm ~42% — FLAG, investigate)
Lease Roll: No major concentration detected — PASS
Vintage: 1987 (value-add range — PASS)

RED FLAGS (2):
• Pro-forma NOI 26% above trailing — underwriting assumes unproven rent bumps
• Expense ratio 6 points above market norm — could mask deferred maintenance

NARRATIVE:
Deal could work at a lower basis. Pro-forma assumptions are aggressive and
expense ratio warrants a full inspection before going to LOI. At asking price,
DSCR is too thin for most lenders at current rates. Recommend counter or pass.
```

---

## Distribution Strategy

This is built to be filmed. Every output is a LinkedIn post waiting to happen:
"I dropped an OM into the agent. Here's what it found in 90 seconds."
The demo IS the marketing. The first paying client comes from inbound, not outreach.

---

## Risks

| Risk | Mitigation |
|---|---|
| LLM hallucinates a metric | Human review gate after extraction, before scoring |
| OM is scanned image (no text layer) | OCR pre-processing step (Tesseract or similar) |
| Broker OM format is non-standard | Test on 5+ real OMs before shipping |
| Criteria schema too rigid | JSON config — user-editable without code changes |
| IP concern (course materials) | Not in MVP — using public knowledge only |

---

## Success Criteria (MVP)

- Extracts correct metrics from a clean PDF OM with >90% accuracy
- Scoring fires correctly against configurable criteria
- Human review gate works before scoring
- Output is clear enough that a non-technical CRE professional understands it
- Demo filmed and posted to LinkedIn within 2 weeks of build complete

---

## Out of Scope (MVP)

- Crexi/LoopNet scraping (Stage 1 — separate build)
- Client historical data ingestion (Layer 3 — post-MVP)
- Web UI (Telegram delivery is sufficient for demo)
- Full RAG knowledge base (prompt-stuffing for MVP, RAG later)
- Automated email ingestion of broker OMs (later)

---

_Next step: Will reviews and approves this brief, then we move to PRD (user stories + acceptance criteria)._
_Zoé — 2026-03-04_
