from nanoid import generate
from sqlalchemy.orm import Session, joinedload

from app.common.exceptions import NotFoundError
from app.core.config import settings
from app.features.auth.models import User
from app.features.cities.schemas import CityResponse
from app.features.sharing.models import TripShare
from app.features.sharing.schemas import (
    CopyTripRequest,
    PublicActivityEntry,
    PublicItineraryResponse,
    PublicStopEntry,
    ShareResponse,
)
from app.features.stops.models import Stop
from app.features.trip_activities.models import TripActivity
from app.features.trips.models import Trip
from app.features.trips.schemas import TripResponse
from app.features.trips.service import (
    build_trip_response as build_trip_response_service,
)


def publish_trip(db: Session, trip: Trip) -> ShareResponse:
    share = db.query(TripShare).filter(TripShare.trip_id == trip.id).first()
    if not share:
        slug = generate(size=10)
        share = TripShare(trip_id=trip.id, slug=slug, is_public=True)
        db.add(share)
    else:
        share.is_public = True

    db.commit()
    db.refresh(share)

    share_url = f"{settings.PUBLIC_BASE_URL}/api/public/itinerary/{share.slug}"
    return ShareResponse(
        trip_id=share.trip_id,
        slug=share.slug,
        is_public=share.is_public,
        share_url=share_url,
        created_at=share.created_at,
    )


def unpublish_trip(db: Session, trip: Trip) -> ShareResponse:
    share = db.query(TripShare).filter(TripShare.trip_id == trip.id).first()
    if not share:
        raise NotFoundError("Trip has not been shared yet")

    share.is_public = False
    db.commit()
    db.refresh(share)

    share_url = f"{settings.PUBLIC_BASE_URL}/api/public/itinerary/{share.slug}"
    return ShareResponse(
        trip_id=share.trip_id,
        slug=share.slug,
        is_public=share.is_public,
        share_url=share_url,
        created_at=share.created_at,
    )


def get_public_share(db: Session, slug: str) -> TripShare:
    share = (
        db.query(TripShare)
        .filter(TripShare.slug == slug, TripShare.is_public.is_(True))
        .first()
    )
    if not share:
        raise NotFoundError("Shared itinerary not found")
    return share


def build_public_itinerary(db: Session, trip: Trip) -> PublicItineraryResponse:
    stops = (
        db.query(Stop)
        .options(joinedload(Stop.city))
        .filter(Stop.trip_id == trip.id)
        .order_by(Stop.order_index.asc())
        .all()
    )

    public_stops: list[PublicStopEntry] = []
    for s in stops:
        activities = (
            db.query(TripActivity)
            .options(joinedload(TripActivity.activity))
            .filter(TripActivity.stop_id == s.id)
            .order_by(TripActivity.scheduled_date.asc(), TripActivity.order_index.asc())
            .all()
        )

        act_entries = [
            PublicActivityEntry(
                name=a.activity.name,
                type=(
                    a.activity.type.value
                    if hasattr(a.activity.type, "value")
                    else str(a.activity.type)
                ),
                description=a.activity.description,
                image_url=a.activity.image_url,
                duration_mins=a.activity.duration_mins,
                scheduled_date=a.scheduled_date,
                scheduled_time=a.scheduled_time,
            )
            for a in activities
        ]

        public_stops.append(
            PublicStopEntry(
                city=CityResponse.model_validate(s.city),
                start_date=s.start_date,
                end_date=s.end_date,
                notes=s.notes,
                activities=act_entries,
            )
        )

    return PublicItineraryResponse(
        trip_name=trip.name,
        start_date=trip.start_date,
        end_date=trip.end_date,
        cover_photo_url=trip.cover_photo_url,
        stops=public_stops,
    )


def copy_trip(
    db: Session, source_trip: Trip, copier: User, data: CopyTripRequest
) -> TripResponse:
    new_name = (
        data.name.strip()
        if (data.name and data.name.strip())
        else f"Copy of {source_trip.name}"
    )

    new_trip = Trip(
        user_id=copier.id,
        name=new_name,
        description=source_trip.description,
        start_date=source_trip.start_date,
        end_date=source_trip.end_date,
        cover_photo_url=source_trip.cover_photo_url,
    )
    db.add(new_trip)
    db.flush()

    # Product decision: Do NOT copy budget_estimate or StopBudgetOverride onto copied stops — those are the original owner's manual financial estimates.
    source_stops = (
        db.query(Stop)
        .filter(Stop.trip_id == source_trip.id)
        .order_by(Stop.order_index.asc())
        .all()
    )

    for s_stop in source_stops:
        new_stop = Stop(
            trip_id=new_trip.id,
            city_id=s_stop.city_id,
            order_index=s_stop.order_index,
            start_date=s_stop.start_date,
            end_date=s_stop.end_date,
            budget_estimate=None,
            notes=s_stop.notes,
        )
        db.add(new_stop)
        db.flush()

        # Product decision: Do NOT copy cost_override onto copied TripActivity rows.
        source_tas = (
            db.query(TripActivity)
            .filter(TripActivity.stop_id == s_stop.id)
            .order_by(TripActivity.scheduled_date.asc(), TripActivity.order_index.asc())
            .all()
        )

        for s_ta in source_tas:
            new_ta = TripActivity(
                stop_id=new_stop.id,
                activity_id=s_ta.activity_id,
                scheduled_date=s_ta.scheduled_date,
                scheduled_time=s_ta.scheduled_time,
                cost_override=None,
                order_index=s_ta.order_index,
            )
            db.add(new_ta)

    db.commit()
    db.refresh(new_trip)

    return build_trip_response_service(new_trip)
