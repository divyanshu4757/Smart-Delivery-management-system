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
from routes import admin, drivers

app = FastAPI()


Base.metadata.create_all(bind=engine)


app.include_router(admin.router)
app.include_router(drivers.router)



