
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException
from routes.admin import db_dependency, user_dependency
from starlette import status
from models.drivers import Driver
from models.assignments import Assignment
from models.orders import Order
from routes.order import assign_order_to_driver



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

@router.get('/my_assignments', status_code=status.HTTP_200_OK)
async def my_assignments(db:db_dependency, user: user_dependency):
    if user['user_role'] != "DRIVER":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only drivers can view their assignments")
    
    driver = db.query(Driver).filter(Driver.user_id == user['user_id']).first()
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver profile not found")
    
    assignments = db.query(Assignment).filter(Assignment.driver_id == driver.id , Assignment.status == "PENDING").all()
    
    return {"assignments": assignments}

@router.post('/accept_assignment/{assignment_id}', status_code=status.HTTP_200_OK)
async def accept_assignment(assignment_id: int, db:db_dependency, user: user_dependency):
    if user['user_role'] != "DRIVER":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only drivers can accept assignments")
    
    
    driver = db.query(Driver).filter(Driver.user_id == user['user_id']).first()
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver profile not found")
    
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id, Assignment.driver_id == driver.id).first()
    if not assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")
    
    if assignment.status != "PENDING":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assignment is not pending")
    
    assignment.status = "ACCEPTED"
    assignment.responded_at = datetime.now(UTC)

    get_order = db.query(Order).filter(Order.id == assignment.order_id).first()
    get_order.status = "ASSIGNED"

    db.commit()
    
    return {"message": "Assignment accepted successfully."}

@router.post('/reject_assignment/{assignment_id}', status_code=status.HTTP_200_OK)
async def reject_assignment(assignment_id: int, db:db_dependency, user: user_dependency):
    if user['user_role'] != "DRIVER":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only drivers can reject assignments")
    
    driver = db.query(Driver).filter(Driver.user_id == user['user_id']).first()
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver profile not found")
    
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id, Assignment.driver_id == driver.id).first()
    if not assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")
    
    if assignment.status != "PENDING":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assignment is not pending")
    
    assignment.status = "REJECTED"
    assignment.responded_at = datetime.now(UTC)
    db.commit()
    
    return {"message": "Assignment rejected successfully."}