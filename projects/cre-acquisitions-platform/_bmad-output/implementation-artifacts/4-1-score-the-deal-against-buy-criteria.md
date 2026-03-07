# Story 4.1: Score the deal against buy criteria

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an acquisitions professional,
I want each metric scored against my criteria,
so that I know immediately which criteria the deal passes or fails.

## Acceptance Criteria

1. **Given** confirmed metrics and buy-criteria.json **When** the scoring engine runs **Then** each criterion produces a PASS / FAIL / FLAG result
2. **And** FLAG is used when data is present but ambiguous (e.g., DSCR marginally below threshold)
3. **And** overall verdict is GO / CONDITIONAL / NO-GO
4. **And** Python handles all numeric comparisons — Claude never does arithmetic
5. **And** scoring logic is in a separate, readable Python file (not buried in a prompt)

## Tasks / Subtasks

- [x] Task 1: Verify PASS/FAIL/FLAG per criterion (AC: 1)
  - [x] Each buy-criteria field produces a result in criteria_results
  - [x] Hard gates (property type, markets, max_asking_price, hard_min_dscr) → FAIL = NO-GO
  - [x] Soft gates (min_dscr, max_ltv, min_cap, min_occ, max_exp, vintage) → FLAG when failed
  - [x] PASS when criterion met
- [x] Task 2: FLAG semantics (AC: 2)
  - [x] FLAG when metric marginally fails (e.g., DSCR below min but above hard_min)
  - [x] FLAG when metric unavailable but criterion is set (e.g., DSCR null, hard_min_dscr set)
  - [x] Document FLAG vs FAIL in score.py comments
- [x] Task 3: Verdict logic (AC: 3)
  - [x] GO = no FAIL, no FLAG
  - [x] CONDITIONAL = no FAIL, has FLAG or red_flags
  - [x] NO-GO = any FAIL
- [x] Task 4: Python-only scoring (AC: 4)
  - [x] All comparisons in score.py; no Claude calls for scoring
  - [x] Numeric types: Decimal where appropriate, float for ratios
- [x] Task 5: Readable scoring file (AC: 5)
  - [x] score.py is the single source; no scoring logic in prompts
  - [x] Clear section comments (HARD GATES, SOFT GATES, SOFT FLAGS)
- [x] Task 6: Tests (AC: all)
  - [x] Test each criterion: PASS, FAIL, FLAG paths
  - [x] Test verdict: GO, CONDITIONAL, NO-GO
  - [x] Run: `python3 tests/test_score.py` or `pytest tests/test_score.py -v`

## Dev Notes

### Architecture Compliance

- **Scoring:** `stage-1-om-screener/src/score.py`
- **Input:** confirmed_metrics.json (from apply_corrections.py) + buy-criteria.json
- **Output:** ScreeningResult JSON (verdict, criteria_results, red_flags, extracted_metrics)
- **Pipeline:** Stage 4 in architecture — after human review gate, before narrative/output

### Technical Requirements

- **PASS:** Criterion met (value within threshold)
- **FAIL:** Hard criterion not met → NO-GO verdict
- **FLAG:** Soft criterion not met, or data ambiguous → CONDITIONAL verdict
- **Verdict:** GO (all pass) | CONDITIONAL (flags, no fails) | NO-GO (any fail)
- **Plausibility:** score.py validates metrics are within plausible CRE ranges before scoring; implausible → NO-GO with Data Integrity flag

### File Structure Requirements

```
stage-1-om-screener/
  src/
    score.py              ← scoring logic (Screener class, run())
  tests/
    test_score.py         ← unit tests per criterion, verdict, flags
shared/
  buy-criteria.json       ← criteria config (from Story 3.1)
  buy-criteria-schema.md  ← field reference
```

### Testing Requirements

- Test each criterion independently (DSCR, LTV, cap rate, occupancy, expense ratio, property type, markets, max_asking_price, vintage)
- Test verdict determination: GO, CONDITIONAL, NO-GO
- Test red flag propagation (extraction_flags, proforma premium)
- Test plausibility validation (out-of-range metrics → NO-GO)
- Test gate enforcement: _human_confirmed required (from Story 2.2)

### Previous Story Intelligence (3.1)

- score.py consumes buy-criteria.json; all sections optional (missing = no filter)
- Criteria fields: property_types, markets, max_asking_price, debt (hard_min_dscr, min_dscr, max_ltv), income (min_cap_rate_trailing, min_occupancy, max_proforma_noi_premium), expenses (max_expense_ratio), vintage_min, vintage_max
- Markets: exact or city substring match (e.g., "Phoenix" matches "Phoenix, AZ")
- Schema doc: shared/buy-criteria-schema.md

### References

- [Source: stage-1-om-screener/src/score.py] — current implementation
- [Source: shared/data-model.md#ScreeningResult] — output schema
- [Source: shared/buy-criteria-schema.md] — criteria fields
- [Source: stage-1-om-screener/architecture.md] — score.py spec, pipeline Stage 4
- [Source: _bmad-output/planning-artifacts/epics.md] — Epic 4, Story 4.1

## Change Log

- 2026-03-06: Dev-story complete. Verified all AC; added Screener docstring (FLAG vs FAIL). 31 tests pass. Ready for review.
- 2026-03-06: Story created via create-story workflow. Ready for dev.

## Dev Agent Record

### Agent Model Used

Claude (dev-story workflow)

### Debug Log References

### Completion Notes List

- score.py already implements all AC from Story 3.1 + Epic 4
- Added Screener class docstring documenting PASS/FAIL/FLAG semantics
- All 31 tests pass (criterion, verdict, flags, integration)

### File List

- stage-1-om-screener/src/score.py (modified: Screener docstring)
