# Final Project: Build a Travel Agent

## The goal

Build a working travel agent that takes a user's destination, dates, budget, and interests, and returns a useful day-by-day itinerary with **real booking links** the user can click. Deploy it. Put the live URL on your resume.

You have one week and an AI coding agent. Don't try to build a real booking system — that requires business contracts you don't have. Instead, build the part that's actually useful: planning, recommendations, and **deep links** to existing booking sites.

---

## Realistic scope: what consumer travel agents actually do

Production travel agents (Wonderplan, Mindtrip, Roam Around) don't book anything themselves. They:

1. Take a free-text request
2. Generate a structured itinerary
3. Output **deep-link URLs** to Booking.com, Skyscanner, Google Flights, Google Maps with the user's dates pre-filled

Example deep links your agent should construct:

```
https://www.booking.com/searchresults.html?ss=Barcelona&checkin=2026-05-15&checkout=2026-05-18&group_adults=2
https://www.google.com/travel/flights?q=flights%20from%20JFK%20to%20BCN%20on%202026-05-15
https://www.google.com/maps/search/tapas+restaurants/@41.3851,2.1734,14z
```

You **don't need API keys** for any of those. They're just URLs the user clicks. This is honest about the scope and exactly what the industry does.

---

## Tiered requirements

Pick a tier based on how ambitious you want to be. **Aim for Tier 1 first**, then push higher if you have time.

### Tier 1 — MVP (required to pass)

- [ ] Takes user input: destination, start/end dates, budget, list of interests
- [ ] Returns a **day-by-day itinerary** in a readable format (markdown is fine)
- [ ] Each day has morning / afternoon / evening blocks with specific suggestions
- [ ] Includes **clickable deep links** to Booking.com (lodging) and Google Flights or Skyscanner (flights)
- [ ] Uses **at least one tool**: web search via Tavily for current info (events, weather, hours)
- [ ] Has **conversation memory within a session** — user can refine ("make day 2 less touristy") without restating context
- [ ] Runs as a Streamlit chat app
- [ ] Deployed to Streamlit Community Cloud with a public URL

### Tier 2 — Solid portfolio piece

Everything in Tier 1, plus **at least two** of:

- [ ] **Persistent memory across sessions** — when the same user comes back, the agent remembers their preferences (vegetarian, hates museums, prefers boutique hotels). Use a SQLite checkpoint or vector store keyed by user ID.
- [ ] **RAG over your own curated content** — guides for 3-5 cities you've personally researched, retrieved when the user asks about those cities. The user's question pulls relevant chunks; web search fills in the rest.
- [ ] **Multi-step planning with conditional routing** — a LangGraph with at least 3 nodes (e.g., `analyze → research → generate`) and a router that decides whether to use RAG, web search, or both.
- [ ] **Structured output** — itineraries returned as a Pydantic model (so the UI can render days/times consistently and you can export to JSON).

### Tier 3 — Going further (optional, for ambitious students)

