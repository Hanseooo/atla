import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple, Union

from app.ai.chains.intent_extraction import (
    extract_intent,
    generate_clarification_questions,
    update_intent_from_answers,
)
from app.ai.chains.itinerary_generation import generate_itinerary
from app.ai.schemas.intent import TravelIntent
from app.schemas.chat_api import (
    ChatSession,
    ClarificationResponse,
    ErrorResponse,
    ItineraryResponse,
)

logger = logging.getLogger(__name__)


class ChatService:
    """Main orchestrator for chat interactions."""

    _sessions: Dict[str, ChatSession] = {}

    def __init__(self, redis_url: Optional[str] = None):
        # Kept for backward compatibility while Redis is intentionally disabled.
        self.redis_url = redis_url

    def _reconcile_session_identity(
        self,
        session: ChatSession,
        user_id: Optional[str],
    ) -> Tuple[bool, Optional[ErrorResponse]]:
        """Bind anonymous sessions to authenticated users and enforce ownership."""
        if session.user_id is None and user_id:
            session.user_id = user_id
            return True, None

        if session.user_id is None:
            return False, None

        if user_id is None:
            return False, ErrorResponse(
                error_code="SESSION_ACCESS_DENIED",
                message="Authentication is required to access this session.",
            )

        if session.user_id != user_id:
            return False, ErrorResponse(
                error_code="SESSION_ACCESS_DENIED",
                message="You do not have access to this chat session.",
            )

        return False, None

    async def _get_or_create_session(
        self,
        session_id: Optional[str],
        user_id: Optional[str],
    ) -> Union[ChatSession, ErrorResponse]:
        """Get existing in-memory session or create new one."""
        if session_id and session_id in self._sessions:
            session = self._sessions[session_id]
            identity_changed, error = self._reconcile_session_identity(session, user_id)
            if error:
                return error
            if identity_changed:
                await self._save_session(session)
            return session

        session = ChatSession(
            id=session_id or str(uuid.uuid4()),
            user_id=user_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self._sessions[session.id] = session
        return session

    async def _save_session(self, session: ChatSession) -> None:
        session.updated_at = datetime.now(timezone.utc)
        self._sessions[session.id] = session

    async def _get_session(self, session_id: str) -> Optional[ChatSession]:
        return self._sessions.get(session_id)

    async def get_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
    ) -> Union[ChatSession, ErrorResponse, None]:
        """Get a session while enforcing ownership rules for the active user."""
        session = await self._get_session(session_id)
        if session is None:
            return None

        identity_changed, error = self._reconcile_session_identity(session, user_id)
        if error:
            return error

        if identity_changed:
            await self._save_session(session)

        return session

    async def _load_user_preferences(self, user_id: str) -> Optional[dict]:
        """Load user preferences from DB (stub for future integration)."""
        return None

    async def _merge_intents(
        self,
        existing: TravelIntent,
        new_intent: TravelIntent,
    ) -> TravelIntent:
        """Merge new extracted intent data into an existing session intent."""
        merged_data = existing.model_dump()
        new_data = new_intent.model_dump(exclude_unset=True, exclude_none=True)

        for key, value in new_data.items():
            if value and (isinstance(value, list) and len(value) > 0 or not isinstance(value, list)):
                if key == "extra_notes" and isinstance(value, dict):
                    for en_key, en_val in value.items():
                        if en_val:
                            if "extra_notes" not in merged_data:
                                merged_data["extra_notes"] = {}
                            merged_data["extra_notes"][en_key] = en_val
                else:
                    merged_data[key] = value

        merged_intent = TravelIntent(**merged_data)
        merged_intent.missing_info = merged_intent.get_missing_fields()
        return merged_intent

    def _build_itinerary_response(self, session_id: str, itinerary: Any) -> ItineraryResponse:
        return ItineraryResponse(
            session_id=session_id,
            destination=itinerary.destination,
            days=itinerary.days,
            budget=itinerary.budget,
            companions=itinerary.companions,
            days_data=itinerary.days_data,
            summary=itinerary.summary,
            highlights=itinerary.highlights,
            estimated_cost=itinerary.estimated_cost,
            tips=itinerary.tips,
            packing_suggestions=itinerary.packing_suggestions,
            message="Your itinerary is ready!",
        )

    async def process_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Union[ClarificationResponse, ItineraryResponse, ErrorResponse]:
        """Process an incoming chat message."""
        try:
            session_or_error = await self._get_or_create_session(session_id, user_id)
            if isinstance(session_or_error, ErrorResponse):
                return session_or_error
            session = session_or_error
            user_context = await self._load_user_preferences(user_id) if user_id else None

            intent = await extract_intent(message, user_context)

            if session.current_intent:
                intent = await self._merge_intents(session.current_intent, intent)

            session.current_intent = intent

            if not intent.is_complete():
                clarification = generate_clarification_questions(intent)
                clarification.session_id = session.id
                session.last_clarification = clarification
                await self._save_session(session)
                return clarification

            itinerary = await generate_itinerary(intent)
            await self._save_session(session)
            return self._build_itinerary_response(session.id, itinerary)

        except Exception as e:
            logger.error("Chat processing failed: %s", e, exc_info=True)
            return ErrorResponse(
                error_code="PROCESSING_ERROR",
                message="I'm having trouble understanding your request. Could you try rephrasing?",
            )

    async def process_clarification(
        self,
        session_id: str,
        answers: Dict[str, Any],
        user_id: Optional[str] = None,
    ) -> Union[ClarificationResponse, ItineraryResponse, ErrorResponse]:
        """Process answers to clarification questions."""
        try:
            session_or_error = await self._get_or_create_session(session_id, user_id)
            if isinstance(session_or_error, ErrorResponse):
                return session_or_error
            session = session_or_error

            if not session.current_intent:
                return ErrorResponse(
                    error_code="SESSION_NOT_FOUND",
                    message="Session not found or expired. Please start over.",
                )

            intent = update_intent_from_answers(session.current_intent, answers)
            session.current_intent = intent

            if not intent.is_complete():
                clarification = generate_clarification_questions(intent)
                clarification.session_id = session.id
                session.last_clarification = clarification
                await self._save_session(session)
                return clarification

            itinerary = await generate_itinerary(intent)
            await self._save_session(session)
            return self._build_itinerary_response(session.id, itinerary)

        except Exception as e:
            logger.error("Clarification processing failed: %s", e, exc_info=True)
            return ErrorResponse(
                error_code="PROCESSING_ERROR",
                message="I encountered an error processing your answers. Please try again.",
            )

    async def generate_itinerary_for_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
    ) -> Union[ItineraryResponse, ErrorResponse]:
        """Generate an itinerary for a complete intent in an existing session."""
        try:
            session_or_error = await self._get_or_create_session(session_id, user_id)
            if isinstance(session_or_error, ErrorResponse):
                return session_or_error
            session = session_or_error

            if not session.current_intent:
                return ErrorResponse(
                    error_code="SESSION_NOT_FOUND",
                    message="Session not found or expired. Please start over.",
                )

            if not session.current_intent.is_complete():
                return ErrorResponse(
                    error_code="INTENT_INCOMPLETE",
                    message="Trip details are incomplete. Please answer the remaining questions first.",
                )

            itinerary = await generate_itinerary(session.current_intent)
            await self._save_session(session)
            return self._build_itinerary_response(session.id, itinerary)

        except Exception as e:
            logger.error("Itinerary generation failed for session %s: %s", session_id, e, exc_info=True)
            return ErrorResponse(
                error_code="PROCESSING_ERROR",
                message="I encountered an error generating your itinerary. Please try again.",
            )
