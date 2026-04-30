# Travel Agent — Final Project Starter

You finished the four-week workshop. Now you're going to **build your own travel agent** and **deploy it to a public URL** that lives on your portfolio. This is your project. Make it yours.

You'll use an AI coding agent (Claude Code, Cursor, or similar) as your implementation partner. Your job is to make architectural choices, write good prompts, test, and ship. The AI coding agent fills in the boilerplate.

> **Read [PROJECT.md](PROJECT.md) first** — that's the spec. This README is just for getting set up.

---

## What's in this starter

```
final-project-starter/
├── README.md            ← you are here (setup + how to run)
├── PROJECT.md           ← the spec: what you must build, what's optional
├── AGENTS.md            ← brief your AI coding agent (Cursor / Claude Code / Codex auto-load this)
├── pyproject.toml       ← project + pinned dependencies (uv reads this)
├── requirements.txt     ← same pins, in pip format (fallback)
├── setup.sh             ← one command to install everything
├── .env.example         ← copy to .env and paste your API keys
├── src/
│   ├── agent.py         ← skeleton with TODOs — your job to fill in
│   ├── tools.py         ← one working example tool (web_search) + booking link helpers
│   └── system_prompt.py ← travel-domain expertise (READ THIS — it's the secret sauce)
├── data/                ← put your RAG corpus here (city guides, etc.) if you use RAG
└── app.py               ← Streamlit chat shell, ready to deploy
```

---

## Getting started

### Step 1: Get your API keys (free, no credit card)

Open both pages and create a key — keep them in a notes file for now.

| Service | What it's for | Where to get a key |
|---|---|---|
| **Groq** | The LLM (llama-3.3-70b) | https://console.groq.com/keys |
| **Tavily** | Web search | https://app.tavily.com/home |

### Step 2: Run the setup script

From inside the `final-project-starter/` folder:

```bash
bash setup.sh
```

This script will:
1. Install **uv** (a fast Python package manager) if you don't have it
2. Run `uv sync` — which downloads a compatible Python (3.10–3.12), creates a `.venv/`, and installs all dependencies
3. Copy `.env.example` → `.env` so you can fill in your API keys

Takes about 30 seconds. **You don't need Python pre-installed** — uv will fetch one for you if needed.

### Step 3: Add your API keys

Open `.env` (the file the setup script just created) and paste in your keys:

```bash
GROQ_API_KEY=gsk_your_actual_key_here
TAVILY_API_KEY=tvly-your_actual_key_here
```

> **Don't commit `.env` to GitHub.** It's already in `.gitignore`. If you accidentally push a key, rotate it immediately at the provider's site.

### Step 4: Run the app

```bash
uv run streamlit run app.py
```

That's it. **No `source .venv/bin/activate` needed** — `uv run` automatically uses the project's virtual environment for you. This is one of the nicest things about uv.

Streamlit will open `http://localhost:8501` in your browser. You'll see a barebones chat interface. Right now the agent is a basic ReAct loop with a few tools — your job is to extend it into something useful.

---

## Working on the project: common commands

```bash
# Run the Streamlit app
uv run streamlit run app.py

# Run a quick Python check / smoke test
uv run python -c "from src.agent import build_agent; print(build_agent())"

# Add a new dependency (auto-updates pyproject.toml)
uv add chromadb

# Add an optional dep group
uv add --optional rag chromadb langchain-chroma fastembed

# Update everything to latest compatible versions
uv lock --upgrade && uv sync

# Drop into a Python REPL with project deps loaded
uv run python
```

> **You don't have to activate a venv for any of these.** `uv run <cmd>` runs `<cmd>` inside the project's `.venv` automatically. If you *prefer* an activated venv (some IDEs are happier with it), you can run `source .venv/bin/activate` (Mac/Linux) or `.venv\Scripts\Activate.ps1` (Windows) — but it's not required.

---

## Windows users (PowerShell)

If you can't run `bash setup.sh`, do these manually:

```powershell
# Install uv
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install deps (auto-creates .venv)
uv sync

# Copy .env
copy .env.example .env

# Run
uv run streamlit run app.py
```

---

## Already prefer plain pip?

uv is much faster and handles Python versioning for you, but if you want plain pip:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Mac/Linux
# .venv\Scripts\Activate.ps1       # Windows

pip install -r requirements.txt
cp .env.example .env               # Mac/Linux
# copy .env.example .env           # Windows

streamlit run app.py
```

With plain pip you DO need to activate the venv before running commands.

---

## Troubleshooting

### "command not found: uv"
The installer added uv to `~/.local/bin`. Open a new terminal, or run:
```bash
source $HOME/.local/bin/env   # Mac/Linux
```

### "ModuleNotFoundError: No module named 'langchain_groq'"
You're probably running `python` or `streamlit` directly without uv. Use `uv run streamlit run app.py` instead. Or, if you activated a venv, make sure it's the project's `.venv/`.

### "GROQ_API_KEY not found" or 401 errors
Open `.env` and confirm your keys are there with no quotes around them. After editing `.env`, restart Streamlit (Ctrl+C and re-run).

### Install fails with "ResolutionImpossible" or version conflicts
A common cause is a broken `.venv/`. Delete it and re-run setup:
```bash
rm -rf .venv && uv sync
```

### "AttributeError: module 'pydantic' has no attribute 'X'"
You likely have pydantic v1 installed elsewhere on your system. uv's isolated venv should prevent this — make sure you're running via `uv run`, not the system Python.

### Streamlit Cloud deployment fails on `chromadb`
chromadb has heavy native deps that occasionally break Streamlit Cloud's build environment. If you don't need RAG, leave it commented out. If you do, see deployment notes in [PROJECT.md](PROJECT.md).

### My imports work locally but fail on Colab
Don't run this project in Colab. Colab's preinstalled packages clash with the agent stack and force constant `--upgrade` flags that subtly break things. Use a local venv (these instructions) or GitHub Codespaces.

---

## Deploying your finished project (Streamlit Community Cloud — free)

When your agent works locally and you're ready to ship:

1. **Push your repo to GitHub** (public is fine; free tier requires it):
   ```bash
   git init
   git add .
   git commit -m "Initial travel agent"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo>.git
   git push -u origin main
   ```

2. **Go to https://share.streamlit.io** and sign in with GitHub.

3. **Click "Create app"** → pick your repo → set **Main file path** to `app.py`.

4. **Add your secrets** (Settings → Secrets), in TOML format:
   ```toml
   GROQ_API_KEY = "gsk_..."
   TAVILY_API_KEY = "tvly-..."
   ```

5. **Click Deploy.** You'll get a public URL like `https://your-travel-agent.streamlit.app`. Add it to your GitHub repo's About section and your resume.

> Streamlit Cloud reads from `requirements.txt` automatically (it doesn't speak `pyproject.toml` yet). The `requirements.txt` and `pyproject.toml` in this repo are kept in sync — both deploy and local-dev work.

---

## Where to look next

- **[PROJECT.md](PROJECT.md)** — the actual project spec (MVP requirements, optional tiers, evaluation criteria)
- **[AGENTS.md](AGENTS.md)** — what your AI coding agent will read about this project. Cursor, Claude Code, and Codex all auto-load this file. Edit it as the project evolves.
- **[src/system_prompt.py](src/system_prompt.py)** — read this carefully. It's the travel-domain expertise that turns a generic chatbot into something travel-specific. Edit it to match the agent you want to build.

Good luck. Make something you'd actually use.
