from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.storage import StorageBackend, get_storage
from app.features.auth.models import User
from app.features.trips.schemas import (
    TripCreate,
    TripListFlat,
    TripListGrouped,
    TripListParams,
    TripResponse,
    TripUpdate,
)
from app.features.trips.service import (
    create_trip,
    delete_trip,
    delete_trip_cover_photo,
    get_trip_response,
    list_trips,
    update_trip,
    update_trip_cover_photo,
)

# NOTE: Dashboard's "Top Regional Selections" / recommended destinations strip is
# backed by GET /api/cities?sort_by=popularity in the cities slice.

router = APIRouter(prefix="/api/trips", tags=["trips"])


@router.post("", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
@router.post(
    "/",
    response_model=TripResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def create_trip_endpoint(
    data: TripCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_trip(db, current_user, data)


@router.get("", response_model=TripListFlat | TripListGrouped)
@router.get(
    "/",
    response_model=TripListFlat | TripListGrouped,
    include_in_schema=False,
)
def list_trips_endpoint(
    params: TripListParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_trips(db, current_user, params)


@router.get("/{trip_id}", response_model=TripResponse)
def get_trip_endpoint(
    trip_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_trip_response(db, current_user, trip_id)


@router.patch("/{trip_id}", response_model=TripResponse)
def update_trip_endpoint(
    trip_id: UUID,
    data: TripUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_trip(db, current_user, trip_id, data)


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip_endpoint(
    trip_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_trip(db, current_user, trip_id)


@router.post("/{trip_id}/cover-photo", response_model=TripResponse)
async def upload_cover_photo(
    trip_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    storage: StorageBackend = Depends(get_storage),
):
    return await update_trip_cover_photo(db, current_user, trip_id, storage, file)


@router.delete("/{trip_id}/cover-photo", response_model=TripResponse)
def remove_cover_photo(
    trip_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    storage: StorageBackend = Depends(get_storage),
):
    return delete_trip_cover_photo(db, current_user, trip_id, storage)
