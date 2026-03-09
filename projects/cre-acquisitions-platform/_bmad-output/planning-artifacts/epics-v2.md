---
stepsCompleted: ['step-01-validate-prerequisites', 'step-02-design-epics', 'step-03-create-stories', 'step-04-final-validation']
inputDocuments:
  - stage-2-valuation/v2/prd.md
  - stage-2-valuation/v2/architecture.md
---

# cre-acquisitions-platform V2 — Epic Breakdown (Argus-Lite)

## Overview

This document provides the complete epic and story breakdown for V2 Argus-Lite (lease-level modeling), decomposing the requirements from the V2 PRD and Architecture into implementable stories.

## Requirements Inventory

### Functional Requirements

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
FR12: Lease schema extends shared/data-model.md; v1 leases remain valid; v2 adds optional rich fields
FR13: System applies market_rent_at_rollover at lease expiration
FR14: System applies renewal_probability to determine renewal vs new-tenant path
FR15: System supports downtime between lease expiration and next lease start
FR16: System models absorption (vacancy fill) during downtime
FR17: Rollover logic handles multiple leases expiring in same period
FR18: Rollover assumptions are explicit and reviewable before model runs
FR19: System calculates TI (tenant improvement) cost per lease
FR20: System applies free_rent_months to reduce cash flow during lease start
FR21: System calculates leasing commission (LC) as % of rent
FR22: System supports different TI/LC for renewal vs new-tenant scenarios
FR23: Leasing costs are applied at appropriate timing (lease start, renewal)
FR24: Leasing cost assumptions are documented and reviewable
FR25: System builds lease-by-lease schedule across hold period
FR26: System aggregates lease-level cash flows to property-level by year
FR27: System handles rent steps (rent_step_schedule) within lease term
FR28: System applies free rent, TI, LC timing correctly in annual schedule
FR29: Cash flow engine outputs annual property NOI, revenue, expenses
FR30: System outputs lease-level detail for explainability and audit
FR31: System computes reversion value at hold-period end
FR32: System produces sensitivity tables (cap rate, rent growth) for lease-level model
FR33: Exit valuation uses lease-level cash flow assumptions
FR34: Reversion cap rate and assumptions are configurable
FR35: Output includes IRR, equity multiple, and value from lease-level DCF
FR36: Human review gate displays lease assumptions before model runs
FR37: Assumption review includes lease-level summary (rollover, renewal prob, costs)
FR38: Output provides line-of-sight to value impact (narrative/explainability)
FR39: Key assumptions can be traced to cash flow and value impact
FR40: Narrative explains lease-level drivers in plain language
FR41: At least 3 real or sanitized lease-heavy test cases exist
FR42: One simple case expected to match closely (manual or Argus benchmark)
FR43: One mixed-use or office/retail case with meaningful rollover exposure
FR44: Output comparison against manual underwriting or Argus-style benchmark
FR45: Documented tolerance bands for NOI, value, and key cash flow differences
FR46: System defines and documents which asset types v2 handles well; scope disclaimer
FR47: No public "Argus replacement" claim until repeatable across real cases
FR48: Public claim remains "matches a targeted slice of Argus lease-level modeling" unless broader evidence exists

### Non-Functional Requirements

NFR1: Python does math; Claude does language (no LLM arithmetic)
NFR2: Prompts are files — never hardcoded in src
NFR3: Human review gate before model runs
NFR4: Documented tolerance bands for NOI, value, cash flow differences

### Additional Requirements

- Target asset types: Office, retail, mixed-use with meaningful commercial concentration
- Model scope: One hold-period model; explicit rollover assumptions
- Data model: Extend shared/data-model.md leases; do not break v1 schema
- Separation: V2 is separate BMAD track; do not contaminate v1 with v2 complexity

### FR Coverage Map

FR1-FR12: Epic 1 - Lease-Level Data Model
FR13-FR18: Epic 2 - Rollover and Renewal Logic
FR19-FR24: Epic 3 - Leasing Cost Logic
FR25-FR30: Epic 4 - Annual Cash Flow Engine
FR31-FR35: Epic 5 - Exit and Valuation Logic
FR36-FR40: Epic 6 - Review and Explainability
FR41-FR45: Epic 7 - Validation Against Known Cases
FR46-FR48: Epic 8 - Boundaries

## Epic List

### Epic 1: Lease-Level Data Model
CRE professionals can provide lease-level data with all required fields (lease_start, lease_end, base_rent, rent_step_schedule, market_rent_at_rollover, ti_per_sf, free_rent_months, downtime_months, leasing_commission_pct, renewal_probability, tenant_category) and have it normalized for the valuation model.
**FRs covered:** FR1-FR12

### Epic 2: Rollover and Renewal Logic
CRE professionals can model lease rollovers with market rent at expiration, renewal probability, downtime, and absorption assumptions.
**FRs covered:** FR13-FR18

### Epic 3: Leasing Cost Logic
CRE professionals can model TI, free rent, and leasing commission with different costs for renewal vs new-tenant scenarios.
**FRs covered:** FR19-FR24

