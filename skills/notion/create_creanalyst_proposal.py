#!/usr/bin/env python3
"""
Creates the CREanalyst AI-Augmented Fast Track proposal page in Notion.
Parent: DataGrove.ai database
"""
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

ENV_PATH = Path(__file__).parent / ".env"
API_KEY = None

if ENV_PATH.exists():
    for line in ENV_PATH.read_text().splitlines():
        if line.startswith("NOTION_API_KEY="):
            API_KEY = line.split("=", 1)[1].strip()

if not API_KEY:
    print("ERROR: NOTION_API_KEY not found in .env", file=sys.stderr)
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}
BASE = "https://api.notion.com/v1"
DATAGOVE_DB = "2f3a3175-c27b-8001-a173-dfc7a7c47653"


def api(method, path, body=None):
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err = json.loads(e.read())
        print(f"ERROR {e.code}: {err.get('message', str(err))}", file=sys.stderr)
        sys.exit(1)


def h1(text):
    return {"object": "block", "type": "heading_1", "heading_1": {
        "rich_text": [{"type": "text", "text": {"content": text}}]}}

def h2(text):
    return {"object": "block", "type": "heading_2", "heading_2": {
        "rich_text": [{"type": "text", "text": {"content": text}}]}}

def h3(text):
    return {"object": "block", "type": "heading_3", "heading_3": {
        "rich_text": [{"type": "text", "text": {"content": text}}]}}

def p(text, bold=False):
    part = {"type": "text", "text": {"content": text}}
    if bold:
        part["annotations"] = {"bold": True}
    return {"object": "block", "type": "paragraph", "paragraph": {
        "rich_text": [part]}}

def p_empty():
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": []}}

def bullet(text, bold_prefix=None):
    if bold_prefix:
        parts = [
            {"type": "text", "text": {"content": bold_prefix}, "annotations": {"bold": True}},
            {"type": "text", "text": {"content": text}}
        ]
    else:
        parts = [{"type": "text", "text": {"content": text}}]
    return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {
        "rich_text": parts}}

def numbered(text, bold_prefix=None):
    if bold_prefix:
        parts = [
            {"type": "text", "text": {"content": bold_prefix}, "annotations": {"bold": True}},
            {"type": "text", "text": {"content": text}}
        ]
    else:
        parts = [{"type": "text", "text": {"content": text}}]
    return {"object": "block", "type": "numbered_list_item", "numbered_list_item": {
        "rich_text": parts}}

def divider():
    return {"object": "block", "type": "divider", "divider": {}}

def callout(text, emoji="💡"):
    return {"object": "block", "type": "callout", "callout": {
        "rich_text": [{"type": "text", "text": {"content": text}}],
        "icon": {"type": "emoji", "emoji": emoji}}}

def code_block(text):
    return {"object": "block", "type": "code", "code": {
        "rich_text": [{"type": "text", "text": {"content": text}}],
        "language": "plain text"}}

def toggle(title, children):
    return {"object": "block", "type": "toggle", "toggle": {
        "rich_text": [{"type": "text", "text": {"content": title}, "annotations": {"bold": True}}],
        "children": children
    }}


