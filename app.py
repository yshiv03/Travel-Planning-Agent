"""
Streamlit chat shell for the travel agent.

Run with:
    uv run streamlit run app.py     # if using uv (no venv activation needed)
    streamlit run app.py            # if you've activated a venv manually

This is a working MVP — it runs the agent with conversation memory. Extend it
as you add features: sidebar for preferences, expander to show "agent thinking"
(intermediate tool calls), trip export buttons, etc.
"""

import os
import uuid
from pathlib import Path

from dotenv import load_dotenv

# Load project `.env` by path so keys work even when cwd is not the repo root
# (e.g. `streamlit run /path/to/app.py` from another directory).
_ROOT = Path(__file__).resolve().parent
load_dotenv(_ROOT / ".env")

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from streamlit.errors import StreamlitSecretNotFoundError

from src.agent import build_agent

# Streamlit Cloud injects secrets into st.secrets — copy them to env vars so
# the rest of the code (which reads os.environ) just works in both places.
# Locally, missing `.streamlit/secrets.toml` makes any `st.secrets` access raise;
# `.env` already populated keys above.
try:
    for key in ("GROQ_API_KEY", "TAVILY_API_KEY"):
        if key in st.secrets and key not in os.environ:
            os.environ[key] = st.secrets[key]
except StreamlitSecretNotFoundError:
    pass


# --- Page config -------------------------------------------------------------

st.set_page_config(page_title="Travel Agent", page_icon=None, layout="centered")
st.title("Travel Agent")
st.caption("Plan a trip. I'll suggest a day-by-day itinerary with booking links.")


# --- Pre-flight: check for API keys ------------------------------------------

def _env_nonempty(key: str) -> bool:
    v = os.environ.get(key)
    return bool(v and str(v).strip())


missing = [k for k in ("GROQ_API_KEY", "TAVILY_API_KEY") if not _env_nonempty(k)]
if missing:
    st.error(
        f"Missing API key(s): {', '.join(missing)}.\n\n"
        "Locally: add them to `.env`.\n"
        "On Streamlit Cloud: add them under Settings → Secrets."
    )
    st.stop()


# --- Build the agent (cached so we don't rebuild on every keystroke) ---------

@st.cache_resource
def get_agent():
    return build_agent()


agent = get_agent()


# --- Session state -----------------------------------------------------------
# `thread_id` is what LangGraph uses to scope conversation memory. One per
# Streamlit session means each browser tab has its own chat history.

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "history" not in st.session_state:
    st.session_state.history = []  # list of (role, content) for display


# --- Render past messages ----------------------------------------------------

for role, content in st.session_state.history:
    with st.chat_message(role):
        st.markdown(content)


# --- New user input ----------------------------------------------------------

if prompt := st.chat_input("Where are you thinking of going?"):
    st.session_state.history.append(("user", prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Planning..."):
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            result = agent.invoke(
                {"messages": [HumanMessage(content=prompt)]},
                config=config,
            )
            # The last message is the agent's final reply.
            reply = result["messages"][-1].content
            st.markdown(reply)

    st.session_state.history.append(("assistant", reply))


# --- Sidebar -----------------------------------------------------------------

with st.sidebar:
    st.subheader("Session")
    st.caption(f"Thread: `{st.session_state.thread_id[:8]}…`")
    if st.button("Start a new trip"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.history = []
        st.rerun()

    st.divider()
    st.subheader("About")
    st.markdown(
        "This agent plans trips with booking links. It doesn't actually book "
        "anything — click the links to book on the real sites."
    )
