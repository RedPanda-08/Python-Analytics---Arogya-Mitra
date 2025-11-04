from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session 
from database import SessionLocal, engine
import models
from sqlalchemy import func
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware 


#Creates tables in database
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Python Analytics Service",
    description="A service for performing analytics on Python data.",
    version="1.0.0"
)

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_started_date(period:str):
    today = datetime.now()
    if period == "week":
        return today - timedelta(days=7)
    elif period == "month":
        return today - timedelta(days=30)
    elif period == "year":
        return today - timedelta(days=365)
    return today - timedelta(days=1)

#API Endpoints for Analytics
# ----------- Hospital and Doctor Rating Endpoints --------------
@app.get("/")
def home():
    return {"message": "Welcome to the Python Analytics Service"}

@app.get("/analytics/hospitals/{hospital_id}/rating")
def get_hospital_rating(hospital_id: int, db: Session = Depends(get_db)):
    """Calculates and returns the average star rating for a specific hospital."""
    avg_rating = db.query(func.avg(models.Review.rating)).join(
        models.Appointment, models.Review.appointment_id == models.Appointment.id
    ).filter(
        models.Appointment.hospital_id == hospital_id
    ).scalar()

    return {
        "hospital_id": hospital_id,
        "average_rating": avg_rating or 0.0 
    }

@app.get("/analytics/doctors/{doctor_id}/rating")
def get_doctor_rating(doctor_id: int, db: Session = Depends(get_db)):
    """Calculates and returns the average star rating for a specific doctor."""
    avg_rating = db.query(func.avg(models.Review.rating)).join(
        models.Appointment, models.Review.appointment_id == models.Appointment.id
    ).filter(
        models.Appointment.doctor_id == doctor_id
    ).scalar()
    return{"doctor_id": doctor_id,
           "average_rating": avg_rating or 0.0}

@app.get("/analytics/doctors/{doctor_id}/reviews")
def get_doctor_reviews(doctor_id: int, db: Session = Depends(get_db)):
    reviews = db.query(models.Review).join(
        models.Appointment, models.Review.appointment_id == models.Appointment.id
    ).filter(
        models.Appointment.doctor_id == doctor_id
    ).all()
    return{"doctor_id": doctor_id, "reviews": reviews}

# ---------- Hospital Operations -----------

@app.get("/analytics/hospitals/{hospital_id}/bed-occupancy")
def get_bed_occupancy(hospital_id: int, db: Session = Depends(get_db)):
    occupied_beds_count = db.query(models.Bed).filter(
        models.Bed.hospital_id == hospital_id,
        models.Bed.status == 'OCCUPIED'
    ).count()
    total_beds_count = db.query(models.Bed).filter(
        models.Bed.hospital_id == hospital_id
    ).count()

    if total_beds_count == 0:
        rate = 0.0
    else:
        rate = occupied_beds_count / total_beds_count

    return {
        "hospital_id": hospital_id,
        "total_beds": total_beds_count,
        "occupied_beds": occupied_beds_count,
        "occupancy_rate": rate
    }

@app.get("/analytics/hospitals/{hospital_id}/patient-flow")
def get_patient_flow(hospital_id: int, period: str="week", db: Session = Depends(get_db)):
    start_date = get_started_date(period)
    inflow_count = db.query(models.Appointment).filter(
        models.Appointment.hospital_id == hospital_id,
        models.Appointment.admission_time>=start_date
    ).count()

    outflow_count = db.query(models.Appointment).filter(
        models.Appointment.hospital_id == hospital_id,
        models.Appointment.disacharge_time>=start_date
    ).count()
    return{"hospital_id": hospital_id,
           "period": period,
           "inflow_count": inflow_count,
           "outflow_count": outflow_count
           }

# ---------- Health Trends -----------

@app.get("/analytics/hospitals/{hospital_id}/disease-trends")
def get_disease_trends(hospital_id: int, period: str = "month", db: Session = Depends(get_db)):
    start_date = get_started_date(period)
    trends = db.query(
        models.Appointement.diagnosis,
        func.count(models.Appointment.id).label("count")
    ).filter(
        models.Appointment.hospital_id == hospital_id,
        models.Appointment.admission_time >= start_date,
        models.Appointment.diagnosis != None
    ).group_by(
        models.Appointment.diagnosis
    ).order_by(
        func.count(models.Appointment.id).desc()
    ).all()
    return{"hospital_id": hospital_id,
           "period": period,
           "start_date": start_date,
           "disease_trends": trends
           }

@app.get("/analytics/hospitals/{hospital_id}/mortality-rate")
def get_mortality_rate(hospital_id: int, period: str = "month", db: Session = Depends(get_db)):
    start_date = get_started_date(period)
    patient_ids_query = db.query(models.Appointment.patient_user_id).filter(
        models.Appointment.hospital_id == hospital_id,
        models.Appointment.admission_time >= start_date
    ).distinct()

    patient_ids = [id[0] for id in patient_ids_query.all()]
    if not patient_ids:
        return{
            "hospital_id": hospital_id,
            "period": period,
            "total_patients__admitted":0,
            "deaths_in_periods":0,
            "maortality_rate":0.0
        }
    death_count = db.query(models.User).filter(
        models.User.id.in_(patient_ids),
        models.User.status == 'DECEASED',
        models.User.date_of_mortality >= start_date
    ).count()
    total_patients_admitted = len(patient_ids)
    
    return {
        "hospital_id": hospital_id,
        "period": period,
        "total_patients_admitted": total_patients_admitted,
        "deaths_in_period": death_count,
        "mortality_rate": death_count / total_patients_admitted if total_patients_admitted > 0 else 0.0
    }



