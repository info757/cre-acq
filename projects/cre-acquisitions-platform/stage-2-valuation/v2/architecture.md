# Architecture — Stage 2 V2: Argus-Lite Lease-Level Modeling

**BMAD Phase 3: Solutioning**
_Status: Planning — extends v1 architecture_

---

## Core Principles (Non-Negotiable)

1. **Python does math. Claude does language.** No LLM arithmetic, ever.
2. **Prompts are files.** Never hardcoded in src.
3. **Human review gate before model runs.** Assumptions displayed and confirmed.
4. **V2 is separate from v1.** Do not contaminate v1 with v2 complexity.
5. **Stage 2 v2 runs after Stage 1.** Input is ScreeningResult with LeaseV2[] leases.

---

## Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| Input | ScreeningResult + LeaseV2[] | Deal metrics, lease-level data |
| Lease schema | LeaseV2 (shared/data-model.md) | lease_start, lease_end, base_rent, rent_step_schedule, market_rent_at_rollover, ti_per_sf, free_rent_months, downtime_months, leasing_commission_pct, renewal_probability, tenant_category |
| Lease schedule | Python | Lease-by-lease schedule builder |
| Rollover | Python | Renewal probability, downtime, market rent at rollover |
| Leasing costs | Python | TI, free rent, LC (renewal vs new tenant) |
| Cash flow | Python | Annual cash flows from lease schedule |
| Exit | Python | Reversion, sensitivity tables |
| Narrative | Claude claude-sonnet-4-6 | Plain-English value summary and lease drivers |
| Delivery | Telegram + JSON | Same pattern as Stage 1 |
| Storage | Local JSON files | output/ directory, ValuationResultV2 schema |

---

## Pipeline: V2 Stages

```
[INPUT]
  ScreeningResult (from Stage 1 output/DEAL_ID.json)
  + ValuationInput with LeaseV2[] leases
  + valuation_overrides (optional)
  + buy-criteria.json (defaults)
      ↓
[STAGE 1] Normalize Input (v2)
  Python: normalize_input_v2.py
  Merge ScreeningResult + LeaseV2[] + overrides + buy-criteria defaults
  Output: valuation_input_v2.json (full assumptions including lease-level)
      ↓
[STAGE 2] Human Review Gate
  Display assumptions including lease summary (rollover, renewal prob, costs).
  Wait for confirm.
  Output: confirmed valuation_input_v2.json
      ↓
[STAGE 3] Lease Schedule
  Python: lease_schedule.py
  Build lease-by-lease schedule across hold period
  Output: lease_schedule.json
      ↓
[STAGE 4] Rollover Engine
  Python: rollover_engine.py
  Apply renewal probability, downtime, market rent at rollover
  Output: rollover_scenarios (renewal vs new tenant paths)
      ↓
[STAGE 5] Leasing Costs
  Python: leasing_costs.py
  TI, free rent, LC (renewal vs new tenant)
  Output: leasing_cost_schedule.json
      ↓
[STAGE 6] Cash Flow Engine
  Python: cash_flow_engine.py
  Aggregate lease-level to property-level annual cash flows
  Output: annual_cash_flows.json
      ↓
[STAGE 7] Exit Valuation
  Python: exit_valuation.py
  Reversion, sensitivity tables, IRR, equity multiple
  Output: dcf_value, returns, sensitivity
      ↓
[STAGE 8] Flags and Output
  Python: flags_v2.py — sanity checks
  Python: format_valuation_output_v2.py — assemble + Claude narrative
  Output: ValuationResultV2 JSON + Telegram message
```

---

## Python Scripts

### `src/normalize_input_v2.py`
```
Input:  --screening-result <path>  --overrides <path or JSON>  --criteria <path>
Action: Load ScreeningResult with LeaseV2[], merge valuation_overrides, fill defaults
Output: valuation_input_v2.json to stdout or --out
Test:   tests/test_normalize_input_v2.py
```

### `src/lease_schedule.py`
```
Input:  --valuation-input-v2 <path>
Action: Build lease-by-lease schedule across hold period (rent steps, free rent)
Output: lease_schedule.json
Test:   tests/test_lease_schedule.py
```

