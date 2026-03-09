import uuid
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# Import your models from your project
from app.models import Hospital, Staff, Doctor, Nurse

# 1. Database Setup (Update with your Supabase/Postgres URL)
DATABASE_URL = "postgresql://postgres:am_datatbase_0905@db.ktumlblvfndgyoengcun.supabase.co:5432/postgres?sslmode=require"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# 2. Use the SAME ID from your Streamlit config
HOSPITAL_ID = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")

def seed():
    # Add Hospital if missing
    if not session.query(Hospital).filter_by(hospitalId=HOSPITAL_ID).first():
        h = Hospital(hospitalId=HOSPITAL_ID, name="Arogya Main Hospital - Hyderabad")
        session.add(h)
    
    # Add 5 Doctors
    specialties = ["Cardiology", "Neurology", "Pediatrics", "General", "Oncology"]
    for i in range(5):
        s_id = uuid.uuid4()
        staff = Staff(staff_id=s_id, full_name=f"Dr. Navraj {i+1}", role="Doctor", 
                      status="Active", hospital_id=HOSPITAL_ID)
        doc = Doctor(staff_id=s_id, specialization=specialties[i], rating=4.5 + (i/10))
        session.add_all([staff, doc])

    # Add 5 Nurses
    shifts = ["Day", "Night", "Evening"]
    for i in range(5):
        s_id = uuid.uuid4()
        staff = Staff(staff_id=s_id, full_name=f"Nurse Smith {i+1}", role="Nurse", 
                      status="Active", hospital_id=HOSPITAL_ID)
        nurse = Nurse(staff_id=s_id, shift_type=shifts[i % 3])
        session.add_all([staff, nurse])

    session.commit()
    print("✅ Database Seeded Successfully!")

seed()