# MEMORY.md - Long-Term Memory

<!--
SECURITY NOTE: This file contains personal information.
Only loaded in direct/main sessions with Will — NOT in group chats.
-->

## 🗂️ Memory Index (Entity Files)

All detailed entity context lives in structured files — searchable via memory_search.

### People
- `memory/people/jason-sommerset.md` — Bandwidth hiring manager, consultant at Galleon Strategies
- _(add more as they come up)_

### Companies
- `memory/companies/bandwidth.md` — Bandwidth Inc. (BAND), AI Voice Agents, Will's job opportunity
- _(add more as they come up)_

### Briefings
- `memory/bandwidth-jason-briefing.md` — Full deep-dive on Bandwidth + Jason (Feb 2026)

### Daily Notes
- `memory/2026-02-26.md` — First awakening
- `memory/2026-02-28.md` — Morning Big 3, Will's background (athlete, cyclist, Mia, Dusty)
- _(new file each day)_

---

## First Awakening

- **Date:** 2026-02-26
- **AI Name:** Zoé 🌹
- **Human:** Will Holt
- Initial setup completed

---

## About Will

- **Age:** 53
- **Location:** Greensboro, NC area
- **Athletic background:** College soccer; all-state soccer + basketball in high school
- **Competitive cyclist:** 25 years; road biking 5–6x/week, non-negotiable
- **Other sports:** Backcountry skiing, heli-skiing, hiking
- **Coaching:** Coaches daughter Mia's (14) soccer team — being near Greensboro matters
- **Health:** Worn hip needing replacement — still training strong regardless
- **Dog:** Dusty
- **Relationship:** Divorced ~1 year ago

---

## Financial Context (Private)

- Took a significant investment loss
- High living expenses + expensive health insurance
- ~1 year of runway as of Feb 2026
- Lease ends end of May 2026 — opportunity to reduce expenses
- A job would stabilize finances; DataGrove is the longer play
- The Bandwidth offer (salary + 100% healthcare) would meaningfully relieve financial pressure

---

## Agent HQ — Telegram Group

- **Chat ID:** -1003783443203
- **Topic 1:** General
- **Topic 2:** Code and Dev
- **Topic 3:** Research
- **Topic 4:** Content
- **Topic 5:** Automations
- **Topic 6:** 📥 Saves
- **Topic 7:** 💕 Girls (dating life)
- Bot: @Holt_ai_bot (ID: 8453434126)
- Group policy: allowlist; requireMention: false

---

## Saves System (📥 Topic 6)

- **Topic:** "📥 Saves" — Telegram topic ID 103 in Agent HQ
- **Purpose:** Will drops links here when he can't engage immediately
- **My job:** Auto-fetch + summarize every link, no need to ask
- **Log file:** `reading-list.md` in workspace
- **Periodic:** Surface themes/patterns across saved items during heartbeats or on demand

---

## Ongoing Projects

### DataGrove.ai — Will's Business
- **Stage:** GTM strategy being developed (2026-03-01)
- **Current idea:** "AI Life OS" service — set up OpenClaw + n8n for executives/individuals wanting persistent-memory AI automation
- **Evolution path:** Individual setups → exec "teams" of AI agents → enterprise systems
- **Pricing thinking:** $500–2500 setup fee | monthly retainer (monitoring/upgrades) | $150–200/hr add-ons
- **Content strategy:** LinkedIn, X, YouTube — use Will + Zoé setup as the live demo
- **Key appeal:** Lean team, fast revenue, no product build required
- **Differentiator:** Persistent memory + context IS the moat — nobody else does this at depth
- **Stack question:** OpenClaw vs BMAD still being evaluated
- **Next:** Develop content strategy (2026-03-01 agenda item)

### CRE Acquisitions Platform — Internal BMAD Build
- **Status:** Stage 1 OM Screener build in progress (started 2026-03-04)
- **Architecture:** BMAD Phase 3 (Solutioning) — strict discipline on testing, code review, no advancement until Tested
- **Build order:** Week 1 (Days 1-5) ingestion → merge → human review gate
- **Progress:** Days 1-3 complete and shipped to TESTED status (2026-03-05)
  - Ingestion layer: discover_inputs.py, parse_excel.py, extract_text.py, ocr_pdf.py (70 tests passing)
  - Merge layer: merge_inputs.py, om-extractor.md prompt, test_merge.py (23 tests passing)
- **Next:** Day 4-5 human review gate (format_review_message.py, apply_corrections.py), then scoring & output
- **Sample data:** Mill One (multifamily, stabilized), Navaho Drive (pref equity, lease-up, different deal type)
- **Key insight:** Prompt generalizes across deal types — correctly identifies when metrics absent
- **Stack:** Python (pdfplumber, Tesseract OCR, pandas/openpyxl for Excel), Claude API, n8n for orchestration

### CREanalyst — Exploratory, NOT a partnership
- Will has been commenting on CREanalyst's LinkedIn posts, getting traction
- Meeting with founder **James** expected within the next week or so — purely exploratory
- **No partnership, no commitment on either side**
- If it develops into paid work (AI module for Fast Track), great — but don't assume it

### Bandwidth Job — Running Simultaneously
- Interview with **Jason Sommerset** — 2026-02-27
- Went well; ran over time (positive signal)
- Jason is reviewing the recording; next steps TBD
- **See:** `memory/companies/bandwidth.md` and `memory/people/jason-sommerset.md`
- **Decision still open:** Bandwidth job vs. doubling down on DataGrove
- **Action:** Follow up with Jason; Will promised to talk to resellers about pricing

### Email + Outbound Setup
- n8n send-email workflow working (webhook: localhost:5678)
- Approval queue live: `.outbound-queue/queue.sh`
- Approval bot: @Holt_ai_bot, run via `.outbound-queue/run-approval-bot.sh`
- Inbox reading: ideas saved in `memory/inbox-reading-ideas.md` — needs n8n workflow

---

## Preferences & Decisions

- **Memory discipline:** Write to daily file at end of every meaningful session. No mental notes.
- **Group chats:** Don't share Will's private context. Participate like a human, not a proxy.
- **External actions:** Always queue for approval. Never send anything without Will confirming.
- **Exercise:** Non-negotiable for Will — never schedule over it, always respect it.

---

## Lessons Learned

- **2026-03-01:** Session context doesn't cross Telegram topics automatically. If something important happens in Research (topic:3), General (topic:1) won't know unless I write it to memory. Write it down!
- **2026-03-01:** OpenClaw's `memory_search` already uses vector search (OpenAI text-embedding-3-small, hybrid mode). The lever is *writing good notes*, not building new infra.
- **2026-03-01:** Sub-agents can time out on large JSONL files. Use grep-first extraction strategies for files >500K.

---

## Important Dates

- **2026-02-27:** Will's interview at Bandwidth with Jason Sommerset
- **2026-05-xx:** Will's lease ends — financial reset opportunity

---
*Last updated: 2026-03-01 by Zoé 🌹*
