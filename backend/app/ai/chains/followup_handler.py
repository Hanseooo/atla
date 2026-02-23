"""Follow-up handler chain for travel planning."""

import json
import re
import logging
from datetime import datetime
from typing import Optional, List

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

from app.ai.models.llms.gemini import LLMFactory
from app.ai.schemas.intent import TravelIntent
from app.ai.schemas.followup import (
    ModificationRequest,
    Suggestion,
    FollowupType,
    FollowupResponse,
)
from app.ai.prompts.followup_handler import (
    FOLLOWUP_TYPE_DETECTION_PROMPT,
    MODIFICATION_DETECTION_PROMPT,
    SUGGESTION_EXTRACTION_PROMPT,
    STATIC_SUGGESTIONS,
    COMPANION_SUGGESTION_FILTERS,
)
from app.ai.chains.intent_extraction import generate_clarification_questions, extract_intent
from app.ai.tools.duckduckgo_search import duckduckgo_search

logger = logging.getLogger(__name__)


async def detect_followup_type(
    message: str,
    current_intent: TravelIntent,
    conversation_history: List[dict],
) -> FollowupType:
    """
    Classify the type of follow-up message.

    Args:
        message: User's latest message
        current_intent: Current travel intent state
        conversation_history: Previous messages [{"role": "user/assistant", "content": str}]

    Returns:
        FollowupType with classification
    """
    try:
        llm = LLMFactory.create_llm(model_name="gemini-2.5-flash-lite", temp=0.1)

        parser = PydanticOutputParser(pydantic_object=FollowupType)

        prompt = PromptTemplate(
            template=FOLLOWUP_TYPE_DETECTION_PROMPT,
            input_variables=["message", "conversation_history", "current_intent"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        chain = prompt | llm

        history_str = _format_conversation_history(conversation_history)
        intent_str = current_intent.model_dump_json(indent=2)

        result = await chain.ainvoke({
            "message": message,
            "conversation_history": history_str,
            "current_intent": intent_str,
        })

        result_text = _extract_content(result)
        return await _parse_followup_type(result_text, parser)

    except Exception as e:
        logger.error(f"Followup type detection failed: {e}", exc_info=True)
        return FollowupType(type="unknown", confidence=0.0, reasoning=str(e))


async def detect_modification(
    message: str,
    current_intent: TravelIntent,
) -> ModificationRequest:
    """
    Extract modification details from user message.

    Args:
        message: User's modification request
        current_intent: Current travel intent

    Returns:
        ModificationRequest with parsed details
    """
    try:
        llm = LLMFactory.create_llm(model_name="gemini-2.5-flash-lite", temp=0.1)

        parser = PydanticOutputParser(pydantic_object=ModificationRequest)

        prompt = PromptTemplate(
            template=MODIFICATION_DETECTION_PROMPT,
            input_variables=["message", "current_intent"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        chain = prompt | llm

        result = await chain.ainvoke({
            "message": message,
            "current_intent": current_intent.model_dump_json(indent=2),
        })

        result_text = _extract_content(result)
        modification = await _parse_modification(result_text, parser)
        modification.original_message = message
        return modification

    except Exception as e:
        logger.error(f"Modification detection failed: {e}", exc_info=True)
        return ModificationRequest(
            action="change",
            target="unknown",
            original_message=message,
            confidence=0.0,
        )


def apply_modification(
    intent: TravelIntent,
    modification: ModificationRequest,
) -> TravelIntent:
    """
    Apply a modification to the travel intent.

    Args:
        intent: Current travel intent
        modification: Modification to apply

    Returns:
        Updated TravelIntent
    """
    update_data = intent.model_dump()

    target = modification.target
    action = modification.action
    new_value = modification.new_value

    if target == "destination":
        if new_value:
            update_data["destination"] = str(new_value)

    elif target == "days":
        current_days = update_data.get("days")
        validated_days = None
        if action == "change":
            validated_days = _validate_days(new_value)
        elif action == "extend" and current_days is not None:
            validated_days = _validate_days(current_days + (new_value or 0))
        elif action == "shorten" and current_days is not None:
            validated_days = _validate_days(current_days - (new_value or 0))
        if validated_days is not None:
            update_data["days"] = validated_days

    elif target == "budget":
        validated_budget = _validate_budget(new_value)
        if validated_budget is not None:
            update_data["budget"] = validated_budget

    elif target == "companions":
        validated_companions = _validate_companions(new_value)
        if validated_companions is not None:
            update_data["companions"] = validated_companions

    elif target == "travel_style":
        current_styles = update_data.get("travel_style", [])
        validated_styles = _validate_travel_style(new_value)
        
        if action == "add":
            if validated_styles:
                update_data["travel_style"] = list(set(current_styles + validated_styles))
        elif action == "remove":
            styles_to_remove = validated_styles if validated_styles else (
                [new_value] if isinstance(new_value, str) else (
                    new_value if isinstance(new_value, list) else []
                )
            )
            update_data["travel_style"] = [
                s for s in current_styles if s not in styles_to_remove
            ]
        elif action == "change":
            if validated_styles:
                update_data["travel_style"] = validated_styles

    updated_intent = TravelIntent(**update_data)
    updated_intent.missing_info = updated_intent.get_missing_fields()

    return updated_intent


async def generate_suggestions(
    partial_intent: TravelIntent,
    max_suggestions: int = 5,
) -> List[Suggestion]:
    """
    Generate destination suggestions using hybrid approach.

    Priority:
    1. Use duckduckgo_search for dynamic suggestions if we have partial info
    2. Fall back to curated static suggestions

    Args:
        partial_intent: Partial travel intent (may have travel_style, companions)
        max_suggestions: Maximum number of suggestions to return

    Returns:
        List of Suggestion objects
    """
    if partial_intent.travel_style or partial_intent.companions:
        dynamic_suggestions = await _generate_dynamic_suggestions(
            partial_intent, max_suggestions
        )
        if dynamic_suggestions:
            return dynamic_suggestions

    return _generate_static_suggestions(partial_intent, max_suggestions)


async def _generate_dynamic_suggestions(
    partial_intent: TravelIntent,
    max_suggestions: int,
) -> Optional[List[Suggestion]]:
    """Generate suggestions using search tools + LLM extraction."""
    try:
        query = _build_suggestion_query(partial_intent)

        search_results = await duckduckgo_search.ainvoke({
            "query": query,
            "region": "ph-ph",
            "max_results": 8,
        })

        if "[ERROR]" in search_results:
            logger.warning(f"Search tool returned error: {search_results}")
            return None

        suggestions = await _extract_suggestions_from_search(
            search_results, partial_intent, max_suggestions
        )

        for s in suggestions:
            s.source = "search"

        return suggestions

    except Exception as e:
        logger.warning(f"Dynamic suggestions failed: {e}")
        return None


def _generate_static_suggestions(
    partial_intent: TravelIntent,
    max_suggestions: int,
) -> List[Suggestion]:
    """Generate suggestions from curated static data."""
    suggestions = []
    seen_destinations = set()

    styles = partial_intent.travel_style or []
    companions = partial_intent.companions

    companion_filter = COMPANION_SUGGESTION_FILTERS.get(companions, {}) if companions else {}
    avoid_styles = companion_filter.get("avoid", [])
    prioritize_styles = companion_filter.get("prioritize", [])

    if prioritize_styles:
        styles = prioritize_styles + [s for s in styles if s not in prioritize_styles]

    for style in styles:
        if style in STATIC_SUGGESTIONS:
            for suggestion_data in STATIC_SUGGESTIONS[style]:
                dest = suggestion_data["destination"]

                if dest in seen_destinations:
                    continue

                dest_styles = suggestion_data.get("best_for", [])
                if any(s in avoid_styles for s in dest_styles):
                    continue

                seen_destinations.add(dest)

                suggestions.append(
                    Suggestion(
                        destination=dest,
                        reason=suggestion_data["reason"],
                        best_for=dest_styles,
                        source="static",
                    )
                )

                if len(suggestions) >= max_suggestions:
                    break

        if len(suggestions) >= max_suggestions:
            break

    if not suggestions:
        return _get_popular_destinations(max_suggestions)

    return suggestions


def _get_popular_destinations(max_suggestions: int) -> List[Suggestion]:
    """Return popular destinations as fallback when no style matches."""
    popular = [
        Suggestion(
            destination="Boracay",
            reason="Most popular beach destination with white sand and vibrant nightlife.",
            best_for=["beach", "nightlife", "relaxation"],
            source="static",
        ),
        Suggestion(
            destination="Palawan",
            reason="Pristine nature, underground river, and stunning lagoons.",
            best_for=["nature", "beach", "adventure"],
            source="static",
        ),
        Suggestion(
            destination="Cebu",
            reason="Diverse activities from waterfalls to whale shark watching.",
            best_for=["adventure", "nature", "culture"],
            source="static",
        ),
        Suggestion(
            destination="Siargao",
            reason="Surfing capital with laid-back island vibe.",
            best_for=["adventure", "beach", "relaxation"],
            source="static",
        ),
        Suggestion(
            destination="Bohol",
            reason="Chocolate Hills, tarsiers, and heritage sites.",
            best_for=["nature", "culture", "beach"],
            source="static",
        ),
    ]
    return popular[:max_suggestions]


async def process_followup(
    message: str,
    current_intent: TravelIntent,
    conversation_history: List[dict],
) -> FollowupResponse:
    """
    Main orchestrator for handling follow-up messages.

    Args:
        message: User's latest message
        current_intent: Current travel intent state
        conversation_history: Previous messages

    Returns:
        FollowupResponse with appropriate action
    """
    followup_type = await detect_followup_type(
        message, current_intent, conversation_history
    )

    if followup_type.type == "clarification":
        return await _handle_clarification(message, current_intent)

    elif followup_type.type == "modification":
        return await _handle_modification(message, current_intent)

    elif followup_type.type == "new_intent":
        return await _handle_new_intent(message, current_intent)

    elif followup_type.type == "unsure":
        return await _handle_unsure(current_intent)

    else:
        return FollowupResponse(
            type="error",
            message="I'm not sure what you mean. Could you rephrase that?",
            updated_intent=current_intent,
        )


async def _handle_clarification(
    message: str,
    current_intent: TravelIntent,
) -> FollowupResponse:
    """Handle clarification response - merge new info into intent."""
    new_intent = await extract_intent(message)

    merged_data = current_intent.model_dump()
    for field in [
        "destination",
        "days",
        "budget",
        "companions",
        "travel_style",
        "time_of_year",
    ]:
        new_value = getattr(new_intent, field, None)
        if new_value:
            if field == "travel_style" and isinstance(new_value, list):
                existing = merged_data.get(field, [])
                merged_data[field] = list(set(existing + new_value))
            else:
                merged_data[field] = new_value

    for note_field in [
        "dietary_restrictions",
        "accessibility_needs",
        "must_visit",
        "avoid",
        "interests",
    ]:
        new_value = getattr(new_intent.extra_notes, note_field, None)
        if new_value:
            if isinstance(new_value, list):
                existing = merged_data["extra_notes"].get(note_field, [])
                merged_data["extra_notes"][note_field] = list(set(existing + new_value))
            else:
                merged_data["extra_notes"][note_field] = new_value

    updated_intent = TravelIntent(**merged_data)
    updated_intent.missing_info = updated_intent.get_missing_fields()

    if updated_intent.is_complete():
        return FollowupResponse(
            type="complete",
            updated_intent=updated_intent,
            message="I have all the info I need! Generating your itinerary...",
            requires_regeneration=True,
        )

    clarification = generate_clarification_questions(updated_intent)

    return FollowupResponse(
        type="clarification",
        updated_intent=updated_intent,
        questions=clarification.questions,
        message=clarification.message,
        requires_regeneration=False,
    )


async def _handle_modification(
    message: str,
    current_intent: TravelIntent,
) -> FollowupResponse:
    """Handle modification request."""
    modification = await detect_modification(message, current_intent)

    updated_intent = apply_modification(current_intent, modification)

    target_display = modification.target.replace("_", " ").title()
    action_messages = {
        "change": f"Updated your {target_display}.",
        "add": f"Added to your {target_display}.",
        "remove": f"Removed from your {target_display}.",
        "extend": "Extended your trip.",
        "shorten": "Shortened your trip.",
    }

    current = current_intent.model_dump()
    updated = updated_intent.model_dump()

    for field in ["travel_style"]:
        if current.get(field):
            current[field] = sorted(current[field])
        if updated.get(field):
            updated[field] = sorted(updated[field])

    intent_changed = current != updated

    base_message = action_messages.get(
        modification.action, f"Modified your {target_display}."
    )

    if intent_changed:
        response_message = base_message + " Regenerating your itinerary..."
        requires_regeneration = True
    else:
        response_message = base_message + " I couldn't apply that change to your trip."
        requires_regeneration = False

    return FollowupResponse(
        type="modification_applied",
        updated_intent=updated_intent,
        message=response_message,
        requires_regeneration=requires_regeneration,
    )


async def _handle_new_intent(
    message: str,
    current_intent: TravelIntent,
) -> FollowupResponse:
    """Handle completely new intent - start fresh extraction."""
    new_intent = await extract_intent(message)

    if new_intent.is_complete():
        return FollowupResponse(
            type="complete",
            updated_intent=new_intent,
            message="Got it! Let me plan a new trip for you...",
            requires_regeneration=True,
        )

    clarification = generate_clarification_questions(new_intent)

    return FollowupResponse(
        type="clarification",
        updated_intent=new_intent,
        questions=clarification.questions,
        message="Starting fresh! " + clarification.message,
        requires_regeneration=False,
    )


async def _handle_unsure(current_intent: TravelIntent) -> FollowupResponse:
    """Handle unsure user - provide suggestions."""
    suggestions = await generate_suggestions(current_intent)

    return FollowupResponse(
        type="suggestions",
        updated_intent=current_intent,
        suggestions=suggestions,
        message="No worries! Here are some popular destinations that might interest you:",
        requires_regeneration=False,
    )


def _format_conversation_history(history: List[dict]) -> str:
    """Format conversation history for prompt."""
    if not history:
        return "No previous conversation."

    lines = []
    for msg in history[-10:]:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        lines.append(f"{role.upper()}: {content}")

    return "\n".join(lines)


def _extract_content(result) -> str:
    """Extract string content from LLM result."""
    if hasattr(result, "content"):
        content = result.content
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            return "".join(str(item) for item in content)
    return str(result)


async def _parse_followup_type(
    text: str, parser: PydanticOutputParser
) -> FollowupType:
    """Parse LLM output into FollowupType with fallback."""
    try:
        return parser.parse(text)
    except Exception:
        pass

    try:
        json_match = re.search(r"\{[\s\S]*\}", text)
        if json_match:
            data = json.loads(json_match.group())
            return FollowupType(**data)
    except Exception:
        pass

    return FollowupType(type="unknown", confidence=0.0)


async def _parse_modification(
    text: str, parser: PydanticOutputParser
) -> ModificationRequest:
    """Parse LLM output into ModificationRequest with fallback."""
    try:
        return parser.parse(text)
    except Exception:
        pass

    try:
        json_match = re.search(r"\{[\s\S]*\}", text)
        if json_match:
            data = json.loads(json_match.group())
            return ModificationRequest(**data)
    except Exception:
        pass

    return ModificationRequest(
        action="change", target="unknown", original_message="", confidence=0.0
    )


async def _extract_suggestions_from_search(
    search_results: str,
    partial_intent: TravelIntent,
    max_suggestions: int,
) -> List[Suggestion]:
    """Use LLM to extract structured suggestions from search results."""
    try:
        llm = LLMFactory.create_llm(model_name="gemini-2.5-flash-lite", temp=0.3)

        prompt = PromptTemplate(
            template=SUGGESTION_EXTRACTION_PROMPT,
            input_variables=["companions", "travel_style", "budget", "search_results"],
        )

        chain = prompt | llm

        result = await chain.ainvoke({
            "companions": partial_intent.companions or "not specified",
            "travel_style": (
                ", ".join(partial_intent.travel_style)
                if partial_intent.travel_style
                else "not specified"
            ),
            "budget": partial_intent.budget or "not specified",
            "search_results": search_results,
        })

        result_text = _extract_content(result)

        json_match = re.search(r"\{[\s\S]*\}", result_text)
        if json_match:
            data = json.loads(json_match.group())
            suggestions_data = data.get("suggestions", [])
            return [Suggestion(**s) for s in suggestions_data[:max_suggestions]]

    except Exception as e:
        logger.warning(f"Failed to extract suggestions from search: {e}")

    return []


def _build_suggestion_query(partial_intent: TravelIntent) -> str:
    """Build search query for destination suggestions."""
    parts = ["best"]

    if partial_intent.companions:
        parts.append(partial_intent.companions)

    if partial_intent.travel_style:
        parts.append(" ".join(partial_intent.travel_style[:2]))

    parts.append(f"destinations Philippines {datetime.now().year}")

    return " ".join(parts)


def _validate_days(value) -> Optional[int]:
    """Validate and constrain days value to 1-30 range."""
    if value is None:
        return None
    try:
        days = int(value)
        return max(1, min(30, days))
    except (ValueError, TypeError):
        return None


def _validate_budget(value) -> Optional[str]:
    """Validate budget value."""
    if value is None:
        return None
    if isinstance(value, str) and value in ["low", "mid", "luxury"]:
        return value
    return None


def _validate_companions(value) -> Optional[str]:
    """Validate companions value."""
    if value is None:
        return None
    if isinstance(value, str) and value in ["solo", "couple", "family", "group"]:
        return value
    return None


VALID_TRAVEL_STYLES = {"adventure", "relaxation", "culture", "food", "beach", "nature", "nightlife"}


def _validate_travel_style(value) -> List[str]:
    """Validate and filter travel_style values against valid options."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value in VALID_TRAVEL_STYLES else []
    if isinstance(value, list):
        return [s for s in value if isinstance(s, str) and s in VALID_TRAVEL_STYLES]
    return []
