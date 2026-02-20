from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import app.models as models
import app.schemas as schemas
from ..database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.HospitalRead])
def get_all_hospitals(db: Session = Depends(get_db)):
    """Fetches all hospitals."""
    return db.query(models.Hospital).all()

@router.get("/{hospital_id}", response_model=schemas.HospitalRead)
def get_hospital(hospital_id: UUID, db: Session = Depends(get_db)):
    """Fetches details for one hospital."""
    hospital = db.query(models.Hospital).filter(models.Hospital.hospitalId == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return hospital

@router.get("/capacity/occupancy/{hospital_id}")
def get_bed_occupancy_rate(hospital_id: UUID, db: Session = Depends(get_db)):
    """
    Analytics: Calculates real-time bed occupancy percentage.
    Used for the 'Capacity Gauge' on the main dashboard.
    """
    total = db.query(models.Bed).filter(models.Bed.hospitalId == hospital_id).count()
    
    occupied = db.query(models.Bed).filter(
        models.Bed.hospitalId == hospital_id, 
        models.Bed.status == "OCCUPIED"
    ).count()
    
    # Formula: (Occupied / Total) * 100
    rate = (occupied / total * 100) if total > 0 else 0
    
    return {
        "hospitalId": hospital_id,
        "totalBeds": total,
        "occupiedCount": occupied,
        "occupancyPercentage": f"{rate:.2f}%"
    }

@router.get("/departments/service-count/{hospital_id}")
def get_department_service_count(hospital_id: UUID, db: Session = Depends(get_db)):
    """
    Analytics: Counts treatments per department for a specific hospital.
    Used for 'Service Capability' charts on the dashboard.
    """
    results = db.query(
        models.Department.deptName,
        func.count(models.DepartmentTreatment.treatmentName).label("total_services")
    ).join(models.DepartmentTreatment).filter(
        models.Department.hospitalId == hospital_id
    ).group_by(models.Department.deptName).all()
    
    return {row.deptName: row.total_services for row in results}

@router.get("/departments/diversity/{hospital_id}")
def get_department_service_diversity(hospital_id: UUID, db: Session = Depends(get_db)):
    """
    Analytics: Counts how many unique treatments each department offers.
    Used for a 'Departmental Strength' Bar Chart.
    """
    results = db.query(
        models.Department.deptName,
        func.count(models.DepartmentTreatment.treatmentName).label("service_count")
    ).join(models.DepartmentTreatment).filter(
        models.Department.hospitalId == hospital_id
    ).group_by(models.Department.deptName).all()
    
    return {row.deptName: row.service_count for row in results}

@router.get("/emergency/readiness/{hospital_id}")
def get_ambulance_readiness(hospital_id: UUID, db: Session = Depends(get_db)):
    """
    Analytics: Calculates the percentage of ambulances currently available.
    Used for an 'Emergency Status' indicator on the dashboard.
    """
    total = db.query(models.Ambulance).filter(models.Ambulance.hospitalId == hospital_id).count()
    available_count = db.query(models.Ambulance).filter(
        models.Ambulance.hospitalId == hospital_id, 
        models.Ambulance.available == True
    ).count()
    
    readiness_rate = (available_count / total * 100) if total > 0 else 0
    return {
        "hospitalId": hospital_id,
        "totalAmbulances": total,
        "availableCount": available_count,
        "readinessPercentage": f"{readiness_rate:.2f}%"
    }