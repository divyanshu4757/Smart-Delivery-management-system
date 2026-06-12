from enum import Enum as PyEnum
from datetime import datetime, UTC

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
)

from database import Base


class VehicleType(str, PyEnum):
    BIKE = "BIKE"
    SCOOTER = "SCOOTER"
    VAN = "VAN"
    MINI_TRUCK = "MINI_TRUCK"
    TRUCK = "TRUCK"


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    city_id = Column(
        Integer,
        ForeignKey("cities.id"),
        nullable=False
    )

    vehicle_type = Column(
        Enum(VehicleType, name="vehicle_type_enum"),
        nullable=False
    )

    license_number = Column(String, unique=True, nullable=False)

    max_capacity_kg = Column(Integer, nullable=False)

    available = Column(Boolean, default=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)
    )