from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict
from ..database import get_db
import app.models as models

router = APIRouter()

@router.get("/outcomes/summary")
def get_outcome_distribution(db: Session = Depends(get_db)):
    """
    Analytics: Returns a count of each outcome type (e.g., SUCCESS: 50, RECOVERY: 30).
    This is used for Pie Charts on the dashboard.
    """
    results = db.query(
        models.TreatmentRecord.outcome,
        func.count(models.TreatmentRecord.recordId).label("count")
    ).group_by(models.TreatmentRecord.outcome).all()
    
    return {row.outcome: row.count for row in results if row.outcome}