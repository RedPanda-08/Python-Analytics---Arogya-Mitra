from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from uuid import UUID
import app.models as models
import app.schemas as schemas
from ..database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.AppointmentRead])
def get_all_appointments(db: Session = Depends(get_db)):
    """Fetches all appointments. Verifies snake_case mapping for 'time_slot'."""
    return db.query(models.Appointment).all()

@router.get("/today/{hospital_id}")
def get_todays_count(hospital_id: UUID, db: Session = Depends(get_db)):
    """Dashboard KPI: Count of all appointments scheduled for today."""
    today = datetime.now().date()
    count = db.query(models.Appointment).filter(
        models.Appointment.hospitalId == hospital_id,
        models.Appointment.date == today
    ).count()
    return {"hospitalId": hospital_id, "date": today, "count": count}