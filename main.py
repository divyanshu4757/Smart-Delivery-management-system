from fastapi import FastAPI
from database import engine, Base
from models.cities import Cities
from models.users import User
from models.drivers import Driver
from models.warehouses import Warehouse
from models.orders import Order
from models.assignments import Assignment
from database import SessionLocal
from sqlalchemy import text
from routes import admin, drivers, order
from jobs.expired_assignments import expired_scheduler
from jobs.rejected_assignments import rejected_scheduler



app = FastAPI()


Base.metadata.create_all(bind=engine)





@app.on_event("startup")
async def startup():
    expired_scheduler.start()
    rejected_scheduler.start()

app.include_router(admin.router)
app.include_router(drivers.router)
app.include_router(order.router)



