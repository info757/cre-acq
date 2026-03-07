---
stepsCompleted: ['step-01-validate-prerequisites', 'step-02-design-epics', 'step-03-create-stories', 'step-04-final-validation']
inputDocuments:
  - stage-1-om-screener/prd.md
  - stage-1-om-screener/architecture.md
---

# cre-acquisitions-platform - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for cre-acquisitions-platform, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: System scans a folder and identifies all .pdf and .xlsx/.xls files; returns has_pdf, pdf_path, has_excel, excel_paths as JSON
FR2: If multiple PDFs found, system selects the largest file (most likely the OM)
FR3: System exits with error if folder is empty or contains no supported files
FR4: Neither PDF nor Excel is required — any combination is valid (at least one must be present)
FR5: Extracts readable text from a clean (text-layer) PDF using pdfplumber
FR6: Detects low-density pages (image-embedded financials); falls back to targeted OCR on those pages only
FR7: Falls back to full OCR for scanned documents (avg <100 chars/page) using Tesseract
FR8: Returns error if file not found or not a valid PDF
FR9: Page-level metadata written alongside text (char counts, OCR flags)
FR10: System detects Excel file type from filename keywords and sheet names (financials, rent_roll, commercial_rent_roll, loan_info)
FR11: Extracts partial ExtractedMetrics JSON from each recognized Excel file type
FR12: All numeric extraction uses Decimal — never float
FR13: Excel values take priority over Claude-extracted values at merge step
FR14: Unrecognized Excel files are skipped with a warning, not a failure
FR15: Extraction flags logged per field (source file, any anomalies)
FR16: Extracts key financial metrics from OM: property type, market, asking price, NOI (trailing + pro-forma), cap rate, occupancy, expense ratio, debt terms, vintage, units/SF, lease info
FR17: Output is structured JSON matching the data-model schema (ExtractedMetrics)
FR18: If a field is ambiguous, agent flags it for human review rather than guessing
FR19: After extraction, system displays the metrics table and pauses for user review
FR20: User can confirm (proceed to scoring) or flag any incorrect fields
FR21: If user flags a field, they can correct it inline before scoring
FR22: Corrected values are used in scoring, not the extracted values
FR23: Human review gate cannot be bypassed — scoring always waits for confirmation
FR24: Criteria are defined in a JSON config file (human-editable, no code required)
FR25: Supported criteria fields: property type, target markets, max asking price, min cap rate, min occupancy, max LTV, min DSCR, max expense ratio, vintage range, max pro-forma to trailing NOI gap %
FR26: Criteria can be changed between runs without code changes
FR27: Missing criteria fields default to "no filter" (pass everything)
FR28: Criteria file is version-controlled alongside the project
FR29: Each criterion produces a PASS / FAIL / FLAG result
FR30: FLAG is used when data is present but ambiguous (e.g., DSCR marginally below threshold)
FR31: Overall verdict is GO / CONDITIONAL / NO-GO (GO = all pass, CONDITIONAL = passes with flags, NO-GO = fails hard criteria)
FR32: Python handles all numeric comparisons — Claude never does arithmetic
FR33: Scoring logic is in a separate, readable Python file (not buried in a prompt)
FR34: Agent detects and flags red flags: pro-forma NOI gap >15%, expense ratio above norm, DSCR margin, lease expiration concentration, deferred maintenance language
FR35: Red flags are listed separately from criteria pass/fail with one-line explanations
FR36: Output includes verdict with emoji, property summary, metrics table, red flags list, one-paragraph narrative summary
FR37: Narrative is written in plain language, no jargon the user didn't already know
FR38: Output is delivered to Telegram as a formatted message
FR39: Output is also written as a JSON file to output/ for record-keeping
FR40: Verdict and key metrics visible in a single Telegram message without scrolling
FR41: Emoji usage is consistent and meaningful (✅ PASS, ❌ FAIL, ⚠️ FLAG)
FR42: Red flags are scannable at a glance; non-CRE person can understand verdict without explanation
FR43: Each stage has a test script in tests/ that runs independently
FR44: Test data: minimum 3 real OMs saved in tests/sample-oms/
FR45: Each test script produces a clear PASS/FAIL result with output shown
FR46: Stage N is not built until Stage N-1 passes tests on all 3 sample OMs
FR47: No stage is "done" until tested — not just "looks right"

