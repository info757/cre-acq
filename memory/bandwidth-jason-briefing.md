# Bandwidth + Jason Briefing
*Long-term memory for Zoé | Compiled from session transcripts, Feb 2026*

---

## Who is Jason?

**Full name:** Jason Sommerset
**LinkedIn:** https://www.linkedin.com/in/jasonsommerset/
**Current company:** Galleon Strategies (independent consultant)
**Current role:** Independent Consultant, Product Strategy & Leadership

**Career history at Bandwidth:**
- Director of Product Development
- Senior Director, Product Management
- VP Product Management
- GM/SVP of Product Management (highest level)
- Nearly a decade at Bandwidth total

**After Bandwidth:**
- Also served as Head of Product at Diveplane
- Now runs Galleon Strategies as an independent consultant

**Work arrangement for this hire:** Jason works **fully remote from Mosier, Oregon** (~3,000 miles from Bandwidth HQ in Raleigh, NC). He was brought in as an external consultant to run Bandwidth's Innovation Studio team (autonomous 7-person team inside Bandwidth). The JD's Raleigh language is likely boilerplate, not a hard requirement.

**Personality / interview style:**
- Thinks like a founder-operator, not a corporate gatekeeper
- Values directness, product intuition, execution speed, and technical depth
- He built the Bandwidth product culture — evaluates candidates against standards he personally set
- He is sophisticated and will not be fooled by buzzword soup
- At the end of the interview with Will, he said he would review the recording and then decide about moving to next steps

**Testimonials about Jason (from LinkedIn search snippet):**
> "If you are lucky enough to have worked with Jason, then you just know. I had the honor and privilege of working for Jason for 3 years at Bandwidth and during that time I learned more from him than I will ever be able to repay."

---

## What is Bandwidth?

**Company:** Bandwidth Inc. (BAND — publicly traded)
**Headquarters:** Raleigh, NC
**Type:** Global software/communications company
**Description:** "The universal platform for global enterprise communications." Bandwidth helps enterprises deliver voice, messaging, and emergency services. Reaches 65+ countries and 90%+ of the global economy. Trusted by the Global 2000, hyperscalers, and SaaS builders.

**Prior recognition:** "Best of EC" award winner. ~68,970 LinkedIn followers.

**Core business model (existing):**
- Sells communications APIs (Voice, SMS, 911) to enterprise resellers
- Customers include CallRail, Microsoft Teams integrators, Dental Intelligence, and others
- The "connectivity" business: charging for access to Bandwidth's owned PSTN infrastructure

**The Innovation Studio:**
- Launched approximately 9 months before February 2026 (i.e., around May 2025)
- Described internally as a "startup-within-a-giant" — operates at venture team speed using Bandwidth's global scale
- 7-person autonomous team
- Flagship initiative: AI Voice Agents for SMBs
- Jason Sommerset is the external consultant leading this team

**Key product in development:**
- **AI Voice Receptionist / Agent Platform** — white-label, B2B2B model
- Resellers (MSPs, agencies, vertical SaaS companies like Dental Intelligence) deploy branded AI receptionists to their SMB clients
- SMBs get an AI that answers calls, books appointments, handles scheduling 24/7
- Built on Bandwidth's **Voice AI Edge Platform** (PSTN-edge deployed, SIP-native, sub-300ms latency)

