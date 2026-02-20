import enum
import uuid
from sqlalchemy import Column, String, Integer, DateTime, Date, ForeignKey, Boolean, Enum as SQLEnum, Float
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from .database import Base

#-- Enums ---- 

class AppointmentType(str, enum.Enum):
    ONLINE = "ONLINE"
    IN_PERSON = "IN_PERSON"

class AppointmentStatus(str, enum.Enum):
    BOOKED = "BOOKED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"

class InvoiceStatus(str, enum.Enum):
    PAID = "PAID"
    UNPAID = "UNPAID"
    PARTIAL = "PARTIAL"

# --- HOSPITAL MODEL ---
class Hospital(Base):
    __tablename__ = "hospitals"
    # Column is named "hospital_id" in the database
    hospitalId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="hospital_id")
    name = Column(String(255), nullable=False)
    addressLine = Column(String(255), name="address_line")
    area = Column(String(100))
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(20))
    contactNumber = Column(String(20), name="contact_number")
    achievements = Column(ARRAY(String)) 
    establishedDate = Column(Date, name="established_date")
    totalBeds = Column(Integer, name="total_beds")
    createdAt = Column(DateTime, name="created_at")
    updatedAt = Column(DateTime, name="updated_at")

# --- PATIENT MODEL ---
class Patient(Base):
    __tablename__ = "patients"
    patientId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="patient_id")
    hospitalId = Column(UUID(as_uuid=True), ForeignKey("hospitals.hospital_id"), name="hospital_id", nullable=False)
    userId = Column(UUID(as_uuid=True), name="user_id", unique=True, nullable=False)
    
    fullName = Column(String(255), name="full_name", nullable=False)
    address = Column(String(255), name="address")
    phoneNumber = Column(String(20), name="phone_number")
    emergencyContact = Column(String(20), name="emergency_contact")
    bloodGroup = Column(String(20), name="blood_group")
    gender = Column(String(20), name="gender")
    dateOfBirth = Column(Date, name="date_of_birth")
    
    active = Column(Boolean, default=True, name="active")
    createdAt = Column(DateTime, name="created_at")
    updatedAt = Column(DateTime, name="updated_at")

# --- APPOINTMENT MODEL ---
class Appointment(Base):
    __tablename__ = "appointments"
    appointmentId = Column("appointment_id", UUID(as_uuid=True), primary_key=True)
    hospitalId = Column("hospital_id", UUID(as_uuid=True))
    date = Column("date", Date) 
    status = Column("status", String)
    createdAt = Column("created_at", DateTime)

class Invoice(Base):
    __tablename__ = "invoices"
    invoiceId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="invoice_id")
    hospitalId = Column(UUID(as_uuid=True), ForeignKey("hospitals.hospital_id"), name="hospital_id", nullable=False)
    patientId = Column(UUID(as_uuid=True), ForeignKey("patients.patient_id"), name="patient_id", nullable=False) 
    totalAmount = Column(Float, name="total_amount", default=0.0)
    status = Column(SQLEnum(InvoiceStatus), name="status")
    createdAt = Column(DateTime, name="created_at")
    items = relationship("InvoiceItem", back_populates="invoice")

# --- INVOICE ITEM MODEL ---
class InvoiceItem(Base):
    __tablename__ = "invoice_items"
    itemId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="item_id")
    invoiceId = Column(UUID(as_uuid=True), ForeignKey("invoices.invoice_id"), name="invoice_id", nullable=False)
    referenceId = Column(UUID(as_uuid=True), name="reference_id") 
    referenceType = Column(String(50), name="reference_type") 
    description = Column(String(255), name="description")
    cost = Column(Float, name="cost", default=0.0)
    invoice = relationship("Invoice", back_populates="items")

# --- INSURANCE CLAIMS MODEL ---
class InsuranceClaim(Base):
    __tablename__ = "insurance_claims"
    claimId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="claim_id")
    invoiceId = Column(UUID(as_uuid=True), ForeignKey("invoices.invoice_id"), name="invoice_id", nullable=False)
    providerName = Column(String(255), name="provider_name")
    policyNumber = Column(String(100), name="policy_number")
    claimAmount = Column(Float, name="claim_amount")
    status = Column(String(50), name="status") 

class TreatmentRecord(Base):
    __tablename__ = "treatment_records"
    recordId = Column(UUID(as_uuid=True), primary_key=True, name="record_id")
    treatmentId = Column(UUID(as_uuid=True), name="treatment_id", nullable=False)
    performedAt = Column(DateTime, name="performed_at")
    outcome = Column(String(100), name="outcome") 

