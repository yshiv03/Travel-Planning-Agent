#!/usr/bin/env bash
# One-shot setup for the Travel Agent final project, using uv.
#
# uv manages the venv automatically — you do NOT need to `source .venv/bin/activate`.
# After running this, just use `uv run streamlit run app.py`.
#
# Usage:   bash setup.sh

set -euo pipefail

echo "Travel Agent — Setup"
echo "===================="

# --- 1. Install uv if missing ---
if ! command -v uv >/dev/null 2>&1; then
    echo "Installing uv (fast Python package manager)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # shellcheck disable=SC1091
    [ -f "$HOME/.local/bin/env" ] && . "$HOME/.local/bin/env" || export PATH="$HOME/.local/bin:$PATH"
fi
echo "uv $(uv --version | awk '{print $2}') ready."

# --- 2. Sync dependencies ---
# `uv sync` reads pyproject.toml, picks a compatible Python (downloads one if
# needed), creates .venv/, and installs everything. Idempotent — safe to re-run.
echo "Installing dependencies (this takes ~30s the first time)..."
uv sync

# --- 3. Copy .env if missing ---
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env — open it and paste in your API keys."
else
    echo ".env already exists — leaving it alone."
fi

# --- 4. Done ---
cat <<'EOF'

Setup complete!

Next steps:
  1. Edit .env and paste in your GROQ_API_KEY and TAVILY_API_KEY.
       Get them free at:
         - https://console.groq.com/keys
         - https://app.tavily.com/home
  2. Run the app (no venv activation needed — uv handles it):
       uv run streamlit run app.py

EOF
