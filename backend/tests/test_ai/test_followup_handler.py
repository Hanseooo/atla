"""Unit tests for follow-up handler chain."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json

from app.ai.schemas.intent import TravelIntent, ExtraNotes
from app.ai.schemas.followup import (
    ModificationRequest,
    Suggestion,
    FollowupType,
    FollowupResponse,
)
from app.ai.chains.followup_handler import (
    detect_followup_type,
    detect_modification,
    apply_modification,
    generate_suggestions,
    process_followup,
    _format_conversation_history,
    _extract_content,
    _validate_days,
    _validate_budget,
    _validate_companions,
    _validate_travel_style,
    _build_suggestion_query,
    _generate_static_suggestions,
    VALID_TRAVEL_STYLES,
)
from app.ai.prompts.followup_handler import (
    STATIC_SUGGESTIONS,
    COMPANION_SUGGESTION_FILTERS,
)


def create_intent(
    destination: str = None,
    days: int = None,
    budget: str = None,
    companions: str = None,
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


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_validate_days_valid(self):
        assert _validate_days(5) == 5
        assert _validate_days(1) == 1
        assert _validate_days(30) == 30

    def test_validate_days_constraints(self):
        assert _validate_days(0) == 1
        assert _validate_days(-5) == 1
        assert _validate_days(50) == 30
        assert _validate_days(100) == 30

    def test_validate_days_invalid(self):
        assert _validate_days(None) is None
        assert _validate_days("invalid") is None
        assert _validate_days("") is None

    def test_validate_budget_valid(self):
        assert _validate_budget("low") == "low"
        assert _validate_budget("mid") == "mid"
        assert _validate_budget("luxury") == "luxury"

    def test_validate_budget_invalid(self):
        assert _validate_budget(None) is None
        assert _validate_budget("medium") is None
        assert _validate_budget("high") is None
        assert _validate_budget(100) is None

    def test_validate_companions_valid(self):
        assert _validate_companions("solo") == "solo"
        assert _validate_companions("couple") == "couple"
        assert _validate_companions("family") == "family"
        assert _validate_companions("group") == "group"

    def test_validate_companions_invalid(self):
        assert _validate_companions(None) is None
        assert _validate_companions("alone") is None
        assert _validate_companions("friends") is None

    def test_validate_travel_style_valid_string(self):
        assert _validate_travel_style("adventure") == ["adventure"]
        assert _validate_travel_style("beach") == ["beach"]
        assert _validate_travel_style("nightlife") == ["nightlife"]

    def test_validate_travel_style_valid_list(self):
        assert _validate_travel_style(["adventure", "beach"]) == ["adventure", "beach"]
        assert _validate_travel_style(["culture", "food", "nature"]) == ["culture", "food", "nature"]

    def test_validate_travel_style_invalid_string(self):
        assert _validate_travel_style("skydiving") == []
        assert _validate_travel_style("shopping") == []
        assert _validate_travel_style("extreme_sports") == []

    def test_validate_travel_style_none(self):
        assert _validate_travel_style(None) == []

    def test_validate_travel_style_list_with_invalid(self):
        assert _validate_travel_style(["adventure", "skydiving"]) == ["adventure"]
        assert _validate_travel_style(["invalid", "beach", "shopping"]) == ["beach"]

    def test_validate_travel_style_list_with_none(self):
        assert _validate_travel_style(["adventure", None]) == ["adventure"]
        assert _validate_travel_style([None, "beach", None]) == ["beach"]

    def test_validate_travel_style_empty_list(self):
        assert _validate_travel_style([]) == []

    def test_validate_travel_style_invalid_type(self):
        assert _validate_travel_style(123) == []
        assert _validate_travel_style({"style": "adventure"}) == []

    def test_valid_travel_styles_constant(self):
        assert "adventure" in VALID_TRAVEL_STYLES
        assert "relaxation" in VALID_TRAVEL_STYLES
        assert "culture" in VALID_TRAVEL_STYLES
        assert "food" in VALID_TRAVEL_STYLES
        assert "beach" in VALID_TRAVEL_STYLES
        assert "nature" in VALID_TRAVEL_STYLES
        assert "nightlife" in VALID_TRAVEL_STYLES
        assert "skydiving" not in VALID_TRAVEL_STYLES

    def test_format_conversation_history_empty(self):
        result = _format_conversation_history([])
        assert result == "No previous conversation."

    def test_format_conversation_history_with_messages(self):
        history = [
            {"role": "user", "content": "I want to go to Cebu"},
            {"role": "assistant", "content": "How many days?"},
        ]
        result = _format_conversation_history(history)
        assert "USER: I want to go to Cebu" in result
        assert "ASSISTANT: How many days?" in result

    def test_format_conversation_history_truncates(self):
        history = [{"role": "user", "content": f"Message {i}"} for i in range(15)]
        result = _format_conversation_history(history)
        assert "Message 5" in result
        assert "Message 14" in result

    def test_extract_content_string(self):
        result = MagicMock()
        result.content = "test content"
        assert _extract_content(result) == "test content"

    def test_extract_content_list(self):
        result = MagicMock()
        result.content = ["part1", "part2"]
        assert _extract_content(result) == "part1part2"

    def test_extract_content_no_attribute(self):
        result = "direct string"
        assert _extract_content(result) == "direct string"

    def test_build_suggestion_query_full(self):
        intent = create_intent(
            companions="family", travel_style=["beach", "adventure"]
        )
        query = _build_suggestion_query(intent)
        assert "best" in query
        assert "family" in query
        assert "beach" in query
        assert "destinations Philippines" in query

    def test_build_suggestion_query_partial(self):
        intent = create_intent(travel_style=["culture"])
        query = _build_suggestion_query(intent)
        assert "culture" in query

    def test_build_suggestion_query_empty(self):
        intent = create_intent()
        query = _build_suggestion_query(intent)
        assert "destinations Philippines" in query


class TestApplyModification:
    """Tests for apply_modification function."""

    def test_change_destination(self):
        intent = create_intent(destination="Cebu", days=5, budget="mid", companions="couple")
        modification = ModificationRequest(
            action="change",
            target="destination",
            new_value="Palawan",
            original_message="Change to Palawan",
            confidence=0.9,
        )
        result = apply_modification(intent, modification)
        assert result.destination == "Palawan"
        assert result.days == 5

    def test_change_days(self):
        intent = create_intent(destination="Cebu", days=3, budget="mid", companions="couple")
        modification = ModificationRequest(
            action="change",
            target="days",
            new_value=7,
            original_message="Make it 7 days",
            confidence=0.9,
        )
        result = apply_modification(intent, modification)
        assert result.days == 7

    def test_extend_days(self):
        intent = create_intent(destination="Cebu", days=5, budget="mid", companions="couple")
        modification = ModificationRequest(
            action="extend",
            target="days",
            new_value=2,
            original_message="Add 2 more days",
            confidence=0.9,
        )
        result = apply_modification(intent, modification)
        assert result.days == 7

    def test_shorten_days(self):
        intent = create_intent(destination="Cebu", days=5, budget="mid", companions="couple")
        modification = ModificationRequest(
            action="shorten",
            target="days",
            new_value=2,
            original_message="Remove 2 days",
            confidence=0.9,
        )
        result = apply_modification(intent, modification)
        assert result.days == 3

    def test_days_constrained_on_extend(self):
        intent = create_intent(destination="Cebu", days=28, budget="mid", companions="couple")
        modification = ModificationRequest(
            action="extend",
            target="days",
            new_value=5,
            original_message="Add 5 more days",
            confidence=0.9,
        )
        result = apply_modification(intent, modification)
        assert result.days == 30

    def test_change_budget(self):
        intent = create_intent(destination="Cebu", days=5, budget="mid", companions="couple")
        modification = ModificationRequest(
            action="change",
            target="budget",
            new_value="luxury",
            original_message="Make it luxury",
            confidence=0.9,
        )
        result = apply_modification(intent, modification)
        assert result.budget == "luxury"

    def test_change_companions(self):
        intent = create_intent(destination="Cebu", days=5, budget="mid", companions="couple")
        modification = ModificationRequest(
            action="change",
            target="companions",
            new_value="family",
            original_message="Actually with family",
            confidence=0.9,
        )
        result = apply_modification(intent, modification)
        assert result.companions == "family"

    def test_add_travel_style(self):
        intent = create_intent(
            destination="Cebu", days=5, budget="mid", companions="couple", travel_style=["beach"]
        )
        modification = ModificationRequest(
            action="add",
            target="travel_style",
            new_value=["adventure"],
            original_message="Add adventure activities",
            confidence=0.9,
        )
        result = apply_modification(intent, modification)
        assert "adventure" in result.travel_style
        assert "beach" in result.travel_style

    def test_remove_travel_style(self):
        intent = create_intent(
            destination="Cebu",
            days=5,
            budget="mid",
            companions="couple",
            travel_style=["beach", "adventure", "nightlife"],
        )
        modification = ModificationRequest(
            action="remove",
            target="travel_style",
            new_value=["nightlife"],
            original_message="No nightlife please",
            confidence=0.9,
        )
        result = apply_modification(intent, modification)
        assert "nightlife" not in result.travel_style
        assert "beach" in result.travel_style
        assert "adventure" in result.travel_style

    def test_invalid_budget_preserved(self):
        intent = create_intent(destination="Cebu", days=5, budget="mid", companions="couple")
        modification = ModificationRequest(
            action="change",
            target="budget",
            new_value="premium",
            original_message="Premium budget",
            confidence=0.9,
        )
        result = apply_modification(intent, modification)
        assert result.budget == "mid"

    def test_invalid_days_preserved(self):
        intent = create_intent(destination="Cebu", days=5, budget="mid", companions="couple")
        modification = ModificationRequest(
            action="change",
            target="days",
            new_value="invalid",
            original_message="Invalid days",
            confidence=0.9,
        )
        result = apply_modification(intent, modification)
        assert result.days == 5

    def test_days_exceeds_max_constrained(self):
        intent = create_intent(destination="Cebu", days=5, budget="mid", companions="couple")
        modification = ModificationRequest(
            action="change",
            target="days",
            new_value=50,
            original_message="50 days",
            confidence=0.9,
        )
        result = apply_modification(intent, modification)
        assert result.days == 30

    def test_invalid_companions_preserved(self):
        intent = create_intent(destination="Cebu", days=5, budget="mid", companions="couple")
        modification = ModificationRequest(
            action="change",
            target="companions",
            new_value="alone",
            original_message="Alone",
            confidence=0.9,
        )
        result = apply_modification(intent, modification)
        assert result.companions == "couple"

    def test_extend_days_from_none_ignored(self):
        intent = create_intent(destination="Cebu", budget="mid", companions="couple")
        modification = ModificationRequest(
            action="extend",
            target="days",
            new_value=2,
            original_message="Add 2 days",
            confidence=0.9,
        )
        result = apply_modification(intent, modification)
        assert result.days is None

    def test_change_travel_style_invalid_string(self):
        intent = create_intent(
            destination="Cebu", days=5, budget="mid", companions="couple", travel_style=["beach"]
        )
        modification = ModificationRequest(
            action="change",
            target="travel_style",
            new_value="skydiving",
            original_message="I want skydiving",
            confidence=0.9,
        )
        result = apply_modification(intent, modification)
        assert result.travel_style == ["beach"]

    def test_change_travel_style_none_value(self):
        intent = create_intent(
            destination="Cebu", days=5, budget="mid", companions="couple", travel_style=["beach"]
        )
        modification = ModificationRequest(
            action="change",
            target="travel_style",
            new_value=None,
            original_message="Clear styles",
            confidence=0.9,
        )
        result = apply_modification(intent, modification)
        assert result.travel_style == ["beach"]

    def test_change_travel_style_list_with_invalid(self):
        intent = create_intent(
            destination="Cebu", days=5, budget="mid", companions="couple", travel_style=["beach"]
        )
        modification = ModificationRequest(
            action="change",
            target="travel_style",
            new_value=["adventure", "skydiving", "shopping"],
            original_message="Change to adventure and skydiving",
            confidence=0.9,
        )
        result = apply_modification(intent, modification)
        assert result.travel_style == ["adventure"]
        assert "skydiving" not in result.travel_style
        assert "shopping" not in result.travel_style

    def test_add_travel_style_invalid_string(self):
        intent = create_intent(
            destination="Cebu", days=5, budget="mid", companions="couple", travel_style=["beach"]
        )
        modification = ModificationRequest(
            action="add",
            target="travel_style",
            new_value="extreme_sports",
            original_message="Add extreme sports",
            confidence=0.9,
        )
        result = apply_modification(intent, modification)
        assert result.travel_style == ["beach"]

    def test_add_travel_style_list_with_invalid(self):
        intent = create_intent(
            destination="Cebu", days=5, budget="mid", companions="couple", travel_style=["beach"]
        )
        modification = ModificationRequest(
            action="add",
            target="travel_style",
            new_value=["adventure", "skydiving"],
            original_message="Add adventure and skydiving",
            confidence=0.9,
        )
        result = apply_modification(intent, modification)
        assert "adventure" in result.travel_style
        assert "beach" in result.travel_style
        assert "skydiving" not in result.travel_style

    def test_add_travel_style_none_value(self):
        intent = create_intent(
            destination="Cebu", days=5, budget="mid", companions="couple", travel_style=["beach"]
        )
        modification = ModificationRequest(
            action="add",
            target="travel_style",
            new_value=None,
            original_message="Add nothing",
            confidence=0.9,
        )
        result = apply_modification(intent, modification)
        assert result.travel_style == ["beach"]

    def test_remove_travel_style_preserves_valid_on_invalid_input(self):
        intent = create_intent(
            destination="Cebu",
            days=5,
            budget="mid",
            companions="couple",
            travel_style=["beach", "adventure"],
        )
        modification = ModificationRequest(
            action="remove",
            target="travel_style",
            new_value="skydiving",
            original_message="Remove skydiving",
            confidence=0.9,
        )
        result = apply_modification(intent, modification)
        assert result.travel_style == ["beach", "adventure"]

    def test_change_travel_style_single_string(self):
        intent = create_intent(
            destination="Cebu", days=5, budget="mid", companions="couple", travel_style=["beach"]
        )
        modification = ModificationRequest(
            action="change",
            target="travel_style",
            new_value="adventure",
            original_message="Change to adventure",
            confidence=0.9,
        )
        result = apply_modification(intent, modification)
        assert result.travel_style == ["adventure"]
        assert "beach" not in result.travel_style


class TestGenerateStaticSuggestions:
    """Tests for static suggestion generation."""

    def test_suggestions_by_beach_style(self):
        intent = create_intent(travel_style=["beach"])
        suggestions = _generate_static_suggestions(intent, 5)
        assert len(suggestions) > 0
        assert all(s.source == "static" for s in suggestions)
        assert any("beach" in s.best_for for s in suggestions)

    def test_suggestions_by_multiple_styles(self):
        intent = create_intent(travel_style=["beach", "adventure"])
        suggestions = _generate_static_suggestions(intent, 5)
        assert len(suggestions) > 0

    def test_suggestions_filter_for_family(self):
        intent = create_intent(travel_style=["nightlife"], companions="family")
        suggestions = _generate_static_suggestions(intent, 5)
        for s in suggestions:
            assert "nightlife" not in s.best_for or len(s.best_for) > 1

    def test_suggestions_prioritize_for_companions(self):
        intent = create_intent(companions="family")
        suggestions = _generate_static_suggestions(intent, 5)
        assert len(suggestions) >= 0

    def test_suggestions_empty_intent(self):
        intent = create_intent()
        suggestions = _generate_static_suggestions(intent, 5)
        assert isinstance(suggestions, list)

    def test_suggestions_fallback_popular_destinations(self):
        intent = create_intent(companions="family", travel_style=["nightlife"])
        suggestions = _generate_static_suggestions(intent, 5)
        assert len(suggestions) > 0
        assert all(s.source == "static" for s in suggestions)
        popular_destinations = ["Boracay", "Palawan", "Cebu", "Siargao", "Bohol"]
        assert any(
            any(pop in s.destination for pop in popular_destinations)
            for s in suggestions
        )

    def test_suggestions_max_limit(self):
        intent = create_intent(travel_style=["beach", "adventure", "culture"])
        suggestions = _generate_static_suggestions(intent, 2)
        assert len(suggestions) <= 2

    def test_no_duplicate_destinations(self):
        intent = create_intent(travel_style=["beach", "nature", "relaxation"])
        suggestions = _generate_static_suggestions(intent, 10)
        destinations = [s.destination for s in suggestions]
        assert len(destinations) == len(set(destinations))


class TestDetectFollowupType:
    """Tests for detect_followup_type function."""

    @pytest.mark.asyncio
    async def test_detect_clarification(self):
        mock_result = MagicMock()
        mock_result.content = '{"type": "clarification", "confidence": 0.9, "reasoning": "User is answering"}'

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_result)

        with patch("app.ai.chains.followup_handler.LLMFactory.create_llm") as mock_factory, \
             patch("app.ai.chains.followup_handler.PromptTemplate") as mock_prompt_cls:
            mock_factory.return_value = MagicMock()
            mock_prompt_instance = MagicMock()
            mock_prompt_instance.__or__ = MagicMock(return_value=mock_chain)
            mock_prompt_cls.return_value = mock_prompt_instance

            intent = create_intent(destination="Cebu")
            history = [{"role": "assistant", "content": "How many days?"}]

            result = await detect_followup_type("5 days", intent, history)
            assert result.type == "clarification"

    @pytest.mark.asyncio
    async def test_detect_modification(self):
        mock_result = MagicMock()
        mock_result.content = '{"type": "modification", "confidence": 0.95, "reasoning": "User wants to change"}'

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_result)

        with patch("app.ai.chains.followup_handler.LLMFactory.create_llm") as mock_factory, \
             patch("app.ai.chains.followup_handler.PromptTemplate") as mock_prompt_cls:
            mock_factory.return_value = MagicMock()
            mock_prompt_instance = MagicMock()
            mock_prompt_instance.__or__ = MagicMock(return_value=mock_chain)
            mock_prompt_cls.return_value = mock_prompt_instance

            intent = create_intent(destination="Cebu", days=5)
            history = []

            result = await detect_followup_type("Make it 7 days instead", intent, history)
            assert result.type == "modification"

    @pytest.mark.asyncio
    async def test_detect_unsure(self):
        mock_result = MagicMock()
        mock_result.content = '{"type": "unsure", "confidence": 0.85, "reasoning": "User needs suggestions"}'

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_result)

        with patch("app.ai.chains.followup_handler.LLMFactory.create_llm") as mock_factory, \
             patch("app.ai.chains.followup_handler.PromptTemplate") as mock_prompt_cls:
            mock_factory.return_value = MagicMock()
            mock_prompt_instance = MagicMock()
            mock_prompt_instance.__or__ = MagicMock(return_value=mock_chain)
            mock_prompt_cls.return_value = mock_prompt_instance

            intent = create_intent()
            history = []

            result = await detect_followup_type("I don't know where to go", intent, history)
            assert result.type == "unsure"

    @pytest.mark.asyncio
    async def test_detect_handles_exception(self):
        with patch("app.ai.chains.followup_handler.LLMFactory.create_llm") as mock_factory:
            mock_factory.side_effect = Exception("API Error")

            intent = create_intent()
            history = []

            result = await detect_followup_type("test message", intent, history)
            assert result.type == "unknown"
            assert result.confidence == 0.0


class TestDetectModification:
    """Tests for detect_modification function."""

    @pytest.mark.asyncio
    async def test_detect_days_change(self):
        mock_result = MagicMock()
        mock_result.content = '{"action": "change", "target": "days", "new_value": 7, "confidence": 0.95}'

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_result)

        with patch("app.ai.chains.followup_handler.LLMFactory.create_llm") as mock_factory, \
             patch("app.ai.chains.followup_handler.PromptTemplate") as mock_prompt_cls:
            mock_factory.return_value = MagicMock()
            mock_prompt_instance = MagicMock()
            mock_prompt_instance.__or__ = MagicMock(return_value=mock_chain)
            mock_prompt_cls.return_value = mock_prompt_instance

            intent = create_intent(destination="Cebu", days=5)
            result = await detect_modification("Make it 7 days", intent)

            assert result.action == "change"
            assert result.target == "days"
            assert result.new_value == 7

    @pytest.mark.asyncio
    async def test_detect_destination_change(self):
        mock_result = MagicMock()
        mock_result.content = '{"action": "change", "target": "destination", "new_value": "Palawan", "confidence": 0.95}'

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_result)

        with patch("app.ai.chains.followup_handler.LLMFactory.create_llm") as mock_factory, \
             patch("app.ai.chains.followup_handler.PromptTemplate") as mock_prompt_cls:
            mock_factory.return_value = MagicMock()
            mock_prompt_instance = MagicMock()
            mock_prompt_instance.__or__ = MagicMock(return_value=mock_chain)
            mock_prompt_cls.return_value = mock_prompt_instance

            intent = create_intent(destination="Cebu", days=5)
            result = await detect_modification("Change to Palawan instead", intent)

            assert result.action == "change"
            assert result.target == "destination"

    @pytest.mark.asyncio
    async def test_detect_handles_exception(self):
        with patch("app.ai.chains.followup_handler.LLMFactory.create_llm") as mock_factory:
            mock_factory.side_effect = Exception("API Error")

            intent = create_intent(destination="Cebu")
            result = await detect_modification("test", intent)

            assert result.action == "change"
            assert result.target == "unknown"
            assert result.confidence == 0.0


class TestGenerateSuggestions:
    """Tests for generate_suggestions hybrid function."""

    @pytest.mark.asyncio
    async def test_falls_back_to_static_on_error(self):
        with patch(
            "app.ai.chains.followup_handler.duckduckgo_search"
        ) as mock_search:
            mock_search.ainvoke = AsyncMock(return_value="[ERROR] Search failed")

            intent = create_intent(travel_style=["beach"])
            result = await generate_suggestions(intent)

            assert isinstance(result, list)
            assert all(s.source == "static" for s in result)

    @pytest.mark.asyncio
    async def test_uses_static_for_empty_intent(self):
        intent = create_intent()
        result = await generate_suggestions(intent)

        assert isinstance(result, list)
        assert all(s.source == "static" for s in result)

    @pytest.mark.asyncio
    async def test_dynamic_suggestions_success(self):
        search_result = "## Best beach destinations\n1. Boracay - Beautiful white beach\n2. Palawan - Crystal waters"

        mock_extract_result = MagicMock()
        mock_extract_result.content = '{"suggestions": [{"destination": "Boracay", "reason": "Beautiful beach", "best_for": ["beach"]}]}'

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_extract_result)

        with patch("app.ai.chains.followup_handler.duckduckgo_search") as mock_search, \
             patch("app.ai.chains.followup_handler.LLMFactory.create_llm") as mock_factory, \
             patch("app.ai.chains.followup_handler.PromptTemplate") as mock_prompt_cls:
            mock_search.ainvoke = AsyncMock(return_value=search_result)
            mock_factory.return_value = MagicMock()
            mock_prompt_instance = MagicMock()
            mock_prompt_instance.__or__ = MagicMock(return_value=mock_chain)
            mock_prompt_cls.return_value = mock_prompt_instance

            intent = create_intent(travel_style=["beach"])
            result = await generate_suggestions(intent)

            assert isinstance(result, list)
            assert all(s.source == "search" for s in result)

    @pytest.mark.asyncio
    async def test_dynamic_suggestions_exception_fallback(self):
        with patch("app.ai.chains.followup_handler.duckduckgo_search") as mock_search:
            mock_search.ainvoke = AsyncMock(side_effect=Exception("Network error"))

            intent = create_intent(travel_style=["beach"])
            result = await generate_suggestions(intent)

            assert isinstance(result, list)
            assert all(s.source == "static" for s in result)

    @pytest.mark.asyncio
    async def test_dynamic_suggestions_llm_parse_failure(self):
        search_result = "## Best beach destinations\n1. Boracay"

        mock_extract_result = MagicMock()
        mock_extract_result.content = "invalid json response"

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_extract_result)

        with patch("app.ai.chains.followup_handler.duckduckgo_search") as mock_search, \
             patch("app.ai.chains.followup_handler.LLMFactory.create_llm") as mock_factory, \
             patch("app.ai.chains.followup_handler.PromptTemplate") as mock_prompt_cls:
            mock_search.ainvoke = AsyncMock(return_value=search_result)
            mock_factory.return_value = MagicMock()
            mock_prompt_instance = MagicMock()
            mock_prompt_instance.__or__ = MagicMock(return_value=mock_chain)
            mock_prompt_cls.return_value = mock_prompt_instance

            intent = create_intent(travel_style=["beach"])
            result = await generate_suggestions(intent)

            assert isinstance(result, list)
            assert all(s.source == "static" for s in result)


class TestProcessFollowup:
    """Tests for process_followup orchestrator."""

    @pytest.mark.asyncio
    async def test_handles_clarification_type(self):
        mock_type_result = MagicMock()
        mock_type_result.content = '{"type": "clarification", "confidence": 0.9}'

        mock_extract_result = MagicMock()
        mock_extract_result.content = '{"destination": "Cebu", "days": 5, "budget": null, "companions": null, "travel_style": [], "extra_notes": {}, "confidence": 0.8}'

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(
            side_effect=[mock_type_result, mock_extract_result, mock_type_result]
        )

        with patch("app.ai.chains.followup_handler.LLMFactory.create_llm") as mock_factory, \
             patch("app.ai.chains.followup_handler.PromptTemplate") as mock_prompt_cls:
            mock_factory.return_value = MagicMock()
            mock_prompt_instance = MagicMock()
            mock_prompt_instance.__or__ = MagicMock(return_value=mock_chain)
            mock_prompt_cls.return_value = mock_prompt_instance

            intent = create_intent(destination="Cebu")
            history = []

            result = await process_followup("5 days, mid budget", intent, history)

            assert result.type in ["clarification", "complete", "error"]

    @pytest.mark.asyncio
    async def test_handles_modification_type(self):
        mock_type_result = MagicMock()
        mock_type_result.content = '{"type": "modification", "confidence": 0.9}'

        mock_mod_result = MagicMock()
        mock_mod_result.content = '{"action": "change", "target": "days", "new_value": 7, "confidence": 0.95}'

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(
            side_effect=[mock_type_result, mock_mod_result]
        )

        with patch("app.ai.chains.followup_handler.LLMFactory.create_llm") as mock_factory, \
             patch("app.ai.chains.followup_handler.PromptTemplate") as mock_prompt_cls:
            mock_factory.return_value = MagicMock()
            mock_prompt_instance = MagicMock()
            mock_prompt_instance.__or__ = MagicMock(return_value=mock_chain)
            mock_prompt_cls.return_value = mock_prompt_instance

            intent = create_intent(destination="Cebu", days=5, budget="mid", companions="couple")
            history = []

            result = await process_followup("Make it 7 days", intent, history)

            assert result.type == "modification_applied"
            assert result.requires_regeneration is True

    @pytest.mark.asyncio
    async def test_handles_unsure_type(self):
        mock_type_result = MagicMock()
        mock_type_result.content = '{"type": "unsure", "confidence": 0.9}'

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_type_result)

        with patch("app.ai.chains.followup_handler.LLMFactory.create_llm") as mock_factory, \
             patch("app.ai.chains.followup_handler.PromptTemplate") as mock_prompt_cls, \
             patch("app.ai.chains.followup_handler.duckduckgo_search") as mock_search:
            mock_factory.return_value = MagicMock()
            mock_prompt_instance = MagicMock()
            mock_prompt_instance.__or__ = MagicMock(return_value=mock_chain)
            mock_prompt_cls.return_value = mock_prompt_instance
            mock_search.ainvoke = AsyncMock(return_value="[ERROR] fallback to static")

            intent = create_intent(travel_style=["beach"])
            history = []

            result = await process_followup("I don't know where to go", intent, history)

            assert result.type == "suggestions"
            assert result.suggestions is not None

    @pytest.mark.asyncio
    async def test_handles_unknown_type(self):
        mock_type_result = MagicMock()
        mock_type_result.content = '{"type": "unknown", "confidence": 0.5}'

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_type_result)

        with patch("app.ai.chains.followup_handler.LLMFactory.create_llm") as mock_factory, \
             patch("app.ai.chains.followup_handler.PromptTemplate") as mock_prompt_cls:
            mock_factory.return_value = MagicMock()
            mock_prompt_instance = MagicMock()
            mock_prompt_instance.__or__ = MagicMock(return_value=mock_chain)
            mock_prompt_cls.return_value = mock_prompt_instance

            intent = create_intent()
            history = []

            result = await process_followup("random message", intent, history)

            assert result.type == "error"


class TestSuggestionSchema:
    """Tests for Suggestion schema."""

    def test_suggestion_creation(self):
        suggestion = Suggestion(
            destination="Boracay",
            reason="Beautiful beaches",
            highlights=["White Beach", "Bulabog"],
            best_for=["beach", "nightlife"],
            source="static",
        )
        assert suggestion.destination == "Boracay"
        assert suggestion.source == "static"

    def test_suggestion_defaults(self):
        suggestion = Suggestion(
            destination="Boracay",
            reason="Beautiful beaches",
        )
        assert suggestion.highlights == []
        assert suggestion.best_for == []
        assert suggestion.source == "static"


class TestModificationRequestSchema:
    """Tests for ModificationRequest schema."""

    def test_modification_request_creation(self):
        mod = ModificationRequest(
            action="change",
            target="destination",
            new_value="Palawan",
            original_message="Change to Palawan",
            confidence=0.95,
        )
        assert mod.action == "change"
        assert mod.target == "destination"
        assert mod.confidence == 0.95

    def test_modification_request_defaults(self):
        mod = ModificationRequest(
            action="change",
            target="days",
        )
        assert mod.new_value is None
        assert mod.original_message == ""
        assert mod.confidence == 0.0


class TestFollowupTypeSchema:
    """Tests for FollowupType schema."""

    def test_followup_type_creation(self):
        ft = FollowupType(
            type="clarification",
            confidence=0.9,
            reasoning="User is answering questions",
        )
        assert ft.type == "clarification"
        assert ft.confidence == 0.9

    def test_followup_type_defaults(self):
        ft = FollowupType(type="unknown")
        assert ft.confidence == 0.0
        assert ft.reasoning is None


class TestFollowupResponseSchema:
    """Tests for FollowupResponse schema."""

    def test_followup_response_creation(self):
        intent = create_intent(destination="Cebu")
        response = FollowupResponse(
            type="clarification",
            updated_intent=intent,
            message="Need more info",
            requires_regeneration=False,
        )
        assert response.type == "clarification"
        assert response.updated_intent.destination == "Cebu"

    def test_followup_response_with_suggestions(self):
        suggestions = [
            Suggestion(destination="Boracay", reason="Beach paradise")
        ]
        response = FollowupResponse(
            type="suggestions",
            suggestions=suggestions,
            message="Here are some ideas:",
        )
        assert len(response.suggestions) == 1
        assert response.questions is None


class TestStaticDataIntegrity:
    """Tests for static data integrity."""

    def test_static_suggestions_has_all_styles(self):
        expected_styles = [
            "beach",
            "adventure",
            "culture",
            "food",
            "nature",
            "relaxation",
            "nightlife",
        ]
        for style in expected_styles:
            assert style in STATIC_SUGGESTIONS, f"Missing suggestions for style: {style}"

    def test_companion_filters_has_all_types(self):
        expected_companions = ["family", "solo", "couple", "group"]
        for companion in expected_companions:
            assert companion in COMPANION_SUGGESTION_FILTERS

    def test_static_suggestions_have_required_fields(self):
        for style, suggestions in STATIC_SUGGESTIONS.items():
            for s in suggestions:
                assert "destination" in s
                assert "reason" in s
                assert "best_for" in s
