# Permit Silence — Business Plan v1
*Draft: 2026-03-06 | Author: Zoé (with Will Holt)*

---

## Executive Summary

Permit Silence turns publicly available municipal permit records and property data into actionable intelligence for two high-value buyers: contractors who want better-timed leads, and PE firms who need data-driven territory selection for home services roll-ups.

The company launches in Greensboro, NC and expands sequentially across the Triad, Charlotte Metro, and the Triangle — markets where the team has relationships and geographic density justifies dedicated datasets.

**Phase 1 Products:**
- **Trade Sniper Lists** — Monthly address lists ranked by replacement probability, sold to HVAC, roofing, plumbing, and electrical contractors
- **PE Territory Health Reports** — Zip-code and county-level replacement demand analysis for PE firms evaluating home services acquisitions

---

## The Core Insight

Municipal permit records document when major home systems were replaced. When a system *hasn't* been replaced in 15–25 years, the permit record is silent. That silence is the signal.

Combined with county assessor data (home age, square footage, owner type) and property sales history, permit silence creates a probabilistic picture of what systems are near end-of-life at any given address — without requiring access to the home itself.

**The "silence" signal works even with partial permit history.** A 1985 home with no HVAC permit ever filed is a high-probability replacement candidate regardless of whether you have every year on record. The age gap between home construction and the absence of system-level permits is itself the evidence.

---

## Problem & Solution

### For Contractors
**Problem:** HVAC, roofing, and plumbing companies spend heavily on generic lead generation (Angi, HomeAdvisor, Google ads) that reaches homeowners who aren't ready to buy. Conversion is low, cost per acquisition is high, and timing is pure luck.

**Solution:** Trade Sniper Lists surface addresses where replacement is statistically likely within the next 6–18 months. Contractors market to these addresses with better timing, higher conversion, and lower CPL.

### For PE / M&A
**Problem:** PE firms building home services roll-ups (HVAC, roofing, plumbing) choose territories based on population density and revenue — but not on whether the underlying housing stock actually needs service. They overpay for territories with aging installed bases that are post-replacement cycle and undervalue territories with a wave of replacements coming.

**Solution:** PE Territory Health Reports quantify replacement demand by zip code and county — ranking territories by "replacement headroom" so PE can price acquisitions with an evidence base, not instinct.

---

## Products

### 1. Trade Sniper Lists

**What it is:** A monthly refreshed CSV/dashboard of addresses in a contractor's service area, ranked by replacement probability for a specific system (HVAC, roof, water heater, plumbing).

**How it works:**
- Ingest permit history + county assessor data for every parcel in market
- Build system age inference model: known installs from permits + estimated installs from home age for silent properties
- Score each address by replacement probability over 6/12/24 months
- Filter by system type (HVAC, roof, etc.), geography (zip, radius), and property type
- Deliver monthly as CSV or simple dashboard

**Customer:** Local and regional HVAC, roofing, plumbing, electrical contractors. Initially single-trade (HVAC first — highest ticket, clearest permit trail).

**Pricing:**
- Beta (first 5 customers): $199/month per market per trade
- Standard: $399/month per market per trade
- Multi-trade discount: 20% for second trade add-on
- Annual: 2 months free

**Unit economics target:** 20 beta customers at $199 = $3,980 MRR at launch. 50 paying customers at $399 = $19,950 MRR at steady state in Greensboro.

---

### 2. PE Territory Health Report

**What it is:** A one-time or annual research report scoring zip codes and counties in a target market by replacement demand for a specific trade (HVAC, roofing, etc.). Delivered as a PDF + Excel data file.

**How it works:**
- Aggregate address-level scores to zip and county level
- Compute: estimated units needing replacement in next 24 months, expected spend per unit, density vs. competition ratio
- Layer in: housing stock age distribution, home value range, owner-occupancy rate
- Output: ranked territory heat map + narrative analysis

**Customer:** PE firms, family offices, and M&A advisors evaluating home services acquisitions in the Southeast.

**Pricing:**
- Per report (single market, single trade): $7,500–$15,000
- Annual subscription (ongoing monitoring across portfolio markets): $30,000–$60,000/year
- Custom scope (multi-trade, multi-market): quoted per engagement

**Volume reality:** 1–2 reports/month in early stage = $10,000–$30,000/month. This is a high-value, low-volume product. Prioritize quality and referrals over volume.

---

## Data Strategy

### Sources (Priority Order)

1. **Municipal permit databases** — Direct pulls from city/county permit portals. NC municipalities increasingly have open data portals or APIs (Accela Civic Platform is common). Guilford County / City of Greensboro is the starting point.

2. **Commercial permit data APIs** — Betsy and Katerina are evaluating vendors (BuildZoom, ATTOM, CoreLogic, DataTree / First American). Goal: 20+ years of permit history. Challenge: coverage varies by municipality; older records may be paper-only.

3. **County assessor / parcel data** — Property age, square footage, owner name, assessed value. Generally free or low-cost public records. NC has county-level GIS portals. This is the baseline layer.

