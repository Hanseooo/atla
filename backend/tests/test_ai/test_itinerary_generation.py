"""Unit tests for itinerary generation chain."""

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock

from app.ai.schemas.intent import TravelIntent, ExtraNotes
from app.ai.schemas.itinerary import (
    ActivityData,
    TripDayData,
    ItineraryOutput,
    ItineraryGenerationError,
)
from app.ai.chains.itinerary_generation import (
    generate_itinerary,
    _gather_context,
    _get_categories_for_style,
    _parse_json,
    _convert_to_output,
)


def create_intent(
    destination: str = "Cebu",
    days: int = 3,
    budget: str = "mid",
    companions: str = "solo",
    travel_style: list = None,
    time_of_year: str = None,
) -> TravelIntent:
    """Helper to create TravelIntent with defaults."""
    return TravelIntent(
        destination=destination,
        days=days,
        budget=budget,
        companions=companions,
        travel_style=travel_style or [],
        time_of_year=time_of_year,
    )


class TestActivityDataSchema:
    """Tests for ActivityData schema."""

    def test_activity_creation_minimal(self):
        activity = ActivityData(name="Visit Church")
        assert activity.name == "Visit Church"
        assert activity.category == "activity"
        assert activity.description is None

    def test_activity_creation_full(self):
        activity = ActivityData(
            name="Kawasan Falls",
            description="Beautiful waterfalls",
            category="attraction",
            start_time="09:00",
            duration_minutes=120,
            cost_min=0,
            cost_max=500,
            latitude=9.7928,
            longitude=124.1425,
            notes="Bring waterproof bag",
        )
        assert activity.name == "Kawasan Falls"
        assert activity.category == "attraction"
        assert activity.duration_minutes == 120

    def test_activity_defaults(self):
        activity = ActivityData(name="Test")
        assert activity.cost_min is None
        assert activity.cost_max is None
        assert activity.start_time is None
        assert activity.notes is None


class TestTripDayDataSchema:
    """Tests for TripDayData schema."""

    def test_day_creation(self):
        day = TripDayData(
            day_number=1,
            title="Day 1: Arrival",
            activities=[],
        )
        assert day.day_number == 1
        assert day.daily_tips == []

    def test_day_with_activities(self):
        activities = [
            ActivityData(name="Activity 1", start_time="09:00"),
            ActivityData(name="Activity 2", start_time="14:00"),
        ]
        day = TripDayData(
            day_number=1,
            title="Day 1",
            activities=activities,
            meals={"breakfast": "Hotel", "lunch": "Local", "dinner": "Seafood"},
            daily_tips=["Wear comfortable shoes"],
        )
        assert len(day.activities) == 2
        assert day.meals["breakfast"] == "Hotel"


class TestItineraryOutputSchema:
    """Tests for ItineraryOutput schema."""

    def test_output_creation(self):
        output = ItineraryOutput(
            days_data=[],
            summary="Great trip",
            highlights=["Beach", "Food"],
            estimated_cost={"total_min": 10000, "total_max": 20000},
            tips=["Bring sunscreen"],
            destination="Cebu",
            days=3,
        )
        assert output.destination == "Cebu"
        assert output.days == 3

    def test_output_with_trip_data(self):
        output = ItineraryOutput(
            days_data=[
                TripDayData(
                    day_number=1,
                    title="Day 1",
                    activities=[ActivityData(name="Test")],
                )
            ],
            summary="Summary",
            highlights=["H1"],
            estimated_cost={"total_min": 5000},
            tips=["Tip"],
            destination="Boracay",
            days=5,
            budget="luxury",
            companions="couple",
            travel_style=["beach", "relaxation"],
            time_of_year="December",
            packing_suggestions=["Sunscreen", "Swimsuit"],
        )
        assert output.budget == "luxury"
        assert "beach" in output.travel_style
        assert len(output.packing_suggestions) == 2

    def test_output_defaults(self):
        output = ItineraryOutput(
            days_data=[],
            summary="",
            highlights=[],
            estimated_cost={},
            tips=[],
            destination="Test",
            days=1,
        )
        assert output.budget is None
        assert output.companions is None
        assert output.travel_style == []
        assert output.packing_suggestions == []


