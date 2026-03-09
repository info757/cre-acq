# Story V2-4: Annual cash flow engine

Status: ready-for-dev

## Story

As a CRE professional,
I want the model to build a lease-by-lease schedule and aggregate to property-level annual cash flows,
so that I get annual NOI, revenue, and expenses for DCF from lease-level detail.

## Acceptance Criteria

1. **Given** ValuationInputV2 with LeaseV2[] **When** lease_schedule runs **Then** output is lease-by-lease timeline across hold_period_years
2. **And** rent_step_schedule bumps applied at specified dates
3. **And** free_rent_months applied at lease start
4. **And** lease expirations trigger rollover logic (renewal vs new tenant)
5. **Given** lease schedule and leasing costs **When** cash_flow_engine runs **Then** output is annual property NOI, revenue, expenses by year
6. **And** lease-level detail preserved for explainability and audit
7. **And** TI, free rent, LC timing correctly reflected in annual cash flows

## Tasks / Subtasks

- [ ] Task 1: lease_schedule.py (AC: 1, 2, 3, 4)
  - [ ] Build monthly or quarterly timeline across hold period
  - [ ] Apply rent_step_schedule at dates
  - [ ] Apply free_rent_months at lease start
  - [ ] Integrate with rollover_engine for expirations
- [ ] Task 2: cash_flow_engine.py (AC: 5, 6, 7)
  - [ ] Aggregate lease-level to property-level by year
  - [ ] Include TI, free rent, LC in timing
  - [ ] Preserve lease-level detail in output for audit
- [ ] Task 3: Tests
  - [ ] Test lease schedule with rent steps
  - [ ] Test property-level aggregation
  - [ ] Test TI/free rent/LC timing in annual output

## Dev Notes

- Architecture: stage-2-valuation/v2/architecture.md
- Granularity: monthly or quarterly (configurable); annual aggregation for DCF
- Output format: annual_cash_flows.json with year, noi, revenue, expenses, lease_detail[]
