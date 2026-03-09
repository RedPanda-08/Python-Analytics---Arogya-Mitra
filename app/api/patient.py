from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from uuid import UUID
from datetime import date as date_obj
import app.models as models
import app.schemas as schemas
from ..database import get_db

router = APIRouter()

# --- 1. DATA RETRIEVAL (Standard) ---

@router.get("/{hospital_id}", response_model=List[schemas.PatientRead])
def get_hospital_patients(hospital_id: UUID, db: Session = Depends(get_db)):
    """Multi-tenant fetch: Only returns patients for a specific hospital"""
    return db.query(models.Patient).filter(models.Patient.hospital_id == hospital_id).all()

@router.get("/record/{patient_id}", response_model=schemas.PatientRead)
def get_patient_by_id(patient_id: UUID, db: Session = Depends(get_db)):
    """Fetches a specific patient record by UUID"""
    patient = db.query(models.Patient).filter(models.Patient.patientId == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient record not found")
    return patient

# --- 2. OPERATIONAL ANALYTICS ---

@router.get("/analytics/load/{hospital_id}")
def get_patient_load_analytics(hospital_id: UUID, db: Session = Depends(get_db)):
    """
    Robust Analytics: Measures Live Patient Flow.
    Used to detect waiting room bottlenecks in real-time.
    """
    today = date_obj.today()

    # 1. Total Registered Base for this Hospital
    total_registered = db.query(models.Patient).filter(
        models.Patient.hospital_id == hospital_id
    ).count()

    # 2. Waiting Room Count: Today's appointments not yet started
    waiting = db.query(models.Appointment).filter(
        models.Appointment.hospital_id == hospital_id,
        models.Appointment.date == today,
        models.Appointment.status == "SCHEDULED"
    ).count()

    # 3. Active Consultations: Currently with a doctor
    active_treatments = db.query(models.Appointment).filter(
        models.Appointment.hospital_id == hospital_id,
        models.Appointment.date == today,
        models.Appointment.status == "IN_PROGRESS"
    ).count()

    load_status = "CRITICAL" if waiting > (active_treatments * 3) and waiting > 5 else "STABLE"

    return {
        "hospital_id": hospital_id,
        "total_registered_patients": total_registered,
        "waiting_now": waiting,
        "in_consultation": active_treatments,
        "flow_status": load_status,
        "timestamp": today
    }