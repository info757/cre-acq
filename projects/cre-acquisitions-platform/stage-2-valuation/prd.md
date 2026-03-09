# Product Requirements Document — CRE Valuation Agent
**BMAD Phase 2: Planning**
_Status: APPROVED for v1 — demo-ready scope_

---

## Overview

User stories and acceptance criteria for the v1 Valuation Agent. Each story has a clear "done" definition. Scope is constrained to direct cap + 10-year DCF only. No lease-level modeling in v1.

---

## Epic 1: Input and Assumptions

### US-V1 — Confirm structured valuation inputs before model runs
**As a** CRE professional,
**I want to** review and confirm valuation assumptions before the model runs,
**so that** I control the inputs and catch errors before they affect the output.

**Acceptance Criteria:**
- [ ] Stage 2 accepts ScreeningResult (from Stage 1) as primary input
- [ ] Valuation overrides supported: market_cap_rate, exit_cap_rate, hold_period_years, rent_growth_rate, expense_growth_rate, vacancy_rate, debt_terms
- [ ] Defaults pulled from buy-criteria.json returns section when overrides not provided
- [ ] Human review gate displays assumptions before model runs
- [ ] Output is clearly labeled as agent-generated analysis, not a certified appraisal

---

## Epic 2: Direct Capitalization

### US-V2 — Calculate direct cap value
**As a** CRE professional,
**I want** the system to compute value via direct capitalization,
**so that** I have a quick sanity check against market cap rates.

**Acceptance Criteria:**
- [ ] NOI / market_cap_rate = indicated value
- [ ] NOI source: trailing from ExtractedMetrics, or pro-forma if trailing absent
- [ ] Cap rate: from overrides or buy-criteria default
- [ ] Python handles all arithmetic
- [ ] Output matches manual calculation within rounding tolerance

---

## Epic 3: DCF and Returns

### US-V3 — Calculate 10-year DCF and investment returns
**As a** CRE professional,
**I want** a full 10-year DCF with reversion and return metrics,
**so that** I can compare value across methods and assess IRR/equity multiple.

**Acceptance Criteria:**
- [ ] Annual NOI projection: Year 1 from input, then rent_growth and expense_growth applied
- [ ] Reversion: Year 11 NOI / exit_cap_rate
- [ ] PV of cash flows at discount_rate
- [ ] IRR (unleveraged) and equity multiple computed correctly
- [ ] Cash-on-cash Year 1 if debt terms provided
- [ ] Python handles all arithmetic
- [ ] Output matches manual calculation within rounding tolerance

---

## Epic 4: Sanity Checks and Flags

### US-V4 — Flag outlier assumptions and comp inconsistencies
**As a** CRE professional,
**I want** the system to flag inputs that deviate from market norms,
**so that** I know when my assumptions are aggressive or unusual.

**Acceptance Criteria:**
- [ ] Flags expense ratio outliers vs asset-class norms
- [ ] Flags rent growth above market trailing average when known
- [ ] Flags cap rate spread vs comps when comp data provided
- [ ] At least one flag surfaced in the demo deal
- [ ] Flags are explanatory, not blocking

---

## Epic 5: Output and Narrative

### US-V5 — Produce readable valuation output and narrative
**As a** CRE professional,
**I want** a clear value summary plus plain-English narrative,
**so that** I can use the output for pricing guidance or internal memos.

**Acceptance Criteria:**
- [ ] Output includes: direct_cap_value, dcf_value, suggested_offer, returns (IRR, equity multiple, cash-on-cash), sensitivity, narrative
- [ ] Narrative explains value range, key assumptions, and primary risks
- [ ] Claude writes narrative; Python does math
- [ ] Output written to JSON and formatted for Telegram/markdown
- [ ] Delivery path matches Stage 1 (Telegram + disk)

---

## Out of Scope (v1)

- Lease-level commercial modeling
- Leveraged DCF / debt service modeling
- Multi-scenario (base / bull / bear)
- Automated rent roll PDF parsing
- USPAP appraisal
- Web UI

---

_Next step: Architecture (script decomposition, data flow, prompts)._
