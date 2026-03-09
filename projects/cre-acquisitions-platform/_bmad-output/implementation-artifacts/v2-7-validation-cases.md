# Story V2-7: Validation against known cases

Status: ready-for-dev

## Story

As a developer,
I want at least 3 real or sanitized lease-heavy test cases with documented tolerance bands,
so that the model can be validated against known outcomes.

## Acceptance Criteria

1. **Given** the v2 pipeline **When** validation runs **Then** at least 3 test cases exist in tests/sample/
2. **And** one simple case expected to match closely (manual or Argus benchmark)
3. **And** one mixed-use or office/retail case with meaningful rollover exposure
4. **And** output comparison against manual underwriting or Argus-style benchmark
5. **And** each test produces PASS/FAIL with output shown
6. **And** tolerance bands documented for NOI, value, key cash flow differences

## Tasks / Subtasks

- [ ] Task 1: Test cases (AC: 1, 2, 3, 4, 5)
  - [ ] Create tests/sample/lease-heavy-case-1.json (simple)
  - [ ] Create tests/sample/lease-heavy-case-2.json (mixed-use or office/retail)
  - [ ] Create tests/sample/lease-heavy-case-3.json (third case)
  - [ ] Each: LeaseV2[] + expected NOI/value or benchmark reference
  - [ ] Test script: run pipeline, compare output to expected, PASS/FAIL
- [ ] Task 2: Tolerance bands documentation (AC: 6)
  - [ ] Document NOI tolerance (e.g., ±2% or ±$X)
  - [ ] Document value tolerance
  - [ ] Document key cash flow differences (year-by-year)
  - [ ] Location: stage-2-valuation/v2/tolerance-bands.md or tests/README
- [ ] Task 3: Validation script
  - [ ] Run all 3 cases, report PASS/FAIL
  - [ ] Output comparison summary

## Dev Notes

- v2-argus-lite-brief.md: "At least 3 real or sanitized lease-heavy test cases"
- Sanitized = real structure, anonymized numbers
- Benchmark: manual underwriting or Argus export if available
- Public claim: "matches a targeted slice of Argus lease-level modeling" until broader evidence
