# Story V1: Normalize valuation input

Status: ready-for-dev

## Story

As a CRE professional,
I want to confirm valuation assumptions before the model runs,
so that I control the inputs and catch errors before they affect the output.

## Acceptance Criteria

1. **Given** ScreeningResult and optional valuation_overrides **When** normalize runs **Then** output is full ValuationInput with defaults from buy-criteria
2. **And** Supported overrides: market_cap_rate, exit_cap_rate, hold_period_years, rent_growth_rate, expense_growth_rate, vacancy_rate, debt_terms
3. **And** Defaults pulled from buy-criteria.json returns section when overrides not provided
4. **And** Human review gate displays assumptions before model runs (run_valuation responsibility)

## Tasks / Subtasks

- [ ] Task 1: normalize_input.py (AC: 1, 2, 3)
  - [ ] Load ScreeningResult from path
  - [ ] Merge valuation_overrides (file or JSON string)
  - [ ] Fill defaults from buy-criteria.returns
  - [ ] Output ValuationInput JSON
- [ ] Task 2: Tests
  - [ ] Test with ScreeningResult only (defaults applied)
  - [ ] Test with overrides (overrides win)
  - [ ] Test missing buy-criteria (sensible fallbacks)

## Dev Notes

- Input: shared/data-model.md ValuationInput schema
- Defaults: buy-criteria.json returns.hold_period_years, returns.discount_rate, returns.rent_growth_pct, returns.exit_cap_rate
- Output: valuation_input.json structure
