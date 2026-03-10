import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.chat_service import ChatService
from app.ai.schemas.intent import TravelIntent, ClarificationResponse, ClarificationQuestion
from app.schemas.chat_api import ItineraryResponse
from app.models.trip import Trip

@pytest.fixture
def mock_redis():
    with patch("app.services.chat_service.Redis.from_url") as mock_from_url:
        mock_redis_instance = AsyncMock()
        mock_from_url.return_value = mock_redis_instance
        yield mock_redis_instance

@pytest.fixture
def chat_service(mock_redis):
    return ChatService(redis_url="redis://mock")

@pytest.mark.asyncio
async def test_process_message_clarification(chat_service, mock_redis):
    # Mock extract_intent to return an incomplete intent
    with patch("app.services.chat_service.extract_intent", new_callable=AsyncMock) as mock_extract:
        mock_intent = TravelIntent(destination="Cebu")
        mock_extract.return_value = mock_intent
        
        # Test process_message
        mock_redis.get.return_value = None # No existing session
        
        response = await chat_service.process_message("I want to go to Cebu")
        
        assert isinstance(response, ClarificationResponse)
        assert response.session_id is not None
        assert response.current_intent.destination == "Cebu"
        assert response.progress["completed"] < 4
        
        # Verify redis methods called
        mock_redis.setex.assert_called_once()

@pytest.mark.asyncio
async def test_process_message_itinerary(chat_service, mock_redis):
    # Mock extract_intent to return a complete intent
    with patch("app.services.chat_service.extract_intent", new_callable=AsyncMock) as mock_extract:
        mock_intent = TravelIntent(destination="Cebu", days=3, budget="mid", companions="solo")
        mock_extract.return_value = mock_intent
        
        mock_redis.get.return_value = None
        
        response = await chat_service.process_message("I want to go to Cebu for 3 days solo with mid budget")
        
        assert isinstance(response, ItineraryResponse)
        assert response.session_id is not None
        assert response.trip.destination == "Cebu"
        assert response.trip.days == 3
        
        mock_redis.expire.assert_called_once()