### NonFunctional Requirements

NFR1: Full run takes under 3 minutes end-to-end on a clean PDF
NFR2: User can make a decision in under 60 seconds from output
NFR3: Output is readable without being a data scientist
NFR4: Each pipeline stage is testable in isolation before wiring together
NFR5: Prompts are stored as files — never hardcoded in src or n8n
NFR6: One n8n node = one responsibility (no fat nodes)

### Additional Requirements

- **Stack (from Architecture):** n8n for orchestration (localhost:5678), pdfplumber for PDF extraction, Tesseract + pdf2image for OCR, pandas + openpyxl for Excel, Claude claude-sonnet-4-6 for extraction and narrative, Python for merge and scoring, Telegram for delivery
- **Pipeline stages:** 1a PDF→Text, 1b Excel→Partial Metrics, 2 Merge, 3 Human Review Gate, 4 Scoring, 5 Output
- **File layout:** stage-1-om-screener/ with src/, prompts/, tests/sample-oms/, output/, n8n/
- **Merge rule:** Excel values take priority field-by-field; Claude fills remaining nulls; source tag per field (excel | claude | null)
- **Human review gate UX:** Telegram message with metrics table + source tags; user replies "ok" to proceed or "fix: field_name new_value" to correct
- **Red flag thresholds:** Pro-forma NOI >15% above trailing (configurable), expense ratio >5 pts above asset-class norm, DSCR within 5% of threshold, >40% leases expiring within 12 months
- **Dependencies:** pdfplumber, pytesseract, Pillow, anthropic, pdf2image, pandas, openpyxl; system: tesseract, poppler (brew install)
- **No starter template** specified in Architecture — project structure already established in stage-1-om-screener

### FR Coverage Map

FR1-FR15: Epic 1 - Ingestion (folder discovery, PDF extraction, Excel parsing)
FR16-FR23: Epic 2 - Structured Data Extraction (metric extraction, human review gate)
FR24-FR28: Epic 3 - Criteria Configuration (JSON config, criteria fields)
FR29-FR35: Epic 4 - Scoring (pass/fail/flag, verdict, red flags)
FR36-FR42: Epic 5 - Output and Delivery (verdict, Telegram, JSON, formatting)
FR43-FR47: Epic 6 - Reliability and Testability (stage tests, sample OMs)

## Epic List

### Epic 1: Ingestion
Acquisitions professionals can point the system at a deal folder and have it discover PDFs and Excel files, extract text from PDFs (with OCR fallback), and parse Excel into structured metrics.
**FRs covered:** FR1-FR15

### Epic 2: Structured Data Extraction
Acquisitions professionals can get key financial metrics extracted from OMs (merged from Excel and Claude), review them before scoring, and correct any extraction errors.
**FRs covered:** FR16-FR23

### Epic 3: Criteria Configuration
Acquisitions professionals can define buy criteria in a JSON config and change them between runs without code changes.
**FRs covered:** FR24-FR28

### Epic 4: Scoring
Acquisitions professionals can see each metric scored against their criteria, get PASS/FAIL/FLAG results, and see red flags beyond the explicit criteria.
**FRs covered:** FR29-FR35

### Epic 5: Output and Delivery
Acquisitions professionals can receive a clear verdict (GO/CONDITIONAL/NO-GO) with metrics, red flags, and narrative, delivered to Telegram and saved as JSON.
**FRs covered:** FR36-FR42

### Epic 6: Reliability and Testability
Developers can test each pipeline stage in isolation with real OMs and ensure no stage is marked done until it passes tests.
**FRs covered:** FR43-FR47

---

## Epic 1: Ingestion

Acquisitions professionals can point the system at a deal folder and have it discover PDFs and Excel files, extract text from PDFs (with OCR fallback), and parse Excel into structured metrics.

### Story 1.1: Discover deal folder inputs

As an acquisitions professional,
I want to point the system at a folder of deal files,
so that it figures out what's there and routes each file correctly.

**Acceptance Criteria:**

