from datetime import date
from uuid import UUID

from pydantic import BaseModel

from app.features.cities.schemas import CityResponse
from app.features.trip_activities.schemas import TripActivityResponse


class ItineraryDayEntry(BaseModel):
    date: date
    stop_id: UUID
    city: CityResponse
    activities: list[TripActivityResponse]
    day_total_cost: float


class ItineraryResponse(BaseModel):
    trip_id: UUID
    trip_name: str
    start_date: date
    end_date: date
    days: list[ItineraryDayEntry]
    trip_total_cost: float


class CalendarTripEntry(BaseModel):
    trip_id: UUID
    name: str
    start_date: date
    end_date: date
    status: str


class CalendarResponse(BaseModel):
    year: int
    month: int
    trips: list[CalendarTripEntry]