### `src/rollover_engine.py`
```
Input:  --lease-schedule <path>  --valuation-input-v2 <path>
Action: Apply renewal probability, downtime, market rent at rollover
Output: rollover_scenarios (renewal vs new tenant paths)
Test:   tests/test_rollover_engine.py
```

### `src/leasing_costs.py`
```
Input:  --lease-schedule <path>  --rollover-scenarios <path>
Action: Calculate TI, free rent, LC (renewal vs new tenant)
Output: leasing_cost_schedule.json
Test:   tests/test_leasing_costs.py
```

### `src/cash_flow_engine.py`
```
Input:  --lease-schedule <path>  --leasing-costs <path>
Action: Aggregate to property-level annual cash flows
Output: annual_cash_flows.json
Test:   tests/test_cash_flow_engine.py
```

### `src/exit_valuation.py`
```
Input:  --annual-cash-flows <path>  --valuation-input-v2 <path>
Action: Reversion, sensitivity tables, IRR, equity multiple
Output: dcf_value, returns, sensitivity
Test:   tests/test_exit_valuation.py
```

### `src/flags_v2.py`
```
Input:  --valuation-input-v2 <path>  --valuation-result-v2 <path>
Action: Check expense ratio, rent growth, cap spread, lease concentration
Output: list of flag objects (flag, explanation)
Test:   tests/test_flags_v2.py
```

### `src/format_valuation_output_v2.py`
```
Input:  --valuation-input-v2 <path>  --valuation-result-v2 <path>  --prompt <path>  --out <path>
Action: Assemble ValuationResultV2, call Claude for narrative (lease drivers), write JSON
Output: ValuationResultV2 JSON + formatted message to stdout
Test:   tests/test_format_valuation_output_v2.py
```

### `src/run_valuation_v2.py`
```
Input:  --screening-result <path>  [--overrides <path>]  [--skip-gate]
Action: Orchestrate normalize_v2 -> [gate] -> lease_schedule -> rollover -> leasing_costs -> cash_flow -> exit_valuation -> flags_v2 -> format_output_v2
Output: output/DEAL_ID_valuation_v2.json
Test:   tests/test_run_valuation_v2.py
```

---

## File Layout

```
stage-2-valuation/v2/
  architecture.md          ← THIS FILE
  prd.md
  src/
    normalize_input_v2.py
    lease_schedule.py
    rollover_engine.py
    leasing_costs.py
    cash_flow_engine.py
    exit_valuation.py
    flags_v2.py
    format_valuation_output_v2.py
    run_valuation_v2.py
  prompts/
    valuation-narrator-v2.md
  tests/
    test_normalize_input_v2.py
    test_lease_schedule.py
    test_rollover_engine.py
    test_leasing_costs.py
    test_cash_flow_engine.py
    test_exit_valuation.py
    test_flags_v2.py
    test_format_valuation_output_v2.py
    test_run_valuation_v2.py
    sample/
      lease-heavy-case-1.json
      lease-heavy-case-2.json
      lease-heavy-case-3.json
  output/                   ← ValuationResultV2 JSONs
  requirements.txt
```

---

## Data Flow

- **ValuationInputV2** = ScreeningResult + LeaseV2[] + valuation_overrides
- **LeaseV2** = extended lease schema (see shared/data-model.md)
- **LeaseSchedule** = lease-by-lease timeline across hold period
- **AnnualCashFlows** = property-level NOI, revenue, expenses by year
- **ValuationResultV2** = direct_cap_value, dcf_value (lease-level), suggested_offer, returns, sensitivity, assumptions, lease_drivers_narrative

---

## Integration with Stage 1 and V1

- Stage 1 writes output/DEAL_ID.json (ScreeningResult)
- V1 leases (tenant, sf, expiration, rent_per_sf) can be upgraded to LeaseV2 with defaults for missing fields
- V2 pipeline is separate; v1 run_valuation.py unchanged
- pipeline/run-full.py can optionally chain: Stage 1 -> Stage 2 v2 (when lease data available)

---

## Boundaries

- **Asset types:** Office, retail, mixed-use with meaningful commercial concentration
- **Scope disclaimer:** "Matches a targeted slice of Argus lease-level modeling" until broader validation
- **No Argus replacement claim** until 3+ real cases with documented tolerance bands

---

_Updated 2026-03-09 for v2 BMAD planning._
