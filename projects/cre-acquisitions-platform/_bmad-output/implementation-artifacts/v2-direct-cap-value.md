# Story V2: Calculate direct cap value

Status: ready-for-dev

## Story

As a CRE professional,
I want the system to compute value via direct capitalization,
so that I have a quick sanity check against market cap rates.

## Acceptance Criteria

1. **Given** NOI and market_cap_rate **When** direct_cap runs **Then** value = NOI / cap_rate
2. **And** NOI source: trailing from ExtractedMetrics, or pro-forma if trailing absent
3. **And** Python handles all arithmetic
4. **And** Output matches manual calculation within rounding tolerance

## Tasks / Subtasks

- [ ] Task 1: direct_cap.py (AC: 1, 2, 3)
  - [ ] Accept --noi and --cap-rate or read from ValuationInput
  - [ ] value = noi / cap_rate (Decimal for precision)
  - [ ] Output JSON with direct_cap_value
- [ ] Task 2: Tests
  - [ ] Unit test: known NOI/cap -> known value
  - [ ] Test NOI selection: trailing preferred, pro-forma fallback

## Dev Notes

- Use Decimal for financial calculations
- Round output to 2 decimal places for display