**Given** a folder path containing deal files
**When** the system scans the folder
**Then** it identifies all .pdf and .xlsx/.xls files
**And** returns has_pdf, pdf_path, has_excel, excel_paths as JSON
**And** if multiple PDFs found, selects the largest (most likely the OM)
**And** exits with error if folder is empty or contains no supported files
**And** neither PDF nor Excel is required — any combination is valid (at least one must be present)

### Story 1.2: Extract text from PDF

As an acquisitions professional,
I want to provide an OM PDF,
so that the system can process its text content.

**Acceptance Criteria:**

**Given** a valid PDF file path
**When** the system extracts text
**Then** it extracts readable text from a clean (text-layer) PDF using pdfplumber
**And** detects low-density pages (image-embedded financials)
**And** falls back to targeted OCR (Tesseract) on low-density pages only
**And** falls back to full OCR for scanned documents (avg <100 chars/page)
**And** returns error if file not found or not a valid PDF
**And** page-level metadata written alongside text (char counts, OCR flags)

### Story 1.3: Ingest Excel files and extract structured metrics

As an acquisitions professional,
I want the system to read any Excel files provided with an OM,
so that financial data from rent rolls, operating statements, and loan files is used directly rather than extracted by Claude from PDFs.

**Acceptance Criteria:**

**Given** one or more Excel file paths
**When** the system parses each file
**Then** it detects file type from filename keywords and sheet names (financials, rent_roll, commercial_rent_roll, loan_info)
**And** extracts partial ExtractedMetrics JSON from each recognized file type
**And** all numeric extraction uses Decimal — never float
**And** Excel values take priority over Claude-extracted values at merge step
**And** unrecognized files are skipped with a warning, not a failure
**And** extraction flags logged per field (source file, any anomalies)

---

## Epic 2: Structured Data Extraction

Acquisitions professionals can get key financial metrics extracted from OMs (merged from Excel and Claude), review them before scoring, and correct any extraction errors.

### Story 2.1: Merge inputs and extract metrics from OM

As an acquisitions professional,
I want the agent to pull key metrics from the OM and combine them with Excel data,
so that I don't have to read the full document to find the numbers.

**Acceptance Criteria:**

**Given** raw text from PDF (optional) and/or partial metrics from Excel (optional)
**When** at least one input is provided
**Then** the system merges inputs: Excel values take priority field-by-field, Claude fills remaining nulls from PDF text
**And** extracts: property type, market, asking price, NOI (trailing + pro-forma), cap rate, occupancy, expense ratio, debt terms, vintage, units/SF, lease info
**And** uses null if not found — never hallucinates
**And** each field carries a source tag (excel | claude | null)
**And** output is full ExtractedMetrics JSON matching the data-model schema
**And** if a field is ambiguous, agent flags it for human review rather than guessing

### Story 2.2: Human review gate before scoring

As an acquisitions professional,
I want to see the extracted metrics before scoring fires,
so that I can catch any extraction errors before they affect the verdict.

**Acceptance Criteria:**

**Given** extracted metrics from the merge step
**When** the system displays the metrics table
**Then** it pauses and waits for user confirmation
**And** user can confirm (proceed to scoring) or flag any incorrect fields
**And** if user flags a field, they can correct it inline (e.g., "fix: noi_trailing 920000") before scoring
**And** corrected values are used in scoring, not the extracted values
**And** this gate cannot be bypassed — scoring always waits for confirmation

---

## Epic 3: Criteria Configuration

Acquisitions professionals can define buy criteria in a JSON config and change them between runs without code changes.

### Story 3.1: Set buy criteria before screening

As an acquisitions professional,
I want to define my screening criteria in plain terms,
so that the scoring reflects what I'm actually looking for today.

**Acceptance Criteria:**

**Given** a buy-criteria.json config file
**When** the user edits the file
**Then** criteria are human-editable (no code required)
**And** supported fields: property type, target markets, max asking price, min cap rate, min occupancy, max LTV, min DSCR, max expense ratio, vintage range, max pro-forma to trailing NOI gap %
**And** criteria can be changed between runs without code changes
**And** missing criteria fields default to "no filter" (pass everything)
**And** criteria file is version-controlled alongside the project

---

## Epic 4: Scoring

Acquisitions professionals can see each metric scored against their criteria, get PASS/FAIL/FLAG results, and see red flags beyond the explicit criteria.

