from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from datetime import date as date_obj
import app.models as models
import app.schemas as schemas
from ..database import get_db

router = APIRouter()

# ---  GENERAL STAFF ANALYTICS ---

@router.get("/summary/{hospital_id}")
def get_workforce_summary(hospital_id: UUID, db: Session = Depends(get_db)):
    """
    Analytics: High-level headcount overview.
    Used for 'Total Staff' cards on the dashboard.
    """
    total = db.query(models.Staff).filter(models.Staff.hospital_id == hospital_id).count()
    
    # Grouping by status (Active, On Leave, etc.)
    status_dist = db.query(
        models.Staff.status, func.count(models.Staff.staff_id)
    ).filter(models.Staff.hospital_id == hospital_id).group_by(models.Staff.status).all()

    return {
        "total_headcount": total,
        "status_distribution": {row[0]: row[1] for row in status_dist}
    }

# ---  DOCTOR & SPECIALTY ANALYTICS ---

@router.get("/doctors/specialty-mix/{hospital_id}")
def get_specialty_analytics(hospital_id: UUID, db: Session = Depends(get_db)):
    """
    Analytics: Counts doctors per specialty.
    Used for 'Medical Coverage' charts.
    """
    results = db.query(
        models.Doctor.specialization,
        func.count(models.Doctor.staff_id).label("count")
    ).join(models.Staff).filter(
        models.Staff.hospital_id == hospital_id
    ).group_by(models.Doctor.specialization).all()
    
    return {row.specialization: row.count for row in results}

# ---  NURSE & SHIFT ANALYTICS ---

@router.get("/nurses/shift-load/{hospital_id}")
def get_nurse_shift_analytics(hospital_id: UUID, db: Session = Depends(get_db)):
    """
    Analytics: Measures nursing staff availability per shift.
    Used to identify potential understaffing in night shifts.
    """
    results = db.query(
        models.Nurse.shift_type,
        func.count(models.Nurse.staff_id)
    ).join(models.Staff).filter(
        models.Staff.hospital_id == hospital_id
    ).group_by(models.Nurse.shift_type).all()
    
    return {row.shift_type: row[1] for row in results}

# ---  LIVE AVAILABILITY ANALYTICS ---

@router.get("/availability/daily-readiness/{hospital_id}")
def get_daily_readiness(hospital_id: UUID, db: Session = Depends(get_db)):
    """
    Analytics: Calculates % of doctors available today.
    Used for the 'Live Readiness' Gauge.
    """
    today = date_obj.today()
    
    total_docs = db.query(models.Doctor).join(models.Staff).filter(
        models.Staff.hospital_id == hospital_id
    ).count()
    
    available = db.query(models.DoctorAvailability).join(models.Doctor).join(models.Staff).filter(
        models.Staff.hospital_id == hospital_id,
        models.DoctorAvailability.date == today
    ).count()
    
    rate = (available / total_docs * 100) if total_docs > 0 else 0
    return {"date": today, "available_count": available, "readiness_rate": f"{rate:.2f}%"}

# ---  QUALITY & FEEDBACK ANALYTICS ---

@router.get("/doctors/top-rated/{hospital_id}")
def get_top_rated_doctors(hospital_id: UUID, db: Session = Depends(get_db)):
    """
    Analytics: Identifies doctors with the highest ratings.
    Used for 'Star Performers' section.
    """
    return db.query(
        models.Staff.full_name,
        models.Doctor.rating,
        models.Doctor.specialization
    ).join(models.Doctor).filter(
        models.Staff.hospital_id == hospital_id
    ).order_by(models.Doctor.rating.desc()).limit(5).all()