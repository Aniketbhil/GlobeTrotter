from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.features.trips.schemas import TripResponse

# Alias TripResponse for admin user-trips response
AdminTripResponse = TripResponse


class AdminStatsOverview(BaseModel):
    total_users: int
    total_trips: int
    total_stops: int
    total_scheduled_activities: int
    trips_created_last_30_days: int
    active_users_last_30_days: int


class AdminTopCityEntry(BaseModel):
    city_id: UUID
    name: str
    country: str
    stop_count: int


class AdminTopActivityEntry(BaseModel):
    activity_id: UUID
    name: str
    city_name: str
    scheduled_count: int


class AdminUserListParams(BaseModel):
    search: str | None = None
    sort_by: Literal["created_at", "email", "trip_count"] = "created_at"
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class AdminUserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    first_name: str
    last_name: str
    phone_number: str | None = None
    is_admin: bool
    created_at: datetime
    trip_count: int


class AdminUserListResponse(BaseModel):
    items: list[AdminUserSummary]
    total: int
    page: int
    page_size: int
