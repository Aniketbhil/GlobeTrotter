from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.common.exceptions import NotFoundError
from app.core.dependencies import get_current_user, get_db
from app.features.auth.models import User
from app.features.sharing.schemas import (
    CopyTripRequest,
    CopyTripResponse,
    PublicItineraryResponse,
    ShareResponse,
)
from app.features.sharing.service import (
    build_public_itinerary,
    copy_trip,
    get_public_share,
    publish_trip,
    unpublish_trip,
)
from app.features.trips.models import Trip
from app.features.trips.service import get_trip as get_trip_service

router = APIRouter(tags=["sharing"])


@router.post("/api/trips/{trip_id}/share", response_model=ShareResponse)
def publish_trip_endpoint(
    trip_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = get_trip_service(db, current_user, trip_id)
    return publish_trip(db, trip)


@router.delete("/api/trips/{trip_id}/share", response_model=ShareResponse)
def unpublish_trip_endpoint(
    trip_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = get_trip_service(db, current_user, trip_id)
    return unpublish_trip(db, trip)


@router.get("/api/public/itinerary/{slug}", response_model=PublicItineraryResponse)
def get_public_itinerary_endpoint(
    slug: str,
    db: Session = Depends(get_db),
):
    """Public read-only view for a shared trip itinerary. No login required."""
    share = get_public_share(db, slug)
    trip = db.query(Trip).filter(Trip.id == share.trip_id).first()
    if not trip:
        raise NotFoundError("Trip not found")
    return build_public_itinerary(db, trip)


@router.post(
    "/api/public/itinerary/{slug}/copy",
    response_model=CopyTripResponse,
    status_code=status.HTTP_201_CREATED,
)
def copy_public_itinerary_endpoint(
    slug: str,
    data: CopyTripRequest = CopyTripRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    share = get_public_share(db, slug)
    source_trip = db.query(Trip).filter(Trip.id == share.trip_id).first()
    if not source_trip:
        raise NotFoundError("Trip not found")
    return copy_trip(db, source_trip, current_user, data)
