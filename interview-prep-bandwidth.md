# 🎯 Interview Prep: Sr. PM, AI Voice & Messaging Agents @ Bandwidth
**Interviewer:** Jason Sommerset, former GM/SVP Product @ Bandwidth
**Role type:** Launch PM — inherit a built AI Voice product and ship it to market

---

## 👤 Who Is Jason Sommerset?

- Spent nearly a decade at Bandwidth: Director → Sr. Director → VP → **GM/SVP of Product Management**
- He **built the Bandwidth product culture** — evaluating you against standards he personally set
- Now an independent consultant at **Galleon Strategies**
- Thinks like a **founder-operator**: values execution, speed, product intuition, and technical depth
- He's sophisticated. No fluff. Match his directness.

---

## 🏢 The Real Job (What the Recruiter Revealed)

The JD says "Founding PM" — but the recruiter told you the truth:

> There is an **AI Voice product ready to ship.** The current SPM stays on to create new products. You come in to **own the launch, scale it, and operationalize it.**

| What the JD implied | What the job actually is |
|---|---|
| 0-to-1 builder | Take existing product to GA |
| Product ideation | Launch execution + scale |
| Architecture decisions | Partner enablement + GTM |
| Discovery-heavy | Operational + commercial |

**You are not the inventor. You are the closer.** That is your identity for this call.

---

## 🏗️ What Is the Product?

Bandwidth's **Innovation Studio** (launched ~9 months ago) built an **AI Voice Receptionist / Agent Platform:**

- White-label, B2B2B: Bandwidth → Resellers (MSPs, agencies, vertical SaaS) → SMB clients
- SMBs get an AI that answers calls, books appointments, handles scheduling — no human receptionist
- Built on Bandwidth's **Voice AI Edge Platform**: SIP/PSTN-native, sub-300ms latency, multi-agent orchestration
- "Ready to ship" likely means: core functionality ✅, Anchor partners in pilot ✅ — what's missing is pricing, reseller enablement, GTM motion, and GA release execution

### The Technical Architecture (Enough to Hang With Engineers)
- **Orchestration:** LangGraph (cyclic conversational state — handles loops and interruptions)
- **Data Validation:** PydanticAI (strict JSON schemas at runtime — no malformed CRM data)
- **Audio Pipeline:** Deepgram (STT) + Cartesia (TTS) — near-instant processing
- **The Bandwidth Moat:** Agentic graph runs on Bandwidth's Carrier Edge via SIP — bypasses public internet entirely → sub-300ms, human-like latency
- **Reliability:** FSM (Finite State Machine) separates LLM from business logic — the LLM listens/speaks, the state machine controls the conversation graph and prevents hallucination off-script

### The Business Model Pivot
> Bandwidth used to sell **connectivity** (APIs for Voice, SMS, 911). This product sells **labor** (the AI worker).

This shift dramatically changes reseller economics: lower CAC for partners, higher recurring margin, stickier product. The reseller bundles it with software they're *already* selling to dentists, plumbers, and law firms.

---

## 🎤 Your Core Narrative

Lead with this early and frame everything around it:

> *"Based on what I heard from the recruiter, the core product is built and the job is to get it across the finish line and into the hands of thousands of resellers. That's the work I'm best at — I'm a closer. I've inherited stalled projects and shipped them fast. I've launched products in new markets. And I have enough technical depth to earn trust from the team that built this. Tell me what 'done' looks like and I'll show you how I'd get there."*

---

## 🗺️ Your Resume → This Role

