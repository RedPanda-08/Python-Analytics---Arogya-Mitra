from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
import app.models as models
from uuid import UUID

router = APIRouter()

@router.get("/load/daily")
def get_daily_diagnostic_load(db: Session = Depends(get_db)):
    """
    Analytics: Returns the number of lab results uploaded per day.
    Used for Bar Charts showing lab activity trends.
    """
    results = db.query(
        func.date(models.LabResult.uploadedAt).label("day"),
        func.count(models.LabResult.id).label("count")
    ).group_by(func.date(models.LabResult.uploadedAt)).all()
    
    return {str(row.day): row.count for row in results if row.day}

@router.get("/centres/rankings/{hospital_id}")
def get_centre_rankings(hospital_id: UUID, db: Session = Depends(get_db)):
    hospital_id_str = str(hospital_id)
    return db.query(models.DiagnosticCentre).filter(
        models.DiagnosticCentre.affiliatedHospital == hospital_id_str
    ).order_by(models.DiagnosticCentre.rating.desc()).all()