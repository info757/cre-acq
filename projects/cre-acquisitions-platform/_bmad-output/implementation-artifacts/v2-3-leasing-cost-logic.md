# Story V2-3: Leasing cost logic

Status: ready-for-dev

## Story

As a CRE professional,
I want the model to calculate TI, free rent, and leasing commission correctly,
so that leasing costs are applied at the right timing with renewal vs new-tenant differences.

## Acceptance Criteria

1. **Given** a lease with ti_per_sf, free_rent_months, leasing_commission_pct **When** leasing_costs runs **Then** TI cost = ti_per_sf * sf, applied at lease start
2. **And** free_rent_months reduces cash flow for that period (no rent collected)
3. **And** LC = leasing_commission_pct * (base_rent or first-year rent), applied at lease start
4. **And** renewal path uses lower TI/LC than new-tenant path (configurable ratios)
5. **And** leasing cost assumptions are documented and reviewable

## Tasks / Subtasks

- [ ] Task 1: leasing_costs.py (AC: 1, 2, 3, 4)
  - [ ] TI: ti_per_sf * sf at lease start (or renewal)
  - [ ] Free rent: zero rent for free_rent_months at lease start
  - [ ] LC: leasing_commission_pct * annual rent (or first-year) at lease start
  - [ ] Renewal vs new-tenant: apply configurable multiplier (e.g., 0.5 for renewal)
- [ ] Task 2: Integration with rollover_engine
  - [ ] Receive renewal vs new-tenant path from rollover_engine
  - [ ] Apply appropriate TI/LC per path
- [ ] Task 3: Tests
  - [ ] Test TI calculation
  - [ ] Test free rent application
  - [ ] Test LC calculation
  - [ ] Test renewal vs new-tenant cost difference

## Dev Notes

- Architecture: stage-2-valuation/v2/architecture.md
- LC typically 3–6% of first-year rent for new tenant, 1–2% for renewal
- TI: one-time cost at lease start; free rent: revenue reduction over period
