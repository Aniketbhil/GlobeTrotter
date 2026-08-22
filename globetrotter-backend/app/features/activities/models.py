import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.base_model import Base, TimestampMixin

if TYPE_CHECKING:
    from app.features.cities.models import City


class ActivityType(str, enum.Enum):
    sightseeing = "sightseeing"
    food = "food"
    adventure = "adventure"
    culture = "culture"
    nightlife = "nightlife"
    other = "other"


class Activity(Base, TimestampMixin):
    __tablename__ = "activities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    city_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cities.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    type: Mapped[ActivityType] = mapped_column(
        Enum(ActivityType, name="activity_type_enum"),
        nullable=False,
        index=True,
    )
    cost: Mapped[float] = mapped_column(
        Numeric(8, 2), default=0.0, server_default="0.00", nullable=False
    )
    duration_mins: Mapped[int | None] = mapped_column(nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    city: Mapped["City"] = relationship("City", back_populates="activities")
