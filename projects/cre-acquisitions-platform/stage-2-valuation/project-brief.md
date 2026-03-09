# Project Brief — CRE Valuation Agent
**BMAD Phase 1: Analysis**
_Status: APPROVED for v1 — scope locked for LinkedIn demo_

---

## V1 Scope Lock (Non-Negotiable for This Build)

- **No lease-level commercial parity claim in v1.** We prove direct cap + DCF from structured inputs only. Lease-level complexity (TI, free rent, downtime, commissions, renewal probability) is explicitly out of scope and reserved for v2.
- **One hero deal.** Mill One or a sanitized broker valuation. One repeatable golden path.
- **One structured input path.** Stage 1 ScreeningResult + valuation overrides. No automated rent roll PDF parsing.
- **Direct cap + 10-year DCF only.** No leveraged DCF, no multi-scenario, no lease-by-lease modeling.
- **Publishable thesis:** Argus is overkill for a large share of CRE valuation work, even if it still matters for the hardest lease-level cases. We do not claim Argus replacement in v1.

---

## What We're Building

An AI agent that takes structured property inputs — rent roll, expense data,
market comps, cap rates — and produces a complete property valuation: estimated
value, direct capitalization, a full DCF model, IRR, and equity multiple. The
work a CRE professional currently does across Excel, ARGUS, and their own
judgment, done in under 3 minutes, with a human review gate before the numbers
finalize.

This is not a replacement for CRE expertise. It is what a senior analyst with
25 years of experience would produce if they could run every calculation
simultaneously, surface every assumption, and explain every output in plain
English — every time, instantly.

---

## The Problem

Commercial real estate valuation is manual by default. Every deal requires an
analyst to build a rent roll in Excel, layer in expenses, model rent growth and
vacancy, discount cash flows, and triangulate with market comps. It's repetitive,
error-prone, and slow.

ARGUS is the industry standard for DCF modeling — and it costs $5,000–$10,000
per license per year. For smaller shops, independent investors, and brokers who
need quick valuations for pricing guidance, that's inaccessible. For larger
firms, it's still a bottleneck: ARGUS requires training, licenses, and a full
build process for every deal.

The result: valuation quality is directly correlated to the time and money a
team can throw at it. Deals get passed because the model wasn't worth building.
Deals get done at the wrong basis because the model was thin.

---

## Why This Is Better Than Excel + ARGUS

| Excel + ARGUS | CRE Valuation Agent |
|---|---|
| $5K–$10K/yr ARGUS license | No per-seat cost |
| Hours to build a full DCF | Full model in under 3 minutes |
| Manual comp lookups | Comp inputs structured and scored automatically |
| No plain-English narrative | Every assumption and output explained |
| No built-in sanity checks | Flags inputs that deviate from market norms |
| Static model — assumptions hidden | Assumptions explicit and reviewable before output |
| Requires ARGUS training | Structured inputs, no software training required |
| No human review gate | Human confirms inputs before final output fires |

---

## Primary User

**CRE professional doing property valuation** — brokers pricing a listing,
investors underwriting an acquisition, lenders sizing a loan, advisors
preparing a client report. Not limited to asset class or market.

Will Holt is the primary user and demo subject — 25 years in CRE, completed
CREanalyst Fast Track and Valuation courses, has a real-world broker valuation
to use as the demo example.

---

## Knowledge Architecture (3 Layers)

**Layer 1 — Base CRE Valuation Knowledge (built in)**
Public-domain valuation fundamentals: income approach (direct cap and DCF),
CCIM methodology, NOI calculation conventions, vacancy and credit loss
standards, expense ratio benchmarks by property type, cap rate norms by
market tier and asset class, discount rate conventions, IRR and equity
multiple interpretation. No proprietary course materials. This grounds every
output in CRE-specific logic, not generic math.

**Layer 2 — Configurable Criteria (per session)**
User-defined parameters that shape the model: target hold period, discount
rate, rent growth assumptions, expense inflation, exit cap rate, vacancy
assumptions, financing terms. Changeable on every run. This is how the same
agent works for a 5-year multifamily hold and a 10-year industrial sale-leaseback.

**Layer 3 — Client Historical Data (per engagement)**
When deployed for a paying client: their past valuations, comp databases,
and market assumptions ingested to calibrate outputs. The agent learns the
market and criteria that firm works in. This is the retainer story.

---

## MVP Scope (Demo-Ready)

- Structured input form: rent roll (tenant, suite, SF, rent/SF, lease term),
  operating expenses (line-item or total), market comps (3–5 sale comps with
  address, SF, sale price, cap rate), market cap rate range
- Property types: multifamily and office/retail (covers the demo use case)
- Calculates: Gross Potential Income, Effective Gross Income, NOI, value via
  direct cap, full 10-year DCF (annual cash flows, reversion, discount rate),
  IRR, equity multiple, cash-on-cash (Year 1)
