import math
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.common.exceptions import ConflictError, NotFoundError
from app.features.activities.models import Activity
from app.features.cities.models import City
from app.features.cities.schemas import CityCreate, CityListParams, CityUpdate


def search_cities(db: Session, params: CityListParams) -> tuple[list[City], int, int]:
    query = db.query(City)

    if params.search:
        query = query.filter(City.name.ilike(f"%{params.search}%"))
    if params.country:
        query = query.filter(City.country.ilike(params.country))
    if params.region:
        query = query.filter(City.region.ilike(params.region))

    total = query.count()

    if params.sort_by == "name":
        query = query.order_by(City.name.asc())
    elif params.sort_by == "cost_index":
        query = query.order_by(City.cost_index.asc().nulls_last())
    else:  # default "popularity"
        query = query.order_by(City.popularity_score.desc())

    offset = (params.page - 1) * params.page_size
    items = query.offset(offset).limit(params.page_size).all()
    pages = math.ceil(total / params.page_size) if total > 0 else 0

    return items, total, pages


def get_city(db: Session, city_id: UUID) -> City:
    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise NotFoundError("City not found")
    return city


def create_city(db: Session, data: CityCreate) -> City:
    existing = (
        db.query(City)
        .filter(
            func.lower(City.name) == data.name.lower(),
            func.lower(City.country) == data.country.lower(),
        )
        .first()
    )
    if existing:
        raise ConflictError(f"City '{data.name}' in '{data.country}' already exists")

    city = City(
        name=data.name,
        country=data.country,
        region=data.region,
        cost_index=data.cost_index,
        popularity_score=data.popularity_score,
        image_url=data.image_url,
    )
    db.add(city)
    db.commit()
    db.refresh(city)
    return city


def update_city(db: Session, city_id: UUID, data: CityUpdate) -> City:
    city = get_city(db, city_id)
    update_data = data.model_dump(exclude_unset=True)

    if "name" in update_data or "country" in update_data:
        new_name = update_data.get("name", city.name)
        new_country = update_data.get("country", city.country)
        existing = (
            db.query(City)
            .filter(
                func.lower(City.name) == new_name.lower(),
                func.lower(City.country) == new_country.lower(),
                City.id != city_id,
            )
            .first()
        )
        if existing:
            raise ConflictError(f"City '{new_name}' in '{new_country}' already exists")

    for field, value in update_data.items():
        setattr(city, field, value)

    db.commit()
    db.refresh(city)
    return city


def delete_city(db: Session, city_id: UUID) -> None:
    city = get_city(db, city_id)

    activity_count = db.query(Activity).filter(Activity.city_id == city_id).count()
    if activity_count > 0:
        raise ConflictError("Cannot delete city that has referencing activities")

    # TODO: Check if any Stop references this city once stops feature is built

    db.delete(city)
    db.commit()
