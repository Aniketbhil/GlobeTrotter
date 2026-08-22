from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.features.cities.schemas import CityResponse
from app.features.trips.schemas import TripResponse

# Alias for CopyTripResponse as required
CopyTripResponse = TripResponse


class ShareResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    trip_id: UUID
    slug: str
    is_public: bool
    share_url: str
    created_at: datetime


class PublicActivityEntry(BaseModel):
    name: str
    type: str
    description: str | None = None
    image_url: str | None = None
    duration_mins: int | None = None
    scheduled_date: date
    scheduled_time: time | None = None


class PublicStopEntry(BaseModel):
    city: CityResponse
    start_date: date
    end_date: date
    notes: str | None = None
    activities: list[PublicActivityEntry]


class PublicItineraryResponse(BaseModel):
    trip_name: str
    start_date: date
    end_date: date
    cover_photo_url: str | None = None
    stops: list[PublicStopEntry]


class CopyTripRequest(BaseModel):
    name: str | None = None
