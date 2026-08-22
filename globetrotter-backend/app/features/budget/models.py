import uuid

from sqlalchemy import ForeignKey, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.base_model import Base, TimestampMixin
from app.features.stops.models import Stop


class StopBudgetOverride(Base, TimestampMixin):
    __tablename__ = "stop_budget_overrides"

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
        unique=True,
        index=True,
    )
    transport_cost_override: Mapped[float | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    stay_cost_override: Mapped[float | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )

    stop: Mapped[Stop] = relationship("Stop")