**Technical architecture (as revealed by Jason in the interview):**
- **No third-party AI frameworks** — building all orchestration in-house (no LangGraph, no LangChain, no OpenAI)
- **Open source LLMs** self-hosted — because OpenAI would cost ~$0.35/min, which is too expensive
- **Target infrastructure cost:** $0.02/minute (Jason's stated goal, currently aspirational not achieved)
- The custom stack runs at the PSTN carrier edge via SIP — bypasses public internet entirely for sub-300ms latency
- Custom state machines control conversation logic (FSM approach) — LLM handles listening/speaking, not business logic
- **Key competitive moat:** Bandwidth owns both the PSTN infrastructure AND the AI agent layer simultaneously — no competitor (VAPI, Retell, Bland AI, Twilio) can match this

**Business model pivot:**
- From selling **connectivity** (APIs) → to selling **labor** (the AI worker)
- This changes buyer psychology: it's not an IT software budget line, it's an operations/payroll line

**The job Will interviewed for:**
- **Title:** Sr. Product Manager, AI Voice & Messaging Agents
- **Job URL:** https://job-boards.greenhouse.io/bandwidth/jobs/7613346
- **Type:** "Founding PM" as stated in JD — but recruiter clarified the real job is to inherit a built product and ship it to market (the "closer" role)
- **Key objectives per JD:**
  - Scale: support tens of thousands of active agents
  - Speed: achieve 10-minute "Zero-Touch" onboarding for resellers
  - Consistency: maintain 90%+ Task Completion Rate (TCR) for scheduling
  - Market Validation: translate Anchor partner feedback into scalable product roadmap
- **Salary:** $160k base + equity grants (2 types mentioned) + 100% healthcare coverage + bonus. Recruiter said all-in total compensation is significantly higher than base. Bandwidth confirmed fully remote-friendly for this team given Jason's own remote arrangement.

---

## The Opportunity / Why This Matters

**For Will personally:**
- Will has been divorced for about a year and is in a financial position where stable income would help
- He is actively weighing Bandwidth job vs. building DataGrove.ai (his own AI proptech startup)
- The Bandwidth role offers: financial stability, full healthcare coverage (a significant expense for Will currently), proximity to Greensboro (where daughter Mia, 14, lives), startup energy within a large company, and direct relevance to his AI skillset
- The role is a rare match: Will's 0-to-1 builder experience, multi-agent AI background, and distribution/channel thinking directly map to what the Innovation Studio needs

**For the product:**
- The AI receptionist market is a labor replacement play, not a software add-on
- US virtual receptionist market: $5.26B (2025), growing at ~10%/year
- Global wage bill: ~$52–55 trillion/year — the addressable opportunity is enormous if you frame this as replacing human labor, not selling software
- SMBs currently pay $3,000–5,000/month for human receptionists; the AI version can be sold for $150–300/month = 10–20x ROI for the buyer

**The competitive window:**
- VAPI, Retell, Bland AI all operate over public internet, have no PSTN ownership, and charge developer-tier pricing ($0.05–0.33/min)
- Twilio ConversationRelay is general-purpose with no white-label SMB engine
- Bandwidth's owned PSTN + carrier-edge inference is a defensible technical moat that takes years to replicate

---

## History & Context of the Relationship

**How it started:** Will found the job posting at https://job-boards.greenhouse.io/bandwidth/jobs/7613346 and set up an interview with Jason through the standard Bandwidth recruiting process.

**Pre-interview prep (Feb 27, 2026 — Topic 3 "Research" channel of Agent HQ):**
- Will shared his resume (DataGroveAI, Winterfield LLC, Starr Electric, Altr Ergo, Lekker Bikes) and the job posting
- Zoé fetched the job posting and researched Jason's background
- Zoé discovered Jason was former GM/SVP at Bandwidth who now consults via Galleon Strategies
- Will and Zoé co-developed a deep interview strategy including:
  - The "closer" narrative (not the builder/inventor)
  - Key stories: Starr Electric speed story, Lekker Bikes B2B2B story, Estimai AI architecture story
  - Technical architecture framing (FSM, LangGraph, Deepgram/Cartesia)
  - Competitive landscape (VAPI, Retell, Twilio)
  - Questions to ask Jason
  - Gaps to get ahead of (no PM title, CRE domain, no voice-specific background)
  - Opening move + closing line
- Created interview prep PDF: `/Users/willholt/.openclaw/workspace/interview-prep-bandwidth.pdf`

**The interview (Feb 27–28, 2026):**
- Will had a video interview with Jason
- **It went well — they ran over time**, which Will noted as a positive signal (Jason was engaged and didn't want to cut it off)
- Key things Jason revealed during the interview:
  1. There is an AI voice product already built and "ready to ship" — the current SPM built it and will pivot to new product development; Will would own the launch and scaling
  2. Bandwidth is using open source LLMs (not OpenAI/Claude) because OpenAI would cost $0.35/min — too expensive for the business model
  3. Target infrastructure cost is $0.02/minute (Jason's stated goal, building all in-house)
  4. Jason mentioned the pricing challenge — "getting the first dollar" — indicating they haven't yet commercialized the product
  5. Jason is fully remote in Oregon
  6. Jason said he would review the recording of the interview and then decide about next steps

**Post-interview (Feb 28, 2026 — continued in Topic 3 and Topic 1):**
- Will and Zoé discussed pricing strategy, market research, and potential follow-up
- Zoé created a full pricing research document: `/Users/willholt/.openclaw/workspace/bandwidth-pricing-research.pdf`
- Jason's comment about "getting the first dollar" and pricing discovery was the key post-interview discussion thread
- Will confirmed he told Jason he would talk to resellers about pricing — a smart, proactive move
- Discussion of whether/how to send the pricing research to Jason as a follow-up

**Key personal context Will shared (Feb 28):**
- He has been divorced for about a year
- He is personally in a financial spot where a job would be helpful
- He is genuinely excited about both opportunities (Bandwidth job AND DataGrove.ai)
- The two-home scenario (staying in Greensboro vs. potentially needing to be in Raleigh) was a concern — but Jason's remote arrangement in Oregon makes this much less of an issue
- Will coaches daughter Mia's (14) soccer team — being in Greensboro matters for that reason

---

## Strategies & Decisions Made

**Interview framing strategy:**
- Lead with "closer" identity, not "builder" — the product is built, the job is to launch it
- Core narrative: "I'm a closer. I've inherited stalled projects and shipped them fast."
- Anchor stories: Starr Electric (speed + enterprise execution), Lekker Bikes (B2B2B/channel), Estimai (AI credibility), Defensibility Dashboard (validation thinking)
- Questions to ask Jason focused on: what "ready to ship" means, who Anchor partners are, what the handoff looks like, what success at 6 months looks like
- Opening move: Don't wait for Jason to set the agenda — open with direct framing of the role

**Post-interview strategy:**
- Will told Jason he would talk to resellers about pricing — this is the promised follow-up
- Pricing research document created as a potential artifact to share with Jason while he reviews the interview recording
- The "labor dollars vs. product dollars" framing was identified as the single most important strategic insight for positioning and pricing
- Recommended pricing approach: flat monthly tiers, price against human receptionist ($3–5K/mo), not against API competitors ($0.07/min)

**Pricing framework developed:**
- Starter: $49 wholesale / $129 retail, 500 min included
- Growth: $99 wholesale / $249 retail, 1,200 min included
- Pro: $179 wholesale / $449 retail, unlimited
- Overage: $0.08/min wholesale / $0.20/min retail
- Reseller margin target: ~60%+
- Founding Partner strategy: lock 10–20 early resellers at 30% discount in exchange for feedback commitment

**Price discovery methods identified:**
1. Van Westendorp Price Sensitivity Meter (4-question framework) — best for new categories
2. Gabor-Granger testing (directional data quickly)
3. Jobs-to-Be-Done interviews with resellers (Will's instinct, the richest data)
4. Value-based anchoring against human receptionist cost
5. Founding Partner pricing for "first dollar" moment

---

## Action Items / Next Steps

- **Will to talk to resellers** about pricing (as promised to Jason) — use the 5-question interview framework from the pricing research doc
- **Follow-up to Jason** — timing TBD, but the window is while Jason reviews the interview recording. Two options discussed: (a) LinkedIn message referencing the pricing conversation and offering to share research, (b) send pricing research doc directly
  - Suggested message framing: *"Jason — really enjoyed our conversation. The 'first dollar' comment stuck with me. I've been sketching out a pricing framework for the B2B2B model and have a few thoughts on how to structure it for reseller adoption. Happy to share if useful."*
- **Decision point:** Will needs to decide between Bandwidth job and doubling down on DataGrove.ai — still open as of Feb 28, 2026
- **Financial math:** Run the actual numbers on Bandwidth offer (salary + healthcare savings + equity) vs. DataGrove.ai 100-client model ($44K/mo at scale)
- **Salary negotiation research:** $160k may be below market for a Sr. PM building agentic AI at this level — worth researching before negotiating

---

## Other Key Details

**Will's resume highlights (mapped to this role):**
- DataGroveAI: BuildOptima (0.77 AUC ML model), Estimai (LangGraph multi-agent), Defensibility Dashboard (1,000-agent simulation)
- Starr Electric: Deployed middleware in 1 week after IT stalled 9 months; 5 apps in 90 days with 3-person team; saved $500k/year
- Lekker Bikes: OEM → exclusive US distribution → DTC launch → exit in 2.5 years (textbook B2B2B)
- Winterfield LLC: $3M+ capital raised, ~100k multifamily unit network, zoning text amendment that created new asset category

**Key technical vocabulary for Bandwidth conversations:**
- Do NOT lead with LangGraph, LangChain, or OpenAI (they built everything in-house)
- DO reference the concepts: cyclic conversational state, finite state machines, task completion rate, knowledge ingestion, post-call eval loops
- Bandwidth's moat language: "carrier edge," "SIP-native," "sub-300ms," "PSTN ownership"

**Competitive landscape (for reference in future conversations):**

| Competitor | Weakness | Bandwidth's Edge |
|---|---|---|
| VAPI / Retell / Bland AI | Public internet, high latency, no PSTN ownership | Carrier edge, sub-300ms, SIP-native |
| Twilio ConversationRelay | General-purpose, no white-label SMB engine | Opinionated blueprints, zero-touch onboarding |
| DIY (n8n / Make) | Requires technical setup, can't be white-labeled | Turnkey for non-technical resellers |

**Key files in workspace:**
- `/Users/willholt/.openclaw/workspace/interview-prep-bandwidth.md` — full interview prep doc (and .pdf)
- `/Users/willholt/.openclaw/workspace/bandwidth-pricing-research.md` — market research + pricing strategy (and .pdf)
- Both PDFs were sent to Will via Telegram on Feb 27–28, 2026

**Key URLs:**
- Job posting: https://job-boards.greenhouse.io/bandwidth/jobs/7613346
- Jason's LinkedIn: https://www.linkedin.com/in/jasonsommerset/
- Bandwidth Innovation Studio: https://www.bandwidth.com/innovation-studio/

**Status as of Feb 28, 2026:**
- Interview completed, went well (ran over time)
- Jason is reviewing the recording before deciding on next steps
- No offer yet; no rejection yet
- Will is genuinely interested and financially motivated to accept if offered
- The remote arrangement is confirmed viable given Jason's own Oregon setup

---

*Briefing compiled by Zoé 🌹 | Sources: session transcripts from Agent HQ topic:3 (research session Feb 27–28, 2026) and topic:1 (general chat Feb 28, 2026)*
