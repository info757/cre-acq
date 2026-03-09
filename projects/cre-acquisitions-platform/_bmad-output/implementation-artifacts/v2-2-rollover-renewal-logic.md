# Story V2-2: Rollover and renewal logic

Status: ready-for-dev

## Story

As a CRE professional,
I want the model to apply market rent and renewal probability at lease expiration,
so that rollover scenarios reflect realistic renewal vs new-tenant outcomes.

## Acceptance Criteria

1. **Given** a lease schedule and valuation assumptions **When** rollover_engine runs **Then** market_rent_at_rollover applied at lease_end for renewal and new-tenant paths
2. **And** renewal_probability determines weighted blend of renewal vs new-tenant outcome
3. **And** renewal path uses lower TI/LC than new-tenant path (configurable)
4. **And** rollover logic handles multiple leases expiring in same period
5. **And** downtime_months applied between lease expiration and next lease start
6. **And** absorption (vacancy fill) modeled during downtime

## Tasks / Subtasks

- [ ] Task 1: rollover_engine.py (AC: 1, 2, 3, 4)
  - [ ] For each expiring lease: apply renewal_probability to branch renewal vs new-tenant
  - [ ] Apply market_rent_at_rollover at lease_end
  - [ ] Configurable TI/LC ratios: renewal vs new-tenant (e.g., 50% TI, 50% LC for renewal)
  - [ ] Handle multiple leases expiring in same period (sequential or parallel)
- [ ] Task 2: Downtime and absorption (AC: 5, 6)
  - [ ] Apply downtime_months (no rent) between expiration and next lease
  - [ ] Model absorption at lease start
- [ ] Task 3: Tests
  - [ ] Test single lease rollover (renewal vs new tenant)
  - [ ] Test multiple leases expiring same period
  - [ ] Test downtime application

## Dev Notes

- Architecture: stage-2-valuation/v2/architecture.md
- Renewal vs new-tenant cost ratios: configurable in valuation_overrides or buy-criteria
- downtime_months: typically 0–6 for office/retail
