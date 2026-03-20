from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.main import app
from app.models.trip import Activity, Trip, TripDay

client = TestClient(app)


def _make_trip(*, trip_id: int = 1, user_id: str = "user-123") -> Trip:
    return Trip(
        id=trip_id,
        user_id=user_id,
        title="Cebu Adventure",
        summary="A 3-day Cebu itinerary",
        destination="Cebu",
        days=3,
        budget="mid",
        travel_style=["culture", "food"],
        companions="solo",
        time_of_year="April",
        total_budget_min=10000,
        total_budget_max=18000,
        is_public=False,
        view_count=0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def test_list_trips_requires_authentication():
    response = client.get("/api/trips/")

    assert response.status_code == 401


def test_list_trips_returns_authenticated_user_trips():
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id="user-123")

    try:
        with patch("app.api.trips.TripRepository") as mock_trip_repo:
            mock_repo = mock_trip_repo.return_value
            mock_repo.get_by_user = AsyncMock(return_value=[_make_trip()])

            response = client.get("/api/trips/")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["id"] == 1
            assert data[0]["destination"] == "Cebu"
            mock_repo.get_by_user.assert_awaited_once_with("user-123", skip=0, limit=20)
    finally:
        app.dependency_overrides.clear()


def test_get_trip_detail_requires_authentication():
    response = client.get("/api/trips/1")

    assert response.status_code == 401


def test_get_trip_detail_returns_nested_days_and_activities():
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id="user-123")

    try:
        with patch("app.api.trips.TripRepository") as mock_trip_repo, patch(
            "app.api.trips.TripDayRepository"
        ) as mock_day_repo, patch("app.api.trips.ActivityRepository") as mock_activity_repo:
            trip_repo = mock_trip_repo.return_value
            day_repo = mock_day_repo.return_value
            activity_repo = mock_activity_repo.return_value

            trip_repo.get = AsyncMock(return_value=_make_trip())
            day_repo.get_by_trip = AsyncMock(
                return_value=[
                    TripDay(
                        id=10,
                        trip_id=1,
                        day_number=1,
                        title="Arrival",
                    )
                ]
            )
            activity_repo.get_by_trip_day = AsyncMock(
                return_value=[
                    Activity(
                        id=100,
                        trip_day_id=10,
                        name="Magellan's Cross",
                        category="attraction",
                        sort_order=0,
                    )
                ]
            )

            response = client.get("/api/trips/1")

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == 1
            assert len(data["trip_days"]) == 1
            assert data["trip_days"][0]["day_number"] == 1
            assert len(data["trip_days"][0]["activities"]) == 1
            assert data["trip_days"][0]["activities"][0]["name"] == "Magellan's Cross"
            trip_repo.get.assert_awaited_once_with(1)
            day_repo.get_by_trip.assert_awaited_once_with(1)
            activity_repo.get_by_trip_day.assert_awaited_once_with(10)
    finally:
        app.dependency_overrides.clear()


def test_get_trip_detail_returns_404_for_cross_user_access():
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id="user-999")

    try:
        with patch("app.api.trips.TripRepository") as mock_trip_repo:
            trip_repo = mock_trip_repo.return_value
            trip_repo.get = AsyncMock(return_value=_make_trip(user_id="user-123"))

            response = client.get("/api/trips/1")

            assert response.status_code == 404
            assert response.json()["detail"] == "Trip not found"
    finally:
        app.dependency_overrides.clear()


def test_get_trip_detail_returns_404_when_missing():
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id="user-123")

    try:
        with patch("app.api.trips.TripRepository") as mock_trip_repo:
            trip_repo = mock_trip_repo.return_value
            trip_repo.get = AsyncMock(return_value=None)

            response = client.get("/api/trips/999")

            assert response.status_code == 404
            assert response.json()["detail"] == "Trip not found"
    finally:
        app.dependency_overrides.clear()
