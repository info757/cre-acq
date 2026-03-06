# Architecture — Stage 1: OM Screener
**BMAD Phase 3: Solutioning**
_Status: APPROVED (updated 2026-03-05 — Excel ingestion added)_

---

## Core Principles (Non-Negotiable)

1. **Python does math. Claude does language.** No LLM arithmetic, ever.
2. **One n8n node = one responsibility.** No fat nodes.
3. **Prompts are files.** Never hardcoded in src or n8n.
4. **Human review gate cannot be bypassed.** Scoring always waits for confirmation.
5. **Stage N not built until Stage N-1 passes tests on 3 real OMs.**

---

## Stack

| Layer | Tool | Purpose |
|---|---|---|
| Orchestration | n8n (localhost:5678) | Pipeline wiring, webhook triggers, wait nodes |
| PDF extraction | pdfplumber (Python) | Primary text extraction from clean PDFs |
| OCR fallback | Tesseract + pdf2image | Scanned/image-only PDFs |
| Excel ingestion | pandas + openpyxl | Structured data from rent rolls, financials, loan files |
| LLM extraction | Claude claude-sonnet-4-6 | Structured metric extraction from PDF text |
| Merge layer | Python | Excel values overwrite Claude values; nulls filled from either source |
| Scoring | Python (pure logic) | Rule-based scoring vs. buy-criteria.json |
| LLM narrative | Claude claude-sonnet-4-6 | One-paragraph verdict summary |
| Delivery | Telegram (via OpenClaw) | Human review gate + final verdict |
| Storage | Local JSON files | output/ directory, one file per deal |

## Input Policy

PDF and Excel are both optional. At least one must be present. Any combination is valid:
- **PDF only** — Claude extracts all metrics from text
- **Excel only** — parse_excel.py extracts financial metrics; narrative fields left null
- **PDF + Excel** — Excel wins on numbers; Claude fills narrative/market fields from PDF text

---

## Pipeline: 6 Stages

```
[INPUT]
  Deal folder: any combination of .pdf and .xlsx files
  At least one file required. Neither type is mandatory.
      ↓
[STAGE 1a] PDF → Text                        (skipped if no PDF)
  Python: extract_text.py (pdfplumber)
  Fallback: ocr_pdf.py (Tesseract) if text density < threshold
  Output: raw_text.txt

[STAGE 1b] Excel → Partial Metrics           (skipped if no .xlsx files)
  Python: parse_excel.py
  Detects file type per file (financials / rent roll / loan info)
  Output: excel_metrics.json (partial ExtractedMetrics — only fields found)

      ↓ (both run in parallel if both inputs present)

[STAGE 2] Merge Inputs
  Python: merge_inputs.py
  If PDF present: Claude extracts metrics from raw_text.txt → claude_metrics.json
  Merge rule: Excel values take priority. Claude fills nulls.
  Output: extracted_metrics.json (full ExtractedMetrics schema)
      ↓
[STAGE 3] Human Review Gate
  Telegram: display metrics table + source tags (Excel / Claude / null)
  Wait for: "ok" (proceed) or corrections ("fix: field value")
  Output: confirmed_metrics.json (same schema, corrections applied)
      ↓
[STAGE 4] Metrics → Scoring
  Python: score.py reads confirmed_metrics.json + buy-criteria.json
  Output: scoring_results.json (ScreeningResult schema minus narrative)
      ↓
[STAGE 5] Scoring → Output
  Claude: om-narrator.md prompt → narrative paragraph
  Python: format_output.py → Telegram message string
  Delivery: Telegram message + output/DEAL_ID.json written to disk
```

---

## n8n Workflow Design

