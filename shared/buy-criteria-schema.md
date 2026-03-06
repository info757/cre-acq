# buy-criteria.json — Schema Reference

Human-editable screening criteria. Edit `shared/buy-criteria.json` directly; no code changes needed. The next pipeline run uses the updated values.

## Sections

All sections are optional. Missing sections or nested fields default to "no filter."

| Section | Purpose |
|---------|---------|
| `property_types` | Whitelist of allowed property types |
| `markets` | Geographic filter (empty = all markets) |
| `debt` | Debt thresholds |
| `income` | Income/returns thresholds |
| `expenses` | Expense thresholds |

## Supported Fields

### property_types
- **Type:** `string[]`
- **No filter:** `[]` or missing → all property types pass
- **Example:** `["multifamily", "industrial", "mixed_use"]`

### markets
- **Type:** `string[]`
- **No filter:** `[]` or missing → all markets pass
- **Match:** Exact or city substring (e.g. `"Phoenix"` matches `property.market` "Phoenix, AZ")
- **Example:** `["Charlotte", "Phoenix"]`

### max_asking_price
- **Type:** `number | null`
- **No filter:** `null` → no price cap
- **Example:** `50000000`

### debt
- **hard_min_dscr:** `number | null` — Hard NO-GO if DSCR below this. `null` or missing = no filter.
- **min_dscr:** `number | null` — FLAG if below. `null` or missing = no filter.
- **max_ltv:** `number | null` — FLAG if above. `null` or missing = no filter.

### income
- **min_cap_rate_trailing:** `number | null` — Min cap rate. `null` or missing = no filter.
- **min_occupancy:** `number | null` — Min occupancy. `null` or missing = no filter.
- **max_proforma_noi_premium:** `number | null` — Flag if pro-forma NOI > this % above trailing. `null` or missing = no filter.

### expenses
- **max_expense_ratio:** `number | null` — Max expense ratio. `null` or missing = no filter.

### vintage_min, vintage_max
- **Type:** `number | null`
- **No filter:** `null` or missing → no vintage filter

## Version Control

`shared/buy-criteria.json` lives in the repo. Edit, commit, and push. No deploy required.
