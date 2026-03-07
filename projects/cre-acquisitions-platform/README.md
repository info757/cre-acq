# CRE Acquisitions Intelligence Platform

An end-to-end AI pipeline that takes a CRE deal from raw OM to LOI-ready offer.
Built by Will Holt + Zoé. Stack: n8n + Python + Claude.

---

## Git

This project lives inside the OpenClaw workspace. Two remotes:

- **origin (life_automation)** — OpenClaw workspace. `git push` pushes everything.
- **cre-acq** — This project only. Run `./push-to-cre-acq.sh` to push just cre-acquisitions-platform.

---

## The Pipeline

```
[Stage 0 — future]     Crexi Scraper
                         ↓ surfaces deals matching rough criteria

[Stage 1 — build first] OM Screener
                         ↓ reads the OM, screens against buy criteria
                         ↓ outputs GO deals with extracted financial data (JSON)

[Stage 2 — build second] Valuation Agent
                          ↓ takes Stage 1 JSON, runs DCF + direct cap
                          ↓ outputs property value + suggested LOI offer price

[Human]                  Reviews verdict → signs LOI
```

---

## Directory Structure

```
cre-acquisitions-platform/
  shared/
    data-model.md        ← THE contract between stages. Read before touching anything.
    buy-criteria.json    ← user-configurable screening criteria (edit directly, no code deploy)
    buy-criteria-schema.md ← field reference, null = no filter
  stage-1-om-screener/
    project-brief.md     ← APPROVED
    prd.md               ← APPROVED
    architecture.md      ← TODO
    prompts/
    src/
    tests/
  stage-2-valuation/
    project-brief.md     ← DRAFT (needs review)
    prd.md               ← TODO
    architecture.md      ← TODO
    prompts/
    src/
    tests/
  pipeline/
    run-full.py          ← end-to-end: Stage 1 → Stage 2
  CURSOR-SETUP.md        ← how to connect Cursor to Zoé
```

---

## Build Status

| Stage | Brief | PRD | Architecture | Build | Codex Review | Tested | Integration |
|---|---|---|---|---|---|---|---|
| Stage 1 — OM Screener (Days 1-3: Ingestion) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⬜ |
| Stage 1 — OM Screener (Days 4-9: Review→Output) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 🟡 |
| Stage 2 — Valuation | 🟡 draft | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |

**Build Status Legend:**
- ✅ Complete (passed tests/Codex review)
- 🟡 In Progress
- ⬜ Not Started
- Integration = n8n workflow wiring + end-to-end demo

**Codex Review** is a mandatory BMAD gate. Stage cannot advance to Tested until
`openai/gpt-5.4-codex` review returns PASS or PASS WITH WARNINGS.
See `code-review/GATE.md` for process. Reports saved to `code-review/reports/`.

---

## Rules

1. Read `shared/data-model.md` before writing any code in either stage.
2. Stage N is not started until Stage N-1 passes tests on 3 real OMs.
3. Prompts live in files, never hardcoded in src.
4. Python does math. Claude does language.
5. Human review gate after extraction, before scoring. Always.
6. Codex review gate before Tested. No exceptions. See `code-review/GATE.md`.
