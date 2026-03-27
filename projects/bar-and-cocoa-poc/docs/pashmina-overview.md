# Bar & Cocoa — Curation Agent: Overview

## What it does

The agent helps you build the monthly gift box in two moves instead of twenty. You tell it what you want in plain English — "select the box," "why was this bar included," "how many bars expire before June" — and it handles the rest. Under the hood it scores all 100 bars in inventory, picks the best 10 that balance expiry urgency with curation quality, and shows you its reasoning for every pick.

---

## How to use it

Open the chat and try any of these:

- `Select the box` — runs a full selection and shows the 10-bar breakdown
- `Lower the velocity threshold to 1.0` — adjusts a rule and immediately reselects
- `Why was the Miso Caramel Dark chosen?` — explains the inventory and curation reasoning for any bar
- `How many bars expire before June?` — answers inventory questions directly
- `What's our most urgent bar?` — general questions work too

---

## The current rules (plain English)

### What gets considered
- Only bars selling fewer than **1.5 units/week** are eligible — faster sellers don't need help moving
- Bars reordered fewer than **4 times/year** are excluded — too hard to restock safely if we deplete them
- Bars expiring within **90 days** are flagged as urgent and prioritized

### Hard constraints the agent never violates
| Rule | Value |
|---|---|
| Bars per box | Exactly 10 |
| Max bars from same maker | 2 |
| Max bars from same origin country | 3 |
| Minimum dark chocolate bars | 3 |
| Minimum distinct origins | 4 |
| Box price ceiling | $150 |

### What it optimizes for (in priority order)
1. Bars most at risk of expiring before they sell through
2. Range of intensities — mild through bold
3. Variety of types — dark, milk, white, inclusions
4. Flavor diversity across the box

### What it never touches
- **Fast movers** (≥4 units/week) — they sell themselves, no need to promote them
- **Rare/imported bars** reordered once or twice a year — can't safely deplete stock we can't reliably replace

---

## What you can change

Any rule above can be adjusted mid-conversation. Examples:

- *"Change max bars per maker to 3"*
- *"Raise the price ceiling to $175"*
- *"Lower the expiry threshold to 60 days"*

The agent will acknowledge the change and immediately show you a new box with the updated rules applied. Rules reset if you start a new chat session.

---

*Bar & Cocoa POC — built by Triad AI*
