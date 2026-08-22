from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.common.exceptions import (
    BadRequestError,
    NotFoundError,
    UnprocessableEntityError,
)
from app.features.cities.service import get_city as get_city_service
from app.features.stops.models import Stop
from app.features.stops.schemas import (
    StopCreate,
    StopReorderRequest,
    StopUpdate,
)
from app.features.trips.models import Trip


def list_stops(db: Session, trip: Trip) -> list[Stop]:
    return (
        db.query(Stop)
        .options(joinedload(Stop.city))
        .filter(Stop.trip_id == trip.id)
        .order_by(Stop.order_index.asc())
        .all()
    )


def create_stop(db: Session, trip: Trip, data: StopCreate) -> Stop:
    get_city_service(db, data.city_id)

    max_order = (
        db.query(func.max(Stop.order_index)).filter(Stop.trip_id == trip.id).scalar()
    )
    next_order = (max_order or 0) + 1

    # TODO: Product decision — confirm if a stop's date range falling outside trip's start_date/end_date should auto-expand trip's date range.

    stop = Stop(
        trip_id=trip.id,
        city_id=data.city_id,
        order_index=next_order,
        start_date=data.start_date,
        end_date=data.end_date,
        budget_estimate=data.budget_estimate,
        notes=data.notes,
    )
    db.add(stop)
    db.commit()
    db.refresh(stop)

    return get_stop(db, trip, stop.id)


def get_stop(db: Session, trip: Trip, stop_id: UUID) -> Stop:
    stop = (
        db.query(Stop)
        .options(joinedload(Stop.city))
        .filter(Stop.id == stop_id, Stop.trip_id == trip.id)
        .first()
    )
    if not stop:
        raise NotFoundError("Stop not found")
    return stop


def update_stop(db: Session, trip: Trip, stop_id: UUID, data: StopUpdate) -> Stop:
    stop = get_stop(db, trip, stop_id)
    update_data = data.model_dump(exclude_unset=True)

    if "city_id" in update_data:
        get_city_service(db, update_data["city_id"])

    new_start = update_data.get("start_date", stop.start_date)
    new_end = update_data.get("end_date", stop.end_date)
    if new_end < new_start:
        raise BadRequestError("end_date must be greater than or equal to start_date")

    for field, value in update_data.items():
        setattr(stop, field, value)

    db.commit()
    db.refresh(stop)
    return get_stop(db, trip, stop.id)


def delete_stop(db: Session, trip: Trip, stop_id: UUID) -> None:
    stop = get_stop(db, trip, stop_id)
    db.delete(stop)
    db.commit()


def reorder_stops(db: Session, trip: Trip, data: StopReorderRequest) -> list[Stop]:
    existing_stops = (
        db.query(Stop)
        .options(joinedload(Stop.city))
        .filter(Stop.trip_id == trip.id)
        .all()
    )
    existing_map = {s.id: s for s in existing_stops}

    if set(data.ordered_stop_ids) != set(existing_map.keys()) or len(
        data.ordered_stop_ids
    ) != len(existing_stops):
        raise UnprocessableEntityError(
            "ordered_stop_ids must contain exact same stop IDs as current trip stops"
        )

    for idx, s in enumerate(existing_stops):
        s.order_index = -(idx + 1)
    db.flush()

    for new_idx, stop_id in enumerate(data.ordered_stop_ids, start=1):
        existing_map[stop_id].order_index = new_idx

    db.commit()
    return list_stops(db, trip)
