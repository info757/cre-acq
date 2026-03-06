#!/usr/bin/env python3
"""
Build DataGrove AI Life OS GTM Strategy + Content Calendar in Notion.
Run once to populate. Safe to re-run (creates new entries).
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
CONTENT_CAL_DB = "2f3a3175-c27b-8191-83b2-c0f9e362d143"


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


def h1(text):
    return {"object": "block", "type": "heading_1", "heading_1": {"rich_text": [{"text": {"content": text}}]}}

def h2(text):
    return {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": text}}]}}

def h3(text):
    return {"object": "block", "type": "heading_3", "heading_3": {"rich_text": [{"text": {"content": text}}]}}

def p(text):
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": text}}]}}

def p_bold(text):
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": text}, "annotations": {"bold": True}}]}}

def bullet(text):
    return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": text}}]}}

def divider():
    return {"object": "block", "type": "divider", "divider": {}}

def callout(text, emoji="💡"):
    return {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": [{"text": {"content": text}}],
            "icon": {"type": "emoji", "emoji": emoji}
        }
    }


# ─────────────────────────────────────────────
# 1. GTM STRATEGY PAGE
# ─────────────────────────────────────────────

def create_gtm_strategy():
    print("\n📄 Creating GTM Strategy page in DataGrove.ai...")

    blocks = [
        callout("AI Life OS — Go-to-Market Strategy v1 | Last updated: 2026-03-01", "🌹"),
        divider(),

        h2("🎯 The Product"),
        p("We set up a persistent-memory AI operating system (OpenClaw + n8n) for executives and operators. The AI knows who you are, remembers your deals, your contacts, your decisions, and your voice — permanently. No re-explaining. Ever."),
        p("Setup is done-for-you. The client gets a working AI assistant in days, not months."),
        divider(),

        h2("👤 ICP — Ideal Customer Profile (v1)"),
        p_bold("The Overwhelmed Operator"),
        bullet("Exec, solopreneur, or operator in Will's existing network"),
        bullet("Has tried ChatGPT/Claude — frustrated by the context reset every session"),
        bullet("Drowning in email, context-switching, and repetitive administrative work"),
        bullet("Tech-curious but not technical enough to DIY"),
        bullet("Would pay to have it 'just set up and working'"),
        bullet("Values: time, leverage, staying sharp"),
        p("Think: consultants, small business owners, CRE operators, coaches, execs from Will's cycling / Greensboro / proptech network."),
        divider(),

        h2("🪝 Positioning & Hook"),
        callout('"You\'ve tried AI. It forgot everything the next day. I set up an AI that actually knows you — your deals, your contacts, your voice. Set up once, runs forever."', "💬"),
        p_bold("The frame: We don\'t sell software. We sell labor."),
        p("A senior EA in NYC costs $80–120K/yr. This is an AI EA that never forgets anything, works 24/7, and costs 1/10th the price. Anchor pricing against human labor, NOT against ChatGPT Pro."),
        p_bold("The differentiator: Persistent memory is the moat."),
        p("Every other AI resets. Ours doesn\'t. That\'s not a feature — that\'s a fundamentally different product."),
        divider(),

        h2("💰 Pricing"),
        bullet("Setup fee: $500–$2,500 (depends on complexity, # of workflows, # of integrations)"),
        bullet("Monthly retainer: $150–$300/mo (monitoring, updates, new workflow requests)"),
        bullet("Hourly: $150–$200/hr for custom add-ons"),
        p("Initial clients from network may get a founding-partner discount (30% off setup) in exchange for feedback and a testimonial."),
        divider(),

        h2("📣 Content Channels"),
        bullet("Primary: LinkedIn (long-form posts, demos, ROI stories)"),
        bullet("Primary: X / Twitter (short hooks, threads, engagement)"),
        bullet("Secondary: YouTube (setup walkthroughs, demos — longer shelf life)"),
        p("Content strategy: Will + Zoé in action IS the demo. Real usage, not polished marketing. Authenticity is the advantage."),
        divider(),

        h2("📅 30-Day Content Strategy"),
        h3("Week 1 — The Pain"),
        p("Goal: Make people in Will\'s network say 'I feel this every day'"),
        bullet("Tweet: 'Your AI has amnesia. Every. Single. Session.'"),
        bullet("LinkedIn: 'I typed my context into ChatGPT 300+ times last year. Here\'s what I built instead.'"),
        bullet("Tweet thread: 'The problem with AI assistants isn\'t intelligence. It\'s memory.'"),
        bullet("LinkedIn: 'What if your AI already knew your deals, your team, your voice?'"),
        h3("Week 2 — The Demo"),
        p("Goal: Show, don\'t tell. The demo video is the killer piece of content."),
        bullet("Video/LinkedIn: Watch Zoé recall full context on Jason + Bandwidth with zero prompting"),
        bullet("Tweet: 'Asked my AI about a deal from last week. It remembered everything.'"),
        bullet("Tweet: 'People keep asking how I set this up. Short version:'"),
        bullet("LinkedIn: Behind the scenes — OpenClaw + n8n, how persistent memory actually works"),
        h3("Week 3 — The ROI"),
        p("Goal: Make the math undeniable"),
        bullet("LinkedIn: 'A senior EA costs $90K/yr. Here\'s what I built for under $100/mo.'"),
        bullet("Tweet: 'Time saved this week by AI with real context: 4 hours. No re-explaining. No searching.'"),
        bullet("LinkedIn: 'The hidden cost of context-switching. 50 minutes/day lost to re-explaining yourself to AI.'"),
        h3("Week 4 — The Offer"),
        p("Goal: Soft pitch to network, open the door"),
        bullet("LinkedIn: 'Setting up AI Life OS for 5 people in my network. Here\'s what\'s included.'"),
        bullet("Tweet: 'DMs open. If you want an AI that actually knows your business, let\'s talk.'"),
        bullet("Video: Full setup walkthrough — 'How I built my AI assistant in a weekend'"),
        divider(),

        h2("🔁 Inbound Lead Strategy"),
        bullet("Content drives awareness → interested people DM or comment"),
        bullet("Will responds personally (high-touch, network-first)"),
        bullet("15-min discovery call → scoped proposal → setup"),
        bullet("Testimonial collected after setup → used in next wave of content"),
        bullet("Goal: 3–5 paying clients in month 1 from network, then use their results as case studies"),
        divider(),

        h2("📊 Success Metrics (Month 1)"),
        bullet("3–5 network clients set up and paying retainer"),
        bullet("$5K–$10K in setup fees"),
        bullet("$500–$1,500/mo in recurring retainer revenue"),
        bullet("1 demo video with >500 views"),
        bullet("Net Promoter Score from clients ≥ 8/10"),
        divider(),

        h2("🚀 Next Steps"),
        bullet("[ ] Film the demo video (Will + Zoé, show persistent context in action)"),
        bullet("[ ] Write LinkedIn post #1: 'I typed my context into ChatGPT 300+ times last year'"),
        bullet("[ ] Identify 10 people in network who are the perfect first clients"),
        bullet("[ ] Draft DM outreach template for warm intro"),
        bullet("[ ] Build a simple landing page or Notion page as the 'product'"),
    ]

    body = {
        "parent": {"database_id": DATAGROVE_DB},
        "properties": {
            "Name": {"title": [{"text": {"content": "GTM Strategy — AI Life OS v1"}}]},
            "Stage": {"select": {"name": "Launch"}},
            "Description": {"rich_text": [{"text": {"content": "Go-to-market strategy for the AI Life OS service. ICP, positioning, pricing, 30-day content plan, inbound lead strategy."}}]},
        },
        "children": blocks
    }

    result = notion_request("POST", "/pages", body)
    if result:
        print(f"  ✅ GTM Strategy page created: {result['id']}")
        print(f"  🔗 {result.get('url', '')}")
    return result


# ─────────────────────────────────────────────
# 2. CONTENT CALENDAR — 30-day plan
# ─────────────────────────────────────────────

CONTENT_ITEMS = [
    # Week 1 — The Pain
    {
        "title": "Tweet: Your AI has amnesia. Every. Single. Session.",
        "type": "Tweet",
        "date": "2026-03-03",
        "status": "Idea 💡",
        "notes": "Hook post. Short and punchy. 'Your AI has amnesia. Every. Single. Session.\n\nYou re-explain your company, your deals, your team — every time you open a new chat.\n\nThere\'s a better way. 🧵'"
    },
    {
        "title": "LinkedIn: I typed my context into ChatGPT 300+ times last year",
        "type": "Blog Post",
        "date": "2026-03-04",
        "status": "Idea 💡",
        "notes": "Story-driven post. Pain → attempt → solution. Lead with frustration, end with the concept of persistent AI memory. No hard pitch yet. Goal: resonance + shares."
    },
    {
        "title": "Tweet Thread: The problem with AI isn't intelligence. It's memory.",
        "type": "Tweet",
        "date": "2026-03-06",
        "status": "Idea 💡",
        "notes": "5-tweet thread. Hook → problem → why it matters → hint at solution → CTA (follow for the demo). Designed to get retweets from the 'I feel this' crowd."
    },
    {
        "title": "LinkedIn: What if your AI already knew your deals, your team, your voice?",
        "type": "Blog Post",
        "date": "2026-03-07",
        "status": "Idea 💡",
        "notes": "Vision post. Paint the picture of what persistent AI feels like day-to-day. No product pitch — just the dream. End with 'I\'ve been building this. Demo coming next week.'"
    },

    # Week 2 — The Demo
    {
        "title": "Video: Watch my AI recall full context on a deal — no prompting",
        "type": "Video",
        "date": "2026-03-10",
        "status": "Idea 💡",
        "notes": "THE key piece of content. Screen record of Will asking Zoé about Bandwidth/Jason. She already knows everything — name, role, interview status, next steps. No explanation needed. Keep it under 90 seconds. Post to LinkedIn + X."
    },
    {
        "title": "Tweet: Asked my AI about a deal from last week. It remembered everything.",
        "type": "Tweet",
        "date": "2026-03-11",
        "status": "Idea 💡",
        "notes": "Reaction-style tweet after the video drops. 'Names. Context. Next steps. This is what AI should feel like.' Link back to the video."
    },
    {
        "title": "Tweet: How I set this up (short version)",
        "type": "Tweet",
        "date": "2026-03-13",
        "status": "Idea 💡",
        "notes": "Short thread teasing the stack: OpenClaw + n8n + structured memory files. Not a tutorial — just enough to make technical people curious and non-technical people want it done for them."
    },
    {
        "title": "LinkedIn: Behind the scenes — how persistent AI memory actually works",
        "type": "Blog Post",
        "date": "2026-03-14",
        "status": "Idea 💡",
        "notes": "Deep-dive post for the curious. Explain the architecture at a high level: session transcripts → structured memory files → vector search → instant context retrieval. Make it accessible. End with 'I set this up for people. DM me.'"
    },

    # Week 3 — The ROI
    {
        "title": "LinkedIn: A senior EA costs $90K/yr. Here's what I built for under $100/mo.",
        "type": "Blog Post",
        "date": "2026-03-17",
        "status": "Idea 💡",
        "notes": "The money post. Break down the math: EA salary vs. AI setup cost + retainer. Be specific. $90K salary + benefits = ~$120K all-in. AI Life OS = $2K setup + $300/mo = $5,600 year one. Same outcome. 20x cheaper. ROI = undeniable."
    },
    {
        "title": "Tweet: Time saved this week by AI with real context: 4 hours",
        "type": "Tweet",
        "date": "2026-03-18",
        "status": "Idea 💡",
        "notes": "Personal, authentic. 'No re-explaining. No searching for old emails. It just knew. That\'s 4 hours I got back this week.' Simple and believable."
    },
    {
        "title": "LinkedIn: The hidden cost of context-switching — 50 minutes/day lost",
        "type": "Blog Post",
        "date": "2026-03-21",
        "status": "Idea 💡",
        "notes": "Make the math visceral. 10 min lost every time you re-explain to AI. If that happens 5x/day = 50 min/day = 18,000 min/year = 300 hours = $30,000+ in lost executive time at $100/hr. That\'s the real cost."
    },

    # Week 4 — The Offer
    {
        "title": "LinkedIn: Setting up AI Life OS for 5 people in my network",
        "type": "Blog Post",
        "date": "2026-03-24",
        "status": "Idea 💡",
        "notes": "Soft launch post. What\'s included: setup, n8n automations, persistent memory, email handling, weekly check-ins. Founding member pricing. 5 spots. DM to apply. This is the conversion post."
    },
    {
        "title": "Tweet: DMs open. AI that actually knows your business.",
        "type": "Tweet",
        "date": "2026-03-25",
        "status": "Idea 💡",
        "notes": "Simple CTA tweet. No fluff. 'If you want an AI that actually knows your business — your deals, your contacts, your voice — DMs are open. 5 spots.'"
    },
    {
        "title": "Video: How I built my AI assistant in a weekend (full walkthrough)",
        "type": "Video",
        "date": "2026-03-28",
        "status": "Idea 💡",
        "notes": "Longer-form YouTube/LinkedIn video. Full setup walkthrough for the DIY audience. This builds authority + attracts people who try it and get stuck — they become clients. End with offer."
    },
]


def create_content_calendar():
    print(f"\n📅 Creating {len(CONTENT_ITEMS)} content calendar entries...")

    for item in CONTENT_ITEMS:
        props = {
            "Name": {"title": [{"text": {"content": item["title"]}}]},
            "Status": {"select": {"name": item["status"]}},
            "Type": {"select": {"name": item["type"]}},
        }
        if item.get("date"):
            props["Date"] = {"date": {"start": item["date"]}}

        body = {
            "parent": {"database_id": CONTENT_CAL_DB},
            "properties": props,
        }

        if item.get("notes"):
            body["children"] = [
                p(item["notes"])
            ]

        result = notion_request("POST", "/pages", body)
        if result:
            print(f"  ✅ {item['date']} — {item['title'][:60]}")
        else:
            print(f"  ❌ Failed: {item['title'][:60]}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("🚀 Building DataGrove AI Life OS GTM in Notion...")
    create_gtm_strategy()
    create_content_calendar()
    print("\n✅ Done! Check Notion — DataGrove.ai database + Content Calendar.")
