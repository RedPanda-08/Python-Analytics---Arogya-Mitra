from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
import app.models as models

router = APIRouter()

@router.get("/inventory/manufacturers")
def get_manufacturer_distribution(db: Session = Depends(get_db)):
    """
    Analytics: Returns a count of medicines grouped by manufacturer.
    Used for Pie Charts to show brand reliance.
    """
    results = db.query(
        models.Medicine.manufacturer,
        func.count(models.Medicine.id).label("count")
    ).group_by(models.Medicine.manufacturer).all()
    
    return {row.manufacturer: row.count for row in results if row.manufacturer}