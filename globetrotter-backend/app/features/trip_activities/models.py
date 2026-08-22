import datetime
import uuid

from sqlalchemy import (
    Date,
    ForeignKey,
    Numeric,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.base_model import Base, TimestampMixin
from app.features.activities.models import Activity
from app.features.stops.models import Stop


class TripActivity(Base, TimestampMixin):
    __tablename__ = "trip_activities"
    __table_args__ = (
        UniqueConstraint(
            "stop_id",
            "scheduled_date",
            "order_index",
            name="uq_trip_activities_stop_date_order",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    stop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("stops.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    activity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("activities.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    scheduled_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    scheduled_time: Mapped[datetime.time | None] = mapped_column(Time, nullable=True)
    cost_override: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    order_index: Mapped[int] = mapped_column(nullable=False)

    stop: Mapped[Stop] = relationship("Stop")
    activity: Mapped[Activity] = relationship("Activity")