class TestGetCategoriesForStyle:
    """Tests for _get_categories_for_style helper function."""

    def test_empty_style(self):
        result = _get_categories_for_style([])
        assert "tourism" in result
        assert "catering" in result

    def test_beach_style(self):
        result = _get_categories_for_style(["beach"])
        assert "tourism" in result
        assert "natural" in result

    def test_food_style(self):
        result = _get_categories_for_style(["food"])
        assert "catering" in result

    def test_culture_style(self):
        result = _get_categories_for_style(["culture"])
        assert "tourism" in result
        assert "entertainment" in result

    def test_adventure_style(self):
        result = _get_categories_for_style(["adventure"])
        assert "tourism" in result
        assert "natural" in result
        assert "sport" in result

    def test_nature_style(self):
        result = _get_categories_for_style(["nature"])
        assert "natural" in result
        assert "tourism" in result

    def test_relaxation_style(self):
        result = _get_categories_for_style(["relaxation"])
        assert "accommodation" in result
        assert "catering" in result

    def test_nightlife_style(self):
        result = _get_categories_for_style(["nightlife"])
        assert "catering" in result
        assert "bar" in result
        assert "entertainment" in result

    def test_multiple_styles(self):
        result = _get_categories_for_style(["beach", "food", "adventure"])
        assert "tourism" in result
        assert "catering" in result
        assert "natural" in result

    def test_unknown_style_ignored(self):
        result = _get_categories_for_style(["unknown_style"])
        # Order may vary, just check both categories present
        assert "tourism" in result
        assert "catering" in result

    def test_mixed_valid_invalid(self):
        result = _get_categories_for_style(["beach", "invalid"])
        assert "tourism" in result
        assert "natural" in result


class TestParseJson:
    """Tests for _parse_json helper function."""

    def test_parse_valid_json(self):
        raw = '{"destination": "Cebu", "days": 5}'
        result = _parse_json(raw)
        assert result["destination"] == "Cebu"
        assert result["days"] == 5

    def test_parse_json_with_whitespace(self):
        raw = '   {"key": "value"}   '
        result = _parse_json(raw)
        assert result["key"] == "value"

    def test_parse_json_in_code_block(self):
        raw = '```json\n{"key": "value"}\n```'
        result = _parse_json(raw)
        assert result["key"] == "value"

    def test_parse_json_in_markdown_code_block(self):
        raw = '```\n{"key": "value"}\n```'
        result = _parse_json(raw)
        assert result["key"] == "value"

    def test_parse_json_with_preceding_text(self):
        raw = 'Here is the itinerary: {"key": "value"}'
        result = _parse_json(raw)
        assert result["key"] == "value"

    def test_parse_json_with_following_text(self):
        raw = '{"key": "value"} is the result.'
        result = _parse_json(raw)
        assert result["key"] == "value"

    def test_parse_json_with_wrapper_text(self):
        raw = 'Some text around {"key": "value"} more text'
        result = _parse_json(raw)
        assert result["key"] == "value"

    def test_parse_invalid_json_raises(self):
        with pytest.raises(ItineraryGenerationError):
            _parse_json("not valid json at all")

    def test_parse_empty_string_raises(self):
        with pytest.raises(ItineraryGenerationError):
            _parse_json("")

    def test_parse_only_text_no_json_raises(self):
        with pytest.raises(ItineraryGenerationError):
            _parse_json("Just some text without JSON")


