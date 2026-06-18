from enum import Enum as PyEnum
from datetime import datetime, UTC

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Enum,
)

from database import Base


class DeliveryType(str, PyEnum):
    STANDARD = "STANDARD"
    EXPRESS = "EXPRESS"

class OrderStatus(str, PyEnum):
    ADDRESS_VERIFICATION_PENDING = "ADDRESS_VERIFICATION_PENDING"
    CREATED = "CREATED"
    ASSIGNING = "ASSIGNING"
    ASSIGNED = "ASSIGNED"
    PICKED_UP = "PICKED_UP"
    DELIVERED = "DELIVERED"
    EXCEPTION = "EXCEPTION"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    external_order_id = Column(
        String,
        unique=True,
        nullable=False
    )

    warehouse_id = Column(
        Integer,
        ForeignKey("warehouses.id"),
        nullable=False
    )

    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)

    delivery_address = Column(String, nullable=False)
    delivery_latitude = Column(Float, nullable=False)
    delivery_longitude = Column(Float, nullable=False)

    weight_kg = Column(Float, nullable=False)

    delivery_type = Column(
        Enum(DeliveryType, name="delivery_type_enum"),
        nullable=False
    )

    status = Column(
        Enum(OrderStatus ,name = "order_status"),
        nullable= False
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)
    )