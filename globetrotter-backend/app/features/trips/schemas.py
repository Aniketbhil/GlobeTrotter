from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TripCreate(BaseModel):
    name: str
    description: str | None = None
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_dates(self) -> "TripCreate":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be greater than or equal to start_date")
        return self


class TripUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> "TripUpdate":
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise ValueError("end_date must be greater than or equal to start_date")
        return self


class TripResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None = None
    start_date: date
    end_date: date
    cover_photo_url: str | None = None
    status: Literal["upcoming", "ongoing", "completed"]
    created_at: datetime


class TripListParams(BaseModel):
    search: str | None = None
    status: Literal["upcoming", "ongoing", "completed"] | None = None
    group_by: Literal["status"] | None = None
    sort_by: Literal["start_date", "name", "created_at"] = "start_date"
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")


class TripListFlat(BaseModel):
    items: list[TripResponse]
    total: int
    page: int
    page_size: int
    pages: int


class TripListGrouped(BaseModel):
    ongoing: list[TripResponse]
    upcoming: list[TripResponse]
    completed: list[TripResponse]
