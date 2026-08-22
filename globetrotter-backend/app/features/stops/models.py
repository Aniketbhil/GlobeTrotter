import datetime
import uuid

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Numeric,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.base_model import Base, TimestampMixin
from app.features.cities.models import City
from app.features.trips.models import Trip


class Stop(Base, TimestampMixin):
    __tablename__ = "stops"
    __table_args__ = (
        CheckConstraint(
            "end_date >= start_date", name="ck_stops_end_date_gte_start_date"
        ),
        UniqueConstraint("trip_id", "order_index", name="uq_stops_trip_id_order_index"),
    )

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
        index=True,
    )
    city_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cities.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    order_index: Mapped[int] = mapped_column(nullable=False)
    start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    end_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    budget_estimate: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    city: Mapped[City] = relationship("City")
    trip: Mapped[Trip] = relationship("Trip")
