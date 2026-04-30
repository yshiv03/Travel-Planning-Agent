# Travel Agent Project — Brief for AI Coding Agents

> This file is read automatically by Cursor, Claude Code, OpenAI Codex, and other AI coding agents that follow the `AGENTS.md` convention. Edit it as your project evolves so the agent has accurate context.

## What we're building

A travel-planning agent that takes destination + dates + budget + interests and returns a day-by-day itinerary with deep links to Booking.com, Google Flights, etc. **It does not perform real bookings** — it constructs URLs the user clicks. This matches how production consumer travel agents (Wonderplan, Mindtrip) actually work.

The full spec is in `PROJECT.md`. Read it before suggesting architectural changes.

## Tech stack (pinned, don't change without asking)

- **LLM:** Groq via `langchain-groq` (model: `llama-3.3-70b-versatile`)
- **Agent framework:** LangGraph (not legacy LangChain `AgentExecutor`)
- **Web search:** Tavily (`tavily-python`)
- **Validation:** Pydantic v2
- **UI:** Streamlit
- **Optional vector store:** Chroma (only if RAG is enabled — uncomment in `requirements.txt`)
- **Python:** 3.10–3.12

Exact pins are in `requirements.txt`. If you suggest adding a new dep, pin it explicitly and explain why.

## Conventions

- **API keys** come from `.env` via `python-dotenv` locally, and from `st.secrets` when deployed to Streamlit Cloud. The `agent.py` module loads via `os.environ` after `load_dotenv()` is called in `app.py` — don't sprinkle `load_dotenv()` calls everywhere.
- **No `print()` in agent code** — use Streamlit's UI for user-visible output. Use Python's `logging` module for diagnostics.
- **State** lives in a single `TypedDict` (see `src/agent.py`). New fields go there, not in scattered globals.
- **Tools** go in `src/tools.py`. Each tool is a plain Python function decorated with `@tool` from `langchain_core.tools`. Write a clear docstring — that's what the LLM sees when deciding whether to call the tool.
- **The system prompt** lives in `src/system_prompt.py`. Travel-domain expertise (geographic clustering, budget rules, etc.) belongs there, not in code logic.
- **Don't add files** that aren't directly serving the spec. No `utils/`, no `helpers/`, no premature abstractions.

## What "done" looks like

- `streamlit run app.py` works locally without errors
- The agent answers a query like "Plan a 3-day trip to Barcelona for 2 people on a $1500 budget, we like food and architecture" with a useful day-by-day itinerary with clickable booking links
- Deployed to Streamlit Cloud at a public URL
- README has the live URL prominently at the top

## What to NOT do

- **Don't introduce LangChain `AgentExecutor`.** We use LangGraph.
- **Don't add OpenAI or Anthropic dependencies.** This project uses Groq.
- **Don't hardcode API keys** — even temporarily for debugging.
- **Don't try to integrate real booking APIs** (Sabre, Amadeus production, Stripe). The student doesn't have business credentials and these aren't getting approved in a week.
- **Don't refactor the file structure** unless I ask. Keep `src/agent.py`, `src/tools.py`, `src/system_prompt.py` as the three primary modules.
- **Don't add tests for trivial code.** If you add a non-trivial function, a small test in `tests/` is fine, but don't write tests for things like "tool returns a string."

## Common requests and how to handle them

- **"Add a tool for X"** → write the function in `src/tools.py`, decorate with `@tool`, register it in the agent's tools list in `src/agent.py`. Confirm the docstring describes what it's for.
- **"Add memory"** → first ask: in-session only, or persistent across sessions? Default to in-session (`MemorySaver`) unless I've said otherwise. Persistent = `SqliteSaver` from `langgraph.checkpoint.sqlite`.
- **"Add RAG"** → ask what corpus, then create a `data/` folder of markdown files, build a Chroma index in `src/rag.py`, expose a `search_guides` tool in `src/tools.py`. Uncomment chromadb deps in `requirements.txt`.
- **"Make it remember the user"** → that's per-user persistent memory. Use a `user_id` thread ID with `SqliteSaver`, store preferences in the state.

## How to verify changes

After changes, run:

```bash
streamlit run app.py
```

Send a test query: *"Plan a 3-day trip to Tokyo for 2 people, budget $2000, we like food and quiet temples."* The agent should respond with a structured day-by-day plan including booking links. If it crashes, fix it before reporting done.

## Project-specific gotchas

- `langchain-groq` requires `GROQ_API_KEY` in the environment **before** `ChatGroq()` is constructed.
- LangGraph compiles a graph object — call `.invoke()` or `.stream()` on the compiled object, not the builder.
- Tavily's `TavilyClient` returns a dict, not text — extract `results[i]["content"]` for the LLM.
- Streamlit reruns the whole script on each interaction. Cache the agent with `@st.cache_resource` so we don't rebuild the graph every keystroke.

## When in doubt

Ask. The architectural decisions are mine, not yours. You're an excellent implementation partner — but a partner, not a driver.
