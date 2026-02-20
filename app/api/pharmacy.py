from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from typing import List
import app.models as models
import app.schemas as schemas
from ..database import get_db

# The single router for all Pharmacy-related analytics
router = APIRouter()

# --- MEDICINE CATALOG ANALYTICS ---

@router.get("/medicines", response_model=List[schemas.MedicineRead])
def get_all_medicines(db: Session = Depends(get_db)):
    """Returns the full medicine catalog."""
    return db.query(models.Medicine).all()

@router.get("/analytics/manufacturers")
def get_manufacturer_distribution(db: Session = Depends(get_db)):
    """Dashboard KPI: Shows brand diversity in the pharmacy."""
    results = db.query(
        models.Medicine.manufacturer,
        func.count(models.Medicine.id).label("count")
    ).group_by(models.Medicine.manufacturer).all()
    return {row.manufacturer: row.count for row in results if row.manufacturer}

# --- PHARMACY BRANCH ANALYTICS ---
@router.get("/branches/{hospital_id}")
def get_hospital_pharmacies(hospital_id: UUID, db: Session = Depends(get_db)):
    hospital_id_str = str(hospital_id)
    return db.query(models.Pharmacy).filter(
        models.Pharmacy.affiliatedHospitalId == hospital_id_str
    ).all()