4. **Property sales data** — Sale dates and prices from county deed records. New sales = potential system upgrades; long-tenured owners = higher silence risk.

5. **Optional enrichment (Phase 2):** Home age distribution models, climate zone data (HVAC wear rates), neighborhood income proxies.

### 20-Year Coverage Strategy

- Start with whatever digital records exist (typically 10–15 years for most NC municipalities)
- Use home age as the backstop: if a home was built in 2000 and we only have permits back to 2010, the pre-2010 silence is still meaningful
- Flag data confidence level in output (HIGH = permit record verified, MEDIUM = inferred from age, LOW = insufficient data)
- As coverage improves, rescore and refresh — this is a moat that strengthens over time

### Data Storage & Refresh

- PostgreSQL with PostGIS for spatial queries
- Monthly refresh cycle for active markets
- Greensboro pilot: target 100,000 parcels as initial dataset

---

## Go-to-Market

### Phase 1: Greensboro (Months 1–4)

**Trade Sniper — Launch Sequence:**
1. Identify top 20 HVAC contractors in Greensboro by permit volume (permit data tells you who's active)
2. Outreach: Will does direct outreach — phone and in-person. No cold email campaigns at this stage.
3. Offer: Free 30-day trial list, limited to their service zip codes
4. Target: 5 beta customers by end of Month 2
5. After beta: convert to $199/month; get 3 case studies (before/after on conversion rate)
6. Case studies unlock referral channel — contractors talk to each other

**PE Territory — Launch Sequence:**
1. Will maps PE firms actively doing HVAC/roofing/plumbing roll-ups in the Southeast (LinkedIn, PitchBook, press coverage)
2. Build a list of 50 target firms and advisors
3. Reach out with a "complimentary snapshot" — a 1-page preview of the Greensboro HVAC replacement map
4. First paid engagement: $5,000 pilot report, positioned as a proof-of-concept
5. Referral target: M&A advisors and business brokers who work with PE on home services deals

### Phase 2: Triad (Months 4–8)
Add Winston-Salem and High Point to the dataset. Sell Triad-wide Trade Sniper lists; upgrade Greensboro customers to Triad.

### Phase 3: Charlotte Metro (Months 8–14)
Larger market, more contractors, more PE activity. Repeat playbook with case studies from Triad.

### Phase 4: Triangle (Months 14–20)
Raleigh-Durham-Chapel Hill. Tech-heavy market with strong PE presence. Also positions the company for a Series A narrative.

---

## Team

| Name | Role | Focus |
|------|------|-------|
| Will | CEO / GTM | Sales, BD, PE relationships, fundraising |
| Betsy | Co-founder / Engineering | Data pipeline, product build |
| Katerina | Co-founder / Engineering | Data pipeline, product build |

---

## Milestones

| Month | Milestone |
|-------|-----------|
| 1 | Greensboro data pipeline live (parcels + permits ingested) |
| 2 | First Trade Sniper beta list delivered |
| 3 | 5 beta customers; first PE prospect outreach |
| 4 | 3 paying Trade Sniper customers; first PE report in progress |
| 5 | First PE report delivered ($5–10K) |
| 6 | $15K+ MRR; expand to Triad |
| 9 | 20+ Trade Sniper customers; 3+ PE reports completed |
| 12 | Charlotte data live; $35–50K MRR total |
| 18 | Triangle data live; considering Series A or strategic raise |

---

## Revenue Projections (Conservative)

| Month | Trade Sniper MRR | PE Reports (one-time) | Total Monthly |
|-------|-----------------|----------------------|---------------|
| 3 | $1,000 | — | $1,000 |
| 6 | $8,000 | $10,000 | $18,000 |
| 9 | $18,000 | $15,000 | $33,000 |
| 12 | $30,000 | $20,000 | $50,000 |
| 18 | $60,000 | $30,000 | $90,000 |

*PE reports treated as one-time revenue; recurring PE subscriptions would change this profile significantly.*

---

## Key Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Can't get 20 years of permit history | Age-based inference covers the gap; flag confidence level in output |
| Data quality varies by municipality | Start with Greensboro where we can verify; build quality score into product |
| Contractors don't convert from trial | In-person sales + case studies; start with contractors Will knows personally |
| PE sales cycle is long | PE is upside, not survival; Trade Sniper covers operating costs |
| Competitor emerges with similar product | Speed + NC market depth is the moat; be the best in the Southeast before expanding |

---

## Next Steps

- [ ] Betsy + Katerina: finalize data source evaluation (API coverage, cost, 20-year depth)
- [ ] Will: map top 20 HVAC contractors in Greensboro by permit volume
- [ ] Will: identify 10 target PE firms doing home services roll-ups in the Southeast
- [ ] Team: set up Greensboro data pipeline (target: live in 30 days)
- [ ] Will: schedule first contractor conversations (beta offer)

---

*Version 1.0 — to be refined as data sourcing picture clarifies*