class TestConvertToOutput:
    """Tests for _convert_to_output helper function."""

    def test_convert_minimal_data(self):
        raw = {
            "summary": "Great trip",
            "highlights": ["Beach"],
            "days": [
                {
                    "day_number": 1,
                    "title": "Day 1",
                    "activities": [],
                }
            ],
            "estimated_cost": {"total_min": 1000},
            "general_tips": ["Tip"],
        }
        intent = create_intent(days=5)

        result = _convert_to_output(raw, intent)

        assert result.summary == "Great trip"
        assert result.destination == "Cebu"
        assert result.days == 5  # From intent, not raw

    def test_convert_with_activities(self):
        raw = {
            "summary": "Trip",
            "highlights": [],
            "days": [
                {
                    "day_number": 1,
                    "title": "Day 1",
                    "activities": [
                        {
                            "name": "Kawasan Falls",
                            "description": "Waterfalls",
                            "category": "attraction",
                            "start_time": "09:00",
                            "duration_minutes": 120,
                            "cost_min": 0,
                            "cost_max": 500,
                        }
                    ],
                    "meals": {"breakfast": "Hotel"},
                    "daily_tips": ["Tip"],
                }
            ],
            "estimated_cost": {},
            "general_tips": [],
            "packing_suggestions": [],
        }
        intent = create_intent()

        result = _convert_to_output(raw, intent)

        assert len(result.days_data) == 1
        assert len(result.days_data[0].activities) == 1
        assert result.days_data[0].activities[0].name == "Kawasan Falls"

    def test_convert_preserves_intent_metadata(self):
        raw = {
            "summary": "Test",
            "highlights": [],
            "days": [],
            "estimated_cost": {},
            "general_tips": [],
        }
        intent = create_intent(
            destination="Boracay",
            days=7,
            budget="luxury",
            companions="couple",
            travel_style=["beach", "relaxation"],
            time_of_year="December",
        )

        result = _convert_to_output(raw, intent)

        assert result.destination == "Boracay"
        assert result.days == 7
        assert result.budget == "luxury"
        assert result.companions == "couple"
        assert result.travel_style == ["beach", "relaxation"]
        assert result.time_of_year == "December"

    def test_convert_handles_missing_fields(self):
        raw = {
            "summary": "Test",
            "days": [],  # Missing highlights, estimated_cost
        }
        intent = create_intent()

        result = _convert_to_output(raw, intent)

        assert result.highlights == []
        assert result.tips == []

    def test_convert_with_packing_suggestions(self):
        raw = {
            "summary": "Test",
            "highlights": [],
            "days": [],
            "estimated_cost": {},
            "general_tips": [],
            "packing_suggestions": ["Sunscreen", "Camera"],
        }
        intent = create_intent()

        result = _convert_to_output(raw, intent)

        assert len(result.packing_suggestions) == 2


