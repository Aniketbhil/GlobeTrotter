from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    country: str
    region: str | None = None
    cost_index: Decimal | float | None = None
    popularity_score: int
    image_url: str | None = None
    created_at: datetime


class CityListParams(BaseModel):
    search: str | None = None
    country: str | None = None
    region: str | None = None
    sort_by: Literal["popularity", "name", "cost_index"] = "popularity"
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")


class CityCreate(BaseModel):
    name: str
    country: str
    region: str | None = None
    cost_index: Decimal | float | None = None
    popularity_score: int = 0
    image_url: str | None = None


class CityUpdate(BaseModel):
    name: str | None = None
    country: str | None = None
    region: str | None = None
    cost_index: Decimal | float | None = None
    popularity_score: int | None = None
    image_url: str | None = None


class PaginatedCityResponse(BaseModel):
    items: list[CityResponse]
    total: int
    page: int
    page_size: int
    pages: int
