"""
The travel agent — minimal LangGraph skeleton.

This is intentionally small. It's a single ReAct loop: the LLM decides whether
to call tools or respond, and the graph routes accordingly. That's all the
architecture you need for Tier 1 of the project (see PROJECT.md).

When you're ready for Tier 2, add nodes here:
- A `route` node that classifies queries
- A `rag_lookup` node for retrieving from your own corpus
- A `critic` node that reviews the itinerary before returning it

The state, the tools, and the prompt are decoupled — extend any of them
without touching the others.
"""

from pathlib import Path
from typing import Annotated, TypedDict

from dotenv import load_dotenv

# `app.py` also loads `.env`; this covers REPL / `python -c` / tests that import
# `build_agent` without running Streamlit first.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from langchain_core.messages import AnyMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from src.system_prompt import SYSTEM_PROMPT
from src.tools import ALL_TOOLS


# --- State -------------------------------------------------------------------
# `messages` accumulates the conversation. `add_messages` is a reducer that
# appends new messages to the list (rather than replacing it).

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


# --- Build the agent ---------------------------------------------------------

def build_agent(model_name: str = "llama-3.3-70b-versatile"):
    """Compile the LangGraph travel agent.

    Returns a compiled graph you call with .invoke() or .stream().

    Args:
        model_name: Groq model ID. Default is llama-3.3-70b-versatile, which
            balances quality and speed. Try llama-3.1-8b-instant if you want
            faster responses for testing.
    """
    llm = ChatGroq(model=model_name, temperature=0.3)
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    def call_model(state: AgentState) -> dict:
        """The agent's reasoning step. Sees the system prompt + history, decides
        whether to call a tool or respond directly.
        """
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    # Build graph: agent ↔ tools loop until the LLM stops calling tools.
    graph = StateGraph(AgentState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", ToolNode(ALL_TOOLS))

    graph.add_edge(START, "agent")
    # `tools_condition` routes to "tools" if the last message has tool calls,
    # else to END.
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")

    # MemorySaver keeps conversation history within a single process run.
    # For persistent memory across sessions, swap this for SqliteSaver:
    #   from langgraph.checkpoint.sqlite import SqliteSaver
    #   checkpointer = SqliteSaver.from_conn_string("trips.db")
    checkpointer = MemorySaver()

    return graph.compile(checkpointer=checkpointer)