- [ ] **Real flight prices** via Amadeus self-service API (free tier; requires sign-up)
- [ ] **Multi-agent system** — separate "researcher" and "planner" agents, with a supervisor coordinating them
- [ ] **Trip critic** — a second LLM call that reviews the itinerary and suggests fixes (geographic clustering, pacing, budget realism)
- [ ] **Export to calendar** — generate an `.ics` file the user can import into Google Calendar
- [ ] **User accounts** — multiple users with separate trip histories (use Streamlit's auth or a simple SQLite users table)

---

## Decisions you have to make

These aren't "right answer" decisions — they depend on what you want to build. Your AI coding agent will ask you these. Have answers ready.

### 1. Memory: how should the agent remember things?

| Option | Use when | Complexity |
|---|---|---|
| **In-session only** (LangGraph `MemorySaver`) | MVP, you want it simple | Low |
| **Persistent, per-user** (SQLite checkpointer) | You want users to come back to saved trips | Medium |
| **Vector memory** (Chroma + embeddings) | Long histories, semantic recall ("trips like the one to Barcelona") | High |
| **Hybrid** (SQLite for state + vector for preferences) | Production-shaped | High |

For Tier 1, in-session is fine. Tier 2 requires persistent.

### 2. Tools: what should the agent be able to call?

Pick what your agent needs. Don't add tools you won't use.

| Tool | What it does | API key needed | Free tier |
|---|---|---|---|
| **Tavily web search** | Current events, hours, news | Yes | 1000 searches/mo |
| **Booking deep-link constructor** | Builds Booking.com URLs (no API call, just string formatting) | No | Unlimited |
| **Google Flights deep-link** | Same idea for flights | No | Unlimited |
| **Google Maps directions deep-link** | Same idea for "how to get from X to Y" | No | Unlimited |
| **OpenWeatherMap** | Weather forecasts | Yes | 1000 calls/day |
| **Amadeus self-service** | Real flight search | Yes | Limited free tier |
| **Wikivoyage** | Open travel encyclopedia | No | Unlimited |
| **Currency conversion (Frankfurter)** | Exchange rates | No | Unlimited |

### 3. Architecture: how is the agent structured?

| Pattern | What it looks like | When to pick it |
|---|---|---|
| **Single ReAct loop** | LLM with bound tools, calls them as needed | Tier 1, you want to ship fast |
| **Router → tool nodes → generator** | LangGraph with explicit routing | Tier 2, you want to combine RAG + web search |
| **Multi-agent (supervisor)** | Multiple agents, one coordinator | Tier 3, you have time to debug |

Single ReAct is the right default. Don't over-engineer.

### 4. RAG corpus: if you use RAG, what's in it?

If you do RAG, your corpus has to be **something Google doesn't already have indexed well**. Otherwise web search beats it. Good corpus ideas:

- **Your own opinionated city guides** — your own taste, written by you. This becomes a curated voice the agent speaks in.
- **Niche travel content** — hidden food spots, local events, curated based on your travel
- **Made-up "boutique agency" policies** — "We only book sustainable hotels, our preferred vendors are X, Y, Z" — use this to give the agent a personality
- **The user's own past trips** — natural fit for a "remember me" agent

Bad corpus ideas (web search beats them):
- Generic Wikipedia-style content
- Public travel guides that already rank on Google
- Anything you copy-pasted from existing travel sites

---

## Domain knowledge you'll need (and where it lives)

Travel planning has real domain expertise — geographic clustering, budget allocation, seasonal timing, visa rules. You don't need to memorize this. **It belongs in your system prompt.** See [src/system_prompt.py](src/system_prompt.py) — that's the starter system prompt with travel domain rules baked in. Read it. Edit it to match the agent you're building.

Key principles that should be in your prompt:

- **Geographic clustering**: don't schedule activities >5km apart back-to-back. Cluster by neighborhood.
- **Pacing**: 3-4 anchor activities per day, not 8. Leave gaps for meals, rest, spontaneous discoveries.
- **Budget allocation**: roughly 30-40% flights, 25-35% lodging, 20% food, 10-15% activities/misc.
- **Booking timing**: flights ~6-8 weeks out for international, hotels can be later, attractions same-day to a few weeks.
- **Visa & entry**: flag if dates conflict with visa rules. Schengen 90/180, ESTA, ETIAS, etc.
- **Local rhythms**: dinner in Spain at 9pm, siesta closures in Spain/Italy, Sunday closures in Germany, Ramadan timing, etc.
- **Output format**: itinerary in markdown, each day has morning/afternoon/evening, every booking has a deep link.

---

## Evaluation rubric

Your project will be evaluated on:

| Dimension | What it means | Weight |
|---|---|---|
| **It works end-to-end** | Live URL, no crashes, agent actually plans trips | 30% |
| **Itinerary quality** | Realistic, well-paced, geographically sensible, useful links | 25% |
| **Architectural choices** | You picked the right complexity for the goal — no over-engineering, no skipped corners | 15% |
| **Code organization** | Clean repo, good README, sensible structure, `.env` not committed | 15% |
| **Documentation** | README explains what it does, screenshot/demo, deployment URL prominent | 10% |
| **Stretch tier** | Tier 2 or Tier 3 features successfully shipped | 5% bonus |

---

## How to use your AI coding agent on this project

1. **Read this entire spec** before opening Claude Code/Cursor. You can't delegate decisions you haven't made yourself.
2. **Point it at [AGENTS.md](AGENTS.md)** — Cursor, Claude Code, and Codex auto-load this file as project context. Edit it as you go so the agent has accurate context.
3. **Ask for one thing at a time.** "Add a booking-link tool" beats "build the whole agent."
4. **Test what it gives you.** AI agents hallucinate API names. Run the code. If a tool import fails, say so — don't paper over it.
5. **Make it explain its choices.** When it picks `MemorySaver` over `SqliteSaver`, ask why. The architectural decision is yours; the AI just implements.
6. **Check git diffs before accepting.** Especially when it modifies files you didn't ask it to.

---

## Deliverables checklist

Before submitting, confirm:

- [ ] Public GitHub repo with descriptive README (what it does, screenshot, live URL)
- [ ] Working live deployment (Streamlit Cloud URL)
- [ ] No API keys committed (`git log -p | grep -i "api_key" | grep -v example` should be empty)
- [ ] `requirements.txt` matches what your repo actually imports
- [ ] At least one screenshot or short demo gif in the README
- [ ] Tier 1 requirements all met
- [ ] At least one Tier 2 feature attempted

Good luck.
