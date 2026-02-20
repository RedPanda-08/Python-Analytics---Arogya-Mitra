from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from uuid import UUID
import app.models as models
import app.schemas as schemas
from ..database import get_db

router = APIRouter()

@router.get("/invoices/", response_model=List[schemas.InvoiceRead])
def get_all_invoices(db: Session = Depends(get_db)):
    """Fetches all invoices. Verifies mapping for 'total_amount' and 'invoice_id'."""
    return db.query(models.Invoice).all()

@router.get("/revenue/total/{hospital_id}")
def get_total_revenue(hospital_id: UUID, db: Session = Depends(get_db)):
    """Dashboard KPI: Aggregates total revenue for a specific hospital."""
    total = db.query(func.sum(models.Invoice.totalAmount)).filter(
        models.Invoice.hospitalId == hospital_id
    ).scalar() or 0.0
    return {"hospitalId": hospital_id, "totalRevenue": total}

@router.get("/revenue/by-service/{hospital_id}")
def get_service_revenue_breakdown(hospital_id: UUID, db: Session = Depends(get_db)):
    """Financial Insight: Breakdown of revenue by service type (Bed, Appointment, etc.)."""
    results = db.query(
        models.InvoiceItem.referenceType,
        func.sum(models.InvoiceItem.cost).label("revenue")
    ).join(models.Invoice).filter(
        models.Invoice.hospitalId == hospital_id
    ).group_by(models.InvoiceItem.referenceType).all()

    # Returns a clean dictionary for frontend charts: {"BED": 5000, "LAB": 2000}
    return {row.referenceType: row.revenue for row in results if row.referenceType}

@router.get("/insurance/summary/{hospital_id}")
def get_insurance_analytics(hospital_id: UUID, db: Session = Depends(get_db)):
    """Measures Insurance Volume: Total claimed amount across the hospital."""
    results = db.query(
        func.count(models.InsuranceClaim.claimId).label("total_claims"),
        func.sum(models.InsuranceClaim.claimAmount).label("total_value")
    ).join(models.Invoice).filter(
        models.Invoice.hospitalId == hospital_id
    ).first()

    return {
        "hospitalId": hospital_id,
        "totalClaimsCount": results.total_claims or 0,
        "totalClaimedValue": results.total_value or 0.0
    }