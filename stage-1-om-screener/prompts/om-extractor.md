TASK: Extract structured CRE financial data from the following Offering Memorandum text.

OUTPUT FORMAT: Return ONLY valid JSON matching this exact schema. No explanation. No markdown. No code fences.
Do not add fields not in the schema. Use null for any field not found in the document.
Do not calculate or infer values — extract only what is explicitly stated in the document.

SCHEMA:
{
  "property": {
    "type": "<multifamily | industrial | office | retail | mixed | null>",
    "market": "<city, state string | null>",
    "submarket": "<submarket name | null>",
    "address": "<full address | null>",
    "vintage": "<integer year built | null>",
    "units": "<integer unit count | null>",
    "total_sf": "<number square footage | null>"
  },
  "financials": {
    "asking_price": "<number | null>",
    "price_per_unit": "<number | null>",
    "price_per_sf": "<number | null>",
    "noi_trailing": "<number, trailing/actual 12-month NOI | null>",
    "noi_proforma": "<number, projected/pro-forma NOI | null>",
    "cap_rate_trailing": "<decimal e.g. 0.048 for 4.8% | null>",
    "cap_rate_proforma": "<decimal | null>",
    "occupancy_current": "<decimal e.g. 0.91 for 91% | null>",
    "occupancy_economic": "<decimal | null>",
    "gross_revenue": "<number | null>",
    "total_expenses": "<number | null>",
    "expense_ratio": "<decimal | null>"
  },
  "debt": {
    "ltv": "<decimal e.g. 0.75 for 75% | null>",
    "dscr": "<number | null>",
    "interest_rate": "<decimal | null>",
    "maturity_date": "<ISO8601 date string | null>",
    "assumable": "<true | false | null>"
  },
  "leases": [
    {
      "tenant": "<string | null>",
      "sf": "<number | null>",
      "expiration": "<ISO8601 date string | null>",
      "rent_per_sf": "<number | null>"
    }
  ],
  "extraction_flags": ["<note about ambiguity or missing data>"]
}

RULES:
- If you see both trailing and pro-forma values for NOI or cap rate, extract BOTH.
- If a value is ambiguous (unclear if trailing or pro-forma), set the field to null and add a note to extraction_flags, e.g. "noi_trailing: ambiguous — see page 12".
- Percentages: convert to decimals (48% → 0.48).
- Do not hallucinate numbers. null is always correct when data is absent or unclear.
- leases array: include only if lease-level data is present. Empty array [] if not found.
- extraction_flags: list any data quality issues, ambiguities, or missing expected fields.

OM TEXT:
{{raw_text}}
