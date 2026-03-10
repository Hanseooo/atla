"""Itinerary generation chain.

This module implements the core itinerary generation logic for the Atla travel
planner. It gathers real-world data from external APIs using tools and then
uses an LLM to generate a complete, personalized day-by-day itinerary.
"""

import asyncio
import json
import logging
import re
from typing import Optional

from langchain_core.prompts import PromptTemplate

from app.ai.models.llms.gemini import LLMFactory
from app.ai.prompts.itinerary_generation import ITINERARY_GENERATION_PROMPT
from app.ai.schemas.intent import TravelIntent
from app.ai.schemas.itinerary import (
    ActivityData,
    ItineraryGenerationError,
    ItineraryOutput,
    TripDayData,
)

logger = logging.getLogger(__name__)


async def generate_itinerary(intent: TravelIntent) -> ItineraryOutput:
    """Generate a complete day-by-day itinerary from a travel intent.

    This function orchestrates the full itinerary generation pipeline:
    1. Geocode the destination to get coordinates.
    2. Concurrently gather places data and weather forecast.
    3. Invoke the LLM with the gathered context.
    4. Parse and validate the JSON response.
    5. Convert to ``ItineraryOutput``.

    Args:
        intent: A fully-complete ``TravelIntent`` with at minimum destination,
            days, budget, and companions populated.

    Returns:
        ``ItineraryOutput`` containing days, activities, cost estimates, and tips.

    Raises:
        ItineraryGenerationError: If the LLM call or parsing fails.
    """
    try:
        # Step 1: Gather external data concurrently
        places_data, weather_data = await _gather_context(intent)

        # Step 2: Build and invoke LLM chain
        llm = LLMFactory.create_llm(model_name="gemini-2.5-flash-lite", temp=0.7)

        prompt = PromptTemplate(
            template=ITINERARY_GENERATION_PROMPT,
            input_variables=[
                "destination",
                "days",
                "budget",
                "companions",
                "travel_style",
                "time_of_year",
                "extra_notes",
                "places_data",
                "weather_data",
            ],
        )

        chain = prompt | llm

        result = await chain.ainvoke(
            {
                "destination": intent.destination,
                "days": intent.days,
                "budget": intent.budget or "mid",
                "companions": intent.companions or "solo",
                "travel_style": ", ".join(intent.travel_style) if intent.travel_style else "general sightseeing",
                "time_of_year": intent.time_of_year or "Not specified",
                "extra_notes": json.dumps(intent.extra_notes.model_dump(), indent=2),
                "places_data": places_data,
                "weather_data": weather_data,
            }
        )

        # Step 3: Parse the LLM response
        raw_text = result.content if hasattr(result, "content") else str(result)
        if isinstance(raw_text, list):
            raw_text = raw_text[0]

        raw_itinerary = _parse_json(raw_text)

        # Step 4: Convert to ItineraryOutput
        return _convert_to_output(raw_itinerary, intent)

    except ItineraryGenerationError:
        raise
    except Exception as e:
        logger.error(f"Itinerary generation failed: {e}", exc_info=True)
        raise ItineraryGenerationError(f"Failed to generate itinerary: {str(e)}") from e


async def _gather_context(intent: TravelIntent) -> tuple[str, str]:
    """Geocode destination and concurrently fetch places and weather data.

    Args:
        intent: Travel intent containing destination and preferences.

    Returns:
        Tuple of (places_data_str, weather_data_str).
    """
    places_data = "No places data available."
    weather_data = "No weather data available."

    try:
        # Import tools here to avoid circular imports and allow easy mocking
        from app.ai.tools.geocode import geocode
        from app.ai.tools.search_places import search_places
        from app.ai.tools.weather import get_weather

        # Geocode the destination
        coordinates_str = await geocode.ainvoke({"query": f"{intent.destination}, Philippines"})

        if coordinates_str and not coordinates_str.startswith("error"):
            try:
                lat_str, lon_str = coordinates_str.split(",")
                lat = float(lat_str.strip())
                lon = float(lon_str.strip())

                # Determine categories based on travel style
                categories = _get_categories_for_style(intent.travel_style)

                # Fetch places and weather concurrently
                places_task = search_places.ainvoke({
                    "latitude": lat,
                    "longitude": lon,
                    "radius": 10000,
                    "categories": categories,
                    "limit": 30,
                })
                weather_task = get_weather.ainvoke({
                    "latitude": lat,
                    "longitude": lon,
                })

                places_result, weather_result = await asyncio.gather(
                    places_task, weather_task, return_exceptions=True
                )

                if isinstance(places_result, str):
                    places_data = places_result
                if isinstance(weather_result, str):
                    weather_data = weather_result

            except (ValueError, AttributeError) as parse_err:
                logger.warning(f"Could not parse coordinates '{coordinates_str}': {parse_err}")

    except Exception as e:
        logger.warning(f"Could not gather context data: {e}")

    return places_data, weather_data


