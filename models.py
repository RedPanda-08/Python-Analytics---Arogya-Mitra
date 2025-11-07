from database import Base
from sqlalchemy import Column, Integer, String, DateTime, Date, Text, ForeignKey
from sqlalchemy.orm import relationship

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    firstName = Column(String(255), nullable=False)
    lastName = Column(String(255), nullable=False)
    dateOfBirth = Column(Date, nullable=False)
    sex = Column(String(50), nullable=False)
    contactNumber = Column(String(50), nullable=False, unique=True)
    emergencyContactNumber = Column(String(50))
    street = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    zipCode = Column(String(20))
    status = Column(String(50), default='ACTIVE', index=True)
    date_of_mortality = Column(DateTime, nullable=True)
    
    identities = relationship("PatientIdentity", back_populates="patient")
    medical_history = relationship("MedicalRecord", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient")


class PatientIdentity(Base):
    __tablename__ = "patient_identities"
    
    id = Column(Integer, primary_key=True, index=True)
    identityType = Column(String(100), nullable=False)
    identityNumber = Column(String(100), nullable=False, unique=True)
    
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    patient = relationship("Patient", back_populates="identities")

class MedicalRecord(Base):
    __tablename__ = "medical_records"
    
    id = Column(Integer, primary_key=True, index=True)
    recordDate = Column(Date)
    diagnosis = Column(Text)
    treatment = Column(Text)
    notes = Column(Text)
    
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    patient = relationship("Patient", back_populates="medical_history")


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
    patient_id = Column(Integer, ForeignKey("patients.id"), index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id")) 
    hospital_id = Column(Integer, ForeignKey("hospitals.id")) 
    admission_time = Column(DateTime, nullable=True)
    discharge_time = Column(DateTime, nullable=True)
    diagnosis = Column(Text, nullable=True)
    review = relationship("Review", back_populates="appointment", uselist=False)
    patient = relationship("Patient", back_populates="appointments")

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