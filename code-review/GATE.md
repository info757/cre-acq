# Codex Review Gate

## What This Is

Every stage must pass a Codex 5.3 review before it advances from **Build** to **Tested**.

This is a second-LLM adversarial review. Claude writes the code. GPT-5.3-Codex reviews it.
Different model, different blind spots — that's the point.

---

## When It Runs

**Required before a stage can be marked "Tested" in the build status table.**

Specifically: after all user stories in a stage are code-complete, before any real OM
is run through the system for acceptance testing.

Can also be triggered any time during build (recommended after each major script is complete).

---

## How to Trigger

Tell Zoé in Telegram:

> "Z, run Codex review on stage-1"

Or for a specific file:

> "Z, run Codex review on stage-1-om-screener/src/extract_text.py"

Zoé will:
1. Read the target file(s)
2. Spawn a sub-agent using `openai/gpt-5.3-codex` with the CRE review prompt
3. Save the report to `code-review/reports/YYYY-MM-DD-<stage>-<target>.md`
4. Surface any BLOCKER findings immediately

---

## Review Scope

### Full Stage Review (use before advancing to Tested)
All files in `stage-N/src/`, all prompts in `stage-N/prompts/`

### Single-File Review (use during build)
Any specific Python script or prompt file

---

## Report Format

Each report in `code-review/reports/` contains:

- Date + model used
- Files reviewed
- Findings by severity: BLOCKER / WARNING / SUGGESTION
- Overall verdict: PASS / FAIL / PASS WITH WARNINGS

**BLOCKER = stage cannot advance until resolved.**
**WARNING = must be addressed before demo.**
**SUGGESTION = nice to have, log and decide.**

---

## Gate Status

| Stage | Last Review | Verdict | Report |
|---|---|---|---|
| Stage 1 — OM Screener | — | ⬜ pending | — |
| Stage 2 — Valuation | — | ⬜ pending | — |

Update this table after each review.

---

## Rules

1. Gate is mandatory. Not optional. Not skippable.
2. A PASS WITH WARNINGS is acceptable to advance, provided WARNINGs are tracked.
3. FAIL means: fix the BLOCKERs, re-run, get a clean report before moving on.
4. Reviewer model: `openai/gpt-5.3-codex`. Do not substitute.
5. Reports are cumulative. Don't delete old ones. The history is the audit trail.