class TestGenerateItinerary:
    """Tests for generate_itinerary main function."""

    @pytest.mark.asyncio
    async def test_generate_complete_itinerary(self):
        mock_result = MagicMock()
        mock_result.content = json.dumps({
            "summary": "Amazing trip to Cebu",
            "highlights": ["Kawasan Falls", "Beaches"],
            "days": [
                {
                    "day_number": 1,
                    "title": "Day 1: Arrival",
                    "activities": [
                        {
                            "name": "Check-in",
                            "description": "Hotel check-in",
                            "category": "accommodation",
                            "start_time": "14:00",
                            "duration_minutes": 60,
                            "cost_min": 0,
                            "cost_max": 0,
                        }
                    ],
                    "meals": {"breakfast": "Hotel"},
                    "daily_tips": ["Rest after travel"],
                }
            ],
            "estimated_cost": {"total_min": 10000, "total_max": 20000},
            "general_tips": ["Bring sunscreen"],
            "packing_suggestions": ["Swimsuit"],
        })

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_result)

        with patch("app.ai.chains.itinerary_generation.LLMFactory.create_llm") as mock_factory, \
             patch("app.ai.chains.itinerary_generation.PromptTemplate") as mock_prompt_cls, \
             patch("app.ai.chains.itinerary_generation._gather_context") as mock_gather:
            mock_factory.return_value = MagicMock()
            mock_prompt_instance = MagicMock()
            mock_prompt_instance.__or__ = MagicMock(return_value=mock_chain)
            mock_prompt_cls.return_value = mock_prompt_instance
            mock_gather.return_value = ("places data", "weather data")

            intent = create_intent()
            result = await generate_itinerary(intent)

            assert result.destination == "Cebu"
            assert result.days == 3
            assert len(result.days_data) == 1

    @pytest.mark.asyncio
    async def test_generate_handles_llm_list_response(self):
        mock_result = MagicMock()
        mock_result.content = [
            json.dumps({
                "summary": "Test",
                "highlights": [],
                "days": [],
                "estimated_cost": {},
                "general_tips": [],
            })
        ]

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_result)

        with patch("app.ai.chains.itinerary_generation.LLMFactory.create_llm") as mock_factory, \
             patch("app.ai.chains.itinerary_generation.PromptTemplate") as mock_prompt_cls, \
             patch("app.ai.chains.itinerary_generation._gather_context") as mock_gather:
            mock_factory.return_value = MagicMock()
            mock_prompt_instance = MagicMock()
            mock_prompt_instance.__or__ = MagicMock(return_value=mock_chain)
            mock_prompt_cls.return_value = mock_prompt_instance
            mock_gather.return_value = ("", "")

            intent = create_intent()
            result = await generate_itinerary(intent)

            assert result.summary == "Test"

    @pytest.mark.asyncio
    async def test_generate_raises_on_invalid_json(self):
        mock_result = MagicMock()
        mock_result.content = "invalid json response"

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_result)

        with patch("app.ai.chains.itinerary_generation.LLMFactory.create_llm") as mock_factory, \
             patch("app.ai.chains.itinerary_generation.PromptTemplate") as mock_prompt_cls, \
             patch("app.ai.chains.itinerary_generation._gather_context") as mock_gather:
            mock_factory.return_value = MagicMock()
            mock_prompt_instance = MagicMock()
            mock_prompt_instance.__or__ = MagicMock(return_value=mock_chain)
            mock_prompt_cls.return_value = mock_prompt_instance
            mock_gather.return_value = ("", "")

            intent = create_intent()

            with pytest.raises(ItineraryGenerationError):
                await generate_itinerary(intent)

    @pytest.mark.asyncio
    async def test_generate_handles_llm_exception(self):
        with patch("app.ai.chains.itinerary_generation.LLMFactory.create_llm") as mock_factory, \
             patch("app.ai.chains.itinerary_generation._gather_context") as mock_gather:
            mock_factory.side_effect = Exception("API Error")
            mock_gather.return_value = ("", "")

            intent = create_intent()

            with pytest.raises(ItineraryGenerationError):
                await generate_itinerary(intent)

    @pytest.mark.asyncio
    async def test_generate_uses_travel_style_in_prompt(self):
        mock_result = MagicMock()
        mock_result.content = json.dumps({
            "summary": "Test",
            "highlights": [],
            "days": [],
            "estimated_cost": {},
            "general_tips": [],
        })

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_result)

        with patch("app.ai.chains.itinerary_generation.LLMFactory.create_llm") as mock_factory, \
             patch("app.ai.chains.itinerary_generation.PromptTemplate") as mock_prompt_cls, \
             patch("app.ai.chains.itinerary_generation._gather_context") as mock_gather:
            mock_factory.return_value = MagicMock()
            mock_prompt_instance = MagicMock()
            mock_prompt_instance.__or__ = MagicMock(return_value=mock_chain)
            mock_prompt_cls.return_value = mock_prompt_instance
            mock_gather.return_value = ("", "")

            intent = create_intent(travel_style=["beach", "food"])
            result = await generate_itinerary(intent)

            # Verify the chain was invoked
            mock_chain.ainvoke.assert_called_once()
            call_args = mock_chain.ainvoke.call_args[0][0]
            assert "beach" in call_args["travel_style"]
            assert "food" in call_args["travel_style"]

    @pytest.mark.asyncio
    async def test_generate_uses_default_budget(self):
        mock_result = MagicMock()
        mock_result.content = json.dumps({
            "summary": "Test",
            "highlights": [],
            "days": [],
            "estimated_cost": {},
            "general_tips": [],
        })

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_result)

        with patch("app.ai.chains.itinerary_generation.LLMFactory.create_llm") as mock_factory, \
             patch("app.ai.chains.itinerary_generation.PromptTemplate") as mock_prompt_cls, \
             patch("app.ai.chains.itinerary_generation._gather_context") as mock_gather:
            mock_factory.return_value = MagicMock()
            mock_prompt_instance = MagicMock()
            mock_prompt_instance.__or__ = MagicMock(return_value=mock_chain)
            mock_prompt_cls.return_value = mock_prompt_instance
            mock_gather.return_value = ("", "")

            intent = create_intent(budget=None)
            result = await generate_itinerary(intent)

            mock_chain.ainvoke.assert_called_once()
            call_args = mock_chain.ainvoke.call_args[0][0]
            assert call_args["budget"] == "mid"

    @pytest.mark.asyncio
    async def test_generate_uses_default_companions(self):
        mock_result = MagicMock()
        mock_result.content = json.dumps({
            "summary": "Test",
            "highlights": [],
            "days": [],
            "estimated_cost": {},
            "general_tips": [],
        })

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_result)

        with patch("app.ai.chains.itinerary_generation.LLMFactory.create_llm") as mock_factory, \
             patch("app.ai.chains.itinerary_generation.PromptTemplate") as mock_prompt_cls, \
             patch("app.ai.chains.itinerary_generation._gather_context") as mock_gather:
            mock_factory.return_value = MagicMock()
            mock_prompt_instance = MagicMock()
            mock_prompt_instance.__or__ = MagicMock(return_value=mock_chain)
            mock_prompt_cls.return_value = mock_prompt_instance
            mock_gather.return_value = ("", "")

            intent = create_intent(companions=None)
            result = await generate_itinerary(intent)

            mock_chain.ainvoke.assert_called_once()
            call_args = mock_chain.ainvoke.call_args[0][0]
            assert call_args["companions"] == "solo"