```
Node 1:  Webhook (POST /om-screener/run)
           Body: { deal_folder: string, deal_id: string }
           deal_folder: path containing .pdf and/or .xlsx files
           At least one file required.

Node 2:  Execute Command — Discover inputs
           Script: python3 src/discover_inputs.py --folder {{deal_folder}}
           Returns: { has_pdf: bool, pdf_path: string|null,
                      has_excel: bool, excel_paths: [string] }

Node 3:  IF node — has_pdf == true
           True branch → Node 3a + 3b (parallel)
           False branch → Node 4 (Excel only)

Node 3a: Execute Command (PDF branch — extract text)
           Script: python3 src/extract_text.py --pdf {{pdf_path}} --out /tmp/{{deal_id}}_raw.txt

Node 3b: Execute Command (PDF branch — check OCR needed)
           Script: python3 src/check_ocr_needed.py --txt /tmp/{{deal_id}}_raw.txt
           Returns: { needs_ocr: bool }

Node 3c: IF node — needs_ocr == true
           True: python3 src/ocr_pdf.py --pdf {{pdf_path}} --out /tmp/{{deal_id}}_raw.txt
           False: continue

Node 4:  IF node — has_excel == true
           True branch → Node 4a
           False branch → continue

Node 4a: Execute Command (Excel branch)
           Script: python3 src/parse_excel.py
                   --files {{excel_paths_json}}
                   --out /tmp/{{deal_id}}_excel.json
           Returns: partial ExtractedMetrics JSON

Node 5:  Execute Command — Merge + Claude extraction
           Script: python3 src/merge_inputs.py
                   --raw-text /tmp/{{deal_id}}_raw.txt (optional)
                   --excel /tmp/{{deal_id}}_excel.json (optional)
                   --prompt prompts/om-extractor.md
                   --out /tmp/{{deal_id}}_extracted.json
           Logic: if PDF present, calls Claude to fill gaps Excel didn't cover
                  Excel values always win over Claude values

Node 6:  Execute Command
           Script: python3 src/format_review_message.py --metrics /tmp/{{deal_id}}_extracted.json
           Returns: formatted metrics table (with source tags: Excel / Claude / null)

Node 7:  HTTP Request → Telegram (send review message)

Node 8:  Wait for Webhook (human review gate)
           Timeout: 24 hours
           Listens: POST /om-screener/confirm/{deal_id}

Node 9:  Execute Command — Apply corrections
           Script: python3 src/apply_corrections.py
                   --metrics /tmp/{{deal_id}}_extracted.json
                   --corrections {{Node8.corrections}}
                   --out /tmp/{{deal_id}}_confirmed.json

Node 10: Execute Command — Score
           Script: python3 src/score.py
                   --metrics /tmp/{{deal_id}}_confirmed.json
                   --criteria shared/buy-criteria.json
                   --out /tmp/{{deal_id}}_scored.json

Node 11: HTTP Request (Anthropic API) — Narrative
           Prompt: prompts/om-narrator.md
           Input: /tmp/{{deal_id}}_scored.json

Node 12: Execute Command — Format output
           Script: python3 src/format_output.py
                   --scored /tmp/{{deal_id}}_scored.json
                   --narrative {{Node11.narrative}}
                   --out output/{{deal_id}}.json

Node 13: HTTP Request → Telegram (deliver final verdict)
```

---

## Python Scripts

### `src/discover_inputs.py`
```
Input:  --folder <path>
Action: Scan folder for .pdf and .xlsx files
Output: JSON to stdout: { has_pdf, pdf_path, has_excel, excel_paths: [] }
        Raises error if folder is empty or contains no supported files
Test:   tests/test_discover.py
```

### `src/parse_excel.py`
```
Input:  --files <JSON array of paths>  --out <path>
Action: For each .xlsx file:
          Detect file type using filename keywords + sheet names:
            - "financials" / "financial" → parse_financials()
            - "rent roll" / "rr" / "itemized" → parse_rent_roll()
            - "loan" / "debt" → parse_loan_info()
            - "commercial" → parse_commercial_rent_roll()
          Extract fields into partial ExtractedMetrics JSON
          Later files do NOT overwrite earlier ones (first clean value wins per field)
Output: partial ExtractedMetrics JSON written to --out
        Only includes fields actually found — no nulls for fields not in Excel
Rules:
  - All numeric extraction uses Decimal, not float
  - Skips rows where value is clearly a header or formula artifact
  - Logs any sheet/column it couldn't parse to extraction_flags
Test:   tests/test_parse_excel.py (uses Mill One sample files)
```

