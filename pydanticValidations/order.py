from pydantic import BaseModel, Field
from  models.orders import DeliveryType, OrderStatus


class create_order_request(BaseModel):
    external_order_id: str
    warehouse_id: int
    customer_name: str
    customer_phone: str
    delivery_address: str
    delivery_latitude: float = Field(..., ge=-90, le=90)
    delivery_longitude: float = Field(..., ge=-180, le=180)
    weight_kg: float = Field(..., gt=0)
    delivery_type: DeliveryType