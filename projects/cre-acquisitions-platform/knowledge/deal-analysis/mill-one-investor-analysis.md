# Mill One — Investor Analysis
_Source: Will Holt, March 2026. This is real deal analysis on a real OM._
_Archived here as Layer 2/3 knowledge — feeds screening rules and buy-criteria._

---

## The Deal

**Property:** Mill One, LLC — mixed-use multifamily + commercial
**Location:** Greensboro, NC area
**Type:** 76 residential units + 12 commercial tenants
**Asking price:** ~$38,900,000 (implied by OM at 5.1% cap)
**OM date:** ~2024

---

## The Headline Discrepancy: Property Taxes

**This is the single most important finding from this analysis.**

The OM financials show property taxes of **$24,643/year**.
For a $38.9M commercial asset in North Carolina, the correct figure is approximately:

- Tax assessment: 60% of purchase price = $23,340,000
- Tax rate: 1.2775% (Guilford County)
- **Correct annual taxes: ~$298,169/year**

**Gap: $273,526/year understated.**

At a 5.1% cap rate, this alone reduces value by: $273,526 / 0.051 = **~$5.36M**

This is not unusual for a recently completed or recently sold asset — the assessment
hasn't caught up to market value yet. But any buyer must model the correct taxes.
The OM number is essentially meaningless for underwriting purposes.

**Rule encoded:** Flag any commercial property where stated property taxes are below
0.5% of asking price annually. That threshold would catch this ($38.9M × 0.5% = $194,500
— still above $24,643 by 8x).

---

## Valuation: Will's DCF

Using 3% rent growth, 7% discount rate, 10-year hold:

| Metric | Value |
|---|---|
| Purchase price tested | $38,900,000 |
| **Will's DCF value (PV @ 7%)** | **$35,065,501** |
| Gap to asking | ~$3,834,499 (~10% overpriced) |
| Year 11 NOI (exit) | $2,664,733 |
| Exit cap rate | 6.65% |
| Exit value (gross) | $40,071,173 |
| Net reversion proceeds | $39,670,461 |
| Unlevered IRR at asking price | 5.62% |
| Unlevered IRR at DCF value | 7.00% |

**Bottom line:** At asking, the unlevered IRR is 5.62%. At Will's fair value ($35M),
the unlevered IRR is exactly 7% (the hurdle). Asking is ~10% rich.

---

## Two Leverage Scenarios

### Scenario 1: 59% LTV — Assumable Current Debt

| Metric | Value |
|---|---|
| Loan amount | $23,000,000 |
| Interest rate | 4.33% (assumable) |
| Amortization | 30 years |
| Annual debt service | $1,370,711 |
| Equity required | $15,900,000 |
| **Levered IRR** | **7.18%** |
| **DSCR Year 1** | **1.447** |
| Equity multiple | 1.83x |
| Year 1 cash-on-cash | 3.63% |

**Verdict:** Solid. The assumable debt at 4.33% is the deal's biggest asset.
DSCR is comfortable. Levered IRR beats hurdle rate by 18bps.

### Scenario 2: 70% LTV — Adding $4.23M at ~12% (mezzanine/debt fund)

| Metric | Value |
|---|---|
| Total loan amount | $27,230,000 |
| Blended rate | ~5.52% |
| Annual debt service | $1,859,410 |
| **Levered IRR** | **5.89%** |
| **DSCR Year 1** | **~1.07** |

**Verdict:** The additional leverage cost of capital (12% for last-dollar position)
eats the NOI. DSCR at 1.07 is dangerous — one bad month triggers covenant risk.
IRR drops below hurdle rate. Anything past 70% LTV "blows up the proforma."

**Rule encoded:** Max acceptable LTV = 70%. DSCR minimum = 1.20.
DSCR <1.10 = hard NO-GO.

---

## Commercial Space: 41% of Gross Rent

Mill One is ~41% commercial by gross rent. This creates both risk and opportunity
that a standard multifamily screener will miss.

**Seller's pitch:** Model the leases in Argus, add rent bumps + renewal at market rent.
Commercial rents at market could push Year 11 NOI closer to $3M, making asking price
more defensible.

**Buyer's concern:**
- All commercial leases turn on a 10-year hold
- TI, free rent, downtime, leasing commissions are real costs
- On a $38.9M deal, a 6-month dark period on one anchor tenant hits hard
- Core buyers see this as risk; Core Plus / Value Add buyers see it as upside

**Key Argus inputs needed for accurate commercial modeling:**
1. Rent bumps per lease
2. Market rent at renewal
3. Tenant Improvement allowances (TI)
4. Free rent periods
5. Downtime between leases
6. Leasing commissions
7. Renewal probability per tenant

**Rule encoded:** Commercial concentration >40% triggers a warning to flag for
lease-level modeling. This is not a hard stop, but screener output must note it
prominently — especially for hold periods ≥7 years.

---

## Underwriting Assumptions (Will's Model)

These are the inputs Will actually used. These become our Layer 2 defaults.

| Input | Value | Notes |
|---|---|---|
| Rent growth | 3.0% / year | Conservative, straight-line |
| Discount rate (hurdle) | 7.0% | Unlevered IRR hurdle |
| Exit cap rate | 6.65% | ~50bps above going-in if bought at asking |
| Tax assessment % | 60% of purchase price | North Carolina norm post-sale |
| Tax rate | 1.2775% | Guilford County |
| Property mgmt fee | 2.5% of EGR | |
| CapEx reserve | $0.20/SF | |
| Other expenses (base) | $199,548 | |
| Expense inflation | 3% / year | |
| Hold period | 10 years | |
| Selling costs | 1% of gross price | |
| Vacancy & credit loss | Per market (0% modeled here — risk) | |

---

## Red Flags Identified (For Screening Rules)

| Flag | What triggered it | Threshold |
|---|---|---|
| **Property tax understatement** | $24,643 stated vs. ~$298,169 correct | Taxes < 0.5% of asking price |
| **Commercial concentration** | 41% of gross rent from commercial | > 40% → warn, model separately |
| **All commercial leases turn** | 10-year hold, all leases expire | All leases <10 years remaining → warn |
| **DSCR cliff at higher LTV** | 1.447 at 59% → 1.07 at 70% | DSCR <1.20 = warning; <1.10 = NO-GO |
| **Price vs. DCF gap** | Asking ~10% above DCF value | >10% above → flag for negotiation note |

---

## Buyer Profile

Will's view: **Best fit for a high-net-worth individual with cash** who can take the
assumable 4.33% debt without needing additional leverage. The deal makes sense at
59% LTV with a patient hold. It does not make sense for a fund that needs to lever up.

This maps to a screening dimension we should add: "Does this deal require additional
leverage to pencil?" If yes, flag it.

---

## Files

- `Mill_One_10yr_proforma.xlsx` — 10-year DCF model, PV calculation
- `Mill_One_proforma_59pct_LTV.xlsx` — Full pro forma, 59% LTV (assumable debt)
- `Mill_One_proforma_70pct_LTV.xlsx` — Full pro forma, 70% LTV (added mezzanine)

---

_Written by Zoé from Will's analysis — 2026-03-05_
_This document is Layer 2 knowledge: it encodes domain expertise into the screening engine._
