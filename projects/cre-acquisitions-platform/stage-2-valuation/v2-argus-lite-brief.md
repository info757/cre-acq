# V2 Argus-Lite — Lease-Level Modeling

**Status:** Planning. Do not start v2 coding until v1 demo is published.

---

## Scope

V2 is a **separate BMAD track** focused on lease-level modeling. It is not an extension of v1. Do not contaminate v1 with v2 complexity.

**Target:** Office, retail, mixed-use with meaningful commercial concentration. One hold-period model. Explicit rollover assumptions.

---

## Richer Lease Schema (Required Before v2 Coding)

Extend `shared/data-model.md` leases with:

| Field | Type | Purpose |
|-------|------|---------|
| lease_start | date | Lease commencement |
| lease_end | date | Lease expiration |
| base_rent | number | Contractual rent |
| rent_step_schedule | array | Bumps by date or interval |
| market_rent_at_rollover | number | Mark-to-market at expiration |
| ti_per_sf | number | Tenant improvement allowance |
| free_rent_months | integer | Free rent period |
| downtime_months | number | Vacancy between leases |
| leasing_commission_pct | number | LC as % of rent |
| renewal_probability | number | 0-1 |
| tenant_category | string | anchor / inline / etc |

---

## Exact V2 Functionality Required Before Credible Argus-Parity Claim

1. **Lease-level data model** — All fields above
2. **Rollover and renewal logic** — Market rent at expiration, renewal probability, downtime, absorption
3. **Leasing cost logic** — TI, free rent, LC, renewal vs new-tenant cost differences
4. **Annual cash flow engine** — Lease-by-lease schedule, property-level aggregation
5. **Exit and valuation logic** — Reversion, sensitivity tables
6. **Review and explainability** — Assumption review, line-of-sight to value impact
7. **Validation against known cases** — At least 3 real or sanitized lease-heavy test cases, documented tolerance bands
8. **Boundaries** — Define which asset types v2 handles well; do not claim "Argus replacement" until repeatable across real cases

---

## Validation Requirement

Before making any public Argus-matching claim:

- At least 3 real or sanitized lease-heavy test cases
- One simple case expected to match closely
- One mixed-use or office/retail case with meaningful rollover exposure
- Output comparison against manual underwriting or Argus-style benchmark
- Documented tolerance bands for NOI, value, and key cash flow differences
- Public claim remains "matches a targeted slice of Argus lease-level modeling" unless broader evidence exists

---

_Do not start v2 until v1 demo is filmed and published._
