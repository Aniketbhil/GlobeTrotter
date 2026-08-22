import math
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.common.exceptions import ConflictError, NotFoundError
from app.features.activities.models import Activity
from app.features.activities.schemas import (
    ActivityCreate,
    ActivityListParams,
    ActivityUpdate,
)
from app.features.cities.models import City
from app.features.trip_activities.models import TripActivity


def search_activities(
    db: Session, params: ActivityListParams
) -> tuple[list[Activity], int, int]:
    query = db.query(Activity)

    if params.search:
        search_pattern = f"%{params.search}%"
        query = query.filter(
            (Activity.name.ilike(search_pattern))
            | (Activity.description.ilike(search_pattern))
        )
    if params.city_id:
        query = query.filter(Activity.city_id == params.city_id)
    if params.type:
        query = query.filter(Activity.type == params.type)
    if params.max_cost is not None:
        query = query.filter(Activity.cost <= params.max_cost)
    if params.max_duration_mins is not None:
        query = query.filter(Activity.duration_mins <= params.max_duration_mins)

    total = query.count()

    if params.sort_by == "cost":
        query = query.order_by(Activity.cost.asc())
    elif params.sort_by == "duration":
        query = query.order_by(Activity.duration_mins.asc().nulls_last())
    else:  # default "name"
        query = query.order_by(Activity.name.asc())

    offset = (params.page - 1) * params.page_size
    items = query.offset(offset).limit(params.page_size).all()
    pages = math.ceil(total / params.page_size) if total > 0 else 0

    return items, total, pages


def get_activity(db: Session, activity_id: UUID) -> Activity:
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise NotFoundError("Activity not found")
    return activity


def create_activity(db: Session, data: ActivityCreate) -> Activity:
    city = db.query(City).filter(City.id == data.city_id).first()
    if not city:
        raise NotFoundError("City not found")

    activity = Activity(
        city_id=data.city_id,
        name=data.name,
        type=data.type,
        cost=data.cost,
        duration_mins=data.duration_mins,
        description=data.description,
        image_url=data.image_url,
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


def update_activity(db: Session, activity_id: UUID, data: ActivityUpdate) -> Activity:
    activity = get_activity(db, activity_id)
    update_data = data.model_dump(exclude_unset=True)

    if "city_id" in update_data:
        city = db.query(City).filter(City.id == update_data["city_id"]).first()
        if not city:
            raise NotFoundError("City not found")

    for field, value in update_data.items():
        setattr(activity, field, value)

    db.commit()
    db.refresh(activity)
    return activity


def delete_activity(db: Session, activity_id: UUID) -> None:
    activity = get_activity(db, activity_id)

    trip_activity_count = (
        db.query(TripActivity).filter(TripActivity.activity_id == activity_id).count()
    )
    if trip_activity_count > 0:
        raise ConflictError("Cannot delete activity that is scheduled in trip stops")

    try:
        db.delete(activity)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise ConflictError(
            "Cannot delete activity referenced by other resources"
        ) from e
