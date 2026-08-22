from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_admin_user,
    get_current_user,
    get_db,
)
from app.features.auth.models import User
from app.features.cities.schemas import (
    CityCreate,
    CityListParams,
    CityResponse,
    CityUpdate,
    PaginatedCityResponse,
)
from app.features.cities.service import (
    create_city,
    delete_city,
    get_city,
    search_cities,
    update_city,
)

router = APIRouter(prefix="/api/cities", tags=["cities"])


@router.get("", response_model=PaginatedCityResponse)
@router.get("/", response_model=PaginatedCityResponse, include_in_schema=False)
def list_cities(
    params: CityListParams = Depends(),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    items, total, pages = search_cities(db, params)
    return PaginatedCityResponse(
        items=items,
        total=total,
        page=params.page,
        page_size=params.page_size,
        pages=pages,
    )


@router.get("/{city_id}", response_model=CityResponse)
def get_city_endpoint(
    city_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return get_city(db, city_id)


@router.post("", response_model=CityResponse, status_code=status.HTTP_201_CREATED)
@router.post(
    "/",
    response_model=CityResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def create_city_endpoint(
    data: CityCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
):
    return create_city(db, data)


@router.patch("/{city_id}", response_model=CityResponse)
def update_city_endpoint(
    city_id: UUID,
    data: CityUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
):
    return update_city(db, city_id, data)


@router.delete("/{city_id}")
def delete_city_endpoint(
    city_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
):
    delete_city(db, city_id)
    return {"message": "City deleted successfully"}
