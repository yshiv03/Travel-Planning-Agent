"""
Tools the agent can call.

Two kinds here:

1. **web_search** — calls Tavily for live web info (current events, hours,
   weather, recent reviews). Already wired up; works out of the box.

2. **booking_link / flight_link / map_link** — pure URL constructors. They
   don't make API calls; they just build deep-links the user clicks. This is
   how production travel agents actually handle "booking" without business API
   credentials.

Add new tools here. Each one needs:
- The @tool decorator
- A clear docstring (the LLM reads this to decide when to use the tool)
- Type hints on arguments
"""

import os
from datetime import date
from urllib.parse import quote_plus

from langchain_core.tools import tool
from tavily import TavilyClient


# --- Web search via Tavily ---------------------------------------------------

@tool
def web_search(query: str) -> str:
    """Search the live web for current information.

    Use for: current events, business hours, weather, recent reviews, prices,
    flight availability, or anything time-sensitive that may have changed
    since training.

    Args:
        query: A focused search query, e.g. "Sagrada Familia opening hours
            May 2026" or "Tokyo restaurant reservations Narisawa".

    Returns:
        A formatted string of the top search results with titles, URLs, and
        content snippets.
    """
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return "Error: TAVILY_API_KEY is not set. Add it to your .env file."

    client = TavilyClient(api_key=api_key)
    response = client.search(query=query, max_results=5, search_depth="basic")

    results = response.get("results", [])
    if not results:
        return f"No results for: {query}"

    lines = [f"Search results for: {query}\n"]
    for i, r in enumerate(results, 1):
        title = r.get("title", "Untitled")
        url = r.get("url", "")
        content = r.get("content", "").strip()
        lines.append(f"{i}. {title}\n   {url}\n   {content[:300]}\n")
    return "\n".join(lines)


# --- Deep-link constructors --------------------------------------------------
# These build URLs to external booking sites with the user's parameters
# pre-filled. No API calls, no API keys, no business credentials needed.
# This is exactly what consumer travel agents like Wonderplan, Mindtrip, and
# Roam Around do for their "booking" step.

@tool
def booking_link(
    destination: str,
    checkin: str,
    checkout: str,
    adults: int = 2,
) -> str:
    """Build a Booking.com search URL with the user's dates pre-filled.

    The user clicks this link to see live hotel options and book directly on
    Booking.com. We do NOT actually book — that requires business credentials.

    Args:
        destination: City or area name, e.g. "Barcelona" or "Tokyo, Shibuya".
        checkin: ISO date string, YYYY-MM-DD.
        checkout: ISO date string, YYYY-MM-DD.
        adults: Number of adult guests. Defaults to 2.

    Returns:
        A clickable Booking.com search URL.
    """
    params = (
        f"ss={quote_plus(destination)}"
        f"&checkin={checkin}"
        f"&checkout={checkout}"
        f"&group_adults={adults}"
    )
    return f"https://www.booking.com/searchresults.html?{params}"


@tool
def flight_link(
    origin: str,
    destination: str,
    depart_date: str,
    return_date: str | None = None,
    adults: int = 1,
) -> str:
    """Build a Google Flights search URL.

    Args:
        origin: Airport code (BCN, JFK) or city name.
        destination: Airport code or city name.
        depart_date: ISO date string, YYYY-MM-DD.
        return_date: Optional ISO date string for round-trip. Omit for one-way.
        adults: Number of adult passengers. Defaults to 1.

    Returns:
        A clickable Google Flights URL.
    """
    if return_date:
        query = (
            f"flights from {origin} to {destination} "
            f"on {depart_date} returning {return_date} for {adults} adults"
        )
    else:
        query = (
            f"flights from {origin} to {destination} "
            f"on {depart_date} for {adults} adults"
        )
    return f"https://www.google.com/travel/flights?q={quote_plus(query)}"


@tool
def map_search_link(query: str, near: str) -> str:
    """Build a Google Maps search URL for finding places near a location.

    Use this for restaurant searches, attractions, neighborhoods.

    Args:
        query: What to search for, e.g. "tapas" or "vegetarian restaurants".
        near: City or neighborhood, e.g. "Gracia, Barcelona".

    Returns:
        A clickable Google Maps URL.
    """
    full_query = f"{query} near {near}"
    return f"https://www.google.com/maps/search/{quote_plus(full_query)}"


# --- Tool registry -----------------------------------------------------------
# This is the list the agent binds to. Add new tools here when you create them.

ALL_TOOLS = [
    web_search,
    booking_link,
    flight_link,
    map_search_link,
]