| What the Role Needs | Your Evidence |
|---|---|
| **Take a built product and ship it** | Starr Electric: IT stalled 9 months, you deployed middleware in 1 week, shipped 5 apps in 90 days |
| **GTM execution in a new market** | Lekker Bikes: took an existing Dutch product, secured exclusive US distribution, launched DTC from scratch, exited after 2.5 years |
| **Last-mile launch coordination** | Real estate development: entitlement → capital → construction → sold. You manage the final 20% that most people can't |
| **Technical credibility with the team** | LangGraph, RAG, PydanticAI, multi-agent systems — you can inherit this product without a 3-month ramp |
| **0-to-1 AI product validation** | DataGroveAI: BuildOptima (0.77 AUC), Estimai (LangGraph multi-agent), Defensibility Dashboard (1,000-agent simulation) |
| **Reseller / channel thinking** | Lekker Bikes (OEM → exclusive distributor → DTC) = textbook B2B2B mental model |
| **Non-technical user empathy** | Starr Electric: built software for safety crews and fleet managers — not engineers |

---

## 🔑 Key Stories to Deploy

### Story 1 — The Speed Story *(for "can you execute fast?")*
**Starr Electric.** Internal IT stalled 9 months on a middleware integration. You came in, deployed it in 1 week, hired a 3-person dev team, and shipped 5 production applications in 90 days.

> *"That's the Starr playbook: walk into something technically sound but stuck, strip out the friction, and ship. That's exactly what this role is."*

### Story 2 — The B2B2B / Channel Story *(for "do you understand our model?")*
**Lekker Bikes.** OEM in the Netherlands → you secured exclusive US distribution → launched DTC from scratch → exited after 2.5 years.

> *"That's B2B2B at its simplest: the manufacturer, the distributor, the end customer. Each layer has different needs and success metrics. I think about Bandwidth the same way — you're the OEM, resellers are the distributors, SMBs are the end users. The product has to work for all three simultaneously."*

### Story 3 — The AI Architecture Story *(for "can you hang with our engineers?")*
**Estimai.** Architected a LangGraph multi-agent system to simulate human estimator workflows — scope extraction, quantity takeoff — from PDF plan sets.

> *"I didn't hire someone to build this. I designed the state graph, connected the tool calls, and ran evals on it. That gives me a very concrete understanding of where LangGraph's cyclic graph helps with conversational state, and where FSMs need to own the logic instead."*

### Story 4 — The Validation Story *(for "how do you know the product is working?")*
**Defensibility Dashboard.** Built a simulation of 1,000 AI consumer agents to model buying journeys and generate mathematically defensible ROI for partners.

> *"My instinct when a product is 'ready to ship' is to simulate scale before you hit it. I'd want to stress-test the reseller onboarding flow with real non-technical users before GA — not after."*

---

## ⚡ "What Would You Do First?"

Don't lead with features. Sound like a PM:

> *"Day one, I'm not building anything — I'm closing the feedback loop with the Anchor partners. I want to watch a non-technical reseller try to onboard in real-time. Where do they drop off? What question do they get stuck on? That tells me whether the Blueprint templates are the right abstraction or if there's earlier friction I'm not seeing. I'd want to get something in front of them within the first sprint — even if it's a flow change, not a feature."*

Then add your perspective on the opinionated Blueprint approach (dental scheduler template, URL-scraping for RAG ingestion, pre-built tool blocks for Calendly/HubSpot) as where you *expect* to land based on existing research.

---

## 🏆 Competitive Landscape (Know This Cold)

Jason will probe: *"How does this compare to what's out there?"*

| Competitor | Weakness | Bandwidth's Edge |
|---|---|---|
| **VAPI / Retell / Bland AI** | Public internet routing, high latency, no PSTN ownership | Carrier edge, sub-300ms, SIP-native |
| **Twilio ConversationRelay** | General-purpose, no white-label SMB engine | Opinionated Blueprints, zero-touch onboarding |
| **DIY (n8n / Make)** | Requires technical setup, can't be white-labeled | Turnkey for non-technical resellers |

Your line:
> *"No one else owns both the PSTN infrastructure and the AI agent layer. That's the moat. The latency advantage alone kills the competition for voice — you can't fake sub-300ms when you're routing over public internet."*

---

## ❓ Questions to Ask Jason

These signal strategic depth and that you did your homework on him specifically:

