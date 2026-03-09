from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case, select
from uuid import UUID
from datetime import date as date_obj
import app.models as models
import app.schemas as schemas
from ..database import get_db

router = APIRouter()

# ---  GENERAL SUMMARY ---
@router.get("/summary/{hospital_id}")
def get_workforce_summary(hospital_id: UUID, db: Session = Depends(get_db)):
    today = date_obj.today()
    total = db.query(models.Staff).filter(models.Staff.hospital_id == hospital_id).count()
    
    # Real-time check-in count
    present = db.query(models.Staff).join(
        models.DoctorAvailability, models.Staff.staff_id == models.DoctorAvailability.doctor_id
    ).filter(models.Staff.hospital_id == hospital_id, models.DoctorAvailability.date == today).count()

    status_dist = db.query(models.Staff.status, func.count(models.Staff.staff_id)).filter(
        models.Staff.hospital_id == hospital_id
    ).group_by(models.Staff.status).all()

    return {
        "total_headcount": total,
        "present_for_duty": present,
        "absent_today": total - present,
        "status_distribution": {row[0]: row[1] for row in status_dist}
    }

# ---  SPECIALTY MIX ---
@router.get("/doctors/specialty-mix/{hospital_id}")
def get_specialty_analytics(hospital_id: UUID, db: Session = Depends(get_db)):
    results = db.query(models.Doctor.specialization, func.count(models.Doctor.staff_id)).join(
        models.Staff).filter(models.Staff.hospital_id == hospital_id
    ).group_by(models.Doctor.specialization).all()
    return {row[0]: row[1] for row in results}

# --- RESTORED SHIFT LOAD ---
@router.get("/nurses/shift-load/{hospital_id}")
def get_nurse_shift_analytics(hospital_id: UUID, db: Session = Depends(get_db)):
    results = db.query(models.Nurse.shift_type, func.count(models.Nurse.staff_id)).join(
        models.Staff).filter(models.Staff.hospital_id == hospital_id
    ).group_by(models.Nurse.shift_type).all()
    return {row[0]: row[1] for row in results}

# ---  RESTORED DAILY READINESS ---
@router.get("/availability/daily-readiness/{hospital_id}")
def get_daily_readiness(hospital_id: UUID, db: Session = Depends(get_db)):
    today = date_obj.today()
    total_docs = db.query(models.Doctor).join(models.Staff).filter(models.Staff.hospital_id == hospital_id).count()
    available = db.query(models.DoctorAvailability).join(models.Doctor).join(models.Staff).filter(
        models.Staff.hospital_id == hospital_id, models.DoctorAvailability.date == today).count()
    rate = (available / total_docs * 100) if total_docs > 0 else 0
    return {"date": today, "available_count": available, "readiness_rate": f"{rate:.2f}%"}

# ---  TOP RATED (With Subquery Fix) ---
@router.get("/doctors/top-rated/{hospital_id}", response_model=List[schemas.DoctorAnalytics])
def get_top_rated_doctors(hospital_id: UUID, db: Session = Depends(get_db)):
    today = date_obj.today()

    # FIX: Using select() explicitly to remove the SAWarning
    available_today_stmt = select(models.DoctorAvailability.doctor_id).where(
        models.DoctorAvailability.date == today
    )

    results = db.query(
        models.Staff.full_name,
        models.Doctor.specialization,
        models.Doctor.rating,
        case(
            (models.Staff.staff_id.in_(available_today_stmt), " ON-DUTY"),
            else_=" UNAVAILABLE"
        ).label("status")
    ).join(models.Doctor).filter(
        models.Staff.hospital_id == hospital_id
    ).order_by(models.Doctor.rating.desc()).limit(5).all()

    return results