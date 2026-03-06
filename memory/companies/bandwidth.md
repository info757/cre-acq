# Bandwidth Inc.

**Last updated:** 2026-03-01
**Source:** bandwidth-jason-briefing.md, Agent HQ topic:3 + topic:1 (Feb 2026)

## Identity
- **Ticker:** BAND (public)
- **HQ:** Raleigh, NC
- **Description:** "The universal platform for global enterprise communications"
- **Reach:** 65+ countries, 90%+ of global economy
- **Customers:** Global 2000, hyperscalers, SaaS builders (CallRail, Microsoft Teams integrators, Dental Intelligence)
- **LinkedIn followers:** ~68,970

## Core Business (Legacy)
- Communications APIs: Voice, SMS, 911
- Sells access to owned PSTN infrastructure
- B2B: API resellers → enterprises

## Innovation Studio (New)
- **Launched:** ~May 2025
- **Team:** 7-person autonomous unit inside Bandwidth
- **Leader:** Jason Sommerset (external consultant)
- **Model:** "Startup-within-a-giant" — venture speed + corporate scale
- **Flagship:** AI Voice Agents for SMBs — white-label, B2B2B

## Product: AI Voice Receptionist Platform
- White-label AI receptionists sold to resellers (MSPs, agencies, vertical SaaS) who sell to SMBs
- Target: answer calls, book appointments, handle scheduling 24/7
- Built on **Voice AI Edge Platform** (PSTN-edge, SIP-native, sub-300ms latency)

## Technical Architecture
- **No third-party AI frameworks** (no LangGraph, LangChain, OpenAI) — all built in-house
- **Open source LLMs** self-hosted (OpenAI = ~$0.35/min, too expensive)
- **Target cost:** $0.02/minute (Jason's goal — aspirational, not yet achieved)
- **FSM approach:** LLM handles listen/speak; state machines control business logic
- **Moat:** Owns PSTN infrastructure AND AI agent layer simultaneously — impossible for VAPI/Retell/Twilio to replicate without years of infrastructure build

## Business Model Pivot
- **From:** Selling connectivity (APIs) → **To:** Selling labor (AI workers)
- Buyer shifts from IT/software budget → operations/payroll budget
- Pricing should anchor to human receptionist cost ($3–5K/mo), not API competitors ($0.05–0.33/min)

## Competitive Landscape

| Competitor | Weakness | Bandwidth Edge |
|---|---|---|
| VAPI / Retell / Bland AI | Public internet, high latency, no PSTN | Carrier edge, sub-300ms, SIP-native |
| Twilio ConversationRelay | General-purpose, no white-label SMB engine | Opinionated blueprints, zero-touch onboarding |
| DIY (n8n / Make) | Requires technical setup, not white-labelable | Turnkey for non-technical resellers |

## Market Opportunity
- US virtual receptionist market: $5.26B (2025), ~10%/yr growth
- SMBs pay $3–5K/mo for human receptionists; AI version = $150–300/mo = 10–20x ROI for buyer
- Global wage bill: ~$52–55T/yr — this is a labor replacement play, not software

## Will's Job Opportunity
- **Title:** Sr. Product Manager, AI Voice & Messaging Agents
- **Job URL:** https://job-boards.greenhouse.io/bandwidth/jobs/7613346
- **Salary:** $160k base + equity + 100% healthcare + bonus
- **Role framing:** Not founding PM — inherit built product and **launch/scale it**
- **Interview:** 2026-02-27 with Jason Sommerset — went well, ran over time
- **Status:** Jason reviewing recording before deciding next steps

## Key Vocabulary (Use When Talking About Bandwidth)
- ✅ Carrier edge, SIP-native, sub-300ms, PSTN ownership, TCR, zero-touch onboarding, knowledge ingestion, post-call eval loops, FSM
- ❌ LangGraph, LangChain, OpenAI, Claude (they don't use these — deliberate)

## Key Files
- `/Users/willholt/.openclaw/workspace/interview-prep-bandwidth.md` (+ .pdf)
- `/Users/willholt/.openclaw/workspace/bandwidth-pricing-research.md` (+ .pdf)
- `/Users/willholt/.openclaw/workspace/memory/bandwidth-jason-briefing.md` (full briefing)
