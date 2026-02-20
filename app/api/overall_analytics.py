from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from datetime import datetime
import app.models as models
from ..database import get_db
from datetime import datetime, timedelta


router = APIRouter()

@router.get("/executive-summary/{hospital_id}")
def get_master_executive_summary(hospital_id: UUID, db: Session = Depends(get_db)):
    """
    INTELLIGENCE LAYER: This is the primary endpoint for the Arogya Mitra Admin Dashboard.
    It synthesizes 5 key business pillars into one JSON response.
    """
    
    # Service 1: Financial Health (Total Revenue)
    revenue = db.query(func.sum(models.Invoice.totalAmount)).filter(
        models.Invoice.hospitalId == hospital_id
    ).scalar() or 0

    # Service 2: Clinical Quality (Success Rate)
    # Count only records that have an outcome status
    total_clinical = db.query(models.TreatmentRecord).count()
    success_clinical = db.query(models.TreatmentRecord).filter(
        models.TreatmentRecord.outcome == "SUCCESS"
    ).count()
    success_rate = (success_clinical / total_clinical * 100) if total_clinical > 0 else 0

    # Service 3: Infrastructure Capacity (Bed Occupancy)
    total_beds = db.query(models.Bed).filter(models.Bed.hospitalId == hospital_id).count()
    occupied = db.query(models.Bed).filter(
        models.Bed.hospitalId == hospital_id, 
        models.Bed.status == "OCCUPIED"
    ).count()
    occupancy = (occupied / total_beds * 100) if total_beds > 0 else 0

    # Service 4: Operational Load (Pending Appointments)
    pending_appts = db.query(models.Appointment).filter(
        models.Appointment.hospitalId == hospital_id,
        models.Appointment.status == "PENDING"
    ).count()

    # Service 5: Emergency Readiness (Ambulances)
    available_ambulances = db.query(models.Ambulance).filter(
        models.Ambulance.hospitalId == hospital_id,
        models.Ambulance.available == True
    ).count()

    return {
        "hospitalId": hospital_id,
        "generatedAt": datetime.now(),
        "dashboard_stats": {
            "financial": {"totalRevenue": round(revenue, 2), "unit": "INR"},
            "clinical": {"successRate": f"{success_rate:.1f}%", "totalCases": total_clinical},
            "capacity": {"occupancyRate": f"{occupancy:.1f}%", "activeBeds": occupied},
            "operations": {"pendingAppointments": pending_appts, "readyAmbulances": available_ambulances}
        }
    }

@router.get("/trends/patient-flow/{hospital_id}")
def get_patient_flow_trends(hospital_id: UUID, db: Session = Depends(get_db)):
    trends = db.query(
        models.Appointment.date.label("date"),
        func.count(models.Appointment.appointmentId).label("patient_count")
    ).filter(
        models.Appointment.hospitalId == hospital_id
    ).group_by(models.Appointment.date).order_by(models.Appointment.date.desc()).limit(7).all()

    return [{"date": str(t.date), "count": t.patient_count} for t in trends]

@router.get("/health/watchdog")
def system_health_watchdog(db: Session = Depends(get_db)):
    """
    Monitors data integrity and freshness across the Arogya Mitra hub.
    Flags services as 'old data' if no data has been synced in 24 hours.
    """
    def check_freshness(model, timestamp_col):
        # Find the most recent update in the table
        latest_record = db.query(func.max(timestamp_col)).scalar()
        
        if not latest_record:
            return {"status": "EMPTY", "last_sync": None}
            
        # Check if the data is older than 24 hours
        is_stale = datetime.now() - latest_record > timedelta(hours=24)
        return {
            "status": "STALE" if is_stale else "HEALTHY",
            "last_sync": latest_record.strftime("%Y-%m-%d %H:%M:%S")
        }

    return {
        "services": {
            "pharmacy_pipeline": check_freshness(models.Pharmacy, models.Pharmacy.createdAt),
            "billing_pipeline": check_freshness(models.Invoice, models.Invoice.createdAt),
            "clinical_pipeline": check_freshness(models.TreatmentRecord, models.TreatmentRecord.performedAt),
            "appointment_sync": check_freshness(models.Appointment, models.Appointment.createdAt)
        },
        "system_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }