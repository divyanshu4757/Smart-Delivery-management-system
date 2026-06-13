from fastapi import APIRouter,HTTPException,Depends
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel
from models.users import User
from passlib.context import CryptContext


router=APIRouter(
    prefix='/auth',
    tags=['auth']
)

bcrypt_context = CryptContext(schemes=["bcrypt"],deprecated = "auto")


class user_request(BaseModel):
    username:str
    password_hash:str

def get_db():
    db = SessionLocal()
    print("1st print")
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session,Depends(get_db)]

def create_master_admin():
    db = SessionLocal()
    hashed_password=bcrypt_context.hash("Ak475767@")

    master_admin  = User(
    username="Div",
    full_name="Divyanshu Gupta",
    password_hash=hashed_password,
    role="DRIVER")

    db.add(master_admin)
    db.commit()




@router.post('/login',status_code=status.HTTP_200_OK)
async def login_admin(db:db_dependency,login_request:user_request):
    user= db.query(User).filter(User.username==login_request.username  , User.password_hash==login_request.password_hash).first()
   
    if user is  None:
         raise HTTPException(status_code=401,detail="Authentication failed") 
    print(user.password_hash, "ye password aaya")
    return {"message":"logged in successfully"}  

