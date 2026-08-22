from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator

from app.features.cities.schemas import CityResponse


class StopCreate(BaseModel):
    city_id: UUID
    start_date: date
    end_date: date
    budget_estimate: Decimal | float | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> "StopCreate":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be greater than or equal to start_date")
        return self


class StopUpdate(BaseModel):
    city_id: UUID | None = None
    start_date: date | None = None
    end_date: date | None = None
    budget_estimate: Decimal | float | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> "StopUpdate":
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise ValueError("end_date must be greater than or equal to start_date")
        return self


class StopResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    trip_id: UUID
    city_id: UUID
    city: CityResponse
    order_index: int
    start_date: date
    end_date: date
    budget_estimate: Decimal | float | None = None
    notes: str | None = None
    created_at: datetime


class StopReorderRequest(BaseModel):
    ordered_stop_ids: list[UUID]
