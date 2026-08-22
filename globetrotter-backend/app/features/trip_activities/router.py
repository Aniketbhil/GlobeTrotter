from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.features.auth.models import User
from app.features.stops.models import Stop
from app.features.stops.service import get_stop as get_stop_service
from app.features.trip_activities.schemas import (
    TripActivityCreate,
    TripActivityReorderRequest,
    TripActivityResponse,
    TripActivityUpdate,
)
from app.features.trip_activities.service import (
    add_trip_activity,
    delete_trip_activity,
    get_trip_activity_response,
    list_trip_activities_grouped_by_day,
    reorder_trip_activities,
    update_trip_activity,
)
from app.features.trips.service import get_trip as get_trip_service

router = APIRouter(
    prefix="/api/trips/{trip_id}/stops/{stop_id}/activities",
    tags=["trip-activities"],
)


def resolve_stop(
    trip_id: UUID,
    stop_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Stop:
    trip = get_trip_service(db, current_user, trip_id)
    return get_stop_service(db, trip, stop_id)


@router.post(
    "", response_model=TripActivityResponse, status_code=status.HTTP_201_CREATED
)
@router.post(
    "/",
    response_model=TripActivityResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def create_trip_activity_endpoint(
    data: TripActivityCreate,
    db: Session = Depends(get_db),
    stop: Stop = Depends(resolve_stop),
):
    return add_trip_activity(db, stop, data)


@router.get("", response_model=dict[str, list[TripActivityResponse]])
@router.get(
    "/",
    response_model=dict[str, list[TripActivityResponse]],
    include_in_schema=False,
)
def list_trip_activities_endpoint(
    db: Session = Depends(get_db), stop: Stop = Depends(resolve_stop)
):
    """Returns trip activities for this stop grouped by ISO date string in chronological order."""
    return list_trip_activities_grouped_by_day(db, stop)


@router.patch("/reorder", response_model=list[TripActivityResponse])
def reorder_trip_activities_endpoint(
    data: TripActivityReorderRequest,
    db: Session = Depends(get_db),
    stop: Stop = Depends(resolve_stop),
):
    return reorder_trip_activities(db, stop, data)


@router.get("/{trip_activity_id}", response_model=TripActivityResponse)
def get_trip_activity_endpoint(
    trip_activity_id: UUID,
    db: Session = Depends(get_db),
    stop: Stop = Depends(resolve_stop),
):
    return get_trip_activity_response(db, stop, trip_activity_id)


@router.patch("/{trip_activity_id}", response_model=TripActivityResponse)
def update_trip_activity_endpoint(
    trip_activity_id: UUID,
    data: TripActivityUpdate,
    db: Session = Depends(get_db),
    stop: Stop = Depends(resolve_stop),
):
    return update_trip_activity(db, stop, trip_activity_id, data)


@router.delete("/{trip_activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip_activity_endpoint(
    trip_activity_id: UUID,
    db: Session = Depends(get_db),
    stop: Stop = Depends(resolve_stop),
):
    delete_trip_activity(db, stop, trip_activity_id)
