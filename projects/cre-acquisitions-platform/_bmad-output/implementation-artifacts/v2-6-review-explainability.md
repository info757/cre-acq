# Story V2-6: Review and explainability

Status: ready-for-dev

## Story

As a CRE professional,
I want to review lease assumptions before the model runs and see line-of-sight to value impact in the output,
so that I can catch errors and understand the key drivers.

## Acceptance Criteria

1. **Given** ValuationInputV2 with LeaseV2[] **When** human review gate displays assumptions **Then** lease-level summary shown (rollover dates, renewal probability, TI/LC by lease)
2. **And** user can confirm (proceed) or correct assumptions before model runs
3. **And** gate cannot be bypassed in production (--skip-gate for local testing only)
4. **Given** ValuationResultV2 **When** format_valuation_output_v2 assembles output **Then** narrative explains lease-level drivers in plain language
5. **And** key assumptions can be traced to cash flow and value impact
6. **And** Claude generates narrative from prompts file (not hardcoded)
7. **And** output includes lease-level summary for audit

## Tasks / Subtasks

- [ ] Task 1: Human review gate (AC: 1, 2, 3)
  - [ ] Display lease-level summary: rollover dates, renewal prob, TI/LC by lease
  - [ ] Same pattern as v1: Telegram or CLI with confirm/correct
  - [ ] run_valuation_v2 respects --skip-gate for local testing only
- [ ] Task 2: format_valuation_output_v2.py (AC: 4, 5, 6, 7)
  - [ ] Assemble ValuationResultV2
  - [ ] Call Claude with prompts/valuation-narrator-v2.md for lease-level narrative
  - [ ] Include lease-level summary in output JSON
  - [ ] Narrative: key lease drivers, rollover impact, value sensitivity
- [ ] Task 3: prompts/valuation-narrator-v2.md
  - [ ] Prompt for Claude: explain lease-level drivers in plain language
  - [ ] Input: assumptions, cash flows, value; output: narrative
- [ ] Task 4: Tests
  - [ ] Test gate display format
  - [ ] Test narrative generation
  - [ ] Test lease-level summary in output

## Dev Notes

- Architecture: stage-2-valuation/v2/architecture.md
- Prompts: never hardcoded; use prompts/valuation-narrator-v2.md
- Lease-level summary: top N leases by value impact, rollover concentration, etc.
