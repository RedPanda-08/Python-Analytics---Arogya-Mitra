from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from typing import Dict, List
import app.models as models
import app.schemas as schemas
from ..database import get_db

router = APIRouter()

# --- 1. CLINICAL EFFICACY ANALYTICS ---

@router.get("/outcomes/summary/{hospital_id}")
def get_clinical_outcome_analytics(hospital_id: UUID, db: Session = Depends(get_db)):
    """
    Robust Analytics: Measures Clinical Success & Recovery Rates.
    Used for 'Quality of Care' donut charts on the executive dashboard.
    """
    
    results = db.query(
        models.TreatmentRecord.outcome,
        func.count(models.TreatmentRecord.recordId).label("count")
    ).join(models.TreatmentRecordRead).filter(
        models.TreatmentRecordRead.hospital_id == hospital_id 
    ).group_by(models.TreatmentRecord.outcome).all()

    outcome_map = {row.outcome: row.count for row in results if row.outcome}
    
    # 2. Advanced Metric: Success Rate Calculation
    total_cases = sum(outcome_map.values())
    success_cases = outcome_map.get("SUCCESS", 0) + outcome_map.get("RECOVERY", 0)
    
    success_rate = (success_cases / total_cases * 100) if total_cases > 0 else 0

    return {
        "hospital_id": hospital_id,
        "outcome_distribution": outcome_map,
        "clinical_success_rate": f"{success_rate:.1f}%",
        "total_treated_cases": total_cases
    }

# --- 2. DEPARTMENTAL PERFORMANCE ---

@router.get("/departmental-success/{hospital_id}")
def get_dept_clinical_performance(hospital_id: UUID, db: Session = Depends(get_db)):
    """
    Robust Analytics: Identifies high-performing vs. struggling departments.
    """
    results = db.query(
        models.DepartmentRead.deptName,
        func.count(models.TreatmentRecord.recordId).label("success_count")
    ).join(models.TreatmentRecordRead).join(models.DepartmentRead).filter(
        models.DepartmentRead.hospital_id == hospital_id,
        models.TreatmentRecord.outcome == "SUCCESS"
    ).group_by(models.DepartmentRead.deptName).all()

    return {row.deptName: row.success_count for row in results}