# Build the full block list
blocks = [

    # Header callout
    callout("Prepared by Will Holt  |  March 2026  |  Confidential — For CRE Analyst Review", "🏢"),
    p_empty(),

    # Executive Summary
    h1("Executive Summary"),
    p("Fast Track already delivers the most rigorous CRE fundamentals training available. This proposal adds one thing: an AI layer that eliminates manual grunt work so students spend more time thinking like investors and less time fighting Excel."),
    p_empty(),
    p("The goal is not to replace the curriculum. It is to future-proof it."),
    p_empty(),
    p("CRE professionals who cannot use AI to accelerate financial analysis, document review, and model building will be at a structural disadvantage within 2-3 years. Fast Track is uniquely positioned to address that gap — before anyone else does."),
    p_empty(),
    p("This module introduces AI workflows as a parallel track woven into each of the 8 Fast Track phases. Students learn the same fundamentals they always have, and they also learn how to work 10x faster using tools already reshaping how deals get done."),
    divider(),

    # The Problem
    h1("The Problem"),
    p("Fast Track teaches students to build Excel models, read deal documents, and think through capital structures. That will always matter."),
    p_empty(),
    p("But today, a significant portion of the work required to get to insight is still manual:"),
    bullet("Extracting financial data from OMs, rent rolls, and loan term sheets"),
    bullet("Populating pro forma templates line by line"),
    bullet("Building comparison tables from scratch"),
    bullet("Abstracting leases by hand"),
    bullet("Writing market memos from raw data"),
    p_empty(),
    p("These tasks are not where analysis happens. They are the work that precedes analysis. AI can automate most of them — accurately, auditably, and fast."),
    p_empty(),
    callout("The professionals entering CRE today are competing against peers who are already using AI to do in 10 minutes what used to take 3 hours. Fast Track students deserve to know how.", "⚡"),
    divider(),

    # The Solution
    h1("The Solution: An AI Layer Across All 8 Phases"),
    p("Each Fast Track phase gets a 30-60 minute AI workflow session that maps directly to the skills students are already learning. The sessions are hands-on. Students replicate every workflow themselves."),
    p_empty(),
    p("The AI does not replace the model. It builds the inputs for the model — extracted from real documents, validated for accuracy, and reviewed by the student before anything hits a cell."),
    divider(),

    # Three Superpowers
    h1("The Three Superpowers"),
    p_empty(),

    h2("⚡ Superpower 1: Document → Model"),
    p("Upload a deal document — an OM, rent roll, loan term sheet, or lease — and AI extracts the key financial data and auto-populates the relevant fields in the Excel model."),
    p_empty(),
    callout("Example: Student uploads a 40-page OM. Within seconds, the system has extracted NOI, in-place cap rate, occupancy, rent/SF, lease expirations, and loan terms — and flagged two figures it could not confirm with high confidence for human review. Student approves. Excel model populates.", "📄"),
    p_empty(),

    h2("💬 Superpower 2: Text → Model"),
    p("Student types deal assumptions in plain language. AI interprets them and builds the pro forma structure in Excel."),
    p_empty(),
    callout('Example: "200-unit multifamily, average 950 SF, $2.50/SF monthly rent, 5% vacancy, 65% LTV, 6.5% interest rate, 5.5% exit cap, 5-year hold." — AI builds the pro forma. Student reviews, adjusts, refines.', "✍️"),
    p_empty(),

    h2("🎙️ Superpower 3: Voice → Model (STT)"),
    p("Student dictates deal assumptions out loud. Speech-to-text transcribes it. AI structures the output. Excel gets built."),
    p_empty(),
    callout("Example: Analyst records a 90-second voice memo after a site tour. By the time they get back to the office, a draft pro forma is waiting.", "🎤"),
    divider(),

    # Module-by-Module
    h1("Module-by-Module Breakdown"),
    p("Each of the 8 Fast Track phases maps to a specific AI workflow:"),
    p_empty(),

    h3("Phase 1 — Valuation"),
    p("AI Workflow: Deal document extraction → DCF model population"),
    p("Students upload an OM or broker package. AI extracts NOI, cap rate, rent roll summary, lease term data, and operating expense assumptions. Validated output populates the valuation model inputs."),
    p_empty(),

    h3("Phase 2 — Debt and Leverage"),
    p("AI Workflow: Natural language → loan comparison table"),
    p("Students describe a deal and financing scenario in plain text. AI generates a structured loan comparison table across multiple scenarios (different LTVs, rates, amortization schedules) in Excel."),
    p_empty(),

    h3("Phase 3 — Development"),
    p("AI Workflow: Voice or text → development pro forma"),
    p("Students dictate or type a development scenario. AI builds a development pro forma including construction budget, equity/debt stack, and stabilized yield."),
    p_empty(),

    h3("Phase 4 — Joint Ventures"),
    p("AI Workflow: JV agreement → waterfall explanation + model mapping"),
    p("Students upload a JV agreement excerpt. AI identifies the waterfall structure, explains each tier in plain language, and maps the promote logic to the appropriate cells in a waterfall model."),
    p_empty(),

    h3("Phase 5 — Capital Markets"),
    p("AI Workflow: Market data → investment memo draft"),
    p("Students provide comp transactions or market data. AI synthesizes them into a structured market summary memo — supply/demand dynamics, cap rate trends, buyer profiles — ready for a client presentation."),
    p_empty(),

    h3("Phase 6 — CRE System"),
    p("AI Workflow: Natural language → deal tracking dashboard"),
    p("Students describe what they want to track. AI generates the Excel or Notion database structure and writes the formulas. Students learn to use AI as a formula engine, not just an analysis tool."),
    p_empty(),

    h3("Phase 7 — Sales and Due Diligence"),
    p("AI Workflow: Due diligence documents → checklist population + issue flagging"),
    p("Students upload a set of due diligence documents. AI reviews them against a standard DD checklist, marks completed items, summarizes key findings, and flags items that require further attention or are missing."),
    p_empty(),

    h3("Phase 8 — Leasing"),
    p("AI Workflow: Lease document → abstraction table"),
    p("Students upload a lease. AI extracts base rent, escalations, TI allowance, lease term, options, co-tenancy clauses, and exclusivity provisions — populating a standard lease abstraction template for multi-lease comparison."),
    divider(),

    # Architecture
    h1("Architecture: Why This Is Compliant and Accurate"),
    callout("This is the section that matters for any firm evaluating whether to trust AI-assisted workflows in a professional environment.", "🔒"),
    p_empty(),
    h2("The Core Principle"),
    p("AI is one step in a deterministic pipeline — not the final word. Accuracy is enforced at the system level, not hoped for at the prompt level."),
    p_empty(),
    h2("The Pipeline"),
    code_block(
        "Deal Document (PDF / email attachment)\n"
        "        ↓\n"
        "[Step 1: Document Parser]       — extracts raw text, preserves structure\n"
        "        ↓\n"
        "[Step 2: AI Extraction]         — structured JSON output only, no free-form text\n"
        "                                  temperature = 0, source citation required\n"
        "        ↓\n"
        "[Step 3: Validation Layer]      — math checks, range checks, anomaly flagging\n"
        "                                  non-AI logic: does NOI ÷ Cap Rate = Value?\n"
        "        ↓\n"
        "[Step 4: Human Review]          — student/analyst approves extracted data\n"
        "                                  nothing hits the model without confirmation\n"
        "        ↓\n"
        "[Step 5: Model Population]      — validated data writes to Excel\n"
        "        ↓\n"
        "[Step 6: Audit Log]             — source doc, timestamp, values, approver"
    ),
    p_empty(),
    h2("Why Each Step Matters"),
    bullet("Structured output enforcement — AI returns only a predefined JSON schema. No narrative, no approximation. Eliminates hallucinated numbers."),
    bullet("Source citation requirement — AI must quote the exact text where it found each figure. If it cannot find a citation, it flags the field as unconfirmed. Fully auditable."),
    bullet("Validation layer — automated logic checks that numbers are internally consistent and within expected ranges. Outliers are flagged, not silently passed through."),
    bullet("Human checkpoint — analyst approves before anything populates a model. AI surfaces the data; the human owns the decision."),
    bullet("Audit log — every extraction logged with source doc, timestamp, extracted values, and approver. Full paper trail."),
    p_empty(),
    h2("Data Security"),
    bullet("Self-hosted workflow engine — orchestration runs on infrastructure the firm controls. Data does not flow through third-party automation platforms."),
    bullet("Document data stays internal — pipeline can be configured so document text never leaves the firm's environment."),
    bullet("Local model option — for firms with strict data policies, the AI extraction step can run on a locally hosted model (Llama/Mistral via Ollama) with zero external API calls."),
    divider(),

    # Tool Stack
    h1("Tool Stack"),
    h2("For Students — No Coding Required"),
    bullet("n8n", bold_prefix="Workflow orchestration: "),
    bullet("Claude or ChatGPT", bold_prefix="AI extraction and generation: "),
    bullet("Whisper", bold_prefix="Speech-to-text for voice workflows: "),
    bullet("Excel / Google Sheets", bold_prefix="Output target: "),
    p_empty(),
    h2("For Students Who Want to Go Deeper"),
    bullet("Python + openpyxl / xlwings — programmatic Excel control"),
    bullet("LlamaIndex / LangChain — advanced document parsing and RAG workflows"),
    bullet("Ollama — run local AI models with zero API costs and full data privacy"),
    p_empty(),
    h2("Why n8n Over Alternatives"),
    bullet("vs. Zapier: more powerful, more flexible for AI workflows, and self-hostable. Zapier costs more and keeps data in their cloud."),
    bullet("vs. Make: similar capabilities, but n8n has better AI node support and is open source."),
    bullet("vs. Python scripts: more accessible for non-developers, visual by design, easier to teach and debug in a classroom setting."),
    p_empty(),
    callout("The key pedagogical advantage of n8n: the workflow is visible. Students can see every step on a canvas — document in, AI extraction, validation, human review, Excel output. That transparency builds understanding and trust.", "👁️"),
    divider(),

    # Delivery Format
    h1("Proposed Delivery Format"),
    p_empty(),

    h2("Option A: AI Add-On (Recommended for Initial Rollout)"),
    p("Each Fast Track session ends with a 30-45 minute AI workflow module that maps directly to the phase covered that week. Students replicate the workflow in real time. Total addition: 4-6 hours across the 8-week cohort."),
    bullet("Minimal disruption to existing curriculum"),
    bullet("AI reinforces what was just taught"),
    bullet("Easiest to pilot and refine"),
    p_empty(),

    h2("Option B: Standalone AI Track"),
    p("A parallel 4-session AI cohort available to Fast Track graduates or as an add-on enrollment. Covers the 3 Superpowers in depth with hands-on build sessions."),
    bullet("Deeper coverage"),
    bullet("Can be priced separately"),
    bullet("Attracts working professionals who want AI skills without repeating the full Fast Track"),
    p_empty(),

    h2("Option C: Full Integration"),
    p("AI workflows embedded directly into each phase from day one. Excel and AI taught side by side throughout."),
    bullet("Most cohesive experience"),
    bullet("Best long-term positioning for the curriculum"),
    divider(),

    # Why This Works
    h1("Why This Works for CRE Analyst"),
    bullet("Deepens the value of a curriculum that is already best-in-class"),
    bullet("Creates a new revenue stream (AI module add-on or standalone track)"),
    bullet("Positions CRE Analyst as the first CRE training program to take AI seriously at the workflow level — not just mentioning it, but teaching it hands-on"),
    bullet("Gives graduates a skill set that is immediately deployable in their first job"),
    bullet("The compliance-first architecture addresses the objection that kills most AI proposals in institutional settings"),
    p_empty(),
    callout("\"We're not teaching students to trust the AI blindly. We're teaching them to build systems where accuracy is enforced and the AI is one auditable step in a human-supervised pipeline. That's the skill that will survive compliance review.\"", "💬"),
    divider(),

    # About Will
    h1("About Will Holt"),
    p("Will is a Fast Track and Valuation alum who has spent the past several years at the intersection of commercial real estate and technology. He is currently building AI workflow systems for CRE applications — including document extraction pipelines, automated financial modeling, and voice-to-model tools of the type described in this proposal."),
    p_empty(),
    p("He is not pitching a concept. He is pitching what he has already built."),
    p_empty(),
    p("His background in CRE fundamentals combined with hands-on AI implementation experience makes him uniquely suited to bridge the gap between what the Fast Track curriculum teaches and where the industry is heading."),
    divider(),
    p("This proposal is intended as a starting point for a conversation. The specific module design, delivery format, and tool choices can be adapted to fit CRE Analyst's curriculum structure, student base, and institutional requirements."),
]

# Notion API limits: 100 blocks per request
# Create the page first with the first 100 blocks, then append the rest

def chunk(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

print(f"Total blocks: {len(blocks)}")

# Step 1: Create page in DataGrove.ai database
page_body = {
    "parent": {"database_id": DATAGOVE_DB},
    "icon": {"type": "emoji", "emoji": "🏢"},
    "properties": {
        "Name": {
            "title": [{"type": "text", "text": {"content": "CREanalyst — AI-Augmented Fast Track Proposal"}}]
        }
    },
    "children": blocks[:100]
}

print("Creating page...")
result = api("POST", "/pages", page_body)
page_id = result["id"]
page_url = result.get("url", "")
print(f"✓ Page created: {page_id}")
print(f"  URL: {page_url}")

# Step 2: Append remaining blocks if any
remaining = blocks[100:]
for chunk_blocks in chunk(remaining, 100):
    print(f"Appending {len(chunk_blocks)} more blocks...")
    api("PATCH", f"/blocks/{page_id}/children", {"children": chunk_blocks})

print(f"\n✅ Done! Page URL: {page_url}")
