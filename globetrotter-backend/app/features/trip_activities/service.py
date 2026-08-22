from collections import defaultdict
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.common.exceptions import NotFoundError, UnprocessableEntityError
from app.features.activities.service import (
    get_activity as get_activity_service,
)
from app.features.stops.models import Stop
from app.features.trip_activities.models import TripActivity
from app.features.trip_activities.schemas import (
    TripActivityCreate,
    TripActivityReorderRequest,
    TripActivityResponse,
    TripActivityUpdate,
)


def build_trip_activity_response(ta: TripActivity) -> TripActivityResponse:
    eff_cost = ta.cost_override if ta.cost_override is not None else ta.activity.cost
    return TripActivityResponse(
        id=ta.id,
        stop_id=ta.stop_id,
        scheduled_date=ta.scheduled_date,
        scheduled_time=ta.scheduled_time,
        effective_cost=eff_cost,
        cost_override=ta.cost_override,
        activity=ta.activity,
        order_index=ta.order_index,
        created_at=ta.created_at,
    )


def list_trip_activities(db: Session, stop: Stop) -> list[TripActivity]:
    return (
        db.query(TripActivity)
        .options(joinedload(TripActivity.activity))
        .filter(TripActivity.stop_id == stop.id)
        .order_by(TripActivity.scheduled_date.asc(), TripActivity.order_index.asc())
        .all()
    )


def list_trip_activities_grouped_by_day(
    db: Session, stop: Stop
) -> dict[str, list[TripActivityResponse]]:
    activities = list_trip_activities(db, stop)
    grouped: dict[str, list[TripActivityResponse]] = defaultdict(list)

    for ta in activities:
        date_key = ta.scheduled_date.isoformat()
        grouped[date_key].append(build_trip_activity_response(ta))

    sorted_keys = sorted(grouped.keys())
    return {k: grouped[k] for k in sorted_keys}


def add_trip_activity(
    db: Session, stop: Stop, data: TripActivityCreate
) -> TripActivityResponse:
    get_activity_service(db, data.activity_id)

    if data.scheduled_date < stop.start_date or data.scheduled_date > stop.end_date:
        raise UnprocessableEntityError(
            f"scheduled_date {data.scheduled_date} must be within stop date range"
            f" [{stop.start_date}, {stop.end_date}]"
        )

    max_order = (
        db.query(func.max(TripActivity.order_index))
        .filter(
            TripActivity.stop_id == stop.id,
            TripActivity.scheduled_date == data.scheduled_date,
        )
        .scalar()
    )
    next_order = (max_order or 0) + 1

    ta = TripActivity(
        stop_id=stop.id,
        activity_id=data.activity_id,
        scheduled_date=data.scheduled_date,
        scheduled_time=data.scheduled_time,
        cost_override=data.cost_override,
        order_index=next_order,
    )
    db.add(ta)
    db.commit()
    db.refresh(ta)

    return get_trip_activity_response(db, stop, ta.id)


def get_trip_activity(db: Session, stop: Stop, trip_activity_id: UUID) -> TripActivity:
    ta = (
        db.query(TripActivity)
        .options(joinedload(TripActivity.activity))
        .filter(
            TripActivity.id == trip_activity_id,
            TripActivity.stop_id == stop.id,
        )
        .first()
    )
    if not ta:
        raise NotFoundError("TripActivity not found")
    return ta


def get_trip_activity_response(
    db: Session, stop: Stop, trip_activity_id: UUID
) -> TripActivityResponse:
    ta = get_trip_activity(db, stop, trip_activity_id)
    return build_trip_activity_response(ta)


def update_trip_activity(
    db: Session, stop: Stop, trip_activity_id: UUID, data: TripActivityUpdate
) -> TripActivityResponse:
    ta = get_trip_activity(db, stop, trip_activity_id)
    update_data = data.model_dump(exclude_unset=True)

    if (
        "scheduled_date" in update_data
        and update_data["scheduled_date"] != ta.scheduled_date
    ):
        new_date = update_data["scheduled_date"]
        if new_date < stop.start_date or new_date > stop.end_date:
            raise UnprocessableEntityError(
                f"scheduled_date {new_date} must be within stop date range"
                f" [{stop.start_date}, {stop.end_date}]"
            )
        max_order = (
            db.query(func.max(TripActivity.order_index))
            .filter(
                TripActivity.stop_id == stop.id,
                TripActivity.scheduled_date == new_date,
            )
            .scalar()
        )
        update_data["order_index"] = (max_order or 0) + 1

    for field, value in update_data.items():
        setattr(ta, field, value)

    db.commit()
    db.refresh(ta)
    return get_trip_activity_response(db, stop, ta.id)


def delete_trip_activity(db: Session, stop: Stop, trip_activity_id: UUID) -> None:
    ta = get_trip_activity(db, stop, trip_activity_id)
    db.delete(ta)
    db.commit()


def reorder_trip_activities(
    db: Session, stop: Stop, data: TripActivityReorderRequest
) -> list[TripActivityResponse]:
    entries = (
        db.query(TripActivity)
        .options(joinedload(TripActivity.activity))
        .filter(
            TripActivity.stop_id == stop.id,
            TripActivity.scheduled_date == data.scheduled_date,
        )
        .all()
    )
    entry_map = {e.id: e for e in entries}

    if set(data.ordered_ids) != set(entry_map.keys()) or len(data.ordered_ids) != len(
        entries
    ):
        raise UnprocessableEntityError(
            "ordered_ids must contain exact same trip activity IDs scheduled"
            " for this date"
        )

    for idx, e in enumerate(entries):
        e.order_index = -(idx + 1)
    db.flush()

    for new_idx, ta_id in enumerate(data.ordered_ids, start=1):
        entry_map[ta_id].order_index = new_idx

    db.commit()

    reordered = (
        db.query(TripActivity)
        .options(joinedload(TripActivity.activity))
        .filter(
            TripActivity.stop_id == stop.id,
            TripActivity.scheduled_date == data.scheduled_date,
        )
        .order_by(TripActivity.order_index.asc())
        .all()
    )

    return [build_trip_activity_response(e) for e in reordered]