### Epic 4: Annual Cash Flow Engine
CRE professionals can generate lease-by-lease schedules and property-level annual cash flows across the hold period.
**FRs covered:** FR25-FR30

### Epic 5: Exit and Valuation Logic
CRE professionals can compute reversion value, sensitivity tables, IRR, and equity multiple from the lease-level model.
**FRs covered:** FR31-FR35

### Epic 6: Review and Explainability
CRE professionals can review lease assumptions before the model runs and see line-of-sight to value impact in the output.
**FRs covered:** FR36-FR40

### Epic 7: Validation Against Known Cases
Developers can validate the model against at least 3 real or sanitized lease-heavy cases with documented tolerance bands.
**FRs covered:** FR41-FR45

### Epic 8: Boundaries
The system documents which asset types v2 handles well and does not claim Argus replacement until validated.
**FRs covered:** FR46-FR48

---

## Epic 1: Lease-Level Data Model

CRE professionals can provide lease-level data with all required fields and have it normalized for the valuation model.

### Story 1.1: Extend shared data model with LeaseV2 schema

As a CRE professional,
I want the data model to support rich lease fields,
so that lease-level modeling can capture TI, free rent, rollover assumptions, and leasing costs.

**Acceptance Criteria:**

**Given** the shared data model (shared/data-model.md)
**When** we extend the leases structure for v2
**Then** LeaseV2 includes: lease_start, lease_end, base_rent, rent_step_schedule, market_rent_at_rollover, ti_per_sf, free_rent_months, downtime_months, leasing_commission_pct, renewal_probability, tenant_category
**And** v1 lease fields (tenant, sf, expiration, rent_per_sf) remain valid
**And** v2 fields are optional; missing fields have sensible defaults for backward compatibility
**And** rent_step_schedule is array of {date, rent_per_sf} objects

### Story 1.2: Input normalization for lease-level data

As a CRE professional,
I want to provide lease data from OM/Excel or manual input,
so that the valuation model receives properly normalized LeaseV2 data.

**Acceptance Criteria:**

**Given** ScreeningResult with leases (v1 or v2 format) and optional valuation_overrides
**When** normalize_input_v2 runs
**Then** output is ValuationInputV2 with LeaseV2[] normalized
**And** v1 leases (tenant, sf, expiration, rent_per_sf) are upgraded to LeaseV2 with defaults for missing fields
**And** defaults pulled from buy-criteria when overrides not provided
**And** lease-level assumptions (renewal_probability, market_rent_at_rollover, etc.) are mergeable from overrides

---

## Epic 2: Rollover and Renewal Logic

CRE professionals can model lease rollovers with market rent at expiration, renewal probability, downtime, and absorption assumptions.

### Story 2.1: Market rent at expiration, renewal probability application

As a CRE professional,
I want the model to apply market rent and renewal probability at lease expiration,
so that rollover scenarios reflect realistic renewal vs new-tenant outcomes.

**Acceptance Criteria:**

**Given** a lease schedule and valuation assumptions
**When** the rollover engine runs
**Then** market_rent_at_rollover is applied at lease_end for renewal and new-tenant paths
**And** renewal_probability determines weighted blend of renewal vs new-tenant outcome
**And** renewal path uses lower TI/LC than new-tenant path (configurable)
**And** rollover logic handles multiple leases expiring in same period

### Story 2.2: Downtime and absorption between leases

As a CRE professional,
I want the model to support downtime between lease expiration and next lease start,
so that vacancy and absorption are explicitly modeled.

**Acceptance Criteria:**

**Given** a lease expiring and a new lease (renewal or new tenant)
**When** downtime_months is specified
**Then** the model applies vacancy (no rent) for the downtime period
**And** absorption is modeled (vacancy fill) at lease start
**And** downtime assumptions are reviewable before model runs

---

## Epic 3: Leasing Cost Logic

CRE professionals can model TI, free rent, and leasing commission with different costs for renewal vs new-tenant scenarios.

### Story 3.1: TI, free rent, LC calculation (renewal vs new tenant)

As a CRE professional,
I want the model to calculate TI, free rent, and leasing commission correctly,
so that leasing costs are applied at the right timing with renewal vs new-tenant differences.

**Acceptance Criteria:**

**Given** a lease (renewal or new tenant) with ti_per_sf, free_rent_months, leasing_commission_pct
**When** leasing_costs runs
**Then** TI cost = ti_per_sf * sf, applied at lease start
**And** free_rent_months reduces cash flow for that period (no rent collected)
**And** LC = leasing_commission_pct * (base_rent or first-year rent), applied at lease start
**And** renewal path uses lower TI/LC than new-tenant path (configurable ratios)
**And** leasing cost assumptions are documented and reviewable

---

## Epic 4: Annual Cash Flow Engine

CRE professionals can generate lease-by-lease schedules and property-level annual cash flows across the hold period.

### Story 4.1: Lease-by-lease schedule builder