1. *"What's the current SPM's definition of 'ready to ship' — what's the specific gap between where the product is and GA?"*
2. *"Who are the Anchor partners right now, and what's the most common friction they're hitting during onboarding?"*
3. *"What does the handoff from the current SPM look like — are they staying advisory on the voice product or fully pivoting to the next thing?"*
4. *"What's the GTM motion — are you selling through Bandwidth's existing channel partners or building a new reseller acquisition motion?"*
5. *"What does success look like at 6 months — is it resellers live, agents deployed, ARR, or task completion rate?"*
6. *"You built the product culture at Bandwidth — what's the one thing that separates PMs who thrive here from ones who struggle?"* *(Personal to Jason. Shows you researched him.)*

---

## 💪 Tough Questions — Prepared Answers

**"You haven't been a PM. How do I know you can work inside an organization?"**
> *"At Starr Electric I led a dev team I didn't hire, shipped inside an enterprise, and had to navigate internal politics to deploy something IT had blocked for 9 months. I know how to move inside an org. The founder work at DataGroveAI sharpened my conviction and my technical depth — but I've always operated in both modes."*

**"Walk me through how you'd actually hit 90%+ Task Completion Rate."**
> Hit the FSM answer: separate LLM (listening/speaking) from business logic. The state machine controls the conversation graph — the LLM can't hallucinate its way off-script because it only has valid next-state options. PydanticAI enforces schema at runtime. LangSmith gives post-call observability so you can pinpoint exactly where completions drop off. You iterate on the FSM, not the prompt.

**"What's the hardest part of this job?"**
> *"Managing the gap between what resellers think they want — customization — and what actually makes them successful, which is constraint. Non-technical users need opinionated defaults. The hardest PM work here is saying no to feature requests in a way that keeps partners feeling heard while protecting the product experience for the SMB end user."*

**"Why are you leaving PropTech/AI?"**
> Don't frame it as leaving. *"I'm not leaving the problem — I'm moving to a bigger distribution surface. Bandwidth's reseller network reaches SMBs at a scale that would take me a decade to build from DataGroveAI. The problem I've been solving — complex AI workflows for non-technical users — is identical. The domain just has better infrastructure and a real GTM engine behind it."*

---

## ⚠️ Gaps to Get Ahead Of

**No "PM" title on the resume**
> *"Every PM I've worked with could tell you the theory. I've been doing the practice — architecture, validation, iteration — because I didn't have a team to hand it off to. That makes me a stronger launch PM, not a weaker one. I've never had the luxury of not shipping."*

**CRE/PropTech ≠ Telecom**
Translate early and often. The domain changes; the physics doesn't.
> *"The SMB owner who can't configure an AI agent is the same as the developer who can't navigate an entitlement process. Both need the friction removed. I've made a career out of removing that friction in complex industries."*

**No voice AI / PSTN experience specifically**
Be honest, then pivot:
> *"I haven't worked directly with SIP or PSTN pipelines, but the multi-agent orchestration and latency challenges are familiar territory from LangGraph. The layer I'd ramp fastest on is the telephony stack — and there's no better place to do that than at Bandwidth."*

---

## 🎯 Opening Move

Don't wait for him to set the agenda. Open with:

> *"Jason, I want to be direct about how I see this role: from what I understand, there's a working AI Voice product that needs to get across the finish line and into the hands of resellers. I've spent this week going deep on the architecture, the competitive landscape, and the B2B2B model — and I'm going to spend today showing you that I'm the person who closes this. Does that framing match how you're thinking about the hire?"*

---

## 🏁 Closing Line (Leave This Ringing)

> *"You're not looking for a PM who can learn AI — there are plenty of those. You need someone who has already architected a multi-agent system, shipped products from zero, and knows what reseller distribution actually looks like in practice. That's a rare combination. And it's exactly what I've been building toward."*

---

*Prepared by Zoé 🌹 | Bandwidth Sr. PM Interview | Feb 2026*
