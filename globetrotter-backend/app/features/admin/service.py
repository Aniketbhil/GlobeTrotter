from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from sqlalchemy import func, literal_column, or_
from sqlalchemy.orm import Session

from app.common.exceptions import NotFoundError
from app.features.activities.models import Activity
from app.features.admin.schemas import (
    AdminStatsOverview,
    AdminTopActivityEntry,
    AdminTopCityEntry,
    AdminUserListParams,
    AdminUserListResponse,
    AdminUserSummary,
)
from app.features.auth.models import User
from app.features.cities.models import City
from app.features.stops.models import Stop
from app.features.trip_activities.models import TripActivity
from app.features.trips.models import Trip
from app.features.trips.schemas import TripResponse
from app.features.trips.service import (
    build_trip_response as build_trip_response_service,
)


def get_stats_overview(db: Session, now: datetime | None = None) -> AdminStatsOverview:
    current_time = now if now is not None else datetime.now(UTC)
    thirty_days_ago = current_time - timedelta(days=30)

    total_users = db.query(func.count(User.id)).scalar() or 0
    total_trips = db.query(func.count(Trip.id)).scalar() or 0
    total_stops = db.query(func.count(Stop.id)).scalar() or 0
    total_scheduled_activities = db.query(func.count(TripActivity.id)).scalar() or 0

    trips_created_last_30_days = (
        db.query(func.count(Trip.id))
        .filter(Trip.created_at >= thirty_days_ago)
        .scalar()
        or 0
    )

    # Active users signal: users who created or updated at least one trip in the last 30 days.
    active_users_last_30_days = (
        db.query(func.count(func.distinct(Trip.user_id)))
        .filter(
            or_(
                Trip.created_at >= thirty_days_ago,
                Trip.updated_at >= thirty_days_ago,
            )
        )
        .scalar()
        or 0
    )

    return AdminStatsOverview(
        total_users=total_users,
        total_trips=total_trips,
        total_stops=total_stops,
        total_scheduled_activities=total_scheduled_activities,
        trips_created_last_30_days=trips_created_last_30_days,
        active_users_last_30_days=active_users_last_30_days,
    )


def get_top_cities(db: Session, limit: int = 10) -> list[AdminTopCityEntry]:
    capped_limit = min(limit, 50)
    results = (
        db.query(
            City.id,
            City.name,
            City.country,
            func.count(Stop.id).label("stop_count"),
        )
        .join(Stop, Stop.city_id == City.id)
        .group_by(City.id, City.name, City.country)
        .order_by(func.count(Stop.id).desc())
        .limit(capped_limit)
        .all()
    )

    return [
        AdminTopCityEntry(city_id=r[0], name=r[1], country=r[2], stop_count=r[3])
        for r in results
    ]


def get_top_activities(db: Session, limit: int = 10) -> list[AdminTopActivityEntry]:
    capped_limit = min(limit, 50)
    results = (
        db.query(
            Activity.id,
            Activity.name,
            City.name.label("city_name"),
            func.count(TripActivity.id).label("scheduled_count"),
        )
        .join(TripActivity, TripActivity.activity_id == Activity.id)
        .join(City, Activity.city_id == City.id)
        .group_by(Activity.id, Activity.name, City.name)
        .order_by(func.count(TripActivity.id).desc())
        .limit(capped_limit)
        .all()
    )

    return [
        AdminTopActivityEntry(
            activity_id=r[0], name=r[1], city_name=r[2], scheduled_count=r[3]
        )
        for r in results
    ]


def list_users(db: Session, params: AdminUserListParams) -> AdminUserListResponse:
    trip_count_sub = (
        db.query(Trip.user_id, func.count(Trip.id).label("cnt"))
        .group_by(Trip.user_id)
        .subquery()
    )

    query = db.query(
        User, func.coalesce(trip_count_sub.c.cnt, 0).label("trip_count")
    ).outerjoin(trip_count_sub, User.id == trip_count_sub.c.user_id)

    if params.search and params.search.strip():
        s = f"%{params.search.strip()}%"
        query = query.filter(
            or_(
                User.first_name.ilike(s),
                User.last_name.ilike(s),
                User.email.ilike(s),
            )
        )

    if params.sort_by == "email":
        query = query.order_by(User.email.asc())
    elif params.sort_by == "trip_count":
        query = query.order_by(
            literal_column("trip_count").desc(), User.created_at.desc()
        )
    else:
        query = query.order_by(User.created_at.desc())

    total = query.count()
    rows = (
        query.offset((params.page - 1) * params.page_size).limit(params.page_size).all()
    )

    items = [
        AdminUserSummary(
            id=u.id,
            email=u.email,
            first_name=u.first_name,
            last_name=u.last_name,
            phone_number=u.phone_number,
            is_admin=u.is_admin,
            created_at=u.created_at,
            trip_count=cnt,
        )
        for u, cnt in rows
    ]

    return AdminUserListResponse(
        items=items, total=total, page=params.page, page_size=params.page_size
    )


def get_user_or_404(db: Session, user_id: UUID) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError(f"User '{user_id}' not found")
    return user


def list_user_trips(
    db: Session, user_id: UUID, today: date | None = None
) -> list[TripResponse]:
    # Intentionally isolated admin ownership bypass — direct query against Trip for target user_id.
    get_user_or_404(db, user_id)
    trips = (
        db.query(Trip)
        .filter(Trip.user_id == user_id)
        .order_by(Trip.start_date.asc())
        .all()
    )

    return [build_trip_response_service(t, today) for t in trips]
