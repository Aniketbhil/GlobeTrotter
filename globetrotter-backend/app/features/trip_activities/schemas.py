from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.features.activities.schemas import ActivityResponse


class TripActivityCreate(BaseModel):
    activity_id: UUID
    scheduled_date: date
    scheduled_time: time | None = None
    cost_override: Decimal | float | None = None


class TripActivityUpdate(BaseModel):
    scheduled_date: date | None = None
    scheduled_time: time | None = None
    cost_override: Decimal | float | None = None


class TripActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    stop_id: UUID
    scheduled_date: date
    scheduled_time: time | None = None
    effective_cost: Decimal | float
    cost_override: Decimal | float | None = None
    activity: ActivityResponse
    order_index: int
    created_at: datetime


class TripActivityReorderRequest(BaseModel):
    scheduled_date: date
    ordered_ids: list[UUID]
