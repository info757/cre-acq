# Shared Data Model — CRE Acquisitions Platform
_This schema is the contract between Stage 1 (OM Screener) and Stage 2 (Valuation)._
_Both stages read and write to this structure. Do not change it without updating both._

---

## DealInput (what goes into Stage 1)

```json
{
  "deal_id": "string (uuid)",
  "source": "string (crexi | loopnet | broker-email | manual)",
  "pdf_path": "string (local file path)",
  "submitted_at": "ISO8601 timestamp",
  "submitted_by": "string"
}
```

---

## ExtractedMetrics (Stage 1 output → Stage 2 input)

```json
{
  "deal_id": "string",
  "extraction_timestamp": "ISO8601",
  "property": {
    "type": "string (multifamily | industrial | office | retail | mixed)",
    "market": "string",
    "submarket": "string | null",
    "address": "string | null",
    "vintage": "integer | null",
    "units": "integer | null",
    "total_sf": "number | null"
  },
  "financials": {
    "asking_price": "number | null",
    "price_per_unit": "number | null",
    "price_per_sf": "number | null",
    "noi_trailing": "number | null",
    "noi_proforma": "number | null",
    "cap_rate_trailing": "number | null",
    "cap_rate_proforma": "number | null",
    "occupancy_current": "number | null",
    "occupancy_economic": "number | null",
    "gross_revenue": "number | null",
    "total_expenses": "number | null",
    "expense_ratio": "number | null"
  },
  "debt": {
    "ltv": "number | null",
    "dscr": "number | null",
    "interest_rate": "number | null",
    "maturity_date": "string | null",
    "assumable": "boolean | null"
  },
  "leases": [
    {
      "tenant": "string | null",
      "sf": "number | null",
      "expiration": "string | null",
      "rent_per_sf": "number | null"
    }
  ],
  "extraction_flags": ["string"]
}
```

---

## ScreeningResult (Stage 1 final output)

```json
{
  "deal_id": "string",
  "screened_at": "ISO8601",
  "criteria_used": "string (path to buy-criteria.json)",
  "verdict": "GO | CONDITIONAL | NO-GO",
  "criteria_results": [
    {
      "criterion": "string",
      "value": "any",
      "threshold": "any",
      "result": "PASS | FAIL | FLAG",
      "note": "string | null"
    }
  ],
  "red_flags": [
    {
      "flag": "string",
      "explanation": "string"
    }
  ],
  "narrative": "string",
  "extracted_metrics": "ExtractedMetrics (embedded)"
}
```

---

## ValuationInput (Stage 2 input — extends ScreeningResult)

Stage 2 accepts a ScreeningResult directly. Additional inputs the user
can provide to improve valuation accuracy:

```json
{
  "screening_result": "ScreeningResult (from Stage 1)",
  "valuation_overrides": {
    "market_cap_rate": "number | null",
    "exit_cap_rate": "number | null",
    "hold_period_years": "integer (default 5)",
    "rent_growth_rate": "number (default 0.03)",
    "expense_growth_rate": "number (default 0.02)",
    "vacancy_rate": "number | null",
    "capex_reserve_per_unit": "number | null",
    "debt_terms": {
      "ltv": "number (default 0.70)",
      "interest_rate": "number",
      "amortization_years": "integer (default 30)"
    }
  }
}
```

---

## ValuationResult (Stage 2 output)

```json
{
  "deal_id": "string",
  "valued_at": "ISO8601",
  "direct_cap_value": "number",
  "dcf_value": "number",
  "suggested_offer": "number",
  "suggested_offer_note": "string",
  "returns": {
    "cash_on_cash_yr1": "number",
    "irr": "number",
    "equity_multiple": "number",
    "cap_rate_on_cost": "number"
  },
  "sensitivity": {
    "cap_rate_range": [{"cap_rate": "number", "value": "number"}],
    "rent_growth_range": [{"growth": "number", "irr": "number"}]
  },
  "assumptions": "ValuationInput.valuation_overrides (echoed)",
  "narrative": "string"
}
```

---

## buy-criteria.json (shared config)

```json
{
  "property_types": ["multifamily", "industrial"],
  "markets": [],
  "max_asking_price": null,
  "min_cap_rate_trailing": 0.055,
  "min_occupancy": 0.88,
  "max_ltv": 0.75,
  "min_dscr": 1.20,
  "max_expense_ratio": 0.50,
  "vintage_min": null,
  "vintage_max": null,
  "max_proforma_noi_premium": 0.15
}
```

---

_Any change to this file requires updating both stage-1 and stage-2 code and tests._
