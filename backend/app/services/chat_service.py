import logging
import uuid
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple, Union, cast

from app.ai.chains.intent_extraction import (
    extract_intent,
    generate_clarification_questions,
    update_intent_from_answers,
)
from app.ai.chains.itinerary_generation import generate_itinerary
from app.ai.schemas.intent import TravelIntent
from app.ai.schemas.itinerary import ItineraryOutput
from app.db.engine import async_session
from app.models.trip import Activity, Trip, TripDay
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

    def __init__(
        self,
        redis_url: Optional[str] = None,
        write_session_factory: Callable[[], Any] = async_session,
    ):
        # Kept for backward compatibility while Redis is intentionally disabled.
        self.redis_url = redis_url
        self.write_session_factory = write_session_factory

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

    def _extract_budget_range(self, estimated_cost: Dict[str, Any]) -> Tuple[Optional[int], Optional[int]]:
        total_min = estimated_cost.get("total_min")
        total_max = estimated_cost.get("total_max")

        if isinstance(total_min, int) or total_min is None:
            parsed_min = total_min
        else:
            parsed_min = None

        if isinstance(total_max, int) or total_max is None:
            parsed_max = total_max
        else:
            parsed_max = None

        return parsed_min, parsed_max

    def _build_trip_title(self, itinerary: ItineraryOutput) -> str:
        return f"{itinerary.destination} {itinerary.days}-day itinerary"

    async def _persist_itinerary(
        self,
        itinerary: ItineraryOutput,
        intent: TravelIntent,
        user_id: str,
    ) -> int:
        total_budget_min, total_budget_max = self._extract_budget_range(itinerary.estimated_cost)

        async with self.write_session_factory() as write_session:
            async with write_session.begin():
                trip = Trip(
                    user_id=user_id,
                    title=self._build_trip_title(itinerary),
                    summary=itinerary.summary,
                    destination=itinerary.destination,
                    days=itinerary.days,
                    budget=itinerary.budget,
                    travel_style=[str(style) for style in intent.travel_style],
                    companions=itinerary.companions,
                    time_of_year=intent.time_of_year,
                    total_budget_min=total_budget_min,
                    total_budget_max=total_budget_max,
                )
                write_session.add(trip)
                await write_session.flush()

                if trip.id is None:
                    raise RuntimeError("Trip persistence failed to generate an identifier.")
                persisted_trip_id = cast(int, trip.id)

                for day_data in itinerary.days_data:
                    trip_day = TripDay(
                        trip_id=persisted_trip_id,
                        day_number=day_data.day_number,
                        title=day_data.title,
                    )
                    write_session.add(trip_day)
                    await write_session.flush()

                    if trip_day.id is None:
                        raise RuntimeError("Trip day persistence failed to generate an identifier.")
                    persisted_day_id = cast(int, trip_day.id)

                    for index, activity_data in enumerate(day_data.activities):
                        activity = Activity(
                            trip_day_id=persisted_day_id,
                            name=activity_data.name,
                            description=activity_data.description,
                            category=activity_data.category,
                            latitude=activity_data.latitude,
                            longitude=activity_data.longitude,
                            duration_minutes=activity_data.duration_minutes,
                            cost_min=activity_data.cost_min,
                            cost_max=activity_data.cost_max,
                            start_time=activity_data.start_time,
                            notes=activity_data.notes,
                            sort_order=index,
                        )
                        write_session.add(activity)

                return persisted_trip_id

    def _build_itinerary_response(
        self,
        session_id: str,
        itinerary: ItineraryOutput,
        trip_id: Optional[int] = None,
    ) -> ItineraryResponse:
        return ItineraryResponse(
            session_id=session_id,
            trip_id=trip_id,
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

            trip_id: Optional[int] = None
            if user_id:
                try:
                    trip_id = await self._persist_itinerary(itinerary, intent, user_id)
                except Exception as error:
                    logger.error("Failed to persist itinerary for session %s: %s", session.id, error, exc_info=True)
                    return ErrorResponse(
                        error_code="PERSISTENCE_ERROR",
                        message="Unable to save your itinerary right now. Please try again.",
                    )

            return self._build_itinerary_response(session.id, itinerary, trip_id)

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

            trip_id: Optional[int] = None
            if user_id:
                try:
                    trip_id = await self._persist_itinerary(itinerary, intent, user_id)
                except Exception as error:
                    logger.error("Failed to persist itinerary for session %s: %s", session.id, error, exc_info=True)
                    return ErrorResponse(
                        error_code="PERSISTENCE_ERROR",
                        message="Unable to save your itinerary right now. Please try again.",
                    )

            return self._build_itinerary_response(session.id, itinerary, trip_id)

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

            trip_id: Optional[int] = None
            if user_id:
                try:
                    trip_id = await self._persist_itinerary(itinerary, session.current_intent, user_id)
                except Exception as error:
                    logger.error("Failed to persist itinerary for session %s: %s", session.id, error, exc_info=True)
                    return ErrorResponse(
                        error_code="PERSISTENCE_ERROR",
                        message="Unable to save your itinerary right now. Please try again.",
                    )

            return self._build_itinerary_response(session.id, itinerary, trip_id)

        except Exception as e:
            logger.error("Itinerary generation failed for session %s: %s", session_id, e, exc_info=True)
            return ErrorResponse(
                error_code="PROCESSING_ERROR",
                message="I encountered an error generating your itinerary. Please try again.",
            )
