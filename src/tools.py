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


def _parse_iso_date(value: str, field_name: str) -> date | None:
    """Parse YYYY-MM-DD; return None if invalid."""
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        return None


def _date_error(value: str, field_name: str) -> str:
    return f"Error: {field_name} must be YYYY-MM-DD (got {value!r})."


# --- Web search via Tavily ---------------------------------------------------

@tool
def web_search(query: str) -> str:
    """Search the live web for current travel information.

    Call this BEFORE writing the final itinerary — at least once per trip.
    Use for: events, weather, seasonal closures, attraction hours, reservation
    lead times, or anything time-sensitive.

    Args:
        query: A focused search query, e.g. "Barcelona events May 2026" or
            "Sagrada Familia tickets advance booking".

    Returns:
        Top search results with titles, URLs, and snippets.
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
    """Build a Booking.com lodging search URL (required for every itinerary).

    Call after you have destination and dates. Paste the returned URL in the
    "## Booking links" section of your response.

    Args:
        destination: City or area, e.g. "Barcelona" or "Tokyo Shibuya".
        checkin: Trip start / hotel check-in, YYYY-MM-DD.
        checkout: Trip end / hotel check-out, YYYY-MM-DD (day after last night).
        adults: Number of adult guests from party size.

    Returns:
        Clickable Booking.com search URL with dates and guests pre-filled.
    """
    checkin_d = _parse_iso_date(checkin, "checkin")
    if checkin_d is None:
        return _date_error(checkin, "checkin")
    checkout_d = _parse_iso_date(checkout, "checkout")
    if checkout_d is None:
        return _date_error(checkout, "checkout")
    if checkout_d <= checkin_d:
        return "Error: checkout must be after checkin (YYYY-MM-DD)."
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
    """Build a Google Flights search URL (required for every itinerary).

    Call after you have origin city/airport and trip dates. Paste the returned
    URL in the "## Booking links" section.

    Args:
        origin: User's home city or airport code, e.g. "JFK" or "Chicago".
        destination: Trip city or airport code, e.g. "BCN" or "Barcelona".
        depart_date: Outbound date, YYYY-MM-DD.
        return_date: Return date YYYY-MM-DD for round-trip; omit for one-way.
        adults: Number of adult passengers.

    Returns:
        Clickable Google Flights URL.
    """
    dep = _parse_iso_date(depart_date, "depart_date")
    if dep is None:
        return _date_error(depart_date, "depart_date")
    if return_date:
        ret = _parse_iso_date(return_date, "return_date")
        if ret is None:
            return _date_error(return_date, "return_date")
        if ret < dep:
            return "Error: return_date must be on or after depart_date."
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
    """Build a Google Maps search URL for restaurants or places.

    Call for meal suggestions or neighborhood exploration; include at least one
    map link in the itinerary or Booking links section.

    Args:
        query: What to find, e.g. "tapas restaurants" or "quiet temples".
        near: City or neighborhood, e.g. "Gothic Quarter, Barcelona".

    Returns:
        Clickable Google Maps search URL.
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
