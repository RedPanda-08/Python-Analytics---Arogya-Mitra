from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import app.models as models
import app.schemas as schemas
from ..database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.PatientRead])
def get_all_patients(db: Session = Depends(get_db)):
    """Fetches all registered patients from Supabase."""
    return db.query(models.Patient).all()

@router.get("/{patient_id}", response_model=schemas.PatientRead)
def get_patient_by_id(patient_id: UUID, db: Session = Depends(get_db)):
    """Fetches a specific patient record by UUID."""
    patient = db.query(models.Patient).filter(models.Patient.patientId == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient