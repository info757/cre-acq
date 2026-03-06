#!/usr/bin/env python3
"""
Creates the CRE Agent Roadmap page in Notion under DataGrove.ai database.
"""
import json, urllib.request, urllib.error
from pathlib import Path

API_KEY = None
for line in Path(".env").read_text().splitlines():
    if line.startswith("NOTION_API_KEY="):
        API_KEY = line.split("=",1)[1].strip()

HEADERS = {"Authorization": f"Bearer {API_KEY}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"}
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
        print(f"ERROR: {json.loads(e.read()).get('message')}")
        return None

def h1(text):
    return {"object":"block","type":"heading_1","heading_1":{"rich_text":[{"type":"text","text":{"content":text}}]}}
def h2(text):
    return {"object":"block","type":"heading_2","heading_2":{"rich_text":[{"type":"text","text":{"content":text}}]}}
def h3(text):
    return {"object":"block","type":"heading_3","heading_3":{"rich_text":[{"type":"text","text":{"content":text}}]}}
def p(text):
    return {"object":"block","type":"paragraph","paragraph":{"rich_text":[{"type":"text","text":{"content":text}}]}}
def p_empty():
    return {"object":"block","type":"paragraph","paragraph":{"rich_text":[]}}
def bullet(text, bold_prefix=None):
    if bold_prefix:
        parts = [{"type":"text","text":{"content":bold_prefix},"annotations":{"bold":True}},{"type":"text","text":{"content":text}}]
    else:
        parts = [{"type":"text","text":{"content":text}}]
    return {"object":"block","type":"bulleted_list_item","bulleted_list_item":{"rich_text":parts}}
def divider():
    return {"object":"block","type":"divider","divider":{}}
def callout(text, emoji="💡"):
    return {"object":"block","type":"callout","callout":{"rich_text":[{"type":"text","text":{"content":text}}],"icon":{"type":"emoji","emoji":emoji}}}

