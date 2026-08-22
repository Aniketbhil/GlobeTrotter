import calendar
from datetime import date as date_type
from datetime import timedelta

from sqlalchemy.orm import Session

from app.features.auth.models import User
from app.features.cities.schemas import CityResponse
from app.features.itinerary.schemas import (
    CalendarResponse,
    CalendarTripEntry,
    ItineraryDayEntry,
    ItineraryResponse,
)
from app.features.stops.service import list_stops as list_stops_service
from app.features.trip_activities.service import (
    list_trip_activities_grouped_by_day,
)
from app.features.trips.models import Trip
from app.features.trips.service import compute_status as compute_status_service


def build_trip_itinerary(
    db: Session, trip: Trip, today: date_type | None = None
) -> ItineraryResponse:
    stops = list_stops_service(db, trip)
    days_list: list[ItineraryDayEntry] = []

    for stop in stops:
        grouped = list_trip_activities_grouped_by_day(db, stop)
        curr = stop.start_date
        while curr <= stop.end_date:
            date_str = curr.isoformat()
            acts = grouped.get(date_str, [])
            day_cost = sum(float(a.effective_cost) for a in acts)

            city_resp = CityResponse.model_validate(stop.city)
            days_list.append(
                ItineraryDayEntry(
                    date=curr,
                    stop_id=stop.id,
                    city=city_resp,
                    activities=acts,
                    day_total_cost=day_cost,
                )
            )
            curr += timedelta(days=1)

    # TODO: Product decision — if a later stop's dates overlap an earlier stop's, do not deduplicate or merge; emit both in stop order_index order.

    trip_total_cost = sum(d.day_total_cost for d in days_list)

    return ItineraryResponse(
        trip_id=trip.id,
        trip_name=trip.name,
        start_date=trip.start_date,
        end_date=trip.end_date,
        days=days_list,
        trip_total_cost=trip_total_cost,
    )


def build_month_calendar(
    db: Session,
    user: User,
    year: int,
    month: int,
    today: date_type | None = None,
) -> CalendarResponse:
    month_start = date_type(year, month, 1)
    _, num_days = calendar.monthrange(year, month)
    month_end = date_type(year, month, num_days)

    trips = (
        db.query(Trip)
        .filter(
            Trip.user_id == user.id,
            Trip.start_date <= month_end,
            Trip.end_date >= month_start,
        )
        .order_by(Trip.start_date.asc())
        .all()
    )

    calendar_entries: list[CalendarTripEntry] = []
    for t in trips:
        status_str = compute_status_service(t, today)
        calendar_entries.append(
            CalendarTripEntry(
                trip_id=t.id,
                name=t.name,
                start_date=t.start_date,
                end_date=t.end_date,
                status=status_str,
            )
        )

    return CalendarResponse(year=year, month=month, trips=calendar_entries)