### Story 4.1: Score the deal against buy criteria

As an acquisitions professional,
I want each metric scored against my criteria,
so that I know immediately which criteria the deal passes or fails.

**Acceptance Criteria:**

**Given** confirmed metrics and buy-criteria.json
**When** the scoring engine runs
**Then** each criterion produces a PASS / FAIL / FLAG result
**And** FLAG is used when data is present but ambiguous (e.g., DSCR marginally below threshold)
**And** overall verdict is GO / CONDITIONAL / NO-GO
**And** Python handles all numeric comparisons — Claude never does arithmetic
**And** scoring logic is in a separate, readable Python file (not buried in a prompt)

### Story 4.2: Detect red flags beyond the criteria

As an acquisitions professional,
I want the agent to flag issues that aren't covered by my explicit criteria,
so that I don't miss something the numbers alone don't capture.

**Acceptance Criteria:**

**Given** confirmed metrics and scoring results
**When** red flag detection runs
**Then** it flags: pro-forma NOI >15% above trailing (configurable), expense ratio >5 pts above asset-class norm, DSCR within 5% of threshold, >40% leases expiring within 12 months, deferred maintenance language in OM
**And** red flags are listed separately from criteria pass/fail
**And** each red flag includes a one-line explanation of why it was flagged

---

## Epic 5: Output and Delivery

Acquisitions professionals can receive a clear verdict (GO/CONDITIONAL/NO-GO) with metrics, red flags, and narrative, delivered to Telegram and saved as JSON.

### Story 5.1: Receive a clear, readable verdict

As an acquisitions professional,
I want the output to be readable without being a data scientist,
so that I can make a decision in under 60 seconds.

**Acceptance Criteria:**

**Given** scoring results and red flags
**When** the output is generated
**Then** it includes: verdict (GO/CONDITIONAL/NO-GO) with emoji, property summary, metrics table, red flags list, one-paragraph narrative (Claude-generated)
**And** narrative is written in plain language, no jargon
**And** output is delivered to Telegram as a formatted message
**And** output is also written as a JSON file to output/ for record-keeping
**And** full run takes under 3 minutes end-to-end on a clean PDF

### Story 5.2: Output is filmable for LinkedIn

As Will,
I want the output to be visually clean and self-explanatory on camera,
so that the demo is compelling without narration explaining everything.

**Acceptance Criteria:**

**Given** the verdict message
**When** displayed in Telegram
**Then** verdict and key metrics are visible in a single message without scrolling
**And** emoji usage is consistent and meaningful (✅ PASS, ❌ FAIL, ⚠️ FLAG)
**And** red flags are scannable at a glance
**And** a non-CRE person watching can understand the verdict without explanation

---

## Epic 6: Reliability and Testability

Developers can test each pipeline stage in isolation with real OMs and ensure no stage is marked done until it passes tests.

### Story 6.1: Each stage is independently testable

As the developer (Will + Zoé),
we want each pipeline stage to be testable in isolation,
so that we can catch errors stage-by-stage before wiring everything together.

**Acceptance Criteria:**

**Given** the pipeline stages (discover, extract, merge, review gate, score, output)
**When** developing or modifying a stage
**Then** each stage has a test script in tests/ that runs independently
**And** test data: minimum 3 real OMs saved in tests/sample-oms/
**And** each test script produces a clear PASS/FAIL result with output shown
**And** stage N is not built until stage N-1 passes tests on all 3 sample OMs
**And** no stage is "done" until tested — not just "looks right"

### Story 6.2: Wire pipeline in n8n

As the developer (Will + Zoé),
we want the OM Screener pipeline orchestrated in n8n,
so that we can run it end-to-end from a webhook and demo it on real deals.

**Acceptance Criteria:**

**Given** a deal folder path
**When** we POST to the n8n webhook
**Then** the pipeline runs: discover → extract/parse → merge → score → format_output
**And** a CLI runner (run_pipeline.py) exists to test the pipeline without n8n
**And** n8n workflow JSON is importable and documented
**And** the human review gate cannot be bypassed in production (architecture principle)
**And** a minimal workflow with --skip-gate exists for local testing only; production must use the full flow with Wait for Webhook