class LabResult(Base):
    __tablename__ = "lab_result"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="id")
    testId = Column(UUID(as_uuid=True), name="test_id", nullable=False)
    uploadedAt = Column(DateTime, name="uploaded_at")
    uploadedBy = Column(UUID(as_uuid=True), name="uploaded_by") 
    description = Column(String(255), name="description")
    resultData = Column(String, name="result_data") 

class Medicine(Base):
    __tablename__ = "medicine"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="id")
    name = Column(String(255), name="name", nullable=False)
    dosageForm = Column(String(100), name="dosage_form")
    strength = Column(String(100), name="strength")
    manufacturer = Column(String(255), name="manufacturer")

class Pharmacy(Base):
    __tablename__ = "pharmacy"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    affiliatedHospitalId = Column("affiliated_hospital_id", String) 

class Bed(Base):
    __tablename__ = "beds"
    bedId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="bed_id")
    hospitalId = Column(UUID(as_uuid=True), ForeignKey("hospitals.hospital_id"), name="hospital_id")
    bedType = Column(String(50), name="bed_type") 
    status = Column(String(50), name="status") 
    createdAt = Column(DateTime, name="created_at")
    updatedAt = Column(DateTime, name="updated_at")

class Department(Base):
    __tablename__ = "departments"
    # Primary Key is named "department_id"
    departmentId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="department_id")
    hospitalId = Column(UUID(as_uuid=True), ForeignKey("hospitals.hospital_id"), name="hospital_id")
    deptName = Column(String(255), name="dept_name", nullable=False)

class DepartmentTreatment(Base):
    __tablename__ = "department_treatments_offered"
    id = Column(Integer, primary_key=True, autoincrement=True)
    departmentId = Column(
        UUID(as_uuid=True), 
        ForeignKey("departments.department_id"), # Point to the DB column name
        name="department_department_id"
    )
    treatmentName = Column(String(255), name="treatments_offered")
    department = relationship("Department")

class Ambulance(Base):
    __tablename__ = "ambulances"
    ambulanceId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="ambulance_id")
    hospitalId = Column(UUID(as_uuid=True), ForeignKey("hospitals.hospital_id"), name="hospital_id")
    vehicleNumber = Column(String(20), name="vehicle_number")
    driverName = Column(String(255), name="driver_name")
    location = Column(String(255), name="location") 
    available = Column(Boolean, default=True, name="available")

class DiagnosticCentre(Base):
    __tablename__ = "diagnostic_centre"
    id = Column(String, primary_key=True)
    affiliatedHospital = Column("affiliated_hospital", String) 
    name = Column(String, nullable=False)
    location = Column(String)
    rating = Column(Float) 

class Staff(Base):
    __tablename__ = "staff"
    staff_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(255))
    age = Column(Integer)
    sex = Column(String(255))
    role = Column(String(255))
    qualification = Column(String(255))
    experience = Column(Integer)
    status = Column(String(255))
    joined_date = Column(Date)
    # Corrected Foreign Key to point to hospitals.hospital_id
    hospital_id = Column(UUID(as_uuid=True), ForeignKey("hospitals.hospital_id"))
    app_user_id = Column(UUID(as_uuid=True), name="app_user_id", nullable=True)

class Doctor(Base):
    __tablename__ = "doctor"
    staff_id = Column(UUID(as_uuid=True), ForeignKey("staff.staff_id"), primary_key=True)
    specialization = Column(String(255))
    consultation_fee = Column(Float) 
    rating = Column(Float)    

class Nurse(Base):
    __tablename__ = "nurse"
    staff_id = Column(UUID(as_uuid=True), ForeignKey("staff.staff_id"), primary_key=True)
    shift_type = Column(String(255)) 
    # Corrected Foreign Key to point to departments.department_id
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.department_id"), nullable=True) 

class DoctorAvailability(Base):
    __tablename__ = "doctor_availability"
    availability_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(Date)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctor.staff_id"))  

class DoctorAvailabilityTimeSlot(Base):
    __tablename__ = "doctor_availability_time_slots"
    doctor_availability_availability_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("doctor_availability.availability_id"), 
        primary_key=True
    )
    time_slots = Column(String(255), primary_key=True) 

class DoctorFeedback(Base):
    __tablename__ = "doctor_feedback"
    doctor_staff_id = Column(UUID(as_uuid=True), ForeignKey("doctor.staff_id"), primary_key=True)
    feedback = Column(String(255))