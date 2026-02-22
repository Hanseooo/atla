from langchain.tools import tool
import httpx
from app.config import settings
from typing import List, Dict, Any


DEFAULT_CATEGORIES = "catering,tourism,entertainment"

CATEGORY_ICONS = {
    "catering": "🍽️",
    "tourism": "🎯",
    "entertainment": "🎭",
    "accommodation": "🏨",
    "commercial": "🛍️",
    "natural": "🏞️",
    "leisure": "🎪",
    "sport": "⚽",
}

CATEGORY_DESCRIPTIONS = {
    "catering.restaurant": "Restaurant",
    "catering.cafe": "Cafe",
    "catering.bar": "Bar",
    "catering.fast_food": "Fast Food",
    "tourism.attraction": "Tourist Attraction",
    "tourism.sights": "Landmark",
    "entertainment.museum": "Museum",
    "entertainment.cinema": "Cinema",
    "entertainment.theme_park": "Theme Park",
    "accommodation.hotel": "Hotel",
    "accommodation.hostel": "Hostel",
    "commercial.shopping_mall": "Shopping Mall",
    "commercial.supermarket": "Supermarket",
}


def get_category_icon(category: str) -> str:
    """Get emoji icon for category."""
    for key, icon in CATEGORY_ICONS.items():
        if key in category:
            return icon
    return "📍"


def get_category_description(category: str) -> str:
    """Get human-readable category description."""
    for key, desc in CATEGORY_DESCRIPTIONS.items():
        if key in category:
            return desc
    return category.split(".")[-1].replace("_", " ").title()


def get_trip_planning_hint(categories: List[str]) -> str:
    """Generate contextual hint based on place category."""
    hints = {
        "catering.restaurant": "Good for meals, reservations recommended for dinner",
        "catering.cafe": "Good for quick breaks, coffee, or light snacks",
        "catering.bar": "Evening/night spot, check opening hours",
        "tourism.attraction": "Popular tourist spot, may be crowded during peak hours",
        "tourism.sights": "Photo opportunity, great for sightseeing",
        "entertainment.museum": "Check opening days/hours, allow 1-2 hours",
        "entertainment.cinema": "Book tickets in advance",
        "entertainment.theme_park": "Full day activity, arrive early",
        "accommodation.hotel": "Potential stay option",
        "commercial.shopping_mall": "Good for shopping, food courts, air conditioning",
    }

    for cat in categories:
        for key, hint in hints.items():
            if key in cat:
                return hint
    return "Explore this place based on your interests"


def format_place(place: Dict[str, Any], index: int) -> str:
    """Format a single place into markdown string."""
    properties = place.get("properties", {})

    # Basic info
    name = properties.get("name", "Unnamed Place")
    formatted_cat = get_category_description(properties.get("categories", [""])[0])
    rating = properties.get("rating")

    # Location info
    address = properties.get("formatted", "Address not available")
    lat = properties.get("lat")
    lon = properties.get("lon")
    distance = properties.get("distance")

    # Contact info
    website = properties.get("website")
    phone = properties.get("phone")

    # Categories for hints
    categories = properties.get("categories", [])
    hint = get_trip_planning_hint(categories)

    # Build output
    lines = [f"**{index}. {name}** - {formatted_cat}"]

    if rating:
        lines.append(f"⭐ {rating}")

    lines.append(f"📍 {address}")

    if website or phone:
        contact_parts = []
        if website:
            contact_parts.append(f"🌐 {website}")
        if phone:
            contact_parts.append(f"📞 {phone}")
        lines.append(" | ".join(contact_parts))

    distance_str = f"📏 {distance}m away" if distance else ""
    cat_tags = f"🏷️ `{', '.join(categories[:2])}`" if categories else ""
    if distance_str or cat_tags:
        lines.append(f"{distance_str} | {cat_tags}")

    if lat and lon:
        lines.append(f"📍 Coordinates: {lat}, {lon}")

    lines.append(f"💡 {hint}")

    return "\n".join(lines)


def group_places_by_category(places: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group places by their primary category."""
    grouped = {}
    for place in places:
        categories = place.get("properties", {}).get("categories", [])
        primary_cat = categories[0] if categories else "other"

        # Get top-level category
        top_level = primary_cat.split(".")[0] if "." in primary_cat else primary_cat

        if top_level not in grouped:
            grouped[top_level] = []
        grouped[top_level].append(place)

    return grouped


def format_results(places: List[Dict[str, Any]], lat: float, lon: float, radius: int) -> str:
    """Format all places into a markdown summary."""
    if not places:
        return f"❌ No places found within {radius}m of coordinates [{lat}, {lon}]"

    # Header
    lines = [
        f"## 🔍 Found {len(places)} places within {radius}m of [{lat}, {lon}]",
        "",
        "---",
        "",
    ]

    # Group by category
    grouped = group_places_by_category(places)

    # Track global index for numbering
    global_index = 1

    for category, cat_places in grouped.items():
        icon = get_category_icon(category)
        lines.append(f"### {icon} {category.upper()} ({len(cat_places)} places)")
        lines.append("")

        for place in cat_places:
            lines.append(format_place(place, global_index))
            lines.append("")
            global_index += 1

        lines.append("---")
        lines.append("")

    # Footer with tips
    lines.extend([
        "### 💡 Trip Planning Tips",
        "",
        "- **Coordinates**: Use latitude,longitude for precise navigation",
        "- **Distance**: Walking distance approx: 100m = 1-2 mins, 1000m = 12-15 mins",
        "- **Ratings**: ⭐ ratings are out of 5, based on user reviews",
        "- **Best Route**: Group nearby places to minimize travel time",
        "",
    ])

    return "\n".join(lines)


@tool
async def search_places(
    latitude: float,
    longitude: float,
    radius: int = 5000,
    categories: str = DEFAULT_CATEGORIES,
    limit: int = 20,
) -> str:
    """
    Search for places near a location using Geoapify Places API.

    Args:
        latitude: Latitude of search center (e.g., 14.5995 for Manila)
        longitude: Longitude of search center (e.g., 120.9842 for Manila)
        radius: Search radius in meters (default: 5000 = 5km)
        categories: Comma-separated categories (default: "catering,tourism,entertainment")
                   Options: catering, tourism, entertainment, accommodation,
                           commercial, natural, leisure, sport
        limit: Maximum number of results (default: 20, max: 100)

    Returns:
        Formatted markdown string with places grouped by category,
        including names, addresses, coordinates, ratings, and trip tips.
    """
    # Build filter string for circle search
    filter_str = f"circle:{longitude},{latitude},{radius}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://api.geoapify.com/v2/places",
                params={
                    "categories": categories,
                    "filter": filter_str,
                    "limit": min(limit, 100),  # API max is 100
                    "apiKey": settings.GEOAPIFY_API_KEY,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()

            places = data.get("features", [])
            return format_results(places, latitude, longitude, radius)

        except httpx.HTTPError as e:
            return f"❌ API Error: Failed to fetch places - {str(e)}"
        except Exception as e:
            return f"❌ Error: {str(e)}"
