from langchain.tools import tool
from ddgs import DDGS
from typing import Optional


@tool
async def duckduckgo_search(
    query: str,
    region: str = "ph-ph",
    max_results: int = 5,
) -> str:
    """
    Search for travel information using DuckDuckGo.

    Args:
        query: Search query (e.g., "best beaches in Cebu", "things to do in Palawan")
        region: Region code for localized results (default: "ph-ph" for Philippines)
        max_results: Maximum number of results to return (default: 5, max: 10)

    Returns:
        Formatted markdown string with search results including titles, snippets, and URLs.
    """
    try:
        # Limit max results
        max_results = min(max_results, 10)

        # Perform search using DuckDuckGo
        with DDGS() as ddgs:
            results = list(ddgs.text(
                query,
                region=region,
                safesearch="moderate",
                max_results=max_results,
            ))

        if not results:
            return f"[ERROR] No results found for: '{query}'"

        # Format results as markdown
        lines = [
            f"## Search Results: {query}",
            "",
            f"Found {len(results)} results:",
            "",
        ]

        for i, result in enumerate(results, 1):
            title = result.get("title", "No title")
            snippet = result.get("body", "No description available")
            url = result.get("href", "")

            lines.append(f"**{i}. {title}**")
            lines.append(f"{snippet}")
            if url:
                lines.append(f"Link: {url}")
            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        return f"[ERROR] Search error: {str(e)}"
