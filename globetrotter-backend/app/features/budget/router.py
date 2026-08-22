from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.features.auth.models import User
from app.features.budget.schemas import (
    BudgetResponse,
    StopBudgetOverrideResponse,
    StopBudgetOverrideUpsert,
)
from app.features.budget.service import (
    build_trip_budget,
    upsert_stop_budget_override,
)
from app.features.stops.service import get_stop as get_stop_service
from app.features.trips.service import get_trip as get_trip_service

router = APIRouter(tags=["budget"])


@router.put(
    "/api/trips/{trip_id}/stops/{stop_id}/budget-override",
    response_model=StopBudgetOverrideResponse,
)
def upsert_budget_override_endpoint(
    trip_id: UUID,
    stop_id: UUID,
    data: StopBudgetOverrideUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = get_trip_service(db, current_user, trip_id)
    stop = get_stop_service(db, trip, stop_id)
    return upsert_stop_budget_override(db, stop, data)


@router.get("/api/trips/{trip_id}/budget", response_model=BudgetResponse)
def get_trip_budget_endpoint(
    trip_id: UUID,
    daily_budget_threshold: float | None = Query(
        None, description="Optional daily budget threshold"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = get_trip_service(db, current_user, trip_id)
    return build_trip_budget(db, trip, daily_budget_threshold)
