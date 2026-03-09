# Story V2-1: Lease-level data model

Status: ready-for-dev

## Story

As a CRE professional,
I want the data model to support rich lease fields,
so that lease-level modeling can capture TI, free rent, rollover assumptions, and leasing costs.

## Acceptance Criteria

1. **Given** the shared data model **When** we extend leases for v2 **Then** LeaseV2 includes: lease_start, lease_end, base_rent, rent_step_schedule, market_rent_at_rollover, ti_per_sf, free_rent_months, downtime_months, leasing_commission_pct, renewal_probability, tenant_category
2. **And** v1 lease fields (tenant, sf, expiration, rent_per_sf) remain valid
3. **And** v2 fields are optional; missing fields have sensible defaults for backward compatibility
4. **And** rent_step_schedule is array of {date, rent_per_sf} objects

## Tasks / Subtasks

- [ ] Task 1: Extend shared/data-model.md (AC: 1, 2, 3, 4)
  - [ ] Add LeaseV2 schema with all fields
  - [ ] Document backward compatibility with v1 leases
  - [ ] Define defaults for optional fields (e.g., renewal_probability 0.5, downtime_months 0)
- [ ] Task 2: normalize_input_v2.py (AC: 1, 2, 3)
  - [ ] Load ScreeningResult with leases (v1 or v2 format)
  - [ ] Upgrade v1 leases to LeaseV2 with defaults
  - [ ] Output ValuationInputV2 JSON
- [ ] Task 3: Tests
  - [ ] Test v1 lease upgrade to LeaseV2
  - [ ] Test full LeaseV2 passthrough
  - [ ] Test missing optional fields get defaults

## Dev Notes

- Input: shared/data-model.md, v2-argus-lite-brief.md
- LeaseV2 extends ExtractedMetrics.leases structure
- ValuationInputV2 = ValuationInput with LeaseV2[] in extracted_metrics.leases