blocks = [

    callout("Internal planning document. Last updated March 2026.", "📋"),
    p_empty(),
    p("The idea: build CRE-specific agents backed by an intelligence layer that encodes how the best practitioners in the industry actually think. Start in the classroom. Grow into a commercial product. End up as the most capable CRE analysis tool available anywhere."),
    p_empty(),
    p("The CREanalyst partnership is the unlock. Their curriculum, their instructors, their brand, and their graduate network are what make this defensible. Nobody else has that combination."),
    divider(),

    # PHASE 1
    h1("Phase 1: Intelligence Layer Foundation"),
    callout("Timeline: months 1-4. This runs in parallel with Phase 2, not before it.", "🗓"),
    p_empty(),
    p("The intelligence layer is what separates these agents from anything else in the market. It is a CRE-specific knowledge base that encodes not just facts but how expert practitioners reason through problems. Every agent queries it on every task."),
    p_empty(),

    h2("Knowledge Encoding, CREanalyst Partnership"),
    p("The most valuable part of the intelligence layer comes directly from CREanalyst's instructors. The process:"),
    bullet("Run structured interviews with instructors for each of the 7 Fast Track phases. One session per phase."),
    bullet("Question: walk me through exactly how you think about this type of problem from the moment you see a deal."),
    bullet("Record, transcribe, extract the reasoning sequence, structure it into a playbook."),
    bullet("Instructors review and validate. This is their expertise encoded, not ours."),
    bullet("Fast Track curriculum materials (lecture notes, case studies, worked examples) already contain most of this. Extraction and structuring is the work."),
    p_empty(),

    h2("Reasoning Frameworks to Encode (by Phase)"),
    bullet("CRE System and Capital Markets: deal flow analysis, market cycle positioning, capital stack structuring"),
    bullet("Commercial Leases: lease economics, TI negotiation logic, co-tenancy risk assessment, rent escalation structuring"),
    bullet("Valuation and Return Measures: DCF assumptions, cap rate selection by market and asset class, IRR sensitivity analysis"),
    bullet("Acquisitions and Due Diligence: DD sequencing, red flag identification, risk-adjusted pricing logic"),
    bullet("Debt: loan sizing, lender selection by deal type, coverage ratio thresholds, refinancing triggers"),
    bullet("CRE Development: site feasibility logic, construction risk underwriting, lease-up assumptions by market"),
    bullet("Joint Ventures: waterfall structuring, promote benchmarks, alignment of interest considerations"),
    p_empty(),

    h2("Data Sources for the Vector DB"),
    p("Three categories: standards and frameworks, market benchmarks, and structured data feeds."),
    p_empty(),
    h3("Standards and Frameworks (Public, Free)"),
    bullet("CREFC: commercial real estate debt standards, loan documentation guidelines"),
    bullet("BOMA: building measurement standards, operating expense definitions"),
    bullet("NAIOP: development guidelines, industrial and office market frameworks"),
    bullet("ULI: urban land use research, development best practices publications"),
    bullet("USPAP: appraisal standards and methodology (MAI frameworks)"),
    bullet("Standard lease forms: BOMA office lease, AIR industrial lease, ICSC retail forms"),
    bullet("CMBS and agency lending guidelines: Fannie, Freddie, FHA multifamily standards"),
    bullet("CREanalyst curriculum materials (with partnership agreement)"),
    p_empty(),
    h3("Market Benchmarks (Periodic Updates)"),
    bullet("CBRE, JLL, Cushman and Wakefield quarterly market reports (publicly available PDFs)"),
    bullet("MSCI and RCA transaction data summaries"),
    bullet("NCREIF performance indices and methodology"),
    bullet("RSMeans construction cost data (licensed, updated annually)"),
    bullet("CoStar market reports (licensed, highest quality but most expensive)"),
    p_empty(),
    h3("Structured Data Feeds (Live or Regular Updates)"),
    bullet("FRED (Federal Reserve): interest rates, Treasury yields, inflation, GDP, employment by MSA. Free."),
    bullet("Census and HUD: demographics, housing supply, population migration, income by market. Free."),
    bullet("CoStar API: vacancy, asking rents, absorption, cap rates by submarket. Licensed, premium cost."),
    bullet("MSCI RCA: transaction comps, cap rate trends by asset class. Licensed."),
    p_empty(),

    h2("Technical Architecture"),
    bullet("Embedding model: text-embedding-3-small (OpenAI) or equivalent for converting documents to vectors"),
    bullet("Vector store: pgvector (self-hosted, free, solid for this scale) or Pinecone (managed, scalable)"),
    bullet("RAG pipeline: LlamaIndex or LangChain for chunking, indexing, and retrieval"),
    bullet("Query layer: REST API endpoint that agents call with their question and get relevant context back"),
    bullet("Update pipeline: new documents and market data ingested on a schedule (weekly or monthly depending on source)"),
    divider(),

    # PHASE 2
    h1("Phase 2: Fast Track Agents"),
    callout("Timeline: months 2-5. These are the proof of concept and the distribution channel.", "🗓"),
    p_empty(),
    p("Seven purpose-built agents, one per Fast Track phase. Students use them in class to handle the data entry layer on their coursework. Simple, reliable, and directly mapped to the CREanalyst Excel templates students already know."),
    p_empty(),

    h2("The Seven Agents"),
    bullet("Phase 1 Agent, CRE System and Capital Markets: builds deal tracking dashboard from natural language, synthesizes market data into memo draft"),
    bullet("Phase 2 Agent, Commercial Leases: reads a lease, extracts key terms, populates abstraction template, enables multi-lease comparison"),
    bullet("Phase 3 Agent, Valuation and Return Measures: extracts NOI, cap rate, occupancy, and expense data from an OM, populates valuation model"),
    bullet("Phase 4 Agent, Acquisitions and DD: reviews uploaded DD documents against standard checklist, flags gaps and summarizes findings"),
    bullet("Phase 5 Agent, Debt: takes plain-language deal description, returns structured loan scenario comparison"),
    bullet("Phase 6 Agent, Development: takes voice or text assumptions, populates development pro forma inputs"),
    bullet("Phase 7 Agent, Joint Ventures: reads JV agreement, explains waterfall structure in plain language. v1 explanation only, v2 model mapping."),
    p_empty(),

    h2("How It Works in the Classroom"),
    bullet("Each agent is pre-configured and handed to students the same way they receive Excel templates today"),
    bullet("Student uploads a document or types assumptions, agent extracts and structures the data, student reviews and approves, n8n writes to Excel template"),
    bullet("No black boxes. Student sees every step and owns the data before it touches the model."),
    bullet("Fallback: if a student cannot deploy their own agent, a working version is always available so coursework keeps moving"),
    p_empty(),

    h2("Education Agent"),
    p("A separate agent pre-loaded with the Fast Track curriculum that guides students through building and configuring their own agents. Available 24/7. Knows exactly where in the setup process a student is likely to be stuck and walks them through it conversationally."),
    p_empty(),

    h2("Phase 2 Intelligence Layer Connection"),
    p("Agents in Phase 2 connect to a v1 knowledge base, the standards and curriculum materials from the vector DB. Market benchmark data and live feeds come in Phase 3 and 4. Even v1 produces noticeably better analysis than a general-purpose model with no CRE context."),
    divider(),

    # PHASE 3
    h1("Phase 3: Commercial CRE Agents"),
    callout("Timeline: months 6-12. Same agents, graduated from classroom to commercial product.", "🗓"),
    p_empty(),
    p("The agents students use in Fast Track become available as a commercial subscription. CREanalyst brand on the product. Will and DataGrove build and maintain the backend. Revenue split on subscriptions sourced through the CREanalyst graduate network."),
    p_empty(),

    h2("Who Buys This"),
    bullet("Fast Track graduates entering the workforce who want to keep using the tools"),
    bullet("Working CRE professionals who hear about it through the CREanalyst network"),
    bullet("Small to mid-size investment firms and developer teams looking for a practical AI workflow tool"),
    p_empty(),

    h2("Pricing Tiers"),
    bullet("Individual: $99-149/month. Cloud-based, enterprise AI data agreements, personal use."),
    bullet("Team: $500-1,500/month. Multi-user, firm-level audit logs, admin controls."),
    bullet("How students get it: same pre-configured agents from class, now available with a subscription. No new learning curve."),
    p_empty(),

    h2("The CREanalyst Brand Advantage"),
    p("This is not a generic AI tool marketed into CRE. It is a product built on the CREanalyst knowledge base, carrying their name, and sold to people who already trust that name because it trained them. That is a distribution and credibility advantage that cannot be replicated by a startup coming in cold."),
    p_empty(),

    h2("Phase 3 Intelligence Layer"),
    p("Market benchmark data is added. Agents now answer questions with current cap rate context, rent benchmark data, and debt pricing benchmarks by market. Analysis quality takes a meaningful step up from Phase 2."),
    divider(),

    # PHASE 4
    h1("Phase 4: CRE Super Agents"),
    callout("Timeline: months 12-24. The full vision. Agents plus intelligence layer plus proprietary firm data.", "🗓"),
    p_empty(),
    p("The Super Agent is what happens when the full intelligence layer is live and each client's own deal history becomes part of the model's context. The agent does not just know CRE broadly, it knows this firm's specific deals, their underwriting assumptions, their market preferences, and their historical performance. That is not something any competitor can replicate because it is built from data only that firm has."),
    p_empty(),

    h2("What Makes a Super Agent"),
    bullet("All seven agents fully connected to the complete intelligence layer"),
    bullet("RAG on the client's own deal history, past OM analyses, past DD packages, closed transaction data"),
    bullet("Expert reasoning frameworks fully encoded from CREanalyst instructor interviews"),
    bullet("Live market data feeds connected (cap rates, rents, construction costs, debt pricing)"),
    bullet("The model answers questions the way a senior analyst at that specific firm would answer them"),
    p_empty(),

    h2("Security Tiers for Enterprise"),
    bullet("Cloud tier: frontier model (Claude or GPT-5.2), enterprise data agreements, no data used for training"),
    bullet("Private deployment tier: agents and intelligence layer run on client's own infrastructure, no data leaves their environment, local open source model option available"),
    bullet("Same agents, same intelligence layer, different model and hosting based on the client's compliance requirements"),
    p_empty(),

    h2("IaaS, Intelligence as a Service"),
    p("The intelligence layer becomes its own product. Other CRE developers and tool builders can query it via API to improve their own applications. CREanalyst-branded, priced per query or per seat. This is the platform play that turns DataGrove from a services business into something with compounding network value."),
    p_empty(),

    h2("Phase 4 Intelligence Layer"),
    p("Complete knowledge base: standards, frameworks, market data, live feeds, and fully encoded expert reasoning from CREanalyst instructors. Possibly a fine-tuned open source model layer for firms that want full data control and are willing to accept a slightly lower quality ceiling. The combination of the intelligence layer and the proprietary firm data makes this the most capable CRE analysis capability available."),
    divider(),

    # Summary
    h1("The Through-Line"),
    p("Phase 2 proves the concept in the classroom and builds the distribution channel. Phase 3 monetizes what Phase 2 created. Phase 4 adds the intelligence layer that makes the product genuinely hard to compete with. The CREanalyst partnership is the thing that makes all of it defensible, because it gives us the expert knowledge, the brand, and the graduate network that nobody else can replicate."),
    p_empty(),
    p("The James conversation is about Phase 2 and 3. Phase 4 is the vision you share to show where this is going."),

]

print(f"Total blocks: {len(blocks)}")

# Chunk into 100-block batches
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

page_body = {
    "parent": {"database_id": DATAGOVE_DB},
    "icon": {"type": "emoji", "emoji": "🧠"},
    "properties": {
        "Name": {"title": [{"type":"text","text":{"content":"CRE Agent Roadmap, Intelligence Layer to Super Agents"}}]}
    },
    "children": blocks[:100]
}

print("Creating page...")
result = api("POST", "/pages", page_body)
page_id = result["id"]
page_url = result.get("url","")
print(f"Page created: {page_url}")

remaining = blocks[100:]
after_id = None
for chunk in chunks(remaining, 100):
    print(f"Appending {len(chunk)} blocks...")
    body = {"children": chunk}
    r = api("PATCH", f"/blocks/{page_id}/children", body)
    if r:
        results = r.get("results",[])
        if results:
            after_id = results[-1]["id"]

print(f"\nDone. {page_url}")
