from datetime import datetime
from database import Base
from sqlalchemy import Column, DateTime, ForeignKey,Integer, String, Boolean


class Cities(Base):
    __tablename__ = "cities"
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String,unique=True)
    State = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
