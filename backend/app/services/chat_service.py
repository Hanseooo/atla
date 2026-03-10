import uuid
import json
import logging
from typing import Optional, Union, Dict, Any
from datetime import datetime
from redis.asyncio import Redis

# Using a mocked itinerary generator since Issue #6 is not implemented yet
# When Issue #6 is complete, this will be replaced with the real chain
try:
    from app.ai.chains.itinerary_generation import generate_itinerary
except ImportError:
    from app.models.trip import Trip, TripDay, Activity
    async def generate_itinerary(intent: Any) -> Any:
        class MockItinerary:
            trip = Trip(destination=intent.destination, days=intent.days, title=f"{intent.days}-Day Trip to {intent.destination}", user_id="mock")
            days = []
            activities = []
            summary = "Mock itinerary summary."
            highlights = ["Mock highlight"]
            estimated_cost = {"total_min": 1000, "total_max": 2000, "currency": "PHP"}
            tips = ["Mock tip"]
        
        return MockItinerary()

from app.ai.chains.intent_extraction import extract_intent, generate_clarification_questions, update_intent_from_answers
from app.schemas.chat_api import ChatSession, ClarificationResponse, ItineraryResponse, ErrorResponse
from app.ai.schemas.intent import TravelIntent
from pydantic import ValidationError

logger = logging.getLogger(__name__)

class ChatService:
    """Main orchestrator for chat interactions"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = Redis.from_url(redis_url)
        self.session_ttl = 600  # 10 minutes
        self.cleanup_delay = 120  # 2 minutes after completion

    async def _get_or_create_session(
        self,
        session_id: Optional[str],
        user_id: Optional[str]
    ) -> ChatSession:
        """Get existing session or create new one"""
        if session_id:
            try:
                data = await self.redis.get(f"chat:{session_id}")
                if data:
                    return ChatSession.model_validate_json(data)
            except Exception as e:
                logger.warning(f"Failed to load session {session_id} from Redis: {e}")
        
        # Create new session
        return ChatSession(
            id=session_id or str(uuid.uuid4()),
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    async def _save_session(self, session: ChatSession):
        """Save session to Redis"""
        session.updated_at = datetime.utcnow()
        try:
            await self.redis.setex(
                f"chat:{session.id}",
                self.session_ttl,
                session.model_dump_json()
            )
        except Exception as e:
            logger.error(f"Failed to save session {session.id} to Redis: {e}")

    async def _schedule_cleanup(self, session_id: str):
        """Schedule Redis cleanup after delay"""
        try:
            await self.redis.expire(f"chat:{session_id}", self.cleanup_delay)
        except Exception as e:
            logger.error(f"Failed to schedule cleanup for session {session_id}: {e}")

    async def _load_user_preferences(self, user_id: str) -> Optional[dict]:
        """Load user preferences from DB (Mocked for now)"""
        return None

    async def _merge_intents(self, existing: TravelIntent, new_intent: TravelIntent) -> TravelIntent:
        """Merge new intent data into existing intent"""
        merged_data = existing.model_dump()
        new_data = new_intent.model_dump(exclude_unset=True, exclude_none=True)
        
        for key, value in new_data.items():
            if value and (isinstance(value, list) and len(value) > 0 or not isinstance(value, list)):
                if key == "extra_notes":
                    # Deep merge extra notes
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

    async def process_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Union[ClarificationResponse, ItineraryResponse, ErrorResponse]:
        """
        Main entry point for processing chat messages.
        """
        try:
            session = await self._get_or_create_session(session_id, user_id)
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
            
            await self._schedule_cleanup(session.id)
            
            return ItineraryResponse(
                session_id=session.id,
                trip=itinerary.trip,
                days=itinerary.days,
                activities=itinerary.activities,
                summary=itinerary.summary,
                highlights=itinerary.highlights,
                estimated_cost=itinerary.estimated_cost,
                tips=itinerary.tips,
                message="Your itinerary is ready! 🎉"
            )
            
        except Exception as e:
            logger.error(f"Chat processing failed: {e}", exc_info=True)
            return ErrorResponse(
                error_code="PROCESSING_ERROR",
                message="I'm having trouble understanding your request. Could you try rephrasing?"
            )

    async def process_clarification(
        self,
        session_id: str,
        answers: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Union[ClarificationResponse, ItineraryResponse, ErrorResponse]:
        """Process answers to clarification questions."""
        try:
            session = await self._get_or_create_session(session_id, user_id)
            
            if not session.current_intent:
                return ErrorResponse(
                    error_code="SESSION_NOT_FOUND",
                    message="Session not found or expired. Please start over."
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
            await self._schedule_cleanup(session.id)
            
            return ItineraryResponse(
                session_id=session.id,
                trip=itinerary.trip,
                days=itinerary.days,
                activities=itinerary.activities,
                summary=itinerary.summary,
                highlights=itinerary.highlights,
                estimated_cost=itinerary.estimated_cost,
                tips=itinerary.tips,
                message="Your itinerary is ready! 🎉"
            )
            
        except Exception as e:
            logger.error(f"Clarification processing failed: {e}", exc_info=True)
            return ErrorResponse(
                error_code="PROCESSING_ERROR",
                message="I encountered an error processing your answers. Please try again."
            )
