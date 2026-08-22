from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_admin_user,
    get_current_user,
    get_db,
)
from app.features.activities.schemas import (
    ActivityCreate,
    ActivityListParams,
    ActivityResponse,
    ActivityUpdate,
    PaginatedActivityResponse,
)
from app.features.activities.service import (
    create_activity,
    delete_activity,
    get_activity,
    search_activities,
    update_activity,
)
from app.features.auth.models import User

router = APIRouter(prefix="/api/activities", tags=["activities"])


@router.get("", response_model=PaginatedActivityResponse)
@router.get("/", response_model=PaginatedActivityResponse, include_in_schema=False)
def list_activities(
    params: ActivityListParams = Depends(),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    items, total, pages = search_activities(db, params)
    return PaginatedActivityResponse(
        items=items,
        total=total,
        page=params.page,
        page_size=params.page_size,
        pages=pages,
    )


@router.get("/{activity_id}", response_model=ActivityResponse)
def get_activity_endpoint(
    activity_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return get_activity(db, activity_id)


@router.post("", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
@router.post(
    "/",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def create_activity_endpoint(
    data: ActivityCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
):
    return create_activity(db, data)


@router.patch("/{activity_id}", response_model=ActivityResponse)
def update_activity_endpoint(
    activity_id: UUID,
    data: ActivityUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
):
    return update_activity(db, activity_id, data)


@router.delete("/{activity_id}")
def delete_activity_endpoint(
    activity_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
):
    delete_activity(db, activity_id)
    return {"message": "Activity deleted successfully"}
