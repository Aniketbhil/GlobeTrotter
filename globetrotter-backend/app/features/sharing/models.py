import uuid

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.base_model import Base, TimestampMixin
from app.features.trips.models import Trip


class TripShare(Base, TimestampMixin):
    __tablename__ = "trip_shares"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trips.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    slug: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, index=True
    )
    is_public: Mapped[bool] = mapped_column(default=True, nullable=False)

    trip: Mapped[Trip] = relationship("Trip")
