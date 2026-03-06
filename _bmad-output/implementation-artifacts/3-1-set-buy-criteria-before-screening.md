# Story 3.1: Set buy criteria before screening

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an acquisitions professional,
I want to define my screening criteria in plain terms,
so that the scoring reflects what I'm actually looking for today.

## Acceptance Criteria

1. **Given** a buy-criteria.json config file **When** the user edits the file **Then** criteria are human-editable (no code required)
2. **And** supported fields: property type, target markets, max asking price, min cap rate, min occupancy, max LTV, min DSCR, max expense ratio, vintage range, max pro-forma to trailing NOI gap %
3. **And** criteria can be changed between runs without code changes
4. **And** missing criteria fields default to "no filter" (pass everything)
5. **And** criteria file is version-controlled alongside the project

## Tasks / Subtasks

- [x] Task 1: Document buy-criteria schema (AC: 1, 2)
  - [x] Schema doc: shared/buy-criteria-schema.md
  - [x] List all supported fields with types, examples, "no filter" meaning
  - [x] property_types, markets, max_asking_price, debt, income, expenses, vintage
- [x] Task 2: Verify score.py defaults (AC: 4)
  - [x] Each criterion: when null, scoring skips (no filter)
  - [x] property_types: [] → pass all types
  - [x] markets: [] → pass all markets
  - [x] Numeric thresholds: null → no filter for that criterion
- [x] Task 3: Schema validation vs flexibility (AC: 1, 4)
  - [x] score.py: required sections; nested fields may be null
  - [x] Minimal criteria (all null filters) runs without failing
  - [x] Document: buy-criteria-schema.md
- [x] Task 4: Version control and location (AC: 5)
  - [x] Criteria at shared/buy-criteria.json (already in repo)
  - [x] README: buy-criteria-schema.md reference, no code deploy needed
- [x] Task 5: Tests (AC: all)
  - [x] Test: minimal criteria (MINIMAL_CRITERIA) → score runs
  - [x] Test: property_types=[] → all types pass
  - [x] Test: null DSCR filter → check skipped

## Dev Notes

### Architecture Compliance

- **Config:** `shared/buy-criteria.json`
- **Consumer:** `stage-1-om-screener/src/score.py` (--criteria path)
- **Schema:** score.py REQUIRED_CRITERIA_SECTIONS = ["property_types", "debt", "income", "expenses"]; nested fields have defaults

### Technical Requirements

- **Human-editable:** JSON only. No Python, no code. User edits file, next run uses new values.
- **Defaults:** criteria.get("debt", {}).get("hard_min_dscr", 1.10) pattern. null in JSON → treat as "no filter" where applicable.
- **property_types:** [] or missing → allow all. Non-empty list → whitelist.
- **markets:** [] or missing → allow all. (Future: geographic filter.)

### File Structure Requirements

```
shared/
  buy-criteria.json       ← user edits this
  buy-criteria-schema.md  ← optional: schema doc (this story)
  data-model.md           ← may extend buy-criteria section
stage-1-om-screener/
  src/
    score.py              ← consumes criteria, applies defaults
  tests/
    test_score.py         ← criteria tests
```

### Testing Requirements

- Test score with minimal criteria (only required sections, null optional fields)
- Test property_types=[] → all types pass
- Test missing max_asking_price → no price filter
- Run: `pytest tests/test_score.py -v`

### Previous Story Intelligence (2.2)

- score.py consumes confirmed_metrics + buy-criteria.json
- Gate enforcement: _human_confirmed required
- buy-criteria.json exists with rich structure (returns, debt, income, expenses, commercial, capex, vintage)

### References

- [Source: shared/buy-criteria.json] — current schema
- [Source: shared/data-model.md#buy-criteria] — schema sketch
- [Source: stage-1-om-screener/src/score.py] — REQUIRED_CRITERIA_SECTIONS, default handling
- [Source: _bmad-output/planning-artifacts/epics.md] — Epic 3, Story 3.1

## Change Log

- 2026-03-06: Dev-story complete. Schema doc, null=no filter in score.py, TestBuyCriteriaDefaults, README update. 19 score tests + 22 review-gate pass. Ready for review.
- 2026-03-06: Story created via create-story workflow. Ready for dev.

## Dev Agent Record

### Agent Model Used

Claude (dev-story workflow)

### Debug Log References

### Completion Notes List

- shared/buy-criteria-schema.md: field reference, null = no filter
- score.py: null thresholds skip criterion (hard_min_dscr, min_dscr, max_ltv, min_cap, min_occ, max_exp, max_premium)
- test_score: _human_confirmed in STRONG_METRICS; TestBuyCriteriaDefaults (minimal criteria, property_types=[], null DSCR)
- README: buy-criteria-schema.md reference

### File List

- shared/buy-criteria-schema.md (new)
- stage-1-om-screener/src/score.py (modified: null = no filter)
- stage-1-om-screener/tests/test_score.py (modified: _human_confirmed, TestBuyCriteriaDefaults)
- README.md (modified: buy-criteria-schema reference)
