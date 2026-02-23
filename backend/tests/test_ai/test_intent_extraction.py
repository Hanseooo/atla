"""Unit tests for intent extraction chain."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import json

from app.ai.schemas.intent import (
    TravelIntent,
    ExtraNotes,
    ClarificationQuestion,
    ClarificationResponse,
    QuestionOption,
    IntentExtractionError,
)
from app.ai.chains.intent_extraction import (
    extract_intent,
    generate_clarification_questions,
    update_intent_from_answers,
    _parse_intent,
)
from app.ai.prompts.intent_extraction import (
    QUESTION_TEMPLATES,
    PROGRESS_MESSAGES,
)


def create_intent(
    destination: str = None,
    days: int = None,
    budget: str = None,
    companions: str = None,
    travel_style: list = None,
    time_of_year: str = None,
    confidence: float = 0.0,
) -> TravelIntent:
    """Helper to create TravelIntent with defaults."""
    return TravelIntent(
        destination=destination,
        days=days,
        budget=budget,
        companions=companions,
        travel_style=travel_style or [],
        time_of_year=time_of_year,
        confidence=confidence,
    )


class TestTravelIntentSchema:
    """Tests for TravelIntent schema methods."""

    def test_is_complete_all_fields(self):
        intent = create_intent(
            destination="Cebu",
            days=5,
            budget="mid",
            companions="couple",
        )
        assert intent.is_complete() is True

    def test_is_complete_missing_destination(self):
        intent = create_intent(days=5, budget="mid", companions="couple")
        assert intent.is_complete() is False

    def test_is_complete_missing_days(self):
        intent = create_intent(destination="Cebu", budget="mid", companions="couple")
        assert intent.is_complete() is False

    def test_is_complete_missing_budget(self):
        intent = create_intent(destination="Cebu", days=5, companions="couple")
        assert intent.is_complete() is False

    def test_is_complete_missing_companions(self):
        intent = create_intent(destination="Cebu", days=5, budget="mid")
        assert intent.is_complete() is False

    def test_is_complete_all_missing(self):
        intent = create_intent()
        assert intent.is_complete() is False

    def test_get_missing_fields_none_missing(self):
        intent = create_intent(
            destination="Cebu",
            days=5,
            budget="mid",
            companions="couple",
        )
        assert intent.get_missing_fields() == []

    def test_get_missing_fields_one_missing(self):
        intent = create_intent(destination="Cebu", days=5, budget="mid")
        assert intent.get_missing_fields() == ["companions"]

    def test_get_missing_fields_all_missing(self):
        intent = create_intent()
        missing = intent.get_missing_fields()
        assert "destination" in missing
        assert "days" in missing
        assert "budget" in missing
        assert "companions" in missing
        assert len(missing) == 4

    def test_days_validation_within_range(self):
        intent = TravelIntent(destination="Cebu", days=15)
        assert intent.days == 15

    def test_days_validation_at_minimum(self):
        intent = TravelIntent(destination="Cebu", days=1)
        assert intent.days == 1

    def test_days_validation_at_maximum(self):
        intent = TravelIntent(destination="Cebu", days=30)
        assert intent.days == 30

    def test_travel_style_default_empty(self):
        intent = create_intent()
        assert intent.travel_style == []

    def test_travel_style_with_values(self):
        intent = create_intent(travel_style=["beach", "adventure", "food"])
        assert intent.travel_style == ["beach", "adventure", "food"]

    def test_extra_notes_default(self):
        intent = create_intent()
        assert isinstance(intent.extra_notes, ExtraNotes)
        assert intent.extra_notes.preferred_pace == "moderate"

    def test_confidence_default_zero(self):
        intent = create_intent()
        assert intent.confidence == 0.0


class TestExtraNotesSchema:
    """Tests for ExtraNotes schema."""

    def test_default_values(self):
        notes = ExtraNotes()
        assert notes.dietary_restrictions is None
        assert notes.accessibility_needs is None
        assert notes.must_visit == []
        assert notes.avoid == []
        assert notes.interests == []
        assert notes.special_occasion is None
        assert notes.preferred_pace == "moderate"
        assert notes.accommodation_type is None
        assert notes.budget_flexibility is None
        assert notes.transport_preference is None

    def test_with_values(self):
        notes = ExtraNotes(
            dietary_restrictions="vegetarian",
            must_visit=["Chocolate Hills", "Tarsier Sanctuary"],
            interests=["photography"],
            preferred_pace="relaxed",
        )
        assert notes.dietary_restrictions == "vegetarian"
        assert len(notes.must_visit) == 2
        assert notes.preferred_pace == "relaxed"


class TestClarificationQuestionSchema:
    """Tests for ClarificationQuestion schema."""

    def test_single_choice_question(self):
        question = ClarificationQuestion(
            id="q_budget",
            field="budget",
            type="single_choice",
            question="What's your budget?",
            options=[
                QuestionOption(id="low", label="Budget-friendly"),
                QuestionOption(id="mid", label="Moderate"),
            ],
        )
        assert question.id == "q_budget"
        assert question.type == "single_choice"
        assert len(question.options) == 2
        assert question.required is True

    def test_text_question(self):
        question = ClarificationQuestion(
            id="q_destination",
            field="destination",
            type="text",
            question="Where do you want to go?",
            placeholder="e.g., Cebu, Boracay",
        )
        assert question.type == "text"
        assert question.placeholder == "e.g., Cebu, Boracay"
        assert question.options is None


class TestClarificationResponseSchema:
    """Tests for ClarificationResponse schema."""

    def test_response_creation(self):
        intent = create_intent(destination="Cebu")
        response = ClarificationResponse(
            questions=[],
            current_intent=intent,
            progress={"completed": 1, "total": 4, "percentage": 25},
            message="Great start!",
        )
        assert response.type == "clarification"
        assert response.session_id is None
        assert response.current_intent.destination == "Cebu"


class TestGenerateClarificationQuestions:
    """Tests for generate_clarification_questions function."""

    def test_all_fields_missing(self):
        intent = create_intent()
        response = generate_clarification_questions(intent)

        assert response.type == "clarification"
        assert len(response.questions) == 3
        assert response.progress["completed"] == 0
        assert response.progress["total"] == 4
        assert response.progress["percentage"] == 0

    def test_one_field_missing(self):
        intent = create_intent(destination="Cebu", days=5, budget="mid")
        response = generate_clarification_questions(intent)

        assert len(response.questions) == 1
        assert response.questions[0].field == "companions"
        assert response.progress["completed"] == 3
        assert response.progress["percentage"] == 75

    def test_two_fields_missing(self):
        intent = create_intent(destination="Cebu", days=5)
        response = generate_clarification_questions(intent)

        assert len(response.questions) == 2
        assert response.progress["completed"] == 2
        assert response.progress["percentage"] == 50

    def test_no_fields_missing(self):
        intent = create_intent(
            destination="Cebu", days=5, budget="mid", companions="couple"
        )
        response = generate_clarification_questions(intent)

        assert len(response.questions) == 0
        assert response.progress["completed"] == 4
        assert response.progress["percentage"] == 100

    def test_max_questions_limit(self):
        intent = create_intent()
        response = generate_clarification_questions(intent, max_questions=2)

        assert len(response.questions) == 2

    def test_question_order_by_priority(self):
        intent = create_intent()
        response = generate_clarification_questions(intent, max_questions=4)

        fields = [q.field for q in response.questions]
        assert fields[0] == "destination"
        assert fields[1] == "days"
        assert fields[2] == "budget"
        assert fields[3] == "companions"

    def test_question_has_correct_type(self):
        intent = create_intent()
        response = generate_clarification_questions(intent)

        for question in response.questions:
            template = QUESTION_TEMPLATES.get(question.field)
            if template:
                assert question.type == template["type"]

    def test_question_has_options_when_applicable(self):
        intent = create_intent()
        response = generate_clarification_questions(intent)

        for question in response.questions:
            template = QUESTION_TEMPLATES.get(question.field)
            if template and "options" in template:
                assert question.options is not None
                assert len(question.options) > 0

    def test_progress_message_from_template(self):
        intent = create_intent()
        response = generate_clarification_questions(intent)

        assert response.message == PROGRESS_MESSAGES[0]


class TestUpdateIntentFromAnswers:
    """Tests for update_intent_from_answers function."""

    def test_update_destination(self):
        intent = create_intent(days=5, budget="mid", companions="couple")
        answers = {"q_destination": "Palawan"}

        updated = update_intent_from_answers(intent, answers)

        assert updated.destination == "Palawan"
        assert updated.days == 5

    def test_update_days(self):
        intent = create_intent(destination="Cebu", budget="mid", companions="couple")
        answers = {"q_days": "7"}

        updated = update_intent_from_answers(intent, answers)

        assert updated.days == 7

    def test_update_days_string_to_int(self):
        intent = create_intent(destination="Cebu")
        answers = {"q_days": "5"}

        updated = update_intent_from_answers(intent, answers)

        assert updated.days == 5
        assert isinstance(updated.days, int)

    def test_update_days_invalid_value_ignored(self):
        intent = create_intent(destination="Cebu", days=3)
        answers = {"q_days": "invalid"}

        updated = update_intent_from_answers(intent, answers)

        assert updated.days == 3

    def test_update_budget(self):
        intent = create_intent(destination="Cebu", days=5, companions="couple")
        answers = {"q_budget": "luxury"}

        updated = update_intent_from_answers(intent, answers)

        assert updated.budget == "luxury"

    def test_update_companions(self):
        intent = create_intent(destination="Cebu", days=5, budget="mid")
        answers = {"q_companions": "family"}

        updated = update_intent_from_answers(intent, answers)

        assert updated.companions == "family"

    def test_update_travel_style_single(self):
        intent = create_intent(destination="Cebu")
        answers = {"q_travel_style": "beach"}

        updated = update_intent_from_answers(intent, answers)

        assert updated.travel_style == ["beach"]

    def test_update_travel_style_list(self):
        intent = create_intent(destination="Cebu")
        answers = {"q_travel_style": ["beach", "adventure", "food"]}

        updated = update_intent_from_answers(intent, answers)

        assert updated.travel_style == ["beach", "adventure", "food"]

    def test_update_time_of_year(self):
        intent = create_intent(destination="Cebu")
        answers = {"q_time_of_year": "December 2024"}

        updated = update_intent_from_answers(intent, answers)

        assert updated.time_of_year == "December 2024"

    def test_update_multiple_fields(self):
        intent = create_intent()
        answers = {
            "q_destination": "Boracay",
            "q_days": "5",
            "q_budget": "mid",
            "q_companions": "couple",
        }

        updated = update_intent_from_answers(intent, answers)

        assert updated.destination == "Boracay"
        assert updated.days == 5
        assert updated.budget == "mid"
        assert updated.companions == "couple"
        assert updated.is_complete()

    def test_missing_info_recalculated(self):
        intent = create_intent()
        answers = {"q_destination": "Cebu"}

        updated = update_intent_from_answers(intent, answers)

        assert "destination" not in updated.missing_info
        assert "days" in updated.missing_info

    def test_preserves_existing_values(self):
        intent = create_intent(
            destination="Cebu",
            days=5,
            budget="mid",
            companions="couple",
            travel_style=["beach"],
        )
        answers = {"q_budget": "luxury"}

        updated = update_intent_from_answers(intent, answers)

        assert updated.destination == "Cebu"
        assert updated.days == 5
        assert updated.budget == "luxury"
        assert updated.companions == "couple"
        assert updated.travel_style == ["beach"]


class TestExtractIntent:
    """Tests for extract_intent function."""

    @pytest.mark.asyncio
    async def test_extract_complete_intent(self):
        mock_result = MagicMock()
        mock_result.content = json.dumps({
            "destination": "Cebu",
            "days": 5,
            "budget": "mid",
            "companions": "couple",
            "travel_style": ["beach", "food"],
            "extra_notes": {},
            "confidence": 0.9,
        })

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_result)

        with patch("app.ai.chains.intent_extraction.LLMFactory.create_llm") as mock_factory, \
             patch("app.ai.chains.intent_extraction.PromptTemplate") as mock_prompt_cls:
            mock_factory.return_value = MagicMock()
            mock_prompt_instance = MagicMock()
            mock_prompt_instance.__or__ = MagicMock(return_value=mock_chain)
            mock_prompt_cls.return_value = mock_prompt_instance

            result = await extract_intent("I want to go to Cebu for 5 days with my partner, mid budget")

            assert result.destination == "Cebu"
            assert result.days == 5
            assert result.budget == "mid"
            assert result.companions == "couple"
            assert result.confidence == 0.9

    @pytest.mark.asyncio
    async def test_extract_partial_intent(self):
        mock_result = MagicMock()
        mock_result.content = json.dumps({
            "destination": "Palawan",
            "days": None,
            "budget": None,
            "companions": None,
            "travel_style": [],
            "extra_notes": {},
            "confidence": 0.5,
        })

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_result)

        with patch("app.ai.chains.intent_extraction.LLMFactory.create_llm") as mock_factory, \
             patch("app.ai.chains.intent_extraction.PromptTemplate") as mock_prompt_cls:
            mock_factory.return_value = MagicMock()
            mock_prompt_instance = MagicMock()
            mock_prompt_instance.__or__ = MagicMock(return_value=mock_chain)
            mock_prompt_cls.return_value = mock_prompt_instance

            result = await extract_intent("I want to visit Palawan")

            assert result.destination == "Palawan"
            assert result.days is None
            assert not result.is_complete()

    @pytest.mark.asyncio
    async def test_extract_with_user_context(self):
        mock_result = MagicMock()
        mock_result.content = json.dumps({
            "destination": "Cebu",
            "days": 3,
            "budget": "low",
            "companions": "solo",
            "travel_style": [],
            "extra_notes": {},
            "confidence": 0.8,
        })

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_result)

        with patch("app.ai.chains.intent_extraction.LLMFactory.create_llm") as mock_factory, \
             patch("app.ai.chains.intent_extraction.PromptTemplate") as mock_prompt_cls:
            mock_factory.return_value = MagicMock()
            mock_prompt_instance = MagicMock()
            mock_prompt_instance.__or__ = MagicMock(return_value=mock_chain)
            mock_prompt_cls.return_value = mock_prompt_instance

            user_context = {"preferred_destination": "Cebu", "past_trips": 2}
            result = await extract_intent("Quick trip", user_context)

            assert result.destination == "Cebu"

    @pytest.mark.asyncio
    async def test_extract_handles_exception(self):
        with patch("app.ai.chains.intent_extraction.LLMFactory.create_llm") as mock_factory:
            mock_factory.side_effect = Exception("API Error")

            result = await extract_intent("test message")

            assert result.confidence == 0.0
            assert len(result.missing_info) == 4
            assert result.destination is None

    @pytest.mark.asyncio
    async def test_extract_handles_list_content(self):
        mock_result = MagicMock()
        mock_result.content = [
            json.dumps({
                "destination": "Boracay",
                "days": 7,
                "budget": "luxury",
                "companions": "group",
                "travel_style": ["beach", "nightlife"],
                "extra_notes": {},
                "confidence": 0.85,
            })
        ]

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_result)

        with patch("app.ai.chains.intent_extraction.LLMFactory.create_llm") as mock_factory, \
             patch("app.ai.chains.intent_extraction.PromptTemplate") as mock_prompt_cls:
            mock_factory.return_value = MagicMock()
            mock_prompt_instance = MagicMock()
            mock_prompt_instance.__or__ = MagicMock(return_value=mock_chain)
            mock_prompt_cls.return_value = mock_prompt_instance

            result = await extract_intent("Group trip to Boracay")

            assert result.destination == "Boracay"
            assert result.days == 7

    @pytest.mark.asyncio
    async def test_extract_with_extra_notes(self):
        mock_result = MagicMock()
        mock_result.content = json.dumps({
            "destination": "Cebu",
            "days": 5,
            "budget": "mid",
            "companions": "couple",
            "travel_style": ["food"],
            "extra_notes": {
                "dietary_restrictions": "vegetarian",
                "must_visit": ["Kawasan Falls"],
                "interests": ["photography"],
            },
            "confidence": 0.9,
        })

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_result)

        with patch("app.ai.chains.intent_extraction.LLMFactory.create_llm") as mock_factory, \
             patch("app.ai.chains.intent_extraction.PromptTemplate") as mock_prompt_cls:
            mock_factory.return_value = MagicMock()
            mock_prompt_instance = MagicMock()
            mock_prompt_instance.__or__ = MagicMock(return_value=mock_chain)
            mock_prompt_cls.return_value = mock_prompt_instance

            result = await extract_intent("Cebu trip, vegetarian, want to see Kawasan Falls")

            assert result.extra_notes.dietary_restrictions == "vegetarian"
            assert "Kawasan Falls" in result.extra_notes.must_visit
            assert "photography" in result.extra_notes.interests


class TestParseIntent:
    """Tests for _parse_intent internal function."""

    @pytest.mark.asyncio
    async def test_parse_valid_json(self):
        from langchain_core.output_parsers import PydanticOutputParser

        parser = PydanticOutputParser(pydantic_object=TravelIntent)

        json_text = json.dumps({
            "destination": "Cebu",
            "days": 5,
            "budget": "mid",
            "companions": "couple",
            "travel_style": [],
            "extra_notes": {},
            "confidence": 0.9,
        })

        result = await _parse_intent(json_text, parser)

        assert result.destination == "Cebu"
        assert result.days == 5

    @pytest.mark.asyncio
    async def test_parse_json_with_extra_text(self):
        from langchain_core.output_parsers import PydanticOutputParser

        parser = PydanticOutputParser(pydantic_object=TravelIntent)

        text = 'Here is the result: {"destination": "Palawan", "days": 7, "budget": "luxury", "companions": "family", "travel_style": [], "extra_notes": {}, "confidence": 0.8}'

        result = await _parse_intent(text, parser)

        assert result.destination == "Palawan"
        assert result.days == 7

    @pytest.mark.asyncio
    async def test_parse_missing_extra_notes_defaults(self):
        from langchain_core.output_parsers import PydanticOutputParser

        parser = PydanticOutputParser(pydantic_object=TravelIntent)

        text = '{"destination": "Cebu", "days": 3, "budget": "low", "companions": "solo"}'

        result = await _parse_intent(text, parser)

        assert result.extra_notes is not None
        assert result.travel_style == []

    @pytest.mark.asyncio
    async def test_parse_invalid_json_returns_empty(self):
        from langchain_core.output_parsers import PydanticOutputParser

        parser = PydanticOutputParser(pydantic_object=TravelIntent)

        result = await _parse_intent("not valid json at all", parser)

        assert result.confidence == 0.0
        assert len(result.missing_info) == 4

    @pytest.mark.asyncio
    async def test_parse_empty_string_returns_empty(self):
        from langchain_core.output_parsers import PydanticOutputParser

        parser = PydanticOutputParser(pydantic_object=TravelIntent)

        result = await _parse_intent("", parser)

        assert result.confidence == 0.0


class TestQuestionTemplatesData:
    """Tests for QUESTION_TEMPLATES data integrity."""

    def test_all_required_fields_have_templates(self):
        required_fields = ["destination", "days", "budget", "companions"]
        for field in required_fields:
            assert field in QUESTION_TEMPLATES, f"Missing template for {field}"

    def test_all_templates_have_required_keys(self):
        required_keys = ["question", "type"]
        for field, template in QUESTION_TEMPLATES.items():
            for key in required_keys:
                assert key in template, f"Template for {field} missing {key}"

    def test_choice_templates_have_options(self):
        choice_types = ["single_choice", "multiple_choice"]
        for field, template in QUESTION_TEMPLATES.items():
            if template["type"] in choice_types:
                assert "options" in template, f"Choice template {field} missing options"
                assert len(template["options"]) > 0, f"Choice template {field} has empty options"

    def test_text_templates_have_placeholder(self):
        for field, template in QUESTION_TEMPLATES.items():
            if template["type"] == "text":
                assert "placeholder" in template, f"Text template {field} missing placeholder"

    def test_options_have_required_fields(self):
        for field, template in QUESTION_TEMPLATES.items():
            if "options" in template:
                for option in template["options"]:
                    assert "id" in option, f"Option in {field} missing id"
                    assert "label" in option, f"Option in {field} missing label"


class TestProgressMessagesData:
    """Tests for PROGRESS_MESSAGES data integrity."""

    def test_has_messages_for_all_progress_levels(self):
        for i in range(4):
            assert i in PROGRESS_MESSAGES, f"Missing progress message for level {i}"

    def test_messages_are_strings(self):
        for level, message in PROGRESS_MESSAGES.items():
            assert isinstance(message, str), f"Progress message for {level} is not a string"
