from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.features.auth.models import User
from app.features.stops.schemas import (
    StopCreate,
    StopReorderRequest,
    StopResponse,
    StopUpdate,
)
from app.features.stops.service import (
    create_stop,
    delete_stop,
    get_stop,
    list_stops,
    reorder_stops,
    update_stop,
)
from app.features.trips.service import get_trip as get_trip_service

router = APIRouter(prefix="/api/trips/{trip_id}/stops", tags=["stops"])


@router.post("", response_model=StopResponse, status_code=status.HTTP_201_CREATED)
@router.post(
    "/",
    response_model=StopResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def create_stop_endpoint(
    trip_id: UUID,
    data: StopCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = get_trip_service(db, current_user, trip_id)
    return create_stop(db, trip, data)


@router.get("", response_model=list[StopResponse])
@router.get("/", response_model=list[StopResponse], include_in_schema=False)
def list_stops_endpoint(
    trip_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = get_trip_service(db, current_user, trip_id)
    return list_stops(db, trip)


@router.patch("/reorder", response_model=list[StopResponse])
def reorder_stops_endpoint(
    trip_id: UUID,
    data: StopReorderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = get_trip_service(db, current_user, trip_id)
    return reorder_stops(db, trip, data)


@router.get("/{stop_id}", response_model=StopResponse)
def get_stop_endpoint(
    trip_id: UUID,
    stop_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = get_trip_service(db, current_user, trip_id)
    return get_stop(db, trip, stop_id)


@router.patch("/{stop_id}", response_model=StopResponse)
def update_stop_endpoint(
    trip_id: UUID,
    stop_id: UUID,
    data: StopUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = get_trip_service(db, current_user, trip_id)
    return update_stop(db, trip, stop_id, data)


@router.delete("/{stop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stop_endpoint(
    trip_id: UUID,
    stop_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = get_trip_service(db, current_user, trip_id)
    delete_stop(db, trip, stop_id)
