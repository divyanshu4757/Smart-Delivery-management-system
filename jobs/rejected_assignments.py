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
    
        rejected_assignments = db.query(Assignment).filter(Assignment.status == "REJECTED" ,Assignment.is_processed == 0).all()
        
        for assignment in rejected_assignments:
            order = db.query(Order).filter(Order.id == assignment.order_id).first()
            available_drivers = get_available_drivers(db, order)
            if not available_drivers:
                continue
            Rejected_driver_Ids = {
                                        row.driver_id
                                        for row in db.query(Assignment.driver_id)
                                        .filter(
                                            Assignment.order_id == order.id,
                                            Assignment.status == "REJECTED"
                                        )
                                        .all()
                                    }
            
            drivers_after_rejection = [driver for driver in available_drivers if driver.driver_id not in Rejected_driver_Ids]
            if not drivers_after_rejection:
                                        continue
            sorted_drivers = sorted(drivers_after_rejection, key=calculate_distance)
            closest_driver = sorted_drivers[0]
            assignment_new = assign_order_to_driver(db, order, closest_driver.driver_id)  
            assignment.is_processed = 1


        db.commit()

    finally:
        db.close()




rejected_scheduler = BackgroundScheduler()

rejected_scheduler.add_job(
    process_assignments,
    trigger="interval",
    seconds=5
)
