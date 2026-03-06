# Product Requirements Document — CRE OM Screener
**BMAD Phase 2: Planning**
_Status: APPROVED — updated 2026-03-05 to add US-01b (Excel ingestion)_

---

## Overview

User stories and acceptance criteria for the MVP OM Screener. Each story has a
clear "done" definition. Nothing moves to the Architecture phase until all stories
are agreed on here.

---

## Epic 1: Ingestion

### US-01 — Drop a deal folder and get all inputs discovered
**As an** acquisitions professional,
**I want to** point the system at a folder of deal files,
**so that** it figures out what's there and routes each file correctly.

**Acceptance Criteria:**
- [x] System scans a folder and identifies all .pdf and .xlsx/.xls files
- [x] Returns has_pdf, pdf_path, has_excel, excel_paths as JSON
- [x] If multiple PDFs found, selects the largest (most likely the OM)
- [x] Exits with error if folder is empty or contains no supported files
- [x] Neither PDF nor Excel is required — any combination is valid
- [ ] Tested on 5 real deal folders before Stage 2 is built

### US-01a — Drop a PDF and get raw text back
**As an** acquisitions professional,
**I want to** provide an OM PDF,
**so that** the system can process its text content.

**Acceptance Criteria:**
- [x] Extracts readable text from a clean (text-layer) PDF
- [x] Detects low-density pages (image-embedded financials)
- [x] Falls back to targeted OCR (Tesseract) on low-density pages only
- [x] Falls back to full OCR for scanned documents (avg <100 chars/page)
- [x] Returns error if file not found or not a valid PDF
- [x] Page-level metadata written alongside text (char counts, OCR flags)
- [ ] Tested on 5 real OMs including at least 1 scanned PDF before Stage 2 is built

### US-01b — Ingest Excel files and extract structured metrics
**As an** acquisitions professional,
**I want** the system to read any Excel files provided with an OM,
**so that** financial data from rent rolls, operating statements, and loan files
is used directly rather than extracted by Claude from PDFs.

**Acceptance Criteria:**
- [x] System detects Excel file type from filename keywords and sheet names
      (financials / rent_roll / commercial_rent_roll / loan_info)
- [x] Extracts partial ExtractedMetrics JSON from each recognized file type
- [x] All numeric extraction uses Decimal — never float
- [x] Excel values take priority over Claude-extracted values at merge step
- [x] Unrecognized files are skipped with a warning, not a failure
- [x] Extraction flags logged per field (source file, any anomalies)
- [ ] Tested on 5 real deal packages before Stage 2 is built
- [ ] _Note: PRD updated 2026-03-05 — Excel ingestion added after first real deal
      (Mill One) revealed standard broker package includes rent rolls + financials_

---

## Epic 2: Structured Data Extraction

### US-02 — Extract key financial metrics from the OM
**As an** acquisitions professional,
**I want** the agent to pull key metrics from the OM,
**so that** I don't have to read the full document to find the numbers.

**Acceptance Criteria:**
- [ ] Extracts the following fields (null if not found, never hallucinated):
  - Property type
  - Market / submarket
  - Asking price
  - Price per unit (multifamily) or price per SF (industrial)
  - NOI — trailing 12 months AND pro-forma (both if present)
  - Cap rate — trailing AND pro-forma (both if present)
  - Occupancy rate — current AND economic (both if present)
  - Expense ratio (total expenses / gross revenue)
  - Debt terms: LTV, DSCR, interest rate, maturity date (if disclosed)
  - Vintage (year built)
  - Number of units (multifamily) or total SF (industrial)
  - Key lease info: largest tenants, lease expiration dates if present
- [ ] Output is structured JSON matching the data-model schema
- [ ] If a field is ambiguous (e.g., unclear if NOI is trailing or pro-forma),
  agent flags it for human review rather than guessing
- [ ] Tested on 5 real OMs before Stage 3 is built

### US-03 — Human review gate before scoring
**As an** acquisitions professional,
**I want to** see the extracted metrics before scoring fires,
**so that** I can catch any extraction errors before they affect the verdict.

**Acceptance Criteria:**
- [ ] After extraction, system displays the metrics table and pauses
- [ ] User can confirm (proceed to scoring) or flag any incorrect fields
- [ ] If user flags a field, they can correct it inline before scoring
- [ ] Corrected values are used in scoring, not the extracted values
- [ ] This gate cannot be bypassed — scoring always waits for confirmation

---

## Epic 3: Criteria Configuration

### US-04 — Set buy criteria before screening
**As an** acquisitions professional,
**I want to** define my screening criteria in plain terms,
**so that** the scoring reflects what I'm actually looking for today.

