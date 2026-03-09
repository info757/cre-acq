# V2 Argus-Lite — Product Requirements Document

**Status:** Planning (BMAD v6)
**Source:** v2-argus-lite-brief.md

---

## Overview

V2 is a separate BMAD track focused on lease-level modeling. It is not an extension of v1. Target: office, retail, mixed-use with meaningful commercial concentration. One hold-period model. Explicit rollover assumptions.

---

## Functional Requirements

### Lease Schema (FR1–FR12)

FR1: Lease schema supports lease_start (date) — lease commencement
FR2: Lease schema supports lease_end (date) — lease expiration
FR3: Lease schema supports base_rent (number) — contractual rent
FR4: Lease schema supports rent_step_schedule (array) — bumps by date or interval
FR5: Lease schema supports market_rent_at_rollover (number) — mark-to-market at expiration
FR6: Lease schema supports ti_per_sf (number) — tenant improvement allowance
FR7: Lease schema supports free_rent_months (integer) — free rent period
FR8: Lease schema supports downtime_months (number) — vacancy between leases
FR9: Lease schema supports leasing_commission_pct (number) — LC as % of rent
FR10: Lease schema supports renewal_probability (number, 0–1)
FR11: Lease schema supports tenant_category (string) — anchor / inline / etc
FR12: Lease schema extends shared/data-model.md; v1 leases (tenant, sf, expiration, rent_per_sf) remain valid; v2 adds optional rich fields

### Rollover and Renewal Logic (FR13–FR18)

FR13: System applies market_rent_at_rollover at lease expiration
FR14: System applies renewal_probability to determine renewal vs new-tenant path
FR15: System supports downtime between lease expiration and next lease start
FR16: System models absorption (vacancy fill) during downtime
FR17: Rollover logic handles multiple leases expiring in same period
FR18: Rollover assumptions are explicit and reviewable before model runs

### Leasing Cost Logic (FR19–FR24)

FR19: System calculates TI (tenant improvement) cost per lease
FR20: System applies free_rent_months to reduce cash flow during lease start
FR21: System calculates leasing commission (LC) as % of rent
FR22: System supports different TI/LC for renewal vs new-tenant scenarios
FR23: Leasing costs are applied at appropriate timing (lease start, renewal)
FR24: Leasing cost assumptions are documented and reviewable

### Annual Cash Flow Engine (FR25–FR30)

FR25: System builds lease-by-lease schedule across hold period
FR26: System aggregates lease-level cash flows to property-level by year
FR27: System handles rent steps (rent_step_schedule) within lease term
FR28: System applies free rent, TI, LC timing correctly in annual schedule
FR29: Cash flow engine outputs annual property NOI, revenue, expenses
FR30: System outputs lease-level detail for explainability and audit

### Exit and Valuation Logic (FR31–FR35)

FR31: System computes reversion value at hold-period end
FR32: System produces sensitivity tables (cap rate, rent growth) for lease-level model
FR33: Exit valuation uses lease-level cash flow assumptions
FR34: Reversion cap rate and assumptions are configurable
FR35: Output includes IRR, equity multiple, and value from lease-level DCF

### Review and Explainability (FR36–FR40)

FR36: Human review gate displays lease assumptions before model runs
FR37: Assumption review includes lease-level summary (rollover, renewal prob, costs)
FR38: Output provides line-of-sight to value impact (narrative/explainability)
FR39: Key assumptions can be traced to cash flow and value impact
FR40: Narrative explains lease-level drivers in plain language

### Validation (FR41–FR45)

FR41: At least 3 real or sanitized lease-heavy test cases exist
FR42: One simple case expected to match closely (manual or Argus benchmark)
FR43: One mixed-use or office/retail case with meaningful rollover exposure
FR44: Output comparison against manual underwriting or Argus-style benchmark
FR45: Documented tolerance bands for NOI, value, and key cash flow differences

### Boundaries (FR46–FR48)

FR46: System defines and documents which asset types v2 handles well; scope disclaimer
FR47: No public "Argus replacement" claim until repeatable across real cases
FR48: Public claim remains "matches a targeted slice of Argus lease-level modeling" unless broader evidence exists

---

## Non-Functional Requirements

NFR1: Python does math; Claude does language (no LLM arithmetic)
NFR2: Prompts are files — never hardcoded in src
NFR3: Human review gate before model runs
NFR4: Documented tolerance bands for NOI, value, cash flow differences

---

## Additional Requirements

- **Target asset types:** Office, retail, mixed-use with meaningful commercial concentration
- **Model scope:** One hold-period model; explicit rollover assumptions
- **Data model:** Extend shared/data-model.md leases; do not break v1 schema
- **Separation:** V2 is separate BMAD track; do not contaminate v1 with v2 complexity