- Flags: inputs that deviate significantly from market norms (e.g. expense
  ratio outlier, aggressive rent growth assumption, cap rate spread vs. comps)
- Output: value summary table + DCF schedule + IRR/equity multiple + narrative
  analysis + assumption review
- Delivery: Telegram message + structured markdown/JSON file written to disk
- Human review gate: all inputs confirmed before model runs; assumptions
  displayed and confirmed before final output

---

## Sample Output Format

```
VALUATION SUMMARY — 47,000 SF Office Building | Nashville, TN

──────────────────────────────────────
DIRECT CAPITALIZATION
──────────────────────────────────────
Gross Potential Income:     $940,000
Vacancy / Credit Loss:      $47,000  (5.0%)
Effective Gross Income:     $893,000
Operating Expenses:         $329,410 (36.9%)
Net Operating Income:       $563,590
Market Cap Rate Applied:    6.25%
Indicated Value (Direct Cap): $9,017,440

──────────────────────────────────────
DCF MODEL — 10-Year Hold
──────────────────────────────────────
Year   NOI        Cash Flow    PV @ 7.5%
1      $563,590   $563,590     $524,270
2      $580,498   $580,498     $502,550
...
10     $673,219   $673,219     $325,840
Reversion (6.5% exit cap):  $10,357,215
PV of Reversion:            $5,006,840

Indicated Value (DCF):      $9,230,000

──────────────────────────────────────
INVESTMENT METRICS
──────────────────────────────────────
IRR (unleveraged):          8.4%
Equity Multiple:            1.87x
Cash-on-Cash (Year 1):      6.3%

──────────────────────────────────────
COMP CHECK
──────────────────────────────────────
3 comps averaged:           $194/SF
Indicated value/SF:         $196/SF — CONSISTENT ✓
Cap rate spread vs. comps:  +25bps — within range ✓

──────────────────────────────────────
FLAGS (1)
• Rent growth assumption (3.5%/yr) is above Nashville office trailing
  average (2.8%). Recommend sensitivity test at 2.5% growth.

NARRATIVE:
Value range $9.0M–$9.2M across methods, consistent with comp set. DCF
and direct cap are well-aligned. Primary risk is rent growth assumption,
which is on the optimistic end for Nashville office. At a 6.5% cap,
this pencils. At 7.0%, value drops to approximately $8.05M.
```

---

## Distribution Strategy

Same playbook as the OM Screener: build it to be filmed. Will demos a
real valuation — one he actually did for a broker — and posts it to LinkedIn.
The content writes itself: "I ran a full CRE valuation in 3 minutes. Here's
every number it produced."

The ARGUS price point ($5K–$10K/year) is the hook. Every CRE professional
watching that video has either paid that or knows someone who has. That's the
comment section. That's the inbound.

---

## Risks

| Risk | Mitigation |
|---|---|
| User enters garbage inputs | Input validation + flag layer before model runs |
| LLM miscalculates DCF math | Python handles all arithmetic; Claude handles logic and narrative |
| Cap rate / comp assumptions vary by market | Layer 1 knowledge includes market-tier norms; flags outliers |
| Demo deal has data sensitivity | Use sanitized version of real deal — same structure, anonymized |
| Scope creep into full appraisal report | Hard scope boundary: agent produces valuation analysis, not a USPAP appraisal |
| IP concern (CREanalyst course materials) | Not in MVP — public CCIM methodology and income approach only |

---

## Success Criteria (MVP)

- Given clean structured inputs, produces NOI, direct cap value, and 10-year
  DCF that match manual calculation within rounding tolerance
- IRR and equity multiple are correct (Python-validated)
- Flags at least one input assumption that deviates from market norms
  in the demo deal
- Human review gate fires before model runs; output is clearly labeled
  as agent-generated analysis, not a certified appraisal
- Demo filmed using Will's real broker valuation and posted to LinkedIn
  within 2 weeks of build complete

---

## Out of Scope (MVP)

- **Lease-level commercial modeling (v2).** TI, free rent, downtime, leasing commissions, renewal probability, rent bumps per lease, mark-to-market at rollover. Argus still matters there. We do not claim parity in v1.
- USPAP-compliant appraisal report (this is analysis, not a certified appraisal)
- Sales comparison approach (comp-based land value, replacement cost approach)
- Leveraged DCF / debt service modeling (Layer 2 extension, post-MVP)
- Client historical deal ingestion (Layer 3 — post-MVP)
- Web UI (Telegram delivery sufficient for demo)
- Automated rent roll PDF parsing (structured input form for MVP)
- Multi-scenario modeling (base / bull / bear) — post-MVP

---

_Next step: Will reviews and approves this brief, then we move to PRD (user stories + acceptance criteria)._
_Zoé — 2026-03-04_