**Acceptance Criteria:**
- [ ] Criteria are defined in a JSON config file (human-editable, no code required)
- [ ] Supported criteria fields:
  - Property type (allowlist: multifamily, industrial, office, retail, mixed)
  - Target markets (allowlist of metro names or states)
  - Max asking price
  - Min cap rate (trailing)
  - Min occupancy %
  - Max LTV
  - Min DSCR
  - Max expense ratio
  - Vintage range (min/max year built)
  - Max pro-forma to trailing NOI gap % (e.g., flag if >15%)
- [ ] Criteria can be changed between runs without code changes
- [ ] Missing criteria fields default to "no filter" (pass everything)
- [ ] Criteria file is version-controlled alongside the project

---

## Epic 4: Scoring

### US-05 — Score the deal against buy criteria
**As an** acquisitions professional,
**I want** each metric scored against my criteria,
**so that** I know immediately which criteria the deal passes or fails.

**Acceptance Criteria:**
- [ ] Each criterion produces a PASS / FAIL / FLAG result
- [ ] FLAG is used when data is present but ambiguous (e.g., DSCR marginally below threshold)
- [ ] Overall verdict is: GO / CONDITIONAL / NO-GO
  - GO = all hard criteria pass, no red flags
  - CONDITIONAL = passes hard criteria but has 1+ flags worth investigating
  - NO-GO = fails one or more hard criteria
- [ ] Python handles all numeric comparisons — Claude never does arithmetic
- [ ] Scoring logic is in a separate, readable Python file (not buried in a prompt)

### US-06 — Detect red flags beyond the criteria
**As an** acquisitions professional,
**I want** the agent to flag issues that aren't covered by my explicit criteria,
**so that** I don't miss something the numbers alone don't capture.

**Acceptance Criteria:**
- [ ] Agent detects and flags:
  - Pro-forma NOI more than 15% above trailing (configurable threshold)
  - Expense ratio more than 5 points above market norm for asset class
  - DSCR within 5% of the threshold (marginal — warrants investigation)
  - Lease expiration concentration (>40% of leases expiring within 12 months)
  - Any language in the OM suggesting deferred maintenance or value-add assumptions
    that aren't reflected in pro-forma expenses
- [ ] Red flags are listed separately from criteria pass/fail
- [ ] Red flags include a one-line explanation of why it was flagged

---

## Epic 5: Output and Delivery

### US-07 — Receive a clear, readable verdict
**As an** acquisitions professional,
**I want** the output to be readable without being a data scientist,
**so that** I can make a decision in under 60 seconds.

**Acceptance Criteria:**
- [ ] Output includes:
  - Verdict (GO / CONDITIONAL / NO-GO) with emoji indicator
  - Property summary line (type, market, asking price)
  - Metrics table (extracted values + pass/fail per criterion)
  - Red flags list (with one-line explanations)
  - One-paragraph narrative summary (generated by Claude)
- [ ] Narrative is written in plain language, no jargon the user didn't already know
- [ ] Output is delivered to Telegram as a formatted message
- [ ] Output is also written as a JSON file to `/output/` for record-keeping
- [ ] Full run takes under 3 minutes end-to-end on a clean PDF

### US-08 — Output is filmable for LinkedIn
**As** Will,
**I want** the output to be visually clean and self-explanatory on camera,
**so that** the demo is compelling without narration explaining everything.

**Acceptance Criteria:**
- [ ] Verdict and key metrics are visible in a single Telegram message without scrolling
- [ ] Emoji usage is consistent and meaningful (✅ PASS, ❌ FAIL, ⚠️ FLAG)
- [ ] Red flags are scannable at a glance
- [ ] A non-CRE person watching the demo can understand the verdict without explanation

---

## Epic 6: Reliability and Testability

### US-09 — Each stage is independently testable
**As** the developer (Will + Zoé),
**we want** each pipeline stage to be testable in isolation,
**so that** we can catch errors stage-by-stage before wiring everything together.

**Acceptance Criteria:**
- [ ] Each stage has a test script in `/tests/` that runs independently
- [ ] Test data: minimum 3 real OMs saved in `/tests/sample-oms/`
- [ ] Each test script produces a clear PASS/FAIL result with output shown
- [ ] Stage N is not built until Stage N-1 passes tests on all 3 sample OMs
- [ ] No stage is "done" until tested — not just "looks right"

---

## Story Map (Build Order)

```
US-01 PDF Ingestion
  ↓ (tests pass)
US-02 Metric Extraction + US-03 Human Review Gate
  ↓ (tests pass + Will reviews output on 3 real OMs)
US-04 Criteria Configuration
  ↓
US-05 Scoring + US-06 Red Flag Detection
  ↓ (tests pass)
US-07 Output + Delivery + US-08 LinkedIn formatting
  ↓
End-to-end test on 3 fresh OMs → Film demo → Post
```

---

_Next step: Will reviews and approves this PRD, then we move to Architecture (data models, stage definitions, tech stack decisions)._
_Zoé — 2026-03-04_
