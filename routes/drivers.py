
from fastapi import APIRouter, HTTPException
from routes.admin import db_dependency, user_dependency
from starlette import status
from models.drivers import Driver




router=APIRouter(
    prefix='/drivers',
    tags=['driver operations']
)


@router.put('/start_shift' ,status_code=status.HTTP_200_OK)
async def start_shift(db:db_dependency, user: user_dependency):
    if user['user_role'] != "DRIVER":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only drivers can start their shift")
    
    driver = db.query(Driver).filter(Driver.user_id == user['user_id']).first()
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver profile not found")
    
    driver.available = True
    db.commit()
    
    return {"message": "Shift started. You are now available for deliveries."}


@router.put('/end_shift' ,status_code=status.HTTP_200_OK)
async def end_shift(db:db_dependency, user: user_dependency):
    if user['user_role'] != "DRIVER":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only drivers can end their shift")
    
    driver = db.query(Driver).filter(Driver.user_id == user['user_id']).first()
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver profile not found")
    
    driver.available = False
    db.commit()
    
    return {"message": "Shift ended. You are now unavailable for deliveries."}