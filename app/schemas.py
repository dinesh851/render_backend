from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

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

class Token(BaseModel):
    access_token: str
    token_type: str

# Availability Schemas
class SlotValues(BaseModel):
    slot1: bool
    slot2: bool
    slot3: bool
    slot4: bool
    slot5: bool
    slot6: bool
    slot7: bool
    slot8: bool
    slot9: bool
    slot10: bool
    slot11: bool
    slot12: bool
    slot13: bool
    slot14: bool
    slot15: bool
    slot16: bool

class AvailabilityCreate(BaseModel):
    doctor_id: int
    date: datetime
    slot_values: SlotValues

class AvailabilityResponse(AvailabilityCreate):
    id: int
    
    class Config:
        from_attributes = True