from apscheduler.schedulers.background import BackgroundScheduler
from models.assignments import Assignment
from models.orders import Order
from datetime import datetime, timedelta
from routes.admin import db_dependency, user_dependency
from database import SessionLocal
from routes.order import get_available_drivers, assign_order_to_driver ,calculate_distance


def process_assignments():
    db = SessionLocal()

    try:
        pending_assignments = db.query(Assignment).filter(Assignment.status == "PENDING" , Assignment.expires_at < datetime.now()).all()
        
        for assignment in pending_assignments:
            order = db.query(Order).filter(Order.id == assignment.order_id).first()
            available_drivers = get_available_drivers(db, order)
            if not available_drivers:
                continue
            sorted_drivers = sorted(available_drivers, key=calculate_distance)
            closest_driver = sorted_drivers[0]
            assignment_new = assign_order_to_driver(db, order, closest_driver.driver_id)  
            assignment.status = "EXPIRED"
        db.commit()
    finally:
        db.close()



expired_scheduler = BackgroundScheduler()

expired_scheduler.add_job(
    process_assignments,
    trigger="interval",
    seconds=5
)
