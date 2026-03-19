from unittest.mock import AsyncMock, patch

import pytest

from app.ai.schemas.intent import ClarificationResponse, TravelIntent
from app.ai.schemas.itinerary import ActivityData, ItineraryOutput, TripDayData
from app.models.trip import Activity, Trip, TripDay
from app.schemas.chat_api import ErrorResponse, ItineraryResponse
from app.services.chat_service import ChatService


@pytest.fixture
def chat_service():
    ChatService._sessions.clear()
    return ChatService()


class FakeTransaction:
    def __init__(self, session):
        self.session = session

    async def __aenter__(self):
        return self.session

    async def __aexit__(self, exc_type, exc, tb):
        if exc is not None:
            self.session.rolled_back = True
        else:
            self.session.committed = True
        return False


class FakeSession:
    def __init__(self, fail_on_activity: bool = False):
        self.added = []
        self.fail_on_activity = fail_on_activity
        self.trip_id_counter = 1
        self.day_id_counter = 1
        self.rolled_back = False
        self.committed = False

    def begin(self):
        return FakeTransaction(self)

    def add(self, model):
        if self.fail_on_activity and isinstance(model, Activity):
            raise RuntimeError("activity write failed")
        self.added.append(model)

    async def flush(self):
        current = self.added[-1]
        if isinstance(current, Trip) and current.id is None:
            current.id = self.trip_id_counter
            self.trip_id_counter += 1
        if isinstance(current, TripDay) and current.id is None:
            current.id = self.day_id_counter
            self.day_id_counter += 1

    def in_transaction(self):
        return False

    async def rollback(self):
        self.rolled_back = True


class FakeSessionFactory:
    def __init__(self, session: FakeSession):
        self.session = session

    async def __aenter__(self):
        return self.session

    async def __aexit__(self, exc_type, exc, tb):
        return False


def make_session_factory(fake_session: FakeSession):
    def _factory():
        return FakeSessionFactory(fake_session)

    return _factory


def make_complete_intent() -> TravelIntent:
    return TravelIntent(
        destination="Cebu",
        days=3,
        budget="mid",
        companions="solo",
        travel_style=["culture"],
        time_of_year="April",
    )


def make_itinerary_output() -> ItineraryOutput:
    return ItineraryOutput(
        destination="Cebu",
        days=3,
        budget="mid",
        companions="solo",
        summary="Great trip",
        highlights=["Historic sites"],
        estimated_cost={"total_min": 10000, "total_max": 18000},
        tips=["Bring water"],
        packing_suggestions=["Light clothes"],
        days_data=[
            TripDayData(
                day_number=1,
                title="Arrival",
                activities=[
                    ActivityData(
                        name="Magellan's Cross",
                        category="attraction",
                        duration_minutes=90,
                        cost_min=100,
                        cost_max=200,
                    )
                ],
            )
        ],
    )


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


@pytest.mark.asyncio
async def test_process_message_persists_trip_for_authenticated_user():
    ChatService._sessions.clear()
    fake_session = FakeSession()
    service = ChatService(write_session_factory=make_session_factory(fake_session))

    with patch("app.services.chat_service.extract_intent", new_callable=AsyncMock) as mock_extract, patch(
        "app.services.chat_service.generate_itinerary", new_callable=AsyncMock
    ) as mock_generate:
        mock_extract.return_value = make_complete_intent()
        mock_generate.return_value = make_itinerary_output()

        response = await service.process_message(
            "Plan my trip",
            user_id="user-123",
        )

        assert isinstance(response, ItineraryResponse)
        assert response.trip_id == 1
        assert fake_session.committed is True
        assert any(isinstance(item, Trip) for item in fake_session.added)
        assert any(isinstance(item, TripDay) for item in fake_session.added)
        assert any(isinstance(item, Activity) for item in fake_session.added)


@pytest.mark.asyncio
async def test_process_message_skips_persistence_for_anonymous_user():
    ChatService._sessions.clear()
    fake_session = FakeSession()
    service = ChatService(write_session_factory=make_session_factory(fake_session))

    with patch("app.services.chat_service.extract_intent", new_callable=AsyncMock) as mock_extract, patch(
        "app.services.chat_service.generate_itinerary", new_callable=AsyncMock
    ) as mock_generate:
        mock_extract.return_value = make_complete_intent()
        mock_generate.return_value = make_itinerary_output()

        response = await service.process_message("Plan my trip")

        assert isinstance(response, ItineraryResponse)
        assert response.trip_id is None
        assert fake_session.added == []


@pytest.mark.asyncio
async def test_process_message_returns_error_when_persistence_fails():
    ChatService._sessions.clear()
    fake_session = FakeSession(fail_on_activity=True)
    service = ChatService(write_session_factory=make_session_factory(fake_session))

    with patch("app.services.chat_service.extract_intent", new_callable=AsyncMock) as mock_extract, patch(
        "app.services.chat_service.generate_itinerary", new_callable=AsyncMock
    ) as mock_generate:
        mock_extract.return_value = make_complete_intent()
        mock_generate.return_value = make_itinerary_output()

        response = await service.process_message(
            "Plan my trip",
            user_id="user-123",
        )

        assert isinstance(response, ErrorResponse)
        assert response.error_code == "PERSISTENCE_ERROR"
        assert fake_session.rolled_back is True


@pytest.mark.asyncio
async def test_generate_itinerary_for_session_persists_trip_for_authenticated_user():
    ChatService._sessions.clear()
    fake_session = FakeSession()
    service = ChatService(write_session_factory=make_session_factory(fake_session))

    with patch("app.services.chat_service.extract_intent", new_callable=AsyncMock) as mock_extract, patch(
        "app.services.chat_service.generate_itinerary", new_callable=AsyncMock
    ) as mock_generate:
        mock_extract.return_value = make_complete_intent()
        mock_generate.return_value = make_itinerary_output()

        initial = await service.process_message(
            "Plan my trip",
            session_id="persist-session",
        )
        assert isinstance(initial, ItineraryResponse)

        response = await service.generate_itinerary_for_session(
            "persist-session",
            user_id="user-123",
        )

        assert isinstance(response, ItineraryResponse)
        assert response.trip_id == 1
