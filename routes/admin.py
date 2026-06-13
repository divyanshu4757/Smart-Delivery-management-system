from fastapi import APIRouter,HTTPException,Depends
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel
from models.users import User
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from jose import jwt ,JWTError
from dotenv import load_dotenv
import os




load_dotenv()


router=APIRouter(
    prefix='/auth',
    tags=['auth']
)

bcrypt_context = CryptContext(schemes=["bcrypt"],deprecated = "auto")

Oauth2_bearer= OAuth2PasswordBearer(tokenUrl='auth/login')



class TokenResponse(BaseModel):
    access_token:str
    token_type:str

def get_db():
    db = SessionLocal()
    print("1st print")
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session,Depends(get_db)]

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def authenticate_user(username:str,password:str,db):
    user= db.query(User).filter(User.username==username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password,user.password_hash):
        return False
    return user

def create_access_token(username:str,user_id:int,role:str,expires_delta:timedelta):
    encode = {'sub':username,'id':user_id,'role':role}
    expires = datetime.now(timezone.utc) +expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)


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


def get_current_user(token:Annotated[str,Depends(Oauth2_bearer)]):
    try:
         payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
         username:str =payload.get('sub')
         
         user_id:int =payload.get('id')
         role= payload.get('role')
         if username is None or user_id is None:
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate user")
         return {'username':username,'user_id':user_id,'user_role':role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate user")


@router.post('/login',status_code=status.HTTP_200_OK)
async def login_admin(form_data:Annotated[OAuth2PasswordRequestForm,Depends()],db:db_dependency):
    user = authenticate_user(form_data.username,form_data.password,db)
    if not user:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate user")
    token = create_access_token(user.username,user.id,user.role,timedelta(minutes=30))
    return TokenResponse(access_token=token, token_type="bearer")


     

