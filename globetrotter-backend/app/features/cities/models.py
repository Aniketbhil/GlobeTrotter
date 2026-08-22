import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.base_model import Base, TimestampMixin

if TYPE_CHECKING:
    from app.features.activities.models import Activity


class City(Base, TimestampMixin):
    __tablename__ = "cities"
    __table_args__ = (
        UniqueConstraint("name", "country", name="uq_cities_name_country"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cost_index: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    popularity_score: Mapped[int] = mapped_column(
        default=0, server_default="0", nullable=False
    )
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    activities: Mapped[list["Activity"]] = relationship(
        "Activity", back_populates="city"
    )
