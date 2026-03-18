from unittest.mock import AsyncMock, patch
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.ai.schemas.intent import TravelIntent
from app.ai.schemas.itinerary import TripDayData
from app.api.deps import get_optional_user
from app.main import app
from app.schemas.chat_api import ClarificationResponse, ErrorResponse, ItineraryResponse

client = TestClient(app)


def test_chat_endpoint_clarification():
    with patch("app.api.chat.ChatService") as mock_chat_service:
        mock_service = mock_chat_service.return_value

        mock_clarification = ClarificationResponse(
            type="clarification",
            session_id="test-session-123",
            questions=[],
            current_intent=TravelIntent(destination="Palawan"),
            progress={"completed": 1, "total": 4, "percentage": 25},
            message="Please provide more details.",
        )
        mock_service.process_message = AsyncMock(return_value=mock_clarification)

        response = client.post("/api/chat/", json={"message": "I want to go to Palawan"})

        assert response.status_code == 200
        mock_service.process_message.assert_awaited_once_with(
            message="I want to go to Palawan",
            session_id=None,
            user_id=None,
        )
        data = response.json()
        assert data["type"] == "clarification"
        assert data["session_id"] == "test-session-123"


def test_chat_endpoint_passes_authenticated_user_id():
    app.dependency_overrides[get_optional_user] = lambda: SimpleNamespace(id="user-123")

    try:
        with patch("app.api.chat.ChatService") as mock_chat_service:
            mock_service = mock_chat_service.return_value

            mock_clarification = ClarificationResponse(
                type="clarification",
                session_id="test-session-123",
                questions=[],
                current_intent=TravelIntent(destination="Palawan"),
                progress={"completed": 1, "total": 4, "percentage": 25},
                message="Please provide more details.",
            )
            mock_service.process_message = AsyncMock(return_value=mock_clarification)

            response = client.post("/api/chat/", json={"message": "Plan a Palawan trip"})

            assert response.status_code == 200
            mock_service.process_message.assert_awaited_once_with(
                message="Plan a Palawan trip",
                session_id=None,
                user_id="user-123",
            )
    finally:
        app.dependency_overrides.clear()


def test_chat_clarify_endpoint():
    with patch("app.api.chat.ChatService") as mock_chat_service:
        mock_service = mock_chat_service.return_value

        mock_itinerary = ItineraryResponse(
            type="itinerary",
            session_id="test-session-123",
            destination="Palawan",
            days=3,
            budget="mid",
            companions="couple",
            days_data=[TripDayData(day_number=1, title="Day 1", activities=[])],
            summary="Great trip",
            highlights=[],
            estimated_cost={},
            tips=[],
            packing_suggestions=[],
            message="Your itinerary is ready!",
        )

        mock_service.process_clarification = AsyncMock(return_value=mock_itinerary)

        response = client.post(
            "/api/chat/test-session-123/clarify",
            json={"q_days": 3, "q_budget": "mid", "q_companions": "couple"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "itinerary"
        assert data["session_id"] == "test-session-123"
        assert data["destination"] == "Palawan"


def test_generate_itinerary_endpoint():
    with patch("app.api.chat.ChatService") as mock_chat_service:
        mock_service = mock_chat_service.return_value
        mock_itinerary = ItineraryResponse(
            type="itinerary",
            session_id="test-session-123",
            destination="Cebu",
            days=5,
            budget="mid",
            companions="solo",
            days_data=[],
            summary="Generated",
            highlights=[],
            estimated_cost={},
            tips=[],
            packing_suggestions=[],
            message="Your itinerary is ready!",
        )
        mock_service.generate_itinerary_for_session = AsyncMock(return_value=mock_itinerary)

        response = client.post("/api/chat/test-session-123/generate-itinerary")

        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "itinerary"
        assert data["destination"] == "Cebu"


def test_get_chat_history_forbidden_when_service_denies_access():
    with patch("app.api.chat.ChatService") as mock_chat_service:
        mock_service = mock_chat_service.return_value
        mock_service.get_session = AsyncMock(
            return_value=ErrorResponse(
                error_code="SESSION_ACCESS_DENIED",
                message="You do not have access to this chat session.",
            )
        )

        response = client.get("/api/chat/test-session-123")

        assert response.status_code == 403
        assert response.json()["detail"] == "You do not have access to this chat session."


def test_chat_endpoint_forbidden_when_service_denies_access():
    with patch("app.api.chat.ChatService") as mock_chat_service:
        mock_service = mock_chat_service.return_value
        mock_service.process_message = AsyncMock(
            return_value=ErrorResponse(
                error_code="SESSION_ACCESS_DENIED",
                message="You do not have access to this chat session.",
            )
        )

        response = client.post("/api/chat/", json={"message": "blocked"})

        assert response.status_code == 403
        assert response.json()["detail"] == "You do not have access to this chat session."


def test_chat_clarify_forbidden_when_service_denies_access():
    with patch("app.api.chat.ChatService") as mock_chat_service:
        mock_service = mock_chat_service.return_value
        mock_service.process_clarification = AsyncMock(
            return_value=ErrorResponse(
                error_code="SESSION_ACCESS_DENIED",
                message="You do not have access to this chat session.",
            )
        )

        response = client.post("/api/chat/test-session-123/clarify", json={"q_budget": "mid"})

        assert response.status_code == 403
        assert response.json()["detail"] == "You do not have access to this chat session."


def test_generate_itinerary_forbidden_when_service_denies_access():
    with patch("app.api.chat.ChatService") as mock_chat_service:
        mock_service = mock_chat_service.return_value
        mock_service.generate_itinerary_for_session = AsyncMock(
            return_value=ErrorResponse(
                error_code="SESSION_ACCESS_DENIED",
                message="You do not have access to this chat session.",
            )
        )

        response = client.post("/api/chat/test-session-123/generate-itinerary")

        assert response.status_code == 403
        assert response.json()["detail"] == "You do not have access to this chat session."


def test_generate_itinerary_keeps_non_auth_errors_as_bad_request():
    with patch("app.api.chat.ChatService") as mock_chat_service:
        mock_service = mock_chat_service.return_value
        mock_service.generate_itinerary_for_session = AsyncMock(
            return_value=ErrorResponse(
                error_code="INTENT_INCOMPLETE",
                message="Trip details are incomplete.",
            )
        )

        response = client.post("/api/chat/test-session-123/generate-itinerary")

        assert response.status_code == 400
        assert response.json()["detail"] == "Trip details are incomplete."
