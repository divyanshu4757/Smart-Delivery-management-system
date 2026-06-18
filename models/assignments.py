from enum import Enum as PyEnum
from datetime import datetime, UTC

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    Enum,
)

from database import Base


class AssignmentStatus(str, PyEnum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
  


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False
    )

    driver_id = Column(
        Integer,
        ForeignKey("drivers.id"),
        nullable=False
    )

    status = Column(
        Enum(AssignmentStatus, name="assignment_status_enum"),
        nullable=False
    )

    is_processed = Column(Integer, default=0)  # 0 for not processed, 1 for processed

    responded_at = Column(DateTime(timezone=True), nullable=True)

    expires_at = Column(DateTime(timezone=True), nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )