from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.user import UserProfile
from app.repositories.trip_repo import ActivityRepository, TripDayRepository, TripRepository
from app.schemas.trip_api import (
    ActivityResponse,
    TripDayResponse,
    TripDetailResponse,
    TripListItemResponse,
)

router = APIRouter(prefix="/api/trips", tags=["trips"])


@router.get("/", response_model=List[TripListItemResponse])
async def list_trips(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: UserProfile = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    trip_repo = TripRepository(session)
    trips = await trip_repo.get_by_user(current_user.id, skip=skip, limit=limit)

    return [
        TripListItemResponse(
            id=trip.id,
            user_id=trip.user_id,
            title=trip.title,
            summary=trip.summary,
            destination=trip.destination,
            days=trip.days,
            budget=trip.budget,
            travel_style=trip.travel_style,
            companions=trip.companions,
            time_of_year=trip.time_of_year,
            total_budget_min=trip.total_budget_min,
            total_budget_max=trip.total_budget_max,
            is_public=trip.is_public,
            view_count=trip.view_count,
            created_from_template_id=trip.created_from_template_id,
            created_at=trip.created_at,
            updated_at=trip.updated_at,
        )
        for trip in trips
    ]


@router.get("/{trip_id}", response_model=TripDetailResponse)
async def get_trip_detail(
    trip_id: int,
    current_user: UserProfile = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    trip_repo = TripRepository(session)
    day_repo = TripDayRepository(session)
    activity_repo = ActivityRepository(session)

    trip = await trip_repo.get(trip_id)
    if trip is None or trip.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Trip not found")

    trip_days = await day_repo.get_by_trip(trip_id)
    day_responses: List[TripDayResponse] = []

    for trip_day in trip_days:
        if trip_day.id is None:
            continue
        activities = await activity_repo.get_by_trip_day(trip_day.id)
        activity_responses = [
            ActivityResponse(
                id=activity.id,
                trip_day_id=activity.trip_day_id,
                name=activity.name,
                description=activity.description,
                category=activity.category,
                place_id=activity.place_id,
                latitude=activity.latitude,
                longitude=activity.longitude,
                address=activity.address,
                duration_minutes=activity.duration_minutes,
                cost_min=activity.cost_min,
                cost_max=activity.cost_max,
                start_time=activity.start_time,
                end_time=activity.end_time,
                booking_required=activity.booking_required,
                booking_url=activity.booking_url,
                notes=activity.notes,
                sort_order=activity.sort_order,
                created_at=activity.created_at,
            )
            for activity in activities
        ]

        day_responses.append(
            TripDayResponse(
                id=trip_day.id,
                trip_id=trip_day.trip_id,
                day_number=trip_day.day_number,
                title=trip_day.title,
                trip_date=trip_day.trip_date,
                total_cost_min=trip_day.total_cost_min,
                total_cost_max=trip_day.total_cost_max,
                created_at=trip_day.created_at,
                activities=activity_responses,
            )
        )

    return TripDetailResponse(
        id=trip.id,
        user_id=trip.user_id,
        title=trip.title,
        summary=trip.summary,
        destination=trip.destination,
        days=trip.days,
        budget=trip.budget,
        travel_style=trip.travel_style,
        companions=trip.companions,
        time_of_year=trip.time_of_year,
        total_budget_min=trip.total_budget_min,
        total_budget_max=trip.total_budget_max,
        is_public=trip.is_public,
        view_count=trip.view_count,
        created_from_template_id=trip.created_from_template_id,
        created_at=trip.created_at,
        updated_at=trip.updated_at,
        trip_days=day_responses,
    )
