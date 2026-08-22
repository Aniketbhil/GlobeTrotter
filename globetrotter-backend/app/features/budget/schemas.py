from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.features.cities.schemas import CityResponse


class StopBudgetOverrideUpsert(BaseModel):
    transport_cost_override: float | None = None
    stay_cost_override: float | None = None


class StopBudgetOverrideResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    stop_id: UUID
    transport_cost_override: float | None = None
    stay_cost_override: float | None = None
    updated_at: datetime


class StopBudgetBreakdown(BaseModel):
    stop_id: UUID
    city: CityResponse
    nights: int
    transport_cost: float
    transport_is_override: bool
    stay_cost: float
    stay_is_override: bool
    meal_cost: float
    activity_cost: float
    stop_total: float


class DayBudgetEntry(BaseModel):
    date: date
    activity_cost: float
    is_overbudget: bool | None = None


class BudgetCategoryTotals(BaseModel):
    transport: float
    stay: float
    meals: float
    activities: float


class BudgetResponse(BaseModel):
    trip_id: UUID
    trip_name: str
    stops: list[StopBudgetBreakdown]
    days: list[DayBudgetEntry]
    category_totals: BudgetCategoryTotals
    trip_total_cost: float
    daily_budget_threshold: float | None = None
    overbudget_day_count: int
