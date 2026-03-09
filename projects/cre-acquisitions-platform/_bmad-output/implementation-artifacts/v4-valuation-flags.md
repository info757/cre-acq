# Story V4: Flag outlier assumptions

Status: ready-for-dev

## Story

As a CRE professional,
I want the system to flag inputs that deviate from market norms,
so that I know when my assumptions are aggressive or unusual.

## Acceptance Criteria

1. **Given** valuation input and result **When** flags runs **Then** list of flag objects (flag, explanation)
2. **And** Flags: expense ratio outlier, rent growth above norm, cap rate spread vs comps
3. **And** At least one flag surfaced in the demo deal
4. **And** Flags are explanatory, not blocking

## Tasks / Subtasks

- [ ] Task 1: flags.py (AC: 1, 2, 3, 4)
  - [ ] Expense ratio vs asset-class norm (e.g. multifamily ~35-45%, office ~40-50%)
  - [ ] Rent growth vs conservative default (3%)
  - [ ] Cap rate spread when comp data available
  - [ ] Output list of {flag, explanation}
- [ ] Task 2: Tests
  - [ ] Test expense ratio flag
  - [ ] Test rent growth flag
  - [ ] Test no flags when inputs within norms

## Dev Notes

- Asset-class norms: use simple thresholds from project-brief / CRE conventions
- Mill One: expense ratio, rent growth can be flagged
