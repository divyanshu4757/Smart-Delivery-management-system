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


app = FastAPI()


Base.metadata.create_all(bind=engine)




@app.get('/test')
def test():
    
    return {"Status":"Running"}

@app.get("/db-check")
def db_check():
    db = SessionLocal()

    return {"database": "Working"}


