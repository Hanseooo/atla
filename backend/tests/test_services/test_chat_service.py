from unittest.mock import AsyncMock, patch

import pytest

from app.ai.schemas.intent import ClarificationResponse, TravelIntent
from app.ai.schemas.itinerary import ItineraryOutput
from app.schemas.chat_api import ItineraryResponse
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
