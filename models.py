from database import Base
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String(50), default='ACTIVE')
    date_of_mortality = Column(DateTime, nullable=True)

class Hospital(Base):
    __tablename__ = "hospitals" 
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    location = Column(String(255))

class Doctor(Base):
    __tablename__ = "doctors" 
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"))
    status = Column(String(50), default='ACTIVE')

class Appointment(Base):
    __tablename__ = "appointments" 
    id = Column(Integer, primary_key=True, index=True)
    patient_user_id = Column(Integer, ForeignKey("users.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id")) 
    hospital_id = Column(Integer, ForeignKey("hospitals.id")) 
    admission_time = Column(DateTime, nullable=True)
    discharge_time = Column(DateTime, nullable=True)
    diagnosis = Column(Text, nullable=True)
    review = relationship("Review", back_populates="appointment", uselist=False)

class Review(Base):
    __tablename__ = "reviews" 
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"))
    rating = Column(Integer)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime)
    appointment = relationship("Appointment", back_populates="review")

class Bed(Base):
    __tablename__ = "beds"
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"))
    status = Column(String(50)) 