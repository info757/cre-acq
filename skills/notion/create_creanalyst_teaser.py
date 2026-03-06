#!/usr/bin/env python3
"""
Creates a short teaser page for CREanalyst — humble, conversation-starting tone.
Separate from the planning doc.
"""
import json
import urllib.request
import urllib.error
from pathlib import Path

ENV_PATH = Path(__file__).parent / ".env"
API_KEY = None
if ENV_PATH.exists():
    for line in ENV_PATH.read_text().splitlines():
        if line.startswith("NOTION_API_KEY="):
            API_KEY = line.split("=", 1)[1].strip()

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
        print(f"ERROR {e.code}: {err.get('message', str(err))}")
        return None


def h1(text):
    return {"object":"block","type":"heading_1","heading_1":{
        "rich_text":[{"type":"text","text":{"content":text}}]}}

def h2(text):
    return {"object":"block","type":"heading_2","heading_2":{
        "rich_text":[{"type":"text","text":{"content":text}}]}}

def p(text):
    return {"object":"block","type":"paragraph","paragraph":{
        "rich_text":[{"type":"text","text":{"content":text}}]}}

def p_rich(parts):
    """parts = list of (text, bold) tuples"""
    rich = []
    for text, bold in parts:
        part = {"type":"text","text":{"content":text}}
        if bold:
            part["annotations"] = {"bold": True}
        rich.append(part)
    return {"object":"block","type":"paragraph","paragraph":{"rich_text": rich}}

def p_empty():
    return {"object":"block","type":"paragraph","paragraph":{"rich_text":[]}}

def bullet(text, bold_prefix=None):
    if bold_prefix:
        parts = [
            {"type":"text","text":{"content":bold_prefix},"annotations":{"bold":True}},
            {"type":"text","text":{"content":text}}
        ]
    else:
        parts = [{"type":"text","text":{"content":text}}]
    return {"object":"block","type":"bulleted_list_item","bulleted_list_item":{"rich_text":parts}}

def divider():
    return {"object":"block","type":"divider","divider":{}}

def callout(text, emoji="💡"):
    return {"object":"block","type":"callout","callout":{
        "rich_text":[{"type":"text","text":{"content":text}}],
        "icon":{"type":"emoji","emoji":emoji}}}


blocks = [

    callout("From Will Holt, Fast Track and Valuation alum. Sharing an idea, would love your reaction.", "👋"),
    p_empty(),

    p("I have been experimenting with AI workflow tools over the past several months, and one idea keeps coming back to me: how much of the manual work students do inside the Fast Track Excel templates could be handled by a purpose-built AI agent."),
    p_empty(),
    p("I wanted to share the concept and see if it is something worth exploring together. This is very much an early conversation, not a finished proposal."),
    divider(),

    h1("The Idea"),
    p("What if each Fast Track phase came with a small AI agent, pre-configured for that phase, that handles the data entry layer? Students would still work in the same Excel templates. The agent would just take care of extracting and populating the inputs, so students spend their time on the analysis rather than the transcription."),
    p_empty(),
    p("The workflow is straightforward. A student uploads a document or describes their deal assumptions. The agent extracts the relevant data, structured and cited back to the source. The student reviews it. Then a simple automation tool called n8n takes that clean output and writes it directly into the Excel template."),
    p_empty(),
    p("No black boxes. The student sees every step and approves the data before it touches the model."),
    divider(),

    h1("One Agent Per Phase"),
    p("Each agent would be tuned to the specific work of that phase, using the CREanalyst template structure as its guide."),
    p_empty(),

    bullet("CRE System and Capital Markets: builds a deal tracking dashboard from a plain-language description, and synthesizes market comp data into a memo draft"),
    bullet("Commercial Leases: reads a lease and extracts the key terms into the abstraction template, base rent, escalations, TI, options, expirations"),
    bullet("Valuation and Return Measures: pulls NOI, cap rate, occupancy, and expense data from an offering memorandum and populates the valuation model inputs"),
    bullet("Acquisitions and Due Diligence: reviews uploaded documents against a due diligence checklist, flags gaps, and summarizes findings"),
    bullet("Debt: takes a plain-language description of a deal and returns a structured loan scenario comparison"),
    bullet("CRE Development: takes voice or typed assumptions and builds the development pro forma inputs"),
    bullet("Joint Ventures: reads a JV agreement and explains the waterfall structure in plain language, tier by tier"),
    divider(),

    h1("A Few Things Worth Discussing"),
    p("I have a lot of questions and would genuinely value your perspective on whether this fits how students learn and what would make it useful rather than just interesting."),
    p_empty(),
    bullet("How closely do students follow the templates today, and would pre-populated inputs help or short-circuit the learning?"),
    bullet("What would compliance and data handling need to look like for this to be viable in a professional setting after graduation?"),
    bullet("Is there a version of this that fits naturally into the existing curriculum, or does it need its own space?"),
    p_empty(),
    p("Happy to walk through a live demo of any of the workflows if that would be a useful next step."),
    divider(),

    p("Thanks for taking a look. I am proud of what Fast Track taught me and would love to find a way to contribute something back."),
    p_empty(),
    p("Will Holt"),

]

print(f"Total blocks: {len(blocks)}")

page_body = {
    "parent": {"database_id": DATAGOVE_DB},
    "icon": {"type": "emoji", "emoji": "✉️"},
    "properties": {
        "Name": {
            "title": [{"type": "text", "text": {"content": "CREanalyst Teaser, For Sending"}}]
        }
    },
    "children": blocks
}

print("Creating teaser page...")
result = api("POST", "/pages", page_body)
page_id = result["id"]
page_url = result.get("url", "")
print(f"Done. URL: {page_url}")
