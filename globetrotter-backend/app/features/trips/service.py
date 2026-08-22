import logging
import math
from datetime import UTC, date, datetime
from typing import Any
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.common.exceptions import BadRequestError, NotFoundError
from app.core.storage import StorageBackend
from app.features.auth.models import User
from app.features.trips.models import Trip
from app.features.trips.schemas import (
    TripCreate,
    TripListFlat,
    TripListGrouped,
    TripListParams,
    TripResponse,
    TripUpdate,
)

logger = logging.getLogger(__name__)


def compute_status(trip: Any, today: date | None = None) -> str:
    current_date = today or datetime.now(UTC).date()
    if hasattr(trip, "start_date"):
        start = trip.start_date
        end = trip.end_date
    else:
        start = trip["start_date"]
        end = trip["end_date"]

    if current_date < start:
        return "upcoming"
    if start <= current_date <= end:
        return "ongoing"
    return "completed"


def build_trip_response(trip: Trip, today: date | None = None) -> TripResponse:
    status_str = compute_status(trip, today)
    return TripResponse(
        id=trip.id,
        name=trip.name,
        description=trip.description,
        start_date=trip.start_date,
        end_date=trip.end_date,
        cover_photo_url=trip.cover_photo_url,
        status=status_str,
        created_at=trip.created_at,
    )


def create_trip(
    db: Session, user: User, data: TripCreate, today: date | None = None
) -> TripResponse:
    trip = Trip(
        user_id=user.id,
        name=data.name,
        description=data.description,
        start_date=data.start_date,
        end_date=data.end_date,
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return build_trip_response(trip, today)


def list_trips(
    db: Session, user: User, params: TripListParams, today: date | None = None
) -> TripListFlat | TripListGrouped:
    query = db.query(Trip).filter(Trip.user_id == user.id)

    if params.search:
        query = query.filter(Trip.name.ilike(f"%{params.search}%"))

    if params.sort_by == "name":
        query = query.order_by(Trip.name.asc())
    elif params.sort_by == "created_at":
        query = query.order_by(Trip.created_at.desc())
    else:  # default "start_date"
        query = query.order_by(Trip.start_date.asc())

    all_trips = query.all()

    if params.group_by == "status":
        ongoing_list = []
        upcoming_list = []
        completed_list = []

        for t in all_trips:
            resp = build_trip_response(t, today)
            if params.status and resp.status != params.status:
                continue
            if resp.status == "ongoing":
                ongoing_list.append(resp)
            elif resp.status == "upcoming":
                upcoming_list.append(resp)
            elif resp.status == "completed":
                completed_list.append(resp)

        return TripListGrouped(
            ongoing=ongoing_list,
            upcoming=upcoming_list,
            completed=completed_list,
        )

    all_responses = [build_trip_response(t, today) for t in all_trips]
    if params.status:
        all_responses = [r for r in all_responses if r.status == params.status]

    total = len(all_responses)
    offset = (params.page - 1) * params.page_size
    items = all_responses[offset : offset + params.page_size]
    pages = math.ceil(total / params.page_size) if total > 0 else 0

    return TripListFlat(
        items=items,
        total=total,
        page=params.page,
        page_size=params.page_size,
        pages=pages,
    )


def get_trip(db: Session, user: User, trip_id: UUID) -> Trip:
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user.id).first()
    if not trip:
        raise NotFoundError("Trip not found")
    return trip


def get_trip_response(
    db: Session, user: User, trip_id: UUID, today: date | None = None
) -> TripResponse:
    trip = get_trip(db, user, trip_id)
    return build_trip_response(trip, today)


def update_trip(
    db: Session,
    user: User,
    trip_id: UUID,
    data: TripUpdate,
    today: date | None = None,
) -> TripResponse:
    trip = get_trip(db, user, trip_id)
    update_data = data.model_dump(exclude_unset=True)

    new_start = update_data.get("start_date", trip.start_date)
    new_end = update_data.get("end_date", trip.end_date)
    if new_end < new_start:
        raise BadRequestError("end_date must be greater than or equal to start_date")

    for field, value in update_data.items():
        setattr(trip, field, value)

    db.commit()
    db.refresh(trip)
    return build_trip_response(trip, today)


def delete_trip(db: Session, user: User, trip_id: UUID) -> None:
    trip = get_trip(db, user, trip_id)

    # TODO: Cascade deletion to Stops and TripActivities once those slices exist

    db.delete(trip)
    db.commit()


async def update_trip_cover_photo(
    db: Session,
    user: User,
    trip_id: UUID,
    storage: StorageBackend,
    file: UploadFile,
    today: date | None = None,
) -> TripResponse:
    trip = get_trip(db, user, trip_id)
    relative_path = await storage.save(file, subfolder="trip_covers")
    public_url = storage.url_for(relative_path)

    if trip.cover_photo_url:
        try:
            storage.delete(trip.cover_photo_url)
        except Exception as e:  # noqa: BLE001
            logger.warning("Could not delete old trip cover photo: %s", e)

    trip.cover_photo_url = public_url
    db.commit()
    db.refresh(trip)
    return build_trip_response(trip, today)


def delete_trip_cover_photo(
    db: Session,
    user: User,
    trip_id: UUID,
    storage: StorageBackend,
    today: date | None = None,
) -> TripResponse:
    trip = get_trip(db, user, trip_id)

    if trip.cover_photo_url:
        try:
            storage.delete(trip.cover_photo_url)
        except Exception as e:  # noqa: BLE001
            logger.warning("Could not delete trip cover photo: %s", e)
        trip.cover_photo_url = None
        db.commit()
        db.refresh(trip)

    return build_trip_response(trip, today)
