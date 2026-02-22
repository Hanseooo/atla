"""Intent extraction chain for travel planning."""

import json
import re
import logging
from typing import Optional

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

from app.ai.models.llms.gemini import LLMFactory
from app.ai.schemas.intent import (
    TravelIntent,
    ExtraNotes,
    ClarificationQuestion,
    ClarificationResponse,
    QuestionOption,
    IntentExtractionError,
)
from app.ai.prompts.intent_extraction import (
    INTENT_EXTRACTION_PROMPT,
    QUESTION_TEMPLATES,
    PROGRESS_MESSAGES,
)

logger = logging.getLogger(__name__)

async def extract_intent(
    message: str,
    user_context: Optional[dict] = None,
) -> TravelIntent:
    """
    Extract travel intent from user message.

    Args:
        message: User's natural language message
        user_context: Optional user preferences from database

    Returns:
        TravelIntent object with extracted data.
        Returns empty intent with confidence=0.0 on failure.
    """
    try:
        llm = LLMFactory.create_llm(
            model_name="gemini-2.5-flash-lite",
            temp=0.1,
        )

        parser = PydanticOutputParser(pydantic_object=TravelIntent)

        prompt = PromptTemplate(
            template=INTENT_EXTRACTION_PROMPT,
            input_variables=["message", "context"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        chain = prompt | llm

        context_str = json.dumps(user_context) if user_context else "No previous context"

        result = await chain.ainvoke({
            "message": message,
            "context": context_str,
        })

        if hasattr(result, "content"):
            content = result.content
            if isinstance(content, str):
                result_text = content
            elif isinstance(content, list):
                result_text = "".join(str(item) if isinstance(item, str) else str(item) for item in content)
            else:
                result_text = str(content)
        else:
            result_text = str(result)

        intent = await _parse_intent(result_text, parser)

        intent.missing_info = intent.get_missing_fields()

        return intent

    except Exception as e:
        logger.error(f"Intent extraction failed: {e}", exc_info=True)
        return TravelIntent(
            missing_info=["destination", "days", "budget", "companions"],
            confidence=0.0,
        )


async def _parse_intent(text: str, parser: PydanticOutputParser) -> TravelIntent:
    """Parse LLM output into TravelIntent with fallback handling."""
    
    try:
        intent = parser.parse(text)
        return intent
    except Exception:
        pass

    try:
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            data = json.loads(json_match.group())
            
            if "extra_notes" not in data:
                data["extra_notes"] = {}
            
            data.setdefault("travel_style", [])
            data.setdefault("missing_info", [])
            data.setdefault("confidence", 0.5)
            
            return TravelIntent(**data)
    except (json.JSONDecodeError, Exception) as e:
        logger.warning(f"Fallback JSON parsing failed: {e}")

    return TravelIntent(
        missing_info=["destination", "days", "budget", "companions"],
        confidence=0.0,
    )


def generate_clarification_questions(
    intent: TravelIntent,
    max_questions: int = 3,
) -> ClarificationResponse:
    """
    Generate questions for missing required fields.

    Args:
        intent: Partial TravelIntent
        max_questions: Maximum questions to ask at once

    Returns:
        ClarificationResponse with questions and current state
    """
    missing = intent.get_missing_fields()

    priority_order = ["destination", "days", "budget", "companions", "travel_style", "time_of_year"]
    missing.sort(key=lambda x: priority_order.index(x) if x in priority_order else 999)

    to_ask = missing[:max_questions]

    questions = []
    for field in to_ask:
        template = QUESTION_TEMPLATES.get(field)
        if template:
            questions.append(ClarificationQuestion(
                id=f"q_{field}",
                field=field,
                type=template["type"],
                question=template["question"],
                options=[QuestionOption(**opt) for opt in template.get("options", [])] if template.get("options") else None,
                placeholder=template.get("placeholder"),
                priority=priority_order.index(field) + 1,
            ))

    total_required = 4
    completed = total_required - len(missing)

    return ClarificationResponse(
        type="clarification",
        session_id=None,
        questions=questions,
        current_intent=intent,
        progress={
            "completed": completed,
            "total": total_required,
            "percentage": int((completed / total_required) * 100),
        },
        message=PROGRESS_MESSAGES.get(completed, "Let's continue planning your adventure!"),
    )


def update_intent_from_answers(
    intent: TravelIntent,
    answers: dict,
) -> TravelIntent:
    """
    Update intent based on user's clarification answers.

    Args:
        intent: Current partial intent
        answers: Dictionary of question_id -> answer

    Returns:
        Updated TravelIntent
    """
    update_data = intent.model_dump()

    for question_id, answer in answers.items():
        field = question_id.replace("q_", "")

        if field == "destination":
            update_data["destination"] = answer
        elif field == "days":
            try:
                update_data["days"] = int(answer)
            except (ValueError, TypeError):
                pass
        elif field == "budget":
            update_data["budget"] = answer
        elif field == "companions":
            update_data["companions"] = answer
        elif field == "travel_style":
            if isinstance(answer, list):
                update_data["travel_style"] = answer
            else:
                update_data["travel_style"] = [answer]
        elif field == "time_of_year":
            update_data["time_of_year"] = answer

    updated_intent = TravelIntent(**update_data)
    updated_intent.missing_info = updated_intent.get_missing_fields()

    return updated_intent