As a CRE professional,
I want the model to build a lease-by-lease schedule across the hold period,
so that each lease's rent, steps, and costs are correctly timed.

**Acceptance Criteria:**

**Given** ValuationInputV2 with LeaseV2[] leases
**When** lease_schedule runs
**Then** output is a lease-by-lease timeline across hold_period_years
**And** rent_step_schedule bumps are applied at specified dates
**And** free_rent_months applied at lease start
**And** lease expirations trigger rollover logic (renewal vs new tenant)
**And** schedule is monthly or quarterly granular (configurable)

### Story 4.2: Property-level aggregation by year

As a CRE professional,
I want lease-level cash flows aggregated to property-level by year,
so that I get annual NOI, revenue, and expenses for DCF.

**Acceptance Criteria:**

**Given** lease-by-lease schedule and leasing costs
**When** cash_flow_engine runs
**Then** output is annual property NOI, revenue, expenses by year
**And** lease-level detail is preserved for explainability and audit
**And** TI, free rent, LC timing correctly reflected in annual cash flows
**And** output format supports exit valuation and sensitivity

---

## Epic 5: Exit and Valuation Logic

CRE professionals can compute reversion value, sensitivity tables, IRR, and equity multiple from the lease-level model.

### Story 5.1: Reversion and sensitivity tables for lease-level model

As a CRE professional,
I want the model to compute reversion and sensitivity from lease-level cash flows,
so that I get IRR, equity multiple, and value with cap rate / rent growth sensitivity.

**Acceptance Criteria:**

**Given** annual cash flows from lease-level engine
**When** exit_valuation runs
**Then** reversion value = terminal NOI / exit_cap_rate
**And** sensitivity tables: cap rate range, rent growth range
**And** output includes IRR, equity multiple, dcf_value
**And** reversion cap rate and assumptions are configurable
**And** output format matches ValuationResultV2 schema

---

## Epic 6: Review and Explainability

CRE professionals can review lease assumptions before the model runs and see line-of-sight to value impact in the output.

### Story 6.1: Assumption review gate for lease assumptions

As a CRE professional,
I want to review lease assumptions before the model runs,
so that I can catch errors and confirm rollover, renewal, and cost assumptions.

**Acceptance Criteria:**

**Given** ValuationInputV2 with LeaseV2[] and valuation overrides
**When** the human review gate displays assumptions
**Then** lease-level summary is shown (rollover dates, renewal probability, TI/LC by lease)
**And** user can confirm (proceed) or correct assumptions before model runs
**And** gate cannot be bypassed in production (--skip-gate for local testing only)

### Story 6.2: Line-of-sight to value impact (narrative/explainability)

As a CRE professional,
I want the output to explain how lease-level assumptions drive value,
so that I understand the key drivers and can trace assumptions to impact.

**Acceptance Criteria:**

**Given** ValuationResultV2 from lease-level model
**When** format_valuation_output_v2 assembles the output
**Then** narrative explains lease-level drivers in plain language
**And** key assumptions can be traced to cash flow and value impact
**And** Claude generates narrative from prompts file (not hardcoded)
**And** output includes lease-level summary for audit

---

## Epic 7: Validation Against Known Cases

Developers can validate the model against at least 3 real or sanitized lease-heavy cases with documented tolerance bands.

### Story 7.1: 3 real or sanitized lease-heavy test cases

As a developer,
I want at least 3 real or sanitized lease-heavy test cases,
so that the model can be validated against known outcomes.

**Acceptance Criteria:**

**Given** the v2 pipeline
**When** validation runs
**Then** at least 3 test cases exist in tests/sample/
**And** one simple case expected to match closely (manual or Argus benchmark)
**And** one mixed-use or office/retail case with meaningful rollover exposure
**And** output comparison against manual underwriting or Argus-style benchmark
**And** each test produces PASS/FAIL with output shown

### Story 7.2: Tolerance bands documentation

As a developer,
I want documented tolerance bands for NOI, value, and cash flow differences,
so that we know when the model is "close enough" and when to investigate.

**Acceptance Criteria:**

**Given** validation test cases
**When** tolerance bands are documented
**Then** NOI tolerance (e.g., ±X% or ±$Y) is specified
**And** value tolerance is specified
**And** key cash flow differences (e.g., year-by-year) have tolerance bands
**And** documentation lives in stage-2-valuation/v2/ or tests/

---

## Epic 8: Boundaries

The system documents which asset types v2 handles well and does not claim Argus replacement until validated.

### Story 8.1: Define and document asset types v2 handles; scope disclaimer

As a CRE professional,
I want clear documentation of what v2 handles well and what it does not,
so that I don't over-rely on the model for unsupported scenarios.

**Acceptance Criteria:**

**Given** the v2 implementation
**When** boundaries are documented
**Then** asset types v2 handles well are listed (office, retail, mixed-use with commercial concentration)
**And** scope disclaimer: "matches a targeted slice of Argus lease-level modeling"
**And** no "Argus replacement" claim until repeatable across 3+ real cases
**And** documentation is in architecture.md, prd.md, or README
