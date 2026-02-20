from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from uuid import UUID
from datetime import datetime, date
from typing import Optional, List

class BaseSchema(BaseModel):
    # Automatically handles snake_case to camelCase conversion
    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)

class HospitalRead(BaseSchema):
    hospitalId: UUID
    name: str
    addressLine: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    totalBeds: int
    contactNumber: Optional[str] = None
    establishedDate: Optional[date] = None
    createdAt: Optional[datetime] = None

class PatientBase(BaseSchema):
    fullName: str
    address: Optional[str] = None
    phoneNumber: Optional[str] = None
    emergencyContact: Optional[str] = None
    bloodGroup: Optional[str] = None
    gender: Optional[str] = None
    dateOfBirth: Optional[date] = None
    active: bool = True

class PatientRead(PatientBase):
    patientId: UUID
    hospitalId: UUID
    userId: UUID
    createdAt: Optional[datetime] = None

class AppointmentBase(BaseSchema):
    date: date
    timeSlot: str
    type: str
    status: str

class AppointmentRead(AppointmentBase):
    appointmentId: UUID
    hospitalId: UUID
    patientId: UUID
    doctorId: UUID
    createdAt: Optional[datetime] = None

class InvoiceItemRead(BaseSchema):
    itemId: UUID
    referenceType: Optional[str] = None
    description: Optional[str] = None
    cost: float

class InvoiceBase(BaseSchema):
    totalAmount: float
    status: str

class InvoiceRead(InvoiceBase):
    invoiceId: UUID
    hospitalId: UUID
    patientId: UUID
    createdAt: Optional[datetime] = None
    items: List[InvoiceItemRead] = []

class InsuranceClaimRead(BaseSchema):
    claimId: UUID
    invoiceId: UUID
    providerName: Optional[str] = None
    policyNumber: Optional[str] = None
    claimAmount: float
    status: str

class TreatmentRecordRead(BaseSchema):
    recordId: UUID
    treatmentId: UUID
    performedAt: Optional[datetime] = None
    outcome: Optional[str] = None

class LabResultRead(BaseSchema):
    id: UUID
    testId: UUID
    description: Optional[str] = None
    resultData: Optional[str] = None
    uploadedAt: Optional[datetime] = None
    uploadedBy: Optional[UUID] = None

class MedicineRead(BaseSchema):
    id: UUID
    name: str
    dosageForm: Optional[str] = None
    strength: Optional[str] = None
    manufacturer: Optional[str] = None

class PharmacyRead(BaseSchema):
    id: UUID
    name: str
    address: Optional[str] = None
    affiliatedHospitalId: UUID

class BedRead(BaseSchema):
    bedId: UUID
    hospitalId: UUID
    bedType: str
    status: str
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

class DepartmentRead(BaseSchema):
    departmentId: UUID
    hospitalId: UUID
    deptName: str

class DepartmentTreatmentRead(BaseSchema):
    departmentId: UUID
    treatmentName: str

class AmbulanceRead(BaseSchema):
    ambulanceId: UUID
    hospitalId: UUID
    vehicleNumber: str
    driverName: Optional[str] = None
    location: Optional[str] = None
    available: bool

class DiagnosticCentreRead(BaseSchema):
    id: UUID
    name: str
    location: Optional[str] = None
    rating: float
    affiliatedHospital: UUID

class StaffBase(BaseModel):
    full_name: str
    age: Optional[int] = None
    sex: Optional[str] = None
    role: str
    qualification: Optional[str] = None
    experience: Optional[int] = None
    status: str
    joined_date: Optional[date] = None
    hospital_id: UUID
    app_user_id: Optional[UUID] = None

class StaffCreate(StaffBase):
    pass

class StaffRead(StaffBase):
    staff_id: UUID

    class Config:
        from_attributes = True

class DoctorBase(BaseModel):
    specialization: str
    consultation_fee: float
    rating: Optional[float] = None
    staff_id: UUID

class DoctorRead(DoctorBase):
    class Config:
        from_attributes = True

class DoctorAnalytics(BaseModel):
    full_name: str
    specialization: str
    rating: float
    status: str

class NurseBase(BaseModel):
    shift_type: Optional[str] = None
    department_id: Optional[UUID] = None
    staff_id: UUID

class NurseCreate(NurseBase):
    pass

class NurseRead(NurseBase):
    class Config:
        from_attributes = True

class DoctorAvailabilityBase(BaseModel):
    date: date
    doctor_id: UUID

class DoctorAvailabilityCreate(DoctorAvailabilityBase):
    pass

class DoctorAvailabilityRead(DoctorAvailabilityBase):
    availability_id: UUID

    class Config:
        from_attributes = True

class TimeSlotBase(BaseModel):
    doctor_availability_availability_id: UUID
    time_slots: str

class TimeSlotCreate(TimeSlotBase):
    pass

class TimeSlotRead(TimeSlotBase):
    class Config:
        from_attributes = True

class DoctorFeedbackBase(BaseModel):
    doctor_staff_id: UUID
    feedback: Optional[str] = None

class DoctorFeedbackRead(DoctorFeedbackBase):
    class Config:
        from_attributes = True