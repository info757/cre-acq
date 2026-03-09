# Architecture — Stage 2: Valuation Agent
**BMAD Phase 3: Solutioning**
_Status: APPROVED for v1 — direct cap + DCF only_

---

## Core Principles (Non-Negotiable)

1. **Python does math. Claude does language.** No LLM arithmetic, ever.
2. **Prompts are files.** Never hardcoded in src.
3. **Human review gate before model runs.** Assumptions displayed and confirmed.
4. **No lease-level modeling in v1.** TI, free rent, downtime, commissions, renewal probability reserved for v2.
5. **Stage 2 runs after Stage 1.** Input is ScreeningResult. No standalone valuation without screening.

---

## Stack

| Layer | Tool | Purpose |
|---|---|---|
| Input | Stage 1 output (ScreeningResult) | Deal metrics, verdict, red flags |
| Overrides | JSON / buy-criteria.json | Cap rates, hold period, growth, debt terms |
| Direct cap | Python | NOI / cap_rate = value |
| DCF | Python | 10-year cash flows, reversion, IRR, equity multiple |
| Flags | Python | Expense ratio, rent growth, cap spread vs comps |
| Narrative | Claude claude-sonnet-4-6 | Plain-English value summary and risks |
| Delivery | Telegram + JSON | Same pattern as Stage 1 |
| Storage | Local JSON files | output/ directory, ValuationResult schema |

---

## Pipeline: 5 Stages

```
[INPUT]
  ScreeningResult (from Stage 1 output/DEAL_ID.json)
  + valuation_overrides (optional)
  + buy-criteria.json (defaults)
      ↓
[STAGE 1] Normalize Input
  Python: normalize_input.py
  Merge ScreeningResult + overrides + buy-criteria defaults
  Output: valuation_input.json (full assumptions)
      ↓
[STAGE 2] Human Review Gate
  Display assumptions. Wait for confirm.
  Output: confirmed valuation_input.json
      ↓
[STAGE 3] Direct Cap
  Python: direct_cap.py
  NOI / market_cap_rate = value
  Output: direct_cap_value
      ↓
[STAGE 4] DCF and Returns
  Python: dcf.py
  10-year NOI projection, reversion, PV, IRR, equity multiple
  Output: dcf_value, returns, sensitivity
      ↓
[STAGE 5] Flags and Output
  Python: flags.py — sanity checks
  Python: format_valuation_output.py — assemble + Claude narrative
  Output: ValuationResult JSON + Telegram message
```

---

## Python Scripts

### `src/normalize_input.py`
```
Input:  --screening-result <path>  --overrides <path or JSON>  --criteria <path>
Action: Load ScreeningResult, merge valuation_overrides, fill defaults from buy-criteria
Output: valuation_input.json to stdout or --out
Test:   tests/test_normalize_input.py
```

### `src/direct_cap.py`
```
Input:  --noi <number>  --cap-rate <number>
Action: value = noi / cap_rate
Output: JSON with direct_cap_value
Test:   tests/test_direct_cap.py
```

### `src/dcf.py`
```
Input:  --noi <number>  --hold-years <int>  --rent-growth <number>  --expense-growth <number>
        --exit-cap <number>  --discount-rate <number>  [--debt-terms JSON]
Action: Project NOI, compute reversion, PV, IRR, equity multiple
Output: JSON with dcf_value, returns, sensitivity
Test:   tests/test_dcf.py
```

### `src/flags.py`
```
Input:  --valuation-input <path>  --valuation-result <path>
Action: Check expense ratio, rent growth, cap spread vs norms
Output: list of flag objects (flag, explanation)
Test:   tests/test_flags.py
```

### `src/format_valuation_output.py`
```
Input:  --valuation-input <path>  --direct-cap <number>  --dcf <number>  --returns <path>
        --flags <path>  --prompt <path>  --out <path>
Action: Assemble ValuationResult, call Claude for narrative, write JSON
Output: ValuationResult JSON + formatted message to stdout
Test:   tests/test_format_valuation_output.py
```

### `src/run_valuation.py`
```
Input:  --screening-result <path>  [--overrides <path>]  [--skip-gate]
Action: Orchestrate normalize -> [gate] -> direct_cap -> dcf -> flags -> format_output
Output: output/DEAL_ID_valuation.json
Test:   tests/test_run_valuation.py
```

---

## File Layout

```
stage-2-valuation/
  architecture.md          ← THIS FILE
  project-brief.md
  prd.md
  src/
    normalize_input.py
    direct_cap.py
    dcf.py
    flags.py
    format_valuation_output.py
    run_valuation.py
  prompts/
    valuation-narrator.md
  tests/
    test_normalize_input.py
    test_direct_cap.py
    test_dcf.py
    test_flags.py
    test_format_valuation_output.py
    test_run_valuation.py
    sample/
      mill-one-screening-result.json   ← hero deal input
  output/                   ← ValuationResult JSONs
  requirements.txt
```

---

## Data Flow

- **ValuationInput** = ScreeningResult + valuation_overrides (from shared/data-model.md)
- **ValuationResult** = direct_cap_value, dcf_value, suggested_offer, returns, sensitivity, assumptions, narrative
- **Defaults** from buy-criteria.json: returns.hold_period_years, returns.discount_rate, returns.rent_growth_pct, returns.exit_cap_rate

---

## Integration with Stage 1

- Stage 1 writes output/DEAL_ID.json (ScreeningResult)
- Stage 2 reads that file as --screening-result
- pipeline/run-full.py chains: Stage 1 (deal folder) -> Stage 2 (screening result path)

---

_Updated 2026-03-09 for v1 demo scope._
