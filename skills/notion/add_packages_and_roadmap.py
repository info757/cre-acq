#!/usr/bin/env python3
"""
1. Append Packages section to the GTM Strategy page
2. Create a Build + Content Roadmap page in DataGrove.ai database
"""

import json
import urllib.request
import urllib.error
from pathlib import Path

ENV_PATH = Path(__file__).parent / ".env"
key = [l.split("=", 1)[1].strip() for l in ENV_PATH.read_text().splitlines() if l.startswith("NOTION_API_KEY=")][0]

HEADERS = {
    "Authorization": f"Bearer {key}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

DATAGROVE_DB = "2f3a3175-c27b-8001-a173-dfc7a7c47653"
GTM_PAGE_ID  = "316a3175-c27b-81a6-90b8-c8f1cf04a626"


def notion_request(method, path, body=None):
    url = f"https://api.notion.com/v1{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err = json.loads(e.read())
        print(f"  ERROR {e.code}: {err.get('message', str(err))}")
        return None

def h2(text):
    return {"object":"block","type":"heading_2","heading_2":{"rich_text":[{"text":{"content":text}}]}}
def h3(text):
    return {"object":"block","type":"heading_3","heading_3":{"rich_text":[{"text":{"content":text}}]}}
def p(text):
    return {"object":"block","type":"paragraph","paragraph":{"rich_text":[{"text":{"content":text}}]}}
def p_bold(text):
    return {"object":"block","type":"paragraph","paragraph":{"rich_text":[{"text":{"content":text},"annotations":{"bold":True}}]}}
def bullet(text):
    return {"object":"block","type":"bulleted_list_item","bulleted_list_item":{"rich_text":[{"text":{"content":text}}]}}
def divider():
    return {"object":"block","type":"divider","divider":{}}
def callout(text, emoji="💡"):
    return {"object":"block","type":"callout","callout":{"rich_text":[{"text":{"content":text}}],"icon":{"type":"emoji","emoji":emoji}}}


# ─────────────────────────────────────────────
# 1. APPEND PACKAGES TO GTM PAGE
# ─────────────────────────────────────────────

def append_packages():
    print("\n📦 Appending Packages to GTM Strategy page...")

    blocks = [
        divider(),
        h2("📦 Service Packages"),
        callout("Framed as labor, not software. Price against a human EA ($80–120K/yr), not ChatGPT Pro ($20/mo).", "💰"),

        h3("Package 1 — The Assistant | $750 setup · $200/mo"),
        p("Your always-on AI that handles the daily grind."),
        bullet("OpenClaw setup + Telegram (command center)"),
        bullet("Persistent memory — knows contacts, deals, context permanently"),
        bullet("Email drafting queue (approval-gated, nothing sends without you)"),
        bullet("Daily briefings — calendar, urgent emails, priorities"),
        bullet("On-demand web research"),
        bullet("Heartbeat check-ins (2x/day proactive nudges)"),
        p("Best for: Solopreneurs, consultants, busy operators drowning in email + context-switching."),

        h3("Package 2 — Chief of Staff | $1,500 setup · $350/mo"),
        p("Everything in Package 1, plus choose 3 add-on agents:"),
        bullet("📝 Notes/Knowledge agent (Notion or Obsidian)"),
        bullet("📋 Task agent (Things 3 or Apple Reminders)"),
        bullet("🔍 Research agent (scheduled intel, blog monitoring, summarized)"),
        bullet("📣 Content agent (drafts LinkedIn + X posts, queued for approval)"),
        bullet("🎙️ Voice agent (meetings → structured notes → memory)"),
        p("Best for: Executives and founders running multiple priorities simultaneously."),

        h3("Package 3 — Full OS | $2,500 setup · $500/mo"),
        p("Everything in Packages 1 + 2, plus:"),
        bullet("All add-on agents installed and configured (no picking)"),
        bullet("Custom n8n workflows built for YOUR specific business"),
        bullet("GitHub / dev workflow integration (if applicable)"),
        bullet("Social media agent (post, monitor, engage on X + LinkedIn)"),
        bullet("Monthly optimization call — tune, expand, improve"),
        bullet("Priority support (24hr response vs. async)"),
        p("Best for: High-output founders and execs who want maximum leverage, zero manual setup."),

        h3("🔄 Rental Agents (any tier, any time)"),
        bullet("Accounting Agent (tax season) — $150/week"),
        bullet("Due Diligence / Research Agent — $200/week"),
        bullet("Launch Agent (product or campaign) — $300/week"),
        bullet("Hiring Agent (job posting, resume screening) — $200/week"),
    ]

    result = notion_request("PATCH", f"/blocks/{GTM_PAGE_ID}/children", {"children": blocks})
    if result:
        print(f"  ✅ Packages appended to GTM page")
    return result


# ─────────────────────────────────────────────
# 2. BUILD + CONTENT ROADMAP PAGE
# ─────────────────────────────────────────────

def create_roadmap():
    print("\n🗺️  Creating Build + Content Roadmap page...")

    blocks = [
        callout("Strategy: Build each agent/skill on Will's own system first. Document everything. Content = expertise + evergreen marketing.", "🌹"),
        p("For each agent: implement it → use it → document the setup → create content. By the time we sell, Will is the expert and has the proof."),
        divider(),

        h2("🏗️ Build Order + Content Map"),
        p("Ordered by: impact on Will's daily life first, then sellability."),
        divider(),

        # TIER 1 — FOUNDATION
        h3("Tier 1 — Foundation (Build First)"),
        p("These are already live or nearly live. Document and create content NOW."),

        p_bold("✅ 1. Persistent Memory System"),
        bullet("What: Entity files, daily notes, vector search — AI that remembers everything"),
        bullet("Status: LIVE (built 2026-03-01)"),
        bullet("Content: 'I solved AI amnesia' — LinkedIn post + demo video"),
        bullet("Demo: Ask Zoé about Jason Sommerset cold — she knows everything"),

        p_bold("✅ 2. Email Drafting + Approval Queue"),
        bullet("What: AI drafts emails, you approve in Telegram before anything sends"),
        bullet("Status: LIVE (n8n + outbound queue)"),
        bullet("Content: 'My AI writes my emails but can't send without me' — the trust architecture post"),
        bullet("Demo: Show draft → approve flow in Telegram"),

        p_bold("✅ 3. Notion Integration"),
        bullet("What: AI reads, writes, updates Notion databases directly"),
        bullet("Status: LIVE"),
        bullet("Content: 'How I use AI to run my entire knowledge base'"),
        bullet("Demo: 'I said go, Zoé built an entire GTM strategy in Notion in 3 minutes'"),
        divider(),

        # TIER 2 — CHIEF OF STAFF LAYER
        h3("Tier 2 — Chief of Staff Layer (Build Next)"),

        p_bold("⬜ 4. Calendar Agent (Google Calendar via gog)"),
        bullet("What: AI reads calendar, gives daily briefings, flags conflicts, suggests scheduling"),
        bullet("Status: Not yet configured"),
        bullet("Content: 'My AI reads my calendar every morning and tells me what matters'"),
        bullet("Demo: Morning briefing video — Zoé summarizes the day unprompted"),

        p_bold("⬜ 5. Gmail Agent (full inbox)"),
        bullet("What: AI reads inbox, prioritizes, drafts responses, archives noise"),
        bullet("Status: Partial (send works, full inbox read needs gog setup)"),
        bullet("Content: 'I haven't opened my email app in 3 days. Here's what I did instead.'"),
        bullet("Demo: Inbox zero via AI — show the before/after"),

        p_bold("⬜ 6. Task Agent (Things 3 or Apple Reminders)"),
        bullet("What: AI captures tasks from conversation, manages due dates, morning task brief"),
        bullet("Status: Not configured"),
        bullet("Content: 'I stopped using a task app. My AI just... knows what I need to do.'"),
        bullet("Demo: Mid-conversation task capture — Will mentions something → Zoé logs it"),

        p_bold("⬜ 7. Voice / Meeting Transcription Agent (Whisper)"),
        bullet("What: Record a meeting → Whisper transcribes → Zoé extracts decisions + action items → saves to memory"),
        bullet("Status: Not configured"),
        bullet("Content: 'Every meeting I have ends up in my AI's long-term memory automatically'"),
        bullet("Demo: Drop a voice memo → get structured notes + next steps"),
        divider(),

        # TIER 3 — CONTENT + SOCIAL
        h3("Tier 3 — Content & Social Layer"),

        p_bold("⬜ 8. Content Agent (X + LinkedIn)"),
        bullet("What: Will drops an idea → Zoé drafts a post → approval queue → scheduled post"),
        bullet("Status: Not configured (xurl skill available)"),
        bullet("Content: 'My AI writes and posts my content. I just approve it.'"),
        bullet("Demo: Idea → polished LinkedIn post in 60 seconds"),

        p_bold("⬜ 9. Research Agent (web search + summarize + memory write)"),
        bullet("What: Scheduled competitive intel, blog monitoring, news digests written to memory"),
        bullet("Status: Partial (web search live, scheduling needed)"),
        bullet("Content: 'Every morning my AI reads the internet and tells me what matters to MY business'"),
        bullet("Demo: Morning intel briefing — industry news, competitor moves, relevant content"),
        divider(),

        # TIER 4 — POWER / RENTAL AGENTS
        h3("Tier 4 — Power / Rental Agents (Build for Product)"),

        p_bold("⬜ 10. Accounting Agent"),
        bullet("What: Parse invoices, categorize expenses, tax prep support, export to CSV"),
        bullet("Status: Not built (exec + file parsing capability exists)"),
        bullet("Content: 'I rented an accounting agent for tax season. It cost $150. My CPA was shocked.'"),
        bullet("Seasonal: April = tax season launch"),

        p_bold("⬜ 11. Due Diligence / Research Agent"),
        bullet("What: Deep research on a person, company, or deal — structured report output"),
        bullet("Status: Partial (we built the Bandwidth briefing this way)"),
        bullet("Content: 'Before every important meeting, my AI gives me a 10-page brief on who I'm meeting'"),
        bullet("Demo: The Jason Sommerset briefing — built from 1MB of transcripts in 10 min"),

        p_bold("⬜ 12. Hiring Agent"),
        bullet("What: Write job posts, screen resumes, schedule interviews, track candidates"),
        bullet("Status: Not built"),
        bullet("Content: 'I hired someone and my AI did 80% of the work'"),
        divider(),

        h2("📣 Content Creation Rhythm"),
        p("For each agent we build: implement it → use it for 1 week → document the setup → create 2 pieces of content (1 LinkedIn, 1 tweet/thread)."),
        bullet("LinkedIn: Story-driven. Pain → attempt → solution. Real numbers."),
        bullet("X/Twitter: Hook + thread. Punchy. Designed for shares."),
        bullet("Every 3rd agent: short video demo. Under 90 seconds. Real usage, no polish."),
        bullet("Goal: by the time we have 10 agents built, we have 20+ pieces of evergreen content."),
        divider(),

        h2("🎯 Content Themes (Evergreen)"),
        bullet("'Your AI has amnesia. Mine doesn't.' — memory series"),
        bullet("'I rented a [X] agent for a week' — rental agent series"),
        bullet("'My AI vs. a human [role]' — labor comparison series"),
        bullet("'Here's what my AI did while I was on a bike ride' — proactive AI series"),
        bullet("'Setup Saturday' — behind-the-scenes build content"),
    ]

    body = {
        "parent": {"database_id": DATAGROVE_DB},
        "properties": {
            "Name": {"title": [{"text": {"content": "Build + Content Roadmap — AI Life OS"}}]},
            "Stage": {"select": {"name": "Launch"}},
            "Description": {"rich_text": [{"text": {"content": "Implementation order for each agent/skill on Will's system, mapped to content pieces. Build it → use it → document it → publish it."}}]},
        },
        "children": blocks
    }

    result = notion_request("POST", "/pages", body)
    if result:
        print(f"  ✅ Build + Content Roadmap created: {result['id']}")
        print(f"  🔗 {result.get('url','')}")
    return result


if __name__ == "__main__":
    print("🚀 Updating Notion with Packages + Build Roadmap...")
    append_packages()
    create_roadmap()
    print("\n✅ Done!")
