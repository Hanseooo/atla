from unittest.mock import AsyncMock, patch

import pytest

from app.ai.schemas.intent import ClarificationResponse, TravelIntent
from app.ai.schemas.itinerary import ItineraryOutput
from app.schemas.chat_api import ErrorResponse, ItineraryResponse
from app.services.chat_service import ChatService


@pytest.fixture
def chat_service():
    ChatService._sessions.clear()
    return ChatService()


@pytest.mark.asyncio
async def test_process_message_clarification(chat_service):
    with patch("app.services.chat_service.extract_intent", new_callable=AsyncMock) as mock_extract:
        mock_extract.return_value = TravelIntent(destination="Cebu")

        response = await chat_service.process_message("I want to go to Cebu")

        assert isinstance(response, ClarificationResponse)
        assert response.session_id is not None
        assert response.current_intent.destination == "Cebu"
        assert response.progress["completed"] < 4


@pytest.mark.asyncio
async def test_process_message_itinerary(chat_service):
    with patch("app.services.chat_service.extract_intent", new_callable=AsyncMock) as mock_extract, patch(
        "app.services.chat_service.generate_itinerary", new_callable=AsyncMock
    ) as mock_generate:
        mock_extract.return_value = TravelIntent(
            destination="Cebu",
            days=3,
            budget="mid",
            companions="solo",
        )
        mock_generate.return_value = ItineraryOutput(
            destination="Cebu",
            days=3,
            budget="mid",
            companions="solo",
            days_data=[],
            summary="Great trip",
            highlights=[],
            estimated_cost={},
            tips=[],
            packing_suggestions=[],
        )

        response = await chat_service.process_message(
            "I want to go to Cebu for 3 days solo with mid budget"
        )

        assert isinstance(response, ItineraryResponse)
        assert response.session_id is not None
        assert response.destination == "Cebu"
        assert response.days == 3


@pytest.mark.asyncio
async def test_existing_anonymous_session_binds_to_authenticated_user(chat_service):
    anonymous_session = await chat_service._get_or_create_session("session-1", None)

    assert anonymous_session.user_id is None

    bound_session = await chat_service._get_or_create_session("session-1", "user-123")

    assert not isinstance(bound_session, ErrorResponse)
    assert bound_session.user_id == "user-123"


@pytest.mark.asyncio
async def test_owned_session_denies_different_authenticated_user(chat_service):
    owner_session = await chat_service._get_or_create_session("session-2", "user-123")

    assert owner_session.user_id == "user-123"

    denied = await chat_service._get_or_create_session("session-2", "user-999")

    assert isinstance(denied, ErrorResponse)
    assert denied.error_code == "SESSION_ACCESS_DENIED"


@pytest.mark.asyncio
async def test_owned_session_denies_anonymous_access(chat_service):
    owner_session = await chat_service._get_or_create_session("session-3", "user-123")

    assert owner_session.user_id == "user-123"

    denied = await chat_service.get_session("session-3", None)

    assert isinstance(denied, ErrorResponse)
    assert denied.error_code == "SESSION_ACCESS_DENIED"
