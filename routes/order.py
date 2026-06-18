
import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from routes.admin import db_dependency, user_dependency
from starlette import status
from models.orders import Order
from models.drivers import Driver
from models.warehouses import Warehouse
from models.assignments import Assignment
from pydanticValidations.order import create_order_request
from sqlalchemy import and_
from haversine import haversine, Unit


router=APIRouter(
    prefix='/order',
    tags=['order operations']
)




def get_available_drivers(db, order:Order):
    result = (
        db.query(
            Driver.id.label("driver_id"),
            Driver.latitude.label("driver_lat"),
            Driver.longitude.label("driver_lng"),
            Driver.max_capacity_kg,
            Warehouse.id.label("warehouse_id"),
            Warehouse.latitude.label("warehouse_lat"),
            Warehouse.longitude.label("warehouse_lng"),
        )
        .join(Warehouse, Warehouse.city_id == Driver.city_id)
        .filter(
            and_(
                Warehouse.id == order.warehouse_id,
                Driver.available == True,
                Driver.max_capacity_kg >= order.weight_kg,
                Driver.latitude.isnot(None),      
                Driver.longitude.isnot(None), 
            )
        )
        .all()
    )
    return result
    
 # Calculate distances and sort drivers
def calculate_distance(driver):
        driver_location = (driver.driver_lat, driver.driver_lng)
        warehouse_location = (driver.warehouse_lat, driver.warehouse_lng)
        return haversine(driver_location, warehouse_location, unit=Unit.KILOMETERS)

def assign_order_to_driver(db, order: Order, driver_id: int):
    assignment = Assignment(
        order_id=order.id,
        driver_id=driver_id,
        status="PENDING",
        responded_at=None,
        expires_at=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=3)
    )
    db.add(assignment)
    db.commit()
    return assignment

        


@router.post('/create_order', status_code=status.HTTP_201_CREATED)
async def create_order(db: db_dependency, order_details: create_order_request):
    new_order = Order()
    for key, value in order_details.dict().items():
        setattr(new_order, key, value)
    new_order.status = "CREATED" 
    db.add(new_order)
    db.commit()

    avaialble_drivers =  get_available_drivers(db, new_order)
    print(avaialble_drivers)
    if not avaialble_drivers:
        raise HTTPException(status_code=404, detail="No available drivers found for this order")
    
    sorted_drivers = sorted(avaialble_drivers, key=calculate_distance)
    closest_driver = sorted_drivers[0]
    assignment = assign_order_to_driver(db, new_order, closest_driver.driver_id)
    return {"message": "Order created and assigned to driver", "order_id": new_order.id, "assigned_driver_id": closest_driver.driver_id}


    
