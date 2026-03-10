import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.schemas.chat_api import ClarificationResponse, ItineraryResponse
from app.ai.schemas.intent import TravelIntent
from app.models.trip import Trip

client = TestClient(app)

def test_chat_endpoint_clarification():
    with patch("app.api.chat.ChatService") as MockChatService:
        mock_service = MockChatService.return_value
        
        # Setup mock return value for clarification
        mock_clarification = ClarificationResponse(
            type="clarification",
            session_id="test-session-123",
            questions=[],
            current_intent=TravelIntent(destination="Palawan"),
            progress={"completed": 1, "total": 4, "percentage": 25},
            message="Please provide more details."
        )
        mock_service.process_message = AsyncMock(return_value=mock_clarification)
        
        response = client.post(
            "/api/chat/",
            json={"message": "I want to go to Palawan"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "clarification"
        assert data["session_id"] == "test-session-123"

def test_chat_clarify_endpoint():
    with patch("app.api.chat.ChatService") as MockChatService:
        mock_service = MockChatService.return_value
        
        mock_itinerary = ItineraryResponse(
            type="itinerary",
            session_id="test-session-123",
            trip=Trip(destination="Palawan", days=3, title="Trip", user_id="user"),
            days=[],
            activities=[],
            summary="Great trip",
            highlights=[],
            estimated_cost={},
            tips=[],
            message="Your itinerary is ready!"
        )
        
        mock_service.process_clarification = AsyncMock(return_value=mock_itinerary)
        
        response = client.post(
            "/api/chat/test-session-123/clarify",
            json={"q_days": 3, "q_budget": "mid", "q_companions": "couple"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "itinerary"
        assert data["session_id"] == "test-session-123"
        assert data["trip"]["destination"] == "Palawan"
