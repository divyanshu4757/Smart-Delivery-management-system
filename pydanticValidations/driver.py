from pydantic import BaseModel,Field
from enum import Enum
from datetime import datetime
from models.drivers import VehicleType

class UserRole(str, Enum):
    DRIVER = "DRIVER"

class DriverDetailsSchema(BaseModel):
    city_id: int = Field(..., description="The ID of the city the driver operates in")
    vehicle_type: VehicleType = Field(..., description="Must match one of your predefined VehicleType enum options")
    license_number: str = Field(..., min_length=5, max_length=30)
    max_capacity_kg: int = Field(..., gt=0, description="Maximum carrying capacity in kilograms")
    available: bool = False

class DriverCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.DRIVER
    
    driver_details: DriverDetailsSchema