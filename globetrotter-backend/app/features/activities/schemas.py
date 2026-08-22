from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.features.activities.models import ActivityType


class ActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    city_id: UUID
    name: str
    type: ActivityType
    cost: Decimal | float
    duration_mins: int | None = None
    description: str | None = None
    image_url: str | None = None
    created_at: datetime


class ActivityListParams(BaseModel):
    search: str | None = None
    city_id: UUID | None = None
    type: ActivityType | None = None
    max_cost: Decimal | float | None = None
    max_duration_mins: int | None = None
    sort_by: Literal["cost", "duration", "name"] = "name"
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")


class ActivityCreate(BaseModel):
    city_id: UUID
    name: str
    type: ActivityType
    cost: Decimal | float = 0
    duration_mins: int | None = None
    description: str | None = None
    image_url: str | None = None


class ActivityUpdate(BaseModel):
    city_id: UUID | None = None
    name: str | None = None
    type: ActivityType | None = None
    cost: Decimal | float | None = None
    duration_mins: int | None = None
    description: str | None = None
    image_url: str | None = None


class PaginatedActivityResponse(BaseModel):
    items: list[ActivityResponse]
    total: int
    page: int
    page_size: int
    pages: int
