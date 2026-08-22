from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin_user, get_db
from app.features.admin.schemas import (
    AdminStatsOverview,
    AdminTopActivityEntry,
    AdminTopCityEntry,
    AdminUserListParams,
    AdminUserListResponse,
)
from app.features.admin.service import (
    get_stats_overview,
    get_top_activities,
    get_top_cities,
    list_user_trips,
    list_users,
)
from app.features.auth.models import User
from app.features.trips.schemas import TripResponse

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/stats/overview", response_model=AdminStatsOverview)
def get_stats_overview_endpoint(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    return get_stats_overview(db)


@router.get("/stats/top-cities", response_model=list[AdminTopCityEntry])
def get_top_cities_endpoint(
    limit: int = Query(10, ge=1, le=50, description="Limit max 50"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    return get_top_cities(db, limit)


@router.get("/stats/top-activities", response_model=list[AdminTopActivityEntry])
def get_top_activities_endpoint(
    limit: int = Query(10, ge=1, le=50, description="Limit max 50"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    return get_top_activities(db, limit)


@router.get("/users", response_model=AdminUserListResponse)
def list_users_endpoint(
    search: str | None = Query(None, description="Search by name or email"),
    sort_by: Literal["created_at", "email", "trip_count"] = Query(
        "created_at", description="Sort order"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    params = AdminUserListParams(
        search=search, sort_by=sort_by, page=page, page_size=page_size
    )
    return list_users(db, params)


@router.get("/users/{user_id}/trips", response_model=list[TripResponse])
def list_user_trips_endpoint(
    user_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    return list_user_trips(db, user_id)
