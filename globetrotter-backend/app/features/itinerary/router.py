from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.features.auth.models import User
from app.features.itinerary.schemas import CalendarResponse, ItineraryResponse
from app.features.itinerary.service import (
    build_month_calendar,
    build_trip_itinerary,
)
from app.features.trips.service import get_trip as get_trip_service

router = APIRouter(tags=["itinerary"])


@router.get("/api/trips/calendar", response_model=CalendarResponse)
def get_month_calendar_endpoint(
    year: int | None = Query(None, description="Year (e.g. 2026)"),
    month: int | None = Query(None, ge=1, le=12, description="Month (1-12)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.now(UTC).date()
    target_year = year if year is not None else now.year
    target_month = month if month is not None else now.month

    return build_month_calendar(db, current_user, target_year, target_month)


@router.get("/api/trips/{trip_id}/itinerary", response_model=ItineraryResponse)
def get_trip_itinerary_endpoint(
    trip_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = get_trip_service(db, current_user, trip_id)
    return build_trip_itinerary(db, trip)