### `src/merge_inputs.py`
```
Input:  --raw-text <path> (optional)  --excel <path> (optional)  --prompt <path>  --out <path>
Action: 
  If raw-text provided: call Claude with om-extractor.md prompt → claude_metrics.json
  Load excel metrics if provided (already written by parse_excel.py)
  Merge: Excel values take priority field-by-field
         Claude fills any remaining null fields
         Source tag written per field: "excel" | "claude" | null
Output: full ExtractedMetrics JSON written to --out (with _sources dict)
Error:  exits 1 if neither raw-text nor excel is provided
Test:   tests/test_merge.py
```

### `src/extract_text.py`
```
Input:  --pdf <path>  --out <path>
Action: Open PDF with pdfplumber, extract all text page by page
Output: writes raw text to --out
Error:  exits 1 with message if file not found or not a PDF
Test:   tests/test_extract.py
```

### `src/check_ocr_needed.py`
```
Input:  --txt <path>
Action: Count chars in text file. If < 100 chars per page on average → needs OCR
Output: JSON to stdout: { "needs_ocr": bool, "char_count": int, "page_count": int }
Test:   tested inline in test_extract.py
```

### `src/ocr_pdf.py`
```
Input:  --pdf <path>  --out <path>
Action: Convert PDF pages to images (pdf2image), run Tesseract on each, concat
Output: writes OCR text to --out
Deps:   tesseract-ocr (brew install tesseract), pdf2image, Pillow
Test:   tests/test_extract.py (scanned OM sample)
```

### `src/apply_corrections.py`
```
Input:  --metrics <path>  --corrections <JSON string>  --out <path>
Action: Load extracted_metrics.json, apply key:value corrections from input
Output: writes corrected JSON to --out
        also writes correction_log entry (what was changed and by whom)
Test:   tests/test_corrections.py
```

### `src/score.py`
```
Input:  --metrics <path>  --criteria <path>  --out <path>
Action: Load confirmed_metrics.json + buy-criteria.json
        For each criterion: compare metric value to threshold
        Detect red flags (pro-forma gap, expense ratio, DSCR margin, lease roll)
        Compute overall verdict (GO / CONDITIONAL / NO-GO)
Output: writes ScreeningResult JSON (minus narrative) to --out
Rules:
  - FAIL if any hard criterion not met → NO-GO
  - FLAG if within 5% of threshold → CONDITIONAL
  - Red flag if pro-forma NOI > trailing * (1 + max_proforma_noi_premium)
  - Red flag if expense_ratio > asset_class_norm + 0.05
  - Red flag if lease expirations > 40% within 12 months
  - null metric = skip that criterion (never fail on missing data)
Test:   tests/test_score.py (unit tests for each rule)
```

### `src/format_review_message.py`
```
Input:  --metrics <path>
Action: Read extracted_metrics.json, build readable table string
Output: prints formatted string to stdout
Format: (see sample below)
Test:   visual — run it and read the output
```

### `src/format_output.py`
```
Input:  --scored <path>  --narrative <string>  --out <path>
Action: Build complete verdict message (Telegram formatted) + write full JSON
Output: prints Telegram message string to stdout, writes JSON to --out
Test:   visual — run it and read the output
```

---

## Prompt Files

### `prompts/om-extractor.md`
```
TASK: Extract structured CRE financial data from the following OM text.

OUTPUT FORMAT: Return ONLY valid JSON matching this exact schema.
Do not add fields. Use null for any field not found in the document.
Do not calculate or infer values — extract only what is explicitly stated.

[Schema embedded — mirrors ExtractedMetrics from shared/data-model.md]

IMPORTANT:
- If you see both trailing and pro-forma values for NOI or cap rate, extract BOTH.
- If a value is ambiguous (unclear if trailing or pro-forma), set the field to null
  and add a note to extraction_flags: ["noi_trailing: ambiguous — see page 12"]
- Never hallucinate a number. null is always better than a guess.

OM TEXT:
{{raw_text}}
```

### `prompts/om-narrator.md`
```
TASK: Write a 3-5 sentence plain-English summary of this CRE deal screening result.

AUDIENCE: An acquisitions professional making a quick go/no-go decision.
TONE: Direct, no jargon the reader doesn't already know, no filler phrases.
LENGTH: 3-5 sentences maximum.

Include: the verdict, the strongest reason for it, and one actionable next step
if the verdict is GO or CONDITIONAL.

Do not repeat every number — the reader already has the metrics table.

SCREENING RESULT:
{{scored_json}}
```

