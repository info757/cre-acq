# Story V3: Calculate 10-year DCF and returns

Status: ready-for-dev

## Story

As a CRE professional,
I want a full 10-year DCF with reversion and return metrics,
so that I can compare value across methods and assess IRR/equity multiple.

## Acceptance Criteria

1. **Given** NOI, hold_period, rent_growth, expense_growth, exit_cap, discount_rate **When** dcf runs **Then** annual NOI projection, reversion, PV, IRR, equity multiple computed
2. **And** Reversion = Year N+1 NOI / exit_cap_rate
3. **And** Python handles all arithmetic
4. **And** Output matches manual calculation within rounding tolerance

## Tasks / Subtasks

- [ ] Task 1: dcf.py (AC: 1, 2, 3)
  - [ ] Project NOI: Year 1 from input, then growth applied
  - [ ] Reversion at end of hold
  - [ ] PV of cash flows at discount_rate
  - [ ] IRR via numpy or scipy, or iterative solution
  - [ ] Equity multiple = (sum of cash flows + reversion) / initial equity
  - [ ] Cash-on-cash Year 1 if debt terms provided
- [ ] Task 2: Tests
  - [ ] Test against Mill One known values (Will's DCF: $35,065,501 at 7% discount)
  - [ ] Test IRR calculation
  - [ ] Test equity multiple

## Dev Notes

- Mill One reference: knowledge/deal-analysis/mill-one-investor-analysis.md
- Will's model: 3% rent growth, 7% discount, 10-year hold, 6.65% exit cap
- Use Decimal where appropriate, float for IRR (scipy/numpy)
