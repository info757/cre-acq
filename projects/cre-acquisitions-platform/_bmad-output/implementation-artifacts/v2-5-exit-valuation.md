# Story V2-5: Exit and valuation logic

Status: ready-for-dev

## Story

As a CRE professional,
I want the model to compute reversion and sensitivity from lease-level cash flows,
so that I get IRR, equity multiple, and value with cap rate / rent growth sensitivity.

## Acceptance Criteria

1. **Given** annual cash flows from lease-level engine **When** exit_valuation runs **Then** reversion value = terminal NOI / exit_cap_rate
2. **And** sensitivity tables: cap rate range, rent growth range
3. **And** output includes IRR, equity multiple, dcf_value
4. **And** reversion cap rate and assumptions are configurable
5. **And** output format matches ValuationResultV2 schema

## Tasks / Subtasks

- [ ] Task 1: exit_valuation.py (AC: 1, 2, 3, 4, 5)
  - [ ] Terminal NOI from last year of cash flows (or Year N+1 if stabilized)
  - [ ] Reversion = terminal NOI / exit_cap_rate
  - [ ] PV of cash flows + reversion at discount_rate
  - [ ] IRR via numpy/scipy
  - [ ] Equity multiple = (sum cash flows + reversion) / initial equity
  - [ ] Sensitivity: cap rate range (e.g., 5.5%–7.5%), rent growth range
- [ ] Task 2: ValuationResultV2 schema
  - [ ] Extend ValuationResult with lease-level fields if needed
  - [ ] Include sensitivity tables in output
- [ ] Task 3: Tests
  - [ ] Test reversion calculation
  - [ ] Test IRR and equity multiple
  - [ ] Test sensitivity table output

## Dev Notes

- Architecture: stage-2-valuation/v2/architecture.md
- Reuse patterns from v1 dcf.py where applicable
- Terminal NOI: use last year of lease-level cash flows; consider stabilization adjustment if needed
