# app/schemas.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy import Enum as SqlEnum
import enum

# Patient Schemas
class PatientBase(BaseModel):
    name: str
    mobile_number: str

class PatientCreate(PatientBase):
    email: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[datetime] = None

class PatientResponse(PatientCreate):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Appointment Schemas
class AppointmentStatus(str, enum.Enum):
    WAITING_APPROVAL = "waiting_approval"
    APPROVED = "approved"
    DONE = "done"
    CANCELLED = "cancelled"

class AppointmentBase(BaseModel):
    doctor_id: int
    appointment_datetime: datetime

class AppointmentCreate(AppointmentBase):
    notes: Optional[str] = None

class AppointmentResponse(AppointmentBase):
    id: str
    patient_id: str
    status: str
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Doctor Schemas
class DoctorBase(BaseModel):
    name: str
    specialization: str

class DoctorResponse(DoctorBase):
    id: int
    
    class Config:
        from_attributes = True

# Admin Schemas
class AdminBase(BaseModel):
    username: str

class AdminCreate(AdminBase):
    password: str
    is_superadmin: bool = False

# Auth Schemas
class OTPRequest(BaseModel):
    mobile_number: str

class OTPVerify(BaseModel):
    mobile_number: str
    otp: str

class OTPSuccessResponse(BaseModel):
    success: bool
    message: str
    mobile_number: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Availability Schemas
class SlotValues(BaseModel):
    slot1: bool = False
    slot2: bool = False
    slot3: bool = False
    slot4: bool = False
    slot5: bool = False
    slot6: bool = False
    slot7: bool = False
    slot8: bool = False
    slot9: bool = False
    slot10: bool = False
    slot11: bool = False
    slot12: bool = False
    slot13: bool = False
    slot14: bool = False
    slot15: bool = False
    slot16: bool = False

class AvailabilityItem(BaseModel):
    date: str  # Format: "YYYY-MM-DD"
    slot_values: SlotValues

class BulkAvailabilityCreate(BaseModel):
    availability: List[AvailabilityItem]

class AvailabilityCreate(BaseModel):
    doctor_id: int
    date: datetime
    slot_values: SlotValues

class AvailabilityResponse(AvailabilityCreate):
    id: int
    
    class Config:
        from_attributes = True

# HomeUserResponse schema
class HomeUserResponse(BaseModel):
    patient: PatientResponse
    appointments: List[AppointmentResponse]