class TestGatherContext:
    """Tests for _gather_context helper function."""

    @pytest.mark.asyncio
    async def test_gather_context_success(self):
        intent = create_intent(destination="Cebu", travel_style=["beach"])

        with patch("app.ai.tools.geocode.geocode") as mock_geocode, \
             patch("app.ai.tools.search_places.search_places") as mock_places, \
             patch("app.ai.tools.weather.get_weather") as mock_weather:
            mock_geocode.ainvoke = AsyncMock(return_value="10.0,124.0")
            mock_places.ainvoke = AsyncMock(return_value="Beach resorts found")
            mock_weather.ainvoke = AsyncMock(return_value="Sunny 28C")

            places, weather = await _gather_context(intent)

            assert "Beach resorts" in places
            assert "Sunny" in weather

    @pytest.mark.asyncio
    async def test_gather_context_handles_invalid_coordinates(self):
        intent = create_intent(destination="Invalid")

        with patch("app.ai.tools.geocode.geocode") as mock_geocode:
            mock_geocode.ainvoke = AsyncMock(return_value="invalid")

            places, weather = await _gather_context(intent)

            assert places == "No places data available."
            assert weather == "No weather data available."

    @pytest.mark.asyncio
    async def test_gather_context_handles_error(self):
        intent = create_intent(destination="Cebu")

        with patch("app.ai.tools.geocode.geocode") as mock_geocode:
            mock_geocode.ainvoke = AsyncMock(side_effect=Exception("API Error"))

            places, weather = await _gather_context(intent)

            assert places == "No places data available."
            assert weather == "No weather data available."

    @pytest.mark.asyncio
    async def test_gather_context_handles_exception_in_gather(self):
        intent = create_intent(destination="Cebu", travel_style=["beach"])

        with patch("app.ai.tools.geocode.geocode") as mock_geocode:
            mock_geocode.ainvoke = AsyncMock(return_value="10.0,124.0")
            with patch("app.ai.tools.search_places.search_places") as mock_places:
                mock_places.ainvoke = AsyncMock(side_effect=Exception("Error"))
                with patch("app.ai.tools.weather.get_weather") as mock_weather:
                    mock_weather.ainvoke = AsyncMock(side_effect=Exception("Error"))

                    places, weather = await _gather_context(intent)

                    # Should still return with empty defaults
                    assert isinstance(places, str)
                    assert isinstance(weather, str)


class TestItineraryGenerationError:
    """Tests for ItineraryGenerationError exception."""

    def test_error_creation(self):
        error = ItineraryGenerationError("Test error")
        assert str(error) == "Test error"

    def test_error_chaining_with_cause(self):
        original = ValueError("Original")
        try:
            raise original
        except ValueError:
            error = ItineraryGenerationError("Wrapped")
            error.__cause__ = original
            assert error.__cause__ == original