---

## File Layout

```
stage-1-om-screener/
  architecture.md          ← THIS FILE
  project-brief.md
  prd.md
  src/
    discover_inputs.py       ← scan deal folder, detect PDF + Excel files
    extract_text.py          ← PDF → raw text
    check_ocr_needed.py      ← decide if OCR needed
    ocr_pdf.py               ← Tesseract OCR fallback
    parse_excel.py           ← Excel → partial metrics JSON
    merge_inputs.py          ← merge Excel + Claude extraction
    apply_corrections.py
    score.py
    format_review_message.py
    format_output.py
    run_pipeline.py          ← CLI runner (test without n8n)
  prompts/
    om-extractor.md
    om-narrator.md
  tests/
    sample-oms/
      sample-01.pdf          ← multifamily clean PDF
      sample-02.pdf          ← industrial clean PDF
      sample-03.pdf          ← scanned/image PDF (OCR test)
    test_discover.py
    test_extract.py
    test_parse_excel.py
    test_merge.py
    test_corrections.py
    test_score.py
    test_end_to_end.py
  n8n/
    workflow.json            ← export from n8n after building
  output/                    ← deal verdict JSONs written here
  requirements.txt
  .cursor/rules
  .cursorignore
```

---

## Dependencies

### Python (requirements.txt)
```
pdfplumber>=0.10.0
pytesseract>=0.3.10
Pillow>=10.0.0
anthropic>=0.40.0
pdf2image>=1.16.3
pandas>=2.0.0
openpyxl>=3.1.0
```

### System (one-time install)
```bash
brew install tesseract
brew install poppler   # required by pdf2image
```

---

## Human Review Gate — UX

Will receives this Telegram message after extraction:

```
📋 OM EXTRACTED — Review before scoring fires

Property: Multifamily | Charlotte, NC
Asking Price: $18,200,000
NOI (trailing): $873,000
NOI (pro-forma): $1,100,000  ⚠️ pro-forma present
Cap Rate (trailing): 4.8%
Occupancy: 91%
Expense Ratio: 48%
DSCR: 1.18 (at 6.5% / 75% LTV)
Vintage: 1987
Units: 142

Extraction flags: none

Reply 'ok' to run scoring.
Reply 'fix: field_name new_value' to correct a field first.
Example: 'fix: noi_trailing 920000'
```

When Will replies "ok", n8n webhook fires, scoring runs.
When Will replies "fix: dscr 1.22", corrections applied, then he re-confirms or says "ok".

---

## Build Order (mirrors PRD story map)

```
Week 1, Day 1:    discover_inputs.py — scan folder, detect file types
                   parse_excel.py — ingest Mill One Excel files, extract metrics
                   Test: run on Mill One sample, inspect excel_metrics.json

Week 1, Day 2:    extract_text.py + check_ocr_needed.py — PDF text extraction
                   Test: run on Mill One PDF, inspect raw_text.txt

Week 1, Day 3:    merge_inputs.py — combine Excel + Claude extraction
                   Test: merged output for Mill One should prefer Excel values

Week 1, Day 4-5:  om-extractor.md prompt refinement
                   Test Claude extraction on PDF-only path (no Excel)

Week 2, Day 1:    US-03 — Human review gate + format_review_message.py
                   Source tags visible: (Excel) / (Claude) / (null) per field

Week 2, Day 2-3:  score.py + buy-criteria.json
                   Unit test every scoring rule independently.

Week 2, Day 4:    Red flag detection (inside score.py)

Week 2, Day 5:    format_output.py + Telegram delivery
                   End-to-end test on Mill One.

Week 3:           Film demo. Post to LinkedIn.
```

---

_Updated 2026-03-05: Excel ingestion added. Neither PDF nor Excel required — any combo valid. Excel wins on numbers, Claude fills narrative gaps._
_First build target: discover_inputs.py + parse_excel.py — run on Mill One sample files._
