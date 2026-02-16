"""AI Tools module for travel planning."""

from .duckduckgo_search import duckduckgo_search
from .geocode import geocode
from .search_places import search_places
from .weather import get_weather

# Export all available tools
ALL_TOOLS = [
    duckduckgo_search,
    geocode,
    search_places,
    get_weather,
]


def get_tools():
    """Get all available AI tools."""
    return ALL_TOOLS


__all__ = [
    "duckduckgo_search",
    "geocode",
    "search_places",
    "get_weather",
    "get_tools",
    "ALL_TOOLS",
]
