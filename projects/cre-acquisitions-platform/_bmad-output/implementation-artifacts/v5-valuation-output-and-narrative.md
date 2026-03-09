# Story V5: Produce valuation output and narrative

Status: ready-for-dev

## Story

As a CRE professional,
I want a clear value summary plus plain-English narrative,
so that I can use the output for pricing guidance or internal memos.

## Acceptance Criteria

1. **Given** valuation inputs, direct_cap_value, dcf_value, returns, flags **When** format runs **Then** ValuationResult JSON with narrative
2. **And** Narrative explains value range, key assumptions, primary risks
3. **And** Claude writes narrative; Python does math
4. **And** Output written to JSON and formatted for Telegram/markdown

## Tasks / Subtasks

- [ ] Task 1: format_valuation_output.py (AC: 1, 2, 3, 4)
  - [ ] Assemble ValuationResult schema
  - [ ] Call Claude with valuation-narrator.md prompt
  - [ ] Write JSON to --out
  - [ ] Print formatted message to stdout (Telegram-ready)
- [ ] Task 2: prompts/valuation-narrator.md
  - [ ] Template with placeholders for value, returns, flags, assumptions
  - [ ] Output: 3-5 sentence narrative
- [ ] Task 3: Tests
  - [ ] Test output schema matches data-model
  - [ ] Test narrative generation (mock or integration)

## Dev Notes

- Follow format_output.py pattern from Stage 1
- ValuationResult schema: shared/data-model.md
