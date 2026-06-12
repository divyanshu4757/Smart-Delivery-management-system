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


db = SessionLocal()


# this is to create cities and warehouses through static data,later admin will perform this function
def Create_cities_and_warehouses_manually():
    cities = [
        Cities(name="Mumbai", State="Maharashtra"),
        Cities(name="Delhi", State="Delhi"),
        Cities(name="Bengaluru", State="Karnataka"),
        Cities(name="Hyderabad", State="Telangana"),
        Cities(name="Bhopal", State="Madhya Pradesh"),
    ]

    for city in cities:
        db.add(city)

    db.commit()


    warehouses = [
        # Mumbai
        Warehouse(
            name="Mumbai Central Warehouse",
            city_id=db.query(Cities).filter(Cities.name=='Mumbai').first().id,
            address="Andheri East, Mumbai",
            latitude=19.1136,
            longitude=72.8697,
        ),
        Warehouse(
            name="Mumbai North Warehouse",
            city_id=db.query(Cities).filter(Cities.name=='Mumbai').first().id,
            address="Borivali West, Mumbai",
            latitude=19.2307,
            longitude=72.8567,
        ),
        # Delhi
        Warehouse(
            name="Delhi Hub Warehouse",
            city_id=db.query(Cities).filter(Cities.name=='Delhi').first().id,
            address="Dwarka Sector 21, Delhi",
            latitude=28.5511,
            longitude=77.0565,
        ),
        Warehouse(
            name="Delhi East Warehouse",
            city_id=db.query(Cities).filter(Cities.name=='Delhi').first().id,
            address="Laxmi Nagar, Delhi",
            latitude=28.6304,
            longitude=77.2773,
        ),
        # Bengaluru
        Warehouse(
            name="Bengaluru South Warehouse",
            city_id=db.query(Cities).filter(Cities.name=='Bengaluru').first().id,
            address="Electronic City, Bengaluru",
            latitude=12.8456,
            longitude=77.6603,
        ),
        Warehouse(
            name="Bengaluru North Warehouse",
            city_id=db.query(Cities).filter(Cities.name=='Bengaluru').first().id,
            address="Yelahanka, Bengaluru",
            latitude=13.1007,
            longitude=77.5963,
        ),
        # Hyderabad
        Warehouse(
            name="Hyderabad West Warehouse",
            city_id=db.query(Cities).filter(Cities.name=='Hyderabad').first().id,
            address="Gachibowli, Hyderabad",
            latitude=17.4401,
            longitude=78.3489,
        ),
        Warehouse(
            name="Hyderabad Central Warehouse",
            city_id=db.query(Cities).filter(Cities.name=='Hyderabad').first().id,
            address="Madhapur, Hyderabad",
            latitude=17.4483,
            longitude=78.3915,
        ),
        # Bhopal
        Warehouse(
            name="Bhopal North Warehouse",
            city_id=db.query(Cities).filter(Cities.name=='Bhopal').first().id,
            address="MP Nagar, Bhopal",
            latitude=23.2336,
            longitude=77.4340,
        ),
        Warehouse(
            name="Bhopal South Warehouse",
            city_id=db.query(Cities).filter(Cities.name=='Bhopal').first().id,
            address="Kolar Road, Bhopal",
            latitude=23.1666,
            longitude=77.4630,
        ),
    ]

    db.add_all(warehouses)
    db.commit()
Create_cities_and_warehouses_manually()