def _get_categories_for_style(travel_style: list) -> str:
    """Map travel style preferences to Geoapify place categories.

    Args:
        travel_style: List of style strings such as ``["beach", "food"]``.

    Returns:
        Comma-separated Geoapify category string.
    """
    category_map = {
        "food": "catering",
        "culture": "tourism,entertainment",
        "adventure": "tourism,natural,sport",
        "nature": "natural,tourism",
        "beach": "tourism,natural",
        "relaxation": "accommodation,catering",
        "nightlife": "catering.bar,entertainment",
    }

    categories = {"tourism", "catering"}  # always include basics
    for style in travel_style:
        if style in category_map:
            for cat in category_map[style].split(","):
                categories.add(cat.strip())

    return ",".join(categories)


def _parse_json(raw_text: str) -> dict:
    """Parse and extract a JSON object from LLM response text.

    Handles cases where the LLM wraps JSON in markdown code blocks or adds
    explanatory prose before/after the JSON object.

    Args:
        raw_text: Raw string output from the LLM.

    Returns:
        Parsed dictionary.

    Raises:
        ItineraryGenerationError: If no valid JSON can be extracted.
    """
    # Try direct parse first
    try:
        return json.loads(raw_text.strip())
    except json.JSONDecodeError:
        pass

    # Strip markdown code fences
    code_block = re.search(r"```(?:json)?\s*([\s\S]+?)```", raw_text)
    if code_block:
        try:
            return json.loads(code_block.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Find the outermost JSON object
    match = re.search(r"\{[\s\S]+\}", raw_text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    raise ItineraryGenerationError(
        f"Could not parse JSON from LLM response. Response starts with: {raw_text[:200]}"
    )


def _convert_to_output(raw: dict, intent: TravelIntent) -> ItineraryOutput:
    """Convert a raw LLM JSON dict to a structured ``ItineraryOutput``.

    Args:
        raw: Dict parsed from the LLM JSON response.
        intent: Original travel intent for metadata.

    Returns:
        ``ItineraryOutput`` with fully typed days and activities.
    """
    days_data: list[TripDayData] = []

    for day_raw in raw.get("days", []):
        activities: list[ActivityData] = []
        for act_raw in day_raw.get("activities", []):
            activities.append(
                ActivityData(
                    name=act_raw.get("name", "Activity"),
                    description=act_raw.get("description"),
                    category=act_raw.get("category", "activity"),
                    start_time=act_raw.get("start_time"),
                    duration_minutes=act_raw.get("duration_minutes"),
                    cost_min=act_raw.get("cost_min"),
                    cost_max=act_raw.get("cost_max"),
                    notes=act_raw.get("notes"),
                )
            )

        days_data.append(
            TripDayData(
                day_number=day_raw.get("day_number", len(days_data) + 1),
                title=day_raw.get("title", f"Day {len(days_data) + 1}"),
                activities=activities,
                meals=day_raw.get("meals"),
                daily_tips=day_raw.get("daily_tips", []),
            )
        )

    return ItineraryOutput(
        days_data=days_data,
        summary=raw.get("summary", ""),
        highlights=raw.get("highlights", []),
        estimated_cost=raw.get("estimated_cost", {}),
        tips=raw.get("general_tips", []),
        packing_suggestions=raw.get("packing_suggestions", []),
        destination=intent.destination or "",
        days=intent.days or len(days_data),
        budget=intent.budget,
        companions=intent.companions,
        travel_style=intent.travel_style,
        time_of_year=intent.time_of_year,
    )
